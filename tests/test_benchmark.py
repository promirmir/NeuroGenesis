"""Cross-version deterministic evaluation and non-regression checks."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from neurogenesis.benchmark import _probe, _stimulus, continual_learning_benchmark
from neurogenesis.predictor import NextInputPredictor


class ContinualLearningBenchmarkTests(unittest.TestCase):
    def test_repeated_benchmark_is_exactly_deterministic(self):
        first = continual_learning_benchmark(seeds=3, steps_per_phase=48,
                                             probe_steps=12, noise=0.2)
        second = continual_learning_benchmark(seeds=3, steps_per_phase=48,
                                              probe_steps=12, noise=0.2)
        self.assertEqual(first, second)
        self.assertEqual(set(first['per_seed']), {'growth_enabled', 'fixed_structure'})
        for rows in first['per_seed'].values():
            self.assertEqual([r['seed'] for r in rows], [1, 2, 3])
            for row in rows:
                for key in ('a_before_shift_mse', 'a_after_shift_mse',
                            'a_after_relearning_mse'):
                    self.assertTrue(0 <= row[key] <= 1)

    def test_aba_probe_cannot_modify_training_model(self):
        learner = NextInputPredictor()
        for i in range(64):
            learner.step(_stimulus('A', i))
        before = learner.to_dict()
        score = _probe(learner, seed=7, steps=24, noise=0.1)
        self.assertTrue(0 <= score <= 1)
        self.assertEqual(learner.to_dict(), before)
        self.assertEqual(len(learner.weights[0]), len(learner.brain.voltages))

    def test_learn_false_does_not_update_readout_and_old_api_still_works(self):
        learner = NextInputPredictor()
        for i in range(24):
            learner.step(_stimulus('A', i))
        weights = [row.copy() for row in learner.weights]
        bias = learner.bias.copy()
        learner.step(_stimulus('A', 24), learn=False)
        self.assertEqual(learner.weights, weights)
        self.assertEqual(learner.bias, bias)
        with self.assertRaises(ValueError):
            learner.step(_stimulus('A', 25), learn='yes')

    def test_invalid_parameters_are_rejected(self):
        cases = ({'seeds': 1}, {'seeds': True}, {'seeds': 101},
                 {'steps_per_phase': 20}, {'probe_steps': 2},
                 {'noise': -0.1}, {'noise': float('nan')},
                 {'noise': float('inf')})
        for params in cases:
            with self.subTest(params=params), self.assertRaises(ValueError):
                continual_learning_benchmark(**params)

    def test_cli_reproducibility_and_json(self):
        cmd = [sys.executable, '-m', 'neurogenesis', 'benchmark',
               '--seeds', '2', '--steps-per-phase', '48', '--probe-steps', '12']
        output = subprocess.check_output(cmd, text=True)
        self.assertEqual(json.loads(output)['settings']['task_order'], 'A-B-A')


if __name__ == '__main__':
    unittest.main()
