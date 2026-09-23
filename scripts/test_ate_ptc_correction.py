import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("ate_ptc_runner", Path(__file__).with_name("ate_ptc_runner.py"))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class RoutedCorrectionTests(unittest.TestCase):
    def test_signed_input_hash_prevents_redispatch_loop(self):
        with tempfile.TemporaryDirectory() as temp:
            trial = Path(temp)
            contract = trial / "strategy" / "tm109-resource-config-contract.json"
            contract.parent.mkdir(parents=True)
            contract.write_text(json.dumps({"revision": "R1"}), encoding="utf-8")
            blocked = trial / "method" / "tm109-method-blocked.json"
            blocked.parent.mkdir(parents=True)
            blocked.write_text(json.dumps({
                "status": "BLOCKED",
                "verdict": "blocked_routed_to_owner",
                "requiredOwnerAction": {"owner": "test-strategy-architect"},
                "finding": {"id": "BF-1"},
                "signedInputBoundary": [{"sha256": runner.byte_sha256(contract)}],
            }), encoding="utf-8")

            first = runner.routed_correction(trial, "TM109", trial / "input-manifest.json", contract, trial / "strategy" / "deliverable-ready.json")
            self.assertEqual(first["state"], "CORRECTION_STRATEGY")

            contract.write_text(json.dumps({"revision": "R2"}), encoding="utf-8")
            changed_without_ack = runner.routed_correction(trial, "TM109", trial / "input-manifest.json", contract, trial / "strategy" / "deliverable-ready.json")
            self.assertEqual(changed_without_ack["state"], "BLOCKED")

            contract.write_text(json.dumps({"revision": "R3", "resolvedFindings": ["BF-1"]}), encoding="utf-8")
            acknowledged = runner.routed_correction(trial, "TM109", trial / "input-manifest.json", contract, trial / "strategy" / "deliverable-ready.json")
            self.assertIsNone(acknowledged)


if __name__ == "__main__":
    unittest.main()
