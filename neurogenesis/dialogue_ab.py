"""Prospective paired evaluation of the REAL bundled Qwen conversation path.

Compares pretrained Qwen alone against the SAME model with approved local TXT
retrieval. Never trains or modifies model weights, learns from audit questions,
browses the web, claims ACF causes gains, or silently publishes test data.

This is an exact-literal benchmark, not an independent truth/AGI evaluation.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
from typing import Any, Callable

from .bundled_llm import BundledModelSession
from .local_knowledge import LocalKnowledge

MAX_CASES = 32
MAX_AUDIT_BYTES = 96_000
MAX_ROW_BYTES = 3000


class ReadOnlyKnowledge(LocalKnowledge):
    """Use approved existing FTS indexes; refuse schema creation and writes."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        if (not self.db_path.is_file() or self.db_path.is_symlink()
                or self.db_path.stat().st_size > 256 * 1024 * 1024):
            raise ValueError("Existing regular local TXT SQLite database required.")
        with self._open() as con:
            expected = {"local_sources", "local_passages", "local_fts"}
            actual = {r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
            if not expected <= actual:
                raise ValueError("Database does not contain approved local TXT index.")

    @contextmanager
    def _open(self):
        uri = self.db_path.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=5)) as con:
            con.execute("PRAGMA query_only=ON")
            yield con


def load_audit(path: Path) -> tuple[list[dict[str, str]], str]:
    if (not path.is_file() or path.is_symlink()
            or path.suffix.lower() != ".jsonl"
            or not 1 <= path.stat().st_size <= MAX_AUDIT_BYTES):
        raise ValueError("Existing bounded local .jsonl audit required.")
    raw = path.read_bytes()
    seen: set[str] = set()
    cases = []
    for line in raw.splitlines():
        if not 1 <= len(line) <= MAX_ROW_BYTES:
            raise ValueError("Blank or oversized audit row.")
        try:
            item = json.loads(line.decode("utf-8", errors="strict"),
                              parse_constant=lambda _: (_ for _ in ()).throw(
                                  ValueError("Nonfinite JSON not allowed.")))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid UTF-8/JSON evaluation row.") from exc
        if type(item) is not dict or set(item) != {
                "question", "expected_answer_fragment", "expected_source"}:
            raise ValueError("Each audit case requires three exact fields.")
        q, phrase, source = (item[k] for k in (
            "question", "expected_answer_fragment", "expected_source"))
        if (any(type(v) is not str for v in (q, phrase, source))
                or not 3 <= len(q.strip()) <= 512
                or not 2 <= len(phrase.strip()) <= 160
                or not 1 <= len(source.strip()) <= 150
                or any(ord(ch) < 32 for v in (q, phrase, source) for ch in v)
                or "/" in source or "\\" in source or source in (".", "..")):
            raise ValueError("Invalid question, literal answer or source basename.")
        key = " ".join(q.casefold().split())
        if key in seen:
            raise ValueError("Repeated test question; holdout cannot be weighted twice.")
        seen.add(key)
        cases.append(item)
        if len(cases) > MAX_CASES:
            raise ValueError("Too many evaluation cases.")
    if len(cases) < 4:
        raise ValueError("At least four independent held-out cases required.")
    return cases, hashlib.sha256(raw).hexdigest()


def _contains_answer(reply: str, expected: str) -> bool:
    # Literal, whitespace-normalized only; deliberately no LLM-as-judge.
    clean = lambda text: " ".join(text.casefold().split())
    return clean(expected) in clean(reply)


def _citation_invalid(reply: str, sources: list[dict[str, Any]]) -> bool:
    """Flag every numeric [L...] citation without an EXACT supplied label.

    Previous [1-99] matching missed hallucinated [L0], [L100] and [L999].
    Literal labels are required: [L01] is not the same as [L1].
    This metric detects unsupported numeric source references; it is not
    a semantic truth/factual correctness judge.
    """
    allowed = {s.get("label") for s in sources if type(s) is dict}
    return any("L" + number not in allowed for number in re.findall(
        r"\[L([0-9]+)\]", reply))


