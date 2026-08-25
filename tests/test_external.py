import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.external import validate_external_dependencies


class ExternalDependencyTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {"generated_at": "2026-08-25T00:00:00Z", "projects": [{"path_with_namespace": "un/unece/uncefact/gtr"}]}

    def test_valid_dependency(self):
        data = validate_external_dependencies(self.snapshot, {"dependencies": [{"id": "x", "name": "X", "url": "https://example.org/spec", "type": "normative-dependency", "affected_projects": ["un/unece/uncefact/gtr"]}]})
        self.assertEqual(data["dependency_count"], 1)
        self.assertEqual(data["dependencies"][0]["provenance"], "declared-external-dependency")

    def test_unknown_project_fails(self):
        with self.assertRaises(ValueError):
            validate_external_dependencies(self.snapshot, {"dependencies": [{"id": "x", "url": "https://example.org", "type": "normative-dependency", "affected_projects": ["missing"]}]})

    def test_duplicate_id_fails(self):
        dep = {"id": "x", "url": "https://example.org", "type": "normative-dependency", "affected_projects": ["un/unece/uncefact/gtr"]}
        with self.assertRaises(ValueError):
            validate_external_dependencies(self.snapshot, {"dependencies": [dep, dep]})


if __name__ == "__main__":
    unittest.main()
