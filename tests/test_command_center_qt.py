"""Real optional Qt widget smoke tests; CI installs PySide6-Essentials for this suite.

The standard dependency-free tests intentionally skip Qt when not installed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if importlib.util.find_spec("PySide6") is None:
    raise unittest.SkipTest("optional Qt is not installed; dedicated Qt CI installs it")

from PySide6.QtWidgets import QApplication
from neurogenesis.command_center import CommandCenter, PANELS
from neurogenesis.command_service import CommandService
from neurogenesis.web_sense import WebObservation


class QtCommandCenterSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db = Path(folder.name) / "memory.sqlite3"
        self.service = CommandService(self.db)
        self.window = CommandCenter(self.service)
        self.addCleanup(self.window.close)

    def test_sidebar_contains_real_modules_and_network_off(self):
        self.assertEqual(self.window.pages.count(), len(PANELS))
        self.assertEqual(self.window.network_indicator.text(), "HTTPS WYŁĄCZONY")
        self.assertFalse(self.service.network_enabled)
        self.assertIn("Dokumenty: 0", self.window.overview_metrics.text())
        self.window.navigate(4)
        self.window.refresh()
        self.assertIn("NIEURUCHOMIONY", self.window.training_status.text())

    def test_chat_uses_sqlite_source_not_hardcoded_gui_response(self):
        text = "Plastyczność synaptyczna umożliwia zmianę siły połączeń neuronów."
        self.service.memory.observe_web(WebObservation(
            url="https://example.org/evidence", host="example.org", text=text,
            content_sha256=hashlib.sha256(text.encode()).hexdigest(),
            retrieved_utc=datetime.now(timezone.utc).isoformat(),
            bytes_read=len(text.encode())))
        self.window.navigate(1)
        self.window.chat_input.setPlainText("Czym jest plastyczność synaptyczna?")
        self.window.send_message()
        transcript = self.window.chat_history.toPlainText()
        self.assertIn("source_evidence", transcript)
        self.assertIn("https://example.org/evidence", transcript)
        self.assertEqual(self.window.chat_input.toPlainText(), "")
        self.window.navigate(5)
        self.window.refresh_sources()
        self.assertEqual(self.window.sources_table.rowCount(), 1)
        self.window.sources_table.selectRow(0)
        self.window.show_selected_source()
        self.assertIn("połączeń neuronów", self.window.source_preview.toPlainText())

    def test_consent_updates_real_service_and_stops_on_close(self):
        self.window.navigate(6)
        self.window.allow_https.setChecked(True)
        self.assertTrue(self.service.network_enabled)
        self.window.close()
        self.assertFalse(self.service.network_enabled)


if __name__ == "__main__":
    unittest.main()
