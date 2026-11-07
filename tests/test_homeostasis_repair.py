"""Unit tests for optional biologically inspired regulation and repair.

ToyBrain is a structural contract double; real Brain integration must be run
on clean repository checkout before merging.
"""
import copy
from dataclasses import dataclass
import unittest

from neurogenesis.homeostasis import HomeostaticRegulator, HomeostasisConfig
from neurogenesis.repair import lesioned_copy, repair_candidate, trial_repair


@dataclass
class Config:
    input_size: int = 2
    initial_neurons: int = 4
    max_neurons: int = 10
    weight_limit: float = 1.5
    max_synapses: int = 8


@dataclass
class Edge:
    pre: int
    post: int
    weight: float
    age: int = 0


class ToyBrain:
    def __init__(self):
        self.config = Config()
        self.spikes = [0, 0, 0, 0]
        self.traces = [0.0] * 4
        self.voltages = [0.0] * 4
        self.synapses = [Edge(0, 2, 0.5), Edge(1, 3, 0.5)]
        self.last_stimulus = [0, 0]
        self.steps = 0

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__ = copy.deepcopy(data)
        return obj

    def step(self, spikes, stimulus=(1.0, 0.0)):
        self.steps += 1
        self.spikes = list(spikes)
        self.last_stimulus = list(stimulus)


class HomeostasisTests(unittest.TestCase):
    def test_downscales_overactive_neurons_but_not_input(self):
        brain = ToyBrain()
        control = HomeostaticRegulator(HomeostasisConfig(
            target_rate=0.1, rate_decay=0.5, adapt_every=4,
            gain=1.0, max_relative_change=0.05, min_input_steps=3))
        for _ in range(4):
            brain.step([1, 0, 1, 0])
            control.observe(brain)
        self.assertLess(brain.synapses[0].weight, 0.5)
        self.assertGreater(brain.synapses[1].weight, 0.5)
        self.assertEqual(control.scaled_synapses, 2)

    def test_no_input_no_unfounded_repairs(self):
        brain = ToyBrain()
        ctrl = HomeostaticRegulator(HomeostasisConfig(adapt_every=4, min_input_steps=2))
        for _ in range(4):
            brain.step([0, 0, 0, 0], stimulus=(0, 0))
            self.assertEqual(ctrl.observe(brain), 0)
        self.assertEqual([e.weight for e in brain.synapses], [0.5, 0.5])

    def test_limits_change_per_interval_and_weight(self):
        brain = ToyBrain()
        brain.synapses[0].weight = 1.5
        ctrl = HomeostaticRegulator(HomeostasisConfig(
            adapt_every=4, rate_decay=0.5, target_rate=0.1,
            max_relative_change=0.02, gain=1.0, min_input_steps=1))
        for _ in range(4):
            brain.step([0, 0, 0, 0])
            ctrl.observe(brain)
        self.assertEqual(brain.synapses[0].weight, 1.5)
        self.assertLessEqual(brain.synapses[1].weight, 0.51)

    def test_snapshot_resume_exact(self):
        b = ToyBrain()
        c = HomeostaticRegulator(HomeostasisConfig(adapt_every=4, min_input_steps=2))
        for i in range(5):
            b.step([0, 0, i % 2, 0])
            c.observe(b)
        clone = HomeostaticRegulator.from_dict(c.to_dict())
        self.assertEqual(clone.to_dict(), c.to_dict())
        for _ in range(4):
            b.step([0, 0, 1, 0])
            self.assertEqual(c.observe(b), clone.observe(b))
        self.assertEqual(clone.to_dict(), c.to_dict())

    def test_growth_extends_rate_vector_safely(self):
        b = ToyBrain()
        c = HomeostaticRegulator(HomeostasisConfig(adapt_every=4, min_input_steps=2))
        b.step([1, 0, 1, 0]); c.observe(b)
        b.spikes.append(0); b.voltages.append(0); b.traces.append(0)
        b.step([1, 0, 1, 0, 0]); c.observe(b)
        self.assertEqual(len(c.rates), 5)

    def test_attach_to_preexisting_brain_does_not_reset_neural_state(self):
        b = ToyBrain()
        for _ in range(15):
            b.step([1, 0, 0, 1])
        before = b.to_dict()
        c = HomeostaticRegulator.attach(b)
        self.assertEqual(c.steps, 15)
        self.assertEqual(len(c.rates), 4)
        self.assertEqual(b.to_dict(), before)
        b.step([0, 1, 1, 0])
        self.assertEqual(c.observe(b), 0)

    def test_rejects_invalid_states_without_change(self):
        b = ToyBrain()
        c = HomeostaticRegulator()
        b.steps = 2
        with self.assertRaises(ValueError): c.observe(b)
        self.assertEqual(c.steps, 0)
        for field, val in [('rates', [float('nan')]), ('steps', True), ('input_steps', -1)]:
            d = c.to_dict(); d[field] = val
            with self.subTest(field=field), self.assertRaises(ValueError):
                HomeostaticRegulator.from_dict(d)

    def test_long_run_synaptic_weights_remain_bounded(self):
        brain = ToyBrain()
        ctrl = HomeostaticRegulator(HomeostasisConfig(adapt_every=4, min_input_steps=2))
        for tick in range(2000):
            brain.step([1, 0, int(tick % 7 == 0), 1])
            ctrl.observe(brain)
        self.assertEqual(ctrl.steps, 2000)
        self.assertGreater(ctrl.scaled_synapses, 0)
        self.assertTrue(all(0 <= edge.weight <= brain.config.weight_limit
                            for edge in brain.synapses))

    def test_duplicate_steps_are_rejected(self):
        brain = ToyBrain()
        ctrl = HomeostaticRegulator()
        brain.step([0, 0, 0, 0]); ctrl.observe(brain)
        saved = ctrl.to_dict()
        with self.assertRaises(ValueError): ctrl.observe(brain)
        self.assertEqual(ctrl.to_dict(), saved)

    def test_invalid_edges_fail_before_regulator_state_changes(self):
        brain = ToyBrain()
        brain.synapses.append(Edge(-1, 3, 0.5))
        brain.step([1, 0, 0, 1])
        ctrl = HomeostaticRegulator()
        before = ctrl.to_dict()
        with self.assertRaises(ValueError): ctrl.observe(brain)
        self.assertEqual(ctrl.to_dict(), before)

    def test_parameter_checks(self):
        for params in [dict(target_rate=0), dict(rate_decay=1),
                       dict(adapt_every=3), dict(min_input_steps=100),
                       dict(max_relative_change=.2), dict(gain=float('nan'))]:
            with self.subTest(params=params), self.assertRaises(ValueError):
                HomeostasisConfig(**params)


