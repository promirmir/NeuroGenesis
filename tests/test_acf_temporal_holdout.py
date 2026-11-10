"""Tests for temporally held-out structural ACF evidence, not an AGI benchmark.

All tags below are synthetic test data. The production CLI accepts only an
existing private Qwen semantic observation ledger. No private text is read.
"""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from neurogenesis.acf_semantics import VERSION
from neurogenesis.acf_temporal_holdout import (
    DEFAULT_SEEDS, ROUTES, evaluate_temporal, evaluate_private_ledger)


def pattern_stream(count=112):
    result = []
    for i in range(count):
        v = [0.0] * 8
        v[i % 2] = 1.0
        v[2 + (i // 4) % 4] = 1.0
        result.append(v)
    return result


class TemporalHoldoutTests(unittest.TestCase):
    def test_all_five_seeds_train_then_freeze_whole_unseen_tail(self):
        stream = pattern_stream()
        a = evaluate_temporal(stream)
        b = evaluate_temporal(stream)
        self.assertEqual(a, b)  # no unpinned runtime timing in the evidence
        self.assertEqual(a["seeds"], list(DEFAULT_SEEDS))
        self.assertEqual(a["observations"], len(stream))
        self.assertEqual(a["train_count"] + a["unseen_future_count"],
                         len(stream))
        self.assertEqual(len(a["per_seed"]), 5)
        for record in a["per_seed"]:
            self.assertTrue(record["holdout_structure_unchanged"])
            self.assertEqual(record["training_structure"]["fixed_grown"], 0)
            self.assertEqual(
                record["training_structure"]["fixed_neurons"], 24)
            self.assertEqual(set(record["frozen_future_mean_mse"]), set(ROUTES))
            for mse in record["frozen_future_mean_mse"].values():
                self.assertGreaterEqual(mse, 0.0)
                self.assertLessEqual(mse, 1.0)
        self.assertFalse(a["language_reasoning_improvement_proven"])
        self.assertFalse(a["neural_architecture_promoted"])
        self.assertFalse(a["comparison_resource_matched"])
        self.assertFalse(a["out_of_distribution_guaranteed"])
        self.assertFalse(a["human_label_truth_verified"])
        self.assertFalse(a["multiple_seed_events_statistically_independent"])

    def test_constant_stream_can_grow_once_but_must_not_claim_gain(self):
        # The first observation is novel even in a constant stream, so
        # structural growth by itself is not evidence of generalisation.
        # Persistence predicts constant zeros perfectly and must not be
        # beaten by a neural model with non-negative prediction loss.
        values = [[0.0] * 8 for _ in range(96)]
        report = evaluate_temporal(values, seeds=(1, 2, 3))
        self.assertTrue(report["structural_growth_observed_in_training"])
        self.assertAlmostEqual(
            report["pooled_frozen_future_mse"]["persistence"], 0.0)
        self.assertFalse(report["predeclared_descriptive_numeric_gate_passed"])

    def test_invalid_or_cherry_picked_seed_protocol_refused(self):
        stream = pattern_stream(96)
        for seeds in ((1,), (1, 1, 2), (1, False, 3),
                      (1, 2, 2 ** 32), [1, 2, 3]):
            with self.subTest(seeds=seeds), self.assertRaises(ValueError):
                evaluate_temporal(stream, seeds=seeds)

    def test_bad_input_rejected_before_learning(self):
        for stream in (
                pattern_stream(95),
                pattern_stream(2001),
                [[0.0] * 7] * 100,
                [[True] * 8] * 100,
                [[float("nan")] * 8] * 100,
                [[0.4] * 8] * 100):
            with self.subTest(length=len(stream)), self.assertRaises(ValueError):
                evaluate_temporal(stream)


class PrivateLedgerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.db = self.root / "semantic_fabric.sqlite3"
        with closing(sqlite3.connect(self.db)) as con:
            with con:
                con.execute(
                    "CREATE TABLE observations("
                    "id INTEGER PRIMARY KEY, features TEXT NOT NULL, "
                    "tagger TEXT NOT NULL, recorded_utc TEXT NOT NULL)")
                for i, data in enumerate(pattern_stream(), 1):
                    con.execute(
                        "INSERT INTO observations VALUES(?,?,?,?)",
                        (i, json.dumps(data), VERSION, "fixture-only"))

    def test_private_sqlite_readonly_and_frozen_replay(self):
        before = self.db.read_bytes()
        report = evaluate_private_ledger(self.db)
        self.assertEqual(self.db.read_bytes(), before)
        self.assertTrue(report["private_sqlite_read_only_verified"])
        self.assertTrue(report["private_text_not_read_or_emitted"])
        self.assertEqual(len(report["semantic_ledger_sha256"]), 64)
        self.assertEqual(report["observations"], 112)
        self.assertNotIn("fixture-only", json.dumps(report))

    def test_tagger_provenance_validation(self):
        with closing(sqlite3.connect(self.db)) as con:
            with con:
                con.execute("UPDATE observations SET tagger='not-qwen' WHERE id=30")
        with self.assertRaisesRegex(ValueError, "Nonmonotonic or non-pinned"):
            evaluate_private_ledger(self.db)

    def test_readonly_state_change_aborts_instead_of_reporting_mixed_stream(self):
        from neurogenesis import acf_temporal_holdout as module
        original = module.evaluate_temporal
        def modify_db_during_evaluation(vectors):
            result = original(vectors)
            with closing(sqlite3.connect(self.db)) as con:
                with con:
                    con.execute(
                        "UPDATE observations SET features=? WHERE id=111",
                        (json.dumps([1.0] * 8),))
            return result
        with patch.object(module, "evaluate_temporal",
                          side_effect=modify_db_during_evaluation):
            with self.assertRaisesRegex(ValueError, "changed during"):
                evaluate_private_ledger(self.db)

    def test_oversized_silent_truncation_refused(self):
        with self.assertRaisesRegex(ValueError, "exceeds selected bound"):
            evaluate_private_ledger(self.db, limit=100)

    def test_missing_database_never_created(self):
        ghost = self.root / "missing.sqlite3"
        with self.assertRaises(ValueError):
            evaluate_private_ledger(ghost)
        self.assertFalse(ghost.exists())


if __name__ == "__main__":
    unittest.main()
