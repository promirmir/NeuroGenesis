"""Frozen chronological ACF ablation on *real persisted semantic tags*.

The earliest 70% of the sequential Qwen-classified observations trains two
matched LIF predictors: structural growth allowed versus fixed structure.
The later 30% is completely unseen during training. ALL readout, synaptic
and structural updates are disabled on the test portion. A persistence and a
constant-half predictor are additional non-neural controls.

Five predeclared random seeds and two consecutive held-out blocks expose
unfavourable outcomes and increased structural cost; there is NO selective
evaluation or neural activation based on these results. These eight binary
semantic categories are not independent human-labelled correctness, nor is
a chronological tail necessarily out-of-distribution or task generalisation.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from typing import Any, Sequence

from .acf import AdaptiveCognitiveFabric, _mse, _sample
from .acf_semantics import AXES, VERSION
from .brain import BrainConfig

DEFAULT_SEEDS = (3, 7, 11, 19, 23)
ROUTES = ("adaptive", "fixed", "persistence", "constant_half")
MAX_ROWS = 2000
MIN_ROWS = 96
TEST_FRACTION = 0.30
REQUIRED_GAIN = 0.002


def _validated_vectors(vectors: Sequence[Sequence[float]]) -> list[list[float]]:
    if (not isinstance(vectors, (tuple, list))
            or not MIN_ROWS <= len(vectors) <= MAX_ROWS):
        raise ValueError("ACF holdout requires 96..2000 chronological observations.")
    samples = [_sample(row, len(AXES)) for row in vectors]
    if any(x not in (0.0, 1.0) for row in samples for x in row):
        raise ValueError("Only genuine eight binary semantic categories are admissible.")
    return samples


def _means(values: list[dict[str, float]]) -> dict[str, float]:
    if not values:
        raise ValueError("No scored unseen events.")
    return {
        route: round(sum(row[route] for row in values) / len(values), 9)
        for route in ROUTES
    }


def evaluate_temporal(
        vectors: Sequence[Sequence[float]], *,
        seeds: tuple[int, ...] = DEFAULT_SEEDS,
        config: BrainConfig | None = None,
        ) -> dict[str, Any]:
    """Immutable 70% train / 30% frozen future, multiple matched initialisations.

    The chronologically last 30% are NOT used to choose seeds, models,
    parameter values, hyperparameters or routes. This is an evaluation only.
    """
    stream = _validated_vectors(vectors)
    if (type(seeds) is not tuple or not 3 <= len(seeds) <= 9
            or any(type(seed) is not int or not 0 <= seed < 2**32
                   for seed in seeds)
            or len(set(seeds)) != len(seeds)):
        raise ValueError("Specify 3..9 distinct uint32 seed initialisations.")
    cfg = config or BrainConfig(
        max_neurons=64, max_synapses=384, max_patterns=128,
        growth_interval=6, novelty_threshold=0.18)
    if not isinstance(cfg, BrainConfig):
        raise ValueError("Invalid bounded model configuration.")
    boundary = int(len(stream) * (1 - TEST_FRACTION))
    training, unseen = stream[:boundary], stream[boundary:]
    if len(training) < 64 or len(unseen) < 28:
        raise ValueError("Insufficient training/heldout observations.")
    half = len(unseen) // 2
    evaluations: list[dict[str, Any]] = []
    all_holdout = []
    any_grown = False
    for seed in seeds:
        fabric = AdaptiveCognitiveFabric(config=cfg, seed=seed)
        for row in training:
            fabric.observe(row)
        adaptive, fixed = fabric.adaptive, fabric.fixed
        structure_before = {
            "adaptive_neurons": len(adaptive.brain.voltages),
            "fixed_neurons": len(fixed.brain.voltages),
            "adaptive_synapses": len(adaptive.brain.synapses),
            "fixed_synapses": len(fixed.brain.synapses),
            "adaptive_grown": adaptive.brain.total_grown,
            "fixed_grown": fixed.brain.total_grown,
        }
        if (structure_before["fixed_neurons"] != cfg.initial_neurons
                or structure_before["fixed_grown"] != 0):
            raise RuntimeError("Fixed-structure control was not held fixed.")
        any_grown |= structure_before["adaptive_grown"] > 0

        # We read the forecast BEFORE advancing any model on the heldout
        # target. No row may influence weights, patterns or topology.
        previous = training[-1]
        scores: list[dict[str, float]] = []
        adaptive_learned = (
            json.dumps(adaptive.weights, separators=(",", ":")),
            json.dumps(adaptive.bias, separators=(",", ":")),
            json.dumps(adaptive.brain.to_dict()["synapses"],
                       sort_keys=True, separators=(",", ":")),
            json.dumps(adaptive.brain.patterns, separators=(",", ":")),
        )
        fixed_learned = (
            json.dumps(fixed.weights, separators=(",", ":")),
            json.dumps(fixed.bias, separators=(",", ":")),
            json.dumps(fixed.brain.to_dict()["synapses"],
                       sort_keys=True, separators=(",", ":")),
            json.dumps(fixed.brain.patterns, separators=(",", ":")),
        )
        for target in unseen:
            scores.append({
                "adaptive": _mse(adaptive.next_forecast, target),
                "fixed": _mse(fixed.next_forecast, target),
                "persistence": _mse(previous, target),
                "constant_half": _mse([0.5] * len(AXES), target),
            })
            adaptive.step(target, learn=False)
            fixed.step(target, learn=False)
            previous = target
        if (adaptive_learned != (
                json.dumps(adaptive.weights, separators=(",", ":")),
                json.dumps(adaptive.bias, separators=(",", ":")),
                json.dumps(adaptive.brain.to_dict()["synapses"],
                           sort_keys=True, separators=(",", ":")),
                json.dumps(adaptive.brain.patterns, separators=(",", ":")))
                or fixed_learned != (
                json.dumps(fixed.weights, separators=(",", ":")),
                json.dumps(fixed.bias, separators=(",", ":")),
                json.dumps(fixed.brain.to_dict()["synapses"],
                           sort_keys=True, separators=(",", ":")),
                json.dumps(fixed.brain.patterns, separators=(",", ":")))):
            raise RuntimeError("An allegedly frozen holdout modified learned parameters.")
        structure_after = {
            "adaptive_neurons": len(adaptive.brain.voltages),
            "fixed_neurons": len(fixed.brain.voltages),
            "adaptive_synapses": len(adaptive.brain.synapses),
            "fixed_synapses": len(fixed.brain.synapses),
            "adaptive_grown": adaptive.brain.total_grown,
            "fixed_grown": fixed.brain.total_grown,
        }
        if structure_after != structure_before:
            raise RuntimeError("Holdout neural topology changed.")
        global_mse = _means(scores)
        evaluations.append({
            "seed": seed,
            "frozen_future_mean_mse": global_mse,
            "frozen_future_first_half_mse": _means(scores[:half]),
            "frozen_future_second_half_mse": _means(scores[half:]),
            "adaptive_advantage_vs_fixed": round(
                global_mse["fixed"] - global_mse["adaptive"], 9),
            "adaptive_advantage_vs_persistence": round(
                global_mse["persistence"] - global_mse["adaptive"], 9),
            "training_structure": structure_before,
            "holdout_structure_unchanged": structure_before == structure_after,
            "extra_neurons_relative_to_fixed": (
                structure_before["adaptive_neurons"]
                - structure_before["fixed_neurons"]),
            "extra_synapses_relative_to_fixed": (
                structure_before["adaptive_synapses"]
                - structure_before["fixed_synapses"]),
        })
        all_holdout.extend(scores)
    pooled = _means(all_holdout)
    per_seed = [row["adaptive_advantage_vs_fixed"] for row in evaluations]
    first = [row["frozen_future_first_half_mse"] for row in evaluations]
    second = [row["frozen_future_second_half_mse"] for row in evaluations]
    # A predeclared, strict descriptive gate, not statistical proof:
    # all seeds and both chronological blocks must beat BOTH controls.
    blocks_won = all(
        sum(x["adaptive"] for x in block) < min(
            sum(x["fixed"] for x in block),
            sum(x["persistence"] for x in block))
        for block in (first, second))
    gate = (
        any_grown
        and all(row["adaptive_advantage_vs_fixed"] >= REQUIRED_GAIN
                and row["adaptive_advantage_vs_persistence"] >= REQUIRED_GAIN
                for row in evaluations)
        and blocks_won)
    return {
        "protocol": "acf_real_semantic_frozen_future_multiseed_v1",
        "observations": len(stream),
        "train_count": len(training),
        "unseen_future_count": len(unseen),
        "chronological_split": "first_70_percent_train_last_30_percent_frozen",
        "seeds": list(seeds),
        "per_seed": evaluations,
        "pooled_frozen_future_mse": pooled,
        "adaptive_advantage_vs_fixed_all_seeds": per_seed,
        "structural_growth_observed_in_training": any_grown,
        "predeclared_descriptive_numeric_gate_passed": gate,
        "predeclared_min_gain": REQUIRED_GAIN,
        "all_training_readout_synapses_patterns_and_topology_frozen_on_test": True,
        "comparison_resource_matched": False,
        "multiple_seed_events_statistically_independent": False,
        "human_label_truth_verified": False,
        "out_of_distribution_guaranteed": False,
        "language_reasoning_improvement_proven": False,
        "neural_architecture_promoted": False,
        "user_data_or_Qwen_weights_modified": False,
        "limitations": (
            "Observed 8 binary Qwen-tagged categories only. Same chronological "
            "stream and repeated seeds are correlated; a positive numerical "
            "gate is descriptive, NOT a p-value or proof of transferable "
            "intelligence. Growth consumes more neurons/synapses and is NOT "
            "compute-matched to the fixed-size control. No learning occurs "
            "on heldout events, but recurrent neural dynamics evolve."
        ),
    }


def evaluate_private_ledger(path: Path, *,
                            limit: int = MAX_ROWS) -> dict[str, Any]:
    """Require a local immutable snapshot of genuine existing semantic tags."""
    if (not isinstance(path, Path) or not path.is_file()
            or path.is_symlink() or type(limit) is not int
            or not MIN_ROWS <= limit <= MAX_ROWS):
        raise ValueError("Existing regular private semantic SQLite and bounded limit required.")
    uri = path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=8)) as con:
        con.execute("PRAGMA query_only=ON")
        first_version = int(con.execute("PRAGMA data_version").fetchone()[0])
        rows = con.execute(
            "SELECT id,features,tagger FROM observations "
            "ORDER BY id ASC LIMIT ?", (limit + 1,)).fetchall()
        if len(rows) > limit:
            raise ValueError("Existing semantic history exceeds selected bound; no truncating heldout.")
        if len(rows) < MIN_ROWS:
            raise ValueError("Insufficient actual semantic observations to test.")
        observations: list[list[float]] = []
        preceding_id = 0
        for event_id, raw, tagger in rows:
            if (type(event_id) is not int or event_id <= preceding_id
                    or type(raw) is not str or len(raw) > 1024
                    or tagger != VERSION):
                raise ValueError("Nonmonotonic or non-pinned semantic observations.")
            preceding_id = event_id
            try:
                data = json.loads(raw, parse_constant=lambda _x: (_ for _ in ()).throw(
                    ValueError("Nonfinite semantic tag.")))
            except json.JSONDecodeError as exc:
                raise ValueError("Malformed private semantic observation.") from exc
            observations.append(_sample(data, len(AXES)))
        if any(v not in (0.0, 1.0) for x in observations for v in x):
            raise ValueError("Invalid non-binary semantic event.")
        before_hash = hashlib.sha256(json.dumps(
            rows, separators=(",", ":")).encode("utf-8")).hexdigest()
        report = evaluate_temporal(observations)
        again = con.execute(
            "SELECT id,features,tagger FROM observations "
            "ORDER BY id ASC LIMIT ?", (limit + 1,)).fetchall()
        if (first_version != int(con.execute("PRAGMA data_version").fetchone()[0])
                or before_hash != hashlib.sha256(json.dumps(
                    again, separators=(",", ":")).encode("utf-8")).hexdigest()):
            raise ValueError("Semantic SQLite changed during frozen evaluation.")
    report["semantic_ledger_sha256"] = before_hash
    report["private_sqlite_read_only_verified"] = True
    report["private_text_not_read_or_emitted"] = True
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Private chronological frozen ACF vs fixed LIF, persistence and constant on actual Qwen tags")
    parser.add_argument("--semantic-sqlite", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=MAX_ROWS)
    args = parser.parse_args(argv)
    try:
        report = evaluate_private_ledger(args.semantic_sqlite, limit=args.limit)
    except (OSError, ValueError, RuntimeError, sqlite3.DatabaseError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True,
                     indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
