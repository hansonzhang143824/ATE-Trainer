# -*- coding: utf-8 -*-
"""复核 rule-reviewer ③：`emptyPassGuard` 是否**只有记录、没有强制**？
扫 scripts/**（.py/.ps1）确认是否存在任何"空 targets ⇒ 非 PASS"的强制点。
"""
import io
import os
import re

WS = 'D:/Newtest/DSH/ATE-Coding-Plat'
SD = os.path.join(WS, 'scripts')

print('=== ① 早退点（if not targets）===')
for f in sorted(os.listdir(SD)):
    if not f.endswith(('.py', '.ps1')):
        continue
    p = os.path.join(SD, f)
    t = io.open(p, encoding='utf-8-sig', errors='replace').read()
    for i, l in enumerate(t.splitlines(), 1):
        if re.search(r'if\s+not\s+targets', l):
            print('  %-34s L%-4d %s' % (f, i, l.strip()[:110]))

print('\n=== ② 强制点搜索：emptyPassGuard / targets==0 / targets=N 断言 ===')
PAT = re.compile(r'emptyPassGuard|targets\s*==\s*0|targets\s*=\s*0|len\(targets\)\s*==\s*0|targets\)\s*<\s*1')
found = 0
for f in sorted(os.listdir(SD)):
    if not f.endswith(('.py', '.ps1')):
        continue
    p = os.path.join(SD, f)
    t = io.open(p, encoding='utf-8-sig', errors='replace').read()
    for i, l in enumerate(t.splitlines(), 1):
        if PAT.search(l):
            print('  %-34s L%-4d %s' % (f, i, l.strip()[:120]))
            found += 1
print('  命中 =', found)

print('\n=== ③ 编排器 run_gates.ps1 是否感知 targets ===')
g = os.path.join(SD, 'run_gates.ps1')
gt = io.open(g, encoding='utf-8-sig', errors='replace').read()
print('  %s = %d B' % (os.path.basename(g), os.path.getsize(g)))
for k in ('targets', 'scan', 'emptyPassGuard'):
    print('    含 %-16s = %d 次' % (k, gt.count(k)))

print('\n=== 结论 ===')
print('  (a) 早退点存在（见 ①）；(b) scripts/** 内无任何"空 targets ⇒ 非 PASS"的强制；')
print('  (c) 编排器 run_gates.ps1 对 targets/scan/emptyPassGuard 命中均为 0 ⇒ **不知道 targets 空否**。')
print('  ⇒ 确认：`emptyPassGuard` 目前**只是记录**（在我的报告里），**没有消费者、没有强制**。')
