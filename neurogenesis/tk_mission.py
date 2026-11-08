"""Default Windows EXE Mission Control, bound to the ACTUAL persisted LIF brain.

No Qt dependency, external network call, fabricated neural activity, mock KPI
or new user-memory format. This is the native interface shipped in the existing
standalone Windows EXE; optional Qt remains a separately maintained source UI.
"""
from __future__ import annotations

from collections import deque
from typing import Callable
import tkinter as tk

from .memory import ExperienceMemory
from .neural_telemetry import NeuralTelemetry, snapshot_neural_telemetry
from .tk_connectome import TkConnectome
from .tk_hologram import HolographicBrain
from .tk_avatar import NeuralAvatar


BACKGROUND = "#07111d"
PANEL = "#0c1d2e"
DEEP = "#071522"
BORDER = "#234d63"
ACCENT = "#57e7d1"
PRIMARY = "#e7f9ff"
MUTED = "#8baebc"
GRID = "#204155"


def _label(parent: tk.Misc, text: str, *, size: int = 10,
           color: str = PRIMARY, bold: bool = False,
           background: str | None = None, **options) -> tk.Label:
    return tk.Label(parent, text=text, bg=background or BACKGROUND,
                    fg=color, font=("Segoe UI", size, "bold" if bold else "normal"),
                    anchor="w", **options)


def _panel(parent: tk.Misc, padding: int = 12) -> tuple[tk.Frame, tk.Frame]:
    border = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
    inner = tk.Frame(border, bg=PANEL, padx=padding, pady=padding)
    inner.pack(fill="both", expand=True)
    return border, inner


def _action(parent: tk.Misc, text: str, command: Callable[[], None],
            *, primary: bool = False) -> tk.Button:
    return tk.Button(
        parent, text=text, command=command, cursor="hand2",
        font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
        bg="#0d8186" if primary else "#123349",
        fg="#ffffff" if primary else "#d6f3f9",
        activebackground="#16a6ac" if primary else "#1a4c64",
        activeforeground="#ffffff", padx=14, pady=9,
        highlightthickness=0, takefocus=True)


