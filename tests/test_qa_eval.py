"""Read-only evidence QA fixture. Fictional local data, no external sources."""
from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit

from neurogenesis.memory import ExperienceMemory
from neurogenesis.qa_eval import evaluate_qa, main
from neurogenesis.web_sense import WebObservation


def synthetic_web(url: str, text: str) -> WebObservation:
    raw = text.encode("utf-8")
    return WebObservation(
        url=url, host=urlsplit(url).hostname or "",
        text=text, content_sha256=hashlib.sha256(raw).hexdigest(),
        retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
        bytes_read=len(raw))


class ReadOnlyQaAuditTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.db = self.root / "private.sqlite3"
        self.audit = self.root / "prospective.jsonl"
        self.memory = ExperienceMemory(self.db)
        self.memory.observe_web(synthetic_web(
            "https://docs.example.org/neuronix",
            "Teoria Neuronix opisuje plastyczność synaptyczna układów. "
            "Badanie Neuronix obejmuje odrębne eksperymenty."))
        self.memory.observe_web(synthetic_web(
            "https://docs.example.net/atria",
            "Eksperymenty Atria wymagają pomiaru temperatury sensorów. "
            "Raport Atria opisuje testy trwałości."))
        self.rows = [
            {"question": "Czym jest plastyczność synaptyczna?",
             "answerable": True, "expected_source_url": "https://docs.example.org/neuronix",
             "required_quote": "plastyczność synaptyczna układów"},
            {"question": "Jak mierzyć temperatury sensorów?",
             "answerable": True, "expected_source_url": "https://docs.example.net/atria",
             "required_quote": "pomiaru temperatury sensorów"},
            {"question": "Jakie testy opisuje raport Atria?",
             "answerable": True, "expected_source_url": "https://docs.example.net/atria",
             "required_quote": "Raport Atria opisuje testy trwałości"},
            {"question": "Dlaczego Neuronix lubi pomarańcze?", "answerable": False},
            {"question": "Jak pracują kriogeniczne silniki rakietowe?",
             "answerable": False},
            # Deliberately lexical-overlapping but factually unsupported. The
            # current heuristic can over-answer; the benchmark reports this
            # failure rather than claiming perfect calibrated abstention.
            {"question": "Czy teoria Neuronix jest całkowicie fałszywa?",
             "answerable": False},
        ]
        self.write_rows(self.rows)

    def write_rows(self, rows):
        self.audit.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
            encoding="utf-8")

    def test_real_local_qa_metrics_provenance_abstention_and_no_sqlite_mutation(self):
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        report = evaluate_qa(self.db, self.audit,
                             confirm_rights=True, confirm_heldout=True)
        self.assertEqual(report["task"],
                         "literal_evidence_qa_and_abstention_not_semantic_or_truth_accuracy")
        self.assertEqual(report["cases"], 6)
        self.assertEqual(report["supported_cases"], 3)
        self.assertEqual(report["unsupported_cases"], 3)
        self.assertEqual(report["correct_literal_citations"], 3)
        self.assertEqual(report["supported_exact_quote_recall"], 1.0)
        self.assertEqual(report["supported_source_hit_rate"], 1.0)
        # Development fixture was previously observed. A rule improvement here
        # is NOT independent prospective semantic-answer evidence.
        self.assertGreaterEqual(report["unsupported_abstention_rate"], 2 / 3)
        self.assertLessEqual(report["unsupported_false_citation_rate"], 1 / 3)
        self.assertTrue(0.0 <= report["overall_strict_fixture_accuracy"] <= 1.0)
        self.assertGreaterEqual(report["latency_p95_ms"], report["latency_p50_ms"])
        self.assertFalse(report["internet_used"])
        self.assertFalse(report["sqlite_modified"])
        self.assertFalse(report["trainable_weights_evaluated"])
        self.assertFalse(report["independently_fact_checked"])
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(), before)
        self.assertEqual(self.memory.status()["records_with_raw_text"], 0)
        print("GROUNDING_QA_SYNTHETIC_METRICS=" + json.dumps({
            k: report[k] for k in (
                "supported_exact_quote_recall", "unsupported_abstention_rate",
                "unsupported_false_citation_rate", "overall_strict_fixture_accuracy",
                "latency_p95_ms")
        }, sort_keys=True), flush=True)

    def test_permissions_required_and_bad_input_never_creates_db(self):
        with self.assertRaises(PermissionError):
            evaluate_qa(self.db, self.audit)
        with self.assertRaises(ValueError):
            evaluate_qa(self.root / "absent.sqlite3", self.audit,
                        confirm_rights=True, confirm_heldout=True)
        self.assertFalse((self.root / "absent.sqlite3").exists())
        self.write_rows(self.rows + [self.rows[0]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate_qa(self.db, self.audit, confirm_rights=True, confirm_heldout=True)
        invalid = [{"question": "Co to jest?", "answerable": True,
                    "expected_source_url": "http://invalid.example", "required_quote": "co"}]
        self.write_rows(invalid + [self.rows[3]])
        with self.assertRaisesRegex(ValueError, "source URL"):
            evaluate_qa(self.db, self.audit, confirm_rights=True, confirm_heldout=True)

    def test_evaluator_produces_only_aggregate_json_never_private_questions(self):
        buf = StringIO()
        with redirect_stdout(buf):
            rc = main([
                "--db", str(self.db), "--audit", str(self.audit),
                "--confirm-corpus-rights", "--confirm-held-out"])
        self.assertEqual(rc, 0)
        result = json.loads(buf.getvalue())
        self.assertNotIn("Czym jest", buf.getvalue())
        self.assertNotIn("http", buf.getvalue())
        self.assertEqual(result["cases"], 6)
        self.assertEqual(result["raw_questions_in_report"], False)

    def test_unreadable_audit_utf8_and_missing_negative_examples_fail(self):
        self.audit.write_bytes(b"\xff" * 100)
        with self.assertRaises(ValueError):
            evaluate_qa(self.db, self.audit, confirm_rights=True, confirm_heldout=True)
        self.write_rows(self.rows[:3])
        with self.assertRaisesRegex(ValueError, "both"):
            evaluate_qa(self.db, self.audit, confirm_rights=True, confirm_heldout=True)


if __name__ == "__main__":
    unittest.main()
