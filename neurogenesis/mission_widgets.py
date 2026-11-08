"""Visual components for the real-data NeuroGenesis mission dashboard.

The display is event-driven and deliberately cannot synthesize brain activity:
no sample, pulse, learning or GPU utilization is fabricated by a rendering timer.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .neural_telemetry import NeuralTelemetry


class MetricTile(QFrame):
    """Compact dashboard telemetry card with explicit units and provenance."""

    def __init__(self, title: str, footnote: str, parent=None):
        super().__init__(parent)
        self.setObjectName("metricTile")
        self.setMinimumWidth(155)
        column = QVBoxLayout(self)
        column.setContentsMargins(20, 17, 20, 18)
        column.setSpacing(5)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("metricCaption")
        self.value_label = QLabel("—")
        self.value_label.setObjectName("metricValue")
        self.value_label.setMinimumHeight(42)
        self.footnote_label = QLabel(footnote)
        self.footnote_label.setObjectName("metricFootnote")
        self.footnote_label.setWordWrap(True)
        column.addWidget(self.title_label)
        column.addWidget(self.value_label)
        column.addWidget(self.footnote_label)
        self.set_value(0)

    def set_value(self, value: int | str) -> None:
        if type(value) is int:
            if value < 0:
                raise ValueError("metric cannot be negative")
            shown = f"{value:,}".replace(",", " ")
        elif type(value) is str and 0 < len(value) <= 32:
            shown = value
        else:
            raise ValueError("metric must be a valid explicit value")
        self.value_label.setText(shown)


class SignalHistory(QWidget):
    """A trace made only from new, persisted LIF brain-step measurements."""

    MAX_POINTS = 96

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(166)
        self._samples: list[tuple[int, int]] = []
        self.setToolTip("Próbki tylko po zmianie kroku zapisanego w lokalnej bazie")

    @property
    def samples(self) -> tuple[tuple[int, int], ...]:
        return tuple(self._samples)

    def ingest(self, state: NeuralTelemetry) -> bool:
        if not isinstance(state, NeuralTelemetry):
            raise TypeError("measured NeuralTelemetry is required")
        if self._samples and state.step <= self._samples[-1][0]:
            return False
        # A sample is the last persisted spike mask count, not a synthetic
        # aggregate firing rate or artificial per-frame number.
        count = sum(int(node.fired) for node in state.nodes)
        self._samples.append((state.step, count))
        self._samples = self._samples[-self.MAX_POINTS:]
        self.update()
        return True

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(self.rect(), QColor("#071522"))
        w, h = self.width(), self.height()
        p.setPen(QColor("#8cb7cb"))
        p.setFont(QFont("Consolas", 9))
        p.drawText(17, 22, "SPIKE TRACE / ZAPISANE KROKI")
        left, top, right, bottom = 18.0, 38.0, max(40., float(w-18)), max(55., float(h-27))
        p.setPen(QPen(QColor("#1a3547"), 1))
        for i in range(4):
            yy = top+(bottom-top)*i/3
            p.drawLine(QPointF(left, yy), QPointF(right, yy))
        if len(self._samples) == 0:
            p.setPen(QColor("#6f8b9c"))
            p.drawText(QRectF(left, top, right-left, bottom-top),
                       Qt.AlignmentFlag.AlignCenter, "Oczekiwanie na zapisany stan LIF")
            p.end()
            return
        max_count = max(1, *(count for _, count in self._samples))
        points: list[QPointF] = []
        for i, (_, count) in enumerate(self._samples):
            x = left+(right-left)*i/max(1, len(self._samples)-1)
            y = bottom-(bottom-top)*(count/max_count)
            points.append(QPointF(x, y))
        p.setPen(QPen(QColor("#43dfd1"), 2))
        for i in range(1, len(points)):
            p.drawLine(points[i-1], points[i])
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#c3fff0"))
        p.drawEllipse(points[-1], 3.5, 3.5)
        p.setPen(QColor("#86b4c3"))
        last_step, last_count = self._samples[-1]
        p.drawText(17, h-7, f"OSTATNI KROK {last_step}  /  SPIKI W MASCE {last_count}  /  PRÓBEK {len(points)}")
        p.end()


class PipelineStep(QFrame):
    """Status labels state what each module really does, without fake flow."""

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("pipelineStep")
        self.setMinimumWidth(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(13, 13, 13, 13)
        layout.setSpacing(5)
        heading = QLabel(title)
        heading.setObjectName("pipelineHeading")
        self.state_label = QLabel("—")
        self.state_label.setObjectName("pipelineValue")
        self.state_label.setWordWrap(True)
        hint = QLabel(description)
        hint.setObjectName("pipelineHint")
        hint.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(self.state_label)
        layout.addWidget(hint)

    def set_state(self, state: str) -> None:
        if type(state) is not str or not 0 < len(state) <= 90:
            raise ValueError("pipeline state requires a bounded string")
        self.state_label.setText(state)
