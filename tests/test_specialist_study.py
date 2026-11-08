"""Offline specialist-study safety and persistence contract tests."""
import unittest
from unittest.mock import Mock

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
        study = SpecialistStudy("mechanika", observe, fetch=fetch)
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
        study = SpecialistStudy("mechanika", Mock(), fetch=Mock(side_effect=ValueError("bad")))
        result = study.run(consent=True)
        self.assertEqual(result.errors, 1)
        self.assertEqual(result.accepted, 0)


if __name__ == "__main__":
    unittest.main()
