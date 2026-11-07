"""Regulators do not touch the existing v0.4 SQLite experience format."""
from contextlib import closing
import tempfile
import sqlite3
from pathlib import Path
import unittest
from neurogenesis.brain import Brain
from neurogenesis.memory import ExperienceMemory
from neurogenesis.homeostasis import HomeostaticRegulator
from neurogenesis.repair import lesioned_copy, trial_repair

class SqliteCompatibilityTests(unittest.TestCase):
    def test_sqlite_ledger_unchanged_by_external_regulation(self):
        with tempfile.TemporaryDirectory() as tmp:
            filename=Path(tmp)/'experiences.sqlite3'
            m=ExperienceMemory(filename)
            r=m.remember('Zdarzenie testowe')
            old=m.brain().to_dict()
            ctrl=HomeostaticRegulator.attach(m.brain())
            damaged=lesioned_copy(m.brain(),fraction=.25,seed=1)
            trial_repair(damaged,lambda _:0.4)
            self.assertEqual(m.brain().to_dict(),old)
            self.assertEqual(ExperienceMemory(filename).status()['observations'],1)
            self.assertFalse('raw_text' in m.recall('Zdarzenie testowe')[0])
            self.assertFalse(r['stored_raw_text'])
            self.assertEqual(ctrl.steps,old['steps'])

    def test_corrupt_db_brain_fails_closed_and_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            filename=Path(tmp)/'experiences.sqlite3'
            m=ExperienceMemory(filename);m.remember('sample')
            with closing(sqlite3.connect(filename)) as db, db:
                db.execute("UPDATE neural_state SET brain_json='{}'")
            with self.assertRaises(ValueError):ExperienceMemory(filename).remember('second sample')
            with closing(sqlite3.connect(filename)) as db, db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM observations').fetchone()[0],1)
                self.assertEqual(db.execute('SELECT brain_json FROM neural_state').fetchone()[0], '{}')

    def test_legacy_brain_without_origin_still_loads(self):
        x=Brain().to_dict()
        x.pop('origin')
        self.assertEqual(Brain.from_dict(x).to_dict()['origin']['credit'],'Miron przy pomocy AI')
