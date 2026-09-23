# -*- coding: utf-8 -*-
"""并入 rule-reviewer ② 的推广（幂等）：
**声明必须出现在"读者会去的地方"** —— 同一约定若被两处引用（报告 + 收据），
则两处都须有声明副本（或一处声明 + 另一处指向），否则"有声明"只在读某一侧时成立。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附十四｜声明必须出现在读者会去的地方（声明的覆盖面 = 使用面）'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 采纳我方一处自纠（`standardTriHash` **只落在收据里、报告侧没有** ⇒ 已补到报告侧），并把它一般化。

**规则**
> **同一约定若被两处引用（报告 + 收据），则两处都须有该声明的副本**（或一处声明 + **另一处显式指向**）——
> **否则"有声明"只在读某一侧时成立。**

**判据**
> **声明的覆盖面必须与使用面一致。**

**归族（同源三条，均为本 run 实证）**
| # | 形态 | 本 run 实例 |
| --- | --- | --- |
| 1 | **记录 ≠ 强制** | `emptyPassGuard` 只是记录、未进脚本/编排器 |
| 2 | **未声明框架/作用域** | `parse_defines` 的截断+消费者标量签名耦合 |
| 3 | **声明 ≠ 在读者会去的地方**（本条） | `standardTriHash` 只在一侧 ⇒ 另一侧读者看不到 |

⇒ 与"**知识在场、但不在读者会去的地方**"同形（亦可类比我方"**第三条分发路径**"：
把读者须知**分发到读者实际会读的入口**，而非仅"某处已存在"）。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
