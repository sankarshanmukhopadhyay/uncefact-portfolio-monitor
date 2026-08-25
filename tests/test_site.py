import importlib.util
from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
