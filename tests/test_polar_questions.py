"""Strict conservative evidence rule for explicit Polish yes/no claims.

All examples fictional, source passages untrusted. Not a proof of factual
truth or semantic entailment: improved abstention deliberately lowers recall.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit

from neurogenesis.desktop import process_message
from neurogenesis.memory import ExperienceMemory
from neurogenesis.web_sense import WebObservation


def page(url: str, text: str) -> WebObservation:
    raw = text.encode("utf-8")
    return WebObservation(
        url=url, host=urlsplit(url).hostname or "", text=text,
        content_sha256=hashlib.sha256(raw).hexdigest(),
        bytes_read=len(raw),
        retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat())


class ConservativePolarEvidenceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db = Path(folder.name) / "local.sqlite3"
        self.memory = ExperienceMemory(self.db)
        self.url = "https://docs.example.org/nimbus"
        self.memory.observe_web(page(
            self.url, "Urządzenie Nimbus posiada filtr HEPA do oczyszczania powietrza."))

    def test_explicit_yes_no_requires_all_content_words_in_one_passage(self):
        supported = process_message(
            self.memory, "Czy urządzenie Nimbus posiada filtr HEPA?")
        self.assertEqual(supported["response_kind"], "source_evidence")
        self.assertEqual(supported["sources"][0]["url"], self.url)
        self.assertTrue(supported["evidence_review"]["polar_claim_lexical_coverage_required"])
        unsupported = process_message(
            self.memory, "Czy urządzenie Nimbus posiada filtr węglowy?")
        self.assertEqual(unsupported["response_kind"], "sensory_acknowledgement")
        self.assertEqual(unsupported["sources"], [])
        self.assertIsNone(unsupported["evidence_review"])

    def test_negated_yes_no_cannot_be_inferred_from_positive_excerpt(self):
        question = "Czy urządzenie Nimbus nie posiada filtr HEPA?"
        answer = process_message(self.memory, question)
        self.assertEqual(answer["response_kind"], "sensory_acknowledgement")
        self.assertEqual(answer["sources"], [])
        self.assertEqual(ExperienceMemory(self.db).status()["records_with_raw_text"], 0)

    def test_same_claim_from_negative_source_is_only_verbatim_not_proven(self):
        neg_url = "https://other.example.net/nimbus"
        self.memory.observe_web(page(
            neg_url, "Urządzenie Nimbus nie posiada filtr HEPA do oczyszczania powietrza."))
        answer = process_message(self.memory, "Czy urządzenie Nimbus nie posiada filtr HEPA?")
        self.assertEqual(answer["response_kind"], "source_evidence")
        self.assertEqual(answer["sources"][0]["url"], neg_url)
        self.assertNotIn(self.url, [s["url"] for s in answer["sources"]])
        self.assertIn("nie posiada", answer["reply"])
        self.assertIn("niezweryfikowany", answer["reply"])

    def test_nonpolar_lexical_retrieval_remains_compatible(self):
        response = process_message(self.memory, "Jak opisano urządzenie Nimbus?")
        self.assertEqual(response["response_kind"], "source_evidence")
        self.assertFalse(response["evidence_review"]["polar_claim_lexical_coverage_required"])

    def test_taught_answers_remain_first_and_never_claim_citation(self):
        question = "Czy urządzenie Nimbus posiada filtr węglowy?"
        self.memory.teach(question, "Operator: to prywatna odpowiedź.")
        answer = process_message(self.memory, question)
        self.assertEqual(answer["response_kind"], "explicit_local_teaching")
        self.assertEqual(answer["reply"], "Operator: to prywatna odpowiedź.")
        self.assertEqual(answer["sources"], [])


if __name__ == "__main__":
    unittest.main()
