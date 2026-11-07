"""Bounded, transactional self-development of the *persisted* neural substrate.

This is a local experiment scheduler, NOT general intelligence or autonomous code
modification. It never reads raw conversation text or contacts the internet.
Fresh 40-event windows have disjoint, single-use training/selection/audit/guard
roles. The proven input is hashed sensory features, not linguistic semantics.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from threading import Event
from typing import Any

from .brain import Brain
from .memory import ExperienceMemory
from .predictor import NextInputPredictor
from .self_development import DevelopmentLimits, run_self_development_cycle


WINDOW = 40  # 8 prior-skill guard, 16 training, 8 selection, 8 audit
MAX_CYCLES = 200
MAX_CHECKPOINTS = 3


@dataclass(frozen=True)
class SupervisorConfig:
    """Operator-controlled bounds; a self-tuning candidate cannot edit them."""

    min_gain: float = 0.0001
    max_guard_regression: float = 0.002
    max_trials: int = 3
    interval_seconds: float = 30.0

    def __post_init__(self) -> None:
        for name, upper in (("min_gain", 1), ("max_guard_regression", 1)):
            value = getattr(self, name)
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= upper:
                raise ValueError("invalid " + name)
        if type(self.max_trials) is not int or not 2 <= self.max_trials <= 5:
            raise ValueError("max_trials must be in [2, 5]")
        if type(self.interval_seconds) not in (int, float) or not math.isfinite(self.interval_seconds) or not 1 <= self.interval_seconds <= 3600:
            raise ValueError("interval_seconds must be in [1, 3600]")


def _dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _tables(con: sqlite3.Connection) -> None:
    con.execute("""CREATE TABLE IF NOT EXISTS autonomy_meta (
        id INTEGER PRIMARY KEY CHECK(id=1), last_event_id INTEGER NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS autonomy_cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT, recorded_utc TEXT NOT NULL,
        last_event_id INTEGER NOT NULL, promoted INTEGER NOT NULL,
        report_json TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS predictor_state (
        id INTEGER PRIMARY KEY CHECK(id=1), predictor_json TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS autonomy_checkpoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_utc TEXT NOT NULL,
        before_brain_json TEXT NOT NULL, before_predictor_json TEXT,
        after_brain_sha256 TEXT NOT NULL, event_id INTEGER NOT NULL,
        active INTEGER NOT NULL CHECK(active IN (0,1))
    )""")


def _checked_samples(rows: list[tuple[int, str]], width: int) -> list[tuple[float, ...]]:
    samples = []
    for _, packed in rows:
        if type(packed) is not str or len(packed) > 100_000:
            raise ValueError("invalid saved sensory features")
        try:
            data = json.loads(packed, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite feature")))
        except json.JSONDecodeError as exc:
            raise ValueError("invalid saved sensory features") from exc
        if type(data) is not list or len(data) != width:
            raise ValueError("stored feature dimensions differ from current brain")
        if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in data):
            raise ValueError("stored sensory features outside [0,1]")
        samples.append(tuple(float(v) for v in data))
    return samples


class AutonomicSupervisor:
    """Periodically test candidate predictors using private, single-use events.

    A successful proposal persists the updated predictor AND its internal brain
    to one SQLite transaction. A failed proposal does not change either.
    """

    def __init__(self, memory: ExperienceMemory | str | Path, *,
                 config: SupervisorConfig | None = None) -> None:
        self.memory = memory if isinstance(memory, ExperienceMemory) else ExperienceMemory(memory)
        self.config = SupervisorConfig() if config is None else config
        if not isinstance(self.config, SupervisorConfig):
            raise TypeError("config must be SupervisorConfig")

    def status(self) -> dict[str, Any]:
        with closing(self.memory._connect()) as con:
            brain = self.memory._brain_from_connection(con)  # corruption fails closed
            count = con.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
            if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='autonomy_meta'").fetchone():
                return {"brain_steps": brain.steps, "observations": count, "new_events": count,
                        "needed_for_trial": WINDOW, "cycles": 0, "promotions": 0,
                        "last_report": None, "auto_enabled": False}
            row = con.execute("SELECT last_event_id FROM autonomy_meta WHERE id=1").fetchone()
            last_id = row[0] if row is not None else 0
            new_count = con.execute("SELECT COUNT(*) FROM observations WHERE id>?", (last_id,)).fetchone()[0]
            cycles, promotions = con.execute(
                "SELECT COUNT(*), COALESCE(SUM(promoted),0) FROM autonomy_cycles").fetchone()
            latest = con.execute("SELECT report_json FROM autonomy_cycles ORDER BY id DESC LIMIT 1").fetchone()
            last_report = json.loads(latest[0]) if latest else None
            return {"brain_steps": brain.steps, "observations": count,
                    "new_events": new_count, "needed_for_trial": WINDOW,
                    "cycles": cycles, "promotions": promotions,
                    "last_report": last_report, "auto_enabled": False}

    def cycle(self) -> dict[str, Any]:
        """Run one bounded trial only after 40 *fresh* observations.

        SQLite IMMEDIATE transaction serializes this operation with remember();
        on validation failure the transaction rolls back without losing events.
        """
        with closing(self.memory._connect()) as con:
            with con:
                con.execute("BEGIN IMMEDIATE")
                brain = self.memory._brain_from_connection(con)
                _tables(con)
                row = con.execute("SELECT last_event_id FROM autonomy_meta WHERE id=1").fetchone()
                last_id = row[0] if row is not None else 0
                rows = con.execute("SELECT id,features FROM observations WHERE id>? ORDER BY id LIMIT ?",
                                   (last_id, WINDOW)).fetchall()
                if len(rows) < WINDOW:
                    return {"promoted": False, "reason": "not_enough_new_experiences",
                            "available": len(rows), "required": WINDOW,
                            "brain_unchanged": True}
                samples = _checked_samples(rows, brain.config.input_size)
                stored = con.execute("SELECT predictor_json FROM predictor_state WHERE id=1").fetchone()
                if stored:
                    raw = stored[0]
                    if type(raw) is not str or len(raw.encode("utf-8")) > Brain.MAX_STATE_BYTES:
                        raise ValueError("stored predictor exceeds size limit")
                    try:
                        predictor = NextInputPredictor.from_dict(json.loads(
                            raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid predictor number"))))
                    except (TypeError, json.JSONDecodeError) as exc:
                        raise ValueError("invalid stored predictor") from exc
                    if predictor.brain.to_dict() != brain.to_dict():
                        raise ValueError("predictor/brain divergence: refusing update")
                else:
                    predictor = NextInputPredictor(brain)

                limits = DevelopmentLimits(min_gain=self.config.min_gain,
                                           max_guard_regression=self.config.max_guard_regression,
                                           max_trials=self.config.max_trials,
                                           max_neurons_increase=0,
                                           max_synapses_increase=0,
                                           max_samples_per_stream=WINDOW)
                proposed, report = run_self_development_cycle(
                    predictor,
                    retained_skill=samples[:8],
                    training=samples[8:24],
                    selection=samples[24:32],
                    audit=samples[32:40],
                    limits=limits)
                accepted = report["promoted"] is True
                end_id = rows[-1][0]
                out = dict(report)
                out.update({"last_event_id": end_id, "window_events": WINDOW,
                            "input_type": "local hashed sensory features",
                            "audit_scope": ("not reused for supervisor selection; however the "
                                            "live neural substrate previously processed all events "
                                            "during remember(), so this is not a strictly unseen "
                                            "substrate holdout or OOD generalization test"),
                            "brain_unchanged": not accepted,
                            "no_raw_text_read": True})
                if accepted:
                    original_brain = _dump(brain.to_dict())
                    after_brain = _dump(proposed.brain.to_dict())
                    after_predictor = _dump(proposed.to_dict())
                    if (len(after_brain.encode("utf-8")) > Brain.MAX_STATE_BYTES or
                            len(after_predictor.encode("utf-8")) > Brain.MAX_STATE_BYTES):
                        raise ValueError("trial exceeds saved state limit")
                    con.execute("INSERT INTO autonomy_checkpoints "
                                "(created_utc,before_brain_json,before_predictor_json,"
                                "after_brain_sha256,event_id,active) VALUES(?,?,?,?,?,1)",
                                (datetime.now(timezone.utc).isoformat(), original_brain,
                                 stored[0] if stored else None, _sha(after_brain), end_id))
                    con.execute("INSERT INTO neural_state(id,brain_json) VALUES(1,?) "
                                "ON CONFLICT(id) DO UPDATE SET brain_json=excluded.brain_json",
                                (after_brain,))
                    con.execute("INSERT INTO predictor_state(id,predictor_json) VALUES(1,?) "
                                "ON CONFLICT(id) DO UPDATE SET predictor_json=excluded.predictor_json",
                                (after_predictor,))
                    con.execute("DELETE FROM autonomy_checkpoints WHERE id NOT IN "
                                "(SELECT id FROM autonomy_checkpoints ORDER BY id DESC LIMIT ?)",
                                (MAX_CHECKPOINTS,))
                con.execute("INSERT INTO autonomy_meta(id,last_event_id) VALUES(1,?) "
                            "ON CONFLICT(id) DO UPDATE SET last_event_id=excluded.last_event_id", (end_id,))
                con.execute("INSERT INTO autonomy_cycles(recorded_utc,last_event_id,promoted,report_json)"
                            " VALUES(?,?,?,?)",
                            (datetime.now(timezone.utc).isoformat(), end_id, int(accepted), _dump(out)))
                con.execute("DELETE FROM autonomy_cycles WHERE id NOT IN "
                            "(SELECT id FROM autonomy_cycles ORDER BY id DESC LIMIT ?)", (MAX_CYCLES,))
                return out

    def rollback_last_promotion(self) -> bool:
        """Restore exact prior brain/readout, only if neither has changed since.

        Rejects attempts to roll back after further experience: that would
        discard newly learned state. The event ledger is never rewritten.
        """
        with closing(self.memory._connect()) as con:
            with con:
                con.execute("BEGIN IMMEDIATE")
                brain = self.memory._brain_from_connection(con)
                if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='autonomy_checkpoints'").fetchone():
                    return False
                row = con.execute("SELECT id,before_brain_json,before_predictor_json,"
                                  "after_brain_sha256,event_id FROM autonomy_checkpoints "
                                  "WHERE active=1 ORDER BY id DESC LIMIT 1").fetchone()
                if row is None:
                    return False
                cid, before, old_predictor, after_digest, event_id = row
                current = _dump(brain.to_dict())
                if _sha(current) != after_digest:
                    raise ValueError("brain advanced since promotion: rollback would lose experience")
                saved = con.execute("SELECT predictor_json FROM predictor_state WHERE id=1").fetchone()
                if not saved:
                    raise ValueError("predictor missing: cannot safely rollback")
                current_predictor = NextInputPredictor.from_dict(json.loads(saved[0]))
                if current_predictor.brain.to_dict() != brain.to_dict():
                    raise ValueError("predictor/brain divergence: cannot rollback")
                Brain.from_dict(json.loads(before))
                if old_predictor is not None:
                    prev = NextInputPredictor.from_dict(json.loads(old_predictor))
                    if prev.brain.to_dict() != Brain.from_dict(json.loads(before)).to_dict():
                        raise ValueError("prior checkpoint mismatch")
                con.execute("UPDATE neural_state SET brain_json=? WHERE id=1", (before,))
                if old_predictor is None:
                    con.execute("DELETE FROM predictor_state WHERE id=1")
                else:
                    con.execute("UPDATE predictor_state SET predictor_json=? WHERE id=1", (old_predictor,))
                con.execute("UPDATE autonomy_checkpoints SET active=0 WHERE id=?", (cid,))
                # New observations after the last promotion are not removed, but
                # digest matching prevents rollback if they affected brain state.
                return True

    def run_until_stopped(self, stop: Event) -> None:
        """Local opt-in periodic loop; no worker starts just by importing."""

        if not isinstance(stop, Event):
            raise TypeError("stop must be threading.Event")
        while not stop.is_set():
            self.cycle()
            stop.wait(self.config.interval_seconds)
