"""Offline regression for fair ACF-vs-nonneural retrieval ablation.

Synthetic neural state and canned completion responses are explicitly TEST
FIXTURES; never interpret these tests as proof of real model quality.
"""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from neurogenesis.acf import AdaptiveCognitiveFabric
from neurogenesis.acf_answer_router import (
    route_for_question, route_with_topic_control)
from neurogenesis.acf_semantic_memory import SemanticFabricStore
from neurogenesis.acf_semantics import AXES, VERSION
from neurogenesis.bundled_llm import BundledModelSession
from neurogenesis.dialogue_abcd import (
    FrozenLocalEvidence, _wilson, evaluate_abcd, paired_binary_compare)
from neurogenesis.dialogue_ab import ReadOnlyKnowledge
from neurogenesis.local_knowledge import LocalKnowledge


def tag(axis="programming"):
    return {
        "axes": [int(a == axis) for a in AXES],
        "version": VERSION,
        "model": "Qwen3-1.7B-Q4_K_M",
        "inference": "actual_local_gguf_semantic_classification",
        "cloud_api_used": False,
        "raw_text_persisted": False,
    }


class ABCCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.local = LocalKnowledge(self.root / "approved.sqlite3")
        fp = self.root / "programowanie.txt"
        fp.write_text(
            ("Programowanie Python algorytm neuronowy wykonuje instrukcje "
             "w funkcji testowej o nazwie BłękitnyNeuron. ") * 8,
            encoding="utf-8")
        self.local.import_txt(fp, approved=True)
        self.question = "Wyjaśnij algorytm neuronowy wykorzystany w Python"
        self.state = self.root / "semantic_fabric.acf.json"
        self.ledger = SemanticFabricStore(self.root)
        fabric = AdaptiveCognitiveFabric()
        for i in range(75):
            vector = [0.0] * 8
            vector[2 + (i % 3)] = 1.0
            fabric.observe(vector)
        # Synthetic *policy branch* scores, not evidence of learning.
        n = len(fabric.losses["adaptive"])
        for kind, mse in (("adaptive", .01), ("fixed", .09),
                          ("persistence", .10), ("constant_half", .22)):
            fabric.losses[kind] = [mse] * n
        fabric.selected_route = "adaptive"
        fabric.adaptive.next_forecast = [0.01, 0.01, 0.01, 0.96,
                                         0.01, 0.01, 0.01, 0.01]
        fabric.next_forecast = list(fabric.adaptive.next_forecast)
        fabric.last_event_id = fabric.events
        fabric.save(self.state)
        with closing(sqlite3.connect(self.ledger.path)) as con:
            with con:
                con.executemany(
                    "INSERT INTO observations(features,tagger,recorded_utc) "
                    "VALUES(?,?,?)",
                    [(json.dumps([0] * 8), VERSION, "synthetic-only")
                     for _ in range(fabric.events)])
        self.audit = self.root / "private.jsonl"
        tests = [
            {"question": self.question + " " + str(k),
             "expected_answer_fragment": "BłękitnyNeuron",
             "expected_source": "programowanie.txt"}
            for k in range(4)
        ]
        self.audit.write_text(
            "\n".join(json.dumps(q, ensure_ascii=False) for q in tests) + "\n",
            encoding="utf-8")

    def test_matched_control_and_acf_obey_same_retrieval_budget(self):
        classify = lambda _: tag()
        a, ameta = route_for_question(
            self.question, [], self.local, self.state, classify)
        b, bmeta = route_with_topic_control(
            self.question, [], self.local, classify)
        self.assertEqual(len(a), 1)
        self.assertEqual(a, b)
        self.assertEqual(ameta["status"], "acf_passage_added")
        self.assertEqual(bmeta["status"], "topic_control_passage_added")
        self.assertFalse(bmeta["neural_task_improvement_proven"])
        self.assertNotIn("BłękitnyNeuron", json.dumps(bmeta))

    def test_control_uses_question_if_neural_historical_topic_mismatches(self):
        control, cmeta = route_with_topic_control(
            self.question, [], self.local, lambda _: tag())
        neural, nmeta = route_for_question(
            self.question, [], self.local, self.state,
            lambda _: tag("engineering"))
        self.assertEqual(len(control), 1)
        self.assertEqual(neural, [])
        self.assertEqual(nmeta["status"], "predicted_topic_mismatch")
        self.assertEqual(cmeta["status"], "topic_control_passage_added")

    def test_strong_non_neural_multi_axis_tie_break_never_uses_acf(self):
        def classify(_):
            classified = tag("engineering")
            classified["axes"][AXES.index("programming")] = 1
            return classified
        with patch.object(self.local, "retrieve",
                          wraps=self.local.retrieve) as lookup:
            sources, report = route_with_topic_control(
                self.question, [], self.local, classify)
        self.assertEqual(report["predicted_axis"], "programming")
        self.assertEqual(len(sources), 1)
        self.assertEqual(lookup.call_count, 1)
        self.assertNotIn("acf", json.dumps(report).lower())

    def test_do_not_replace_better_existing_fourth_source(self):
        baseline = [
            {"text": "nawigacja", "file": "a", "sha256": str(i)}
            for i in range(3)
        ] + [{"text": self.question + " inne słowa",
              "file": "best.txt", "sha256": "best"}]
        a, meta = route_for_question(
            self.question, baseline, self.local, self.state, lambda _: tag())
        d, dmeta = route_with_topic_control(
            self.question, baseline, self.local, lambda _: tag())
        self.assertEqual(a, baseline)
        self.assertEqual(d, baseline)
        self.assertEqual(meta["added_approved_txt_passages"], 0)
        self.assertEqual(dmeta["added_approved_txt_passages"], 0)

    def test_invalid_current_classifier_stops_both_controls(self):
        bad = lambda _: {"axes": [True] * 8}
        self.assertEqual(
            route_with_topic_control(self.question, [], self.local, bad)[1]["status"],
            "invalid_current_semantics")
        self.assertEqual(
            route_for_question(self.question, [], self.local,
                               self.state, bad)[1]["status"],
            "invalid_current_semantics")

    def test_real_bundled_request_controls_not_default(self):
        session = BundledModelSession(knowledge=self.local)
        session._proc = MagicMock()
        session._proc.poll.return_value = None
        session._port = 40123
        payloads = []
        def response(_port, _key, _endpoint, *, payload, timeout):
            payloads.append(payload)
            if "response_format" in payload:
                return {"choices": [{"message": {"content":
                    json.dumps(dict(zip(AXES, tag()["axes"])))}}]}
            return {"choices": [{"message": {"content": "Testowa odpowiedź"}}]}
        with patch("neurogenesis.bundled_llm._http_request", side_effect=response):
            q = [{"role": "user", "content": self.question}]
            ordinary = session.chat(q)
            baseline = session.chat(q, deterministic=True, use_context=False)
            ctrl = session.chat(q, topic_control=True, deterministic=True)
            neural = session.chat(q, acf_state_path=self.state, deterministic=True)
        self.assertNotIn("acf_routing", ordinary)
        self.assertNotIn("topic_control_routing", ordinary)
        self.assertEqual(baseline["sources"], [])
        self.assertEqual(ctrl["topic_control_routing"]["status"],
                         "no_new_question_grounded_source")
        self.assertIn("acf_routing", neural)
        self.assertEqual(sum("response_format" in p for p in payloads), 2)
        with self.assertRaises(ValueError):
            session.chat(q, topic_control=True, use_context=False)
        with self.assertRaises(ValueError):
            session.chat(q, topic_control=True, acf_state_path=self.state)
        with self.assertRaises(ValueError):
            session.chat(q, topic_control="yes")

    def test_frozen_snapshot_and_sqlite_external_change_guards(self):
        frozen = ReadOnlyKnowledge(self.local.db_path)
        with FrozenLocalEvidence(self.state, frozen) as guard:
            guard.verify()
            with closing(sqlite3.connect(self.local.db_path)) as con:
                with con:
                    con.execute("UPDATE local_sources SET display_name=?",
                                ("changed.txt",))
            with self.assertRaisesRegex(ValueError, "SQLite changed"):
                guard.verify()
        # separate check of ACF digest, with unchanged source/ledger DB
        with FrozenLocalEvidence(self.state, frozen) as guard:
            original = self.state.read_bytes()
            self.state.write_bytes(original + b"\n")
            with self.assertRaisesRegex(ValueError, "ACF checkpoint changed"):
                guard.verify()

    def test_4_arm_private_aggregates_and_cleanup(self):
        before = (
            self.local.db_path.read_bytes(),
            self.ledger.path.read_bytes(),
            self.state.read_bytes())
        instances = []
        class Fake:
            def __init__(self, k):
                self.k, self.calls, self.stopped = k, [], False
            def start(self):
                pass
            def stop(self):
                self.stopped = True
            def chat(self, messages, *, use_context=True, deterministic=False,
                     acf_state_path=None, topic_control=False):
                self.calls.append((acf_state_path is not None,
                                   topic_control, deterministic))
                question = messages[-1]["content"]
                sources = self.k.retrieve(question) if use_context else []
                result = {}
                if acf_state_path is not None:
                    sources, meta = route_for_question(
                        question, sources, self.k, acf_state_path,
                        lambda _: tag())
                    result["acf_routing"] = meta
                if topic_control:
                    sources, meta = route_with_topic_control(
                        question, sources, self.k, lambda _: tag())
                    result["topic_control_routing"] = meta
                result["reply"] = ("BłękitnyNeuron" if sources else "bez danych")
                result["sources"] = [
                    {"label": "L" + str(i+1),
                     "file": s["file"], "sha256": s["sha256"]}
                    for i, s in enumerate(sources)]
                return result
        def make(k):
            s = Fake(k)
            instances.append(s)
            return s
        r = evaluate_abcd(
            self.local.db_path, self.audit, self.state,
            confirm_rights=True, confirm_holdout=True, session_factory=make)
        self.assertEqual(r["audited_cases"], 4)
        self.assertEqual(sum(r["paired_outcomes_abcd_bits"].values()), 4)
        self.assertEqual(sum(r["acf_routing_status_counts"].values()), 4)
        self.assertEqual(sum(r["topic_control_status_counts"].values()), 4)
        self.assertTrue(instances[0].stopped)
        self.assertEqual(len(instances[0].calls), 16)
        self.assertTrue(all(c[2] for c in instances[0].calls))
        self.assertEqual(r["actual_gguf_inference"], False)
        self.assertFalse(r["neural_growth_causally_proven"])
        self.assertEqual(self.local.db_path.read_bytes(), before[0])
        self.assertEqual(self.ledger.path.read_bytes(), before[1])
        self.assertEqual(self.state.read_bytes(), before[2])
        report = json.dumps(r, ensure_ascii=False)
        self.assertNotIn(self.question, report)
        self.assertNotIn("BłękitnyNeuron", report)
        self.assertNotIn("programowanie.txt", report)

    def test_stop_on_model_failure(self):
        created = []
        class Broken:
            def start(self): pass
            def stop(self): self.stopped = True
            def chat(self, *args, **kwargs): raise RuntimeError("synthetic")
        def factory(_):
            b=Broken()
            created.append(b)
            return b
        with self.assertRaises(RuntimeError):
            evaluate_abcd(
                self.local.db_path, self.audit, self.state,
                confirm_rights=True, confirm_holdout=True,
                session_factory=factory)
        self.assertTrue(created[0].stopped)

    def test_holdout_needs_consent(self):
        with self.assertRaises(PermissionError):
            evaluate_abcd(self.local.db_path, self.audit, self.state)


class StatisticsTests(unittest.TestCase):
    def test_exact_binary_comparison_zero_regression_and_one_sided_gain(self):
        equal = [{"c": True, "d": True}] * 3
        score = paired_binary_compare(equal, left="c", right="d")
        self.assertEqual(score["exploratory_two_sided_exact_p"], 1.0)
        self.assertEqual(score["discordant_pairs"], 0)
        assert paired_binary_compare([{"c": True, "d": False}] * 6,
                                     left="c", right="d")[
                                         "exploratory_two_sided_exact_p"] == 0.03125
        regression = paired_binary_compare(
            [{"c": False, "d": True}] * 4,
            left="c", right="d")
        self.assertEqual(regression["literal_rate_difference"], -1.0)
        self.assertEqual(regression["left_only_correct"], 0)
        self.assertEqual(_wilson(0, 4)[0], 0.0)
        self.assertEqual(_wilson(4, 4)[1], 1.0)

    def test_invalid_binary_inference_prevented(self):
        with self.assertRaises(ValueError):
            paired_binary_compare([{"c": 1, "d": 0}], left="c", right="d")
        with self.assertRaises(ValueError):
            _wilson(5, 4)


if __name__ == "__main__":
    unittest.main()
