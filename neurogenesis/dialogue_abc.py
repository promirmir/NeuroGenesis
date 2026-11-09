"""Three-way private real-GGUF Qwen experiment: no RAG / TXT RAG / TXT+ACF.

ACF only has a pre-existing READ-ONLY checkpoint at audit start; the same
snapshot is used for each case and is never trained on held-out questions.
Questions and completions do not enter SQLite or the aggregate report.

This is a prospective *snapshot-routing comparison*, not causal evidence
that neural structural growth improved user tasks. Literal matches are
deliberately conservative and not externally fact checked.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Callable

from .acf import AdaptiveCognitiveFabric
from .acf_answer_router import validate_semantic_provenance
from .bundled_llm import BundledModelSession
from .dialogue_ab import (
    ReadOnlyKnowledge, _contains_answer, _citation_invalid, load_audit)

KEYS = ("qwen_only", "qwen_txt", "qwen_txt_acf")


def evaluate_abc(database: str | Path, audit_jsonl: str | Path,
                 state_path: str | Path, *,
                 confirm_rights: bool = False,
                 confirm_holdout: bool = False,
                 assets_root: str | Path | None = None,
                 session_factory: Callable[[ReadOnlyKnowledge], Any] | None = None
                 ) -> dict[str, Any]:
    """Measure paired A/B/C responses on an external untouched test set."""
    if confirm_rights is not True or confirm_holdout is not True:
        raise PermissionError("Corpus rights and untouched holdout must be confirmed.")
    database, audit_jsonl, state_path = (
        Path(database), Path(audit_jsonl), Path(state_path))
    if len({database.resolve(), audit_jsonl.resolve(), state_path.resolve()}) != 3:
        raise ValueError("Corpus, audit and frozen ACF checkpoint must differ.")
    if not state_path.is_file() or state_path.is_symlink():
        raise ValueError("Existing regular private semantic ACF checkpoint required.")
    # Do not proceed if snapshot is malformed; do not replace it with fabricated
    # confidence or let holdout questions train the ACF.
    inspected = AdaptiveCognitiveFabric.load(state_path)
    if not validate_semantic_provenance(state_path, inspected):
        raise ValueError("ACF checkpoint lacks matching pinned semantic SQLite provenance.")
    scores = {key: {"literal_hits": 0, "expected_source_hits": 0,
                    "invalid_citation_cases": 0,
                    "mean_latency_ms": 0.0} for key in KEYS}
    cases, audit_digest = load_audit(audit_jsonl)
    knowledge = ReadOnlyKnowledge(database)
    session = (BundledModelSession(
        assets_root=assets_root, knowledge=knowledge, web_memory=None,
        max_tokens=240) if session_factory is None
        else session_factory(knowledge))
    outcomes: Counter[str] = Counter()
    route_status: Counter[str] = Counter()
    try:
        session.start()
        for index, case in enumerate(cases):
            # Rotate order A->B->C, B->C->A, C->A->B.
            ordered = list(KEYS[index % 3:] + KEYS[:index % 3])
            hits: dict[str, bool] = {}
            for key in ordered:
                use_context = key != "qwen_only"
                options: dict[str, Any] = {}
                if key == "qwen_txt_acf":
                    options["acf_state_path"] = state_path
                begin = time.perf_counter()
                result = session.chat(
                    [{"role": "user", "content": case["question"]}],
                    use_context=use_context, deterministic=True, **options)
                elapsed = (time.perf_counter() - begin) * 1000
                if (type(result) is not dict
                        or type(result.get("reply")) is not str
                        or type(result.get("sources")) is not list):
                    raise ValueError("Invalid local Qwen test response.")
                hit = _contains_answer(
                    result["reply"], case["expected_answer_fragment"])
                hits[key] = hit
                scores[key]["literal_hits"] += int(hit)
                scores[key]["expected_source_hits"] += int(any(
                    s.get("file") == case["expected_source"]
                    for s in result["sources"] if type(s) is dict))
                scores[key]["invalid_citation_cases"] += int(
                    _citation_invalid(result["reply"], result["sources"]))
                scores[key]["mean_latency_ms"] += elapsed
                if key == "qwen_txt_acf":
                    route = result.get("acf_routing")
                    if type(route) is not dict or type(route.get("status")) is not str:
                        raise ValueError("ACF control did not report its real route.")
                    route_status[route["status"]] += 1
            outcomes["".join("1" if hits[k] else "0" for k in KEYS)] += 1
    finally:
        # This also terminates a partially initialized native model server.
        session.stop()
    total = len(cases)
    for score in scores.values():
        score["literal_hit_rate"] = round(score["literal_hits"] / total, 6)
        score["mean_latency_ms"] = round(score["mean_latency_ms"] / total, 2)
    return {
        "protocol": "qwen_paired_abc_real_gguf_snapshot_acf_literal_v1",
        "audited_cases": total,
        "audit_sha256": audit_digest,
        "state_snapshot_event_count": inspected.events,
        "conditions": scores,
        "paired_outcomes_abc_bits": dict(sorted(outcomes.items())),
        "acf_route_status_counts": dict(sorted(route_status.items())),
        "acf_added_sources_cases": route_status.get("acf_passage_added", 0),
        "measured_literal_delta_acf_minus_txt": round(
            (scores["qwen_txt_acf"]["literal_hits"]
             - scores["qwen_txt"]["literal_hits"]) / total, 6),
        "actual_gguf_inference": session_factory is None,
        "frozen_acf_state_not_trained_on_audit": True,
        "local_sqlite_written": False,
        "internet_or_cloud_used": False,
        "raw_questions_answers_sources_in_report": False,
        "semantic_factual_accuracy_proven": False,
        "acf_neuroplasticity_caused_improvement_proven": False,
        "heldout_independence_verified": False,
        "operator_review_required_for_any_default_enablement": True,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Private read-only local 3-arm Qwen vs TXT vs TXT+ACF experiment")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--acf-state", type=Path, required=True)
    p.add_argument("--assets-root", type=Path)
    p.add_argument("--confirm-corpus-rights", action="store_true")
    p.add_argument("--confirm-heldout", action="store_true")
    args = p.parse_args(argv)
    try:
        report = evaluate_abc(
            args.db, args.audit, args.acf_state,
            confirm_rights=args.confirm_corpus_rights,
            confirm_holdout=args.confirm_heldout, assets_root=args.assets_root)
    except (OSError, ValueError, RuntimeError, sqlite3.DatabaseError,
            TimeoutError, PermissionError) as exc:
        p.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True,
                     allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
