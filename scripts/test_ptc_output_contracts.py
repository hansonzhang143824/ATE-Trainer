import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "validate_ptc_output_contracts",
    Path(__file__).with_name("validate_ptc_output_contracts.py"),
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class OutputContractTests(unittest.TestCase):
    def test_live_role_contracts_expose_all_gate_outputs(self):
        self.assertEqual(module.validate(), [])

    def test_missing_output_abi_marker_is_detected_before_dispatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative, markers in module.REQUIRED.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(markers), encoding="utf-8")
            broken = root / "team/roles/test-method-expert.md"
            broken.write_text("team/ptc/OUTPUT_CONTRACTS.md", encoding="utf-8")
            errors = module.validate(root)
        self.assertTrue(any("test-method-expert.md missing required ABI marker" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
