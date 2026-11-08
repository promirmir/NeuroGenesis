"""Read-only prospective QA/citation/abstention evaluator for LOCAL evidence.

Scores *literal source attribution*, NOT correctness of factual claims, model
reasoning, multilingual semantics or neural weight improvement.
No network, brain updates, SQLite writes, per-question logging or uploads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import time
from typing import Any
from urllib.parse import urlsplit

from .knowledge import answer_question

MAX_EVAL_BYTES = 256 * 4096
MAX_EXAMPLES = 256
MAX_ROW_BYTES = 4096
MAX_QUESTION_CHARS = 512
MAX_REQUIRED_QUOTE = 160


def _read_audit(path: Path) -> tuple[list[dict[str, Any]], str]:
    if path.is_symlink() or not path.is_file() or path.suffix.lower() != ".jsonl":
        raise ValueError("local audit must be an existing regular .jsonl file")
    if not 1 <= path.stat().st_size <= MAX_EVAL_BYTES:
        raise ValueError("audit exceeds bounded size")
    raw = path.read_bytes()
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line or len(line) > MAX_ROW_BYTES:
            raise ValueError(f"empty or oversized audit row {line_no}")
        try:
            row = json.loads(line.decode("utf-8", errors="strict"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid audit JSON/UTF-8 row {line_no}") from exc
        if type(row) is not dict or type(row.get("question")) is not str:
            raise ValueError(f"invalid audit object row {line_no}")
        q = row["question"]
        if not 1 <= len(q.strip()) <= MAX_QUESTION_CHARS or any(ord(c) < 32 for c in q):
            raise ValueError(f"invalid question row {line_no}")
        key = " ".join(q.casefold().split())
        if key in seen:
            raise ValueError("duplicate evaluation question")
        seen.add(key)
        answerable = row.get("answerable")
        if type(answerable) is not bool:
            raise ValueError(f"explicit answerable boolean required row {line_no}")
        if answerable:
            if set(row) != {"question", "answerable", "expected_source_url", "required_quote"}:
                raise ValueError(f"answerable row {line_no} has missing/extra keys")
            url = row["expected_source_url"]
            quote = row["required_quote"]
            if (type(url) is not str or len(url) > 2048 or
                    urlsplit(url).scheme != "https" or not urlsplit(url).hostname):
                raise ValueError(f"invalid source URL row {line_no}")
            if (type(quote) is not str or
                    not 2 <= len(quote.strip()) <= MAX_REQUIRED_QUOTE):
                raise ValueError(f"invalid expected literal quote row {line_no}")
        else:
            if set(row) != {"question", "answerable"}:
                raise ValueError(f"unsupported row {line_no} must not have expected claims")
        rows.append(row)
        if len(rows) > MAX_EXAMPLES:
            raise ValueError("too many evaluation cases")
    if not rows:
        raise ValueError("audit corpus is empty")
    if not any(r["answerable"] for r in rows) or all(r["answerable"] for r in rows):
        raise ValueError("audit must contain both source-answerable and unsupported cases")
    return rows, hashlib.sha256(raw).hexdigest()


def _percentile_ms(samples: list[float], fraction: float) -> float:
    sorted_samples = sorted(samples)
    return sorted_samples[max(0, math.ceil(fraction * len(samples)) - 1)] * 1000


def evaluate_qa(database: str | Path, audit_jsonl: str | Path, *,
                confirm_rights: bool = False,
                confirm_heldout: bool = False) -> dict[str, Any]:
    """Prospective QA evaluation of CURRENT local knowledge, no mutations.

    'correct' means the answer actually QUOTED the operator-expected exact
    literal span from the operator-expected URL. It does NOT assert that
    the quoted words are true or that a semantic answer was synthesized.
    """
    if confirm_rights is not True or confirm_heldout is not True:
        raise PermissionError("explicit audit-corpus rights and untouched heldout confirmation required")
    db = Path(database)
    if not db.is_file() or db.is_symlink():
        raise ValueError("existing regular private SQLite required; never create an audit database")
    audit_path = Path(audit_jsonl)
    if audit_path.resolve() == db.resolve():
        raise ValueError("audit JSONL must differ from local SQLite")
    rows, audit_sha = _read_audit(audit_path)
    supported = sum(int(r["answerable"]) for r in rows)
    unsupported = len(rows) - supported
    answered = 0
    correct = 0
    source_hits = 0
    unsupported_abstentions = 0
    times: list[float] = []

    # SQLite read-only URI ensures no schema migrations, no hidden SQLite
    # writes, and no accidental brain/sensory updates from test questions.
    uri = db.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=2) as con:
        con.execute("PRAGMA query_only=ON")
        for case in rows:
            start = time.perf_counter()
            result = answer_question(con, case["question"])
            times.append(max(0.0, time.perf_counter() - start))
            if result is not None:
                answered += 1
            if case["answerable"]:
                if result is None:
                    continue
                expected_url = case["expected_source_url"]
                source_hits += int(any(s["url"] == expected_url for s in result["sources"]))
                correct += int(any(
                    q["url"] == expected_url
                    and case["required_quote"].casefold() in q["text"].casefold()
                    for q in result["quoted_evidence"]))
            else:
                unsupported_abstentions += int(result is None)
    return {
        "task": "literal_evidence_qa_and_abstention_not_semantic_or_truth_accuracy",
        "audit_sha256": audit_sha,
        "cases": len(rows),
        "supported_cases": supported,
        "unsupported_cases": unsupported,
        "answered_cases": answered,
        "correct_literal_citations": correct,
        "supported_source_hit_rate": source_hits / supported,
        "supported_exact_quote_recall": correct / supported,
        "quote_precision_all_answered": correct / answered if answered else 0.0,
        "unsupported_abstention_rate": unsupported_abstentions / unsupported,
        "unsupported_false_citation_rate": (unsupported - unsupported_abstentions) / unsupported,
        "overall_strict_fixture_accuracy": (correct + unsupported_abstentions) / len(rows),
        "latency_p50_ms": _percentile_ms(times, 0.5),
        "latency_p95_ms": _percentile_ms(times, 0.95),
        "independently_fact_checked": False,
        "audit_independence_verified": False,
        "trainable_weights_evaluated": False,
        "internet_used": False,
        "sqlite_modified": False,
        "raw_questions_in_report": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline private SQLite evidence citation QA evaluator (no model inference)")
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--confirm-held-out", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = evaluate_qa(
            args.db, args.audit, confirm_rights=args.confirm_corpus_rights,
            confirm_heldout=args.confirm_held_out)
    except (OSError, ValueError, PermissionError, sqlite3.DatabaseError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
