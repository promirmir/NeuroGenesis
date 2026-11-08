"""Private continual-learning ledger of real LLM-inferred semantic axes.

No user messages, private files, source URLs, or digests of a message are
stored. Only eight 0/1 tag values (which themselves reveal broad topic
categories), the pinned model label and a clock value remain in SQLite.

The independent ACF plastic/fixed predictor is updated via the SAME atomic
checkpoint + observation-cursor facility as the original sensory ACF.
This never modifies the pretrained Qwen weights or existing LIF state.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Any, Sequence

from .acf import AdaptiveCognitiveFabric, _sample
from .acf_memory import FabricMemoryObserver
from .local_knowledge import LocalKnowledge
from .semantic_policy import prepare_local_sources
from .acf_semantics import VERSION

MAX_EVENTS = 50000


class SemanticFabricStore:
    def __init__(self, private_root: str | Path):
        root = Path(private_root)
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / "semantic_fabric.sqlite3"
        self.state_path = root / "semantic_fabric.acf.json"
        self._lock = Lock()
        self._observer = FabricMemoryObserver(self.path, self.state_path)
        with closing(self._connect()) as con:
            with con:
                con.execute("""CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    features TEXT NOT NULL,
                    tagger TEXT NOT NULL,
                    recorded_utc TEXT NOT NULL
                )""")

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path, timeout=7)
        con.execute("PRAGMA busy_timeout=7000")
        return con

    def learn(self, classified: dict[str, Any]) -> dict[str, Any]:
        """Append ONLY a valid model-generated topic vector, then train ACF.

        A successful SQLite commit with failed checkpoint sync is replayed
        from the same event on restart. No source text ever reaches storage.
        """
        if type(classified) is not dict or set(classified) != {
                "axes", "version", "model", "inference",
                "cloud_api_used", "raw_text_persisted"}:
            raise ValueError("Invalid semantic classifier attestation.")
        if (classified["version"] != VERSION
                or classified["model"] != "Qwen3-1.7B-Q4_K_M"
                or classified["inference"] != "actual_local_gguf_semantic_classification"
                or classified["cloud_api_used"] is not False
                or classified["raw_text_persisted"] is not False):
            raise ValueError("Only real local verified Qwen semantic inference accepted.")
        axes = _sample(classified["axes"], 8)
        if any(value not in (0.0, 1.0) for value in axes):
            raise ValueError("Semantic features must use audited binary axes.")
        with self._lock:
            with closing(self._connect()) as con:
                with con:
                    row = con.execute("SELECT COUNT(*) FROM observations").fetchone()
                    if row[0] >= MAX_EVENTS:
                        raise ValueError("Semantic ACF ledger is full.")
                    con.execute(
                        "INSERT INTO observations(features,tagger,recorded_utc)"
                        " VALUES(?,?,?)",
                        (json.dumps(axes, separators=(",", ":")), VERSION,
                         datetime.now(timezone.utc).isoformat()))
            result = self._observer.poll(limit=96)
        return result

    def sync(self, limit: int = 96) -> dict[str, Any]:
        return self._observer.poll(limit=limit)

    def prepare_next_topic(self, knowledge: LocalKnowledge) -> dict[str, Any]:
        """Autonomously decide and, only when measured advantage is adequate,
        read approved LOCAL indexed material for the next predicted topic.
        Returns counts and measurements, never private file names or bodies.
        """
        with self._lock:
            fabric = (AdaptiveCognitiveFabric.load(self.state_path)
                      if self.state_path.is_file()
                      else AdaptiveCognitiveFabric())
            return prepare_local_sources(fabric, knowledge).public()

    def status(self) -> dict[str, Any]:
        data = self._observer.status()
        with closing(self._connect()) as con:
            n = con.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        return {"source": VERSION, "observations_stored": n,
                "model": data, "no_raw_text_stored": True}
