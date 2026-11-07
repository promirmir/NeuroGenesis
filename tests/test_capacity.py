"""Resource limits, cloned capacity search and observational hardware tests."""
from dataclasses import replace
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from neurogenesis.brain import Brain, BrainConfig
from neurogenesis.capacity import ResourceBudget, capacity_trial, hardware_profile, _frozen_score
from neurogenesis.predictor import NextInputPredictor


def stream(kind: int, length: int = 48):
    rows = []
    for i in range(length):
        row = [0.0] * 8
        row[(i + kind) % 8] = 1.0
        row[(i + kind + 3) % 8] = 1.0
        rows.append(row)
    return rows


def predictor(*, can_grow=False):
    cfg = replace(BrainConfig(), max_neurons=24, max_synapses=16,
                  growth_enabled=can_grow)
    return NextInputPredictor(Brain(cfg, seed=5))


def run(p, budget=None):
    return capacity_trial(p, training=stream(0), selection=stream(1, 24),
                          audit=stream(2, 25), retained_skill=stream(3, 26),
                          budget=budget or ResourceBudget())


class CapacityTests(unittest.TestCase):
    def test_local_hardware_probe_does_not_require_cuda(self):
        info = hardware_profile()
        self.assertGreaterEqual(info['logical_cpu_threads'], 1)
        self.assertEqual(info['cuda_status'], 'not_checked')
        self.assertFalse(info['gpu_backend_implemented'])
        self.assertEqual(info['distributed_workers'], 0)
        self.assertFalse(info['internet_used'])

    def test_hardware_probe_refuses_invalid_boolean(self):
        with self.assertRaises(ValueError):
            hardware_profile(probe_cuda='yes')

    def test_cli_json_is_parseable(self):
        output = subprocess.check_output([sys.executable, '-m', 'neurogenesis.capacity'], text=True)
        self.assertIn('logical_cpu_threads', json.loads(output))

    def test_rejects_invalid_resource_budget(self):
        for kwargs in ({'max_neurons': True}, {'max_synapses': 1},
                       {'max_state_bytes': -1}, {'max_work_ratio': float('nan')},
                       {'max_trial_seconds': 0}, {'extra_neurons_per_trial': -1},
                       {'min_audit_gain': -0.1}, {'max_guard_regression': float('inf')}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ResourceBudget(**kwargs)

    def test_no_budget_returns_exact_state_unchanged(self):
        p = predictor()
        before = p.to_dict()
        candidate, report = run(p, ResourceBudget(max_neurons=24, max_synapses=16))
        self.assertFalse(report['accepted'])
        self.assertEqual(report['reason'], 'no_budget_for_growth')
        self.assertEqual(before, p.to_dict())
        self.assertEqual(before, candidate.to_dict())

    def test_rejects_below_existing_hard_limits(self):
        p = predictor()
        with self.assertRaises(ValueError):
            run(p, ResourceBudget(max_neurons=23, max_synapses=16))
        with self.assertRaises(ValueError):
            run(p, ResourceBudget(max_neurons=24, max_synapses=15))

    def test_rejects_bad_input_without_changes(self):
        p = predictor()
        original = p.to_dict()
        for bad in (float('nan'), float('inf'), -0.1, 1.1, True):
            data = stream(0)
            data[2][2] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                capacity_trial(p, training=data, selection=stream(1, 24),
                               audit=stream(2, 25), retained_skill=stream(3, 26))
        self.assertEqual(original, p.to_dict())

    def test_all_streams_distinct(self):
        p = predictor()
        with self.assertRaises(ValueError):
            capacity_trial(p, training=stream(0), selection=stream(1, 24),
                           audit=stream(1, 24), retained_skill=stream(3, 26))

    def test_frozen_probe_does_not_touch_weights_or_topology(self):
        p = predictor(can_grow=True)
        for sample in stream(0, 40):
            p.step(sample)
        original = p.to_dict()
        a = _frozen_score(p, tuple(map(tuple, stream(1, 24))))
        b = _frozen_score(p, tuple(map(tuple, stream(1, 24))))
        self.assertEqual(a, b)
        self.assertEqual(p.to_dict(), original)

    def test_default_rejects_growth_without_measured_advantage(self):
        p = predictor()
        state = p.to_dict()
        result, report = run(p, ResourceBudget(min_selection_gain=1))
        self.assertFalse(report['accepted'])
        self.assertEqual(report['reason'], 'no_selection_gain')
        self.assertGreater(report['challenger_neurons'], report['incumbent_neurons'])
        self.assertEqual(state, result.to_dict())
        self.assertEqual(state, p.to_dict())

    def test_audit_veto(self):
        p = predictor()
        old = p.to_dict()
        with patch('neurogenesis.capacity._frozen_score', side_effect=[0.3, 0.1, 0.4, 0.5, 0.2, 0.19, 0.2]):
            candidate, report = run(p)
        self.assertFalse(report['accepted'])
        self.assertEqual(report['reason'], 'independent_audit_failed')
        self.assertEqual(old, candidate.to_dict())
        self.assertEqual(old, p.to_dict())

    def test_retained_skill_veto(self):
        p = predictor()
        with patch('neurogenesis.capacity._frozen_score', side_effect=[0.3, 0.1, 0.4, 0.2, 0.1, 0.3, 0.1]):
            candidate, report = run(p)
        self.assertFalse(report['accepted'])
        self.assertEqual(report['reason'], 'retained_skill_regressed')
        self.assertEqual(p.to_dict(), candidate.to_dict())

    def test_promote_only_measured_nonregression(self):
        p = predictor()
        original = p.to_dict()
        with patch('neurogenesis.capacity._frozen_score', side_effect=[0.3, 0.1, 0.4, 0.2, 0.1, 0.1, 0.1]):
            candidate, report = run(p)
        self.assertTrue(report['accepted'])
        self.assertEqual(report['reason'], 'measured_gain_within_budget')
        self.assertGreater(len(candidate.brain.voltages), len(p.brain.voltages))
        self.assertEqual(original, p.to_dict())

    def test_rejects_excessive_compute_work(self):
        p = predictor()
        result, report = run(p, ResourceBudget(max_work_ratio=1.0))
        self.assertFalse(report['accepted'])
        self.assertEqual(report['reason'], 'resource_budget_exceeded')
        self.assertEqual(p.to_dict(), result.to_dict())

    def test_work_unit_quota_refuses_trial(self):
        p = predictor()
        old = p.to_dict()
        candidate, report = run(p, ResourceBudget(max_training_work_units=1000))
        self.assertFalse(report['accepted'])
        self.assertEqual(report['reason'], 'training_work_budget_exceeded')
        self.assertEqual(old, p.to_dict())
        self.assertEqual(old, candidate.to_dict())

    def test_training_deadline_checks_before_next_step(self):
        p = predictor()
        old = p.to_dict()
        with patch('neurogenesis.capacity.monotonic', side_effect=[0.0, 2.0]):
            candidate, report = run(p, ResourceBudget(max_trial_seconds=1))
        self.assertFalse(report['accepted'])
        self.assertEqual(report['reason'], 'time_budget_exceeded')
        self.assertEqual(old, candidate.to_dict())

    def test_snapshot_is_backward_compatible(self):
        p = predictor()
        original = p.to_dict()
        result, _ = run(p, ResourceBudget(max_neurons=24, max_synapses=16))
        self.assertEqual(result.to_dict()['schema'], 1)
        self.assertEqual(NextInputPredictor.from_dict(result.to_dict()).to_dict(), original)


if __name__ == '__main__':
    unittest.main()
