"""Controlled, clone-only structural injury and trial repair for v0.4 Brain.

Neural compensation is a falsifiable hypothesis. No source-code rewriting,
no persistence mutation, and no claim that erased experiences can be restored.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Any, Callable


def _clone(brain: Any) -> Any:
    return type(brain).from_dict(brain.to_dict())


def lesioned_copy(brain: Any, *, fraction: float, seed: int) -> Any:
    """Deterministically remove a fraction of synapses from an isolated copy."""
    if type(fraction) not in (int, float) or not math.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError('fraction must be finite in [0,1]')
    if type(seed) is not int or seed < 0:
        raise ValueError('seed must be a nonnegative integer')
    copy = _clone(brain)
    rng = random.Random(seed)
    removed = round(len(copy.synapses) * fraction)
    indices = set(rng.sample(range(len(copy.synapses)), removed))
    copy.synapses = [edge for i, edge in enumerate(copy.synapses) if i not in indices]
    return copy


def repair_candidate(brain: Any, *, max_new_synapses: int = 8,
                     weight: float = 0.4) -> tuple[Any, int]:
    """Generate an alternative structural pathway only to disconnected hidden neurons.

    Does not 'remember' the destroyed edge; the new path is a hypothesis.
    """
    if type(max_new_synapses) is not int or not 0 <= max_new_synapses <= 10000:
        raise ValueError('max_new_synapses must be an integer in [0, 10000]')
    if type(weight) not in (int, float) or not math.isfinite(weight) or not 0 < weight <= brain.config.weight_limit:
        raise ValueError('invalid proposed weight')
    copy = _clone(brain)
    n = len(copy.voltages)
    width = copy.config.input_size
    existing = {(e.pre, e.post) for e in copy.synapses}
    indegree = [0] * n
    for edge in copy.synapses:
        indegree[edge.post] += 1
    limit = min(max_new_synapses, max(0, copy.config.max_synapses - len(copy.synapses)))
    if limit == 0 or n <= width:
        return copy, 0
    if copy.synapses:
        edge_class = type(copy.synapses[0])
    else:
        from .brain import Synapse
        edge_class = Synapse
    candidates = sorted(range(width, n), key=lambda i: (indegree[i], i))
    source_candidates = sorted(range(width), key=lambda i: (-copy.last_stimulus[i], i))
    additions = 0
    for post in candidates:
        if indegree[post] != 0:
            continue
        for pre in source_candidates:
            if (pre, post) in existing:
                continue
            copy.synapses.append(edge_class(pre, post, float(weight)))
            existing.add((pre, post))
            additions += 1
            break
        if additions >= limit:
            break
    return copy, additions


@dataclass(frozen=True)
class RepairTrial:
    accepted: bool
    before_error: float
    candidate_error: float
    new_synapses: int


def trial_repair(brain: Any, evaluate: Callable[[Any], float], *,
                 max_new_synapses: int = 8, min_improvement: float = 0.0,
                 candidate_weight: float = 0.4
                 ) -> tuple[Any, RepairTrial]:
    """Apply a candidate ONLY if a separate validation metric improves.

    Caller must use a held-out evaluation independent from a final test set;
    otherwise the selection could overfit. `evaluate` may advance its copy.
    """
    if type(min_improvement) not in (int, float) or not math.isfinite(min_improvement) or min_improvement < 0:
        raise ValueError('invalid min_improvement')
    candidate, added = repair_candidate(brain, max_new_synapses=max_new_synapses,
                                        weight=candidate_weight)
    def score(b: Any) -> float:
        value = evaluate(_clone(b))
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('evaluate must return finite nonnegative error')
        return float(value)
    baseline = score(brain)
    candidate_error = score(candidate) if added else baseline
    accepted = added > 0 and baseline - candidate_error > float(min_improvement)
    return (candidate if accepted else _clone(brain),
            RepairTrial(accepted, baseline, candidate_error, added))
