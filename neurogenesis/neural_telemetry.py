"""Immutable, bounded, live-derived structural telemetry of the *actual* LIF brain.

No simulation clock, animation timer, fabricated events or LLM telemetry. Every
signal originates from a complete validated Brain state recovered from SQLite.
This graph is the historical small LIF substrate, NOT PyTorch GRU internals.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from .brain import Brain

MAX_VISUAL_NEURONS = 256
MAX_VISUAL_SYNAPSES = 2048


@dataclass(frozen=True)
class NeuralNode:
    index: int
    input_channel: bool
    voltage: float
    trace: float
    fired: bool
    refractory: bool


@dataclass(frozen=True)
class NeuralEdge:
    source: int
    target: int
    weight: float
    age: int


@dataclass(frozen=True)
class NeuralTelemetry:
    step: int
    observation_count: int
    total_neurons: int
    total_synapses: int
    total_spikes: int
    last_novelty: float
    total_grown: int
    total_pruned: int
    input_channels: int
    nodes: tuple[NeuralNode, ...]
    edges: tuple[NeuralEdge, ...]
    truncated: bool


def snapshot_neural_telemetry(brain: Brain) -> NeuralTelemetry:
    """Read only state, never advance/update the brain or network.

    A time series requires successive snapshots with different `step`; Qt
    does not imply that a motionless snapshot is still actively computing.
    """
    if not isinstance(brain, Brain):
        raise TypeError("expected actual validated Brain")
    count = len(brain.voltages)
    if not (len(brain.traces) == len(brain.spikes) ==
            len(brain.refractory) == count):
        raise ValueError("invalid neuron arrays")
    if (brain.steps < 0 or count < brain.config.input_size or
            len(brain.synapses) > brain.config.max_synapses):
        raise ValueError("invalid LIF snapshot")
    limit = min(count, MAX_VISUAL_NEURONS)
    nodes: list[NeuralNode] = []
    for i in range(limit):
        voltage, trace = brain.voltages[i], brain.traces[i]
        if (not math.isfinite(voltage) or not math.isfinite(trace)
                or voltage < 0 or trace < 0):
            raise ValueError("invalid neural activity")
        nodes.append(NeuralNode(
            index=i, input_channel=i < brain.config.input_size,
            voltage=float(voltage), trace=float(trace),
            fired=brain.spikes[i] == 1,
            refractory=brain.refractory[i] > 0))
    edges: list[NeuralEdge] = []
    for e in brain.synapses:
        if len(edges) >= MAX_VISUAL_SYNAPSES:
            break
        if e.pre >= limit or e.post >= limit:
            continue
        if not 0 <= e.pre < count or not 0 <= e.post < count:
            raise ValueError("invalid neural connection index")
        if not math.isfinite(e.weight) or e.weight < 0:
            raise ValueError("invalid synaptic weight")
        edges.append(NeuralEdge(e.pre, e.post, float(e.weight), e.age))
    return NeuralTelemetry(
        step=brain.steps,
        observation_count=brain.observations,
        total_neurons=count,
        total_synapses=len(brain.synapses),
        total_spikes=brain.total_spikes,
        last_novelty=float(brain.last_novelty),
        total_grown=brain.total_grown,
        total_pruned=brain.total_pruned,
        input_channels=brain.config.input_size,
        nodes=tuple(nodes), edges=tuple(edges),
        truncated=(limit < count or len(edges) < len(brain.synapses)))


def diff_neural_telemetry(previous: NeuralTelemetry | None,
                          current: NeuralTelemetry) -> dict[str, int | bool]:
    """Actual persisted changes between observations, never interpolations."""
    if previous is None or current.step <= previous.step:
        return {"advanced": False, "delta_steps": 0, "new_neurons": 0,
                "new_synapses": 0, "new_spikes": 0, "changed_weights": 0}
    old_weights = {(e.source, e.target): e.weight for e in previous.edges}
    changed = sum(
        (e.source, e.target) in old_weights
        and abs(e.weight - old_weights[e.source, e.target]) > 1e-9
        for e in current.edges)
    return {"advanced": True, "delta_steps": current.step - previous.step,
            "new_neurons": max(0, current.total_neurons - previous.total_neurons),
            "new_synapses": max(0, current.total_synapses - previous.total_synapses),
            "new_spikes": max(0, current.total_spikes - previous.total_spikes),
            "changed_weights": changed}
