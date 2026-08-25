import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.relationships import mermaid_graph, validate_relationships


class RelationshipTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "generated_at": "2026-08-25T00:00:00Z",
            "projects": [
                {"path_with_namespace": "un/unece/uncefact/core"},
                {"path_with_namespace": "un/unece/uncefact/profile"},
            ],
        }

    def test_valid_relationship(self):
        data = validate_relationships(self.snapshot, {
            "schema_version": "1",
            "relationships": [{"from": "un/unece/uncefact/profile", "to": "un/unece/uncefact/core", "type": "profile-of"}],
        })
        self.assertEqual(data["relationship_count"], 1)
        self.assertEqual(data["relationships"][0]["provenance"], "declared")
        self.assertIn("profile of", mermaid_graph(data))

    def test_unknown_internal_endpoint_fails(self):
        with self.assertRaises(ValueError):
            validate_relationships(self.snapshot, {
                "relationships": [{"from": "un/unece/uncefact/missing", "to": "un/unece/uncefact/core", "type": "depends-on"}],
            })

    def test_unknown_type_fails(self):
        with self.assertRaises(ValueError):
            validate_relationships(self.snapshot, {
                "relationships": [{"from": "un/unece/uncefact/profile", "to": "un/unece/uncefact/core", "type": "magic"}],
            })


if __name__ == "__main__":
    unittest.main()
