"""Operator-reviewed correction-memory dialog for the real Windows home.

Only deliberate SAVE writes a user's replacement answer, and only deliberate
FORGET deletes it. Model replies are NEVER silently memorized. This is a
simple independent window: closing it does not stop any neural worker.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from .corrective_memory import CorrectiveMemory


def open_corrections_dialog(parent: tk.Misc, store: CorrectiveMemory,
                            latest_exchange: dict[str, str],
                            *, on_change: Callable[[], None] | None = None
                            ) -> tk.Toplevel:
    if not isinstance(store, CorrectiveMemory):
        raise ValueError("A real private corrective memory is required.")

    win = tk.Toplevel(parent)
    win.title("NeuroGenesis — trwała pamięć zatwierdzonych poprawek")
    win.geometry("790x670")
    win.minsize(660, 555)
    win.configure(bg="#07111d")

    ttk.Label(win, text="PAMIĘĆ KOREKT / UCZENIE PRZEZ INFORMACJĘ ZWROTNĄ",
              font=("Segoe UI", 14, "bold")).pack(
                  anchor="w", padx=15, pady=(12, 4))
    ttk.Label(
        win, wraplength=740, justify="left",
        text=("Wpisz własną poprawną odpowiedź do pytania i świadomie ją "
              "zatwierdź. Program zapamięta tylko tę parę w prywatnym SQLite, "
              "po czym wykorzysta ją przy następnym pasującym pytaniu. "
              "Nie zapisuje automatycznie rozmów ani nie zmienia wag Qwen.")
    ).pack(fill="x", padx=15, pady=(0, 8))
    status = tk.StringVar(master=win, value="Brak operacji zapisu.")
    ttk.Label(win, text="Pytanie, do którego zapamiętać poprawkę:").pack(
        anchor="w", padx=15)
    question = tk.Text(win, height=3, wrap="word", font=("Segoe UI", 10))
    question.pack(fill="x", padx=15, pady=(3, 8))
    ttk.Label(win, text="Twoja sprawdzona / poprawiona odpowiedź (nie jest automatycznie generowana):"
              ).pack(anchor="w", padx=15)
    correction = tk.Text(win, height=7, wrap="word", font=("Segoe UI", 10))
    correction.pack(fill="x", padx=15, pady=(3, 6))
    ttk.Label(win, textvariable=status, wraplength=740).pack(
        fill="x", padx=15, pady=(0, 8))

    outer = ttk.LabelFrame(win, text="Zatwierdzone poprawki w tej lokalnej pamięci")
    outer.pack(fill="both", expand=True, padx=15, pady=(0, 9))
    tree = ttk.Treeview(outer, columns=("revision",), selectmode="browse")
    tree.heading("#0", text="ID / pytanie")
    tree.heading("revision", text="Wersja")
    tree.column("#0", width=610, stretch=True)
    tree.column("revision", width=70, stretch=False, anchor="center")
    tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scroll = ttk.Scrollbar(outer, orient="vertical", command=tree.yview)
    scroll.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scroll.set)
    cache: dict[int, dict] = {}

    def set_content(widget: tk.Text, value: str):
        widget.delete("1.0", "end")
        widget.insert("1.0", value)

    def fill_latest():
        value = latest_exchange.get("question", "")
        if value:
            set_content(question, value)
            set_content(correction, "")
            status.set("Ostatnie pytanie wstawione. Wpisz własną poprawkę.")
        else:
            status.set("Brak zakończonej rozmowy; wpisz pytanie ręcznie.")

    def refresh():
        try:
            rows = store.list_entries(limit=250)
        except (ValueError, OSError) as exc:
            status.set("Nie można odczytać korekt: " + str(exc)[:130])
            return
        cache.clear()
        for iid in tree.get_children():
            tree.delete(iid)
        for entry in rows:
            ident = entry["id"]
            cache[ident] = entry
            tree.insert("", "end", iid=str(ident),
                        text=f"#{ident}  {entry['question'][:110]}",
                        values=(entry["revision"],))
        win.title(f"NeuroGenesis — pamięć korekt ({len(rows)} wpisów)")

    def select(_event=None):
        chosen = tree.selection()
        if not chosen:
            return
        item = cache.get(int(chosen[0]))
        if item:
            set_content(question, item["question"])
            set_content(correction, item["correction"])
            status.set(f"Edycja zatwierdzonej korekty #{item['id']}. "
                       "Zapis wymaga ponownego potwierdzenia.")

    def save():
        q = question.get("1.0", "end-1c").strip()
        answer = correction.get("1.0", "end-1c").strip()
        if not messagebox.askyesno(
                "NeuroGenesis — zatwierdzenie pamięci",
                "Zachować dokładnie tę poprawkę w prywatnej pamięci "
                "i pozwolić lokalnemu Qwen wykorzystywać ją przy "
                "pasujących pytaniach? Nie zostanie wysłana do internetu.",
                parent=win):
            return
        try:
            result = store.approve(q, answer, confirmed=True)
        except (OSError, ValueError, PermissionError) as exc:
            messagebox.showerror("Odrzucono korektę", str(exc), parent=win)
            return
        refresh()
        status.set(f"Zapisano poprawkę #{result['id']}, wersja "
                   f"{result['revision']}; będzie dostępna po restarcie.")
        if on_change is not None:
            on_change()

    def delete():
        chosen = tree.selection()
        if not chosen:
            status.set("Najpierw zaznacz zapamiętaną poprawkę na liście.")
            return
        ident = int(chosen[0])
        if not messagebox.askyesno(
                "NeuroGenesis — zapomnij poprawkę",
                f"Usunąć zatwierdzoną poprawkę #{ident} z aktywnej pamięci "
                "i indeksu wyszukiwania? Nie usuwa to kopii systemowych.",
                parent=win):
            return
        try:
            deleted = store.forget(ident, confirmed=True)
        except (OSError, ValueError, PermissionError) as exc:
            messagebox.showerror("Usuwanie niemożliwe", str(exc), parent=win)
            return
        if deleted:
            set_content(question, "")
            set_content(correction, "")
            status.set(f"Usunięto korektę #{ident} z aktywnej pamięci.")
        refresh()
        if on_change is not None:
            on_change()

    tree.bind("<<TreeviewSelect>>", select)
    buttons = ttk.Frame(win)
    buttons.pack(fill="x", padx=15, pady=(0, 12))
    ttk.Button(buttons, text="OSTATNIE PYTANIE",
               command=fill_latest).pack(side="left")
    ttk.Button(buttons, text="ZAPAMIĘTAJ ZATWIERDZONĄ POPRAWKĘ",
               command=save).pack(side="left", padx=(8, 0))
    ttk.Button(buttons, text="ZAPOMNIJ WYBRANĄ",
               command=delete).pack(side="left", padx=(8, 0))
    ttk.Button(buttons, text="ZAMKNIJ", command=win.destroy).pack(side="right")
    refresh()
    fill_latest()
    return win
