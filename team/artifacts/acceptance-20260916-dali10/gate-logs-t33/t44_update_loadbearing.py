# -*- coding: utf-8 -*-
"""更新 t44-count-correction.md §3：不变式"承重状态"随 payload 改版翻转（幂等）。

schematic-expert 实测：现盘 payload 的 TM600 已移除 K109/K110 ⇒ BST 节点只剩 ch5 一个源
⇒ "配对 RELAY_OFF" 由**承重**降为**潜在/良好实践**。同时补他提供的命名层自证（4 条注释）。
"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CORR = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t33', 't44-count-correction.md'))
MARK = '### 3.1 承重状态更新（随 payload 改版翻转）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(CORR, encoding='utf-8-sig').read()
if MARK in t:
    print('已更新（幂等）: %d B' % os.path.getsize(CORR))
    raise SystemExit(0)

ADD = '''

### 3.1 承重状态更新（随 payload 改版翻转）

**触发**：schematic-expert 实测现盘 payload 的 `TM600_HS_RDSON` 已**移除 `K109/K110`**（唯一次 `SetOn` 只闭
`{13,48,57,60,61,76,83,85,126}`）⇒ **BST 节点上只剩 ch5 一个源**。

| 版本 | BST 节点上的源 | "闭 48/76 须与显式 `RELAY_OFF` 成对" 的性质 |
| --- | --- | --- |
| **曾同时闭 `K109/K110` 的中间版本** | ch5（K48/K76）+ ch18（K110） | **承重**（不成对则同时驱动两台源） |
| **现盘版本（K109/K110 已移除）** | **仅 ch5** | **降为"潜在/良好实践"**（不再承重） |

⇒ **凡引用本不变式，必须同时注明版本**；**不得**写成"当前承重"。另：`PB0_BST_ACM` 不驱动（TM600 体内 0 次）
与 `FPVI1.Set(…,FPVIe_RELAY_OFF)` 亦由"必需"降为**双保险/良好实践**。
**§3 的 FACT 不受影响**（`K110.pin4`↔`K76.pin4` 同网、`pin5`↔`pin5` 同网，仍成立）。

### 3.2 命名层旁证（schematic-expert 提供，代码自证）

`K_FPVIH_TO_BST_A` 的 **4 条注释把宏展开写在正文里**（我复核逐字一致）：
```
L7619 / L7730  // FPVI0 High→BST (K_FPVIH_TO_BST_A = K46_BUS0_FH_SW1 + K48_ACM5_AMP_REF + K76_ACM_BST)
L7597 / L7713  // 继电器: FPVI0 High→BST (K_FPVIH_TO_BST_A = K46+K48+K76), FPVI0 Low→SW (K60+K61), ACM200_FH8→SW (共用 K61)
```
⇒ **代码自己写明"FPVIe0→BST 这条腿含 `K48_ACM5_AMP_REF`（= ch5）"**，并解释了 `TM641/TM643`
为何把 ACM ch5 源 `RELAY_OFF` ⇒ **"共用 K48/K76"在代码里三处互相印证**，
**比"仅宏定义存在"强一个层级**（命名层自证）。

### 3.3 版本引用纪律（本文件亦适用）

本文件曾引用的 payload 版本 `6034af71…` / `40,658 B / 5a668fe6…` / `42,998 B / c03632d9…` **均已过期**；
**payload 随时间变动 ⇒ 引用前一律现算**（路径 + size + 现算命令）。
**计数口径同样须标版本**：该 payload 的 `TM600` 体内 `K109`/`K110` 的文本提及（11/20 次）**全部是注释**
（说明"已从本次调用移除"及其理由），**代码层未闭合**——这正是"总提及 ≠ 闭集"的又一实例。
'''

io.open(CORR, 'w', encoding='utf-8', newline='').write(t.rstrip() + ADD)
t2 = io.open(CORR, encoding='utf-8-sig').read()
print('已更新: %d B / %s' % (os.path.getsize(CORR), sha(CORR)))
for k in ('承重状态更新', '降为"潜在/良好实践"', '命名层旁证', '总提及 ≠ 闭集'):
    print('  含 %-22s %s' % (k, k in t2))
