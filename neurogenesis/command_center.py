"""NeuroGenesis Command Center: optional, real-data PySide6 desktop shell.

Run only on explicit request: python -m neurogenesis.command_center.
The default Windows Tk EXE is unchanged. No fake neural/training telemetry.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

# Qt is an OPTIONAL runtime dependency; legacy desktop never imports this file.
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QPushButton, QSpinBox, QStackedWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget, QSizePolicy, QHeaderView,
    QComboBox, QFileDialog, QScrollArea,
)

from .command_service import CommandService
from .qt_neural_view import NeuralFabric

PANELS = (
    ("Przegląd", "Stan systemu"),
    ("Rozmowa", "Odpowiedzi i źródła"),
    ("Badanie", "Kontrolowane HTTPS"),
    ("Mózg", "Rzeczywista aktywność"),
    ("Trening", "Model i zasoby"),
    ("Wiedza", "Lokalne dokumenty"),
    ("Ustawienia", "Zgody i diagnostyka"),
)

STYLE = """
QWidget { background: #081320; color: #e3f1f9; font: 10pt 'Segoe UI'; }
QMainWindow, QFrame#sidebar { background: #091929; }
QFrame#sidebar { border-right: 1px solid #1f5060; }
QFrame#card { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
    stop:0 #14263a, stop:1 #0b1a2b);
    border: 1px solid #2d5266; border-radius: 12px; }
QFrame#topbar { background: #0b2033; border-bottom: 2px solid #1b6278; }
QLabel#heading { color: #e8fbff; font: 700 20pt 'Segoe UI'; }
QLabel#metric { color: #e9ffff; font: 700 19pt 'Segoe UI'; }
QLabel#subtle { color: #9ebaca; }
QLabel#status { color: #65e4d1; font: 600 10pt 'Segoe UI'; }
QPushButton { background: #1a2a41; border: 1px solid #31465e; padding: 11px 14px;
              border-radius: 8px; color: #eaf2fb; text-align: center; }
QPushButton:hover { background: #263c56; }
QPushButton:pressed { background: #162637; }
QPushButton:disabled { color: #67768b; background: #132034; }
QPushButton#primary { background: #0b7e96; border-color: #2bc8d4;
    font-weight: 600; color: #ffffff; }
QPushButton#primary:hover { background: #0b909a; }
QPushButton#nav { text-align: left; border: 0; border-radius: 8px; background: transparent; padding: 12px 16px; }
QPushButton#nav:checked { background: #14516b; border-left: 4px solid #4fe8d4;
    color: #e4fdff; }
QPushButton#nav:hover { background: #1b2e42; }
QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QTableWidget {
    background: #0b1a2c; border: 1px solid #316077; border-radius: 8px;
    padding: 9px; selection-background-color: #19646e; color: #e9f3fa;
}
QCheckBox { color: #d5e4ef; spacing: 9px; }
QHeaderView::section { background: #192b41; color: #d4e7f0; padding: 8px; border: 0; }
QTableWidget { gridline-color: #304158; }
QScrollBar:vertical { background: #111f30; width: 10px; }
QScrollBar::handle:vertical { background: #3b536a; border-radius: 4px; min-height: 20px; }
"""


def label(text: str, *, kind: str | None = None) -> QLabel:
    obj = QLabel(text)
    if kind:
        obj.setObjectName(kind)
    obj.setWordWrap(True)
    return obj


def block(title: str, subtitle: str = "") -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(12)
    layout.addWidget(label(title, kind="heading"))
    if subtitle:
        layout.addWidget(label(subtitle, kind="subtle"))
    return frame, layout


class ActivityPlot(QWidget):
    """Only actual Brain.traces are drawn: no simulated neurons or animation."""

    def __init__(self):
        super().__init__()
        self._values: tuple[float, ...] = ()
        self.setMinimumHeight(230)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_values(self, values: tuple[float, ...]) -> None:
        self._values = values[:256]
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QColor("#101d30"))
        values = self._values
        if not values:
            painter.setPen(QColor("#93a6bf"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Brak zarejestrowanych śladów aktywności")
            return
        width = max(1, self.width() - 36)
        height = max(1, self.height() - 36)
        max_value = max(1.0, max(values))
        painter.setPen(QPen(QColor("#31465e"), 1))
        for fraction in (0.25, 0.5, 0.75):
            y = 12 + int(height * (1 - fraction))
            painter.drawLine(18, y, 18 + width, y)
        bar_width = width / len(values)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#43c9c6"))
        for i, value in enumerate(values):
            h = max(1, int(height * max(0.0, min(1.0, value / max_value))))
            x = 18 + int(i * bar_width)
            next_x = 18 + int((i + 1) * bar_width)
            painter.drawRect(x, 12 + height - h, max(1, next_x - x - 2), h)
        painter.end()


class CommandCenter(QMainWindow):
    def __init__(self, service: CommandService):
        super().__init__()
        self.service = service
        self.setWindowTitle("NeuroGenesis — Command Center")
        self.resize(1460, 900)
        self.setMinimumSize(880, 610)
        self.setStyleSheet(STYLE)

        frame = QWidget()
        shell = QHBoxLayout(frame)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(228)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(18, 26, 18, 20)
        nav.setSpacing(7)
        nav.addWidget(label("NEUROGENESIS", kind="heading"))
        nav.addWidget(label("NEURAL COMMAND CENTER  /  LIVE", kind="subtle"))
        nav.addSpacing(24)
        self.pages = QStackedWidget()
        self._nav_buttons: list[QPushButton] = []
        for index, (name, description) in enumerate(PANELS):
            button = QPushButton(name)
            button.setObjectName("nav")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self.navigate(i))
            self._nav_buttons.append(button)
            nav.addWidget(button)
        nav.addStretch()
        nav.addWidget(label("Miron przy pomocy AI", kind="subtle"))
        shell.addWidget(sidebar)
        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        topbar = QFrame()
        topbar.setObjectName("topbar")
        top = QHBoxLayout(topbar)
        top.setContentsMargins(28, 18, 28, 18)
        self.page_title = label("Przegląd", kind="heading")
        self.network_indicator = label("HTTPS WYŁĄCZONY", kind="status")
        top.addWidget(self.page_title)
        top.addStretch()
        top.addWidget(self.network_indicator)
        main.addWidget(topbar)

        self._build_overview()
        self._build_conversation()
        self._build_research()
        self._build_brain()
        self._build_training()
        self._build_knowledge()
        self._build_settings()
        main.addWidget(self.pages, 1)
        shell.addLayout(main, 1)
        self.setCentralWidget(frame)
        self.navigate(3)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2500)
        self.events_timer = QTimer(self)
        self.events_timer.timeout.connect(self.poll_study_events)
        self.events_timer.start(200)
        # Poll only while the live neural view is visible; no invented activity
        # and no scene redraw when the saved LIF step is unchanged.
        self.neural_timer = QTimer(self)
        self.neural_timer.timeout.connect(self.refresh_neural_view)
        self.neural_timer.start(350)
        self.refresh()

    def _page(self) -> tuple[QWidget, QVBoxLayout]:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(18)
        self.pages.addWidget(widget)
        return widget, layout

    def navigate(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        self.page_title.setText(PANELS[index][0] + "  /  " + PANELS[index][1])
        for i, button in enumerate(self._nav_buttons):
            button.setChecked(i == index)
        if index == 5:
            self.refresh_sources()
        if index == 3:
            self.refresh_neural_view()

    def _build_overview(self) -> None:
        _, layout = self._page()
        intro, inner = block("System badawczy", "Rzeczywiste dane z lokalnej pamięci — bez fikcyjnych wskaźników inteligencji.")
        self.overview_metrics = label("Odczytywanie stanu...")
        self.overview_metrics.setFont(QFont("Consolas", 12))
        inner.addWidget(self.overview_metrics)
        layout.addWidget(intro)
        split = QHBoxLayout()
        for title, text in [
            ("Wiedza", "Fragmenty dokumentów HTTPS pozostają lokalne; cytat nie oznacza potwierdzonej prawdziwości."),
            ("Model neuronowy", "Trenowany Foundation Brain jest nadal osobnym modułem badawczym, nie silnikiem rozmowy."),
            ("Zasoby", "Sieć domyślnie wyłączona. Żadnych ukrytych zadań GPU, chmury ani innych komputerów."),
        ]:
            card, content = block(title)
            content.addWidget(label(text, kind="subtle"))
            split.addWidget(card)
        layout.addLayout(split)
        layout.addStretch()

    def _build_conversation(self) -> None:
        _, layout = self._page()
        header, h = block("Rozmowa oparta na dowodach",
                          "Źródło odpowiedzi: ręcznie nauczona / cytat z bazy / brak potwierdzonego źródła.")
        layout.addWidget(header)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Tutaj pojawi się lokalna historia bieżącej sesji.")
        layout.addWidget(self.chat_history, 1)
        layout.addWidget(label("Twoje pytanie"))
        self.chat_input = QPlainTextEdit()
        self.chat_input.setPlaceholderText("Zapytaj o wybraną dziedzinę...")
        self.chat_input.setFixedHeight(84)
        layout.addWidget(self.chat_input)
        buttons = QHBoxLayout()
        self.chat_send = QPushButton("Wyślij pytanie")
        self.chat_send.setObjectName("primary")
        self.chat_send.clicked.connect(self.send_message)
        buttons.addWidget(self.chat_send)
        self.teach_input = QLineEdit()
        self.teach_input.setPlaceholderText("Opcjonalnie: wpisz ręcznie poprawną odpowiedź")
        buttons.addWidget(self.teach_input, 1)
        teach_button = QPushButton("Naucz ręcznie")
        teach_button.clicked.connect(self.teach_answer)
        buttons.addWidget(teach_button)
        clear = QPushButton("Wyczyść kontekst")
        clear.clicked.connect(self.clear_context)
        buttons.addWidget(clear)
        layout.addLayout(buttons)
        self.chat_status = label("Dane rozmowy nie są przesyłane przez internet.", kind="subtle")
        layout.addWidget(self.chat_status)

    def _append_chat(self, role: str, message: str) -> None:
        # Always inert plain text: untrusted page excerpts never become HTML.
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(role + "\n" + message + "\n\n")
        self.chat_history.setTextCursor(cursor)
        self.chat_history.ensureCursorVisible()

    def send_message(self) -> None:
        content = self.chat_input.toPlainText().strip()
        if not content:
            return
        try:
            result = self.service.ask(content)
        except (ValueError, OSError, RuntimeError) as exc:
            QMessageBox.warning(self, "Pamięć lokalna", str(exc))
            return
        self._append_chat("TY", content)
        self._append_chat("NEUROGENESIS · " + result["response_kind"], result["reply"])
        self.chat_input.clear()
        self.chat_status.setText("Odpowiedź: " + result["response_kind"]
                                 + (" · źródła: " + str(len(result["sources"]))
                                    if result["sources"] else "")
                                 + (" · użyto kontekstu sesji"
                                    if result.get("context_used") else ""))
        self.refresh()

    def clear_context(self) -> None:
        self.service.clear_conversation_context()
        self.chat_status.setText(
            "Wyczyszczono wyłącznie temat bieżącej sesji. Zapisana wiedza SQLite pozostała nienaruszona.")

    def teach_answer(self) -> None:
        question = self.chat_input.toPlainText().strip()
        answer = self.teach_input.text().strip()
        if not question or not answer:
            QMessageBox.information(self, "Nauka ręczna", "Wpisz pytanie i odpowiedź.")
            return
        try:
            self.service.teach(question, answer)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Nie zapisano", str(exc))
            return
        self._append_chat("NAUCZONO RĘCZNIE", question + "\n" + answer)
        self.teach_input.clear()
        self.chat_status.setText("Zapisano ręczną odpowiedź w prywatnej bazie.")
        self.refresh()

    def _build_research(self) -> None:
        _, layout = self._page()
        card, inner = block("Autonomiczne badanie dziedziny",
                            "HTTPS wyłącznie po zgodzie. Robots.txt, domeny, głębokość, tempo i liczba prób są ograniczone.")
        fields = QHBoxLayout()
        self.topic = QLineEdit()
        self.topic.setPlaceholderText("Dziedzina, np. plastyczność synaptyczna")
        fields.addWidget(self.topic, 1)
        self.page_budget = QSpinBox()
        self.page_budget.setRange(1, 500)
        self.page_budget.setValue(30)
        self.page_budget.setSuffix(" prób")
        fields.addWidget(self.page_budget)
        inner.addLayout(fields)
        commands = QHBoxLayout()
        self.research_start = QPushButton("Rozpocznij")
        self.research_start.setObjectName("primary")
        self.research_start.clicked.connect(self.start_study)
        commands.addWidget(self.research_start)
        self.research_stop = QPushButton("Zatrzymaj")
        self.research_stop.clicked.connect(self.stop_study)
        commands.addWidget(self.research_stop)
        commands.addStretch()
        inner.addLayout(commands)
        self.research_status = label("Brak aktywnego zadania.", kind="subtle")
        inner.addWidget(self.research_status)
        layout.addWidget(card)
        self.study_log = QPlainTextEdit()
        self.study_log.setReadOnly(True)
        self.study_log.document().setMaximumBlockCount(1200)
        self.study_log.setPlaceholderText("Zdarzenia źródeł, duplikatów i błędów będą widoczne tutaj.")
        layout.addWidget(self.study_log, 1)
        layout.addWidget(label("Pobieranie tekstu to NIE trening wag sieci. Pauza i wznowienie "
                               "będą dostępne dopiero po wdrożeniu trwałego stanu kolejki.",
                               kind="subtle"))

    def start_study(self) -> None:
        try:
            self.service.start_study(self.topic.text(), self.page_budget.value())
        except (ValueError, PermissionError, RuntimeError) as exc:
            QMessageBox.warning(self, "Badanie dziedziny", str(exc))
            return
        self.refresh()

    def stop_study(self) -> None:
        self.service.stop_study()
        self.refresh()

    def poll_study_events(self) -> None:
        events = self.service.poll_events(limit=100)
        for kind, description in events:
            if kind == "discovered":
                continue
            if kind in ("memory_backup_done", "memory_verify_done"):
                report = json.loads(description)
                what = ("Utworzono zweryfikowaną kopię" if kind == "memory_backup_done"
                        else "Integralność kopii zweryfikowana")
                self.backup_status.setText(
                    what + f" · {report['size_bytes']} bajtów"
                    + f" · {report['observations']} doświadczeń"
                    + f" · {report['source_versions']} wersji źródeł"
                    + "\nSHA-256: " + report["sha256"])
                continue
            if kind in ("memory_backup_failed", "memory_verify_failed"):
                self.backup_status.setText(
                    "Nie ukończono operacji. Zachowano dotychczasowe dane. "
                    "Powód: " + description)
                continue
            if kind == "train_progress":
                metrics = json.loads(description)
                self.training_log.appendPlainText(
                    f"Krok {metrics['step']}/{metrics['total']} · rzeczywista strata {metrics['loss']:.5f}")
                continue
            if kind == "train_done":
                measured = json.loads(description)
                self._last_training_summary = (
                    "Trening ukończony. Holdout (odrębny dokument): "
                    f"{measured['heldout_next_byte_ce_before']:.4f} → "
                    f"{measured['heldout_next_byte_ce_after']:.4f} nats; "
                    f"Markov {measured['heldout_markov_ce_nats']:.4f}; "
                    f"{measured['train_steps_per_second']:.2f} kroków/s; "
                    f"urządzenie {measured['device']}; "
                    f"wznowienie wag: {'tak' if measured.get('resumed_from_trusted_local_checkpoint') else 'nie'}; "
                    f"łączne kroki checkpointu: {measured.get('checkpoint_total_training_steps', measured['training_steps'])}; "
                    "optymalizator przy wznowieniu: nowy AdamW; CUDA VRAM: "
                    f"{measured['gpu_peak_allocated_bytes'] if measured['gpu_peak_allocated_bytes'] is not None else 'niezmierzono'}."
                    " Checkpoint KANDYDAT, nie aktywny silnik rozmowy.")
                self.training_log.appendPlainText("ZAKOŃCZONO · " + self._last_training_summary)
                continue
            if kind == "inference_done":
                report = json.loads(description)
                self.training_log.appendPlainText(
                    "MODELOWA KONTYNUACJA BAJTÓW (EKSPERYMENT, NIE ODPOWIEDŹ):\n"
                    + report["generated_text_utf8_replacement"]
                    + "\nHEX: " + report["generated_hex"]
                    + "\nWagi po " + str(report["trained_steps_in_checkpoint"])
                    + " krokach; " + f"{report['bytes_per_second']:.2f} bajtów/s"
                    + "; UTF-8: " + ("poprawny" if report["generated_valid_utf8"] else
                                     "zastąpiono uszkodzone sekwencje")
                    + ". Brak źródeł i weryfikacji faktów.")
                continue
            if kind in ("inference_cancelled", "inference_fatal"):
                self.training_log.appendPlainText(kind.upper() + " · " + description)
                continue
            if kind in ("train_cancelled", "train_fatal"):
                self._last_training_summary = ("Trening: " + description)
                self.training_log.appendPlainText(kind.upper() + " · " + description)
                continue
            detail = description if kind != "fatal" else "Błąd: " + description
            self.study_log.appendPlainText(kind.upper() + " · " + detail)
        if events:
            self.refresh()

    def _build_brain(self) -> None:
        _, layout = self._page()
        card, inner = block(
            "NEURAL FABRIC  /  LIVE NETWORK",
            "Prawdziwe zapisane neurony, synapsy, wagi, ślady i impulsy małej sieci LIF. "
            "Brak obliczeń oznacza brak nowych błysków.")
        self.brain_metrics = label("Odczytywanie rzeczywistego grafu...", kind="subtle")
        inner.addWidget(self.brain_metrics)
        self.brain_plot = NeuralFabric()
        inner.addWidget(self.brain_plot, 1)
        layout.addWidget(card, 1)
        self.neural_aux_metrics = label(
            "Foundation model: brak aktywnych obliczeń w tym monitorze.", kind="subtle")
        layout.addWidget(self.neural_aux_metrics)
        layout.addWidget(label(
            "Neurony wejściowe: niebieskie; pozostałe: turkusowe; błyski: nowy zapisany impuls. "
            "Wizualizowane przejście przez synapsę jest umowne czasowo, a brakujące "
            "węzły/połączenia są jawnie wykazane. Foundation Brain PyTorch działa "
            "osobno i nie jest tu imitowany. Bez mierników świadomości.",
            kind="subtle"))

    def refresh_neural_view(self) -> None:
        if self.pages.currentIndex() != 3:
            return
        try:
            frame = self.service.neural_frame()
        except (ValueError, OSError, RuntimeError) as exc:
            self.brain_metrics.setText("BŁĄD ODCZYTU GRAFU: " + type(exc).__name__)
            return
        self.brain_plot.set_frame(frame)
        self.brain_metrics.setText(
            f"Krok {frame.step}   ·   {frame.neurons} neuronów   ·   "
            f"{frame.synapses} synaps   ·   ostatnie impulsy {frame.last_spikes}"
            f"   ·   graf {frame.coverage}")

    def _build_training(self) -> None:
        _, page_layout = self._page()
        # Controls and the experimental decoding laboratory must remain
        # reachable on 720p laptops and high-DPI screens without clipping.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 8, 8, 12)
        layout.setSpacing(14)
        scroll.setWidget(content)
        page_layout.addWidget(scroll, 1)
        card, inner = block("Foundation Brain — trening neuronowy",
                            "Wyłącznie dokumenty zatwierdzone przez operatora do lokalnego treningu. "
                            "PyTorch [foundation] jest opcjonalny; brak automatycznego treningu.")
        self.training_status = label("Foundation training worker: NIEURUCHOMIONY")
        self._last_training_summary = ""
        inner.addWidget(self.training_status)
        budget = QHBoxLayout()
        budget.addWidget(label("Kroki:"))
        self.training_steps = QSpinBox()
        self.training_steps.setRange(1, 1000)
        self.training_steps.setValue(20)
        budget.addWidget(self.training_steps)
        budget.addWidget(label("Sprzęt:"))
        self.training_device = QComboBox()
        self.training_device.addItems(["cpu", "cuda"])
        budget.addWidget(self.training_device)
        budget.addStretch()
        inner.addLayout(budget)
        self.training_rights = QCheckBox(
            "Potwierdzam uprawnienie do treningu na zatwierdzonych źródłach")
        inner.addWidget(self.training_rights)
        self.training_resume = QCheckBox(
            "Kontynuuj wagami z zaufanego pliku wybranego poniżej (nowy checkpoint)")
        inner.addWidget(self.training_resume)
        buttons = QHBoxLayout()
        self.training_start = QPushButton("Uruchom trening")
        self.training_start.setObjectName("primary")
        self.training_start.clicked.connect(self.start_training)
        buttons.addWidget(self.training_start)
        self.training_stop = QPushButton("Przerwij")
        self.training_stop.clicked.connect(self.service.stop_training)
        buttons.addWidget(self.training_stop)
        buttons.addStretch()
        inner.addLayout(buttons)
        inner.addWidget(label(
            "Parametry wstępne: batch 2, sekwencja 32 bajty, ukryte 32. "
            "Kontynuacja przywraca wagi, lecz resetuje stan optymalizatora AdamW. "
            "Ostatni odrębny dokument służy do walidacji. "
            "Każdy zapis tworzy NOWY checkpoint, bez podmiany starego. "
            "Rozmowa nadal korzysta z cytatów źródeł.",
            kind="subtle"))
        layout.addWidget(card)
        self.training_log = QPlainTextEdit()
        self.training_log.setReadOnly(True)
        self.training_log.document().setMaximumBlockCount(800)
        self.training_log.setPlaceholderText("Tutaj pojawią się rzeczywiste pomiary strat i wyniki walidacji.")
        lab, controls = block("Eksperyment inferencji modelu",
                              "Niezależny dekoder wag GRU — NIE jest odpowiedzią czatu ani dowodem faktów.")
        checkpoint_row = QHBoxLayout()
        self.checkpoint_path = QLineEdit()
        self.checkpoint_path.setPlaceholderText("Ścieżka do własnego zaufanego checkpointu .pt")
        checkpoint_row.addWidget(self.checkpoint_path, 1)
        choose = QPushButton("Wybierz plik")
        choose.clicked.connect(self.choose_checkpoint)
        checkpoint_row.addWidget(choose)
        controls.addLayout(checkpoint_row)
        self.inference_prompt = QLineEdit()
        self.inference_prompt.setPlaceholderText("Prefiks tekstu dla eksperymentalnego przewidywania")
        controls.addWidget(self.inference_prompt)
        choice = QHBoxLayout()
        self.inference_bytes = QSpinBox()
        self.inference_bytes.setRange(1, 64)
        self.inference_bytes.setValue(16)
        self.inference_bytes.setSuffix(" bajtów")
        choice.addWidget(self.inference_bytes)
        self.trust_checkpoint = QCheckBox("Potwierdzam zaufane pochodzenie lokalnego pliku")
        choice.addWidget(self.trust_checkpoint, 1)
        controls.addLayout(choice)
        buttons = QHBoxLayout()
        self.inference_start = QPushButton("Wykonaj predykcję z wag")
        self.inference_start.clicked.connect(self.start_inference)
        buttons.addWidget(self.inference_start)
        self.inference_stop = QPushButton("Przerwij predykcję")
        self.inference_stop.clicked.connect(self.service.stop_candidate_inference)
        buttons.addWidget(self.inference_stop)
        controls.addLayout(buttons)
        layout.addWidget(lab)
        layout.addWidget(self.training_log, 1)

    def choose_checkpoint(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "Wybierz lokalny zaufany checkpoint", str(self.service.memory.path.parent),
            "Foundation Brain (*.pt *.pth)")
        if selected:
            self.checkpoint_path.setText(selected)

    def start_inference(self) -> None:
        if not self.trust_checkpoint.isChecked():
            QMessageBox.warning(self, "Niezaufany checkpoint",
                                "Potwierdź własny, lokalny checkpoint przed odczytem wag.")
            return
        try:
            self.service.start_candidate_inference(
                self.checkpoint_path.text(), self.inference_prompt.text(),
                confirmed=True, max_new_bytes=self.inference_bytes.value(),
                device=self.training_device.currentText())
        except (ValueError, OSError, RuntimeError, PermissionError) as exc:
            QMessageBox.warning(self, "Eksperyment predykcyjny", str(exc))
            return
        self.training_log.appendPlainText("START · rzeczywisty model, poza rozmową, bez sieci.")
        self.refresh()

    def start_training(self) -> None:
        if not self.training_rights.isChecked():
            QMessageBox.warning(self, "Prawa do treningu",
                                "Potwierdź prawa do zatwierdzonych źródeł.")
            return
        resume = self.training_resume.isChecked()
        if resume and not self.trust_checkpoint.isChecked():
            QMessageBox.warning(self, "Kontynuacja wag",
                                "Potwierdź zaufane pochodzenie wybranego checkpointu.")
            return
        previous = self.checkpoint_path.text().strip() if resume else None
        output = self.service.memory.path.with_name(
            "foundation-candidate-" + str(time.time_ns()) + ".pt")
        try:
            self.service.start_training(
                output, confirmed=True, steps=self.training_steps.value(),
                device=self.training_device.currentText(),
                resume_from=previous, trust_resume=resume)
        except (ValueError, PermissionError, OSError, RuntimeError) as exc:
            QMessageBox.warning(self, "Trening Foundation Brain", str(exc))
            return
        self._last_training_summary = ""
        self.checkpoint_path.setText(str(output))
        self.training_log.appendPlainText(
            "START · " + ("kontynuacja wybranych wag" if resume else "nowy model")
            + "; zaufane źródła, niezależny nowy plik, bez sieci.")
        self.refresh()

    def _build_knowledge(self) -> None:
        _, layout = self._page()
        card, inner = block("Lokalna pamięć źródeł",
                            "Wersje dokumentów, adresy i teksty pobrane po zgodzie. Prawa i fakty nie są automatycznie weryfikowane.")
        self.sources_table = QTableWidget(0, 4)
        self.sources_table.setHorizontalHeaderLabels(["Wersja", "Źródło URL", "Odczyt UTC", "Prawa"])
        self.sources_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self.sources_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sources_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sources_table.itemSelectionChanged.connect(self.show_selected_source)
        inner.addWidget(self.sources_table)
        refresh_button = QPushButton("Odśwież źródła")
        refresh_button.clicked.connect(self.refresh_sources)
        inner.addWidget(refresh_button)
        rights_buttons = QHBoxLayout()
        approve = QPushButton("Zatwierdź prawa do treningu")
        approve.clicked.connect(lambda: self.change_source_rights(True))
        rights_buttons.addWidget(approve)
        revoke = QPushButton("Cofnij zgodę na trening")
        revoke.clicked.connect(lambda: self.change_source_rights(False))
        rights_buttons.addWidget(revoke)
        inner.addLayout(rights_buttons)
        layout.addWidget(card, 1)
        self.source_preview = QPlainTextEdit()
        self.source_preview.setReadOnly(True)
        self.source_preview.setPlaceholderText("Wybierz źródło, aby przeczytać zachowane dosłowne fragmenty.")
        layout.addWidget(self.source_preview, 1)
        self._source_rows: list[dict] = []

    def refresh_sources(self) -> None:
        rows = self.service.sources(limit=20)
        self._source_rows = rows
        self.sources_table.blockSignals(True)
        self.sources_table.setRowCount(len(rows))
        for i, src in enumerate(rows):
            values = [str(src["version"]), src["url"], src["retrieved_utc"], src["rights_status"]]
            for column, value in enumerate(values):
                self.sources_table.setItem(i, column, QTableWidgetItem(value))
        self.sources_table.blockSignals(False)

    def show_selected_source(self) -> None:
        index = self.sources_table.currentRow()
        if not 0 <= index < len(self._source_rows):
            return
        source = self._source_rows[index]
        try:
            passages = self.service.source_passages(source["id"])
        except (ValueError, OSError) as exc:
            self.source_preview.setPlainText("Nie można odczytać źródła: " + str(exc))
            return
        self.source_preview.setPlainText(
            "Adres: " + source["url"] + "\nSHA-256: " + source["sha256"]
            + "\nWersja: " + str(source["version"])
            + "\nStatus praw: " + source["rights_status"] + "\n\n"
            + "\n\n".join(str(p["ordinal"] + 1) + ". " + p["text"] for p in passages))

    def change_source_rights(self, approved: bool) -> None:
        row = self.sources_table.currentRow()
        if not 0 <= row < len(self._source_rows):
            QMessageBox.information(self, "Wybór źródła", "Najpierw wybierz wersję dokumentu.")
            return
        source = self._source_rows[row]
        if approved:
            confirmed = QMessageBox.question(
                self, "Prawa do lokalnego treningu",
                "Czy potwierdzasz posiadanie praw lub uprawnienia do lokalnego "
                "trenowania modelu na tej konkretnej wersji źródła? "
                "To oświadczenie nie wynika automatycznie z dostępności publicznej strony.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmed != QMessageBox.StandardButton.Yes:
                return
        try:
            self.service.set_source_training_rights(source["id"], approved)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Prawa źródła", str(exc))
            return
        self.refresh_sources()
        self.source_preview.setPlainText(
            "Zapisano lokalne oświadczenie o prawach. Nie uruchomiono treningu.")

    def _build_settings(self) -> None:
        _, layout = self._page()
        card, inner = block("Zgoda na publiczny HTTPS",
                            "Zgoda obowiązuje tylko w tej sesji. Cofnięcie zatrzymuje dalsze zbieranie źródeł.")
        self.allow_https = QCheckBox("Zezwól na kontrolowane badanie publicznych źródeł HTTPS")
        self.allow_https.setChecked(False)
        self.allow_https.toggled.connect(self.change_consent)
        inner.addWidget(self.allow_https)
        inner.addWidget(label("Strony są niezaufanymi danymi. Odczyt respektuje robots.txt i "
                               "nie wykonuje kodu z internetu. Witryny widzą publiczny adres IP.", kind="subtle"))
        layout.addWidget(card)
        backup, b = block(
            "Bezpieczeństwo pamięci — kopie i integralność",
            "Ręczna kopia zapisuje pełny, spójny stan SQLite, także aktualne wersje źródeł. "
            "Nie wysyła danych do sieci. Plik NIE jest szyfrowany — chroń go jak prywatny dokument.")
        tools = QHBoxLayout()
        self.backup_button = QPushButton("Zapisz kopię pamięci…")
        self.backup_button.setObjectName("primary")
        self.backup_button.clicked.connect(self.save_memory_backup)
        tools.addWidget(self.backup_button)
        self.verify_button = QPushButton("Sprawdź kopię…")
        self.verify_button.clicked.connect(self.verify_memory_backup)
        tools.addWidget(self.verify_button)
        tools.addStretch()
        b.addLayout(tools)
        self.backup_status = label("Brak uruchomionego zadania kopii.", kind="subtle")
        self.backup_status.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        b.addWidget(self.backup_status)
        b.addWidget(label(
            "Przywracanie odbywa się wyłącznie do NOWEGO pliku, z osobnej komendy "
            "neurogenesis.recovery. Aplikacja nigdy nie nadpisuje automatycznie "
            "bieżącej pamięci.", kind="subtle"))
        layout.addWidget(backup)
        diag, d = block("Diagnostyka")
        self.diag_status = label("Odczytywanie...", kind="subtle")
        d.addWidget(self.diag_status)
        layout.addWidget(diag)
        layout.addStretch()

    def save_memory_backup(self) -> None:
        if (QMessageBox.question(
                self, "Prywatna kopia pamięci",
                "Kopia obejmuje zapisane informacje, źródła i ewentualne "
                "teksty prywatne. Plik nie jest szyfrowany. "
                "Czy utworzyć kopię tylko na tym komputerze?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                != QMessageBox.StandardButton.Yes):
            return
        default = str(self.service.memory.path.parent / "NeuroGenesis-backup.sqlite3")
        path, _ = QFileDialog.getSaveFileName(
            self, "Nowa kopia — nie nadpisuj istniejącej", default,
            "Baza NeuroGenesis (*.sqlite3)")
        if not path:
            return
        try:
            self.service.start_memory_backup(path)
        except (ValueError, RuntimeError, OSError) as exc:
            QMessageBox.warning(self, "Kopia pamięci", str(exc))
            return
        self.backup_status.setText("Trwa bezpieczna kopia SQLite…")
        self.refresh()

    def verify_memory_backup(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Wskaż kopię do weryfikacji",
            str(self.service.memory.path.parent), "Baza NeuroGenesis (*.sqlite3)")
        if not path:
            return
        try:
            self.service.start_memory_verification(path)
        except (ValueError, RuntimeError, OSError) as exc:
            QMessageBox.warning(self, "Weryfikacja pamięci", str(exc))
            return
        self.backup_status.setText("Sprawdzanie integralności kopii…")
        self.refresh()

    def change_consent(self, enabled: bool) -> None:
        self.service.set_network_consent(enabled)
        self.refresh()

    def refresh(self) -> None:
        try:
            s = self.service.snapshot()
        except (ValueError, OSError, RuntimeError) as exc:
            self.network_indicator.setText("BŁĄD PAMIĘCI")
            self.diag_status.setText(str(exc))
            return
        self.network_indicator.setText("HTTPS WŁĄCZONY" if s.network_enabled else "HTTPS WYŁĄCZONY")
        self.overview_metrics.setText(
            f"Dokumenty: {s.documents}     Fragmenty: {s.passages}\n"
            f"Obserwacje: {s.observations}     Kroki mózgu: {s.brain_steps}\n"
            f"Neurony: {s.neurons}     Synapsy: {s.synapses}\n"
            f"Badanie: {'AKTYWNE' if s.research_running else 'BRAK'}")
        self.research_status.setText(
            f"Próby: {s.research_attempted} · zapisano: {s.research_accepted} · "
            f"błędy: {s.research_errors} · odkryto: {s.research_discovered} · "
            f"domeny: {s.research_domains}")
        self.research_start.setEnabled(not s.research_running)
        self.research_stop.setEnabled(s.research_running)
        if self.pages.currentIndex() == 3:
            self.refresh_neural_view()
        self.neural_aux_metrics.setText(
            ("Foundation PyTorch: prawdziwy trening w toku, krok "
             + f"{s.training_step}/{s.training_total}; strata batch "
             + (f"{s.training_last_loss:.5f}" if s.training_last_loss is not None
                else "niezmierzona"))
            if s.training_running else
            "Foundation PyTorch: brak treningu. Graf przedstawia jedynie zapisany mózg LIF."
        )
        status = ("AKTYWNY" if s.training_running else "NIEURUCHOMIONY")
        measured = (f"{s.training_last_loss:.5f}" if s.training_last_loss is not None
                    else "brak pomiaru")
        self.training_status.setText(
            f"Logiczne wątki CPU: {s.cpu_threads or 'brak odczytu'}\n"
            f"Foundation training worker: {status} · {s.training_step}/{s.training_total} kroków\n"
            f"Ostatnia rzeczywista strata batch: {measured}\n"
            + (self._last_training_summary or "CUDA/VRAM: brak zakończonego pomiaru"))
        self.training_start.setEnabled(not s.training_running)
        self.training_stop.setEnabled(s.training_running)
        self.inference_start.setEnabled(not s.training_running and not s.inference_running)
        self.inference_stop.setEnabled(s.inference_running)
        self.backup_button.setEnabled(not s.memory_maintenance_running)
        self.verify_button.setEnabled(not s.memory_maintenance_running)
        self.diag_status.setText(
            f"SQLite: {s.database}\nSieć: {'zezwolono' if s.network_enabled else 'zablokowana'}\n"
            f"Aktywna sesja badawcza: {'tak' if s.research_running else 'nie'}")

    def closeEvent(self, event) -> None:
        self.service.set_network_consent(False)
        self.service.stop_study()
        self.service.stop_training()
        self.service.stop_candidate_inference()
        super().closeEvent(event)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optional NeuroGenesis Qt Command Center")
    parser.add_argument("--db", type=Path, help="Existing private SQLite; never inside the public repo")
    parser.add_argument("--self-test", action="store_true", help="Offline Qt+SQLite evidence smoke")
    args = parser.parse_args(argv)
    app = QApplication.instance() or QApplication([])
    if args.self_test:
        # Exercise the actual Qt widgets and local evidence backend in the
        # frozen binary. Never open a real web connection or touch user data.
        import hashlib
        import tempfile
        from datetime import datetime, timezone
        from .web_sense import WebObservation
        with tempfile.TemporaryDirectory(prefix="ng-qt-smoke-") as folder:
            service = CommandService(Path(folder) / "private.sqlite3")
            sample = "Publiczny tekst o neuronach, uczeniu i aktualnej wiedzy."
            service.memory.observe_web(WebObservation(
                url="https://example.org/research", host="example.org", text=sample,
                content_sha256=hashlib.sha256(sample.encode()).hexdigest(),
                retrieved_utc=datetime.now(timezone.utc).isoformat(),
                bytes_read=len(sample.encode())))
            restored = CommandService(service.memory.path)
            view = CommandCenter(restored)
            view.navigate(1)
            view.chat_input.setPlainText("Co wiadomo o neuronach i uczeniu?")
            view.send_message()
            cited = view.chat_history.toPlainText()
            if "source_evidence" not in cited or "https://example.org/research" not in cited:
                view.close()
                return 2
            view.navigate(5)
            view.refresh_sources()
            if view.sources_table.rowCount() != 1 or restored.network_enabled:
                view.close()
                return 3
            view.close()
        return 0
    try:
        service = CommandService(args.db)
    except (ValueError, OSError, RuntimeError) as exc:
        QMessageBox.critical(None, "NeuroGenesis — pamięć",
                             "Nie zmodyfikowano ani nie zresetowano istniejącej bazy.\n" + str(exc))
        return 1
    view = CommandCenter(service)
    view.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
