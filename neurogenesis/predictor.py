"""Self-supervised next-sensory-step prediction with an adaptive neural readout.

Predictions are causal (made *before* the next observation). No human labels are
required, but this is a toy sequence prediction task, not general intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Sequence

from .brain import Brain, BrainConfig


@dataclass(frozen=True)
class PredictionStep:
    step: int
    mse_before_update: float | None
    next_forecast: tuple[float, ...]
    neurons: int
    grown: int


class NextInputPredictor:
    """Online linear prediction head driven by the growing spiking substrate."""

    SCHEMA_VERSION = 1

    def __init__(self, brain: Brain | None = None, *, learning_rate: float = 0.15) -> None:
        if type(learning_rate) not in (int, float) or not math.isfinite(learning_rate) or not 0 < learning_rate <= 1:
            raise ValueError("learning_rate must be in (0, 1]")
        self.brain = brain or Brain()
        self.learning_rate = float(learning_rate)
        self.weights: list[list[float]] = [
            [0.0] * len(self.brain.voltages) for _ in range(self.brain.config.input_size)
        ]
        self.bias: list[float] = [0.0] * self.brain.config.input_size
        self.last_features: list[float] | None = None
        self.next_forecast: list[float] = [0.5] * self.brain.config.input_size
        self.predicted_steps = 0
        self.error_sum = 0.0

    @staticmethod
    def _sigmoid(value: float) -> float:
        # Numerically stable logistic function.
        return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, value))))

    def _predict(self, features: list[float]) -> list[float]:
        return [self._sigmoid(self.bias[i] + sum(w * x for w, x in zip(row, features)))
                for i, row in enumerate(self.weights)]

    def step(self, stimulus: Sequence[float], *, learn: bool = True) -> PredictionStep:
        if len(stimulus) != self.brain.config.input_size:
            raise ValueError("invalid input width")
        values: list[float] = []
        for value in stimulus:
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("inputs must be finite and in [0, 1]")
            values.append(float(value))
        error: float | None = None
        if type(learn) is not bool:
            raise ValueError("learn must be a boolean")
        if self.last_features is not None:
            error = sum((y - x) ** 2 for y, x in zip(self.next_forecast, values)) / len(values)
            self.predicted_steps += 1
            self.error_sum += error
            # MSE gradient through logistic output; step size normalized to
            # feature activation to avoid instability as neurons are added.
            active = 1.0 + sum(x * x for x in self.last_features)
            if learn:
                for i, (target, estimate) in enumerate(zip(values, self.next_forecast)):
                    delta = self.learning_rate * 2.0 * (target - estimate) * estimate * (1.0 - estimate) / active
                    self.bias[i] += delta
                    for j, feature in enumerate(self.last_features):
                        self.weights[i][j] = max(-8.0, min(8.0, self.weights[i][j] + delta * feature))
        outcome = self.brain.step(values)
        new_n = len(self.brain.voltages)
        for row in self.weights:
            row.extend([0.0] * (new_n - len(row)))
        self.last_features = [min(1.0, t) for t in self.brain.traces]
        self.next_forecast = self._predict(self.last_features)
        return PredictionStep(outcome.step, error, tuple(self.next_forecast), new_n, outcome.grown)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA_VERSION, "brain": self.brain.to_dict(),
            "learning_rate": self.learning_rate, "weights": self.weights,
            "bias": self.bias, "last_features": self.last_features,
            "next_forecast": self.next_forecast, "predicted_steps": self.predicted_steps,
            "error_sum": self.error_sum,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NextInputPredictor:
        if not isinstance(data, dict) or data.get("schema") != cls.SCHEMA_VERSION:
            raise ValueError("unsupported predictor schema")
        try:
            brain = Brain.from_dict(data["brain"])
            obj = cls(brain, learning_rate=data["learning_rate"])
            n = len(brain.voltages)
            width = brain.config.input_size
            rows = data["weights"]
            if len(rows) != width or any(len(row) != n for row in rows):
                raise ValueError("invalid readout shape")
            if len(data["bias"]) != width or len(data["next_forecast"]) != width:
                raise ValueError("invalid prediction shape")
            features = data["last_features"]
            if features is not None and len(features) != n:
                raise ValueError("invalid features shape")
            if (type(data["predicted_steps"]) is not int or data["predicted_steps"] < 0 or
                type(data["error_sum"]) not in (float, int) or not math.isfinite(data["error_sum"]) or
                data["error_sum"] < 0):
                raise ValueError("invalid prediction counters")
            for seq in rows + [data["bias"], data["next_forecast"]] + ([features] if features is not None else []):
                if any(type(x) not in (int, float) or not math.isfinite(x) for x in seq):
                    raise ValueError("non-finite predictor state")
            if any(not 0 <= x <= 1 for x in data["next_forecast"]):
                raise ValueError("invalid forecast values")
            obj.weights = [list(row) for row in rows]
            obj.bias = list(data["bias"])
            obj.last_features = list(features) if features is not None else None
            obj.next_forecast = list(data["next_forecast"])
            obj.predicted_steps = data["predicted_steps"]
            obj.error_sum = data["error_sum"]
            return obj
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError("malformed predictor snapshot") from exc

    def save(self, path: str | Path) -> None:
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.to_dict(), allow_nan=False, separators=(",", ":"))
        if len(payload.encode("utf-8")) > Brain.MAX_STATE_BYTES:
            raise ValueError("predictor snapshot too large")
        temp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=dest.parent,
                                             prefix=".predictor-", suffix=".tmp", delete=False) as stream:
                temp_path = stream.name
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, dest)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    @classmethod
    def load(cls, path: str | Path) -> NextInputPredictor:
        path = Path(path)
        if path.stat().st_size > Brain.MAX_STATE_BYTES:
            raise ValueError("predictor snapshot too large")
        def reject_constant(value: str) -> None:
            raise ValueError(f"invalid JSON constant {value}")
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream, parse_constant=reject_constant)
        return cls.from_dict(data)


def prediction_control(*, steps: int = 400, seed: int = 1,
                       config: BrainConfig | None = None) -> dict[str, Any]:
    """Compare pre-update prediction MSE with/without structural growth."""
    from dataclasses import replace

    if type(steps) is not int or not 32 <= steps <= 100_000:
        raise ValueError("steps must be in [32, 100000]")
    cfg = config or BrainConfig()
    if cfg.input_size < 4:
        raise ValueError("prediction experiment needs >= 4 input channels")
    learners = {
        "growth_enabled": NextInputPredictor(Brain(replace(cfg, growth_enabled=True), seed=seed)),
        "fixed_structure": NextInputPredictor(Brain(replace(cfg, growth_enabled=False), seed=seed)),
    }
    losses: dict[str, list[float]] = {key: [] for key in learners}
    for t in range(steps):
        x = [0.0] * cfg.input_size
        phase = t % 2
        x[phase] = 1.0
        x[phase + 2] = 1.0
        for key, learner in learners.items():
            item = learner.step(x)
            if item.mse_before_update is not None:
                losses[key].append(item.mse_before_update)
    window = min(64, max(8, (steps - 1) // 3))
    return {
        "protocol": "alternating_pair_next_input_prequential_mse",
        "steps": steps, "seed": seed,
        "naive_constant_half_mse": 0.25,
        "evaluation": {
            key: {
                "first_window_mse": sum(values[:window]) / window,
                "last_window_mse": sum(values[-window:]) / window,
                "mean_online_mse": sum(values) / len(values),
                "neurons": learners[key].brain.stats()["neurons"],
                "synapses": learners[key].brain.stats()["synapses"],
            } for key, values in losses.items()
        },
        "limitations": (
            "Prequential score on a repeated, in-distribution toy sequence. "
            "Not a generalization or consciousness benchmark; equal runtime is not guaranteed."
        ),
    }
