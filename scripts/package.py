"""Build a deterministic OpenAI candidate ZIP. Never submit or release it."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from validate import PLUGIN_FILES, ROOT, SCOPES, validate


def build(root=ROOT, submission_ready=False):
    root = Path(root)
    plugin, manifest, _ = validate(root, submission_ready)
    output = root / "dist"
    if output.is_symlink():
        raise ValueError("Output directory must not be a symlink")
    output.mkdir(exist_ok=True)
    archive = output / f"{manifest['name']}-{manifest['version']}-openai-candidate.zip"
    if archive.is_symlink() or archive.with_suffix(".zip.sha256").is_symlink():
        raise ValueError("Output files must not be symlinks")
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        for relative in sorted(PLUGIN_FILES):
            data = (plugin / relative).read_bytes()
            if relative == "mcp.json":
                config = json.loads(data)
                server = config["mcpServers"][manifest["name"]]
                server["extensions"] = {"com.openai": {"auth": {
                    "type": "oauth", "client": {"mode": "dcr"}, "resource": server["url"],
                    "baseScopes": SCOPES, "defaultScopes": SCOPES,
                }}}
                data = (json.dumps(config, indent=2) + "\n").encode()
            entry = ZipInfo(relative, date_time=(2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = ZIP_DEFLATED
            zip_file.writestr(entry, data)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission-ready", action="store_true")
    args = parser.parse_args()
    try:
        print(f"Built {build(submission_ready=args.submission_ready)}. Nothing submitted.")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Build failed: {error}\n")
