"""Integration tests against the v0.4 Brain interface (no ToyBrain)."""
from __future__ import annotations
from dataclasses import replace
import json
import tempfile
from pathlib import Path
import unittest

from neurogenesis.brain import Brain, BrainConfig
from neurogenesis.homeostasis import HomeostaticRegulator, HomeostasisConfig
from neurogenesis.repair import lesioned_copy, repair_candidate, trial_repair
from neurogenesis.lesion_benchmark import lesion_repair_benchmark


def stimulus(t: int) -> list[float]:
    v = [0.0] * 8
    v[t % 8] = 1.0
    v[(t + 2) % 8] = 1.0
    return v


class RealBrainIntegrationTests(unittest.TestCase):
    def test_regulator_grows_with_real_spiking_neurons_and_respects_bounds(self):
        brain = Brain(seed=3)
        ctrl = HomeostaticRegulator.attach(brain)
        original_neurons = len(brain.voltages)
        for t in range(192):
            brain.step(stimulus(t // 4))
            ctrl.observe(brain)
        self.assertGreater(len(brain.voltages), original_neurons)
        self.assertEqual(len(ctrl.rates), len(brain.voltages))
        self.assertEqual(ctrl.steps, brain.steps)
        self.assertTrue(all(0 <= x.weight <= brain.config.weight_limit for x in brain.synapses))
        self.assertLessEqual(len(brain.synapses), brain.config.max_synapses)

    def test_resume_regulator_and_brain_from_snapshots_is_bitwise_identical(self):
        brain = Brain(seed=11)
        ctrl = HomeostaticRegulator.attach(brain)
        for t in range(85):
            brain.step(stimulus(t))
            ctrl.observe(brain)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'brain.snapshot.json'
            brain.save(path)
            loaded = Brain.load(path)
        replay = HomeostaticRegulator.from_dict(json.loads(json.dumps(ctrl.to_dict())))
        self.assertEqual(loaded.to_dict(), brain.to_dict())
        self.assertEqual(replay.to_dict(), ctrl.to_dict())
        for t in range(85, 180):
            sample = stimulus(t)
            brain.step(sample); loaded.step(sample)
            ctrl.observe(brain); replay.observe(loaded)
        self.assertEqual(brain.to_dict(), loaded.to_dict())
        self.assertEqual(ctrl.to_dict(), replay.to_dict())

    def test_repair_on_real_brain_changes_only_clone(self):
        b = Brain(replace(BrainConfig(), growth_enabled=False), seed=19)
        for i in range(40): b.step(stimulus(i))
        old = b.to_dict()
        injured = lesioned_copy(b, fraction=0.5, seed=57)
        candidate, added = repair_candidate(injured, max_new_synapses=8)
        self.assertEqual(b.to_dict(), old)
        self.assertLess(len(injured.synapses), len(b.synapses))
        self.assertTrue(0 <= added <= 8)
        self.assertLessEqual(len(candidate.synapses), candidate.config.max_synapses)
        self.assertEqual(candidate.to_dict()['schema'], old['schema'])
        self.assertEqual(Brain.from_dict(candidate.to_dict()).to_dict(), candidate.to_dict())

    def test_neutral_validation_rejects_candidate_without_mutating_original(self):
        b = Brain(replace(BrainConfig(), growth_enabled=False), seed=6)
        damaged = lesioned_copy(b, fraction=0.5, seed=2)
        old = damaged.to_dict()
        returned, result = trial_repair(damaged, lambda _: 0.25, candidate_weight=0.8)
        self.assertFalse(result.accepted)
        self.assertEqual(returned.to_dict(), old)
        self.assertEqual(damaged.to_dict(), old)

    def test_invalid_repair_weight_cannot_change_brain(self):
        b = Brain(seed=8); old = b.to_dict()
        with self.assertRaises(ValueError):
            trial_repair(b, lambda _: 0.1, candidate_weight=2.5)
        self.assertEqual(b.to_dict(), old)

    def test_lesion_repair_benchmark_deterministic_and_fairly_labeled(self):
        first = lesion_repair_benchmark(seeds=3, fraction=0.5, proposed_weight=0.8)
        second = lesion_repair_benchmark(seeds=3, fraction=0.5, proposed_weight=0.8)
        self.assertEqual(first, second)
        self.assertIn('intact_oracle', first['protocol'])
        self.assertEqual(len(first['paired_results']), 3)
        for r in first['paired_results']:
            self.assertTrue(0 <= r['holdout_untreated_error'] <= 1)
            self.assertTrue(0 <= r['holdout_naive_error'] <= 1)
            self.assertTrue(0 <= r['holdout_gated_error'] <= 1)

    def test_invalid_benchmark_args_rejected(self):
        for params in (dict(seeds=1), dict(seeds=True), dict(fraction=-.1),
                       dict(fraction=float('nan')), dict(proposed_weight=2.0)):
            with self.subTest(params=params), self.assertRaises(ValueError):
                lesion_repair_benchmark(**params)

if __name__ == '__main__': unittest.main()
