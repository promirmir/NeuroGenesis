"""The public source should never re-introduce secrets or private identities."""

from __future__ import annotations

import unittest

from neurogenesis.origin import origin_record
from scripts.privacy_audit import source_findings, text_findings


class PrivacyTests(unittest.TestCase):
    def test_current_distribution_has_no_detected_personal_data(self):
        self.assertEqual(source_findings(), [])

    def test_public_attribution_is_first_name_only(self):
        origin = origin_record()
        self.assertEqual(origin["credit"], "Miron przy pomocy AI")
        self.assertEqual(origin["human_initiator"]["name"], "Miron")
        self.assertEqual(len(origin["human_initiator"]["name"].split()), 1)

    def test_private_email_is_rejected_but_public_github_noreply_is_accepted(self):
        self.assertIn("private email address", text_findings("mail: example.person" + "@example.com"))
        self.assertEqual(text_findings("215201848+promirmir@users.noreply.github.com"), [])

    def test_given_name_plus_family_name_is_blocked_without_embedding_family_name(self):
        self.assertIn("private family name following project initiator given name",
                      text_findings("Miron " + "Example"))
        self.assertEqual(text_findings("Miron przy pomocy AI"), [])

    def test_secret_and_private_path_detection(self):
        self.assertIn("potential credential", text_findings("-----BEGIN" + " PRIVATE KEY-----"))
        self.assertIn("local user profile path", text_findings("C:" + r"\Users\Example\Desktop"))


if __name__ == "__main__":
    unittest.main()
