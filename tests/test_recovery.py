"""Transactional private SQLite memory recovery, real data and WAL regression."""
from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from neurogenesis.memory import ExperienceMemory
from neurogenesis.recovery import (
    backup_private_database, inspect_private_database,
    restore_to_new_database, main,
)
from neurogenesis.web_sense import WebObservation


class MemoryBackupTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.db = self.root / "live.sqlite3"
        self.backup = self.root / "backup.sqlite3"
        self.restored = self.root / "recovered.sqlite3"
        self.memory = ExperienceMemory(self.db)
        self.memory.remember("Bodziec prywatny — zastrzeżony", source="local")
        self.memory.teach("Jak działa urządzenie?", "Odpowiedź prywatna.")
        evidence = "Testowa obserwacja neuroplastyczności i połączeń."
        raw = evidence.encode("utf-8")
        self.memory.observe_web(WebObservation(
            url="https://example.org/private-synthetic",
            host="example.org", text=evidence,
            content_sha256=hashlib.sha256(raw).hexdigest(),
            retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
            bytes_read=len(raw)))
        before = self.memory.knowledge_sources()[0]
        self.memory.set_source_training_rights(before["id"], True)

    def test_complete_local_snapshot_and_non_destructive_recovery(self):
        source_events = self.memory.status()["observations"]
        prior_sha = hashlib.sha256(self.db.read_bytes()).hexdigest()
        report = backup_private_database(self.db, self.backup)
        self.assertEqual(report["integrity"], "ok")
        self.assertTrue(report["new_backup_created"])
        self.assertTrue(report["original_modified"] is False)
        self.assertEqual(report["source_versions"], 1)
        self.assertEqual(report["training_rights_events"], 1)
        self.assertEqual(report["observations"], source_events)
        self.assertEqual(report["teachings"], 1)
        self.assertFalse(report["network_used"])
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(), prior_sha)
        self.assertEqual(inspect_private_database(
            self.backup, expected_sha256=report["sha256"])["sha256"], report["sha256"])
        recovered = restore_to_new_database(
            self.backup, self.restored, confirmed=True)
        self.assertEqual(recovered["sha256"], report["sha256"])
        self.assertTrue(recovered["restored_to_new_path_only"])
        after = ExperienceMemory(self.restored)
        self.assertEqual(after.status()["observations"], source_events)
        self.assertEqual(after.status()["knowledge"]["documents"], 1)
        self.assertEqual(after.status()["taught_responses"], 1)
        self.assertEqual(after.taught_answer("Jak działa urządzenie?")["answer"],
                         "Odpowiedź prywatna.")
        self.assertEqual(after.knowledge_sources()[0]["rights_status"],
                         "operator-approved-local-training")
        self.assertEqual(after.brain().steps, self.memory.brain().steps)
        self.assertTrue(self.db.exists())

    def test_no_overwrite_even_if_target_preexists_or_source_equals_target(self):
        self.backup.write_bytes(b"existing bytes may never be replaced")
        with self.assertRaisesRegex(ValueError, "NEW"):
            backup_private_database(self.db, self.backup)
        self.assertEqual(self.backup.read_bytes(), b"existing bytes may never be replaced")
        with self.assertRaisesRegex(ValueError, "NEW"):
            backup_private_database(self.db, self.db)
        self.assertEqual(list(self.root.glob(".neurogenesis-backup-*.sqlite3")), [])

    def test_refuse_corrupt_copy_wrong_checksum_or_missing_permissions(self):
        good = backup_private_database(self.db, self.backup)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            inspect_private_database(self.backup, expected_sha256="0" * 64)
        with self.assertRaises(PermissionError):
            restore_to_new_database(self.backup, self.restored)
        self.assertFalse(self.restored.exists())
        bad = self.root / "corrupt.sqlite3"
        bad.write_bytes(b"not an sqlite database")
        with self.assertRaises((sqlite3.DatabaseError, ValueError)):
            inspect_private_database(bad)
        self.assertEqual(inspect_private_database(
            self.backup, expected_sha256=good["sha256"])["integrity"], "ok")

    def test_new_snapshot_contains_committed_wal_writes(self):
        # Keep a WAL reader open so SQLite must copy the logical snapshot,
        # not just bytes from the main .sqlite3 file.
        with sqlite3.connect(self.db) as writer:
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("PRAGMA wal_autocheckpoint=0")
            self.memory.remember("Nowy zapis po przejściu do WAL", source="local")
            expected = self.memory.status()["observations"]
            report = backup_private_database(self.db, self.backup)
            recovered = ExperienceMemory(self.backup)
            self.assertEqual(recovered.status()["observations"], expected)
            self.assertEqual(report["observations"], expected)
            self.assertTrue(recovered.recall("Nowy zapis po przejściu do WAL"))
        self.assertTrue(self.db.exists())

    def test_report_contains_no_private_data_and_cli_verification(self):
        digest = backup_private_database(self.db, self.backup)["sha256"]
        output = StringIO()
        with redirect_stdout(output):
            exitcode = main(["--verify", str(self.backup), "--expected-sha256", digest])
        self.assertEqual(exitcode, 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["integrity"], "ok")
        self.assertNotIn("Bodziec prywatny", output.getvalue())
        self.assertNotIn("https://", output.getvalue())
        self.assertNotIn(str(self.db), output.getvalue())
        self.assertNotIn(str(self.backup), output.getvalue())

    def test_symlink_is_rejected_without_touching_source(self):
        alias = self.root / "alias.sqlite3"
        try:
            alias.symlink_to(self.db)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable on this Windows filesystem")
        with self.assertRaises(ValueError):
            inspect_private_database(alias)


if __name__ == "__main__":
    unittest.main()