def evaluate(database: str | Path, audit_jsonl: str | Path, *,
             confirm_rights: bool = False, confirm_holdout: bool = False,
             assets_root: str | Path | None = None,
             session_factory: Callable[[ReadOnlyKnowledge], Any] | None = None
             ) -> dict[str, Any]:
    """Paired, deterministic, single-session inference; no user data published.

    A pre-existing, independent, user-owned reference corpus is required.
    No random split of the model's training data is passed off as a holdout.
    The optional factory exists ONLY to test harness logic without a GGUF.
    """
    if confirm_rights is not True or confirm_holdout is not True:
        raise PermissionError("Explicit corpus rights and untouched holdout required.")
    database, audit_jsonl = Path(database), Path(audit_jsonl)
    if database.resolve() == audit_jsonl.resolve():
        raise ValueError("Audit must be separate from SQLite.")
    cases, digest = load_audit(audit_jsonl)
    knowledge = ReadOnlyKnowledge(database)
    if session_factory is None:
        session = BundledModelSession(
            assets_root=assets_root, knowledge=knowledge, web_memory=None,
            max_tokens=240)
    else:
        session = session_factory(knowledge)
    scores = {
        k: {"literal_answer_hits": 0, "expected_source_hits": 0,
            "unsupported_citations": 0, "latency_ms_total": 0.0}
        for k in ("qwen_only", "qwen_plus_approved_txt")}
    paired = {"both_correct": 0, "rag_only_correct": 0,
              "base_only_correct": 0, "neither_correct": 0}
    completed = 0
    session.start()
    try:
        for index, case in enumerate(cases):
            # Alternate execution order, same model and generation controls.
            # No previous answers are included in the next question history.
            modes = (("qwen_only", False), ("qwen_plus_approved_txt", True))
            if index % 2:
                modes = tuple(reversed(modes))
            matched: dict[str, bool] = {}
            for key, use_context in modes:
                started = time.perf_counter()
                result = session.chat(
                    [{"role": "user", "content": case["question"]}],
                    use_context=use_context, deterministic=True)
                elapsed = (time.perf_counter() - started) * 1000
                reply = result["reply"]
                sources = result["sources"]
                if type(reply) is not str or type(sources) is not list:
                    raise ValueError("Invalid real model response contract.")
                hit = _contains_answer(reply, case["expected_answer_fragment"])
                scores[key]["literal_answer_hits"] += int(hit)
                scores[key]["expected_source_hits"] += int(any(
                    s.get("file") == case["expected_source"] for s in sources))
                scores[key]["unsupported_citations"] += int(
                    _citation_invalid(reply, sources))
                scores[key]["latency_ms_total"] += round(elapsed, 3)
                matched[key] = hit
            b, a = matched["qwen_only"], matched["qwen_plus_approved_txt"]
            bucket = ("both_correct" if b and a else
                      "rag_only_correct" if a else
                      "base_only_correct" if b else "neither_correct")
            paired[bucket] += 1
            completed += 1
    finally:
        session.stop()
    counts = {}
    for key, data in scores.items():
        counts[key] = {
            **{k: data[k] for k in (
                "literal_answer_hits", "expected_source_hits",
                "unsupported_citations")},
            "literal_answer_rate": round(data["literal_answer_hits"] / completed, 6)
                if completed else None,
            "mean_inference_latency_ms": round(
                data["latency_ms_total"] / completed, 2) if completed else None,
        }
    return {
        "protocol": "paired_qwen_approved_txt_literal_holdout_v1",
        "audit_sha256": digest,
        "case_count": completed,
        "conditions": counts,
        "paired_outcomes": paired,
        "measured_literal_answer_rate_delta_rag_minus_base": round(
            (scores["qwen_plus_approved_txt"]["literal_answer_hits"]
             - scores["qwen_only"]["literal_answer_hits"]) / completed, 6),
        "actual_gguf_inference": session_factory is None,
        "same_model_same_session": True,
        "sampling_disabled": True,
        "pretrained_weights_changed": False,
        "acf_influenced_answers": False,
        "independently_verified_truth": False,
        "heldout_independence_verified": False,
        "task_generalization_proven": False,
        "raw_queries_or_answers_in_report": False,
        "internet_or_cloud_used": False,
        "local_knowledge_writes": False,
        "privacy_note": "Report includes only aggregate counts and audit SHA-256.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Local, paired real GGUF Qwen vs approved TXT reference evaluation")
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--assets-root", type=Path)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--confirm-heldout", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = evaluate(
            args.db, args.audit, assets_root=args.assets_root,
            confirm_rights=args.confirm_corpus_rights,
            confirm_holdout=args.confirm_heldout)
    except (OSError, ValueError, PermissionError, RuntimeError,
            sqlite3.DatabaseError, TimeoutError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
