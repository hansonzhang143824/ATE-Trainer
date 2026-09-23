# -*- coding: utf-8 -*-
"""复核 schematic-expert 的"截断器"爆炸半径 + **自行追清 relay-trace 是否把截断值当判据**（其标为 UNKNOWN）。

三问：
  1) StdAfx.h 的多值宏是否 100%（209/209）被 parse_defines 截断？
  2) parse_defines 的调用点是否只在 verify_relay_trace.py？
  3) **关键**：relay-trace 的判据是否消费这些截断值？（若是 ⇒ 其 PASS 不足以作"多值宏路线"的证据）
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
_r = V.read_enc(cfg['derived']['stdafx_h'])
stdx = _r if isinstance(_r, str) else _r[0]          # 兼容两种返回签名（str 或 (text, enc)）

print('=== ① 多值宏是否 100% 被截断 ===')
# 真值：任何 #define K*_<name> <number>[,<number>...]
multi = {}
for m in re.finditer(r'#define\s+(K\d*_\w+)\s+((?:\d+)(?:\s*,\s*\d+)*)', stdx):
    nums = [int(x) for x in re.findall(r'\d+', m.group(2))]
    if len(nums) > 1:
        multi[m.group(1)] = nums
parsed = V.parse_defines(stdx)
trunc = [k for k in multi if str(k) in parsed and not isinstance(parsed[k], (list, tuple))
         and parsed[k] != multi[k]]
print('  多值宏总数 =', len(multi))
print('  其中被解析成"非全量"的 =', len(trunc))
for k in list(multi)[:6]:
    print('     %-22s true=%-16s parsed=%s' % (k, multi[k], parsed.get(k)))

print('\n=== ② parse_defines 的调用点（全 scripts/ 扫描）===')
hits = []
for f in sorted(os.listdir(os.path.join(WS, 'scripts'))):
    if not f.endswith('.py'):
        continue
    t = io.open(os.path.join(WS, 'scripts', f), encoding='utf-8-sig', errors='replace').read()
    if 'parse_defines' in t:
        n = t.count('parse_defines')
        hits.append((f, n))
        for i, l in enumerate(t.splitlines(), 1):
            if 'parse_defines' in l:
                print('  %-32s L%-4d %s' % (f, i, l.strip()[:110]))
print('  含该符号的文件 =', hits)
print('  verify_bst_sw_sequence.py 是否使用 =', 'parse_defines' in io.open(
    os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py'), encoding='utf-8-sig').read())

print('\n=== ③ 关键：relay-trace 是否把 defines 值当判据 ===')
src = io.open(os.path.join(WS, 'scripts', 'verify_relay_trace.py'), encoding='utf-8-sig').read().splitlines()
# 找 cap_defs 构建与消费
for pat in ('cap_defs', 'defines[', 'defines.get', 'K_'):
    print('  --- 含 %-12s 的行 ---' % pat)
    c = 0
    for i, l in enumerate(src, 1):
        if pat in l and c < 6:
            print('     L%-4d %s' % (i, l.strip()[:120]))
            c += 1
