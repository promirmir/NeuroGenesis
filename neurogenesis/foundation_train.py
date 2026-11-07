"""Explicit, local foundation-brain training command. No downloads or crawlers.

Example:
  python -m neurogenesis.foundation_train --input corpus.txt --output brain.pt \
    --confirm-corpus-rights --steps 100 --device auto

This does not install a trained chatbot into the v0.5.6 desktop; the GPU
research model and legacy desktop remain separate until evaluated safely.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .foundation import FoundationBrain, FoundationConfig, torch


MAX_CORPUS_BYTES = 32 * 1024 * 1024


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train local multi-timescale foundation brain")
    parser.add_argument("--input", required=True, type=Path,
                        help="Existing, operator-supplied UTF-8 corpus file")
    parser.add_argument("--output", required=True, type=Path,
                        help="Private atomic foundation checkpoint")
    parser.add_argument("--confirm-corpus-rights", action="store_true",
                        help="I own/have permission to use this corpus locally")
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--sequence", type=int, default=64)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--fast-layers", type=int, default=2)
    parser.add_argument("--slow-layers", type=int, default=1)
    parser.add_argument("--chunk", type=int, default=16)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args(argv)
    if not args.confirm_corpus_rights:
        parser.error("explicit --confirm-corpus-rights is required")
    if torch is None:
        parser.error("PyTorch not installed; use the optional foundation extra")
    if (not 1 <= args.steps <= 100_000 or not 1 <= args.batch <= 32
            or not 0 < args.lr <= 0.1 or not math.isfinite(args.lr)
            or not 0 <= args.seed < 2**32):
        parser.error("invalid bounded training parameters")
    if args.input.resolve() == args.output.resolve():
        parser.error("input and output must not refer to the same file")
    if not args.input.is_file():
        parser.error("corpus file is not present")
    if args.input.stat().st_size > MAX_CORPUS_BYTES:
        parser.error("local corpus exceeds the 32 MiB development limit")
    data = args.input.read_bytes()
    if len(data) < max(100, 12 * (args.sequence + 1)):
        parser.error("corpus too short for disjoint training and validation ranges")
    try:
        config = FoundationConfig(
            hidden_size=args.hidden, fast_layers=args.fast_layers,
            slow_layers=args.slow_layers, chunk_size=args.chunk,
            max_sequence=args.sequence)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA device requested but unavailable")
    device = ("cuda" if torch.cuda.is_available() else "cpu"
              ) if args.device == "auto" else args.device
    torch.manual_seed(args.seed)
    model = FoundationBrain(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    # Contiguous later holdout: never sample training windows across the split.
    # This is a basic chronological split, not genuine OOD language evaluation.
    split = int(len(data) * 0.9)
    train_bytes = torch.tensor(list(data[:split]), dtype=torch.long)
    holdout = torch.tensor(
        list(data[split:split + args.sequence]),
        dtype=torch.long, device=device).unsqueeze(0)
    if split <= args.sequence + 1:
        parser.error("training split too short")
    with torch.no_grad():
        model.eval()
        before = float(model(holdout).token_loss.item())
    generator = torch.Generator(device="cpu").manual_seed(args.seed)
    last = {}
    for _ in range(args.steps):
        starts = torch.randint(
            0, split - args.sequence, (args.batch,),
            generator=generator).tolist()
        sequence = torch.stack(
            [train_bytes[i:i + args.sequence] for i in starts]
        ).to(device)
        last = model.train_batch(sequence, optimizer)
    model.eval()
    with torch.no_grad():
        after = float(model(holdout).token_loss.item())
    if not math.isfinite(after):
        raise ValueError("non-finite held-out loss; checkpoint not saved")
    model.save_checkpoint(args.output, training_steps=args.steps)
    print(json.dumps({
        "status": "trained_local_self_supervised_research_model",
        "parameter_count": model.parameter_count,
        "device": device,
        "steps": args.steps,
        "training_last_batch_loss": last["loss"],
        "heldout_next_byte_ce_before": before,
        "heldout_next_byte_ce_after": after,
        "heldout_kind": "adjacent_contiguous_corpus_segment_not_OOD",
        "context_order_retained": True,
        "pretrained_weights": False,
        "internet_used": False,
        "ready_for_semantic_chat": False,
        "checkpoint_written": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
