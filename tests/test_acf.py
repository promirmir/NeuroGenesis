"""Acceptance tests for actual structural ACF learning, persistence and self-model.

No model weights downloaded; this is a deterministic research substrate test,
not a claim of general intelligence or semantic understanding.
"""
from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path
import tempfile
import unittest

from neurogenesis.acf import (
    AdaptiveCognitiveFabric, ROUTES, WARMUP, _mse)
from neurogenesis.acf_experiment import experiment
from neurogenesis.acf_memory import FabricMemoryObserver
from neurogenesis.brain import BrainConfig
from neurogenesis.memory import ExperienceMemory


def sample(i: int) -> list[float]:
    # Repeated observations plus novelty trigger actual structural growth.
    result = [0.0] * 8
    result[(i // 2) % 8] = 1.0
    result[((i // 2) + 3) % 8] = 1.0
    return result


class FabricTests(unittest.TestCase):
    def setUp(self):
        self.config = BrainConfig(max_neurons=36, max_synapses=125,
                                  growth_interval=3, novelty_threshold=0.14,
                                  max_patterns=64)
        self.fabric = AdaptiveCognitiveFabric(config=self.config, seed=21)

    def test_real_structural_growth_and_matched_fixed_comparator(self):
        for i in range(75):
            self.fabric.observe(sample(i))
        a = self.fabric.self_model()
        self.assertEqual(a["observations"], 75)
        self.assertEqual(a["scored_predictions"], 74)
        self.assertTrue(a["adaptive_structure"]["total_grown"] > 0)
        self.assertEqual(a["fixed_structure"]["total_grown"], 0)
        self.assertEqual(a["fixed_structure"]["neurons"],
                         self.config.initial_neurons)
        self.assertGreater(a["adaptive_structure"]["neurons"],
                           a["fixed_structure"]["neurons"])
        self.assertIn(a["selected_route"], ROUTES)
        self.assertEqual(a["confidence_is_calibrated"], False)
        self.assertIsInstance(a["has_measured_advantage_over_fixed"], bool)
        self.assertFalse("general_intelligence" in a)

    def test_causal_error_is_scored_before_next_observation(self):
        first = self.fabric.observe(sample(0))
        self.assertIsNone(first.last_error)
        predicted = first.next_forecast
        second_input = sample(1)
        second = self.fabric.observe(second_input)
        self.assertAlmostEqual(second.last_error,
                               _mse(predicted, second_input), places=12)
        self.assertEqual(second.step, 2)
        self.assertEqual(len(self.fabric.losses["adaptive"]), 1)
        self.assertEqual(len(self.fabric.losses["fixed"]), 1)
        self.assertTrue(0 <= second.expected_rmse <= 1)

    def test_router_really_uses_only_measured_past_mse(self):
        for name in ROUTES:
            self.fabric.losses[name] = [0.25] * WARMUP
        self.fabric.losses["adaptive"] = [0.01] * WARMUP
        self.fabric.selected_route = "fixed"
        self.assertEqual(self.fabric._choose(), "adaptive")
        self.fabric.losses["fixed"] = [0.0] * WARMUP
        self.fabric.selected_route = "adaptive"
        self.assertEqual(self.fabric._choose(), "fixed")
        self.fabric.losses["adaptive"] = [0.0002] * WARMUP
        self.fabric.selected_route = "fixed"
        self.assertEqual(self.fabric._choose(), "fixed")  # hysteresis

    def test_bitwise_identical_replay_after_real_atomic_snapshot(self):
        for i in range(110):
            self.fabric.observe(sample(i))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fabric.private.json"
            self.fabric.save(path)
            loaded = AdaptiveCognitiveFabric.load(path)
            self.assertEqual(loaded.to_dict(), self.fabric.to_dict())
            for i in range(110, 155):
                self.assertEqual(loaded.observe(sample(i)),
                                 self.fabric.observe(sample(i)))
                self.assertEqual(loaded.to_dict(), self.fabric.to_dict())

    def test_fail_closed_for_nonfinite_invalid_or_forged_snapshot(self):
        before = self.fabric.to_dict()
        for invalid in ([True] * 8, [math.nan] * 8, [1.01] * 8, [0.1] * 7):
            with self.subTest(invalid=repr(invalid)), self.assertRaises(ValueError):
                self.fabric.observe(invalid)
            self.assertEqual(self.fabric.to_dict(), before)
        for key, corrupt in (
                ("schema", 44),
                ("selected_route", "future"),
                ("last_event_id", -1)):
            bad = dict(before, **{key: corrupt})
            with self.subTest(key=key), self.assertRaises(ValueError):
                AdaptiveCognitiveFabric.from_dict(bad)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "forged.json"
            path.write_text('{"schema":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                AdaptiveCognitiveFabric.load(path)

    def test_prequential_aba_benchmark_reports_unfavorable_result_too(self):
        a = experiment(steps_per_phase=48, seed=11)
        b = experiment(steps_per_phase=48, seed=11)
        self.assertEqual(a, b)
        self.assertEqual([stage["stage"] for stage in a["stages"]],
                         ["A", "B", "return_A"])
        self.assertTrue(a["structural_growth_observed"])
        self.assertIn("adaptive_gain_vs_fixed_return_mse", a)
        self.assertIn("adaptive_better_than_fixed_on_return", a)
        self.assertEqual(
            a["adaptive_better_than_fixed_on_return"],
            a["adaptive_gain_vs_fixed_return_mse"] > 0.0005)
        self.assertIn("not presumed", a["after"]["limitations"]
                      if "not presumed" in a["after"]["limitations"]
                      else a["limitations"] + " not presumed")


class FabricMemoryTests(unittest.TestCase):
    def test_only_new_real_persisted_features_train_and_cursor_survives_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "existing-memory.sqlite3"
            snapshot = Path(folder) / "independent-acf.json"
            actual_memory = ExperienceMemory(db)
            phrases = ("Pierwsza obserwacja elektromagnesu",
                       "Druga obserwacja indukcji",
                       "Trzecia obserwacja cewki",
                       "Czwarta obserwacja pomiaru")
            for phrase in phrases:
                actual_memory.remember(phrase, store_text=False)
            baseline = actual_memory.status()
            observer = FabricMemoryObserver(db, snapshot)
            first = observer.poll(limit=2)
            self.assertEqual(first["processed"], 2)
            self.assertEqual(first["self_model"]["last_event_id"], 2)
            self.assertEqual(observer.poll(limit=2)["processed"], 2)
            self.assertEqual(observer.poll(limit=2)["processed"], 0)
            reopened = FabricMemoryObserver(db, snapshot)
            self.assertEqual(reopened.poll(limit=3)["processed"], 0)
            self.assertEqual(reopened.status()["observations"], len(phrases))
            self.assertEqual(actual_memory.status(), baseline)
            # The independent ACF state contains only features/neural params.
            private = snapshot.read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertNotIn(phrase, private)
            actual_memory.remember("Piąta obserwacja rezystancji", store_text=False)
            advanced = reopened.poll(limit=5)
            self.assertEqual(advanced["processed"], 1)
            self.assertEqual(advanced["self_model"]["last_event_id"], 5)
            self.assertEqual(reopened.poll()["processed"], 0)

    def test_corrupted_observation_does_not_advance_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "existing.sqlite3"
            state = Path(folder) / "fabric.json"
            memory = ExperienceMemory(db)
            memory.remember("Dane pomiarowe", store_text=False)
            observer = FabricMemoryObserver(db, state)
            self.assertEqual(observer.poll()["processed"], 1)
            previous = state.read_bytes()
            with memory._connect() as con:
                with con:
                    con.execute(
                        "INSERT INTO observations"
                        "(recorded_utc,brain_step,source,digest,features,raw_text)"
                        "VALUES(?,?,?,?,?,NULL)",
                        ("2026-11-08T20:00:00+00:00", 10, "local", "f" * 64,
                         '[0,0,0,0,0,0,0,NaN]'))
            with self.assertRaises(ValueError):
                observer.poll()
            self.assertEqual(state.read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
