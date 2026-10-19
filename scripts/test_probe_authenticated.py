"""Guard reviewer isolation and prevent misleading live-probe evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from urllib.request import Request

from probe_authenticated import Client, NoRedirect, envelope, private_token, run, valid_tools


class AuthenticatedProbeTests(unittest.TestCase):
    def test_analytics_text_error_is_not_a_success(self):
        result = {"content": [{"type": "text", "text": json.dumps({
            "ok": False, "error": {"code": "invalid_sql"}})}]}
        self.assertFalse(envelope(result)["ok"])
        with self.assertRaises(ValueError):
            envelope({"content": [{"type": "text", "text": '{"data": []}'}]})
        with self.assertRaises(ValueError):
            envelope({"isError": True, "structuredContent": {"ok": True, "data": []}})

    def test_redirect_never_receives_credentials(self):
        request = Request("https://fusionmetrics.com/api/mcp", headers={"Authorization": "Bearer private"})
        self.assertIsNone(NoRedirect().redirect_request(request, None, 302, "", {}, "https://unrelated.example"))

    def test_token_file_requires_private_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review-token"
            path.write_text("private-token\n")
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                private_token(path)
            path.chmod(0o600)
            self.assertEqual(private_token(path), "private-token")

    def test_wrong_organization_stops_before_analytics(self):
        class WrongOrganization:
            def __init__(self):
                self.calls = []

            def start(self):
                return {"protocolVersion": "2025-03-26"}

            def exchange(self, method):
                return {"tools": []}

            def call(self, name, arguments=None):
                self.calls.append(name)
                return {"ok": True, "data": {"organizationId": "wrong-org"}}

        client = WrongOrganization()
        results = run(client, "review-org", "review-app", [])
        self.assertEqual(client.calls, ["setup_get_status"])
        self.assertEqual(results[-1]["status"], "failed")

    def test_write_tool_is_rejected_before_network_access(self):
        client = Client("https://fusionmetrics.com", "private")
        with self.assertRaises(ValueError):
            client.call("ga4_import_attribution", {"appKey": "review-app"})

    def test_missing_scope_tool_list_cannot_pass(self):
        self.assertFalse(valid_tools([]))
        self.assertFalse(valid_tools([{"name": "run_sql", "title": "Query", "annotations": {}}]))


if __name__ == "__main__":
    unittest.main()
