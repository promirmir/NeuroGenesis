"""Reproducible, non-cherry-picked ACF prequential benchmark.

Protocol: A -> B -> A, causal loss computed before updates, matched seeded
grow/fixed LIF, persistence and constant baselines. All segment scores,
negative deltas and measured resource counts are reported. No fabricated
training improvement and no semantic intelligence conclusions.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any

from .acf import AdaptiveCognitiveFabric, ROUTES, WARMUP
from .brain import BrainConfig


def experiment(*, steps_per_phase: int = 96, seed: int = 7) -> dict[str, Any]:
    if type(steps_per_phase) is not int or not 48 <= steps_per_phase <= 500:
        raise ValueError("Expected 48–500 observations per experiment phase.")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Seed must be an unsigned 32-bit integer.")
    model = AdaptiveCognitiveFabric(
        config=BrainConfig(max_neurons=96, max_synapses=512,
                           growth_interval=5, novelty_threshold=0.15),
        seed=seed, learning_rate=0.18)
    rng = random.Random(seed + 713)
    stages = []
    for phase in ("A", "B", "return_A"):
        errors: dict[str, list[float]] = {route: [] for route in ROUTES}
        selected_errors: list[float] = []
        decisions: dict[str, int] = {route: 0 for route in ROUTES}
        for t in range(steps_per_phase):
            x = [0.0] * model.width
            p = t % 2
            pair = 2 if phase != "B" else 4
            x[p], x[p + pair] = 1.0, 1.0
            sample = [max(0.0, min(1.0, v + rng.uniform(-0.03, 0.03)))
                      for v in x]
            point = model.observe(sample)
            if point.last_error is not None:
                for name in ROUTES:
                    errors[name].append(model.losses[name][-1])
                selected_errors.append(point.last_error)
                decisions[point.selected_route] += 1
        def avg(values):
            return round(sum(values) / len(values), 7) if values else None
        stages.append({
            "stage": phase,
            "observations": steps_per_phase,
            "prequential_mean_mse": {name: avg(values)
                                     for name, values in errors.items()},
            "selected_router_prequential_mean_mse": avg(selected_errors),
            "selected_route_counts": decisions,
            "adaptive_neurons": len(model.adaptive.brain.voltages),
            "fixed_neurons": len(model.fixed.brain.voltages),
            "adaptive_synapses": len(model.adaptive.brain.synapses),
            "fixed_synapses": len(model.fixed.brain.synapses),
        })
    after = model.self_model()
    last = stages[-1]["prequential_mean_mse"]
    gain = round(last["fixed"] - last["adaptive"], 7)
    return {
        "protocol": "acf_A_B_return_A_prequential_v1",
        "seed": seed,
        "steps_per_phase": steps_per_phase,
        "stages": stages,
        "structural_growth_observed": (
            after["adaptive_structure"]["total_grown"] > 0
            and after["fixed_structure"]["total_grown"] == 0),
        "adaptive_minus_fixed_return_mse": round(-gain, 7),
        "adaptive_gain_vs_fixed_return_mse": gain,
        "adaptive_better_than_fixed_on_return": gain > 0.0005,
        "after": after,
        "limitations": (
            "Small synthetic eight-channel sequence with online, causal "
            "prediction. All models see the same examples. "
            "No evidence of linguistic understanding, generalization to open "
            "world tasks, calibrated uncertainty, AGI, or biological consciousness. "
            "Growing topology is not presumed better than the fixed control."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ACF causal multi-phase structural-plasticity research benchmark")
    parser.add_argument("--steps-per-phase", type=int, default=96)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)
    try:
        result = experiment(steps_per_phase=args.steps_per_phase, seed=args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
