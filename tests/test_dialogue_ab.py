"""No-model regression for controlled real-Qwen trial harness and its privacy."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from neurogenesis.bundled_llm import BundledModelSession
from neurogenesis.dialogue_ab import ReadOnlyKnowledge, evaluate, load_audit
from neurogenesis.local_knowledge import LocalKnowledge


class FakeSession:
    def __init__(self, knowledge):
        self.knowledge = knowledge
        self.started = False
        self.stopped = False
        self.calls = []

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def chat(self, messages, *, use_context=True, deterministic=False):
        self.calls.append((messages, use_context, deterministic))
        question = messages[-1]["content"]
        snippets = self.knowledge.retrieve(question) if use_context else []
        if not snippets:
            return {"reply": "Nie znam danych.", "sources": []}
        # Deterministic double for harness only: not presented as real inference.
        snippet = snippets[0]
        answer = "Rzeczywista pamięć: " + snippet["text"][:170] + " [L1]"
        return {"reply": answer, "sources": [
            {"label": "L1", "file": snippet["file"], "sha256": snippet["sha256"]}]}


class DialogueABTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.db = self.root / "local.sqlite3"
        local = LocalKnowledge(self.db)
        self.cases = []
        for index, topic in enumerate(
                ("neutron", "kwantowe", "matematyka", "robotyka"), 1):
            path = self.root / (topic + ".txt")
            phrase = "wiadomoscprobna" + str(index)
            path.write_text(
                (topic + " " + phrase + " opis danych testowych. ") * 9,
                encoding="utf-8")
            local.import_txt(path, approved=True)
            self.cases.append({
                "question": "Jakie dane zawiera dokument o " + topic + "?",
                "expected_answer_fragment": phrase,
                "expected_source": path.name})
        self.audit = self.root / "private.jsonl"
        self.audit.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False)
                      for row in self.cases) + "\n", encoding="utf-8")

    def test_paired_positive_and_source_hits_private_report(self):
        instances = []
        def factory(k):
            instance = FakeSession(k)
            instances.append(instance)
            return instance
        before = self.db.read_bytes()
        report = evaluate(
            self.db, self.audit, confirm_rights=True, confirm_holdout=True,
            session_factory=factory)
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(report["case_count"], 4)
        self.assertFalse(report["actual_gguf_inference"])
        self.assertEqual(report["paired_outcomes"]["rag_only_correct"], 4)
        self.assertEqual(report["conditions"]["qwen_only"]["literal_answer_hits"], 0)
        self.assertEqual(report["conditions"]["qwen_plus_approved_txt"]["literal_answer_hits"], 4)
        self.assertEqual(report["conditions"]["qwen_plus_approved_txt"]["expected_source_hits"], 4)
        self.assertEqual(report["measured_literal_answer_rate_delta_rag_minus_base"], 1.0)
        self.assertFalse(report["acf_influenced_answers"])
        self.assertFalse(report["independently_verified_truth"])
        self.assertTrue(instances[0].started and instances[0].stopped)
        self.assertTrue(all(call[2] for call in instances[0].calls))
        self.assertEqual([call[1] for call in instances[0].calls], [
            False, True, True, False, False, True, True, False])
        dumped = json.dumps(report)
        self.assertNotIn(self.cases[0]["question"], dumped)
        self.assertNotIn(self.cases[0]["expected_answer_fragment"], dumped)
        self.assertNotIn(self.cases[0]["expected_source"], dumped)

    def test_explicit_consent_and_malformed_cases(self):
        with self.assertRaises(PermissionError):
            evaluate(self.db, self.audit, session_factory=FakeSession)
        self.cases[1]["question"] = self.cases[0]["question"]
        self.audit.write_text("\n".join(json.dumps(x) for x in self.cases))
        with self.assertRaises(ValueError):
            load_audit(self.audit)
        self.audit.write_text('{"question":"x","expected_answer_fragment":"xy"}\n')
        with self.assertRaises(ValueError):
            load_audit(self.audit)

    def test_missing_db_rejected_and_no_database_created(self):
        missing = self.root / "not-created.sqlite3"
        with self.assertRaises(ValueError):
            ReadOnlyKnowledge(missing)
        self.assertFalse(missing.exists())

    def test_stop_on_model_error_does_not_publish_private_questions(self):
        class Fails(FakeSession):
            def chat(self, messages, **kwargs):
                raise RuntimeError("synthetic model failure")
        sessions = []
        def make(k):
            result = Fails(k)
            sessions.append(result)
            return result
        with self.assertRaises(RuntimeError):
            evaluate(self.db, self.audit, confirm_rights=True,
                     confirm_holdout=True, session_factory=make)
        self.assertTrue(sessions[0].stopped)

    def test_invalid_source_citations_counted_as_invalid_not_verified(self):
        class Hallucinates(FakeSession):
            def chat(self, messages, *, use_context=True, deterministic=False):
                value = super().chat(
                    messages, use_context=use_context, deterministic=deterministic)
                value["reply"] += " [L9]"
                return value
        result = evaluate(
            self.db, self.audit, confirm_rights=True, confirm_holdout=True,
            session_factory=Hallucinates)
        for condition in result["conditions"].values():
            self.assertEqual(condition["unsupported_citations"], 4)


class BundledControlsTest(unittest.TestCase):
    def test_no_retrieval_and_no_sampling_controls_do_not_change_default(self):
        local = MagicMock()
        local.retrieve.return_value = [{
            "text": "example trusted retrieval", "file": "test.txt", "sha256": "a" * 64}]
        web = MagicMock()
        web.answer_from_knowledge.return_value = None
        session = BundledModelSession(knowledge=local, web_memory=web)
        session._proc = MagicMock()
        session._proc.poll.return_value = None
        session._port = 4444
        request_payloads = []
        def fake_request(_port, _key, _endpoint, *, payload, timeout):
            request_payloads.append(payload)
            return {"choices": [{"message": {"content": "Model reply"}}]}
        question = [{"role": "user", "content": "Jaki jest test?"}]
        with patch("neurogenesis.bundled_llm._http_request", side_effect=fake_request):
            control = session.chat(question, use_context=False, deterministic=True)
            self.assertEqual(control["sources"], [])
            local.retrieve.assert_not_called()
            web.answer_from_knowledge.assert_not_called()
            standard = session.chat(question)
        self.assertEqual(len(standard["sources"]), 1)
        self.assertEqual(request_payloads[0]["temperature"], 0.0)
        self.assertEqual(request_payloads[0]["top_k"], 1)
        self.assertEqual(request_payloads[1]["temperature"], 0.7)
        self.assertEqual(request_payloads[1]["top_k"], 20)
        local.retrieve.assert_called_once()
        with self.assertRaises(ValueError):
            session.chat(question, deterministic="yes")


if __name__ == "__main__":
    unittest.main()
