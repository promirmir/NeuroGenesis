"""Render the real Qt Mission Control using ONLY an isolated fictional SQLite fixture.

This is an offscreen visual smoke artifact for human UI review, not a
screenshot of a user's data, a production benchmark or simulated AGI.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import tempfile

from PySide6.QtWidgets import QApplication

from neurogenesis.command_service import CommandService
from neurogenesis.command_center import CommandCenter
from neurogenesis.web_sense import WebObservation


def render(output: Path) -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    if os.name == "nt":
        # Windows CI uses the Qt "offscreen" platform. Unlike the normal
        # Windows plugin it may lack an enumerated system font database,
        # causing square glyphs in a real QWidget screenshot. Load an
        # INSTALLED local Windows font for this CI screenshot ONLY.
        # Never bundle, publish or copy the font file.
        from PySide6.QtGui import QFontDatabase
        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        for font_name in ("segoeui.ttf", "arial.ttf"):
            path = windir / "Fonts" / font_name
            if path.is_file() and QFontDatabase.addApplicationFont(str(path)) >= 0:
                break
    with tempfile.TemporaryDirectory(prefix="ng-mission-preview-") as folder:
        service = CommandService(Path(folder) / "fictional-test-memory.sqlite3")
        evidence = "Syntetyczny dokument testowy: pamięć, synapsy i plastyczność neuronowa."
        raw = evidence.encode("utf-8")
        service.memory.observe_web(WebObservation(
            url="https://example.org/fictional-local-test",
            host="example.org",
            text=evidence,
            content_sha256=hashlib.sha256(raw).hexdigest(),
            retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
            bytes_read=len(raw),
        ))
        for number in range(9):
            service.ask(f"Syntetyczny bodziec neuronowy dla testu interfejsu nr {number+1}")
        window = CommandCenter(service)
        window.resize(1560, 960)
        window.show()
        window.navigate(0)
        window.refresh()
        app.processEvents()
        window.refresh_connectome()
        app.processEvents()
        assert not service.network_enabled
        assert window.mission_tiles["documents"].value_label.text() == "1"
        assert window.mission_connectome.snapshot.step == service.memory.brain().steps
        output.parent.mkdir(parents=True, exist_ok=True)
        if not window.grab().save(str(output), "PNG"):
            raise RuntimeError("Qt offscreen render failed")
        window.close()
    if output.stat().st_size < 10_000 or output.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Qt preview artifact invalid")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline screenshot smoke from fictional data only")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    render(args.output)
    print("Mission Control Qt screenshot: fictional fixture only, no private data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
