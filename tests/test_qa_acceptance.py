"""Offline and real-SQLite prospective QA gate tests; fictional sources only.

Tests do not claim independent factual QA or an actually untouched corpus:
the synthetic examples are development fixtures visible in this repository.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from neurogenesis.memory import ExperienceMemory
from neurogenesis.qa_acceptance import (
    decide_qa_gate, run_prospective_gate, wilson_interval,
)
from neurogenesis.web_sense import WebObservation


class BinomialQualityTests(unittest.TestCase):
    def test_wilson_zero_failure_does_not_imply_zero_uncertainty(self):
        lo, hi = wilson_interval(0, 60)
        self.assertEqual(lo, 0)
        self.assertGreater(hi, .05)
        self.assertLess(hi, .07)
        lo, hi = wilson_interval(0, 100)
        self.assertLess(hi, .05)
        self.assertEqual(wilson_interval(100, 100)[1], 1)

    def test_quality_gate_rejects_tiny_tests_and_abstain_all(self):
        tiny = decide_qa_gate(
            supported_total=3, supported_exact=3,
            unsupported_total=3, unsupported_abstained=3)
        self.assertFalse(tiny["sufficient_class_sample"])
        self.assertFalse(tiny["passes_numeric_prospective_gate"])
        trivial = decide_qa_gate(
            supported_total=40, supported_exact=0,
            unsupported_total=100, unsupported_abstained=100)
        self.assertEqual(trivial["gain_vs_abstain_all"], 0)
        self.assertFalse(trivial["passes_numeric_prospective_gate"])

    def test_sufficient_precise_citations_pass_only_numeric_gate(self):
        result = decide_qa_gate(
            supported_total=40, supported_exact=40,
            unsupported_total=100, unsupported_abstained=100)
        self.assertTrue(result["passes_numeric_prospective_gate"])
        self.assertGreater(result["gain_vs_abstain_all"], .1)
        self.assertFalse(result["ready_for_semantic_chat"])
        self.assertFalse(result["automatically_promoted"])
        self.assertFalse(result["independently_fact_checked"])

    def test_moderate_false_citations_fail_even_if_high_accuracy(self):
        failure = decide_qa_gate(
            supported_total=40, supported_exact=40,
            unsupported_total=100, unsupported_abstained=94)
        self.assertGreater(failure["unsupported_false_citation_wilson95_upper"], .05)
        self.assertFalse(failure["passes_numeric_prospective_gate"])

    def test_invalid_statistics_refused(self):
        for counts in [
            dict(supported_total=0, supported_exact=0, unsupported_total=100, unsupported_abstained=100),
            dict(supported_total=40, supported_exact=41, unsupported_total=100, unsupported_abstained=100),
            dict(supported_total=40, supported_exact=40, unsupported_total=100, unsupported_abstained=101),
            dict(supported_total=True, supported_exact=1, unsupported_total=100, unsupported_abstained=100),
        ]:
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                decide_qa_gate(**counts)
        with self.assertRaises(ValueError):
            wilson_interval(2, 1)
        with self.assertRaises(ValueError):
            decide_qa_gate(supported_total=40, supported_exact=40,
                           unsupported_total=100, unsupported_abstained=100,
                           max_false_citation_upper95=float("nan"))


class ProspectiveSourceProofTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.db = self.folder / "private.sqlite3"
        self.dev = self.folder / "development.jsonl"
        self.prospective = self.folder / "prospective.jsonl"
        memory = ExperienceMemory(self.db)
        self.supported = []
        for index in range(40):
            key = f"protoks{index:04d}"
            second = f"wymiar{index:04d}"
            url = f"https://docs.example.org/evidence-{index:04d}"
            text = f"Kod {key} {second} oznacza pomiar sztucznego instrumentu."
            raw = text.encode("utf-8")
            memory.observe_web(WebObservation(
                url=url, host="docs.example.org", text=text,
                content_sha256=hashlib.sha256(raw).hexdigest(),
                retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
                bytes_read=len(raw)))
            self.supported.append({
                "question": f"Co oznacza kod {key} {second}?",
                "answerable": True, "expected_source_url": url,
                "required_quote": f"Kod {key} {second} oznacza"})
        self.unsupported = [
            {"question": f"Co oznacza niezwiązane oznaczenie datakx{i:04d} spacex{i:04d}?",
             "answerable": False} for i in range(100)]
        self._write(self.dev, [
            {"question": "Co oznacza archiwum wirtualnego silnika?", "answerable": False},
            {"question": "Co to jest fenomen cytatu kodowego?", "answerable": True,
             "expected_source_url": "https://docs.example.org/dev",
             "required_quote": "fenomen cytatu"}])
        self._write(self.prospective, self.supported + self.unsupported)

    @staticmethod
    def _write(path, cases):
        path.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n",
                        encoding="utf-8")

    def test_actual_sqlite_gate_and_no_mutations_or_private_report(self):
        old_digest = hashlib.sha256(self.db.read_bytes()).hexdigest()
        report = run_prospective_gate(
            self.db, self.dev, self.prospective,
            confirm_rights=True, confirm_untouched=True)
        self.assertEqual(report["supported_count"], 40)
        self.assertEqual(report["unsupported_count"], 100)
        self.assertEqual(report["supported_correct_literal"], 40)
        self.assertEqual(report["unsupported_false_citations"], 0)
        self.assertTrue(report["passes_numeric_prospective_gate"])
        self.assertFalse(report["prospective_independence_verified"])
        self.assertFalse(report["ready_for_semantic_chat"])
        self.assertFalse(report["source_quote_truth_verified"])
        self.assertFalse(report["internet_used"])
        self.assertFalse(report["sqlite_modified"])
        self.assertFalse(report["raw_questions_in_report"])
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(), old_digest)
        serial = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("protoks", serial)
        self.assertNotIn("https://", serial)
        print("PROSPECTIVE_QA_SYNTHETIC_METRICS=" + json.dumps({
            k: report[k] for k in (
                "supported_exact_quote_recall", "supported_recall_wilson95_lower",
                "unsupported_false_citation_rate", "unsupported_false_citation_wilson95_upper",
                "abstain_all_baseline_accuracy", "passes_numeric_prospective_gate")
        }, sort_keys=True), flush=True)

    def test_exact_leakage_between_development_and_prospective_is_blocked(self):
        self._write(self.dev, [
            {"question": "CO oznacza KOD protoks0000 wymiar0000 !", "answerable": False},
            {"question": "Co nieistniejące?", "answerable": True,
             "expected_source_url": "https://docs.example.org/test",
             "required_quote": "nieistniejące źródło"}])
        with self.assertRaisesRegex(ValueError, "overlap"):
            run_prospective_gate(
                self.db, self.dev, self.prospective,
                confirm_rights=True, confirm_untouched=True)

    def test_unsupported_claim_sharing_subject_terms_fails_quality_gate(self):
        unsupported = self.unsupported.copy()
        for i in range(12):
            unsupported[i] = {
                "question": f"Dlaczego kod protoks{i:04d} wymiar{i:04d} jest niebezpieczny?",
                "answerable": False}
        self._write(self.prospective, self.supported + unsupported)
        report = run_prospective_gate(
            self.db, self.dev, self.prospective,
            confirm_rights=True, confirm_untouched=True)
        self.assertGreater(report["unsupported_false_citations"], 0)
        self.assertFalse(report["passes_numeric_prospective_gate"])

    def test_no_rights_or_tiny_audit_and_duplicate_normalized_fail_closed(self):
        with self.assertRaises(PermissionError):
            run_prospective_gate(self.db, self.dev, self.prospective)
        with self.assertRaisesRegex(ValueError, "insufficient"):
            run_prospective_gate(
                self.db, self.dev, self.prospective,
                confirm_rights=True, confirm_untouched=True, min_supported=41)
        rows = self.supported + self.unsupported
        rows[-1] = {"question": self.unsupported[0]["question"].upper() + " !",
                    "answerable": False}
        self._write(self.prospective, rows)
        with self.assertRaisesRegex(ValueError, "duplicate normalized"):
            run_prospective_gate(
                self.db, self.dev, self.prospective,
                confirm_rights=True, confirm_untouched=True)


if __name__ == "__main__":
    unittest.main()
