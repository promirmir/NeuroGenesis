"""Rights-gated local knowledge -> actual Foundation Brain gradient training pilot.

Training happens ONLY after explicit per-source rights approvals and invocation
with --confirm-corpus-rights. It never runs on web fetch, chat or GUI startup.
Documents are split before train/evaluation to prevent overlapping windows.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import time
import threading
from typing import Any, Callable

from .foundation import FoundationBrain, FoundationConfig, torch
from .foundation_train import evaluate_holdout
from .memory import ExperienceMemory

MAX_DOCUMENT_BYTES = 6000 * 4
MAX_TRAINING_BYTES = 1_000_000


def markov_holdout_cross_entropy(training: list[bytes], holdout: bytes,
                                  *, sequence: int | None = None) -> float:
    """Laplace-smoothed byte baseline, matching heldout window boundaries."""
    context: Counter[int] = Counter()
    pairs: Counter[tuple[int, int]] = Counter()
    for document in training:
        for a, b in zip(document[:-1], document[1:]):
            context[a] += 1
            pairs[(a, b)] += 1
    if sequence is None:
        windows = [holdout]
    else:
        if type(sequence) is not int or sequence < 2:
            raise ValueError("invalid baseline evaluation sequence")
        windows = [holdout[start:start + sequence]
                   for start in range(0, len(holdout) - 1, sequence)]
    scored = [(-math.log((pairs[(a, b)] + 1) / (context[a] + 256)))
              for window in windows for a, b in zip(window[:-1], window[1:])]
    if not scored:
        raise ValueError("held-out document too short")
    return sum(scored) / len(scored)


def train_approved_knowledge(db_path: str | Path, output: str | Path, *,
                             confirm_rights: bool = False, steps: int = 20,
                             sequence: int = 32, batch: int = 2,
                             hidden: int = 32, seed: int = 1234,
                             device: str = "cpu",
                             resume_from: str | Path | None = None,
                             trust_resume: bool = False,
                             cancel_event: threading.Event | None = None,
                             on_progress: Callable[[int, dict[str, float]], None] | None = None
                             ) -> dict[str, Any]:
    """Train a fresh or explicitly resumed *candidate*, never promote active chat.

    A resumed run restores trained weights, but deliberately starts a fresh
    AdamW optimizer. Optimizer state is not in the numerical checkpoint.
    This is not a byte-identical continuation of one uninterrupted job.
    """
    if confirm_rights is not True:
        raise PermissionError("explicit corpus-rights confirmation required")
    if torch is None:
        raise RuntimeError("install the optional PyTorch foundation dependency")
    if (type(steps) is not int or not 1 <= steps <= 1000
            or type(sequence) is not int or not 16 <= sequence <= 128
            or type(batch) is not int or not 1 <= batch <= 8
            or type(hidden) is not int or not 16 <= hidden <= 256
            or type(seed) is not int or not 0 <= seed <= 2**32 - 1
            or device not in ("cpu", "cuda")):
        raise ValueError("invalid bounded model training configuration")
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA unavailable; explicit GPU training refused")
    destination = Path(output)
    if destination.suffix.lower() not in (".pt", ".pth"):
        raise ValueError("checkpoint must use private .pt or .pth extension")
    if destination.is_symlink() or destination.exists():
        raise ValueError("new candidate output path must not already exist")
    if destination.resolve() == Path(db_path).resolve():
        raise ValueError("checkpoint cannot overwrite local SQLite memory")
    if resume_from is not None and trust_resume is not True:
        raise PermissionError("resume requires explicit trust of LOCAL numerical checkpoint")
    if cancel_event is not None and not isinstance(cancel_event, threading.Event):
        raise ValueError("cancel_event must be a threading.Event")
    if on_progress is not None and not callable(on_progress):
        raise ValueError("on_progress must be callable")
    memory = ExperienceMemory(db_path)
    docs = memory.approved_training_documents()
    if len(docs) < 3:
        raise ValueError("at least three different latest, explicitly approved source URLs required")
    # Distinct URLs alone are not sufficient: identical content on mirror
    # sites would leak evaluation bytes into training.
    if len({doc["sha256"] for doc in docs}) != len(docs):
        raise ValueError("duplicate document hashes across sources invalidate the holdout")
    encoded = [doc["text"].encode("utf-8") for doc in docs]
    if any(len(doc) < sequence * 2 or len(doc) > MAX_DOCUMENT_BYTES for doc in encoded):
        raise ValueError("approved documents too short/large for a safe disjoint evaluation")
    if sum(map(len, encoded)) > MAX_TRAINING_BYTES:
        raise ValueError("approved training collection exceeds one MiB")
    # Stable URL order: last document is a completely unseen evaluation set.
    # Two or more other sources contribute sequences; none crosses document
    # boundaries or includes tokens from the held-out document.
    training = encoded[:-1]
    holdout = encoded[-1]
    cfg = FoundationConfig(hidden_size=hidden, fast_layers=1, slow_layers=1,
                           max_sequence=sequence, chunk_size=8)
    torch.manual_seed(seed)
    initial_training_steps = 0
    resume_sha256: str | None = None
    if resume_from is not None:
        prior_path = Path(resume_from)
        if (prior_path.suffix.lower() not in (".pt", ".pth")
                or prior_path.is_symlink() or not prior_path.is_file()
                or prior_path.resolve() == destination.resolve()):
            raise ValueError("resume source must be a distinct, existing local .pt/.pth")
        if cancel_event is not None and cancel_event.is_set():
            raise InterruptedError("training cancelled before reading previous weights")
        model, initial_training_steps = FoundationBrain.load_checkpoint(
            prior_path, device=device)
        if model.config != cfg or initial_training_steps < 1:
            raise ValueError("resume requires a trained checkpoint with identical architecture")
        digest = hashlib.sha256()
        with prior_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        resume_sha256 = digest.hexdigest()
    else:
        model = FoundationBrain(cfg).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002)
    before = evaluate_holdout(model, holdout, sequence=sequence, device=device)
    baseline_ce = markov_holdout_cross_entropy(training, holdout, sequence=sequence)
    generator = torch.Generator(device="cpu").manual_seed(seed)
    # No held-out document is ever used for gradient updates.
    train_tensors = [torch.tensor(list(x), dtype=torch.long) for x in training]
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    start_time = time.perf_counter()
    last = {}
    for step in range(steps):
        if cancel_event is not None and cancel_event.is_set():
            raise InterruptedError("operator cancelled training; candidate not written")
        samples = []
        for _ in range(batch):
            doc_index = int(torch.randint(0, len(training), (1,), generator=generator).item())
            source = train_tensors[doc_index]
            offset = int(torch.randint(0, len(source) - sequence + 1,
                                       (1,), generator=generator).item())
            samples.append(source[offset:offset + sequence])
        last = model.train_batch(torch.stack(samples).to(device), optimizer)
        if on_progress is not None:
            on_progress(step + 1, last)
    if cancel_event is not None and cancel_event.is_set():
        raise InterruptedError("operator cancelled training; candidate not written")
    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = max(time.perf_counter() - start_time, 1e-9)
    after = evaluate_holdout(model, holdout, sequence=sequence, device=device)
    if not all(math.isfinite(v) for v in (
            before["next_byte_ce_nats"], after["next_byte_ce_nats"],
            baseline_ce, last["loss"])):
        raise ValueError("nonfinite model/holdout metrics; checkpoint not saved")
    if cancel_event is not None and cancel_event.is_set():
        raise InterruptedError("operator cancelled before checkpoint write")
    if destination.exists() or destination.is_symlink():
        raise ValueError("candidate output appeared during training; refusing overwrite")
    model.save_checkpoint(destination, training_steps=initial_training_steps + steps)
    return {
        "status": "candidate_self_supervised_weights_trained",
        "device": device,
        "parameter_count": model.parameter_count,
        "trained_documents": len(training),
        "holdout_documents": 1,
        "holdout_source_sha256": docs[-1]["sha256"],
        "holdout_split": "entire_distinct_latest_document_no_gradient_access",
        "source_rights": "operator_asserted_per_source_not_independently_verified",
        "training_steps": steps,
        "checkpoint_total_training_steps": initial_training_steps + steps,
        "resumed_from_trusted_local_checkpoint": resume_from is not None,
        "resumed_checkpoint_sha256": resume_sha256,
        "optimizer_state_resumed": False,
        "train_last_loss": last["loss"],
        "heldout_next_byte_ce_before": before["next_byte_ce_nats"],
        "heldout_next_byte_ce_after": after["next_byte_ce_nats"],
        "heldout_markov_ce_nats": baseline_ce,
        "heldout_improved": after["next_byte_ce_nats"] < before["next_byte_ce_nats"],
        "beats_markov_baseline": after["next_byte_ce_nats"] < baseline_ce,
        "holdout_scored_transitions": after["scored_transitions"],
        "train_steps_per_second": steps / elapsed,
        "gpu_peak_allocated_bytes": (
            int(torch.cuda.max_memory_allocated()) if device == "cuda" else None),
        "checkpoint_candidate_written": True,
        "ready_for_semantic_chat": False,
        "internet_used_by_trainer": False,
        "automatically_deployed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local rights-approved evidence to Foundation Brain pilot")
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--sequence", type=int, default=32)
    parser.add_argument("--batch", type=int, default=2)
    parser.add_argument("--hidden", type=int, default=32)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--resume-from", type=Path,
                        help="Existing trusted local numerical weights (creates a new output)")
    parser.add_argument("--confirm-trusted-resume", action="store_true")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args(argv)
    try:
        result = train_approved_knowledge(
            args.db, args.output, confirm_rights=args.confirm_corpus_rights,
            steps=args.steps, sequence=args.sequence, batch=args.batch,
            hidden=args.hidden, seed=args.seed, device=args.device,
            resume_from=args.resume_from, trust_resume=args.confirm_trusted_resume)
    except (ValueError, PermissionError, RuntimeError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
