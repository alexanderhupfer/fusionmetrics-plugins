"""Probe public submission prerequisites without credentials or service mutations."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from validate import SCOPES

ORIGINS = {
    "production": ("https://fusionmetrics.com", "https://clerk.fusionmetrics.com"),
    "staging": ("https://staging.fusionmetrics.com", "https://clerk.staging.fusionmetrics.com"),
}


def fetch(url):
    request = Request(url, headers={"User-Agent": "Fusionmetrics-Plugin-Readiness/0.2.1"})
    try:
        response = urlopen(request, timeout=20)
    except HTTPError as error:
        response = error
    with response:
        return response.status, dict(response.headers.items()), response.read(512 * 1024).decode("utf-8", errors="replace"), response.geturl()


def probe(environment="production", expected_sha=None, expected_challenge=None, get=fetch):
    origin, issuer = ORIGINS[environment]
    endpoint = origin + "/api/mcp"
    checks = []

    def check(name, passed, detail):
        checks.append({"check": name, "status": "passed" if passed else "failed", "detail": detail})

    def response(path, base=origin):
        try:
            return get(base + path)
        except (OSError, URLError, ValueError) as error:
            check("reachability:" + path, False, type(error).__name__)
            return 0, {}, "", ""

    def document(path, base=origin):
        status, _, body, final_url = response(path, base)
        if status != 200 or final_url != base + path:
            check("metadata:" + path, False, f"HTTP {status}; exact URL: {final_url == base + path}")
            return {}
        try:
            value = json.loads(body)
            if not isinstance(value, dict):
                raise ValueError("Expected object")
            return value
        except (ValueError, TypeError):
            check("metadata:" + path, False, "Expected a JSON object")
            return {}

    health = document("/healthz")
    sha = health.get("deployedSha")
    check("service-health", health.get("ok") is True, "Healthy hosted service" if health.get("ok") else "Health unavailable")
    check("deployed-revision", bool(sha and re.fullmatch(r"[0-9a-f]{40}", str(sha))) and (not expected_sha or sha == expected_sha),
          {"observed": sha, "expected": expected_sha, "compatibility_verified": bool(expected_sha and sha == expected_sha)})
    resource = document("/.well-known/oauth-protected-resource/api/mcp")
    check("resource-identity", resource.get("resource") == endpoint, {"expected": endpoint, "observed": resource.get("resource")})
    check("authorization-server", resource.get("authorization_servers") == [issuer], {"expected": issuer, "observed": resource.get("authorization_servers")})
    missing = sorted(set(SCOPES) - set(resource.get("scopes_supported", [])))
    check("resource-scopes", not missing, {"missing": missing})
    # Only fetch the expected issuer, never an arbitrary URL from remote metadata.
    auth = document("/.well-known/oauth-authorization-server", issuer)
    missing = sorted(set(SCOPES) - set(auth.get("scopes_supported", [])))
    check("issuer-scopes", not missing, {"missing": missing})
    for key in ("authorization_endpoint", "token_endpoint", "registration_endpoint"):
        value = auth.get(key, "")
        check(key, isinstance(value, str) and value.startswith(issuer + "/"), value)
    check("pkce", "S256" in auth.get("code_challenge_methods_supported", []), "S256 required")
    status, headers, _, final_url = response("/api/mcp")
    challenge = next((value for key, value in headers.items() if key.lower() == "www-authenticate"), "")
    check("unauthenticated-mcp", status == 401 and final_url == endpoint and
          f'resource_metadata="{origin}/.well-known/oauth-protected-resource/api/mcp"' in challenge,
          {"status": status, "resource_metadata_advertised": "resource_metadata=" in challenge})
    for path, marker in (("/terms", "Terms of Service"), ("/privacy", "Hosted analytics and agent connections")):
        status, _, body, final_url = response(path)
        check("public-page:" + path, status == 200 and final_url.rstrip("/") == origin + path and marker in body,
              {"status": status, "expected_content_found": marker in body})
    if expected_challenge:
        status, _, body, final_url = response("/.well-known/openai-apps-challenge")
        check("openai-domain-challenge", status == 200 and body.strip() == expected_challenge and
              final_url == origin + "/.well-known/openai-apps-challenge", "Compared exact portal-supplied value; value omitted from report")
    else:
        checks.append({"check": "openai-domain-challenge", "status": "not_run", "detail": "Supply the actual portal challenge after it is issued."})
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(), "environment": environment,
        "endpoint": endpoint, "passed": all(item["status"] == "passed" for item in checks),
        "limitations": ["No authenticated tool scan or reviewer tests", "Shell reachability does not prove portal scanner reachability",
                        "No service compatibility claim unless the expected release SHA is supplied", "No readiness gates are updated"],
        "checks": checks,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", choices=ORIGINS, default="production")
    parser.add_argument("--expected-sha")
    parser.add_argument("--expected-challenge", help="Actual public domain-verification value supplied by OpenAI")
    parser.add_argument("--output", type=Path, help="Write a new report outside the public repository")
    args = parser.parse_args()
    if args.expected_sha and not re.fullmatch(r"[0-9a-f]{40}", args.expected_sha):
        parser.error("Expected SHA must be a full 40-character commit")
    report = probe(args.environment, args.expected_sha, args.expected_challenge)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(rendered)
    print(rendered, end="")
    raise SystemExit(0 if report["passed"] else 1)
