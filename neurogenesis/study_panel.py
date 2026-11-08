"""Tk specialist-source panel: bounded opt-in acquisition with local progress."""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .specialist_study import SpecialistStudy


def install_study_panel(parent, memory, consent_var):
    """Attach a separate operator-controlled research tab; never auto-start."""
    tab = ttk.Frame(parent)
    parent.add(tab, text="Specjalizacja")
    ttk.Label(tab, text="Dziedzina do badania (publiczna Wikipedia, ograniczony zakres):").pack(
        anchor="w", padx=18, pady=(18, 5))
    topic = tk.StringVar()
    ttk.Entry(tab, textvariable=topic).pack(fill="x", padx=18)
    ttk.Label(tab, text="To gromadzenie źródeł w pamięci, nie trening wag modelu. "
              "Internet wymaga osobnej zgody w karcie Internet.", wraplength=720).pack(
        anchor="w", padx=18, pady=10)
    state = tk.StringVar(value="Gotowy — sieć wyłączona do chwili uruchomienia.")
    ttk.Label(tab, textvariable=state, wraplength=720).pack(fill="x", padx=18, pady=8)
    log = tk.Text(tab, height=12, state="disabled", wrap="word")
    log.pack(fill="both", expand=True, padx=18, pady=10)
    buttons = ttk.Frame(tab)
    buttons.pack(fill="x", padx=18, pady=8)
    events = queue.SimpleQueue()
    current = {"study": None, "thread": None}

    def add_log(line):
        log.configure(state="normal")
        log.insert("end", line + "\n")
        log.see("end")
        log.configure(state="disabled")

    def start():
        if not consent_var.get():
            messagebox.showwarning("Brak zgody", "Włącz zgodę HTTPS w karcie Internet.")
            return
        if current["thread"] is not None and current["thread"].is_alive():
            return
        try:
            # Every start creates a new bounded plan; no hidden queue.
            def persist(observation):
                acknowledgement = threading.Event()
                outcome = []
                events.put(("observation", (observation, acknowledgement, outcome)))
                if not acknowledgement.wait(15):
                    raise TimeoutError("Brak potwierdzenia zapisu")
                if outcome:
                    raise RuntimeError("Zapis odrzucony")
            study = SpecialistStudy(topic.get(), persist, max_pages=6)
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Nieprawidłowa dziedzina", str(exc))
            return
        current["study"] = study
        start_button.configure(state="disabled")
        state.set("Badanie uruchomione; maksymalnie 6 stron, odstęp min. 5 s.")
        add_log("Temat: " + study.topic)
        def worker():
            try:
                study.run(consent=True, on_event=lambda kind, url: events.put((kind, url)))
            except Exception:
                events.put(("fatal", "Nie udało się zakończyć badania"))
            finally:
                events.put(("done", ""))
        thread = threading.Thread(target=worker, daemon=True, name="NeuroGenesis-study")
        current["thread"] = thread
        thread.start()

    def stop():
        if current["study"] is not None:
            current["study"].stop()
            state.set("Zatrzymywanie po bieżącym żądaniu HTTPS...")

    start_button = ttk.Button(buttons, text="Rozpocznij badanie", command=start)
    start_button.pack(side="left")
    ttk.Button(buttons, text="Stop", command=stop).pack(side="left", padx=8)

    def poll():
        if not consent_var.get() and current["study"] is not None:
            current["study"].stop()
        try:
            while True:
                kind, url = events.get_nowait()
                if kind == "observation":
                    observation, acknowledgement, outcome = url
                    try:
                        if not consent_var.get():
                            raise PermissionError("Zgoda cofnięta")
                        memory.observe_web(observation)
                    except Exception:
                        outcome.append("rejected")
                    finally:
                        acknowledgement.set()
                elif kind == "done":
                    result = current["study"].progress()
                    state.set(f"Zakończono: {result.attempted} prób, "
                              f"{result.accepted} zapisanych, {result.errors} błędów.")
                    start_button.configure(state="normal")
                elif kind == "fatal":
                    add_log(url)
                else:
                    add_log(("Zapisano: " if kind == "saved" else "Niepowodzenie: ") + url)
        except queue.Empty:
            pass
        tab.after(250, poll)
    tab.after(250, poll)
    return tab
