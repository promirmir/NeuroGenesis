"""Symbolic embodied avatar for the real local LIF runtime, not an agent.

A continuously moving camera and HUD are presentation, not cognition.
Eye/forehead activity is emitted only after a NEW persisted LIF step; bright
eye response requires an actual recorded spike. No microphone, webcam,
person tracking, external API, simulation of consciousness or background IO.
"""
from __future__ import annotations

import math
import tkinter as tk

from .neural_telemetry import NeuralTelemetry

FRAME_MS = 90
EVENT_FRAMES = 12


def presence_signal(previous: NeuralTelemetry | None,
                    current: NeuralTelemetry) -> tuple[bool, int]:
    """Return real step advance and observed last-step spikes.

    This does not invent event streams or claim individual neuron data
    for any step skipped between two persisted snapshots.
    """
    if not isinstance(current, NeuralTelemetry):
        raise TypeError("verified neural telemetry required")
    if previous is None or current.step <= previous.step:
        return False, 0
    return True, sum(bool(n.fired) for n in current.nodes)


class NeuralAvatar:
    """Futuristic 2.5D humanoid symbol with real event-gated responses."""

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.latest: NeuralTelemetry | None = None
        self.orbit = .0
        self.motion = True
        self._timer: str | None = None
        self._step_frames = 0
        self._spike_frames = 0
        self._last_recorded_spikes = 0
        canvas.bind("<Map>", self._on_map, add="+")
        canvas.bind("<Unmap>", self._on_unmap, add="+")
        canvas.bind("<Configure>", self._resize, add="+")

    def update_state(self, current: NeuralTelemetry) -> bool:
        if not isinstance(current, NeuralTelemetry):
            raise TypeError("verified neural telemetry required")
        if self.latest is not None and current.step < self.latest.step:
            self._step_frames = self._spike_frames = 0
        advanced, spikes = presence_signal(self.latest, current)
        self.latest = current
        if advanced:
            self._step_frames = EVENT_FRAMES
            self._spike_frames = EVENT_FRAMES if spikes else 0
            self._last_recorded_spikes = spikes
        self.draw()
        return advanced

    def toggle_motion(self) -> bool:
        self.motion = not self.motion
        self.draw()
        return self.motion

    def _on_map(self, _event=None) -> None:
        if self._timer is None:
            self._timer = self.canvas.after(FRAME_MS, self._tick)

    def _on_unmap(self, _event=None) -> None:
        if self._timer is not None:
            self.canvas.after_cancel(self._timer)
            self._timer = None

    def _resize(self, _event=None) -> None:
        self.draw()

    def _tick(self) -> None:
        self._timer = None
        if not self.canvas.winfo_ismapped():
            return
        if self.motion:
            self.orbit = (self.orbit + .018) % (math.pi * 2)
        if self._step_frames:
            self._step_frames -= 1
        if self._spike_frames:
            self._spike_frames -= 1
        if self.motion or self._step_frames or self._spike_frames:
            self.draw()
        self._timer = self.canvas.after(FRAME_MS, self._tick)

    def draw(self) -> None:
        c = self.canvas
        c.delete("all")
        width = max(320, c.winfo_width())
        height = max(280, c.winfo_height())
        cx, cy = width * .5, height * .49
        unit = min(width / 390, height / 350)
        dx = 4.0 * math.sin(self.orbit) if self.motion else 0.0

        def xy(x: float, y: float):
            return (cx + (x + dx) * unit, cy + y * unit)

        def line(coords, color: str, thick=1.0, smooth=False):
            pts = []
            for x, y in coords:
                pts.extend(xy(x, y))
            c.create_line(*pts, fill=color, width=thick * unit, smooth=smooth)

        def poly(coords, fill: str, outline: str = ""):
            pts = []
            for x, y in coords:
                pts.extend(xy(x, y))
            c.create_polygon(*pts, fill=fill, outline=outline, width=1)

        def ring(x: float, y: float, rx: float, ry: float, color: str, thick=1):
            a = xy(x-rx, y-ry)
            b = xy(x+rx, y+ry)
            c.create_oval(*a, *b, outline=color, width=thick)

        # Camera/HUD: all of this is a symbolic overlay.
        for k in (1.0, .81, .62):
            ring(0, -5, 145*k, 143*k, "#123247")
        line([(-176, 7), (-136, 7)], "#225a75")
        line([(136, 7), (176, 7)], "#225a75")
        line([(0, -152), (0, -139)], "#2a6d82")

        # Armored shoulders and illuminated sternum.
        poly([(-146, 123), (-127, 88), (-62, 71), (-38, 100), (38, 100),
              (62, 71), (127, 88), (146, 123)], "#10283c", "#285c72")
        poly([(-141, 118), (-123, 91), (-73, 79), (-92, 121)],
             "#173449", "#276178")
        poly([(141, 118), (123, 91), (73, 79), (92, 121)],
             "#173449", "#276178")
        poly([(-35, 83), (-22, 110), (22, 110), (35, 83)],
             "#154052", "#36889b")
        line([(-92, 121), (-68, 106), (-39, 115)], "#378e9d", 1.6)
        line([(92, 121), (68, 106), (39, 115)], "#378e9d", 1.6)
        ring(0, 105, 15, 9, "#4ca5b9")
        ring(0, 105, 5, 5, "#8feeea" if self._step_frames else "#367588", 1.3)

        # Neck, outer skull, cranial shield and ear-mounted signal units.
        poly([(-30, 71), (-30, 47), (30, 47), (30, 71), (17, 90), (-17, 90)],
             "#0e2c3e", "#39758b")
        poly([(-52, -99), (-32, -126), (0, -138), (32, -126), (52, -99),
              (63, -30), (47, 35), (21, 68), (0, 77),
              (-21, 68), (-47, 35), (-63, -30)], "#11283c", "#4d96ae")
        poly([(-49, -104), (-19, -131), (0, -134), (19, -131), (49, -104),
              (37, -70), (-37, -70)], "#214052", "#35879f")
        poly([(-52, -85), (-40, -58), (-46, 8), (-26, 51), (-15, 62),
              (-49, 34), (-61, -22)], "#0c1c2d", "#326076")
        poly([(52, -85), (40, -58), (46, 8), (26, 51), (15, 62),
              (49, 34), (61, -22)], "#0c1c2d", "#326076")
        for side in (-1, 1):
            poly([(side*62, -46), (side*72, -35), (side*72, 12),
                  (side*62, 24), (side*55, 13), (side*55, -34)],
                 "#1b4358", "#3e96a9")
            line([(side*58, -28), (side*68, -24),
                  (side*68, 2)], "#64b6c7", 1.2)
        # Center face architecture: visible structured physical features.
        poly([(-38, -59), (38, -59), (44, -20), (28, 20),
              (9, 50), (0, 54), (-9, 50), (-28, 20), (-44, -20)],
             "#162e40", "#356d83")
        poly([(-11, -12), (11, -12), (7, 25), (0, 32), (-7, 25)],
             "#1b4556", "#56a2b5")
        line([(-26, 36), (-11, 40), (11, 40), (26, 36)],
             "#367f93", 1.4)

        # The eye change is event-gated by real spiking LIF telemetry.
        hot = self._spike_frames > 0
        eye = "#a9ffff" if hot else "#2a8ca8"
        eye_glow = "#2c6d83" if hot else "#14394c"
        for side in (-1, 1):
            poly([(side*8, -44), (side*37, -44),
                  (side*32, -27), (side*13, -24)],
                 eye_glow, "#24758d")
            line([(side*12, -35), (side*32, -35)], eye, 3.0 if hot else 1.4)
            line([(side*20, -54), (side*39, -50)], "#4f9aac", 1.1)
        line([(-10, -112), (0, -122), (10, -112)], "#68b3be")
        line([(0, -113), (0, -78)], "#2c7993", 1.4)

        if self._step_frames:
            ring(0, -18, 96 + (EVENT_FRAMES-self._step_frames)*2,
                 112 + (EVENT_FRAMES-self._step_frames)*1.5,
                 "#226f84", 2)
        # Literal indicators disclose the source and its absence.
        if self.latest is None:
            status = "BRAK DANYCH LIF"
            details = "ODCZYT Z LOKALNEJ PAMIĘCI"
        elif self._spike_frames:
            status = "ZAPISANY IMPULS LIF"
            details = (f"KROK {self.latest.step}  /  "
                       f"SPIKI {self._last_recorded_spikes}")
        elif self._step_frames:
            status = "NOWY KROK LIF / 0 SPIKÓW"
            details = f"KROK {self.latest.step}"
        else:
            status = "BRAK NOWEGO KROKU"
            details = f"OSTATNI KROK {self.latest.step}"
        c.create_text(16, 19, anchor="w", text="EMBODIED PRESENCE  /  NEUROGENESIS",
                      fill="#a0dfe9", font=("Consolas", 10, "bold"))
        c.create_text(16, 40, anchor="w",
                      text="AWATAR SYMBOLICZNY  •  NIE SAMODZIELNA ŚWIADOMOŚĆ",
                      fill="#729eaf", font=("Consolas", 8))
        c.create_text(16, height-39, anchor="w", text=status,
                      fill="#91f4ea" if self._step_frames else "#6da4b6",
                      font=("Consolas", 10, "bold"))
        c.create_text(16, height-18, anchor="w", text=details,
                      fill="#80a9b9", font=("Consolas", 9))
