# -*- coding: utf-8 -*-
"""核查：契约现值 + 我产物里是否残留"rev 28 下不成立 / 即使保留也缺 110"这类**因果反向**表述。"""
import hashlib
import io
import json
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
p = RUN + '/setup-contract.json'
d = open(p, 'rb').read()
j = json.loads(d.decode('utf-8-sig'))
print('现盘契约: %d B / %s' % (len(d), hashlib.sha256(d).hexdigest()))
print('  revision =', j.get('revision'))
b = [x for x in j['aliasResolution'] if x.get('alias') == 'bst2sw'][0]
print('  bst2sw =', (b.get('resolution') or {}).get('closedRelayNumbers'))

r = json.load(io.open(RUN + '/build-report.json', encoding='utf-8-sig'))
s = json.dumps(r, ensure_ascii=False)
print('\n=== 报告内检查 ===')
for k in ('rev 28', '不成立', '即使保留', '缺 110'):
    print('  %-10s 出现 = %s' % (k, k in s))
print('  attributionSplit.sideCause 摘录:')
print('   ', r['attributionSplit']['sideCause'][:220])

print('\n=== 我的产物中含该错误表述的文件 ===')
KEY_A = '不成立'
found = []
for root in ('gate-logs-t33', 'gate-logs-t30', 'gate-logs-t54', 'gate-logs-t28'):
    dp = os.path.join(RUN, root)
    if not os.path.isdir(dp):
        continue
    for f in sorted(os.listdir(dp)):
        fp = os.path.join(dp, f)
        if not os.path.isfile(fp):
            continue
        try:
            t = io.open(fp, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        if 'rev 28' in t and (KEY_A in t or '缺 110' in t):
            found.append((os.path.basename(fp), f))
            for i, l in enumerate(t.splitlines(), 1):
                if 'rev 28' in l and (KEY_A in l or '缺 110' in l):
                    print('  %-44s L%-4d %s' % (os.path.basename(fp), i, l.strip()[:150]))
if not found:
    print('  （无）')
