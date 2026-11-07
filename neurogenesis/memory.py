"""Privacy-conscious local episodic ledger linked atomically to brain state.

This is exact/feature-hash event recall, NOT semantic autobiographical memory.
No internet, secret storage, consciousness or understanding is implied.
"""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
from typing import Any

from .brain import Brain
from .sensory import TextSensor


class ExperienceMemory:
    """Append sensory observations and their updated brain state in one SQL transaction.

    The database is strictly local; raw text is opt-in, but hashes of low-entropy
    text are NOT equivalent to irreversible anonymity. No DB file is committed.
    """

    SCHEMA_VERSION = 1
    MAX_EVENTS = 10_000
    MAX_QUERY_RESULTS = 20

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if self.path.is_symlink():
            raise ValueError("memory database cannot be a symbolic link")
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            if self.path.is_symlink() or not self.path.is_file():
                raise ValueError("memory path must be a normal file")
        else:
            os.close(fd)
        with closing(self._connect()) as con:
            with con:
                con.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                row = con.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()
                if row is None:
                    con.execute("INSERT INTO metadata(key, value) VALUES('schema', ?)",
                                (str(self.SCHEMA_VERSION),))
                elif row[0] != str(self.SCHEMA_VERSION):
                    raise ValueError("unsupported episodic memory schema")
                con.execute("""CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recorded_utc TEXT NOT NULL,
                    brain_step INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    digest TEXT NOT NULL,
                    features TEXT NOT NULL,
                    raw_text TEXT
                )""")
                con.execute("""CREATE TABLE IF NOT EXISTS neural_state (
                    id INTEGER PRIMARY KEY CHECK (id=1),
                    brain_json TEXT NOT NULL
                )""")
                con.execute("CREATE INDEX IF NOT EXISTS ix_observations_digest ON observations(digest)")

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path, timeout=5)
        con.execute("PRAGMA busy_timeout=5000")
        con.execute("PRAGMA secure_delete=ON")
        return con

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def _check_text(text: str) -> None:
        if type(text) is not str or not text.strip() or len(text) > TextSensor.MAX_TEXT_LENGTH:
            raise ValueError("nonempty text of <= 20000 characters required")

    def _brain_from_connection(self, con: sqlite3.Connection) -> Brain:
        row = con.execute("SELECT brain_json FROM neural_state WHERE id=1").fetchone()
        if row is None:
            return Brain()
        raw = row[0]
        if not isinstance(raw, str) or len(raw.encode('utf-8')) > Brain.MAX_STATE_BYTES:
            raise ValueError("brain snapshot exceeds size limit")
        def reject_constant(x: str) -> None:
            raise ValueError("invalid numerical constant in stored brain")
        try:
            return Brain.from_dict(json.loads(raw, parse_constant=reject_constant))
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid stored brain state") from exc

    def remember(self, text: str, *, source: str = 'local',
                 store_text: bool = False) -> dict[str, Any]:
        self._check_text(text)
        if type(source) is not str or not 1 <= len(source) <= 128 or any(ord(c) < 32 for c in source):
            raise ValueError('source must be a short printable string')
        if type(store_text) is not bool:
            raise ValueError('store_text must be a boolean')
        with closing(self._connect()) as con:
            with con:
                con.execute("BEGIN IMMEDIATE")
                count = con.execute('SELECT COUNT(*) FROM observations').fetchone()[0]
                if count >= self.MAX_EVENTS:
                    raise ValueError('episodic memory at capacity; export or clear records explicitly')
                brain = self._brain_from_connection(con)
                features = TextSensor(brain.config.input_size).encode(text)
                # Preserve the legacy four-step brain path until a validated
                # self-development candidate has installed a predictor. Once
                # present, the predictor owns that *same* persisted brain: no
                # duplicated neural updates or diverging brain copies.
                has_predictor_table = con.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='predictor_state'"
                ).fetchone()
                predictor_row = (con.execute(
                    "SELECT predictor_json FROM predictor_state WHERE id=1"
                ).fetchone() if has_predictor_table else None)
                predictor = None
                if predictor_row is not None:
                    from .predictor import NextInputPredictor
                    raw = predictor_row[0]
                    if not isinstance(raw, str) or len(raw.encode('utf-8')) > Brain.MAX_STATE_BYTES:
                        raise ValueError('stored predictor exceeds size limit')
                    def reject_number(x: str) -> None:
                        raise ValueError('invalid numerical constant in stored predictor')
                    try:
                        predictor = NextInputPredictor.from_dict(
                            json.loads(raw, parse_constant=reject_number))
                    except (TypeError, json.JSONDecodeError) as exc:
                        raise ValueError('invalid stored predictor') from exc
                    if predictor.brain.to_dict() != brain.to_dict():
                        raise ValueError('predictor/brain divergence; refusing to overwrite')
                    for _ in range(4):
                        predictor.step(features)
                    brain = predictor.brain
                else:
                    for _ in range(4):
                        brain.step(features)
                serialized = json.dumps(brain.to_dict(), separators=(',', ':'), allow_nan=False)
                if len(serialized.encode('utf-8')) > Brain.MAX_STATE_BYTES:
                    raise ValueError('updated neural state exceeds size limit')
                if predictor is not None:
                    packed_predictor = json.dumps(
                        predictor.to_dict(), separators=(',', ':'), allow_nan=False)
                    if len(packed_predictor.encode('utf-8')) > Brain.MAX_STATE_BYTES:
                        raise ValueError('updated predictor exceeds size limit')
                    con.execute('UPDATE predictor_state SET predictor_json=? WHERE id=1',
                                (packed_predictor,))
                con.execute('INSERT OR REPLACE INTO neural_state(id, brain_json) VALUES(1, ?)',
                            (serialized,))
                cur = con.execute('''INSERT INTO observations
                    (recorded_utc, brain_step, source, digest, features, raw_text)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (datetime.now(timezone.utc).isoformat(), brain.steps, source,
                     self._hash(text), json.dumps(features), text if store_text else None))
                return {'event_id': cur.lastrowid, 'brain_step': brain.steps,
                        'stored_raw_text': store_text, 'neurons': len(brain.voltages),
                        'synapses': len(brain.synapses), 'observations': count + 1}

    def brain(self) -> Brain:
        with closing(self._connect()) as con:
            return self._brain_from_connection(con)

    def status(self) -> dict[str, Any]:
        with closing(self._connect()) as con:
            n, raw = con.execute('SELECT COUNT(*), SUM(raw_text IS NOT NULL) FROM observations').fetchone()
            return {'observations': n, 'records_with_raw_text': raw or 0,
                    'brain': self._brain_from_connection(con).stats()}

    def recall(self, query: str, *, limit: int = 5,
               show_text: bool = False) -> list[dict[str, Any]]:
        self._check_text(query)
        if type(limit) is not int or not 1 <= limit <= self.MAX_QUERY_RESULTS:
            raise ValueError('limit must be in [1, 20]')
        if type(show_text) is not bool:
            raise ValueError('show_text must be a boolean')
        sensor = TextSensor()
        q = sensor.encode(query)
        q_norm = math.sqrt(sum(x * x for x in q))
        with closing(self._connect()) as con:
            rows = con.execute('''SELECT id, recorded_utc, brain_step, source,
                                     digest, features, raw_text FROM observations''').fetchall()
        results = []
        digest = self._hash(query)
        for eid, date, step, source, key, packed, raw in rows:
            v = json.loads(packed)
            if not isinstance(v, list) or len(v) != len(q):
                raise ValueError('stored features have invalid dimensions')
            if any(type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= 1 for x in v):
                raise ValueError('stored features contain invalid values')
            norm = math.sqrt(sum(x * x for x in v))
            similarity = (sum(a * b for a, b in zip(q, v)) / (q_norm * norm)
                          if q_norm and norm else 0.0)
            result: dict[str, Any] = {'event_id': eid, 'recorded_utc': date,
                                      'brain_step': step, 'source': source,
                                      'exact_hash_match': key == digest,
                                      'feature_similarity': round(similarity, 6)}
            if show_text:
                result['raw_text'] = raw
            results.append(result)
        return sorted(results, key=lambda x: (not x['exact_hash_match'],
                           -x['feature_similarity'], -x['event_id']))[:limit]

    def delete_event(self, event_id: int) -> bool:
        """Delete logged text/features, NOT the already-learned synaptic state."""
        if type(event_id) is not int or event_id < 1:
            raise ValueError('event_id must be positive integer')
        with closing(self._connect()) as con:
            with con:
                cursor = con.execute('DELETE FROM observations WHERE id=?', (event_id,))
                return cursor.rowcount > 0
