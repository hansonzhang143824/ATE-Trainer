# -*- coding: utf-8 -*-
"""并入 schematic-expert ④ 的"修复后必须复验"（与"改前先查消费者"配对），并把失败模式分级写清（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附四｜修复后必须复验（与"改前先查消费者"配对）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B' % os.path.getsize(REG))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 对我"修生成器时一度改出语法错误、随即修回并复验"的处置给出定位。

**失败模式分级（关键，决定"能否被及时发现"）**
| 模式 | 例 | 是否响亮 | 后果 |
| --- | --- | --- | --- |
| **语法错误 / 类型错误** | 我改生成器时多写 `')'`；或把 `defines[r]` 改成 `list` 触发 `TypeError: unhashable type` | **响亮**（立即崩） | **良性** —— 必然被发现 |
| **静默漏报** | 把 `defines[r]` 改成 `tuple` ⇒ `in` **恒 `False`** | **静默** | **最危险** —— 看起来仍 PASS |
⇒ **判据**：**"响亮失败"优于"静默失败"**；设计修复时若两难，宁可让它崩。

**两条成对动作**
- **改前先查**：修任何 helper 前，**先枚举其消费者与其签名假设**（见 §附二：`parse_defines` 的三个消费者都假设标量）。
- **改后复验**：**改动后必须立即复跑**，且**连跑两次取同一结果**（幂等）+ **schema/断言全过**，才算修复完成。
（本次正面实例：我改出语法错误后**立即重跑**、**连跑两次一致**、**schema PASS** ⇒ 处置正确、无遗留。）

留证：`gate-logs-t54/t54_verify_expander_coupling.py` / `.log`、生成器两次重跑一致记录。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '响亮', '静默漏报', '改前先查', '改后复验'):
    print('  含 %-16s %s' % (k, k in t2))
