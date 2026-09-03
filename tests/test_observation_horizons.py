import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_observation_horizons", ROOT / "scripts" / "build_observation_horizons.py"
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class ObservationHorizonTests(unittest.TestCase):
    def snapshot(self):
        return {
            "generated_at": "2026-09-03T01:00:00Z",
            "projects": [
                {
                    "name": "September project",
                    "path_with_namespace": "un/unece/uncefact/september",
                    "web_url": "https://example.test/september",
                    "last_activity_at": "2026-09-02T12:00:00Z",
                },
                {
                    "name": "August project",
                    "path_with_namespace": "un/unece/uncefact/august",
                    "web_url": "https://example.test/august",
                    "last_activity_at": "2026-08-20T12:00:00Z",
                },
                {
                    "name": "Old project",
                    "path_with_namespace": "un/unece/uncefact/old",
                    "web_url": "https://example.test/old",
                    "last_activity_at": "2026-01-10T12:00:00Z",
                },
                {
                    "name": "Bad timestamp",
                    "path_with_namespace": "un/unece/uncefact/bad",
                    "web_url": "https://example.test/bad",
                    "last_activity_at": "not-a-date",
                },
            ],
        }

    def test_month_and_trailing_horizons_use_observed_timestamp(self):
        data = module.build_horizons(self.snapshot())
        month, trailing = data["horizons"]
        self.assertEqual(month["start"], "2026-09-01T00:00:00Z")
        self.assertEqual(month["end"], "2026-09-03T01:00:00Z")
        self.assertEqual(month["project_count"], 1)
        self.assertEqual(month["projects"][0]["name"], "September project")
        self.assertEqual(trailing["project_count"], 2)
        self.assertEqual([p["name"] for p in trailing["projects"]], ["September project", "August project"])

    def test_render_escapes_project_content_and_explains_boundary(self):
        snapshot = self.snapshot()
        snapshot["projects"][0]["name"] = "<script>alert(1)</script>"
        html = module.render_horizons(module.build_horizons(snapshot))
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("not counts of normative changes", html)
        self.assertIn("observation-horizons.json", html)

    def test_homepage_fragment_distinguishes_latest_window(self):
        data = module.build_horizons(self.snapshot())
        fragment = module.homepage_fragment(data)
        self.assertIn("latest evidence window remains", fragment.lower())
        self.assertIn("Month to observed date", fragment)
        self.assertIn("Trailing 90 days", fragment)
        self.assertIn("last_activity_at", fragment)

    def test_inject_homepage_places_horizons_before_reading_guidance(self):
        html = "<h2>Current observation</h2><p>latest</p><h2>How to read this monitor</h2>"
        result = module.inject_homepage(html, "<h2>Observation horizons</h2>")
        self.assertLess(result.index("Observation horizons"), result.index("How to read this monitor"))

    def test_invalid_observation_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            module.build_horizons({"generated_at": "bad", "projects": []})


if __name__ == "__main__":
    unittest.main()
