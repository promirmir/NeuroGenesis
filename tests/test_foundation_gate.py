"""Independent two-file model retention gate, actual PyTorch CPU on CI.

Only fictional local data; no network, no user SQLite, no borrowed corpus.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import tempfile
import unittest

from neurogenesis.foundation import FoundationBrain, FoundationConfig, torch
from neurogenesis.foundation_gate import audit_candidate, decide_retention


class PureRetentionDecisionTests(unittest.TestCase):
    def test_candidate_must_improve_new_task_without_forgetting_old(self):
        passed = decide_retention(
            incumbent_old_ce=2.0, candidate_old_ce=2.04,
            incumbent_new_ce=4.0, candidate_new_ce=3.0)
        self.assertTrue(passed["old_skill_retained"])
        self.assertTrue(passed["new_task_improved"])
        self.assertTrue(passed["passes_numeric_retention_gate"])
        self.assertFalse(passed["automatically_promoted"])
        self.assertFalse(passed["ready_for_semantic_chat"])
        forgetting = decide_retention(
            incumbent_old_ce=2.0, candidate_old_ce=3.0,
            incumbent_new_ce=4.0, candidate_new_ce=3.0)
        self.assertFalse(forgetting["passes_numeric_retention_gate"])
        stagnant = decide_retention(
            incumbent_old_ce=2.0, candidate_old_ce=2.0,
            incumbent_new_ce=4.0, candidate_new_ce=4.0)
        self.assertFalse(stagnant["passes_numeric_retention_gate"])

    def test_invalid_floats_or_thresholds_refused(self):
        with self.assertRaises(ValueError):
            decide_retention(
                incumbent_old_ce=float("nan"), candidate_old_ce=2,
                incumbent_new_ce=3, candidate_new_ce=2)
        with self.assertRaises(ValueError):
            decide_retention(
                incumbent_old_ce=2, candidate_old_ce=2,
                incumbent_new_ce=4, candidate_new_ce=3, max_old_regression=-1)
        with self.assertRaises(ValueError):
            decide_retention(
                incumbent_old_ce=2, candidate_old_ce=2,
                incumbent_new_ce=4, candidate_new_ce=3,
                min_new_improvement=float("inf"))


@unittest.skipUnless(torch is not None, "dedicated real PyTorch CPU gate installs torch")
class RealCheckpointRetentionTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(37)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.old = self.root / "old.txt"
        self.new = self.root / "new.txt"
        self.old.write_text("arytmetyka neurony pamięć. " * 32, encoding="utf-8")
        self.new.write_text("teleskop obserwuje gwiazdy. " * 32, encoding="utf-8")
        self.incumbent = self.root / "incumbent.pt"
        self.candidate = self.root / "candidate.pt"
        self.cfg = FoundationConfig(hidden_size=16, fast_layers=1, slow_layers=1,
                                    chunk_size=4, max_sequence=32,
                                    parameter_limit=300_000)
        model = FoundationBrain(self.cfg)
        opt = torch.optim.AdamW(model.parameters(), lr=0.006)
        x = torch.tensor([list(b"abcabcabcabcabcabcabcabcabcabc")], dtype=torch.long)
        for _ in range(3):
            model.train_batch(x, opt)
        model.save_checkpoint(self.incumbent, training_steps=3)
        alt = FoundationBrain.load_checkpoint(self.incumbent)[0]
        opt2 = torch.optim.AdamW(alt.parameters(), lr=0.003)
        y = torch.tensor([list(b"xyzxyzxyzxyzxyzxyzxyzxyzxyzxyz")], dtype=torch.long)
        for _ in range(2):
            alt.train_batch(y, opt2)
        alt.save_checkpoint(self.candidate, training_steps=5)

    def test_actual_candidate_scores_two_distinct_files_and_never_deploys(self):
        old_sha = hashlib.sha256(self.old.read_bytes()).hexdigest()
        incumbent_sha = hashlib.sha256(self.incumbent.read_bytes()).hexdigest()
        candidate_sha = hashlib.sha256(self.candidate.read_bytes()).hexdigest()
        report = audit_candidate(
            self.incumbent, self.candidate, self.old, self.new,
            trust_checkpoints=True, confirm_corpus_rights=True,
            sequence=16, device="cpu")
        self.assertEqual(report["status"], "offline_paired_checkpoint_retention_audit")
        self.assertEqual(report["old_audit_sha256"], old_sha)
        self.assertEqual(report["incumbent_steps"], 3)
        self.assertEqual(report["candidate_steps"], 5)
        self.assertGreater(report["old_audit_transitions"], 0)
        self.assertGreater(report["new_audit_transitions"], 0)
        self.assertNotEqual(report["old_audit_sha256"], report["new_audit_sha256"])
        for key in ("incumbent_old_ce_nats", "candidate_old_ce_nats",
                    "incumbent_new_ce_nats", "candidate_new_ce_nats"):
            self.assertTrue(math.isfinite(report[key]))
        self.assertFalse(report["automatically_promoted"])
        self.assertFalse(report["ready_for_semantic_chat"])
        self.assertFalse(report["internet_used"])
        self.assertEqual(hashlib.sha256(self.incumbent.read_bytes()).hexdigest(),
                         incumbent_sha)
        self.assertEqual(hashlib.sha256(self.candidate.read_bytes()).hexdigest(),
                         candidate_sha)

    def test_input_validation_and_corruption_fail_closed(self):
        with self.assertRaises(PermissionError):
            audit_candidate(self.incumbent, self.candidate, self.old, self.new)
        with self.assertRaises(ValueError):
            audit_candidate(self.incumbent, self.incumbent, self.old, self.new,
                            trust_checkpoints=True, confirm_corpus_rights=True)
        with self.assertRaises(ValueError):
            audit_candidate(self.incumbent, self.candidate, self.old, self.old,
                            trust_checkpoints=True, confirm_corpus_rights=True)
        with self.assertRaises(ValueError):
            audit_candidate(self.incumbent, self.candidate, self.old, self.new,
                            sequence=64, trust_checkpoints=True,
                            confirm_corpus_rights=True)
        invalid = self.root / "binary.txt"
        invalid.write_bytes(b"\xff" * 200)
        with self.assertRaises(UnicodeDecodeError):
            audit_candidate(self.incumbent, self.candidate, invalid, self.new,
                            sequence=16, trust_checkpoints=True,
                            confirm_corpus_rights=True)

    def test_checkpoint_architecture_mismatch_refuses_unfair_comparison(self):
        other = FoundationBrain(FoundationConfig(
            hidden_size=32, fast_layers=1, slow_layers=1, chunk_size=4,
            max_sequence=32, parameter_limit=300_000))
        other.save_checkpoint(self.root / "different.pt", training_steps=1)
        with self.assertRaisesRegex(ValueError, "architecture"):
            audit_candidate(self.incumbent, self.root / "different.pt",
                            self.old, self.new, sequence=16,
                            trust_checkpoints=True, confirm_corpus_rights=True)


if __name__ == "__main__":
    unittest.main()
