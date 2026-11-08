"""Real-PyTorch regression tests for full chronological holdout evaluation."""
import math
import unittest

try:
    import torch
    from neurogenesis.foundation_train import evaluate_holdout
except ImportError:
    torch = None


@unittest.skipIf(torch is None, "optional PyTorch not installed")
class HoldoutEvaluationTests(unittest.TestCase):
    def test_every_window_is_scored_and_weighted(self):
        class FakeModel:
            def eval(self):
                pass

            def __call__(self, tokens):
                # Different losses for different window lengths.
                value = float(tokens.shape[1])
                return type("Result", (), {"token_loss": torch.tensor(value)})()

        result = evaluate_holdout(FakeModel(), bytes(range(10)),
                                  sequence=4, device="cpu")
        # 4, 4, 2 bytes: 3+3+1 predicted transitions.
        self.assertEqual(result["windows"], 3)
        self.assertEqual(result["scored_transitions"], 7)
        self.assertAlmostEqual(result["next_byte_ce_nats"], 26 / 7)

    def test_rejects_insufficient_holdout(self):
        with self.assertRaises(ValueError):
            evaluate_holdout(object(), b"abc", sequence=4, device="cpu")

    def test_nonfinite_loss_is_rejected(self):
        class BadModel:
            def eval(self):
                pass

            def __call__(self, tokens):
                return type("Result", (), {"token_loss": torch.tensor(float("nan"))})()

        with self.assertRaisesRegex(ValueError, "non-finite"):
            evaluate_holdout(BadModel(), b"abcdef", sequence=4, device="cpu")


if __name__ == "__main__":
    unittest.main()
