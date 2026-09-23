"""Tests for the executable golden-case gate (training round 1).

Hermetic: each case builds its own profile under a temporary EXPERT_ROOT via the
lifecycle test's fixture builder, and uses a portable one-liner as the declared
gate command, so nothing depends on project material.

Run:  python -m unittest test_case_gate -v   (from the scripts directory)
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import expert_profile as ep
import evaluate_expert_profile as evaluate
from test_expert_profile_lifecycle import PROFILE_ID, make_profile


class CaseGate(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="ptc-casegate-"))
        self.original = ep.EXPERT_ROOT
        ep.EXPERT_ROOT = self.root
        self.directory = make_profile(self.root)

    def tearDown(self):
        ep.EXPERT_ROOT = self.original
        shutil.rmtree(self.root, ignore_errors=True)

    def declare(self, verification):
        path = self.directory / "cases" / "TM106" / "expected.json"
        case = json.loads(path.read_text(encoding="utf-8"))
        case["verification"] = verification
        path.write_text(json.dumps(case), encoding="utf-8")

    def evaluate(self, **kwargs):
        kwargs.setdefault("skip_regression", True)
        return evaluate.evaluate(PROFILE_ID, **kwargs)

    def test_a_case_gate_that_passes_is_recorded_as_a_check(self):
        self.declare({
            "command": 'python -c "print(\'CASE-GATE-MARKER\')"',
            "expectExit": 0,
            "expectContains": "CASE-GATE-MARKER",
        })
        report = self.evaluate()
        entry = next((check for check in report["checks"] if check["id"] == "case_gate_TM106"), None)
        self.assertIsNotNone(entry, report["checks"])
        self.assertTrue(entry["ok"], entry)
        self.assertEqual(report["verdict"], "pass", report["failed"])

    def test_a_case_gate_that_exits_wrongly_fails_the_evaluation(self):
        self.declare({"command": 'python -c "raise SystemExit(3)"', "expectExit": 0})
        report = self.evaluate()
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("case_gate_TM106", report["failed"])
        entry = next(check for check in report["checks"] if check["id"] == "case_gate_TM106")
        self.assertIn("exit 3, expected 0", entry["detail"])

    def test_a_case_gate_whose_output_lacks_the_expected_text_fails(self):
        self.declare({
            "command": 'python -c "print(\'something else\')"',
            "expectExit": 0,
            "expectContains": "CASE-GATE-MARKER",
        })
        report = self.evaluate()
        self.assertEqual(report["verdict"], "fail")
        entry = next(check for check in report["checks"] if check["id"] == "case_gate_TM106")
        self.assertIn("stdout does not contain", entry["detail"])

    def test_a_malformed_verification_block_is_refused(self):
        for bad in ({"command": "", "expectExit": 0}, {"command": 'python -c "pass"'}, {"command": 'python -c "pass"', "expectExit": "0"}):
            self.declare(bad)
            report = self.evaluate()
            self.assertEqual(report["verdict"], "fail", bad)

    def test_skipping_case_gates_is_reported_as_skipped_not_passed(self):
        self.declare({"command": 'python -c "raise SystemExit(3)"', "expectExit": 0})
        report = self.evaluate(skip_case_gates=True)
        entry = next(check for check in report["checks"] if check["id"] == "case_verification")
        self.assertTrue(entry["ok"])
        self.assertIn("SKIPPED", entry["detail"])
        self.assertNotIn("case_gate_TM106", report["failed"])

    def test_a_case_without_a_verification_block_is_left_alone(self):
        report = self.evaluate()
        self.assertNotIn("case_verification", [check["id"] for check in report["checks"]])
        self.assertEqual(report["verdict"], "pass", report["failed"])


class ShippedCasesDeclareTheirGate(unittest.TestCase):
    """Both shipped masters must declare a re-runnable gate for their golden case."""

    def test_each_shipped_profile_has_an_executable_case_gate(self):
        for profile_id in ("ptc-dft-expert", "ptc-schematic-expert"):
            case = json.loads((ep.profile_dir(profile_id) / "cases" / "TM106" / "expected.json").read_text(encoding="utf-8"))
            verification = case.get("verification")
            self.assertIsInstance(verification, dict, profile_id)
            self.assertIn("validate_", verification.get("command", ""), profile_id)
            self.assertEqual(verification.get("expectExit"), 0, profile_id)


if __name__ == "__main__":
    unittest.main()
