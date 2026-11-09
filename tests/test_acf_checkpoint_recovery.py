"""Crash-safety tests for genuine persisted ACF neural checkpoints.

Fixtures include real, committed SQLite observations. Results demonstrate
checkpoint replay, not recovery of erased experiences or AGI.
"""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from neurogenesis.acf import AdaptiveCognitiveFabric
from neurogenesis.acf_memory import FabricMemoryObserver
from neurogenesis.acf_semantic_memory import SemanticFabricStore
from neurogenesis.acf_semantics import VERSION
from neurogenesis.memory import ExperienceMemory


class VerifiedRecoveryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.store = SemanticFabricStore(self.root)

    def tagged(self, i: int) -> dict:
        axes = [float((i + j) % 3 == 0) for j in range(8)]
        return {
            "axes": axes, "version": VERSION,
            "model": "Qwen3-1.7B-Q4_K_M",
            "inference": "actual_local_gguf_semantic_classification",
            "cloud_api_used": False, "raw_text_persisted": False,
        }

    def _seed(self):
        for i in range(3):
            self.store.learn(self.tagged(i))
        checkpoint = self.store.state_path
        previous = self.store._observer.previous_path
        self.assertTrue(previous.is_file())
        self.assertEqual(AdaptiveCognitiveFabric.load(previous).events, 2)
        self.assertEqual(AdaptiveCognitiveFabric.load(checkpoint).events, 3)
        return checkpoint, previous

    def test_corrupted_snapshot_recovers_previous_then_exact_replay(self):
        checkpoint, prev = self._seed()
        baseline = AdaptiveCognitiveFabric.load(checkpoint).to_dict()
        private_question = "very private do not save this anywhere 793463"
        checkpoint.write_text("{bad JSON" + private_question, encoding="utf-8")
        restarted = SemanticFabricStore(self.root)
        result = restarted.sync()
        self.assertTrue(result["checkpoint_recovered"])
        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["self_model"]["observations"], 3)
        self.assertEqual(AdaptiveCognitiveFabric.load(checkpoint).to_dict(), baseline)
        quarantine = restarted._observer.quarantine_path
        self.assertTrue(quarantine.is_file())
        self.assertEqual(quarantine.read_text(encoding="utf-8"),
                         "{bad JSON" + private_question)
        self.assertEqual(
            restarted.sync()["checkpoint_recovered"], False)
        self.assertEqual(restarted.sync()["processed"], 0)
        # No private phrase can be copied into the *valid* state or ledger.
        self.assertNotIn(private_question.encode(),
                         checkpoint.read_bytes() + self.store.path.read_bytes())
        self.assertTrue(prev.is_file())

    def test_corrupt_without_backup_fails_closed_without_overwrite(self):
        self.store.learn(self.tagged(0))
        self.assertFalse(self.store._observer.previous_path.exists())
        self.store.state_path.write_text("{broken", encoding="utf-8")
        before = self.store.state_path.read_bytes()
        with self.assertRaises(ValueError):
            SemanticFabricStore(self.root).sync()
        self.assertEqual(self.store.state_path.read_bytes(), before)
        self.assertFalse(self.store._observer.quarantine_path.exists())

    def test_reject_replay_from_prior_if_ledger_was_truncated(self):
        checkpoint, prev = self._seed()
        checkpoint.write_text("{corrupt checkpoint}", encoding="utf-8")
        before = checkpoint.read_bytes()
        with closing(sqlite3.connect(self.store.path)) as con:
            with con:
                con.execute("DELETE FROM observations WHERE id=1")
        with self.assertRaisesRegex(ValueError, "cursor disagrees"):
            self.store.sync()
        self.assertEqual(checkpoint.read_bytes(), before)
        self.assertFalse(self.store._observer.quarantine_path.exists())
        self.assertTrue(prev.is_file())

    def test_reject_untrusted_semantic_tagger_during_replay(self):
        checkpoint, _ = self._seed()
        checkpoint.write_text("{malformed}", encoding="utf-8")
        with closing(sqlite3.connect(self.store.path)) as con:
            with con:
                con.execute("UPDATE observations SET tagger='unknown' WHERE id=2")
        with self.assertRaisesRegex(ValueError, "provenance"):
            self.store.sync()
        self.assertEqual(checkpoint.read_text(encoding="utf-8"),
                         "{malformed}")

    def test_quarantine_never_overwritten_by_second_failure(self):
        checkpoint, _ = self._seed()
        checkpoint.write_text("first corruption", encoding="utf-8")
        self.store.sync()
        quarantined = self.store._observer.quarantine_path
        self.assertEqual(quarantined.read_text(encoding="utf-8"),
                         "first corruption")
        checkpoint.write_text("second corruption", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "quarantine already exists"):
            self.store.sync()
        self.assertEqual(quarantined.read_text(encoding="utf-8"),
                         "first corruption")
        self.assertEqual(checkpoint.read_text(encoding="utf-8"),
                         "second corruption")

    def test_clean_snapshot_without_new_observations_never_overwrites_backup(self):
        checkpoint, prev = self._seed()
        old_previous = prev.read_bytes()
        current = checkpoint.read_bytes()
        info = self.store.sync()
        self.assertEqual(info["processed"], 0)
        self.assertFalse(info["checkpoint_recovered"])
        self.assertEqual(prev.read_bytes(), old_previous)
        self.assertEqual(checkpoint.read_bytes(), current)

    def test_optimistic_conflict_guard_prevents_stale_neural_write(self):
        checkpoint, prev = self._seed()
        self.store.learn(self.tagged(3))
        # The new observation is already included. Add an additional valid
        # committed ledger row without calling the ACF optimizer.
        with closing(sqlite3.connect(self.store.path)) as con:
            with con:
                con.execute(
                    "INSERT INTO observations(features,tagger,recorded_utc)"
                    " VALUES(?,?,?)",
                    (json.dumps([0.0] * 8), VERSION, "synthetic-fixture"))
        previous_bytes = prev.read_bytes()
        state_bytes = checkpoint.read_bytes()
        original = self.store._observer._hash_primary
        hits = [0]
        def conflict():
            hits[0] += 1
            return original() if hits[0] == 1 else "externally-changed"
        with patch.object(self.store._observer, "_hash_primary",
                          side_effect=conflict):
            with self.assertRaisesRegex(RuntimeError, "concurrently"):
                self.store.sync()
        self.assertEqual(checkpoint.read_bytes(), state_bytes)
        self.assertEqual(prev.read_bytes(), previous_bytes)


class SensoryRecoveryTests(unittest.TestCase):
    def test_original_hashed_sensory_memory_also_replays_and_does_not_change_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            db = base / "experience.sqlite3"
            state = base / "sensory.acf.json"
            memory = ExperienceMemory(db)
            observer = FabricMemoryObserver(db, state)
            for i in range(3):
                memory.remember(f"sprężyna indukcyjna nr {i}", store_text=False)
                observer.poll()
            before_model = AdaptiveCognitiveFabric.load(state).to_dict()
            before_db = db.read_bytes()
            state.write_text("~bad-state~", encoding="utf-8")
            recovered = FabricMemoryObserver(db, state).poll()
            self.assertEqual(recovered["processed"], 1)
            self.assertTrue(recovered["checkpoint_recovered"])
            self.assertEqual(AdaptiveCognitiveFabric.load(state).to_dict(), before_model)
            self.assertEqual(db.read_bytes(), before_db)


if __name__ == "__main__":
    unittest.main()
