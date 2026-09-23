# -*- coding: utf-8 -*-
"""最终校验：报告两项更正是否到位（幂等、只读）。"""
import io
import json
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
p = os.path.join(RUN, 'build-report.json')
d = json.load(io.open(p, encoding='utf-8-sig'))
g = d['gateFailOpenForms']['forms'][0]
b7 = d['capabilityLimitations'][0]

checks = [
    ('形态1 含「否（不产生假通过）」', '否（不产生假通过）' in g['affectsThisRunGate']),
    ('形态1 含「逐条校验证据」限定', '逐条校验证据' in g['affectsThisRunGate']),
    ('形态1 含 Cap 路径不受影响', 'cap_defs' in g['affectsThisRunGate']),
    ('形态1 含「显式单值别名」', '显式单值别名' in g['affectsThisRunGate']),
    ('B-7 含结构性原因（行级）', '结构性原因（行级）' in b7['behaviorEvidence']),
    ('B-7 含 L512/L515', ('L512' in b7['behaviorEvidence'] and 'L515' in b7['behaviorEvidence'])),
    ('emptyPassGuard 含 targets=N>0', 'targets=N>0' in d['emptyPassGuard']['rule']),
    ('withdrawnClaims 在', bool(d.get('withdrawnClaims'))),
    ('contract.revision=门禁实际', d['contract']['revision'] == '32'),
    ('contract.currentOnDisk 在', 'currentOnDisk' in d['contract']),
]
print('=== 报告 %d B ; verdict=%s ===' % (os.path.getsize(p), d['verdict']))
for label, ok in checks:
    print('  %-32s %s' % (label, '✓' if ok else '✗'))
print('\n  全项通过 =', all(ok for _, ok in checks))
