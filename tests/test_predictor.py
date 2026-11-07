import json
from pathlib import Path
import tempfile
import unittest

from neurogenesis import Brain
from neurogenesis.predictor import NextInputPredictor, prediction_control


class PredictorTests(unittest.TestCase):
    def test_online_prediction_improves_on_repeating_sequence(self):
        result = prediction_control(steps=600)
        for key in ("growth_enabled", "fixed_structure"):
            self.assertLess(result["evaluation"][key]["last_window_mse"],
                            result["evaluation"][key]["first_window_mse"])
            self.assertLess(result["evaluation"][key]["last_window_mse"], 0.25)
        self.assertGreater(result["evaluation"]["growth_enabled"]["neurons"],
                           result["evaluation"]["fixed_structure"]["neurons"])

    def test_predictor_snapshot_replay(self):
        original = NextInputPredictor(Brain())
        inputs = [[1.0 if i % 2 == j % 2 else 0.0 for i in range(8)] for j in range(8)]
        for i in range(60):
            original.step(inputs[i % len(inputs)])
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "predictor.snapshot.json"
            original.save(file)
            cloned = NextInputPredictor.load(file)
            self.assertEqual(original.to_dict(), cloned.to_dict())
            for i in range(30):
                x = inputs[i % len(inputs)]
                self.assertEqual(original.step(x), cloned.step(x))
                self.assertEqual(original.to_dict(), cloned.to_dict())

    def test_snapshot_is_validated(self):
        predictor = NextInputPredictor()
        state = predictor.to_dict()
        state["weights"][0].append(0.0)
        with self.assertRaises(ValueError):
            NextInputPredictor.from_dict(state)
        with self.assertRaises(ValueError):
            predictor.step([float("nan")] * 8)


if __name__ == "__main__":
    unittest.main()
