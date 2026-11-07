"""Transactional supervisor tests against the *real* v0.5.4 SQLite brain."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from neurogenesis.autonomy import AutonomicSupervisor, SupervisorConfig, WINDOW
from neurogenesis.memory import ExperienceMemory
from neurogenesis.predictor import NextInputPredictor


class AutonomyTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "private.sqlite3"
        self.memory = ExperienceMemory(self.path)
        self.supervisor = AutonomicSupervisor(self.memory)

    def fill(self, count=WINDOW):
        for i in range(count):
            self.memory.remember(f"local synthetic feature observation {i}", store_text=False)

    @staticmethod
    def promoted(current, **kwargs):
        """Test double for selection decision; uses an ACTUAL neural predictor."""
        clone = NextInputPredictor.from_dict(current.to_dict())
        clone.step([1.0] + [0.0] * (clone.brain.config.input_size - 1))
        return clone, {"promoted": True, "reason": "validated_candidate_test",
                       "trials": [], "candidate_audit_mse": 0.01}

    def test_first_cycle_waits_for_fresh_experiences_without_changing_brain(self):
        original = self.memory.brain().to_dict()
        report = self.supervisor.cycle()
        self.assertEqual(report["reason"], "not_enough_new_experiences")
        self.assertEqual(self.memory.brain().to_dict(), original)
        st = self.supervisor.status()
        self.assertEqual(st["cycles"], 0)
        self.assertEqual(st["promotions"], 0)
        self.assertEqual(st["needed_for_trial"], WINDOW)

    def test_real_trial_rejects_unproven_change_and_does_not_reuse_audit(self):
        self.fill()
        original = self.memory.brain().to_dict()
        sup = AutonomicSupervisor(self.memory, config=SupervisorConfig(min_gain=1, max_trials=2))
        first = sup.cycle()  # runs actual NextInputPredictor trials
        self.assertFalse(first["promoted"])
        self.assertEqual(first["reason"], "no_selection_gain")
        self.assertTrue(first["brain_unchanged"])
        self.assertEqual(self.memory.brain().to_dict(), original)
        self.assertEqual(sup.status()["cycles"], 1)
        self.assertEqual(sup.status()["new_events"], 0)
        again = sup.cycle()
        self.assertEqual(again["reason"], "not_enough_new_experiences")
        self.assertEqual(sup.status()["cycles"], 1)
        self.assertEqual(self.memory.status()["observations"], WINDOW)

    def test_corrupted_features_fail_closed_before_commit(self):
        self.fill()
        original = self.memory.brain().to_dict()
        with closing(self.memory._connect()) as con, con:
            con.execute("UPDATE observations SET features='invalid JSON' WHERE id=1")
        with self.assertRaises(ValueError):
            self.supervisor.cycle()
        self.assertEqual(self.memory.brain().to_dict(), original)
        self.assertEqual(self.supervisor.status()["cycles"], 0)

    def test_success_is_atomic_with_live_brain_and_predictor(self):
        self.fill()
        old_steps = self.memory.brain().steps
        with patch("neurogenesis.autonomy.run_self_development_cycle",
                   side_effect=self.promoted):
            result = self.supervisor.cycle()
        self.assertTrue(result["promoted"])
        self.assertEqual(self.memory.brain().steps, old_steps + 1)
        self.assertEqual(self.supervisor.status()["promotions"], 1)
        reopened = ExperienceMemory(self.path)
        self.assertEqual(reopened.status()["observations"], WINDOW)
        with closing(reopened._connect()) as con:
            stored = con.execute("SELECT predictor_json FROM predictor_state WHERE id=1").fetchone()
            model = NextInputPredictor.from_dict(json.loads(stored[0]))
            self.assertEqual(model.brain.to_dict(), reopened.brain().to_dict())
        reopened.remember("new actual experience")
        with closing(reopened._connect()) as con:
            stored = con.execute("SELECT predictor_json FROM predictor_state WHERE id=1").fetchone()
            model = NextInputPredictor.from_dict(json.loads(stored[0]))
            self.assertEqual(model.brain.to_dict(), reopened.brain().to_dict())
        self.assertEqual(reopened.brain().steps, old_steps + 5)

    def test_rollback_restores_exact_state_before_further_learning(self):
        self.fill()
        before = self.memory.brain().to_dict()
        with patch("neurogenesis.autonomy.run_self_development_cycle",
                   side_effect=self.promoted):
            self.supervisor.cycle()
        self.assertTrue(self.supervisor.rollback_last_promotion())
        self.assertEqual(self.memory.brain().to_dict(), before)
        self.assertFalse(self.supervisor.rollback_last_promotion())
        with closing(self.memory._connect()) as con:
            self.assertIsNone(con.execute("SELECT predictor_json FROM predictor_state").fetchone())
        self.assertEqual(self.memory.status()["observations"], WINDOW)

    def test_rollback_refuses_to_discard_new_experience(self):
        self.fill()
        with patch("neurogenesis.autonomy.run_self_development_cycle",
                   side_effect=self.promoted):
            self.supervisor.cycle()
        self.memory.remember("new memory must survive")
        expected = self.memory.brain().to_dict()
        with self.assertRaisesRegex(ValueError, "advanced"):
            self.supervisor.rollback_last_promotion()
        self.assertEqual(self.memory.brain().to_dict(), expected)
        self.assertEqual(self.memory.status()["observations"], WINDOW + 1)

    def test_experiment_failure_never_commits_partial_state_or_audit(self):
        self.fill()
        before = self.memory.brain().to_dict()
        with patch("neurogenesis.autonomy.run_self_development_cycle",
                   side_effect=ValueError("synthetic failed audit")):
            with self.assertRaisesRegex(ValueError, "failed audit"):
                self.supervisor.cycle()
        self.assertEqual(self.memory.brain().to_dict(), before)
        self.assertEqual(self.supervisor.status()["cycles"], 0)

    def test_predictor_divergence_fails_closed(self):
        self.fill()
        with patch("neurogenesis.autonomy.run_self_development_cycle",
                   side_effect=self.promoted):
            self.supervisor.cycle()
        with closing(self.memory._connect()) as con, con:
            brain = self.memory.brain()
            brain.step([0.0] * brain.config.input_size)
            con.execute("UPDATE neural_state SET brain_json=? WHERE id=1",
                        (json.dumps(brain.to_dict()),))
        with self.assertRaisesRegex(ValueError, "divergence"):
            self.memory.remember("should not mutate")
        self.assertEqual(self.memory.status()["observations"], WINDOW)
        self.assertEqual(self.supervisor.cycle()["reason"], "not_enough_new_experiences")

    def test_stop_signal_prevents_any_periodic_run(self):
        stop = threading.Event()
        stop.set()
        with patch.object(self.supervisor, "cycle") as attempt:
            self.supervisor.run_until_stopped(stop)
            attempt.assert_not_called()

    def test_invalid_operator_limits_fail_closed(self):
        with self.assertRaises(ValueError):
            SupervisorConfig(max_trials=100)
        with self.assertRaises(ValueError):
            SupervisorConfig(interval_seconds=0)
        with self.assertRaises(ValueError):
            SupervisorConfig(min_gain=float("nan"))
