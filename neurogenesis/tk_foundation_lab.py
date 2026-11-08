"""Explicit offline Foundation Brain inference lab for the REAL Tk Windows app.

The one-file EXE intentionally does NOT ship PyTorch. The operator chooses an
existing Python environment with this project + torch installed, an existing
trusted local checkpoint and a prompt. No untrusted checkpoint is loaded on
startup; no auto-download, training, web access or SQLite writes occur.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def make_inference_command(python_exe: str, checkpoint: str, *,
                           confirmed: bool, count: int, device: str,
                           prompt: str) -> list[str]:
    """Return a strict argv list. The private prompt goes via stdin only."""
    if confirmed is not True:
        raise PermissionError("Potwierdź, że checkpoint pochodzi z zaufanego źródła.")
    runtime = Path(python_exe)
    model = Path(checkpoint)
    if not runtime.is_file() or runtime.is_symlink():
        raise ValueError("Wybierz istniejący, zaufany plik wykonywalny Python.")
    if os.name == "nt" and runtime.suffix.lower() != ".exe":
        raise ValueError("Na Windows wybierz python.exe z przygotowanego środowiska.")
    if model.suffix.lower() not in {".pt", ".pth"} or not model.is_file() or model.is_symlink():
        raise ValueError("Wybierz istniejący zwykły plik .pt lub .pth.")
    if model.stat().st_size > 2 * 1024**3:
        raise ValueError("Checkpoint przekracza limit 2 GiB.")
    if type(count) is not int or not 1 <= count <= 64:
        raise ValueError("Dopuszczalne 1–64 bajty wyniku.")
    if device not in {"cpu", "cuda"}:
        raise ValueError("Urządzenie: cpu albo cuda.")
    if type(prompt) is not str or not 1 <= len(prompt) <= 512:
        raise ValueError("Prefiks powinien mieć 1–512 znaków.")
    raw = prompt.encode("utf-8")
    if not 2 <= len(raw) <= 2048:
        raise ValueError("Prefiks musi mieć 2–2048 bajtów UTF-8.")
    return [
        str(runtime), "-m", "neurogenesis.foundation_infer",
        "--checkpoint", str(model), "--prompt-stdin",
        "--confirm-local-checkpoint", "--bytes", str(count),
        "--device", device,
    ]


class FoundationLabWorker:
    """Subprocess is cancellable and runs outside the frozen Tk process."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.cancelled = threading.Event()
        self._lock = threading.Lock()

    def cancel(self) -> None:
        self.cancelled.set()
        with self._lock:
            p = self.process
        if p is not None and p.poll() is None:
            p.kill()

    def run(self, argv: list[str], prompt: str) -> dict:
        if self.cancelled.is_set():
            raise InterruptedError("Operacja anulowana przed startem.")
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8",
            startupinfo=startupinfo)
        with self._lock:
            self.process = process
        try:
            if self.cancelled.is_set():
                process.kill()
            try:
                stdout, stderr = process.communicate(prompt, timeout=120)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise TimeoutError("Przekroczono limit czasu eksperymentu.")
            if self.cancelled.is_set():
                raise InterruptedError("Eksperyment anulowany.")
            if process.returncode != 0:
                # CLI prints bounded errors; do not leak arbitrary huge logs.
                raise RuntimeError(
                    "Nie udało się uruchomić modelu. Sprawdź, czy wybrany Python "
                    "ma zainstalowane NeuroGenesis i PyTorch. "
                    + stderr[-400:].replace("\r", " ").replace("\n", " "))
            if len(stdout.encode("utf-8")) > 32_768:
                raise ValueError("Zbyt duży wynik eksperymentu.")
            report = json.loads(stdout)
            if (type(report) is not dict or
                    report.get("status") != "experimental_neural_byte_continuation" or
                    report.get("verified_natural_language_answer") is not False or
                    report.get("promoted_to_chat") is not False):
                raise ValueError("Nieprawidłowa odpowiedź eksperymentalnego pracownika.")
            return report
        finally:
            with self._lock:
                self.process = None


