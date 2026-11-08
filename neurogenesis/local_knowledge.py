"""Offline, provenance-aware local TXT memory used by the bundled dialogue.

This is retrieval augmentation, NOT gradient training or self-consciousness.
All text remains in a separate private SQLite file next to existing memory.
No external services, libraries, credentials or model weights are needed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from contextlib import contextmanager
import hashlib
from pathlib import Path
import re
import sqlite3
from typing import Any

MAX_TXT_BYTES = 16 * 1024 * 1024
MAX_PASSAGES = 20_000
CHUNK_CHARS = 900
OVERLAP_CHARS = 100


def segment_text(text: str) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("Local source must be decoded UTF-8")
    cleaned = text.replace("\x00", " ").strip()
    if not cleaned:
        raise ValueError("Nie można dodać pustego TXT.")
    result = []
    i = 0
    while i < len(cleaned):
        end = min(i + CHUNK_CHARS, len(cleaned))
        if end < len(cleaned):
            split = max(cleaned.rfind("\n", i + 320, end),
                        cleaned.rfind(". ", i + 320, end))
            if split > i + 320:
                end = split + 1
        body = cleaned[i:end].strip()
        if body:
            result.append(body)
        if end == len(cleaned):
            break
        i = end - OVERLAP_CHARS
    return result


class LocalKnowledge:
    """Transactional FTS5 corpus with auditable content SHA-256 revisions."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._open() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS local_sources (
                    id INTEGER PRIMARY KEY,
                    source_key TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    bytes INTEGER NOT NULL,
                    added_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS local_passages (
                    id INTEGER PRIMARY KEY,
                    source_id INTEGER NOT NULL REFERENCES local_sources(id)
                        ON DELETE CASCADE,
                    ordinal INTEGER NOT NULL,
                    body TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS local_fts USING fts5(
                    body, tokenize='unicode61 remove_diacritics 2'
                );
            """)

    @contextmanager
    def _open(self):
        """Commit/rollback AND always release the SQLite handle on Windows.

        sqlite3.Connection.__exit__ does not close its file handle, so
        ordinary with sqlite3.connect(...) left temporary database locks.
        """
        con = sqlite3.connect(str(self.db_path), timeout=20)
        try:
            con.execute("PRAGMA foreign_keys=ON")
            con.execute("PRAGMA busy_timeout=20000")
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def import_txt(self, source: str | Path, *, approved: bool = False) -> dict[str, Any]:
        if approved is not True:
            raise PermissionError("Import wiedzy wymaga świadomego wyboru lokalnego TXT.")
        path = Path(source).expanduser()
        if (not path.is_file() or path.is_symlink() or
                path.suffix.lower() != ".txt"):
            raise ValueError("Wybierz istniejący zwykły plik .txt.")
        size = path.stat().st_size
        if not 1 <= size <= MAX_TXT_BYTES:
            raise ValueError("Dopuszczalny TXT: 1 bajt – 16 MiB.")
        raw = path.read_bytes()
        if len(raw) > MAX_TXT_BYTES:
            raise ValueError("TXT zwiększył rozmiar podczas odczytu.")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValueError("Źródło musi być kodowane w UTF-8.") from exc
        digest = hashlib.sha256(raw).hexdigest()
        # Only path HASH is persisted; never publish directory or private text.
        source_key = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()
        passages = segment_text(text)
        if len(passages) > MAX_PASSAGES:
            raise ValueError("Przekroczono bezpieczną liczbę fragmentów.")
        with self._open() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT id,content_sha256 FROM local_sources WHERE source_key=?",
                (source_key,)).fetchone()
            if row is not None and row[1] == digest:
                return {"status": "already_indexed", "sha256": digest,
                        "source": path.name, "passages": len(passages)}
            if row:
                prior = [r[0] for r in con.execute(
                    "SELECT id FROM local_passages WHERE source_id=?", (row[0],))]
                for pid in prior:
                    con.execute("DELETE FROM local_fts WHERE rowid=?", (pid,))
                con.execute("DELETE FROM local_passages WHERE source_id=?", (row[0],))
                con.execute("DELETE FROM local_sources WHERE id=?", (row[0],))
            cur = con.execute(
                "INSERT INTO local_sources(source_key,display_name,content_sha256,bytes,added_utc)"
                "VALUES(?,?,?,?,?)",
                (source_key, path.name, digest, len(raw),
                 datetime.now(timezone.utc).isoformat()))
            src_id = cur.lastrowid
            for ordinal, chunk in enumerate(passages):
                pid = con.execute(
                    "INSERT INTO local_passages(source_id,ordinal,body) VALUES(?,?,?)",
                    (src_id, ordinal, chunk)).lastrowid
                con.execute("INSERT INTO local_fts(rowid,body) VALUES(?,?)",
                            (pid, chunk))
            return {"status": "indexed_local_text", "source": path.name,
                    "sha256": digest, "bytes": len(raw),
                    "passages": len(passages), "new_revision": row is not None,
                    "gradient_training": False}

    def retrieve(self, query: str, *, limit: int = 4) -> list[dict[str, Any]]:
        if not isinstance(query, str) or len(query) > 1800 or not 1 <= limit <= 6:
            raise ValueError("Nieprawidłowe zapytanie do lokalnej pamięci.")
        words = []
        for word in re.findall(r"[^\W_]{3,}", query.lower(), flags=re.UNICODE):
            if word not in words:
                words.append(word)
            if len(words) >= 8:
                break
        if not words:
            return []
        expression = " OR ".join('"' + w + '"' for w in words)
        with self._open() as con:
            rows = con.execute(
                "SELECT p.body,s.display_name,s.content_sha256, "
                "bm25(local_fts) AS relevance "
                "FROM local_fts "
                "JOIN local_passages p ON p.id=local_fts.rowid "
                "JOIN local_sources s ON s.id=p.source_id "
                "WHERE local_fts MATCH ? ORDER BY relevance LIMIT ?",
                (expression, limit)).fetchall()
        return [{"text": t, "file": name, "sha256": sha,
                 "rank": i + 1} for i, (t, name, sha, _score) in enumerate(rows)]

    def status(self) -> dict[str, int]:
        with self._open() as con:
            return {
                "files": int(con.execute("SELECT COUNT(*) FROM local_sources").fetchone()[0]),
                "passages": int(con.execute("SELECT COUNT(*) FROM local_passages").fetchone()[0]),
            }
