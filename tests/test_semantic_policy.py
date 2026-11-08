"""Safety and causal learning tests of real semantic ACF decision gate.

Tests that synthetically edit the MSE windows are POLICY UNIT FIXTURES,
not evidence that trained plastic neurons outperform fixed controls.
The benchmark reads only real (or explicitly synthetic test) semantic tags.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from neurogenesis.acf import AdaptiveCognitiveFabric, ROUTES
from neurogenesis.acf_semantic_memory import SemanticFabricStore
from neurogenesis.acf_semantics import AXES, VERSION
from neurogenesis.local_knowledge import LocalKnowledge
from neurogenesis.semantic_policy import (
    MIN_EVENTS, QUERIES, decide, prepare_local_sources)
from neurogenesis.semantic_policy_benchmark import (
    evaluate, read_private_semantics)


def informed_fixture():
    f = AdaptiveCognitiveFabric()
    for step in range(MIN_EVENTS + 8):
        x = [0.0] * 8
        x[step % 3 + 2] = 1.0
        f.observe(x)
    n = len(f.losses["adaptive"])
    # This deliberately constructs a *controlled unit fixture* to exercise
    # the decision gate; NEVER report the resulting scores as model results.
    f.losses["adaptive"] = [0.01] * n
    f.losses["fixed"] = [0.09] * n
    f.losses["persistence"] = [0.10] * n
    f.losses["constant_half"] = [0.22] * n
    f.selected_route = "adaptive"
    f.adaptive.next_forecast = [0.01, 0.01, 0.01, 0.96,
                                0.01, 0.01, 0.01, 0.01]
    f.next_forecast = list(f.adaptive.next_forecast)
    return f


class DecisionGateTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.knowledge = LocalKnowledge(self.root / "approved_knowledge.sqlite3")

    def test_no_new_data_no_decision_and_no_database_lookup(self):
        f = AdaptiveCognitiveFabric()
        with patch.object(self.knowledge, "retrieve",
                          side_effect=AssertionError("Must not read")):
            d = prepare_local_sources(f, self.knowledge)
        self.assertEqual(d.status, "insufficient_real_observations")
        self.assertEqual(d.local_sources_consulted, 0)
        self.assertFalse(d.public()["improves_user_tasks_proven"])

    def test_no_advantage_must_abstain_even_if_prediction_high(self):
        f = informed_fixture()
        f.losses["adaptive"] = [0.11] * len(f.losses["adaptive"])
        self.assertEqual(decide(f).status, "adaptive_not_selected_by_actual_loss"
                         if f.selected_route != "adaptive"
                         else "no_measured_adaptive_advantage")
        with patch.object(self.knowledge, "retrieve",
                          side_effect=AssertionError("Must not prefetch")):
            d = prepare_local_sources(f, self.knowledge)
        self.assertEqual(d.local_sources_consulted, 0)

    def test_fixed_or_neural_ambiguity_prevents_prefetch(self):
        f = informed_fixture()
        f.selected_route = "fixed"
        self.assertEqual(decide(f).status, "adaptive_not_selected_by_actual_loss")
        f.selected_route = "adaptive"
        f.adaptive.next_forecast = [0.4, 0.3, 0.1, 0.2,
                                    0., 0., 0., 0.]
        f.next_forecast = list(f.adaptive.next_forecast)
        self.assertEqual(decide(f).status, "low_confidence_or_unsuitable_topic")
        f.adaptive.next_forecast = [0.90, 0.04, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
        f.next_forecast = list(f.adaptive.next_forecast)
        self.assertEqual(decide(f).status, "low_confidence_or_unsuitable_topic")
        # No automatic speculative prefetch for general facts or small talk.

    def test_real_local_read_only_action_with_gated_winner(self):
        path = self.root / "approved_programming.txt"
        path.write_text(
            "Programowanie w Pythonie. Kod źródłowy projektów, "
            "funkcje, testy i kontrola jakości oprogramowania. " * 6,
            encoding="utf-8")
        self.knowledge.import_txt(path, approved=True)
        before = self.knowledge.status()
        f = informed_fixture()
        self.assertEqual(decide(f).predicted_axis, "programming")
        with patch.object(self.knowledge, "retrieve",
                          wraps=self.knowledge.retrieve) as retrieval:
            d = prepare_local_sources(f, self.knowledge)
        self.assertEqual(retrieval.call_count, 1)
        self.assertEqual(retrieval.call_args.kwargs["limit"], 3)
        self.assertEqual(retrieval.call_args.args[0], QUERIES["programming"])
        self.assertEqual(d.status, "local_sources_prepared")
        self.assertGreater(d.local_sources_consulted, 0)
        self.assertEqual(self.knowledge.status(), before)
        shown = d.public()
        self.assertNotIn("text", shown)
        self.assertNotIn("file", shown)
        self.assertNotIn("url", shown)
        self.assertNotIn("private", json.dumps(shown).lower())
        self.assertFalse(shown["improves_user_tasks_proven"])

    def test_missing_source_is_not_misrepresented_as_knowledge(self):
        f = informed_fixture()
        d = prepare_local_sources(f, self.knowledge)
        self.assertEqual(d.status, "approved_sources_missing")
        self.assertEqual(d.local_sources_consulted, 0)

    def test_persisted_real_acf_state_drives_same_pure_policy(self):
        f = informed_fixture()
        store = SemanticFabricStore(self.root)
        f.save(store.state_path)
        before = store.state_path.read_bytes()
        with patch.object(self.knowledge, "retrieve", return_value=[]):
            result = store.prepare_next_topic(self.knowledge)
        self.assertEqual(result["status"], "approved_sources_missing")
        self.assertEqual(result["predicted_axis"], "programming")
        self.assertEqual(store.state_path.read_bytes(), before)

    def test_invalid_mse_or_forecast_never_drives_action(self):
        f = informed_fixture()
        f.losses["fixed"] = [0.0] * len(f.losses["fixed"])
        self.assertEqual(decide(f).status, "no_measured_adaptive_advantage")
        f = informed_fixture()
        f.next_forecast[3] = float("nan")
        with self.assertRaises(ValueError):
            decide(f)


class PolicyBenchmarkTests(unittest.TestCase):
    def test_causal_prequential_audit_reports_abstentions_without_fake_gains(self):
        samples = []
        for i in range(90):
            x = [0.0] * 8
            x[3 if i % 5 != 0 else 2] = 1.0
            samples.append(x)
        a = evaluate(samples)
        b = evaluate(samples)
        self.assertEqual(a, b)
        self.assertEqual(a["observation_count"], 90)
        self.assertEqual(a["prefetch_decisions"] + a["abstentions"], 90)
        self.assertEqual(a["user_task_improvement_proven"], False)
        self.assertEqual(a["selection_bias_eliminated"], False)
        if a["prefetch_decisions"] == 0:
            self.assertIsNone(a["next_topic_hit_rate_on_selected_events"])
            self.assertIsNone(a["measured_relative_hit_rate_advantage"])

    def test_only_real_pinned_semantic_ledger_fields_are_read(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SemanticFabricStore(Path(directory))
            annotation = {"axes": [0., 0., 0., 1., 0., 0., 0., 0.],
                          "version": VERSION,
                          "model": "Qwen3-1.7B-Q4_K_M",
                          "inference": "actual_local_gguf_semantic_classification",
                          "cloud_api_used": False,
                          "raw_text_persisted": False}
            for _ in range(3):
                store.learn(annotation)
            input_tags = read_private_semantics(store.path)
            self.assertEqual(len(input_tags), 3)
            self.assertEqual(input_tags[0][AXES.index("programming")], 1)
            r = evaluate(input_tags)
            self.assertEqual(r["observation_count"], 3)
            self.assertFalse(r["user_task_improvement_proven"])
            with self.assertRaises(ValueError):
                read_private_semantics(store.path, limit=0)

    def test_malformed_synthetic_stream_rejected(self):
        for data in ([[True] * 8], [[0.5] * 8], [[1] * 7],
                     [[float("nan")] * 8]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                evaluate(data)


if __name__ == "__main__":
    unittest.main()
