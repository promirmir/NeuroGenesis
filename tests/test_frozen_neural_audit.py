"""Verify private evaluation does not learn from its independent audit stream.

Real LIF dynamics (spikes, traces, voltages, refractory, counters) evolve,
but immutable learning parameters (synapses, ages, patterns, readout weights,
bias, neuron count, connectivity) must remain identical.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import unittest

from neurogenesis.brain import Brain, BrainConfig
from neurogenesis.predictor import NextInputPredictor


class FrozenNeuralAuditTests(unittest.TestCase):
    @staticmethod
    def stimulus(i: int) -> list[float]:
        row = [0.0] * 8
        row[i % 2] = 1.0
        row[2 + i % 3] = 1.0
        return row

    def test_brain_freezes_all_learned_synapses_and_patterns_on_audit(self):
        cfg = replace(
            BrainConfig(), initial_neurons=24, max_neurons=64,
            growth_interval=2, novelty_threshold=0.1, prune_min_age=2)
        brain = Brain(cfg, seed=16)
        for i in range(13):
            brain.step(self.stimulus(i))
        before = brain.to_dict()
        self.assertTrue(brain.stats()["total_grown"] > 0)
        for i in range(48):
            result = brain.step(self.stimulus(i + 60), learn=False)
            self.assertEqual(result.grown, 0)
            self.assertEqual(result.pruned, 0)
        after = brain.to_dict()
        for key in ("synapses", "patterns", "total_grown", "total_pruned",
                    "rng_state", "pending_novelty", "config"):
            with self.subTest(key=key):
                self.assertEqual(after[key], before[key])
        self.assertEqual(len(after["voltages"]), len(before["voltages"]))
        self.assertGreater(after["steps"], before["steps"])
        self.assertGreaterEqual(after["total_spikes"], before["total_spikes"])

    def test_predictor_audit_does_not_change_readout_or_synaptic_learning(self):
        model = NextInputPredictor(
            Brain(replace(BrainConfig(), growth_interval=2,
                          novelty_threshold=0.1), seed=4))
        for i in range(12):
            model.step(self.stimulus(i), learn=True)
        before = model.to_dict()
        for i in range(35):
            model.step(self.stimulus(i + 30), learn=False)
        after = model.to_dict()
        for key in ("weights", "bias", "learning_rate"):
            self.assertEqual(before[key], after[key])
        for key in ("synapses", "patterns", "total_grown", "total_pruned"):
            self.assertEqual(before["brain"][key], after["brain"][key])
        self.assertEqual(len(before["brain"]["voltages"]),
                         len(after["brain"]["voltages"]))

    def test_invalid_learning_flag_rejected_without_state_mutation(self):
        model = NextInputPredictor(Brain())
        brain = Brain()
        before_brain = brain.to_dict()
        with self.assertRaises(ValueError):
            brain.step(self.stimulus(0), learn="False")
        self.assertEqual(before_brain, brain.to_dict())
        with self.assertRaises(ValueError):
            model.step(self.stimulus(0), learn=None)

    def test_training_default_path_still_modifies_real_synapses(self):
        brain = Brain(BrainConfig(growth_interval=2,
                                  novelty_threshold=0.1), seed=7)
        snapshot = brain.to_dict()
        for i in range(16):
            brain.step(self.stimulus(i))
        self.assertNotEqual(snapshot["synapses"], brain.to_dict()["synapses"])
        self.assertGreater(brain.stats()["steps"], 0)
        self.assertGreater(brain.stats()["total_grown"], 0)


if __name__ == "__main__":
    unittest.main()
