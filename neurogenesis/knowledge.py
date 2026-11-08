"""Bounded, local evidence index for operator-approved public web observations.

All retrieved text remains untrusted data. This module does NOT train a neural
model, verify factual claims, interpret instructions, or contact the network.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
import sqlite3
import unicodedata
from typing import Any

MAX_SOURCE_CHARS = 6000
MAX_PASSAGE_CHARS = 450
MAX_CHUNKS_PER_SOURCE = 32
MAX_QUERY_CHARS = 512
MAX_QUERY_TERMS = 12

# Conservative English/Polish function-word filter. This is *lexical* matching,
# not stemming, semantic parsing, inference or factual source verification.
STOP = frozenset("""
a aby albo ale and are as at be bo by can czy dla do does for from
gdy go i in is it jak jaki jaka jakie jakiemu jakieś je jest jeśli już
kiedy kto która które który lub ma mają mi na nad nie no o od on or
oraz po pod przez się są ta tak ten that the their there this to was
we were what when where which who why w we with z za ze że
""".split())
TOKEN = re.compile(r"[^\W_]{3,}", re.UNICODE)
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+", re.UNICODE)


def _terms(text: str) -> tuple[str, ...]:
    words = TOKEN.findall(unicodedata.normalize("NFKC", text).casefold())
    return tuple(dict.fromkeys(w for w in words if w not in STOP))


def passages(text: str) -> tuple[str, ...]:
    """Produce deterministic, short verbatim extracts without rewriting facts."""
    if type(text) is not str or not text.strip() or len(text) > MAX_SOURCE_CHARS:
        raise ValueError("invalid knowledge source text length")
    result: list[str] = []
    current = ""
    for sentence in SENTENCE_BOUNDARY.split(text.strip()):
        sentence = " ".join(sentence.split())
        if not sentence:
            continue
        while len(sentence) > MAX_PASSAGE_CHARS:
            if current:
                result.append(current)
                current = ""
            cut = sentence.rfind(" ", 0, MAX_PASSAGE_CHARS + 1)
            cut = cut if cut >= MAX_PASSAGE_CHARS // 2 else MAX_PASSAGE_CHARS
            result.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if not sentence:
            continue
        if current and len(current) + 1 + len(sentence) <= MAX_PASSAGE_CHARS:
            current += " " + sentence
        else:
            if current:
                result.append(current)
            current = sentence
    if current:
        result.append(current)
    if not result or len(result) > MAX_CHUNKS_PER_SOURCE:
        raise ValueError("knowledge source cannot be safely segmented")
    return tuple(result)


def ensure_schema(con: sqlite3.Connection) -> None:
    """Additive migration of the existing schema=1 private SQLite database."""
    con.execute("""CREATE TABLE IF NOT EXISTS knowledge_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL UNIQUE,
        url TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        retrieved_utc TEXT NOT NULL,
        rights_status TEXT NOT NULL DEFAULT 'unverified',
        UNIQUE(url, sha256)
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS knowledge_passages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        ordinal INTEGER NOT NULL,
        body TEXT NOT NULL,
        UNIQUE(source_id, ordinal)
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS knowledge_terms (
        term TEXT NOT NULL,
        passage_id INTEGER NOT NULL,
        PRIMARY KEY(term, passage_id)
    )""")
    con.execute("CREATE INDEX IF NOT EXISTS ix_knowledge_url ON knowledge_sources(url)")
    con.execute("CREATE INDEX IF NOT EXISTS ix_knowledge_passage_source ON knowledge_passages(source_id)")
    con.execute("CREATE INDEX IF NOT EXISTS ix_knowledge_term ON knowledge_terms(term)")
    con.execute("""CREATE TABLE IF NOT EXISTS knowledge_rights_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        changed_utc TEXT NOT NULL,
        status TEXT NOT NULL
    )""")


def insert_source(con: sqlite3.Connection, *, event_id: int, url: str,
                  sha256: str, retrieved_utc: str, text: str) -> int:
    """Must run INSIDE the same transaction as neural state and web provenance."""
    chunks = passages(text)
    row = con.execute(
        "INSERT INTO knowledge_sources(event_id,url,sha256,retrieved_utc) VALUES(?,?,?,?)",
        (event_id, url, sha256, retrieved_utc))
    source_id = int(row.lastrowid)
    for ordinal, excerpt in enumerate(chunks):
        row = con.execute(
            "INSERT INTO knowledge_passages(source_id,ordinal,body) VALUES(?,?,?)",
            (source_id, ordinal, excerpt))
        passage_id = int(row.lastrowid)
        for term in _terms(excerpt):
            con.execute(
                "INSERT INTO knowledge_terms(term,passage_id) VALUES(?,?)",
                (term, passage_id))
    return len(chunks)


def remove_event(con: sqlite3.Connection, event_id: int) -> None:
    """Remove its text and inverted index; neural-weight unlearning is separate."""
    row = con.execute(
        "SELECT id FROM knowledge_sources WHERE event_id=?", (event_id,)).fetchone()
    if row is None:
        return
    source_id = row[0]
    con.execute("""DELETE FROM knowledge_terms WHERE passage_id IN
                   (SELECT id FROM knowledge_passages WHERE source_id=?)""",
                (source_id,))
    con.execute("DELETE FROM knowledge_passages WHERE source_id=?", (source_id,))
    con.execute("DELETE FROM knowledge_rights_audit WHERE source_id=?", (source_id,))
    con.execute("DELETE FROM knowledge_sources WHERE id=?", (source_id,))


def answer_question(con: sqlite3.Connection, question: str) -> dict[str, Any] | None:
    """Extract a relevant *verbatim* passage from the newest source URL version.

    Returns None for unsupported queries. Any returned text remains unverified
    source evidence, never a claim of learned model competence or ground truth.
    """
    if type(question) is not str or not question.strip() or len(question) > MAX_QUERY_CHARS:
        return None
    terms = _terms(question)[:MAX_QUERY_TERMS]
    if not terms:
        return None
    placeholders = ",".join("?" for _ in terms)
    rows = con.execute(
        "SELECT p.body, s.url, s.sha256, s.retrieved_utc, s.rights_status, "
        "s.id, COUNT(DISTINCT t.term) AS overlap "
        "FROM knowledge_terms t "
        "JOIN knowledge_passages p ON p.id=t.passage_id "
        "JOIN knowledge_sources s ON s.id=p.source_id "
        f"WHERE t.term IN ({placeholders}) "
        "AND s.id=(SELECT MAX(newer.id) FROM knowledge_sources newer WHERE newer.url=s.url) "
        "GROUP BY p.id ORDER BY overlap DESC, s.id DESC, p.ordinal ASC LIMIT 24",
        terms).fetchall()
    if not rows:
        return None
    best = rows[0]
    overlap = int(best[6])
    # At least two distinctive tokens for multi-term questions, to avoid a
    # single common word being presented as a substantive factual answer.
    required = 1 if len(terms) == 1 else 2
    if overlap < required or overlap / len(terms) < 0.4:
        return None
    excerpt, url, sha, timestamp, rights, source_id, _ = best
    version = con.execute(
        "SELECT COUNT(*) FROM knowledge_sources WHERE url=? AND id<=?",
        (url, source_id)).fetchone()[0]
    return {
        "response_kind": "source_evidence",
        "answer": ("Cytat ze zgromadzonego źródła (niezależnie niezweryfikowany):\n"
                   + excerpt + "\n\nŹródło: " + url
                   + "\nWersja: " + str(version)
                   + " · Prawa do dalszego wykorzystania: niezweryfikowane."),
        "source": {"url": url, "sha256": sha, "retrieved_utc": timestamp,
                   "version": version, "rights_status": rights},
        "matched_query_terms": overlap,
        "total_query_terms": len(terms),
    }


def stats(con: sqlite3.Connection) -> dict[str, int]:
    docs = con.execute("SELECT COUNT(*) FROM knowledge_sources").fetchone()[0]
    chunks = con.execute("SELECT COUNT(*) FROM knowledge_passages").fetchone()[0]
    return {"documents": docs, "passages": chunks}


def recent_sources(con: sqlite3.Connection, limit: int = 20) -> list[dict[str, Any]]:
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("invalid source limit")
    rows = con.execute(
        "SELECT s.id,s.url,s.sha256,s.retrieved_utc,s.rights_status,"
        "(SELECT COUNT(*) FROM knowledge_sources older WHERE older.url=s.url AND older.id<=s.id) "
        "FROM knowledge_sources s ORDER BY s.id DESC LIMIT ?", (limit,)).fetchall()
    return [{"id": key, "url": url, "sha256": digest, "retrieved_utc": stamp,
             "rights_status": rights, "version": ver}
            for key, url, digest, stamp, rights, ver in rows]


def source_passages(con: sqlite3.Connection, source_id: int) -> list[dict[str, Any]]:
    """Read one source revision's bounded inert excerpts, never fetch network."""
    if type(source_id) is not int or source_id < 1:
        raise ValueError("invalid source identifier")
    rows = con.execute(
        "SELECT p.ordinal,p.body FROM knowledge_passages p "
        "JOIN knowledge_sources s ON s.id=p.source_id "
        "WHERE s.id=? ORDER BY p.ordinal LIMIT ?", (source_id, MAX_CHUNKS_PER_SOURCE)).fetchall()
    return [{"ordinal": ordinal, "text": body} for ordinal, body in rows]


