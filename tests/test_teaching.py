"""Real neural/SQLite integration tests for explicitly taught local responses.

Associative responses are symbolic teaching, not claims of neural semantics.
"""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from neurogenesis.memory import ExperienceMemory
from neurogenesis.desktop import process_message
from neurogenesis.autonomy import AutonomicSupervisor, WINDOW
from neurogenesis.predictor import NextInputPredictor


class TaughtResponseTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.db = Path(self.folder.name) / "neural.sqlite3"
        self.memory = ExperienceMemory(self.db)

    def test_new_database_has_zero_taught_responses(self):
        self.assertEqual(self.memory.status()["taught_responses"], 0)
        self.assertIsNone(self.memory.taught_answer("Co umiesz?"))

    def test_teaching_updates_same_neural_brain_and_persists_after_restart(self):
        start = self.memory.brain().steps
        row = self.memory.teach("Czym jest neuron?", "Podstawowy element sieci.")
        self.assertTrue(row["teaching_saved"])
        self.assertEqual(row["brain_step"], start + 4)
        reopened = ExperienceMemory(self.db)
        self.assertEqual(reopened.status()["taught_responses"], 1)
        self.assertEqual(reopened.brain().steps, start + 4)
        reply = reopened.taught_answer("  CZYM  jest   NEURON???")
        self.assertEqual(reply["answer"], "Podstawowy element sieci.")
        self.assertEqual(reply["brain_step_at_teaching"], start + 4)
        self.assertEqual(reply["response_kind"], "explicit_local_teaching")
        self.assertEqual(reopened.status()["records_with_raw_text"], 0)

    def test_real_desktop_response_changes_only_for_taught_question(self):
        self.memory.teach("Co to jest synapsa?", "Połączenie neuronów.")
        result = process_message(self.memory, "CO TO JEST SYNAPSA?!")
        self.assertEqual(result["reply"], "Połączenie neuronów.")
        self.assertEqual(result["response_kind"], "explicit_local_teaching")
        unknown = process_message(self.memory, "Co to jest kompletnie inne pytanie?")
        self.assertEqual(unknown["response_kind"], "sensory_acknowledgement")
        self.assertIn("Nie znam jeszcze odpowiedzi", unknown["reply"])
        self.assertEqual(self.memory.status()["taught_responses"], 1)

    def test_overwrite_is_explicit_and_does_not_create_duplicate(self):
        self.memory.teach("Witaj", "Cześć.")
        self.memory.teach("WITAJ!", "Witaj ponownie.")
        self.assertEqual(self.memory.status()["taught_responses"], 1)
        self.assertEqual(self.memory.taught_answer("Witaj")["answer"], "Witaj ponownie.")
        self.assertEqual(self.memory.brain().steps, 8)

    def test_forget_is_explicit_does_not_unlearn_neurons(self):
        self.memory.teach("Pytanie", "Odpowiedź")
        before = self.memory.brain().to_dict()
        self.assertTrue(self.memory.forget_teaching("pytanie???"))
        self.assertFalse(self.memory.forget_teaching("pytanie"))
        self.assertEqual(self.memory.brain().to_dict(), before)
        self.assertIsNone(self.memory.taught_answer("Pytanie"))
        self.assertEqual(self.memory.status()["observations"], 1)

    def test_invalid_teaching_is_atomic_and_fails_closed(self):
        initial = self.memory.brain().to_dict()
        for question, answer in (
            ("", "valid"), ("?", "valid"), ("valid", ""), ("valid", None),
            ("valid", "x" * 2001), ("valid", "bad\0control"),
            ("x" * 513, "valid"),
        ):
            with self.subTest(question=question[:10], answer=repr(answer)[:10]):
                with self.assertRaises(ValueError):
                    self.memory.teach(question, answer)
        self.assertEqual(self.memory.brain().to_dict(), initial)
        self.assertEqual(self.memory.status()["observations"], 0)
        self.assertEqual(self.memory.status()["taught_responses"], 0)

    def test_sqlite_injection_is_ordinary_text_not_sql(self):
        q = "Czy to zapytanie'; DROP TABLE neural_state; --"
        a = "Tak'; DELETE FROM observations;"
        self.memory.teach(q, a)
        self.assertEqual(self.memory.taught_answer(q)["answer"], a)
        self.assertIsNotNone(self.memory.brain())
        self.assertEqual(self.memory.status()["observations"], 1)

    def test_respects_operator_capacity_and_does_not_evict_earlier_teachings(self):
        self.memory.teach("Pierwsze", "A")
        old = ExperienceMemory.MAX_TEACHINGS
        try:
            ExperienceMemory.MAX_TEACHINGS = 1
            before = self.memory.brain().to_dict()
            with self.assertRaisesRegex(ValueError, "capacity"):
                self.memory.teach("Drugie", "B")
            self.assertEqual(self.memory.brain().to_dict(), before)
            self.assertEqual(self.memory.status()["observations"], 1)
            self.memory.teach("pierwsze", "Poprawiona")
            self.assertEqual(self.memory.taught_answer("Pierwsze")["answer"], "Poprawiona")
        finally:
            ExperienceMemory.MAX_TEACHINGS = old

    def test_tampered_association_blocks_retrieval_and_rollback_of_teaching(self):
        self.memory.teach("Bezpieczne pytanie", "Dobra odpowiedź")
        with closing(self.memory._connect()) as con, con:
            con.execute("UPDATE taught_responses SET question_normalized='inny klucz'")
        with self.assertRaisesRegex(ValueError, "corrupted"):
            self.memory.taught_answer("Bezpieczne pytanie")
        before = self.memory.brain().to_dict()
        with self.assertRaisesRegex(ValueError, "corrupted"):
            self.memory.teach("Bezpieczne pytanie", "Nowa")
        self.assertEqual(self.memory.brain().to_dict(), before)
        self.assertEqual(self.memory.status()["observations"], 1)

    def test_general_messages_up_to_original_limit_still_work(self):
        query = "?" * 600
        result = process_message(self.memory, query)
        self.assertEqual(result["response_kind"], "sensory_acknowledgement")
        self.assertEqual(self.memory.status()["observations"], 1)
        self.assertEqual(self.memory.status()["taught_responses"], 0)

    def test_teaching_after_adaptive_predictor_keeps_brain_and_readout_in_sync(self):
        # Force only the commit path of a real NextInputPredictor: the real
        # upstream self-development algorithm is separately benchmarked.
        for i in range(WINDOW):
            self.memory.remember("bodziec {}".format(i))
        def promote(predictor, **kwargs):
            clone = NextInputPredictor.from_dict(predictor.to_dict())
            clone.step([1.0] + [0.0] * (clone.brain.config.input_size - 1))
            return clone, {"promoted": True, "reason": "contract_promotion"}
        with patch("neurogenesis.autonomy.run_self_development_cycle", side_effect=promote):
            self.assertTrue(AutonomicSupervisor(self.memory).cycle()["promoted"])
        before = self.memory.brain().steps
        self.memory.teach("Czy działa po aktualizacji?", "Tak, na tej samej sieci.")
        self.assertEqual(self.memory.brain().steps, before + 4)
        with closing(self.memory._connect()) as con:
            packed = con.execute("SELECT predictor_json FROM predictor_state WHERE id=1").fetchone()[0]
        predictor = NextInputPredictor.from_dict(json.loads(packed))
        self.assertEqual(predictor.brain.to_dict(), self.memory.brain().to_dict())
        self.assertEqual(self.memory.taught_answer("Czy działa po aktualizacji?")["answer"],
                         "Tak, na tej samej sieci.")

    def test_stored_teaching_is_not_copied_into_observation_raw_text(self):
        self.memory.teach("Moje pytanie", "Moja odpowiedź")
        with closing(self.memory._connect()) as con:
            row = con.execute("SELECT raw_text,source FROM observations").fetchone()
        self.assertEqual(row, (None, "desktop-teaching"))
        self.assertEqual(self.memory.status()["records_with_raw_text"], 0)


if __name__ == "__main__":
    unittest.main()
