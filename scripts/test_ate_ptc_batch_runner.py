import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("batch", Path(__file__).with_name("ate_ptc_batch_runner.py"))
batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch)


def item(tm, state, dispatch=None, roles=None):
    result = {"state": state, "dispatch": dispatch, "reason": state}
    if roles is not None:
        result["dispatchableRoles"] = roles
    return {"tm": tm, "trial": f"C:/trial/{tm.lower()}", "result": result}


class BatchPtcRunnerTests(unittest.TestCase):
    def test_batch_list_is_frozen_and_cannot_be_silently_replaced(self):
        original = batch.BATCH_ROOT
        with tempfile.TemporaryDirectory() as temp:
            batch.BATCH_ROOT = Path(temp)
            original_explicit = batch.explicit_tms
            batch.explicit_tms = lambda values: batch.normalized_tms(values)
            self.assertEqual(batch.load_or_create_batch("tm106-110", ["TM106", "TM107"], None), ["TM106", "TM107"])
            self.assertEqual(batch.load_or_create_batch("tm106-110", None, None), ["TM106", "TM107"])
            with self.assertRaises(ValueError):
                batch.load_or_create_batch("tm106-110", ["TM106"], None)
            batch.explicit_tms = original_explicit
        batch.BATCH_ROOT = original

    def test_range_selects_only_existing_tms(self):
        original_workbook, original_rows = batch.dft_source.discover_workbook, batch.dft_source.overview_rows
        batch.dft_source.discover_workbook = lambda: Path("approved.xlsx")
        batch.dft_source.overview_rows = lambda workbook: {"TM106": {}, "TM108": {}, "TM110": {}, "TM135": {}}
        self.assertEqual(batch.range_tms("TM106", "TM110"), ["TM106", "TM108", "TM110"])
        batch.dft_source.discover_workbook, batch.dft_source.overview_rows = original_workbook, original_rows

    def test_one_strategy_handoff_covers_all_tms_at_that_stage(self):
        result = batch.aggregate([
            item("TM106", "STRATEGY", "test-strategy-architect"),
            item("TM107", "STRATEGY", "test-strategy-architect"),
        ])
        self.assertEqual(result["dispatch"], "test-strategy-architect")
        self.assertEqual(result["targetTms"], ["TM106", "TM107"])

    def test_input_sync_deduplicates_shared_schematic_role(self):
        result = batch.aggregate([
            item("TM106", "INPUT_SYNC", roles=["dft-expert", "schematic-expert"]),
            item("TM107", "INPUT_SYNC", roles=["dft-expert", "schematic-expert"]),
        ])
        dispatches = {entry["role"]: entry["tms"] for entry in result["dispatches"]}
        self.assertEqual(dispatches["dft-expert"], ["TM106", "TM107"])
        self.assertEqual(dispatches["schematic-expert"], ["TM106", "TM107"])

    def test_earliest_incomplete_stage_blocks_later_handoff(self):
        result = batch.aggregate([
            item("TM106", "INPUT_SYNC", roles=["dft-expert"]),
            item("TM107", "STRATEGY", "test-strategy-architect"),
        ])
        self.assertEqual(result["state"], "INPUT_SYNC")
        self.assertEqual(result["dispatches"][0]["tms"], ["TM106"])
        self.assertEqual(result["waitingTms"][0]["tm"], "TM107")

    def test_missing_manifest_prepares_every_tm_at_input_sync_before_dispatch(self):
        result = batch.aggregate([
            item("TM106", "INPUT_SYNC"),
            item("TM107", "INPUT_SYNC", roles=["dft-expert"]),
        ])
        self.assertEqual(result["targetTms"], ["TM106", "TM107"])
        self.assertNotIn("dispatches", result)

    def test_complete_requires_every_tm_to_compile(self):
        result = batch.aggregate([item("TM106", "COMPLETE"), item("TM107", "COMPLETE")])
        self.assertEqual(result["state"], "COMPLETE")
        self.assertIsNone(result["dispatch"])


if __name__ == "__main__":
    unittest.main()
