from pathlib import Path
import importlib.util
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_from_manifest", ROOT / "scripts" / "release_from_manifest.py")
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class ReleaseManifestTests(unittest.TestCase):
    def test_foundation_manifest_is_valid(self):
        data = module.validate(ROOT / "releases" / "v0.1.0.yaml")
        self.assertEqual(data["codename"], "Tamsa")

    def test_unknown_codename_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "v9.9.9.yaml"
            path.write_text("version: v9.9.9\ncodename: NotARiver\nstatus: release\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                module.validate(path)


if __name__ == "__main__":
    unittest.main()
