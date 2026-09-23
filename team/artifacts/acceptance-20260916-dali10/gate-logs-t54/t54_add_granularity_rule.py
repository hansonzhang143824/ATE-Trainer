# -*- coding: utf-8 -*-
"""并入 rule-reviewer ① 自述的错误类型 → 一条**可推广**纪律：
**记录的粒度必须与其所声称的事实粒度一致**（`preservedPeerKeys` 声称"键"，不能用来断言"条目"）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附五｜记录的粒度必须与所声称的事实粒度一致'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 撤回自己一条裁定后，**自行给出了错误的类型学**（本 run 少见的"自证其误"）；
我复核其裁定确实错误、其类型学成立，故记为**可推广纪律**。

**规则**
> **记录的粒度必须与其所声称的事实粒度一致。**
> 用一个"**只声称到 A 粒度**"的记录，去断言"**B 粒度（更细）**"的事实 ⇒ **结论无效**。

**本 run 实例（同一族的三个形态）**
| 记录 | 它**只**声称的粒度 | 被误用来断言 | 真相 |
| --- | --- | --- | --- |
| `preservedPeerKeys`（键名清单） | **容器/键名**存在 | "他方**条目**都在" | **键在、条目只剩 1 条**（8 条不可复原） |
| `revision`（版本号） | 一个**自述标签** | "本次运行读的就是**该版内容**" | 无法字节证明（该版文件已不存在） |
| `size`（字节数） | **字节长度** | "**同一版本/同一内容**" | 换行/缩进/键序即可致差异（CRLF=247 ⟷ 差 247 B） |
⇒ **共同修法**：**断言到哪一级，就要求该级的证据** ——
要断言"条目"，须有**条目级记录**（条目数 + 内容哈希）；要断言"读的是某版"，须有**该版字节**；
要断言"同一内容"，须有 **LF-normalized 哈希**（见纪律 2·补）。

**配套动作**：**写结论前先问"我这条记录声称到哪一级？"**；若声称粒度 < 断言粒度 ⇒ **要么补证据、要么降断言**。

**佐证（两侧独立收敛的第二个实例）**：`setup-architect` 在其自有账本用
`selfAnchor.{ledgerSizeBytesBeforeThisWrite, ledgerSha256BeforeThisWrite, entriesBeforeThisWrite}`
逐条记录"**写入前自身状态**"；我在 `t28-anchors.snapshots` 用 `lineCount/prevLineSha256/ledger_self_sha256`
链式自证 ⇒ **两侧独立收敛到同一形态、可互相核**（第一个实例＝"只增快照账本"本身）。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '记录的粒度', '要么补证据、要么降断言', '两侧独立收敛'):
    print('  含 %-22s %s' % (k, k in t2))
