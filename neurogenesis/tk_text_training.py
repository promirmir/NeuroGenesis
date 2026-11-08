"""Training TXT tab for the *shipped* Tk Windows application.

Actual gradient computation runs in a user-selected local Python environment
with optional deps. Every download has its own explicit action and separate
consent. Candidate model changes never silently replace the active model.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

MAX_JOB_SECONDS = 3600 * 3
MAX_LOCAL_TXT = 32 * 1024 * 1024


def local_training_command(python_exe: str, *, task: str,
                           input_txt: str = "", output: str = "",
                           model_dir: str = "", steps: int = 30,
                           device: str = "cpu", rights: bool = False,
                           trusted_model: bool = False,
                           download_consent: bool = False,
                           dataset_limit: int = 300) -> list[str]:
    """Pure control-plane validation, no side effects, no hidden downloads."""
    py = Path(python_exe)
    if not py.is_file() or py.is_symlink():
        raise ValueError("Wybierz istniejący, lokalny interpreter Python.")
    if os.name == "nt" and py.suffix.lower() != ".exe":
        raise ValueError("Na Windows wybierz plik python.exe.")
    if type(steps) is not int or not 1 <= steps <= 1000:
        raise ValueError("Kroki treningu: 1–1000.")
    if device not in ("cpu", "cuda"):
        raise ValueError("Urządzenie: cpu lub cuda.")
    if task in ("foundation", "lora"):
        if rights is not True:
            raise PermissionError("Potwierdź prawo do trenowania na wskazanym TXT.")
        source = Path(input_txt)
        if not source.is_file() or source.is_symlink() or source.suffix.lower() != ".txt":
            raise ValueError("Wybierz regularny istniejący TXT.")
        if not 1024 <= source.stat().st_size <= MAX_LOCAL_TXT:
            raise ValueError("TXT musi mieć 1 KiB–32 MiB.")
        destination = Path(output)
        if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
            raise ValueError("Wybierz nową ścieżkę wyniku; bez nadpisywania.")
        if destination.resolve() == source.resolve():
            raise ValueError("Nie zapisuj wyniku na źródłowym TXT.")
        if task == "foundation":
            if destination.suffix.lower() != ".pt":
                raise ValueError("Foundation oczekuje wyjścia .pt.")
            return [str(py), "-m", "neurogenesis.foundation_train",
                    "--input", str(source), "--output", str(destination),
                    "--confirm-corpus-rights", "--steps", str(steps),
                    "--device", device]
        if trusted_model is not True:
            raise PermissionError("Potwierdź zaufanie do lokalnego modelu.")
        from .local_dialogue import validate_model_dir
        model = validate_model_dir(model_dir)
        return [str(py), "-m", "neurogenesis.lora_train",
                "--model-dir", str(model), "--input", str(source),
                "--output", str(destination), "--confirm-corpus-rights",
                "--confirm-trusted-model", "--steps", str(steps),
                "--device", device]
    if task == "ultrachat":
        if download_consent is not True:
            raise PermissionError("Pobieranie danych wymaga zgody na transfer i przegląd licencji.")
        if type(dataset_limit) is not int or not 10 <= dataset_limit <= 1500:
            raise ValueError("Limit zbioru: 10–1500 dialogów.")
        target = Path(output)
        if target.exists() or target.suffix.lower() != ".txt" or not target.parent.is_dir():
            raise ValueError("Wskaż nowy plik .txt dla profesjonalnego zbioru.")
        return [str(py), "-m", "neurogenesis.dataset_prepare",
                "--source", "ultrachat", "--output", str(target),
                "--limit", str(dataset_limit), "--confirm-source-license"]
    if task == "qwen":
        if download_consent is not True:
            raise PermissionError("Potwierdź pobranie wag (~1.5 GiB) i akceptację Apache-2.0.")
        target = Path(output)
        if target.exists() or target.is_symlink() or not target.parent.is_dir():
            raise ValueError("Wskaż nowy, nieistniejący katalog na model.")
        return [str(py), "-m", "neurogenesis.local_dialogue",
                "--download-model", "--model-dir", str(target),
                "--confirm-download-license"]
    raise ValueError("Nieobsługiwany typ zadania.")


class LocalJob:
    """Kills a child process on operator cancellation; the GUI stays usable."""

    def __init__(self):
        self.cancelled = threading.Event()
        self._lock = threading.Lock()
        self.process: subprocess.Popen | None = None

    def cancel(self):
        self.cancelled.set()
        with self._lock:
            p = self.process
        if p is not None and p.poll() is None:
            p.kill()

    def run(self, argv: list[str]) -> dict:
        if self.cancelled.is_set():
            raise InterruptedError("Przerwano przed startem.")
        info = None
        if os.name == "nt":
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, encoding="utf-8",
                             startupinfo=info)
        with self._lock:
            self.process = p
        try:
            if self.cancelled.is_set():
                p.kill()
            try:
                stdout, stderr = p.communicate(timeout=MAX_JOB_SECONDS)
            except subprocess.TimeoutExpired:
                p.kill()
                p.communicate()
                raise TimeoutError("Przekroczono limit 3 godzin.")
            if self.cancelled.is_set():
                raise InterruptedError("Zadanie zatrzymane.")
            if p.returncode:
                raise RuntimeError("Zadanie nie powiodło się. "
                                   + stderr[-1200:].replace("\r", " "))
            if len(stdout.encode("utf-8")) > 64000:
                raise ValueError("Raport wyjściowy zbyt obszerny.")
            result = json.loads(stdout)
            if type(result) is not dict or "status" not in result:
                raise ValueError("Nieprawidłowy raport procesu treningu.")
            return result
        finally:
            with self._lock:
                self.process = None


def install_text_training(parent) -> ttk.Frame:
    tab = ttk.Frame(parent)
    parent.add(tab, text="Trening TXT")
    parent.insert(1, tab)  # visible beside CENTRUM even on narrower laptops
    outer = tk.Canvas(tab, bg="#07111d", bd=0, highlightthickness=0)
    scroll = ttk.Scrollbar(tab, orient="vertical", command=outer.yview)
    outer.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    outer.pack(side="left", fill="both", expand=True)
    body = tk.Frame(outer, bg="#07111d", padx=17, pady=16)
    item = outer.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>", lambda e: outer.configure(scrollregion=outer.bbox("all")))
    outer.bind("<Configure>", lambda e: outer.itemconfigure(item, width=max(e.width, 680)))

    def label(text, *, accent=False):
        tk.Label(body, text=text, bg="#07111d",
                 fg="#73ece0" if accent else "#b9d1dd", anchor="w",
                 justify="left", wraplength=880,
                 font=("Segoe UI", 10, "bold" if accent else "normal")).pack(
                     fill="x", pady=(5, 3))

    label("TRAINING CONSOLE / WŁASNE TXT + UCZENIE MODELU", accent=True)
    label("Foundation: trening bajtowego GRU z dowolnego TXT (nie tworzy chatbota). "
          "LoRA: faktyczne dostrajanie lokalnego modelu instrukcyjnego na dialogach "
          "USER:/ASSISTANT:. Kandydaci nigdy nie są automatycznie włączani do rozmowy.")
    python = tk.StringVar(value="" if getattr(sys, "frozen", False) else sys.executable)
    source = tk.StringVar()
    target = tk.StringVar(value=str(Path.home() / "NeuroGenesis-candidate.pt"))
    model = tk.StringVar()
    mode = tk.StringVar(value="Foundation TXT / GRU")
    steps = tk.StringVar(value="30")
    size = tk.StringVar(value="300")
    device = tk.StringVar(value="cpu")
    rights = tk.BooleanVar(value=False)
    trusted = tk.BooleanVar(value=False)
    downloads = tk.BooleanVar(value=False)
    continuous = tk.BooleanVar(value=False)
    status = tk.StringVar(value="Gotowy. Wszystkie zadania wymagają świadomego uruchomienia.")
    last_hash: str | None = None
    events = queue.SimpleQueue()
    running: dict[str, object] = {"worker": None, "thread": None}

    def field(title, value, choose=None):
        label(title)
        row = ttk.Frame(body)
        row.pack(fill="x", pady=(0, 5))
        ttk.Entry(row, textvariable=value).pack(side="left", fill="x", expand=True)
        if choose is not None:
            ttk.Button(row, text="Wybierz", command=choose).pack(
                side="left", padx=(6, 0))

    def open_file(var, kinds):
        chosen = filedialog.askopenfilename(filetypes=kinds)
        if chosen:
            var.set(chosen)

    field("PYTHON / LOKALNE ŚRODOWISKO Z NEUROGENESIS", python,
          lambda: open_file(python, [("Python", "*.exe"), ("Wszystkie", "*")]))
    field("PLIK TRENINGOWY TXT (UTF-8)", source,
          lambda: open_file(source, [("TXT", "*.txt")]))
    field("KATALOG MODELU INSTRUKCYJNEGO (WYMAGANY DLA LoRA)", model,
          lambda: model.set(filedialog.askdirectory() or model.get()))
    field("NOWY PLIK WYJŚCIOWY .PT / NOWY KATALOG LoRA / NOWY PLIK TXT", target)
    label("TRYB / RÓŻNE RODZAJE NAUKI")
    ttk.Combobox(body, textvariable=mode, state="readonly", values=(
        "Foundation TXT / GRU", "Dialog TXT / LoRA")).pack(fill="x", pady=(0, 6))
    row = ttk.Frame(body)
    row.pack(fill="x", pady=(3, 8))
    ttk.Label(row, text="KROKI:").pack(side="left")
    ttk.Entry(row, width=7, textvariable=steps).pack(side="left", padx=7)
    ttk.Label(row, text="CPU / GPU:").pack(side="left", padx=(16, 5))
    ttk.Combobox(row, width=7, textvariable=device, state="readonly",
                 values=("cpu", "cuda")).pack(side="left")
    ttk.Label(row, text="DIALOGÓW DO POBRANIA:").pack(side="left", padx=(14, 5))
    ttk.Entry(row, width=7, textvariable=size).pack(side="left")
    ttk.Checkbutton(body, text="Mam prawa do wykorzystania wskazanego TXT w treningu",
                    variable=rights).pack(anchor="w", pady=2)
    ttk.Checkbutton(body, text="Ufam lokalnym wagom modelu (LoRA)",
                    variable=trusted).pack(anchor="w", pady=2)
    ttk.Checkbutton(body, text="Potwierdzam dobrowolne pobranie danych/wag i przegląd licencji",
                    variable=downloads).pack(anchor="w", pady=2)

    label("KATALOG PROFESJONALNY / DANE Z JAWNYM POCHODZENIEM", accent=True)
    label("UltraChat 200k (HuggingFaceH4, karta MIT, język EN) → lokalny TXT. "
          "To przykłady dialogów; nie są z definicji prawdziwe. "
          "Qwen3-0.6B (Apache-2.0) → lokalne wagi ok. 1.5 GB. "
          "Wszystkie pobrania są wyłączone, dopóki ich sam nie uruchomisz.")
    buttons = ttk.Frame(body)
    buttons.pack(fill="x", pady=(7, 6))
    ttk.Button(buttons, text="POBIERZ ULTRACHAT → TXT",
               command=lambda: submit("ultrachat")).pack(side="left", padx=(0, 6))
    ttk.Button(buttons, text="POBIERZ QWEN 0.6B",
               command=lambda: submit("qwen")).pack(side="left")
    row = ttk.Frame(body)
    row.pack(fill="x", pady=(8, 6))
    start_btn = ttk.Button(row, text="ROZPOCZNIJ RZECZYWISTE UCZENIE",
                           command=lambda: submit(
                               "lora" if "LoRA" in mode.get() else "foundation"))
    start_btn.pack(side="left")
    ttk.Button(row, text="STOP", command=lambda: cancel()).pack(
        side="left", padx=8)
    ttk.Checkbutton(body,
        text="AUTO-KANDYDACI: obserwuj zatwierdzony TXT; nowy plik → nowy LoRA (bez aktywacji)",
        variable=continuous).pack(anchor="w", pady=(6, 3))
    label("Automatyczna nauka działa tylko podczas uruchomienia aplikacji, "
          "wyłącznie na wybranym lokalnym pliku, po wcześniejszym potwierdzeniu praw. "
          "Nigdy nie pobiera z internetu ani nie zastępuje czynnego modelu.")
    ttk.Label(body, textvariable=status, wraplength=850).pack(
        fill="x", pady=(8, 4))
    report = tk.Text(body, height=11, bg="#0b2130", fg="#c7e9ee",
                     wrap="word", font=("Consolas", 9), state="disabled")
    report.pack(fill="x", pady=(4, 9))

    def show(text):
        report.configure(state="normal")
        report.delete("1.0", "end")
        report.insert("end", text)
        report.configure(state="disabled")

    def cancel():
        worker = running["worker"]
        if isinstance(worker, LocalJob):
            worker.cancel()
            status.set("Przerywanie zadania w procesie zewnętrznym...")

    def submit(task, *, override_target=None):
        current = running["thread"]
        if isinstance(current, threading.Thread) and current.is_alive():
            return
        desired = override_target or target.get()
        # The shared output entry starts as .pt; suggest coherent, clearly
        # visible default paths for downloaded model, corpus and LoRA.
        if override_target is None:
            if task == "ultrachat" and not desired.lower().endswith(".txt"):
                desired = str(Path.home() / "NeuroGenesis-UltraChat-300.txt")
            elif task == "qwen" and desired.lower().endswith(".pt"):
                desired = str(Path.home() / "NeuroGenesis-Qwen3-0.6B")
            elif task == "lora" and desired.lower().endswith(".pt"):
                desired = str(Path.home() / "NeuroGenesis-LoRA-candidate")
            if desired != target.get():
                target.set(desired)
        try:
            argv = local_training_command(
                python.get(), task=task, input_txt=source.get(),
                output=desired, model_dir=model.get(),
                steps=int(steps.get()), device=device.get(), rights=rights.get(),
                trusted_model=trusted.get(), download_consent=downloads.get(),
                dataset_limit=int(size.get()))
        except (ValueError, PermissionError, OSError) as exc:
            status.set("WYMAGANA KONFIGURACJA / " + str(exc))
            if override_target is None:
                messagebox.showerror("Trening — kontrola", str(exc))
            return
        worker = LocalJob()
        running["worker"] = worker
        start_btn.configure(state="disabled")
        status.set("PRACUJE / odrębny proces Pythona; wynik po ukończeniu.")
        show("Obliczanie... Trening może długo obciążać CPU/GPU. "
             "Nie zamykaj programu podczas pracy.")

        def job():
            try:
                events.put(("ok", worker.run(argv)))
            except (ValueError, RuntimeError, OSError, TimeoutError, InterruptedError) as exc:
                events.put(("error", str(exc)))
        thread = threading.Thread(target=job, daemon=True, name="NG-local-training")
        running["thread"] = thread
        thread.start()

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                start_btn.configure(state="normal")
                running["worker"] = None
                if kind == "ok":
                    if value.get("status") == "local_pretrained_model_downloaded":
                        model.set(value["directory"])
                    elif value.get("status") == "opt_in_dataset_export":
                        source.set(value["file"])
                    status.set("ZAKOŃCZONO / sprawdź raport i walidację; kandydat nie jest aktywny")
                    show(json.dumps(value, ensure_ascii=False, indent=2))
                else:
                    status.set("BŁĄD / bez automatycznego nadpisania wag")
                    show(str(value))
        except queue.Empty:
            pass
        if tab.winfo_exists():
            tab.after(200, poll)

    def monitor():
        nonlocal last_hash
        try:
            if continuous.get() and rights.get() and trusted.get() and model.get() and source.get():
                f = Path(source.get())
                if f.is_file() and not f.is_symlink() and 1024 <= f.stat().st_size <= MAX_LOCAL_TXT:
                    # hash is computed only on approved local TXT; never sent online
                    digest = hashlib.sha256(f.read_bytes()).hexdigest()
                    if last_hash is None:
                        last_hash = digest
                    elif digest != last_hash:
                        current = running["thread"]
                        if not isinstance(current, threading.Thread) or not current.is_alive():
                            dest = str(Path.home() / ("NeuroGenesis-LoRA-auto-" + digest[:12]))
                            if not Path(dest).exists():
                                status.set("AUTO-KANDYDAT / zmieniony zatwierdzony TXT")
                                submit("lora", override_target=dest)
                            last_hash = digest
            else:
                last_hash = None
        except OSError as exc:
            # The file can disappear halfway through a poll. Don't crash Tk.
            status.set("AUTO-KANDYDAT / nie można odczytać TXT: " + str(exc))
        if tab.winfo_exists():
            tab.after(60_000, monitor)

    def on_destroy(event):
        if event.widget == tab:
            continuous.set(False)
            cancel()  # kill any child subprocess; never leave orphan training

    tab.bind("<Destroy>", on_destroy, add="+")
    tab.after(200, poll)
    tab.after(60_000, monitor)
    return tab
