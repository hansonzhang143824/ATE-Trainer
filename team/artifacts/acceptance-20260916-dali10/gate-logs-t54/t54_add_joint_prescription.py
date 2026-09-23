# -*- coding: utf-8 -*-
"""按 rule-reviewer ①② 的建议并入（幂等）：
  ① 把 §附五 的三行表**升为正文**（而非举例）；
  ② 把其 R3"前置式检查"与我的"共同修法"并成一条**联合处方**（两者是同一处方的两面）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 附五·正文表｜粒度—证据对照（三类并列，可枚举、可对号入座、可追加）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**（rule-reviewer 指出：把三类**并列成表**优于"只讲一例" —— 它**可枚举、可对号入座、可追加**，故升为正文。）**

| 记录 | 它**只**声称的粒度 | 曾被误用来断言 | 真相 |
| --- | --- | --- | --- |
| `preservedPeerKeys` | **键名**存在 | "他方**条目**都在" | 键在、条目只剩 **1** 条（8 条不可复原） |
| `revision` | 一个**自述标签** | "本次运行读的就是**该版内容**" | 无法字节证明（该版文件已不存在） |
| `size` | **字节长度** | "**同一版本/同一内容**" | 换行/缩进/键序即可致差异（CRLF=247 ⟷ 差 247 B） |

### 附五·联合处方（我方"共同修法" × 其方 R3"前置式检查" = 同一处方的两面）

| 面 | 表述 | 出处 |
| --- | --- | --- |
| **证据面** | 断言"条目"⇒ 须**条目级记录**（条目数 + 内容哈希）；断言"读的是某版"⇒ 须**该版字节**；断言"同一内容"⇒ 须 **LF 归一化哈希** | 我方"共同修法" |
| **前置面** | **断言到哪一级，就先跑该级的前置检查**（不满足即**停用该判据**） | rule-reviewer R3 |

> **合起来**：**先声明记录的粒度 → 再要求同级的证据 → 否则降断言或补证据。**

**共同实证来源**：**本 run 的三例** —— ①②（键名/条目、自述标签/字节）、③（size/内容）。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '联合处方', '前置面', '先声明记录的粒度'):
    print('  含 %-20s %s' % (k, k in t2))
