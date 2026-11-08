"""Data-driven connectome canvas for the dependency-free published Tk EXE.

The program's existing LIF network is rendered exactly from real saved neuron
states/weights. No idle twinkling, made-up signals or biological-brain claims.
"""
from __future__ import annotations

import math

from .neural_telemetry import NeuralTelemetry


class TkConnectome:
    def __init__(self, canvas):
        self.canvas = canvas
        self._step: int | None = None
        self._zoom = 1.0
        self._latest: NeuralTelemetry | None = None
        self.canvas.bind("<MouseWheel>", self.zoom)

    def zoom(self, event) -> None:
        self._zoom = min(2.2, max(0.70, self._zoom * (
            1.12 if event.delta > 0 else 1 / 1.12)))
        if self._latest is not None:
            self.render(self._latest, force=True)

    def render(self, data: NeuralTelemetry, *, force: bool = False) -> bool:
        if not isinstance(data, NeuralTelemetry):
            raise TypeError("real NeuralTelemetry required")
        if not force and data.step == self._step:
            return False
        self._step = data.step
        self._latest = data
        c = self.canvas
        c.delete("all")
        width = max(320, c.winfo_width())
        height = max(260, c.winfo_height())
        mid_x, mid_y = width * .5, height * .52
        radius = min(width * .43, height * .42) * self._zoom
        for fraction in (.25, .50, .75, 1.0):
            r = fraction * radius
            c.create_oval(mid_x-r, mid_y-r, mid_x+r, mid_y+r,
                         outline="#1b3953", width=1)
        coords: dict[int, tuple[float, float]] = {}
        n = len(data.nodes)
        inputs = min(data.input_channels, n)
        for node in data.nodes:
            i = node.index
            if i < inputs:
                angle = 2 * math.pi * i / max(1, inputs) - math.pi / 2
                distance = radius * .93
            else:
                j = i - inputs
                angle = 2.399963229728653 * j
                distance = radius * (.19 + .65 * math.sqrt((j+.5)/max(1,n-inputs)))
            coords[i] = (mid_x + distance*math.cos(angle),
                         mid_y + distance*math.sin(angle))
        max_weight = max((e.weight for e in data.edges), default=1.0) or 1.0
        for edge in data.edges:
            a, b = coords.get(edge.source), coords.get(edge.target)
            if a is None or b is None:
                continue
            strength = min(1, edge.weight / max_weight)
            active = data.nodes[edge.source].fired
            color = "#59faff" if active else (
                "#365574" if strength < .35 else
                "#487d9f" if strength < .75 else "#65afc9")
            c.create_line(*a, *b, fill=color,
                          width=2.8 if active else 1.0 + strength * .8)
        for node in data.nodes:
            x, y = coords[node.index]
            amp = min(1, node.trace / 5)
            glow = "#2d5a75" if not node.fired else "#26abc2"
            shade = ("#e8fcff" if node.fired else
                     "#54a5fa" if node.input_channel else
                     "#4de1d3" if amp >= .20 else "#238b91")
            diameter = 4.4 if node.fired else (3 if node.input_channel else 2.4)
            c.create_oval(x-diameter-2, y-diameter-2,
                          x+diameter+2, y+diameter+2,
                          fill=glow, outline="")
            c.create_oval(x-diameter, y-diameter,
                          x+diameter, y+diameter, fill=shade, outline="")
        c.create_text(18, 20, text="CONNECTOME / LIVE / PRAWDZIWE SYGNAŁY",
                      fill="#79cfe6", font=("Consolas", 11, "bold"), anchor="w")
        c.create_text(18, height-21,
                      text=(f"KROK {data.step}  ·  NEURONY {data.total_neurons}"
                            f"  ·  SYNAPSY {data.total_synapses}  ·  IMPULSY {data.total_spikes}"),
                      fill="#c2dce8", font=("Consolas", 10), anchor="w")
        if data.truncated:
            c.create_text(18, 45, text="LIMIT WYŚWIETLANIA (nie wszystkie węzły)",
                          fill="#ffd29a", font=("Consolas", 9), anchor="w")
        return True
