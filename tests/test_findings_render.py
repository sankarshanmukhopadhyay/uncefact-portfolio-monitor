import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_findings", ROOT / "scripts" / "build_findings.py"
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class FindingsRenderTests(unittest.TestCase):
    def test_finding_is_human_readable_before_machine_id(self):
        data = {
            "summary": {
                "open_findings": 1,
                "by_severity": {"critical": 0, "high": 1, "medium": 0, "low": 0},
            },
            "findings": [{
                "finding_id": "UCF-PF-001-F3EB6692AE1A",
                "status": "open",
                "severity": "high",
                "title": "Trust infrastructure dependency changed",
                "policy_id": "UCF-PF-001",
                "subject_project": "un/unece/uncefact/reviewer",
                "dependency_project": "un/unece/uncefact/dependency",
                "relationship_type": "trust-infrastructure-dependency",
                "change_type": "changed",
                "reason": "A project with a declared trust-infrastructure dependency requires tracked disposition after structural change in that dependency.",
                "evidence": {
                    "impact_ref": "impacts.json#/review_obligations/0",
                    "change_evidence": "changes.json#/changed/0",
                    "relationship_provenance": "relationships.json#/relationships/0",
                    "policy_provenance": "declared-policy",
                },
            }],
            "assurance_boundary": "A finding is not by itself a trust decision.",
        }
        html = module.render(data)
        self.assertIn("Trust infrastructure dependency changed", html)
        self.assertIn("Why this was flagged", html)
        self.assertIn("requires tracked disposition", html)
        self.assertIn("Stable finding ID", html)
        self.assertIn("UCF-PF-001-F3EB6692AE1A", html)
        self.assertIn("Review obligation", html)
        self.assertIn("Change evidence", html)
        self.assertIn("Relationship provenance", html)
        self.assertLess(
            html.index("Trust infrastructure dependency changed"),
            html.index("Stable finding ID"),
        )

    def test_render_escapes_finding_content(self):
        data = {
            "summary": {"open_findings": 1, "by_severity": {}},
            "findings": [{
                "finding_id": "UCF-PF-X",
                "status": "open",
                "severity": "high",
                "title": "<script>alert(1)</script>",
                "policy_id": "UCF-PF-001",
                "subject_project": "subject",
                "dependency_project": "dependency",
                "relationship_type": "depends-on",
                "change_type": "changed",
                "reason": "review",
                "evidence": {},
            }],
            "assurance_boundary": "",
        }
        html = module.render(data)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)


if __name__ == "__main__":
    unittest.main()
