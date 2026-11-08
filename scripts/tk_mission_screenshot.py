"""Best-effort true Windows screenshot of the PUBLIC Tk Mission dashboard.

Only isolated synthetic SQLite. No user home folders or private data are read.
For interactive Windows CI runners; skipped with a diagnostic if image capture
is unavailable in non-interactive sessions. The real UI smoke is separately
a mandatory test, independent of screenshot generation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import tempfile
import tkinter as tk

from neurogenesis.desktop import process_message
from neurogenesis.memory import ExperienceMemory
from neurogenesis.tk_mission import MissionDashboard
from neurogenesis.web_sense import WebObservation


def capture(output: Path, avatar_output: Path | None = None) -> bool:
    if sys.platform != "win32":
        raise RuntimeError("Windows screenshot only")
    try:
        from PIL import ImageGrab, ImageStat
    except ImportError as exc:
        raise RuntimeError("Pillow needed for CI screenshot") from exc

    with tempfile.TemporaryDirectory(prefix="ng-tk-screen-fiction-") as directory:
        memory = ExperienceMemory(Path(directory) / "fictional-only.sqlite3")
        text = "Fikcyjne źródło zawierające pojęcia neuron, pamięć i sygnał."
        memory.observe_web(WebObservation(
            url="https://example.org/fictional-preview",
            host="example.org",
            text=text, content_sha256=hashlib.sha256(text.encode()).hexdigest(),
            retrieved_utc=datetime(2026, 11, 8, tzinfo=timezone.utc).isoformat(),
            bytes_read=len(text.encode())))
        for i in range(7):
            process_message(memory, f"Fikcyjny sygnał ekranowy numer {i + 1}")
        root = tk.Tk()
        # GitHub-hosted Windows uses a virtual 1024px desktop in some jobs.
        # Do not screenshot a huge offscreen window and mistake cropping for
        # a bug in the application's responsive page.
        virtual_width = max(720, root.winfo_screenwidth() - 24)
        virtual_height = max(520, root.winfo_screenheight() - 92)
        root.geometry(
            f"{min(1450, virtual_width)}x{min(920, virtual_height)}+8+8")
        root.title("NeuroGenesis / Mission Control — synthetic QA only")
        root.configure(bg="#07111d")
        try:
            view = MissionDashboard(
                root, memory,
                navigate=lambda _where: None,
                network_enabled=lambda: False)
            root.update_idletasks()
            view.refresh()
            root.update()
            root.lift()
            root.attributes("-topmost", True)
            root.update()
            root.attributes("-topmost", False)
            if memory.status()["knowledge"]["documents"] != 1 or not view._last:
                raise AssertionError("Synthetic GUI has not rendered actual SQLite")
            x = root.winfo_rootx()
            y = root.winfo_rooty()
            w = root.winfo_width()
            h = root.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            print(f"Tk screenshot captured: {img.width}x{img.height}, "
                  f"window={w}x{h}, screen={root.winfo_screenwidth()}x{root.winfo_screenheight()}",
                  flush=True)
            if img.width < 640 or img.height < 420:
                raise RuntimeError("Windows screenshot dimensions unexpectedly small")
            measured = ImageStat.Stat(img.convert("RGB")).stddev
            if max(measured) < 12:
                raise RuntimeError("Desktop session did not yield a visible GUI screenshot")
            output.parent.mkdir(parents=True, exist_ok=True)
            img.save(str(output), "PNG")
            if avatar_output is not None:
                view._toggle_avatar_view()
                root.update_idletasks()
                root.update()
                if view._view_mode != "avatar" or view.avatar.latest is None:
                    raise AssertionError("Real avatar not connected to saved LIF state")
                avatar_image = ImageGrab.grab(bbox=(x, y, x+w, y+h))
                if avatar_image.size != img.size:
                    raise AssertionError("Avatar screenshot resized unexpectedly")
                if max(ImageStat.Stat(avatar_image.convert("RGB")).stddev) < 12:
                    raise RuntimeError("Avatar view did not render a visible GUI")
                avatar_output.parent.mkdir(parents=True, exist_ok=True)
                avatar_image.save(str(avatar_output), "PNG")
                if avatar_output.stat().st_size < 20_000:
                    raise RuntimeError("Real avatar screenshot suspiciously small")
            return output.stat().st_size > 25_000
        finally:
            root.destroy()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture real Tk dashboard, fictional SQLite only")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--avatar-output", type=Path,
                        help="capture actual avatar mode on synthetic SQLite, too")
    args = parser.parse_args(argv)
    if not capture(args.output, args.avatar_output):
        raise SystemExit("No valid screenshot produced")
    print("Public Windows Tk Mission Control visual QA: real UI, fictional data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
