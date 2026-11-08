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

from PySide6.QtWidgets import QApplication, QScrollArea
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

    def test_inference_lab_requires_explicit_trusted_file_and_is_offline(self):
        self.window.navigate(4)
        self.assertFalse(self.window.trust_checkpoint.isChecked())
        self.assertEqual(self.window.inference_bytes.value(), 16)
        self.assertFalse(self.window.training_resume.isChecked())
        self.assertFalse(self.service.snapshot().inference_running)
        self.assertFalse(self.service.network_enabled)
        self.assertIn("predykcję", self.window.inference_start.text().lower())
        self.assertIsNotNone(self.window.pages.widget(4).findChild(QScrollArea))

    def test_contextual_followup_visible_and_user_can_clear_topic(self):
        text = "Raport Fenix opisuje temperaturę graniczną urządzenia."
        self.service.memory.observe_web(WebObservation(
            url="https://example.org/fenix", host="example.org", text=text,
            content_sha256=hashlib.sha256(text.encode()).hexdigest(),
            retrieved_utc=datetime.now(timezone.utc).isoformat(),
            bytes_read=len(text.encode())))
        self.window.navigate(1)
        self.window.chat_input.setPlainText("Co opisuje raport Fenix?")
        self.window.send_message()
        self.window.chat_input.setPlainText("A co z temperaturę graniczną?")
        self.window.send_message()
        self.assertIn("kontekstu sesji", self.window.chat_status.text())
        self.assertIn("source_evidence", self.window.chat_history.toPlainText())
        before = self.service.memory.status()["knowledge"]["documents"]
        self.window.clear_context()
        self.assertIn("Wyczyszczono", self.window.chat_status.text())
        self.assertEqual(self.service.memory.status()["knowledge"]["documents"], before)
        self.assertEqual(self.service.memory.status()["records_with_raw_text"], 0)

    def test_true_live_neural_fabric_responds_only_to_actual_persisted_steps(self):
        self.window.navigate(3)
        original = self.window.brain_plot._frame
        self.assertIsNotNone(original)
        self.assertEqual(original.step, 0)
        self.assertEqual(original.neurons, self.service.memory.brain().stats()["neurons"])
        self.assertEqual(original.synapses, self.service.memory.brain().stats()["synapses"])
        self.assertFalse(self.window.brain_plot._pulse_timer.isActive())
        self.window.refresh_neural_view()
        self.assertEqual(original, self.window.brain_plot._frame)
        result = self.service.ask("Bodziec dla rzeczywistej sieci neuronowej")
        self.window.refresh_neural_view()
        observed = self.window.brain_plot._frame
        self.assertEqual(observed.step, result["brain_step"])
        self.assertEqual(observed.neurons, result["neurons"])
        self.assertEqual(observed.synapses, result["synapses"])
        self.assertGreater(observed.step, original.step)
        self.assertEqual(observed.last_spikes, sum(self.service.memory.brain().spikes))
        self.assertTrue(self.window.brain_plot._pulse_timer.isActive())
        unchanged = self.service.memory.brain().to_dict()
        self.window.refresh_neural_view()
        self.assertEqual(observed, self.window.brain_plot._frame)
        self.assertEqual(self.service.memory.brain().to_dict(), unchanged)
        self.assertIn("graf", self.window.brain_metrics.text())
        self.assertFalse(self.service.network_enabled)

    def test_memory_backup_panel_runs_real_offline_verified_service(self):
        self.window.navigate(6)
        self.assertTrue(self.window.backup_button.isEnabled())
        self.assertTrue(self.window.verify_button.isEnabled())
        output = self.db.parent / "qt-backup.sqlite3"
        self.service.start_memory_backup(output)
        self.service._memory_maintenance.join(timeout=30)
        self.assertFalse(self.service._memory_maintenance.is_alive())
        self.window.poll_study_events()
        self.assertTrue(output.exists())
        self.assertIn("SHA-256", self.window.backup_status.text())
        self.service.start_memory_verification(output)
        self.service._memory_maintenance.join(timeout=30)
        self.assertFalse(self.service._memory_maintenance.is_alive())
        self.window.poll_study_events()
        self.assertIn("Integralność kopii zweryfikowana",
                      self.window.backup_status.text())
        self.assertFalse(self.service.network_enabled)
        self.assertTrue(self.window.backup_button.isEnabled())

    def test_consent_updates_real_service_and_stops_on_close(self):
        self.window.navigate(6)
        self.window.allow_https.setChecked(True)
        self.assertTrue(self.service.network_enabled)
        self.window.close()
        self.assertFalse(self.service.network_enabled)


if __name__ == "__main__":
    unittest.main()
