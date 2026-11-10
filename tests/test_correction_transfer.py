"""Private held-out correction-memory transfer: no fabricated science claims.

Mocks only test the experiment *protocol*. The model inference is separately
checked with real bundled GGUF in Windows release CI. Neither confirms
independent real-world generalization without an untouched user holdout.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from neurogenesis.corrective_memory import CorrectiveMemory
from neurogenesis.correction_transfer import (
    ReadOnlyCorrections, _read_audit, evaluate_transfer)


class TransferTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.path = self.root / "corrections.sqlite3"
        self.mem = CorrectiveMemory(self.path)
        self.a = self.mem.approve(
            "Jaki jest kod identyfikacyjny urządzenia Kobalt?",
            "Zatwierdzony kod Kobalt to KOB-914.", confirmed=True)
        self.b = self.mem.approve(
            "Jaki identyfikator ma pamięć Kosmos?",
            "Poprawny numer pamięci Kosmos to MEM-72.", confirmed=True)
        self.audit = self.root / "heldout.jsonl"
        self.cases = [
            {"kind": "paraphrase", "question":
             "Podaj numer identyfikacyjny urządzenia Kobalt?",
             "expected_correction_id": self.a["id"],
             "expected_answer_fragment": "KOB-914"},
            {"kind": "paraphrase", "question":
             "Numer identyfikacyjny Kobalt urządzenia?",
             "expected_correction_id": self.a["id"],
             "expected_answer_fragment": "KOB-914"},
            {"kind": "paraphrase", "question":
             "Identyfikacyjny urządzenia Kobalt?",
             "expected_correction_id": self.a["id"],
             "expected_answer_fragment": "KOB-914"},
            {"kind": "unrelated", "question":
             "W jakiej jednostce mierzymy pole magnetyczne?",
             "forbidden_answer_fragment": "KOB-914"},
            {"kind": "unrelated", "question":
             "Jakie gatunki ptaków żyją w tundrze?",
             "forbidden_answer_fragment": "MEM-72"},
            {"kind": "unrelated", "question":
             "Kiedy występuje zaćmienie Księżyca?",
             "forbidden_answer_fragment": "KOB-914"},
        ]
        self._write()

    def _write(self):
        self.audit.write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in self.cases)
            + "\n", encoding="utf-8")

    @staticmethod
    def fake_factory(corrections):
        class Model:
            def __init__(self, memory):
                self.memory = memory
                self.started = False
                self.stopped = False
                self.calls = []

            def start(self):
                self.started = True

            def stop(self):
                self.stopped = True

            def chat(self, messages, *, use_context=True, deterministic=False):
                assert deterministic
                q = messages[-1]["content"]
                self.calls.append((q, use_context))
                selected = self.memory.retrieve(q) if use_context else []
                return {
                    "reply": ("Odpowiedź: " + selected[0]["text"]
                              if selected else "Nie potwierdzono kodu."),
                    "sources": [
                        {"label": "L1", "file": selected[0]["file"],
                         "sha256": selected[0]["sha256"]}] if selected else [],
                    "correction_memory": {
                        "approved_correction_used": bool(selected)}
                }
        return Model(corrections)

    def _evaluate(self, **kwargs):
        return evaluate_transfer(
            self.path, self.audit, confirm_rights=True,
            confirm_independent_holdout=True,
            session_factory=self.fake_factory, **kwargs)

    def test_paraphrase_transfer_and_unrelated_abstention_stays_private(self):
        before_db = self.path.read_bytes()
        original_questions = [x["question"] for x in self.cases]
        report = self._evaluate()
        self.assertEqual(report["total_cases"], 6)
        self.assertEqual(report["paraphrases"], 3)
        self.assertEqual(report["unrelated_negative_controls"], 3)
        self.assertEqual(report["conditions"]["approved_memory"]["literal_hits"], 3)
        self.assertEqual(report["conditions"]["no_memory"]["literal_hits"], 0)
        self.assertEqual(report["positive_expected_source_hits"], 3)
        self.assertEqual(report["positive_wrong_correction_sources"], 0)
        self.assertEqual(report["unrelated_sources_injected"], 0)
        self.assertEqual(report["unrelated_forbidden_fragment_with_memory"], 0)
        self.assertEqual(
            report["paired_positive_literal_comparison"]["literal_rate_difference"],
            1.0)
        self.assertEqual(report["actual_gguf_inference"], False)
        self.assertFalse(report["truth_or_agi_proven"])
        self.assertFalse(report["heldout_independence_verified_by_program"])
        self.assertFalse(report["automatic_model_promotion"])
        self.assertEqual(before_db, self.path.read_bytes())
        packed = json.dumps(report, ensure_ascii=False)
        for q in original_questions:
            self.assertNotIn(q, packed)
        for sensitive in ("KOB-914", "MEM-72", "urządzenia Kobalt"):
            self.assertNotIn(sensitive, packed)

    def test_memory_store_is_read_only_even_if_approve_is_called(self):
        readonly = ReadOnlyCorrections(self.path)
        before = self.path.read_bytes()
        self.assertEqual(len(readonly.retrieve(self.cases[0]["question"])), 1)
        with self.assertRaises(Exception):
            readonly.approve(
                "Pytanie o nową próbę badawczą?",
                "Wymuszona poprawka powinna zostać odrzucona.",
                confirmed=True)
        self.assertEqual(before, self.path.read_bytes())

    def test_no_training_question_leakage_and_no_duplicate_probe(self):
        self.cases[0]["question"] = (
            "Jaki jest kod identyfikacyjny urządzenia Kobalt?")
        self._write()
        with self.assertRaisesRegex(ValueError, "in-training"):
            self._evaluate()
        self.cases[0]["question"] = self.cases[1]["question"]
        self._write()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self._evaluate()

    def test_heldout_answer_must_be_in_training_but_not_in_question(self):
        self.cases[0]["expected_answer_fragment"] = "UNSEEN-NEVER"
        self._write()
        with self.assertRaisesRegex(ValueError, "target missing"):
            self._evaluate()
        self.cases[0]["expected_answer_fragment"] = "KOB-914"
        self.cases[0]["question"] += " KOB-914"
        self._write()
        with self.assertRaisesRegex(ValueError, "leaked into question"):
            self._evaluate()

    def test_only_positive_negative_balanced_private_audit(self):
        self.cases = self.cases[:3]
        self._write()
        with self.assertRaisesRegex(ValueError, "Require"):
            self._evaluate()
        self.cases = self.cases + [self.cases[0]] * 3
        self._write()
        with self.assertRaises(ValueError):
            self._evaluate()

    def test_abort_on_live_memory_change_no_model_promotion(self):
        writable = self.mem
        models = []
        def factory(corrections):
            fake = self.fake_factory(corrections)
            base_chat = fake.chat
            done = [False]

            def with_concurrent_revision(*args, **kwargs):
                res = base_chat(*args, **kwargs)
                if not done[0]:
                    writable.approve(
                        "Jaki jest kod identyfikacyjny urządzenia Kobalt?",
                        "Nowa wersja: KOB-999.",
                        confirmed=True)
                    done[0] = True
                return res

            fake.chat = with_concurrent_revision
            models.append(fake)
            return fake
        with self.assertRaisesRegex(ValueError, "mutated|changed"):
            evaluate_transfer(
                self.path, self.audit, confirm_rights=True,
                confirm_independent_holdout=True, session_factory=factory)
        self.assertTrue(models[0].stopped)

    def test_explicit_consent_missing_fails_before_model_start(self):
        with self.assertRaises(PermissionError):
            evaluate_transfer(self.path, self.audit, session_factory=self.fake_factory)
        with self.assertRaises(ValueError):
            ReadOnlyCorrections(self.root / "missing.sqlite3")

    def test_error_propagates_and_closes_model(self):
        created = []
        class Failure:
            def start(self):
                pass
            def stop(self):
                self.stopped = True
            def chat(self, *_a, **_k):
                raise RuntimeError("deliberate mocked failure")
        def factory(_memory):
            instance = Failure()
            created.append(instance)
            return instance
        with self.assertRaises(RuntimeError):
            evaluate_transfer(
                self.path, self.audit,
                confirm_rights=True, confirm_independent_holdout=True,
                session_factory=factory)
        self.assertTrue(created[0].stopped)


if __name__ == "__main__":
    unittest.main()
