"""Self-contained TXT learning workspace: offline retrievable knowledge, not fake LLM gradients.

This provides an always-usable private knowledge ingest path even when the
frozen EXE has no PyTorch. Automatically observes ONLY an explicitly selected
local folder; import is auditable and never overwrites prior brain state.
"""
from __future__ import annotations

from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .local_knowledge import LocalKnowledge, MAX_TXT_BYTES


def install_bundled_training(parent, knowledge: LocalKnowledge) -> ttk.Frame:
    tab = ttk.Frame(parent)
    parent.add(tab, text="Trening TXT")
    parent.insert(1, tab)
    bg = "#07111d"
    cyan = "#68e6d5"
    tk.Label(tab, text="NEUROGENESIS  /  CONTINUOUS LEARNING CONSOLE",
             bg=bg, fg=cyan, font=("Segoe UI", 15, "bold")).pack(
                 fill="x", anchor="w", padx=16, pady=(15, 6))
    tk.Label(tab, bg=bg, fg="#b4d0d9", justify="left", wraplength=980,
             text=("Pełna funkcja EXE bez dodatkowego Pythona: wskazany plik TXT "
                   "jest indeksowany w prywatnej bazie SQLite. Od tej chwili "
                   "lokalny model wyszukuje fragmenty i wykorzystuje je "
                   "w odpowiedziach (RAG). To jest nauka wiedzy z dokumentów, "
                   "NIE dostrajanie wag sieci neuronowej LoRA. "
                   "Samorozwój obserwuje wyłącznie zatwierdzony folder lokalny.")
             ).pack(fill="x", padx=16, pady=(0, 10))
    status = tk.StringVar(value="GOTOWY / brak zadań; nic nie łączy się z siecią.")
    stats = tk.StringVar()
    selected = tk.StringVar()
    folder = tk.StringVar()
    auto = tk.BooleanVar(value=False)
    confirm_folder = tk.BooleanVar(value=False)
    events: queue.SimpleQueue = queue.SimpleQueue()
    running = {"thread": None, "closing": False}
    memo: dict[str, tuple[int, int]] = {}

    def refresh_stats():
        try:
            st = knowledge.status()
            stats.set(f"PRYWATNA BAZA: {st['files']} plików  /  "
                      f"{st['passages']} fragmentów  /  bez transferu danych")
        except Exception as exc:
            stats.set("Nie można odczytać bazy: " + str(exc)[:180])

    refresh_stats()
    tk.Label(tab, textvariable=stats, bg="#0a2837", fg="#c6faf0",
             padx=12, pady=12, font=("Consolas", 11, "bold")).pack(
                 fill="x", padx=16, pady=(0, 10))

    def choose_txt():
        path = filedialog.askopenfilename(
            title="Wybierz lokalny plik tekstowy UTF-8",
            filetypes=[("Tekst UTF-8", "*.txt")])
        if path:
            selected.set(path)

    def begin(task, action):
        current = running["thread"]
        if isinstance(current, threading.Thread) and current.is_alive():
            return False

        def worker():
            try:
                events.put(("ok", task, action()))
            except Exception as exc:
                events.put(("error", task, str(exc)))
        t = threading.Thread(target=worker, daemon=True,
                             name="NeuroGenesis-private-TXT-ingest")
        running["thread"] = t
        t.start()
        return True

    def import_selected():
        path = selected.get()
        if not path:
            choose_txt()
            path = selected.get()
        if not path:
            return
        if not messagebox.askyesno(
            "Zatwierdź import", "Wprowadzić wybrany lokalny TXT do prywatnej pamięci "
            "NeuroGenesis? Tekst pozostanie na tym komputerze."):
            return
        if begin("manual", lambda: knowledge.import_txt(path, approved=True)):
            status.set("UCZENIE Z TXT / dzielenie, indeksowanie i zapis transakcyjny…")

    row = ttk.Frame(tab)
    row.pack(fill="x", padx=16, pady=(5, 5))
    ttk.Entry(row, textvariable=selected).pack(side="left", fill="x", expand=True)
    ttk.Button(row, text="WYBIERZ PLIK TXT", command=choose_txt).pack(
        side="left", padx=(6, 0))
    ttk.Button(tab, text="NAUCZ SIĘ Z TEGO TXT / ZAPISZ WIEDZĘ OFFLINE",
               command=import_selected).pack(anchor="w", padx=16, pady=(1, 11))
    ttk.Separator(tab, orient="horizontal").pack(fill="x", padx=16, pady=(3, 10))
    tk.Label(tab, bg=bg, fg=cyan, anchor="w",
             text="SAMODZIELNE ZDOBYWANIE WIEDZY Z ZATWIERDZONEGO FOLDERU",
             font=("Segoe UI", 11, "bold")).pack(fill="x", padx=16, pady=(0, 4))
    tk.Label(tab, bg=bg, fg="#abc5ce", anchor="w", wraplength=980,
             justify="left",
             text=("Po aktywacji program co 45 sekund rozpoznaje nowe lub "
                   "zmienione TXT w tym jednym folderze i zapisuje nowe wersje "
                   "wiedzy. Kontrola jakości obejmuje integralność, format "
                   "UTF-8, limity i wersjonowanie. Nie jest to autonomiczne "
                   "trenowanie wag i nie daje nieograniczonych zdolności.")
             ).pack(fill="x", padx=16, pady=(0, 7))

    def choose_dir():
        selected_dir = filedialog.askdirectory(
            title="Wybierz zaufany folder TXT do monitorowania")
        if selected_dir:
            folder.set(selected_dir)
            auto.set(False)
            confirm_folder.set(False)
            memo.clear()

    row2 = ttk.Frame(tab)
    row2.pack(fill="x", padx=16, pady=4)
    ttk.Entry(row2, textvariable=folder).pack(side="left", fill="x", expand=True)
    ttk.Button(row2, text="WYBIERZ FOLDER", command=choose_dir).pack(
        side="left", padx=(6, 0))
    ttk.Checkbutton(tab,
        text="Potwierdzam, że wskazany folder zawiera tylko dane, które wolno mi przetwarzać lokalnie",
        variable=confirm_folder).pack(anchor="w", padx=16, pady=(8, 1))
    ttk.Checkbutton(tab,
        text="AKTYWNY SAMOROZWÓJ WIEDZY / automatycznie indeksuj nowe TXT",
        variable=auto).pack(anchor="w", padx=16, pady=(3, 9))
    ttk.Label(tab, textvariable=status, wraplength=920).pack(
        fill="x", padx=16, pady=(4, 6))
    log = tk.Text(tab, height=7, bg="#081e2d", fg="#c6f0e9",
                  font=("Consolas", 9), wrap="word", state="disabled",
                  padx=9, pady=7)
    log.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    def note(line):
        log.configure(state="normal")
        log.insert("end", line + "\n")
        log.see("end")
        log.configure(state="disabled")

    def poll():
        if running["closing"]:
            return
        try:
            while True:
                kind, task, value = events.get_nowait()
                if kind == "ok":
                    msg = (f"{value['status']}: {value.get('source','')}  "
                           f"/ {value.get('passages',0)} fragmentów")
                    status.set("ZAPIS ZAKOŃCZONY / wiedza dostępna dla Model Chat")
                    note(msg)
                    refresh_stats()
                else:
                    status.set("ODRZUCONO / " + str(value)[:200])
                    note("BŁĄD " + str(value)[:280])
        except queue.Empty:
            pass
        if tab.winfo_exists():
            tab.after(180, poll)

    def scan_folder():
        if running["closing"]:
            return
        if auto.get():
            path = Path(folder.get())
            if not confirm_folder.get() or not path.is_dir() or path.is_symlink():
                status.set("AUTO-WIEDZA WYŁĄCZONA: zatwierdź poprawny folder.")
                auto.set(False)
            else:
                try:
                    files = sorted(path.glob("*.txt"))[:30]
                    for f in files:
                        if f.is_symlink() or not f.is_file():
                            continue
                        st = f.stat()
                        if not 1 <= st.st_size <= MAX_TXT_BYTES:
                            continue
                        stamp = (st.st_size, st.st_mtime_ns)
                        key = str(f.resolve())
                        if memo.get(key) == stamp:
                            continue
                        current = running["thread"]
                        if isinstance(current, threading.Thread) and current.is_alive():
                            break
                        if begin("auto", lambda file=f: knowledge.import_txt(
                                file, approved=True)):
                            memo[key] = stamp
                            status.set("SAMOROZWÓJ / nowy lokalny TXT wykryty, indeksowanie…")
                            break
                except OSError as exc:
                    status.set("AUTO-WIEDZA / nie można skanować folderu: " + str(exc)[:160])
        if tab.winfo_exists():
            tab.after(45_000, scan_folder)

    def on_destroy(event):
        if event.widget == tab:
            running["closing"] = True
            auto.set(False)

    # Shared control-plane references: the autonomy dashboard toggles the
    # SAME watcher rather than creating a second scanner or hidden worker.
    tab.ng_auto = auto
    tab.ng_folder = folder
    tab.ng_consent = confirm_folder
    tab.ng_choose_folder = choose_dir
    tab.ng_training_status = status
    tab.bind("<Destroy>", on_destroy, add="+")
    tab.after(180, poll)
    tab.after(1200, scan_folder)
    return tab
