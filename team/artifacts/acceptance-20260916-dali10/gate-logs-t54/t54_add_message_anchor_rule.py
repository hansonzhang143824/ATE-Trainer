# -*- coding: utf-8 -*-
"""并入 schematic-expert ② 的"消息层版本锚"约定（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 纪律 1·补：消息层版本锚（re: <对象> <版本锚>）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B' % os.path.getsize(REG))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

> **每条消息开头标出"我在对哪一版 / 哪一时刻说话"**，例如：
> `re: build-report 28,909 B` ／ `re: setup-contract rev 39` ／ `re: payload 43,806 B / 66abc088…`。

**动因（本 run 实测）**：产物在**一轮之内**就能变形 —— `build-report.json` 走过
13,075 → 15,960 → 21,015 → 22,706 → 25,119 → 27,268 → **28,909 B**；契约 24 → … → **39**；
payload 出现过四个版本。⇒ **"我们在谈同一件事"这句话本身需要版本锚**，
否则互相纠正的其实是**不同时刻各自都正确的结论** —— 本 run 至少发生三次
（**不是谁错，而是没标基准**）。

**与既有纪律的关系**：这是"**同一对象内时点相关字段必须同一基准**"（schematic-expert 提出）
在**消息层**的对应物：**基准不清 ⇒ 更正会打空气。**

**配套**：更正他方结论前，**先读其消息的版本锚**；若其锚 ≠ 你手上的现值 ⇒ **先声明差值，再判对错**。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '消息层版本锚', '不是谁错，而是没标基准', '更正会打空气'):
    print('  含 %-24s %s' % (k, k in t2))
