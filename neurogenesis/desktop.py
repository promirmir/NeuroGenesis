"""Native Windows-first desktop shell for the existing NeuroGenesis v0.4 brain.

A text input is a sensory observation, not evidence of language understanding.
Internet and autonomous execution remain disabled until implemented and verified.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import queue
import tempfile
import threading
from typing import Any

from .memory import ExperienceMemory
from .autonomy import AutonomicSupervisor, WINDOW
from .web_sense import read_public_page, validate_public_url, WebSenseError

APP_NAME = "NeuroGenesis"


def _is_windows() -> bool:
    return os.name == "nt"


def default_data_dir() -> Path:
    """Persist memory outside a PyInstaller one-file extraction directory."""
    local = os.environ.get("LOCALAPPDATA")
    if _is_windows() and local:
        return Path(local) / APP_NAME
    return Path.home() / ".local" / "share" / APP_NAME


def default_db_path() -> Path:
    return default_data_dir() / "experiences.sqlite3"


def process_message(memory: ExperienceMemory, message: str, *, store_text: bool = False,
                    evidence_query: str | None = None,
                    evidence_source_url: str | None = None,
                    evidence_focus_terms: tuple[str, ...] = ()) -> dict[str, Any]:
    """Call the actual brain/memory transaction, without fabricating conversation."""
    if type(message) is not str or not message.strip():
        raise ValueError("Wiadomość nie może być pusta")
    if type(store_text) is not bool:
        raise ValueError("store_text must be boolean")
    if evidence_query is None:
        if evidence_source_url is not None or evidence_focus_terms:
            raise ValueError("context filters require an explicit contextual query")
    elif type(evidence_query) is not str or not evidence_query.strip() or len(evidence_query) > 512:
        raise ValueError("invalid bounded contextual evidence query")
    # Look up only user-taught exact associations before advancing the brain.
    # Long messages and punctuation-only stimuli remain valid observations.
    taught = (memory.taught_answer(message)
              if len(message) <= memory.MAX_QUESTION_LENGTH and message.strip(" ?!.")
              else None)
    # Source-backed *extractive* answers are distinct from manually taught
    # answers and from any untrained Foundation Brain output.
    question = message.strip().casefold()
    asks = ("?" in question or question.startswith(
        ("co ", "czym ", "kto ", "jak ", "gdzie ", "kiedy ", "ile ",
         "dlaczego ", "czy ", "który ", "jaki ", "jakie ")))
    evidence = (memory.answer_from_knowledge(
                    evidence_query if evidence_query is not None else message,
                    source_url=evidence_source_url,
                    focus_terms=evidence_focus_terms,
                    polar_question=(" ".join(message.casefold().split()).startswith(
                        ("czy ", "a czy "))))
                if taught is None and asks and len(message) <= 512 else None)
    result = memory.remember(message, source="desktop", store_text=store_text)
    reply = (taught["answer"] if taught is not None else
             evidence["answer"] if evidence is not None else
             "Odebrano bodziec i zaktualizowano stan sieci. "
             "Nie znam jeszcze odpowiedzi. Nie znalazłem też odpowiedniego źródła. Wpisz ją w polu nauki "
             "i kliknij «Naucz odpowiedzi».")
    return {
        "reply": reply,
        "response_kind": ("explicit_local_teaching" if taught else
                          "source_evidence" if evidence else "sensory_acknowledgement"),
        "sources": evidence.get("sources", [evidence["source"]]) if evidence else [],
        "evidence_review": evidence.get("evidence_review") if evidence else None,
        "context_used": evidence is not None and evidence_query is not None,
        "event_id": result["event_id"],
        "brain_step": result["brain_step"],
        "neurons": result["neurons"],
        "synapses": result["synapses"],
        "stored_raw_text": result["stored_raw_text"],
    }


def self_test() -> int:
    """Non-GUI integration smoke test for Windows EXE build CI."""
    with tempfile.TemporaryDirectory(prefix="neurogenesis-exe-check-") as directory:
        db = Path(directory) / "memory.sqlite3"
        first = ExperienceMemory(db)
        if first.status()["observations"] != 0:
            return 1
        result = process_message(first, "Bodziec próbny")
        reopened = ExperienceMemory(db)
        status = reopened.status()
        if not (result["brain_step"] == 4 and status["observations"] == 1
                and status["records_with_raw_text"] == 0
                and status["brain"]["steps"] == 4):
            return 2
        if not reopened.recall("Bodziec próbny")[0]["exact_hash_match"]:
            return 3
        # Frozen EXE must include the autonomy implementation without requiring a GUI.
        supervisor = AutonomicSupervisor(reopened)
        if supervisor.status()["new_events"] != 1:
            return 4
        if supervisor.cycle()["reason"] != "not_enough_new_experiences":
            return 5
        trained = reopened.teach("Czym jest NeuroGenesis?", "Eksperymentalny cyfrowy mózg.")
        if not trained["teaching_saved"] or reopened.status()["taught_responses"] != 1:
            return 6
        fresh = ExperienceMemory(db)
        if process_message(fresh, "CZYM JEST NEUROGENESIS??")["reply"] != "Eksperymentalny cyfrowy mózg.":
            return 7
        if fresh.status()["records_with_raw_text"] != 0:
            return 8
        if not fresh.forget_teaching("czym jest neurogenesis"):
            return 9
        # The frozen EXE must verify *real* web-to-brain SQLite persistence
        # using a local synthetic observation: NO outbound network in CI.
        from datetime import datetime, timezone
        import hashlib
        from .web_sense import WebObservation
        sample = "Publiczny tekst o neuronach, uczeniu i aktualnej wiedzy."
        synthetic = WebObservation(
            url="https://example.org/research", host="example.org",
            text=sample,
            content_sha256=hashlib.sha256(sample.encode("utf-8")).hexdigest(),
            retrieved_utc=datetime.now(timezone.utc).isoformat(),
            bytes_read=len(sample.encode("utf-8")))
        web_result = fresh.observe_web(synthetic)
        if web_result["web_duplicate"] or fresh.status()["web_observations"] != 1:
            return 12
        steps = fresh.brain().steps
        again = fresh.observe_web(synthetic)
        if not again["web_duplicate"] or fresh.brain().steps != steps:
            return 13
        if not ExperienceMemory(db).recent_web()[0]["url"].endswith("/research"):
            return 14
        # Offline EXE gate: source-to-knowledge-to-cited-chat after reopening.
        new_session = ExperienceMemory(db)
        grounded = process_message(new_session, "Co wiadomo o neuronach i uczeniu?")
        if (grounded["response_kind"] != "source_evidence"
                or synthetic.url not in grounded["reply"]
                or new_session.status()["knowledge"]["documents"] != 1):
            return 15
        # Verify the Windows frozen EXE includes the actual offline backup
        # module: snapshot, SHA check, a non-destructive restored copy.
        from .recovery import (backup_private_database, inspect_private_database,
                               restore_to_new_database)
        snapshot = Path(directory) / "snapshot.sqlite3"
        restored = Path(directory) / "restored.sqlite3"
        result = backup_private_database(db, snapshot)
        if result["integrity"] != "ok" or result["source_versions"] != 1:
            return 16
        if inspect_private_database(snapshot, expected_sha256=result["sha256"])["sha256"] != result["sha256"]:
            return 17
        restored_report = restore_to_new_database(snapshot, restored, confirmed=True)
        if (restored_report["sha256"] != result["sha256"]
                or ExperienceMemory(restored).status()["knowledge"]["documents"] != 1
                or ExperienceMemory(db).status()["knowledge"]["documents"] != 1):
            return 18
    return 0


def ui_self_test() -> int:
    """Run actual default Tk Mission Control widgets on isolated SQLite.

    Distinct from the headless brain smoke: this verifies that a FROZEN
    public Windows EXE contains and can initialize the new default GUI.
    """
    import tkinter as tk
    from tkinter import ttk
    from .tk_mission import MissionDashboard

    with tempfile.TemporaryDirectory(prefix="ng-public-tk-ui-check-") as folder:
        memory = ExperienceMemory(Path(folder) / "synthetic-private.sqlite3")
        root = tk.Tk()
        root.withdraw()
        try:
            root.geometry("1350x830")
            tabs = ttk.Notebook(root)
            tabs.pack(fill="both", expand=True)
            dashboard = ttk.Frame(tabs)
            tabs.add(dashboard, text="CENTRUM")
            mission = MissionDashboard(
                dashboard, memory, navigate=lambda _where: None,
                network_enabled=lambda: False)
            tabs.select(dashboard)
            root.update_idletasks()
            if mission.refresh() or mission.metrics["steps"].get() != "0":
                return 31
            before = tuple(mission._samples)
            mission.refresh()
            if tuple(mission._samples) != before:
                return 32
            result = process_message(memory, "Syntetyczny bodziec GUI")
            if not mission.refresh():
                return 33
            if (mission._last is None or mission._last.step != result["brain_step"]
                    or not mission.graph._latest
                    or mission.graph._latest.step != result["brain_step"]):
                return 34
            if mission.modules["network"].get() != "WYŁĄCZONY":
                return 35
            if len(mission._samples) != len(before) + 1:
                return 36
        finally:
            root.destroy()
    return 0


def launch(db_path: Path) -> int:
    """Create a native local-first window; web access is off until enabled."""
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    try:
        memory = ExperienceMemory(db_path)
        memory.status()  # do not silently reset malformed persisted brains
        supervisor = AutonomicSupervisor(memory)
        supervisor.status()
    except Exception as exc:
        # This error is shown locally. Never overwrite or discard corrupted DB.
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("NeuroGenesis — pamięć", f"Nie można otworzyć pamięci. Dane nie zostały zresetowane.\n\n{exc}")
        root.destroy()
        return 1

    root = tk.Tk()
    root.title("NeuroGenesis — Mission Control / cyfrowy mózg")
    # The user may have a laptop, high-DPI display or constrained remote
    # desktop. Never position a 1450x920 first-launch window off-screen.
    available_width = max(780, root.winfo_screenwidth() - 34)
    available_height = max(580, root.winfo_screenheight() - 92)
    root.geometry(f"{min(1450, available_width)}x{min(920, available_height)}")
    root.minsize(min(940, available_width), min(620, available_height))
    root.configure(bg="#07111d")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook", background="#07111d", borderwidth=0,
                    lightcolor="#07111d", darkcolor="#07111d")
    style.configure("TNotebook.Tab", padding=(21, 12), borderwidth=0,
                    font=("Segoe UI", 10, "bold"),
                    background="#112637", foreground="#a5c6d3",
                    focuscolor="#112637")
    style.map("TNotebook.Tab",
              background=[("selected", "#135468"), ("active", "#1a4155")],
              foreground=[("selected", "#e8ffff"), ("active", "#ffffff")],
              expand=[("selected", (0, 0, 0, 0))])
    style.configure("TFrame", background="#07111d")
    style.configure("TLabel", background="#07111d", foreground="#cde9ef",
                    font=("Segoe UI", 10))
    style.configure("TCheckbutton", background="#07111d", foreground="#cde9ef")
    style.map("TCheckbutton", background=[("active", "#07111d")],
              foreground=[("active", "#ffffff")])
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(14, 10),
                    background="#164056", foreground="#e8fcff",
                    relief="flat", borderwidth=0)
    style.map("TButton", background=[("active", "#1c6678")],
              foreground=[("active", "#ffffff")])

    header = tk.Frame(root, bg="#07111d")
    header.pack(fill="x", padx=24, pady=(16, 10))
    logo = tk.Frame(header, bg="#07111d")
    logo.pack(side="left")
    tk.Label(logo, text="NEUROGENESIS", bg="#07111d", fg="#f4fffb",
             font=("Segoe UI", 22, "bold")).pack(anchor="w")
    tk.Label(logo, text="MISSION CONTROL  /  LOCAL RESEARCH ENVIRONMENT",
             bg="#07111d", fg="#53e9d5",
             font=("Consolas", 9, "bold")).pack(anchor="w")
    tk.Label(header, text="Miron przy pomocy AI    •    PRYWATNA PAMIĘĆ    •    HTTPS TYLKO PO ZGODZIE",
             bg="#07111d", fg="#95b8c7", font=("Segoe UI", 9)).pack(
                 side="right", padx=(10, 0))
    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True, padx=18, pady=(0, 15))
    mission_tab = ttk.Frame(tabs)
    tabs.add(mission_tab, text="  CENTRUM  ")
    chat_tab = ttk.Frame(tabs)
    brain_tab = ttk.Frame(tabs)
    web_tab = ttk.Frame(tabs)
    tabs.add(chat_tab, text="Rozmowa")
    tabs.add(brain_tab, text="Mózg")
    tabs.add(web_tab, text="Internet")
    backup_tab = ttk.Frame(tabs)
    tabs.add(backup_tab, text="Kopia pamięci")

    tk.Label(backup_tab, text="Ochrona zapisanej wiedzy i pamięci",
             bg="#111827", fg="#f8fafc",
             font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(24, 9))
    tk.Label(backup_tab, text=(
        "Kopie obejmują pełny stan SQLite: neuronowy, doświadczenia, "
        "nauczone odpowiedzi, źródła i zgody. Plik nie jest szyfrowany; "
        "przechowuj go prywatnie. Żadne dane nie są wysyłane do sieci."),
        bg="#111827", fg="#b8cbe0", anchor="w", justify="left",
        wraplength=760).pack(fill="x", padx=24, pady=(0, 14))
    backup_controls = tk.Frame(backup_tab, bg="#111827")
    backup_controls.pack(fill="x", padx=24)
    backup_state = tk.StringVar(value="Kopia nie była jeszcze wykonywana w tej sesji.")
    tk.Label(backup_tab, textvariable=backup_state, bg="#111827", fg="#93e5c9",
             anchor="nw", justify="left", wraplength=780,
             font=("Consolas", 10)).pack(fill="x", padx=24, pady=(14, 10))
    tk.Label(backup_tab, text=(
        "Przywrócenie zapisuje NOWĄ bazę i nigdy nie usuwa ani "
        "nie nadpisuje aktualnej. Instrukcja: docs/MEMORY_RECOVERY.md."),
        bg="#111827", fg="#93a4bc", anchor="w", justify="left",
        wraplength=760).pack(fill="x", padx=24)

    chat_header = tk.Frame(chat_tab, bg="#07111d")
    chat_header.pack(fill="x", padx=20, pady=(15, 9))
    tk.Label(chat_header, text="CONVERSATION / SOURCE CONSOLE",
             bg="#07111d", fg="#f1ffff", anchor="w",
             font=("Segoe UI", 16, "bold")).pack(side="left")
    tk.Label(chat_header, text="● OFFLINE FIRST  /  REAL SQLITE",
             bg="#07111d", fg="#59dccf",
             font=("Consolas", 9, "bold")).pack(side="right")
    tk.Label(chat_tab, text=("Odpowiedzi pochodzą z ręcznej nauki lub cytowanych źródeł. "
                              "Dopóki brak źródła, system nie udaje rozumienia."),
             bg="#07111d", fg="#91b7c6", anchor="w", font=("Segoe UI", 10),
             wraplength=1020).pack(fill="x", padx=20, pady=(0, 10))
    history = tk.Text(chat_tab, font=("Segoe UI", 11), bg="#0c2031", fg="#d7f3fd",
                      insertbackground="#e2e8f0", wrap="word", relief="flat",
                      padx=20, pady=17, height=12, state="disabled",
                      highlightbackground="#235166", highlightthickness=1)
    history.pack(fill="both", expand=True, padx=20, pady=(0, 11))
    history.tag_configure("human", foreground="#74efdc")
    history.tag_configure("assistant", foreground="#e2f5ff")
    history.tag_configure("system", foreground="#819eb2",
                          font=("Consolas", 9))
    history.configure(state="normal")
    history.insert("end", "LOCAL SESSION  /  Twoja rozmowa nie jest wysyłana do Internetu.\n"
                         "Wpisz pytanie poniżej lub wybierz badanie źródeł.\n\n",
                   "system")
    history.configure(state="disabled")
    tk.Label(chat_tab, text="TWOJA WIADOMOŚĆ / PYTANIE", bg="#07111d",
             fg="#6fe1d7", font=("Consolas", 9, "bold")).pack(anchor="w", padx=20)
    message = tk.Text(chat_tab, height=3, font=("Segoe UI", 11), bg="#102739", fg="#f1f9ff",
                      insertbackground="#8bf6df", wrap="word", relief="flat",
                      padx=14, pady=10,
                      highlightthickness=1, highlightbackground="#245367")
    message.pack(fill="x", padx=20, pady=(6, 9))
    controls = tk.Frame(chat_tab, bg="#07111d")
    controls.pack(fill="x", padx=20, pady=(0, 10))
    store_text = tk.BooleanVar(value=False)
    ttk.Checkbutton(controls, text="Zapisuj pełną treść prywatnie (opcjonalnie)", variable=store_text).pack(side="left")
    info = ttk.Label(controls, text="Tekst nie jest wysyłany do internetu")
    info.pack(side="left", padx=18)
    teach_area = tk.Frame(chat_tab, bg="#07111d")
    teach_area.pack(fill="x", padx=20, pady=(0, 10))
    tk.Label(teach_area,
             text="Naucz odpowiedzi na pytanie z pola powyżej (zapis lokalny, tylko na żądanie):",
             bg="#07111d", fg="#a6c8d1", anchor="w").pack(fill="x")
    answer_input = tk.Text(teach_area, height=2, font=("Segoe UI", 10),
                           bg="#102739", fg="#f1f9ff", wrap="word",
                           insertbackground="#8bf6df", relief="flat", padx=10, pady=6,
                           highlightthickness=1, highlightbackground="#245367")
    answer_input.pack(fill="x", pady=(4, 5))
    teaching_controls = tk.Frame(teach_area, bg="#07111d")
    teaching_controls.pack(fill="x")

    status_text = tk.StringVar(value="Odczytywanie stanu...")
    tk.Label(brain_tab, textvariable=status_text, bg="#111827", fg="#e2e8f0",
             justify="left", anchor="nw", font=("Consolas", 12)).pack(fill="x", padx=24, pady=(24, 14))
    canvas = tk.Canvas(brain_tab, bg="#060c17", highlightthickness=0, height=420)
    canvas.pack(fill="both", expand=True, padx=24, pady=(0, 12))
    from .tk_connectome import TkConnectome
    from .neural_telemetry import snapshot_neural_telemetry
    neural_graph = TkConnectome(canvas)
    ttk.Label(brain_tab, text=(
        "Rzeczywista mapa sieci LIF: światło oznacza zapisane impulsy, "
        "linie — faktyczne synapsy, barwa i grubość — ich wagi. "
        "Przy braku nowych kroków graf pozostaje nieruchomy. "
        "Kółko myszy = przybliżanie. To nie jest mapa Foundation Brain ani świadomości."),
        wraplength=750).pack(anchor="w", padx=24)
    autonomy_controls = tk.Frame(brain_tab, bg="#111827")
    autonomy_controls.pack(fill="x", padx=24, pady=(12, 4))
    autonomy_enabled = tk.BooleanVar(value=False)
    ttk.Checkbutton(autonomy_controls,
                    text="AUTO: testuj ulepszenia co 30 s (wymaga nowych doświadczeń)",
                    variable=autonomy_enabled).pack(side="left")
    autonomy_info = tk.StringVar(value="Automatyczny samorozwój wyłączony")
    ttk.Label(brain_tab, textvariable=autonomy_info, wraplength=750).pack(
        fill="x", padx=24, pady=(4, 8))

    tk.Label(web_tab, text="Internet — kontrolowane źródła i lokalna pamięć wiedzy",
             bg="#111827", fg="#f8fafc",
             font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(22, 6))
    ttk.Label(web_tab, text=("Tylko publiczne strony HTTPS:443, bez przekierowań "
                             "i wykonywania kodu. Nic nie jest pobierane bez zgody. "
                             "Wybrane fragmenty są zapisywane w prywatnej bazie "
                             "do cytowanych odpowiedzi. Strony są niezaufanymi danymi, "
                             "nie poleceniami."),
              wraplength=780).pack(anchor="w", padx=24, pady=(0, 8))
    web_enabled = tk.BooleanVar(value=False)
    web_auto = tk.BooleanVar(value=False)
    from .tk_mission import MissionDashboard
    from .tk_foundation_lab import install_foundation_lab
    foundation_tab = install_foundation_lab(tabs)
    targets = {
        "foundation": foundation_tab,
        "chat": chat_tab,
        "brain": brain_tab,
        "web": web_tab,
        "mission": mission_tab,
    }
    mission = MissionDashboard(
        mission_tab, memory,
        navigate=lambda where: tabs.select(targets[where]),
        network_enabled=lambda: web_enabled.get(),
    )
    # Dedicated specialist study tab, off until explicit HTTPS consent.
    from .study_panel import install_study_panel
    install_study_panel(tabs, memory, web_enabled)
    ttk.Checkbutton(web_tab, text="Włącz odczyt HTTPS (domyślnie WYŁĄCZONY)",
                    variable=web_enabled).pack(anchor="w", padx=24, pady=3)
    ttk.Checkbutton(web_tab, text="Sprawdzaj zatwierdzony adres co 5 minut (opcjonalnie)",
                    variable=web_auto).pack(anchor="w", padx=24, pady=3)
    web_url = tk.StringVar(value="")
    ttk.Label(web_tab, text="Publiczny adres HTTPS bez parametrów i danych dostępowych:").pack(
        anchor="w", padx=24, pady=(10, 4))
    web_entry = ttk.Entry(web_tab, textvariable=web_url, font=("Segoe UI", 11))
    web_entry.pack(fill="x", padx=24)
    web_buttons = tk.Frame(web_tab, bg="#111827")
    web_buttons.pack(fill="x", padx=24, pady=10)
    fetch_button = ttk.Button(web_buttons, text="Pobierz stronę i przekaż mózgowi")
    fetch_button.pack(side="left")
    web_state = tk.StringVar(value="Internet wyłączony. Dane rozmowy nie są wysyłane.")
    ttk.Label(web_tab, textvariable=web_state, wraplength=800).pack(
        anchor="w", padx=24, pady=(4, 8))
    web_content = tk.Text(web_tab, bg="#172237", fg="#e2e8f0",
                          wrap="word", font=("Segoe UI", 10), padx=12,
                          pady=10, relief="flat", state="disabled")
    web_content.pack(fill="both", expand=True, padx=24, pady=(0, 14))
    web_queue = queue.SimpleQueue()
    web_pending = {"value": False}
    approved_web_url = {"value": None}

    def append(role: str, text: str) -> None:
        history.configure(state="normal")
        style_tag = "human" if role == "Ty" else "assistant"
        history.insert("end", f"{role.upper()}  /  {text}\n\n", style_tag)
        history.configure(state="disabled")
        history.see("end")

    backup_queue: queue.SimpleQueue[tuple[str, Any]] = queue.SimpleQueue()
    backup_pending = {"value": False}

    def start_backup_operation(mode: str) -> None:
        if backup_pending["value"]:
            return
        if mode == "backup":
            if not messagebox.askyesno(
                    "Prywatna kopia NeuroGenesis",
                    "Kopia zawiera prywatną wiedzę i nie jest szyfrowana. "
                    "Czy utworzyć lokalną kopię bez nadpisywania plików?"):
                return
            chosen = filedialog.asksaveasfilename(
                title="Nowa kopia pamięci (wymaga wolnej nazwy)",
                initialdir=str(db_path.parent),
                initialfile="NeuroGenesis-backup.sqlite3",
                defaultextension=".sqlite3",
                filetypes=[("SQLite NeuroGenesis", "*.sqlite3")])
        else:
            chosen = filedialog.askopenfilename(
                title="Wybierz kopię do sprawdzenia",
                initialdir=str(db_path.parent),
                filetypes=[("SQLite NeuroGenesis", "*.sqlite3")])
        if not chosen:
            return
        backup_pending["value"] = True
        save_backup_btn.configure(state="disabled")
        verify_backup_btn.configure(state="disabled")
        backup_state.set("Kopia lub kontrola integralności w toku — nie zamykaj programu.")

        def worker() -> None:
            try:
                from .recovery import backup_private_database, inspect_private_database
                report = (backup_private_database(db_path, chosen)
                          if mode == "backup"
                          else inspect_private_database(chosen))
                backup_queue.put(("ok", (mode, report)))
            except Exception as exc:
                backup_queue.put(("error", type(exc).__name__))

        threading.Thread(target=worker, name="NeuroGenesis-local-memory-backup",
                         daemon=True).start()

    save_backup_btn = ttk.Button(
        backup_controls, text="Utwórz zweryfikowaną kopię",
        command=lambda: start_backup_operation("backup"))
    save_backup_btn.pack(side="left")
    verify_backup_btn = ttk.Button(
        backup_controls, text="Sprawdź wybraną kopię",
        command=lambda: start_backup_operation("verify"))
    verify_backup_btn.pack(side="left", padx=(12, 0))

    def poll_backup_queue() -> None:
        try:
            while True:
                status, payload = backup_queue.get_nowait()
                backup_pending["value"] = False
                save_backup_btn.configure(state="normal")
                verify_backup_btn.configure(state="normal")
                if status == "ok":
                    mode, report = payload
                    backup_state.set(
                        ("Kopia zapisana i sprawdzona" if mode == "backup"
                         else "Kontrola integralności zaliczona")
                        + f" · {report['observations']} doświadczeń"
                        + f" · {report['source_versions']} wersji źródeł"
                        + "\nSHA-256: " + report["sha256"])
                else:
                    backup_state.set("Nie ukończono operacji — bez zmiany oryginalnych danych. "
                                     "Powód: " + payload)
        except queue.Empty:
            pass
        root.after(250, poll_backup_queue)

    root.after(250, poll_backup_queue)

    def refresh() -> None:
        try:
            st = memory.status()
            bs = st["brain"]
            status_text.set(
                f"Kroki: {bs['steps']}\nNeurony: {bs['neurons']}\nSynapsy: {bs['synapses']}\n"
                f"Wzorce sensoryczne: {bs['stored_patterns']}\n"
                f"Utworzone neurony: {bs['total_grown']}\nUsunięte synapsy: {bs['total_pruned']}\n"
                f"Zapisane doświadczenia: {st['observations']}\n"
                f"Doświadczenia z pełnym tekstem: {st['records_with_raw_text']}\n"
                f"Ręcznie nauczone odpowiedzi: {st['taught_responses']}\n"
                f"Źródła internetowe: {st['web_observations']}\n"
                f"Dokumenty wiedzy: {st['knowledge']['documents']}\n"
                f"Fragmenty wiedzy: {st['knowledge']['passages']}"
            )
            health = supervisor.status()
            autonomy_info.set(
                f"Samorozwój: {'AUTO' if autonomy_enabled.get() else 'ręczny'}; "
                f"nowe doświadczenia {health['new_events']}/{WINDOW}; "
                f"próby {health['cycles']}; zatwierdzone {health['promotions']}")
            # The separately scheduled visible-pane poll below renders the
            # actual connectome only after a *new persisted brain step*.
            # Never invent neural activity by redrawing per UI refresh.
        except (ValueError, OSError, KeyError) as exc:
            status_text.set(f"Błąd odczytu stanu: {exc}")

    def try_improve() -> None:
        try:
            result = supervisor.cycle()
            if result["reason"] == "not_enough_new_experiences":
                summary = f"Brakuje obserwacji: {result['available']}/{result['required']}"
            else:
                summary = ("Ulepszenie zatwierdzone" if result["promoted"]
                           else "Zmiana odrzucona: " + result["reason"])
            refresh()
            autonomy_info.set(summary)
        except (ValueError, OSError, RuntimeError, KeyError) as exc:
            autonomy_enabled.set(False)
            autonomy_info.set("Samorozwój zatrzymany: problem z pamięcią lub walidacją")
            messagebox.showerror("NeuroGenesis — samorozwój",
                                 f"Nie zmieniono danych po nieudanej próbie: {exc}")

    ttk.Button(autonomy_controls, text="Przetestuj ulepszenie",
               command=try_improve).pack(side="right")

    def autonomy_tick() -> None:
        if autonomy_enabled.get():
            try_improve()
        root.after(30_000, autonomy_tick)

    root.after(30_000, autonomy_tick)

    def web_request(*, automatic: bool = False) -> None:
        if not web_enabled.get():
            if not automatic:
                messagebox.showwarning("Internet wyłączony",
                                       "Najpierw zaznacz zgodę na odczyt HTTPS.")
            return
        if web_pending["value"]:
            return
        candidate = approved_web_url["value"] if automatic else web_url.get().strip()
        if automatic and (not candidate or web_url.get().strip() != candidate):
            web_auto.set(False)
            web_state.set("Zmiana adresu wymaga ponownej zgody i ręcznego odczytu.")
            return
        try:
            canonical, _, _ = validate_public_url(candidate)
        except WebSenseError as exc:
            web_state.set(str(exc))
            if not automatic:
                messagebox.showerror("Nieprawidłowy adres", str(exc))
            return
        if not automatic:
            approved_web_url["value"] = canonical
            web_url.set(canonical)
        web_pending["value"] = True
        fetch_button.configure(state="disabled")
        web_state.set("Trwa połączenie HTTPS i kontrola źródła...")

        def worker() -> None:
            try:
                observation = read_public_page(canonical)
                web_queue.put(("ok", observation))
            except (WebSenseError, OSError, ValueError) as exc:
                web_queue.put(("error", str(exc)))
            except Exception:
                web_queue.put(("error", "Niezidentyfikowany błąd odczytu sieciowego"))

        threading.Thread(target=worker, name="NeuroGenesis-web-read",
                         daemon=True).start()

    def poll_web_queue() -> None:
        try:
            while True:
                kind, payload = web_queue.get_nowait()
                web_pending["value"] = False
                fetch_button.configure(state="normal")
                if kind == "error":
                    web_state.set("Nie pobrano strony: " + payload)
                    continue
                if not web_enabled.get():
                    web_state.set("Odczyt ukończony, ale dostęp wyłączono; "
                                  "nie zapisano danych do mózgu.")
                    continue
                try:
                    result = memory.observe_web(payload)
                    refresh()
                    if result["web_duplicate"]:
                        web_state.set("Strona bez zmian. Nie powtórzono uczenia.")
                    else:
                        web_state.set(
                            f"Nowy bodziec: {payload.host}; "
                            f"bajty {payload.bytes_read}; "
                            f"krok mózgu {result['brain_step']}; "
                            f"sha256 {payload.content_sha256[:16]}...")
                    web_content.configure(state="normal")
                    web_content.delete("1.0", "end")
                    web_content.insert(
                        "end", "Źródło: " + payload.url + "\n"
                        + "Odczyt UTC: " + payload.retrieved_utc + "\n"
                        + "SHA-256: " + payload.content_sha256 + "\n\n"
                        + payload.text)
                    web_content.configure(state="disabled")
                except (ValueError, OSError, RuntimeError) as exc:
                    web_enabled.set(False)
                    web_auto.set(False)
                    web_state.set("Błąd zapisu do prywatnej bazy: " + str(exc))
                    messagebox.showerror("NeuroGenesis — pamięć", str(exc))
        except queue.Empty:
            pass
        root.after(250, poll_web_queue)

    def periodic_web() -> None:
        if web_auto.get() and web_enabled.get() and not web_pending["value"]:
            web_request(automatic=True)
        root.after(300_000, periodic_web)

    fetch_button.configure(command=web_request)
    root.after(250, poll_web_queue)
    root.after(300_000, periodic_web)

    def poll_neural_graph() -> None:
        if tabs.select() == str(brain_tab):
            try:
                neural_graph.render(snapshot_neural_telemetry(memory.brain()))
            except (ValueError, OSError, RuntimeError):
                status_text.set("Nie można odczytać zweryfikowanego stanu sieci.")
        root.after(650, poll_neural_graph)

    canvas.bind("<Configure>", lambda _event: (
        neural_graph.render(neural_graph._latest, force=True)
        if neural_graph._latest is not None else None))
    root.after(650, poll_neural_graph)

    def mission_tick() -> None:
        if tabs.select() == str(mission_tab):
            try:
                mission.refresh()
            except (ValueError, OSError, RuntimeError, KeyError):
                mission.status.configure(text="BŁĄD ODCZYTU PAMIĘCI",
                                         fg="#f5b18b")
        root.after(700, mission_tick)

    root.after(700, mission_tick)

    def refresh_tick() -> None:
        refresh()
        root.after(3000, refresh_tick)

    root.after(3000, refresh_tick)
    send_button = ttk.Button(controls, text="Przekaż do mózgu")
    send_button.pack(side="right")

    def send() -> None:
        content = message.get("1.0", "end-1c").strip()
        if not content:
            return
        send_button.configure(state="disabled")
        root.update_idletasks()
        try:
            result = process_message(memory, content, store_text=store_text.get())
        except (ValueError, OSError) as exc:
            messagebox.showerror("NeuroGenesis", f"Nie udało się zapisać obserwacji: {exc}")
        else:
            append("Ty", content)
            append("NeuroGenesis", result["reply"])
            message.delete("1.0", "end")
            refresh()
        finally:
            send_button.configure(state="normal")

    def teach_answer() -> None:
        question = message.get("1.0", "end-1c").strip()
        answer = answer_input.get("1.0", "end-1c").strip()
        try:
            result = memory.teach(question, answer)
        except (ValueError, OSError) as exc:
            messagebox.showerror("NeuroGenesis — nauka", str(exc))
        else:
            append("Nauka", f"Zapisano odpowiedź po kroku mózgu {result['brain_step']}. "
                   "Możesz teraz wysłać pytanie, aby ją odtworzyć.")
            answer_input.delete("1.0", "end")
            refresh()

    def forget_answer() -> None:
        question = message.get("1.0", "end-1c").strip()
        if not question:
            messagebox.showwarning("NeuroGenesis", "Wpisz pytanie, którego odpowiedź usunąć.")
            return
        if not messagebox.askyesno("NeuroGenesis — usuń naukę",
                                   "Usunąć zapamiętaną odpowiedź na wpisane pytanie?"):
            return
        try:
            deleted = memory.forget_teaching(question)
        except (ValueError, OSError) as exc:
            messagebox.showerror("NeuroGenesis", str(exc))
        else:
            append("Pamięć", "Usunięto odpowiedź." if deleted else
                   "Brak takiej nauczonej odpowiedzi.")
            refresh()

    ttk.Button(teaching_controls, text="Naucz odpowiedzi",
               command=teach_answer).pack(side="left")
    ttk.Button(teaching_controls, text="Usuń nauczoną odpowiedź",
               command=forget_answer).pack(side="left", padx=(10, 0))
    send_button.configure(command=send)
    message.bind("<Control-Return>", lambda _event: (send(), "break")[1])
    ttk.Label(chat_tab, text="Ctrl+Enter — zapytaj • przycisk Naucz: jawny zapis pary pytanie/odpowiedź w prywatnej bazie",
              wraplength=770).pack(anchor="w", padx=12, pady=(0, 8))
    tabs.select(mission_tab)
    mission.refresh()
    refresh()

    def on_close() -> None:
        if backup_pending["value"]:
            messagebox.showwarning(
                "Kopia pamięci w toku",
                "Sprawdź zakończenie lokalnego kopiowania przed zamknięciem aplikacji.")
            return
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NeuroGenesis desktop client")
    parser.add_argument("--self-test", action="store_true", help="test brain/SQLite persistence without GUI")
    parser.add_argument("--ui-self-test", action="store_true",
                        help="open real default Tk mission widgets against synthetic local data")
    parser.add_argument("--db", type=Path, default=None, help="explicit private database path")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.ui_self_test:
        return ui_self_test()
    return launch(args.db if args.db is not None else default_db_path())
