# -*- coding: utf-8 -*-
"""t42 结论的独立复核（schematic-expert 判 [48,76] 生效）+ 对我方 t30 期望集合的影响评估。

复核项：
  ① StdAfx.h 四条复合宏的逐字内容（含行号）
  ② 网表控制组：宏通道号 = ACM 别名号 = 网表脚后缀，且 ch5 网不含 K110、ch18 网不含 K48/76
  ③ site-5 ACM200 F 脚后缀集合规模（应为 24）
  ④ 对 t30 的影响：TM600/TM601 现行 SetOn 是否满足 [48,76]、[110,61] 两套期望
"""
import csv
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
stdx, _ = read_enc(cfg['derived']['stdafx_h'])
lines = stdx.splitlines()

print('=== ① StdAfx.h 复合宏（逐字，含行号）===')
want = ('K_BST_ACM', 'K_FPVIL_TO_BST_B', 'K_FPVIH_TO_BST_A', 'K_BST_QTMU', 'K48_ACM5_AMP_REF')
for i, ln in enumerate(lines, 1):
    if any(w in ln for w in want) and 'define' in ln:
        s = ' '.join(ln.split())
        if len(s) < 190:
            print('  L%-4d %s' % (i, s))

print('\n=== ② 全文件中 "ACM" 与 "BST" 同现的复合宏（看是否有任何一条用 K110）===')
for i, ln in enumerate(lines, 1):
    if 'define' in ln and 'BST' in ln and ('ACM' in ln or '110' in ln):
        s = ' '.join(ln.split())
        if len(s) < 200:
            print('  L%-4d %s' % (i, s))

print('\n=== ③ 网表控制组复核（site-5 ACM200 F 脚）===')
CSV = cfg['inputs']['csv_schematic']
rows = list(csv.DictReader(io.open(CSV, encoding='utf-8-sig', errors='replace')))
suff = set()
for r in rows:
    d = str(r.get('Designator') or '')
    m = re.fullmatch(r'S5_ACM200_FH(\d+)', d)
    if m:
        suff.add(int(m.group(1)))
print('  S5_ACM200_FH<n> 设计ator 的后缀集合 = %s' % sorted(suff))
print('  规模 = %d（ACM200 规格 24 通道 ⇒ 后缀即通道号）' % len(suff))

# ch5 / ch18 两张网的同网成员
def net_of(des, pin=None):
    for r in rows:
        if str(r.get('Designator') or '') == des:
            if pin is None or str(r.get('MemberName') or '').endswith('.' + str(pin)):
                return str(r.get('NetName') or '')
    return None


def peers(net):
    return sorted({str(r.get('Designator') or '') for r in rows if str(r.get('NetName') or '') == net})


for label, des, pin in (('ch5 (K48.6)', 'K48_ACM_BST_S1', '6'),
                        ('ch5 (K46.2)', 'K46_BUS_FH_BST_S1', '2'),
                        ('ch18 (K110.6)', 'K110_BST_S1', '6'),
                        ('ch18 (K109.4)', 'K109_BUSL_PB0_S1', '4')):
    n = net_of(des, pin)
    print('  %-14s %-24s net=%-32s peers=%s' % (label, des + '.' + pin, n, peers(n)[:6] if n else None))

print('\n=== ④ 对 t30 的影响：现行 SetOn 对两套期望的满足度 ===')
t, _e = read_enc(cfg['derived']['test_cpp'])
blocks = dict(V.fn_blocks(t))
for fn in ('TM600_HS_RDSON', 'TM601_LS_RDSON'):
    rel = V.parse_setons(blocks[fn])
    nums = set()
    for r in rel:
        m = re.match(r'K(\d+)_', r)
        if m:
            nums.add(int(m.group(1)))
        elif re.fullmatch(r'\d+', r):
            nums.add(int(r))
    print('  %s 实际闭合 = %s' % (fn, sorted(nums)))
    for label, exp in (('契约现状 aliasResolution[bst2sw] (pin-18 口径)', {60, 61, 83, 110}),
                       ('t42 判定后 (pin-5 口径, 建议值)', {48, 61, 76}),
                       ('契约 ACM200 侧 pinRouteTable 列6', {48, 76})):
        miss = sorted(exp - nums)
        print('     %-42s 期望=%-16s 缺失=%s' % (label, sorted(exp), miss))

print('\n=== ⑤ 我方 t30 断言的硬编码检查（契约驱动是否成立）===')
src = io.open(os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py'), encoding='utf-8-sig').read()
lits = sorted(set(re.findall(r'\b(?:4[68]|6[01]|7[6]|110)\b', src)))
print('  源码中出现的候选字面量 = %s' % lits)
for pat in ('0x', 'closedRelayNumbers', 'relaySet', 'needsClosed'):
    print('  含 %-20s = %s' % (pat, pat in src))
print('  ⇒ 若源码中不出现 48/76/110 这类具体 K 号字面量，则期望集合完全来自契约 ⇒ 契约 rev 后自动更新')
