# -*- coding: utf-8 -*-
"""并入 schematic-expert ② 的两条（幂等）：
  ① **第七类：假匹配（假阳性）** —— `prose-substring ≠ structural presence`；
     规则：**存在性判断必须用哨兵常量或结构判据（parse 后测 key/路径），不得用文案里的字符串**；
  ② 原则级结论：**一个文件不能给自己当锚** ⇒ 需**外部收据**。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附六｜第七类：假匹配（假阳性）— 文案串 ≠ 结构存在'


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

**来源**：schematic-expert 用现算**复现了我自曝的一次失误**：
我用 `'build-report.receipt.json' in 生成器文本` 判断"收据写入器是否已存在" —— 而该串**已出现在说明文案里** ⇒ **必然假阳性** ⇒ 跳过追加、收据一度未生成。

**与前六类的方向相反（合起来才是完整的"判断可信性"）**
| 方向 | 类别 | 例 |
| --- | --- | --- |
| **假阴性（漏匹配）** | 第 1–6 类 | `\\bK48\\b` 漏别名；文本搜 `K48` 漏 `K_FPVIH_TO_BST_A`；机械归属跨注释块；`parse_defines` 截断 |
| **假阳性（假匹配）** | **第 7 类（本条）** | **`'X' in 文本` 命中的是"文案里的 X"，而非"结构上的 X 存在"** |

**规则**
> **存在性判断必须用哨兵常量或结构判据**（`parse` 后测 key / 路径 / 字段），
> **不得用文案里的字符串**（`'…' in text`）。
⇒ **配套**：与"**先打印容器与条数、再断言"不存在"**是一对 ——
**前者防假阴性、本条防假阳性**。

**正确做法（我已改用）**：写入器用**哨兵常量** `RECEIPT_WRITER_V1` 判断；结构判据用 `json.loads(...)` 后测 `in dict` / 路径存在。
留证：`gate-logs-t54/t54_fix_receipt_writer.py` / `t54-receipt-writer.log`。

---

## 附六·补｜原则级结论：**一个文件不能给自己当锚**

**来源**：我为此引入**外部收据**（`livenessDeclaration.receiptInstead`），schematic-expert 独立对账通过并认为该句是**原则级**结论。

> **一个文件不能给自己当锚**（写在其内部的"自算哈希"会在下一次写入时立即过期）
> ⇒ 需**外部收据**（`gate-logs-t54/build-report.receipt.json`：每次生成后重算 `size/sha256/sha256_lf_normalized/topLevelEntries/isFrozen`）。
⇒ 与"**指针不得记死 size/hash**"、"**各自只证自己现算过的**"**同源**。
**对账实测**：`receipt.size=29,497`（收据当时）与现盘**逐位一致**；`isFrozen=false`；`topLevelEntries=32` ✓
（注：报告为**活档**，其后我又追加 `baselineTriad` / `gateInputSnapshot` ⇒ **现值见最新收据**。）
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '假阳性（假匹配）', '一个文件不能给自己当锚', '哨兵常量'):
    print('  含 %-22s %s' % (k, k in t2))
