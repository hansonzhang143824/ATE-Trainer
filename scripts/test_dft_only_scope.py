from test_captain_delivery_entry import CaptainDeliveryEntryTests, captain


class DftOnlyScopeTests(CaptainDeliveryEntryTests):
    def test_only_dft_persists_and_cannot_advance(self):
        for text in ["帮我写TM109的code,只执行DFT expert", "生成TM109的code,执行性DFT expert，其余都不执行", "ＴＭ１０９，只执行到ＤＦＴ专家", "TM109 DFT expert only"]:
            with self.subTest(text=text):
                result = captain.open_new_delivery(text)
                self.assertEqual([d["role"] for d in result["dispatches"]], ["dft-expert"])
                self.assertEqual(result["executionScope"]["stopAfter"], "INPUT_SYNC")
                def forbidden(*args):
                    self.fail("DFT-only continuation must not prepare or enter downstream stages")
                stopped = captain.advance_batch(result["batchId"], prepare=forbidden, stage_entry=forbidden)
                self.assertEqual(stopped["dispatches"], [])
                self.assertEqual(stopped["command"], "captain-scope-stop")

    def test_normal_delivery_preserves_both_source_roles(self):
        result = captain.open_new_delivery("写 TM109")
        self.assertEqual([d["role"] for d in result["dispatches"]], ["dft-expert", "schematic-expert"])

    def test_same_session_scope_update_is_persisted_before_advance(self):
        opened = captain.open_new_delivery("写 TM109")
        narrowed = captain.update_delivery_scope(
            opened["batchId"], "帮我写TM109的code,只执行DFT expert，其他不执行")
        self.assertEqual(narrowed["command"], "captain-update-scope")
        self.assertEqual(narrowed["executionScope"], {
            "sourceRoles": ["dft-expert"], "stopAfter": "INPUT_SYNC"})
        saved = captain.batch.load_or_create_batch_definition(opened["batchId"], None, None)
        self.assertEqual(saved["executionScope"], narrowed["executionScope"])


if __name__ == "__main__":
    import unittest
    unittest.main()
