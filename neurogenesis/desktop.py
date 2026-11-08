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
                    focus_terms=evidence_focus_terms)
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
    return 0


def launch(db_path: Path) -> int:
    """Create a native local-first window; web access is off until enabled."""
    import tkinter as tk
    from tkinter import messagebox, ttk

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
    root.title("NeuroGenesis — cyfrowy mózg")
    root.geometry("960x720")
    root.minsize(720, 560)
    root.configure(bg="#111827")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook", background="#111827", borderwidth=0)
    style.configure("TNotebook.Tab", padding=(20, 11), font=("Segoe UI", 10))
    style.configure("TFrame", background="#111827")
    style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
    style.configure("TCheckbutton", background="#111827", foreground="#cbd5e1")
    style.configure("TButton", font=("Segoe UI", 10), padding=(13, 8))

    header = tk.Frame(root, bg="#111827")
    header.pack(fill="x", padx=18, pady=(16, 8))
    tk.Label(header, text="NeuroGenesis", bg="#111827", fg="#f8fafc",
             font=("Segoe UI", 21, "bold")).pack(side="left")
    tk.Label(header, text="Miron przy pomocy AI  •  LOKALNIE  •  SIEĆ TYLKO PO ZGODZIE",
             bg="#111827", fg="#93a4bc", font=("Segoe UI", 9)).pack(side="right", padx=(10, 0))
    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True, padx=14, pady=(0, 14))
    chat_tab = ttk.Frame(tabs)
    brain_tab = ttk.Frame(tabs)
    web_tab = ttk.Frame(tabs)
    tabs.add(chat_tab, text="Rozmowa")
    tabs.add(brain_tab, text="Mózg")
    tabs.add(web_tab, text="Internet")

    tk.Label(chat_tab, text=("Mózg rejestruje bodźce. Odpowiedzi mogą pochodzić z ręcznej nauki "
                              "lub cytatów zapisanych źródeł. Cytaty nie oznaczają treningu modelu."),
             bg="#111827", fg="#a6b6c9", anchor="w", font=("Segoe UI", 10),
             wraplength=840).pack(fill="x", padx=12, pady=(12, 8))
    history = tk.Text(chat_tab, font=("Segoe UI", 11), bg="#172237", fg="#e2e8f0",
                      insertbackground="#e2e8f0", wrap="word", relief="flat",
                      padx=14, pady=12, state="disabled")
    history.pack(fill="both", expand=True, padx=12, pady=(0, 10))
    tk.Label(chat_tab, text="Napisz obserwację:", bg="#111827", fg="#e5e7eb").pack(anchor="w", padx=12)
    message = tk.Text(chat_tab, height=3, font=("Segoe UI", 11), bg="#172237", fg="#f1f5f9",
                      insertbackground="#e2e8f0", wrap="word", relief="flat", padx=10, pady=8)
    message.pack(fill="x", padx=12, pady=(5, 8))
    controls = tk.Frame(chat_tab, bg="#111827")
    controls.pack(fill="x", padx=12, pady=(0, 10))
    store_text = tk.BooleanVar(value=False)
    ttk.Checkbutton(controls, text="Zapisuj pełną treść prywatnie (opcjonalnie)", variable=store_text).pack(side="left")
    info = ttk.Label(controls, text="Tekst nie jest wysyłany do internetu")
    info.pack(side="left", padx=18)
    teach_area = tk.Frame(chat_tab, bg="#111827")
    teach_area.pack(fill="x", padx=12, pady=(0, 10))
    tk.Label(teach_area,
             text="Naucz odpowiedzi na pytanie z pola powyżej (zapis lokalny, tylko na żądanie):",
             bg="#111827", fg="#cbd5e1", anchor="w").pack(fill="x")
    answer_input = tk.Text(teach_area, height=2, font=("Segoe UI", 10),
                           bg="#172237", fg="#f1f5f9", wrap="word",
                           insertbackground="#e2e8f0", relief="flat", padx=8, pady=5)
    answer_input.pack(fill="x", pady=(4, 5))
    teaching_controls = tk.Frame(teach_area, bg="#111827")
    teaching_controls.pack(fill="x")

    status_text = tk.StringVar(value="Odczytywanie stanu...")
    tk.Label(brain_tab, textvariable=status_text, bg="#111827", fg="#e2e8f0",
             justify="left", anchor="nw", font=("Consolas", 12)).pack(fill="x", padx=24, pady=(24, 14))
    canvas = tk.Canvas(brain_tab, bg="#172237", highlightthickness=0, height=205)
    canvas.pack(fill="x", padx=24, pady=(0, 16))
    ttk.Label(brain_tab, text="Wykres przedstawia aktualne ślady aktywności neuronów; nie jest miarą świadomości.",
              wraplength=730).pack(anchor="w", padx=24)
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
        history.insert("end", f"{role}: {text}\n\n")
        history.configure(state="disabled")
        history.see("end")

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
            traces = memory.brain().traces
            canvas.delete("all")
            canvas.update_idletasks()
            width = max(200, canvas.winfo_width())
            for i, t in enumerate(traces[:96]):
                bw = width / max(1, len(traces[:96]))
                height = min(180, max(1, 180 * float(t) / 5))
                canvas.create_rectangle(i*bw+1, 195-height, (i+1)*bw-1, 195,
                                        fill="#34d399", outline="")
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
    refresh()

    def on_close() -> None:
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NeuroGenesis desktop client")
    parser.add_argument("--self-test", action="store_true", help="test brain/SQLite persistence without GUI")
    parser.add_argument("--db", type=Path, default=None, help="explicit private database path")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    return launch(args.db if args.db is not None else default_db_path())
