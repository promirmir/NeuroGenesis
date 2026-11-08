"""Pure autonomy-policy regression and source-control contracts.

The real visual/polling/UI tasks are covered by Windows --ui-self-test and
the on-screen QA screenshots. These tests never crawl the Internet.
"""
from __future__ import annotations

import unittest

from neurogenesis.study_panel import research_autopilot_allowed


class AutonomyPolicyTests(unittest.TestCase):
    def eligible(self, **overrides):
        args = {
            "enabled": True, "consent": True, "topic": "Fotowoltaika",
            "active": False, "cycles": 0, "last_finished": None,
            "now": 10000.0,
        }
        args.update(overrides)
        return research_autopilot_allowed(**args)

    def test_study_only_starts_with_operator_opt_in_and_https_consent(self):
        self.assertTrue(self.eligible())
        self.assertFalse(self.eligible(enabled=False))
        self.assertFalse(self.eligible(consent=False))
        self.assertFalse(self.eligible(active=True))
        self.assertFalse(self.eligible(topic=""))
        self.assertFalse(self.eligible(topic="X"))
        self.assertFalse(self.eligible(topic="X" * 121))

    def test_no_runaway_crawler_finite_cycles_and_real_cooldown(self):
        self.assertTrue(self.eligible(cycles=2))
        self.assertFalse(self.eligible(cycles=3))
        self.assertFalse(self.eligible(cycles=100))
        self.assertFalse(self.eligible(cycles=-1))
        self.assertFalse(self.eligible(last_finished=9999.0))
        self.assertFalse(self.eligible(last_finished=8201.0))
        self.assertTrue(self.eligible(last_finished=8200.0))
        self.assertFalse(self.eligible(limit=999))
        self.assertFalse(self.eligible(cooldown=0))

    def test_no_type_coercion_into_authorization(self):
        for override in ({"enabled": 1}, {"consent": "yes"},
                         {"cycles": True}, {"active": 0},
                         {"now": "10000"}):
            with self.subTest(override=override):
                with self.assertRaises(ValueError):
                    self.eligible(**override)


class WebResearchDialogueTests(unittest.TestCase):
    """Mock only the HTTP runtime; real model generation has a separate
    mandatory 1.1GB Windows FULL release gate.
    """

    def test_approved_web_sources_reach_real_model_prompt_with_provenance(self):
        from unittest.mock import patch
        from neurogenesis.bundled_llm import BundledModelSession

        class FakeProcess:
            def poll(self):
                return None

        class FakeKnowledge:
            def retrieve(self, query):
                return [{"text": "Lokalne dane obserwacyjne.",
                         "file": "notatka.txt", "sha256": "a" * 64}]

        class FakeWebMemory:
            def answer_from_knowledge(self, question):
                self.query = question
                return {
                    "answer": "Zapisany cytat z zatwierdzonego HTTPS. Źródło: https://example.org/raport",
                    "sources": [{"url": "https://example.org/raport",
                                 "sha256": "b" * 64}],
                }

        fake_web = FakeWebMemory()
        session = BundledModelSession(knowledge=FakeKnowledge(),
                                       web_memory=fake_web)
        session._proc = FakeProcess()
        session._port = 12345
        seen = {}

        def fake_http(port, key, endpoint, *, payload=None, timeout=0):
            seen.update({"endpoint": endpoint, "payload": payload})
            return {"choices": [{"message": {"content": "Wniosek z danych."}}]}

        with patch("neurogenesis.bundled_llm._http_request",
                   side_effect=fake_http):
            result = session.chat([
                {"role": "user", "content": "Co zapisano w raporcie?"}
            ])
        self.assertEqual(result["status"], "offline_real_gguf_inference")
        self.assertEqual(fake_web.query, "Co zapisano w raporcie?")
        self.assertEqual(len(result["sources"]), 2)
        self.assertEqual(seen["endpoint"], "/v1/chat/completions")
        prompt = str(seen["payload"]["messages"][-1]["content"])
        self.assertIn("notatka.txt", prompt)
        self.assertIn("example.org/raport", prompt)
        self.assertFalse(result["cloud_api_used"])


if __name__ == "__main__":
    unittest.main()
