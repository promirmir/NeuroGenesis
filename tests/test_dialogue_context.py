"""Offline, source-grounded contextual dialogue without pretending to reason.

Tests use local fictional web observations only. No Internet/model downloads,
no retention of raw private questions in SQLite and no neural inference claim.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit

from neurogenesis.command_service import CommandService
from neurogenesis.desktop import process_message
from neurogenesis.dialogue_context import expand_followup
from neurogenesis.memory import ExperienceMemory
from neurogenesis.web_sense import WebObservation


def observation(text: str, url: str = "https://docs.example.org/fenix") -> WebObservation:
    raw = text.encode("utf-8")
    return WebObservation(
        url=url, host=urlsplit(url).hostname or "",
        text=text, content_sha256=hashlib.sha256(raw).hexdigest(),
        bytes_read=len(raw),
        retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat())


class ContextCarryoverTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = Path(temp.name) / "private.sqlite3"
        self.service = CommandService(self.db)
        self.source = "https://docs.example.org/fenix"
        self.service.memory.observe_web(observation(
            "Raport Fenix opisuje temperaturę graniczną urządzenia. "
            "Raport Fenix zawiera wyniki pomiarów napięcia."))

    def test_short_followup_reuses_prior_grounded_topic_and_actual_source(self):
        first = self.service.ask("Co opisuje raport Fenix?")
        self.assertEqual(first["response_kind"], "source_evidence")
        self.assertFalse(first["context_used"])
        follow = self.service.ask("A co z temperaturę graniczną?")
        self.assertEqual(follow["response_kind"], "source_evidence")
        self.assertTrue(follow["context_used"])
        self.assertIn("temperaturę graniczną", follow["reply"])
        self.assertEqual(follow["sources"][0]["url"], self.source)
        self.assertEqual(self.service.snapshot().observations, 3)
        self.assertEqual(self.service.memory.status()["records_with_raw_text"], 0)
        self.assertTrue(ExperienceMemory(self.db).answer_from_knowledge(
            "Co opisuje raport Fenix?") is not None)

    def test_different_host_and_missing_focus_do_not_reuse_old_topic(self):
        self.service.memory.observe_web(observation(
            "Raport Omega opisuje chłodzenie gazu kriogenicznego.",
            "https://other.example.net/omega"))
        self.assertEqual(self.service.ask("Co opisuje raport Fenix?")["response_kind"],
                         "source_evidence")
        unrelated = self.service.ask("A co z chłodzenie kriogenicznego?")
        self.assertEqual(unrelated["response_kind"], "sensory_acknowledgement")
        self.assertFalse(unrelated["context_used"])
        self.assertEqual(unrelated["sources"], [])
        missing = self.service.ask("A gdzie?")
        self.assertFalse(missing["context_used"])

    def test_context_is_volatile_and_can_be_cleared_without_deleting_sqlite(self):
        self.service.ask("Co opisuje raport Fenix?")
        self.service.clear_conversation_context()
        standalone = self.service.ask("A gdzie?")
        self.assertFalse(standalone["context_used"])
        reopened = CommandService(self.db)
        after = reopened.ask("A co z temperaturę graniczną?")
        # Standalone lexical matching is still possible, but NO prior session
        # subject/source is secretly reused.
        self.assertFalse(after["context_used"])
        self.assertEqual(reopened.memory.status()["knowledge"]["documents"], 1)
        self.assertEqual(reopened.memory.status()["records_with_raw_text"], 0)

    def test_manual_teaching_remains_absolutely_authoritative(self):
        question = "A co z temperaturę graniczną?"
        self.service.memory.teach(question, "Własna prywatna odpowiedź.")
        self.service.ask("Co opisuje raport Fenix?")
        answer = self.service.ask(question)
        self.assertEqual(answer["response_kind"], "explicit_local_teaching")
        self.assertEqual(answer["reply"], "Własna prywatna odpowiedź.")
        self.assertFalse(answer["context_used"])
        self.assertEqual(answer["sources"], [])

    def test_updated_source_supersedes_previous_followup_candidate(self):
        self.service.ask("Co opisuje raport Fenix?")
        self.service.memory.observe_web(observation(
            "Raport Fenix opisuje nowe zasady przechowywania urządzenia.",
            self.source))
        answer = self.service.ask("A co z temperaturę graniczną?")
        self.assertEqual(answer["response_kind"], "sensory_acknowledgement")
        self.assertFalse(answer["context_used"])
        self.assertNotIn(self.source, answer["reply"])
        self.assertEqual(self.service.memory.knowledge_sources()[0]["version"], 2)

    def test_original_tk_direct_path_does_not_invent_session_context(self):
        mem = ExperienceMemory(self.db)
        result = process_message(mem, "A gdzie?")
        self.assertEqual(result["response_kind"], "sensory_acknowledgement")
        self.assertFalse(result["context_used"])
        count = mem.status()["observations"]
        with self.assertRaises(ValueError):
            process_message(mem, "A gdzie?", evidence_source_url=self.source)
        self.assertEqual(mem.status()["observations"], count)

    def test_context_expansion_requires_explicit_question_and_novel_content(self):
        prev = "Co opisuje raport Fenix?"
        self.assertIsNone(expand_followup("A gdzie?", prev))
        self.assertIsNone(expand_followup("Co z temperaturą?", prev))
        self.assertIsNone(expand_followup("A czy to coś zmienia", prev))
        result = expand_followup("A co z temperaturę graniczną?", prev)
        self.assertIsNotNone(result)
        self.assertEqual(result.mandatory_focus_terms,
                         ("temperaturę", "graniczną"))
        self.assertIn("fenix", result.query)


if __name__ == "__main__":
    unittest.main()
