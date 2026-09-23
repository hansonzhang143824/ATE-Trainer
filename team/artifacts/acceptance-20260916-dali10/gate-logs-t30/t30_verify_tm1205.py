# -*- coding: utf-8 -*-
"""复核 Captain ③ 的 TM1205 证据 + 全契约穷举 aliasFlatTable 类结构（只读）。

Captain 主张：TM1205 部署态 `test.cpp:8791` 闭 `K_FPVIH_TO_SW1_A`+`K_FPVIL_TO_BST1_A`；
`:8835` 闭变体 SW2/BST2；期望来源在契约 `aliasFlatTable[14]/[15]`。
我此前在 `tmDeltas.TM1205.aliasFlatTable` 只查到 0 条 ⇒ 本脚本做**穷举**，定位该字段究竟在哪。
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
C = json.loads(open(os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10',
                                 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))

print('=== ① 部署态 TM1205 段落逐行（K_FPVIH_TO_SW*/K_FPVIL_TO_BST*）===')
with open(cfg['derived']['test_cpp'], 'rb') as f:
    t = f.read().decode('utf-8-sig', errors='replace')
lines = t.splitlines()
for ln in (8791, 8835):
    if 0 < ln <= len(lines):
        print('  L%-5d %s' % (ln, ' '.join(lines[ln - 1].split())[:190]))
    else:
        print('  L%-5d <超出>' % ln)

print('\n  TM1205 函数体内所有 SetOn（含别名→StdAfx 展开）:')
import verify_relay_trace as V  # noqa: E402
defs = V.parse_defines(V.read_enc(cfg['derived']['stdafx_h']))
blk = dict(V.fn_blocks(t))['TM1205_TRX_BST_UV_GD']
start = t.index(blk)
base = t.count('\n', 0, start) + 1
for m in re.finditer(r'cbite\.SetOn\(([^;]*)\);', blk):
    ln = base + blk.count('\n', 0, m.start())
    args = [a.strip() for a in m.group(1).split(',') if a.strip() and a.strip() != '-1']
    expanded = []
    for a in args:
        d = defs.get(a)
        expanded.append('%s=%s' % (a, d) if d is not None else a)
    print('    L%-5d %s' % (ln, ', '.join(expanded)))

print('\n=== ② 穷举契约中所有 "aliasFlatTable"（含嵌套）===')
found = []


def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            if 'aliasflattable' in str(k).lower() or 'flattable' in str(k).lower():
                n = len(v) if isinstance(v, (list, dict)) else 'n/a'
                found.append((path + '/' + str(k), n))
            walk(v, path + '/' + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + '[%d]' % i)


walk(C, '$')
if found:
    for p, n in found:
        print('  找到: %-60s 条数=%s' % (p, n))
else:
    print('  **契约中不存在任何 aliasFlatTable / flatTable 字段**')

print('\n=== ③ 穷举含 bst1_sw1 / bst2_sw2 / BST1 / BST2 的键或值 ===')
pat = re.compile(r'bst1[_\-]?sw1|bst2[_\-]?sw2|BST1|BST2', re.I)
hits = []


def walk2(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            s = '%s=%s' % (k, json.dumps(v, ensure_ascii=False)[:120] if not isinstance(v, (dict, list)) else '')
            if pat.search(str(k)) or (not isinstance(v, (dict, list)) and pat.search(str(v))):
                hits.append(path + '/' + s[:160])
            walk2(v, path + '/' + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk2(v, path + '[%d]' % i)


walk2(C, '$')
print('  命中数 = %d' % len(hits))
for h in hits[:15]:
    print('   ', h[:180])
if not hits:
    print('  **契约中不存在任何 bst1_sw1 / bst2_sw2 / BST1 / BST2 字样**')

print('\n=== ④ 结论 ===')
print('  · Captain/对方给的"期望来源 aliasFlatTable[14]/[15]"在**现盘契约 rev 24**中**不可复核**；')
print('  · 但 TM1205 的实际通路（别名展开）可在 StdAfx.h 侧复核（见上表）；')
print('  · 事实层面仍成立：`bst2sw.usedByTm` 收 TM1205 属**登记错项**（BST1/BST2 ≠ BST），')
print('    且 TM1205 **不在**本门禁默认作用范围内 ⇒ **当前不产生假红**。')
