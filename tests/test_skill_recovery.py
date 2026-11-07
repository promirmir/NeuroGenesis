"""Task-level repair validation without fabricated claims of intelligence."""
import json
import subprocess
import sys
import unittest

from neurogenesis.skill_recovery import benchmark_skill_recovery


class SkillRecoveryTests(unittest.TestCase):
    def test_deterministic_and_frozen_eval(self):
        args = dict(seeds=3, fraction=0.5, train_steps=96, probe_steps=24)
        first = benchmark_skill_recovery(**args)
        self.assertEqual(first, benchmark_skill_recovery(**args))
        self.assertEqual(first['settings']['growth_enabled'], False)
        self.assertIn('pre-injury', first['limitations'])
        self.assertEqual(len(first['per_seed']), 3)
        for row in first['per_seed']:
            for key in ('holdout_intact_mse', 'holdout_damaged_mse', 'holdout_repaired_mse',
                        'holdout_markov_mse', 'unseen_repaired_mse', 'unseen_markov_mse'):
                self.assertTrue(0 <= row[key] <= 1, (key, row[key]))

    def test_no_lesion_cannot_manufacture_recovery(self):
        result = benchmark_skill_recovery(seeds=3, fraction=0,
                                         train_steps=100, probe_steps=24)
        for row in result['per_seed']:
            self.assertEqual(row['removed_synapses'], 0)
            self.assertEqual(row['added_synapses'], 0)
            self.assertEqual(row['holdout_intact_mse'], row['holdout_damaged_mse'])
            self.assertEqual(row['holdout_damaged_mse'], row['holdout_repaired_mse'])
        self.assertEqual(result['mean_prediction_gain_vs_damaged_mse'], 0)

    def test_zero_repair_budget_preserves_damaged_scores(self):
        result = benchmark_skill_recovery(seeds=3, fraction=0.5,
                                         train_steps=96, probe_steps=24, repair_budget=0)
        for row in result['per_seed']:
            self.assertEqual(row['holdout_damaged_mse'], row['holdout_repaired_mse'])
            self.assertEqual(row['added_synapses'], 0)

    def test_rejects_invalid_parameters(self):
        for bad in ({'seeds': 1}, {'seeds': True}, {'fraction': -1},
                    {'fraction': float('nan')}, {'fraction': True},
                    {'noise': float('inf')}, {'noise': 0.6}, {'train_steps': 10},
                    {'probe_steps': 0}, {'repair_budget': 9}, {'repair_budget': 2.5}):
            with self.subTest(case=bad), self.assertRaises(ValueError):
                benchmark_skill_recovery(**bad)

    def test_cli_valid_report(self):
        command = [sys.executable, '-m', 'neurogenesis.skill_recovery',
                   '--seeds', '2', '--train-steps', '96', '--probe-steps', '24']
        report = json.loads(subprocess.check_output(command, text=True))
        self.assertEqual(report['protocol'], 'task_level_prediction_recovery_heldout_v1')
        self.assertEqual(len(report['per_seed']), 2)


if __name__ == '__main__':
    unittest.main()
