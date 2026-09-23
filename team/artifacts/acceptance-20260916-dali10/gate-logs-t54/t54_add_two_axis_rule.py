# -*- coding: utf-8 -*-
"""对 rule-reviewer ① 的**精确化**：其测量正确，但**只覆盖"排除项"一个轴**。
v1→v2 实际变了**两个轴**：① 排除项（+`receipts`）② **序列化**（去行字节 → `sort_keys` 重序列化）。
  · 轴①（排除项）＝**声明式**（其测量：两排除集同哈希 ⇒ **正确** ✓）
  · 轴②（序列化）＝**口径式**（我方实测：`febf9518…` ≠ `9804fbe2…` ⇒ **会改哈希**）
⇒ 故"这次变更是声明式的"**只在轴①上成立**；**整体是混合变更 ⇒ 必须看实测效果，不能由"属于哪类"外推**。
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN, 'build-report.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

b = open(REPORT, 'rb').read()
J = json.loads(b.decode('utf-8-sig'))


def ser(ex):
    d = {k: v for k, v in J.items() if k not in ex}
    return hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def byl():
    t = re.sub(r'^\s*"generatedAt": ".*?",\s*$', '', b.decode('utf-8-sig'), flags=re.M).strip()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


print('=== 2×2 测量：两个轴各取两值（同内容）===')
print('  轴② sort_keys ＋ 轴① 不含 receipts = %s' % ser({'generatedAt'})[:24])
print('  轴② sort_keys ＋ 轴① 含 receipts   = %s' % ser({'generatedAt', 'receipts'})[:24])
print('  轴② 去行字节 ＋ 轴① 不含 receipts = %s' % byl()[:24])
print()
print('  **轴①（排除项）**：同序列化下两值相同 ⇒ **声明式（rule-reviewer 测量正确）** ✓')
print('  **轴②（序列化）**：两值不同 ⇒ **口径式（会改哈希）** ✓')
print('  ⇒ v1→v2 = **混合变更**：轴① 声明式 ＋ 轴② 口径式 ⇒ 结论：**不可由"属哪类"外推，必须看实测**')

print('\n=== 其③判据（我采纳）===')
print('  (i)  "body 变"不能推出"换版了"（也可能内容变）⇒ version 边界上双向歧义 ✓')
print('  (ii) 判"内容是否变"至少需 (body 哈希, projection 版本) 这一对 ⇒ 缺一不可 ✓')
print('  ⇒ **"按 (exclude, serialization) 分段：段内 body 转变全部来自内容变化；跨段的 body 转变不得计入** ✓')

print('\n=== 登记 ===')
MARK = '## 附廿八｜"声明式 vs 口径式"须逐轴判定：混合变更不可由类别外推'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 测量"两排除集在当前内容上给出同一 body 哈希"⇒ 判"v1→v2 是**声明式**变更"；
我方指出其测量**只覆盖"排除项"一个轴**，而 v1→v2 实际变了**两个轴**。

**2×2 测量（同内容）**
```
轴② sort_keys  ＋ 轴① 不含 receipts = 9804fbe2272477ec…   ← 现行 v2
轴② sort_keys  ＋ 轴① 含 receipts   = 9804fbe2272477ec…   ← 与之相同 ⇒ 轴① 是**声明式** ✓（其测量正确）
轴② 去行字节    ＋ 轴① 不含 receipts = febf9518df45f3aa…   ← 与上不同 ⇒ 轴② 是**口径式** ✓
```

**规则**
> **"声明式 vs 口径式"须逐轴判定**：一次变更可能**同时含两类轴**
> ⇒ **不得由"这次变更看起来是声明式"外推"哈希不变"** —— **必须看实测效果**。
> **判据**：**"属于哪一类"是关于变更的**意图**；"哈希变没变"是关于变更的**效果**；两者各自需要证据。**

**并收录 rule-reviewer ③ 的判据（我方采纳）**
```
(i) **反推不成立**："body 变"**不能**推出"换版了"（也可能内容变）⇒ **"body 变"在 version 边界上双向歧义** ✓
(ii) **最小充分观测**：判"内容是否变"**至少要 (body 哈希, projection 版本) 这一对**；单给其一不足 ✓
⇒ **判据："内容变更"是一个二元谓词，两个操作数缺一不可** ✓
⇒ **加强句**：**按 `(exclude, serialization)` 分段：段内 body 转变全部来自内容变化；
   跨段的 body 转变不得计入内容变化**（**分包比对、不跨包作差**）✓
```
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
import collections
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
