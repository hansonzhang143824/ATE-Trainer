# -*- coding: utf-8 -*-
"""核查：我方产物里是否有"把 K109/K110 当作部署态缺失/应闭"的表述（rule-reviewer 要求撤该口径）。"""
import io
import os
import re

RUN = 'team/artifacts/acceptance-20260916-dali10'
PATS = [
    r'部署态.{0,12}缺.{0,6}10[89]',
    r'缺\s*(K)?10[89]',
    r'10[89]/110.{0,10}缺',
    r'缺.{0,10}109/110',
]
print('=== 检索"把 109/110 视为部署态缺失"的表述 ===')
hit = 0
for root in ('gate-logs-t33', 'gate-logs-t30', 'gate-logs-t54', 'gate-logs-t28'):
    d = os.path.join(RUN, root)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        fp = os.path.join(d, f)
        if not os.path.isfile(fp):
            continue
        try:
            t = io.open(fp, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        for i, l in enumerate(t.splitlines(), 1):
            for p in PATS:
                if re.search(p, l):
                    print('  %-42s L%-4d %s' % (f, i, l.strip()[:135]))
                    hit += 1
                    break
print('  命中 =', hit)

print('\n=== 同时确认：我记录的"部署态缺件"清单是否只有 48/76 ===')
for f in ('build-report.json',):
    import json
    r = json.load(io.open(os.path.join(RUN, f), encoding='utf-8-sig'))
    dep = r['attributionThreeStates']['deployed']
    print('  build-report.attributionThreeStates.deployed.tm600_seton =', dep['tm600_seton'])
    print('  state 文字 =', dep['state'][:120])
    print('  含 109/110？ =', ('109' in dep['state'] or '110' in dep['state']))
