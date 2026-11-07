"""Reproducible lesion/reconnection benchmark on the actual v0.4 Brain API.

The intact network is used as an *oracle* to quantify activity restoration.
This is NOT proof of restored cognition, independent task accuracy, or an
operational autonomous self-repair policy: an intact oracle is generally not
available at inference time. Every evaluation uses isolated snapshots.
"""
from __future__ import annotations

from dataclasses import replace
import json
import math
import random
from statistics import mean
from typing import Any, Iterator

from .brain import Brain, BrainConfig
from .repair import lesioned_copy, repair_candidate, trial_repair


def _sequence(*, seed: int, steps: int, noisy: bool) -> Iterator[list[float]]:
    rng = random.Random(seed)
    for i in range(steps):
        x = [0.0] * 8
        j = ((i // 4) + seed) % 8
        x[j] = 1.0
        x[(j + 2) % 8] = 1.0
        if noisy:
            x = [min(1.0, max(0.0, v + rng.uniform(-0.10, 0.10))) for v in x]
        yield x


def _activity_error(intact: Brain, candidate: Brain, *, seed: int,
                    steps: int = 96, noisy: bool = False) -> float:
    """Hidden-spike disagreement with intact *oracle* under identical stimuli.

    Both networks are cloned. This proxy is not task-level skill or semantic
    learning; Brain.step modifies synapses during probes, equally in each arm.
    """
    a = Brain.from_dict(intact.to_dict())
    b = Brain.from_dict(candidate.to_dict())
    if len(a.voltages) != len(b.voltages):
        raise ValueError('comparison requires matching neuron counts')
    mismatch = 0
    comparisons = 0
    width = a.config.input_size
    for stimulus in _sequence(seed=seed, steps=steps, noisy=noisy):
        spikes_a = a.step(stimulus).spikes
        spikes_b = b.step(stimulus).spikes
        mismatch += sum(u != v for u, v in zip(spikes_a[width:], spikes_b[width:]))
        comparisons += len(spikes_a) - width
    return mismatch / comparisons


def lesion_repair_benchmark(*, seeds: int = 10, fraction: float = 0.5,
                            proposed_weight: float = 0.8) -> dict[str, Any]:
    """Compare untreated lesion, naive reconnection, validated reconnection.

    The validation signal comes from an intact oracle, making this an upper-
    bound controlled structural assay rather than an autonomous repair agent.
    A disjoint noisy probe is used for reporting only, not candidate selection.
    """
    if type(seeds) is not int or not 2 <= seeds <= 100:
        raise ValueError('seeds must be an integer from 2 to 100')
    if type(fraction) not in (int, float) or not math.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError('fraction must be finite and in [0,1]')
    if type(proposed_weight) not in (int, float) or not math.isfinite(proposed_weight) or not 0 < proposed_weight <= 1.5:
        raise ValueError('proposed_weight must be finite and in (0,1.5]')
    rows: list[dict[str, Any]] = []
    for seed in range(1, seeds + 1):
        config = replace(BrainConfig(), growth_enabled=False)
        healthy = Brain(config, seed=seed)
        for sample in _sequence(seed=seed, steps=160, noisy=False):
            healthy.step(sample)
        baseline_snapshot = healthy.to_dict()
        injured = lesioned_copy(healthy, fraction=fraction, seed=seed * 991)
        naive, added = repair_candidate(injured, max_new_synapses=16,
                                        weight=proposed_weight)
        validate = lambda brain: _activity_error(healthy, brain,
                            seed=10000 + seed, steps=72, noisy=False)
        gated, result = trial_repair(injured, validate, max_new_synapses=16,
                                    candidate_weight=proposed_weight, min_improvement=0)
        if healthy.to_dict() != baseline_snapshot:
            raise AssertionError('evaluation mutated the intact oracle')
        # Never make acceptance decisions on this separately seeded/noisy probe.
        holdout_seed = 20000 + seed
        row = {
            'seed': seed,
            'removed_synapses': len(healthy.synapses) - len(injured.synapses),
            'proposed_synapses': added,
            'accepted': result.accepted,
            'validation_untreated_error': result.before_error,
            'validation_proposed_error': result.candidate_error,
            'holdout_untreated_error': _activity_error(healthy, injured, seed=holdout_seed,
                                                       steps=96, noisy=True),
            'holdout_naive_error': _activity_error(healthy, naive, seed=holdout_seed,
                                                   steps=96, noisy=True),
            'holdout_gated_error': _activity_error(healthy, gated, seed=holdout_seed,
                                                   steps=96, noisy=True),
        }
        rows.append(row)
    names = ('holdout_untreated_error', 'holdout_naive_error', 'holdout_gated_error')
    return {
        'protocol': 'intact_oracle_synapse_lesion_activity_v1',
        'settings': {'seeds': seeds, 'fraction': fraction,
                     'candidate_weight': proposed_weight, 'train_steps': 160,
                     'validation_steps': 72, 'holdout_steps': 96,
                     'holdout_noise_amplitude': 0.10},
        'mean_metrics': {name: mean(row[name] for row in rows) for name in names},
        'accepted_repairs': sum(row['accepted'] for row in rows),
        'paired_results': rows,
        'limitations': (
            'This scores hidden-spike agreement with an inaccessible intact oracle; '
            'not the performance of a learned external task or autonomous repair. '
            'Validation and holdout use the same simple synthetic pattern family; '
            'the holdout uses independent random perturbations. Neural plasticity '
            'remains active in evaluation clones; no equal-compute guarantee. '
            'Refusal to apply harmful proposals is not proof of repair.'
        ),
    }




def fingerprint_repair_benchmark(*, seeds: int = 10,
                                 fraction: float = 0.5) -> dict[str, Any]:
    """Test restoring previous neural *activity* using a private old fingerprint.

    Uses a stored validation fingerprint collected *before* injuring the
    network. Only the independent holdout scorer retains a healthy reference.
    No semantic knowledge, true behavior skill or autonomous recovery inferred.
    """
    from .fingerprint_repair import record_fingerprint, propose_fingerprint_repair

    if type(seeds) is not int or not 2 <= seeds <= 100:
        raise ValueError('seeds must be in [2, 100]')
    if type(fraction) not in (float, int) or not math.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError('fraction must be finite in [0, 1]')
    rows: list[dict[str, Any]] = []
    for seed in range(1, seeds + 1):
        config = replace(BrainConfig(), growth_enabled=False)
        healthy = Brain(config, seed=seed)
        for sample in _sequence(seed=seed, steps=160, noisy=False):
            healthy.step(sample)
        healthy_snapshot = healthy.to_dict()
        # The signature is a compact old activity memory, not the source
        # topology. The repair function is never given the healthy brain.
        signature = record_fingerprint(
            healthy, list(_sequence(seed=10000 + seed, steps=72, noisy=False))
        )
        injured = lesioned_copy(healthy, fraction=fraction, seed=seed * 991)
        injured_snapshot = injured.to_dict()
        proposed, trial = propose_fingerprint_repair(
            injured, signature, max_new_synapses=6)
        if healthy.to_dict() != healthy_snapshot or injured.to_dict() != injured_snapshot:
            raise AssertionError('functional repair leaked into original state')
        holdout_seed = 20000 + seed
        rows.append({
            'seed': seed,
            'removed_synapses': len(healthy.synapses) - len(injured.synapses),
            'proposed_synapses': trial.accepted_connections,
            'validation_before_error': trial.initial_error,
            'validation_after_error': trial.final_validation_error,
            'holdout_injured_error': _activity_error(
                healthy, injured, seed=holdout_seed, steps=96, noisy=True),
            'holdout_repaired_error': _activity_error(
                healthy, proposed, seed=holdout_seed, steps=96, noisy=True),
        })
    return {
        'protocol': 'preinjury_activity_fingerprint_repair_v1',
        'settings': {'seeds': seeds, 'fraction': fraction,
                     'train_steps': 160, 'validation_steps': 72,
                     'holdout_steps': 96, 'holdout_noise_amplitude': 0.10,
                     'proposed_synapse_budget': 6},
        'mean_metrics': {
            'holdout_injured_error': mean(row['holdout_injured_error'] for row in rows),
            'holdout_repaired_error': mean(row['holdout_repaired_error'] for row in rows),
            'synapses_added': mean(row['proposed_synapses'] for row in rows),
        },
        'improved_holdout_seeds': sum(row['holdout_repaired_error'] <
                                      row['holdout_injured_error'] for row in rows),
        'worsened_holdout_seeds': sum(row['holdout_repaired_error'] >
                                      row['holdout_injured_error'] for row in rows),
        'paired_results': rows,
        'limitations': (
            'This is compensation of hidden spike response on a narrow toy '
            'sequence, not restoration of learned task accuracy or memories. '
            'A healthy activity fingerprint is pre-recorded before lesion and '
            'assumed intact; without it this method cannot infer the target. '
            'Final comparison uses the intact brain only as an evaluation oracle. '
            'Validation and independent noisy holdout come from one related '
            'synthetic pattern family; not generalization or cognition evidence.'
        ),
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Synthetic lesion/recovery experiments')
    parser.add_argument('--fingerprint', action='store_true', help='use stored pre-injury activity')
    parser.add_argument('--seeds', type=int, default=10)
    parser.add_argument('--fraction', type=float, default=0.5)
    args = parser.parse_args()
    result = (fingerprint_repair_benchmark(seeds=args.seeds, fraction=args.fraction)
              if args.fingerprint else lesion_repair_benchmark(seeds=args.seeds, fraction=args.fraction))
    print(json.dumps(result, indent=2, sort_keys=True))
