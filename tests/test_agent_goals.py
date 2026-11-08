"""Deterministic agentic workflow tests; no fake LLM success or cloud access.

A separately mandatory Windows FULL test proves actual pretrained model
inference; these cases test goal scheduling, retrieval, source revision,
operator review and crash recovery.
"""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

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
        self.assertIn("Przeanalizuj dostępne lokalne źródła",
                      prompt_for_goal(claim))
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


if __name__ == "__main__":
    unittest.main()
