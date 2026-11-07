"""Task-level skill retention assay for memory-guided neural repair.

This evaluates an actual learned next-sensory-step prediction readout with
intact, lesioned and repaired spiking substrates. The comparison is a small
synthetic task, *not* evidence of general intelligence or semantic recovery.

The intervention is chosen using a pre-injury activity fingerprint only;
actual next-step targets from the holdout sets are NEVER supplied to repair.
All evaluation arms use independent state clones and a frozen linear readout.
"""

from __future__ import annotations

from dataclasses import replace
import argparse
import json
import math
import random
from statistics import mean
from typing import Any

from .brain import Brain, BrainConfig
from .controls import OnlineMarkovBaseline, constant_half_mse
from .fingerprint_repair import propose_fingerprint_repair, record_fingerprint
from .predictor import NextInputPredictor
from .repair import lesioned_copy


def _stimuli(*, steps: int, seed: int, noise: float = 0.0,
             distribution: str = 'train') -> list[list[float]]:
    """Two alternating symbolic pattern pairs; OOD uses disjoint channels."""
    if distribution not in {'train', 'unseen_cues'}:
        raise ValueError('unknown stimulus distribution')
    rng = random.Random(seed)
    offset = 4 if distribution == 'unseen_cues' else 0
    data = []
    for t in range(steps):
        cue = offset + (t % 2)
        x = [0.0] * 8
        x[cue] = x[cue + 2] = 1.0
        if noise:
            x = [max(0.0, min(1.0, v + rng.uniform(-noise, noise))) for v in x]
        data.append(x)
    return data


def _score_readout(reference: NextInputPredictor, brain: Brain,
                   samples: list[list[float]]) -> float:
    """Score one independent clone with frozen readout, prequential MSE.

    The original v0.4 ``learn=False`` freezes the readout, *not* STDP;
    we transparently report this limitation in benchmark output.
    """
    trial = NextInputPredictor.from_dict(reference.to_dict())
    trial.brain = Brain.from_dict(brain.to_dict())
    errors = []
    for i, x in enumerate(samples):
        result = trial.step(x, learn=False)
        # Discard one boundary prediction originating in the training stream.
        if i > 0 and result.mse_before_update is not None:
            errors.append(result.mse_before_update)
    return mean(errors)


def _score_markov(reference: OnlineMarkovBaseline,
                  samples: list[list[float]]) -> float:
    # Rebuilding with the frozen learned table prevents test-set training.
    import copy
    trial = copy.deepcopy(reference)
    errors = []
    for i, x in enumerate(samples):
        error = trial.step(x, learn=False)
        if i > 0 and error is not None:
            errors.append(error)
    return mean(errors)


def _bootstrap_interval(diffs: list[float], *, n_bootstrap: int = 2000,
                        seed: int = 739391) -> list[float]:
    rng = random.Random(seed)
    n = len(diffs)
    ranked = sorted(mean(diffs[rng.randrange(n)] for _ in range(n))
                    for _ in range(n_bootstrap))
    return [ranked[int((n_bootstrap - 1) * 0.025)],
            ranked[int((n_bootstrap - 1) * 0.975)]]


