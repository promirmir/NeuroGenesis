"""Durable, bounded agent goal queue driven by real LOCAL model and evidence.

The coordinator performs an independent cycle: inspect real local sources,
claim changed work, ask the pretrained model to reason about the goal,
store a DRAFT and its provenance. No arbitrary tool execution, silent
network acquisition, self-modifying code, or unreviewed model promotion.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any

from .local_knowledge import LocalKnowledge
from .memory import ExperienceMemory

MAX_ACTIVE = 12
MAX_ATTEMPTS = 32
MAX_GOAL_LENGTH = 600
MAX_ANSWER = 7000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def goal_fingerprint(sources: list[dict[str, Any]], corpus_digest: str) -> str:
    """Stable evidence revision; changes only on new corpus/evidence."""
    items = [(p["sha256"], p["file"], sha256(p["text"].encode("utf-8")).hexdigest())
             for p in sources]
    return sha256(json.dumps(
        [corpus_digest, items], ensure_ascii=False,
        separators=(",", ":")).encode("utf-8")).hexdigest()


def _validate_goal(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("Cel musi być tekstem.")
    goal = " ".join(text.split())
    if not 12 <= len(goal) <= MAX_GOAL_LENGTH:
        raise ValueError("Cel: 12–600 znaków.")
    if any(ord(c) < 32 for c in goal):
        raise ValueError("Niedozwolone znaki w celu.")
    return goal


class GoalStore:
    """Persistent goals with checked status transitions and bounded retries."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn:
            with conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS agent_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    fingerprint TEXT,
                    last_result TEXT NOT NULL DEFAULT '',
                    citations_json TEXT NOT NULL DEFAULT '[]',
                    created_utc TEXT NOT NULL,
                    updated_utc TEXT NOT NULL
                )""")
                conn.execute("""CREATE TABLE IF NOT EXISTS agent_goal_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL REFERENCES agent_goals(id),
                    recorded_utc TEXT NOT NULL,
                    state TEXT NOT NULL,
                    result_sha256 TEXT NOT NULL,
                    citations_json TEXT NOT NULL
                )""")
                # Previous application may have shut down while the local
                # model was computing. Recover queued work on next start,
                # retaining the last successful result for audit.
                conn.execute(
                    "UPDATE agent_goals SET state='queued',fingerprint=NULL,"
                    "updated_utc=? WHERE state='running'", (_now(),))

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.path), timeout=20)
        con.execute("PRAGMA busy_timeout=20000")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def add(self, text: str) -> int:
        goal = _validate_goal(text)
        with closing(self._connect()) as conn:
            with conn:
                conn.execute("BEGIN IMMEDIATE")
                count = conn.execute(
                    "SELECT COUNT(*) FROM agent_goals WHERE state NOT IN ('accepted','paused')").fetchone()[0]
                if count >= MAX_ACTIVE:
                    raise ValueError("Limit 12 aktywnych celów. Zakończ lub wstrzymaj wcześniejsze.")
                cursor = conn.execute(
                    "INSERT INTO agent_goals(goal,state,created_utc,updated_utc)"
                    "VALUES(?,?,?,?)",
                    (goal, "queued", _now(), _now()))
                return int(cursor.lastrowid)

    def list(self, *, limit: int = 12) -> list[dict[str, Any]]:
        if not 1 <= limit <= 100:
            raise ValueError("Nieprawidłowy limit celów.")
        with closing(self._connect()) as con:
            rows = con.execute(
                "SELECT id,goal,state,attempts,last_result,citations_json,updated_utc "
                "FROM agent_goals ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{"id": i, "goal": g, "state": st, "attempts": a, "result": result,
                 "sources": json.loads(cites), "updated_utc": stamp}
                for i, g, st, a, result, cites, stamp in rows]

    def claim(self, knowledge: LocalKnowledge,
              web_memory: ExperienceMemory | None = None) -> dict[str, Any] | None:
        """Claim work on NEW real TXT or approved HTTPS evidence, not clock ticks.

        Web material is an inert, source-labelled quotation. No network is
        accessed by claim(); only existing user-authorized SQLite is read.
        """
        corpus_digest = knowledge.corpus_fingerprint()
        with closing(self._connect()) as con:
            with con:
                con.execute("BEGIN IMMEDIATE")
                rows = con.execute(
                    "SELECT id,goal,fingerprint,attempts FROM agent_goals "
                    "WHERE state IN ('queued','waiting','candidate') "
                    "ORDER BY CASE state WHEN 'queued' THEN 0 "
                    "WHEN 'waiting' THEN 1 ELSE 2 END, updated_utc LIMIT ?",
                    (MAX_ACTIVE,)).fetchall()
                for goal_id, goal, prior_digest, attempts in rows:
                    if attempts >= MAX_ATTEMPTS:
                        continue
                    passages = knowledge.retrieve(goal, limit=4)
                    if web_memory is not None:
                        # The web evidence retriever has a strict 512-char
                        # budget; goals themselves may contain 600 chars.
                        evidence = web_memory.answer_from_knowledge(goal[:512])
                        if evidence is not None and evidence.get("sources"):
                            # A concise previously saved source excerpt is
                            # sufficient to trigger re-analysis of this goal.
                            # Do not treat an unverified quote as truth.
                            for source in evidence["sources"][:2]:
                                url, digest = source["url"], source["sha256"]
                                if not isinstance(url, str) or not isinstance(digest, str):
                                    continue
                                excerpt = evidence.get("answer", "")[:1200]
                                if excerpt and len(passages) < 4:
                                    passages.append({
                                        "text": "NIEZWERYFIKOWANA TREŚĆ ŹRÓDŁA HTTPS:\n" + excerpt,
                                        "file": url,
                                        "sha256": digest,
                                        "rank": len(passages) + 1,
                                    })
                    digest = goal_fingerprint(passages, corpus_digest)
                    if prior_digest == digest and attempts > 0:
                        continue
                    con.execute(
                        "UPDATE agent_goals SET state='running',attempts=attempts+1,"
                        "fingerprint=?,updated_utc=? WHERE id=?",
                        (digest, _now(), goal_id))
                    return {"id": int(goal_id), "goal": goal,
                            "sources": passages, "fingerprint": digest}
        return None

    def complete(self, claimed: dict[str, Any], response: str) -> dict[str, Any]:
        if not isinstance(response, str) or not 1 <= len(response.strip()) <= MAX_ANSWER:
            raise ValueError("Niepoprawny wynik modelu.")
        state = "candidate" if claimed["sources"] else "waiting"
        references = [{"file": p["file"], "sha256": p["sha256"], "rank": p["rank"]}
                      for p in claimed["sources"][:4]]
        cited = json.dumps(references, ensure_ascii=False)
        with closing(self._connect()) as con:
            with con:
                result = con.execute(
                    "UPDATE agent_goals SET state=?,last_result=?,citations_json=?,updated_utc=? "
                    "WHERE id=? AND state='running' AND fingerprint=?",
                    (state, response.strip(), cited, _now(),
                     claimed["id"], claimed["fingerprint"]))
                if result.rowcount != 1:
                    raise ValueError("Cel zmieniono w trakcie obliczeń; wynik odrzucony.")
                con.execute(
                    "INSERT INTO agent_goal_runs(goal_id,recorded_utc,state,result_sha256,citations_json)"
                    "VALUES(?,?,?,?,?)",
                    (claimed["id"], _now(), state,
                     sha256(response.encode("utf-8")).hexdigest(), cited))
        return {"id": claimed["id"], "state": state,
                "source_count": len(references), "review_required": True,
                "model_weight_training": False}

    def fail(self, claimed: dict[str, Any], explanation: str) -> None:
        with closing(self._connect()) as con:
            with con:
                con.execute(
                    "UPDATE agent_goals SET state='error',last_result=?,updated_utc=? "
                    "WHERE id=? AND state='running' AND fingerprint=?",
                    (str(explanation)[:400], _now(), claimed["id"], claimed["fingerprint"]))

    def set_state(self, goal_id: int, action: str) -> str:
        if type(goal_id) is not int or goal_id < 1:
            raise ValueError("Niepoprawny numer celu.")
        actions = {
            "pause": (("queued", "waiting", "candidate", "error"), "paused"),
            "resume": (("paused", "error", "candidate"), "queued"),
            "accept": (("candidate",), "accepted"),
        }
        if action not in actions:
            raise ValueError("Nieobsługiwana decyzja.")
        allowed, desired = actions[action]
        with closing(self._connect()) as con:
            with con:
                row = con.execute(
                    "SELECT state FROM agent_goals WHERE id=?", (goal_id,)).fetchone()
                if row is None or row[0] not in allowed:
                    raise ValueError("Nieprawidłowe przejście stanu celu.")
                con.execute(
                    "UPDATE agent_goals SET state=?, fingerprint=?, updated_utc=? WHERE id=?",
                    (desired, None if action == "resume" else
                     con.execute("SELECT fingerprint FROM agent_goals WHERE id=?",
                                 (goal_id,)).fetchone()[0], _now(), goal_id))
        return desired


def prompt_for_goal(claimed: dict[str, Any]) -> str:
    goal = _validate_goal(claimed["goal"])
    if claimed["sources"]:
        return (
            "Zadanie autonomiczne NeuroGenesis. Cel: " + goal +
            "\n\nPrzeanalizuj dostępne lokalne źródła oraz zatwierdzone źródła HTTPS, przedstaw konkretny "
            "wynik, ryzyka i czego nie można jeszcze potwierdzić. "
            "Nie wymyślaj faktów. To WERSJA DO WERYFIKACJI, "
            "nie wdrażaj zmian, nie deklaruj pełnego wykonania.")
    return (
        "Zadanie autonomiczne NeuroGenesis. Cel: " + goal +
        "\n\nBrak odpowiednich zatwierdzonych źródeł (TXT i HTTPS). Sporządź maksymalnie "
        "trzy konkretne kroki PLANU i wskaż jakie dane trzeba "
        "pozyskać. Nie twierdź, że zadanie zostało zrealizowane. "
        "Nie wymyślaj wyników ani nie wykonuj zewnętrznych działań.")
