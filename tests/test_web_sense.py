"""Fail-closed live HTTPS perception and real neural/SQLite integration tests.

All network inputs are mocked at the socket-connection seam; CI never reaches
a website and never depends on DNS or an external service.
"""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from neurogenesis.memory import ExperienceMemory
from neurogenesis.web_sense import (
    MAX_BODY, WebObservation, WebSenseError,
    read_public_page, resolve_public_address, validate_public_url,
)


def fake_dns(host, port, *, type=None):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443))]


class DummyResponse:
    def __init__(self, body=b"<html><body><p>Some safe public scientific text "
                             b"about neurons, learning and prediction.</p></body></html>",
                 status=200, content_type="text/html", encoding="identity",
                 content_length=None):
        self.status = status
        self.body = body
        self.headers = {"Content-Type": content_type,
                        "Content-Encoding": encoding}
        if content_length is not None:
            self.headers["Content-Length"] = content_length

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def read(self, max_bytes):
        return self.body[:max_bytes]


class DummyConn:
    instances = []
    result = None

    def __init__(self, host, ip, *, timeout):
        self.host = host
        self.ip = ip
        self.timeout = timeout
        self.requested = None
        self.closed = False
        type(self).instances.append(self)

    def request(self, method, path, headers):
        self.requested = (method, path, headers)

    def getresponse(self):
        return type(self).result or DummyResponse()

    def close(self):
        self.closed = True


