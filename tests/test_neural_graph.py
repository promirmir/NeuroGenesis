"""Actual LIF topology telemetry, bounded display, deterministic geometry.

This is not a mock neural simulation: frames reflect the real Brain step,
stored spike bits, trace values and synapse weights. No simulated activity is
created by reading a frame.
"""
from __future__ import annotations

import math
from pathlib import Path
import tempfile
import unittest

from neurogenesis.brain import Brain, BrainConfig, Synapse
from neurogenesis.memory import ExperienceMemory
from neurogenesis.neural_graph import (
    MAX_VIEW_NODES, MAX_VIEW_EDGES, snapshot_brain, positions,
)


class RealNeuralGraphTests(unittest.TestCase):
    def test_live_step_reflects_actual_spikes_edges_and_nonmutation(self):
        brain = Brain()
        before = brain.to_dict()
        base = snapshot_brain(brain)
        self.assertEqual(base.step, 0)
        self.assertEqual(base.last_spikes, 0)
        self.assertEqual(base.neurons, len(before["voltages"]))
        self.assertEqual(base.synapses, len(before["synapses"]))
        self.assertEqual(base.total_spikes, 0)
        self.assertEqual(brain.to_dict(), before)
        result = brain.step([1.0] * brain.config.input_size)
        frame = snapshot_brain(brain)
        self.assertEqual(frame.step, result.step)
        self.assertEqual(frame.neurons, result.neurons)
        self.assertEqual(frame.synapses, result.synapses)
        self.assertEqual(frame.last_spikes, sum(brain.spikes))
        self.assertEqual(frame.total_spikes, brain.total_spikes)
        self.assertEqual({n.index for n in frame.nodes if n.spiked},
                         {i for i, value in enumerate(brain.spikes) if value})
        self.assertEqual(frame.nodes[0].trace, brain.traces[0])
        self.assertEqual(frame.edges[0].weight, brain.synapses[0].weight)
        after = brain.to_dict()
        self.assertEqual(snapshot_brain(brain), frame)
        self.assertEqual(brain.to_dict(), after)

    def test_bounded_graph_with_real_high_activity_and_coverage(self):
        brain = Brain(BrainConfig(initial_neurons=124, max_neurons=128))
        for index in range(900):
            brain.synapses.append(Synapse(
                8 + index % 50,
                8 + (index + 1) % 50,
                .2 + .1 * (index % 8)))
        brain.spikes[-1] = 1
        brain.traces[-1] = 4.0
        frame = snapshot_brain(brain)
        self.assertEqual(frame.neurons, 124)
        self.assertEqual(frame.synapses, 916)
        self.assertEqual(len(frame.nodes), MAX_VIEW_NODES)
        self.assertLessEqual(len(frame.edges), MAX_VIEW_EDGES)
        self.assertIn(123, {n.index for n in frame.nodes})
        self.assertIn("112/124", frame.coverage)
        allowed = {n.index for n in frame.nodes}
        self.assertTrue(all(e.pre in allowed and e.post in allowed for e in frame.edges))
        self.assertEqual(frame.last_spikes, 1)
        self.assertEqual(frame.grown, 0)
        self.assertEqual(frame.pruned, 0)
        layout = positions(frame, 1400, 800)
        self.assertEqual(set(layout), allowed)
        self.assertTrue(all(math.isfinite(x) and math.isfinite(y)
                            and 0 <= x <= 1400 and 0 <= y <= 800
                            for x, y in layout.values()))
        self.assertEqual(layout, positions(frame, 1400, 800))
        self.assertEqual(positions(frame, 0, 800), {})

    def test_persisted_real_neural_graph_reloads_from_private_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "memory.sqlite3"
            live = ExperienceMemory(db)
            saved = live.remember("Uczenie sieci i synaps")
            first = snapshot_brain(live.brain())
            reopened = snapshot_brain(ExperienceMemory(db).brain())
            self.assertEqual(first, reopened)
            self.assertEqual(first.step, saved["brain_step"])
            self.assertEqual(first.neurons, saved["neurons"])
            self.assertEqual(first.synapses, saved["synapses"])
            self.assertGreaterEqual(first.step, 4)
            self.assertEqual(len(reopened.nodes), first.neurons)
            self.assertTrue(all(0 <= e.pre < first.neurons and 0 <= e.post < first.neurons
                                for e in first.edges))


if __name__ == "__main__":
    unittest.main()
