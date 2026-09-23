import importlib.util
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("captain_entry", SCRIPTS / "captain_delivery_entry.py")
captain = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(captain)


class CaptainDeliveryEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_batch_root = captain.batch.BATCH_ROOT
        self.original_load = captain.project_info.load
        self.original_problems = captain.project_info.problems
        self.original_info_path = captain.project_info.PROJECT_INFO
        self.original_explicit = captain.batch.explicit_tms
        self.original_range = captain.batch.range_tms
        captain.batch.BATCH_ROOT = Path(self.temp.name) / "batches"
        captain.project_info.PROJECT_INFO = Path(self.temp.name) / "Project_Info.json"
        captain.project_info.PROJECT_INFO.write_text('{"project":"DALI"}', encoding="utf-8")
        self.info = {
            "project": "DALI", "projectDir": "project/DALI",
            "roots": {"input": "project/DALI/Input_GlobalMaterial"},
            "approval": {"inputsDigest": "approved"},
        }
        captain.project_info.load = lambda: self.info
        captain.project_info.problems = lambda _: []
        captain.batch.explicit_tms = lambda tms: captain.batch.normalized_tms(tms)
        captain.batch.range_tms = lambda start, end: ["TM106", "TM108", "TM110"]

    def tearDown(self):
        captain.batch.BATCH_ROOT = self.original_batch_root
        captain.project_info.load = self.original_load
        captain.project_info.problems = self.original_problems
        captain.project_info.PROJECT_INFO = self.original_info_path
        captain.batch.explicit_tms = self.original_explicit
        captain.batch.range_tms = self.original_range
        self.temp.cleanup()

    @staticmethod
    def entry(tm):
        return {"tm": tm, "trial": f"C:/trial/{tm.lower()}", "result": {
            "state": "STRATEGY", "dispatch": "test-strategy-architect", "reason": "ready",
        }}

    def test_parses_explicit_list_and_range(self):
        self.assertEqual(captain.parse_scope("请跑 TM102、TM105 和 TM425"), {
            "kind": "explicit", "tms": ["TM102", "TM105", "TM425"],
        })
        self.assertEqual(captain.parse_scope("从 TM106 到 TM110"), {
            "kind": "range", "start": "TM106", "end": "TM110",
        })
        self.assertEqual(captain.parse_scope("帮我写TM103/106/108/109/425的code,快速交付模式"), {
            "kind": "explicit", "tms": ["TM103", "TM106", "TM108", "TM109", "TM425"],
        })
        self.assertEqual(captain.parse_scope("做TM106到TM110"), {
            "kind": "range", "start": "TM106", "end": "TM110",
        })

    def test_real_chinese_shorthand_expands_every_tm_without_llm_rewrite(self):
        request = '帮我写TM103/106/108/109/425的code'
        self.assertEqual(captain.parse_scope(request), {
            'kind': 'explicit',
            'tms': ['TM103', 'TM106', 'TM108', 'TM109', 'TM425'],
        })

    def test_open_creates_unique_batch_binds_project_and_prepares(self):
        prepared = []
        result = captain.open_new_delivery(
            "跑 TM102、TM105",
            now=datetime(2026, 9, 19, 10, 11, 12),
            prepare=lambda tms: prepared.append(tms) or [{"tms": tms}],
            stage_entry=self.entry,
        )
        self.assertEqual(result["batchId"], "dali-20260919-101112-tm102-tm105")
        self.assertEqual(prepared, [])
        self.assertEqual(result["state"], "INPUT_SYNC")
        self.assertEqual(result["dispatches"][0]["role"], "dft-expert")
        self.assertEqual(result["dispatches"][0]["tms"], ["TM102", "TM105"])
        saved = captain.batch.load_or_create_batch_definition(result["batchId"], None, None)
        self.assertEqual(saved["projectBinding"]["project"], "DALI")
        self.assertTrue(saved["captainFastDeliveryPolicy"]["defaultEnabled"])
        self.assertEqual(saved["captainFastDeliveryPolicy"]["strictAuditResume"], "user_explicit_instruction_required")

    def test_range_uses_existing_dft_items_only(self):
        result = captain.open_new_delivery(
            "跑 TM106~110",
            now=datetime(2026, 9, 19, 10, 11, 12),
            prepare=lambda tms: [], stage_entry=self.entry,
        )
        saved = captain.batch.load_or_create_batch_definition(result["batchId"], None, None)
        self.assertEqual(saved["tms"], ["TM106", "TM108", "TM110"])

    def test_explicit_missing_tm_is_a_short_user_error(self):
        captain.batch.explicit_tms = lambda _: (_ for _ in ()).throw(ValueError("你点名的 TM999 在 DFT 中没有。"))
        result = captain.open_new_delivery("跑 TM999", prepare=lambda _: [], stage_entry=self.entry)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["reason"], "你点名的 TM999 在 DFT 中没有。")

    def test_fast_delivery_waits_for_implementation_review_and_never_resumes_here(self):
        calls = []
        original_activate = captain.batch.activate_fast_delivery
        original_is_active = captain.batch.is_fast_delivery_active
        original_fast_aggregate = captain.batch.aggregate_fast_delivery
        try:
            captain.batch.activate_fast_delivery = lambda definition, items, captain_authorized: calls.append(captain_authorized) or definition.update({"fastDelivery": {"status": captain.batch.FAST_DELIVERY_STATE}})
            captain.batch.is_fast_delivery_active = lambda definition: bool(definition.get("fastDelivery"))
            captain.batch.aggregate_fast_delivery = lambda definition, items: {"state": captain.batch.FAST_DELIVERY_STATE}
            definition = {"captainFastDeliveryPolicy": {"defaultEnabled": True}}
            items = [{"result": {"state": "RULE_REVIEW_IMPLEMENTATION"}}]
            self.assertEqual(captain._aggregate_with_default_fast(definition, items)["state"], captain.batch.FAST_DELIVERY_STATE)
            self.assertEqual(calls, [True])
        finally:
            captain.batch.activate_fast_delivery = original_activate
            captain.batch.is_fast_delivery_active = original_is_active
            captain.batch.aggregate_fast_delivery = original_fast_aggregate


if __name__ == "__main__":
    unittest.main()
