"""Leakage-free online Markov baseline for synthetic neural prediction studies.

This module is independent of NeuroGenesis's neural substrate. Predictions are
scored against the incoming stimulus BEFORE fitting the previous transition.
"""

from __future__ import annotations

import math
from typing import Sequence


class OnlineMarkovBaseline:
    """One-step conditional-mean predictor with per-channel prior of 0.5.

    Stimuli are quantized into binary cue signatures; targets remain continuous.
    A single unseen cue predicts 0.5 in every channel. No fitting occurs when
    learn=False. Input validation precedes any state mutation.
    """

    def __init__(self, width: int = 8, *, threshold: float = 0.5) -> None:
        if type(width) is not int or not 1 <= width <= 4096:
            raise ValueError("width must be an integer in [1, 4096]")
        if type(threshold) not in (int, float) or not math.isfinite(threshold) or not 0 < threshold < 1:
            raise ValueError("threshold must be finite and in (0, 1)")
        self.width = width
        self.threshold = float(threshold)
        self._counts: dict[tuple[int, ...], int] = {}
        self._sums: dict[tuple[int, ...], list[float]] = {}
        self._previous_key: tuple[int, ...] | None = None
        self.next_forecast = (0.5,) * width
        self.scored = 0

    def step(self, stimulus: Sequence[float], *, learn: bool = True) -> float | None:
        if type(learn) is not bool:
            raise ValueError("learn must be boolean")
        if len(stimulus) != self.width:
            raise ValueError("incorrect stimulus width")
        values = []
        for value in stimulus:
            if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("stimulus channels must be finite in [0, 1]")
            values.append(float(value))
        loss = None
        if self._previous_key is not None:
            loss = sum((prediction - target) ** 2 for prediction, target in zip(self.next_forecast, values)) / self.width
            self.scored += 1
            if learn:
                key = self._previous_key
                if key not in self._counts:
                    self._counts[key] = 0
                    self._sums[key] = [0.0] * self.width
                self._counts[key] += 1
                for i, value in enumerate(values):
                    self._sums[key][i] += value
        key = tuple(int(value >= self.threshold) for value in values)
        self._previous_key = key
        count = self._counts.get(key, 0)
        self.next_forecast = tuple(value / count for value in self._sums[key]) if count else (0.5,) * self.width
        return loss

    @property
    def learned_cues(self) -> int:
        return len(self._counts)


def constant_half_mse(stimulus: Sequence[float]) -> float:
    """No-information baseline; returns the MSE of a constant 0.5 forecast."""
    if not stimulus:
        raise ValueError("empty stimulus")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in stimulus):
        raise ValueError("stimulus channels must be finite in [0, 1]")
    return sum((0.5 - value) ** 2 for value in stimulus) / len(stimulus)
