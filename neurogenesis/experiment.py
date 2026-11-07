"""Reproducible controls for structural growth; not an intelligence benchmark."""

from __future__ import annotations

from dataclasses import replace
from typing import Any
from .brain import Brain, BrainConfig


def compare_growth(*, steps: int = 160, seed: int = 1,
                   config: BrainConfig | None = None) -> dict[str, Any]:
    if type(steps) is not int or not 1 <= steps <= 100_000:
        raise ValueError("steps must be in [1, 100000]")
    original = config or BrainConfig()
    with_growth = Brain(replace(original, growth_enabled=True), seed=seed)
    fixed = Brain(replace(original, growth_enabled=False), seed=seed)
    pattern_count = min(original.input_size, 16)
    for step in range(steps):
        pattern_id = (step // 4) % pattern_count
        stimulus = [0.0] * original.input_size
        stimulus[pattern_id] = 1.0
        stimulus[(pattern_id + 2) % original.input_size] = 1.0
        with_growth.step(stimulus)
        fixed.step(stimulus)
    return {
        "protocol": "identical_input_sequence_growth_on_vs_off",
        "steps": steps, "seed": seed,
        "growth_enabled": with_growth.stats(),
        "fixed_structure": fixed.stats(),
        "limitations": (
            "These are structural and activity metrics only. They do not establish "
            "learning quality, language ability, or consciousness."
        ),
    }