def benchmark_skill_recovery(*, seeds: int = 10,
                             fraction: float = 0.5,
                             train_steps: int = 600,
                             probe_steps: int = 96,
                             noise: float = 0.1,
                             repair_budget: int = 6) -> dict[str, Any]:
    """Paired synthetic holdout for *learned prediction*, with nonneural control.

    All groups share the identical pretrained readout. Repair is selected by
    pre-injury neural activity and does not see targets from either holdout.
    No live memory store or original brain is mutated by lesion/repair/eval.
    """
    if type(seeds) is not int or not 2 <= seeds <= 100:
        raise ValueError('seeds must be an integer in [2, 100]')
    if (type(fraction) not in (float, int) or not math.isfinite(fraction)
            or not 0 <= fraction <= 1):
        raise ValueError('fraction must be finite in [0,1]')
    if type(train_steps) is not int or not 64 <= train_steps <= 4096:
        raise ValueError('train_steps must be an integer in [64,4096]')
    if type(probe_steps) is not int or not 16 <= probe_steps <= 512:
        raise ValueError('probe_steps must be an integer in [16,512]')
    if (type(noise) not in (float, int) or not math.isfinite(noise)
            or not 0 <= noise <= 0.5):
        raise ValueError('noise must be finite in [0,0.5]')
    if type(repair_budget) is not int or not 0 <= repair_budget <= 8:
        raise ValueError('repair_budget must be an integer in [0,8]')

    rows = []
    for seed in range(1, seeds + 1):
        cfg = replace(BrainConfig(), growth_enabled=False)
        learner = NextInputPredictor(Brain(cfg, seed=seed))
        markov = OnlineMarkovBaseline(width=cfg.input_size)
        training = _stimuli(steps=train_steps, seed=seed, distribution='train')
        for x in training:
            learner.step(x)
            markov.step(x)
        original_state = learner.to_dict()
        intact = learner.brain
        fingerprint_inputs = _stimuli(steps=72, seed=10000 + seed,
                                     distribution='train')
        fingerprint = record_fingerprint(intact, fingerprint_inputs)
        damaged = lesioned_copy(intact, fraction=fraction, seed=seed * 991)
        damaged_before = damaged.to_dict()
        candidate, repair = propose_fingerprint_repair(
            damaged, fingerprint, max_new_synapses=repair_budget)
        assert learner.to_dict() == original_state, 'evaluation altered healthy learner'
        assert damaged.to_dict() == damaged_before, 'repair altered damaged reference'
        train_holdout = _stimuli(steps=probe_steps + 1, seed=20000 + seed,
                                noise=noise, distribution='train')
        unseen_holdout = _stimuli(steps=probe_steps + 1, seed=30000 + seed,
                                 noise=noise, distribution='unseen_cues')
        conditions = {'intact': intact, 'damaged': damaged, 'repaired': candidate}
        row = {'seed': seed,
               'removed_synapses': len(intact.synapses) - len(damaged.synapses),
               'added_synapses': repair.accepted_connections,
               'fingerprint_error_before': repair.initial_error,
               'fingerprint_error_after': repair.final_validation_error}
        for condition, brain in conditions.items():
            row[f'holdout_{condition}_mse'] = _score_readout(learner, brain, train_holdout)
            row[f'unseen_{condition}_mse'] = _score_readout(learner, brain, unseen_holdout)
        row['holdout_markov_mse'] = _score_markov(markov, train_holdout)
        row['unseen_markov_mse'] = _score_markov(markov, unseen_holdout)
        row['holdout_constant_mse'] = mean(constant_half_mse(x) for x in train_holdout[1:])
        row['unseen_constant_mse'] = mean(constant_half_mse(x) for x in unseen_holdout[1:])
        rows.append(row)

    keys = tuple(k for k in rows[0] if k != 'seed')
    improvements = [r['holdout_damaged_mse'] - r['holdout_repaired_mse'] for r in rows]
    injury = [r['holdout_damaged_mse'] - r['holdout_intact_mse'] for r in rows]
    return {
        'protocol': 'task_level_prediction_recovery_heldout_v1',
        'settings': {'seeds': seeds, 'fraction': fraction,
                     'train_steps': train_steps, 'probe_steps': probe_steps,
                     'noise': noise, 'repair_budget': repair_budget,
                     'validation_fingerprint_steps': 72,
                     'growth_enabled': False},
        'mean_metrics': {k: mean(float(r[k]) for r in rows) for k in keys},
        'mean_prediction_gain_vs_damaged_mse': mean(improvements),
        'paired_bootstrap_95pct_ci': _bootstrap_interval(improvements),
        'improved_seeds': sum(v > 1e-12 for v in improvements),
        'worsened_seeds': sum(v < -1e-12 for v in improvements),
        'damaged_more_than_intact_seeds': sum(v > 1e-12 for v in injury),
        'per_seed': rows,
        'limitations': (
            'Synthetic two-pattern next-sensory-step prediction, not semantics or '
            'general intelligence. Repair has access to an intact pre-injury '
            'neural activity fingerprint, but no test targets or intact topology. '
            'The learned readout is frozen while spiking network plasticity '
            'continues in isolated evaluation clones. Validation and in-'
            'distribution holdout share an alternating pattern family; independent '
            'noise samples are not unseen concepts. Unseen-cues probes are disjoint '
            'sensory channels but do not establish broad transfer. The nonneural '
            'Markov control is not parameter/compute matched. Averages and bootstrap '
            'interval describe only this deterministic seed/task design. '
            'Recovery of prediction error is not restoration of lost memories.'
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', type=int, default=10)
    parser.add_argument('--fraction', type=float, default=0.5)
    parser.add_argument('--train-steps', type=int, default=600)
    parser.add_argument('--probe-steps', type=int, default=96)
    parser.add_argument('--noise', type=float, default=0.1)
    parser.add_argument('--repair-budget', type=int, default=6)
    args = parser.parse_args()
    report = benchmark_skill_recovery(**vars(args))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