class RepairTests(unittest.TestCase):
    def test_lesion_exact_count_determinism_and_original_unchanged(self):
        b = ToyBrain(); before = b.to_dict()
        damaged1 = lesioned_copy(b, fraction=0.5, seed=17)
        damaged2 = lesioned_copy(b, fraction=0.5, seed=17)
        self.assertEqual(damaged1.to_dict(), damaged2.to_dict())
        self.assertEqual(len(damaged1.synapses), 1)
        self.assertEqual(b.to_dict(), before)

    def test_repair_candidate_does_not_mutate_original_and_respects_budget(self):
        b = ToyBrain(); b.synapses.pop(); before = b.to_dict()
        proposal, count = repair_candidate(b, max_new_synapses=3)
        self.assertEqual(count, 1)
        self.assertEqual(len(proposal.synapses), 2)
        self.assertEqual(b.to_dict(), before)
        self.assertEqual(proposal.synapses[-1].post, 3)
        proposal2, count2 = repair_candidate(b, max_new_synapses=0)
        self.assertEqual(count2, 0)
        self.assertEqual(len(proposal2.synapses), 1)

    def test_repair_trial_accepts_if_measurably_improved(self):
        b = ToyBrain(); b.synapses.pop(); before = b.to_dict()
        repaired, result = trial_repair(b, lambda x: 1 / (1 + len(x.synapses)))
        self.assertTrue(result.accepted)
        self.assertEqual(len(repaired.synapses), 2)
        self.assertEqual(b.to_dict(), before)

    def test_repair_trial_rejects_no_benefit(self):
        b = ToyBrain(); b.synapses.pop()
        repaired, result = trial_repair(b, lambda _: 0.5)
        self.assertFalse(result.accepted)
        self.assertEqual(len(repaired.synapses), len(b.synapses))

    def test_validation_errors_block_bad_repair(self):
        b = ToyBrain()
        for fraction in (-0.01, float('nan'), 1.01, True):
            with self.assertRaises(ValueError): lesioned_copy(b, fraction=fraction, seed=1)
        for score in (float('nan'), -1):
            with self.assertRaises(ValueError): trial_repair(b, lambda _: score)
        with self.assertRaises(ValueError): repair_candidate(b, max_new_synapses=-1)


if __name__ == '__main__':
    unittest.main()
