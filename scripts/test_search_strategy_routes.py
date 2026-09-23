import unittest

from scripts.search_strategy_routes import _candidate, _rank, _routing_conditions, _search_group


class RouteSearchTests(unittest.TestCase):
    def test_force_sense_of_one_endpoint_share_instrument_legally(self):
        pair = {"dut_base": "A", "force_proof": {"source": "SRC_F", "dut": "A_F"},
                "sense_proof": {"source": "SRC_S", "dut": "A_S"}}
        def proof(source, dut, role):
            return {"source_port": source, "dut_pin": dut, "dut_role": role,
                    "source_meta": {"role": role, "pair_key": "SRC:0", "type": "ACM200"},
                    "path": [{"relay_number": 7, "state": "NC"}],
                    "validation": {"terminal_stop": True, "role_match": True, "cbit_complete": True}}
        lookup = {("SRC_F", "A_F"): [proof("SRC_F", "A_F", "F")],
                  ("SRC_S", "A_S"): [proof("SRC_S", "A_S", "S")]}
        candidate = _candidate(pair, lookup)
        self.assertEqual(candidate["sourcePair"], "SRC:0")
        self.assertEqual(candidate["requiredOff"], [7])
        self.assertEqual(candidate["contactCount"], 2)

    def test_relay_conflict_falls_back_to_next_candidate(self):
        def candidate(pair, source, state):
            return {"sourcePair": pair, "sourcePorts": [source + "_F", source + "_S"],
                    "relayStates": {7: state}, "requiredOn": [7] if state == "ON" else [],
                    "requiredOff": [7] if state == "OFF" else []}
        options = {"A": [candidate("A:first", "A0", "ON")],
                   "B": [candidate("B:first", "B0", "OFF"),
                         candidate("B:second", "B1", "ON")]}
        chosen, trace = _search_group(["A", "B"], ["A", "B"], options, set(), set())
        self.assertEqual(chosen["B"]["sourcePair"], "B:second")
        self.assertTrue(any(x["decision"] == "REJECT" and "K7" in x["reason"] for x in trace))

    def test_functional_on_rejects_route_that_requires_nc(self):
        options = {"A": [
            {"sourcePair": "first", "sourcePorts": ["F0", "S0"],
             "relayStates": {13: "OFF"}, "requiredOn": [], "requiredOff": [13]},
            {"sourcePair": "second", "sourcePorts": ["F1", "S1"],
             "relayStates": {13: "ON"}, "requiredOn": [13], "requiredOff": []},
        ]}
        chosen, trace = _search_group(["A"], ["A"], options, set(), {13})
        self.assertEqual(chosen["A"]["sourcePair"], "second")
        self.assertTrue(any("functional relay" in x["reason"] for x in trace))

    def test_non_scarce_then_shortest_then_stable_pair(self):
        short_scarce = {"sourceType": "FPVIe", "contactCount": 1, "sourcePair": "P0"}
        longer_common = {"sourceType": "ACM200", "contactCount": 3, "sourcePair": "A0"}
        self.assertLess(_rank(longer_common, "A", [], []),
                        _rank(short_scarce, "A", [], []))
        self.assertLess(_rank(short_scarce, "A", [["A", "B"]], []),
                        _rank(longer_common, "A", [["A", "B"]], []))

    def test_missing_signed_routing_conditions_are_unknown(self):
        _, _, _, _, _, _, _, missing = _routing_conditions(
            {"tm": "TM106"}, ["VBAT", "VBUS"], {"contracts": {}})
        self.assertTrue(any("routingConditions" in x for x in missing))
        self.assertTrue(any("exclusive_source_pairs" in x for x in missing))


if __name__ == "__main__":
    unittest.main()
