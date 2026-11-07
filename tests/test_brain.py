import json
from pathlib import Path
import tempfile
import unittest

from neurogenesis import Brain, BrainConfig
from neurogenesis.experiment import compare_growth
from neurogenesis.self_model import inspect
from neurogenesis.sensory import TextSensor


class BrainTests(unittest.TestCase):
    def test_initial_state_and_spiking(self):
        brain = Brain()
        self.assertEqual(brain.stats()["neurons"], 24)
        out = brain.step([1.0] + [0.0] * 7)
        self.assertEqual(out.spikes[0], 1)
        self.assertGreater(out.energy_proxy, 0)
        self.assertEqual(brain.stats()["steps"], 1)

    def test_invalid_inputs_and_configuration(self):
        brain = Brain()
        for stimulus in ([0.0], [float("nan")] * 8, [2.0] * 8):
            with self.assertRaises(ValueError):
                brain.step(stimulus)
        with self.assertRaises(ValueError):
            brain.step([0.0] * 8, reward=float("inf"))
        with self.assertRaises(ValueError):
            BrainConfig(max_neurons=2)
        with self.assertRaises(ValueError):
            Brain(seed=-1)

    def test_novelty_growth_and_caps(self):
        config = BrainConfig(initial_neurons=10, max_neurons=12, max_synapses=25,
                             growth_interval=2, novelty_threshold=0.2)
        brain = Brain(config)
        for i in range(48):
            x = [0.0] * 8
            x[(i // 2) % 8] = 1.0
            x[((i // 2) + 1) % 8] = 1.0
            brain.step(x)
        self.assertGreater(brain.total_grown, 0)
        self.assertLessEqual(len(brain.voltages), config.max_neurons)
        self.assertLessEqual(len(brain.synapses), config.max_synapses)
        self.assertEqual(len(brain.traces), len(brain.voltages))
        self.assertEqual(len(brain.spikes), len(brain.voltages))

    def test_repeat_pattern_reduces_novelty(self):
        brain = Brain()
        first = brain.step([1.0] * 8)
        again = brain.step([1.0] * 8)
        self.assertEqual(first.novelty, 1.0)
        self.assertEqual(again.novelty, 0.0)

    def test_causal_synapse_strengthens(self):
        brain = Brain(BrainConfig(weight_decay=0.000001, growth_enabled=False))
        original = brain.synapses[0].weight
        pattern = [1.0] + [0.0] * 7
        for _ in range(40):
            brain.step(pattern, reward=1.0)
        self.assertGreater(brain.synapses[0].weight, original)

    def test_prune_weak_mature_synapse(self):
        brain = Brain(BrainConfig(growth_interval=2, prune_min_age=2,
                                 prune_threshold=0.1, growth_enabled=False))
        original_count = len(brain.synapses)
        brain.synapses[0].weight = 0.001
        brain.step([0.0] * 8)
        outcome = brain.step([0.0] * 8)
        self.assertEqual(outcome.pruned, 1)
        self.assertEqual(len(brain.synapses), original_count - 1)

    def test_snapshot_resume_is_bitwise_deterministic(self):
        brain = Brain()
        patterns = [[float((i + j) % 3 == 0) for i in range(8)] for j in range(8)]
        for i in range(30):
            brain.step(patterns[i % len(patterns)])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.json"
            brain.save(path)
            loaded = Brain.load(path)
            self.assertEqual(brain.to_dict(), loaded.to_dict())
            for i in range(30):
                x = patterns[i % len(patterns)]
                self.assertEqual(brain.step(x), loaded.step(x))
                self.assertEqual(brain.to_dict(), loaded.to_dict())

    def test_corrupted_snapshot_rejected(self):
        brain = Brain()
        data = brain.to_dict()
        data["synapses"][0]["post"] = 9999
        with self.assertRaises(ValueError):
            Brain.from_dict(data)
        data = brain.to_dict()
        data["schema"] = 99
        with self.assertRaises(ValueError):
            Brain.from_dict(data)
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "bad.json"
            file.write_text('{"schema":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                Brain.load(file)

    def test_text_sensor_is_deterministic_not_language_understanding(self):
        sensor = TextSensor()
        self.assertEqual(sensor.encode("Ala ma kota"), sensor.encode("ALA ma KOTA"))
        self.assertEqual(sensor.encode(""), [0.0] * 8)
        with self.assertRaises(ValueError):
            sensor.encode("x" * 20001)
        self.assertFalse(inspect(Brain())["capabilities"]["natural_language_understanding"])

    def test_growth_control_experiment(self):
        result = compare_growth(steps=128)
        self.assertEqual(result["fixed_structure"]["neurons"], 24)
        self.assertGreater(result["growth_enabled"]["neurons"], 24)
        self.assertEqual(result["growth_enabled"]["steps"], 128)
        self.assertIn("not establish", result["limitations"])


if __name__ == "__main__":
    unittest.main()
