"""SQLite experience/brain atomicity, privacy defaults and recovery tests."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from neurogenesis.memory import ExperienceMemory


class ExperienceMemoryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'private.sqlite3'
        self.store = ExperienceMemory(self.path)

    def test_empty_state_is_a_valid_new_brain(self):
        status = self.store.status()
        self.assertEqual(status['observations'], 0)
        self.assertEqual(status['records_with_raw_text'], 0)
        self.assertEqual(status['brain']['steps'], 0)

    def test_default_save_never_persists_raw_text_and_survives_reopen(self):
        item = self.store.remember('prywatny lokalny test')
        self.assertEqual(item['brain_step'], 4)
        self.assertFalse(item['stored_raw_text'])
        reopened = ExperienceMemory(self.path)
        self.assertEqual(reopened.status()['observations'], 1)
        self.assertEqual(reopened.brain().steps, 4)
        found = reopened.recall('prywatny lokalny test')
        self.assertTrue(found[0]['exact_hash_match'])
        self.assertNotIn('raw_text', found[0])
        self.assertIsNone(reopened.recall('prywatny lokalny test', show_text=True)[0]['raw_text'])
        row = reopened.remember('kolejna obserwacja')
        self.assertEqual(row['brain_step'], 8)

    def test_raw_storage_requires_explicit_opt_in_and_can_delete_record(self):
        row = self.store.remember('testowe zdanie', store_text=True)
        event = self.store.recall('testowe zdanie', show_text=True)[0]
        self.assertEqual(event['raw_text'], 'testowe zdanie')
        self.assertTrue(self.store.delete_event(row['event_id']))
        self.assertEqual(self.store.recall('testowe zdanie'), [])
        self.assertEqual(self.store.brain().steps, 4)  # deletion != unlearning
        self.assertFalse(self.store.delete_event(row['event_id']))

    def test_sqlite_transactions_roll_back_on_invalid_input_and_capacity(self):
        with self.assertRaises(ValueError):
            self.store.remember('', source='local')
        with self.assertRaises(ValueError):
            self.store.remember('valid', source='x\nunsafe')
        with self.assertRaises(ValueError):
            self.store.remember('valid', store_text=2)
        self.assertEqual(self.store.status()['observations'], 0)
        old = ExperienceMemory.MAX_EVENTS
        try:
            ExperienceMemory.MAX_EVENTS = 1
            self.store.remember('one')
            with self.assertRaises(ValueError):
                self.store.remember('two')
            self.assertEqual(self.store.brain().steps, 4)
            self.assertEqual(self.store.status()['observations'], 1)
        finally:
            ExperienceMemory.MAX_EVENTS = old

    def test_input_validation_and_safe_querying(self):
        self.store.remember('first', source="quotes ' ; DROP TABLE observations")
        self.store.remember('second')
        self.assertEqual(self.store.status()['observations'], 2)
        for kwargs in ({'limit': 0}, {'limit': 100}, {'show_text': 'yes'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.store.recall('x', **kwargs)
        with self.assertRaises(ValueError):
            self.store.delete_event(-1)

    def test_schema_mismatch_cannot_silently_reset_database(self):
        with self.store._connect() as con:
            con.execute("UPDATE metadata SET value='999' WHERE key='schema'")
        with self.assertRaisesRegex(ValueError, 'schema'):
            ExperienceMemory(self.path)

    def test_cli_remember_and_recall_offline(self):
        base = [sys.executable, '-m', 'neurogenesis']
        saved = subprocess.check_output(base + ['remember', 'offline memory test', '--db', str(self.path)], text=True)
        self.assertEqual(json.loads(saved)['brain_step'], 4)
        recalled = subprocess.check_output(base + ['recall', 'offline memory test', '--db', str(self.path)], text=True)
        self.assertTrue(json.loads(recalled)[0]['exact_hash_match'])
        status = subprocess.check_output(base + ['memory-status', '--db', str(self.path)], text=True)
        self.assertEqual(json.loads(status)['observations'], 1)


if __name__ == '__main__':
    unittest.main()
