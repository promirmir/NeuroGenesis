"""Headless contract and actual brain/SQLite integration tests."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from neurogenesis.desktop import default_data_dir, default_db_path, process_message, self_test
from neurogenesis.memory import ExperienceMemory


class DesktopContractTests(unittest.TestCase):
    def test_self_test_reuses_real_brain_sqlite(self):
        self.assertEqual(self_test(), 0)

    def test_local_persistent_data_path(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": str(Path("C:/ProgramData/TempLocal"))}):
            with patch("neurogenesis.desktop._is_windows", return_value=True):
                self.assertEqual(default_db_path().name, "experiences.sqlite3")
                self.assertEqual(default_data_dir().name, "NeuroGenesis")

    def test_real_sqlite_private_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            mem = ExperienceMemory(Path(tmp) / "private.sqlite3")
            result = process_message(mem, "Pierwsza prywatna obserwacja")
            reopened = ExperienceMemory(Path(tmp) / "private.sqlite3")
            self.assertEqual(reopened.status()["observations"], 1)
            self.assertEqual(reopened.status()["records_with_raw_text"], 0)
            self.assertEqual(reopened.status()["brain"]["steps"], 4)
            self.assertTrue(reopened.recall("Pierwsza prywatna obserwacja")[0]["exact_hash_match"])
            self.assertEqual(result["brain_step"], 4)

    def test_explicit_text_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            mem = ExperienceMemory(Path(tmp) / "private.sqlite3")
            process_message(mem, "Zgoda na zapis", store_text=True)
            self.assertEqual(mem.status()["records_with_raw_text"], 1)

    def test_input_validation_does_not_mutate_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            mem = ExperienceMemory(Path(tmp) / "private.sqlite3")
            for value in ("", " \t", None, 10):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    process_message(mem, value)
            with self.assertRaises(ValueError):
                process_message(mem, "message", store_text="yes")
            self.assertEqual(mem.status()["observations"], 0)

    def test_fail_closed_on_corrupted_brain(self):
        with tempfile.TemporaryDirectory() as tmp:
            import sqlite3
            db = Path(tmp) / "private.sqlite3"
            mem = ExperienceMemory(db)
            mem.remember("valid")
            with sqlite3.connect(db) as conn:
                conn.execute("UPDATE neural_state SET brain_json='invalid json' WHERE id=1")
            with self.assertRaises(ValueError):
                process_message(mem, "should not overwrite")
            with sqlite3.connect(db) as conn:
                self.assertEqual(conn.execute("SELECT brain_json FROM neural_state WHERE id=1").fetchone()[0], "invalid json")

    def test_subprocess_without_gui(self):
        entry = Path(__file__).resolve().parents[1] / "desktop_launcher.py"
        proc = subprocess.run([sys.executable, str(entry), "--self-test"],
                              cwd=entry.parent, capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
