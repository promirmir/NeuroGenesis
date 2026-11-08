"""Offline end-to-end tests: approved web -> SQLite -> quoted chat -> restart.

Synthetic documents and prospective questions are local fixtures; no internet,
copyrighted corpus, PyTorch weight training, or GPU claim is involved.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest
from urllib.parse import urlsplit

from neurogenesis.desktop import process_message
from neurogenesis.knowledge import passages
from neurogenesis.memory import ExperienceMemory
from neurogenesis.web_sense import WebObservation


def source(text: str, url: str = "https://example.org/biology") -> WebObservation:
    data = text.encode("utf-8")
    return WebObservation(url=url, host=urlsplit(url).hostname or "", text=text,
                          content_sha256=hashlib.sha256(data).hexdigest(),
                          retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
                          bytes_read=len(data))


class KnowledgePipelineTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "legacy-compatible.sqlite3"
        self.memory = ExperienceMemory(self.path)

    def test_full_vertical_slice_after_restart_and_source_attribution(self):
        text = ("Plastyczność synaptyczna pozwala zmieniać siłę połączeń neuronów. "
                "Eksperymenty wykorzystują pomiar aktywności sieci.")
        observed = source(text)
        first = self.memory.observe_web(observed)
        self.assertFalse(first["web_duplicate"])
        self.assertEqual(self.memory.status()["knowledge"]["documents"], 1)
        self.assertEqual(self.memory.status()["records_with_raw_text"], 0)
        restored = ExperienceMemory(self.path)
        result = process_message(restored, "Jak działa plastyczność synaptyczna?")
        self.assertEqual(result["response_kind"], "source_evidence")
        self.assertIn("Plastyczność synaptyczna pozwala", result["reply"])
        self.assertIn(observed.url, result["reply"])
        self.assertEqual(result["sources"][0]["sha256"], observed.content_sha256)
        self.assertEqual(result["sources"][0]["version"], 1)
        self.assertEqual(restored.status()["knowledge"]["documents"], 1)

    def test_unknown_question_abstains_and_does_not_forge_sources(self):
        self.memory.observe_web(source("Kora mózgowa zawiera neurony i połączenia synaptyczne."))
        reply = process_message(self.memory, "Dlaczego teleskop obserwuje galaktyki?")
        self.assertEqual(reply["response_kind"], "sensory_acknowledgement")
        self.assertEqual(reply["sources"], [])
        self.assertNotIn("https://", reply["reply"])

    def test_exact_manual_teaching_precedes_index_retrieval(self):
        self.memory.observe_web(source("Plastyczność synaptyczna opisuje zmianę połączeń."))
        self.memory.teach("Jak działa plastyczność synaptyczna?", "Moja prywatna odpowiedź.")
        reply = process_message(self.memory, "Jak działa plastyczność synaptyczna?")
        self.assertEqual(reply["reply"], "Moja prywatna odpowiedź.")
        self.assertEqual(reply["response_kind"], "explicit_local_teaching")
        self.assertEqual(reply["sources"], [])

    def test_content_dedup_preserves_neural_steps_and_index_count(self):
        web = source("Słownik neuronów objaśnia plastyczność synaptyczna.")
        first = self.memory.observe_web(web)
        steps = self.memory.brain().steps
        second = self.memory.observe_web(web)
        self.assertEqual(first["event_id"], second["event_id"])
        self.assertTrue(second["web_duplicate"])
        self.assertEqual(self.memory.brain().steps, steps)
        self.assertEqual(self.memory.status()["knowledge"]["documents"], 1)

    def test_source_revisions_keep_history_but_answers_use_latest(self):
        self.memory.observe_web(source("Gwiazdy są zasilane wodorem i promieniowaniem."))
        self.assertEqual(len(self.memory.knowledge_sources()), 1)
        self.memory.observe_web(source("Planety powstają z pyłu międzygwiazdowego."))
        self.assertEqual(self.memory.status()["knowledge"]["documents"], 2)
        self.assertEqual(self.memory.knowledge_sources()[0]["version"], 2)
        stale = process_message(self.memory, "Co wiadomo o gwiazdy wodorem?")
        self.assertNotEqual(stale["response_kind"], "source_evidence")
        current = process_message(self.memory, "Skąd pochodzą planety pyłu?")
        self.assertEqual(current["response_kind"], "source_evidence")
        self.assertEqual(current["sources"][0]["version"], 2)

    def test_deletion_removes_text_index_but_not_existing_brain_learning(self):
        event = self.memory.observe_web(source(
            "Neuronix zdefiniował plastyczność synaptyczna."))["event_id"]
        neural = self.memory.brain().to_dict()
        self.assertTrue(self.memory.delete_event(event))
        self.assertEqual(self.memory.brain().to_dict(), neural)
        self.assertEqual(self.memory.status()["knowledge"]["documents"], 0)
        self.assertIsNone(self.memory.answer_from_knowledge("Czym jest plastyczność synaptyczna?"))

    def test_failed_knowledge_index_rolls_back_neural_and_provenance(self):
        before = self.memory.brain().to_dict()
        with closing(sqlite3.connect(self.path)) as con, con:
            con.execute("""CREATE TRIGGER fail_index BEFORE INSERT ON knowledge_passages
                           BEGIN SELECT RAISE(ABORT, 'forced rollback'); END""")
        with self.assertRaises(sqlite3.DatabaseError):
            self.memory.observe_web(source("Plastyczność synaptyczna w testach."))
        self.assertEqual(self.memory.brain().to_dict(), before)
        self.assertEqual(self.memory.status()["observations"], 0)
        self.assertEqual(self.memory.status()["web_observations"], 0)
        self.assertEqual(self.memory.status()["knowledge"]["documents"], 0)

    def test_additive_migration_preserves_old_explicit_teachings(self):
        self.memory.teach("Co lubisz?", "Odpowiedź tylko od operatora.")
        with closing(sqlite3.connect(self.path)) as con, con:
            con.execute("DROP TABLE knowledge_terms")
            con.execute("DROP TABLE knowledge_passages")
            con.execute("DROP TABLE knowledge_sources")
        old_brain = self.memory.brain().to_dict()
        reopened = ExperienceMemory(self.path)
        self.assertEqual(reopened.taught_answer("Co lubisz?")["answer"],
                         "Odpowiedź tylko od operatora.")
        self.assertEqual(reopened.brain().to_dict(), old_brain)
        self.assertEqual(reopened.status()["knowledge"], {"documents": 0, "passages": 0})

    def test_invalid_oversized_source_is_atomic(self):
        with self.assertRaises(ValueError):
            self.memory.observe_web(source("A" * 6001))
        self.assertEqual(self.memory.status()["observations"], 0)
        self.assertEqual(self.memory.status()["knowledge"]["passages"], 0)

    def test_heldout_questions_evidence_coverage_not_neural_accuracy(self):
        questions = [
            ("Czym jest plastyczność synaptyczna?", True),
            ("Jak mierzyć temperatury sensorów?", True),
            ("Jakie testy opisuje raport Atria?", True),
            ("Dlaczego Neuronix lubi pomarańcze?", False),
            ("Jak pracują kriogeniczne silniki rakietowe?", False),
        ]
        before = sum(self.memory.answer_from_knowledge(q) is not None for q, _ in questions)
        self.assertEqual(before, 0)
        self.memory.observe_web(source(
            "Teoria Neuronix opisuje plastyczność synaptyczna układów. "
            "Badanie Neuronix obejmuje odrębne eksperymenty."))
        self.memory.observe_web(source(
            "Eksperymenty Atria wymagają pomiaru temperatury sensorów. "
            "Raport Atria opisuje testy trwałości.",
            "https://example.org/instruments"))
        predictions = [self.memory.answer_from_knowledge(q) is not None
                       for q, _ in questions]
        self.assertEqual(predictions, [expected for _, expected in questions])
        # Coverage changes from 0/3 to 3/3 positive cases in this tiny
        # synthetic fixture, not 0% to 100% model accuracy or cognition.

    def test_two_distinct_hosts_show_exact_quotes_and_both_citations(self):
        first = ("Raport Fenix opisuje temperaturę graniczną 42 stopnie urządzenia. "
                 "Metoda stanowi badanie demonstracyjne.")
        second = ("Raport Fenix opisuje temperaturę graniczną 35 stopni urządzenia. "
                  "Metoda stanowi badanie demonstracyjne.")
        self.memory.observe_web(source(first, "https://research.example.org/fenix"))
        self.memory.observe_web(source(second, "https://lab.example.net/fenix"))
        restored = ExperienceMemory(self.path)
        reply = process_message(
            restored, "Co mówi raport Fenix o temperaturę graniczną urządzenia?")
        self.assertEqual(reply["response_kind"], "source_evidence")
        self.assertEqual(len(reply["sources"]), 2)
        self.assertEqual(len({s["url"] for s in reply["sources"]}), 2)
        self.assertIn("42 stopnie", reply["reply"])
        self.assertIn("35 stopni", reply["reply"])
        self.assertEqual(
            reply["evidence_review"]["signals"], ["possible_numeric_difference"])
        self.assertTrue(reply["evidence_review"]["potential_discrepancy"])
        self.assertFalse(reply["evidence_review"]["independently_fact_checked"])
        self.assertFalse(reply["evidence_review"]["publisher_independence_verified"])
        self.assertIn("NIE potwierdzona sprzeczność faktów", reply["reply"])
        self.assertEqual(restored.status()["records_with_raw_text"], 0)

    def test_opposite_negation_flags_inspection_not_verified_fact(self):
        a = "Próba Solara potwierdza obecność lodu w próbkach."
        b = "Próba Solara nie potwierdza obecność lodu w próbkach."
        self.memory.observe_web(source(a, "https://alpha.example.org/solara"))
        self.memory.observe_web(source(b, "https://beta.example.net/solara"))
        answer = self.memory.answer_from_knowledge(
            "Co mówi próba Solara o obecność lodu w próbkach?")
        self.assertIsNotNone(answer)
        self.assertEqual(len(answer["sources"]), 2)
        self.assertIn("possible_negation_difference",
                      answer["evidence_review"]["signals"])

    def test_same_host_variants_do_not_count_as_second_source(self):
        a = "Raport Fenix opisuje temperaturę graniczną 42 stopnie urządzenia."
        b = "Raport Fenix opisuje temperaturę graniczną 35 stopni urządzenia."
        self.memory.observe_web(source(a, "https://www.example.org/lab"))
        self.memory.observe_web(source(b, "https://example.org/other"))
        answer = self.memory.answer_from_knowledge(
            "Co mówi raport Fenix o temperaturę graniczną urządzenia?")
        self.assertIsNotNone(answer)
        self.assertEqual(len(answer["sources"]), 1)
        self.assertFalse(answer["evidence_review"]["potential_discrepancy"])

    def test_updated_latest_revision_hides_stale_numeric_claim(self):
        url = "https://first.example.org/fenix"
        self.memory.observe_web(source(
            "Raport Fenix opisuje temperaturę graniczną 42 stopnie urządzenia.", url))
        self.memory.observe_web(source(
            "Raport Fenix opisuje temperaturę graniczną 44 stopnie urządzenia.", url))
        self.memory.observe_web(source(
            "Raport Fenix opisuje temperaturę graniczną 44 stopnie urządzenia.",
            "https://other.example.net/fenix"))
        answer = self.memory.answer_from_knowledge(
            "Co mówi raport Fenix o temperaturę graniczną urządzenia?")
        self.assertIsNotNone(answer)
        self.assertEqual(len(answer["sources"]), 2)
        self.assertNotIn("42 stopnie", answer["answer"])
        self.assertIn("44 stopnie", answer["answer"])
        self.assertFalse(answer["evidence_review"]["potential_discrepancy"])
        self.assertEqual(len(self.memory.knowledge_sources()), 3)

    def test_multiple_sources_do_not_mistakenly_support_unrelated_question(self):
        self.memory.observe_web(source(
            "Raport Fenix opisuje temperaturę graniczną 42 stopnie urządzenia.",
            "https://first.example.org/fenix"))
        self.memory.observe_web(source(
            "Raport Fenix opisuje temperaturę graniczną 35 stopni urządzenia.",
            "https://other.example.net/fenix"))
        result = process_message(self.memory, "Dlaczego księżyc orbituje wokół planety?")
        self.assertEqual(result["response_kind"], "sensory_acknowledgement")
        self.assertEqual(result["sources"], [])
        self.assertIsNone(result["evidence_review"])

    def test_passage_boundaries_and_rejection(self):
        self.assertTrue(all(len(p) <= 450 for p in passages("Ala." * 1200)))
        with self.assertRaises(ValueError):
            passages(" ")
        with self.assertRaises(ValueError):
            passages("A" * 6001)


if __name__ == "__main__":
    unittest.main()