def install_foundation_lab(parent) -> ttk.Frame:
    """A genuine, operator-gated inference tab in default Windows Tk EXE."""
    tab = ttk.Frame(parent)
    parent.add(tab, text="Foundation Lab")
    bg = "#07111d"
    fg = "#d6f5fa"
    accent = "#6ee7df"

    title = tk.Label(tab, text="FOUNDATION BRAIN / PREDYKCJA Z WYUCZONYCH WAG",
                     bg=bg, fg=accent, font=("Segoe UI", 15, "bold"))
    title.pack(anchor="w", padx=18, pady=(18, 7))
    tk.Label(tab, bg=bg, fg="#aac6d3", wraplength=970, justify="left",
             text=("Odizolowane laboratorium rzeczywistego modelu GRU. Nie jest to "
                   "weryfikowana odpowiedź ani rozmowa. Publiczne EXE nie zawiera "
                   "PyTorch: wybierz lokalny Python z zainstalowanym neurogenesis i torch. "
                   "Nic nie pobieramy automatycznie, nie zmieniamy pamięci i nie "
                   "uruchamiamy niezaufanych checkpointów.")).pack(
                       anchor="w", padx=18, pady=(0, 12))
    python_path = tk.StringVar(value="" if getattr(sys, "frozen", False) else sys.executable)
    checkpoint = tk.StringVar()
    output_count = tk.StringVar(value="16")
    device = tk.StringVar(value="cpu")
    trusted = tk.BooleanVar(value=False)
    status = tk.StringVar(value="Brak operacji. Wybierz środowisko oraz checkpoint.")

    def chooser(var, title, kinds) -> None:
        selected = filedialog.askopenfilename(title=title, filetypes=kinds)
        if selected:
            var.set(selected)

    for header, target, kinds in (
        ("PYTHON / ŚRODOWISKO Z TORCH", python_path,
         [("Python", "*.exe"), ("Wszystkie pliki", "*")]),
        ("ZAUFANY CHECKPOINT .PT / .PTH", checkpoint,
         [("Checkpoint", "*.pt *.pth"), ("Wszystkie pliki", "*")]),
    ):
        tk.Label(tab, text=header, bg=bg, fg=accent,
                 font=("Consolas", 9, "bold")).pack(anchor="w", padx=18)
        row = ttk.Frame(tab)
        row.pack(fill="x", padx=18, pady=(3, 10))
        ttk.Entry(row, textvariable=target).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Wybierz", command=lambda v=target, h=header, k=kinds:
                   chooser(v, h, k)).pack(side="left", padx=(7, 0))

    tk.Label(tab, text="PREFIKS DO PREDYKCJI (TYLKO PAMIĘĆ PROCESU)",
             bg=bg, fg=accent, font=("Consolas", 9, "bold")).pack(anchor="w", padx=18)
    prompt = tk.Text(tab, height=3, wrap="word", bg="#0e2638", fg=fg,
                     insertbackground=accent, padx=10, pady=7)
    prompt.pack(fill="x", padx=18, pady=(4, 9))
    row = ttk.Frame(tab)
    row.pack(fill="x", padx=18, pady=(0, 8))
    ttk.Label(row, text="Generuj bajtów (1–64):").pack(side="left")
    ttk.Entry(row, width=6, textvariable=output_count).pack(side="left", padx=8)
    ttk.Label(row, text="Urządzenie:").pack(side="left", padx=(12, 2))
    ttk.Combobox(row, textvariable=device, values=("cpu", "cuda"),
                 width=7, state="readonly").pack(side="left", padx=8)
    ttk.Checkbutton(tab, text="Potwierdzam, że checkpoint jest lokalny i zaufany",
                    variable=trusted).pack(anchor="w", padx=18, pady=(0, 9))
    ttk.Label(tab, textvariable=status, wraplength=950).pack(
        fill="x", padx=18, pady=(2, 9))
    output = tk.Text(tab, height=11, bg="#0a1d2c", fg=fg,
                     font=("Consolas", 10), wrap="word", state="disabled")
    output.pack(fill="both", expand=True, padx=18, pady=(0, 12))
    buttons = ttk.Frame(tab)
    buttons.pack(fill="x", padx=18, pady=(0, 16))
    events = queue.SimpleQueue()
    current: dict[str, object] = {"thread": None, "worker": None}

    def set_result(text: str) -> None:
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.insert("end", text)
        output.configure(state="disabled")

    def start() -> None:
        running = current["thread"]
        if isinstance(running, threading.Thread) and running.is_alive():
            return
        text = prompt.get("1.0", "end-1c")
        try:
            argv = make_inference_command(
                python_path.get(), checkpoint.get(), confirmed=trusted.get(),
                count=int(output_count.get()), device=device.get(), prompt=text)
        except (OSError, ValueError, PermissionError) as exc:
            messagebox.showerror("Foundation Lab — kontrola dostępu", str(exc))
            return
        worker = FoundationLabWorker()
        current["worker"] = worker
        start_btn.configure(state="disabled")
        status.set("URUCHOMIONO / model oblicza predykcję we własnym procesie...")
        set_result("OBLICZANIE / brak wyniku do momentu ukończenia predykcji.")

        def operation():
            try:
                events.put(("ok", worker.run(argv, text)))
            except (OSError, RuntimeError, ValueError, InterruptedError, TimeoutError) as exc:
                events.put(("error", str(exc)))
        thread = threading.Thread(target=operation, daemon=True,
                                  name="NeuroGenesis-foundation-inference")
        current["thread"] = thread
        thread.start()

    def stop() -> None:
        worker = current["worker"]
        if isinstance(worker, FoundationLabWorker):
            worker.cancel()
            status.set("Anulowanie zewnętrznego obliczenia...")

    start_btn = ttk.Button(buttons, text="URUCHOM RZECZYWISTĄ PREDYKCJĘ",
                           command=start)
    start_btn.pack(side="left")
    ttk.Button(buttons, text="STOP", command=stop).pack(side="left", padx=9)

    def poll() -> None:
        try:
            while True:
                kind, value = events.get_nowait()
                current["worker"] = None
                start_btn.configure(state="normal")
                if kind != "ok":
                    status.set("BŁĄD / wynik eksperymentu niedostępny")
                    set_result(str(value))
                    continue
                status.set("ZAKOŃCZONO / rzeczywisty model Foundation GRU")
                report = value
                set_result(
                    "EKSPERYMENT Z WAG / NIE ODPOWIEDŹ FAKTOGRAFICZNA\n"
                    + f"Urządzenie: {report['device']}\n"
                    + f"Parametry: {report['parameter_count']}\n"
                    + f"Kroki uczenia checkpointu: {report['trained_steps_in_checkpoint']}\n"
                    + f"Przepustowość: {report['bytes_per_second']:.2f} B/s\n"
                    + f"Poprawny UTF-8: {report['generated_valid_utf8']}\n"
                    + f"HEX: {report['generated_hex']}\n\n"
                    + "PREDYKCJA MODELU:\n"
                    + report["generated_text_utf8_replacement"]
                    + "\n\nBrak cytowań; brak weryfikacji prawdziwości; wynik nie trafia do rozmowy.")
        except queue.Empty:
            pass
        if tab.winfo_exists():
            tab.after(180, poll)
    tab.after(180, poll)
    return tab
