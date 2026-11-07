"""Memory-guided structural compensation on the v0.4 spiking brain.

A stored pre-injury *functional* activity fingerprint may be used to propose
connections after simulated damage. This is a bounded research algorithm, not
regeneration of erased memories or autonomous biological self-repair. Never
writes to the operator's brain object, files, code, or SQLite database.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Sequence

from .brain import Brain, Synapse

MAX_SIGNATURE_STEPS = 256
MAX_NEURONS = 128
MAX_INPUTS = 16
WEIGHT_GRID = (0.5, 0.65, 0.8, 1.0, 1.2)


def _clone(brain: Brain) -> Brain:
    if not isinstance(brain, Brain):
        raise ValueError('expected an initialized Brain')
    return Brain.from_dict(brain.to_dict())


@dataclass(frozen=True)
class ActivityFingerprint:
    """A local private record of numeric stimuli and measured hidden spikes."""
    input_size: int
    neuron_count: int
    stimuli: tuple[tuple[float, ...], ...]
    responses: tuple[tuple[int, ...], ...]
    schema: int = 1

    def __post_init__(self) -> None:
        if type(self.schema) is not int or self.schema != 1:
            raise ValueError('unsupported activity fingerprint schema')
        if (type(self.input_size) is not int or type(self.neuron_count) is not int or
            not 1 <= self.input_size <= MAX_INPUTS or
            not self.input_size < self.neuron_count <= MAX_NEURONS):
            raise ValueError('invalid fingerprint dimensions')
        if (type(self.stimuli) is not tuple or type(self.responses) is not tuple or
            not 1 <= len(self.stimuli) <= MAX_SIGNATURE_STEPS or
            len(self.stimuli) != len(self.responses)):
            raise ValueError('invalid fingerprint sequence lengths')
        for stimulus, response in zip(self.stimuli, self.responses):
            if (type(stimulus) is not tuple or len(stimulus) != self.input_size or
                any(type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= 1
                    for x in stimulus)):
                raise ValueError('invalid fingerprint stimulus')
            if (type(response) is not tuple or len(response) != self.neuron_count - self.input_size or
                any(type(x) is not int or x not in (0, 1) for x in response)):
                raise ValueError('invalid fingerprint neural response')

    def to_dict(self) -> dict[str, Any]:
        return {'schema': self.schema, 'input_size': self.input_size,
                'neuron_count': self.neuron_count,
                'stimuli': [list(x) for x in self.stimuli],
                'responses': [list(x) for x in self.responses]}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ActivityFingerprint:
        if not isinstance(value, dict) or set(value) != {
            'schema', 'input_size', 'neuron_count', 'stimuli', 'responses'
        }:
            raise ValueError('malformed fingerprint snapshot')
        if (type(value['stimuli']) is not list or type(value['responses']) is not list or
            len(value['stimuli']) > MAX_SIGNATURE_STEPS or
            len(value['responses']) > MAX_SIGNATURE_STEPS):
            raise ValueError('invalid fingerprint sequences')
        for x in value['stimuli'] + value['responses']:
            if type(x) is not list:
                raise ValueError('fingerprint items must be lists')
        return cls(value['input_size'], value['neuron_count'],
                   tuple(tuple(x) for x in value['stimuli']),
                   tuple(tuple(x) for x in value['responses']), value['schema'])


def record_fingerprint(brain: Brain, stimuli: Iterable[Sequence[float]]) -> ActivityFingerprint:
    """Record activity from a healthy clone without altering the live brain."""
    probe = _clone(brain)
    width = probe.config.input_size
    n = len(probe.voltages)
    if width > MAX_INPUTS or n > MAX_NEURONS:
        raise ValueError('brain too large for bounded fingerprint recording')
    rows: list[tuple[float, ...]] = []
    activity: list[tuple[int, ...]] = []
    for x in stimuli:
        if len(rows) >= MAX_SIGNATURE_STEPS:
            raise ValueError('fingerprint exceeds step budget')
        if (not isinstance(x, (tuple, list)) or
            any(type(v) not in (int, float) for v in x)):
            raise ValueError('fingerprint observations must be numeric vectors')
        values = tuple(float(v) for v in x)
        if (len(values) != width or any(not math.isfinite(v) or v < 0 or v > 1 for v in values)):
            raise ValueError('invalid fingerprint sensory observation')
        output = probe.step(values)
        if output.neurons != n:
            raise ValueError('fingerprint topology changed during recording')
        rows.append(values)
        activity.append(tuple(output.spikes[width:]))
    return ActivityFingerprint(width, n, tuple(rows), tuple(activity))


def fingerprint_error(brain: Brain, fingerprint: ActivityFingerprint) -> float:
    """Mismatch on cloned substrate, normalized to number of hidden-spike bits."""
    if not isinstance(fingerprint, ActivityFingerprint):
        raise ValueError('activity fingerprint required')
    probe = _clone(brain)
    if len(probe.voltages) != fingerprint.neuron_count or probe.config.input_size != fingerprint.input_size:
        raise ValueError('brain and fingerprint dimensions differ')
    misses = 0
    for x, expected in zip(fingerprint.stimuli, fingerprint.responses):
        response = probe.step(x)
        if response.neurons != fingerprint.neuron_count:
            raise ValueError('topology changed during evaluation')
        misses += sum(a != b for a, b in zip(response.spikes[fingerprint.input_size:], expected))
    return misses / (len(fingerprint.stimuli) * (fingerprint.neuron_count - fingerprint.input_size))


@dataclass(frozen=True)
class FingerprintRepairResult:
    initial_error: float
    final_validation_error: float
    attempted_proposals: int
    accepted_connections: int
    added_paths: tuple[tuple[int, int, float], ...]


def propose_fingerprint_repair(brain: Brain, fingerprint: ActivityFingerprint,
                               *, max_new_synapses: int = 6,
                               max_proposals: int = 3000,
                               min_improvement: float = 0.0
                               ) -> tuple[Brain, FingerprintRepairResult]:
    """Bounded greedy search for recovered *recorded* activity, on cloned state.

    Only previously active AND currently fully disconnected hidden neurons are
    considered. Candidate paths are never accepted without an actual reduction
    of validation error. A fully functional network yields no modifications.
    Final independent holdout tests remain the caller's responsibility.
    """
    if type(max_new_synapses) is not int or not 0 <= max_new_synapses <= 8:
        raise ValueError('max_new_synapses must be in [0, 8]')
    if type(max_proposals) is not int or not 0 <= max_proposals <= 10000:
        raise ValueError('max_proposals must be in [0, 10000]')
    if type(min_improvement) not in (int, float) or not math.isfinite(min_improvement) or min_improvement < 0:
        raise ValueError('invalid min_improvement')
    current = _clone(brain)
    initial_error = fingerprint_error(current, fingerprint)
    score = initial_error
    additions: list[tuple[int, int, float]] = []
    attempts = 0
    active = [sum(row[i] for row in fingerprint.responses)
              for i in range(len(current.voltages) - current.config.input_size)]
    width = current.config.input_size
    for _ in range(min(max_new_synapses, max(0, current.config.max_synapses - len(current.synapses)))):
        indegree = [0] * len(current.voltages)
        for edge in current.synapses:
            indegree[edge.post] += 1
        disconnected = [p for p in range(width, len(current.voltages))
                        if indegree[p] == 0 and active[p - width] > 0]
        best_path = None
        best_gain = float(min_improvement)
        exhausted = False
        for post in disconnected:
            for pre in range(width):
                for weight in WEIGHT_GRID:
                    if weight > current.config.weight_limit:
                        continue
                    if attempts >= max_proposals:
                        exhausted = True
                        break
                    attempts += 1
                    proposal = _clone(current)
                    proposal.synapses.append(Synapse(pre, post, weight))
                    test_score = fingerprint_error(proposal, fingerprint)
                    improvement = score - test_score
                    if improvement > best_gain + 1e-12:
                        best_gain = improvement
                        best_path = (pre, post, weight, test_score)
                if exhausted:
                    break
            if exhausted:
                break
        if best_path is None:
            break
        pre, post, weight, new_score = best_path
        current.synapses.append(Synapse(pre, post, weight))
        additions.append((pre, post, weight))
        score = new_score
    return current, FingerprintRepairResult(initial_error, score, attempts,
                                            len(additions), tuple(additions))
