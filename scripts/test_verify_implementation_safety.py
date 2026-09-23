import unittest
from verify_implementation_batch import expected_trim_compliance, signed_source_tables, validate_relay_settle, validate_trim_compliance_evidence, validate_zero_before_off


class ImplementationSafetyTests(unittest.TestCase):
    def test_old_style_source_table_contract_is_included(self):
        self.assertEqual(["VBAT_PD3_FXVI", "VBUS_DRVH1_ACM"], signed_source_tables({"resourceBoundary": {"sourceTablesByEndpoint": {"VBAT": "VBAT_PD3_FXVI", "VBUS": "VBUS_DRVH1_ACM"}}}))

    def test_functional_relay_requires_immediate_three_ms_settle(self):
        self.assertEqual([], validate_relay_settle('cbite.SetOn(K13_VBAT_Cap, -1); delay_ms(3);', 'TM: '))
        self.assertTrue(validate_relay_settle('cbite.SetOn(K13_VBAT_Cap, -1); VBAT_PD3_FXVI.Set(FV, 4.4, X, Y, FXVIe_PLUS_RELAY_ON);', 'TM: '))

    def test_trim_requires_current_standard_and_validator_evidence(self):
        self.assertEqual([], validate_trim_compliance_evidence({"trimCompliance": expected_trim_compliance()}, "TM: "))
        self.assertTrue(validate_trim_compliance_evidence({"trimCompliance": {}}, "TM: "))

    def test_every_signed_source_is_zeroed_while_on_then_released(self):
        body = ('VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_ON);'
                'VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);')
        self.assertEqual([], validate_zero_before_off(body, 'TM: ', ['VBAT_PD3_FXVI']))
        self.assertTrue(validate_zero_before_off('VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);', 'TM: ', ['VBAT_PD3_FXVI']))


if __name__ == '__main__':
    unittest.main()
