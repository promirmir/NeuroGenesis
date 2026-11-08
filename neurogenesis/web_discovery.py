"""Robots-aware bounded source discovery. Public HTTPS only, no search-engine scraping.

Only fetches robots.txt using the same pinned, verified TLS/IP transport as
web_sense. Fail closed on transport failures, forbidden paths and redirects.
External pages are data, never instructions to the agent.
"""
from __future__ import annotations

import http.client
import re
import ssl
from urllib.parse import unquote, urlsplit
from urllib.robotparser import RobotFileParser

from .web_sense import (
    CONNECT_TIMEOUT, _PinnedHTTPS, WebSenseError,
    resolve_public_address, validate_public_url,
)

USER_AGENT = "NeuroGenesisResearchBot"
MAX_ROBOTS_BODY = 64 * 1024


def fetch_public_robots(host: str, *, resolver=None, connection_factory=None) -> str:
    """Read robots.txt over pinned HTTPS; missing 404 means no declared policy.

    Other statuses and network failures are denied by the caller. Never follow
    redirects, use proxies/cookies or fetch non-public IP addresses.
    """
    _, canonical_host, _ = validate_public_url("https://" + host + "/robots.txt")
    ip = resolve_public_address(canonical_host, resolver=resolver)
    factory = connection_factory or _PinnedHTTPS
    conn = factory(canonical_host, ip, timeout=CONNECT_TIMEOUT)
    try:
        conn.request("GET", "/robots.txt", headers={
            "User-Agent": USER_AGENT + "/0.7",
            "Accept": "text/plain",
            "Accept-Encoding": "identity",
            "Connection": "close",
        })
        response = conn.getresponse()
        if response.status == 404:
            return ""
        if response.status != 200:
            raise WebSenseError("robots.txt niedostępny lub zabroniony")
        encoding = response.getheader("Content-Encoding", "identity").lower()
        if encoding not in ("identity", ""):
            raise WebSenseError("Niedozwolona kompresja robots.txt")
        size = response.getheader("Content-Length")
        if size is not None:
            try:
                declared = int(size)
            except ValueError as exc:
                raise WebSenseError("Nieprawidłowy rozmiar robots.txt") from exc
            if not 0 <= declared <= MAX_ROBOTS_BODY:
                raise WebSenseError("Zbyt duży plik robots.txt")
        body = response.read(MAX_ROBOTS_BODY + 1)
        if len(body) > MAX_ROBOTS_BODY:
            raise WebSenseError("Zbyt duży plik robots.txt")
        return body.decode("utf-8-sig", errors="replace")
    except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
        raise WebSenseError("Błąd bezpiecznego odczytu robots.txt") from exc
    finally:
        conn.close()


class RobotsPolicy:
    def __init__(self, fetch=fetch_public_robots):
        if not callable(fetch):
            raise TypeError("fetch musi być wywoływalny")
        self.fetch = fetch
        self.cache: dict[str, RobotFileParser | None] = {}

    def check(self, url: str) -> tuple[bool, float]:
        """Whether public URL is crawlable, plus requested per-host delay."""
        canonical, host, _ = validate_public_url(url)
        if host not in self.cache:
            try:
                data = self.fetch(host)
                if not isinstance(data, str):
                    raise ValueError("robots must be text")
                parser = RobotFileParser()
                parser.parse(data.splitlines())
                self.cache[host] = parser
            except Exception:
                self.cache[host] = None  # unavailable robots => fail closed
        parser = self.cache[host]
        if parser is None or not parser.can_fetch(USER_AGENT, canonical):
            return False, 0.0
        delay = parser.crawl_delay(USER_AGENT)
        return True, float(min(3600, max(0, delay or 0)))


def relevant_public_link(url: str, topic: str) -> bool:
    """Conservative seed expansion: at least one meaningful topic stem in URL."""
    try:
        canonical, host, path = validate_public_url(url)
    except WebSenseError:
        return False
    if path == "/robots.txt":
        return False
    searchable = (host + " " + unquote(path)).casefold()
    words = re.findall(r"\w+", topic.casefold(), flags=re.UNICODE)
    return any(word[:5] in searchable for word in words if len(word) >= 4)
