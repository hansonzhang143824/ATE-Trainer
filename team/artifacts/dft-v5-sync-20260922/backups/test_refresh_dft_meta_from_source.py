"""Focused tests for the DFT meta generator's trial-manifest ruling.

These tests touch real, already-present files only (no temp directory), because
the DSH sandbox in this workspace denies writes into TemporaryDirectory paths.
"""
import importlib.util
import json
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SPEC = importlib.util.spec_from_file_location("refresh_dft_meta", SCRIPTS / "refresh_dft_meta_from_source.py")
refresh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh)

MANIFEST = ROOT / "team" / "artifacts" / "tm103-ptc" / "input-manifest.json"


class RulingTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.digest = self.manifest["canonicalInputs"]["dft"]["sha256"]

    def test_accepts_the_trial_manifest_bound_to_the_canonical_hash(self):
        ruling = refresh.load_ruling(MANIFEST, self.digest)
        self.assertEqual(ruling["canonicalInputsDftSha256"], self.digest)
        self.assertEqual(len(ruling["sha256"]), 64)
        self.assertTrue(ruling["path"].endswith("input-manifest.json"))

    def test_rejects_a_manifest_for_another_source_hash(self):
        with self.assertRaises(ValueError):
            refresh.load_ruling(MANIFEST, "0" * 64)

    def test_rejects_a_path_outside_the_trial_artifacts(self):
        with self.assertRaises(ValueError):
            refresh.load_ruling(ROOT / "Project_Info.json", self.digest)


if __name__ == "__main__":
    unittest.main()
