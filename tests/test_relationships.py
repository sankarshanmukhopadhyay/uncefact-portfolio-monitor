import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_relationships import MERMAID_VERSION, render
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

    def test_relationship_page_renders_mermaid_and_preserves_fallbacks(self):
        data = {
            "relationships": [{
                "from": "un/unece/uncefact/profile",
                "to": "un/unece/uncefact/core",
                "type": "profile-of",
                "note": "Test declaration",
            }]
        }
        source = "graph TD\n  profile -->|profile of| core\n"
        html = render(data, source)

        self.assertIn('<pre class="mermaid">', html)
        self.assertIn(f"mermaid@{MERMAID_VERSION}", html)
        self.assertIn("await mermaid.run", html)
        self.assertIn("relationships.mmd", html)
        self.assertIn("Declared relationships", html)
        self.assertIn("mermaid-error", html)
        self.assertNotIn('<h2>Mermaid graph source</h2>', html)

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
