# -*- coding: utf-8 -*-
"""复核 schematic-expert 的"空目标集 fail-open"分析（比我的 B-7 更硬）+ 记录三类门禁 fail-open 形态。

关键验证：`--tm-scope` 是否真救不了？（他说 scope 来自 resolve_scope()、与 targets 无关，
但早退发生在断言之前 ⇒ 应救不了）
"""
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')
PAY = os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10',
                   'implementation-payload-TM600-TM601.cpp')

src = io.open(SRC, encoding='utf-8-sig').read().splitlines()
print('=== ① 逐字 locator 复核（他给的 L490/497-499/502/515）===')
for n in (259, 490, 497, 498, 499, 502, 506, 507, 515):
    if n - 1 < len(src):
        print('  L%-4d %s' % (n, src[n - 1].strip()[:135]))

print('\n=== ② derive_targets 的筛选条件（L96-114）===')
for i in range(96, 115):
    if i - 1 < len(src):
        print('  L%-4d %s' % (i, src[i - 1].strip()[:130]))

print('\n=== ③ 行为验证：--tm-scope 能否救回空 targets？===')
for args in ([], ['--tm-scope', 'TM600_HS_RDSON,TM601_LS_RDSON']):
    r = subprocess.run([sys.executable, SRC, '--src', PAY] + args,
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = (r.stdout or '').strip().splitlines()
    print('  args=%-46s exit=%-3s 首行=%s' % (' '.join(args) or '(默认)', r.returncode,
                                             out[0][:90] if out else '(空)'))
print('  ⇒ 若两次都"空 PASS / exit 0" ⇒ **--tm-scope 救不了**（早退在断言之前），与其分析一致')

print('\n=== ④ 与文件自身原则的冲突（L506-507 逐字）===')
print('  ' + ' '.join(src[505].strip().split())[:140])
print('  ' + ' '.join(src[506].strip().split())[:140])
print('  ⇒ 原则"缺失必须红而不是静默跳过"只落实在"契约读不到"这条路径上；')
print('     "目标集为空"这条路径**仍静默跳过并 PASS** ⇒ **同一条原则只落实一半**。')

print('\n=== ⑤ 本 run 三类门禁 fail-open 形态（schematic-expert 归纳，我复核）===')
rows = [
    ('1', '展开器静默截断', 'verify_relay_trace.parse_defines()：209/209 多值宏被截为首值',
     '我复核 ✓（Cap 映射路径不受影响；**但 L401/L403 对多值宏只校验首值 ⇒ 欠严**，非「不受影响」）'),
    ('2', '子集判定', 'missing = exp − actual：多余闭合不可见（未启用 --check-extra）',
     '我复核 ✓（Captain 已令写入 attributionLimitations："GREEN ≠ 闭合集被约束"）'),
    ('3', '空目标集 fail-open', 'targets=[] ⇒ "空 PASS" + exit 0，契约闭合断言整段被跳过',
     '我复核 ✓（B-7；本轮实测 --src 候选 payload 得空 PASS，且 --tm-scope 无效）'),
]
for i, name, mech, ok in rows:
    print('  %s) %-16s %s\n      复核：%s' % (i, name, mech, ok))
print('\n  主题一致：**要 fail-closed**。三者的护栏方向：① 先测展开器再信展开；')
print('  ② 若需约束闭合集须显式启用 --check-extra 并定义 budget；③ 空 targets 应 FAIL 或强制记录 targets=N(N>0)。')
