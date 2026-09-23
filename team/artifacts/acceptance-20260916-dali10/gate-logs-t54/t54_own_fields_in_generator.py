# -*- coding: utf-8 -*-
"""使所有"后加字段"成为**生成器自身**的字段（防再被整篇重写丢掉）。

背景：`t54_make_report.py` 会**整篇重写** build-report.json ⇒ 任何事后 patch 进去的字段
（`emptyPassGuard` / `withdrawnClaims` / `capabilityLimitations` 增强 / `gateFailOpenForms` 等）
都会在下次生成时**静默消失**（实测已发生两次）。
本脚本把缺失项以**幂等**方式补进生成器源码（插到 `'builds': [{` 之前）。
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')

INSERT = '''    'emptyPassGuard': {
        'rule': ('**t54 的 PASS 须同时满足 `[scan] targets=N>0`；否则该 PASS 为空跳（未执行断言）。**'
                 '（schematic-expert 提出；Captain 已把 B-7 记为门禁能力局限。本条为可执行验收格式。）'),
        'rationale': ('`verify_bst_sw_sequence.py` L497-499：`if not targets: print(…空 PASS); return 0` '
                      '⇒ 空集时**契约闭合断言整段被跳过**却仍 exit 0 ⇒ "exit 0"本身不足以证明检查已执行。'),
        'counterExample': ('`--src <候选payload>`（只含 TM600/TM601）⇒ 日志无 `targets=`，'
                           '而是"无 rampi_capv 电流斜坡测试项 … 空 PASS" / exit 0 ⇒ **空跳，不得计为通过**。'),
        'evidenceThisRun': {
            'gateLog': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/bst-sw.log',
            'note': ('本轮 t54 的 bst-sw 日志含 `[scan] targets=4`（>0）⇒ **契约闭合断言确已执行**，'
                     '故该次 NEW-RED 是真判定、不是空跳。'),
        },
    },
'''

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B' % os.path.getsize(GEN))

need = []
if "'emptyPassGuard'" not in t:
    need.append('emptyPassGuard')
if "'withdrawnClaims'" not in t:
    need.append('withdrawnClaims')
if "'gateFailOpenForms'" not in t:
    need.append('gateFailOpenForms')
if "'attributionThreeStates'" not in t:
    need.append('attributionThreeStates')
if "'exitZeroSemantics'" not in t:
    need.append('exitZeroSemantics')
print('  生成器缺失的字段 =', need or '（无）')

anchor = "    'builds': [{"
if anchor not in t:
    print('  ERROR: 未找到插入锚点')
    raise SystemExit(1)

if 'emptyPassGuard' in need:
    t = t.replace(anchor, INSERT + anchor, 1)
    print('  已插入 emptyPassGuard（生成器自有）')

io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
print('  → 生成器现 %d B' % os.path.getsize(GEN))

# 复查
t2 = io.open(GEN, encoding='utf-8-sig').read()
for k in ('emptyPassGuard', 'withdrawnClaims', 'gateFailOpenForms', 'attributionThreeStates',
          'exitZeroSemantics', 'capabilityLimitations', 'attributionSplit', 'controls'):
    print('    %-24s 生成器含 = %s' % (k, ("'%s'" % k) in t2))
