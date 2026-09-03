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
                    "web_url": "https://github.com/example/september",
                    "last_activity_at": "2026-09-02T12:00:00Z",
                },
                {
                    "name": "August project",
                    "path_with_namespace": "un/unece/uncefact/august",
                    "web_url": "https://gitlab.example.org/un/august",
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

    def test_evidence_index_maps_both_sides_of_review_and_findings(self):
        changes = {
            "changed": [{"path_with_namespace": "un/unece/uncefact/september"}],
            "activity_advanced": [{"path_with_namespace": "un/unece/uncefact/august"}],
        }
        impacts = {
            "review_obligations": [{
                "review_project": "un/unece/uncefact/september",
                "changed_project": "un/unece/uncefact/dependency",
            }]
        }
        findings = {
            "findings": [{
                "subject_project": "un/unece/uncefact/reviewer",
                "dependency_project": "un/unece/uncefact/september",
            }]
        }
        index = module.build_evidence_index(changes, impacts, findings)
        self.assertEqual(index["un/unece/uncefact/september"], {"changes", "impacts", "findings"})
        self.assertEqual(index["un/unece/uncefact/august"], {"changes"})
        self.assertEqual(index["un/unece/uncefact/dependency"], {"impacts"})
        self.assertEqual(index["un/unece/uncefact/reviewer"], {"findings"})

    def test_commit_history_urls_follow_repository_host(self):
        self.assertEqual(
            module._commit_history_url("https://github.com/example/project"),
            "https://github.com/example/project/commits",
        )
        self.assertEqual(
            module._commit_history_url("https://gitlab.example.org/group/project"),
            "https://gitlab.example.org/group/project/-/commits",
        )
        self.assertEqual(
            module._commit_history_url("https://example.test/project"),
            "https://example.test/project",
        )

    def test_render_links_project_to_supported_current_window_evidence(self):
        data = module.build_horizons(self.snapshot())
        # August remains in the broad horizon but deliberately has no current-window evidence.
        index = {
            "un/unece/uncefact/september": {"changes", "impacts", "findings"},
        }
        html = module.render_horizons(data, index)
        self.assertIn('href="changes.html"', html)
        self.assertIn('href="impacts.html"', html)
        self.assertIn('href="findings.html"', html)
        self.assertIn("No current-window finding or review.", html)
        self.assertIn("Inspect recent commits", html)
        self.assertIn("https://gitlab.example.org/un/august/-/commits", html)
        self.assertIn("commit-history link is only an", html)
        self.assertIn('href="#month-to-observed-date-projects"', html)

    def test_render_escapes_project_content_and_explains_boundary(self):
        snapshot = self.snapshot()
        snapshot["projects"][0]["name"] = "<script>alert(1)</script>"
        html = module.render_horizons(module.build_horizons(snapshot))
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("not counts of normative changes", html)
        self.assertIn("observation-horizons.json", html)

    def test_homepage_fragment_distinguishes_latest_window_and_links_evidence(self):
        data = module.build_horizons(self.snapshot())
        fragment = module.homepage_fragment(data)
        self.assertIn("latest evidence window remains", fragment.lower())
        self.assertIn("Month to observed date", fragment)
        self.assertIn("Trailing 90 days", fragment)
        self.assertIn("last_activity_at", fragment)
        self.assertIn("findings.html", fragment)
        self.assertIn("impacts.html", fragment)
        self.assertIn("#month-to-observed-date", fragment)

    def test_inject_homepage_places_horizons_before_reading_guidance(self):
        html = "<h2>Current observation</h2><p>latest</p><h2>How to read this monitor</h2>"
        result = module.inject_homepage(html, "<h2>Observation horizons</h2>")
        self.assertLess(result.index("Observation horizons"), result.index("How to read this monitor"))

    def test_invalid_observation_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            module.build_horizons({"generated_at": "bad", "projects": []})


if __name__ == "__main__":
    unittest.main()
