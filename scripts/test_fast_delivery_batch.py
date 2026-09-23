import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "ate_ptc_batch_runner", Path(__file__).with_name("ate_ptc_batch_runner.py")
)
batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch)


class FastDeliveryBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_root = batch.BATCH_ROOT
        self.old_gate = batch.run_minimum_implementation_gate
        self.old_config = batch.fast_gate_configuration
        batch.BATCH_ROOT = Path(self.temp.name)
        batch.run_minimum_implementation_gate = lambda items: (True, {"status": "PASS", "checks": []})
        batch.fast_gate_configuration = lambda: {"sha256": "a" * 64, "files": [{"path": "team/ptc/ptc_stage_registry.json", "sha256": "b" * 64}]}

    def tearDown(self):
        batch.BATCH_ROOT = self.old_root
        batch.run_minimum_implementation_gate = self.old_gate
        batch.fast_gate_configuration = self.old_config
        self.temp.cleanup()

    @staticmethod
    def review_items():
        return [{"tm": "TM501", "trial": "C:/trial/tm501-ptc", "result": {"state": "RULE_REVIEW_IMPLEMENTATION", "dispatch": "rule-reviewer"}}]

    def definition(self):
        return {"schemaVersion": 3, "batchId": "fast-test", "tms": ["TM501"], "selection": {"kind": "explicit", "tms": ["TM501"]}}

    def test_missing_batch_cannot_be_enabled(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            batch.load_or_create_batch_definition("absent", None, None)

    def test_enable_rejects_missing_captain_authorization(self):
        with self.assertRaisesRegex(ValueError, "captain-authorized"):
            batch.activate_fast_delivery(self.definition(), self.review_items(), captain_authorized=False)

    def test_enable_rejects_stage_before_implementation_review(self):
        items = [{"tm": "TM501", "trial": "C:/trial/tm501-ptc", "result": {"state": "METHOD"}}]
        with self.assertRaisesRegex(ValueError, "cannot skip input, strategy, method"):
            batch.activate_fast_delivery(self.definition(), items, captain_authorized=True)

    def test_enable_records_gate_hash_and_exact_skipped_stage(self):
        definition = self.definition()
        batch.activate_fast_delivery(definition, self.review_items(), captain_authorized=True)
        saved = json.loads((batch.BATCH_ROOT / "fast-test.json").read_text(encoding="utf-8"))
        fast = saved["fastDelivery"]
        self.assertEqual(fast["status"], batch.FAST_DELIVERY_STATE)
        self.assertEqual(fast["enabledBy"], "captain")
        self.assertEqual(fast["skippedStages"], ["RULE_REVIEW_IMPLEMENTATION"])
        self.assertEqual(fast["preEnableGateConfiguration"]["sha256"], "a" * 64)
        self.assertEqual(fast["minimumImplementationGate"]["status"], "PASS")

    def test_resume_restores_only_deferred_review_without_reenabling_fast_mode(self):
        definition = self.definition()
        batch.activate_fast_delivery(definition, self.review_items(), captain_authorized=True)
        batch.resume_audit(definition)
        saved = json.loads((batch.BATCH_ROOT / "fast-test.json").read_text(encoding="utf-8"))
        fast = saved["fastDelivery"]
        self.assertEqual(fast["status"], "AUDIT_RESUMED")
        self.assertEqual(fast["resumeStage"], "RULE_REVIEW_IMPLEMENTATION")
        self.assertFalse(batch.is_fast_delivery_active(saved))
        self.assertEqual(saved["tms"], ["TM501"])

    def test_resume_rejects_changed_gate_configuration(self):
        definition = self.definition()
        batch.activate_fast_delivery(definition, self.review_items(), captain_authorized=True)
        batch.fast_gate_configuration = lambda: {"sha256": "c" * 64, "files": []}
        with self.assertRaisesRegex(ValueError, "configuration changed"):
            batch.resume_audit(definition)


if __name__ == "__main__":
    unittest.main()
