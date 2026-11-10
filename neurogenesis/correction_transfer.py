"""Independent, privacy-preserving test of correction MEMORY TRANSFER.

Two REAL Qwen arms: no context versus exactly the same model with an
operator-approved correction store. Prospective paraphrase probes must
differ from the stored training questions; unrelated probes measure harmful
false recall. This reports literal answer matches, not factual truth,
general language intelligence, neural plasticity or weights training.

No model promotion, browsing, stored transcript, learning from audits,
SQLite writes, or hidden cloud services. A private explicit holdout is
REQUIRED; fixtures and mock sessions are not scientific results.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Callable, Iterator

from .bundled_llm import BundledModelSession
from .corrective_memory import CorrectiveMemory, _normalized
from .dialogue_ab import _citation_invalid
from .dialogue_abcd import _wilson, paired_binary_compare

MAX_AUDIT_BYTES = 128 * 1024
MAX_CASES = 32
MIN_CASES = 6
MAX_ROW_BYTES = 2500


class ReadOnlyCorrections(CorrectiveMemory):
    """Existing correction database opened ONLY with read-only connections.

    Unlike CorrectiveMemory(), construction never creates tables, a new
    database, or an index. The normal retrieval algorithm is identical.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        if (self.db_path.suffix != ".sqlite3"
                or self.db_path.is_symlink()
                or not self.db_path.is_file()):
            raise ValueError("Existing regular corrections SQLite is required.")
        with self._open() as con:
            existing = {row[0] for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
            if not {"corrections", "correction_fts"}.issubset(existing):
                raise ValueError("Incomplete existing corrections schema.")

    @contextmanager
    def _open(self) -> Iterator[sqlite3.Connection]:
        uri = self.db_path.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=8)) as con:
            con.execute("PRAGMA query_only=ON")
            yield con


def _snapshot(store: ReadOnlyCorrections) -> tuple[str, set[str], dict[int, str]]:
    """Logical digest remains stable even with SQLite WAL/checkpoint changes."""
    with store._open() as con:
        rows = con.execute(
            "SELECT id,canonical_question,question,correction,"
            "content_sha256,revision FROM corrections ORDER BY id").fetchall()
    if not rows:
        raise ValueError("Cannot evaluate an empty approved correction memory.")
    digest = hashlib.sha256(
        json.dumps(rows, ensure_ascii=False,
                   separators=(",", ":")).encode("utf-8")).hexdigest()
    return (digest,
            {str(row[1]) for row in rows},
            {int(row[0]): str(row[3]) for row in rows})


def _read_audit(path: Path, known_questions: set[str],
                corrections: dict[int, str]) -> tuple[list[dict[str, Any]], str]:
    if (path.suffix.lower() != ".jsonl" or path.is_symlink()
            or not path.is_file()
            or not 1 <= path.stat().st_size <= MAX_AUDIT_BYTES):
        raise ValueError("Existing bounded private .jsonl audit is required.")
    data = path.read_bytes()
    cases = []
    seen = set()
    positive = negative = 0
    positive_correction_ids: set[int] = set()
    for i, raw in enumerate(data.splitlines(), 1):
        if not raw or len(raw) > MAX_ROW_BYTES:
            raise ValueError(f"Invalid held-out line size at row {i}.")
        try:
            row = json.loads(raw.decode("utf-8", errors="strict"),
                             parse_constant=lambda _: (_ for _ in ()).throw(
                                 ValueError("Nonfinite audit field.")))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid private held-out JSON at row {i}.") from exc
        if type(row) is not dict or type(row.get("question")) is not str:
            raise ValueError(f"Invalid held-out question at row {i}.")
        question = row["question"].strip()
        canon = _normalized(question)
        if (not 3 <= len(question) <= 512 or canon in known_questions
                or canon in seen or any(ord(c) < 32 for c in question)):
            raise ValueError("Duplicate or in-training question in held-out audit.")
        seen.add(canon)
        if row.get("kind") == "paraphrase":
            if (set(row) != {"kind", "question", "expected_correction_id",
                             "expected_answer_fragment"}
                    or type(row["expected_correction_id"]) is not int
                    or row["expected_correction_id"] not in corrections
                    or type(row["expected_answer_fragment"]) is not str):
                raise ValueError("Malformed paraphrase case.")
            needle = row["expected_answer_fragment"].strip()
            if (not 3 <= len(needle) <= 120
                    or needle.casefold() not in corrections[
                        row["expected_correction_id"]].casefold()
                    or needle.casefold() in question.casefold()):
                raise ValueError("Paraphrase target missing from training answer or leaked into question.")
            positive += 1
            positive_correction_ids.add(row["expected_correction_id"])
        elif row.get("kind") == "unrelated":
            if (set(row) != {"kind", "question", "forbidden_answer_fragment"}
                    or type(row["forbidden_answer_fragment"]) is not str):
                raise ValueError("Malformed unrelated negative control.")
            needle = row["forbidden_answer_fragment"].strip()
            if (not 3 <= len(needle) <= 120
                    or not any(needle.casefold() in v.casefold()
                               for v in corrections.values())
                    or needle.casefold() in question.casefold()):
                raise ValueError("Negative-control fragment must come from a different stored correction.")
            negative += 1
        else:
            raise ValueError("Each case requires paraphrase or unrelated kind.")
        cases.append(row)
        if len(cases) > MAX_CASES:
            raise ValueError("Too many private held-out questions.")
    if (not MIN_CASES <= len(cases) <= MAX_CASES
            or positive < 3 or negative < 3
            or len(positive_correction_ids) < 2):
        raise ValueError(
            "Require 6..32 cases, >=3 paraphrases from >=2 correction IDs "
            "and >=3 unrelated controls.")
    return cases, hashlib.sha256(data).hexdigest()


