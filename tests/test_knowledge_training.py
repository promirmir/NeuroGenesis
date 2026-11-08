"""Rights-gated internet evidence -> real PyTorch Foundation training tests.

Synthetic fictional documents only. No real web/network; no copyrighted corpus.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import tempfile
import unittest

from neurogenesis.foundation import FoundationBrain, torch
from neurogenesis.knowledge_train import (
    markov_holdout_cross_entropy, train_approved_knowledge,
)
from neurogenesis.memory import ExperienceMemory
from neurogenesis.web_sense import WebObservation


def synthetic_document(name: str, *, version: str = "v1") -> WebObservation:
    text = ((name + " " + version + " sieci neuronowe wykazują plastyczność. ") * 95)
    raw = text.encode("utf-8")
    return WebObservation(
        url="https://example.org/" + name, host="example.org", text=text,
        content_sha256=hashlib.sha256(raw).hexdigest(),
        retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
        bytes_read=len(raw))


class ApprovedKnowledgeRightsTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db = Path(folder.name) / "private.sqlite3"
        self.output = Path(folder.name) / "candidate.pt"
        self.memory = ExperienceMemory(self.db)

    def add_sources(self):
        ids = []
        for key in ("alpha", "beta", "gamma"):
            ids.append(self.memory.observe_web(synthetic_document(key))["event_id"])
        return self.memory.knowledge_sources(limit=20)

    def test_training_rights_are_not_inferred_or_auto_approved(self):
        sources = self.add_sources()
        self.assertTrue(all(s["rights_status"] == "unverified" for s in sources))
        self.assertEqual(self.memory.approved_training_documents(), [])
        with self.assertRaises(PermissionError):
            train_approved_knowledge(self.db, self.output, confirm_rights=False)
        self.assertFalse(self.output.exists())
        with self.assertRaises(ValueError):
            self.memory.set_source_training_rights(9999, True)
        with self.assertRaises(ValueError):
            self.memory.set_source_training_rights(sources[0]["id"], "yes")

    def test_only_latest_explicitly_approved_versions_in_training(self):
        sources = self.add_sources()
        for s in sources:
            self.memory.set_source_training_rights(s["id"], True)
        self.assertEqual(len(self.memory.approved_training_documents()), 3)
        old = next(s for s in sources if s["url"].endswith("/alpha"))
        self.memory.observe_web(synthetic_document("alpha", version="v2"))
        # Old approved revision remains for history but cannot train silently.
        self.assertEqual(len(self.memory.approved_training_documents()), 2)
        latest = next(s for s in self.memory.knowledge_sources()
                      if s["url"].endswith("/alpha"))
        self.assertEqual(latest["version"], 2)
        self.assertEqual(latest["rights_status"], "unverified")
        self.memory.set_source_training_rights(latest["id"], True)
        self.assertEqual(len(self.memory.approved_training_documents()), 3)

    def test_rights_revocation_and_deletion_remove_permission_rows(self):
        sources = self.add_sources()
        source = sources[0]
        self.memory.set_source_training_rights(source["id"], True)
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(
                con.execute("SELECT COUNT(*) FROM knowledge_rights_audit").fetchone()[0], 1)
        self.memory.set_source_training_rights(source["id"], False)
        self.assertEqual(self.memory.approved_training_documents(), [])
        self.assertEqual(self.memory.knowledge_sources()[0]["rights_status"], "training-denied")
        self.memory.delete_event(source["id"])
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(
                con.execute("SELECT COUNT(*) FROM knowledge_rights_audit").fetchone()[0], 0)

    def test_markov_baseline_uses_disjoint_training_counts(self):
        train = [b"abcdabcdabcd", b"ababababab"]
        holdout = b"abcdabcd"
        score = markov_holdout_cross_entropy(train, holdout)
        self.assertTrue(math.isfinite(score))
        self.assertGreater(score, 0)
        with self.assertRaises(ValueError):
            markov_holdout_cross_entropy(train, b"x")

    @unittest.skipIf(torch is None, "dedicated CI installs real PyTorch CPU")
    def test_real_cpu_foundation_updates_with_strict_document_holdout(self):
        sources = self.add_sources()
        for s in sources:
            self.memory.set_source_training_rights(s["id"], True)
        progress = []
        report = train_approved_knowledge(
            self.db, self.output, confirm_rights=True,
            steps=3, sequence=16, batch=1, hidden=16, seed=11, device="cpu",
            on_progress=lambda step, metrics: progress.append((step, metrics["loss"])))
        self.assertEqual([p[0] for p in progress], [1, 2, 3])
        self.assertTrue(all(math.isfinite(p[1]) for p in progress))
        # Publish only synthetic, non-personal CI fixture metrics, never
        # source text or a private operator dataset.
        keys = ("heldout_next_byte_ce_before", "heldout_next_byte_ce_after",
                "heldout_markov_ce_nats", "heldout_improved", "beats_markov_baseline",
                "train_steps_per_second", "device", "training_steps")
        print("KNOWLEDGE_TRAIN_CPU_METRICS=" +
              json.dumps({k: report[k] for k in keys}, sort_keys=True), flush=True)
        self.assertEqual(report["training_steps"], 3)
        self.assertEqual(report["device"], "cpu")
        self.assertEqual(report["trained_documents"], 2)
        self.assertEqual(report["holdout_documents"], 1)
        self.assertGreater(report["holdout_scored_transitions"], 0)
        self.assertTrue(math.isfinite(report["heldout_next_byte_ce_before"]))
        self.assertTrue(math.isfinite(report["heldout_next_byte_ce_after"]))
        self.assertTrue(math.isfinite(report["heldout_markov_ce_nats"]))
        self.assertFalse(report["ready_for_semantic_chat"])
        self.assertTrue(report["checkpoint_candidate_written"])
        self.assertTrue(self.output.exists())
        model, steps = FoundationBrain.load_checkpoint(self.output, device="cpu")
        self.assertEqual(steps, 3)
        self.assertEqual(model.parameter_count, report["parameter_count"])
        self.assertEqual(self.memory.status()["records_with_raw_text"], 0)

    @unittest.skipIf(torch is None, "dedicated CI installs real PyTorch CPU")
    def test_cancel_before_gradient_updates_never_writes_checkpoint(self):
        import threading
        for src in self.add_sources():
            self.memory.set_source_training_rights(src["id"], True)
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(InterruptedError):
            train_approved_knowledge(
                self.db, self.output, confirm_rights=True, steps=4,
                sequence=16, batch=1, hidden=16, device="cpu", cancel_event=cancel)
        self.assertFalse(self.output.exists())

    @unittest.skipIf(torch is None, "dedicated CI installs real PyTorch CPU")
    def test_training_never_starts_with_only_two_approved_sources(self):
        sources = self.add_sources()
        for s in sources[:2]:
            self.memory.set_source_training_rights(s["id"], True)
        with self.assertRaisesRegex(ValueError, "at least three"):
            train_approved_knowledge(
                self.db, self.output, confirm_rights=True,
                steps=1, sequence=16, hidden=16)
        self.assertFalse(self.output.exists())

    @unittest.skipIf(torch is None, "dedicated CI installs real PyTorch CPU")
    def test_wrong_cuda_request_cannot_create_checkpoint(self):
        if torch.cuda.is_available():
            self.skipTest("GPU runner has real CUDA")
        with self.assertRaisesRegex(ValueError, "CUDA unavailable"):
            train_approved_knowledge(
                self.db, self.output, confirm_rights=True,
                device="cuda", sequence=16, hidden=16)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
