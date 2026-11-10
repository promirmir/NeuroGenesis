"""Bounded, measurable self-tuning of the real neural predictor.

Research candidate: this tunes existing learning parameters, *not* source code,
semantic cognition, artificial consciousness or autonomous internet use.
Selection and audit streams are intentionally disjoint responsibilities; the
caller must supply fresh, independent sequences for each cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from statistics import mean
from typing import Any, Sequence

from .predictor import NextInputPredictor


@dataclass(frozen=True)
class DevelopmentLimits:
    """Predeclared acceptance and resource limits, never optimized by the agent."""

    min_gain: float = 0.0001
    max_guard_regression: float = 0.002
    max_neurons_increase: int = 0
    max_synapses_increase: int = 0
    max_samples_per_stream: int = 1024
    max_trials: int = 5

    def __post_init__(self) -> None:
        for name in ("min_gain", "max_guard_regression"):
            value = getattr(self, name)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or value > 1:
                raise ValueError(f"invalid {name}")
        for name in ("max_neurons_increase", "max_synapses_increase"):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= 4096:
                raise ValueError(f"invalid {name}")
        if type(self.max_samples_per_stream) is not int or not 8 <= self.max_samples_per_stream <= 4096:
            raise ValueError("invalid max_samples_per_stream")
        if type(self.max_trials) is not int or not 2 <= self.max_trials <= 5:
            raise ValueError("invalid max_trials")


def _checked_stream(stream: Sequence[Sequence[float]], width: int, *,
                    name: str, capacity: int) -> tuple[tuple[float, ...], ...]:
    if not isinstance(stream, (tuple, list)) or not 8 <= len(stream) <= capacity:
        raise ValueError(f"{name}: require 8..{capacity} input vectors")
    prepared = []
    for sample in stream:
        if not isinstance(sample, (tuple, list)) or len(sample) != width:
            raise ValueError(f"{name}: incorrect sample shape")
        if any(type(x) not in (float, int) or not math.isfinite(x) or not 0 <= x <= 1
               for x in sample):
            raise ValueError(f"{name}: invalid input values")
        prepared.append(tuple(float(x) for x in sample))
    return tuple(prepared)


def _score(model: NextInputPredictor,
           stream: tuple[tuple[float, ...], ...]) -> float:
    # Each probe starts from an isolated saved state; learn=False now freezes
    # BOTH the readout AND synaptic/topological learning. Dynamic voltages
    # and spikes still evolve for authentic inference on unseen examples.
    clone = NextInputPredictor.from_dict(model.to_dict())
    errors = []
    for index, sample in enumerate(stream):
        outcome = clone.step(sample, learn=False)
        if index > 0 and outcome.mse_before_update is not None:
            errors.append(outcome.mse_before_update)
    return mean(errors)


def _train(model: NextInputPredictor,
           stream: tuple[tuple[float, ...], ...]) -> NextInputPredictor:
    clone = NextInputPredictor.from_dict(model.to_dict())
    for sample in stream:
        clone.step(sample)
    return clone


def _options(model: NextInputPredictor) -> list[tuple[str, float, float]]:
    rate = model.learning_rate
    plastic = model.brain.config.plasticity_rate
    raw = [
        ("incumbent", rate, plastic),
        ("faster_readout", min(1.0, rate * 2), plastic),
        ("slower_readout", max(0.0001, rate / 2), plastic),
        ("stronger_plasticity", rate, min(1.0, plastic * 1.5)),
        ("weaker_plasticity", rate, max(0.0001, plastic / 1.5)),
    ]
    used = set()
    result = []
    for name, lr, stdp in raw:
        if (lr, stdp) not in used:
            result.append((name, lr, stdp))
            used.add((lr, stdp))
    return result


def run_self_development_cycle(
    current: NextInputPredictor,
    *,
    training: Sequence[Sequence[float]],
    selection: Sequence[Sequence[float]],
    audit: Sequence[Sequence[float]],
    retained_skill: Sequence[Sequence[float]],
    limits: DevelopmentLimits | None = None,
) -> tuple[NextInputPredictor, dict[str, Any]]:
    """Select a bounded learning change with a separate final audit.

    If the guard or independent audit fails, returns a bitwise-identical clone
    of the original *untrained* model. New knowledge is not irreversibly applied
    to existing snapshots or to the SQLite ledger. Future real-world callers
    must bring fresh streams and not recycle the audit set across cycles.
    """
    if not isinstance(current, NextInputPredictor):
        raise TypeError("current must be a NextInputPredictor")
    if limits is None:
        limits = DevelopmentLimits()
    if not isinstance(limits, DevelopmentLimits):
        raise TypeError("limits must be DevelopmentLimits")

    width = current.brain.config.input_size
    train = _checked_stream(training, width, name="training", capacity=limits.max_samples_per_stream)
    choose = _checked_stream(selection, width, name="selection", capacity=limits.max_samples_per_stream)
    confirm = _checked_stream(audit, width, name="audit", capacity=limits.max_samples_per_stream)
    guard = _checked_stream(retained_skill, width, name="retained_skill", capacity=limits.max_samples_per_stream)
    if choose == confirm or train == choose or train == confirm:
        raise ValueError("training, selection and audit must be distinct streams")
    before = current.to_dict()
    old_guard_score = _score(current, guard)

    options = _options(current)[:limits.max_trials]
    trials = []
    learned = []
    for name, lr, stdp in options:
        clone = NextInputPredictor.from_dict(before)
        clone.learning_rate = lr
        clone.brain.config = replace(clone.brain.config, plasticity_rate=stdp)
        trained = _train(clone, train)
        score = _score(trained, choose)
        trials.append({"candidate": name, "readout_learning_rate": lr,
                       "synaptic_plasticity_rate": stdp, "selection_mse": score,
                       "neurons": len(trained.brain.voltages),
                       "synapses": len(trained.brain.synapses)})
        learned.append(trained)

    baseline = learned[0]
    baseline_selection = trials[0]["selection_mse"]
    # We explicitly choose based on selection only; audit does not influence
    # candidate rank (one final audit for the single chosen challenger).
    selection_eligible = [i for i in range(1, len(trials))
        if (trials[i]["selection_mse"] <= baseline_selection - limits.min_gain
            and trials[i]["neurons"] <= trials[0]["neurons"] + limits.max_neurons_increase
            and trials[i]["synapses"] <= trials[0]["synapses"] + limits.max_synapses_increase)]
    winner = min(selection_eligible, key=lambda i: trials[i]["selection_mse"]) if selection_eligible else None
    report: dict[str, Any] = {
        "protocol": "neurogenesis_bounded_self_development_v2_frozen_audit",
        "selected_candidate": None if winner is None else trials[winner]["candidate"],
        "trials": trials,
        "precycle_retained_skill_mse": old_guard_score,
        "limits": {name: getattr(limits, name) for name in limits.__dataclass_fields__},
        "promoted": False,
        "reason": "no_selection_gain" if winner is None else "pending_audit",
        "limitations": ("Only bounded neural/readout parameter tuning on predeclared samples. "
                        "Holdout evaluation freezes synapses, patterns, growth and readout; "
                        "it retains dynamic LIF electrical activity but is not AGI. "
                        "Selection and audit must be independent and audit data never reused."),
    }
    if winner is not None:
        proposal = learned[winner]
        candidate_audit = _score(proposal, confirm)
        baseline_audit = _score(baseline, confirm)
        candidate_guard = _score(proposal, guard)
        baseline_guard = _score(baseline, guard)
        selection_gain = baseline_selection - trials[winner]["selection_mse"]
        audit_gain = baseline_audit - candidate_audit
        report.update({"selection_gain_mse": selection_gain,
                       "baseline_audit_mse": baseline_audit,
                       "candidate_audit_mse": candidate_audit,
                       "audit_gain_mse": audit_gain,
                       "baseline_retained_skill_mse": baseline_guard,
                       "candidate_retained_skill_mse": candidate_guard})
        if audit_gain < limits.min_gain:
            report["reason"] = "independent_audit_failed"
        elif candidate_guard > min(old_guard_score, baseline_guard) + limits.max_guard_regression:
            report["reason"] = "retained_skill_regressed"
        else:
            report["promoted"] = True
            report["reason"] = "measured_gain_no_regression"
            assert current.to_dict() == before, "original state mutated during experiments"
            return proposal, report
    assert current.to_dict() == before, "original state mutated during experiments"
    return NextInputPredictor.from_dict(before), report
