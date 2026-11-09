"""Matched FOUR-arm offline Qwen evaluation for scientific ACF ablation.

A: pretrained Qwen without source passages
B: same Qwen + ordinary approved TXT retrieval
C: B + guarded predictive semantic ACF route
D: B + non-neural current-topic retrieval (matched query/context budget)

C vs D is the essential comparison; C vs B alone cannot show that ACF
predictions add value beyond ordinary topic-driven retrieval. All automated
scoring is an exact literal fragment check, NOT verified factual truth.

Never change an ACF checkpoint or local source index during the trial.
Data-version guards detect concurrent SQLite edits and a cryptographic
digest checks the ACF checkpoint after each case. The GUI is not trained
or switched to this experimental policy automatically.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import time
from typing import Any, Callable

from .acf import AdaptiveCognitiveFabric
from .acf_answer_router import validate_semantic_provenance
from .bundled_llm import BundledModelSession
from .dialogue_ab import (
    ReadOnlyKnowledge, _contains_answer, _citation_invalid, load_audit)

ARMS = ("qwen_only", "qwen_txt", "qwen_txt_acf", "qwen_txt_topic_control")
_95_Z = 1.959963984540054


def _wilson(hits: int, total: int) -> list[float]:
    """Wilson score interval for a binomial rate (descriptive only)."""
    if not 0 <= hits <= total or total < 1:
        raise ValueError("Invalid binary-score denominator.")
    p = hits / total
    z2 = _95_Z * _95_Z
    denom = 1 + z2 / total
    mid = (p + z2 / (2 * total)) / denom
    half = _95_Z * math.sqrt(
        (p * (1 - p) + z2 / (4 * total)) / total) / denom
    return [round(max(0.0, mid - half), 6),
            round(min(1.0, mid + half), 6)]


def paired_binary_compare(rows: list[dict[str, bool]], *,
                          left: str, right: str) -> dict[str, Any]:
    """Exact two-sided sign/McNemar p-value for matched discordant pairs.

    The p-value is exploratory and does not correct multiple comparisons.
    A small/zero sample or result near p=1 is never 'proof of equality'.
    """
    if type(rows) is not list or not rows:
        raise ValueError("Paired binary outcomes must be nonempty.")
    gain = loss = both = neither = 0
    for row in rows:
        if (type(row) is not dict or type(row.get(left)) is not bool
                or type(row.get(right)) is not bool):
            raise ValueError("Missing or nonboolean paired outcome.")
        a, b = row[left], row[right]
        if a and not b:
            gain += 1
        elif b and not a:
            loss += 1
        elif a:
            both += 1
        else:
            neither += 1
    discordant = gain + loss
    exact_p = (min(1.0, 2 * sum(
        math.comb(discordant, k) for k in range(min(gain, loss) + 1))
        / (2 ** discordant)) if discordant else 1.0)
    return {
        "left": left, "right": right,
        "left_only_correct": gain,
        "right_only_correct": loss,
        "both_correct": both, "neither_correct": neither,
        "discordant_pairs": discordant,
        "literal_rate_difference": round((gain - loss) / len(rows), 6),
        "exploratory_two_sided_exact_p": round(exact_p, 8),
        "multiple_testing_corrected": False,
        "independent_factual_verification": False,
    }


class FrozenLocalEvidence:
    """Verify pre-existing snapshot and two read-only SQLite DBs are stable."""

    def __init__(self, state_path: Path, knowledge: ReadOnlyKnowledge):
        self.state = state_path
        self.knowledge = knowledge
        self.ledger = state_path.with_name("semantic_fabric.sqlite3")
        self._handles: list[sqlite3.Connection] = []
        self._versions: list[int] = []
        self._acf_sha: str | None = None
        self._corpus: str | None = None

    def __enter__(self):
        try:
            for filename in (self.ledger, self.knowledge.db_path):
                if not filename.is_file() or filename.is_symlink():
                    raise ValueError("Existing regular private SQLite required.")
                uri = filename.resolve().as_uri() + "?mode=ro"
                con = sqlite3.connect(uri, uri=True, timeout=6)
                self._handles.append(con)
                con.execute("PRAGMA query_only=ON")
                self._versions.append(
                    int(con.execute("PRAGMA data_version").fetchone()[0]))
            self._acf_sha = self._snapshot_sha()
            self._corpus = self.knowledge.corpus_fingerprint()
            self.verify()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def _snapshot_sha(self) -> str:
        if not self.state.is_file() or self.state.is_symlink():
            raise ValueError("Immutable regular ACF checkpoint disappeared.")
        # The verified ACF loader also enforces the snapshot size bound.
        if self.state.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("Oversized ACF checkpoint.")
        return hashlib.sha256(self.state.read_bytes()).hexdigest()

    def verify(self):
        if self._snapshot_sha() != self._acf_sha:
            raise ValueError("ACF checkpoint changed during held-out trial.")
        for con, old_version in zip(self._handles, self._versions):
            if int(con.execute("PRAGMA data_version").fetchone()[0]) != old_version:
                raise ValueError("SQLite changed during held-out trial.")
        if self.knowledge.corpus_fingerprint() != self._corpus:
            raise ValueError("Approved corpus revisions changed during trial.")

    def __exit__(self, _type, _value, _tb):
        for con in reversed(self._handles):
            con.close()
        self._handles.clear()
        return False


def evaluate_abcd(
        database: str | Path, audit_jsonl: str | Path,
        state_path: str | Path, *,
        confirm_rights: bool = False, confirm_holdout: bool = False,
        assets_root: str | Path | None = None,
        session_factory: Callable[[ReadOnlyKnowledge], Any] | None = None
        ) -> dict[str, Any]:
    if confirm_rights is not True or confirm_holdout is not True:
        raise PermissionError("Explicit corpus rights and untouched holdout required.")
    database, audit_jsonl, state_path = map(
        Path, (database, audit_jsonl, state_path))
    if len({p.resolve() for p in (database, audit_jsonl, state_path)}) != 3:
        raise ValueError("Distinct corpus, audit and checkpoint paths required.")
    if not state_path.is_file() or state_path.is_symlink():
        raise ValueError("Existing private ACF checkpoint required.")
    inspected = AdaptiveCognitiveFabric.load(state_path)
    if not validate_semantic_provenance(state_path, inspected):
        raise ValueError("No matching semantic-Qwen observation ledger.")
    cases, audit_digest = load_audit(audit_jsonl)
    knowledge = ReadOnlyKnowledge(database)
    scores: dict[str, dict[str, Any]] = {
        arm: {"literal_hits": 0, "expected_source_hits": 0,
              "invalid_citation_cases": 0, "latency_ms_total": 0.0}
        for arm in ARMS
    }
    status_acf: Counter[str] = Counter()
    status_control: Counter[str] = Counter()
    paired_outcomes: Counter[str] = Counter()
    comparisons: list[dict[str, bool]] = []
    same_sources = 0
    session = (BundledModelSession(
        assets_root=assets_root, knowledge=knowledge, web_memory=None,
        max_tokens=240) if session_factory is None
        else session_factory(knowledge))
    with FrozenLocalEvidence(state_path, knowledge) as frozen:
        try:
            session.start()
            for index, case in enumerate(cases):
                frozen.verify()
                # Latin-square-like rotation minimizes fixed run-order bias.
                order = ARMS[index % 4:] + ARMS[:index % 4]
                outcomes: dict[str, bool] = {}
                sources_by_arm: dict[str, tuple[tuple[str, str], ...]] = {}
                for arm in order:
                    options: dict[str, Any] = {}
                    if arm == "qwen_txt_acf":
                        options["acf_state_path"] = state_path
                    if arm == "qwen_txt_topic_control":
                        options["topic_control"] = True
                    t = time.perf_counter()
                    result = session.chat(
                        [{"role": "user", "content": case["question"]}],
                        use_context=arm != "qwen_only", deterministic=True,
                        **options)
                    elapsed = (time.perf_counter() - t) * 1000
                    if (type(result) is not dict
                            or type(result.get("reply")) is not str
                            or type(result.get("sources")) is not list
                            or any(type(s) is not dict
                                   or type(s.get("file")) is not str
                                   for s in result["sources"])):
                        raise ValueError("Invalid real-Qwen answer evidence envelope.")
                    hit = _contains_answer(
                        result["reply"], case["expected_answer_fragment"])
                    outcomes[arm] = hit
                    scores[arm]["literal_hits"] += int(hit)
                    scores[arm]["expected_source_hits"] += int(any(
                        s["file"] == case["expected_source"]
                        for s in result["sources"]))
                    scores[arm]["invalid_citation_cases"] += int(
                        _citation_invalid(result["reply"], result["sources"]))
                    scores[arm]["latency_ms_total"] += elapsed
                    sources_by_arm[arm] = tuple(
                        (s["file"], str(s.get("sha256", "")))
                        for s in result["sources"])
                    if arm == "qwen_txt_acf":
                        report = result.get("acf_routing")
                        if type(report) is not dict or type(report.get("status")) is not str:
                            raise ValueError("Actual ACF routing result missing.")
                        status_acf[report["status"]] += 1
                    if arm == "qwen_txt_topic_control":
                        report = result.get("topic_control_routing")
                        if type(report) is not dict or type(report.get("status")) is not str:
                            raise ValueError("Actual control routing result missing.")
                        status_control[report["status"]] += 1
                same_sources += int(
                    sources_by_arm["qwen_txt_acf"] ==
                    sources_by_arm["qwen_txt_topic_control"])
                paired_outcomes["".join(
                    "1" if outcomes[k] else "0" for k in ARMS)] += 1
                comparisons.append(outcomes)
                frozen.verify()
        finally:
            # Close even a partially initialized native server.
            session.stop()
    total = len(cases)
    conditions = {}
    for arm, score in scores.items():
        conditions[arm] = {
            "literal_hits": score["literal_hits"],
            "literal_hit_rate": round(score["literal_hits"] / total, 6),
            "wilson_95_descriptive": _wilson(score["literal_hits"], total),
            "expected_source_hits": score["expected_source_hits"],
            "invalid_citation_cases": score["invalid_citation_cases"],
            "mean_latency_ms": round(score["latency_ms_total"] / total, 2),
        }
    return {
        "protocol": "paired_qwen_abcd_acf_vs_non_neural_topic_v1",
        "audited_cases": total,
        "audit_sha256": audit_digest,
        "acf_state_events": inspected.events,
        "conditions": conditions,
        "paired_outcomes_abcd_bits": dict(sorted(paired_outcomes.items())),
        "acf_routing_status_counts": dict(sorted(status_acf.items())),
        "topic_control_status_counts": dict(sorted(status_control.items())),
        "acf_passage_added_cases": status_acf.get("acf_passage_added", 0),
        "topic_control_passage_added_cases": status_control.get(
            "topic_control_passage_added", 0),
        "same_c_and_d_source_selection_cases": same_sources,
        "primary_c_vs_d": paired_binary_compare(
            comparisons, left="qwen_txt_acf",
            right="qwen_txt_topic_control"),
        "secondary_c_vs_b": paired_binary_compare(
            comparisons, left="qwen_txt_acf", right="qwen_txt"),
        "actual_gguf_inference": session_factory is None,
        "pretrained_llm_weights_changed": False,
        "frozen_acf_and_sqlite_guarded_against_concurrent_changes": True,
        "raw_questions_answers_files_in_report": False,
        "automated_exact_literal_scoring_only": True,
        "independent_factual_accuracy_proven": False,
        "neural_growth_causally_proven": False,
        "human_heldout_independence_verified": False,
        "automatic_live_policy_promotion": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=(
        "Read-only A/B/C/D offline Qwen trial; D is non-neural matched control"))
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--acf-state", type=Path, required=True)
    p.add_argument("--assets-root", type=Path)
    p.add_argument("--confirm-corpus-rights", action="store_true")
    p.add_argument("--confirm-heldout", action="store_true")
    args = p.parse_args(argv)
    try:
        result = evaluate_abcd(
            args.db, args.audit, args.acf_state,
            assets_root=args.assets_root,
            confirm_rights=args.confirm_corpus_rights,
            confirm_holdout=args.confirm_heldout)
    except (OSError, ValueError, PermissionError, RuntimeError,
            sqlite3.DatabaseError, TimeoutError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
