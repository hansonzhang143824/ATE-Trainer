# -*- coding: utf-8 -*-
"""并入 schematic-expert ③ 的**阈值**修正（幂等）：
采信的成本阈值 —— **② 绝不能当 ① 用**；**阈值是成本，不是方便**；**采信 ≠ 免责**。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 纪律 2·补二 — 采信的成本阈值（② 不得当 ① 用）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**来源**：schematic-expert 对"各自只证自己现算过的"分栏做法的**阈值补充**。

**三态必须可区分**
| 态 | 含义 | 可否当"独立验证"用 |
| --- | --- | --- |
| **①** | 我**亲自现算** | 是 |
| **②** | **采信生产者的自算**（非独立验证） | **否** |
| **③** | **无人复算** | 否 |
⇒ **引用时必须知道自己在哪一态；② 绝不能当 ① 用。**

**阈值是"成本"，不是"方便"**
> 若**复算成本极低**（例：对一个 20 KB 的 Markdown 跑一次 `sha256` 就是一条命令），
> **就没有理由采信二手值 —— 直接现算**；
> 只有**成本高**（如需重跑长流水线）才退回"**采信 + 标注非独立**"。

**采信 ≠ 免责**
> **登记了"采信"仍负重锚义务** —— 任何采信值若他日产物被改，**仍会产生陈旧引用**。
⇒ 故 **② 的适用范围应缩到"复算成本不可接受"的少数情形**。

**本 run 实证（我方已据此把三处 ② 转为 ①）**：对我方/他方三个 Markdown 的哈希，一次脚本即可现算
⇒ 直接现算并核对一致（`t42-acm200-pin-attribution.md` 19,351 B / `t44-t42-addendum.md` 16,257 B /
`t45-t42-timing-addendum.md` 8,978 B，**三者与申报一致**）—— **不必采信**。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '② 绝不能当 ① 用', '成本', '采信 ≠ 免责'):
    print('  含 %-18s %s' % (k, k in t2))
