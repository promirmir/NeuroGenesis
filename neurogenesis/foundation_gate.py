"""Offline A/B model candidate audit with separate old-skill and new-task texts.

This is a numerical, document-separated *byte prediction* gate, NOT proof of
language understanding, factual grounding or safe model deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .foundation import FoundationBrain, torch
from .foundation_train import evaluate_holdout


MAX_AUDIT_BYTES = 64 * 1024


def decide_retention(*, incumbent_old_ce: float, candidate_old_ce: float,
                     incumbent_new_ce: float, candidate_new_ce: float,
                     max_old_regression: float = 0.05,
                     min_new_improvement: float = 0.01) -> dict[str, Any]:
    """Pure rule: a candidate needs new-task improvement WITHOUT forgetting.

    Returns an objective numeric decision only. Passing does not authorize
    automatic deployment or establish semantic answer quality.
    """
    scores = (incumbent_old_ce, candidate_old_ce, incumbent_new_ce, candidate_new_ce)
    if any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in scores):
        raise ValueError("all audit CE values must be finite and positive")
    if (type(max_old_regression) not in (int, float)
            or not 0 <= max_old_regression <= 0.5
            or type(min_new_improvement) not in (int, float)
            or not 0 <= min_new_improvement <= 0.5):
        raise ValueError("audit numeric tolerances out of bounds")
    old_regression_fraction = (candidate_old_ce - incumbent_old_ce) / incumbent_old_ce
    new_improvement_fraction = (incumbent_new_ce - candidate_new_ce) / incumbent_new_ce
    retained = old_regression_fraction <= max_old_regression
    improved = new_improvement_fraction >= min_new_improvement and candidate_new_ce < incumbent_new_ce
    return {
        "old_skill_regression_fraction": old_regression_fraction,
        "new_task_improvement_fraction": new_improvement_fraction,
        "old_skill_retained": retained,
        "new_task_improved": improved,
        "passes_numeric_retention_gate": retained and improved,
        "operator_thresholds": {"max_old_regression": max_old_regression,
                                "min_new_improvement": min_new_improvement},
        "ready_for_semantic_chat": False,
        "automatically_promoted": False,
    }


def _local_data(path: str | Path, *, minimum: int) -> tuple[bytes, str]:
    target = Path(path)
    if (target.suffix.lower() not in (".txt", ".utf8")
            or target.is_symlink() or not target.is_file()):
        raise ValueError("audit corpus must be a regular local .txt/.utf8 file")
    size = target.stat().st_size
    if not minimum <= size <= MAX_AUDIT_BYTES:
        raise ValueError("audit corpus size outside bounded development limits")
    # Text from the operator is inert data, not an instruction. Reject invalid
    # Unicode rather than disguising binary inputs as natural-language data.
    raw = target.read_bytes()
    raw.decode("utf-8", errors="strict")
    return raw, hashlib.sha256(raw).hexdigest()


def audit_candidate(incumbent_path: str | Path, candidate_path: str | Path,
                    old_audit_text: str | Path, new_audit_text: str | Path, *,
                    trust_checkpoints: bool = False, confirm_corpus_rights: bool = False,
                    sequence: int = 32, device: str = "cpu",
                    max_old_regression: float = 0.05,
                    min_new_improvement: float = 0.01) -> dict[str, Any]:
    """Evaluate BOTH checkpoints on exactly the same two distinct holdout files.

    This function does not train, write checkpoint files or change SQLite.
    It cannot prove that these datasets were never used to tune the models.
    """
    if trust_checkpoints is not True or confirm_corpus_rights is not True:
        raise PermissionError("trusted local checkpoints AND audit corpus rights must be confirmed")
    if torch is None:
        raise RuntimeError("actual PyTorch foundation dependency required")
    if type(sequence) is not int or not 8 <= sequence <= 128:
        raise ValueError("audit sequence must be in [8, 128]")
    if device not in ("cpu", "cuda"):
        raise ValueError("audit device must be CPU or CUDA")
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA requested but unavailable")

    incumbent = Path(incumbent_path)
    candidate = Path(candidate_path)
    for path in (incumbent, candidate):
        if path.suffix.lower() not in (".pt", ".pth") or path.is_symlink() or not path.is_file():
            raise ValueError("checkpoints must be existing, regular local .pt/.pth files")
    if incumbent.resolve() == candidate.resolve():
        raise ValueError("incumbent and candidate checkpoints must be separate")
    old_raw, old_hash = _local_data(old_audit_text, minimum=sequence * 2)
    new_raw, new_hash = _local_data(new_audit_text, minimum=sequence * 2)
    if old_hash == new_hash:
        raise ValueError("old and new audit texts must not be identical")

    current_model, current_steps = FoundationBrain.load_checkpoint(incumbent, device=device)
    trial_model, trial_steps = FoundationBrain.load_checkpoint(candidate, device=device)
    if current_steps < 1 or trial_steps < 1:
        raise ValueError("both checkpoints must contain trained weights")
    if current_model.config != trial_model.config:
        raise ValueError("architecture/config mismatch invalidates paired comparison")
    if sequence > current_model.config.max_sequence:
        raise ValueError("audit sequence exceeds checkpoint context")
    if torch.cuda.is_available() and device == "cuda":
        torch.cuda.synchronize()
    current_model.eval()
    trial_model.eval()
    with torch.inference_mode():
        current_old = evaluate_holdout(current_model, old_raw, sequence=sequence, device=device)
        candidate_old = evaluate_holdout(trial_model, old_raw, sequence=sequence, device=device)
        current_new = evaluate_holdout(current_model, new_raw, sequence=sequence, device=device)
        candidate_new = evaluate_holdout(trial_model, new_raw, sequence=sequence, device=device)
    decision = decide_retention(
        incumbent_old_ce=current_old["next_byte_ce_nats"],
        candidate_old_ce=candidate_old["next_byte_ce_nats"],
        incumbent_new_ce=current_new["next_byte_ce_nats"],
        candidate_new_ce=candidate_new["next_byte_ce_nats"],
        max_old_regression=max_old_regression,
        min_new_improvement=min_new_improvement)
    return {
        "status": "offline_paired_checkpoint_retention_audit",
        "task": "byte_level_next_symbol_cross_entropy_not_qa",
        "incumbent_steps": current_steps,
        "candidate_steps": trial_steps,
        "parameter_count_each": current_model.parameter_count,
        "device": device,
        "sequence": sequence,
        "old_audit_sha256": old_hash,
        "new_audit_sha256": new_hash,
        "old_audit_transitions": current_old["scored_transitions"],
        "new_audit_transitions": current_new["scored_transitions"],
        "incumbent_old_ce_nats": current_old["next_byte_ce_nats"],
        "candidate_old_ce_nats": candidate_old["next_byte_ce_nats"],
        "incumbent_new_ce_nats": current_new["next_byte_ce_nats"],
        "candidate_new_ce_nats": candidate_new["next_byte_ce_nats"],
        "audit_holdout_independence": "operator_asserted_not_automatically_proven",
        "reliability_caveat": "reused_or_tuned_audit_sets_invalidate_prospective_quality_claims",
        "internet_used": False,
        "checkpoint_files_modified": False,
        **decision,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate old skill and new task on a model candidate without deployment")
    parser.add_argument("--incumbent", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--old-audit", required=True, type=Path)
    parser.add_argument("--new-audit", required=True, type=Path)
    parser.add_argument("--confirm-trusted-checkpoints", action="store_true")
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--sequence", type=int, default=32)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--max-old-regression", type=float, default=0.05)
    parser.add_argument("--min-new-improvement", type=float, default=0.01)
    args = parser.parse_args(argv)
    try:
        report = audit_candidate(
            args.incumbent, args.candidate, args.old_audit, args.new_audit,
            trust_checkpoints=args.confirm_trusted_checkpoints,
            confirm_corpus_rights=args.confirm_corpus_rights,
            sequence=args.sequence, device=args.device,
            max_old_regression=args.max_old_regression,
            min_new_improvement=args.min_new_improvement)
    except (ValueError, OSError, RuntimeError, PermissionError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
