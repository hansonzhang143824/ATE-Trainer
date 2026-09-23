# -*- coding: utf-8 -*-
"""决定性结论：relay-trace 的判据**只消费 Cap 家族（全部为单值宏）** ⇒ 截断不影响其 PASS。

依据（读源码）：
  L306-313  cap_defs 仅收录 `cap_pin(r) is not None` 的宏 ⇒ 实际只有 `*_Cap` 家族
  L316      `defines[name] in canon_by_ch` —— 此处 `name` 来自 cap_defs（Cap 家族）
  L376 `n = defines[r]` 之后，**L401 `if n in on_set` / L403 `if n in nc_set` 把 n 当数字使用**，而 `r` 来自 `parse_setons()`（原样取 SetOn 实参、不做宏展开）⇒ **多值宏只校验首值** ⇒ 属**欠严（under-strict）**，**不是"不受影响"**；
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

multi, single = set(), set()
for m in re.finditer(r'#define\s+(K\d*_\w+)\s+((?:\d+)(?:\s*,\s*\d+)*)', stdx):
    nums = [int(x) for x in re.findall(r'\d+', m.group(2))]
    (multi if len(nums) > 1 else single).add(m.group(1))
parsed = V.parse_defines(stdx)

print('=== ① 复现其广度结论 ===')
print('  多值宏 = %d ; 单值宏 = %d' % (len(multi), len(single)))
trunc = [k for k in multi if k in parsed]
print('  多值宏中被 parse_defines 收录且截断的 = %d ⇒ 比例 = %d/%d = %.0f%%'
      % (len(trunc), len(trunc), len(multi), 100.0 * len(trunc) / max(1, len(multi))))

print('\n=== ② 判据真正消费的集合（cap_defs 只收录 cap_pin 非空者）===')
cap_like = [k for k in list(multi) + list(single) if V.cap_pin(k) is not None]
cap_multi = [k for k in cap_like if k in multi]
cap_single = [k for k in cap_like if k in single]
print('  cap 家族（cap_pin 非空）总量 =', len(cap_like))
print('  其中**多值宏** = %d %s' % (len(cap_multi), cap_multi[:10]))
print('  其中单值宏     =', len(cap_single))

print('\n=== ③ L316 那个比较的两个操作数 ===')
print("  LHS defines[name]（name ∈ cap_defs ⊆ cap 家族）")
print('  RHS canon_by_ch（键 = 通道号）')
print('  ⇒ 只有当 LHS 是"通道号"时比较才有意义 ⇒ 由 **单值 Cap 宏** 提供（如 K21_VAC_Cap=21）')
ok = (len(cap_multi) == 0)
print('\n=== 结论 ===')
if ok:
    print('  ✅ cap 家族**无多值宏** ⇒ L316 的比较不受截断影响；')
    print('     ⚠️ 更正：n 在 L401/L403 被当数字使用（只校验多值宏首值）⇒ 属**欠严**，不是"不受影响" ⇒')
    print('     该 PASS **不是假通过**，但**不作为多值宏逐条校验的证据**（欠严）。')
else:
    print('  ⚠️ cap 家族含多值宏 ⇒ 截断可能进入判据 ⇒ PASS 不足以作该证据。')
