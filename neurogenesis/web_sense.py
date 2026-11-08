"""Operator-authorized read-only HTTPS perception with DNS/IP pinning.

Untrusted external pages are *sensory input only*. No JavaScript, redirects,
cookies, auth headers, proxy, downloads, shell, browser automation or external
code execution. This uses a single verified public IP for both validation and
the TLS connection, preventing the usual DNS rebinding time-of-check race.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import http.client
import ipaddress
import re
import socket
import ssl
from urllib.parse import urljoin, urlsplit


MAX_URL = 2048
MAX_BODY = 128 * 1024
MAX_CRAWL_BODY = 512 * 1024
MAX_TEXT = 6000
CONNECT_TIMEOUT = 6.0
MAX_LINKS = 256


class WebSenseError(ValueError):
    """Safe, explicit network-perception failure."""


@dataclass(frozen=True)
class WebObservation:
    url: str
    host: str
    text: str
    content_sha256: str
    retrieved_utc: str
    bytes_read: int
    response_status: int = 200
    links: tuple[str, ...] = ()


def validate_public_url(url: str) -> tuple[str, str, str]:
    """Only HTTPS:443 DNS hostnames; no userinfo, query, credentials or IPs."""
    if (type(url) is not str or not 1 <= len(url) <= MAX_URL
            or any(ord(c) < 33 or ord(c) == 127 for c in url)
            or "\\" in url):
        raise WebSenseError("Nieprawidłowy adres URL")
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise WebSenseError("Nieprawidłowy adres HTTPS") from exc
    if (parsed.scheme != "https" or not host or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment
            or port not in (None, 443)):
        raise WebSenseError("Dozwolone są wyłącznie publiczne adresy HTTPS bez parametrów")
    if (not host.isascii() or len(host) > 253
            or host.endswith((".local", ".internal", ".localhost", ".test", ".invalid"))
            or host == "localhost"
            or not re.fullmatch(
                r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
                r"[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?", host)):
        raise WebSenseError("Wymagana jest publiczna nazwa domenowa")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise WebSenseError("Bezpośrednie adresy IP są zabronione")
    path = parsed.path or "/"
    # Reject percent-encoded control bytes too, even though URL parsing would
    # preserve them in the path. Never allow CRLF request smuggling.
    if (len(path) > 1600 or
            re.search(r"%(?:0[0-9a-f]|1[0-9a-f]|7f)", path, re.I)):
        raise WebSenseError("Niepoprawna lub zbyt długa ścieżka URL")
    # Canonicalize the host and eliminate explicit :443 for stable deduplication.
    clean = "https://" + host + path
    return clean, host, path


def resolve_public_address(host: str, *, resolver=None) -> str:
    resolver = resolver or socket.getaddrinfo
    try:
        addresses = resolver(host, 443, type=socket.SOCK_STREAM)
    except (OSError, ValueError) as exc:
        raise WebSenseError("Nie można zweryfikować publicznego adresu serwera") from exc
    if not addresses or len(addresses) > 32:
        raise WebSenseError("Brak poprawnych adresów DNS")
    ips: list[str] = []
    for entry in addresses:
        try:
            address = ipaddress.ip_address(entry[4][0])
        except (TypeError, ValueError, IndexError) as exc:
            raise WebSenseError("Niepoprawny wynik DNS") from exc
        if not address.is_global:
            raise WebSenseError("Serwer wskazuje na adres prywatny lub zastrzeżony")
        ips.append(str(address))
    return ips[0]


class _PinnedHTTPS(http.client.HTTPSConnection):
    """TLS certificate checked against DNS hostname, socket pinned to public IP."""

    def __init__(self, host: str, ip: str, *, timeout: float = CONNECT_TIMEOUT):
        super().__init__(host, port=443, timeout=timeout,
                         context=ssl.create_default_context())
        self._verified_ip = ip

    def connect(self) -> None:
        plain = socket.create_connection((self._verified_ip, 443),
                                         timeout=self.timeout)
        try:
            self.sock = self._context.wrap_socket(plain, server_hostname=self.host)
        except BaseException:
            plain.close()
            raise


class _PlainTextParser(HTMLParser):
    SKIP = frozenset(("script", "style", "noscript", "svg", "iframe",
                      "form", "template", "head"))
    BLOCK = frozenset(("p", "br", "article", "section", "h1", "h2", "h3",
                       "h4", "li", "blockquote", "div"))

    def __init__(self, base_url: str | None = None) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: list[str] = []
        self._seen_links: set[str] = set()
        self._skip_stack: list[str] = []
        self.words: list[str] = []
        self.total = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if (tag == "a" and self.base_url and not self._skip_stack
                and len(self.links) < MAX_LINKS):
            href = dict(attrs).get("href")
            if isinstance(href, str) and href and len(href) <= MAX_URL:
                try:
                    candidate, _, _ = validate_public_url(urljoin(self.base_url, href))
                    if candidate not in self._seen_links:
                        self._seen_links.add(candidate)
                        self.links.append(candidate)
                except (WebSenseError, ValueError):
                    pass
        if self._skip_stack:
            if tag in self.SKIP:
                self._skip_stack.append(tag)
            return
        if tag in self.SKIP:
            self._skip_stack.append(tag)
        elif tag in self.BLOCK and self.total < MAX_TEXT:
            self.words.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._skip_stack and tag == self._skip_stack[-1]:
            self._skip_stack.pop()
        elif not self._skip_stack and tag in self.BLOCK and self.total < MAX_TEXT:
            self.words.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_stack or self.total >= MAX_TEXT:
            return
        chunk = data[: MAX_TEXT - self.total]
        self.total += len(chunk)
        self.words.append(chunk)

    def result(self) -> str:
        return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n",
                      "".join(self.words))).strip()[:MAX_TEXT]


def read_public_page(url: str, *, resolver=None, connection_factory=None,
                     max_body: int = MAX_BODY) -> WebObservation:
    """Fetch one explicitly approved public HTML/text URL.

    Disallow all redirects; operator must approve their new destination.
    DNS is validated once, and that verified IP is *actually connected*.
    """
    if type(max_body) is not int or not MAX_BODY <= max_body <= MAX_CRAWL_BODY:
        raise WebSenseError("Nieprawidłowy limit rozmiaru strony")
    clean_url, host, path = validate_public_url(url)
    ip = resolve_public_address(host, resolver=resolver)
    factory = connection_factory or _PinnedHTTPS
    conn = factory(host, ip, timeout=CONNECT_TIMEOUT)
    try:
        conn.request("GET", path, headers={
            "User-Agent": "NeuroGenesisResearchBot/0.7 (local read-only)",
            "Accept": "text/html,text/plain;q=0.9",
            "Accept-Encoding": "identity",
            "Connection": "close",
        })
        response = conn.getresponse()
        if response.status in (301, 302, 303, 307, 308):
            raise WebSenseError("Przekierowanie wymaga osobnej zgody na nowy adres")
        if response.status != 200:
            raise WebSenseError(f"Serwer zwrócił status HTTP {response.status}")
        content_type = response.getheader("Content-Type", "").lower()
        media_type = content_type.split(";", 1)[0].strip()
        if media_type not in ("text/html", "text/plain"):
            raise WebSenseError("Obsługiwane są wyłącznie tekst i HTML")
        encoding = response.getheader("Content-Encoding", "identity").lower()
        if encoding not in ("identity", ""):
            raise WebSenseError("Skompresowana odpowiedź nie jest akceptowana")
        length = response.getheader("Content-Length")
        if length is not None:
            try:
                declared = int(length)
            except ValueError as exc:
                raise WebSenseError("Nieprawidłowy nagłówek rozmiaru") from exc
            if not 0 <= declared <= max_body:
                raise WebSenseError("Strona przekracza dozwolony rozmiar")
        data = response.read(max_body + 1)
        if len(data) > max_body:
            raise WebSenseError("Strona przekracza dozwolony rozmiar")
    except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
        raise WebSenseError("Błąd połączenia HTTPS") from exc
    finally:
        conn.close()
    charset_match = re.search(r"(?:^|;)\s*charset\s*=\s*[\"']?([\w-]+)",
                              content_type)
    charset = charset_match.group(1) if charset_match else "utf-8"
    if charset not in ("utf-8", "iso-8859-1", "iso-8859-2", "windows-1250"):
        raise WebSenseError("Nieobsługiwane kodowanie strony")
    text = data.decode(charset, errors="replace")
    if media_type == "text/html":
        parser = _PlainTextParser(base_url=clean_url)
        parser.feed(text)
        result = parser.result()
        links = tuple(parser.links)
    else:
        result = text.strip()[:MAX_TEXT]
        links = ()
    if not result or len(result) < 20:
        raise WebSenseError("Nie znaleziono wystarczającej treści tekstowej")
    return WebObservation(
        url=clean_url,
        host=host,
        text=result,
        content_sha256=hashlib.sha256(data).hexdigest(),
        retrieved_utc=datetime.now(timezone.utc).isoformat(),
        bytes_read=len(data),
        links=links,
    )
