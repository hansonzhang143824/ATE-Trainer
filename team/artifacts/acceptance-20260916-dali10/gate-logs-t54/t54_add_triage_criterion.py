# -*- coding: utf-8 -*-
"""并入 schematic-expert ② 的**分诊判据**（幂等）：给"机制化 vs 下游检查"一个可操作判据，
并用本 run 两个自犯实例做对照 —— 避免滑向"什么都机制化"或"什么都靠自觉"。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 现场违例·分诊判据（schematic-expert 提出，用两个自犯实例对照）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**问题**：§现场违例记录 的元教训说"要么机制化、要么接受违反 + 下游检查"，
但**"要么…要么…"若无判据**，就会滑向两个极端 —— **什么都机制化（成本爆炸）** 或
**什么都靠自觉（静默错误直达交付件）**。

**本 run 两个自犯实例（当对照）**
| 实例 | 失败是否**响亮** | 影响面 | 结论 |
| --- | --- | --- | --- |
| schematic-expert 的**探针错误**（把目录当文件读） | **响亮**（沙箱当场拒／异常立刻暴露，当轮即修） | 极小（只影响那一条命令） | **无需机制化**，下游检查即可 |
| compile-diagnostician 的**计数式错误**（`A−B` 相互抵消 ⇒ 自信地报"3"而非 10） | **静默** | 中（会进入上报清单） | **必须机制化** |

**判据**
> **静默 + 有影响面 ⇒ 机制化；响亮 或 影响面小 ⇒ 接受违反 + 下游检查。**

**落到本 run 的分类**
- 属"**静默**" ⇒ **机制化**：**哈希/锚点**（脚本生成 + 外部收据 + 双哈希）、
  **计数（谓词）**（`(?<!B)` 式否定前瞻、三谓词交叉）、**快照**（三件套 + 链式自证）、**存在性判断**（哨兵常量/结构判据）。
- 属"**响亮**" ⇒ **不必机制化**：**一次性探针／草稿脚本**。

**附带好处（其指出，我方认同）**：这条判据**同时解释了为什么两个自犯的代价天差地别** ——
**不是"谁更认真"，而是"失败模式是否响亮"**。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '静默 + 有影响面 ⇒ 机制化', '响亮', '不是"谁更认真"'):
    print('  含 %-24s %s' % (k, k in t2))
