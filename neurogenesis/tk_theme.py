"""Shared dark visual system for the real public Tk Windows application.

Used by the desktop launcher, real frozen UI self-test and Windows screenshot
acceptance so synthetic test images cannot silently show an entirely different
platform default light theme from the software users actually run.
"""
from __future__ import annotations

from tkinter import ttk


def apply_dark_tk_theme(root) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook", background="#07111d", borderwidth=0,
                    lightcolor="#07111d", darkcolor="#07111d")
    style.configure("TNotebook.Tab", padding=(16, 10), borderwidth=0,
                    font=("Segoe UI", 9, "bold"),
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
    style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(11, 8),
                    background="#164056", foreground="#e8fcff",
                    relief="flat", borderwidth=0)
    style.map("TButton", background=[("active", "#1c6678")],
              foreground=[("active", "#ffffff")])
    style.configure("TEntry", fieldbackground="#0e2839",
                    foreground="#ecfaff", insertcolor="#ecfaff",
                    bordercolor="#2b596c", padding=(6, 5))
    style.map("TEntry", fieldbackground=[("disabled", "#0b1c28")],
              foreground=[("disabled", "#728e99")])
    style.configure("TCombobox", fieldbackground="#0e2839",
                    foreground="#ecfaff", background="#164056",
                    bordercolor="#2b596c", arrowcolor="#7ce8db",
                    padding=(6, 5))
    style.map("TCombobox", fieldbackground=[("readonly", "#0e2839")],
              foreground=[("readonly", "#ecfaff")])
    style.configure("Vertical.TScrollbar", background="#164056",
                    troughcolor="#07111d", arrowcolor="#82cfce")

    style.configure("Treeview", background="#091d2d", foreground="#d8f7f1",
                    fieldbackground="#091d2d", borderwidth=0,
                    font=("Segoe UI", 9), rowheight=25)
    style.map("Treeview",
              background=[("selected", "#14556b")],
              foreground=[("selected", "#efffff")])
    style.configure("Treeview.Heading", background="#123449",
                    foreground="#79e9da", font=("Segoe UI", 9, "bold"),
                    relief="flat")
    style.map("Treeview.Heading", background=[("active", "#1a5267")])
