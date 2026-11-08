"""Windows Foundation Lab contracts: no prompt in argv, no auto model load."""
from __future__ import annotations

import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from neurogenesis.tk_foundation_lab import make_inference_command


class FoundationLabTests(unittest.TestCase):
    def test_trusted_local_checkpoint_and_bounded_private_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            python = root / "python.exe"
            checkpoint = root / "trained.pt"
            python.write_bytes(b"local")
            checkpoint.write_bytes(b"trusted-local-data")
            prompt = "Próba prywatna XYZ"
            argv = make_inference_command(
                str(python), str(checkpoint), confirmed=True,
                count=16, device="cpu", prompt=prompt)
            self.assertEqual(argv[0], str(python))
            self.assertIn("--prompt-stdin", argv)
            self.assertNotIn("--prompt", argv)
            self.assertNotIn(prompt, " ".join(argv))
            self.assertEqual(argv[-1], "cpu")
            with self.assertRaises(PermissionError):
                make_inference_command(
                    str(python), str(checkpoint), confirmed=False,
                    count=16, device="cpu", prompt=prompt)
            with self.assertRaises(ValueError):
                make_inference_command(
                    str(python), str(checkpoint), confirmed=True,
                    count=65, device="cpu", prompt=prompt)
            with self.assertRaises(ValueError):
                make_inference_command(
                    str(python), str(checkpoint), confirmed=True,
                    count=8, device="cpu", prompt="x")

    def test_stdin_cli_passes_private_input_to_existing_model_api(self):
        from neurogenesis import foundation_infer
        fake_stdin = mock.Mock()
        fake_stdin.buffer = io.BytesIO("Próba lokalna".encode("utf-8"))
        fake_result = {
            "status": "experimental_neural_byte_continuation",
            "verified_natural_language_answer": False,
            "promoted_to_chat": False,
        }
        with mock.patch.object(foundation_infer.sys, "stdin", fake_stdin), \
             mock.patch.object(foundation_infer, "generate_candidate",
                               return_value=fake_result) as generator, \
             mock.patch("builtins.print"):
            self.assertEqual(foundation_infer.main([
                "--checkpoint", "local.pt", "--prompt-stdin",
                "--confirm-local-checkpoint", "--bytes", "4",
                "--device", "cpu"]), 0)
        self.assertEqual(generator.call_args.args[1], "Próba lokalna")
        self.assertTrue(generator.call_args.kwargs["trust_checkpoint"])
        self.assertEqual(generator.call_args.kwargs["max_new_bytes"], 4)

    def test_worker_refuses_fabricated_model_output(self):
        from neurogenesis.tk_foundation_lab import FoundationLabWorker
        class FakeProc:
            returncode = 0
            def __init__(self, *args, **kwargs):
                self.args = args
            def communicate(self, prompt, timeout):
                self.prompt = prompt
                return ('{"status":"pretend","verified_natural_language_answer":true}', "")
        worker = FoundationLabWorker()
        with mock.patch("subprocess.Popen", FakeProc):
            with self.assertRaises(ValueError):
                worker.run(["python.exe", "-m", "neurogenesis.foundation_infer"], "local prompt")


if __name__ == "__main__":
    unittest.main()
