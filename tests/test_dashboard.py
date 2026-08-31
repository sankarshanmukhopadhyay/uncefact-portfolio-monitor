import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
build_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_site)


class DashboardTests(unittest.TestCase):
    def test_dashboard_surfaces_v1_evidence_layers(self):
        snapshot = {
            "generated_at": "2026-08-25T05:00:00Z",
            "source": {"base_url": "https://example.test", "group": "un/unece/uncefact"},
            "projects": [{"name": "Spec", "path_with_namespace": "un/unece/uncefact/spec", "web_url": "https://example.test/spec", "default_branch": "main", "archived": False, "last_activity_at": "2026-08-25T04:00:00Z", "topics": []}],
        }
        changes = {"summary": {"added": 1, "removed": 0, "changed": 2}}
        impacts = {"summary": {"review_obligations": 3}}
        lifecycle = {"summary": {"active": 4, "resolved": 5}}
        external = {"dependency_count": 6}
        html = build_site.render(snapshot, changes, impacts, lifecycle, external)
        self.assertIn("Structural changes</span><strong>3", html)
        self.assertIn("Review obligations</span><strong>3", html)
        self.assertIn("Active findings</span><strong>4", html)
        self.assertIn("External dependencies</span><strong>6", html)
        for href in ["changes.html", "relationships.html", "impacts.html", "findings.html", "external-dependencies.html", "weekly-report.html"]:
            self.assertIn(f'href="{href}"', html)
        self.assertIn("not an aggregate assurance score", html)
        self.assertIn("Current observation", html)
        self.assertIn("Direct review queue", html)
        self.assertIn("How to read this monitor", html)
        self.assertNotIn("prefers-color-scheme:dark", html)


if __name__ == "__main__":
    unittest.main()
