# -*- coding: utf-8 -*-
"""按共同纪律（全路径 + size + mtime；不输出哈希字面）核对我需引用的对象现值。

起因为 rule-reviewer 指出我引的三项与现盘不符；本脚本一次给全，供双方对齐。
"""
import datetime
import hashlib
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
ITEMS = [
    ('setup-contract.json', '契约'),
    ('build-report.json', 't54 报告（门禁/编译证据载体）'),
    ('implementation-payload-TM600-TM601.cpp', '候选交付件'),
    ('gate-logs-t28/t28-anchors.json', '单一真源'),
    ('gate-logs-t28/t28-citation-notice.txt', '引用通告'),
    ('gate-logs-t28/t28-summary.md', 't28 报告'),
    ('gate-logs-t30/t30-summary.md', 't30 报告'),
    ('gate-logs-t54/bst-sw.log', 't54 门禁日志'),
    ('gate-logs-t54/run-gates-t54-stdout.log', 't54 门禁汇总'),
]
EXTRA = [
    ('scripts/verify_relay_trace.py', '被审门禁'),
    ('scripts/verify_bst_sw_sequence.py', '被审门禁'),
    ('scripts/gate_baseline.json', '基线（应未改）'),
    ('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp', '部署态（未落盘）'),
    ('D:/PROJECT6-DALI/devel/source/test.cpp', '生产树（只读）'),
]

print('=== run 树内（全路径 + size + mtime）===')
for rel, label in ITEMS:
    p = os.path.join(RUN, rel)
    if not os.path.isfile(p):
        print('  %-52s MISSING' % rel)
        continue
    print('  %-52s %8d B  @%s   %s'
          % ('team/artifacts/acceptance-20260916-dali10/' + rel,
             os.path.getsize(p),
             datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%H:%M:%S'), label))

print('\n=== run 树外 ===')
for rel, label in EXTRA:
    p = rel if os.path.isabs(rel) else rel
    if not os.path.isfile(p):
        print('  %-52s MISSING' % rel)
        continue
    print('  %-52s %8d B  @%s   %s'
          % (rel, os.path.getsize(p),
             datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%H:%M:%S'), label))

# 契约关键字段（决定 t54 期望集）
import json
c = json.loads(open(os.path.join(RUN, 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))
b = [x for x in c['aliasResolution'] if x.get('alias') == 'bst2sw'][0]
print('\n=== 契约关键字段（决定期望集）===')
print('  revision =', c.get('revision'))
print('  aliasResolution[bst2sw].resolution.closedRelayNumbers =',
      (b.get('resolution') or {}).get('closedRelayNumbers'))
print('  …Superseded =', (b.get('resolution') or {}).get('closedRelayNumbersSuperseded'))
