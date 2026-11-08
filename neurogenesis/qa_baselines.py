"""Local, read-only BM25 control for prospective literal-evidence QA.

BM25 is a non-neural *ranking* baseline. It can select an irrelevant passage;
never treat a high lexical rank as factual support or calibrated probability.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
import json
import math
import re
from pathlib import Path
import sqlite3
import statistics
import time
import unicodedata
from typing import Any

from .knowledge import _terms, answer_question, TOKEN, STOP
from .qa_eval import _read_audit

MAX_BASELINE_PASSAGES = 4096
MAX_DOCUMENT_TOKENS = 600


def load_latest_passages(con: sqlite3.Connection) -> list[tuple[str, str, tuple[str, ...]]]:
    """Bounded snapshot of *latest revisions* only, no web calls or DB mutation."""
    rows = con.execute(
        "SELECT p.body,s.url FROM knowledge_passages p "
        "JOIN knowledge_sources s ON s.id=p.source_id "
        "WHERE s.id=(SELECT MAX(s2.id) FROM knowledge_sources s2 WHERE s2.url=s.url) "
        "ORDER BY s.url,p.ordinal LIMIT ?",
        (MAX_BASELINE_PASSAGES + 1,)).fetchall()
    if len(rows) > MAX_BASELINE_PASSAGES:
        raise ValueError("too many passages for bounded BM25 audit")
    result = []
    for body, url in rows:
        # Preserve term frequency: unlike the query-term helper, BM25
        # counts repeated occurrences in each source passage.
        tokens = tuple(
            word for word in TOKEN.findall(
                unicodedata.normalize("NFKC", body).casefold())
            if word not in STOP
        )
        if not tokens or len(tokens) > MAX_DOCUMENT_TOKENS:
            continue
        result.append((body, url, tokens))
    return result


def bm25_excerpt(passages: list[tuple[str, str, tuple[str, ...]]],
                 question: str) -> tuple[str, str] | None:
    """Deterministic BM25 term-rank baseline with conservative overlap guard."""
    if type(question) is not str or not question.strip() or len(question) > 512:
        return None
    qterms = _terms(question)[:12]
    if not qterms or not passages:
        return None
    N = len(passages)
    dfs = Counter()
    lengths = []
    for _, _, words in passages:
        lengths.append(len(words))
        dfs.update(set(words))
    avg_len = sum(lengths) / N
    min_match = 1 if len(qterms) == 1 else 2
    polar = question.casefold().lstrip().startswith(("czy ", "a czy "))
    requested = set(qterms)
    query_negated = bool(re.search(r"\b(?:nie|not|never)\b", question.casefold()))
    winner: tuple[str, str] | None = None
    top = float("-inf")
    for (body, url, tokens), length in zip(passages, lengths):
        tf = Counter(tokens)
        matches = sum(t in tf for t in qterms)
        if matches < min_match or matches / len(qterms) < 0.4:
            continue
        if polar:
            if not requested.issubset(tf):
                continue
            excerpt_negated = bool(__import__("re").search(r"\b(?:nie|not|never)\b", body.casefold()))
            if excerpt_negated != query_negated:
                continue
        score = 0.0
        for t in qterms:
            count = tf[t]
            if not count:
                continue
            idf = math.log1p((N - dfs[t] + 0.5) / (dfs[t] + 0.5))
            score += idf * (count * (1.2 + 1)) / (
                count + 1.2 * (1 - 0.75 + 0.75 * length / avg_len))
        if score > top:
            top = score
            winner = (body, url)
    return winner


def _score(outcomes: list[tuple[dict[str, Any], list[tuple[str, str]]]]) -> dict[str, Any]:
    supported = sum(c["answerable"] for c, _ in outcomes)
    unsupported = len(outcomes) - supported
    answered = sum(bool(hits) for _, hits in outcomes)
    correct = sum(
        case["answerable"] and any(
            hit[1] == case["expected_source_url"]
            and case["required_quote"].casefold() in hit[0].casefold()
            for hit in hits)
        for case, hits in outcomes)
    abstained = sum(not case["answerable"] and not hits for case, hits in outcomes)
    return {
        "supported_literal_quote_recall": correct / supported,
        "unsupported_false_citation_rate": 1 - abstained / unsupported,
        "strict_fixture_accuracy": (correct + abstained) / len(outcomes),
        "answered": answered,
        "correct_literal_citations": correct,
        "unsupported_abstentions": abstained,
    }


def compare_bm25(db_path: str | Path, audit_path: str | Path, *,
                 confirm_rights: bool = False,
                 confirm_untouched: bool = False) -> dict[str, Any]:
    """Compare current production source selection vs BM25 on *same* QA audit.

    No raw questions, source text, URLs or local paths are included in report.
    """
    if confirm_rights is not True or confirm_untouched is not True:
        raise PermissionError("operator must confirm audit rights and untuned heldout data")
    db = Path(db_path)
    audit = Path(audit_path)
    if db.is_symlink() or not db.is_file() or db.resolve() == audit.resolve():
        raise ValueError("existing distinct SQLite database required")
    rows, audit_hash = _read_audit(audit)
    # Both techniques see the exact same read-only latest-revision DB.
    uri = db.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=2)) as con:
        con.execute("PRAGMA query_only=ON")
        passages = load_latest_passages(con)
        actual = []
        baseline = []
        current_seconds = []
        baseline_seconds = []
        for case in rows:
            started = time.perf_counter()
            answer = answer_question(con, case["question"])
            current_seconds.append(max(0.0, time.perf_counter() - started))
            src = [(q["text"], q["url"]) for q in answer["quoted_evidence"]] if answer else []
            actual.append((case, src))
            started = time.perf_counter()
            bm25 = bm25_excerpt(passages, case["question"])
            baseline_seconds.append(max(0.0, time.perf_counter() - started))
            baseline.append((case, [bm25] if bm25 is not None else []))
    a = _score(actual)
    b = _score(baseline)
    return {
        "task": "literal_source_qa_comparison_not_semantic_truth",
        "audit_sha256": audit_hash,
        "cases": len(rows),
        "supported_cases": sum(r["answerable"] for r in rows),
        "unsupported_cases": sum(not r["answerable"] for r in rows),
        "corpus_passages": len(passages),
        "current_source_retrieval": a,
        "bm25_non_neural_control": b,
        "strict_accuracy_difference_current_minus_bm25": (
            a["strict_fixture_accuracy"] - b["strict_fixture_accuracy"]),
        "current_latency_median_ms": statistics.median(current_seconds) * 1000,
        "bm25_latency_median_ms": statistics.median(baseline_seconds) * 1000,
        "baseline_is_deployed": False,
        "current_algorithm_modified": False,
        "no_checkpoint_or_sqlite_mutation": True,
        "training_data_independence_verified": False,
        "factual_truth_verified": False,
        "internet_used": False,
        "raw_private_questions_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only BM25 vs current local cited evidence QA, NOT model deployment")
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--confirm-untouched", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = compare_bm25(
            args.db, args.audit,
            confirm_rights=args.confirm_corpus_rights,
            confirm_untouched=args.confirm_untouched)
    except (OSError, ValueError, PermissionError, sqlite3.DatabaseError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
