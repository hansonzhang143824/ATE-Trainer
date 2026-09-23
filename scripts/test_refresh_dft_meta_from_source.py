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

dft_test_condition = refresh.dft_test_condition
validate_test_condition = refresh.validate_test_condition

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



class V5ContractTests(unittest.TestCase):
    def test_derived_condition_matches_the_v5_gate_types(self):
        row = {
            "Item": "TM109", "Name": "VAC2_PRST", "Level": "HSKP", "Trim": "",
            "Code1": "vset[vbat,3,100e-6,0]",
            "Code2": "en_tm[]\nfield[(DMUX_EN,1),(DMUX_SEL,21)]\nvset[vac2,10,1e-3,0]",
            "Code3": "vset[vac2,0,1e-3,0]", "Dynamic": "VAC2", "Check": "V(DTEST0)",
        }
        condition = dft_test_condition.derive(row)["testCondition"]
        self.assertEqual(validate_test_condition(condition), [])
        self.assertEqual(condition["identity"], "VAC2_PRST")
        self.assertEqual(condition["measurement"], "V(DTEST0)")
        self.assertEqual(condition["involvedPins"], ["vbat", "vac2", "DTEST0"])
        self.assertEqual(condition["registerFieldIntent"][0], {"kind": "en_tm", "raw": "en_tm[]"})
        self.assertEqual(condition["powerSequence"][0], {
            "cmd": "vset", "pin": "vbat", "value": 3, "pluseTime": "100e-6", "status": 0,
        })

    def test_tm109_source_row_is_stable(self):
        workbook = refresh.dft_source.discover_workbook()
        self.assertEqual(refresh.source_row_number(workbook, "TM109"), 12)


if __name__ == "__main__":
    unittest.main()
