import hashlib
import os
import unittest
from pathlib import Path

from ptc_trim_validation import validate_trim_project_evidence


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TrimEvidenceTests(unittest.TestCase):
    def fixture(self, *, active=True, register="F8"):
        root = Path(os.environ.get("PTC_REGRESSION_ROOT", Path(__file__).resolve().parents[1] / "team" / "artifacts" / "_ptc-regression")) / "trim-validator-fixture" / self._testMethodName
        root.mkdir(parents=True, exist_ok=True)
        source = root / "source"
        source.mkdir(exist_ok=True)
        (source / "DALI.vcxproj").write_text(
            '<Project><ItemGroup><ClCompile Include="sub.cpp" /></ItemGroup></Project>',
            encoding="utf-8",
        )
        treg = root / "NU1201.treg"
        treg.write_text(
            "[mnt_v1p2_buf]\n;Target = 1200 mV\nTarget = 1200\n"
            "Table = *0,0.001,0.002,0.003,0.004,0.005,0.006,0.007,0,-0.001,-0.002,-0.003,-0.004,-0.005,-0.006,-0.007\n\n"
            "[_EFUSE_REG_F8]\n4: mnt_v1p2_buf = 0\n5: mnt_v1p2_buf = 1\n6: mnt_v1p2_buf = 2\n7: mnt_v1p2_buf = 3\n",
            encoding="utf-8",
        )
        callback = source / "sub.cpp"
        callback.write_text(
            ("" if active else "// ")
            + "void measure_mnt_v1p2_buf(TRIM_NODE *node, TREG_MEASURE_FLAG flag, double *results) {\n"
            + f'  DWORD value = trim_reg.assy("EFUSE_REG_{register}").get_working(0);\n'
            + f"  dcm.I2CWriteData(DEV_ADDR, 0x{register}, 1, value);\n"
            + "  results[0] = NTC_FOVI.GetMeasResult(0, MVRET) * 1e3;\n}\n",
            encoding="utf-8",
        )
        trim = {
            "required": True,
            "node": 'TRIM_NODE &MNT_V1P2_BUF = trim_reg.trim("mnt_v1p2_buf");',
            "nodeVariable": "MNT_V1P2_BUF",
            "trimKey": "mnt_v1p2_buf",
            "executeCallPrefix": "MNT_V1P2_BUF.execute(measure_mnt_v1p2_buf,",
            "treg": {
                "sourcePath": str(treg), "sourceSha256": digest(treg), "key": "mnt_v1p2_buf",
                "targetMillivolts": 1200, "targetUnit": "mV", "stepCount": 16,
                "registerBitMappings": [{"register": "F8", "bits": [4, 5, 6, 7]}],
            },
            "callback": {
                "sourcePath": str(callback), "sourceSha256": digest(callback),
                "symbol": "measure_mnt_v1p2_buf", "resultUnit": "mV",
            },
        }
        test_body = "DUT_API int TM425() { MNT_V1P2_BUF.execute(measure_mnt_v1p2_buf, spec, 0, 0, 1, 0, 0, 0); }"
        return trim, test_body

    def test_active_callback_matching_treg_passes(self):
        trim, body = self.fixture()
        self.assertEqual(validate_trim_project_evidence(trim, source_body=body), [])

    def test_commented_callback_is_rejected(self):
        trim, body = self.fixture(active=False)
        errors = validate_trim_project_evidence(trim, source_body=body)
        self.assertTrue(any("no active implementation" in error for error in errors))

    def test_register_mapping_mismatch_is_rejected(self):
        trim, body = self.fixture(register="F6")
        errors = validate_trim_project_evidence(trim, source_body=body)
        self.assertTrue(any("do not match signed .treg mapping" in error for error in errors))

    def test_missing_execute_binding_is_rejected(self):
        trim, _ = self.fixture()
        errors = validate_trim_project_evidence(trim, source_body="DUT_API int TM425() { return 0; }")
        self.assertTrue(any("does not bind" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
