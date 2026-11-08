"""The real autonomic operations board of NeuroGenesis Windows EXE.

This UI DOES NOT simulate intelligence. It reads persisted neural LIF events,
knowledge SQLite revisions, and the actual model worker state. It controls the
existing bounded supervisor, the approved-folder watcher, and tab navigation.
No automatic external requests, fake counters, or self-modifying code.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

from .autonomy import AutonomicSupervisor, WINDOW
from .local_knowledge import LocalKnowledge
from .memory import ExperienceMemory

BG = "#07111d"
BG2 = "#0b2232"
BG3 = "#0f2b3e"
LINE = "#235267"
CYAN = "#62e5d9"
WHITE = "#f0fcff"
DIM = "#9abac9"
AMBER = "#ffd08e"
RED = "#ff978d"


def _label(parent, value, size=10, color=DIM, strong=False, **kwargs):
    return tk.Label(parent, text=value, bg=kwargs.pop("bg", BG),
                    fg=color, anchor=kwargs.pop("anchor", "w"),
                    justify="left", wraplength=kwargs.pop("wraplength", 950),
                    font=("Segoe UI", size, "bold" if strong else "normal"),
                    **kwargs)


def _card(parent, title: str, subtitle: str, *, button: str,
          command: Callable[[], None]) -> tuple[tk.Frame, tk.StringVar, tk.StringVar]:
    border = tk.Frame(parent, bg=LINE, padx=1, pady=1)
    cell = tk.Frame(border, bg=BG2, padx=13, pady=12)
    cell.pack(fill="both", expand=True)
    _label(cell, title, 12, WHITE, True, bg=BG2).pack(
        fill="x", pady=(0, 3))
    _label(cell, subtitle, 9, DIM, bg=BG2).pack(
        fill="x", pady=(0, 10))
    state = tk.StringVar(value="OCZEKIWANIE NA ODCZYT")
    details = tk.StringVar(value="Brak pomiaru")
    _label(cell, state, 11, CYAN, True, bg=BG2).pack(
        fill="x", pady=(0, 3))
    ttk.Label(cell, textvariable=details, wraplength=310).pack(
        fill="x", pady=(0, 10))
    ttk.Button(cell, text=button, command=command).pack(
        fill="x")
    return border, state, details


def install_autonomy_hub(
        parent,
        memory: ExperienceMemory, knowledge: LocalKnowledge,
        supervisor: AutonomicSupervisor, *,
        brain_auto: tk.BooleanVar,
        training_auto: tk.BooleanVar,
        training_folder: tk.StringVar,
        training_consent: tk.BooleanVar,
        model_status: tk.StringVar,
        navigate: Callable[[str], None],
        run_brain_trial: Callable[[], None],
        model_start: Callable[[], None],
        model_stop: Callable[[], None],
        choose_training_folder: Callable[[], None],
        allowed_web: Callable[[], bool],
) -> ttk.Frame:
    tab = ttk.Frame(parent)
    parent.add(tab, text="AUTONOMIA")
    parent.insert(1, tab)

    canvas = tk.Canvas(tab, bg=BG, highlightthickness=0, bd=0)
    bar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=bar.set)
    bar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    body = tk.Frame(canvas, bg=BG, padx=16, pady=13)
    body_window = canvas.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>",
              lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
                lambda event: canvas.itemconfigure(body_window, width=max(630, event.width)))

    top = tk.Frame(body, bg=BG)
    top.pack(fill="x")
    _label(top, "NEUROGENESIS / LIVE OPERATIONS", 9, CYAN, True).pack(
        anchor="w")
    _label(top, "Autonomiczne centrum", 21, WHITE, True).pack(
        anchor="w", pady=(2, 4))
    _label(top, "Jedno miejsce do rozmowy, uczenia, nadzoru mózgu i kontroli "
                "prawdziwych zadań. Liczniki pokazują dane zapisane "
                "w pamięci — nie animowaną symulację AI.",
           10, DIM).pack(fill="x", pady=(0, 8))

    global_status = tk.StringVar(value="ODCZYT STANU MODUŁÓW…")
    ttk.Label(body, textvariable=global_status).pack(
        fill="x", pady=(1, 11))
    ttk.Separator(body).pack(fill="x", pady=(0, 12))

    actions = ttk.Frame(body)
    actions.pack(fill="x", pady=(0, 14))
    ttk.Button(actions, text="ROZMAWIAJ Z AI",
               command=lambda: navigate("local_chat")).pack(
                   side="left", padx=(0, 7))
    ttk.Button(actions, text="NAUCZ Z TXT",
               command=lambda: navigate("training")).pack(
                   side="left", padx=(0, 7))
    ttk.Button(actions, text="PODGLĄD MÓZGU",
               command=lambda: navigate("mission")).pack(
                   side="left")

    cards = tk.Frame(body, bg=BG)
    cards.pack(fill="x", pady=(0, 13))
    for x in range(2):
        cards.grid_columnconfigure(x, weight=1, uniform="ops")

    model_card, model_state, model_desc = _card(
        cards, "01 / INTELIGENCJA JĘZYKOWA",
        "Rzeczywisty model Qwen wbudowany w EXE",
        button="PRZEJDŹ DO ROZMOWY", command=lambda: navigate("local_chat"))
    model_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 10))

    knowledge_card, knowledge_state, knowledge_desc = _card(
        cards, "02 / PAMIĘĆ I WIEDZA",
        "Zatwierdzone TXT, wersjonowanie, lokalny RAG",
        button="DODAJ WIEDZĘ", command=lambda: navigate("training"))
    knowledge_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 10))

    brain_card, brain_state, brain_desc = _card(
        cards, "03 / PLASTYCZNOŚĆ MÓZGU",
        "Weryfikowane próby LIF po nowych obserwacjach",
        button="ZOBACZ AKTYWNOŚĆ LIF", command=lambda: navigate("brain"))
    brain_card.grid(row=1, column=0, sticky="nsew", padx=(0, 6))

    monitor_card, monitor_state, monitor_desc = _card(
        cards, "04 / PERCEPCJA I NADZÓR",
        "Kontrola zgód, rzeczywiste zdarzenia i źródła",
        button="ODCZYT ŹRÓDEŁ HTTPS", command=lambda: navigate("web"))
    monitor_card.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

    _label(body, "RZECZYWISTY PRZEPŁYW PRACY / DANE I SYGNAŁY",
           11, CYAN, True).pack(anchor="w", pady=(2, 6))
    signal = tk.Canvas(body, bg="#061824", height=115, highlightthickness=1,
                       highlightbackground=LINE, bd=0)
    signal.pack(fill="x", pady=(0, 14))
    signal.bind("<Configure>", lambda _event: draw_pipeline())

    def draw_pipeline():
        """A static graph of measured component state, not animated fake pulses.

        The pipeline reflects recorded SQLite documents/brain steps and the
        real model worker. A label indicates whether each has any activity.
        """
        width = max(540, signal.winfo_width())
        signal.delete("all")
        values = [
            ("PERCEPCJA", "Zgoda HTTPS", bool(allowed_web())),
            ("WIEDZA", str(previous.get("chunks", 0)) + " fragm.",
             previous.get("chunks", 0) > 0),
            ("MODEL", "Gotowość", bool(previous.get("model_ready"))),
            ("LIF", str(previous.get("steps", 0)) + " kroków",
             previous.get("steps", 0) > 0),
        ]
        spacing = (width - 90) / 3
        coords = [45 + spacing * i for i in range(4)]
        cy = 50
        for i in range(3):
            signal.create_line(coords[i] + 18, cy, coords[i + 1] - 18, cy,
                               fill="#1a5265", width=3)
        for i, (label, detail, active) in enumerate(values):
            x = coords[i]
            outline = CYAN if active else "#507689"
            fill = "#137276" if active else "#123040"
            signal.create_oval(x - 15, cy - 15, x + 15, cy + 15,
                               outline=outline, fill=fill, width=2)
            signal.create_oval(x - 4, cy - 4, x + 4, cy + 4,
                               fill="#dbffff" if active else "#507689", outline="")
            signal.create_text(x, 17, text=label, fill=WHITE,
                               font=("Consolas", 9, "bold"))
            signal.create_text(x, 87, text=detail[:28], fill=DIM,
                               font=("Consolas", 8))
        signal.create_text(
            width - 15, 106, anchor="e",
            text="ŚWIATŁO = STAN POTWIERDZONY / LINIE = SCHEMAT PRZEPŁYWU",
            fill="#7599a9", font=("Consolas", 7))

    _label(body, "AUTOMATYCZNE ZADANIA", 12, CYAN, True).pack(
        anchor="w", pady=(8, 6))
    toggles = tk.Frame(body, bg=BG2, padx=14, pady=11,
                       highlightbackground=LINE, highlightthickness=1)
    toggles.pack(fill="x", pady=(0, 12))
    ttk.Checkbutton(
        toggles, variable=brain_auto,
        text="Samodzielnie sprawdzaj ulepszenia LIF po 40 nowych obserwacjach"
    ).pack(anchor="w", pady=(0, 3))
    _label(
        toggles,
        "Zabezpieczone eksperymenty: kandydat jest promowany tylko po "
        "walidacji i ochronie wcześniejszych wyników. Bez nowych "
        "obserwacji nic nie jest trenowane.",
        9, DIM, bg=BG2).pack(fill="x", pady=(0, 7))
    ttk.Checkbutton(
        toggles, variable=training_auto,
        text="Samodzielnie indeksuj nowe pliki TXT z wybranego folderu"
    ).pack(anchor="w", pady=(0, 5))
    watch_label = tk.StringVar(value="FOLDER NIE WYBRANY")
    ttk.Label(toggles, textvariable=watch_label, wraplength=900).pack(
        fill="x", pady=(0, 7))
    line = ttk.Frame(toggles)
    line.pack(fill="x")
    ttk.Button(line, text="WYBIERZ FOLDER I ZGODY",
               command=lambda: (choose_training_folder(), navigate("training"))).pack(
                   side="left", padx=(0, 7))
    ttk.Button(line, text="URUCHOM PRÓBĘ LIF",
               command=run_brain_trial).pack(side="left", padx=(0, 7))
    ttk.Button(line, text="URUCHOM AI", command=model_start).pack(
        side="left", padx=(0, 7))
    ttk.Button(line, text="ZATRZYMAJ AI", command=model_stop).pack(
        side="left")

    _label(body, "RZECZYWISTE ZDARZENIA / OSTATNIE ZMIANY", 12, CYAN, True).pack(
        anchor="w", pady=(2, 7))
    log = tk.Text(body, height=8, bg="#061a27", fg="#d4f1ef",
                  font=("Consolas", 9), padx=10, pady=9,
                  relief="flat", wrap="word", state="disabled")
    log.pack(fill="x", pady=(0, 13))
    _label(body,
           "Brak nowych wpisów oznacza brak zmian zapisanych w lokalnych bazach. "
           "Animacja mózgu nie może zastępować pomiaru. Przetwarzanie Internetu "
           "wymaga oddzielnej zgody, niezależnie od ustawień autonomii.",
           9, DIM).pack(fill="x")

    previous = {}
    timeline = deque(maxlen=45)
    closing = {"value": False}
    def record(message: str):
        timeline.appendleft(
            datetime.now().strftime("%H:%M:%S") + " / " + message)
        log.configure(state="normal")
        log.delete("1.0", "end")
        log.insert("end", "\n".join(timeline))
        log.configure(state="disabled")

    def refresh():
        if closing["value"]:
            return
        try:
            neural = memory.status()
            brain = neural["brain"]
            autonomy = supervisor.status()
            sources = knowledge.status()
            model_text = model_status.get()
            ready = "GOTOWY" in model_text or "GENEROWAN" in model_text
            model_state.set("GOTOWY / OFFLINE" if ready else "OCZEKUJE / LOKALNY")
            model_desc.set(model_text[:155])
            knowledge_state.set(str(sources["files"]) + " źródeł / " +
                                str(sources["passages"]) + " fragmentów")
            folder_text = training_folder.get().strip()
            approved = bool(training_consent.get() and folder_text)
            watch_label.set(("Folder: " + folder_text[:130] if approved
                             else "Wybierz folder w zakładce Trening TXT i potwierdź prawa.")
                            + (" / AUTO AKTYWNE" if training_auto.get() and approved
                               else " / AUTO WYŁĄCZONE"))
            knowledge_desc.set(
                "Nowe TXT: automatyczny zapis po włączeniu."
                if training_auto.get() and approved else
                "Import ręczny lub monitor zatwierdzonego folderu")
            brain_state.set(str(brain["neurons"]) + " neuronów / " +
                            str(brain["steps"]) + " kroków")
            brain_desc.set(
                f"Próby: {autonomy['cycles']}  ·  Zatwierdzone: {autonomy['promotions']}\n"
                f"Nowe obserwacje: {autonomy['new_events']}/{WINDOW}  ·  "
                f"AUTO: {'TAK' if brain_auto.get() else 'NIE'}")
            monitor_state.set(
                "HTTPS / ZE ZGODĄ" if allowed_web() else "HTTPS / WYŁĄCZONY")
            monitor_desc.set(
                f"Rzeczywiste dokumenty źródłowe: {neural['knowledge']['documents']}\n"
                "Dostęp sieciowy nie jest nadawany automatycznie.")
            snapshot = {
                "steps": brain["steps"], "neurons": brain["neurons"],
                "synapses": brain["synapses"], "docs": sources["files"],
                "chunks": sources["passages"], "cycles": autonomy["cycles"],
                "approved": autonomy["promotions"],
                "model": model_text,
                "model_ready": ready,
            }
            if not previous:
                record("Pierwszy odczyt zapisanego stanu: LIF " +
                       str(snapshot["steps"]) + " / źródła " +
                       str(snapshot["docs"]) + " / próby " +
                       str(snapshot["cycles"]))
            else:
                labels = {
                    "steps": "Nowy krok sieci LIF",
                    "neurons": "Zmiana liczby neuronów",
                    "synapses": "Zmiana synaps",
                    "docs": "Zmiana liczby lokalnych plików wiedzy",
                    "chunks": "Zmiana liczby fragmentów wiedzy",
                    "cycles": "Zakończono próbę samorozwoju LIF",
                    "approved": "Zatwierdzono zmianę po walidacji",
                    "model": "Zmiana stanu lokalnego modelu",
                    "model_ready": "Gotowość silnika językowego",
                }
                for key, value in snapshot.items():
                    if value != previous.get(key):
                        record(labels[key] + ": " + str(previous[key])[:45] +
                               " -> " + str(value)[:70])
            previous.clear()
            previous.update(snapshot)
            draw_pipeline()
            global_status.set(
                f"MODEL: {'GOTOWY' if ready else 'NIEGOTOWY'}   |   "
                f"LOKALNE PLIKI: {sources['files']}   |   "
                f"MÓZG LIF: {brain['steps']} KROKÓW   |   "
                f"AUTONOMIA LIF: {'AKTYWNA' if brain_auto.get() else 'WYŁĄCZONA'}")
        except (OSError, ValueError, RuntimeError, KeyError, IndexError) as exc:
            global_status.set("BŁĄD RZECZYWISTEGO ODCZYTU / " + str(exc)[:230])
            record("Błąd odczytu stanu — nie zmieniono pamięci")
        if tab.winfo_exists():
            tab.after(1700, refresh)

    def close(event):
        if event.widget == tab:
            closing["value"] = True

    tab.bind("<Destroy>", close, add="+")
    tab.after(250, refresh)
    return tab
