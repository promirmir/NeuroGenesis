"""Adaptive Cognitive Fabric v1: causal structural learning and measured self-model.

This is a distinct EXPERIMENTAL predictive neural substrate, not an AGI or a
semantic language model. Every online decision (the next 8-channel forecast)
is actually routed through the prior error-ranked predictor or naive control.
Its output does NOT silently overwrite the verified existing LIF memory.

The protocol is prequential: predict t before observing t; only then learn
from t and select the route for t+1 using past errors. The self-model tracks
measured loss and structural change, not invented abilities or consciousness.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Sequence

from .brain import Brain, BrainConfig
from .predictor import NextInputPredictor

ROUTES = ("adaptive", "fixed", "persistence", "constant_half")
HISTORY = 128
WARMUP = 24
STATE_VERSION = 1
MAX_STATE_BYTES = 16 * 1024 * 1024


def _sample(values: Sequence[float], width: int) -> list[float]:
    if not isinstance(values, (list, tuple)) or len(values) != width:
        raise ValueError("ACF expects exactly the configured sensory channels.")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1
           for v in values):
        raise ValueError("ACF input must be finite numbers within [0,1].")
    return [float(v) for v in values]


def _mse(estimate: Sequence[float], actual: Sequence[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(estimate, actual)) / len(actual)


@dataclass(frozen=True)
class FabricObservation:
    step: int
    selected_route: str
    next_forecast: tuple[float, ...]
    last_error: float | None
    expected_rmse: float | None
    adaptive_neurons: int
    fixed_neurons: int
    total_grown: int
    total_pruned: int


class AdaptiveCognitiveFabric:
    """Online structural LIF predictor with a genuinely empirical route gate.

    Matched adaptive/fixed brain controls start with the SAME seed, initial
    topology, readout learning rate, and training examples. Only growth is
    disabled in the fixed control. A persistence and a 0.5 control run too.
    All four are scored BEFORE each observation updates their parameters.
    A route is selected using *past* trailing losses, never future targets.
    """

    def __init__(self, *, config: BrainConfig | None = None, seed: int = 7,
                 learning_rate: float = 0.15):
        cfg = config or BrainConfig()
        if not isinstance(cfg, BrainConfig) or type(seed) is not int or not 0 <= seed < 2**32:
            raise ValueError("Invalid ACF configuration or seed.")
        self.adaptive = NextInputPredictor(
            Brain(replace(cfg, growth_enabled=True), seed=seed),
            learning_rate=learning_rate)
        self.fixed = NextInputPredictor(
            Brain(replace(cfg, growth_enabled=False), seed=seed),
            learning_rate=learning_rate)
        self.losses: dict[str, list[float]] = {name: [] for name in ROUTES}
        self.events = 0
        self.last_event_id = 0
        self.last_sample: list[float] | None = None
        self.selected_route = "constant_half"
        self.next_forecast = [0.5] * cfg.input_size

    @property
    def width(self) -> int:
        return self.adaptive.brain.config.input_size

    def _route_forecast(self, route: str) -> list[float]:
        if route == "adaptive":
            return list(self.adaptive.next_forecast)
        if route == "fixed":
            return list(self.fixed.next_forecast)
        if route == "persistence" and self.last_sample is not None:
            return list(self.last_sample)
        if route in ("constant_half", "persistence"):
            return [0.5] * self.width
        raise ValueError("Unknown routing decision.")

    def _choose(self) -> str:
        if min(map(len, self.losses.values())) < WARMUP:
            return "constant_half"
        avg = {name: sum(values) / len(values)
               for name, values in self.losses.items()}
        winner = min(ROUTES, key=lambda name: (avg[name], ROUTES.index(name)))
        # A small hysteresis prevents switching models from single noisy points.
        current = self.selected_route
        if current in avg and avg[winner] >= avg[current] - 0.0005:
            return current
        return winner

    def observe(self, sensory: Sequence[float]) -> FabricObservation:
        """One REAL observation, one causal score, then an online update."""
        x = _sample(sensory, self.width)
        prior_route = self.selected_route
        prior_forecast = list(self.next_forecast)
        a = self.adaptive.step(x, learn=True)
        b = self.fixed.step(x, learn=True)
        if a.mse_before_update != b.mse_before_update and self.events == 0:
            raise AssertionError("Unmatched ACF controls at initialization.")
        error = None
        if self.last_sample is not None:
            # Predictor.step already scored its PRE-UPDATE forecast.
            scores = {
                "adaptive": a.mse_before_update,
                "fixed": b.mse_before_update,
                "persistence": _mse(self.last_sample, x),
                "constant_half": _mse([0.5] * self.width, x),
            }
            for key, result in scores.items():
                if result is None or not math.isfinite(result):
                    raise RuntimeError("Missing causal prediction error.")
                self.losses[key].append(float(result))
                if len(self.losses[key]) > HISTORY:
                    self.losses[key].pop(0)
            error = _mse(prior_forecast, x)
        self.events += 1
        self.last_sample = x
        self.selected_route = self._choose()
        self.next_forecast = self._route_forecast(self.selected_route)
        self_report = self.self_model()
        return FabricObservation(
            step=self.events,
            selected_route=self.selected_route,
            next_forecast=tuple(self.next_forecast),
            last_error=error,
            expected_rmse=self_report["estimated_next_rmse"],
            adaptive_neurons=a.neurons,
            fixed_neurons=b.neurons,
            total_grown=self.adaptive.brain.total_grown,
            total_pruned=self.adaptive.brain.total_pruned,
        )

    def self_model(self) -> dict[str, Any]:
        """A compact audit of genuine measured abilities, not self-awareness."""
        counts = {name: len(v) for name, v in self.losses.items()}
        avg = {name: (round(sum(v) / len(v), 8) if v else None)
               for name, v in self.losses.items()}
        chosen = avg[self.selected_route]
        return {
            "protocol": "acf_causal_prequential_v1",
            "observations": self.events,
            "scored_predictions": len(self.losses["adaptive"]),
            "selected_route": self.selected_route,
            "route_mean_mse_recent": avg,
            "estimated_next_rmse": (
                round(math.sqrt(chosen), 6) if chosen is not None else None),
            "confidence_is_calibrated": False,
            "has_measured_advantage_over_fixed": (
                avg["adaptive"] is not None and avg["fixed"] is not None
                and len(self.losses["adaptive"]) >= WARMUP
                and avg["adaptive"] + 0.0005 < avg["fixed"]),
            "has_measured_advantage_over_persistence": (
                avg["adaptive"] is not None and avg["persistence"] is not None
                and len(self.losses["adaptive"]) >= WARMUP
                and avg["adaptive"] + 0.0005 < avg["persistence"]),
            "adaptive_structure": self.adaptive.brain.stats(),
            "fixed_structure": self.fixed.brain.stats(),
            "last_event_id": self.last_event_id,
            "limitations": (
                "Prequential prediction on eight bounded hashed sensory channels; "
                "no semantic cognition, general intelligence, calibrated probability, "
                "or guaranteed benefit from network growth."
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": STATE_VERSION,
            "adaptive": self.adaptive.to_dict(),
            "fixed": self.fixed.to_dict(),
            "losses": {key: list(values) for key, values in self.losses.items()},
            "events": self.events,
            "last_event_id": self.last_event_id,
            "last_sample": self.last_sample,
            "selected_route": self.selected_route,
            "next_forecast": self.next_forecast,
        }

    @classmethod
    def from_dict(cls, state: dict[str, Any]) -> AdaptiveCognitiveFabric:
        required = {"schema", "adaptive", "fixed", "losses", "events",
                    "last_event_id", "last_sample", "selected_route",
                    "next_forecast"}
        if type(state) is not dict or set(state) != required or state["schema"] != STATE_VERSION:
            raise ValueError("Invalid ACF snapshot schema.")
        a = NextInputPredictor.from_dict(state["adaptive"])
        b = NextInputPredictor.from_dict(state["fixed"])
        if (a.brain.config.input_size != b.brain.config.input_size
                or not a.brain.config.growth_enabled
                or b.brain.config.growth_enabled
                or a.brain.config.initial_neurons != b.brain.config.initial_neurons
                or a.learning_rate != b.learning_rate):
            raise ValueError("Unmatched or corrupted ACF comparator pair.")
        if (type(state["events"]) is not int or state["events"] < 0
                or type(state["last_event_id"]) is not int
                or state["last_event_id"] < 0
                or state["last_event_id"] > state["events"] + 1_000_000
                or state["selected_route"] not in ROUTES):
            raise ValueError("Invalid ACF counters or selected route.")
        raw_losses = state["losses"]
        if type(raw_losses) is not dict or set(raw_losses) != set(ROUTES):
            raise ValueError("Invalid ACF loss histories.")
        lengths = set()
        losses = {}
        for name in ROUTES:
            row = raw_losses[name]
            if not isinstance(row, list) or len(row) > HISTORY or len(row) > state["events"]:
                raise ValueError("Invalid ACF loss window.")
            if any(type(n) not in (int, float) or not math.isfinite(n)
                   or not 0 <= n <= 1 for n in row):
                raise ValueError("Non-finite or out-of-bound error.")
            losses[name] = [float(n) for n in row]
            lengths.add(len(row))
        if len(lengths) != 1 or next(iter(lengths)) != min(HISTORY, max(0, state["events"] - 1)):
            raise ValueError("Unmatched causal ACF score windows.")
        w = a.brain.config.input_size
        last = (None if state["last_sample"] is None
                else _sample(state["last_sample"], w))
        if (state["events"] == 0) != (last is None):
            raise ValueError("Inconsistent ACF observation state.")
        forecast = _sample(state["next_forecast"], w)
        obj = cls(config=a.brain.config, learning_rate=a.learning_rate)
        obj.adaptive, obj.fixed = a, b
        obj.losses = losses
        obj.events = state["events"]
        obj.last_event_id = state["last_event_id"]
        obj.last_sample = last
        obj.selected_route = state["selected_route"]
        obj.next_forecast = forecast
        # A restored forecast must be exactly the one used at evaluation.
        if obj.next_forecast != obj._route_forecast(obj.selected_route):
            raise ValueError("Unmatched next forecast and selected route.")
        return obj

    def save(self, path: str | Path) -> None:
        """Atomic private snapshot; no raw documents or conversation text."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.to_dict(), ensure_ascii=False,
                             allow_nan=False, separators=(",", ":")).encode("utf-8")
        if len(payload) > MAX_STATE_BYTES:
            raise ValueError("ACF snapshot exceeds its resource cap.")
        temp = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="wb", dir=target.parent, prefix=".acf-",
                    suffix=".tmp", delete=False) as stream:
                temp = stream.name
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, target)
        finally:
            if temp and os.path.exists(temp):
                os.unlink(temp)

    @classmethod
    def load(cls, path: str | Path) -> AdaptiveCognitiveFabric:
        file = Path(path)
        if file.stat().st_size > MAX_STATE_BYTES:
            raise ValueError("Oversized ACF snapshot.")
        def reject_constant(value: str):
            raise ValueError("Invalid nonfinite JSON value: " + value)
        with file.open("r", encoding="utf-8") as stream:
            return cls.from_dict(json.load(stream, parse_constant=reject_constant))
