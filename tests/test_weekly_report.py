import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_lifecycle_report import html_report


class WeeklyReportRenderingTests(unittest.TestCase):
    def test_report_renders_summary_and_lifecycle_tables(self):
        portfolio = {"generated_at": "2026-09-03T00:00:00Z", "project_count": 12}
        changes = {"summary": {"added": 1, "removed": 1, "changed": 2, "activity_advanced": 3}}
        impacts = {"summary": {"review_obligations": 4}}
        lifecycle = {
            "summary": {"active": 1, "resolved": 1},
            "assurance_boundary": "Evidence is not a trust decision.",
            "records": [
                {
                    "status": "active",
                    "severity": "high",
                    "finding_id": "PF-1",
                    "subject_project": "profile",
                    "dependency_project": "core",
                    "relationship_type": "profile-of",
                    "change_type": "changed",
                    "observation_count": 2,
                },
                {
                    "status": "resolved",
                    "severity": "medium",
                    "finding_id": "PF-2",
                    "subject_project": "consumer",
                    "dependency_project": "profile",
                    "relationship_type": "depends-on",
                    "change_type": "removed",
                    "observation_count": 1,
                },
            ],
        }
        external = {"dependency_count": 5}

        rendered = html_report(portfolio, changes, impacts, lifecycle, external)

        self.assertIn("<table>", rendered)
        self.assertEqual(rendered.count("<table>"), 2)
        self.assertIn("Active findings", rendered)
        self.assertIn("Resolved findings retained", rendered)
        self.assertIn("<strong>4</strong><small>Current observation</small>", rendered)
        self.assertIn("<strong>4</strong><small>Direct</small>", rendered)
        self.assertIn("<code>PF-1</code>", rendered)
        self.assertIn("<code>PF-2</code>", rendered)
        self.assertIn("findings-lifecycle.json", rendered)
        self.assertIn("weekly-report.md", rendered)
        self.assertIn("Evidence is not a trust decision.", rendered)

    def test_report_escapes_finding_evidence(self):
        rendered = html_report(
            {},
            {"summary": {}},
            {"summary": {}},
            {
                "summary": {"active": 1, "resolved": 0},
                "records": [
                    {
                        "status": "active",
                        "severity": "high<script>",
                        "finding_id": "<unsafe>",
                        "subject_project": "a&b",
                        "dependency_project": "core",
                    }
                ],
            },
            {},
        )

        self.assertNotIn("<unsafe>", rendered)
        self.assertIn("&lt;unsafe&gt;", rendered)
        self.assertIn("a&amp;b", rendered)
        self.assertNotIn("high<script>", rendered.lower())

    def test_empty_sections_have_explicit_rows(self):
        rendered = html_report({}, {"summary": {}}, {"summary": {}}, {"summary": {}, "records": []}, {})
        self.assertEqual(rendered.count("None in this observation."), 2)
        self.assertEqual(rendered.count('colspan="7"'), 2)


if __name__ == "__main__":
    unittest.main()
