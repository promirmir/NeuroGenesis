"""Dependency-free shipped Tk connectome renderer: only actual graph changes."""
from __future__ import annotations

import unittest

from neurogenesis.brain import Brain
from neurogenesis.neural_telemetry import snapshot_neural_telemetry
from neurogenesis.tk_connectome import TkConnectome


class CanvasDouble:
    def __init__(self):
        self.ops = []
    def bind(self, event, callback):
        self.bound = event
    def winfo_width(self):
        return 1100
    def winfo_height(self):
        return 640
    def delete(self, *args):
        self.ops.append(("clear", args))
    def create_oval(self, *args, **kwargs):
        self.ops.append(("oval", kwargs))
    def create_line(self, *args, **kwargs):
        self.ops.append(("line", kwargs))
    def create_text(self, *args, **kwargs):
        self.ops.append(("text", kwargs))


class TkConnectomeRegression(unittest.TestCase):
    def test_real_activity_edges_and_no_idle_animation(self):
        canvas = CanvasDouble()
        view = TkConnectome(canvas)
        brain = Brain()
        initial = snapshot_neural_telemetry(brain)
        self.assertTrue(view.render(initial))
        lines = [op for op in canvas.ops if op[0] == "line"]
        self.assertEqual(len(lines), len(brain.synapses))
        self.assertFalse(view.render(initial))
        self.assertEqual(len([op for op in canvas.ops if op[0] == "clear"]), 1)
        brain.step([1.0] * brain.config.input_size)
        updated = snapshot_neural_telemetry(brain)
        self.assertTrue(view.render(updated))
        self.assertEqual(len([op for op in canvas.ops if op[0] == "clear"]), 2)
        self.assertEqual(updated.total_spikes, brain.total_spikes)
        bright = [op for op in canvas.ops if op[0] == "oval"
                  and op[1].get("fill") == "#e8fcff"]
        self.assertEqual(len(bright), sum(bool(s) for s in brain.spikes))
        self.assertEqual(view._step, brain.steps)

    def test_wrong_inputs_are_refused(self):
        canvas = CanvasDouble()
        view = TkConnectome(canvas)
        with self.assertRaises(TypeError):
            view.render({"spikes": "made up"})


if __name__ == "__main__":
    unittest.main()
