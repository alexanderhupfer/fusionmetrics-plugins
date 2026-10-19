"""Public checks must catch a partially deployed OAuth and legal configuration."""
import json
import unittest

from probe_public import ORIGINS, probe
from validate import SCOPES


class PublicProbeTests(unittest.TestCase):
    def setUp(self):
        origin, issuer = ORIGINS["production"]
        self.origin, self.issuer = origin, issuer
        self.responses = {
            origin + "/healthz": {"ok": True, "deployedSha": "a" * 40},
            origin + "/.well-known/oauth-protected-resource/api/mcp": {
                "resource": origin + "/api/mcp", "authorization_servers": [issuer], "scopes_supported": SCOPES},
            issuer + "/.well-known/oauth-authorization-server": {
                "scopes_supported": SCOPES, "code_challenge_methods_supported": ["S256"],
                "authorization_endpoint": issuer + "/oauth/authorize", "token_endpoint": issuer + "/oauth/token",
                "registration_endpoint": issuer + "/oauth/register"},
            origin + "/terms": "Terms of Service",
            origin + "/privacy": "Hosted analytics and agent connections",
            origin + "/.well-known/openai-apps-challenge": "issued-public-challenge",
        }

    def get(self, url):
        if url == self.origin + "/api/mcp":
            return 401, {"WWW-Authenticate": f'Bearer resource_metadata="{self.origin}/.well-known/oauth-protected-resource/api/mcp"'}, "", url
        body = self.responses[url]
        return 200, {}, body if isinstance(body, str) else json.dumps(body), url

    def run_probe(self, **kwargs):
        return probe(expected_sha="a" * 40, expected_challenge="issued-public-challenge", get=self.get, **kwargs)

    def test_complete_public_configuration_passes(self):
        self.assertTrue(self.run_probe()["passed"])

    def test_missing_analytics_in_issuer_cannot_pass(self):
        self.responses[self.issuer + "/.well-known/oauth-authorization-server"]["scopes_supported"] = SCOPES[:-1]
        report = self.run_probe()
        self.assertFalse(report["passed"])
        self.assertIn("analytics:read", next(item["detail"]["missing"] for item in report["checks"] if item["check"] == "issuer-scopes"))

    def test_unissued_challenge_is_not_a_pass(self):
        report = probe(expected_sha="a" * 40, get=self.get)
        self.assertFalse(report["passed"])
        self.assertEqual(report["checks"][-1]["status"], "not_run")

    def test_wrong_revision_and_html_metadata_are_rejected(self):
        self.responses[self.origin + "/healthz"]["deployedSha"] = "b" * 40
        self.responses[self.issuer + "/.well-known/oauth-authorization-server"] = "<html>Sign in</html>"
        report = self.run_probe()
        self.assertFalse(report["passed"])
        self.assertTrue(any(item["check"] == "deployed-revision" and item["status"] == "failed" for item in report["checks"]))

    def test_challenge_must_match_and_is_not_disclosed_in_evidence(self):
        self.responses[self.origin + "/.well-known/openai-apps-challenge"] = "wrong-public-challenge"
        report = self.run_probe()
        self.assertFalse(report["passed"])
        self.assertNotIn("issued-public-challenge", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
