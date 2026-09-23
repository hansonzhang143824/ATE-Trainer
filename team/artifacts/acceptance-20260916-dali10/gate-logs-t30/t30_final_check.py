# -*- coding: utf-8 -*-
"""最终一致性抽检（幂等、只读）。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
checks = [
    ('t30-summary.md',
     os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10/gate-logs-t30/t30-summary.md'),
     ['三情形并列', '[48,60,61,76]', '缺 `{48,76}`', '不得写成"缺 K110"', '不覆盖"pin 归属前提"的正确性']),
    ('t33-transition-plan.md',
     os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t33-transition-plan.md'),
     ['闭集更正', '三情形', '需补的是', '不再是预计路径']),
]
for name, p, keys in checks:
    t = io.open(p, encoding='utf-8-sig').read()
    print('  %s (%d B)' % (name, len(t.encode())))
    for k in keys:
        print('     %-34s %s' % (k[:32], k in t))
