"""Deterministic agentic workflow tests; no fake LLM success or cloud access.

A separately mandatory Windows FULL test proves actual pretrained model
inference; these cases test goal scheduling, retrieval, source revision,
operator review and crash recovery.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import tempfile
import unittest

from neurogenesis.memory import ExperienceMemory
from neurogenesis.web_sense import WebObservation
from neurogenesis.bundled_llm import check_chat_messages

from neurogenesis.agent_goals import (
    GoalStore, MAX_ACTIVE, goal_fingerprint, prompt_for_goal)
from neurogenesis.local_knowledge import LocalKnowledge


class AutonomousAgentGoalsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="ng-autonomous-goals-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.knowledge = LocalKnowledge(self.root / "knowledge.sqlite3")
        self.goals = GoalStore(self.root / "goals.sqlite3")

    def test_no_source_yields_explicit_plan_and_waits_for_new_information(self):
        gid = self.goals.add("Zbadaj zasadę indukcyjności silnika i zaplanuj eksperyment.")
        first = self.goals.claim(self.knowledge)
        self.assertEqual(first["id"], gid)
        self.assertEqual(first["sources"], [])
        self.assertIn("Brak odpowiednich lokalnych źródeł",
                      prompt_for_goal(first))
        report = self.goals.complete(
            first, "Plan: znaleźć źródło, zweryfikować dokumentację, zapisać wynik.")
        self.assertEqual(report["state"], "waiting")
        self.assertTrue(report["review_required"])
        self.assertEqual(self.goals.list()[0]["state"], "waiting")
        self.assertIsNone(self.goals.claim(self.knowledge))
        self.assertEqual(self.knowledge.status()["files"], 0)

    def test_real_source_added_triggers_autonomous_new_candidate(self):
        gid = self.goals.add("Opisz fizykę indukcyjności w eksperymencie elektrycznym.")
        empty = self.goals.claim(self.knowledge)
        self.goals.complete(empty, "Plan działania bez danych.")
        source = self.root / "indukcyjność.txt"
        source.write_text(
            "Właściwości indukcyjności są związane z polem magnetycznym. "
            "Zmiana prądu w cewce indukuje siłę elektromotoryczną. " * 33,
            encoding="utf-8")
        indexed = self.knowledge.import_txt(source, approved=True)
        claim = self.goals.claim(self.knowledge)
        self.assertIsNotNone(claim)
        self.assertEqual(claim["id"], gid)
        self.assertGreater(len(claim["sources"]), 0)
        prompt = prompt_for_goal(claim)
        self.assertIn("Przeanalizuj PONIŻSZE RZECZYWIŚCIE ZEBRANE FRAGMENTY", prompt)
        self.assertIn("SHA256 " + indexed["sha256"][:16], prompt)
        self.assertIn("Właściwości indukcyjności", prompt)
        check_chat_messages([{"role": "user", "content": prompt}])
        self.assertNotEqual(empty["fingerprint"], claim["fingerprint"])
        report = self.goals.complete(
            claim, "Raport-kandydat: indukcyjność wymaga potwierdzania źródłem.")
        self.assertEqual(report["state"], "candidate")
        self.assertFalse(report["model_weight_training"])
        stored = self.goals.list()[0]
        self.assertEqual(stored["state"], "candidate")
        self.assertEqual(stored["sources"][0]["file"], source.name)
        self.assertEqual(stored["sources"][0]["sha256"], indexed["sha256"])
        self.assertIsNone(self.goals.claim(self.knowledge))
        self.goals.set_state(gid, "accept")
        self.assertEqual(self.goals.list()[0]["state"], "accepted")
        self.assertIsNone(self.goals.claim(self.knowledge))

    def test_source_revision_triggers_reanalysis_preserves_private_history(self):
        gid = self.goals.add("Sprawdź parametry przepływu powietrza w układzie testowym.")
        file = self.root / "dane.txt"
        file.write_text("Przepływ powietrza wymaga pomiaru ciśnienia. " * 24,
                        encoding="utf-8")
        self.knowledge.import_txt(file, approved=True)
        first = self.goals.claim(self.knowledge)
        self.goals.complete(first, "Pierwszy raport kandydujący.")
        self.assertIsNone(self.goals.claim(self.knowledge))
        file.write_text(
            "Przepływ powietrza mierzono także temperaturą oraz objętością. " * 24,
            encoding="utf-8")
        self.knowledge.import_txt(file, approved=True)
        next_item = self.goals.claim(self.knowledge)
        self.assertIsNotNone(next_item)
        self.assertEqual(next_item["id"], gid)
        self.assertNotEqual(next_item["fingerprint"], first["fingerprint"])
        self.goals.complete(next_item, "Drugi raport wymagający oceny.")
        self.assertEqual(self.goals.list()[0]["attempts"], 2)
        self.assertEqual(self.goals.list()[0]["result"],
                         "Drugi raport wymagający oceny.")

    def test_queue_survives_restart_and_running_work_recovers_safely(self):
        gid = self.goals.add("Opracuj plan przeglądu lokalnych źródeł wiedzy.")
        claimed = self.goals.claim(self.knowledge)
        self.assertEqual(self.goals.list()[0]["state"], "running")
        reopened = GoalStore(self.goals.path)
        self.assertEqual(reopened.list()[0]["state"], "queued")
        second = reopened.claim(self.knowledge)
        self.assertEqual(second["id"], gid)
        reopened.fail(second, "Model przerwany.")
        self.assertEqual(reopened.list()[0]["state"], "error")
        with self.assertRaises(ValueError):
            reopened.set_state(gid, "accept")
        reopened.set_state(gid, "resume")
        self.assertIsNotNone(reopened.claim(self.knowledge))

    def test_pause_resume_and_bounded_number_of_goals(self):
        for i in range(MAX_ACTIVE):
            self.goals.add("Zbadaj odrębny eksperyment o numerze " + str(i + 100) + ".")
        with self.assertRaisesRegex(ValueError, "Limit"):
            self.goals.add("Zbadaj jeszcze jeden odrębny eksperyment numer 999.")
        gid = self.goals.list()[-1]["id"]
        self.assertEqual(self.goals.set_state(gid, "pause"), "paused")
        self.assertEqual(self.goals.set_state(gid, "resume"), "queued")
        self.assertEqual(self.goals.list()[-1]["state"], "queued")
        with self.assertRaises(ValueError):
            self.goals.add("krótkie")
        with self.assertRaises(ValueError):
            self.goals.add("Za" * 350)

    def test_fingerprint_changes_on_corpus_revision_not_on_idle_clock(self):
        first = goal_fingerprint([], self.knowledge.corpus_fingerprint())
        second = goal_fingerprint([], self.knowledge.corpus_fingerprint())
        self.assertEqual(first, second)
        file = self.root / "źródło.txt"
        file.write_text("Nowe źródło wiedzy laboratoryjnej. " * 40, encoding="utf-8")
        self.knowledge.import_txt(file, approved=True)
        third = goal_fingerprint([], self.knowledge.corpus_fingerprint())
        self.assertNotEqual(first, third)



    def test_real_web_observation_reawakens_waiting_goal_and_reaches_llm(self):
        memory = ExperienceMemory(self.root / "observations.sqlite3")
        goal = ("Wyjaśnij eksperyment związany z indukcyjnością cewki "
                "magnetycznej i jego ograniczenia.")
        gid = self.goals.add(goal)
        initial = self.goals.claim(self.knowledge, web_memory=memory)
        self.assertEqual(initial["sources"], [])
        self.goals.complete(initial, "Plan: poszukać danych o indukcyjności.")
        self.assertIsNone(self.goals.claim(self.knowledge, web_memory=memory))

        text = ("Indukcyjność w eksperymencie cewki magnetycznej "
                "zależy od zmian natężenia prądu i liczby zwojów. "
                "Wnioski wymagają pomiaru napięcia i natężenia.")
        url = "https://example.org/research/inductance"
        raw = text.encode("utf-8")
        observation = WebObservation(
            url=url, host="example.org", text=text,
            content_sha256=hashlib.sha256(raw).hexdigest(),
            retrieved_utc=datetime.now(timezone.utc).isoformat(),
            bytes_read=len(raw))
        memory.observe_web(observation)
        claimed = self.goals.claim(self.knowledge, web_memory=memory)
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed["id"], gid)
        self.assertTrue(claimed["sources"], "saved HTTPS evidence must enter goal")
        self.assertEqual(claimed["sources"][-1]["file"], url)
        self.assertEqual(claimed["sources"][-1]["sha256"],
                         observation.content_sha256)
        prompt = prompt_for_goal(claimed)
        self.assertIn("cewki magnetycznej", prompt)
        self.assertIn(url, prompt)
        self.assertIn(observation.content_sha256[:16], prompt)
        self.assertIn("NIEZAUFANE DANE", prompt)
        check_chat_messages([{"role": "user", "content": prompt}])
        self.goals.complete(claimed, "Kandydat z danych do oceny przez użytkownika.")
        self.assertEqual(self.goals.list()[0]["state"], "candidate")
        self.assertIsNone(self.goals.claim(self.knowledge, web_memory=memory))
        self.assertEqual(memory.status()["records_with_raw_text"], 0)

    def test_goal_prompt_contains_only_real_excerpts_and_is_bounded(self):
        goal = "Oceń eksperyment magnetyczny " + "A" * 550
        samples = [{
            "text": ("Pomiary indukcji wymagają kalibracji. " * 30),
            "file": "notatki.txt",
            "sha256": "a" * 64,
            "rank": 1,
        }, {
            "text": "Zawartość strony jest niepotwierdzona. " * 30,
            "file": "https://example.org/data",
            "sha256": "b" * 64,
            "rank": 2,
        }]
        message = prompt_for_goal({"goal": goal, "sources": samples})
        self.assertLessEqual(len(message), 1750)
        self.assertIn("notatki.txt", message)
        self.assertIn("https://example.org/data", message)
        self.assertIn("Pomiary indukcji", message)
        self.assertIn("Zawartość strony", message)
        check_chat_messages([{"role": "user", "content": message}])
        with self.assertRaises(ValueError):
            prompt_for_goal({"goal": goal, "sources": [dict(
                samples[0], sha256="fake")]})

if __name__ == "__main__":
    unittest.main()
