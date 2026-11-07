"""Real contextual-neural learning, causal holdout and SQLite regression tests."""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from neurogenesis import Brain
from neurogenesis.context import ContextualNextInputPredictor
from neurogenesis.memory import ExperienceMemory
from neurogenesis.desktop import process_message


def cue(slot: int) -> list[float]:
    return [1.0 if i == slot else 0.0 for i in range(8)]


def next_choice(rand_state: int) -> tuple[int, int]:
    next_state = (1664525 * rand_state + 1013904223) & 0xFFFFFFFF
    return next_state, int(next_state >= (1 << 31))


class ContextModelTests(unittest.TestCase):
    def test_online_learning_is_causal_and_automatic(self):
        learner = ContextualNextInputPredictor()
        x = cue(0)
        first = learner.observe(x, [0.0] * 24)
        self.assertIsNone(first.mse_before_update)
        self.assertEqual(first.observations, 1)
        second = learner.observe(cue(1), [0.1] * 24)
        self.assertIsNotNone(second.mse_before_update)
        self.assertEqual(learner.stats()["scored"], 1)
        self.assertLessEqual(second.mse_before_update, 1)
        self.assertEqual(learner.stats()["stored_raw_text"], False)

    def test_context_disambiguates_identical_current_cue_on_unused_sequence(self):
        # A/B -> identical middle cue -> different next target.
        # The cue by itself has no information about which target follows.
        # Learning uses 300 randomly generated episodes and evaluates 100
        # future episodes without changing readout weights.
        full_better = 0
        scores = []
        for seed in range(1, 11):
            full = ContextualNextInputPredictor(use_neural=False)
            no_history = ContextualNextInputPredictor(
                use_history=False, use_neural=False)
            rng = seed
            losses_full = []
            losses_fixed = []
            for ep in range(400):
                rng, choice = next_choice(rng)
                sequence = (cue(choice), cue(2), cue(4 + choice))
                for phase, x in enumerate(sequence):
                    a = full.observe(x, [0.0] * 24, learn=ep < 300)
                    b = no_history.observe(x, [0.0] * 24, learn=ep < 300)
                    if ep >= 300 and phase == 2:
                        losses_full.append(a.mse_before_update)
                        losses_fixed.append(b.mse_before_update)
            full_mse = sum(losses_full) / len(losses_full)
            baseline_mse = sum(losses_fixed) / len(losses_fixed)
            scores.append((full_mse, baseline_mse))
            full_better += full_mse < baseline_mse
        self.assertGreaterEqual(full_better, 9)
        self.assertLess(sum(v[0] for v in scores) / 10,
                        sum(v[1] for v in scores) / 30)

    def test_real_spiking_brain_activity_is_an_input_to_contextual_readout(self):
        from neurogenesis.brain import BrainConfig
        brain = Brain(BrainConfig(growth_enabled=False))
        learner = ContextualNextInputPredictor()
        for i in range(32):
            x = cue(i % 4)
            for _ in range(4):
                brain.step(x)
            learner.observe(x, brain.traces)
        self.assertEqual(learner.stats()["observations"], 32)
        self.assertEqual(learner.stats()["scored"], 31)
        self.assertTrue(any(v > 0 for v in learner.last_features[-8:]))
        self.assertEqual(learner.last_features[0], 1.0)

    def test_snapshot_replay_preserves_online_predictions_exactly(self):
        a = ContextualNextInputPredictor()
        for i in range(25):
            a.observe(cue(i % 4), [float(i % 3) / 3] * 24)
        b = ContextualNextInputPredictor.from_dict(a.to_dict())
        self.assertEqual(a.to_dict(), b.to_dict())
        for i in range(20):
            x = cue((i + 2) % 4)
            z = [.8 if j % 3 == i % 3 else .0 for j in range(24)]
            self.assertEqual(a.observe(x, z), b.observe(x, z))
            self.assertEqual(a.to_dict(), b.to_dict())

    def test_invalid_input_never_changes_readout(self):
        a = ContextualNextInputPredictor()
        a.observe(cue(1), [0.0] * 24)
        old = a.to_dict()
        for x, z in (([float("nan")] * 8, [0.0] * 24),
                     (cue(1), [6.0] * 24),
                     (cue(1), []), ([True] * 8, [0.0] * 24)):
            with self.assertRaises(ValueError):
                a.observe(x, z)
        with self.assertRaises(ValueError):
            a.observe(cue(1), [0.0] * 24, learn="false")
        self.assertEqual(old, a.to_dict())

    def test_corrupt_context_snapshots_fail_closed(self):
        source = ContextualNextInputPredictor()
        source.observe(cue(0), [0.0] * 24)
        for field, value in (
            ("schema", 100), ("width", 9999), ("learning_rate", "fast"),
            ("weights", []), ("previous_cue", [0.0]),
            ("last_features", [1.0]), ("error_sum", float("nan")),
            ("next_forecast", [2.0] * 8), ("observations", -1),
            ("use_neural", 1),
        ):
            with self.subTest(field=field):
                state = source.to_dict()
                state[field] = value
                with self.assertRaises(ValueError):
                    ContextualNextInputPredictor.from_dict(state)

    def test_frozen_probe_does_not_train_but_updates_temporal_context(self):
        source = ContextualNextInputPredictor()
        source.observe(cue(0), [0.0] * 24)
        weights = [w[:] for w in source.weights]
        for _ in range(10):
            source.observe(cue(2), [0.0] * 24, learn=False)
        self.assertEqual(weights, source.weights)
        self.assertEqual(source.scored, 0)
        self.assertEqual(source.observations, 11)

    def test_resource_bounds_and_type_validation(self):
        for args in ({"width": 0}, {"width": 4097},
                     {"learning_rate": 0}, {"learning_rate": float("inf")},
                     {"use_history": 2}, {"use_neural": "true"}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                ContextualNextInputPredictor(**args)


class ContextSQLiteTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "private.sqlite3"
        self.memory = ExperienceMemory(self.path)

    def test_every_message_learns_temporal_state_and_preserves_brain(self):
        baseline = self.memory.status()
        self.assertEqual(baseline["context_learning"]["observations"], 0)
        for i in range(4):
            process_message(self.memory, "Słowo {}".format(i))
        s = self.memory.status()
        self.assertEqual(s["context_learning"]["observations"], 4)
        self.assertEqual(s["context_learning"]["scored"], 3)
        self.assertTrue(s["context_learning"]["uses_real_neural_traces"])
        self.assertTrue(s["context_learning"]["uses_temporal_context"])
        self.assertEqual(s["brain"]["steps"], 16)
        self.assertEqual(s["records_with_raw_text"], 0)
        self.assertEqual(ExperienceMemory(self.path).status(), s)

    def test_old_schema_1_db_opens_and_adds_context_without_erasing_memory(self):
        self.memory.remember("history")
        with closing(self.memory._connect()) as con, con:
            con.execute("DROP TABLE contextual_state")
        old_steps = self.memory.brain().steps
        reopened = ExperienceMemory(self.path)
        reopened.remember("new experience")
        self.assertEqual(reopened.brain().steps, old_steps + 4)
        self.assertEqual(reopened.status()["observations"], 2)
        self.assertEqual(reopened.status()["context_learning"]["observations"], 1)

    def test_corrupted_saved_context_blocks_state_and_observation_updates(self):
        self.memory.remember("first")
        original = self.memory.brain().to_dict()
        with closing(self.memory._connect()) as con, con:
            con.execute("UPDATE contextual_state SET predictor_json='invalid json'")
        with self.assertRaisesRegex(ValueError, "stored contextual"):
            self.memory.remember("should not be saved")
        with self.assertRaises(ValueError):
            self.memory.status()
        with closing(self.memory._connect()) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM observations").fetchone()[0], 1)
            self.assertEqual(self.memory.brain().to_dict(), original)

    def test_context_and_explicit_teaching_use_the_same_brain(self):
        process_message(self.memory, "Message before teaching")
        self.memory.teach("Pytanie", "Odpowiedź")
        result = process_message(self.memory, "Pytanie?")
        self.assertEqual(result["reply"], "Odpowiedź")
        self.assertEqual(self.memory.status()["context_learning"]["observations"], 3)
        self.assertEqual(self.memory.brain().steps, 12)
        self.assertEqual(self.memory.status()["records_with_raw_text"], 0)

    def test_long_messages_remain_accepted_without_extra_raw_text(self):
        self.memory.remember("a " * 9900)
        self.assertEqual(self.memory.status()["observations"], 1)
        self.assertEqual(self.memory.status()["records_with_raw_text"], 0)

    def test_invalid_inputs_do_not_create_context_state(self):
        with self.assertRaises(ValueError):
            self.memory.remember(" ")
        self.assertEqual(self.memory.status()["context_learning"]["observations"], 0)
        with closing(self.memory._connect()) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM contextual_state").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
