"""Autonomous ACF learning from pre-existing, real persisted feature rows.

Maintains a bounded *previous-valid* neural checkpoint in addition to the
atomic primary snapshot. If the primary JSON is corrupt, recovery uses ONLY
a schema-valid prior whose cursor is consistent with the original SQLite
observation ledger, quarantines the damaged bytes (no overwrite), and replays
uncommitted observations. This is crash recovery, NOT independent repair of
learned ability, restored deleted data, or autonomous code mutation.

No conversation text, source bodies, network, or original SQLite writes.
"""
from __future__ import annotations

from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Any

from .acf import AdaptiveCognitiveFabric, _sample
from .acf_semantics import VERSION as SEMANTIC_VERSION


class FabricMemoryObserver:
    """Bounded replay of a persisted feature ledger with checkpoint recovery.

    The per-instance mutex protects threads using *this* observer. A
    read-and-compare guard detects many interprocess snapshot conflicts;
    it is NOT a cross-process transaction. Keep one active application owner
    for this ACF state.
    """

    def __init__(self, memory_path: str | Path, snapshot_path: str | Path):
        self.memory_path = Path(memory_path)
        self.snapshot_path = Path(snapshot_path)
        if self.memory_path.resolve() == self.snapshot_path.resolve():
            raise ValueError("ACF snapshot must be separate from existing memory.")
        self.previous_path = self.snapshot_path.with_name(
            self.snapshot_path.name + ".previous")
        self.quarantine_path = self.snapshot_path.with_name(
            self.snapshot_path.name + ".corrupt")
        self._lock = Lock()

    def _hash_primary(self) -> str | None:
        if self.snapshot_path.is_symlink():
            raise ValueError("ACF snapshot symlinks are forbidden.")
        if not self.snapshot_path.exists():
            return None
        if not self.snapshot_path.is_file():
            raise ValueError("ACF snapshot must be a regular file.")
        if self.snapshot_path.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("Oversized ACF checkpoint.")
        return hashlib.sha256(self.snapshot_path.read_bytes()).hexdigest()

    def _verify_prior_ledger(self, fabric: AdaptiveCognitiveFabric) -> None:
        """Refuse a prior whose trained cursor does not match observed rows."""
        if (not self.memory_path.is_file() or self.memory_path.is_symlink()
                or fabric.events < 1 or fabric.last_event_id < 1):
            raise ValueError("Recovery requires existing actual observation ledger.")
        uri = self.memory_path.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=6)) as con:
            con.execute("PRAGMA query_only=ON")
            n, last = con.execute(
                "SELECT COUNT(*), MAX(id) FROM observations WHERE id <= ?",
                (fabric.last_event_id,)).fetchone()
            if n != fabric.events or last != fabric.last_event_id:
                raise ValueError("Previous checkpoint cursor disagrees with the ledger.")
            # Semantic ACF and hashed sensory ACF are distinct learning
            # channels. A semantic prior needs a matching Qwen tagger ledger.
            if self.memory_path.name == "semantic_fabric.sqlite3":
                incompatible, = con.execute(
                    "SELECT COUNT(*) FROM observations "
                    "WHERE id <= ? AND tagger <> ?",
                    (fabric.last_event_id, SEMANTIC_VERSION)).fetchone()
                if incompatible:
                    raise ValueError("Previous semantic Qwen provenance mismatch.")

    def _load_or_recover(self) -> tuple[AdaptiveCognitiveFabric, bool]:
        if (self.previous_path.is_symlink()
                or self.snapshot_path.is_symlink()):
            raise ValueError("ACF checkpoint links are forbidden.")
        original_error = None
        if self.snapshot_path.is_file():
            try:
                return AdaptiveCognitiveFabric.load(self.snapshot_path), False
            except (ValueError, TypeError, KeyError) as exc:
                original_error = exc
        elif self.snapshot_path.exists():
            raise ValueError("ACF snapshot is not a regular file.")
        elif not self.previous_path.is_file():
            return AdaptiveCognitiveFabric(), False
        # Recovery is impossible without a previous validated checkpoint.
        if not self.previous_path.is_file():
            raise ValueError("Corrupted ACF state; no verified prior available.") from original_error
        prior = AdaptiveCognitiveFabric.load(self.previous_path)
        self._verify_prior_ledger(prior)
        if self.snapshot_path.exists():
            # Exact damaged bytes remain available for operator inspection.
            # Atomic hardlink creation refuses overwriting a previous
            # quarantined failure; never silently destroy forensic evidence.
            if self.quarantine_path.is_symlink() or self.quarantine_path.exists():
                raise ValueError("ACF corrupt quarantine already exists.")
            os.link(self.snapshot_path, self.quarantine_path)
        prior.save(self.snapshot_path)
        return prior, True

    def poll(self, *, limit: int = 96) -> dict[str, Any]:
        if type(limit) is not int or not 1 <= limit <= 256:
            raise ValueError("ACF poll limit must be 1..256 events.")
        with self._lock:
            fabric, recovered = self._load_or_recover()
            before = self._hash_primary()
            if not self.memory_path.is_file() or self.memory_path.is_symlink():
                return {"processed": 0, "status": "memory_not_yet_present",
                        "checkpoint_recovered": recovered,
                        "self_model": fabric.self_model()}
            uri = self.memory_path.resolve().as_uri() + "?mode=ro"
            with closing(sqlite3.connect(uri, uri=True, timeout=8)) as con:
                con.execute("PRAGMA query_only=ON")
                con.execute("PRAGMA busy_timeout=8000")
                rows = con.execute(
                    "SELECT id, features FROM observations "
                    "WHERE id > ? ORDER BY id ASC LIMIT ?",
                    (fabric.last_event_id, limit)).fetchall()
            if not rows:
                return {"processed": 0, "status": "no_new_observations",
                        "checkpoint_recovered": recovered,
                        "self_model": fabric.self_model()}
            # Reject the entire batch before committing any learning/cursor.
            prepared: list[tuple[int, list[float]]] = []
            prior = fabric.last_event_id
            for event_id, raw_features in rows:
                if type(event_id) is not int or event_id <= prior:
                    raise ValueError("Invalid or nonmonotonic sensory event ID.")
                if type(raw_features) is not str or len(raw_features) > 1024:
                    raise ValueError("Oversized/malformed sensory feature record.")
                try:
                    decoded = json.loads(
                        raw_features,
                        parse_constant=lambda constant: (_ for _ in ()).throw(
                            ValueError("Nonfinite feature: " + constant)))
                except json.JSONDecodeError as exc:
                    raise ValueError("Malformed serialized sensory features.") from exc
                vector = _sample(decoded, fabric.width)
                prepared.append((event_id, vector))
                prior = event_id
            for event_id, vector in prepared:
                fabric.observe(vector)
                fabric.last_event_id = event_id
            # An optimistic change guard prevents most lost-update races when
            # two app instances read the SAME snapshot before updating it.
            if before != self._hash_primary():
                raise RuntimeError("ACF checkpoint changed concurrently; refusing stale update.")
            if before is not None:
                # Keep the *last validated old* state on disk before writing
                # the advanced state; the previous checkpoint is atomic too.
                # No user SQLite is modified by either snapshot.
                AdaptiveCognitiveFabric.load(self.snapshot_path).save(
                    self.previous_path)
                if before != self._hash_primary():
                    raise RuntimeError("ACF snapshot changed during backup.")
            fabric.save(self.snapshot_path)
            return {
                "processed": len(prepared),
                "status": "updated_from_real_sensory_observations",
                "checkpoint_recovered": recovered,
                "self_model": fabric.self_model(),
            }

    def status(self) -> dict[str, Any]:
        """Read only: never repair or overwrite files when merely inspecting."""
        with self._lock:
            if not self.snapshot_path.is_file():
                return AdaptiveCognitiveFabric().self_model()
            return AdaptiveCognitiveFabric.load(self.snapshot_path).self_model()
