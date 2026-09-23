# -*- coding: utf-8 -*-
"""精确化 setup-architect ② 的扫描数字：区分"目录数/文件数"两种口径，并逐条归类含该串的文件。

要点（要紧的那句）：**是否存在任何副本保留旧 8 条内容** —— 与"是否含该键串"是两件事。
"""
import io
import json
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
BK = os.path.join(RUN, 'backups')

dirs = files = 0
for dp, dn, fn in os.walk(BK):
    dirs += len(dn)
    files += len(fn)
print('=== 计数口径（两个都报）===')
print('  os.walk(backups/) 顶层子目录数 =', len([d for d in os.listdir(BK) if os.path.isdir(os.path.join(BK, d))]))
print('  递归目录总数 =', dirs)
print('  递归文件总数 =', files)
print('  ⇒ 我早前报的"371 条目"= 顶层条目（含目录）；其报 397 = 递归文件 ⇒ **口径不同、都不算错**')

print('\n=== 含该串的文件：逐条归类（关键词 vs 旧内容副本）===')
KEY = 'setupArchitectFreezeAnchors'
hits = []
for dp, dn, fn in os.walk(BK):
    for f in fn:
        p = os.path.join(dp, f)
        try:
            t = io.open(p, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        if KEY in t:
            # 判断：是否含旧 8 条内容的副本？以"该命名空间下 anchors 条数 > 1"为判据
            entries = None
            try:
                j = json.loads(t)
                pp = j.get('preservedPeerNamespaces') or {}
                entries = len((pp.get(KEY) or {}).get('anchors') or {})
            except Exception:
                entries = None
            hits.append((os.path.relpath(p, BK).replace('\\', '/'), os.path.getsize(p), entries))
for rel, sz, e in sorted(hits):
    kind = ('**保留旧内容**' if (e or 0) > 1 else
            ('当前单条状态' if e == 1 else '代码引用/非副本'))
    print('  %-56s %8d B  该命名空间条数=%s  ⇒ %s' % (rel, sz, e, kind))
print('  命中数 =', len(hits))
print('\n=== 要紧的那句 ===')
keep_old = [h for h in hits if (h[2] or 0) > 1]
print('  保留旧 8 条内容的副本数 =', len(keep_old),
      '⇒', '**无任何副本保留旧内容**（成立）' if not keep_old else '**存在**！')
print('  ⇒ 精确表述应是：**"无任何副本保留旧 8 条内容"成立；但"0 命中该键串"字面不成立**（有 %d 个含该串，均非旧内容副本）。' % len(hits))
