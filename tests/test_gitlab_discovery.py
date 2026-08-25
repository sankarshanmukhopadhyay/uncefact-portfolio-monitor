import sys
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.gitlab import GitLabSource, discover_projects, normalize_project


class GitLabDiscoveryTests(unittest.TestCase):
    def test_normalization_is_stable(self):
        project = normalize_project({
            "id": 2,
            "name": "B",
            "path_with_namespace": "un/unece/uncefact/b",
            "topics": ["z", "a"],
            "archived": False,
        })
        self.assertEqual(project["topics"], ["a", "z"])
        self.assertFalse(project["archived"])

    def test_pagination_and_sorting(self):
        calls = []

        def requester(url):
            calls.append(url)
            page = parse_qs(urlparse(url).query)["page"][0]
            if page == "1":
                return ([{"id": 2, "name": "B", "path_with_namespace": "un/unece/uncefact/b"}], "2")
            return ([{"id": 1, "name": "A", "path_with_namespace": "un/unece/uncefact/a"}], "")

        projects = discover_projects(
            GitLabSource("https://example.test", "un/unece/uncefact"),
            requester=requester,
        )
        self.assertEqual([item["id"] for item in projects], [1, 2])
        self.assertEqual(len(calls), 2)
        self.assertIn("un%2Funece%2Funcefact", calls[0])
        self.assertIn("include_subgroups=true", calls[0])


if __name__ == "__main__":
    unittest.main()
