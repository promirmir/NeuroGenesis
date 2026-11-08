"""Prospective source-QA acceptance: disjoint audit, uncertainty and abstain baseline.

An additional stricter, explicitly operator-driven gate over the existing
read-only local SQLite QA evaluator. Neither this gate nor a numeric PASS
authorizes model installation, neural reasoning claims, or automatic release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
from typing import Any

from .qa_eval import _read_audit, evaluate_qa


def _question_key(question: str) -> str:
    # Stronger than casefold alone for exact punctuation/whitespace leakage.
    # Semantic paraphrase contamination remains outside this tool's ability.
    return " ".join(re.findall(r"[^\W_]+", question.casefold()))


def wilson_interval(successes: int, trials: int, *, z: float = 1.959963984540054
                    ) -> tuple[float, float]:
    """Two-sided approximate 95% Wilson score interval for Bernoulli rate."""
    if (type(successes) is not int or type(trials) is not int or
            trials < 1 or not 0 <= successes <= trials):
        raise ValueError("invalid binomial successes/trials")
    if not math.isfinite(z) or z <= 0:
        raise ValueError("invalid score interval")
    p = successes / trials
    den = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / den
    margin = (z / den) * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials**2))
    return max(0.0, center - margin), min(1.0, center + margin)


def decide_qa_gate(*, supported_total: int, supported_exact: int,
                   unsupported_total: int, unsupported_abstained: int,
                   min_supported: int = 30, min_unsupported: int = 60,
                   min_recall_lower95: float = 0.70,
                   max_false_citation_upper95: float = 0.05,
                   min_gain_over_abstain_all: float = 0.10
                   ) -> dict[str, Any]:
    """Require quantitative evidence beyond tiny toy-fixture point estimates.

    A pass is a *literal-citation quality gate only*, not factual or
    semantic accuracy. Abstain-all is the transparent trivial baseline.
    """
    if (any(type(x) is not int for x in
            (supported_total, supported_exact, unsupported_total, unsupported_abstained,
             min_supported, min_unsupported)) or
            supported_total < 1 or unsupported_total < 1 or
            min_supported < 1 or min_unsupported < 1 or
            not 0 <= supported_exact <= supported_total or
            not 0 <= unsupported_abstained <= unsupported_total):
        raise ValueError("invalid class counts or thresholds")
    tolerances = (min_recall_lower95, max_false_citation_upper95,
                  min_gain_over_abstain_all)
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1
           for v in tolerances):
        raise ValueError("invalid gate fraction threshold")
    false_citations = unsupported_total - unsupported_abstained
    recall_l, recall_u = wilson_interval(supported_exact, supported_total)
    fp_l, fp_u = wilson_interval(false_citations, unsupported_total)
    total = supported_total + unsupported_total
    raw_accuracy = (supported_exact + unsupported_abstained) / total
    trivial_abstain_accuracy = unsupported_total / total
    gain = raw_accuracy - trivial_abstain_accuracy
    sufficient = supported_total >= min_supported and unsupported_total >= min_unsupported
    passes = (sufficient and recall_l >= min_recall_lower95
              and fp_u <= max_false_citation_upper95
              and gain >= min_gain_over_abstain_all)
    return {
        "supported_count": supported_total,
        "unsupported_count": unsupported_total,
        "supported_correct_literal": supported_exact,
        "unsupported_false_citations": false_citations,
        "supported_exact_quote_recall": supported_exact / supported_total,
        "supported_recall_wilson95_lower": recall_l,
        "supported_recall_wilson95_upper": recall_u,
        "unsupported_false_citation_rate": false_citations / unsupported_total,
        "unsupported_false_citation_wilson95_lower": fp_l,
        "unsupported_false_citation_wilson95_upper": fp_u,
        "strict_fixture_accuracy": raw_accuracy,
        "abstain_all_baseline_accuracy": trivial_abstain_accuracy,
        "gain_vs_abstain_all": gain,
        "sufficient_class_sample": sufficient,
        "thresholds": {
            "min_supported": min_supported, "min_unsupported": min_unsupported,
            "min_recall_wilson95_lower": min_recall_lower95,
            "max_false_citation_wilson95_upper": max_false_citation_upper95,
            "min_gain_over_abstain_all": min_gain_over_abstain_all,
        },
        "passes_numeric_prospective_gate": passes,
        "ready_for_semantic_chat": False,
        "independently_fact_checked": False,
        "automatically_promoted": False,
    }


def run_prospective_gate(db: str | Path, development_audit: str | Path,
                         prospective_audit: str | Path, *,
                         confirm_rights: bool = False,
                         confirm_untouched: bool = False,
                         min_supported: int = 30, min_unsupported: int = 60,
                         min_recall_lower95: float = 0.70,
                         max_false_citation_upper95: float = 0.05,
                         min_gain_over_abstain_all: float = 0.10
                         ) -> dict[str, Any]:
    """Check question overlap before read-only prospective scoring.

    No raw questions, quotes, URLs or local paths leave this aggregate report.
    Dataset independence beyond exact normalized question comparison is NOT
    verifiable. Operator must protect and avoid tuning against prospective set.
    """
    if confirm_rights is not True or confirm_untouched is not True:
        raise PermissionError("explicit audit rights and previously unused audit confirmation required")
    previous, previous_sha = _read_audit(Path(development_audit))
    current, current_sha = _read_audit(Path(prospective_audit))
    if previous_sha == current_sha:
        raise ValueError("prospective audit is identical to development audit")
    previous_keys = {_question_key(r["question"]) for r in previous}
    current_keys = [_question_key(r["question"]) for r in current]
    if len(set(current_keys)) != len(current_keys):
        raise ValueError("duplicate normalized prospective questions")
    overlap = previous_keys.intersection(current_keys)
    if overlap:
        raise ValueError("development and prospective questions overlap")
    supported = sum(int(x["answerable"]) for x in current)
    unsupported = len(current) - supported
    # Reject insufficient datasets before opening or scoring SQLite.
    if supported < min_supported or unsupported < min_unsupported:
        raise ValueError("insufficient independent prospective cases for minimum class sizes")
    result = evaluate_qa(
        db, prospective_audit, confirm_rights=True, confirm_heldout=True)
    abstained = round(result["unsupported_abstention_rate"] * unsupported)
    decision = decide_qa_gate(
        supported_total=supported,
        supported_exact=result["correct_literal_citations"],
        unsupported_total=unsupported,
        unsupported_abstained=abstained,
        min_supported=min_supported, min_unsupported=min_unsupported,
        min_recall_lower95=min_recall_lower95,
        max_false_citation_upper95=max_false_citation_upper95,
        min_gain_over_abstain_all=min_gain_over_abstain_all)
    return {
        "task": "prospective_literal_source_attribution_quality_not_semantic_answering",
        "development_audit_sha256": previous_sha,
        "prospective_audit_sha256": current_sha,
        "identical_or_exact_normalized_question_overlap": False,
        "prospective_independence_verified": False,
        "heldout_status": "operator_asserted; paraphrase and training leakage not detectable",
        "source_quote_truth_verified": False,
        "retrieval_latency_p95_ms": result["latency_p95_ms"],
        "internet_used": False,
        "sqlite_modified": False,
        "raw_questions_in_report": False,
        **decision,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prospective, uncertainty-aware local citation QA acceptance; no model promotion")
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--development-audit", required=True, type=Path)
    parser.add_argument("--prospective-audit", required=True, type=Path)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--confirm-untouched", action="store_true")
    parser.add_argument("--min-supported", type=int, default=30)
    parser.add_argument("--min-unsupported", type=int, default=60)
    args = parser.parse_args(argv)
    try:
        report = run_prospective_gate(
            args.db, args.development_audit, args.prospective_audit,
            confirm_rights=args.confirm_corpus_rights,
            confirm_untouched=args.confirm_untouched,
            min_supported=args.min_supported,
            min_unsupported=args.min_unsupported)
    except (ValueError, PermissionError, OSError, sqlite3.DatabaseError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
