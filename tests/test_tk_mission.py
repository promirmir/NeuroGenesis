"""Validate the GUI that is ACTUALLY shipped in the default Windows EXE.

Unlike the optional Qt tests, these use real Tk widgets on the Windows runner,
real private SQLite files, real saved LIF spikes and no network permission.
"""
from __future__ import annotations

from pathlib import Path
import os
import tempfile
import tkinter as tk
import unittest

from neurogenesis.desktop import process_message
from neurogenesis.memory import ExperienceMemory
from neurogenesis.tk_mission import MissionDashboard


@unittest.skipUnless(os.name == "nt", "Real Tk GUI acceptance runs on Windows CI")
class DefaultWindowsMissionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.memory = ExperienceMemory(Path(self.folder.name) / "memory.sqlite3")
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.tab = tk.Frame(self.root)
        self.tab.pack(fill="both", expand=True)
        self.visited: list[str] = []
        self.permission = False
        self.view = MissionDashboard(
            self.tab, self.memory,
            navigate=self.visited.append,
            network_enabled=lambda: self.permission)
        self.root.update_idletasks()

    def test_default_dashboard_uses_real_persisted_local_state(self):
        before = self.memory.brain()
        self.assertFalse(self.view.refresh())
        self.assertEqual(self.view.metrics["steps"].get(), str(before.steps))
        self.assertEqual(self.view.metrics["neurons"].get(), str(len(before.voltages)))
        self.assertEqual(self.view.metrics["synapses"].get(), str(len(before.synapses)))
        self.assertEqual(self.view.metrics["documents"].get(), "0")
        self.assertEqual(self.view.modules["network"].get(), "WYŁĄCZONY")
        self.assertEqual(self.view._last.total_synapses, len(before.synapses))
        first_samples = tuple(self.view._samples)
        first_events = self.view.events.get("1.0", "end-1c")
        for _ in range(3):
            self.assertFalse(self.view.refresh())
        self.assertEqual(tuple(self.view._samples), first_samples)
        self.assertEqual(self.view.events.get("1.0", "end-1c"), first_events)
        self.assertFalse(self.permission)

        result = process_message(self.memory, "Próbny bodziec podglądu")
        self.assertTrue(self.view.refresh())
        latest = self.memory.brain()
        self.assertEqual(self.view._last.step, latest.steps)
        self.assertEqual(self.view._last.total_spikes, latest.total_spikes)
        self.assertEqual(self.view.graph._latest.step, result["brain_step"])
        self.assertEqual(self.view._samples[-1][0], latest.steps)
        self.assertIn("LIF / KROK", self.view.events.get("1.0", "end-1c"))
        self.assertFalse(self.view.refresh())

        reopened = ExperienceMemory(self.memory.path)
        self.assertEqual(reopened.brain().steps, latest.steps)
        self.assertEqual(reopened.status()["observations"], 1)

    def test_dashboard_controls_and_https_indicator_are_real(self):
        self.view.refresh()
        self.assertEqual(self.visited, [])
        self.permission = True
        self.view.refresh()
        self.assertEqual(self.view.modules["network"].get(), "ZEZWOLONO")
        self.permission = False
        self.view.refresh()
        self.assertEqual(self.view.modules["network"].get(), "WYŁĄCZONY")
        # Navigation uses the very same real existing tabs, not fake buttons.
        self.view.navigate("chat")
        self.view.navigate("brain")
        self.view.navigate("web")
        self.assertEqual(self.visited, ["chat", "brain", "web"])
        self.assertTrue(self.root.winfo_exists())
        self.assertFalse(self.permission)


if __name__ == "__main__":
    unittest.main()
