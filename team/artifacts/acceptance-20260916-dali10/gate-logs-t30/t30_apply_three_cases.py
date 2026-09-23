# -*- coding: utf-8 -*-
"""更新我方三份文档以符合 Captain 的最终口径（幂等）：
  A) t30-summary.md §4.5 —— 两口径表 → **三情形表**（rev24+t29 / rev25 未同批 / rev25+payload 同批）
  B) 闭集更正：BST–SW 应为 **[48,60,61,76]**（BST 侧 ∈ ACM200 族 [48,76]；SW 侧 ∈ FPVIe[L] 族 [60,61]）
     —— 把文中的 [48,61,76] 更正为 [48,60,61,76]，并写明"红色叙事目标 = 缺 [48,76]"
  C) t33-transition-plan.md —— 同步三情形 + 闭集数字
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T30 = os.path.join(HERE, 't30-summary.md')
T33 = os.path.join(HERE, '..', 'gate-logs-t33', 't33-transition-plan.md')
MARK = '三情形表（Captain 定的最终口径）'
MARK2 = '闭集更正（Captain 2026-09-16）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ---------- A) t30-summary.md ----------
t = io.open(T30, encoding='utf-8-sig').read()
if MARK in t:
    print('[A] t30-summary 已更新过（幂等）')
else:
    old_head = '**转绿条件取决于契约口径（Captain 令：两口径并列，不得单写"转绿"）**：'
    new_head = ('''**转绿条件取决于契约口径 —— 三情形并列（Captain 定的最终口径）**：

| 情形 | 契约期望（TM600） | 落盘后判定 |
| --- | --- | --- |
| **rev 24（现状）+ 落 t29 payload** | `[60,61,83,110]` | t29 补 `110` 后 `缺失=[]` ⇒ **GREEN**（原预期成立；但该契约字段跨族无效） |
| **rev 25（BST 侧 `[48,76]`）而 payload 未同批改** | `[48,60,61,76]` | TM600 仍缺 `[48,76]` ⇒ **仍 NEW-RED = 第二处真缺陷（非回归、非 t29 之错）** |
| **rev 25 + payload 同批（Captain 裁定 (i)，本 run 实际分支）** | `[48,60,61,76]` | payload 同批补 `K48/K76` ⇒ **期望 GREEN**；**不存在"落盘后仍红"的例外路径** |

''' + MARK2 + '''**：BST–SW 闭集应为 **`[48,60,61,76]`**（不是我先前给的 `[48,61,76]`）——
**BST 侧 ∈ ACM200 族 `[48,76]`、SW 侧 ∈ FPVIe[L] 族 `[60,61]`**；这台仪器是**跨域复合**设计。
⇒ "ch5 `[48,76]`" 指 **BST 侧**（正确）；但**门禁期望应为两侧并集 `[48,60,61,76]`**。
⇒ TM600 现盘已闭 `{60,61}`、**缺 `{48,76}`** ⇒ **红色叙事的目标 = "缺 `48/76`"，不得写成"缺 K110"**。
（现算核对：`gate-logs-t30/t30_check_closureset.py` → `t30-check-closureset.log`；部署态已闭 `{60,61,83,13,57,85,126}`，相对该并集缺 `{48,76}`。）''')
    if old_head not in t:
        print('  ERROR: 未找到 §4.5 表头')
    else:
        t = t.replace(old_head, new_head, 1)
        # 其余处 [48,61,76] → [48,60,61,76]
        t = t.replace('期望集合 `[48,61,76]`', '期望集合 `[48,60,61,76]`')
        t = t.replace('修正后契约期望集 `[48,61,76]`', '修正后契约期望集 `[48,60,61,76]`')
        t = t.replace('`[48,61,76]`', '`[48,60,61,76]`')
        io.open(T30, 'w', encoding='utf-8', newline='').write(t)
        print('[A] t30-summary 已更新: %d B / %s' % (os.path.getsize(T30), sha(T30)[:16]))
        t2 = io.open(T30, encoding='utf-8-sig').read()
        print('   含三情形表 =', MARK in t2, '| 含闭集更正 =', MARK2 in t2,
              '| 残留 [48,61,76] =', ('`[48,61,76]`' in t2))

# ---------- C) t33-transition-plan.md ----------
tp = io.open(T33, encoding='utf-8-sig').read()
if MARK in tp:
    print('[C] transition-plan 已更新过（幂等）')
else:
    a = '**据此更新的落盘后期望**'
    add = ('''**闭集更正（Captain 2026-09-16）**：BST–SW 闭集 = **`[48,60,61,76]`**
（BST 侧 ∈ ACM200 族 `[48,76]`；SW 侧 ∈ FPVIe[L] 族 `[60,61]`）。
**三情形**：rev24+t29 ⇒ GREEN；rev25 未同批 ⇒ 仍 NEW-RED 且**红因是"缺 [48,76]"**；rev25+payload 同批 ⇒ 期望 GREEN（本分支）。

''' + a)
    if a not in tp:
        print('  ERROR: transition-plan 锚点未命中')
    else:
        tp = tp.replace(a, add, 1).replace('`[48,61,76]`', '`[48,60,61,76]`')
        io.open(T33, 'w', encoding='utf-8', newline='').write(tp)
        print('[C] transition-plan 已更新: %d B / %s' % (os.path.getsize(T33), sha(T33)[:16]))
