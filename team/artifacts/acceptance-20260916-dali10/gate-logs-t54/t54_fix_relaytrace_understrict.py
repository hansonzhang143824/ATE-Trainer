# -*- coding: utf-8 -*-
"""更正我方"relay-trace 不受截断影响"的过强表述 → 收紧为"欠严（under-strict）"。幂等。

schematic-expert 报告（我逐行复核成立）：
  L376 n = defines[r]
  L401 if n in on_set:      ← **数值使用**
  L403 if n in nc_set:      ← **数值使用**
  而 r 来自 parse_setons()（原样取 SetOn 实参 token，**不做宏展开**）
  ⇒ 当 SetOn 写**多值宏名**时，只校验 defines[r] 的**首值**那一个继电器
    例：K_FPVIH_TO_PGND_A = 154,155 ⇒ 只校验 154（155 不被校验）；K_FPVIH_TO_BST_A = 46,48,76 ⇒ 只校验 46
"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')

OLD = '**否** —— 其判据只消费 Cap 家族（19 个，多值宏 0）⇒ `relay-trace` 的 PASS 不受影响'
NEW = ('**部分/欠严（under-strict）** —— `cap_defs` 只收录 Cap 家族（多值宏 = 0）⇒ '
       '**Cap 别名↔规范名映射这条路径不受影响**（我原判这条成立）；'
       '但 `n = defines[r]` 在 **L401 `if n in on_set` / L403 `if n in nc_set`** 被**当数字使用**，'
       '而 `r` 来自 `parse_setons()`（**原样取 SetOn 实参、不做宏展开**）'
       '⇒ 当 SetOn 写**多值宏名**时**只校验首值那一个继电器**'
       '（例：`K_FPVIH_TO_PGND_A=154,155` ⇒ 只校验 154；`K_FPVIH_TO_BST_A=46,48,76` ⇒ 只校验 46）')


def patch(path, label):
    if not os.path.isfile(path):
        print('  %-34s MISSING' % label)
        return
    t = io.open(path, encoding='utf-8-sig').read()
    if NEW[:40] in t:
        print('  %-34s 已更正（幂等）: %d B' % (label, os.path.getsize(path)))
        return
    n = t.count(OLD)
    if n == 0:
        print('  %-34s 未找到旧表述（跳过）' % label)
        return
    t = t.replace(OLD, NEW, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(t)
    print('  %-34s 已更正（命中 %d 处，替换 1）: %d B' % (label, n, os.path.getsize(path)))


print('=== 更正受影响产物 ===')
patch(os.path.join(RUN, 'gate-logs-t54', 't54-gate-failopen-forms.md'), 't54-gate-failopen-forms.md')

# 脚本内的同类表述
for f in ('t54_verify_failopen.py', 't54_verify_failopen.log', 't54-failopen-verify.log'):
    patch(os.path.join(RUN, 'gate-logs-t54', f), f)

print('\n=== 收紧后的标准表述（供引用）===')
print('  "`relay-trace` 的 PASS **不是**截断造成的假通过；但其成员性检查（L401/L403）对多值宏**只覆盖首值**')
print('   ⇒ 属**欠严**，**不作为"多值宏逐条校验"的证据**。"')
