# -*- coding: utf-8 -*-
"""最终全量扫描：我方产物里是否仍残留"relay-trace 不受（截断）影响"这类**已撤回**表述。"""
import io
import os
import re

RUN = 'team/artifacts/acceptance-20260916-dali10'
PAT = re.compile(r'不受影响|不是被截断值造成|未再参与数值比较|未再使用\s*n')
SKIP_EXT = ('.pyc',)
print('=== 扫描（含 .md/.json/.log/.py/.txt/.jsonl）===')
hits = []
for dp, dn, fn in os.walk(RUN):
    for f in sorted(fn):
        if f.endswith(SKIP_EXT):
            continue
        p = os.path.join(dp, f)
        try:
            t = io.open(p, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        for i, l in enumerate(t.splitlines(), 1):
            if PAT.search(l):
                rel = os.path.relpath(p, RUN).replace('\\', '/')
                hits.append((rel, i, l.strip()[:140]))

# 过滤：更正脚本/扫描脚本自身、以及明确写着"已撤回/欠严"的行
clean = []
for rel, i, l in hits:
    if 'fix_' in rel or 'check_' in rel or 'verify_' in rel or 'scan' in rel:
        continue
    if '欠严' in l or '已撤回' in l or '原判词' in l or '而不是"小心地写"' in l:
        continue
    clean.append((rel, i, l))

print('  总命中 %d 行；剔除更正/扫描脚本与已标注撤回者后剩 %d 行：' % (len(hits), len(clean)))
for rel, i, l in clean:
    print('    %-46s L%-4d %s' % (rel, i, l))
if not clean:
    print('    （无）⇒ 已无残留的"不受影响"式表述')
