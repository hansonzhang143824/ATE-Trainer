# -*- coding: utf-8 -*-
"""复核 schematic-expert 的"修展开器必须连带修消费者"告诫（解析器-消费者耦合）。

验证三项：
  ① L376 `n = defines[r]` 的**标量假设**；
  ② L401/L403 的 `in` 比较左侧是标量、右侧是**int 集合**；
  ③ 若 defines[r] 变 list/tuple 会发生什么（用最小复现，不改门禁脚本）。
并把结论并入纪律登记。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(WS, 'scripts', 'verify_relay_trace.py')
src = io.open(SRC, encoding='utf-8-sig').read().splitlines()

print('=== ① 标量假设与消费者签名（逐行）===')
for n in (39, 40, 41, 42, 43, 44, 376, 401, 403, 406):
    if n - 1 < len(src):
        print('  L%-4d %s' % (n, src[n - 1].strip()[:120]))

print('\n=== ② on_set/nc_set 的元素类型（生产点 L102-107）===')
for n in range(102, 108):
    if n - 1 < len(src):
        print('  L%-4d %s' % (n, src[n - 1].strip()[:120]))

print('\n=== ③ 最小复现：把 defines[r] 换成 list / tuple 会怎样 ===')
on_set = {154, 155}
for label, val in (('标量 int 154', 154), ('list [154,155]', [154, 155]), ('tuple (154,155)', (154, 155))):
    try:
        r = (val in on_set)
        print('  %-18s ⇒ in 判定 = %-6s %s' % (label, r, '（正常）' if r else '（**恒 False ⇒ 静默漏报**）'))
    except Exception as e:
        print('  %-18s ⇒ **%s: %s** ⇒ 门禁崩（非静默）' % (label, type(e).__name__, e))

print('\n=== ④ 结论（写入纪律登记）===')
print('  `parse_defines()` 的**首值截断**与其消费者（L401/L403/L406）的**标量签名是耦合**的：')
print('   · 改成 list ⇒ `TypeError: unhashable type: list` ⇒ **门禁崩**；')
print('   · 改成 tuple ⇒ `in` 恒 False ⇒ **静默漏报**（更糟）；')
print('   · 要正确修，必须把 L401/L403/L406 改为**逐值循环**。')
print('  ⇒ 这不是"一行正则的 bug"，而是**需要连带改动的小重构**；归 scripts owner，且不得借此改 `gate_baseline.json`。')
