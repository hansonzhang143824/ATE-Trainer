"""P0-B tests: the expert-profile draft→evaluate→publish lifecycle.

Hermetic: every case builds its own profile under a temporary EXPERT_ROOT, so no
test touches the real master assets. The plugin boundary suite is skipped in these
tests on purpose (it is the slow, separately-tested piece) — one test asserts the
skip is reported as SKIPPED rather than silently counted as a pass.

Run:  python -m unittest test_expert_profile_lifecycle -v
"""
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import expert_profile as ep
import evaluate_expert_profile as evaluate
import publish_expert_profile as publish

PROFILE_ID = "ptc-dft-expert"  # must be a registered profile id: the plugin map owns that list


def make_profile(root: Path, profile_id: str = PROFILE_ID) -> Path:
    directory = root / profile_id
    (directory / "cases" / "TM106").mkdir(parents=True)
    (directory / "evaluation").mkdir(parents=True)
    (directory / "profile.yaml").write_text(
        "\n".join([
            "schemaVersion: 1",
            f"id: {profile_id}",
            "displayName: PTC DFT Expert",
            f"presetId: {profile_id}",
            "executionClass: input-dft",
            "stage: INPUT_SYNC",
            "ownerRole: dft-expert",
            "readable:",
            "  - project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx",
            "writable:",
            "  - project/DALI/Output_Global_Material/dft/<TM>",
            "requiredGates:",
            "  - scripts/validate_dft_outputs.py",
        ]) + "\n",
        encoding="utf-8",
    )
    (directory / "instructions.md").write_text("# fixture instructions\n", encoding="utf-8")
    (directory / "CHANGELOG.md").write_text("# fixture changelog\n", encoding="utf-8")
    (directory / "output-contract.schema.json").write_text(
        json.dumps({"type": "object", "required": ["tm", "sourceSha256"], "properties": {"tm": {"type": "string"}}}),
        encoding="utf-8",
    )
    (directory / "status.json").write_text(
        json.dumps({"schemaVersion": 1, "profileId": profile_id, "publishedVersion": None, "history": []}),
        encoding="utf-8",
    )
    case = {
        "schemaVersion": 1,
        "profileId": profile_id,
        "caseId": "TM106",
        "expectedVerdict": "pass",
        "canonicalInput": "project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx",
        "expectedReadSources": ["project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx"],
        "expectedOutputs": ["project/DALI/Output_Global_Material/dft/TM106/dft-meta.json"],
        "semanticTruthStatus": "PENDING_DOMAIN_INPUT",
        "semanticTruthNote": "fixture defers semantic truth",
    }
    (directory / "cases" / "TM106" / "expected.json").write_text(json.dumps(case), encoding="utf-8")
    (directory / "evaluation" / "expected-results.json").write_text(
        json.dumps({"schemaVersion": 1, "profileId": profile_id, "cases": [{"caseId": "TM106", "expectedVerdict": "pass"}]}),
        encoding="utf-8",
    )
    return directory


