"""Bounded cognitive-capacity experiments and local hardware discovery.

This is a research candidate, NOT autonomous hardware provisioning, GPU
acceleration, distributed execution, or a general-intelligence mechanism.
It never mutates a caller's trained brain or authorizes network access.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from statistics import mean
from time import monotonic
from typing import Any, Sequence

from .brain import Brain
from .predictor import NextInputPredictor


@dataclass(frozen=True)
class ResourceBudget:
    """Operator-owned ceilings. Candidates cannot raise these ceilings."""

    max_neurons: int = 256
    max_synapses: int = 2048
    extra_neurons_per_trial: int = 8
    extra_synapses_per_trial: int = 32
    max_samples_per_stream: int = 1024
    max_state_bytes: int = 8_000_000
    max_training_work_units: int = 2_000_000
    max_work_ratio: float = 2.0
    max_trial_seconds: float = 30.0
    min_selection_gain: float = 0.0001
    min_audit_gain: float = 0.0001
    max_guard_regression: float = 0.002

    def __post_init__(self) -> None:
        boundaries = {
            "max_neurons": (2, 4096),
            "max_synapses": (2, 100_000),
            "extra_neurons_per_trial": (0, 4096),
            "extra_synapses_per_trial": (0, 100_000),
            "max_samples_per_stream": (8, 4096),
            "max_state_bytes": (1_024, Brain.MAX_STATE_BYTES),
            "max_training_work_units": (1_000, 100_000_000),
        }
        for key, (low, high) in boundaries.items():
            x = getattr(self, key)
            if type(x) is not int or not low <= x <= high:
                raise ValueError(f"{key} must be an integer in [{low}, {high}]")
        for key, low, high in (
            ("max_work_ratio", 1.0, 100.0),
            ("max_trial_seconds", 0.001, 3600.0),
            ("min_selection_gain", 0.0, 1.0),
            ("min_audit_gain", 0.0, 1.0),
            ("max_guard_regression", 0.0, 1.0),
        ):
            x = getattr(self, key)
            if type(x) not in (int, float) or not math.isfinite(x) or not low <= x <= high:
                raise ValueError(f"{key} must be finite in [{low}, {high}]")


def hardware_profile(*, probe_cuda: bool = False) -> dict[str, Any]:
    """Read-only local discovery. No device allocation or external network.

    Available RAM may be unknown. CUDA is *not checked* by default, because
    importing an optional large framework can slow the one-click application.
    """
    if type(probe_cuda) is not bool:
        raise ValueError("probe_cuda must be boolean")
    threads = os.cpu_count() or 1
    if type(threads) is not int or threads < 1:
        threads = 1
    total_ram: int | None = None
    if sys.platform == "win32":
        try:
            import ctypes

            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong),
                            ("memory_load", ctypes.c_ulong),
                            ("total_physical", ctypes.c_ulonglong),
                            ("available_physical", ctypes.c_ulonglong),
                            ("total_page", ctypes.c_ulonglong),
                            ("available_page", ctypes.c_ulonglong),
                            ("total_virtual", ctypes.c_ulonglong),
                            ("available_virtual", ctypes.c_ulonglong),
                            ("available_extended", ctypes.c_ulonglong)]
            record = MemoryStatus()
            record.length = ctypes.sizeof(MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(record)):
                total_ram = int(record.total_physical)
        except (AttributeError, OSError, ValueError):
            pass
    elif hasattr(os, "sysconf"):
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_bytes = os.sysconf("SC_PAGE_SIZE")
            if type(pages) is int and type(page_bytes) is int and pages > 0 and page_bytes > 0:
                total_ram = pages * page_bytes
        except (ValueError, OSError, AttributeError):
            pass

    cuda_status = "not_checked"
    cuda_devices = 0
    if probe_cuda:
        cuda_status = "unavailable"
        try:
            import torch  # optional; never required for CPU-only operation
            if torch.cuda.is_available():
                cuda_devices = int(torch.cuda.device_count())
                if cuda_devices > 0:
                    cuda_status = "available"
        except (ImportError, OSError, RuntimeError, AttributeError):
            pass
    return {"logical_cpu_threads": threads,
            "physical_ram_bytes": total_ram,
            "cuda_status": cuda_status,
            "cuda_devices": cuda_devices,
            "gpu_backend_implemented": False,
            "distributed_workers": 0,
            "internet_used": False}


def _stream(value: Sequence[Sequence[float]], width: int, *, name: str,
            max_samples: int) -> tuple[tuple[float, ...], ...]:
    if not isinstance(value, (list, tuple)) or not 8 <= len(value) <= max_samples:
        raise ValueError(f"{name}: expected 8..{max_samples} samples")
    rows: list[tuple[float, ...]] = []
    for row in value:
        if not isinstance(row, (list, tuple)) or len(row) != width:
            raise ValueError(f"{name}: wrong sample width")
        if any(type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= 1
               for x in row):
            raise ValueError(f"{name}: invalid input")
        rows.append(tuple(float(x) for x in row))
    return tuple(rows)


def _frozen_score(model: NextInputPredictor,
                  samples: tuple[tuple[float, ...], ...]) -> float:
    """Measure prequential MSE without changing topology or synaptic weights.

    Only the *clone's* temporal voltages/traces advance. The original model
    remains untouched. Unlike v0.4 learn=False, STDP updates are neutralized
    in this isolated probe and structural changes are disabled.
    """
    clone = NextInputPredictor.from_dict(model.to_dict())
    brain = clone.brain
    max_age = max((edge.age for edge in brain.synapses), default=0)
    brain.config = replace(brain.config, growth_enabled=False,
                           prune_min_age=max_age + len(samples) + 2)
    weights = tuple(edge.weight for edge in brain.synapses)
    scores = []
    for i, x in enumerate(samples):
        result = clone.step(x, learn=False)
        if len(brain.synapses) != len(weights):
            raise AssertionError("frozen probe unexpectedly changed topology")
        for edge, weight in zip(brain.synapses, weights):
            edge.weight = weight
        if i > 0 and result.mse_before_update is not None:
            scores.append(result.mse_before_update)
    return mean(scores)


def _fit(model: NextInputPredictor,
         samples: tuple[tuple[float, ...], ...], *,
         deadline: float, max_work_units: int) -> tuple[NextInputPredictor, int]:
    clone = NextInputPredictor.from_dict(model.to_dict())
    work = 0
    for sample in samples:
        if monotonic() > deadline:
            raise TimeoutError("trial time budget exhausted")
        work += len(clone.brain.voltages) + len(clone.brain.synapses)
        if work > max_work_units:
            raise OverflowError("training work unit budget exhausted")
        clone.step(sample)
    return clone, work


def _size_bytes(model: NextInputPredictor) -> int:
    return len(json.dumps(model.to_dict(), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("utf-8"))


def capacity_trial(
    current: NextInputPredictor,
    *,
    training: Sequence[Sequence[float]],
    selection: Sequence[Sequence[float]],
    audit: Sequence[Sequence[float]],
    retained_skill: Sequence[Sequence[float]],
    budget: ResourceBudget | None = None,
) -> tuple[NextInputPredictor, dict[str, Any]]:
    """Compare bounded expansion against an equally trained incumbent.

    On any veto, return a bitwise-equivalent clone of the original. A positive
    result is a candidate checkpoint, *not* permission to overwrite a live DB.
    Independent audit data must never be recycled across adaptation cycles.
    """
    if not isinstance(current, NextInputPredictor):
        raise TypeError("current must be NextInputPredictor")
    if budget is None:
        budget = ResourceBudget()
    if not isinstance(budget, ResourceBudget):
        raise TypeError("budget must be ResourceBudget")
    cfg = current.brain.config
    if len(current.brain.voltages) > budget.max_neurons or len(current.brain.synapses) > budget.max_synapses:
        raise ValueError("current state exceeds operator resource limits")
    if cfg.max_neurons > budget.max_neurons or cfg.max_synapses > budget.max_synapses:
        raise ValueError("current configured maximum exceeds operator limits")
    if _size_bytes(current) > budget.max_state_bytes:
        raise ValueError("current checkpoint exceeds operator size budget")

    width = cfg.input_size
    train = _stream(training, width, name="training", max_samples=budget.max_samples_per_stream)
    select = _stream(selection, width, name="selection", max_samples=budget.max_samples_per_stream)
    holdout = _stream(audit, width, name="audit", max_samples=budget.max_samples_per_stream)
    guard = _stream(retained_skill, width, name="retained_skill", max_samples=budget.max_samples_per_stream)
    if len({train, select, holdout, guard}) != 4:
        raise ValueError("all four experiment streams must be distinct")

    state = current.to_dict()
    stamp = hashlib.sha256(json.dumps(state, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()
    original = NextInputPredictor.from_dict(state)
    cap_neurons = min(budget.max_neurons, cfg.max_neurons + budget.extra_neurons_per_trial)
    cap_synapses = min(budget.max_synapses, cfg.max_synapses + budget.extra_synapses_per_trial)
    result: dict[str, Any] = {
        "protocol": "neurogenesis_bounded_capacity_v1",
        "source_state_sha256": stamp,
        "accepted": False,
        "reason": "not_evaluated",
        "budget": asdict(budget),
        "old_neuron_limit": cfg.max_neurons,
        "old_synapse_limit": cfg.max_synapses,
        "proposed_neuron_limit": cap_neurons,
        "proposed_synapse_limit": cap_synapses,
        "limitations": (
            "Synthetic paired local experiment, not evidence of human intelligence. "
            "A larger network is not automatically more capable. "
            "Audit streams must be fresh for each trial; CPU work units are a proxy, "
            "not hardware energy. This function does not deploy GPU or workers."
        )
    }

    if cap_neurons == cfg.max_neurons and cap_synapses == cfg.max_synapses:
        result["reason"] = "no_budget_for_growth"
        return original, result
    started = monotonic()
    deadline = started + budget.max_trial_seconds
    try:
        incumbent, old_work = _fit(original, train, deadline=deadline,
                                   max_work_units=budget.max_training_work_units)
        trial = NextInputPredictor.from_dict(state)
        trial.brain.config = replace(cfg, max_neurons=cap_neurons,
                                     max_synapses=cap_synapses, growth_enabled=True)
        challenger, extra_work = _fit(trial, train, deadline=deadline,
                                      max_work_units=budget.max_training_work_units)
    except (TimeoutError, OverflowError) as exc:
        result["reason"] = ("time_budget_exceeded" if isinstance(exc, TimeoutError)
                            else "training_work_budget_exceeded")
        return original, result
    result.update({"incumbent_neurons": len(incumbent.brain.voltages),
                   "challenger_neurons": len(challenger.brain.voltages),
                   "incumbent_synapses": len(incumbent.brain.synapses),
                   "challenger_synapses": len(challenger.brain.synapses),
                   "compute_work_ratio": extra_work / max(1, old_work),
                   "checkpoint_bytes": _size_bytes(challenger)})
    if monotonic() - started > budget.max_trial_seconds:
        result["reason"] = "time_budget_exceeded"
        return original, result
    if (len(challenger.brain.voltages) <= len(incumbent.brain.voltages)
        and len(challenger.brain.synapses) <= len(incumbent.brain.synapses)):
        result["reason"] = "no_structural_change"
        return original, result
    if (result["compute_work_ratio"] > budget.max_work_ratio or
        result["checkpoint_bytes"] > budget.max_state_bytes or
        len(challenger.brain.voltages) > budget.max_neurons or
        len(challenger.brain.synapses) > budget.max_synapses):
        result["reason"] = "resource_budget_exceeded"
        return original, result

    old_selection = _frozen_score(incumbent, select)
    new_selection = _frozen_score(challenger, select)
    result.update({"incumbent_selection_mse": old_selection,
                   "challenger_selection_mse": new_selection,
                   "selection_gain_mse": old_selection - new_selection})
    if monotonic() - started > budget.max_trial_seconds:
        result["reason"] = "time_budget_exceeded"
        return original, result
    if old_selection - new_selection < budget.min_selection_gain:
        result["reason"] = "no_selection_gain"
        return original, result
    old_audit = _frozen_score(incumbent, holdout)
    new_audit = _frozen_score(challenger, holdout)
    old_guard = _frozen_score(incumbent, guard)
    new_guard = _frozen_score(challenger, guard)
    current_guard = _frozen_score(original, guard)
    result.update({"incumbent_audit_mse": old_audit,
                   "challenger_audit_mse": new_audit,
                   "audit_gain_mse": old_audit - new_audit,
                   "incumbent_retained_mse": old_guard,
                   "challenger_retained_mse": new_guard,
                   "pretrial_retained_mse": current_guard})
    if monotonic() - started > budget.max_trial_seconds:
        result["reason"] = "time_budget_exceeded"
    elif old_audit - new_audit < budget.min_audit_gain:
        result["reason"] = "independent_audit_failed"
    elif new_guard > min(old_guard, current_guard) + budget.max_guard_regression:
        result["reason"] = "retained_skill_regressed"
    else:
        result["accepted"] = True
        result["reason"] = "measured_gain_within_budget"
        assert current.to_dict() == state, "live brain mutated"
        return challenger, result
    assert current.to_dict() == state, "live brain mutated"
    return original, result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local resource discovery for NeuroGenesis")
    parser.add_argument("--probe-cuda", action="store_true", help="query optional CUDA support (may import PyTorch)")
    args = parser.parse_args(argv)
    print(json.dumps(hardware_profile(probe_cuda=args.probe_cuda), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
