# -*- coding: utf-8 -*-
"""并入 rule-reviewer ② 的方法学教训（幂等）：
**"更正"本身也会过简** ⇒ 撤回某结论时，**只撤回越界的那一步，不得整条推翻**；
**两段式更正写法**：先写"哪一步越界"，再写"哪一部分仍成立"。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 附五·补二 — 更正本身也会过简（两段式更正写法）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**来源**：rule-reviewer 自领 —— 其对同一条争议**先错一次、再错一次（方向相反）**：
第一次过度断言（键层证据 → 条目层结论）；**第二次又把"键层推断越界"错当成"整条结论错误"**，
于是给出过简的"我错了、你对"；**精确结论是两段式**（键在／条目内容只 1 条）。

**规则**
> **"更正"本身也会过简** ⇒ **凡撤回某结论时，只撤回越界的那一步，不得整条推翻**。
> **两段式更正写法**：**先写"哪一步越界"，再写"哪一部分仍成立"**。

**与附五主条的关系（同一条纪律的两面）**
| 面 | 表述 |
| --- | --- |
| 正向（主条） | **记录的粒度必须与其所声称的事实粒度一致** |
| 反向（本条） | **撤回的粒度也必须与其越界的粒度一致** |
⇒ 合起来：**证据/更正的粒度必须覆盖所断言的事实**（键层证据不得支持条目层断言；size 不得支持身份；记录不得支持强制）。

**本 run 最终口径（两段式，三方一致）**
```
(1) 键：共享生成器**确实保留**他方命名空间的**顶层键**（实测在档）
(2) 条目内容：被保留的**内容只有 1 条**（唯一 = 'acceptance-report.json'）；
    此前 8 条**不在其中、全树无副本** ⇒ 不可复原
```
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '只撤回越界的那一步', '两段式更正写法', '撤回的粒度'):
    print('  含 %-22s %s' % (k, k in t2))
