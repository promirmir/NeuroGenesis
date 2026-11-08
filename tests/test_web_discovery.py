"""Offline test for robots transport and link-scoped policy."""
import socket
import unittest

from neurogenesis.web_discovery import (
    RobotsPolicy, fetch_public_robots, relevant_public_link,
)
from neurogenesis.web_sense import WebSenseError


def dns(host, port, *, type=None):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("1.1.1.1", 443))]


class FakeResponse:
    status = 200
    body = b"User-agent: NeuroGenesisResearchBot\nDisallow: /secret\nCrawl-delay: 9\n"
    def getheader(self, name, default=None):
        return default
    def read(self, n):
        return self.body[:n]


class FakeConnection:
    instances = []
    def __init__(self, host, ip, *, timeout):
        self.host = host
        self.ip = ip
        self.path = None
        self.closed = False
        self.instances.append(self)
    def request(self, method, path, headers):
        self.path = path
        self.headers = headers
    def getresponse(self):
        return FakeResponse()
    def close(self):
        self.closed = True


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        FakeConnection.instances.clear()
        FakeResponse.status = 200
        FakeResponse.body = (
            b"User-agent: NeuroGenesisResearchBot\n"
            b"Disallow: /secret\nCrawl-delay: 9\n")

    def test_robot_fetch_uses_pinned_public_ip_and_closes(self):
        text = fetch_public_robots("example.org", resolver=dns,
                                   connection_factory=FakeConnection)
        self.assertIn("Disallow", text)
        conn, = FakeConnection.instances
        self.assertEqual(conn.ip, "1.1.1.1")
        self.assertEqual(conn.path, "/robots.txt")
        self.assertTrue(conn.closed)

    def test_robot_redirect_denied_without_following(self):
        FakeResponse.status = 302
        with self.assertRaises(WebSenseError):
            fetch_public_robots("example.org", resolver=dns,
                                connection_factory=FakeConnection)
        self.assertEqual(len(FakeConnection.instances), 1)
        self.assertTrue(FakeConnection.instances[0].closed)

    def test_robot_404_is_valid_missing_policy(self):
        FakeResponse.status = 404
        self.assertEqual(fetch_public_robots(
            "example.org", resolver=dns,
            connection_factory=FakeConnection), "")

    def test_robots_rules_and_delay(self):
        calls = []
        def fake_fetch(host):
            calls.append(host)
            return FakeResponse.body.decode()
        policy = RobotsPolicy(fetch=fake_fetch)
        self.assertEqual(policy.check("https://example.org/public"), (True, 9.0))
        self.assertEqual(policy.check("https://example.org/secret"), (False, 0.0))
        self.assertEqual(calls, ["example.org"])

    def test_topic_filter_excludes_queries_credentials_private_host(self):
        self.assertTrue(relevant_public_link(
            "https://open-source.example/articles/mechanika", "mechanika"))
        self.assertFalse(relevant_public_link(
            "https://open-source.example/garden", "mechanika"))
        for url in ("https://127.0.0.1/mechanika",
                    "https://example.org/?q=mechanika",
                    "http://example.org/mechanika",
                    "https://user:pw@" + "example.org/mechanika"):
            with self.subTest(url=url):
                self.assertFalse(relevant_public_link(url, "mechanika"))


if __name__ == "__main__":
    unittest.main()
