"""Autonomous learning bridge from REAL persisted experience features to ACF.

Read-only reads the existing ExperienceMemory observations table. Learns from
8-dimensional hashed TextSensor features only: NEVER requests raw_text,
URLs, conversation prompts, private source bodies or remote services.

Checkpoint and observation cursor advance atomically in a single separate
file; a crash before the atomic rename replays uncommitted events next run.
The existing brain/predictor SQLite is NEVER modified by this experiment.
"""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Any

from .acf import AdaptiveCognitiveFabric, _sample


class FabricMemoryObserver:
    """Poll a pre-existing real SQLite memory for new sensory events."""

    def __init__(self, memory_path: str | Path, snapshot_path: str | Path):
        self.memory_path = Path(memory_path)
        self.snapshot_path = Path(snapshot_path)
        if self.memory_path.resolve() == self.snapshot_path.resolve():
            raise ValueError("ACF snapshot must be separate from existing memory.")
        self._lock = Lock()

    def poll(self, *, limit: int = 96) -> dict[str, Any]:
        if type(limit) is not int or not 1 <= limit <= 256:
            raise ValueError("ACF poll limit must be 1..256 events.")
        with self._lock:
            fabric = (AdaptiveCognitiveFabric.load(self.snapshot_path)
                      if self.snapshot_path.is_file()
                      else AdaptiveCognitiveFabric())
            if not self.memory_path.is_file() or self.memory_path.is_symlink():
                return {"processed": 0, "status": "memory_not_yet_present",
                        "self_model": fabric.self_model()}
            with closing(sqlite3.connect(str(self.memory_path), timeout=8)) as con:
                con.execute("PRAGMA query_only=ON")
                con.execute("PRAGMA busy_timeout=8000")
                rows = con.execute(
                    "SELECT id, features FROM observations "
                    "WHERE id > ? ORDER BY id ASC LIMIT ?",
                    (fabric.last_event_id, limit)).fetchall()
            if not rows:
                return {"processed": 0, "status": "no_new_observations",
                        "self_model": fabric.self_model()}
            # Validate the ENTIRE batch BEFORE training or writing. An
            # invalid record must not advance the persisted event cursor.
            prepared: list[tuple[int, list[float]]] = []
            prior = fabric.last_event_id
            for event_id, raw_features in rows:
                if type(event_id) is not int or event_id <= prior:
                    raise ValueError("Invalid or nonmonotonic sensory event ID.")
                if type(raw_features) is not str or len(raw_features) > 1024:
                    raise ValueError("Oversized/malformed sensory feature record.")
                try:
                    decoded = json.loads(raw_features, parse_constant=lambda _x: None)
                except json.JSONDecodeError as exc:
                    raise ValueError("Malformed serialized sensory features.") from exc
                vector = _sample(decoded, fabric.width)
                prepared.append((event_id, vector))
                prior = event_id
            for event_id, vector in prepared:
                fabric.observe(vector)
                fabric.last_event_id = event_id
            # Includes both the last processed ID and all updated neural
            # states; interruption cannot commit one without the other.
            fabric.save(self.snapshot_path)
            return {
                "processed": len(prepared),
                "status": "updated_from_real_sensory_observations",
                "self_model": fabric.self_model(),
            }

    def status(self) -> dict[str, Any]:
        with self._lock:
            if not self.snapshot_path.is_file():
                return AdaptiveCognitiveFabric().self_model()
            return AdaptiveCognitiveFabric.load(self.snapshot_path).self_model()