class MissionDashboard:
    """Visually advanced dashboard; it only reads existing local memory."""

    def __init__(self, parent: tk.Misc, memory: ExperienceMemory,
                 *, navigate: Callable[[str], None],
                 network_enabled: Callable[[], bool]):
        self.parent = parent
        self.memory = memory
        self.navigate = navigate
        self.network_enabled = network_enabled
        self._last: NeuralTelemetry | None = None
        self._samples: deque[tuple[int, int]] = deque(maxlen=72)
        self._last_status: tuple[int, int, int, int, int, bool] | None = None

        self.scroll = tk.Canvas(parent, bg=BACKGROUND, bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.scroll.yview,
                                bg="#153348", troughcolor=BACKGROUND)
        self.scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.scroll.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.scroll, bg=BACKGROUND, padx=18, pady=14)
        self.window_id = self.scroll.create_window((0, 0), window=self.body,
                                                    anchor="nw")
        self.body.bind("<Configure>", self._body_resized)
        self.scroll.bind("<Configure>", self._viewport_resized)
        self.scroll.bind("<MouseWheel>", self._scroll_wheel)

        top = tk.Frame(self.body, bg=BACKGROUND)
        top.pack(fill="x", pady=(1, 13))
        _label(top, "01 / NEUROGENESIS SYSTEM", size=9, color=ACCENT, bold=True).pack(anchor="w")
        headline = tk.Frame(top, bg=BACKGROUND)
        headline.pack(fill="x", pady=(3, 4))
        _label(headline, "MISSION CONTROL", size=26, bold=True).pack(side="left")
        self.status = _label(headline, "● GOTOWY", size=10,
                             bold=True, color=ACCENT)
        self.status.pack(side="right", padx=(15, 0))
        _label(top, "Rzeczywisty zapisany stan mózgu LIF, prywatna pamięć i źródła · bez symulowanej inteligencji",
               size=10, color=MUTED).pack(anchor="w")

        metrics = tk.Frame(self.body, bg=BACKGROUND)
        metrics.pack(fill="x", pady=(0, 12))
        self.metrics: dict[str, tk.StringVar] = {}
        for index, (key, title, caption) in enumerate((
            ("steps", "LIF / KROKI", "Zapisane aktualizacje"),
            ("neurons", "NEURONY", "Rzeczywista sieć LIF"),
            ("synapses", "SYNAPSY", "Zapisane połączenia"),
            ("documents", "DOKUMENTY", "Pamięć lokalna SQLite"),
        )):
            metrics.columnconfigure(index, weight=1, uniform="tiles")
            card, inner = _panel(metrics, 14)
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 9 if index < 3 else 0))
            _label(inner, title, color="#82bbcb", size=9,
                   bold=True, background=PANEL).pack(anchor="w")
            value = tk.StringVar(value="—")
            self.metrics[key] = value
            tk.Label(inner, textvariable=value, font=("Segoe UI", 25, "bold"),
                     bg=PANEL, fg="#d9fff6", anchor="w").pack(fill="x", pady=(3, 1))
            _label(inner, caption, color=MUTED, size=9,
                   background=PANEL).pack(anchor="w")

        middle = tk.Frame(self.body, bg=BACKGROUND)
        middle.pack(fill="both", expand=True, pady=(0, 12))
        middle.columnconfigure(0, weight=5)
        middle.columnconfigure(1, weight=2, minsize=280)

        neural_card, neural = _panel(middle, 9)
        neural_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        band = tk.Frame(neural, bg=PANEL)
        band.pack(fill="x", padx=5, pady=(4, 8))
        _label(band, "NEURAL FABRIC / LIVE", size=12, bold=True,
               background=PANEL).pack(side="left")
        self.neural_step = _label(band, "BEZ NOWEGO KROKU", size=9,
                                  color=ACCENT, background=PANEL)
        self.neural_step.pack(side="right")
        # The actual shipped Windows EXE opens the 3D-looking view by default.
        # The original exact 2D connectivity plot is preserved one click away.
        self.hologram_canvas = tk.Canvas(neural, bg="#040d18", height=355,
                                         highlightthickness=0, bd=0)
        self.hologram_canvas.pack(fill="both", expand=True)
        self.hologram = HolographicBrain(self.hologram_canvas)
        self.neural_canvas = tk.Canvas(neural, bg="#050e1a", height=355,
                                       highlightthickness=0, bd=0)
        self.graph = TkConnectome(self.neural_canvas)
        self.neural_canvas.bind("<Configure>", self._resize_graph, add="+")
        self.avatar_canvas = tk.Canvas(neural, bg="#040d18", height=355,
                                       highlightthickness=0, bd=0)
        self.avatar = NeuralAvatar(self.avatar_canvas)
        self._view_mode = "3d"
        mode_row = tk.Frame(neural, bg=PANEL)
        self.mode_row = mode_row
        mode_row.pack(fill="x", padx=5, pady=(6, 0))
        self.view_label = tk.StringVar(value="HOLOGRAM 3D / PODGLĄD PRZESTRZENNY")
        _action(mode_row, "3D / 2D", self._toggle_neural_view).pack(side="left")
        _action(mode_row, "AWATAR", self._toggle_avatar_view).pack(side="left", padx=6)
        _action(mode_row, "PAUZA", self._toggle_hologram_motion).pack(side="left")
        tk.Label(neural, textvariable=self.view_label, bg=PANEL, fg=ACCENT,
                 font=("Consolas", 8, "bold")).pack(anchor="w", padx=6)
        _label(neural, "Mózg i awatar są symboliczne. Światło aktywności pojawia się wyłącznie po zapisanym kroku LIF.",
               color=MUTED, size=9, background=PANEL).pack(fill="x", padx=5, pady=(7, 1))
        _action(neural, "OTWÓRZ PEŁNY MONITOR MÓZGU  ›",
                lambda: navigate("brain")).pack(fill="x", pady=(7, 1))

        right = tk.Frame(middle, bg=BACKGROUND)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        signal_card, signals = _panel(right, 9)
        signal_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        _label(signals, "SPIKE TRACE / RZECZYWISTE", size=9, bold=True,
               background=PANEL, color=ACCENT).pack(anchor="w", pady=(0, 6))
        self.signal_canvas = tk.Canvas(signals, bg=DEEP, bd=0,
                                       highlightthickness=0, height=142)
        self.signal_canvas.pack(fill="both", expand=True)
        self.signal_canvas.bind("<Configure>", self._resize_signals)
        self.signal_label = tk.StringVar(value="Oczekiwanie na zapisany stan")
        tk.Label(signals, textvariable=self.signal_label, bg=PANEL, fg=MUTED,
                 font=("Consolas", 8), anchor="w").pack(fill="x", pady=(6, 0))

        event_card, event_inner = _panel(right, 9)
        event_card.grid(row=1, column=0, sticky="nsew")
        _label(event_inner, "EVENT JOURNAL / SQLITE", size=9, bold=True,
               background=PANEL, color=ACCENT).pack(anchor="w", pady=(0, 6))
        self.events = tk.Text(event_inner, height=7, width=27, wrap="word",
                              bg=DEEP, fg="#b9dde5",
                              font=("Consolas", 9), relief="flat",
                              padx=10, pady=8, state="disabled",
                              insertbackground=ACCENT, highlightthickness=0)
        self.events.pack(fill="both", expand=True)
        self._event("PAMIĘĆ / LOKALNA SQLITE. Brak nowych kroków.")

        pipeline_card, pipeline = _panel(self.body, 12)
        pipeline_card.pack(fill="x", pady=(0, 11))
        _label(pipeline, "SYSTEM MODULES / STAN FAKTYCZNY", size=10,
               bold=True, color=ACCENT, background=PANEL).pack(anchor="w", pady=(0, 10))
        channels = tk.Frame(pipeline, bg=PANEL)
        channels.pack(fill="x")
        self.modules: dict[str, tk.StringVar] = {}
        for index, (key, title, hint) in enumerate((
            ("network", "PERCEPTION / HTTPS", "Tylko po zgodzie"),
            ("memory", "LONG-TERM MEMORY", "Prywatna SQLite"),
            ("lif", "NEURAL SUBSTRATE", "Eksperymentalna LIF"),
            ("foundation", "FOUNDATION MODEL", "Oddzielne od rozmowy"),
        )):
            channels.columnconfigure(index, weight=1, uniform="modules")
            cell = tk.Frame(channels, bg="#0d2739", padx=10, pady=9,
                            highlightbackground="#2c5063", highlightthickness=1)
            cell.grid(row=0, column=index, sticky="nsew",
                      padx=(0, 9 if index < 3 else 0))
            _label(cell, title, size=9, color="#73c6d5", bold=True,
                   background="#0d2739").pack(anchor="w")
            value = tk.StringVar(value="—")
            self.modules[key] = value
            tk.Label(cell, textvariable=value, bg="#0d2739", fg=PRIMARY,
                     anchor="w", font=("Segoe UI", 10, "bold")).pack(
                         fill="x", pady=(4, 3))
            _label(cell, hint, size=8, color=MUTED,
                   background="#0d2739").pack(anchor="w")

        self.capacity_text = tk.StringVar(value="LIMIT SIECI LIF: odczytywanie...")
        tk.Label(self.body, textvariable=self.capacity_text, bg=BACKGROUND,
                 fg="#769eaf", font=("Consolas", 9)).pack(
                     anchor="w", pady=(0, 10))

        quick = tk.Frame(self.body, bg=BACKGROUND)
        quick.pack(fill="x", pady=(0, 4))
        for label, where in (
            ("ROZMOWA I ŹRÓDŁA", "chat"),
            ("BADANIE INTERNETU", "web"),
            ("PODGLĄD MÓZGU", "brain"),
        ):
            _action(quick, label, lambda section=where: navigate(section),
                    primary=where == "chat").pack(side="left", padx=(0, 10))
        _label(quick, "STATUS BADAWCZY · NIE AGI · BEZ UKRYTEJ SIECI",
               size=9, color=MUTED).pack(side="right")

    def _toggle_neural_view(self) -> None:
        # Preserve 3D↔2D semantics for existing users/tests. Clicking
        # the button from Avatar returns to the precise 2D graph.
        if self._view_mode == "3d":
            self._show_neural_view("2d")
        else:
            self._show_neural_view("3d")

    def _toggle_avatar_view(self) -> None:
        self._show_neural_view("3d" if self._view_mode == "avatar" else "avatar")

    def _show_neural_view(self, mode: str) -> None:
        if mode not in {"3d", "2d", "avatar"}:
            raise ValueError("invalid neural presentation mode")
        for canvas in (self.hologram_canvas, self.neural_canvas, self.avatar_canvas):
            canvas.pack_forget()
        canvas = {"3d": self.hologram_canvas, "2d": self.neural_canvas,
                  "avatar": self.avatar_canvas}[mode]
        canvas.pack(fill="both", expand=True, before=self.mode_row)
        self._view_mode = mode
        self.view_label.set({
            "3d": "HOLOGRAM 3D / KAMERA",
            "2d": "CONNECTOME 2D / SYNAPSY",
            "avatar": "EMBODIED PRESENCE / LIF",
        }[mode])
        if mode == "2d" and self.graph._latest is not None:
            self.graph.render(self.graph._latest, force=True)
        if mode == "avatar":
            self.avatar.draw()

    def _toggle_hologram_motion(self) -> None:
        moving = self.hologram.toggle_motion()
        self._event("KAMERA 3D / " + ("OBRÓT WŁĄCZONY" if moving else "OBRÓT ZATRZYMANY"))

    def _event(self, text: str) -> None:
        self.events.configure(state="normal")
        self.events.insert("end", text + "\n")
        if int(self.events.index("end-1c").split(".")[0]) > 90:
            self.events.delete("1.0", "25.0")
        self.events.configure(state="disabled")
        self.events.see("end")

    def _body_resized(self, _event) -> None:
        self.scroll.configure(scrollregion=self.scroll.bbox("all"))

    def _viewport_resized(self, event) -> None:
        # Let the page shrink on 1024px Windows/DPI desktops. Only truly
        # narrow screens retain a minimum internal width for legibility.
        self.scroll.itemconfigure(self.window_id, width=max(860, event.width))

    def _scroll_wheel(self, event) -> None:
        self.scroll.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _resize_graph(self, _event) -> None:
        if self.graph._latest is not None:
            self.graph.render(self.graph._latest, force=True)

    def _resize_signals(self, _event) -> None:
        self._draw_signals()

    def _draw_signals(self) -> None:
        canvas = self.signal_canvas
        canvas.delete("all")
        w = max(80, canvas.winfo_width())
        h = max(80, canvas.winfo_height())
        left, top, right, bottom = 12, 14, w - 12, h - 19
        for index in range(4):
            y = top + (bottom - top) * index / 3
            canvas.create_line(left, y, right, y, fill=GRID)
        if not self._samples:
            canvas.create_text(w / 2, h / 2, text="BRAK PRÓBEK",
                               fill=MUTED, font=("Consolas", 9))
            return
        ceiling = max(1, *(value for _, value in self._samples))
        points = []
        for idx, (_, value) in enumerate(self._samples):
            x = left + (right - left) * idx / max(1, len(self._samples) - 1)
            y = bottom - (bottom - top) * value / ceiling
            points.extend((x, y))
        if len(points) >= 4:
            canvas.create_line(*points, fill=ACCENT, width=2, smooth=False)
        canvas.create_oval(points[-2] - 3, points[-1] - 3,
                           points[-2] + 3, points[-1] + 3,
                           fill="#eefff5", outline="")

    def refresh(self) -> bool:
        """One synchronous, read-only update. Returns True only for a NEW brain step."""
        status = self.memory.status()
        values = status["brain"]
        self.metrics["steps"].set(f"{values['steps']:,}".replace(",", " "))
        self.metrics["neurons"].set(f"{values['neurons']:,}".replace(",", " "))
        self.metrics["synapses"].set(f"{values['synapses']:,}".replace(",", " "))
        self.metrics["documents"].set(
            f"{status['knowledge']['documents']:,}".replace(",", " "))
        allowed = bool(self.network_enabled())
        self.modules["network"].set("ZEZWOLONO" if allowed else "WYŁĄCZONY")
        self.modules["memory"].set(
            f"{status['knowledge']['documents']} dok. / "
            f"{status['knowledge']['passages']} frag.")
        self.modules["lif"].set(f"KROK {values['steps']}")
        self.modules["foundation"].set("TRENING OSOBNO")
        brain = self.memory.brain()
        state = snapshot_neural_telemetry(brain)
        self.capacity_text.set(
            f"AKTYWNY LIMIT LIF: {brain.config.max_neurons} NEURONÓW / "
            f"{brain.config.max_synapses} SYNAPS / {brain.config.max_patterns} WZORCÓW  ·  "
            "starsze pamięci zachowują swoje limity")
        was = self._last
        advanced = was is not None and state.step > was.step
        if was is None or advanced:
            self.graph.render(state)
            self.hologram.update_state(state)
            self.avatar.update_state(state)
            self._samples.append((state.step, sum(int(n.fired) for n in state.nodes)))
            self._draw_signals()
            self.signal_label.set(
                f"KROK {state.step} / SPIKI {self._samples[-1][1]} / "
                f"PRÓBEK {len(self._samples)}")
        if advanced:
            self._event(
                f"LIF / KROK {state.step}  +{state.step - was.step} kroków; "
                f"+{max(0, state.total_spikes-was.total_spikes)} spike; "
                f"+{max(0, state.total_synapses-was.total_synapses)} synaps")
            self.status.configure(text="● LIF / NOWY KROK", fg=ACCENT)
            self.neural_step.configure(text=f"KROK {state.step}", fg=ACCENT)
        else:
            self.status.configure(text="○ BEZ NOWEGO KROKU", fg=MUTED)
            self.neural_step.configure(text=f"KROK {state.step} / BEZ ZMIANY",
                                       fg=MUTED)
        self._last = state
        return advanced
