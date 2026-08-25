import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.lifecycle import update_lifecycle


class LifecycleTests(unittest.TestCase):
    def finding(self, finding_id="PF-1"):
        return {"finding_id": finding_id, "severity": "high", "policy_id": "p1", "subject_project": "profile", "dependency_project": "core", "relationship_type": "profile-of", "change_type": "changed"}

    def test_new_finding_becomes_active(self):
        data = update_lifecycle({"generated_from": {"observation": "2026-08-25T00:00:00Z"}, "findings": [self.finding()]}, None)
        self.assertEqual(data["summary"]["active"], 1)
        self.assertEqual(data["records"][0]["observation_count"], 1)

    def test_repeated_finding_preserves_first_seen_and_increments(self):
        previous = {"records": [{**self.finding(), "status": "active", "first_observed": "2026-08-24T00:00:00Z", "last_observed": "2026-08-24T00:00:00Z", "observation_count": 1, "resolved_at": None, "evidence": self.finding()}]}
        data = update_lifecycle({"generated_from": {"observation": "2026-08-25T00:00:00Z"}, "findings": [self.finding()]}, previous)
        record = data["records"][0]
        self.assertEqual(record["first_observed"], "2026-08-24T00:00:00Z")
        self.assertEqual(record["observation_count"], 2)

    def test_missing_current_finding_resolves_but_is_retained(self):
        previous = {"records": [{**self.finding(), "status": "active", "first_observed": "2026-08-24T00:00:00Z", "last_observed": "2026-08-24T00:00:00Z", "observation_count": 1, "resolved_at": None, "evidence": self.finding()}]}
        data = update_lifecycle({"generated_from": {"observation": "2026-08-25T00:00:00Z"}, "findings": []}, previous)
        self.assertEqual(data["summary"]["resolved"], 1)
        self.assertEqual(data["records"][0]["status"], "resolved")


if __name__ == "__main__":
    unittest.main()
