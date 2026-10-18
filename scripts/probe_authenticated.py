"""Run bounded, read-only MCP checks with an existing reviewer OAuth grant.

This is an operator probe, not evidence of assistant prompts or native-client UX.
It never obtains credentials, approves OAuth, changes readiness, or submits a plugin.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from probe_public import ORIGINS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "2025-03-26"
ANALYTICS = {"list_apps", "select_app", "describe_schema", "run_sql"}
WRITES = {"setup_request_credential_entry", "setup_discover_apps", "setup_configure_app",
          "setup_retry_import", "setup_get_capture_installation", "setup_mark_capture_prepared",
          "ga4_configure_dataset", "ga4_import_attribution"}
READS = ANALYTICS | {"setup_get_instructions", "setup_get_status", "ga4_get_status"}
REPLACES = {"setup_configure_app", "setup_mark_capture_prepared", "ga4_configure_dataset"}
EXTERNAL = {"setup_discover_apps", "setup_configure_app", "setup_retry_import",
            "ga4_configure_dataset", "ga4_import_attribution"}
QUERY = ("SELECT CAST(MIN(bucket_start) AS VARCHAR) AS first_day, "
         "CAST(MAX(bucket_start) AS VARCHAR) AS last_day, CAST(COUNT(*) AS INTEGER) AS points, "
         "CAST(MAX(summary_current) AS DOUBLE) AS closing_mrr "
         "FROM range_metrics WHERE metric_key = 'mrr' AND range_key = 'last_30_days'")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward a reviewer bearer token to a redirect target.
        return None


class ProbeFailure(Exception):
    def __init__(self, reason, status):
        super().__init__(reason)
        self.reason, self.status = reason, status


def private_token(path):
    path = path.resolve()
    if path.is_relative_to(ROOT) or path.stat().st_mode & 0o077:
        raise ValueError("Token files must be outside this repository and readable only by their owner.")
    token = path.read_text().strip()
    if not token or any(char.isspace() for char in token):
        raise ValueError("Expected one bearer token in the private file.")
    return token


def envelope(result):
    value = result.get("structuredContent")
    if value is None:
        blocks = result.get("content", [])
        texts = [block["text"] for block in blocks if block.get("type") == "text"]
        if len(texts) != 1:
            raise ValueError("Expected one JSON tool envelope.")
        value = json.loads(texts[0])
    if not isinstance(value, dict) or not isinstance(value.get("ok"), bool):
        raise ValueError("Missing explicit tool outcome.")
    if result.get("isError") is True and value["ok"]:
        raise ValueError("Conflicting tool outcomes.")
    return value


def valid_tools(items):
    if len(items) != 15 or {tool.get("name") for tool in items} != READS | WRITES:
        return False
    for tool in items:
        name = tool["name"]
        expected = {"readOnlyHint": name in READS, "destructiveHint": name in REPLACES,
                    "idempotentHint": True, "openWorldHint": name in EXTERNAL}
        actual = tool.get("annotations", {})
        if not tool.get("title") or any(actual.get(key) is not value for key, value in expected.items()):
            return False
    return True


class Client:
    def __init__(self, origin, token):
        self.origin, self.token, self.session, self.sequence = origin, token, None, 0
        self.opener = build_opener(NoRedirect())

    def exchange(self, method, params=None, notification=False, http_method="POST"):
        self.sequence += 1
        payload = {"jsonrpc": "2.0", "method": method}
        if not notification:
            payload["id"] = self.sequence
        if params is not None:
            payload["params"] = params
        headers = {"Authorization": "Bearer " + self.token, "Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": PROTOCOL}
        if self.session:
            headers["MCP-Session-Id"] = self.session
        request = Request(self.origin + "/api/mcp", headers=headers, method=http_method,
                          data=json.dumps(payload).encode() if http_method == "POST" else None)
        try:
            response = self.opener.open(request, timeout=90)
        except HTTPError as error:
            # Do not include response bodies or request headers in exceptions/logs.
            raise ProbeFailure("mcp-http", error.code) from None
        with response:
            self.session = response.headers.get("MCP-Session-Id") or self.session
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError("MCP response exceeded probe limit.")
            if not raw:
                return {}
            value = json.loads(raw)
            if "error" in value:
                raise ValueError("JSON-RPC request was rejected.")
            return value.get("result", {})

    def start(self):
        result = self.exchange("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
            "clientInfo": {"name": "fusionmetrics-review-probe", "version": "0.2.1"}})
        if not self.session:
            raise ValueError("Server did not create an MCP session.")
        self.exchange("notifications/initialized", notification=True)
        return result

    def call(self, name, arguments=None):
        if name not in READS:
            raise ValueError("This probe cannot invoke setup or GA4 mutations.")
        return envelope(self.exchange("tools/call", {"name": name, "arguments": arguments or {}}))


def run(client, expected_org, app_key, expected_rows, checks=None):
    if checks is None:
        checks = []

    def record(name, passed, evidence):
        checks.append({"check": name, "status": "passed" if passed else "failed", "evidence": evidence})

    init = client.start()
    record("initialize", init.get("protocolVersion") == PROTOCOL, init)
    tools = client.exchange("tools/list").get("tools", [])
    record("fifteen-tools-and-annotations", valid_tools(tools), tools)
    state = client.call("setup_get_status")
    matches = state.get("ok") and state.get("data", {}).get("organizationId") == expected_org
    record("reviewer-organization", bool(matches), {"matches_expected": bool(matches)})
    if not matches:
        return checks  # Do not query an unintended Organization's business data.
    record("setup-status", state["ok"], state)
    apps = client.call("list_apps")
    found = apps.get("ok") and any(app.get("key") == app_key for app in apps.get("data", {}).get("apps", []))
    record("reviewer-app-available", bool(found), apps)
    if not found:
        return checks
    selected = client.call("select_app", {"appKey": app_key})
    record("select-app", selected["ok"], selected)
    if not selected["ok"]:
        return checks
    schema = client.call("describe_schema")
    record("describe-schema", schema["ok"] and bool(schema.get("data", {}).get("metricDefinitions")), schema)
    totals = client.call("run_sql", {"sql": QUERY, "maxRows": 10})
    record("recorded-fixture-totals", totals["ok"] and totals.get("data", {}).get("rows") == expected_rows, totals)
    ga4 = client.call("ga4_get_status", {"appKey": app_key})
    record("ga4-status-not-import-completion", ga4["ok"], ga4)
    for name, sql in (
        ("reject-write-sql", "CREATE TEMP TABLE __fusionmetrics_review_probe (value INTEGER)"),
        ("reject-file-functions", "SELECT * FROM read_csv_auto('/nonexistent/fusionmetrics-review-probe.csv')"),
    ):
        result = client.call("run_sql", {"sql": sql})
        record(name, result.get("ok") is False and result.get("error", {}).get("code") == "invalid_sql", result)
    missing = client.call("select_app", {"appKey": "app-plugin-review-inaccessible-20261018"})
    record("reject-unknown-app-not-cross-org-proof", missing.get("ok") is False and
           missing.get("error", {}).get("code") == "app_not_found", missing)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", choices=ORIGINS, default="production")
    parser.add_argument("--access-token-file", required=True, type=Path)
    parser.add_argument("--fixture-file", required=True, type=Path,
                        help="Private JSON with organizationId, appKey, expectedRows, expectedSha and pluginCommit")
    parser.add_argument("--output", required=True, type=Path, help="New private report outside this repository")
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT):
        parser.error("Evidence must stay outside the public repository.")
    fixture = json.loads(args.fixture_file.read_text())
    if not re.fullmatch(r"[0-9a-f]{40}", fixture.get("expectedSha", "")):
        parser.error("Fixture must pin the full deployed revision.")
    origin = ORIGINS[args.environment][0]
    client = Client(origin, private_token(args.access_token_file))
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "origin": origin,
              "plugin_commit": fixture.get("pluginCommit"), "checks": [], "limitations": [
                  "Operator protocol probe, not native-client or assistant prompt evidence",
                  "No setup writes, real GA4 import, listing edits, revocation, legacy parity or cross-Organization test",
                  "No readiness gates changed; contains private fixture evidence"]}
    try:
        with client.opener.open(origin + "/healthz", timeout=20) as response:
            health = json.load(response)
        matches = health.get("deployedSha") == fixture["expectedSha"] and health.get("ok") is True
        report["checks"].append({"check": "deployed-revision", "status": "passed" if matches else "failed", "evidence": health})
        if matches:
            run(client, fixture["organizationId"], fixture["appKey"], fixture["expectedRows"], report["checks"])
    except Exception as error:
        evidence = {"error_type": type(error).__name__}
        if isinstance(error, ProbeFailure):
            evidence.update(reason=error.reason, http_status=error.status)
        report["checks"].append({"check": "probe-execution", "status": "failed", "evidence": evidence})
    finally:
        if client.session:
            try:
                client.exchange("", http_method="DELETE")
            except Exception:
                report["limitations"].append("Session cleanup failed; server expiry still applies.")
    report["passed"] = len(report["checks"]) == 13 and all(check["status"] == "passed" for check in report["checks"])
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"passed": report["passed"], "checks": [
        {"check": check["check"], "status": check["status"]} for check in report["checks"]]}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
