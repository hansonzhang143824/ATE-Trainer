import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "ptc_contract_schema", Path(__file__).with_name("ptc_contract_schema.py")
)
schema = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(schema)


def condition(*, trim=False, ramp=False):
    return {
        "identity": {
            "testItem": "TM900",
            "parameterName": "EXAMPLE",
            "description": "example parameter",
            "purpose": "verification",
            "unit": "V",
        },
        "remarks": "",
        "expectedValue": 1.2,
        "isTrim": trim,
        "staticPower": [],
        "hasRamp": ramp,
        "ramps": [{"pin": "VAC"}] if ramp else [],
        "scanIntent": {"state": "DECLARED" if ramp else "NOT_DECLARED", "entries": [{"kind": "ramp", "from": "0.2", "to": "3.7"}] if ramp else []},
        "highCurrent": {"state": "NOT_DECLARED"},
        "differentialVoltage": {"state": "NOT_DECLARED"},
        "involvedPins": {"vsetPins": ["vbat"], "logicalCheck": "V(ATEST0)"},
        "measurement": {
            "check": "V(ATEST0)",
            "quantity": "VOLTAGE",
            "isToggle": ramp,
            "resultTypes": ["reading"],
        },
    }


def contract(family, publisher, **measurement_extra):
    plan = {
        "measurementPin": "V(ATEST0)",
        "quantity": "VOLTAGE",
        "resultPublisher": publisher,
        "scanRangeResolution": {"state": "NOT_APPLICABLE"},
    }
    plan.update(measurement_extra)
    return {
        "stage": "METHOD",
        "verdict": "deliverable_ready",
        "tm": "TM900",
        "methodFamily": family,
        "signedInputs": {"strategyContractSha256": "strategy-hash"},
        "resourceBoundary": {"allocations": []},
        "methodPhases": [{"id": "one"}],
        "measurementPlan": plan,
        "logPlan": {"requiredResults": list(publisher["resultNames"])},
        "powerDownPlan": {"actions": ["zero sources"], "safeEndState": "sources safe"},
    }


class ContractSchemaTests(unittest.TestCase):
    def test_direct_measurement_contract_is_valid(self):
        data = contract(
            "direct_measurement",
            {"kind": "set_test_result", "minimumCount": 1, "resultNames": ["reading"]},
        )
        self.assertEqual(schema.validate_method_contract(data, "strategy-hash"), [])
        self.assertEqual(schema.validate_test_condition(condition()), [])
        self.assertEqual(schema.classify_test_condition(condition()), "direct_measurement")

    def test_scan_contract_is_valid_without_fixed_direction_or_result_count(self):
        data = contract(
            "scan",
            {"kind": "set_test_result", "minimumCount": 1, "resultNames": ["edge"]},
            scanRangeResolution={"state": "USER_DECIDED", "range": [0.2, 3.7]},
            sweeps=[{"direction": "CUSTOM_DECLARED_DIRECTION", "fromV": 0.2, "toV": 3.7, "result": "edge"}],
        )
        self.assertEqual(schema.validate_method_contract(data, "strategy-hash"), [])
        self.assertEqual(schema.validate_test_condition(condition(ramp=True)), [])
        self.assertEqual(schema.validate_method_dft_alignment(data, condition(ramp=True)), [])
        self.assertEqual(schema.classify_test_condition(condition(ramp=True)), "scan")

    def test_project_scan_direction_rule_is_enforced_without_a_fixed_range(self):
        data = contract(
            "scan",
            {"kind": "set_test_result", "minimumCount": 1, "resultNames": ["FALLING", "RISING"]},
            scanRangeResolution={"state": "USER_DECIDED", "range": [0.2, 3.7]},
            sweeps=[{"direction": "RISING", "fromV": 0.2, "toV": 3.7, "result": "RISING"}],
        )
        errors = schema.validate_method_dft_alignment(data, condition(ramp=True))
        self.assertTrue(any("project/contract direction mapping" in item for item in errors))

    def test_trim_contract_is_valid(self):
        data = contract(
            "trim",
            {"kind": "trim_node_execute", "minimumCount": 1, "resultNames": ["trimmed"]},
            trimExecution={
                "required": True,
                "node": "TRIM_NODE &X = trim_reg.trim(\"x\");",
                "nodeVariable": "X",
                "trimKey": "x",
                "executeCallPrefix": "X.execute(",
                "treg": {
                    "sourcePath": "C:/project/NU1201.treg",
                    "sourceSha256": "treg-hash",
                    "key": "x",
                    "targetMillivolts": 1200,
                    "targetUnit": "mV",
                    "stepCount": 16,
                    "registerBitMappings": [{"register": "F8", "bits": [4, 5, 6, 7]}],
                },
                "callback": {
                    "sourcePath": "C:/project/source/sub.cpp",
                    "sourceSha256": "sub-hash",
                    "symbol": "measure_x",
                    "resultUnit": "mV",
                },
            },
        )
        self.assertEqual(schema.validate_method_contract(data, "strategy-hash"), [])
        self.assertEqual(schema.validate_test_condition(condition(trim=True)), [])
        self.assertEqual(schema.classify_test_condition(condition(trim=True)), "trim")

    def test_invalid_scan_and_publisher_are_rejected(self):
        data = contract(
            "scan",
            {"kind": "set_test_result", "minimumCount": 2, "resultNames": ["only-one"]},
            scanRangeResolution={"state": "NOT_APPLICABLE"},
            sweeps=[],
        )
        errors = schema.validate_method_contract(data, "strategy-hash")
        self.assertTrue(any("resolved scan range" in item for item in errors))
        self.assertTrue(any("at least one sweep" in item for item in errors))
        self.assertTrue(any("at least minimumCount" in item for item in errors))

    def test_trim_without_trim_execution_and_ambiguous_dft_scan_are_rejected(self):
        data = contract(
            "trim",
            {"kind": "set_test_result", "minimumCount": 1, "resultNames": ["reading"]},
        )
        self.assertTrue(any("trim_node_execute" in item for item in schema.validate_method_contract(data, "strategy-hash")))
        dft = condition(ramp=True)
        dft["scanIntent"] = {"state": "AMBIGUOUS"}
        self.assertTrue(any("must be DECLARED" in item for item in schema.validate_test_condition(dft)))


    def test_trim_contract_requires_treg_and_callback_evidence(self):
        data = contract(
            "trim",
            {"kind": "trim_node_execute", "minimumCount": 1, "resultNames": ["trimmed"]},
            trimExecution={
                "required": True,
                "node": "TRIM_NODE &X = trim_reg.trim(\"x\");",
                "nodeVariable": "X",
                "trimKey": "x",
                "executeCallPrefix": "X.execute(",
            },
        )
        errors = schema.validate_method_contract(data, "strategy-hash")
        self.assertTrue(any("trimExecution.treg" in item for item in errors))
        self.assertTrue(any("trimExecution.callback" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
