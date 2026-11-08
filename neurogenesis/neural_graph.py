"""Truthful, bounded topology/telemetry snapshots for both desktop renderers.

This reads the persisted *LIF* Brain. It does not simulate neuron firings,
mutate weights, or claim to display PyTorch Foundation hidden states.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from .brain import Brain

MAX_VIEW_NODES = 112
MAX_VIEW_EDGES = 520


@dataclass(frozen=True)
class NeuronDot:
    index: int
    is_input: bool
    trace: float
    voltage: float
    spiked: bool


@dataclass(frozen=True)
class Connection:
    pre: int
    post: int
    weight: float


@dataclass(frozen=True)
class BrainFrame:
    step: int
    neurons: int
    synapses: int
    total_spikes: int
    last_spikes: int
    grown: int
    pruned: int
    novelty: float
    energy_proxy: float
    nodes: tuple[NeuronDot, ...]
    edges: tuple[Connection, ...]

    @property
    def coverage(self) -> str:
        return f"{len(self.nodes)}/{self.neurons} neuronów · {len(self.edges)}/{self.synapses} synaps"


def snapshot_brain(brain: Brain) -> BrainFrame:
    """Bounded, immutable real graph sampled from a validated local Brain.

    Priority for non-input neurons: active spikes, high trace intensity, most
    recent grown neurons, then stable low IDs. All indices remain real IDs.
    Strongest real edges between visible endpoints are drawn, with exact
    coverage counters. Never invent or extrapolate missing graph elements.
    """
    n = len(brain.voltages)
    inputs = brain.config.input_size
    chosen: set[int] = set(range(min(n, inputs)))
    capacity = max(0, MAX_VIEW_NODES - len(chosen))
    others = list(range(inputs, n))
    priority = sorted(
        others,
        key=lambda i: (
            -int(brain.spikes[i] != 0),
            -brain.traces[i],
            -int(i >= n - 24),
            i,
        ))
    chosen.update(priority[:capacity])
    nodes = tuple(
        NeuronDot(i, i < inputs, float(brain.traces[i]),
                  float(brain.voltages[i]), bool(brain.spikes[i]))
        for i in sorted(chosen))
    edges_all = [
        Connection(edge.pre, edge.post, float(edge.weight))
        for edge in brain.synapses
        if edge.pre in chosen and edge.post in chosen
    ]
    edges = tuple(sorted(
        sorted(edges_all, key=lambda e: (-e.weight, e.pre, e.post))
        [:MAX_VIEW_EDGES],
        key=lambda e: (e.pre, e.post)))
    return BrainFrame(
        step=brain.steps, neurons=n, synapses=len(brain.synapses),
        total_spikes=brain.total_spikes, last_spikes=sum(brain.spikes),
        grown=brain.total_grown, pruned=brain.total_pruned,
        novelty=float(brain.last_novelty),
        energy_proxy=float(brain.total_energy_proxy),
        nodes=nodes, edges=edges,
    )


def positions(frame: BrainFrame, width: float, height: float
              ) -> dict[int, tuple[float, float]]:
    """Deterministic, index-stable hemispherical topology positioning.

    Layout is a visual convention, NOT physical positions in brain tissue.
    """
    if width <= 0 or height <= 0:
        return {}
    in_nodes = [node.index for node in frame.nodes if node.is_input]
    out: dict[int, tuple[float, float]] = {}
    for rank, index in enumerate(in_nodes):
        out[index] = (width * .085, height * (.12 + .76 * (rank + .5) / max(1, len(in_nodes))))
    inner = [node.index for node in frame.nodes if not node.is_input]
    for i in inner:
        k = i - len(in_nodes)
        ring = max(0, k // 18)
        slot = k % 18
        radius = min(.98, .16 + ring * .125)
        theta = 2 * math.pi * (slot / 18 + .073 * ring)
        out[i] = (
            width * (.57 + .35 * radius * math.cos(theta)),
            height * (.50 + .43 * radius * math.sin(theta)))
    return out
