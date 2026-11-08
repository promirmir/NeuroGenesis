"""Benchmark current source quotes against real BM25 on same local SQLite data."""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from neurogenesis.memory import ExperienceMemory
from neurogenesis.qa_baselines import (
    bm25_excerpt, compare_bm25, load_latest_passages,
)
from neurogenesis.web_sense import WebObservation


def fake_observation(url: str, text: str) -> WebObservation:
    raw = text.encode("utf-8")
    return WebObservation(
        url=url, host=url.split("/")[2], text=text,
        content_sha256=hashlib.sha256(raw).hexdigest(),
        retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
        bytes_read=len(raw))


class Bm25BenchmarkTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.db = self.root / "memory.sqlite3"
        self.audit = self.root / "prospective.jsonl"
        self.memory = ExperienceMemory(self.db)
        self.memory.observe_web(fake_observation(
            "https://docs.example.org/solaris",
            "Stary dokument SolarisX opisuje wyłącznie proces chemiczny."))
        self.memory.observe_web(fake_observation(
            "https://docs.example.org/solaris",
            "Nowy Kod SolarisX oznacza kryształowy czujnik w laboratorium."))
        self.memory.observe_web(fake_observation(
            "https://docs.example.net/nebula",
            "Projekt NebulaY opisuje pomiar temperatury na stacji badawczej."))
        self.cases = [
            {"question": "Co oznacza Kod SolarisX?", "answerable": True,
             "expected_source_url": "https://docs.example.org/solaris",
             "required_quote": "Nowy Kod SolarisX oznacza"},
            {"question": "Co opisuje projekt NebulaY?", "answerable": True,
             "expected_source_url": "https://docs.example.net/nebula",
             "required_quote": "Projekt NebulaY opisuje"},
            {"question": "Dlaczego Kod SolarisX niszczy rośliny?", "answerable": False},
            {"question": "Czy stacja NebulaY jest na Marsie?", "answerable": False},
            {"question": "Ile wynosi stopień mrozu w nieistniejącym laboratorium?",
             "answerable": False},
        ]
        self.audit.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in self.cases) + "\n",
            encoding="utf-8")

    def test_real_latest_revision_only_and_deterministic_bm25(self):
        with closing(sqlite3.connect(self.db)) as con:
            docs = load_latest_passages(con)
        self.assertEqual(len(docs), 2)
        self.assertTrue(all("Stary dokument" not in t for t, _, _ in docs))
        hit = bm25_excerpt(docs, "Co oznacza Kod SolarisX?")
        self.assertIsNotNone(hit)
        self.assertIn("Nowy Kod SolarisX", hit[0])
        self.assertEqual(hit[1], "https://docs.example.org/solaris")
        self.assertEqual(bm25_excerpt(docs, "Co oznacza Kod SolarisX?"), hit)
        self.assertIsNone(bm25_excerpt(docs, "Niewiadoma glosurf astrotyp"))

    def test_readonly_full_comparison_reports_errors_without_private_text(self):
        prior = hashlib.sha256(self.db.read_bytes()).hexdigest()
        report = compare_bm25(
            self.db, self.audit, confirm_rights=True, confirm_untouched=True)
        self.assertEqual(report["cases"], 5)
        self.assertEqual(report["supported_cases"], 2)
        self.assertEqual(report["unsupported_cases"], 3)
        self.assertEqual(report["corpus_passages"], 2)
        self.assertEqual(report["bm25_non_neural_control"]["correct_literal_citations"], 2)
        self.assertEqual(report["current_source_retrieval"]["correct_literal_citations"], 2)
        self.assertGreater(report["bm25_non_neural_control"]["unsupported_false_citation_rate"], 0)
        self.assertFalse(report["baseline_is_deployed"])
        self.assertFalse(report["current_algorithm_modified"])
        self.assertFalse(report["factual_truth_verified"])
        self.assertTrue(report["no_checkpoint_or_sqlite_mutation"])
        self.assertEqual(prior, hashlib.sha256(self.db.read_bytes()).hexdigest())
        printable = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("SolarisX", printable)
        self.assertNotIn("https://", printable)
        print("BM25_QA_SYNTHETIC_COMPARISON=" + json.dumps({
            "current": report["current_source_retrieval"],
            "bm25": report["bm25_non_neural_control"],
            "difference": report["strict_accuracy_difference_current_minus_bm25"],
        }, sort_keys=True), flush=True)

    def test_no_permission_or_missing_files_fail_before_output(self):
        with self.assertRaises(PermissionError):
            compare_bm25(self.db, self.audit)
        with self.assertRaises(ValueError):
            compare_bm25(self.root / "absent.sqlite3", self.audit,
                         confirm_rights=True, confirm_untouched=True)
        self.assertFalse((self.root / "absent.sqlite3").exists())
        self.assertIsNone(bm25_excerpt([], " "))
        self.assertIsNone(bm25_excerpt([], "Co to jest SolarisX?"))


if __name__ == "__main__":
    unittest.main()
