import unittest

from scripts.check_path_conflicts import check_contract


def fixture():
    accepted = []
    resources = []
    for endpoint, channel in (("A", 0), ("B", 1)):
        physical = []
        ports = []
        for role, side in (("F", "FH"), ("S", "SH")):
            source = f"S5_ACM200_{side}{channel}"
            dut = f"{endpoint}_{role}_S1"
            ports.append(source)
            physical.append({"sourcePort": source, "dutPin": dut, "requiredOn": [], "locator": "test"})
            accepted.append({
                "source_port": source,
                "dut_pin": dut,
                "dut_base": endpoint,
                "dut_role": role,
                "source_meta": {"role": role, "pair_key": f"S5_ACM200:{channel}:HIGH"},
                "required_on": [],
                "path": [],
                "terminal_stop": True,
                "validation": {"terminal_stop": True, "role_match": True, "cbit_complete": True},
            })
        resources.append({"dutPin": endpoint, "ports": ports,
                          "physicalProofs": physical, "requiredActuations": []})
    contract = {"resourceAllocation": resources,
                "resourceSummary": {"setOnRelayUnion": []},
                "relayGroups": [{"groupId": "all", "setOnRelayIds": []}]}
    proofs = {"status": "PASS", "accepted_path_proofs": accepted,
              "contracts": {"shared_relay_state_must_match": True}}
    return contract, proofs


class PathConflictTests(unittest.TestCase):
    def test_proven_routes_have_no_structural_conflict_but_function_is_unknown(self):
        contract, proofs = fixture()
        result = check_contract(contract, proofs)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["functionalRelayCompleteness"], "UNKNOWN")
        self.assertEqual(result["electricalCompatibility"], "UNKNOWN")

    def test_shared_relay_on_and_off_is_conflict(self):
        contract, proofs = fixture()
        for proof in proofs["accepted_path_proofs"]:
            on = proof["dut_base"] == "A"
            proof["path"] = [{"relay_number": 7, "state": "ON" if on else "NC"}]
            proof["required_on"] = [7] if on else []
        for entry in contract["resourceAllocation"][0]["physicalProofs"]:
            entry["requiredOn"] = [7]
        contract["resourceAllocation"][0]["requiredActuations"] = [7]
        contract["resourceSummary"]["setOnRelayUnion"] = [7]
        contract["relayGroups"][0]["setOnRelayIds"] = [7]
        result = check_contract(contract, proofs)
        self.assertEqual(result["status"], "CONFLICT")
        self.assertTrue(any("K7 needs both ON and OFF" in x for x in result["conflicts"]))

    def test_incomplete_proof_is_unknown(self):
        contract, proofs = fixture()
        proofs["accepted_path_proofs"][0]["validation"]["cbit_complete"] = False
        result = check_contract(contract, proofs)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertTrue(any("not a complete PASS proof" in x for x in result["unknown"]))

    def test_source_pair_occupied_by_two_pins_is_conflict(self):
        contract, proofs = fixture()
        for proof in proofs["accepted_path_proofs"]:
            if proof["dut_base"] == "B":
                proof["source_meta"]["pair_key"] = "S5_ACM200:0:HIGH"
        result = check_contract(contract, proofs)
        self.assertEqual(result["status"], "CONFLICT")
        self.assertTrue(any("source pair" in x for x in result["conflicts"]))
        final_result = check_contract(contract, proofs, final_four_only=True)
        self.assertEqual(final_result["status"], "CONFLICT")

    def test_exact_source_end_reuse_by_distinct_pins_is_conflict(self):
        contract, proofs = fixture()
        first = contract["resourceAllocation"][0]
        second = contract["resourceAllocation"][1]
        for index in range(2):
            shared = first["ports"][index]
            second["ports"][index] = shared
            second["physicalProofs"][index]["sourcePort"] = shared
            proofs["accepted_path_proofs"][index + 2]["source_port"] = shared
            proofs["accepted_path_proofs"][index + 2]["source_meta"]["pair_key"] = "S5_ACM200:0:HIGH"
        result = check_contract(contract, proofs, final_four_only=True)
        self.assertEqual(result["status"], "CONFLICT")
        self.assertTrue(any("source port" in x for x in result["conflicts"]))


if __name__ == "__main__":
    unittest.main()
