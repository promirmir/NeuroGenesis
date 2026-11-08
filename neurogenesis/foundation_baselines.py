"""Leakage-controlled byte-level unigram and Markov-1 baselines.

Pure standard library; no network, no neural dependency, no user data logging.
Scores a disjoint chronological holdout using training counts only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

MAX_BYTES = 32 * 1024 * 1024
VOCAB = 256


def evaluate(data: bytes, *, split_fraction: float = 0.9, smoothing: float = 1.0) -> dict:
    if type(data) is not bytes or len(data) < 100:
        raise ValueError("at least 100 corpus bytes required")
    if not (type(split_fraction) is float and 0.5 <= split_fraction <= 0.95):
        raise ValueError("split_fraction must be a float in [0.5, 0.95]")
    if not (type(smoothing) in (float, int) and math.isfinite(smoothing)
            and 0 < smoothing <= 100):
        raise ValueError("smoothing must be finite and positive")
    cut = int(len(data) * split_fraction)
    train, holdout = data[:cut], data[cut:]
    if len(train) < 2 or len(holdout) < 2:
        raise ValueError("insufficient disjoint sequences")
    unigram = Counter(train[1:])
    pairs = Counter(zip(train[:-1], train[1:]))
    preceding = Counter(train[:-1])
    # The first holdout byte has no holdout predecessor: never use a
    # training-to-holdout boundary transition in either model.
    n = len(holdout) - 1
    u_loss = m_loss = 0.0
    for prev, target in zip(holdout[:-1], holdout[1:]):
        p_u = (unigram[target] + smoothing) / (len(train) - 1 + VOCAB * smoothing)
        p_m = (pairs[(prev, target)] + smoothing) / (
            preceding[prev] + VOCAB * smoothing)
        u_loss -= math.log(p_u)
        m_loss -= math.log(p_m)
    return {
        "train_bytes": len(train),
        "holdout_bytes": len(holdout),
        "scored_holdout_transitions": n,
        "unigram_next_byte_ce_nats": u_loss / n,
        "markov1_next_byte_ce_nats": m_loss / n,
        "split": "chronological_disjoint",
        "smoothing": float(smoothing),
        "model": "count_based_no_context_vs_one_byte_context",
        "semantic_understanding": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline held-out byte baselines")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_corpus_rights:
        parser.error("explicit --confirm-corpus-rights is required")
    if not args.input.is_file() or args.input.stat().st_size > MAX_BYTES:
        parser.error("corpus missing or exceeds 32 MiB")
    try:
        result = evaluate(args.input.read_bytes())
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
