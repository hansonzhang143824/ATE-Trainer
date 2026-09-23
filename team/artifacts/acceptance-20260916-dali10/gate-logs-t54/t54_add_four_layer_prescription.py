# -*- coding: utf-8 -*-
"""并入 rule-reviewer ② 的**四层处方**（幂等）：防重复插入 / 结构状态判断的分层手段。
采纳其结论：**层④ 作最终判据、层③ 作发现手段、层② 替代层① 作判断依据**。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附九｜结构状态判断的四层处方（防重复插入 / 防"靠文本记号判断"）'


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

**来源**：rule-reviewer 由我方一次自曝（**哨兵串 = `读序提示（层级）`，而落盘 markdown 实为 `` `读序提示（层级）` ``（含反引号）** ⇒
哨兵不匹配 ⇒ 脚本误判"未并入" ⇒ 第二次运行**重复插入同一节**；已去重并做全节检查）推出。

**四层手段**
| 层 | 手段 | 在本次的作用 |
| --- | --- | --- |
| ① | **哨兵常量** | 我最初用的 —— **被 markdown 反引号一字之差破坏** |
| ② | **结构判据**（`parse` 后测 key / 路径 / 标题存在，而非文本包含） | 本应替代 ① 作**判断依据** |
| ③ | **幂等复跑**（跑两次比对） | **本处正是它抓出来的** ✓（发现手段） |
| ④ | **全节唯一性检查**（本次：13 节各 1 次；reviewer 复核：28 标题全唯一） | **最终判据** ✓ |

**处方（采纳其结论）**
> **防重复插入：用「层④ 全节唯一性检查」作最终判据，用「层③ 幂等复跑」作发现手段，
> 用「层② 结构判据」替代「层① 哨兵」作判断依据。**

**判据**
> **"靠文本记号判断结构状态"必败；结构状态须用结构判据。**（与 R3"前提式检查"同源。）
⇒ 理由：**哨兵是自由文本，容易被 markdown 语法或一字之差破坏**（本 run 已实测）。

**族的归并**：本实例属 **§附七**同族（**存在性/状态检查指向"信号"而非"对象"**）——
只是此处"信号"是**一段自由文本**，而非键名/字段名。

**该族对双方都适用（本 run 实证）**
- 我方：8 处自纠中**两处**正是"层① 哨兵/记号"式失误；
- 他方：**先测他方引用数（0）再动**（`t57`）属"层②/③"的正确应用。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '全节唯一性检查', '靠文本记号判断结构状态', '四层'):
    print('  含 %-24s %s' % (k, k in t2))
# 结构自检：各节唯一
import re
hits = t2.count(MARK)
print('  该节出现次数 = %d（应为 1）' % hits)
