"""Default NeuroGenesis autonomous workspace — chat, goals, live neural evidence.

One pretrained, locally bundled model shared by conversation and background
goal-work. All independent activity is observable, bounded and documented.
Never simulate brain activity or claim RAG is gradient training.
"""
from __future__ import annotations

import queue
import threading
import time
from typing import Callable
import tkinter as tk
from tkinter import ttk, messagebox

from .agent_goals import GoalStore, prompt_for_goal
from .autonomy import AutonomicSupervisor, WINDOW
from .acf_memory import FabricMemoryObserver
from .acf_semantic_memory import SemanticFabricStore
from .bundled_llm import BundledModelSession, has_bundled_model, bounded_chat_history
from .local_knowledge import LocalKnowledge
from .corrective_memory import CorrectiveMemory
from .tk_corrections import open_corrections_dialog
from .memory import ExperienceMemory
from .neural_telemetry import snapshot_neural_telemetry
from .tk_connectome import TkConnectome


BG, PANEL, BORDER = "#07111d", "#0b2130", "#24566a"
CYAN, WHITE, MUTED = "#68eadd", "#e7faff", "#98b9c9"


def _caption(parent, text, *, fg=CYAN):
    tk.Label(parent, text=text, bg=PANEL, fg=fg, anchor="w",
             font=("Segoe UI", 10, "bold")).pack(
                 fill="x", padx=10, pady=(8, 3))


