import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.changes import compare_snapshots


def snapshot(projects, generated_at="2026-08-25T00:00:00Z"):
    return {"generated_at": generated_at, "projects": projects}


class ChangeDetectionTests(unittest.TestCase):
    def test_first_run_is_explicit_baseline(self):
        current = snapshot([{"id": 1, "path_with_namespace": "a"}])
        result = compare_snapshots(None, current)
        self.assertEqual(result["baseline"], "none")
        self.assertEqual(result["summary"], {"added": 0, "removed": 0, "changed": 0, "activity_advanced": 0})

    def test_added_removed_structural_and_activity_are_separate(self):
        previous = snapshot([
            {"id": 1, "path_with_namespace": "a", "default_branch": "main", "archived": False, "topics": [], "last_activity_at": "2026-08-20T00:00:00Z"},
            {"id": 2, "path_with_namespace": "b", "default_branch": "main", "archived": False, "topics": [], "last_activity_at": "2026-08-20T00:00:00Z"},
        ])
        current = snapshot([
            {"id": 1, "path_with_namespace": "a", "default_branch": "trunk", "archived": False, "topics": [], "last_activity_at": "2026-08-25T00:00:00Z"},
            {"id": 3, "path_with_namespace": "c", "default_branch": "main", "archived": False, "topics": [], "last_activity_at": "2026-08-25T00:00:00Z"},
        ], "2026-08-26T00:00:00Z")
        result = compare_snapshots(previous, current)
        self.assertEqual(result["summary"], {"added": 1, "removed": 1, "changed": 1, "activity_advanced": 1})
        self.assertEqual(result["changed"][0]["fields"]["default_branch"], {"before": "main", "after": "trunk"})
        self.assertEqual(result["activity_advanced"][0]["id"], 1)

    def test_activity_only_is_not_structural_change(self):
        previous = snapshot([{"id": 1, "path_with_namespace": "a", "last_activity_at": "old"}])
        current = snapshot([{"id": 1, "path_with_namespace": "a", "last_activity_at": "new"}])
        result = compare_snapshots(previous, current)
        self.assertEqual(result["summary"]["changed"], 0)
        self.assertEqual(result["summary"]["activity_advanced"], 1)


if __name__ == "__main__":
    unittest.main()
