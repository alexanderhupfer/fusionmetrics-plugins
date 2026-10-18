"""Exercise credential containment, archive layout, scopes, and readiness failures."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from zipfile import ZipFile

from package import build
from validate import PLUGIN_FILES, ROOT, SCOPES, validate


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
        self.plugin, self.manifest, _ = validate(self.root)

    def test_archive_is_reproducible_and_scoped(self):
        archive = build(self.root)
        first = archive.read_bytes()
        self.assertEqual(first, build(self.root).read_bytes())
        with ZipFile(archive) as bundle:
            self.assertEqual(set(bundle.namelist()), PLUGIN_FILES)
            server = json.loads(bundle.read("mcp.json"))["mcpServers"][self.manifest["name"]]
            auth = server["extensions"]["com.openai"]["auth"]
            self.assertEqual(auth["baseScopes"], SCOPES)
            self.assertEqual(auth["defaultScopes"], SCOPES)
            self.assertEqual(auth["resource"], server["url"])
        source = json.loads((self.plugin / "mcp.json").read_text())
        self.assertNotIn("extensions", source["mcpServers"][self.manifest["name"]])

    def test_unexpected_file_is_not_packaged(self):
        (self.plugin / ".env").write_text("PRIVATE_CONFIGURATION=yes")
        with self.assertRaisesRegex(ValueError, "Unexpected distribution file"):
            build(self.root)

    def test_symlink_cannot_import_private_content(self):
        path = self.plugin / "SUPPORT.md"
        path.unlink()
        path.symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            build(self.root)

    def test_known_credential_is_rejected(self):
        (self.plugin / "README.md").write_text("ghp_" + "x" * 36)
        with self.assertRaisesRegex(ValueError, "Possible credential"):
            build(self.root)

    def test_manifest_cannot_escape_plugin(self):
        path = self.plugin / "plugin.json"
        manifest = json.loads(path.read_text())
        manifest["extensions"]["com.openai"]["interface"]["logo"] = "./../../README.md"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Unsafe plugin path"):
            build(self.root)

    def test_readiness_cannot_pass_with_no_evidence(self):
        with self.assertRaisesRegex(ValueError, "Unverified submission gates|production endpoint"):
            validate(self.root, submission_ready=True)


if __name__ == "__main__":
    unittest.main()
