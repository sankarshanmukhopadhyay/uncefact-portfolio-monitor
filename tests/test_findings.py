import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.findings import derive_findings, validate_policies


class FindingTests(unittest.TestCase):
    def setUp(self):
        self.impacts = {
            "generated_from": {"changes_current_generated_at": "2026-08-25T00:00:00Z"},
            "review_obligations": [{
                "review_project": "un/unece/uncefact/profile",
                "changed_project": "un/unece/uncefact/core",
                "relationship_type": "profile-of",
                "change_type": "changed",
                "change_evidence": {"fields": {"default_branch": {"before": "master", "after": "main"}}},
                "relationship_provenance": "declared",
            }],
            "informational": [{"project": "x", "change_type": "activity_advanced"}],
        }
        self.policy = {
            "schema_version": "1",
            "policies": [{
                "id": "UCF-PF-002",
                "title": "Declared specification dependency changed",
                "severity": "medium",
                "relationship_types": ["profile-of"],
                "change_types": ["changed"],
                "description": "Tracked disposition required.",
            }],
        }

    def test_policy_match_creates_evidence_backed_finding(self):
        data = derive_findings(self.impacts, self.policy)
        self.assertEqual(data["summary"]["open_findings"], 1)
        finding = data["findings"][0]
        self.assertEqual(finding["severity"], "medium")
        self.assertEqual(finding["policy_id"], "UCF-PF-002")
        self.assertEqual(finding["evidence"]["relationship_provenance"], "declared")
        self.assertIn("impact_ref", finding["evidence"])

    def test_finding_id_is_stable(self):
        first = derive_findings(self.impacts, self.policy)["findings"][0]["finding_id"]
        second = derive_findings(self.impacts, self.policy)["findings"][0]["finding_id"]
        self.assertEqual(first, second)

    def test_no_matching_policy_creates_no_finding(self):
        policy = {"policies": [{
            "id": "UCF-PF-003", "title": "Other", "severity": "low",
            "relationship_types": ["semantic-dependency"], "change_types": ["changed"]
        }]}
        self.assertEqual(derive_findings(self.impacts, policy)["findings"], [])

    def test_informational_evidence_never_becomes_finding(self):
        impacts = {"generated_from": self.impacts["generated_from"], "review_obligations": [], "informational": self.impacts["informational"]}
        self.assertEqual(derive_findings(impacts, self.policy)["findings"], [])

    def test_duplicate_policy_id_is_rejected(self):
        policy = dict(self.policy)
        policy["policies"] = self.policy["policies"] * 2
        with self.assertRaises(ValueError):
            validate_policies(policy)


if __name__ == "__main__":
    unittest.main()