def evaluate_transfer(
        db_path: str | Path, audit_jsonl: str | Path, *,
        confirm_rights: bool = False,
        confirm_independent_holdout: bool = False,
        assets_root: str | Path | None = None,
        session_factory: Callable[[ReadOnlyCorrections], Any] | None = None,
        ) -> dict[str, Any]:
    """Matched real-Qwen baseline vs explicit corrective memory, no updates."""
    if confirm_rights is not True or confirm_independent_holdout is not True:
        raise PermissionError("Explicit corpus rights and independent holdout confirmation required.")
    db_path, audit_jsonl = Path(db_path), Path(audit_jsonl)
    if db_path.resolve() == audit_jsonl.resolve():
        raise ValueError("Audit and correction memory must be separate files.")
    store = ReadOnlyCorrections(db_path)
    frozen_hash, known, approved = _snapshot(store)
    cases, audit_sha = _read_audit(audit_jsonl, known, approved)
    with store._open() as guard:
        initial_version = guard.execute("PRAGMA data_version").fetchone()[0]
        session = (BundledModelSession(
            assets_root=assets_root, corrections=store, knowledge=None,
            web_memory=None, max_tokens=160) if session_factory is None
            else session_factory(store))
        started = False
        outcome = {"no_memory": {"literal_hits": 0, "invalid_citation_cases": 0,
                                  "total_time_ms": 0.0},
                   "approved_memory": {"literal_hits": 0, "invalid_citation_cases": 0,
                                        "total_time_ms": 0.0}}
        positive_rows = []
        negatives: Counter[str] = Counter()
        routing: Counter[str] = Counter()
        try:
            session.start()
            started = True
            for i, case in enumerate(cases):
                if (guard.execute("PRAGMA data_version").fetchone()[0] != initial_version
                        or _snapshot(store)[0] != frozen_hash):
                    raise ValueError("Approved memory changed during independent audit.")
                answers: dict[str, str] = {}
                sources: dict[str, list[dict[str, Any]]] = {}
                for key in (("no_memory", "approved_memory") if i % 2 == 0
                            else ("approved_memory", "no_memory")):
                    start = time.perf_counter()
                    result = session.chat(
                        [{"role": "user", "content": case["question"]}],
                        use_context=key == "approved_memory",
                        deterministic=True)
                    elapsed = (time.perf_counter() - start) * 1000
                    if (type(result) is not dict
                            or type(result.get("reply")) is not str
                            or type(result.get("sources")) is not list
                            or any(type(src) is not dict
                                   or type(src.get("file")) is not str
                                   for src in result["sources"])):
                        raise ValueError("Invalid genuine-model response envelope.")
                    if key == "no_memory" and result["sources"]:
                        raise ValueError("No-context model leaked retrieved sources.")
                    answers[key] = result["reply"]
                    sources[key] = result["sources"]
                    outcome[key]["total_time_ms"] += elapsed
                    outcome[key]["invalid_citation_cases"] += int(
                        _citation_invalid(result["reply"], result["sources"]))
                    if key == "approved_memory":
                        meta = result.get("correction_memory")
                        if (type(meta) is not dict
                                or type(meta.get("approved_correction_used")) is not bool):
                            raise ValueError("Missing real correction-memory routing status.")
                        routing["used" if meta["approved_correction_used"] else "abstained"] += 1
                if case["kind"] == "paraphrase":
                    phrase = case["expected_answer_fragment"].casefold()
                    results = {}
                    expected_source = ("poprawka użytkownika #"
                                       + str(case["expected_correction_id"]))
                    for k in outcome:
                        hit = phrase in answers[k].casefold()
                        results[k] = hit
                        outcome[k]["literal_hits"] += int(hit)
                    selected = sources["approved_memory"]
                    negatives["positive_target_source_retrieved"] += int(any(
                        src["file"] == expected_source for src in selected))
                    negatives["positive_wrong_correction_source"] += int(any(
                        src["file"].startswith("poprawka użytkownika #")
                        and src["file"] != expected_source for src in selected))
                    positive_rows.append(results)
                else:
                    phrase = case["forbidden_answer_fragment"].casefold()
                    selected = sources["approved_memory"]
                    negatives["unrelated_cases"] += 1
                    negatives["unrelated_source_injected"] += int(bool(selected))
                    negatives["unrelated_forbidden_fragment_with_memory"] += int(
                        phrase in answers["approved_memory"].casefold())
                    negatives["unrelated_forbidden_fragment_without_memory"] += int(
                        phrase in answers["no_memory"].casefold())
                if (guard.execute("PRAGMA data_version").fetchone()[0] != initial_version
                        or _snapshot(store)[0] != frozen_hash):
                    raise ValueError("Approved memory mutated during private holdout.")
        finally:
            # Release the native server even if startup/response failed.
            session.stop()
    count_pos = len(positive_rows)
    for label, values in outcome.items():
        values["positive_literal_rate"] = round(
            values["literal_hits"] / count_pos, 6)
        values["positive_wilson_95_descriptive"] = _wilson(
            values["literal_hits"], count_pos)
        values["mean_latency_ms_all_cases"] = round(
            values.pop("total_time_ms") / len(cases), 2)
    return {
        "protocol": "neurogenesis_prospective_correction_transfer_ab_v1",
        "audit_sha256": audit_sha,
        "private_memory_logical_sha256": frozen_hash,
        "total_cases": len(cases),
        "paraphrases": count_pos,
        "unrelated_negative_controls": negatives["unrelated_cases"],
        "conditions": outcome,
        "paired_positive_literal_comparison": paired_binary_compare(
            positive_rows, left="approved_memory", right="no_memory"),
        "positive_expected_source_hits": negatives["positive_target_source_retrieved"],
        "positive_wrong_correction_sources": negatives["positive_wrong_correction_source"],
        "unrelated_sources_injected": negatives["unrelated_source_injected"],
        "unrelated_forbidden_fragment_with_memory": negatives[
            "unrelated_forbidden_fragment_with_memory"],
        "unrelated_forbidden_fragment_without_memory": negatives[
            "unrelated_forbidden_fragment_without_memory"],
        "retrieval": dict(sorted(routing.items())),
        "actual_gguf_inference": session_factory is None,
        "frozen_corpus_checked": True,
        "automatic_updates_or_training": False,
        "raw_private_questions_answers_emitted": False,
        "truth_or_agi_proven": False,
        "heldout_independence_verified_by_program": False,
        "automatic_model_promotion": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only local Qwen memory vs no-memory on private unseen paraphrases/controls")
    parser.add_argument("--corrections-db", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--assets-root", type=Path)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--confirm-heldout", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = evaluate_transfer(
            args.corrections_db, args.audit, assets_root=args.assets_root,
            confirm_rights=args.confirm_corpus_rights,
            confirm_independent_holdout=args.confirm_heldout)
    except (OSError, ValueError, RuntimeError, PermissionError,
            sqlite3.DatabaseError, TimeoutError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True,
                     allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
