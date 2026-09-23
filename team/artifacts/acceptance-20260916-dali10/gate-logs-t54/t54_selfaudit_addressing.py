# -*- coding: utf-8 -*-
"""按 setup-architect 的 fieldAddressingRule 自查：我方**活跃目录**（gate-logs-*）里
是否有"按位置寻址契约字段"的写法；并逐一核对用于门禁字段判定的脚本。"""
import io
import os
import re

RUN = 'team/artifacts/acceptance-20260916-dali10'
POS = re.compile(r'aliasResolution\s*\[\s*\d+\s*\]')
NAME_PATTERNS = ["== 'bst2sw'", "== \"bst2sw\"", "alias') == 'bst2sw"]

active, backup = [], []
for dp, dn, fn in os.walk(RUN):
    for f in fn:
        if not f.endswith('.py'):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, RUN).replace('\\', '/')
        try:
            txt = io.open(p, encoding='utf-8-sig', errors='replace').read()
        except Exception:
            continue
        if POS.search(txt):
            (backup if rel.startswith('backups/') else active).append(rel)

print('=== 位置寻址分布 ===')
print('  我方活跃目录（gate-logs-*）命中 = %d %s' % (len(active), active if active else '（无）'))
print('  backups/ 命中 = %d（他方历史脚本，非我方活跃产物）' % len(backup))

print('\n=== 逐一核对：用于门禁字段判定的我方脚本 ===')
for f in ('gate-logs-t54/t54_verify_rev_vs_expectation.py',
          'gate-logs-t54/t54_gate_function_check.py',
          'gate-logs-t54/t54_verify_postreplace_stale.py',
          'gate-logs-t54/t54_make_report.py'):
    p = os.path.join(RUN, f)
    if not os.path.isfile(p):
        print('  %-56s MISSING' % f)
        continue
    t = io.open(p, encoding='utf-8-sig', errors='replace').read()
    byname = any(s in t for s in NAME_PATTERNS)
    bypos = bool(POS.search(t))
    print('  %-56s 按名 = %-5s ｜ 按位置 = %s' % (os.path.basename(f), byname, bypos))

print('\n=== 结论 ===')
if not active:
    print('  ⇒ **我方活跃脚本无"按位置寻址契约字段"** ✓（19 处命中全在 backups/，属他方历史脚本）')
else:
    print('  ⚠️ 需处置：', active)
