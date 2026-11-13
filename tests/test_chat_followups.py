"""Regression tests for continued offline conversation after the first reply.

Pure history tests run on every CI platform. The Windows acceptance case
exercises the actual default Tk widgets with a deterministic fake transport;
the separate FULL release gate validates real Qwen inference.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

from neurogenesis.bundled_llm import bounded_chat_history, check_chat_messages
from neurogenesis.agent_goals import GoalStore
from neurogenesis.autonomy import AutonomicSupervisor
from neurogenesis.local_knowledge import LocalKnowledge
from neurogenesis.memory import ExperienceMemory
from neurogenesis.tk_autonomous_home import install_autonomous_home


class BoundedDialogueTests(unittest.TestCase):
    def test_second_question_keeps_first_exchange_in_order(self):
        first = [{"role": "user", "content": "Co to jest neuron?"},
                 {"role": "assistant", "content": "Komórka nerwowa."}]
        result = bounded_chat_history(first, "A jak działa synapsa?")
        self.assertEqual([turn["role"] for turn in result],
                         ["user", "assistant", "user"])
        self.assertEqual(result[-1]["content"], "A jak działa synapsa?")

    def test_long_dialogue_discards_whole_oldest_pairs(self):
        turns = []
        for i in range(14):
            turns.extend((
                {"role": "user", "content": f"Pytanie {i} " + "x" * 750},
                {"role": "assistant", "content": f"Odpowiedź {i} " + "y" * 750},
            ))
        result = bounded_chat_history(turns, "Kontynuuj")
        self.assertLessEqual(sum(len(item["content"]) for item in result), 4500)
        self.assertLessEqual(len(result), 14)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[-1]["role"], "user")
        self.assertEqual(result[-1]["content"], "Kontynuuj")
        self.assertEqual(result, check_chat_messages(result))

    def test_latest_question_is_never_truncated(self):
        question = "Z" * 1800
        result = bounded_chat_history([
            {"role": "user", "content": "U" * 1800},
            {"role": "assistant", "content": "A" * 1800},
        ], question)
        self.assertEqual(result, [{"role": "user", "content": question}])
        with self.assertRaises(ValueError):
            bounded_chat_history([{"role": "assistant", "content": "X"}], "Cześć")


@unittest.skipUnless(os.name == "nt", "Real Tk acceptance runs on Windows CI")
class DefaultHomeMultiTurnTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        directory = Path(self.folder.name)
        memory = ExperienceMemory(directory / "memory.sqlite3")
        knowledge = LocalKnowledge(directory / "knowledge.sqlite3")
        supervisor = AutonomicSupervisor(memory)
        goals = GoalStore(directory / "goals.sqlite3")
        self.calls = []

        calls = self.calls
        class Model:
            def __init__(self, *args, **kwargs):
                pass

            def start(self):
                return None

            def stop(self):
                return None

            def chat(self, messages, **kwargs):
                calls.append([dict(m) for m in messages])
                return {"reply": f"Testowa odpowiedź {len(calls)}.",
                        "sources": [], "status": "offline_real_gguf_inference"}

            def classify_semantics(self, message):
                raise AssertionError("Semantic worker must not compete with immediate follow-up")

        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)
        patches = [
            patch("neurogenesis.tk_autonomous_home.BundledModelSession", Model),
            patch("neurogenesis.tk_autonomous_home.has_bundled_model", return_value=True),
        ]
        for item in patches:
            item.start()
            self.addCleanup(item.stop)
        self.view = install_autonomous_home(
            self.tabs, memory, knowledge, supervisor, goals, auto_start=False)
        self.tabs.select(self.view)
        elements = self._widgets(self.view)
        self.input = next(w for w in elements if isinstance(w, tk.Text)
                          and w.cget("background") == "#12374a")
        self.transcript = next(w for w in self._widgets(self.view)
                               if isinstance(w, tk.Text)
                               and w.cget("background") == "#061624")
        self.send = next(w for w in self._widgets(self.view)
                         if isinstance(w, ttk.Button)
                         and str(w.cget("text")).startswith("WYŚLIJ"))

    def _widgets(self, parent):
        items = [parent]
        for child in parent.winfo_children():
            items.extend(self._widgets(child))
        return items

    def _await_text(self, phrase, seconds=5):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.root.update()
            if phrase in self.transcript.get("1.0", "end-1c"):
                return
            time.sleep(0.01)
        self.fail(
            f"No model reply: {phrase}; calls={len(self.calls)}; "
            f"button={self.send.cget('state')}; "
            f"input={self.input.get('1.0', 'end-1c')!r}; "
            f"transcript={self.transcript.get('1.0', 'end-1c')[-900:]!r}")

    def test_two_sequential_questions_are_both_answered(self):
        self.input.insert("1.0", "Pierwsze pytanie?")
        self.send.invoke()
        self._await_text("Testowa odpowiedź 1.")
        self.assertEqual(str(self.send.cget("state")), "normal")
        self.input.insert("1.0", "A co dalej?")
        self.send.invoke()
        self._await_text("Testowa odpowiedź 2.")
        self.assertEqual(len(self.calls), 2)
        self.assertEqual([x["role"] for x in self.calls[1]],
                         ["user", "assistant", "user"])
        self.assertEqual(self.calls[1][-1]["content"], "A co dalej?")
        self.assertEqual(str(self.send.cget("state")), "normal")


if __name__ == "__main__":
    unittest.main()