def install_autonomous_home(parent: ttk.Notebook, memory: ExperienceMemory,
                            knowledge: LocalKnowledge,
                            supervisor: AutonomicSupervisor, goals: GoalStore,
                            *, brain_enabled: tk.BooleanVar | None = None,
                            auto_start: bool = True,
                            open_research: Callable[[], None] | None = None) -> ttk.Frame:
    """Install as first and default page, without adding fake demo metrics."""
    tab = ttk.Frame(parent)
    parent.add(tab, text="  NEUROGENESIS  ")
    parent.insert(0, tab)
    corrections = CorrectiveMemory(
        memory.path.with_name("approved_corrections.sqlite3"))
    model = BundledModelSession(
        knowledge=knowledge, web_memory=memory,
        corrections=corrections, max_tokens=240)
    # ACF is independent of the legacy LIF database schema and weights.
    # It learns from existing hashed eight-channel observations ONLY.
    fabric_observer = FabricMemoryObserver(
        memory.path, memory.path.with_name("adaptive_fabric.acf.json"))
    fabric_events: queue.SimpleQueue = queue.SimpleQueue()
    semantic_store = SemanticFabricStore(memory.path.parent)
    semantic_pending: list[str] = []  # RAM only, never persisted as raw text.
    events: queue.SimpleQueue = queue.SimpleQueue()
    running: dict[str, object] = {
        "job": None, "brain_job": None, "acf_job": None,
        "semantic_job": None, "ready": False,
        "starting": False, "closing": False, "pending_message": None,
    }
    own_brain_enabled = brain_enabled or tk.BooleanVar(master=tab, value=True)
    auto_goals = tk.BooleanVar(master=tab, value=True)
    sensory_inputs = tk.BooleanVar(master=tab, value=True)
    acf_answer_mode = tk.BooleanVar(master=tab, value=False)  # opt-in research
    state_model = tk.StringVar(master=tab, value="MODEL / przygotowanie...")
    state_brain = tk.StringVar(master=tab, value="MÓZG / odczyt stanu...")
    state_corpus = tk.StringVar(master=tab, value="WIEDZA / odczyt danych...")
    state_agent = tk.StringVar(master=tab, value="AUTONOMIA / gotowa")
    conversation_status = tk.StringVar(master=tab, value=(
        "Model uruchamia się sam. Wpisz wiadomość — możesz to zrobić "
        "również podczas jego pierwszego ładowania."))
    turns: list[dict[str, str]] = []
    last_chat_activity = {"at": time.monotonic()}
    last_exchange = {"question": "", "answer": ""}  # RAM only until approval
    last_brain_step = {"value": None}
    last_goal_refresh = {"value": ()}

    top = tk.Frame(tab, bg=BG)
    top.pack(fill="x", padx=16, pady=(13, 8))
    tk.Label(top, text="NEUROGENESIS", bg=BG, fg=WHITE,
             font=("Segoe UI", 21, "bold")).pack(side="left")
    tk.Label(top, text="AUTONOMOUS INTELLIGENCE CONSOLE  /  OFFLINE",
             bg=BG, fg=CYAN, font=("Consolas", 10)).pack(
                 side="left", padx=(18, 0))
    top_buttons = tk.Frame(top, bg=BG)
    top_buttons.pack(side="right")
    ttk.Button(top_buttons, text="MÓZG / TELEMETRIA",
               command=lambda: select_named_tab(parent, "  CENTRUM  ")).pack(side="left")
    ttk.Button(top_buttons, text="DODAJ WIEDZĘ",
               command=lambda: select_named_tab(parent, "Trening TXT")).pack(
                   side="left", padx=(7, 0))
    if open_research is not None:
        ttk.Button(top_buttons, text="BADAJ ŹRÓDŁA",
                   command=open_research).pack(
                       side="left", padx=(7, 0))

    states = tk.Frame(tab, bg=BG)
    states.pack(fill="x", padx=16, pady=(0, 9))
    for var in (state_model, state_brain, state_corpus, state_agent):
        tile = tk.Frame(states, bg=PANEL, highlightthickness=1,
                        highlightbackground=BORDER, padx=9, pady=9)
        tile.pack(side="left", fill="x", expand=True, padx=3)
        tk.Label(tile, textvariable=var, bg=PANEL, fg=CYAN, anchor="w",
                 justify="left", wraplength=230,
                 font=("Segoe UI", 9, "bold")).pack(fill="x")

    splitter = tk.PanedWindow(tab, orient="horizontal", bg=BG,
                              sashwidth=5, sashrelief="flat",
                              borderwidth=0)
    splitter.pack(fill="both", expand=True, padx=16, pady=(0, 13))
    left = tk.Frame(splitter, bg=PANEL, highlightthickness=1,
                    highlightbackground=BORDER)
    right_container = tk.Frame(splitter, bg=BG, width=360)
    splitter.add(left, stretch="always", minsize=370)
    splitter.add(right_container, stretch="never", minsize=265)

    _caption(left, "ROZMOWA Z RZECZYWISTYM MODELEM JĘZYKOWYM")
    tk.Label(left, text="Wagi Qwen3-1.7B w EXE • rozmowa w RAM • "
             "źródła z prywatnego TXT • brak połączeń z zewnętrznym API",
             bg=PANEL, fg=MUTED, anchor="w", wraplength=475).pack(
                 fill="x", padx=10, pady=(0, 5))
    buttons = tk.Frame(left, bg=PANEL)
    buttons.pack(side="bottom", fill="x", padx=10, pady=(4, 10))
    input_field = tk.Text(left, height=3, wrap="word", bg="#12374a",
                          fg=WHITE, insertbackground=CYAN,
                          padx=10, pady=8, relief="flat",
                          font=("Segoe UI", 11))
    input_field.pack(side="bottom", fill="x", padx=10, pady=(2, 4))
    tk.Label(left, textvariable=conversation_status,
             bg=PANEL, fg=MUTED, anchor="w", justify="left",
             wraplength=470).pack(side="bottom", fill="x", padx=10, pady=(2, 2))
    transcript = tk.Text(left, wrap="word", bg="#061624", fg=WHITE,
                         padx=13, pady=11, relief="flat",
                         font=("Segoe UI", 11), state="disabled")
    transcript.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 5))
    transcript.tag_configure("you", foreground="#73cfff")
    transcript.tag_configure("ai", foreground=CYAN)
    transcript.tag_configure("event", foreground="#90afbd")

    def log(role: str, content: str):
        transcript.configure(state="normal")
        style = "you" if role == "TY" else ("ai" if role == "NEUROGENESIS" else "event")
        transcript.insert("end", role + "\n", style)
        transcript.insert("end", content + "\n\n")
        transcript.see("end")
        transcript.configure(state="disabled")

    log("SYSTEM", "Witaj w centrum NeuroGenesis. Wpisz pytanie poniżej lub dodaj "
        "samodzielny cel w panelu po prawej. Statusy i graf przedstawiają "
        "rzeczywistą pracę zapisanych modułów — bez symulowania zdarzeń.")

    def background(task, fn, *, detail=None, brain=False):
        key = "brain_job" if brain else "job"
        previous = running[key]
        if isinstance(previous, threading.Thread) and previous.is_alive():
            return False
        def worker():
            try:
                value = fn()
                events.put(("ok", task, detail, value))
            except Exception as exc:
                events.put(("error", task, detail, str(exc)))
        thread = threading.Thread(target=worker, daemon=True,
                                  name="NeuroGenesis-" + task)
        running[key] = thread
        thread.start()
        return True

    def initialize_model():
        if (running["closing"] or running["starting"] or running["ready"]
                or not has_bundled_model()):
            if not has_bundled_model():
                state_model.set("MODEL / BRAK PAKIETU FULL")
                conversation_status.set(
                    "Nie znaleziono wag modelu w EXE. Wybierz wydanie FULL.")
                running["pending_message"] = None
                send_btn.configure(state="normal")
            return
        running["starting"] = True
        state_model.set("MODEL / ładowanie lokalnych wag...")
        conversation_status.set(
            "Weryfikacja SHA-256 i uruchamianie lokalnej sieci — "
            "zapisane pytanie zostanie wysłane automatycznie.")
        if not background("start", model.start):
            running["starting"] = False

    def submit_chat():
        if running["closing"] or running["pending_message"] is not None:
            return
        message = input_field.get("1.0", "end-1c").strip()
        if not 1 <= len(message) <= 1800:
            messagebox.showwarning("NeuroGenesis", "Wpisz wiadomość: 1–1800 znaków.")
            return
        input_field.delete("1.0", "end")
        last_chat_activity["at"] = time.monotonic()
        log("TY", message)
        running["pending_message"] = message
        send_btn.configure(state="disabled")
        if not running["ready"]:
            initialize_model()
        else:
            flush_message()

    def flush_message():
        message = running.get("pending_message")
        if not running["ready"] or not isinstance(message, str):
            return
        history = bounded_chat_history(turns, message)
        record_sensory = bool(sensory_inputs.get())
        acf_path = semantic_store.state_path if acf_answer_mode.get() else None
        def run():
            reply = model.chat(history, acf_state_path=acf_path)
            sensory_error = None
            if record_sensory:
                try:
                    # Only hashed sensory features enter existing LIF SQLite.
                    # This does NOT store raw conversation text.
                    memory.remember(message, source="local", store_text=False)
                except (ValueError, OSError) as exc:
                    sensory_error = str(exc)[:130]
            return {"reply": reply, "sensory_error": sensory_error,
                    "record_sensory": record_sensory}
        if background("chat", run, detail=message):
            state_model.set("MODEL / generuje odpowiedź")
            conversation_status.set("Lokalne obliczenia — prawdziwy model językowy pracuje...")
        else:
            conversation_status.set("Agent kończy bieżące zadanie. Wiadomość jest w kolejce.")

    send_btn = ttk.Button(buttons, text="WYŚLIJ  ↵", command=submit_chat)
    send_btn.pack(side="left")
    ttk.Button(buttons, text="ZATRZYMAJ", command=lambda: stop_model()).pack(
        side="left", padx=(6, 0))
    ttk.Button(buttons, text="NOWA ROZMOWA", command=lambda: clear_chat()).pack(
        side="left", padx=(6, 0))
    ttk.Checkbutton(
        buttons, text="Uczenie LIF + semantyczne ACF (bez treści rozmów)",
        variable=sensory_inputs).pack(side="right")
    acf_options = tk.Frame(left, bg=PANEL)
    acf_options.pack(side="bottom", fill="x", padx=10, pady=(0, 3))
    ttk.Checkbutton(
        acf_options, text="BADANIE: ACF może dobrać 1 lokalny fragment TXT",
        variable=acf_answer_mode).pack(side="left")
    tk.Label(
        acf_options, text="Domyślnie wyłączone · tylko przy przewadze MSE",
        bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(side="right")
    memory_options = tk.Frame(left, bg=PANEL)
    memory_options.pack(side="bottom", fill="x", padx=10, pady=(3, 3))
    ttk.Button(
        memory_options, text="PAMIĘĆ POPRAWEK / ZAPAMIĘTAJ I POPRAW",
        command=lambda: open_corrections_dialog(
            tab, corrections, last_exchange,
            on_change=lambda: state_corpus.set(
                "PAMIĘĆ KOREKT / " +
                str(corrections.status()["approved_corrections"]) +
                " zatwierdzonych wpisów"))
    ).pack(side="left")
    tk.Label(
        memory_options, text="Tylko świadomie zatwierdzone informacje",
        bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", padx=(8, 0))

    def stop_model():
        model.stop()
        running["ready"] = False
        running["starting"] = False
        state_model.set("MODEL / zatrzymany")
        conversation_status.set("Model zatrzymany. Uruchomi się przy następnym pytaniu.")
        send_btn.configure(state="normal")
        running["pending_message"] = None

    def clear_chat():
        previous = running["job"]
        if isinstance(previous, threading.Thread) and previous.is_alive():
            return
        turns.clear()
        last_exchange["question"] = ""
        last_exchange["answer"] = ""
        transcript.configure(state="normal")
        transcript.delete("1.0", "end")
        transcript.configure(state="disabled")
        conversation_status.set("Nowa rozmowa — poprzednia historia usunięta z RAM.")

    def key_send(event):
        if event.state & 0x0001:
            return  # Shift+Enter is newline
        submit_chat()
        return "break"
    input_field.bind("<Return>", key_send)

    # Always-visible real neural monitor: separate from the scrolling
    # autonomous goals, so the user can inspect both on a 768p laptop.
    brain_footer = tk.Frame(right_container, bg=PANEL, height=318,
                            highlightbackground=BORDER, highlightthickness=1)
    brain_footer.pack(side="bottom", fill="x", pady=(6, 0))
    brain_footer.pack_propagate(False)

    # Right goal list scrolls independently at laptop resolutions.
    side_canvas = tk.Canvas(right_container, bg=BG, highlightthickness=0,
                            borderwidth=0)
    side_scroll = ttk.Scrollbar(right_container, orient="vertical",
                                command=side_canvas.yview)
    side_canvas.configure(yscrollcommand=side_scroll.set)
    side_scroll.pack(side="right", fill="y")
    side_canvas.pack(fill="both", expand=True)
    side = tk.Frame(side_canvas, bg=BG)
    side_window = side_canvas.create_window((0, 0), window=side, anchor="nw")
    side.bind("<Configure>", lambda _e: side_canvas.configure(
        scrollregion=side_canvas.bbox("all")))
    side_canvas.bind("<Configure>", lambda e: side_canvas.itemconfigure(
        side_window, width=e.width))

    def card(title):
        border = tk.Frame(side, bg=BORDER, padx=1, pady=1)
        border.pack(fill="x", pady=(0, 9))
        inner = tk.Frame(border, bg=PANEL, padx=9, pady=7)
        inner.pack(fill="both", expand=True)
        _caption(inner, title)
        return inner

    goals_card = card("AUTONOMICZNE CELE / PLAN → ANALIZA → OCENA")
    tk.Label(goals_card, text="Zleć cel raz. Agent sam planuje i "
             "wznawia ocenę po zmianie zatwierdzonych TXT lub źródeł HTTPS.",
             wraplength=345, bg=PANEL, fg=MUTED, justify="left").pack(
                 fill="x", padx=10, pady=(0, 7))
    goal_entry = tk.Text(goals_card, height=2, bg="#103346",
                         fg=WHITE, insertbackground=CYAN, wrap="word",
                         font=("Segoe UI", 10))
    goal_entry.pack(fill="x", padx=10, pady=(0, 6))
    goal_controls = tk.Frame(goals_card, bg=PANEL)
    goal_controls.pack(fill="x", padx=10, pady=(0, 6))
    goal_list = ttk.Treeview(goals_card, columns=("state",),
                              show="tree headings", height=5)
    goal_list.heading("#0", text="CEL")
    goal_list.heading("state", text="STAN")
    goal_list.column("#0", width=235, stretch=True)
    goal_list.column("state", width=110, stretch=False)
    goal_list.pack(fill="x", padx=10, pady=(3, 5))
    goal_details = tk.Text(goals_card, height=6, wrap="word",
                           state="disabled", bg="#071c2b", fg=WHITE,
                           padx=8, pady=7)
    goal_details.pack(fill="x", padx=10, pady=(0, 5))
    decisions = tk.Frame(goals_card, bg=PANEL)
    decisions.pack(fill="x", padx=10, pady=(0, 6))

    def add_goal():
        statement = goal_entry.get("1.0", "end-1c").strip()
        try:
            goal_id = goals.add(statement)
        except (ValueError, OSError) as exc:
            messagebox.showerror("NeuroGenesis — cele", str(exc))
            return
        goal_entry.delete("1.0", "end")
        state_agent.set(f"AGENT / cel #{goal_id} w kolejce")
        refresh_goals(force=True)

    ttk.Button(goal_controls, text="+ DODAJ CEL", command=add_goal).pack(side="left")
    ttk.Checkbutton(goal_controls, text="Samodzielne wykonywanie",
                    variable=auto_goals).pack(side="right")

    def selected_goal() -> int | None:
        chosen = goal_list.selection()
        if not chosen:
            return None
        try:
            return int(chosen[0])
        except ValueError:
            return None

    def change_goal(action: str):
        goal_id = selected_goal()
        if goal_id is None:
            return
        try:
            goals.set_state(goal_id, action)
            refresh_goals(force=True)
        except (ValueError, OSError) as exc:
            messagebox.showerror("NeuroGenesis — cele", str(exc))

    ttk.Button(decisions, text="ZATWIERDŹ", command=lambda: change_goal("accept")).pack(
        side="left")
    ttk.Button(decisions, text="WSTRZYMAJ", command=lambda: change_goal("pause")).pack(
        side="left", padx=(5, 0))
    ttk.Button(decisions, text="WZNÓW", command=lambda: change_goal("resume")).pack(
        side="left", padx=(5, 0))
    tk.Label(goals_card, text="Wyniki są kandydatami, nie samodzielnie "
             "potwierdzonymi faktami. Cele i raporty pozostają w SQLite.",
             bg=PANEL, fg=MUTED, wraplength=345, justify="left").pack(
                 fill="x", padx=10, pady=(0, 4))

    def show_details(_event=None):
        gid = selected_goal()
        item = next((g for g in goals.list() if g["id"] == gid), None)
        details = "Wybierz cel."
        if item:
            details = (f"Cel #{item['id']} / {item['state']} / "
                       f"próby: {item['attempts']}\n\n" +
                       (item["result"] or "Agent nie wygenerował jeszcze raportu."))
            if item["sources"]:
                details += "\n\nŹRÓDŁA (TXT / zatwierdzone HTTPS):\n" + "\n".join(
                    p["file"] + " / " + p["sha256"][:12] for p in item["sources"])
        goal_details.configure(state="normal")
        goal_details.delete("1.0", "end")
        goal_details.insert("end", details)
        goal_details.configure(state="disabled")

    goal_list.bind("<<TreeviewSelect>>", show_details)

    def refresh_goals(*, force=False):
        data = goals.list()
        signature = tuple((g["id"], g["state"], g["attempts"], len(g["result"]))
                          for g in data)
        if signature == last_goal_refresh["value"] and not force:
            return
        current = selected_goal()
        for item in goal_list.get_children():
            goal_list.delete(item)
        for g in data:
            goal_list.insert("", "end", iid=str(g["id"]),
                              text=g["goal"][:65], values=(g["state"],))
        if current is not None and goal_list.exists(str(current)):
            goal_list.selection_set(str(current))
            show_details()
        last_goal_refresh["value"] = signature

    brain_card = brain_footer
    _caption(brain_card, "NEURAL FABRIC / RZECZYWISTY LIF")
    brain_activity = tk.StringVar(master=tab, value="Stan bez nowych impulsów.")
    fabric_status = tk.StringVar(
        master=tab,
        value="ACF / oddzielna sieć predykcyjna; oczekiwanie na pomiary SQLite")
    semantic_status = tk.StringVar(
        master=tab,
        value="SEMANTYCZNY ACF / lokalna klasyfikacja Qwen; brak pomiarów")
    tk.Label(brain_card, textvariable=brain_activity,
             bg=PANEL, fg=MUTED, anchor="w", wraplength=345).pack(
                 fill="x", padx=10, pady=(0, 5))
    neural_canvas = tk.Canvas(brain_card, width=320, height=108,
                              bg="#041624", highlightthickness=0)
    neural_canvas.pack(fill="x", padx=10, pady=(0, 6))
    neural_canvas.bind("<Configure>",
                       lambda _e: redraw_connectome(force=True), add="+")
    connectome = TkConnectome(neural_canvas, compact=True)
    ttk.Checkbutton(brain_card, text="AUTO: testuj rozwój LIF po 40 nowych bodźcach",
                    variable=own_brain_enabled).pack(
                        anchor="w", padx=10, pady=(0, 6))
    _caption(brain_card, "ACF / AUTONOMICZNA PLASTYCZNOŚĆ I SAMOMODEL")
    tk.Label(brain_card, textvariable=fabric_status, bg=PANEL, fg=CYAN,
             justify="left", anchor="w", wraplength=345,
             font=("Consolas", 9)).pack(fill="x", padx=10, pady=(0, 4))
    tk.Label(brain_card, text=(
        "Sensoryczny: hashe · semantyczny: Qwen; "
        "MSE nie mierzy jakości rozmowy."),
        bg=PANEL, fg=MUTED, justify="left", anchor="w",
        wraplength=345, font=("Segoe UI", 8)).pack(
            fill="x", padx=10, pady=(0, 3))
    tk.Label(
        brain_card, textvariable=semantic_status, bg=PANEL, fg=CYAN,
        justify="left", anchor="w", wraplength=345,
        font=("Consolas", 9)).pack(fill="x", padx=10, pady=(0, 5))

    def redraw_connectome(*, force=False):
        if running["closing"]:
            return
        try:
            state = snapshot_neural_telemetry(memory.brain())
            if force or state.step != last_brain_step["value"]:
                connectome.render(state, force=True)
                last_brain_step["value"] = state.step
                brain_activity.set(
                    f"Krok {state.step} · neurony {state.total_neurons} "
                    f"· synapsy {state.total_synapses} · impulsy {state.total_spikes}")
        except (OSError, ValueError) as exc:
            brain_activity.set("Błąd odczytu rzeczywistego LIF: " + str(exc)[:90])

    # Dashboard follows persisted model/knowledge and never fabricates progress.
    def refresh_status():
        if running["closing"]:
            return
        try:
            neural = supervisor.status()
            brain = memory.status()["brain"]
            corpus = knowledge.status()
            state_brain.set(
                f"LIF / {brain['neurons']} neuronów · {brain['steps']} kroków")
            corrections_count = corrections.status()["approved_corrections"]
            state_corpus.set(
                f"WIEDZA / {corpus['files']} TXT · {corpus['passages']} frag. "
                f"· {corrections_count} poprawek")
            state_agent.set(
                f"AUTO / {neural['new_events']}/{WINDOW} bodźców "
                f"· {neural['promotions']} zatwierdz.")
            redraw_connectome()
            refresh_goals()
        except (OSError, ValueError, KeyError, RuntimeError) as exc:
            state_agent.set("BŁĄD STANU / " + str(exc)[:100])
        if tab.winfo_exists():
            tab.after(2800, refresh_status)

    def run_goal(claimed):
        try:
            response = model.chat([{
                "role": "user", "content": prompt_for_goal(claimed)}])
            return goals.complete(claimed, response["reply"])
        except Exception as exc:
            goals.fail(claimed, str(exc))
            raise

    def acf_tick():
        if running["closing"]:
            return
        if own_brain_enabled.get():
            job = running["acf_job"]
            if not isinstance(job, threading.Thread) or not job.is_alive():
                def measure():
                    try:
                        fabric_events.put(("ok", fabric_observer.poll(limit=96)))
                    except (OSError, ValueError, RuntimeError, KeyError) as exc:
                        fabric_events.put(("error", str(exc)[:220]))
                new_job = threading.Thread(
                    target=measure, daemon=True, name="NeuroGenesis-ACF-sensory")
                running["acf_job"] = new_job
                new_job.start()
        if tab.winfo_exists():
            tab.after(8_000, acf_tick)

    def autonomy_tick():
        if running["closing"]:
            return
        # Actual bounded LIF optimization only after a fresh 40-event window.
        if own_brain_enabled.get():
            busy = running["brain_job"]
            if not isinstance(busy, threading.Thread) or not busy.is_alive():
                try:
                    if supervisor.status()["new_events"] >= WINDOW:
                        background("lif-cycle", supervisor.cycle, brain=True)
                except (OSError, ValueError) as exc:
                    state_agent.set("LIF / zatrzymany: " + str(exc)[:100])
        if running["ready"] and auto_goals.get() and running["pending_message"] is None:
            job = running["job"]
            if not isinstance(job, threading.Thread) or not job.is_alive():
                try:
                    claimed = goals.claim(knowledge, memory)
                    if claimed is not None:
                        state_agent.set(f"AGENT / analizuje cel #{claimed['id']}")
                        background("goal", lambda c=claimed: run_goal(c), detail=claimed)
                except (OSError, ValueError) as exc:
                    state_agent.set("AGENT / błąd danych: " + str(exc)[:100])
        if tab.winfo_exists():
            tab.after(9500, autonomy_tick)

    def launch_semantic():
        # Give real-time user dialogue priority over optional semantic inference.
        # A follow-up must never be blocked by immediate post-answer work.
        if running["closing"] or not running["ready"] or not sensory_inputs.get():
            semantic_pending.clear()
            return
        if (running["pending_message"] is not None or
                time.monotonic() - last_chat_activity["at"] < 18):
            return
        foreground = running["job"]
        if isinstance(foreground, threading.Thread) and foreground.is_alive():
            return
        work = running["semantic_job"]
        if isinstance(work, threading.Thread) and work.is_alive():
            return
        if not semantic_pending:
            return
        message = semantic_pending.pop(0)
        def work_semantic():
            try:
                classification = model.classify_semantics(message)
                result = semantic_store.learn(classification)
                # ACF may trigger a REAL read-only approved-TXT prefetch
                # ONLY after measured adaptive > fixed/persistence controls.
                # No data content sent to model; no Internet calls here.
                try:
                    result["policy"] = semantic_store.prepare_next_topic(knowledge)
                except (OSError, ValueError, RuntimeError, KeyError) as exc:
                    result["policy"] = {
                        "status": "local_policy_read_failed",
                        "detail": str(exc)[:110],
                        "local_sources_consulted": 0,
                    }
                events.put(("ok", "semantic", None, result))
            except (OSError, ValueError, RuntimeError, KeyError,
                    TimeoutError) as exc:
                events.put(("error", "semantic", None, str(exc)[:180]))
        thread = threading.Thread(
            target=work_semantic, daemon=True, name="NeuroGenesis-semantic-ACF")
        running["semantic_job"] = thread
        thread.start()

    def poll():
        if running["closing"]:
            return
        try:
            while True:
                kind, task, detail, value = events.get_nowait()
                if task == "start":
                    running["starting"] = False
                    running["ready"] = kind == "ok"
                    if kind == "ok":
                        state_model.set("MODEL / Qwen3 · gotowy offline")
                        conversation_status.set("Gotowy do rozmowy — bez dodatkowej konfiguracji.")
                        if running.get("pending_message") is not None:
                            flush_message()
                    else:
                        state_model.set("MODEL / błąd uruchomienia")
                        conversation_status.set(str(value)[:200])
                        running["pending_message"] = None
                        send_btn.configure(state="normal")
                elif task == "chat":
                    send_btn.configure(state="normal")
                    question = running["pending_message"]
                    running["pending_message"] = None
                    if kind == "ok":
                        report = value["reply"]
                        answer = report["reply"]
                        if question:
                            turns.extend((
                                {"role": "user", "content": question},
                                {"role": "assistant", "content": answer[:1800]},
                            ))
                            last_exchange["question"] = question
                            last_exchange["answer"] = answer[:1800]
                        sources = report.get("sources", [])
                        log("NEUROGENESIS", answer)
                        last_chat_activity["at"] = time.monotonic()
                        acf = report.get("acf_routing")
                        acf_note = ""
                        if acf:
                            acf_note = (
                                " ACF: +1 zatwierdzony TXT (eksperyment)."
                                if acf.get("status") == "acf_passage_added"
                                else " ACF: bez wpływu (" +
                                str(acf.get("status", "brak danych")) + ").")
                        correction_used = bool(
                            report.get("correction_memory", {}).get(
                                "approved_correction_used", False))
                        conversation_status.set(
                            f"Odpowiedź z lokalnych wag; "
                            f"{len(sources)} pobranych fragmentów. "
                            + ("LIF: " + value["sensory_error"]
                               if value["sensory_error"] else "Bodźce LIF zapisane w SQLite."
                               if sensory_inputs.get() else "Bez zapisu treści rozmowy.")
                            + acf_note
                            + (" PAMIĘĆ: wykorzystano zatwierdzoną "
                               "poprawkę z poprzedniej rozmowy."
                               if correction_used else ""))
                        state_model.set("MODEL / gotowy na następne pytanie")
                        if (question and value.get("record_sensory")
                                and sensory_inputs.get()):
                            if len(semantic_pending) < 8:
                                semantic_pending.append(question[:1200])
                                launch_semantic()
                            else:
                                semantic_status.set(
                                    "SEMANTYCZNY ACF / zapełniona kolejka RAM; "
                                    "nie zapisano tekstu do treningu")
                    else:
                        log("SYSTEM", "Nie udało się wygenerować odpowiedzi: " + str(value)[:320])
                        conversation_status.set("Generacja nieudana; spróbuj ponownie.")
                        state_model.set("MODEL / błąd odpowiedzi")
                elif task == "semantic":
                    if kind == "ok":
                        sm = value["self_model"]
                        learned = sm["observations"]
                        route = sm["selected_route"]
                        scores = sm["route_mean_mse_recent"]
                        error = scores[route]
                        metric = f"{error:.5f}" if error is not None else "brak próbek"
                        choice = value.get("policy", {})
                        state = choice.get("status", "unavailable")
                        status_text = {
                            "local_sources_prepared": (
                                f"WSTĘPNY ODCZYT TXT: {choice.get('predicted_axis')} "
                                f"· {choice.get('local_sources_consulted', 0)} frag."),
                            "approved_sources_missing": (
                                f"LUKA W WIEDZY: {choice.get('predicted_axis')} "
                                f"· dodaj zatwierdzony TXT"),
                            "insufficient_real_observations": (
                                "POLITYKA ACF: za mało obserwacji"),
                            "no_measured_adaptive_advantage": (
                                "POLITYKA ACF: brak przewagi nad kontrolą"),
                            "adaptive_not_selected_by_actual_loss": (
                                "POLITYKA ACF: wybrano lepszy model kontrolny"),
                            "low_confidence_or_unsuitable_topic": (
                                "POLITYKA ACF: brak pewnego tematu"),
                            "local_policy_read_failed": (
                                "POLITYKA ACF: błąd lokalnego odczytu"),
                        }.get(state, "POLITYKA ACF: brak potwierdzonej decyzji")
                        semantic_status.set(
                            f"SEMANTYKA Qwen / {learned} wektorów · nowe "
                            f"{value['processed']}\nACF: {route} · MSE {metric} "
                            f"· neurony {sm['adaptive_structure']['neurons']}\n"
                            f"{status_text}"
                            + ("\nODZYSKANO ACF: zweryfikowana poprzednia migawka "
                               "i odtworzone zdarzenia."
                               if value.get("checkpoint_recovered") else ""))
                    else:
                        semantic_status.set(
                            "SEMANTYCZNY ACF / błąd klasyfikacji, "
                            "nie zapisano fikcyjnych cech: " + str(value)[:120])
                    # The worker may still be alive while its last
                    # queue event is processed. Retry on the next Tk tick.
                    if tab.winfo_exists():
                        tab.after(200, launch_semantic)
                elif task == "goal":
                    refresh_goals(force=True)
                    if kind == "ok":
                        state_agent.set(
                            f"AGENT / cel #{value['id']}: {value['state']} "
                            f"({value['source_count']} źródeł)")
                        log("SYSTEM", "Agent przygotował nowy raport do oceny "
                            "w panelu celów. Żadne działania zewnętrzne nie zostały wykonane.")
                    else:
                        state_agent.set("AGENT / błąd celu; szczegóły w panelu")
                    if running["pending_message"] is not None:
                        flush_message()
                elif task == "lif-cycle":
                    if kind == "ok":
                        state_agent.set(
                            "LIF / " + ("propozycja zatwierdzona"
                                        if value.get("promoted") else
                                        "próba odrzucona / bez zmiany"))
                    else:
                        state_agent.set("LIF / błąd cyklu: " + str(value)[:100])
        except queue.Empty:
            pass
        except (KeyError, TypeError, ValueError, RuntimeError, IndexError) as exc:
            # Optional telemetry must not kill the event poller: otherwise a
            # subsequent chat response would never be displayed/re-enabled.
            conversation_status.set(
                "Błąd obsługi zdarzenia (dialog nadal aktywny): "
                + type(exc).__name__ + ": " + str(exc)[:150])
        try:
            while True:
                status, data = fabric_events.get_nowait()
                if status == "error":
                    fabric_status.set("ACF / zatrzymany błąd odczytu: " + str(data))
                    continue
                sm = data["self_model"]
                structural = sm["adaptive_structure"]
                fixed = sm["fixed_structure"]
                recent = sm["route_mean_mse_recent"]
                selected = sm["selected_route"]
                mse = recent[selected]
                label = f"{mse:.5f}" if mse is not None else "brak pomiaru"
                fabric_status.set(
                    f"Bodźce: {sm['observations']} · nowe: {data['processed']}\n"
                    f"Neurony {structural['neurons']} vs kontrola {fixed['neurons']} "
                    f"· zmiany +{structural['total_grown']} / -{structural['total_pruned']}\n"
                    f"Przewidywanie: {selected} · zmierzony MSE: {label}"
                    + ("\nODZYSKANO ACF: poprzedni stan i ponowne "
                       "odtworzenie obserwacji."
                       if data.get("checkpoint_recovered") else ""))
        except queue.Empty:
            pass
        except (KeyError, TypeError, ValueError, RuntimeError, IndexError) as exc:
            fabric_status.set("ACF / błąd odczytu telemetrii: " + str(exc)[:140])
        # Queue entries can arrive before the worker thread has fully exited.
        # Recheck on every UI tick instead of stranding the next user turn.
        if running["ready"] and running["pending_message"] is not None:
            foreground = running["job"]
            if not isinstance(foreground, threading.Thread) or not foreground.is_alive():
                flush_message()
        elif running["ready"]:
            launch_semantic()
        if tab.winfo_exists():
            tab.after(140, poll)

    def on_destroy(event):
        if event.widget == tab:
            running["closing"] = True
            model.stop()

    tab.bind("<Destroy>", on_destroy, add="+")
    tab.after(0, refresh_status)
    # Separate 8-D topic measurements are only made from user questions
    # with the SAME opt-in sensory-learning switch; no transcript persisted.
    tab.after(1200, acf_tick)
    if auto_start:
        tab.after(400, initialize_model)
    tab.after(500, poll)
    tab.after(1700, autonomy_tick)
    return tab


def select_named_tab(parent: ttk.Notebook, name: str) -> bool:
    """Keyboard-button navigation uses existing real tabs, not hardcoded indices."""
    for index in range(parent.index("end")):
        if parent.tab(index, "text").strip() == name.strip():
            parent.select(index)
            return True
    return False
