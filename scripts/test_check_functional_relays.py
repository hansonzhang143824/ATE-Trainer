import copy
import unittest

from scripts.check_functional_relays import check_functional_relays


RELAYS_RULE = """**总原则 (FR-001)**: PIN 加电需要 Cap。
- 观测开漏输出 → 必须闭合
**DALI 实例**: K65_nQON_PU 是 nQON/DTEST0 上拉。
"""
CHECKLIST_RULE = "**总原则 (FR-001, 2026-08-10 重构)**: PIN 加电需要 Cap。"
MAP = {"rawText": "  nQON 上拉-固定5V R_nQON_PU_S1 需闭合: K65\n"
                  "  VBAT 稳压 Cap2_VBAT_S1 C=4.7uF 需闭合: K13\n"}


def fixture(relays=(13, 65)):
    contract = {
        "tm": "TM106", "verdict": "deliverable_ready",
        "pinResolution": {"resolutionState": "RESOLVED", "logicalSignal": "V(DTEST0)",
                          "physicalDutPin": "nQON"},
        "resourceSummary": {"setOnRelayUnion": list(relays), "functionalRelayUnion": list(relays)},
        "relayGroups": [{"groupId": "all", "setOnRelayIds": list(relays)}],
    }
    dft = {
        "tm": "TM106", "verdict": "generated", "sourceSha256": "a" * 64,
        "rawIntent": {"Power": "VBAT", "Dynamic": "VBUS", "Check": "V(DTEST0)",
                      "Code1": "vset[vbat,3,100e-6,0]", "Code2": "vset[vbus,5,1e-3,0]"},
    }
    return contract, dft, copy.deepcopy(MAP)


def assess(contract, dft, schematic):
    return check_functional_relays(contract, dft, schematic, RELAYS_RULE, CHECKLIST_RULE)


class FunctionalRelayTests(unittest.TestCase):
    def test_missing_k13(self):
        contract, dft, schematic = fixture((65,))
        result = assess(contract, dft, schematic)
        self.assertEqual(result["status"], "MISSING")
        self.assertEqual(result["requirements"][0]["closure"], "MISSING")
        self.assertEqual(result["requirements"][1]["closure"], "PRESENT")

    def test_missing_k65(self):
        contract, dft, schematic = fixture((13,))
        result = assess(contract, dft, schematic)
        self.assertEqual(result["status"], "MISSING")
        self.assertEqual(result["requirements"][0]["closure"], "PRESENT")
        self.assertEqual(result["requirements"][1]["closure"], "MISSING")

    def test_both_present_with_source_locators(self):
        contract, dft, schematic = fixture()
        result = assess(contract, dft, schematic)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(any("SCH-Connect-Map.json:rawText line 2" in x
                            for x in result["requirements"][0]["evidence"]))

    def test_same_pin_sweep_exempts_k13(self):
        contract, dft, schematic = fixture((65,))
        dft["rawIntent"]["Dynamic"] = "VBAT"
        result = assess(contract, dft, schematic)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["requirements"][0]["applicability"], "EXEMPT")

    def test_missing_schematic_evidence_is_unknown(self):
        contract, dft, schematic = fixture()
        schematic["rawText"] = "nQON 上拉-固定5V 需闭合: K65"
        result = assess(contract, dft, schematic)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["requirements"][0]["applicability"], "UNKNOWN")

    def test_workflow_exposes_pins_and_unformalized_steps(self):
        contract, dft, schematic = fixture()
        schematic["readSources"] = [{"path": "project/DALI/Input_GlobalMaterial/Dali-SCH.csv",
                                     "sha256": "b" * 64}]
        proof_data = {
            "status": "PASS", "accepted_path_proofs": [], "kelvin_pairs": [],
            "readSources": [{"path": "project/DALI/Input_GlobalMaterial/Dali-SCH.csv",
                             "sha256": "b" * 64}],
        }
        result = check_functional_relays(contract, dft, schematic, RELAYS_RULE,
                                         CHECKLIST_RULE, proof_data)
        workflow = result["workflowEvidence"]
        self.assertTrue(workflow["pinnedInputs"]["schematicAndProofSourceAgree"])
        self.assertEqual(workflow["conflictAndTiming"]["globalElectricalConflict"], "UNKNOWN")
        self.assertEqual(workflow["eightStepCoverage"][2]["coverage"], "NOT_FORMALIZED")
        self.assertEqual(result["status"], "CONFLICT")

    def test_missing_functional_relay_is_not_hidden_by_unknown_paths(self):
        contract, dft, schematic = fixture((65,))
        schematic["readSources"] = [{"path": "project/DALI/Input_GlobalMaterial/Dali-SCH.csv",
                                     "sha256": "b" * 64}]
        proof_data = {"status": "PASS", "accepted_path_proofs": [], "kelvin_pairs": [],
                      "readSources": [{"path": "project/DALI/Input_GlobalMaterial/Dali-SCH.csv",
                                       "sha256": "b" * 64}]}
        result = check_functional_relays(contract, dft, schematic, RELAYS_RULE,
                                         CHECKLIST_RULE, proof_data)
        self.assertEqual(result["status"], "MISSING")
        self.assertEqual(result["requirements"][0]["closure"], "MISSING")


if __name__ == "__main__":
    unittest.main()
