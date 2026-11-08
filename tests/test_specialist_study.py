"""Offline specialist-study safety and persistence contract tests."""
import unittest
from unittest.mock import Mock
from types import SimpleNamespace

from neurogenesis.web_discovery import RobotsPolicy

from neurogenesis.specialist_study import SpecialistStudy, plan_topic


class SpecialistStudyTests(unittest.TestCase):
    def test_plan_is_bounded_and_public(self):
        urls = plan_topic("silniki spalinowe", max_pages=3)
        self.assertEqual(len(urls), 3)
        self.assertTrue(all(u.startswith("https://pl.wikipedia.org/wiki/") for u in urls))

    def test_rejects_invalid_topics_and_limits(self):
        for topic in ("", "x" * 101, "https://evil.example", "test?token=secret"):
            with self.subTest(topic=topic):
                with self.assertRaises(ValueError):
                    plan_topic(topic)
        with self.assertRaises(ValueError):
            plan_topic("mechanika", max_pages=1000)

    def test_no_network_without_consent(self):
        fetch, observe = Mock(), Mock()
        study = SpecialistStudy("mechanika", observe, fetch=fetch)
        with self.assertRaises(PermissionError):
            study.run()
        fetch.assert_not_called()
        observe.assert_not_called()

    def test_observations_forwarded_without_raw_storage(self):
        fetch, observe = Mock(return_value=object()), Mock()
        study = SpecialistStudy("mechanika", observe, fetch=fetch, max_pages=1,
                                robots=RobotsPolicy(fetch=lambda host: ""))
        result = study.run(consent=True)
        self.assertEqual(result.accepted, 1)
        self.assertEqual(result.attempted, 1)
        observe.assert_called_once()

    def test_stop_before_start(self):
        fetch = Mock()
        study = SpecialistStudy("mechanika", Mock(), fetch=fetch)
        study.stop()
        result = study.run(consent=True)
        self.assertTrue(result.stopped)
        self.assertEqual(result.attempted, 0)
        fetch.assert_not_called()

    def test_failed_source_does_not_block_progress(self):
        study = SpecialistStudy("mechanika", Mock(), max_pages=1,
                                fetch=Mock(side_effect=ValueError("bad")),
                                robots=RobotsPolicy(fetch=lambda host: ""))
        result = study.run(consent=True)
        self.assertEqual(result.errors, 1)
        self.assertEqual(result.accepted, 0)


    def test_cross_domain_relevant_links_are_followed(self):
        observed = []
        def fetch(url):
            observed.append(url)
            if "pl.wikipedia.org" in url:
                return SimpleNamespace(links=(
                    "https://example.org/mechanika/poradnik",
                    "https://example.org/ogrodnictwo",
                    "https://127.0.0.1/mechanika",
                    "https://example.org/?token=secret"))
            return SimpleNamespace(links=())
        study = SpecialistStudy("mechanika", Mock(), max_pages=3, fetch=fetch,
                                robots=RobotsPolicy(fetch=lambda host: ""),
                                max_domains=3)
        study._stop.wait = lambda duration: False  # no real sleep in offline test
        result = study.run(consent=True)
        self.assertEqual(result.accepted, 3)
        self.assertEqual(result.domains, 3)
        self.assertEqual(result.attempted, 3)
        self.assertTrue(any("example.org/mechanika" in x for x in observed))
        self.assertFalse(any("127.0.0.1" in x or "token" in x for x in observed))

    def test_robots_denial_never_fetches_page(self):
        fetch = Mock()
        policy = RobotsPolicy(fetch=lambda host:
                              "User-agent: NeuroGenesisResearchBot\nDisallow: /\n")
        study = SpecialistStudy("mechanika", Mock(), max_pages=1,
                                fetch=fetch, robots=policy)
        result = study.run(consent=True)
        self.assertEqual(result.accepted, 0)
        self.assertEqual(result.errors, 1)
        fetch.assert_not_called()

    def test_robots_read_failure_is_fail_closed(self):
        fetch = Mock()
        policy = RobotsPolicy(fetch=lambda host: (_ for _ in ()).throw(OSError("offline")))
        study = SpecialistStudy("mechanika", Mock(), max_pages=1,
                                fetch=fetch, robots=policy)
        self.assertEqual(study.run(consent=True).errors, 1)
        fetch.assert_not_called()

    def test_domain_budget_blocks_cross_site_hops(self):
        def fetch(url):
            return SimpleNamespace(links=("https://example.org/mechanika/info",))
        study = SpecialistStudy("mechanika", Mock(), max_pages=3,
                                max_domains=1, fetch=fetch,
                                robots=RobotsPolicy(fetch=lambda host: ""))
        study._stop.wait = lambda duration: False
        result = study.run(consent=True)
        self.assertEqual(result.domains, 1)
        self.assertEqual(result.accepted, 1)

if __name__ == "__main__":
    unittest.main()
