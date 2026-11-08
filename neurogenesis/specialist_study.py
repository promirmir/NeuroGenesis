"""Autonomous but strictly bounded public-web specialist acquisition.

The study follows relevant hyperlinks across publicly accessible domains.
External pages are inert observations, never model instructions. This is not
gradient training, semantic mastery or a claim to cover the entire Internet.

Miron przy pomocy AI.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import re
import threading
import time
from urllib.parse import quote

from .web_discovery import RobotsPolicy, relevant_public_link
from .web_sense import read_public_page, validate_public_url

MAX_PAGES = 500
MAX_TOPIC = 100
MIN_INTERVAL = 5.0
MAX_QUEUE = 600
MAX_DOMAINS = 50
MAX_DEPTH = 3
MAX_PER_DOMAIN = 20


def plan_topic(topic: str, *, max_pages: int = 6) -> list[str]:
    """Create bounded public seed pages without remote requests."""
    if type(topic) is not str or not 1 <= len(topic.strip()) <= MAX_TOPIC:
        raise ValueError("Dziedzina musi mieć od 1 do 100 znaków")
    if not re.fullmatch(r"[\w\s\-(),.]+", topic, re.UNICODE):
        raise ValueError("Dziedzina zawiera niedozwolone znaki")
    if type(max_pages) is not int or not 1 <= max_pages <= MAX_PAGES:
        raise ValueError("Nieprawidłowy limit stron")
    words = topic.strip().split()
    if len(words) > 12:
        raise ValueError("Zbyt wiele słów")
    title = "_".join(words)
    titles = [title] + (words[: max_pages - 1] if len(words) > 1 else [])
    urls = ["https://pl.wikipedia.org/wiki/" + quote(t, safe="_") for t in titles]
    # An English seed also supports domains that are not linked from Polish pages.
    if len(urls) < max_pages:
        urls.append("https://en.wikipedia.org/wiki/" + quote(title, safe="_"))
    return [validate_public_url(url)[0] for url in dict.fromkeys(urls)][:max_pages]


@dataclass(frozen=True)
class StudyProgress:
    topic: str
    attempted: int
    accepted: int
    errors: int
    stopped: bool
    discovered: int = 0
    domains: int = 0


class SpecialistStudy:
    """Opt-in breadth-first source discovery with robots, budgets and stop.

    This class does not persist raw article text. Each successful observation
    is forwarded to the caller's existing local SQLite provenance pipeline.
    """

    def __init__(self, topic: str, observe, *, max_pages: int = 60,
                 interval: float = MIN_INTERVAL, fetch=read_public_page,
                 robots: RobotsPolicy | None = None, max_depth: int = MAX_DEPTH,
                 max_domains: int = MAX_DOMAINS,
                 max_per_domain: int = MAX_PER_DOMAIN):
        if not callable(observe) or not callable(fetch):
            raise TypeError("Wymagane funkcje obserwacji i pobierania")
        if type(interval) not in (int, float) or not MIN_INTERVAL <= interval <= 3600:
            raise ValueError("Odstęp musi wynosić co najmniej 5 sekund")
        if type(max_pages) is not int or not 1 <= max_pages <= MAX_PAGES:
            raise ValueError("Nieprawidłowy limit stron")
        if type(max_depth) is not int or not 0 <= max_depth <= MAX_DEPTH:
            raise ValueError("Nieprawidłowa głębokość wyszukiwania")
        if type(max_domains) is not int or not 1 <= max_domains <= MAX_DOMAINS:
            raise ValueError("Nieprawidłowy limit domen")
        if type(max_per_domain) is not int or not 1 <= max_per_domain <= MAX_PER_DOMAIN:
            raise ValueError("Nieprawidłowy limit na domenę")
        if robots is not None and not hasattr(robots, "check"):
            raise TypeError("Brak polityki robots.txt")
        self.topic = topic.strip()
        self.max_pages = max_pages
        self.urls = plan_topic(topic, max_pages=min(max_pages, 12))
        self.observe = observe
        self.fetch = fetch
        self.interval = float(interval)
        self.robots = robots if robots is not None else RobotsPolicy()
        self.max_depth = max_depth
        self.max_domains = max_domains
        self.max_per_domain = max_per_domain
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._running = False
        self.attempted = 0
        self.accepted = 0
        self.discovered = len(self.urls)
        self.domains = 0
        self.errors: list[str] = []

    def stop(self) -> None:
        self._stop.set()

    def progress(self) -> StudyProgress:
        with self._lock:
            return StudyProgress(
                self.topic, self.attempted, self.accepted, len(self.errors),
                self._stop.is_set(), self.discovered, self.domains)

    def run(self, *, consent: bool = False, on_event=None) -> StudyProgress:
        if consent is not True:
            raise PermissionError("Wymagana jawna zgoda na dostęp HTTPS")
        with self._lock:
            if self._running:
                raise RuntimeError("Szkolenie już trwa")
            self._running = True
        pending = deque((url, 0) for url in self.urls)
        seen = set(self.urls)
        domain_attempts: dict[str, int] = {}
        allowed_domains: set[str] = set()
        next_global = 0.0
        next_host: dict[str, float] = {}
        try:
            while pending and not self._stop.is_set() and self.attempted < self.max_pages:
                url, depth = pending.popleft()
                _, host, _ = validate_public_url(url)
                if domain_attempts.get(host, 0) >= self.max_per_domain:
                    continue
                if host not in allowed_domains and len(allowed_domains) >= self.max_domains:
                    continue
                try:
                    allowed, delay = self.robots.check(url)
                    if not allowed:
                        raise PermissionError("robots.txt blocks or cannot be verified")
                    # No HTTP page requests faster than the global and per-host budgets.
                    pause = max(0.0, next_global - time.monotonic(),
                                next_host.get(host, 0.0) - time.monotonic())
                    if pause and self._stop.wait(pause):
                        break
                    if self._stop.is_set():
                        break
                    allowed_domains.add(host)
                    domain_attempts[host] = domain_attempts.get(host, 0) + 1
                    with self._lock:
                        self.domains = len(allowed_domains)
                    # Rate limits apply even when fetching/processing later fails.
                    next_global = time.monotonic() + self.interval
                    next_host[host] = time.monotonic() + max(self.interval, delay)
                    observation = self.fetch(url)
                    if self._stop.is_set():
                        break
                    self.observe(observation)
                    with self._lock:
                        self.accepted += 1
                    if on_event:
                        on_event("saved", url)
                    if depth < self.max_depth:
                        for candidate in getattr(observation, "links", ()):
                            if len(pending) >= MAX_QUEUE:
                                break
                            if (candidate in seen or
                                    not relevant_public_link(candidate, self.topic)):
                                continue
                            try:
                                _, other_host, _ = validate_public_url(candidate)
                            except ValueError:
                                continue
                            if (other_host not in allowed_domains and
                                    len(allowed_domains) >= self.max_domains):
                                continue
                            seen.add(candidate)
                            pending.append((candidate, depth + 1))
                            with self._lock:
                                self.discovered += 1
                            if on_event:
                                on_event("discovered", candidate)
                except Exception as exc:
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
