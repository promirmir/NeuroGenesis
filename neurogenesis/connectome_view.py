"""Futuristic but factual Qt connectome rendering of NeuroGenesis LIF state.

All colors, brightness and edges are derived from persisted neural activity
and weights. A stopped brain remains visually still: no invented firing or
pseudo-intelligence animation. Drawing is bounded and occurs on the UI thread.
"""
from __future__ import annotations

import math
import time

from PySide6.QtCore import QPointF, Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient
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
        self._pulse_started = -1e9
        self._pulse = QTimer(self)
        self._pulse.setInterval(48)
        self._pulse.timeout.connect(self._event_pulse_tick)
        self._pan = QPointF(0, 0)
        self._drag_from: QPointF | None = None

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
        is_real_new_step = self._snapshot is not None and data.step > self._snapshot.step
        self._delta = diff_neural_telemetry(self._snapshot, data)
        self._snapshot = data
        if is_real_new_step:
            self._pulse_started = time.monotonic()
            self._pulse.start()
        self.update()

    def _event_pulse_tick(self) -> None:
        # Sub-second render after an ACTUAL observed step: animation is a
        # visual transition, not an inferred axonal propagation measurement.
        if not self.isVisible() or time.monotonic() - self._pulse_started >= .8:
            self._pulse.stop()
            return
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_from = event.position()
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_from = None
            event.accept()

    def wheelEvent(self, event) -> None:
        self._zoom = max(0.70, min(2.3, self._zoom * (
            1.12 if event.angleDelta().y() > 0 else 1 / 1.12)))
        self.update()
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_from is not None and event.buttons() & Qt.MouseButton.LeftButton:
            movement = event.position() - self._drag_from
            self._pan += movement
            self._drag_from = event.position()
            self.update()
            event.accept()
            return
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
        center_x = self.width() * 0.50 + self._pan.x()
        center_y = self.height() * 0.51 + self._pan.y()
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
        w, h = self.width(), self.height()
        cx, cy = w*.50 + self._pan.x(), h*.51 + self._pan.y()
        radius = min(w*.44, h*.43) * self._zoom

        # Background, contours and navigation grid are decoration ONLY.
        # Every lit foreground node/edge below is backed by persisted LIF data.
        night = QRadialGradient(QPointF(cx, cy), max(w, h)*.65)
        night.setColorAt(0, QColor("#17384c"))
        night.setColorAt(.55, QColor("#0a1c2d"))
        night.setColorAt(1, QColor("#040b15"))
        painter.fillRect(self.rect(), night)
        painter.setPen(QPen(QColor(26, 69, 86, 46), 1))
        for x in range(0, w+1, 38):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h+1, 38):
            painter.drawLine(0, y, w, y)
        painter.setPen(QPen(QColor(40, 141, 164, 48), 1))
        for portion in (.24, .47, .72, 1.0):
            r = radius*portion
            painter.drawEllipse(QPointF(cx, cy), r, r)
        painter.setPen(QPen(QColor(67, 149, 165, 60), 1, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(cx-radius, cy), QPointF(cx+radius, cy))
        painter.drawLine(QPointF(cx, cy-radius), QPointF(cx, cy+radius))
        painter.setFont(QFont("Consolas", 9))
        painter.setPen(QColor("#a4eff1"))
        painter.drawText(20, 29, "NEUROGENESIS  /  REAL NEURAL FABRIC")

        state = self._snapshot
        if state is None:
            painter.setPen(QColor("#98b5c3"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Oczekiwanie na zapisany stan neuronowy")
            painter.end()
            return
        positions = self._positions(state)
        self._coordinates = positions
        elapsed = time.monotonic() - self._pulse_started
        transient = bool(self._delta.get("advanced")) and 0 <= elapsed < .8
        phase = max(0.0, min(1.0, elapsed/.8)) if transient else 1.0
        max_weight = max((edge.weight for edge in state.edges), default=1.0) or 1.0
        selected = self._selected
        for edge in state.edges:
            a, b = positions.get(edge.source), positions.get(edge.target)
            if a is None or b is None:
                continue
            active = transient and state.nodes[edge.source].fired
            related = selected in (edge.source, edge.target)
            strength = max(0.0, min(1.0, edge.weight/max_weight))
            ink = QColor("#62f7ef" if active else "#53a1be")
            ink.setAlpha(230 if active else (205 if related else 26 + int(110*strength)))
            painter.setPen(QPen(ink, 2.4 if active else (1.65 if related else .65 + 1.15*strength)))
            painter.drawLine(a, b)
            if active:
                # Traversing light = a stylized visualization of the observed
                # presynaptic spike; NOT a measured conduction speed or delay.
                spot = QPointF(a.x()+(b.x()-a.x())*phase,
                               a.y()+(b.y()-a.y())*phase)
                glow = QRadialGradient(spot, 11)
                glow.setColorAt(0, QColor(235, 255, 243, 235))
                glow.setColorAt(.55, QColor(86, 250, 227, 115))
                glow.setColorAt(1, QColor(86, 250, 227, 0))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow)
                painter.drawEllipse(spot, 11, 11)
        painter.setPen(Qt.PenStyle.NoPen)
        for node in state.nodes:
            point = positions[node.index]
            intensity = max(0.0, min(1.0, node.trace/5.0))
            selected_node = node.index == selected
            is_pulsing = transient and node.fired
            if is_pulsing:
                fill = QColor("#fff4c8")
                aura = QColor(255, 194, 105, 160)
                size = 5.8
            elif node.input_channel:
                fill = QColor("#62b6ff")
                aura = QColor(64, 153, 252, 90)
                size = 4.3
            else:
                fill = QColor.fromRgb(39+int(intensity*63),
                                     160+int(intensity*90),
                                     157+int(intensity*90))
                aura = QColor(56, 231, 214, 22+int(intensity*83))
                size = 3.1 + intensity*2.8
            r = 17 if is_pulsing else (12 if intensity>.25 else 8)
            glow = QRadialGradient(point, r)
            glow.setColorAt(0, aura)
            fade = QColor(aura)
            fade.setAlpha(0)
            glow.setColorAt(1, fade)
            painter.setBrush(glow)
            painter.drawEllipse(point, r, r)
            painter.setBrush(fill)
            painter.drawEllipse(point, size, size)
            if selected_node:
                painter.setPen(QPen(QColor("#ffe49b"), 1.5))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(point, 14, 14)
                painter.setPen(Qt.PenStyle.NoPen)
        # UI overlays are telemetry labels, not extra simulated computation.
        painter.fillRect(QRectF(0, max(0,h-56), w, 56), QColor(3, 12, 24, 220))
        painter.setPen(QColor("#c3f5f2"))
        painter.drawText(18, h-32,
                         f"STEP {state.step:>6}  ·  {state.total_neurons} NEURONS  "
                         f"·  {state.total_synapses} SYNAPSES  ·  {state.total_spikes} RECORDED SPIKES")
        painter.setPen(QColor("#8baebf"))
        painter.drawText(18, h-12,
                         "SOURCE: LOCAL LIF / SQLite   •   DRAG: PAN   •   SCROLL: ZOOM   "
                         "•   PATH ANIMATION: SCHEMATIC")
        painter.setPen(QColor("#77decf" if transient else "#8ba6b6"))
        painter.drawText(max(20, w-210), 29,
                         "● OBSERVED STEP" if transient else "○ NO NEW STEP")
        if state.truncated:
            painter.setPen(QColor("#ffc17f"))
            painter.drawText(20, 49, "DISPLAY LIMIT / partial neural graph")
        if selected is not None and 0 <= selected < len(state.nodes):
            n = state.nodes[selected]
            painter.setPen(QColor("#f1d9a6"))
            painter.drawText(20, 48,
                             f"NEURON {selected:03d} / V={n.voltage:.4f} / "
                             f"TRACE={n.trace:.4f} / SPIKE={int(n.fired)}")
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
