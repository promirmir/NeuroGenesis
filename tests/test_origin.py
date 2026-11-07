"""Continuity, explicit attribution and non-regression of saved state."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from neurogenesis import Brain
from neurogenesis.origin import origin_record, validate_origin
from neurogenesis.self_model import inspect


class ProvenanceTests(unittest.TestCase):
    def test_creator_and_ai_contribution_are_explicit(self):
        record = origin_record()
        self.assertEqual(record["human_initiator"]["github"], "promirmir")
        self.assertEqual(record["human_initiator"]["name"], "Miron")
        self.assertEqual(record["credit"], "Miron przy pomocy AI")
        self.assertEqual(record["ai_collaboration"]["name"], "AI")
        self.assertIn("without evidence", record["appreciation"])
        self.assertIn("authorized", record["relationship"])
        self.assertEqual(inspect(Brain())["origin"], record)
        self.assertFalse(inspect(Brain())["capabilities"]["authenticated_operator_controls"])

    def test_provenance_is_defensively_copied(self):
        changed = origin_record()
        changed["human_initiator"]["name"] = "intruder"
        self.assertEqual(origin_record()["human_initiator"]["name"], "Miron")
        with self.assertRaises(ValueError):
            validate_origin(changed)

    def test_snapshots_include_origin_and_reject_tampering(self):
        brain = Brain()
        brain.step([1.0] + [0.0] * 7)
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "state.json"
            brain.save(file)
            loaded = Brain.load(file)
            self.assertEqual(loaded.to_dict(), brain.to_dict())
            data = json.loads(file.read_text(encoding="utf-8"))
            data["origin"]["human_initiator"]["github"] = "spoofed"
            file.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "origin"):
                Brain.load(file)

    def test_prior_v02_snapshot_loads_without_regression(self):
        state = Brain().to_dict()
        state.pop("origin")  # Old v0.2 format
        loaded = Brain.from_dict(deepcopy(state))
        self.assertEqual(loaded.stats(), Brain().stats())
        self.assertIn("origin", loaded.to_dict())  # Upgraded at next save

    def test_prior_v02_predictor_snapshot_loads(self):
        from neurogenesis.predictor import NextInputPredictor
        original = NextInputPredictor()
        for index in range(12):
            stimulus = [0.0] * 8
            stimulus[index % 8] = 1.0
            original.step(stimulus)
        legacy = original.to_dict()
        legacy["brain"].pop("origin")  # Original v0.2 nested snapshot
        restored = NextInputPredictor.from_dict(legacy)
        self.assertEqual(restored.to_dict(), original.to_dict())
        for index in range(12, 20):
            stimulus = [0.0] * 8
            stimulus[index % 8] = 1.0
            self.assertEqual(restored.step(stimulus), original.step(stimulus))


    def test_old_attribution_migrates_without_exporting_old_identity(self):
        from neurogenesis.origin import _LEGACY_WITHOUT_NAME
        legacy = deepcopy(_LEGACY_WITHOUT_NAME)
        legacy["human_initiator"]["name"] = "Miron " + "Example"  # synthetic test string
        state = Brain().to_dict()
        state["origin"] = legacy
        recovered = Brain.from_dict(state)
        self.assertEqual(recovered.to_dict()["origin"], origin_record())
        self.assertNotIn("Example", json.dumps(recovered.to_dict()))

    def test_incorrect_legacy_origin_still_rejected(self):
        from neurogenesis.origin import _LEGACY_WITHOUT_NAME
        legacy = deepcopy(_LEGACY_WITHOUT_NAME)
        legacy["human_initiator"]["name"] = "Miron " + "Example"
        legacy["project"] = "Other"
        with self.assertRaisesRegex(ValueError, "origin"):
            validate_origin(legacy)

    def test_origin_cli_is_stable_machine_readable_json(self):
        output = subprocess.check_output([sys.executable, "-m", "neurogenesis", "origin"], text=True)
        self.assertEqual(json.loads(output), origin_record())

    def test_existing_learning_controls_still_work(self):
        from neurogenesis.experiment import compare_growth
        from neurogenesis.predictor import prediction_control
        structural = compare_growth(steps=128)
        self.assertEqual(structural["fixed_structure"]["neurons"], 24)
        self.assertEqual(structural["growth_enabled"]["neurons"], 28)
        prediction = prediction_control(steps=600)
        for variant in ("growth_enabled", "fixed_structure"):
            results = prediction["evaluation"][variant]
            self.assertLess(results["last_window_mse"], results["first_window_mse"])


if __name__ == "__main__":
    unittest.main()
