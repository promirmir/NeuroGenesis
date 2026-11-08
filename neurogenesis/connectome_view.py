"""Futuristic but factual Qt connectome rendering of NeuroGenesis LIF state.

All colors, brightness and edges are derived from persisted neural activity
and weights. A stopped brain remains visually still: no invented firing or
pseudo-intelligence animation. Drawing is bounded and occurs on the UI thread.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from .neural_telemetry import (
    NeuralTelemetry, diff_neural_telemetry,
)


class ConnectomeView(QWidget):
    """Live structural network: nodes=neurons; edges=actual synapses."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(390)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self._snapshot: NeuralTelemetry | None = None
        self._delta: dict[str, int | bool] = {}
        self._zoom = 1.0
        self._selected: int | None = None
        self._coordinates: dict[int, QPointF] = {}
        self.setToolTip("Najedź na neuron, aby odczytać jego rzeczywiste wartości")

    @property
    def snapshot(self) -> NeuralTelemetry | None:
        return self._snapshot

    @property
    def change(self) -> dict[str, int | bool]:
        return dict(self._delta)

    def set_telemetry(self, data: NeuralTelemetry) -> None:
        if not isinstance(data, NeuralTelemetry):
            raise TypeError("real NeuralTelemetry snapshot required")
        if self._snapshot is not None and data.step == self._snapshot.step:
            # No new brain step => do NOT flash or pretend the network works.
            self._delta = diff_neural_telemetry(None, data)
            return
        self._delta = diff_neural_telemetry(self._snapshot, data)
        self._snapshot = data
        self.update()

    def wheelEvent(self, event) -> None:
        self._zoom = max(0.70, min(2.3, self._zoom * (
            1.12 if event.angleDelta().y() > 0 else 1 / 1.12)))
        self.update()
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        nearby = [(i, math.hypot(event.position().x()-p.x(),
                                 event.position().y()-p.y()))
                  for i, p in self._coordinates.items()]
        found = min(nearby, key=lambda pair: pair[1]) if nearby else None
        selected = found[0] if found is not None and found[1] <= 13 else None
        if selected != self._selected:
            self._selected = selected
            self.update()
        if selected is not None and self._snapshot is not None:
            node = self._snapshot.nodes[selected]
            self.setToolTip(
                f"Neuron {selected} | wejście={node.input_channel} | "
                f"ślad={node.trace:.4f} | potencjał={node.voltage:.4f} | "
                f"spike={node.fired} | refractory={node.refractory}")
        else:
            self.setToolTip("Rzeczywiste neurony i synapsy z prywatnej bazy SQLite")

    def _positions(self, state: NeuralTelemetry) -> dict[int, QPointF]:
        center_x = self.width() * 0.50
        center_y = self.height() * 0.51
        base = min(self.width() * 0.44, self.height() * 0.43) * self._zoom
        total = len(state.nodes)
        inputs = min(state.input_channels, total)
        positions = {}
        for i in range(total):
            if i < inputs:
                angle = -math.pi / 2 + 2 * math.pi * i / max(1, inputs)
                radius = base * 0.93
            else:
                j = i - inputs
                n = max(1, total - inputs)
                angle = j * 2.399963229728653
                radius = base * (0.19 + 0.65 * math.sqrt((j + 0.5) / n))
            positions[i] = QPointF(
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle))
        return positions

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#060c17"))
        w, h = self.width(), self.height()
        cx, cy = w * .5, h * .51
        radius = min(w * .44, h * .43) * self._zoom
        painter.setPen(QPen(QColor(29, 72, 102, 100), 1))
        for portion in (.25, .50, .75, 1.0):
            r = radius * portion
            painter.drawEllipse(QPointF(cx, cy), r, r)
        painter.setPen(QPen(QColor(34, 98, 122, 75), 1, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(cx - radius, cy), QPointF(cx + radius, cy))
        painter.drawLine(QPointF(cx, cy - radius), QPointF(cx, cy + radius))
        state = self._snapshot
        if not state:
            painter.setPen(QColor("#a2c3d3"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Brak stanu neuronu · brak syntetycznych animacji")
            painter.end()
            return
        positions = self._positions(state)
        self._coordinates = positions
        max_weight = max((edge.weight for edge in state.edges), default=1.0) or 1.0
        selected = self._selected
        for edge in state.edges:
            a, b = positions.get(edge.source), positions.get(edge.target)
            if a is None or b is None:
                continue
            src = state.nodes[edge.source]
            active = src.fired
            selected_edge = selected in (edge.source, edge.target)
            strength = max(0, min(1, edge.weight / max_weight))
            color = QColor("#48e8ef") if active else QColor("#4e719b")
            color.setAlpha(245 if active else (205 if selected_edge else 38 + int(105 * strength)))
            painter.setPen(QPen(color, 2.2 if active else (1.6 if selected_edge else .55 + 1.25 * strength)))
            painter.drawLine(a, b)
        for node in state.nodes:
            point = positions[node.index]
            selected_node = node.index == selected
            intensity = max(0, min(1, node.trace / 5.0))
            if node.fired:
                fill, halo = QColor("#f3fdff"), QColor(40, 235, 255, 95)
                diameter = 6.0
            elif node.input_channel:
                fill, halo = QColor("#55a8ff"), QColor(50, 132, 255, 45)
                diameter = 4.2
            else:
                fill = QColor.fromRgb(42 + int(intensity * 76),
                                      175 + int(intensity * 65),
                                      179 + int(intensity * 64))
                halo = QColor(38, 224, 210, 18 + int(intensity * 63))
                diameter = 3.0 + 2.5 * intensity
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(halo)
            painter.drawEllipse(point, diameter + (8 if selected_node else 4),
                                diameter + (8 if selected_node else 4))
            painter.setBrush(fill)
            painter.drawEllipse(point, diameter, diameter)
            if selected_node:
                painter.setPen(QPen(QColor("#f7d782"), 1.5))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(point, 13, 13)
        painter.setFont(QFont("Consolas", 9))
        painter.setPen(QColor("#87b8cd"))
        painter.drawText(20, 27, "CONNECTOME / LIF    •    STRUKTURA + SYGNAŁY RZECZYWISTE")
        painter.setPen(QColor("#a6c5d4"))
        painter.drawText(20, h - 24, (
            f"KROK {state.step}  /  {state.total_neurons} NEURONÓW  /  "
            f"{state.total_synapses} SYNAPS  /  "
            + ("POMIAR ZMIENIONY" if self._delta.get("advanced") else "BEZ NOWEGO KROKU")))
        if state.truncated:
            painter.setPen(QColor("#ffca7c"))
            painter.drawText(20, 48, "LIMIT WYŚWIETLANIA — część połączeń pominięta")
        painter.end()


class TrainingLossPlot(QWidget):
    """Plots ONLY actual reported PyTorch batch losses from training events."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(155)
        self._points: list[tuple[int, float]] = []

    @property
    def points(self) -> tuple[tuple[int, float], ...]:
        return tuple(self._points)

    def add_real_loss(self, step: int, loss: float) -> None:
        if (type(step) is not int or step < 1 or
                type(loss) not in (float, int) or not math.isfinite(loss)
                or loss < 0):
            raise ValueError("only finite real training losses with positive step")
        if self._points and step <= self._points[-1][0]:
            # New training runs intentionally reset the chart, not fabricate
            # continuous steps across unrelated checkpoint sessions.
            self._points.clear()
        self._points.append((step, float(loss)))
        if len(self._points) > 600:
            del self._points[:-600]
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#091322"))
        painter.setPen(QColor("#9ac6d9"))
        painter.setFont(QFont("Consolas", 9))
        painter.drawText(17, 24, "FOUNDATION / REAL TORCH LOSS")
        if not self._points:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Brak rzeczywistych pomiarów w bieżącej sesji")
            painter.end()
            return
        left, right = 43, max(44, self.width() - 19)
        top, bottom = 45, max(46, self.height() - 26)
        vals = [x[1] for x in self._points]
        low, high = min(vals), max(vals)
        span = max(0.001, high - low)
        painter.setPen(QPen(QColor("#213b52"), 1))
        for i in range(4):
            y = top + (bottom - top) * i / 3
            painter.drawLine(QPointF(left, y), QPointF(right, y))
        painter.setPen(QPen(QColor("#4fe6c8"), 2.2))
        previous = None
        for i, (_, loss) in enumerate(self._points):
            x = left + (right - left) * i / max(1, len(self._points) - 1)
            y = bottom - (bottom - top) * (loss - low) / span
            point = QPointF(x, y)
            if previous is not None:
                painter.drawLine(previous, point)
            previous = point
        painter.setPen(QColor("#cfedf4"))
        painter.drawText(17, self.height() - 7,
                         f"{self._points[-1][0]} steps / last {vals[-1]:.5f} nats "
                         f"/ range {low:.3f}–{high:.3f}")
        painter.end()
