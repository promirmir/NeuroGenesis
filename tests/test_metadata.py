"""Block version drift between package metadata, API and public documentation."""

from __future__ import annotations

from pathlib import Path
import tomllib
import unittest

import neurogenesis
from neurogenesis.origin import origin_record


ROOT = Path(__file__).resolve().parents[1]


class MetadataTests(unittest.TestCase):
    def test_versions_are_consistent(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
        version = project['project']['version']
        self.assertEqual(neurogenesis.__version__, version)
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('research prototype v' + version + '.', readme)

    def test_public_credit_does_not_require_family_name(self):
        origin = origin_record()
        self.assertEqual(origin['credit'], 'Miron przy pomocy AI')
        self.assertEqual(origin['human_initiator']['name'], 'Miron')
        self.assertEqual(len(origin['human_initiator']['name'].split()), 1)


if __name__ == '__main__':
    unittest.main()
