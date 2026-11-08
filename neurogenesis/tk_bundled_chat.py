"""Real packaged Qwen Model Chat, with NO external Python or cloud API.

One GGUF server lives only while this Tk application is open; user history
stays in memory, indexed TXT stays in a separate private SQLite database.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from .bundled_llm import BundledModelSession, has_bundled_model
from .local_knowledge import LocalKnowledge


def install_bundled_chat(parent, knowledge: LocalKnowledge) -> ttk.Frame:
    tab = ttk.Frame(parent)
    parent.add(tab, text="Model Chat")
    parent.insert(2, tab)

    bg, aqua, grey = "#07111d", "#71eadb", "#a6c3d2"
    title = tk.Frame(tab, bg=bg)
    title.pack(fill="x", padx=14, pady=(11, 4))
    tk.Label(title, text="NEUROGENESIS  /  LOCAL INTELLIGENCE",
             bg=bg, fg=aqua, font=("Segoe UI", 13, "bold")).pack(
                 side="left")
    tk.Label(title, text="Qwen3-1.7B  •  GGUF  •  OFFLINE",
             bg=bg, fg=grey, font=("Consolas", 9)).pack(
                 side="right", padx=(10, 0))
    tk.Label(tab, bg=bg, fg=grey, anchor="w",
             text=("Rozmowa z prawdziwego modelu zawartego w EXE. "
                   "Żadnego zewnętrznego Pythona ani pobierania. "
                   "Treść rozmowy tylko w RAM; lokalna wiedza z TXT "
                   "w prywatnej bazie. Model może popełniać błędy."),
             wraplength=1020, justify="left").pack(
                 fill="x", padx=14, pady=(0, 5))

    model = BundledModelSession(knowledge=knowledge, max_tokens=224)
    events: queue.SimpleQueue = queue.SimpleQueue()
    running = {"thread": None, "closing": False, "ready": False, "starting": False}
    turns: list[dict[str, str]] = []
    status = tk.StringVar(value=(
        "SPRAWDZANIE MODELU: " +
        ("komponenty znalezione; model uruchamia się przy wejściu do zakładki."
         if has_bundled_model() else
         "brak wag/silnika w tym EXE — pobierz pełną wersję NeuroGenesis.")))
    ttk.Label(tab, textvariable=status, wraplength=950).pack(
        fill="x", padx=14, pady=(3, 7))
    actions = ttk.Frame(tab)
    actions.pack(side="bottom", fill="x", padx=14, pady=(6, 10))
    entry = tk.Text(tab, height=2, wrap="word", bg="#0d2b3a",
                    fg="#f0ffff", insertbackground=aqua,
                    font=("Segoe UI", 11), relief="flat", padx=9, pady=5)
    entry.pack(side="bottom", fill="x", padx=14, pady=(2, 2))
    transcript = tk.Text(tab, height=12, wrap="word", bg="#061c2b",
                         fg="#cceee9", state="disabled",
                         font=("Segoe UI", 11), relief="flat",
                         padx=11, pady=9)
    transcript.pack(fill="both", expand=True, padx=14, pady=(5, 6))
    transcript.tag_configure("human", foreground="#70e0ff")
    transcript.tag_configure("ai", foreground="#ebfbf5")

    def write(role, message):
        transcript.configure(state="normal")
        transcript.insert("end", role + "\n", "human" if role == "TY" else "ai")
        transcript.insert("end", message + "\n\n")
        transcript.see("end")
        transcript.configure(state="disabled")

    def threaded(task, callback):
        current = running["thread"]
        if isinstance(current, threading.Thread) and current.is_alive():
            return False

        def worker():
            try:
                events.put(("ok", task, callback()))
            except Exception as exc:
                events.put(("error", task, str(exc)))
        thread = threading.Thread(
            target=worker, name="NeuroGenesis-bundled-LLM",
            daemon=True)
        running["thread"] = thread
        thread.start()
        return True

    def start(*, allow_if_not_selected=False):
        if running["closing"] or running["ready"] or running["starting"]:
            return
        if not has_bundled_model():
            status.set("BRAK MODELU W EXE. Pobierz wersję FULL, a nie LITE.")
            return
        running["starting"] = True
        status.set("ŁADOWANIE / sprawdzanie integralności wag i uruchamianie modelu offline…")
        send_btn.configure(state="disabled")
        if not threaded("start", lambda: model.start()):
            running["starting"] = False

    def send():
        if running["closing"]:
            return
        message = entry.get("1.0", "end-1c").strip()
        if not 1 <= len(message) <= 1800:
            messagebox.showwarning("Model Chat", "Wpisz pytanie o długości 1–1800 znaków.")
            return
        if not running["ready"]:
            start()
            status.set("POCZĄTKOWA INICJALIZACJA / po uruchomieniu modelu wyślij pytanie.")
            return
        if len(turns) >= 12:
            history = turns[-12:]
        else:
            history = list(turns)
        query = history + [{"role": "user", "content": message}]
        if len(query) > 13:
            query = query[-13:]
        if threaded("chat", lambda: model.chat(query)):
            send_btn.configure(state="disabled")
            entry.delete("1.0", "end")
            write("TY", message)
            status.set("OBLICZENIA MODELU / lokalna generacja odpowiedzi w pamięci RAM…")
            running["pending_message"] = message

    def stop():
        model.stop()
        running["ready"] = False
        status.set("MODEL ZATRZYMANY / możesz uruchomić go ponownie.")

    def reset():
        if isinstance(running["thread"], threading.Thread) and running["thread"].is_alive():
            return
        turns.clear()
        transcript.configure(state="normal")
        transcript.delete("1.0", "end")
        transcript.configure(state="disabled")
        status.set("Historia rozmowy tej sesji została usunięta z RAM.")

    send_btn = ttk.Button(actions, text="WYŚLIJ WIADOMOŚĆ", command=send)
    send_btn.pack(side="left")
    ttk.Button(actions, text="URUCHOM MODEL", command=start).pack(
        side="left", padx=(7, 0))
    ttk.Button(actions, text="STOP", command=stop).pack(
        side="left", padx=(7, 0))
    ttk.Button(actions, text="NOWA ROZMOWA", command=reset).pack(
        side="left", padx=(7, 0))

    def poll():
        if running["closing"]:
            return
        try:
            while True:
                kind, task, value = events.get_nowait()
                if task == "start":
                    running["starting"] = False
                    running["ready"] = kind == "ok"
                    if kind == "ok":
                        status.set("MODEL GOTOWY / Qwen3-1.7B · offline · wagi wewnątrz EXE")
                        send_btn.configure(state="normal")
                    else:
                        status.set("BŁĄD ZAŁADOWANIA MODELU / " + str(value)[:300])
                        send_btn.configure(state="normal")
                elif task == "chat":
                    send_btn.configure(state="normal")
                    if kind == "ok":
                        answer = value["reply"]
                        question = running.pop("pending_message", "")
                        if question:
                            turns.extend(({"role": "user", "content": question},
                                          {"role": "assistant", "content": answer[:1800]}))
                        status.set(
                            "GOTOWY / odpowiedź lokalna; wykorzystano " +
                            str(len(value.get("sources", []))) +
                            " fragmentów wiedzy TXT (jeśli dostępne).")
                        write("NEUROGENESIS", answer)
                    else:
                        status.set("BŁĄD GENERACJI / " + str(value)[:300])
                        write("BŁĄD", str(value))
        except queue.Empty:
            pass
        if tab.winfo_exists():
            tab.after(140, poll)

    def on_selected(_event=None):
        if running["closing"]:
            return
        if parent.select() == str(tab) and not running["ready"]:
            start()

    def on_destroy(event):
        if event.widget == tab:
            running["closing"] = True
            model.stop()

    # Expose real running-process status and UI commands to the operations
    # dashboard. These are live Tk variables/callbacks, not proxy metrics.
    tab.ng_model_status = status
    tab.ng_model_start = start
    tab.ng_model_stop = stop
    tab.bind("<Destroy>", on_destroy, add="+")
    parent.bind("<<NotebookTabChanged>>", on_selected, add="+")
    tab.after(140, poll)
    return tab
