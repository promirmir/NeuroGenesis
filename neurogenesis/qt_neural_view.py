"""NeuroGenesis Qt neural topology oscilloscope. Not a prerecorded animation.

Only validated LIF BrainFrame values are rendered. An event flare is allowed
for 850 ms after an observed *change of saved step*; zero computation or
animation is synthesized while the brain is idle.
"""
from __future__ import annotations

import math
import time

from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget, QSizePolicy

from .neural_graph import BrainFrame, positions


class NeuralFabric(QWidget):
    """Resize-aware QPainter scene driven by immutable actual neural snapshots."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame: BrainFrame | None = None
        self._changed_at = -1e9
        self.setMinimumHeight(430)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(55)
        self._pulse_timer.timeout.connect(self._pulse_tick)

    def set_frame(self, frame: BrainFrame) -> None:
        if not isinstance(frame, BrainFrame):
            raise TypeError("real BrainFrame required")
        first = self._frame is None
        change = not first and frame.step != self._frame.step
        self._frame = frame
        if change and frame.step > 0:
            self._changed_at = time.monotonic()
            self._pulse_timer.start()
        self.update()

    def _pulse_tick(self) -> None:
        if time.monotonic() - self._changed_at > .85 or not self.isVisible():
            self._pulse_timer.stop()
        self.update()

    def _text(self, painter: QPainter, x: float, y: float,
              content: str, *, size: int = 10, color: str = "#c8e3ef",
              bold: bool = False) -> None:
        painter.setPen(QColor(color))
        font = QFont("Consolas", size)
        font.setBold(bold)
        painter.setFont(font)
        painter.drawText(QPointF(x, y), content)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w, h = max(420, self.width()), max(340, self.height())
        background = QRadialGradient(QPointF(w*.57, h*.48), max(w, h)*.69)
        background.setColorAt(0.0, QColor("#15304a"))
        background.setColorAt(.58, QColor("#091b30"))
        background.setColorAt(1.0, QColor("#06101e"))
        painter.fillRect(self.rect(), background)
        painter.setPen(QPen(QColor("#152b3f"), 1))
        for x in range(0, w, 38):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, 38):
            painter.drawLine(0, y, w, y)
        painter.setPen(QPen(QColor("#1a4058"), 1))
        for r in (.20, .45, .70, .95):
            painter.drawEllipse(QRectF(
                w*(.57-.35*r), h*(.50-.43*r), w*.70*r, h*.86*r))
        frame = self._frame
        self._text(painter, 24, 29, "NEUROGENESIS  /  NEURAL FABRIC",
                   size=13, bold=True, color="#eaf8ff")
        if frame is None:
            self._text(painter, 24, h/2, "BRAK ZAPISANEGO STANU NEURONOWEGO",
                       color="#86a8bd")
            painter.end()
            return
        age = time.monotonic() - self._changed_at
        flare = frame.step > 0 and 0 <= age < .85
        self._text(painter, w-230, 29,
                   "● ZMIANA KROKU" if flare else "○ STAN SPOCZYNKOWY",
                   size=10, bold=True,
                   color="#ffc876" if flare else "#8bafc1")
        self._text(painter, 24, 58,
                   f"KROK {frame.step}   NEURONY {frame.neurons}   SYNAPSY {frame.synapses}",
                   size=10, color="#89c6df")
        points = positions(frame, w, h)
        nodes_by_id = {n.index: n for n in frame.nodes}
        phase = min(1., max(0., age / .85)) if flare else 1.
        for edge in frame.edges:
            if edge.pre not in points or edge.post not in points:
                continue
            x1, y1 = points[edge.pre]
            x2, y2 = points[edge.post]
            active = flare and nodes_by_id[edge.pre].spiked
            power = min(1., max(0., edge.weight / 1.5))
            base = QColor("#6de2ff" if active else "#46b2d2")
            base.setAlpha(230 if active else int(32 + 100 * power))
            painter.setPen(QPen(base, 2.0 if active else .85))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            if active:
                px = x1 + (x2-x1)*phase
                py = y1 + (y2-y1)*phase
                glow = QRadialGradient(QPointF(px, py), 11)
                glow.setColorAt(0, QColor(255, 228, 165, 240))
                glow.setColorAt(1, QColor(255, 184, 70, 0))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow)
                painter.drawEllipse(QPointF(px, py), 11, 11)
        painter.setPen(Qt.PenStyle.NoPen)
        for neuron in frame.nodes:
            x, y = points[neuron.index]
            active = flare and neuron.spiked
            trace = min(1., max(0., neuron.trace / 5))
            size = 4 + 3 * trace
            glow_radius = 15 if active else 10 if trace >= .3 else 0
            if glow_radius:
                glow = QRadialGradient(QPointF(x, y), glow_radius)
                col = QColor("#ffae63" if active else "#00ddce")
                col.setAlpha(120 if active else 65)
                glow.setColorAt(0.0, col)
                col2 = QColor(col)
                col2.setAlpha(0)
                glow.setColorAt(1.0, col2)
                painter.setBrush(glow)
                painter.drawEllipse(QPointF(x, y), glow_radius, glow_radius)
            color = ("#ffcc84" if active else "#3fc6ff" if neuron.is_input
                     else "#58e4d4" if trace > .05 else "#587b90")
            painter.setBrush(QColor(color))
            painter.drawEllipse(QPointF(x, y), size, size)
        painter.fillRect(QRectF(0, h-88, w, 88), QColor(4, 12, 25, 225))
        self._text(painter, 24, h-63,
                   f"IMPULSY / KROK {frame.last_spikes}     IMPULSY ŁĄCZNIE {frame.total_spikes}"
                   f"     WZROST +{frame.grown}     PRZYCINANIE -{frame.pruned}",
                   color="#b5ecf4", size=10)
        self._text(painter, 24, h-39,
                   f"NOWOŚĆ {frame.novelty:.3f}     ENERGIA PROXY {frame.energy_proxy:.2f}"
                   f"     WIDOCZNE {frame.coverage}",
                   color="#91bace", size=9)
        self._text(painter, 24, h-15,
                   "BŁYSK = NOWO ZAREJESTROWANY KROK · LOKALIZACJA I CZAS PRZEPŁYWU SĄ UMOWNE",
                   color="#708aa4", size=8)
        painter.end()
