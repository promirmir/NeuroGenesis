"""Offline, non-destructive snapshots and integrity checks of private SQLite.

Copies every committed source, brain state, manual teaching and rights revision
using SQLite's transactional backup API. No upload, network or automatic restore.
Destination is committed using an atomic *no-overwrite* same-directory hardlink.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
from typing import Any

from .brain import Brain


_REQUIRED_TABLES = frozenset((
    "metadata", "observations", "neural_state", "taught_responses",
    "web_observations", "knowledge_sources", "knowledge_passages",
    "knowledge_rights_audit",
))
_MAX_SNAPSHOT_SIZE = 2 * 1024 * 1024 * 1024


def _file(path: str | Path) -> Path:
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.suffix.lower() != ".sqlite3":
        raise ValueError("expected an existing regular local .sqlite3 database (no symlink)")
    if not 0 < p.stat().st_size <= _MAX_SNAPSHOT_SIZE:
        raise ValueError("database exceeds safe snapshot size limit")
    return p


def _target(path: str | Path, source: Path) -> Path:
    p = Path(path)
    if (p.suffix.lower() != ".sqlite3" or p.is_symlink()
            or p.exists() or not p.parent.is_dir() or p.parent.is_symlink()):
        raise ValueError("output must be a NEW local .sqlite3 file in an existing directory")
    if p.resolve() == source.resolve():
        raise ValueError("refusing to replace the source database")
    return p


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as inp:
        for part in iter(lambda: inp.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def inspect_private_database(path: str | Path, *,
                             expected_sha256: str | None = None) -> dict[str, Any]:
    """Verify a database read-only, without migrations or touching live state."""
    p = _file(path)
    if expected_sha256 is not None:
        if type(expected_sha256) is not str or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            raise ValueError("expected checksum must be 64 lowercase hexadecimal characters")
    digest = _sha256(p)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("snapshot SHA-256 mismatch")
    uri = p.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as con:
        con.execute("PRAGMA query_only=ON")
        if con.execute("PRAGMA quick_check").fetchone() != ("ok",):
            raise ValueError("SQLite quick_check failed")
        existing = {row[0] for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        if not _REQUIRED_TABLES.issubset(existing):
            raise ValueError("missing required private memory tables")
        version = con.execute(
            "SELECT value FROM metadata WHERE key='schema'").fetchone()
        if version != ("1",):
            raise ValueError("unsupported private memory schema")
        observations = con.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        row = con.execute("SELECT brain_json FROM neural_state WHERE id=1").fetchone()
        if row is None and observations:
            raise ValueError("brain snapshot missing despite persisted observations")
        if row is not None:
            def reject_constant(value: str) -> None:
                raise ValueError("invalid numerical constant in brain snapshot")
            try:
                state = json.loads(row[0], parse_constant=reject_constant)
                Brain.from_dict(state)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError("stored brain snapshot failed validation") from exc
        result = {
            "integrity": "ok",
            "schema": 1,
            "size_bytes": p.stat().st_size,
            "sha256": digest,
            "observations": observations,
            "teachings": con.execute(
                "SELECT COUNT(*) FROM taught_responses").fetchone()[0],
            "source_versions": con.execute(
                "SELECT COUNT(*) FROM knowledge_sources").fetchone()[0],
            "passages": con.execute(
                "SELECT COUNT(*) FROM knowledge_passages").fetchone()[0],
            "training_rights_events": con.execute(
                "SELECT COUNT(*) FROM knowledge_rights_audit").fetchone()[0],
            "network_used": False,
            "database_modified": False,
        }
    return result


def _publish_no_replace(staging: Path, destination: Path) -> None:
    """Single atomic directory entry creation; never overwrite user data.

    Staging and destination are siblings on the same filesystem. NTFS and
    normal POSIX filesystems support atomic hardlinks. If the filesystem does
    not, fail closed; never fall back to partial-file copy or overwrite.
    """
    os.link(staging, destination)


def backup_private_database(source: str | Path, destination: str | Path
                            ) -> dict[str, Any]:
    """Copy a consistent live SQLite snapshot, including its committed WAL."""
    original = _file(source)
    output = _target(destination, original)
    # Always inspect the source first, so corruption never becomes a false
    # "verified good" backup. No schema migration occurs in this operation.
    inspect_private_database(original)
    fd, temp_name = tempfile.mkstemp(
        prefix=".neurogenesis-backup-", suffix=".sqlite3", dir=output.parent)
    os.close(fd)
    staging = Path(temp_name)
    try:
        uri = original.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=5)) as source_con:
            with closing(sqlite3.connect(staging)) as dest_con:
                source_con.backup(dest_con, pages=64, sleep=0.1)
                dest_con.commit()
        os.chmod(staging, 0o600)
        result = inspect_private_database(staging)
        if output.is_symlink() or output.exists():
            raise FileExistsError("destination already exists; refusing overwrite")
        _publish_no_replace(staging, output)
        return {**result, "new_backup_created": True,
                "original_modified": False, "upload_performed": False}
    finally:
        staging.unlink(missing_ok=True)


def restore_to_new_database(backup: str | Path, destination: str | Path, *,
                            confirmed: bool = False) -> dict[str, Any]:
    """Prepare a restored COPY as a new file; never overwrite live SQLite."""
    if confirmed is not True:
        raise PermissionError("explicit operator restoration confirmation required")
    prior = _file(backup)
    original_check = inspect_private_database(prior)
    target = _target(destination, prior)
    fd, temp_name = tempfile.mkstemp(
        prefix=".neurogenesis-restore-", suffix=".sqlite3", dir=target.parent)
    os.close(fd)
    staging = Path(temp_name)
    try:
        with prior.open("rb") as inp, staging.open("wb") as out:
            shutil.copyfileobj(inp, out, length=1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(staging, 0o600)
        restored = inspect_private_database(
            staging, expected_sha256=original_check["sha256"])
        if target.is_symlink() or target.exists():
            raise FileExistsError("refusing to overwrite existing private memory")
        _publish_no_replace(staging, target)
        return {**restored, "restored_to_new_path_only": True,
                "original_modified": False, "network_used": False}
    finally:
        staging.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline transactional private-memory backup, verify or restore to a NEW file")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--backup", type=Path, help="Live local private SQLite source")
    mode.add_argument("--verify", type=Path, help="Existing private SQLite snapshot")
    mode.add_argument("--restore", type=Path, help="Existing verified backup")
    parser.add_argument("--output", type=Path, help="Fresh .sqlite3 output (never overwrite)")
    parser.add_argument("--expected-sha256", help="Optional checksum when verifying")
    parser.add_argument("--confirm-restore-new", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.backup is not None:
            if args.output is None:
                parser.error("--output is required for backup")
            report = backup_private_database(args.backup, args.output)
        elif args.restore is not None:
            if args.output is None:
                parser.error("--output is required for restoration")
            report = restore_to_new_database(
                args.restore, args.output, confirmed=args.confirm_restore_new)
        else:
            report = inspect_private_database(
                args.verify, expected_sha256=args.expected_sha256)
    except (sqlite3.DatabaseError, ValueError, PermissionError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
