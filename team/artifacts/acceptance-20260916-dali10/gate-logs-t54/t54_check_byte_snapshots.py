# -*- coding: utf-8 -*-
"""核实纪律 #3：run 树里现有哪些快照/备份可作"字节副本"（哈希不可复原，字节才可）。"""
import hashlib
import io
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
print('=== run 树中的快照/备份类目录 ===')
snaps = []
for dp, dn, fn in os.walk(RUN):
    base = os.path.basename(dp)
    if any(k in base for k in ('backup', 'snapshot', 'frozen', 't53-', 'pret')):
        n = len(fn)
        total = sum(os.path.getsize(os.path.join(dp, f)) for f in fn if os.path.isfile(os.path.join(dp, f)))
        snaps.append((os.path.relpath(dp, RUN), n, total))
for s in sorted(snaps):
    print('  %-58s %3d 文件 / %8d B' % s)
print('  共 %d 个快照类目录' % len(snaps))

print('\n=== 判据：被覆写的版本是否还有**字节副本**可复核？ ===')
probes = [
    ('setup-contract.json 旧版(354,106 / rev28 / 含[110,61])',
     ['backups/t53-20260916-211719/setup-contract.json']),
    ('setup-contract.json 旧版(328,805 / rev24 / fd00a508…)', []),
    ('payload union 版(6034af71…)', []),
    ('payload 版(39,457 / 2d0984d9…)', []),
    ('payload 版(42,998 / c03632d9…)', []),
]
for label, cands in probes:
    found = []
    for c in cands:
        p = os.path.join(RUN, c)
        if os.path.isfile(p):
            found.append('%s (%d B)' % (c, os.path.getsize(p)))
    # 全树按 size 再找一次
    print('  %-56s ⇒ %s' % (label, ('有：' + '; '.join(found)) if found else '**无字节副本（不可复核）**'))

print('\n=== 全树按"已知旧尺寸"搜索 ===')
sizes = {328805: 'setup-contract rev24', 354106: 'setup-contract rev28', 42998: 'payload c03632d9',
         39457: 'payload 2d0984d9'}
hits = {k: [] for k in sizes}
for dp, dn, fn in os.walk(RUN):
    for f in fn:
        p = os.path.join(dp, f)
        try:
            s = os.path.getsize(p)
        except Exception:
            continue
        if s in sizes:
            hits[s].append(os.path.relpath(p, RUN))
for s, lbl in sizes.items():
    print('  %-30s (%7d B) ⇒ %s' % (lbl, s, hits[s] or '**0 命中**'))
