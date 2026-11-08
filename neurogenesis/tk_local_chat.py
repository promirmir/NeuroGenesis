"""Actual local pretrained conversational model tab in the shipped Tk EXE.

Separate from the sourced deterministic `Rozmowa` panel, which keeps its
existing privacy/evidence semantics. This tab runs model inference offline
with explicit local weights and an operator-specified Python environment.
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

from .local_dialogue import validate_messages, validate_model_dir

MAX_OUTPUT_BYTES = 96_000


def build_local_chat_command(python_exe: str, model_dir: str, *,
                             device: str, tokens: int,
                             adapter_dir: str = "") -> list[str]:
    py = Path(python_exe)
    if not py.is_file() or py.is_symlink():
        raise ValueError("Wskaż istniejący Python z zainstalowanym torch i transformers.")
    if os.name == "nt" and py.suffix.lower() != ".exe":
        raise ValueError("Na Windows wybierz python.exe.")
    model = validate_model_dir(model_dir)
    if device not in ("cpu", "cuda") or type(tokens) is not int or not 16 <= tokens <= 256:
        raise ValueError("Nieprawidłowy limit CPU/CUDA lub liczba tokenów.")
    cmd = [str(py), "-m", "neurogenesis.local_dialogue", "--respond-stdin",
           "--model-dir", str(model), "--device", device,
           "--max-new-tokens", str(tokens)]
    if adapter_dir.strip():
        adapter = Path(adapter_dir)
        if not adapter.is_dir() or not (adapter / "adapter_config.json").is_file():
            raise ValueError("Wskaż katalog zatwierdzonego adaptera LoRA.")
        cmd.extend(["--adapter-dir", str(adapter)])
    return cmd


class LocalChatWorker:
    def __init__(self):
        self.cancelled = threading.Event()
        self.lock = threading.Lock()
        self.proc: subprocess.Popen | None = None

    def cancel(self):
        self.cancelled.set()
        with self.lock:
            p = self.proc
        if p is not None and p.poll() is None:
            p.kill()

    def run(self, argv, messages):
        data = json.dumps({"messages": validate_messages({"messages": messages})},
                          ensure_ascii=False)
        if self.cancelled.is_set():
            raise InterruptedError("Rozmowa przerwana.")
        info = None
        if os.name == "nt":
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, encoding="utf-8", text=True,
                             startupinfo=info)
        with self.lock:
            self.proc = p
        try:
            if self.cancelled.is_set():
                p.kill()
            try:
                stdout, stderr = p.communicate(data, timeout=240)
            except subprocess.TimeoutExpired:
                p.kill()
                p.communicate()
                raise TimeoutError("Limit 4 minut na odpowiedź został przekroczony.")
            if self.cancelled.is_set():
                raise InterruptedError("Rozmowa anulowana.")
            if p.returncode:
                raise RuntimeError("Model nie może odpowiedzieć: "
                                   + stderr[-1000:].replace("\r", " "))
            if len(stdout.encode("utf-8")) > MAX_OUTPUT_BYTES:
                raise ValueError("Model zwrócił za długi tekst.")
            result = json.loads(stdout)
            if (type(result) is not dict or
                    result.get("status") != "local_conversational_model" or
                    result.get("offline_inference") is not True or
                    type(result.get("reply")) is not str):
                raise ValueError("Nieprawidłowa odpowiedź lokalnego modelu.")
            return result
        finally:
            with self.lock:
                self.proc = None


def install_local_chat(parent) -> ttk.Frame:
    tab = ttk.Frame(parent)
    parent.add(tab, text="Model Chat")
    parent.insert(2, tab)  # show actual model dialogue early in notebook
    background = "#07111d"
    tk.Label(tab, text="NEUROGENESIS / AUTENTYCZNY MODEL KONWERSACYJNY OFFLINE",
             bg=background, fg="#77e7e0",
             font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(15, 4))
    tk.Label(tab, text=(
        "To odrębny dialog z lokalnym modelem instrukcyjnym, NIE z eksperymentalnym GRU. "
        "Wymaga wcześniej pobranych wag i Pythona z torch/transformers. Nie przesyła "
        "rozmowy do chmury, nie udaje cytowań ani nie trenuje automatycznie na rozmowie."),
        bg=background, fg="#a3c0ca", justify="left",
        wraplength=970).pack(fill="x", padx=18, pady=(0, 8))
    interpreter = tk.StringVar(value="" if getattr(sys, "frozen", False) else sys.executable)
    model = tk.StringVar()
    adapter = tk.StringVar()
    device = tk.StringVar(value="cpu")
    tokens = tk.StringVar(value="128")
    status = tk.StringVar(value="OFFLINE / wybierz lokalny model")
    turns: list[dict[str, str]] = []
    events = queue.SimpleQueue()
    running: dict[str, object] = {"worker": None, "thread": None}
    def field(text, var, chooser=None):
        row = ttk.Frame(tab)
        row.pack(fill="x", padx=18, pady=3)
        ttk.Label(row, text=text, width=20).pack(side="left")
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
        if chooser:
            ttk.Button(row, text="Wybierz", command=chooser).pack(side="left", padx=5)
    field("Python z Torch", interpreter,
          lambda: interpreter.set(filedialog.askopenfilename(
              filetypes=[("Python", "*.exe"), ("Wszystkie", "*")]) or interpreter.get()))
    field("Lokalny model", model,
          lambda: model.set(filedialog.askdirectory() or model.get()))
    field("Adapter LoRA (opc.)", adapter,
          lambda: adapter.set(filedialog.askdirectory() or adapter.get()))
    settings = ttk.Frame(tab)
    settings.pack(fill="x", padx=18, pady=(4, 6))
    ttk.Label(settings, text="Procesor:").pack(side="left")
    ttk.Combobox(settings, state="readonly", textvariable=device,
                 values=("cpu", "cuda"), width=8).pack(side="left", padx=7)
    ttk.Label(settings, text="Limit tokenów:").pack(side="left", padx=(15, 3))
    ttk.Entry(settings, textvariable=tokens, width=6).pack(side="left")
    ttk.Label(tab, textvariable=status, wraplength=950).pack(fill="x", padx=18, pady=3)
    console = tk.Text(tab, height=14, wrap="word", bg="#091f2c", fg="#d4f3ed",
                      font=("Segoe UI", 10), padx=12, pady=8,
                      state="disabled")
    console.pack(fill="both", expand=True, padx=18, pady=(7, 8))
    entry = tk.Text(tab, height=3, bg="#102d3c", fg="#f2ffff",
                    insertbackground="#d4ffff", wrap="word",
                    font=("Segoe UI", 10))
    entry.pack(fill="x", padx=18)
    btns = ttk.Frame(tab)
    btns.pack(fill="x", padx=18, pady=(8, 13))

    def append(text):
        console.configure(state="normal")
        console.insert("end", text + "\n\n")
        console.see("end")
        console.configure(state="disabled")

    def send():
        active = running["thread"]
        if isinstance(active, threading.Thread) and active.is_alive():
            return
        message = entry.get("1.0", "end-1c").strip()
        if not 1 <= len(message) <= 1800:
            messagebox.showerror("Model Chat", "Wpisz 1–1800 znaków.")
            return
        try:
            argv = build_local_chat_command(
                interpreter.get(), model.get(), device=device.get(),
                tokens=int(tokens.get()), adapter_dir=adapter.get())
            history = turns[-8:] + [{"role": "user", "content": message}]
            validate_messages({"messages": history})
        except (OSError, ValueError) as exc:
            status.set("BŁĄD KONFIGURACJI / " + str(exc))
            return
        entry.delete("1.0", "end")
        append("TY: " + message)
        status.set("GENEROWANIE / lokalny model oblicza odpowiedź, bez API")
        send_button.configure(state="disabled")
        worker = LocalChatWorker()
        running["worker"] = worker
        def calculate():
            try:
                events.put(("ok", message, worker.run(argv, history)))
            except (ValueError, OSError, RuntimeError, InterruptedError, TimeoutError) as exc:
                events.put(("error", message, str(exc)))
        thread = threading.Thread(target=calculate, daemon=True, name="NG-local-chat")
        running["thread"] = thread
        thread.start()

    def stop():
        worker = running["worker"]
        if isinstance(worker, LocalChatWorker):
            worker.cancel()

    def reset():
        active = running["thread"]
        if isinstance(active, threading.Thread) and active.is_alive():
            return
        turns.clear()
        console.configure(state="normal")
        console.delete("1.0", "end")
        console.configure(state="disabled")
        status.set("Historia sesji wyczyszczona; prywatna baza SQLite niezmieniona.")

    send_button = ttk.Button(btns, text="WYŚLIJ DO MODELU OFFLINE", command=send)
    send_button.pack(side="left")
    ttk.Button(btns, text="STOP", command=stop).pack(side="left", padx=8)
    ttk.Button(btns, text="NOWA ROZMOWA", command=reset).pack(side="left")

    def poll():
        try:
            while True:
                kind, message, response = events.get_nowait()
                send_button.configure(state="normal")
                running["worker"] = None
                if kind == "error":
                    status.set("NIE POWIODŁO SIĘ / brak dopisania do historii")
                    append("BŁĄD: " + response)
                else:
                    answer = response["reply"]
                    # Only successfully generated replies become the conversation.
                    turns.extend(({"role": "user", "content": message},
                                  {"role": "assistant", "content": answer or "(pusty wynik)"}))
                    status.set("OFFLINE / lokalne wagi; odpowiedź bez sprawdzania faktów")
                    append("NEUROGENESIS: " + (answer or "(brak treści)"))
        except queue.Empty:
            pass
        if tab.winfo_exists():
            tab.after(200, poll)
    def on_destroy(event):
        if event.widget == tab:
            stop()  # the model child process must never outlive GUI shutdown

    tab.bind("<Destroy>", on_destroy, add="+")
    tab.after(200, poll)
    return tab
