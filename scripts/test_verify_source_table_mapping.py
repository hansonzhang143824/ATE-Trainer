import copy
import unittest

from scripts.verify_source_table_mapping import check_source_table_mapping


HEADER = '''#define _PIN_CHANNEL_DEFINE_VBAT_PD3_FXVI_  "S3_5,S4_5"
extern FXVIe_PLUS VBAT_PD3_FXVI;
#define _PIN_CHANNEL_DEFINE_VBUS_DRVH1_ACM_  "S5_10,S6_10"
extern ACM200 VBUS_DRVH1_ACM;
'''
CONTRACT = {'resourceAllocation': [
    {'dutPin': 'VBAT', 'sourceTable': 'VBAT_PD3_FXVI', 'instrumentCategory': 'FXVIe_PLUS',
     'ports': ['S3_FXVIe_PLUS_FH5', 'S3_FXVIe_PLUS_SH5']},
    {'dutPin': 'VBUS', 'sourceTable': 'VBUS_DRVH1_ACM', 'instrumentCategory': 'ACM200',
     'ports': ['S5_ACM200_FH10', 'S5_ACM200_SH10']},
]}


class SourceTableMappingTests(unittest.TestCase):
    def test_exact_header_mapping(self):
        self.assertEqual(check_source_table_mapping(CONTRACT, HEADER)['status'], 'PASS')

    def test_wrong_channel_is_rejected(self):
        contract = copy.deepcopy(CONTRACT)
        contract['resourceAllocation'][1]['ports'] = ['S5_ACM200_FH11', 'S5_ACM200_SH11']
        result = check_source_table_mapping(contract, HEADER)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('does not contain S5_11' in error for error in result['errors']))

    def test_similar_name_is_not_accepted(self):
        contract = copy.deepcopy(CONTRACT)
        contract['resourceAllocation'][1]['sourceTable'] = 'VBUS_DRVH1_ACM_ALIAS'
        self.assertEqual(check_source_table_mapping(contract, HEADER)['status'], 'FAIL')

    def test_force_sense_must_match_one_instrument_channel(self):
        contract = copy.deepcopy(CONTRACT)
        contract['resourceAllocation'][1]['ports'][1] = 'S5_ACM200_SH9'
        self.assertEqual(check_source_table_mapping(contract, HEADER)['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
