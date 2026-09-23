# -*- coding: utf-8 -*-
"""在 t33-k110-mechanism.md 顶部插入"本文第 1/2 句已作废"的醒目更正横幅（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MECH = os.path.join(HERE, 't33-k110-mechanism.md')
MARK = '> ⚠️ **更正横幅（2026-09-16，t42/t44 之后）**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(MECH, encoding='utf-8-sig').read()
if MARK in t:
    print('已插入（幂等）: %d B' % os.path.getsize(MECH))
    raise SystemExit(0)

BANNER = (MARK + '\n'
          '> 本文 **§3 第 1 句（"ACM 脚路线由 K110 单独完成、必须 SetOn"）已作废** ——\n'
          '> 依 `t42`（requirements，verdict=pass）与 `t44` 补遗：**`SW12_U1REF_BST_ACM` 是 ACM200 `channel 5`**\n'
          '> ⇒ 到 BST 需 **`K48 + K76`**；**`K110_ACM18_BST` 属另一台仪器 `PB0_BST_ACM`（ch18）**。\n'
          '> 精确表述应为："**K109/K110 属 ch18 路线，不是本案仪器（ch5）的路线**"（本文第 2 句方向仍成立）。\n'
          '> **完整更正见同目录 `t33-k110-mechanism-correction.md`**（含被推翻行的精确 locator 与现行结论）。\n'
          '> 本文其余部分（端子表读数、`K110.4(NC)`/`K110.7(NO)` 引脚标注、K109 与 K110 公共端"同 net ≠ 串联"）**保持不变**。\n\n')

# 插到首个标题之后，便于读者先看到
lines = t.splitlines(keepends=True)
idx = 0
for i, l in enumerate(lines):
    if l.startswith('#'):
        idx = i + 1
        break
out = ''.join(lines[:idx]) + '\n' + BANNER + ''.join(lines[idx:])
io.open(MECH, 'w', encoding='utf-8', newline='').write(out)
t2 = io.open(MECH, encoding='utf-8-sig').read()
print('已插入: %d B / %s' % (os.path.getsize(MECH), sha(MECH)))
print('  含横幅 =', MARK in t2)
print('  含"作废" =', '已作废' in t2)
