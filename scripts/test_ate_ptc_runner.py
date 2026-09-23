import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("ate_ptc_runner", Path(__file__).with_name("ate_ptc_runner.py"))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def ready(path: Path, stage: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": "success", "stage": stage, "verdict": "deliverable_ready"}), encoding="utf-8")


class PtcRunnerTests(unittest.TestCase):
    def setUp(self):
        self.original_validate = runner.validate_strategy
        self.original_validate_method = runner.validate_method_contract
        self.original_implementation_current = runner.implementation_is_current
        self.original_compile_current = runner.compile_is_current
        runner.validate_strategy = lambda trial, tm: (True, "ok")
        # This is a routing unit test. Schema, source and compile checks have
        # their own tests, so use current placeholders as already validated.
        runner.validate_method_contract = lambda path, strategy_sha: True
        runner.implementation_is_current = lambda path, method_sha: True
        runner.compile_is_current = lambda path: True

    def tearDown(self):
        runner.validate_strategy = self.original_validate
        runner.validate_method_contract = self.original_validate_method
        runner.implementation_is_current = self.original_implementation_current
        runner.compile_is_current = self.original_compile_current

    def test_missing_manifest_stays_at_input_sync(self):
        with tempfile.TemporaryDirectory() as temp:
            result = runner.stage(Path(temp), "TM109")
        self.assertEqual(result["state"], "INPUT_SYNC")
        self.assertIsNone(result["dispatch"])

    def test_ready_input_requires_method_after_valid_strategy(self):
        with tempfile.TemporaryDirectory() as temp:
            trial = Path(temp)
            (trial / "input-manifest.json").write_text(json.dumps({"status": "ready"}), encoding="utf-8")
            result = runner.stage(trial, "TM109")
        self.assertEqual(result["state"], "METHOD")
        self.assertEqual(result["dispatch"], "test-method-expert")

    def test_method_requires_independent_review_before_implementation(self):
        with tempfile.TemporaryDirectory() as temp:
            trial = Path(temp)
            (trial / "input-manifest.json").write_text(json.dumps({"status": "ready"}), encoding="utf-8")
            method = trial / "method"
            (method / "tm109-test-method-contract.json").parent.mkdir(parents=True, exist_ok=True)
            (method / "tm109-test-method-contract.json").write_text("{}", encoding="utf-8")
            ready(method / "deliverable-ready.json", "METHOD")
            result = runner.stage(trial, "TM109")
        self.assertEqual(result["state"], "RULE_REVIEW_METHOD")
        self.assertEqual(result["dispatch"], "rule-reviewer")

    def test_full_chain_reaches_complete_only_after_compile(self):
        with tempfile.TemporaryDirectory() as temp:
            trial = Path(temp)
            (trial / "input-manifest.json").write_text(json.dumps({"status": "ready"}), encoding="utf-8")
            method = trial / "method"
            impl = trial / "implementation"
            review = trial / "review"
            compile_dir = trial / "compile"
            (method / "tm109-test-method-contract.json").parent.mkdir(parents=True, exist_ok=True)
            (method / "tm109-test-method-contract.json").write_text("{}", encoding="utf-8")
            ready(method / "deliverable-ready.json", "METHOD")
            method_sha = runner.byte_sha256(method / "tm109-test-method-contract.json")
            (review / "method-contract-review.json").parent.mkdir(parents=True, exist_ok=True)
            (review / "method-contract-review.json").write_text(json.dumps({"signedInputs": {"methodContractSha256": method_sha}}), encoding="utf-8")
            ready(review / "method-contract-review-deliverable-ready.json", "RULE_REVIEW_METHOD")
            (impl / "implementation-manifest.json").parent.mkdir(parents=True, exist_ok=True)
            (impl / "implementation-manifest.json").write_text("{}", encoding="utf-8")
            ready(impl / "deliverable-ready.json", "IMPLEMENTATION")
            implementation_sha = runner.byte_sha256(impl / "implementation-manifest.json")
            (review / "implementation-review.json").write_text(json.dumps({"signedInputs": {"implementationManifestSha256": implementation_sha}}), encoding="utf-8")
            ready(review / "implementation-review-deliverable-ready.json", "RULE_REVIEW_IMPLEMENTATION")
            result = runner.stage(trial, "TM109")
            self.assertEqual(result["state"], "COMPILE")
            ready(compile_dir / "deliverable-ready.json", "COMPILE")
            result = runner.stage(trial, "TM109")
        self.assertEqual(result["state"], "COMPLETE")
        self.assertIsNone(result["dispatch"])


if __name__ == "__main__":
    unittest.main()
