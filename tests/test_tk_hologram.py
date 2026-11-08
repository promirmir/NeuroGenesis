"""3D-like orbital projection draws only verified telemetry, never fake spikes."""
from __future__ import annotations

import unittest

from neurogenesis.brain import Brain, BrainConfig
from neurogenesis.neural_telemetry import snapshot_neural_telemetry
from neurogenesis.tk_hologram import (
    EVENT_FRAMES, HolographicBrain, MAX_HOLOGRAM_NODES,
    project_real_nodes,
)


class DummyCanvas:
    def __init__(self):
        self.ops = []
        self.callbacks = {}
    def bind(self, name, callback, add=None):
        self.callbacks[name] = callback
    def winfo_width(self):
        return 900
    def winfo_height(self):
        return 500
    def delete(self, *args):
        self.ops.append(("delete", args))
    def create_oval(self, *args, **kwargs):
        self.ops.append(("oval", kwargs))
    def create_line(self, *args, **kwargs):
        self.ops.append(("line", kwargs))
    def create_text(self, *args, **kwargs):
        self.ops.append(("text", kwargs))
    def create_arc(self, *args, **kwargs):
        self.ops.append(("arc", kwargs))


class HolographicBrainTests(unittest.TestCase):
    def test_real_nodes_persist_and_idle_does_not_forge_spikes(self):
        brain = Brain()
        c = DummyCanvas()
        view = HolographicBrain(c)
        initial = snapshot_neural_telemetry(brain)
        self.assertTrue(view.update_state(initial))
        self.assertEqual(view._event_frames, 0)
        self.assertEqual(view._step_frames, 0)
        self.assertFalse(view.update_state(initial))
        self.assertEqual(set(project_real_nodes(initial, .45, 900, 500)),
                         {node.index for node in initial.nodes})
        self.assertEqual(view.latest.step, 0)
        self.assertFalse(any(op[0] == "oval" and op[1].get("fill") == "#d8ffff"
                             for op in c.ops))

        brain.step([1.0] * brain.config.input_size)
        updated = snapshot_neural_telemetry(brain)
        self.assertTrue(view.update_state(updated))
        self.assertEqual(view.latest.total_spikes, brain.total_spikes)
        self.assertEqual(view._event_step, brain.steps)
        self.assertEqual(view._event_frames, EVENT_FRAMES)
        self.assertEqual(view._step_frames, EVENT_FRAMES)
        self.assertFalse(view.update_state(updated))
        self.assertEqual(view._event_frames, EVENT_FRAMES)
        # Rendering an idle step does NOT invent a new event.
        view._event_frames = 0
        c.ops.clear()
        view.draw()
        self.assertFalse(any(op[0] == "oval" and op[1].get("fill") == "#d8ffff"
                             for op in c.ops))

    def test_projection_is_bounded_and_input_must_be_real_telemetry(self):
        brain = Brain(BrainConfig(initial_neurons=180, max_neurons=512))
        data = snapshot_neural_telemetry(brain)
        points = project_real_nodes(data, 1.1, 1100, 550)
        self.assertEqual(len(points), MAX_HOLOGRAM_NODES)
        self.assertEqual(len(set(points)), MAX_HOLOGRAM_NODES)
        view = HolographicBrain(DummyCanvas())
        with self.assertRaises(TypeError):
            view.update_state({"brain": "not an actual snapshot"})
        with self.assertRaises(TypeError):
            project_real_nodes(None, 1, 900, 500)

    def test_expanded_headroom_applies_only_to_new_brains(self):
        new = Brain()
        self.assertEqual(
            (new.config.max_neurons, new.config.max_synapses,
             new.config.max_patterns), (512, 4096, 1024))
        old = Brain(BrainConfig(max_neurons=128, max_synapses=1024,
                                max_patterns=256))
        saved = old.to_dict()
        loaded = Brain.from_dict(saved)
        self.assertEqual(loaded.config.max_neurons, 128)
        self.assertEqual(loaded.config.max_synapses, 1024)
        self.assertEqual(loaded.config.max_patterns, 256)
        self.assertEqual(loaded.to_dict(), saved)


if __name__ == "__main__":
    unittest.main()
