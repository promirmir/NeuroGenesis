"""Real event provenance and fake-activity prevention for embodied UI."""
from __future__ import annotations

import unittest

from neurogenesis.brain import Brain
from neurogenesis.neural_telemetry import snapshot_neural_telemetry
from neurogenesis.tk_avatar import NeuralAvatar, EVENT_FRAMES, presence_signal


class RecordingCanvas:
    def __init__(self):
        self.operations = []
        self.bindings = {}
    def bind(self, name, fn, add=None):
        self.bindings[name] = fn
    def winfo_width(self):
        return 950
    def winfo_height(self):
        return 475
    def delete(self, *args):
        self.operations.append(("delete", args))
    def create_oval(self, *args, **kwargs):
        self.operations.append(("oval", kwargs))
    def create_line(self, *args, **kwargs):
        self.operations.append(("line", kwargs))
    def create_polygon(self, *args, **kwargs):
        self.operations.append(("polygon", kwargs))
    def create_text(self, *args, **kwargs):
        self.operations.append(("text", kwargs))


class AvatarTests(unittest.TestCase):
    def test_event_only_from_real_saved_step(self):
        brain = Brain()
        initial = snapshot_neural_telemetry(brain)
        canvas = RecordingCanvas()
        avatar = NeuralAvatar(canvas)
        self.assertFalse(avatar.update_state(initial))
        self.assertEqual((avatar._step_frames, avatar._spike_frames), (0, 0))
        self.assertFalse(avatar.update_state(initial))
        self.assertEqual(avatar._last_recorded_spikes, 0)
        self.assertTrue(any(op[0] == "polygon" for op in canvas.operations))
        self.assertEqual(presence_signal(None, initial), (False, 0))
        with self.assertRaises(TypeError):
            presence_signal(initial, {"step": 99})
        with self.assertRaises(TypeError):
            avatar.update_state({"spikes": "fake"})

        brain.step([1.0] * brain.config.input_size)
        advanced = snapshot_neural_telemetry(brain)
        self.assertEqual(presence_signal(initial, advanced),
                         (True, sum(n.fired for n in advanced.nodes)))
        self.assertTrue(avatar.update_state(advanced))
        self.assertEqual(avatar._step_frames, EVENT_FRAMES)
        self.assertEqual(avatar._spike_frames, EVENT_FRAMES)
        avatar._step_frames = avatar._spike_frames = 0
        avatar.update_state(advanced)
        self.assertEqual(avatar._step_frames, 0)
        self.assertEqual(avatar._spike_frames, 0)

    def test_idle_camera_motion_is_distinct_from_telemetry(self):
        canvas = RecordingCanvas()
        avatar = NeuralAvatar(canvas)
        before = avatar.motion
        self.assertNotEqual(avatar.toggle_motion(), before)
        self.assertIsNone(avatar.latest)


if __name__ == "__main__":
    unittest.main()