class PublicHTTPSValidationTests(unittest.TestCase):
    def setUp(self):
        DummyConn.instances.clear()
        DummyConn.result = None

    def read(self, url="https://example.org/research"):
        return read_public_page(url, resolver=fake_dns,
                                connection_factory=DummyConn)

    def test_hard_reject_private_urls_and_auth_query_redirect_schemes(self):
        bad = (
            "http://example.org/", "https://localhost/", "https://127.0.0.1/",
            "https://10.0.0.1/x", "https://internal.local/thing",
            "https://example.org:8443/a", "https://user:password@" + "example.org/",
            "https://example.org/?token=topsecret",
            "https://example.org/page#private",
            "https://example.org/%0a",
            "file:///etc/passwd", "https://example.org\\@127.0.0.1/",
            "https://example.org/a\nX-Test: secret", "https://[::1]/",
            "https://example.org:abc/", "https://a.invalid/",
            "https://example.org " )
        for url in bad:
            with self.subTest(url=url), self.assertRaises(WebSenseError):
                validate_public_url(url)
        self.assertEqual(DummyConn.instances, [])

    def test_public_dns_resolves_once_to_pinned_ip(self):
        obs = self.read("https://EXAMPLE.ORG/research")
        self.assertEqual(obs.url, "https://example.org/research")
        self.assertEqual(obs.host, "example.org")
        conn, = DummyConn.instances
        self.assertEqual((conn.host, conn.ip), ("example.org", "1.1.1.1"))
        self.assertEqual(conn.requested[0], "GET")
        self.assertEqual(conn.requested[1], "/research")
        self.assertTrue(conn.closed)
        self.assertNotIn("Cookie", conn.requested[2])
        self.assertEqual(len(obs.content_sha256), 64)
        self.assertIn("neurons", obs.text)

    def test_mixed_private_and_public_dns_fails_closed(self):
        for private in ("127.0.0.1", "10.0.0.5", "192.168.1.1",
                        "169.254.169.254", "100.64.0.1", "192.0.2.1",
                        "::1", "fd00::1"):
            with self.subTest(ip=private):
                def mixed(host, port, *, type=None):
                    return [("", "", "", "", ("1.1.1.1", 443)),
                            ("", "", "", "", (private, 443))]
                with self.assertRaises(WebSenseError):
                    read_public_page("https://example.org/",
                                     resolver=mixed,
                                     connection_factory=DummyConn)
        self.assertEqual(DummyConn.instances, [])

    def test_redirects_rejected_and_never_followed(self):
        DummyConn.result = DummyResponse(status=302)
        with self.assertRaisesRegex(WebSenseError, "Przekierowanie"):
            self.read()
        self.assertEqual(len(DummyConn.instances), 1)
        self.assertTrue(DummyConn.instances[0].closed)

    def test_reject_binary_compressed_or_oversized_pages(self):
        cases = (
            DummyResponse(content_type="application/octet-stream"),
            DummyResponse(encoding="gzip"),
            DummyResponse(body=b"x" * (MAX_BODY + 2),
                          content_type="text/plain"),
            DummyResponse(content_length=str(MAX_BODY + 1)),
            DummyResponse(status=503),
            DummyResponse(body=b"small", content_type="text/plain"),
        )
        for response in cases:
            DummyConn.result = response
            with self.subTest(response=response), self.assertRaises(WebSenseError):
                self.read()
        self.assertTrue(all(c.closed for c in DummyConn.instances))

    def test_html_untrusted_scripts_forms_and_head_are_not_executed(self):
        DummyConn.result = DummyResponse(
            body=(b"<html><head><title>Hidden title</title></head><body>"
                  b"<h1>Public heading text here</h1>"
                  b"<script>STEAL_PASSWORD();</script>"
                  b"<form><input value='secret'>PRIVATE_FIELD</form>"
                  b"<p>Research shows that context matters to prediction.</p>"
                  b"</body></html>"))
        obs = self.read()
        self.assertIn("context matters", obs.text)
        self.assertNotIn("STEAL_PASSWORD", obs.text)
        self.assertNotIn("PRIVATE_FIELD", obs.text)
        self.assertNotIn("Hidden title", obs.text)

    def test_html_links_are_validated_before_research_discovery(self):
        DummyConn.result = DummyResponse(body=(
            b"<html><body><h1>Science about learning and memory</h1>"
            b"<a href='/Mechanika'>local</a>"
            b"<a href='https://public.example/Mechanika'>external</a>"
            b"<a href='http://public.example/Mechanika'>insecure</a>"
            b"<a href='https://127.0.0.1/Mechanika'>private</a>"
            b"<a href='https://public.example/?token=secret'>query</a>"
            b"<a href='javascript:alert(1)'>javascript</a></body></html>"))
        observation = self.read()
        self.assertIn("https://example.org/Mechanika", observation.links)
        self.assertIn("https://public.example/Mechanika", observation.links)
        self.assertEqual(len(observation.links), 2)

    def test_larger_crawler_limit_requires_explicit_opt_in(self):
        from neurogenesis.web_sense import MAX_CRAWL_BODY
        DummyConn.result = DummyResponse(
            body=b"Learning mechanisms are measurable. " * 7000,
            content_type="text/plain")
        with self.assertRaises(WebSenseError):
            self.read()
        self.assertGreater(DummyConn.result.body.__len__(), MAX_BODY)
        obs = read_public_page("https://example.org/learning", resolver=fake_dns,
                               connection_factory=DummyConn,
                               max_body=MAX_CRAWL_BODY)
        self.assertGreater(obs.bytes_read, MAX_BODY)
        self.assertEqual(obs.links, ())

    def test_dns_failure_is_explicit_and_does_not_touch_network(self):
        def unreachable(host, port, *, type=None):
            raise OSError("not found")
        with self.assertRaises(WebSenseError):
            read_public_page("https://example.org/",
                             resolver=unreachable,
                             connection_factory=DummyConn)
        self.assertEqual(len(DummyConn.instances), 0)

    def test_plain_text_and_legacy_codepages_are_supported(self):
        DummyConn.result = DummyResponse(
            body=("To jest polski tekst o nauce neuronowej. " * 3).encode("windows-1250"),
            content_type="text/plain; charset=windows-1250")
        obs = self.read()
        self.assertIn("polski tekst", obs.text)
        self.assertEqual(obs.bytes_read, len(DummyConn.result.body))


class PublicWebSQLiteTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db = Path(folder.name) / "private.sqlite3"
        self.mem = ExperienceMemory(self.db)

    def observation(self, *, url="https://example.org/lesson", body=None):
        body = body or "Neuron. Synapses adapt as new observations arrive."
        data = body.encode("utf-8")
        return WebObservation(
            url=url, host="example.org", text=body,
            content_sha256=hashlib.sha256(data).hexdigest(),
            retrieved_utc=datetime.now(timezone.utc).isoformat(),
            bytes_read=len(data))

    def test_web_ingestion_is_neural_and_provenance_atomic_without_raw_text(self):
        before = self.mem.brain().steps
        page = self.observation()
        result = self.mem.observe_web(page)
        self.assertFalse(result["web_duplicate"])
        self.assertEqual(self.mem.brain().steps, before + 4)
        self.assertEqual(self.mem.status()["observations"], 1)
        self.assertEqual(self.mem.status()["web_observations"], 1)
        self.assertEqual(self.mem.status()["records_with_raw_text"], 0)
        saved = ExperienceMemory(self.db).recent_web()
        self.assertEqual(saved[0]["url"], page.url)
        self.assertEqual(saved[0]["sha256"], page.content_sha256)
        self.assertEqual(saved[0]["event_id"], result["event_id"])
        with closing(self.mem._connect()) as con:
            row = con.execute("SELECT source,raw_text FROM observations").fetchone()
        self.assertEqual(row, ("internet", None))

    def test_repeated_page_is_deduplicated_without_neural_training(self):
        page = self.observation()
        first = self.mem.observe_web(page)
        steps = self.mem.brain().steps
        second = self.mem.observe_web(page)
        self.assertTrue(second["web_duplicate"])
        self.assertEqual(second["event_id"], first["event_id"])
        self.assertEqual(self.mem.brain().steps, steps)
        self.assertEqual(self.mem.status()["observations"], 1)

    def test_changed_content_is_a_new_neural_observation(self):
        self.mem.observe_web(self.observation())
        self.mem.observe_web(self.observation(body="A totally new and changed public article about neurons."))
        self.assertEqual(self.mem.status()["observations"], 2)
        self.assertEqual(self.mem.status()["web_observations"], 2)
        self.assertEqual(self.mem.brain().steps, 8)

    def test_bad_provenance_fails_before_any_mutation(self):
        page = self.observation()
        baseline = self.mem.brain().to_dict()
        for kwargs in (
            {"source": "internet", "store_text": True},
            {"source": "desktop", "store_text": False},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.mem.remember(
                    page.text, web_provenance={
                        "url": page.url,
                        "sha256": page.content_sha256,
                        "retrieved_utc": page.retrieved_utc}, **kwargs)
        with self.assertRaises(ValueError):
            self.mem.remember(
                page.text, source="internet", web_provenance={
                    "url": "https://127.0.0.1/", "sha256": page.content_sha256,
                    "retrieved_utc": page.retrieved_utc})
        self.assertEqual(self.mem.brain().to_dict(), baseline)
        self.assertEqual(self.mem.status()["observations"], 0)

    def test_deleted_observation_deletes_provenance_but_not_brain(self):
        event = self.mem.observe_web(self.observation())["event_id"]
        before = self.mem.brain().to_dict()
        self.assertTrue(self.mem.delete_event(event))
        self.assertEqual(self.mem.recent_web(), [])
        self.assertEqual(self.mem.status()["observations"], 0)
        self.assertEqual(self.mem.brain().to_dict(), before)

    def test_legacy_user_memory_remains_backward_compatible(self):
        self.mem.remember("local existing experience")
        self.mem.teach("Kto to?", "NeuroGenesis.")
        self.mem.observe_web(self.observation())
        fresh = ExperienceMemory(self.db)
        self.assertEqual(fresh.status()["observations"], 3)
        self.assertEqual(fresh.status()["taught_responses"], 1)
        self.assertEqual(fresh.taught_answer("Kto to?")["answer"], "NeuroGenesis.")
        self.assertEqual(fresh.brain().steps, 12)


if __name__ == "__main__":
    unittest.main()
