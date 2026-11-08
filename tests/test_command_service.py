"""Real SQLite Command Center service tests, all offline and Qt-independent."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import tempfile
import threading
import unittest

from neurogenesis.command_service import CommandService
from neurogenesis.web_sense import WebObservation


def page(text="Plastyczność synaptyczna reguluje połączenia neuronalne."):
    return WebObservation(
        url="https://example.org/neuro",
        host="example.org", text=text,
        content_sha256=hashlib.sha256(text.encode()).hexdigest(),
        retrieved_utc=datetime.now(timezone.utc).isoformat(),
        bytes_read=len(text.encode()))


@dataclass(frozen=True)
class Progress:
    attempted: int = 1
    accepted: int = 1
    errors: int = 0
    stopped: bool = False
    discovered: int = 1
    domains: int = 1


class FakeStudy:
    def __init__(self, topic, observe, *, max_pages):
        self.topic = topic
        self.max_pages = max_pages
        self.observe = observe
        self.completed = threading.Event()
        self.stopped = threading.Event()
        self.result = None

    def stop(self):
        self.stopped.set()

    def progress(self):
        return Progress(stopped=self.stopped.is_set())

    def run(self, *, consent=False, on_event=None):
        if not consent:
            raise PermissionError("no consent")
        try:
            self.result = self.observe(page())
            if on_event:
                on_event("saved", "https://example.org/neuro")
        finally:
            self.completed.set()
        return self.progress()


class WaitingStudy(FakeStudy):
    waiting = threading.Event()
    proceed = threading.Event()

    def run(self, *, consent=False, on_event=None):
        self.waiting.set()
        if not self.proceed.wait(2):
            self.completed.set()
            raise TimeoutError("fake study timed out")
        return super().run(consent=consent, on_event=on_event)


class CommandServiceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = Path(directory.name) / "private.sqlite3"
        self.service = CommandService(self.db, study_factory=FakeStudy)

    def test_reopens_legacy_brain_and_real_snapshot(self):
        before = self.service.snapshot()
        self.assertFalse(before.network_enabled)
        self.assertEqual(before.documents, 0)
        self.service.memory.observe_web(page())
        after = CommandService(self.db).snapshot()
        self.assertEqual(after.documents, 1)
        self.assertGreater(after.brain_steps, before.brain_steps)
        self.assertGreater(after.passages, 0)
        self.assertEqual(after.database, str(self.db))

    def test_service_answers_with_citation_and_reads_real_passages(self):
        self.service.memory.observe_web(page())
        source = self.service.sources(20)[0]
        extracts = self.service.source_passages(source["id"])
        self.assertIn("Plastyczność synaptyczna", extracts[0]["text"])
        reply = self.service.ask("Co reguluje plastyczność synaptyczna?")
        self.assertEqual(reply["response_kind"], "source_evidence")
        self.assertIn("https://example.org/neuro", reply["reply"])
        self.assertEqual(self.service.neural_traces(), tuple(self.service.memory.brain().traces))

    def test_no_automatic_network_traffic_and_permission_required(self):
        with self.assertRaises(PermissionError):
            self.service.start_study("synapsy", 1)
        self.assertFalse(self.service.snapshot().network_enabled)
        self.assertFalse(self.service.snapshot().research_running)
        for invalid in (1, "true", None):
            with self.assertRaises(ValueError):
                self.service.set_network_consent(invalid)

    def test_explicit_study_uses_existing_brain_sqlite_not_a_second_fake_store(self):
        self.service.set_network_consent(True)
        self.service.start_study("synapsy", 1)
        study = self.service._study
        self.assertTrue(study.completed.wait(3), "mock worker did not finish")
        self.assertEqual(self.service.snapshot().documents, 1)
        self.assertEqual(self.service.snapshot().research_accepted, 1)
        events = self.service.poll_events()
        self.assertTrue(any(kind == "saved" for kind, _ in events))
        self.assertEqual(self.service.sources()[0]["url"], "https://example.org/neuro")
        self.service.set_network_consent(False)
        self.assertFalse(self.service.network_enabled)

    def test_revoking_consent_during_a_pending_study_prevents_persistence(self):
        WaitingStudy.waiting = threading.Event()
        WaitingStudy.proceed = threading.Event()
        service = CommandService(self.db, study_factory=WaitingStudy)
        service.set_network_consent(True)
        service.start_study("synapsy", 1)
        self.assertTrue(WaitingStudy.waiting.wait(3))
        service.set_network_consent(False)
        WaitingStudy.proceed.set()
        self.assertTrue(service._study.completed.wait(3))
        self.assertEqual(service.snapshot().documents, 0)
        self.assertEqual(service.snapshot().observations, 0)
        self.assertTrue(any(kind == "fatal" for kind, _ in service.poll_events()))

    def test_old_manual_teachings_remain_authoritative(self):
        self.service.teach("Co to jest?", "Prywatna odpowiedź.")
        self.assertEqual(self.service.ask("Co to jest?")["response_kind"],
                         "explicit_local_teaching")
        self.assertEqual(CommandService(self.db).ask("Co to jest?")["reply"],
                         "Prywatna odpowiedź.")

    def test_source_id_validation_and_empty_result(self):
        with self.assertRaises(ValueError):
            self.service.source_passages(0)
        self.assertEqual(self.service.source_passages(777), [])
        with self.assertRaises(ValueError):
            self.service.poll_events(limit=0)


if __name__ == "__main__":
    unittest.main()
