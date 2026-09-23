import copy
import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("ate_ptc_runner", Path(__file__).with_name("ate_ptc_runner.py"))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class StageRegistryTests(unittest.TestCase):
    """Registry checks use no temporary files because the PTC filesystem is DLP-managed."""

    def setUp(self):
        self.read_json = runner.read_json
        self.registry_path = runner.STAGE_REGISTRY_PATH
        self.project_info_gate = runner.project_info_gate
        self.validate_output_abi = runner.validate_output_abi
        runner.project_info_gate = lambda: None
        runner.validate_output_abi = lambda: (True, "ok")

    def tearDown(self):
        runner.read_json = self.read_json
        runner.STAGE_REGISTRY_PATH = self.registry_path
        runner.project_info_gate = self.project_info_gate
        runner.validate_output_abi = self.validate_output_abi

    def test_current_registry_has_every_dispatchable_stage(self):
        registry, error = runner.load_stage_registry()
        self.assertIsNone(error)
        self.assertIsNotNone(registry)
        self.assertEqual(
            set(registry["stages"]),
            set(registry["stateMachine"]) - {"COMPLETE"},
        )

    def test_missing_registry_blocks_before_any_dispatch(self):
        runner.STAGE_REGISTRY_PATH = Path("__missing_ptc_stage_registry__.json")
        result = runner.stage(Path("__no_trial__"), "TM102")
        self.assertEqual(result["state"], "BLOCKED")
        self.assertIsNone(result["dispatch"])
        self.assertIn("stage registry", result["reason"])

    def test_missing_stage_configuration_blocks_before_any_dispatch(self):
        registry = self.read_json(self.registry_path)
        malformed = copy.deepcopy(registry)
        del malformed["stages"]["METHOD"]

        def controlled_read(path):
            return malformed if path == runner.STAGE_REGISTRY_PATH else self.read_json(path)

        runner.read_json = controlled_read
        result = runner.stage(Path("__no_trial__"), "TM102")
        self.assertEqual(result["state"], "BLOCKED")
        self.assertIsNone(result["dispatch"])
        self.assertIn("stages do not exactly match", result["reason"])

    def test_current_input_stage_exposes_registered_owner_and_gate(self):
        result = runner.stage(Path("__no_trial__"), "TM102")
        self.assertEqual(result["state"], "INPUT_SYNC")
        self.assertEqual(result["registeredStage"], "INPUT_SYNC")
        self.assertEqual(result["registeredOwner"], "captain")
        self.assertEqual(result["registeredGate"], "scripts/prepare_input_sync_v2.py")

    def test_dispatch_owner_mismatch_is_blocked(self):
        registry, error = runner.load_stage_registry()
        self.assertIsNone(error)
        result = runner.apply_stage_registry(
            {"state": "METHOD", "dispatch": "ate-implementer"}, registry
        )
        self.assertEqual(result["state"], "BLOCKED")
        self.assertIsNone(result["dispatch"])
        self.assertIn("does not match registered owner", result["reason"])


if __name__ == "__main__":
    unittest.main()
