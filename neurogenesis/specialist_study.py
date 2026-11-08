"""Bounded, opt-in specialist research queue; never executes page instructions.

This is source acquisition and local provenance, NOT neural weight training.
Miron przy pomocy AI.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import re
import tempfile
import threading
import time
from urllib.parse import quote

from .web_sense import read_public_page, validate_public_url

MAX_PAGES = 20
MAX_TOPIC = 100
MIN_INTERVAL = 5.0


def plan_topic(topic: str, *, max_pages: int = 6) -> list[str]:
    """Deterministic Wikipedia topic seed; no remote search or network side effects."""
    if type(topic) is not str or not 1 <= len(topic.strip()) <= MAX_TOPIC:
        raise ValueError("Dziedzina musi mieć od 1 do 100 znaków")
    if not re.fullmatch(r"[\w\s\-(),.]+", topic, re.UNICODE):
        raise ValueError("Dziedzina zawiera niedozwolone znaki")
    if type(max_pages) is not int or not 1 <= max_pages <= MAX_PAGES:
        raise ValueError("Nieprawidłowy limit stron")
    words = topic.strip().split()
    if len(words) > 12:
        raise ValueError("Zbyt wiele słów")
    # No uncontrolled web crawling; derived Wikipedia URLs are visible and bounded.
    titles = ["_".join(words)]
    if len(words) > 1:
        titles.extend(words[: max_pages - 1])
    urls = ["https://pl.wikipedia.org/wiki/" + quote(t, safe="_") for t in titles]
    return [validate_public_url(url)[0] for url in dict.fromkeys(urls)][:max_pages]


@dataclass(frozen=True)
class StudyProgress:
    topic: str
    attempted: int
    accepted: int
    errors: int
    stopped: bool


class SpecialistStudy:
    """Explicit start; sequential, rate-limited, interruptible, private local metadata.

    Caller supplies observe callback (e.g. ExperienceMemory.observe_web) to persist
    a successful observation. No raw page content is saved by this controller.
    """

    def __init__(self, topic: str, observe, *, max_pages: int = 6,
                 interval: float = MIN_INTERVAL, fetch=read_public_page):
        if not callable(observe) or not callable(fetch):
            raise TypeError("Wymagane funkcje obserwacji i pobierania")
        if not isinstance(interval, (int, float)) or not MIN_INTERVAL <= interval <= 3600:
            raise ValueError("Odstęp musi wynosić co najmniej 5 sekund")
        self.topic = topic.strip()
        self.urls = plan_topic(topic, max_pages=max_pages)
        self.observe = observe
        self.fetch = fetch
        self.interval = float(interval)
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._running = False
        self.attempted = 0
        self.accepted = 0
        self.errors: list[str] = []

    def stop(self) -> None:
        self._stop.set()

    def progress(self) -> StudyProgress:
        with self._lock:
            return StudyProgress(self.topic, self.attempted, self.accepted,
                                 len(self.errors), self._stop.is_set())

    def run(self, *, consent: bool = False, on_event=None) -> StudyProgress:
        if consent is not True:
            raise PermissionError("Wymagana jawna zgoda na dostęp HTTPS")
        with self._lock:
            if self._running:
                raise RuntimeError("Szkolenie już trwa")
            self._running = True
        try:
            for index, url in enumerate(self.urls):
                if self._stop.is_set():
                    break
                if index and self._stop.wait(self.interval):
                    break
                try:
                    # Revalidate even if the plan was previously constructed.
                    validate_public_url(url)
                    observation = self.fetch(url)
                    self.observe(observation)
                    with self._lock:
                        self.accepted += 1
                    if on_event:
                        on_event("saved", url)
                except Exception as exc:
                    # Do not expose fetched text, credentials or exception internals.
                    with self._lock:
                        self.errors.append(type(exc).__name__)
                    if on_event:
                        on_event("error", url)
                finally:
                    with self._lock:
                        self.attempted += 1
            return self.progress()
        finally:
            with self._lock:
                self._running = False
