# -*- coding: utf-8 -*-
"""复核 setup-architect ① 的"peer 值重测"标注：其自有档是否把我方产物标为 peer artifact
（owner=compile-diagnostician、"owner-reported + recomputed by me"），即是否符合其与我共同立的
`provenanceSources` 规则（peer ledger 不得称中立基准）。只读。
"""
import hashlib
import io
import json
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
A = os.path.join(RUN, 'gate-logs-t28', 'setupArchitect-anchors.json')
print('=== 其自有锚点档 ===')
d = open(A, 'rb').read()
J = json.loads(d.decode('utf-8-sig'))
print('  %d B / %s' % (len(d), hashlib.sha256(d).hexdigest()))
txt = json.dumps(J, ensure_ascii=False)
print('  含 build-report.json 条目 =', 'build-report.json' in txt)
print('  含 owner=compile-diagnostician =', 'compile-diagnostician' in txt)
for kw in ('peer artifact', 'recomputed', 'owner-reported', 'citeRule', 'identityRule'):
    print('  含 %-26s %s' % (kw, kw in txt))

# 找该条目并打印其关键字段
def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + '[%d]' % i)
    else:
        yield path, o


print('\n=== 与该 peer 条目相关的键值 ===')
shown = 0
for p, v in walk(J):
    if 'build-report' in str(v) or 'build-report' in p:
        print('  %-58s = %s' % (p[:58], str(v)[:70]))
        shown += 1
        if shown > 14:
            break

print('\n=== 与现盘我方报告的对照（现算）===')
RP = os.path.join(RUN, 'build-report.json')
b = open(RP, 'rb').read()
print('  我方现盘 build-report.json = %d B / %s' % (len(b), hashlib.sha256(b).hexdigest()[:32]))
