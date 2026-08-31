import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
build_site = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_site)


class SiteTests(unittest.TestCase):
    def test_render_uses_snapshot_projects_and_evidence_link(self):
        snapshot = {
            "generated_at": "2026-08-25T05:00:00Z",
            "source": {"base_url": "https://opensource.unicc.org", "group": "un/unece/uncefact"},
            "projects": [{
                "name": "Example",
                "path_with_namespace": "un/unece/uncefact/example",
                "web_url": "https://opensource.unicc.org/un/unece/uncefact/example",
                "default_branch": "main",
                "archived": False,
                "last_activity_at": "2026-08-24T12:00:00Z",
                "topics": ["trade"],
                "description": "Example project",
            }],
        }
        html = build_site.render(snapshot)
        self.assertIn("Example", html)
        self.assertIn("un/unece/uncefact/example", html)
        self.assertIn("portfolio.json", html)
        self.assertIn("not an aggregate assurance score", html.lower())
        self.assertNotIn("prefers-color-scheme:dark", html)

    def test_render_changes_exposes_human_detail_and_raw_evidence(self):
        changes = {
            "previous_generated_at": "2026-08-24T05:00:00Z",
            "current_generated_at": "2026-08-25T05:00:00Z",
            "summary": {"added": 0, "removed": 0, "changed": 1, "activity_advanced": 1},
            "changed": [{
                "path_with_namespace": "un/unece/uncefact/example",
                "fields": {"visibility": {"before": None, "after": "public"}},
            }],
            "activity_advanced": [{
                "path_with_namespace": "un/unece/uncefact/example",
                "before": "2026-08-24T12:00:00Z",
                "after": "2026-08-25T12:00:00Z",
            }],
        }
        html = build_site.render_changes(changes)
        self.assertIn("Observed portfolio changes", html)
        self.assertIn("changes.json", html)
        self.assertIn("visibility", html)
        self.assertIn("null", html)
        self.assertIn("public", html)
        self.assertIn("Activity advancements", html)
        self.assertNotIn("prefers-color-scheme:dark", html)

    def test_main_preserves_canonical_changes_json_and_adds_html(self):
        snapshot = {
            "generated_at": "2026-08-25T05:00:00Z",
            "source": {"base_url": "https://example.test", "group": "un/unece/uncefact"},
            "projects": [],
        }
        changes = {
            "schema_version": "1",
            "summary": {"added": 0, "removed": 0, "changed": 0, "activity_advanced": 0},
            "added": [], "removed": [], "changed": [], "activity_advanced": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            portfolio_path = root / "portfolio.json"
            changes_path = root / "input-changes.json"
            output = root / "site"
            portfolio_path.write_text(json.dumps(snapshot), encoding="utf-8")
            changes_path.write_text(json.dumps(changes), encoding="utf-8")
            argv = [
                "build_site.py", "--input", str(portfolio_path), "--changes", str(changes_path),
                "--impacts", str(root / "missing-impacts.json"),
                "--lifecycle", str(root / "missing-lifecycle.json"),
                "--external", str(root / "missing-external.json"),
                "--output-dir", str(output),
            ]
            with patch("sys.argv", argv):
                self.assertEqual(build_site.main(), 0)
            self.assertEqual(json.loads((output / "changes.json").read_text(encoding="utf-8")), changes)
            self.assertIn("Observed portfolio changes", (output / "changes.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
