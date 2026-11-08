"""NeuroGenesis Command Center: optional, real-data PySide6 desktop shell.

Run only on explicit request: python -m neurogenesis.command_center.
The default Windows Tk EXE is unchanged. No fake neural/training telemetry.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

# Qt is an OPTIONAL runtime dependency; legacy desktop never imports this file.
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QPushButton, QSpinBox, QStackedWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget, QSizePolicy, QHeaderView,
)

from .command_service import CommandService

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
QWidget { background: #0b1220; color: #e2e8f0; font: 10pt 'Segoe UI'; }
QMainWindow, QFrame#sidebar { background: #0b1220; }
QFrame#card { background: #151f30; border: 1px solid #2b3950; border-radius: 12px; }
QFrame#topbar { background: #101a29; border-bottom: 1px solid #2b3950; }
QLabel#heading { color: #f5f9ff; font: 700 20pt 'Segoe UI'; }
QLabel#metric { color: #eff9ff; font: 700 19pt 'Segoe UI'; }
QLabel#subtle { color: #93a6bf; }
QLabel#status { color: #8ee5c9; font: 600 10pt 'Segoe UI'; }
QPushButton { background: #1a2a41; border: 1px solid #31465e; padding: 11px 14px;
              border-radius: 8px; color: #eaf2fb; text-align: center; }
QPushButton:hover { background: #263c56; }
QPushButton:pressed { background: #162637; }
QPushButton:disabled { color: #67768b; background: #132034; }
QPushButton#primary { background: #087e88; border-color: #159ba4; font-weight: 600; color: #ffffff; }
QPushButton#primary:hover { background: #0b909a; }
QPushButton#nav { text-align: left; border: 0; border-radius: 8px; background: transparent; padding: 12px 16px; }
QPushButton#nav:checked { background: #173c49; border-left: 3px solid #38c9c7; }
QPushButton#nav:hover { background: #1b2e42; }
QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QTableWidget {
    background: #0d1929; border: 1px solid #304158; border-radius: 8px;
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
        nav.addWidget(label("COMMAND CENTER  •  EXPERIMENTAL", kind="subtle"))
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
        self.navigate(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2500)
        self.events_timer = QTimer(self)
        self.events_timer.timeout.connect(self.poll_study_events)
        self.events_timer.start(200)
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
                                    if result["sources"] else ""))
        self.refresh()

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
            detail = description if kind != "fatal" else "Błąd: " + description
            self.study_log.appendPlainText(kind.upper() + " · " + detail)
        if events:
            self.refresh()

    def _build_brain(self) -> None:
        _, layout = self._page()
        card, inner = block("Monitor aktywności neuronowej",
                            "Rzeczywiste ślady aktywności z lokalnego Brain. Wykres nie mierzy świadomości.")
        self.brain_metrics = label("Ładowanie pomiarów...", kind="subtle")
        inner.addWidget(self.brain_metrics)
        self.brain_plot = ActivityPlot()
        inner.addWidget(self.brain_plot, 1)
        layout.addWidget(card, 1)
        layout.addWidget(label("Historyczna sieć LIF pozostaje eksperymentalnym punktem odniesienia. "
                               "Bez podłączonego modelu PyTorch nie pokazujemy strat ani dokładności treningu.",
                               kind="subtle"))

    def _build_training(self) -> None:
        _, layout = self._page()
        card, inner = block("Trening i sprzęt — stan rzeczywisty",
                            "Oddzielny Foundation Brain wymaga zatwierdzonego korpusu, checkpointu i kontrolowanego uruchomienia.")
        self.training_status = label("Brak uruchomionego procesu treningu.")
        inner.addWidget(self.training_status)
        inner.addWidget(label("CUDA, VRAM, parametry, loss, walidacja i prędkość będą prezentowane "
                               "dopiero po podłączeniu mierzonego pracownika modelu. "
                               "Dzisiaj Command Center nie uruchamia treningu samodzielnie.", kind="subtle"))
        layout.addWidget(card)
        layout.addStretch()

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
        diag, d = block("Diagnostyka")
        self.diag_status = label("Odczytywanie...", kind="subtle")
        d.addWidget(self.diag_status)
        layout.addWidget(diag)
        layout.addStretch()

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
        self.brain_metrics.setText(
            f"Rzeczywisty stan: neurony {s.neurons}, synapsy {s.synapses}, krok {s.brain_steps}")
        if self.pages.currentIndex() == 3:
            self.brain_plot.set_values(self.service.neural_traces())
        self.training_status.setText(
            f"Logiczne wątki CPU: {s.cpu_threads or 'brak odczytu'}\n"
            "Foundation training worker: NIEURUCHOMIONY\n"
            "CUDA/VRAM: NIEPOMIERZONE")
        self.diag_status.setText(
            f"SQLite: {s.database}\nSieć: {'zezwolono' if s.network_enabled else 'zablokowana'}\n"
            f"Aktywna sesja badawcza: {'tak' if s.research_running else 'nie'}")

    def closeEvent(self, event) -> None:
        self.service.set_network_consent(False)
        self.service.stop_study()
        super().closeEvent(event)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optional NeuroGenesis Qt Command Center")
    parser.add_argument("--db", type=Path, help="Existing private SQLite; never inside the public repo")
    args = parser.parse_args(argv)
    app = QApplication.instance() or QApplication([])
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
