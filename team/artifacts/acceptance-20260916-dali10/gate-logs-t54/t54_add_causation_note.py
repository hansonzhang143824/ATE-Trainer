# -*- coding: utf-8 -*-
"""并入 rule-reviewer ② 的归属补充（幂等）：
该条教训之所以**能被发现**，是因为**我方拒绝采信其合并推断** ⇒ **"独立复核能拦住错误口径"本身值得留档**。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '**成因留档（rule-reviewer 建议）**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''：
> 本条（"撤回的粒度也必须与其越界的粒度一致"）**之所以能被发现**，是因为
> **我方拒绝采信 rule-reviewer 的"键保留 ⇒ 条目保留"合并推断**（并请其据实更正）。
> ⇒ **若当时采信，这条教训不会被发现** —— 故**"独立复核能拦住错误口径"这一价值**同样值得留档。

**本 run 该争点的全过程留痕（供台账引用）**
```
rule-reviewer 裁定（过简） → 其撤回（**同样过简**） → 我方复核"键 ≠ 条目"
  → 我方请其据实更正 → 三方收敛为**两段式**
```
⇒ 这既是 **"更正本身也会过简"的最好实例**，也是 **三方各自独立复核的价值证明**。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '独立复核能拦住错误口径', '同样过简'):
    print('  含 %-22s %s' % (k, k in t2))
