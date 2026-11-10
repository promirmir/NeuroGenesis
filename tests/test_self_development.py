"""Checks neural self-tuning on real v0.4 Brain and NextInputPredictor classes."""

from __future__ import annotations

from dataclasses import replace
import math
import random
import unittest

from neurogenesis.brain import Brain, BrainConfig
from neurogenesis.predictor import NextInputPredictor
from neurogenesis.self_development import DevelopmentLimits, run_self_development_cycle


def stream(n, *, reverse=False, seed=0, task="A"):
    rng = random.Random(seed)
    result = []
    for t in range(n):
        phase = (t + int(reverse)) % 2
        v = [0.0] * 8
        v[phase] = 1.0
        v[phase + (2 if task == "A" else 4)] = 1.0
        result.append([max(0.0, min(1.0, a + rng.uniform(-0.08, 0.08))) for a in v])
    return result


class SelfDevelopmentTests(unittest.TestCase):
    def setUp(self):
        config = replace(BrainConfig(), growth_enabled=False)
        self.current = NextInputPredictor(Brain(config, seed=7), learning_rate=0.01)
        self.params = dict(training=stream(256, seed=11), selection=stream(80, seed=12),
                           audit=stream(96, seed=13), retained_skill=stream(96, seed=14))

    def test_source_does_not_mutate(self):
        old = self.current.to_dict()
        _, report = run_self_development_cycle(self.current, **self.params)
        self.assertEqual(self.current.to_dict(), old)
        self.assertEqual(report["protocol"], "neurogenesis_bounded_self_development_v2_frozen_audit")
        self.assertLessEqual(len(report["trials"]), 5)

    def test_deterministic_replay(self):
        a, report1 = run_self_development_cycle(self.current, **self.params)
        b, report2 = run_self_development_cycle(self.current, **self.params)
        self.assertEqual(a.to_dict(), b.to_dict())
        self.assertEqual(report1, report2)

    def test_promotion_when_independent_audit_improves(self):
        promoted, report = run_self_development_cycle(self.current, **self.params)
        self.assertTrue(report["promoted"])
        self.assertEqual(report["reason"], "measured_gain_no_regression")
        self.assertGreater(report["audit_gain_mse"], 0)
        self.assertNotEqual(promoted.to_dict(), self.current.to_dict())

    def test_held_out_audit_can_veto_overfit_to_selection_task(self):
        tested = NextInputPredictor(Brain(replace(BrainConfig(), growth_enabled=False), seed=7),
                                   learning_rate=0.05)
        original = tested.to_dict()
        result, report = run_self_development_cycle(
            tested, training=stream(256, seed=11, task="A"),
            selection=stream(80, seed=12, task="A"),
            audit=stream(96, seed=13, task="B"),
            retained_skill=stream(96, seed=14, task="A"))
        self.assertEqual(report["reason"], "independent_audit_failed")
        self.assertFalse(report["promoted"])
        self.assertLess(report["audit_gain_mse"], 0)
        self.assertEqual(result.to_dict(), original)

    def test_rejects_retention_regression_on_old_task(self):
        trained = NextInputPredictor(Brain(replace(BrainConfig(), growth_enabled=False), seed=6),
                                     learning_rate=0.05)
        for x in stream(160, seed=1, task="A"):
            trained.step(x)
        before = trained.to_dict()
        result, report = run_self_development_cycle(
            trained, training=stream(256, seed=10, task="B"),
            selection=stream(64, seed=11, task="B"),
            audit=stream(64, seed=12, task="B"),
            retained_skill=stream(64, seed=13, task="A"),
            limits=DevelopmentLimits(max_guard_regression=0.0))
        self.assertFalse(report["promoted"])
        self.assertEqual(report["reason"], "retained_skill_regressed")
        self.assertEqual(result.to_dict(), before)
        self.assertEqual(trained.to_dict(), before)

    def test_identical_audit_rejected(self):
        with self.assertRaisesRegex(ValueError, "distinct streams"):
            run_self_development_cycle(self.current, **dict(self.params, audit=self.params["selection"]))

    def test_no_promotion_if_gain_threshold_unachievable(self):
        before = self.current.to_dict()
        result, report = run_self_development_cycle(
            self.current, **self.params, limits=DevelopmentLimits(min_gain=1))
        self.assertEqual(result.to_dict(), before)
        self.assertFalse(report["promoted"])
        self.assertEqual(report["reason"], "no_selection_gain")

    def test_invalid_input_is_rejected_before_mutation(self):
        original = self.current.to_dict()
        for changed in [dict(training=stream(3)),
                        dict(selection=stream(8)[:-1]),
                        dict(audit=[[float('nan')]*8]*16),
                        dict(retained_skill=[[True]*8]*16),
                        dict(training=[[0.1]*7]*16)]:
            with self.subTest(changed=changed.keys()), self.assertRaises(ValueError):
                run_self_development_cycle(self.current,
                    **dict(self.params, **changed))
            self.assertEqual(self.current.to_dict(), original)

    def test_trial_budget(self):
        _, report = run_self_development_cycle(self.current, **self.params,
                          limits=DevelopmentLimits(max_trials=2))
        self.assertEqual(len(report["trials"]), 2)

    def test_option_gates_have_distinct_audit(self):
        _, report = run_self_development_cycle(self.current, **self.params)
        if report["selected_candidate"]:
            self.assertIn("baseline_audit_mse", report)
            self.assertIn("candidate_audit_mse", report)
            self.assertIn(report["reason"],
                {"independent_audit_failed", "retained_skill_regressed",
                 "measured_gain_no_regression"})

    def test_snapshot_compatibility(self):
        result, report = run_self_development_cycle(self.current, **self.params)
        self.assertEqual(NextInputPredictor.from_dict(result.to_dict()).to_dict(), result.to_dict())
        self.assertEqual(result.brain.SCHEMA_VERSION, 1)

    def test_limits_rejected(self):
        for kw in (dict(min_gain=math.nan), dict(max_guard_regression=-0.1),
                   dict(max_trials=100), dict(max_trials=True),
                   dict(max_samples_per_stream=0), dict(max_neurons_increase=-2)):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                DevelopmentLimits(**kw)


if __name__ == "__main__":
    unittest.main()
