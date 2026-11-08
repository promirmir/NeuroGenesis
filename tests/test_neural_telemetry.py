"""Real persisted-neuron to screen telemetry tests without synthetic animation."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from neurogenesis.brain import Brain
from neurogenesis.command_service import CommandService
from neurogenesis.neural_telemetry import (
    NeuralTelemetry, diff_neural_telemetry, snapshot_neural_telemetry,
)


class LiveConnectomeTelemetryTests(unittest.TestCase):
    def test_exact_real_nodes_connections_and_no_fake_activity(self):
        brain = Brain()
        first = snapshot_neural_telemetry(brain)
        self.assertEqual(first.step, 0)
        self.assertEqual(len(first.nodes), 24)
        self.assertEqual(len(first.edges), len(brain.synapses))
        self.assertEqual(first.edges[0].weight, brain.synapses[0].weight)
        self.assertTrue(first.nodes[0].input_channel)
        self.assertFalse(first.nodes[8].input_channel)
        self.assertFalse(first.nodes[0].fired)
        self.assertFalse(first.truncated)
        self.assertFalse(diff_neural_telemetry(first, first)["advanced"])
        brain.step([1.0] * brain.config.input_size)
        second = snapshot_neural_telemetry(brain)
        self.assertEqual(second.step, 1)
        self.assertEqual(second.total_spikes, brain.total_spikes)
        self.assertEqual(tuple(node.fired for node in second.nodes), tuple(
            bool(spike) for spike in brain.spikes))
        self.assertTrue(diff_neural_telemetry(first, second)["advanced"])
        self.assertEqual(diff_neural_telemetry(first, second)["new_spikes"],
                         second.total_spikes - first.total_spikes)
        self.assertEqual(second.edges[0].age, brain.synapses[0].age)
        self.assertEqual(brain.steps, 1)

    def test_real_sqlite_restart_and_step_visibility(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "local.sqlite3"
            service = CommandService(path)
            idle = service.neural_connectome()
            self.assertEqual(idle.step, 0)
            service.ask("Pierwszy bodziec, próbna pamięć")
            now = service.neural_connectome()
            self.assertGreater(now.step, idle.step)
            self.assertEqual(now.step, service.memory.brain().steps)
            self.assertEqual(now.total_synapses, len(service.memory.brain().synapses))
            second_service = CommandService(path)
            reopened = second_service.neural_connectome()
            self.assertEqual(reopened, now)
            self.assertFalse(second_service.network_enabled)
            self.assertEqual(second_service.neural_connectome(), reopened)

    def test_reject_invalid_or_fabricated_brain_state(self):
        with self.assertRaises(TypeError):
            snapshot_neural_telemetry(None)
        brain = Brain()
        brain.voltages[0] = float("nan")
        with self.assertRaisesRegex(ValueError, "invalid neural activity"):
            snapshot_neural_telemetry(brain)


if __name__ == "__main__":
    unittest.main()
