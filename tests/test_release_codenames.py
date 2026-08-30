import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("release_codenames", Path(__file__).resolve().parents[1] / "scripts" / "release_codenames.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ReleaseCodenameTests(unittest.TestCase):
    def test_repository_release_governance_is_valid(self):
        mod.validate()

    def test_existing_manifest_binding_is_idempotent(self):
        bindings = mod.release_bindings()
        self.assertTrue(bindings)
        item = bindings[0]
        codename, existing = mod.select(item["version"], seed="ignored")
        self.assertTrue(existing)
        self.assertEqual(item["codename"], codename)

    def test_future_selection_uses_unused_pool_name(self):
        used = {item["codename"] for item in mod.release_bindings()}
        codename, existing = mod.select("v99.99.99", seed="fixed")
        self.assertFalse(existing)
        self.assertNotIn(codename, used)


if __name__ == "__main__":
    unittest.main()
