"""Self-contained regression tests for a simple non-neural research control."""
import unittest
from neurogenesis.controls import OnlineMarkovBaseline, constant_half_mse


class MarkovBaselineTests(unittest.TestCase):
    def test_initial_forecast_and_no_labels(self):
        model = OnlineMarkovBaseline(width=2)
        self.assertIsNone(model.step([1, 0]))
        self.assertEqual(model.next_forecast, (0.5, 0.5))
        self.assertEqual(model.learned_cues, 0)

    def test_prediction_scored_before_training(self):
        model = OnlineMarkovBaseline(width=2)
        model.step([1, 0])
        self.assertEqual(model.step([0, 1]), 0.25)
        self.assertEqual(model.learned_cues, 1)
        model.step([1, 0])
        self.assertEqual(model.next_forecast, (0.0, 1.0))
        self.assertEqual(model.step([0, 1]), 0.0)

    def test_unseen_cues_use_prior_not_future_targets(self):
        model = OnlineMarkovBaseline(width=2)
        model.step([1, 0])
        model.step([0, 1])
        self.assertEqual(model.next_forecast, (0.5, 0.5))
        self.assertEqual(model.learned_cues, 1)

    def test_frozen_probe_retains_learned_table(self):
        model = OnlineMarkovBaseline(width=2)
        model.step([1, 0]); model.step([0, 1])
        before = (model.learned_cues, model._counts.copy(), {k:v.copy() for k,v in model._sums.items()})
        model.step([1, 0], learn=False)
        model.step([0, 1], learn=False)
        self.assertEqual((model.learned_cues, model._counts, model._sums), before)

    def test_invalid_values_do_not_mutate(self):
        model = OnlineMarkovBaseline(width=2)
        model.step([1, 0])
        before = (model._previous_key, model.next_forecast, model.scored)
        for bad in ([float('nan'), 0], [float('inf'), 0], [2, 0], [0], [True, 0]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                model.step(bad)
            self.assertEqual((model._previous_key, model.next_forecast, model.scored), before)
        with self.assertRaises(ValueError): model.step([1, 0], learn=1)

    def test_deterministic_stream(self):
        data = [[1, 0], [0, 1]] * 20
        def run():
            m = OnlineMarkovBaseline(width=2)
            return [m.step(x) for x in data]
        self.assertEqual(run(), run())
        self.assertLess(sum(run()[-10:]) / 10, 0.25)

    def test_baseline_validation(self):
        self.assertEqual(constant_half_mse([1,0]), 0.25)
        for x in ([], [float('nan')], [True]):
            with self.assertRaises(ValueError): constant_half_mse(x)

    def test_parameter_validation(self):
        for n in (0, True, 4097):
            with self.assertRaises(ValueError): OnlineMarkovBaseline(width=n)
        for t in (0.0, 1.0, float('nan'), True):
            with self.assertRaises(ValueError): OnlineMarkovBaseline(threshold=t)


if __name__ == '__main__': unittest.main()
