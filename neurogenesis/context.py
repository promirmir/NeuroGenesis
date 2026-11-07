"""Autonomous local learning of temporal sensory context from spiking traces.

ContextualNextInputPredictor is a *readout* of NeuroGenesis's real spiking
substrate, not a generative language model. Every observation trains a bounded,
online, prequential next-sensory predictor using recent hashed stimuli and
neuron activation traces. No raw text or external data is read or stored here.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence


BINS = 8
INPUT_FEATURES = 1 + BINS * 3  # bias, present cue, preceding cue, neural traces


@dataclass(frozen=True)
class ContextStep:
    observations: int
    mse_before_update: float | None
    next_forecast: tuple[float, ...]


class ContextualNextInputPredictor:
    """Bounded online delta-rule readout with recurrent sensory context.

    It autonomously learns sequential regularities, not word meanings.
    History and neural readout can be independently ablated for research.
    """

    SCHEMA_VERSION = 1
    MAX_SNAPSHOT_BYTES = 16 * 1024 * 1024

    def __init__(self, width: int = 8, *, learning_rate: float = 0.65,
                 use_history: bool = True, use_neural: bool = True) -> None:
        if type(width) is not int or not 1 <= width <= 4096:
            raise ValueError("invalid sensory width")
        if (type(learning_rate) not in (int, float)
                or not math.isfinite(learning_rate)
                or not 0 < learning_rate <= 1):
            raise ValueError("invalid context learning rate")
        if type(use_history) is not bool or type(use_neural) is not bool:
            raise ValueError("ablation settings must be boolean")
        self.width = width
        self.learning_rate = float(learning_rate)
        self.use_history = use_history
        self.use_neural = use_neural
        self.weights = [[0.5] + [0.0] * (INPUT_FEATURES - 1)
                        for _ in range(width)]
        self.previous_cue = [0.0] * BINS
        self.last_features: list[float] | None = None
        self.next_forecast = [0.5] * width
        self.observations = 0
        self.scored = 0
        self.error_sum = 0.0
        self.last_mse: float | None = None

    @staticmethod
    def _validate_values(values: Sequence[float], *, minimum: float,
                         maximum: float, label: str) -> list[float]:
        if len(values) == 0 or len(values) > 4096:
            raise ValueError("invalid " + label + " length")
        out: list[float] = []
        for value in values:
            if (type(value) not in (int, float) or not math.isfinite(value)
                    or not minimum <= value <= maximum):
                raise ValueError("invalid " + label + " values")
            out.append(float(value))
        return out

    @staticmethod
    def _fold(values: Sequence[float]) -> list[float]:
        bins = [0.0] * BINS
        for index, value in enumerate(values):
            slot = index % BINS
            bins[slot] = max(bins[slot], value)
        return bins

    @staticmethod
    def _activity(traces: Sequence[float]) -> list[float]:
        bins = [0.0] * BINS
        counts = [0] * BINS
        for i, value in enumerate(traces):
            slot = i % BINS
            bins[slot] += min(1.0, value / 5.0)
            counts[slot] += 1
        return [bins[i] / counts[i] if counts[i] else 0.0
                for i in range(BINS)]

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def observe(self, stimulus: Sequence[float], neural_traces: Sequence[float],
                *, learn: bool = True) -> ContextStep:
        """Score *before* training on the arriving stimulus, then update.

        Neural traces must belong to the brain **after** consuming this
        stimulus; they are used ONLY for forecasting the *next* stimulus.
        """
        if type(learn) is not bool:
            raise ValueError("learn must be boolean")
        x = self._validate_values(stimulus, minimum=0.0, maximum=1.0,
                                  label="sensory")
        if len(x) != self.width:
            raise ValueError("sensory width mismatch")
        traces = self._validate_values(neural_traces, minimum=0.0,
                                       maximum=5.0, label="neural traces")
        error: float | None = None
        if self.last_features is not None:
            error = sum((prediction - actual) ** 2
                        for prediction, actual in zip(self.next_forecast, x)) / self.width
            # Snapshot the preceding features before updating any parameters.
            if learn:
                normalization = 1.0 + sum(v * v for v in self.last_features)
                for row, actual, prediction in zip(self.weights, x, self.next_forecast):
                    delta = self.learning_rate * (actual - prediction) / normalization
                    for j, activation in enumerate(self.last_features):
                        row[j] = max(-4.0, min(4.0, row[j] + delta * activation))
                self.scored += 1
                self.error_sum += error
                self.last_mse = error
        cue = self._fold(x)
        history = self.previous_cue if self.use_history else [0.0] * BINS
        neural = self._activity(traces) if self.use_neural else [0.0] * BINS
        phi = [1.0] + cue + history + neural
        self.last_features = phi
        self.previous_cue = cue
        self.next_forecast = [self._clamp(sum(w * activation
                                               for w, activation in zip(row, phi)))
                              for row in self.weights]
        self.observations += 1
        return ContextStep(self.observations, error, tuple(self.next_forecast))

    def stats(self) -> dict[str, Any]:
        return {
            "observations": self.observations,
            "scored": self.scored,
            "mean_prequential_mse": (round(self.error_sum / self.scored, 8)
                                     if self.scored else None),
            "last_prequential_mse": (round(self.last_mse, 8)
                                     if self.last_mse is not None else None),
            "uses_temporal_context": self.use_history,
            "uses_real_neural_traces": self.use_neural,
            "stored_raw_text": False,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA_VERSION, "width": self.width,
            "learning_rate": self.learning_rate,
            "use_history": self.use_history, "use_neural": self.use_neural,
            "weights": [row[:] for row in self.weights],
            "previous_cue": self.previous_cue[:],
            "last_features": (self.last_features[:] if self.last_features is not None
                              else None),
            "next_forecast": self.next_forecast[:],
            "observations": self.observations, "scored": self.scored,
            "error_sum": self.error_sum, "last_mse": self.last_mse,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContextualNextInputPredictor:
        if type(data) is not dict or data.get("schema") != cls.SCHEMA_VERSION:
            raise ValueError("invalid contextual predictor schema")
        try:
            model = cls(data["width"], learning_rate=data["learning_rate"],
                        use_history=data["use_history"], use_neural=data["use_neural"])
            weights = data["weights"]
            if type(weights) is not list or len(weights) != model.width:
                raise ValueError("invalid context weight dimensions")
            for row in weights:
                if type(row) is not list or len(row) != INPUT_FEATURES:
                    raise ValueError("invalid context weight shape")
                if any(type(v) not in (int, float) or not math.isfinite(v)
                       or abs(v) > 4 for v in row):
                    raise ValueError("invalid context weights")
            prev = model._validate_values(data["previous_cue"], minimum=0,
                                           maximum=1, label="previous cue")
            forecast = model._validate_values(data["next_forecast"], minimum=0,
                                               maximum=1, label="forecast")
            phi = data["last_features"]
            if phi is not None:
                phi = model._validate_values(phi, minimum=0,
                                              maximum=1, label="last features")
            if len(prev) != BINS or len(forecast) != model.width or (
                    phi is not None and len(phi) != INPUT_FEATURES):
                raise ValueError("context state dimension mismatch")
            seen, scored = data["observations"], data["scored"]
            if (type(seen) is not int or type(scored) is not int or not 0 <= scored <= seen
                    or (phi is None and seen != 0)
                    or (phi is not None and seen == 0)):
                raise ValueError("invalid context counters")
            err = data["error_sum"]
            last = data["last_mse"]
            if (type(err) not in (float, int) or not math.isfinite(err)
                    or err < 0 or err > scored or
                    (last is not None and (type(last) not in (float, int)
                                           or not math.isfinite(last)
                                           or not 0 <= last <= 1))):
                raise ValueError("invalid contextual learning error")
            if scored == 0 and (err != 0 or last is not None):
                raise ValueError("context score missing")
            model.weights = [list(row) for row in weights]
            model.previous_cue = prev
            model.last_features = phi
            model.next_forecast = forecast
            model.observations = seen
            model.scored = scored
            model.error_sum = float(err)
            model.last_mse = float(last) if last is not None else None
            return model
        except (KeyError, TypeError, AttributeError, IndexError, OverflowError) as exc:
            raise ValueError("malformed contextual predictor snapshot") from exc
