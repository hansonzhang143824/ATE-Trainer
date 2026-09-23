# -*- coding: utf-8 -*-
"""决定性核查：relay-trace 是否把**被截断的多值宏**当判据（schematic-expert 标为 UNKNOWN）。

依据读源码：
  L316  if not re.match(r'^K\\d+_', name) and defines[name] in canon_by_ch:
  L317      cap_defs[pt] = canon_by_ch[defines[name]]
  L376  n = defines[r]
⇒ **只有 `name` 不带通道号（不以 `K\\d+_` 开头）时才使用 defines 值**。
   ⇒ 关键问题：这些"无通道号别名"是否落在**多值宏**里？若是 ⇒ 截断影响判据；若否 ⇒ PASS 不受影响。
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
stdx = _r if isinstance(_r, str) else _r[0]

# 真值表（全量）与截断表
multi, allm = {}, {}
for m in re.finditer(r'#define\s+(K\d*_\w+)\s+((?:\d+)(?:\s*,\s*\d+)*)', stdx):
    nums = [int(x) for x in re.findall(r'\d+', m.group(2))]
    allm[m.group(1)] = nums
    if len(nums) > 1:
        multi[m.group(1)] = nums
parsed = V.parse_defines(stdx)

print('=== 无通道号别名（L316 判据真正使用的集合）===')
chanless = [k for k in allm if not re.match(r'^K\d+_', k)]
print('  无通道号宏总数 =', len(chanless))
in_multi = [k for k in chanless if k in multi]
print('  其中**属于多值宏**的 =', len(in_multi), in_multi[:12])
print('  ⇒ 若为 0/极少 ⇒ relay-trace 的 L317 路径**不依赖多值宏**')

print('\n=== L316 的完整守卫（逐字）===')
src = io.open(os.path.join(WS, 'scripts', 'verify_relay_trace.py'), encoding='utf-8-sig').read().splitlines()
for i in range(310, 320):
    if i - 1 < len(src):
        print('  L%-4d %s' % (i, src[i - 1].strip()[:130]))
print()
for i in range(370, 380):
    if i - 1 < len(src):
        print('  L%-4d %s' % (i, src[i - 1].strip()[:130]))

print('\n=== 结论判定 ===')
if not in_multi:
    print('  ✅ relay-trace 的 L317/L376 只消费**单值宏** ⇒ 截断**不影响其判据** ⇒')
    print('     更正：该 PASS 不是假通过，但**不作为多值宏逐条校验的证据**（L401/L403 只覆盖首值 ⇒ 欠严）。')
else:
    print('  ⚠️ 存在无通道号的多值宏 ⇒ 截断值**可能**进入判据 ⇒ 其 PASS 不足以作该证据。')
    for k in in_multi:
        print('     %-24s true=%-20s parsed=%s' % (k, multi[k], parsed.get(k)))
