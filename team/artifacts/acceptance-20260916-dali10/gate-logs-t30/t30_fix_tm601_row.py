# -*- coding: utf-8 -*-
"""更正 t30-summary.md：撤掉"TM601 亦受 bst2sw 约束"的误用行，改为两函数分开表述（幂等）。

依据（现盘契约重算，见 t30-rederive-expectation.log）：
  aliasResolution: bst2sw.usedByTm = [TM600, TM1205]（**不含 TM601**）；sw2pgnd.usedByTm = [TM601]
  tmDeltas: TM600.aliasesUsed=['pmid2sw']、TM601.aliasesUsed=['sw2pgnd']
  部署态 TM601 实际 = {13,57,60,61,85,126,154,155} ⊇ sw2pgnd{154,155,60,61} ⇒ **TM601 现行契约下为绿**
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SUM = os.path.join(HERE, 't30-summary.md')
MARK = '**更正（schematic-expert 指出、我重算确认）：TM601 行已撤销**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(SUM, encoding='utf-8-sig').read()
if MARK in t:
    print('已更正过（幂等）: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
    raise SystemExit(0)

OLD = '| **rev 25（`t42`/`t44` 判 ch5 后，`[48,76]` 口径）** | `[48,61,76]` | 部署态**仍缺 `48/76`**（payload 亦缺） | ⇒ **仍 NEW-RED**，属**第二处真缺陷**（TM600 未闭 `[48,76]`），**不是回归、也不是 t29 的错** |'
NEW = ('| **rev 25（`t42`/`t44` 判 ch5 后，`[48,76]` 口径）** | 仅 **TM600**：BST `[48,76]` + SW `[61]` | TM600 部署态**仍缺 `48/76`**（payload 亦缺）；**TM601 不受此期望约束**（其别名是 `sw2pgnd=[154,155,60,61]`，部署态**已满足**） | ⇒ **仅 TM600 仍 NEW-RED**，属**第二处真缺陷**（TM600 未闭 `[48,76]`），**不是回归、也不是 t29 的错** |\n'
       '| 备注 | TM1205 | 契约 `bst2sw.usedByTm` 含 TM1205，但 TM1205 不属本门禁默认作用范围（`--tm-scope`），且其变体通路在契约中**无 `aliasFlatTable` 经查为空** ⇒ 期望不可从契约派生 | 见 §6 超范围发现 |')

if OLD not in t:
    print('ERROR: 未找到待更正的 rev 25 行')
    raise SystemExit(1)
t = t.replace(OLD, NEW, 1)

anchor = '- 取证：`gate-logs-t33/t33_postreplace_expectation.log`'
note = ('- ' + MARK + '**：我方先前的 `t33_postreplace_expectation.log` 把 bst2sw 的期望'
        '套到了 TM601 上（"TM601 pin-5 缺 [48,76]"）——**该行作废**。按现盘契约重算'
        '（`gate-logs-t30/t30-rederive-expectation.log`）：\n'
        '  · `bst2sw.usedByTm = [TM600, TM1205]`、`sw2pgnd.usedByTm = [TM601]`；'
        '`TM601.aliasesUsed=[\'sw2pgnd\']` ⇒ **TM601 现行契约下 `缺失=[]`（绿）**；\n'
        '  · 故 rev 25 后**只有 TM600 需要闭 `[48,76]`**；若把 TM601 也纳入 bst2sw，会产生**假红**，'
        '并可能把实现推向 **t38 已明确移除**的"TM601 ACM 驱动"方向（t38 结论：TM601 的 ACM 驱动**无需**到达 BST）。\n'
        '  · **给 rev 25 的护栏**：修订时**不得**把 TM601 加入 `bst2sw.usedByTm`（其 ACM 变体属别的别名）。\n')
t = t.replace(anchor, note + anchor, 1)
io.open(SUM, 'w', encoding='utf-8', newline='').write(t)
t2 = io.open(SUM, encoding='utf-8-sig').read()
print('已更正: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
for k in ('TM601 行已撤销', 'TM601 不受此期望约束', '给 rev 25 的护栏'):
    print('  含 %-18s %s' % (k, k in t2))
