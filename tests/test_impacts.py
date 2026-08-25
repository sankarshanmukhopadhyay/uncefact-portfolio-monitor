import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.impacts import propagate_impacts


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.relationships = {
            "generated_from": "2026-08-25T00:00:00Z",
            "relationships": [
                {"from": "profile", "to": "core", "type": "profile-of", "provenance": "declared"},
                {"from": "consumer", "to": "profile", "type": "depends-on", "provenance": "declared"},
                {"from": "peer", "to": "core", "type": "related-to", "provenance": "declared"},
                {"from": "core", "to": "consumer", "type": "depends-on", "provenance": "declared"},
            ],
        }

    def test_dependency_change_creates_direct_obligation_only(self):
        data = propagate_impacts({
            "current_generated_at": "2026-08-25T01:00:00Z",
            "added": [], "removed": [],
            "changed": [{"path_with_namespace": "core", "fields": {"default_branch": {"before": "master", "after": "main"}}}],
            "activity_advanced": [],
        }, self.relationships)
        self.assertEqual(data["summary"]["review_obligations"], 1)
        self.assertEqual(data["review_obligations"][0]["review_project"], "profile")
        self.assertEqual(data["review_obligations"][0]["changed_project"], "core")
        self.assertEqual(data["summary"]["informational"], 1)

    def test_activity_only_is_informational(self):
        data = propagate_impacts({
            "current_generated_at": "2026-08-25T01:00:00Z",
            "added": [], "removed": [], "changed": [],
            "activity_advanced": [{"path_with_namespace": "core", "before": "a", "after": "b"}],
        }, self.relationships)
        self.assertEqual(data["summary"]["review_obligations"], 0)
        self.assertEqual(data["summary"]["informational"], 1)

    def test_no_change_produces_no_obligation(self):
        data = propagate_impacts({
            "current_generated_at": "2026-08-25T01:00:00Z",
            "added": [], "removed": [], "changed": [], "activity_advanced": [],
        }, self.relationships)
        self.assertEqual(data["summary"], {"review_obligations": 0, "informational": 0})

    def test_cycle_does_not_recurse_or_duplicate(self):
        data = propagate_impacts({
            "current_generated_at": "2026-08-25T01:00:00Z",
            "added": [], "removed": [],
            "changed": [{"path_with_namespace": "consumer", "fields": {"topics": {"before": [], "after": ["x"]}}}],
            "activity_advanced": [],
        }, self.relationships)
        self.assertEqual(data["summary"]["review_obligations"], 1)
        self.assertEqual(data["review_obligations"][0]["review_project"], "core")


if __name__ == "__main__":
    unittest.main()
