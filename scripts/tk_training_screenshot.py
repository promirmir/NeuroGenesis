"""Visual QA of the ACTUAL two new public Tk tabs on Windows CI.

Never opens a real user memory/database, never downloads datasets or weights,
and never starts a training subprocess. The separate frozen --ui-self-test
checks source and executable widget behavior.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk

from neurogenesis.tk_bundled_chat import install_bundled_chat
from neurogenesis.tk_bundled_training import install_bundled_training
from neurogenesis.local_knowledge import LocalKnowledge
import tempfile
from neurogenesis.tk_theme import apply_dark_tk_theme


def capture(training_output: Path, model_chat_output: Path) -> bool:
    if sys.platform != "win32":
        raise RuntimeError("Windows screenshots only")
    try:
        from PIL import ImageGrab, ImageStat
    except ImportError as exc:
        raise RuntimeError("Pillow is required for Windows screenshots") from exc
    folder = tempfile.TemporaryDirectory(prefix="ng-public-visual-fixture-")
    root = tk.Tk()
    try:
        knowledge = LocalKnowledge(Path(folder.name) / "fictional-local.sqlite3")
        apply_dark_tk_theme(root)
        width = min(1250, max(760, root.winfo_screenwidth() - 24))
        height = min(850, max(540, root.winfo_screenheight() - 92))
        root.geometry(f"{width}x{height}+8+8")
        root.configure(bg="#07111d")
        root.title("NeuroGenesis / Real offline training and Model Chat visual QA")
        tabs = ttk.Notebook(root)
        tabs.pack(fill="both", expand=True, padx=10, pady=12)
        mission = ttk.Frame(tabs)
        tabs.add(mission, text="CENTRUM")
        training = install_bundled_training(tabs, knowledge)
        chat = install_bundled_chat(tabs, knowledge)
        if tabs.index(training) != 1 or tabs.index(chat) != 2:
            raise AssertionError("New training/chat tabs aren't visible near CENTRUM")
        def screen(tab, path):
            tabs.select(tab)
            root.update_idletasks()
            root.update()
            root.lift()
            root.attributes("-topmost", True)
            root.update()
            root.attributes("-topmost", False)
            a = (root.winfo_rootx(), root.winfo_rooty())
            b = (a[0] + root.winfo_width(), a[1] + root.winfo_height())
            shot = ImageGrab.grab(bbox=(*a, *b))
            if min(shot.size) < 500 or max(ImageStat.Stat(shot.convert("RGB")).stddev) < 12:
                raise RuntimeError("Screen capture did not contain a visible real Tk tab")
            path.parent.mkdir(parents=True, exist_ok=True)
            shot.save(str(path))
            if path.stat().st_size < 12_000:
                raise RuntimeError("Unexpectedly empty screenshot")
        screen(training, training_output)
        screen(chat, model_chat_output)
        # Validate that the actions needed for a REAL conversation remain
        # visible on constrained Windows hosted desktop dimensions.
        def find_action(widget, label):
            if widget.winfo_class() == "TButton" and widget.cget("text") == label:
                return widget
            for child in widget.winfo_children():
                found = find_action(child, label)
                if found is not None:
                    return found
            return None
        for label in ("WYŚLIJ WIADOMOŚĆ", "STOP", "NOWA ROZMOWA"):
            btn = find_action(chat, label)
            if (btn is None or not btn.winfo_ismapped() or
                    btn.winfo_rooty() + btn.winfo_height() > root.winfo_rooty() + root.winfo_height() - 3):
                raise RuntimeError("Model Chat button is outside the visible desktop: " + label)
        return True
    finally:
        root.destroy()
        folder.cleanup()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Actual Windows Tk training and offline model chat screenshot")
    parser.add_argument("--training-output", type=Path, required=True)
    parser.add_argument("--model-chat-output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not capture(args.training_output, args.model_chat_output):
        return 1
    print("Actual Tk training/chat visual QA: isolated UI; no files, models, or network")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
