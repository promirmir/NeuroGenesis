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
import re
from pathlib import Path
import sqlite3
from typing import Any

from .brain import Brain
from .context import ContextualNextInputPredictor
from .sensory import TextSensor


class ExperienceMemory:
    """Append sensory observations and their updated brain state in one SQL transaction.

    The database is strictly local; raw text is opt-in, but hashes of low-entropy
    text are NOT equivalent to irreversible anonymity. No DB file is committed.
    """

    SCHEMA_VERSION = 1
    MAX_EVENTS = 10_000
    MAX_QUERY_RESULTS = 20
    MAX_TEACHINGS = 512
    MAX_QUESTION_LENGTH = 512
    MAX_ANSWER_LENGTH = 2000

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
                # Explicitly taught, private response associations. Existing
                # v0.4/v0.5.5 DB files remain schema-1 compatible.
                con.execute("""CREATE TABLE IF NOT EXISTS taught_responses (
                    question_digest TEXT PRIMARY KEY,
                    question_normalized TEXT NOT NULL,
                    answer_text TEXT NOT NULL,
                    neural_step INTEGER NOT NULL,
                    learned_utc TEXT NOT NULL
                )""")
                # Online temporal predictor is optional/additive on existing
                # schema-1 databases; it contains no raw text or user strings.
                con.execute("""CREATE TABLE IF NOT EXISTS contextual_state (
                    id INTEGER PRIMARY KEY CHECK (id=1),
                    predictor_json TEXT NOT NULL
                )""")

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
            # A database with recorded experiences but no neural snapshot
            # is corrupt or partially erased. Never replace learned state
            # with a fresh random brain while keeping the old event ledger.
            if con.execute("SELECT 1 FROM observations LIMIT 1").fetchone() is not None:
                raise ValueError("stored brain state missing for existing observations")
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

    @classmethod
    def _normalize_question(cls, question: str) -> str:
        cls._check_text(question)
        if len(question) > cls.MAX_QUESTION_LENGTH:
            raise ValueError("taught question exceeds 512 characters")
        normalized = " ".join(question.casefold().split()).rstrip(" ?!.")
        if not normalized:
            raise ValueError("question has no meaningful content")
        return normalized

    @classmethod
    def _check_answer(cls, answer: str) -> None:
        if (type(answer) is not str or not answer.strip()
                or len(answer) > cls.MAX_ANSWER_LENGTH
                or any(ord(c) < 32 and c not in "\n\t" for c in answer)):
            raise ValueError("answer must contain 1..2000 printable characters")

    def remember(self, text: str, *, source: str = 'local',
                 store_text: bool = False, taught_answer: str | None = None) -> dict[str, Any]:
        self._check_text(text)
        if type(source) is not str or not 1 <= len(source) <= 128 or any(ord(c) < 32 for c in source):
            raise ValueError('source must be a short printable string')
        if type(store_text) is not bool:
            raise ValueError('store_text must be a boolean')
        taught_question = None
        if taught_answer is not None:
            self._check_answer(taught_answer)
            taught_question = self._normalize_question(text)
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
                # Online context learning uses actual post-stimulus neural
                # traces and previous sensory context, with its own bounded
                # readout. All learning, brain and text-event persistence is
                # protected by the same SQLite IMMEDIATE transaction.
                contextual_row = con.execute(
                    'SELECT predictor_json FROM contextual_state WHERE id=1'
                ).fetchone()
                if contextual_row is None:
                    context_model = ContextualNextInputPredictor(brain.config.input_size)
                else:
                    packed = contextual_row[0]
                    if (type(packed) is not str or
                            len(packed.encode('utf-8')) > ContextualNextInputPredictor.MAX_SNAPSHOT_BYTES):
                        raise ValueError('contextual predictor snapshot exceeds size limit')
                    def reject_context_constant(value: str) -> None:
                        raise ValueError('non-finite contextual predictor constant')
                    try:
                        context_model = ContextualNextInputPredictor.from_dict(
                            json.loads(packed, parse_constant=reject_context_constant))
                    except (TypeError, json.JSONDecodeError) as exc:
                        raise ValueError('invalid stored contextual predictor') from exc
                    if context_model.width != brain.config.input_size:
                        raise ValueError('contextual predictor/brain width mismatch')
                context_model.observe(features, brain.traces)
                contextual_json = json.dumps(
                    context_model.to_dict(), allow_nan=False, separators=(',', ':'))
                if len(contextual_json.encode('utf-8')) > ContextualNextInputPredictor.MAX_SNAPSHOT_BYTES:
                    raise ValueError('updated contextual predictor exceeds size limit')
                con.execute('INSERT OR REPLACE INTO contextual_state(id,predictor_json)'
                            ' VALUES(1, ?)', (contextual_json,))
                con.execute('INSERT OR REPLACE INTO neural_state(id, brain_json) VALUES(1, ?)',
                            (serialized,))
                cur = con.execute('''INSERT INTO observations
                    (recorded_utc, brain_step, source, digest, features, raw_text)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (datetime.now(timezone.utc).isoformat(), brain.steps, source,
                     self._hash(text), json.dumps(features), text if store_text else None))
                if taught_question is not None:
                    key = self._hash(taught_question)
                    found = con.execute(
                        'SELECT question_normalized FROM taught_responses WHERE question_digest=?',
                        (key,)).fetchone()
                    if found is not None and found[0] != taught_question:
                        raise ValueError("teaching digest collision or corrupted association")
                    if found is None:
                        n = con.execute('SELECT COUNT(*) FROM taught_responses').fetchone()[0]
                        if n >= self.MAX_TEACHINGS:
                            raise ValueError("taught response capacity exhausted")
                    con.execute('''INSERT INTO taught_responses
                        (question_digest, question_normalized, answer_text, neural_step, learned_utc)
                        VALUES(?,?,?,?,?)
                        ON CONFLICT(question_digest) DO UPDATE SET
                        answer_text=excluded.answer_text,
                        neural_step=excluded.neural_step,
                        learned_utc=excluded.learned_utc''',
                        (key, taught_question, taught_answer, brain.steps,
                         datetime.now(timezone.utc).isoformat()))
                return {'event_id': cur.lastrowid, 'brain_step': brain.steps,
                        'stored_raw_text': store_text, 'neurons': len(brain.voltages),
                        'synapses': len(brain.synapses), 'observations': count + 1,
                        'teaching_saved': taught_question is not None}

    def teach(self, question: str, answer: str) -> dict[str, Any]:
        """Explicit user-approved Q/A training, atomically with brain stimulus.

        This is a private symbolic association attached to a real neural event,
        NOT a claim that the neurons have learned to generate this answer.
        """
        # None is the *internal* default for remember(), never a valid
        # answer supplied to the explicit teaching API. Reject before any
        # SQLite write or neural step.
        self._check_answer(answer)
        return self.remember(question, source="desktop-teaching",
                             store_text=False, taught_answer=answer)

    def taught_answer(self, question: str) -> dict[str, Any] | None:
        """Return only an exact, explicitly taught response; never guess."""
        normalized = self._normalize_question(question)
        key = self._hash(normalized)
        with closing(self._connect()) as con:
            row = con.execute('''SELECT question_normalized, answer_text, neural_step
                                 FROM taught_responses WHERE question_digest=?''', (key,)).fetchone()
        if row is None:
            return None
        if row[0] != normalized or type(row[2]) is not int or row[2] < 0:
            raise ValueError("taught association corrupted")
        self._check_answer(row[1])
        return {"answer": row[1], "brain_step_at_teaching": row[2],
                "response_kind": "explicit_local_teaching"}

    def forget_teaching(self, question: str) -> bool:
        """Forget private answer text; this does NOT undo neural plasticity."""
        normalized = self._normalize_question(question)
        key = self._hash(normalized)
        with closing(self._connect()) as con:
            with con:
                con.execute("BEGIN IMMEDIATE")
                row = con.execute("SELECT question_normalized FROM taught_responses "
                                  "WHERE question_digest=?", (key,)).fetchone()
                if row is not None and row[0] != normalized:
                    raise ValueError("taught association corrupted")
                return con.execute("DELETE FROM taught_responses WHERE question_digest=?",
                                   (key,)).rowcount > 0

    def brain(self) -> Brain:
        with closing(self._connect()) as con:
            return self._brain_from_connection(con)

    def status(self) -> dict[str, Any]:
        with closing(self._connect()) as con:
            n, raw = con.execute('SELECT COUNT(*), SUM(raw_text IS NOT NULL) FROM observations').fetchone()
            taught_count = con.execute("SELECT COUNT(*) FROM taught_responses").fetchone()[0]
            brain = self._brain_from_connection(con)
            context_row = con.execute('SELECT predictor_json FROM contextual_state WHERE id=1').fetchone()
            if context_row is None:
                # Empty or pre-v0.5.7 database; no secret data is created
                # by a read-only status inspection.
                context_stats = ContextualNextInputPredictor(brain.config.input_size).stats()
            else:
                packed = context_row[0]
                if (type(packed) is not str or
                        len(packed.encode('utf-8')) > ContextualNextInputPredictor.MAX_SNAPSHOT_BYTES):
                    raise ValueError('contextual predictor snapshot exceeds size limit')
                try:
                    model = ContextualNextInputPredictor.from_dict(
                        json.loads(packed, parse_constant=lambda value: (
                            _ for _ in ()).throw(ValueError('invalid context constant'))))
                except (TypeError, json.JSONDecodeError) as exc:
                    raise ValueError('invalid stored contextual predictor') from exc
                if model.width != brain.config.input_size:
                    raise ValueError('contextual predictor/brain width mismatch')
                context_stats = model.stats()
            return {'observations': n, 'records_with_raw_text': raw or 0,
                    'taught_responses': taught_count,
                    'context_learning': context_stats,
                    'brain': brain.stats()}

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
