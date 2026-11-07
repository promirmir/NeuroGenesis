"""Real CPU PyTorch foundation tests; mandatory in foundation-cpu.yml.

The standard Windows EXE can import the original package with no PyTorch.
Dedicated foundation CI MUST install torch and run every test, not skip them.
"""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from neurogenesis.foundation import (
    FoundationBrain, FoundationConfig, encode_utf8, torch,
)
from neurogenesis.foundation_train import main as train_main


@unittest.skipUnless(torch is not None, "optional PyTorch installed in foundation-cpu CI")
class FoundationTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(42)
        self.cfg = FoundationConfig(
            hidden_size=32, fast_layers=1, slow_layers=1,
            chunk_size=4, max_sequence=48, parameter_limit=300_000)

    def test_causal_future_tokens_cannot_change_earlier_predictions(self):
        model = FoundationBrain(self.cfg).eval()
        a = torch.randint(0, 256, (2, 32), dtype=torch.long)
        b = a.clone()
        b[:, 21:] = (b[:, 21:] + 7) % 256
        with torch.no_grad():
            logits_a = model(a).logits
            logits_b = model(b).logits
        self.assertTrue(torch.equal(logits_a[:, :21], logits_b[:, :21]))
        self.assertFalse(torch.equal(logits_a[:, 21:], logits_b[:, 21:]))

    def test_fast_and_slow_cortex_receive_gradients(self):
        brain = FoundationBrain(self.cfg)
        data = torch.randint(0, 256, (2, 24), dtype=torch.long)
        out = brain(data)
        self.assertTrue(torch.isfinite(out.loss))
        out.loss.backward()
        self.assertGreater(float(brain.fast_cortex.weight_ih_l0.grad.abs().sum()), 0)
        self.assertGreater(float(brain.slow_cortex.weight_ih_l0.grad.abs().sum()), 0)
        self.assertGreater(float(brain.latent_predictor.weight.grad.abs().sum()), 0)

    def test_self_supervised_training_reduces_actual_next_byte_loss(self):
        brain = FoundationBrain(self.cfg)
        optimizer = torch.optim.AdamW(brain.parameters(), lr=0.012)
        sample = torch.tensor([list(b"abc" * 12)] * 3, dtype=torch.long)
        brain.eval()
        with torch.no_grad():
            before = float(brain(sample).token_loss)
        for _ in range(35):
            scores = brain.train_batch(sample, optimizer)
            self.assertTrue(all(__import__("math").isfinite(v) for v in scores.values()))
        brain.eval()
        with torch.no_grad():
            after = float(brain(sample).token_loss)
        self.assertLess(after, before * 0.75)
        self.assertLess(after, 2.5)
        self.assertGreater(brain.parameter_count, 10_000)
        self.assertEqual(brain.statistics()["trained_data_provenance"],
                         "not recorded in weights")

    def test_atomic_checkpoint_restores_trainable_foundation_exactly(self):
        brain = FoundationBrain(self.cfg)
        optimizer = torch.optim.AdamW(brain.parameters(), lr=0.003)
        sample = torch.randint(0, 256, (1, 24), dtype=torch.long)
        for _ in range(3):
            brain.train_batch(sample, optimizer)
        brain.eval()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "foundation.pt"
            brain.save_checkpoint(path, training_steps=3)
            self.assertTrue(path.exists())
            restored, step = FoundationBrain.load_checkpoint(path)
            restored.eval()
            self.assertEqual(step, 3)
            self.assertEqual(brain.parameter_count, restored.parameter_count)
            with torch.no_grad():
                self.assertTrue(torch.equal(brain(sample).logits,
                                            restored(sample).logits))
            self.assertEqual(brain.statistics()["parameters"],
                             restored.statistics()["parameters"])

    def test_checkpoint_version_and_corrupt_weights_fail_closed(self):
        brain = FoundationBrain(self.cfg)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.pt"
            brain.save_checkpoint(path)
            state = torch.load(path, weights_only=True)
            state["version"] = 9
            torch.save(state, path)
            with self.assertRaises(ValueError):
                FoundationBrain.load_checkpoint(path)
            state["version"] = 1
            state["parameters"]["embedding.weight"] = torch.ones(
                1, brain.config.hidden_size)
            torch.save(state, path)
            with self.assertRaises(RuntimeError):
                FoundationBrain.load_checkpoint(path)

    def test_invalid_shapes_dtypes_and_limits_fail_closed(self):
        brain = FoundationBrain(self.cfg)
        for case in (torch.randn(1, 8), torch.ones(8, dtype=torch.long),
                     torch.full((1, 8), 256, dtype=torch.long),
                     torch.ones((1, 100), dtype=torch.long),
                     torch.ones((0, 8), dtype=torch.long)):
            with self.subTest(shape=tuple(case.shape)), self.assertRaises(ValueError):
                brain(case)
        with self.assertRaises(ValueError):
            FoundationBrain(FoundationConfig(
                hidden_size=32, fast_layers=1, slow_layers=1,
                parameter_limit=10_000))
        with self.assertRaises(ValueError):
            FoundationConfig(hidden_size=15)
        with self.assertRaises(ValueError):
            FoundationConfig(chunk_size=1)
        with self.assertRaises(ValueError):
            brain.save_checkpoint("/tmp/no-such-weights.pt", training_steps=-1)

    def test_training_cli_requires_explicit_permission_and_uses_local_only(self):
        corpus = (b"abc def ghi 123 . " * 64)
        with tempfile.TemporaryDirectory() as folder:
            inp = Path(folder) / "corpus.txt"
            out = Path(folder) / "brain.pt"
            inp.write_bytes(corpus)
            with self.assertRaises(SystemExit):
                train_main(["--input", str(inp), "--output", str(out),
                            "--steps", "1", "--sequence", "16",
                            "--hidden", "32", "--fast-layers", "1",
                            "--chunk", "4"])
            self.assertFalse(out.exists())
            buf = StringIO()
            with redirect_stdout(buf):
                rc = train_main([
                    "--input", str(inp), "--output", str(out),
                    "--confirm-corpus-rights", "--steps", "3",
                    "--sequence", "16", "--hidden", "32",
                    "--fast-layers", "1", "--chunk", "4",
                    "--batch", "2", "--device", "cpu",
                ])
            self.assertEqual(rc, 0)
            self.assertTrue(out.exists())
            self.assertIn('"ready_for_semantic_chat": false', buf.getvalue())
            model, steps = FoundationBrain.load_checkpoint(out)
            self.assertEqual(steps, 3)
            self.assertEqual(model.config.hidden_size, 32)

    def test_byte_input_preserves_order_and_polish_utf8(self):
        self.assertNotEqual(encode_utf8("kot pies"), encode_utf8("pies kot"))
        self.assertGreater(len(encode_utf8("żółw")), 4)
        self.assertEqual(encode_utf8("abc"), [97, 98, 99])
        with self.assertRaises(ValueError):
            encode_utf8("")


if __name__ == "__main__":
    unittest.main()
