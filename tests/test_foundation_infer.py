"""Mandatory actual PyTorch CPU proof for isolated neural checkpoint inference.

No network, no external corpus, no semantic-chat claims, no user-data files.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import tempfile
import threading
import unittest

from neurogenesis.foundation import FoundationBrain, FoundationConfig, torch
from neurogenesis.foundation_infer import generate_candidate
from neurogenesis.memory import ExperienceMemory


@unittest.skipUnless(torch is not None, "real PyTorch CPU is installed by foundation CI")
class CandidateInferenceTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(19)
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.path = self.root / "candidate.pt"
        self.cfg = FoundationConfig(hidden_size=16, fast_layers=1, slow_layers=1,
                                    max_sequence=24, chunk_size=4,
                                    parameter_limit=300_000)
        self.model = FoundationBrain(self.cfg)
        training = torch.tensor([list(b"abcdefabcdefabcdefabcd")], dtype=torch.long)
        self.model.train_batch(training, torch.optim.AdamW(self.model.parameters(), lr=0.01))
        self.model.save_checkpoint(self.path, training_steps=1)

    def test_actual_greedy_byte_matches_saved_model_logits(self):
        loaded, steps = FoundationBrain.load_checkpoint(self.path, device="cpu")
        loaded.eval()
        with torch.inference_mode():
            source = torch.tensor([list(b"abcdef")], dtype=torch.long)
            expected = int(torch.argmax(loaded(source).logits[0, -1]).item())
        result = generate_candidate(self.path, "abcdef", trust_checkpoint=True,
                                    max_new_bytes=1, device="cpu")
        self.assertEqual(steps, 1)
        self.assertEqual(result["generated_hex"], bytes([expected]).hex())
        self.assertEqual(result["response_kind"], "ungrounded_neural_experiment")
        self.assertEqual(result["source_citations"], [])
        self.assertFalse(result["promoted_to_chat"])
        self.assertFalse(result["verified_natural_language_answer"])
        self.assertFalse(result["internet_used"])
        self.assertTrue(math.isfinite(result["mean_chosen_token_log_probability"]))

    def test_reloading_same_checkpoint_is_deterministic_and_bounded(self):
        first = generate_candidate(self.path, "żółw", trust_checkpoint=True,
                                   max_new_bytes=4)
        second = generate_candidate(self.path, "żółw", trust_checkpoint=True,
                                    max_new_bytes=4)
        self.assertEqual(first["generated_hex"], second["generated_hex"])
        self.assertEqual(first["generated_bytes"], 4)
        self.assertGreater(first["bytes_per_second"], 0)
        self.assertEqual(first["device"], "cpu")
        self.assertEqual(first["trained_steps_in_checkpoint"], 1)
        self.assertEqual(first["context_bytes_used"], len("żółw".encode("utf-8")))

    def test_refuses_untrusted_file_untrained_checkpoint_and_invalid_inputs(self):
        with self.assertRaises(PermissionError):
            generate_candidate(self.path, "abcdef")
        untrained = self.root / "untrained.pt"
        self.model.save_checkpoint(untrained, training_steps=0)
        with self.assertRaisesRegex(ValueError, "untrained"):
            generate_candidate(untrained, "abcdef", trust_checkpoint=True)
        for prompt, n in [("", 2), ("x", 2), ("x" * 513, 2),
                          ("abcdef", 0), ("abcdef", 65), ("abcdef", True)]:
            with self.subTest(prompt=prompt[:8], n=n), self.assertRaises(ValueError):
                generate_candidate(self.path, prompt, trust_checkpoint=True,
                                   max_new_bytes=n)
        with self.assertRaises(ValueError):
            generate_candidate(self.path, "abcdef", trust_checkpoint=True, device="invalid")
        with self.assertRaises(ValueError):
            generate_candidate(self.root / "absent.pt", "abcdef", trust_checkpoint=True)
        with self.assertRaises(ValueError):
            generate_candidate(self.path, "abcdef", trust_checkpoint=True,
                               cancel_event="not a stop event")

    def test_cancellation_and_failed_checkpoint_never_mutate_memory(self):
        db = self.root / "private.sqlite3"
        memory = ExperienceMemory(db)
        memory.teach("Kto to?", "Prywatna pamięć.")
        initial_hash = hashlib.sha256(db.read_bytes()).hexdigest()
        cancelled = threading.Event()
        cancelled.set()
        with self.assertRaises(InterruptedError):
            generate_candidate(self.path, "abcdef", trust_checkpoint=True,
                               cancel_event=cancelled)
        bad = self.root / "invalid.pt"
        bad.write_text("not weights", encoding="utf-8")
        with self.assertRaises(Exception):
            generate_candidate(bad, "abcdef", trust_checkpoint=True)
        self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(), initial_hash)
        self.assertEqual(ExperienceMemory(db).taught_answer("Kto to?")["answer"],
                         "Prywatna pamięć.")


if __name__ == "__main__":
    unittest.main()