MAX_APPROVED_TRAINING_SOURCES = 64
TRAINING_APPROVED = "operator-approved-local-training"


def set_training_rights(con: sqlite3.Connection, source_id: int,
                        approved: bool) -> dict[str, Any]:
    """Record explicit operator assertion; not proof of the source's license."""
    if type(source_id) is not int or source_id < 1 or type(approved) is not bool:
        raise ValueError("explicit source identifier and approval boolean required")
    row = con.execute(
        "SELECT url,sha256 FROM knowledge_sources WHERE id=?", (source_id,)).fetchone()
    if row is None:
        raise ValueError("source revision not found")
    status = TRAINING_APPROVED if approved else "training-denied"
    con.execute("UPDATE knowledge_sources SET rights_status=? WHERE id=?",
                (status, source_id))
    con.execute(
        "INSERT INTO knowledge_rights_audit(source_id,changed_utc,status) VALUES(?,?,?)",
        (source_id, datetime.now(timezone.utc).isoformat(), status))
    return {"source_id": source_id, "url": row[0], "sha256": row[1],
            "rights_status": status}


def approved_training_documents(con: sqlite3.Connection) -> list[dict[str, Any]]:
    """Only latest explicitly approved source revisions, preserving doc splits.

    All text remains local. No network calls and no automatic approvals.
    """
    rows = con.execute(
        "SELECT s.id,s.url,s.sha256 FROM knowledge_sources s "
        "WHERE s.rights_status=? "
        "AND s.id=(SELECT MAX(n.id) FROM knowledge_sources n WHERE n.url=s.url) "
        "ORDER BY s.url,s.id LIMIT ?",
        (TRAINING_APPROVED, MAX_APPROVED_TRAINING_SOURCES + 1)).fetchall()
    if len(rows) > MAX_APPROVED_TRAINING_SOURCES:
        raise ValueError("too many approved documents for bounded training")
    documents = []
    for key, url, sha in rows:
        parts = con.execute(
            "SELECT body FROM knowledge_passages WHERE source_id=? "
            "ORDER BY ordinal LIMIT ?", (key, MAX_CHUNKS_PER_SOURCE)).fetchall()
        if not parts:
            raise ValueError("approved knowledge source has no passages")
        text = "\n".join(part[0] for part in parts)
        documents.append({"source_id": key, "url": url, "sha256": sha, "text": text})
    return documents
