# -*- coding: utf-8 -*-
"""核查我方产物里关于 `--check-extra` 的措辞是否与 setup-architect ④(c) 一致：
  · 现版单路线闭合 ⇒ "禁用要求"自 rev 29 起已解除
  · 是否启用属**独立决定**（需 budget 池 + 实测）
  · **不得写成 RE-ENABLED**
"""
import io
import os
import re

RUN = 'team/artifacts/acceptance-20260916-dali10'
PAT = re.compile(r'check-extra|check_extra')
print('=== 我方产物中所有 `--check-extra` 相关行 ===')
hits = 0
for dp, dn, fn in os.walk(RUN):
    for f in sorted(fn):
        if not f.endswith(('.md', '.json', '.log', '.py', '.txt')):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, RUN).replace('\\', '/')
        if rel.startswith('review/') or rel.startswith('backups/'):
            continue          # 他人产物 / 备份目录
        try:
            t = io.open(p, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        for i, l in enumerate(t.splitlines(), 1):
            if PAT.search(l):
                print('  %-52s L%-4d %s' % (rel, i, l.strip()[:130]))
                hits += 1
print('  命中 =', hits)

print('\n=== 措辞核查 ===')
bad = []
for dp, dn, fn in os.walk(RUN):
    for f in sorted(fn):
        if not f.endswith(('.md', '.json', '.log', '.txt')):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, RUN).replace('\\', '/')
        if rel.startswith('review/') or rel.startswith('backups/'):
            continue
        try:
            t = io.open(p, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        for i, l in enumerate(t.splitlines(), 1):
            if PAT.search(l) and re.search(r'禁用|不得启用|RE-ENABLED|re-enabled|已启用|enabled', l):
                bad.append((rel, i, l.strip()[:140]))
for rel, i, l in bad:
    print('  %-52s L%-4d %s' % (rel, i, l))
if not bad:
    print('  （无"禁用/不得启用/RE-ENABLED"这类措辞）')
