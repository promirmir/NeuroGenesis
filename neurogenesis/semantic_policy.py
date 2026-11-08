"""Measured, reversible semantic ACF influence on ONE real agent action.

The action is restricted to read-only *proactive LOCAL knowledge retrieval*
for a predicted NEXT topic. No network, file writing, raw messages, tool
execution, source injection into model, or automatic acceptance of results.

A structural neural model may influence that action ONLY if its measured
causal MSE is demonstrably lower than all fixed/non-neural controls and its
prediction is sufficiently decisive. Otherwise the policy ABSTAINS.

This is NOT a demonstrated conversation improvement. A semantic category
forecast is not a validated fact, and prefetch is not used to answer a later
question unless independently re-retrieved/verified for that question.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from .acf import AdaptiveCognitiveFabric
from .acf_semantics import AXES
from .local_knowledge import LocalKnowledge

MIN_EVENTS = 65  # 64 strictly prequential scored predictions.
MIN_ABSOLUTE_MSE_GAIN = 0.005
MIN_RELATIVE_MSE_GAIN = 0.05
MIN_AXIS_PROBABILITY = 0.70
MIN_AXIS_MARGIN = 0.12

# Deterministic, auditable local FTS queries — *not* hidden web searches.
# 'facts' and 'dialogue' are too broad to justify speculative prefetch.
QUERIES = {
    "science": "nauka badania eksperyment fizyka science",
    "mathematics": "matematyka obliczenia równania mathematics",
    "programming": "programowanie kod Python software programming",
    "engineering": "technologia konstrukcja urządzenie engineering",
    "planning": "projekt strategia planowanie harmonogram planning",
    "creativity": "projektowanie twórczość design kreatywność",
}


@dataclass(frozen=True)
class SemanticDecision:
    status: str
    predicted_axis: str | None
    expected_activation: float | None
    measured_advantage: float | None
    scored_predictions: int
    baseline_mse: float | None
    adaptive_mse: float | None
    local_sources_consulted: int

    def public(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "predicted_axis": self.predicted_axis,
            "expected_activation": self.expected_activation,
            "measured_advantage": self.measured_advantage,
            "scored_predictions": self.scored_predictions,
            "baseline_mse": self.baseline_mse,
            "adaptive_mse": self.adaptive_mse,
            "local_sources_consulted": self.local_sources_consulted,
            "only_local_read_only_action": True,
            "improves_user_tasks_proven": False,
        }


def _stop(name: str, n: int, neural: float | None = None,
          baseline: float | None = None) -> SemanticDecision:
    gain = (round(baseline - neural, 8)
            if neural is not None and baseline is not None else None)
    return SemanticDecision(name, None, None, gain, n, baseline, neural, 0)


def decide(fabric: AdaptiveCognitiveFabric) -> SemanticDecision:
    """Use prior error only, never the next true sensory value."""
    if not isinstance(fabric, AdaptiveCognitiveFabric):
        raise ValueError("Only persisted validated ACF can vote.")
    summary = fabric.self_model()
    n = summary["scored_predictions"]
    if n < MIN_EVENTS - 1:
        return _stop("insufficient_real_observations", n)
    errors = summary["route_mean_mse_recent"]
    neural = errors["adaptive"]
    controls = [errors[k] for k in ("fixed", "persistence", "constant_half")]
    if (neural is None or any(v is None or not math.isfinite(v)
                              for v in controls)
            or not math.isfinite(neural)):
        return _stop("no_valid_causal_comparison", n)
    baseline = min(controls)
    if fabric.selected_route != "adaptive":
        return _stop("adaptive_not_selected_by_actual_loss", n, neural, baseline)
    if (baseline <= 0 or
            neural + MIN_ABSOLUTE_MSE_GAIN >= baseline or
            (baseline - neural) / baseline < MIN_RELATIVE_MSE_GAIN):
        return _stop("no_measured_adaptive_advantage", n, neural, baseline)
    forecast = fabric.next_forecast
    if len(forecast) != len(AXES):
        raise ValueError("Unexpected semantic forecast dimensions.")
    if any(type(x) not in (int, float) or
           not math.isfinite(x) or not 0 <= x <= 1 for x in forecast):
        raise ValueError("Nonfinite or invalid next semantic forecast.")
    ranked = sorted(range(len(AXES)), key=lambda i: (-forecast[i], i))
    winner, runner_up = ranked[0], ranked[1]
    axis = AXES[winner]
    if (axis not in QUERIES or forecast[winner] < MIN_AXIS_PROBABILITY
            or forecast[winner] - forecast[runner_up] < MIN_AXIS_MARGIN):
        return _stop("low_confidence_or_unsuitable_topic", n, neural, baseline)
    return SemanticDecision(
        "eligible_for_local_prefetch", axis, round(forecast[winner], 6),
        round(baseline - neural, 8), n, baseline, neural, 0)


def prepare_local_sources(
        fabric: AdaptiveCognitiveFabric,
        knowledge: LocalKnowledge) -> SemanticDecision:
    """Actually perform a bounded local read only if the neural gate passes.

    The retrieved passages remain entirely inside the existing approved
    LocalKnowledge DB; no body text, private file names or URLs are returned
    to the UI or included in a model prompt.
    """
    if not isinstance(knowledge, LocalKnowledge):
        raise ValueError("Requires existing approved local knowledge store.")
    choice = decide(fabric)
    if choice.status != "eligible_for_local_prefetch":
        return choice
    # LocalKnowledge's own FTS query is the ONLY side-effect-free action.
    passages = knowledge.retrieve(QUERIES[choice.predicted_axis], limit=3)
    return SemanticDecision(
        "local_sources_prepared" if passages else "approved_sources_missing",
        choice.predicted_axis, choice.expected_activation,
        choice.measured_advantage, choice.scored_predictions,
        choice.baseline_mse, choice.adaptive_mse, len(passages))
