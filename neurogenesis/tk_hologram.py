"""Cinematic camera on ACTUAL, persisted LIF telemetry in the shipped Tk EXE.

Orbital motion and a faint anatomical silhouette are visual presentation ONLY.
Synapses, neuron count, last saved spike mask and short signal highlights come
solely from NeuralTelemetry. This is NOT a 3-D neural reconstruction or a map
of the separate PyTorch Foundation Brain model.
"""
from __future__ import annotations

import math
import tkinter as tk

from .neural_telemetry import NeuralTelemetry

MAX_HOLOGRAM_NODES = 144
MAX_HOLOGRAM_EDGES = 360
FRAME_MS = 90
EVENT_FRAMES = 10
GOLDEN = math.pi * (3 - math.sqrt(5))


def project_real_nodes(data: NeuralTelemetry, angle: float, width: int,
                       height: int) -> dict[int, tuple[float, float, float]]:
    """Deterministic, symbolic 3D placement for real node identifiers.

    Positions are illustrative, NOT anatomical coordinates. This function
    neither generates new neural nodes nor changes their observed activity.
    """
    if not isinstance(data, NeuralTelemetry):
        raise TypeError("actual LIF telemetry required")
    nodes = data.nodes[:MAX_HOLOGRAM_NODES]
    count = max(1, (len(nodes) + 1) // 2)
    radius = min(width * .45, height * .46)
    center_x, center_y = width * .50, height * .52
    ca, sa = math.cos(angle), math.sin(angle)
    projected: dict[int, tuple[float, float, float]] = {}
    for node in nodes:
        side = -1 if node.index % 2 == 0 else 1
        order = node.index // 2
        polar = 1 - 2 * (order + .5) / count
        ring = math.sqrt(max(0, 1 - polar * polar))
        spiral = GOLDEN * order
        # Two rounded hemisphere-like lobes, with a visible center fissure.
        x = side * (.17 + .55 * ring * abs(math.cos(spiral)))
        y = .77 * polar + .12 * ring * math.sin(spiral)
        z = .56 * ring * math.sin(spiral) + .16 * math.cos(order * .7)
        xr, zr = x * ca + z * sa, z * ca - x * sa
        perspective = 2.8 / (2.8 - zr)
        projected[node.index] = (
            center_x + radius * xr * perspective,
            center_y + radius * y * perspective,
            zr,
        )
    return projected


class HolographicBrain:
    """Canvas renderer with a 3D orbit; event animation requires a NEW step."""

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.latest: NeuralTelemetry | None = None
        self.angle = .22
        self.motion = True
        self._timer: str | None = None
        self._event_frames = 0
        self._step_frames = 0
        self._event_step: int | None = None
        canvas.bind("<Map>", self._on_map, add="+")
        canvas.bind("<Unmap>", self._on_unmap, add="+")
        canvas.bind("<Configure>", self._on_resize, add="+")

    def update_state(self, data: NeuralTelemetry) -> bool:
        if not isinstance(data, NeuralTelemetry):
            raise TypeError("actual LIF telemetry required")
        if self.latest is not None and data.step < self.latest.step:
            # A memory restore can rewind the view, but must not fabricate
            # a fresh activity event.
            self._event_frames = 0
            self._step_frames = 0
        if self.latest is not None and data.step > self.latest.step:
            self._step_frames = EVENT_FRAMES
            self._event_frames = EVENT_FRAMES if any(n.fired for n in data.nodes) else 0
            self._event_step = data.step  # recorded step even if no neuron fired
        updated = self.latest is None or data.step != self.latest.step
        self.latest = data
        if updated:
            self.draw()
        return updated

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

    def _on_resize(self, _event=None) -> None:
        if self.latest is not None:
            self.draw()

    def _tick(self) -> None:
        self._timer = None
        if not self.canvas.winfo_ismapped():
            return
        if self.motion:
            self.angle = (self.angle + .016) % (math.pi * 2)
        if self._event_frames:
            self._event_frames -= 1
        if self._step_frames:
            self._step_frames -= 1
        if self.motion or self._event_frames or self._step_frames:
            self.draw()
        self._timer = self.canvas.after(FRAME_MS, self._tick)

    def draw(self) -> None:
        c = self.canvas
        c.delete("all")
        w, h = max(320, c.winfo_width()), max(270, c.winfo_height())
        cx, cy = w * .50, h * .52
        scale = min(w * .45, h * .46)
        # HUD backdrop: scanning rings are presentation, not neuron activity.
        for fraction in (.36, .67, .98):
            r = scale * fraction
            c.create_oval(cx - r, cy - r * .86, cx + r, cy + r * .86,
                          outline="#123449", width=1)
        c.create_line(cx - scale * 1.12, cy, cx + scale * 1.12, cy,
                      fill="#102c40")
        c.create_line(cx, cy - scale * .94, cx, cy + scale * .94,
                      fill="#102c40")
        if self._step_frames:
            # A saved step occurred; this ring is a bounded event indicator,
            # not a claim that any neuron spiked.
            progress = (EVENT_FRAMES - self._step_frames) / EVENT_FRAMES
            r = scale * (.74 + .25 * progress)
            c.create_oval(cx-r, cy-r*.86, cx+r, cy+r*.86,
                          outline="#2c7e91", width=2)
        # Two independently rounded cortical lobes form a cinematic
        # WIREFRAME shell. These lines are decorative coordinates; only
        # actual LIF nodes/edges below represent measured neural state.
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        def camera(x: float, y: float, z: float):
            xr, zr = x * ca + z * sa, z * ca - x * sa
            size = 2.8 / (2.8 - zr)
            return (cx + scale * xr * size,
                    cy + scale * y * size, zr)
        def cortex(lobe: int, latitude: float, longitude: float):
            r = math.sqrt(max(0.0, 1 - latitude * latitude))
            ripple = .023 * math.sin(11 * longitude + 8 * latitude)
            x = lobe * .29 + (.35 * r + ripple) * math.cos(longitude)
            y = .76 * latitude + .022 * math.sin(9 * longitude + 5 * latitude)
            z = (.57 * r + ripple) * math.sin(longitude)
            return camera(x, y, z)
        for lobe in (-1, 1):
            # Subtle gyri: latitude arcs + longitude ribs follow a turning
            # 3D shell. This never draws an imaginary synapse.
            for band in range(-4, 5):
                lat = band / 5
                path = []
                depths = []
                for k in range(37):
                    px, py, depth = cortex(lobe, lat, 2 * math.pi * k / 36)
                    path.extend((px, py))
                    depths.append(depth)
                c.create_line(*path, smooth=True,
                              fill="#22526a" if max(depths) > .15 else "#16394f",
                              width=1)
            for meridian in range(12):
                lon = 2 * math.pi * meridian / 12
                path = []
                for k in range(25):
                    px, py, _depth = cortex(lobe, -.97 + 1.94 * k / 24, lon)
                    path.extend((px, py))
                c.create_line(*path, smooth=True, fill="#174258", width=1)
        # Major silhouette arc uses a different hue from live synapses.
        for lobe in (-1, 1):
            outline = []
            for k in range(41):
                lat = -.98 + 1.96 * k / 40
                px, py, _ = cortex(lobe, lat, math.pi * .04)
                outline.extend((px, py))
            c.create_line(*outline, smooth=True, fill="#2b7792", width=1.5)

        data = self.latest
        if data is None:
            c.create_text(cx, cy, text="OCZEKIWANIE NA LOKALNĄ TELEMETRIĘ LIF",
                          fill="#80adb8", font=("Consolas", 10))
            return
        coords = project_real_nodes(data, self.angle, w, h)
        visible_edges = [e for e in data.edges
                         if e.source in coords and e.target in coords][:MAX_HOLOGRAM_EDGES]
        nodes = {n.index: n for n in data.nodes[:MAX_HOLOGRAM_NODES]}
        peak = max((e.weight for e in visible_edges), default=1.0) or 1.0
        for edge in sorted(visible_edges, key=lambda e: (
                coords[e.source][2] + coords[e.target][2])):
            a, b = coords[edge.source], coords[edge.target]
            strength = edge.weight / peak
            active = self._event_frames > 0 and nodes[edge.source].fired
            color = ("#65eaff" if active else "#2d6c86" if strength >= .5
                     else "#1c4b64")
            c.create_line(a[0], a[1], b[0], b[1], fill=color,
                          width=2 if active else 1)
            if active:
                # Progress indicates an illustrative transition along an
                # ACTUAL edge after a newly SAVED spike, not measured latency.
                progress = (EVENT_FRAMES - self._event_frames) / EVENT_FRAMES
                px = a[0] + (b[0] - a[0]) * progress
                py = a[1] + (b[1] - a[1]) * progress
                c.create_oval(px - 3, py - 3, px + 3, py + 3,
                              fill="#d8ffff", outline="")
        for index in sorted(coords, key=lambda k: coords[k][2]):
            x, y, depth = coords[index]
            node = nodes[index]
            fired_now = self._event_frames > 0 and node.fired
            r = (3.7 if fired_now else 2.9 if node.input_channel else 2.3)
            base = "#b9fffb" if fired_now else "#60c9ff" if node.input_channel else (
                "#52ddca" if node.trace > 1 else "#368b99")
            if fired_now:
                c.create_oval(x - r - 4, y - r - 4, x + r + 4, y + r + 4,
                              fill="#146a81", outline="")
            c.create_oval(x-r, y-r, x+r, y+r, fill=base, outline="")
        count_fired = sum(int(n.fired) for n in data.nodes)
        c.create_text(16, 19, anchor="w", text="NEUROGENESIS  /  HOLOGRAPHIC CORE",
                      fill="#9be9ea", font=("Consolas", 11, "bold"))
        c.create_text(16, 40, anchor="w",
                      text="OBRÓT = KAMERA  •  IMPULSY = ZAPISANE KROKI LIF",
                      fill="#6a9dae", font=("Consolas", 8))
        c.create_text(16, h - 39, anchor="w",
                      text=(f"KROK {data.step}   NEURONY {data.total_neurons}   "
                            f"SYNAPSY {data.total_synapses}   OSTATNIE SPIKI {count_fired}"),
                      fill="#c2f0ee", font=("Consolas", 9, "bold"))
        subtitle = ("WIDOK OGRANICZONY" if data.truncated or
                    len(data.nodes) > MAX_HOLOGRAM_NODES or
                    len(data.edges) > MAX_HOLOGRAM_EDGES else "POZYCJE SYMBOLICZNE")
        c.create_text(16, h - 18, anchor="w",
                      text=subtitle + "  /  DANE ZE ZWERYFIKOWANEGO STANU SQLITE",
                      fill="#719ab0", font=("Consolas", 8))
