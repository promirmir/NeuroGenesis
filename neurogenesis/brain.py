"""A bounded, deterministic spiking-network research baseline.

This is a computational experiment, not a biological brain or consciousness model.
All structural changes and learning signals are explicitly measurable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Sequence

from .origin import origin_record, validate_origin


@dataclass(frozen=True)
class BrainConfig:
    input_size: int = 8
    initial_neurons: int = 24
    # Expanded capacity for NEW memory databases only. Existing snapshots
    # persist their own configuration and are never silently migrated.
    # This is additional headroom, not a benchmark or a claim of improved AI.
    max_neurons: int = 512
    max_synapses: int = 4096
    max_patterns: int = 1024
    membrane_decay: float = 0.65
    threshold: float = 0.9
    input_gain: float = 1.2
    trace_decay: float = 0.8
    plasticity_rate: float = 0.025
    weight_decay: float = 0.0001
    weight_limit: float = 1.5
    growth_interval: int = 8
    novelty_threshold: float = 0.24
    prune_threshold: float = 0.02
    prune_min_age: int = 40
    growth_enabled: bool = True

    def __post_init__(self) -> None:
        ints = ("input_size", "initial_neurons", "max_neurons", "max_synapses",
                "max_patterns", "growth_interval", "prune_min_age")
        for name in ints:
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if not (1 <= self.input_size < self.initial_neurons <= self.max_neurons <= 4096):
            raise ValueError("require 1 <= input_size < initial_neurons <= max_neurons <= 4096")
        if not (2 <= self.max_synapses <= 100000 and 1 <= self.max_patterns <= 4096):
            raise ValueError("invalid resource limits")
        if self.growth_interval < 1 or self.prune_min_age < 1:
            raise ValueError("growth_interval and prune_min_age must be positive")
        bounds = {
            "membrane_decay": (0, 1), "threshold": (0, 10),
            "input_gain": (0, 10), "trace_decay": (0, 1),
            "plasticity_rate": (0, 1), "weight_decay": (0, 1),
            "weight_limit": (0, 10), "novelty_threshold": (0, 1),
            "prune_threshold": (0, 10),
        }
        for name, (low, high) in bounds.items():
            value = getattr(self, name)
            if type(value) not in (int, float) or not math.isfinite(value) or not low < value <= high:
                raise ValueError(f"invalid {name}")
        if type(self.growth_enabled) is not bool:
            raise ValueError("growth_enabled must be boolean")


@dataclass
class Synapse:
    pre: int
    post: int
    weight: float
    age: int = 0


@dataclass(frozen=True)
class StepResult:
    step: int
    spikes: tuple[int, ...]
    novelty: float
    neurons: int
    synapses: int
    grown: int
    pruned: int
    energy_proxy: float


class Brain:
    """Sparse leaky integrate-and-fire neurons with trace-based plasticity.

    Inputs are bounded [0,1] sensory channels, not arbitrary instructions.
    New neurons are triggered by novel sensory patterns, not a claim of cognition.
    """

    SCHEMA_VERSION = 1
    MAX_STATE_BYTES = 16 * 1024 * 1024

    def __init__(self, config: BrainConfig | None = None, *, seed: int = 1) -> None:
        self.config = config or BrainConfig()
        if type(seed) is not int or not 0 <= seed < 2**32:
            raise ValueError("seed must be a uint32")
        self.rng_state = seed
        n = self.config.initial_neurons
        self.voltages: list[float] = [0.0] * n
        self.traces: list[float] = [0.0] * n
        self.spikes: list[int] = [0] * n
        self.refractory: list[int] = [0] * n
        self.synapses: list[Synapse] = []
        self.patterns: list[list[float]] = []
        self.steps = 0
        self.observations = 0
        self.total_grown = 0
        self.total_pruned = 0
        self.pending_novelty = 0
        self.last_novelty = 0.0
        self.total_spikes = 0
        self.total_energy_proxy = 0.0
        self.last_stimulus = [0.0] * self.config.input_size
        hidden_count = n - self.config.input_size
        for i in range(self.config.input_size):
            for offset in range(min(2, hidden_count)):
                if len(self.synapses) >= self.config.max_synapses:
                    break
                target = self.config.input_size + (i + offset) % hidden_count
                self.synapses.append(Synapse(i, target, 0.65 + 0.2 * self._rand()))

    def _rand(self) -> float:
        # Portable LCG: deterministic across Python versions and JSON snapshots.
        self.rng_state = (1664525 * self.rng_state + 1013904223) % (2**32)
        return self.rng_state / (2**32)

    def _novelty(self, stimulus: list[float]) -> float:
        if not self.patterns:
            distance = 1.0
        else:
            distance = min(
                sum(abs(a - b) for a, b in zip(stimulus, pattern)) / self.config.input_size
                for pattern in self.patterns
            )
        if distance >= self.config.novelty_threshold and len(self.patterns) < self.config.max_patterns:
            self.patterns.append(stimulus.copy())
            self.pending_novelty += 1
        return distance

    def _grow(self) -> int:
        c = self.config
        if not c.growth_enabled or not self.pending_novelty:
            return 0
        if len(self.voltages) >= c.max_neurons or len(self.synapses) + 2 > c.max_synapses:
            return 0
        index = len(self.voltages)
        source = max(range(c.input_size), key=lambda i: (self.last_stimulus[i], -i))
        target = max(range(c.input_size, index), key=lambda i: (self.traces[i], -i))
        self.voltages.append(0.0)
        self.traces.append(0.0)
        self.spikes.append(0)
        self.refractory.append(0)
        self.synapses.extend([Synapse(source, index, 0.8), Synapse(index, target, 0.55)])
        self.total_grown += 1
        return 1

    def step(self, stimulus: Sequence[float], *, reward: float = 0.0) -> StepResult:
        c = self.config
        if len(stimulus) != c.input_size:
            raise ValueError(f"expected {c.input_size} input channels")
        if type(reward) not in (float, int) or not math.isfinite(reward) or not -1 <= reward <= 1:
            raise ValueError("reward must be finite and between -1 and 1")
        values: list[float] = []
        for value in stimulus:
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("input values must be finite numbers in [0, 1]")
            values.append(float(value))
        self.last_stimulus = values
        novelty = self._novelty(values)
        n = len(self.voltages)
        current = [0.0] * n
        for i, value in enumerate(values):
            current[i] += c.input_gain * value
        for edge in self.synapses:
            if self.spikes[edge.pre]:
                current[edge.post] += edge.weight
        new_spikes = [0] * n
        for i in range(n):
            if self.refractory[i] > 0:
                self.refractory[i] -= 1
                continue
            self.voltages[i] = self.voltages[i] * c.membrane_decay + current[i]
            if self.voltages[i] >= c.threshold:
                new_spikes[i] = 1
                self.voltages[i] = 0.0
                self.refractory[i] = 1
        # Causal pre-before-post potentiation and weaker reverse depression.
        for edge in self.synapses:
            potentiation = self.traces[edge.pre] * new_spikes[edge.post]
            depression = 0.25 * self.traces[edge.post] * new_spikes[edge.pre]
            delta = c.plasticity_rate * (1.0 + float(reward)) * (potentiation - depression)
            edge.weight = max(0.0, min(c.weight_limit, edge.weight * (1 - c.weight_decay) + delta))
            edge.age += 1
        for i in range(n):
            self.traces[i] = min(5.0, self.traces[i] * c.trace_decay + new_spikes[i])
        self.spikes = new_spikes
        self.steps += 1
        self.observations += 1
        self.last_novelty = novelty
        spiked = sum(new_spikes)
        self.total_spikes += spiked
        energy_proxy = spiked + 0.001 * len(self.synapses)
        self.total_energy_proxy += energy_proxy
        grown = pruned = 0
        if self.steps % c.growth_interval == 0:
            grown = self._grow()
            before = len(self.synapses)
            self.synapses = [e for e in self.synapses if not (e.age >= c.prune_min_age and e.weight < c.prune_threshold)]
            pruned = before - len(self.synapses)
            self.total_pruned += pruned
            self.pending_novelty = 0
        return StepResult(self.steps, tuple(new_spikes), novelty, len(self.voltages),
                          len(self.synapses), grown, pruned, energy_proxy)

    def stats(self) -> dict[str, Any]:
        return {
            "steps": self.steps, "neurons": len(self.voltages),
            "synapses": len(self.synapses), "stored_patterns": len(self.patterns),
            "total_grown": self.total_grown, "total_pruned": self.total_pruned,
            "total_spikes": self.total_spikes,
            "last_novelty": round(self.last_novelty, 6),
            "energy_proxy_total": round(self.total_energy_proxy, 6),
            "growth_enabled": self.config.growth_enabled,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA_VERSION, "origin": origin_record(),
            "config": asdict(self.config),
            "rng_state": self.rng_state, "voltages": self.voltages,
            "traces": self.traces, "spikes": self.spikes,
            "refractory": self.refractory, "synapses": [asdict(e) for e in self.synapses],
            "patterns": self.patterns, "steps": self.steps, "observations": self.observations,
            "total_grown": self.total_grown, "total_pruned": self.total_pruned,
            "pending_novelty": self.pending_novelty, "last_novelty": self.last_novelty,
            "total_spikes": self.total_spikes, "total_energy_proxy": self.total_energy_proxy,
            "last_stimulus": self.last_stimulus,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Brain:
        if not isinstance(data, dict) or data.get("schema") != cls.SCHEMA_VERSION:
            raise ValueError("unsupported brain snapshot schema")
        # Backward compatibility: snapshots written before provenance was added
        # are accepted, but all new saves embed the canonical origin record.
        if "origin" in data:
            validate_origin(data["origin"])
        try:
            config = BrainConfig(**data["config"])
            brain = cls(config, seed=data["rng_state"])
            n = len(data["voltages"])
            if not config.initial_neurons <= n <= config.max_neurons:
                raise ValueError("invalid neuron count")
            for name in ("voltages", "traces", "spikes", "refractory"):
                if len(data[name]) != n:
                    raise ValueError(f"invalid {name} length")
            for name in ("voltages", "traces"):
                if any(type(x) not in (int, float) or not math.isfinite(x) for x in data[name]):
                    raise ValueError(f"invalid {name} values")
            if any(x not in (0, 1) or type(x) is not int for x in data["spikes"]):
                raise ValueError("invalid spikes")
            if any(type(x) is not int or x not in (0, 1) for x in data["refractory"]):
                raise ValueError("invalid refractory")
            if len(data["synapses"]) > config.max_synapses:
                raise ValueError("too many synapses")
            synapses = [Synapse(**e) for e in data["synapses"]]
            for e in synapses:
                if (type(e.pre) is not int or type(e.post) is not int or
                    not 0 <= e.pre < n or not 0 <= e.post < n or e.pre == e.post or
                    type(e.age) is not int or e.age < 0 or
                    type(e.weight) not in (int, float) or not math.isfinite(e.weight) or
                    not 0 <= e.weight <= config.weight_limit):
                    raise ValueError("invalid synapse")
            if len(data["patterns"]) > config.max_patterns:
                raise ValueError("too many patterns")
            for pattern in data["patterns"] + [data["last_stimulus"]]:
                if len(pattern) != config.input_size or any(type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= 1 for x in pattern):
                    raise ValueError("invalid sensory pattern")
            counters = ("steps", "observations", "total_grown", "total_pruned",
                        "pending_novelty", "total_spikes")
            if any(type(data[k]) is not int or data[k] < 0 for k in counters):
                raise ValueError("invalid counters")
            if (type(data["last_novelty"]) not in (int, float) or
                not 0 <= data["last_novelty"] <= 1 or
                type(data["total_energy_proxy"]) not in (int, float) or
                not math.isfinite(data["total_energy_proxy"]) or data["total_energy_proxy"] < 0):
                raise ValueError("invalid metrics")
            brain.rng_state = data["rng_state"]
            brain.voltages = list(data["voltages"])
            brain.traces = list(data["traces"])
            brain.spikes = list(data["spikes"])
            brain.refractory = list(data["refractory"])
            brain.synapses = synapses
            brain.patterns = [list(p) for p in data["patterns"]]
            for key in counters + ("last_novelty", "total_energy_proxy"):
                setattr(brain, key, data[key])
            brain.last_stimulus = list(data["last_stimulus"])
            return brain
        except (KeyError, TypeError, AttributeError, IndexError) as exc:
            raise ValueError("malformed brain snapshot") from exc

    def save(self, path: str | Path) -> None:
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.to_dict(), allow_nan=False, separators=(",", ":"))
        if len(payload.encode("utf-8")) > self.MAX_STATE_BYTES:
            raise ValueError("snapshot exceeds size limit")
        tmp: str | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=dest.parent,
                                             prefix=".neurogenesis-", suffix=".tmp", delete=False) as file:
                tmp = file.name
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp, dest)
        finally:
            if tmp is not None and os.path.exists(tmp):
                os.unlink(tmp)

    @classmethod
    def load(cls, path: str | Path) -> Brain:
        file = Path(path)
        if file.stat().st_size > cls.MAX_STATE_BYTES:
            raise ValueError("snapshot exceeds size limit")
        def reject_constant(value: str) -> None:
            raise ValueError(f"non-finite JSON constant: {value}")
        with file.open("r", encoding="utf-8") as stream:
            data = json.load(stream, parse_constant=reject_constant)
        return cls.from_dict(data)
