# -*- coding: utf-8 -*-
"""并入 rule-reviewer ①② 的两条（幂等）：
 ① 其自纠：**"某一部分无效果"不推出"整体无效果"**（部分与整体是两个域）。
 ② 其把我方规则二提升为一般句：**当一次变更同时改动多个变量时，须做拆分实验（每次只换一个变量）**
    —— 否则归因只能靠推断。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附卅一｜"部分无效果"不推出"整体无效果"；多变量变更须做拆分实验'


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

**来源**：rule-reviewer 复核我方拆分实验后**撤回其"v2 是 no-op"**，并自陈其错误所在；
我方则撤回"v1 不稳定"。**双方各撤一半，结论收敛。**

**收敛点（三方一致）**
```
· 排除项 `receipts`：**no-op**（当前正文无该键，属**预防性**）✓
· 序列化口径：v1（去行字节）→ v2（`json.dumps(sort_keys)`）⇒ **是实质变更** ✓
· 故：**"v2 改变了口径"成立**；**"v2 无效果"不成立**；**"v1 不稳定"也不成立** ✓
```

**规则一｜部分与整体是两个域（其自纠）**
> **"某一部分无效果" 不推出 "整体无效果"。**
> 其错误：把"某一项的 no-op"（排除 `receipts`）**推广成"整次变更的 no-op"**，而该次变更**还改了序列化**。
> ⇒ **"部分与整体是两个域"**，与"缺域/缺单位"同族 ✓

**规则二｜多变量变更须做拆分实验（其提升为一般句）**
> **当一次变更同时改动多个变量时，须做**拆分实验**（每次只换一个变量）——否则归因只能靠推断。**
> ⇒ 本 run 实测：**主因是序列化，排除项恰为 no-op** ✓
> ⇒ 我方所做的正是该实验（**两个方向各得一个结论、且各自撤回一半**）✓

**同族（已入册 §附廿八）**：**"声明式 vs 口径式"须逐轴判定** ——
**"属于哪一类"是意图；"哈希变没变"是效果；两者各自需要证据。**
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
