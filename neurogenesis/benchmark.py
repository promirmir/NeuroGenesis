"""Deterministic A->B->A continual-learning evaluation with held-out probes.

This is a synthetic prediction benchmark, not evidence of cognition. Probes
freeze the *readout only*, and use independent cloned neural substrates.
"""

from __future__ import annotations

from dataclasses import replace
import math
import random
from statistics import mean
from typing import Any

from .brain import Brain, BrainConfig
from .predictor import NextInputPredictor


def _stimulus(task: str, index: int, *, noise: float = 0.0,
              rng: random.Random | None = None) -> list[float]:
    if task not in ("A", "B"):
        raise ValueError("task must be A or B")
    if not 0 <= noise <= 0.5:
        raise ValueError("noise must be in [0, 0.5]")
    # Phase shared across tasks; B changes the following feature association.
    # Both tasks are deterministic 2-cycle streams before optional noise.
    channels = ((0, 2), (1, 3)) if task == "A" else ((0, 4), (1, 5))
    active = channels[index % 2]
    vector = [0.0] * 8
    for pos in active:
        vector[pos] = 1.0
    if noise:
        if rng is None:
            raise ValueError("noise requires a controlled RNG")
        vector = [min(1.0, max(0.0, value + rng.uniform(-noise, noise)))
                  for value in vector]
    return vector


def _train(learner: NextInputPredictor, task: str, steps: int) -> float:
    losses = []
    for i in range(steps):
        sample = learner.step(_stimulus(task, i))
        if sample.mse_before_update is not None:
            losses.append(sample.mse_before_update)
    return mean(losses[-min(32, len(losses)):])


def _probe(learner: NextInputPredictor, *, seed: int, steps: int,
           noise: float = 0.0) -> float:
    # Test on an isolated copy, so adaptation in the probe never affects training.
    clone = NextInputPredictor.from_dict(learner.to_dict())
    old_weights = [row.copy() for row in clone.weights]
    old_bias = clone.bias.copy()
    rng = random.Random(seed)
    losses = []
    # Skip one transition originating in the previous task: it cannot predict
    # a task switch which is not signalled in the input.
    for i in range(steps + 1):
        x = _stimulus("A", i, noise=noise, rng=rng)
        result = clone.step(x, learn=False)
        if i > 0 and result.mse_before_update is not None:
            losses.append(result.mse_before_update)
    if old_weights != clone.weights or old_bias != clone.bias:
        raise AssertionError("probe unexpectedly changed readout parameters")
    return mean(losses)


def _bootstrap_ci(deltas: list[float], *, seed: int = 104729,
                  replicates: int = 1200) -> list[float]:
    rng = random.Random(seed)
    n = len(deltas)
    means = sorted(mean(deltas[rng.randrange(n)] for _ in range(n))
                   for _ in range(replicates))
    return [means[int(0.025 * (replicates - 1))],
            means[int(0.975 * (replicates - 1))]]


def continual_learning_benchmark(*, seeds: int = 10,
                                 steps_per_phase: int = 160,
                                 probe_steps: int = 64,
                                 noise: float = 0.15) -> dict[str, Any]:
    """Report paired synthetic adaptation/forgetting scores across seeds.

    Same inputs and seeds for both groups. Structural growth changes the
    number of parameters and runtime, so this is *not* compute-matched.
    """
    if type(seeds) is not int or not 2 <= seeds <= 100:
        raise ValueError("seeds must be an integer in [2, 100]")
    if type(steps_per_phase) is not int or not 32 <= steps_per_phase <= 4096:
        raise ValueError("steps_per_phase must be an integer in [32, 4096]")
    if type(probe_steps) is not int or not 8 <= probe_steps <= 512:
        raise ValueError("probe_steps must be an integer in [8, 512]")
    if type(noise) not in (int, float) or not math.isfinite(noise) or not 0 <= noise <= 0.5:
        raise ValueError("noise must be finite in [0, 0.5]")
    reports: dict[str, list[dict[str, float | int]]] = {
        "growth_enabled": [], "fixed_structure": []}
    for seed in range(1, seeds + 1):
        for name, grow in (("growth_enabled", True), ("fixed_structure", False)):
            config = replace(BrainConfig(), growth_enabled=grow)
            learner = NextInputPredictor(Brain(config, seed=seed))
            _train(learner, "A", steps_per_phase)
            before = _probe(learner, seed=seed * 11, steps=probe_steps, noise=noise)
            _train(learner, "B", steps_per_phase)
            after = _probe(learner, seed=seed * 11, steps=probe_steps, noise=noise)
            _train(learner, "A", steps_per_phase)
            recovered = _probe(learner, seed=seed * 11, steps=probe_steps, noise=noise)
            stats = learner.brain.stats()
            reports[name].append({
                "seed": seed,
                "a_before_shift_mse": before,
                "a_after_shift_mse": after,
                "a_after_relearning_mse": recovered,
                "forgetting_delta_mse": after - before,
                "relearning_delta_mse": recovered - after,
                "final_neurons": stats["neurons"],
                "final_synapses": stats["synapses"],
            })
    metrics = ("a_before_shift_mse", "a_after_shift_mse",
               "a_after_relearning_mse", "forgetting_delta_mse",
               "relearning_delta_mse", "final_neurons", "final_synapses")
    averages = {name: {key: mean(float(row[key]) for row in rows)
                       for key in metrics} for name, rows in reports.items()}
    # Paired estimate: equal seeds, same input stream, but unequal compute.
    paired = [float(g["a_after_shift_mse"]) - float(f["a_after_shift_mse"])
              for g, f in zip(reports["growth_enabled"], reports["fixed_structure"])]
    return {
        "protocol": "synthetic_aba_readout_frozen_noisy_probe_v1",
        "settings": {"seeds": seeds, "steps_per_phase": steps_per_phase,
                     "probe_steps": probe_steps, "noise_amplitude": noise,
                     "task_order": "A-B-A"},
        "mean_metrics": averages,
        "paired_growth_minus_fixed_after_shift_mse": mean(paired),
        "paired_bootstrap_95pct_ci": _bootstrap_ci(paired),
        "per_seed": reports,
        "limitations": (
            "Synthetic repeated patterns; held-out probes perturb the same pattern family. "
            "Only the readout is frozen during independent probes; cloned neural "
            "substrate remains plastic. Not parameter/compute-matched, not an unseen-" 
            "concept generalization benchmark, and not consciousness evidence. "
            "Bootstrap interval describes seed variation, not universal performance."
        ),
    }
