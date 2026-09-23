# -*- coding: utf-8 -*-
"""并入 rule-reviewer ② 的判据（幂等）：
**"实例复现"不等于"规则重复"** —— 判重复看的是"它被用来支持什么"，不是"它是什么"。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '#### 附七·补充·判据｜「实例复现」≠「规则重复」'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**来源**：rule-reviewer 采纳我方"**同一实例、两个视角**"的消歧写法，并补一条通用判据。

**判据**
> **判重复看的是"它被用来支持什么"，不是"它是什么"。**
> ⇒ **"实例复现"（同一现象出现在两条规则下）≠ "规则重复"**。

**本 run 实例（消歧的标准写法）**
```
§附五 看**记录粒度**：`size` 只声称"**字节长度**"
§附七 看**信号是否指向对象**：`size` **不指向内容**
⇒ **同一实例、两个视角；不是两处重复** ✓
```
**为何这条重要**：**同一实例出现在两条规则下，若不给视角差异，读者会删掉一处** ——
**而两处各有其用**（一个约束"该用什么证据"，一个约束"信号是否指向对象"）。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
for k in (MARK, '实例复现', '它被用来支持什么'):
    print('  含 %-18s %s' % (k, k in t2))
