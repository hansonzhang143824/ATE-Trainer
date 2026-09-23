# -*- coding: utf-8 -*-
"""核查 check-extra 澄清是否到位（只读）。"""
import io
import json
import os

p = 'team/artifacts/acceptance-20260916-dali10/build-report.json'
d = json.load(io.open(p, encoding='utf-8-sig'))
s = json.dumps(d, ensure_ascii=False)
print('报告 %d B ; verdict=%s' % (os.path.getsize(p), d['verdict']))
print('  checkExtraStance 在                 =', 'checkExtraStance' in d)
print('  含「禁用要求自 rev 29 起已解除」      =', '禁用要求自 rev 29 起已解除' in s)
print('  含「独立决定」                        =', '独立决定' in s)
print('  含 RE-ENABLED（不应出现）             =', 'RE-ENABLED' in s)
print('  含「本次核验选择走默认判据」          =', '本次核验选择走默认判据' in s)
if 'checkExtraStance' in d:
    for k, v in d['checkExtraStance'].items():
        print('   • %-16s %s' % (k, str(v)[:110]))