class ExpertProfileLifecycle(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="ptc-expert-"))
        self.original = ep.EXPERT_ROOT
        ep.EXPERT_ROOT = self.root
        self.directory = make_profile(self.root)

    def tearDown(self):
        ep.EXPERT_ROOT = self.original
        shutil.rmtree(self.root, ignore_errors=True)

    def evaluate(self, **kwargs):
        kwargs.setdefault("skip_regression", True)
        return evaluate.evaluate(PROFILE_ID, **kwargs)

    def publish(self, version="v1", **kwargs):
        kwargs.setdefault("skip_regression", True)
        return publish.publish(PROFILE_ID, version, **kwargs)

    # ── evaluation ─────────────────────────────────────────────────────────
    def test_a_complete_draft_evaluates_as_pass(self):
        report = self.evaluate()
        self.assertEqual(report["verdict"], "pass", report["checks"])
        self.assertEqual(report["caseCount"], 1)
        self.assertIn("assetDigest", report)

    def test_skipping_the_regression_suite_is_reported_as_skipped_not_passed(self):
        entry = next(check for check in self.evaluate()["checks"] if check["id"] == "boundary_regression")
        self.assertTrue(entry["ok"])
        self.assertIn("SKIPPED", entry["detail"])

    def test_an_id_that_disagrees_with_its_directory_fails(self):
        (self.directory / "profile.yaml").write_text(
            (self.directory / "profile.yaml").read_text(encoding="utf-8").replace(f"id: {PROFILE_ID}", "id: some-other-id"),
            encoding="utf-8",
        )
        report = self.evaluate()
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("profile_metadata", report["failed"])

    def test_an_unregistered_execution_class_fails(self):
        (self.directory / "profile.yaml").write_text(
            (self.directory / "profile.yaml").read_text(encoding="utf-8").replace("executionClass: input-dft", "executionClass: made-up-class"),
            encoding="utf-8",
        )
        report = self.evaluate()
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("execution_class_registered", report["failed"])

    def test_a_case_on_disk_that_the_index_omits_fails(self):
        (self.directory / "cases" / "TM108").mkdir()
        (self.directory / "cases" / "TM108" / "expected.json").write_text(json.dumps({"caseId": "TM108"}), encoding="utf-8")
        report = self.evaluate()
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("case_index_matches_disk", report["failed"])

    def test_a_case_that_reads_an_old_artifact_outside_the_input_root_fails(self):
        case_path = self.directory / "cases" / "TM106" / "expected.json"
        case = json.loads(case_path.read_text(encoding="utf-8"))
        case["expectedReadSources"] = ["project/DALI/schematic-ir.json"]
        case_path.write_text(json.dumps(case), encoding="utf-8")
        report = self.evaluate()
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("case_TM106", report["failed"])

    def test_a_case_that_defers_semantic_truth_must_say_so(self):
        case_path = self.directory / "cases" / "TM106" / "expected.json"
        case = json.loads(case_path.read_text(encoding="utf-8"))
        case.pop("semanticTruthNote")
        case_path.write_text(json.dumps(case), encoding="utf-8")
        report = self.evaluate()
        self.assertEqual(report["verdict"], "fail")

    # ── publishing ─────────────────────────────────────────────────────────
    def test_a_failed_draft_is_refused_and_writes_no_version(self):
        (self.directory / "output-contract.schema.json").write_text("{}", encoding="utf-8")
        result = self.publish("v1")
        self.assertFalse(result["published"])
        self.assertIn("evaluation failed", result["reason"])
        self.assertFalse((self.directory / "versions").exists(), "a refused publish must not create snapshot state")

    def test_publishing_snapshots_the_assets_with_a_matching_manifest(self):
        result = self.publish("v1", now=datetime(2026, 9, 19, tzinfo=timezone.utc))
        self.assertTrue(result["published"], result)
        manifest = json.loads((self.directory / "versions" / "v1" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "v1")
        self.assertEqual(manifest["publishedAt"], "2026-09-19T00:00:00Z")
        self.assertEqual(manifest["executionClass"], "input-dft")
        for relative, digest in manifest["files"].items():
            self.assertEqual(ep.sha256_file(self.directory / "versions" / "v1" / relative), digest, relative)
        self.assertEqual(manifest["digest"], ep.snapshot_digest(manifest["files"]))
        status = json.loads((self.directory / "status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["publishedVersion"], "v1")
        self.assertIsNone(status["previousVersion"])
        self.assertEqual(status["manifestDigest"], manifest["digest"])

    def test_a_published_version_cannot_be_overwritten(self):
        self.publish("v1")
        manifest_path = self.directory / "versions" / "v1" / "manifest.json"
        before = manifest_path.read_bytes()
        again = self.publish("v1")
        self.assertFalse(again["published"])
        self.assertIn("immutable", again["reason"])
        self.assertEqual(manifest_path.read_bytes(), before)

    def test_publishing_a_second_version_keeps_the_first_and_records_the_previous(self):
        self.publish("v1")
        first = (self.directory / "versions" / "v1" / "manifest.json").read_bytes()
        (self.directory / "CHANGELOG.md").write_text("# fixture changelog\n\n- a draft change\n", encoding="utf-8")
        second = self.publish("v2")
        self.assertTrue(second["published"], second)
        self.assertEqual(second["previousVersion"], "v1")
        self.assertEqual((self.directory / "versions" / "v1" / "manifest.json").read_bytes(), first, "v1 must stay byte-identical")
        status = json.loads((self.directory / "status.json").read_text(encoding="utf-8"))
        self.assertEqual([entry["version"] for entry in status["history"]], ["v1", "v2"])
        self.assertEqual(status["previousVersion"], "v1")

    def test_a_tampered_published_file_no_longer_matches_its_manifest(self):
        self.publish("v1")
        snapshot = self.directory / "versions" / "v1"
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        (snapshot / "instructions.md").write_text("tampered\n", encoding="utf-8")
        recomputed = {relative: ep.sha256_file(snapshot / relative) for relative in manifest["files"]}
        self.assertNotEqual(ep.snapshot_digest(recomputed), manifest["digest"], "tampering must break the manifest digest")
        self.assertNotEqual(recomputed["instructions.md"], manifest["files"]["instructions.md"])

    def test_a_malformed_version_is_refused(self):
        for bad in ("1", "latest", "v1.2", "../escape"):
            self.assertFalse(self.publish(bad)["published"], bad)
        self.assertFalse((self.directory / "versions").exists())


class RealDftExpertAssets(unittest.TestCase):
    """The master assets committed in this checkout must evaluate cleanly."""

    def test_the_shipped_ptc_dft_expert_draft_evaluates_as_pass(self):
        report = evaluate.evaluate("ptc-dft-expert", skip_regression=True)
        self.assertEqual(report["verdict"], "pass", report["failed"])
        self.assertEqual(report["caseCount"], 1)
        preset = next(check for check in report["checks"] if check["id"] == "preset_agreement")
        self.assertTrue(preset["ok"])


if __name__ == "__main__":
    unittest.main()
