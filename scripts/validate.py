"""Validate the public distribution, without network access or third-party packages."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCOPES = ["openid", "user:org:read", "setup:read", "setup:write", "analytics:read"]
SKILLS = {"get-started", "analytics", "setup", "optimize-listing", "ga4-bigquery"}
PLUGIN_FILES = {
    "plugin.json", "mcp.json", ".mcp.json", ".claude-mcp.json",
    ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", ".cursor-plugin/plugin.json",
    "skills/setup/SKILL.md", "README.md", "SUPPORT.md", "LICENSE", "assets/logo.svg",
    "skills/get-started/SKILL.md", "skills/analytics/SKILL.md", "skills/ga4-bigquery/SKILL.md",
    "skills/ga4-bigquery/references/browser-setup.md", "skills/optimize-listing/SKILL.md",
    "skills/optimize-listing/references/analytics.md", "skills/optimize-listing/references/traffic-quality.md",
    "skills/optimize-listing/references/live-experiment.md", "skills/optimize-listing/references/listing-baseline.schema.json",
    "skills/optimize-listing/references/experiment.schema.json", "skills/optimize-listing/scripts/validate_artifacts.py",
}
REPO_FILES = {
    ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json",
    ".github/workflows/validate.yml", ".gitignore", "README.md", "LICENSE",
    "docs/publication.md", "docs/submission-packet.md", "readiness.json", "openai-connection.json", "scripts/validate.py",
    "scripts/package.py", "scripts/test_package.py", "scripts/probe_public.py", "scripts/test_probe_public.py",
}
GATES = {
    "publisher-and-portal-access", "hosted-service-terms-and-privacy-review",
    "production-client-oauth-and-scopes", "organization-permissions-and-revocation",
    "tool-titles-and-annotations", "reviewer-account-and-seeded-data",
    "five-positive-three-negative-live-tests", "review-demo-recording",
    "scanner-reachability-and-domain-verification", "claude-portal-validation-and-connector-pairing",
    "compatible-hosted-runtime", "analytics-parity-and-migration", "listing-and-ga4-browser-workflows",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


def public_url(value):
    url = urlsplit(value)
    require(url.scheme == "https" and url.hostname and not url.username and not url.password
            and not url.query and not url.fragment, f"Invalid public URL: {value}")


def local_reference(root, reference):
    require(reference.startswith("./") and ".." not in Path(reference).parts,
            f"Unsafe plugin path: {reference}")
    path = root / reference
    require(path.resolve().is_relative_to(root.resolve()) and path.exists(), f"Missing or escaped path: {reference}")


def validate(root=ROOT, submission_ready=False):
    root = Path(root)
    marketplace = read_json(root / ".agents/plugins/marketplace.json")
    require(len(marketplace["plugins"]) == 1, "Expected exactly one plugin")
    entry = marketplace["plugins"][0]
    name = entry["name"]
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), "Invalid plugin name")
    relative = f"plugins/{name}"
    require(entry["source"] == {"source": "local", "path": f"./{relative}"}, "Invalid Codex marketplace source")
    require(entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "Invalid marketplace policy")
    claude_marketplace = read_json(root / ".claude-plugin/marketplace.json")
    require(claude_marketplace["name"] == marketplace["name"], "Marketplace identities differ")
    require(len(claude_marketplace["plugins"]) == 1 and claude_marketplace["plugins"][0]["source"] == f"./{relative}", "Invalid Claude source")
    allowed = REPO_FILES | {f"{relative}/{file}" for file in PLUGIN_FILES}
    found = set()
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if rel.parts[0] in {".git", "dist"} or "__pycache__" in rel.parts:
            continue
        require(not path.is_symlink(), f"Symlinks are not allowed: {rel}")
        if not path.is_file():
            continue
        require(rel.as_posix() in allowed, f"Unexpected distribution file: {rel}")
        found.add(rel.as_posix())
        require(path.stat().st_size < 256 * 1024, f"Oversized file: {rel}")
        content = path.read_text()
        # Patterns intentionally do not match ordinary documentation about credentials.
        require(not re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:gh[pousr]_[A-Za-z0-9]{20,})|(?:sk_live_[A-Za-z0-9]{16,})|Bearer\s+[A-Za-z0-9._-]{24,}", content), f"Possible credential: {rel}")
        if path.suffix == ".json":
            json.loads(content)
    require(found == allowed, f"Missing distribution files: {sorted(allowed - found)}")
    plugin = root / relative
    manifest = read_json(plugin / "plugin.json")
    require(manifest["name"] == name and re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), "Invalid identity/version")
    require(manifest["license"] == "MIT", "Expected MIT plugin license")
    require(manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "Invalid plugin schema")
    require((plugin / "LICENSE").read_text() == (root / "LICENSE").read_text(), "License copies differ")
    if "repository" in manifest:
        public_url(manifest["repository"])
    extension = manifest["extensions"]["com.openai"]
    interface = extension["interface"]
    for field, limit in {"displayName": 30, "shortDescription": 30, "developerName": 80, "longDescription": 4000}.items():
        require(0 < len(interface[field]) <= limit, f"Invalid {field} length")
    for field in ("websiteURL", "supportURL", "privacyPolicyURL"):
        public_url(interface[field])
    for reference in (extension["onboardingSkill"], interface["logo"], interface["composerIcon"]):
        local_reference(plugin, reference)
    svg = ET.fromstring((plugin / "assets/logo.svg").read_text())
    require(svg.attrib["viewBox"] == "0 0 512 512", "Expected square 512px artwork")
    require(not any(tag.tag.split("}")[-1] in {"script", "foreignObject"} for tag in svg.iter()), "Executable SVG content")
    skill = (plugin / "skills/setup/SKILL.md").read_text()
    require(skill.startswith("---\nname: setup\ndescription: ") and "setup_get_instructions" in skill and "setup_get_status" in skill, "Invalid setup skill")
    require(extension["onboardingSkill"] == "./skills/get-started/SKILL.md", "Invalid entry skill")
    for skill_name in SKILLS:
        directory = plugin / "skills" / skill_name
        content = (directory / "SKILL.md").read_text()
        require(content.startswith(f"---\nname: {skill_name}\ndescription: "), f"Invalid skill metadata: {skill_name}")
        require("{{" not in content, f"Unresolved skill template: {skill_name}")
        for reference in re.findall(r"\]\(([^)]+)\)", content):
            if not urlsplit(reference).scheme and not reference.startswith("#"):
                path = (directory / reference.split("#")[0]).resolve()
                require(path.is_relative_to(plugin.resolve()) and path.is_file(), f"Broken skill reference: {skill_name}/{reference}")
    require(len(re.sub(r"```.*?```", "", (plugin / "README.md").read_text(), flags=re.S).split()) >= 40, "Plugin README needs at least 40 words")
    portable = read_json(plugin / "mcp.json")
    require(portable["$schema"] == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "Invalid MCP schema")
    require(set(portable["mcpServers"]) == {name}, "Unexpected MCP servers")
    server = portable["mcpServers"][name]
    endpoint = server["url"]
    public_url(endpoint)
    require(server == {"type": "streamable-http", "url": endpoint}, "Portable MCP config must remain URL-only")
    connection = read_json(root / "openai-connection.json")
    require(connection["url"] == endpoint and connection["auth"] == {
        "type": "oauth", "client": {"mode": "dcr"}, "resource": endpoint,
        "baseScopes": SCOPES, "defaultScopes": SCOPES,
    }, "OpenAI submission connection settings differ from the full plugin scope policy")
    require(read_json(plugin / ".mcp.json") == {"mcpServers": {name: {"type": "http", "url": endpoint}}}, "Legacy MCP mismatch")
    require(read_json(plugin / ".claude-mcp.json") == {"mcpServers": {name: {"type": "http", "url": endpoint, "oauth": {"scopes": " ".join(SCOPES)}}}}, "Claude endpoint/scopes mismatch")
    for host in ("codex", "claude", "cursor"):
        compatibility = read_json(plugin / f".{host}-plugin/plugin.json")
        for field in ("name", "version", "license", "description", "author", "homepage", "repository"):
            require(compatibility.get(field) == manifest.get(field), f"{host} manifest differs: {field}")
        local_reference(plugin, compatibility["skills"])
        local_reference(plugin, compatibility["mcpServers"])
        expected = "./.claude-mcp.json" if host == "claude" else "./.mcp.json"
        require(compatibility["mcpServers"] == expected, f"Wrong MCP file for {host}")
    cases = extension["review"]["test_cases"]
    require(len(cases["positive"]) >= 5 and len(cases["negative"]) >= 3, "Need five positive and three negative review cases")
    readiness = read_json(root / "readiness.json")
    require({gate["id"] for gate in readiness["gates"]} == GATES and len(readiness["gates"]) == len(GATES), "Readiness gates missing or duplicated")
    pending = [gate["id"] for gate in readiness["gates"] if gate["status"] != "verified" or not gate["evidence"].strip()]
    if submission_ready:
        require(name == "fusionmetrics" and endpoint == "https://fusionmetrics.com/api/mcp", "Public submission requires the production endpoint")
        require(not pending, f"Unverified submission gates: {', '.join(pending)}")
        public_url(interface.get("termsOfServiceURL", ""))
        public_url(extension["review"].get("demo_recording_url", ""))
        require(manifest.get("repository"), "Missing publication repository")
    return plugin, manifest, pending


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission-ready", action="store_true")
    args = parser.parse_args()
    try:
        plugin, manifest, pending = validate(submission_ready=args.submission_ready)
        print(f"Package valid: {manifest['name']} {manifest['version']}. {len(pending)} live submission gates pending. Nothing submitted.")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Validation failed: {error}\n")
