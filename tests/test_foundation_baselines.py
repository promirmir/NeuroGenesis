"""Offline, dependency-free regression tests for independent baselines."""
import unittest

from neurogenesis.foundation_baselines import evaluate


class FoundationBaselineTests(unittest.TestCase):
    def test_reproducible_and_context_advantage_on_predictable_sequence(self):
        data = bytes([0, 1] * 1000)
        result = evaluate(data)
        self.assertEqual(result, evaluate(data))
        self.assertLess(result["markov1_next_byte_ce_nats"],
                        result["unigram_next_byte_ce_nats"])
        self.assertEqual(result["scored_holdout_transitions"], 199)

    def test_holdout_never_updates_training_counts(self):
        training = bytes([0, 1] * 45)
        a = evaluate(training + bytes([2] * 10))
        b = evaluate(training + bytes([3] * 10))
        self.assertAlmostEqual(a["unigram_next_byte_ce_nats"],
                               b["unigram_next_byte_ce_nats"])
        self.assertEqual(a["train_bytes"], 90)

    def test_invalid_inputs_fail_closed(self):
        for data in (b"", b"a" * 99, bytearray(b"a" * 100)):
            with self.subTest(data_type=type(data)), self.assertRaises(ValueError):
                evaluate(data)
        for smoothing in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                evaluate(b"a" * 100, smoothing=smoothing)
        with self.assertRaises(ValueError):
            evaluate(b"a" * 100, split_fraction=1.0)


if __name__ == "__main__":
    unittest.main()
