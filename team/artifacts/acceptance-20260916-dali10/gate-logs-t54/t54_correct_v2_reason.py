# -*- coding: utf-8 -*-
"""三方结论修正（我方的两处更正，均须留痕）：
  · rule-reviewer 说"`receipts` 不在报告里 ⇒ v2 是 no-op" —— **后半句被实测否证**：
    v2 **改变了口径**（`fe bf9518…` ≠ `9804fbe2…`），但**改变的原因不是排除 `receipts`，而是序列化方式变了**
    （v1＝**去行字节**（regex 删行）；v2＝**json.dumps sort_keys** 重序列化）。
  · 我原先说"v1 不稳 ⇒ 才升 v2" —— **被实测否证**：v1 跨次**本来就稳定**。
  ⇒ **两处更正**：① `receipts` 排除在当前正文上是 **no-op**（其前半句**对**）；
     ② 版本必须升的**真正理由＝序列化口径变化**（我方原始理由**错**）。
"""
import collections
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.join(RUN, 'build-report.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
REC = os.path.join(HERE, 'build-report.receipt.json')

print('=== 拆分验证：口径变化到底来自"排除项"还是"序列化" ===')
b = open(REPORT, 'rb').read()


def v1_asis(b):        # v1 的真实算法：去 generatedAt 行 + strip（行字节级）
    t = re.sub(r'^\s*"generatedAt": ".*?",\s*$', '', b.decode('utf-8-sig'), flags=re.M).strip()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def serialize(j):
    return hashlib.sha256(json.dumps(j, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


J = json.loads(b.decode('utf-8-sig'))
ex_gen = {k: v for k, v in J.items() if k != 'generatedAt'}
ex_gen_rec = {k: v for k, v in J.items() if k not in ('generatedAt', 'receipts')}
print('  v1 原算法（去行字节）                    =', v1_asis(b)[:24])
print('  去 generatedAt + **sort_keys 重序列化** =', serialize(ex_gen)[:24])
print('  去 generatedAt+receipts + 重序列化      =', serialize(ex_gen_rec)[:24])
print('  （去 gen）vs（去 gen+receipts）相同 =', serialize(ex_gen) == serialize(ex_gen_rec),
      '⇒ `receipts` 排除= **no-op**' if serialize(ex_gen) == serialize(ex_gen_rec) else '')
print('  v1原算法 vs 去gen重序列化 相同 =', v1_asis(b) == serialize(ex_gen),
      '⇒ 差别主因 = **序列化方式**，非排除项' if v1_asis(b) != serialize(ex_gen) else '')

print('\n=== 写入纪律登记（我方两处更正）===')
MARK = '## 附十八｜"升版本"须写清变更的**实质**；且差异须拆分到"排除项 vs 序列化"'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 逐键穷举（343 路径）后指出我方 `projectionSpec` v2 的**理由与工件现状不符**；我方据此做**拆分实验**，结果**双方各有一半成立**。

**事实（我方实测，可复算）**
```
报告顶层键 35、键路径 **343**；含 "receipt" 的路径 **仅 1 个**：`/livenessDeclaration/receiptInstead`（**指针字符串**）
字面 `"receipts"` 出现 **0 次**；`"generatedAt"` **1 次**
· 去 generatedAt（原算法：去行字节）      = febf9518df45f3aa…
· 去 generatedAt（sort_keys 重序列化）    = 9804fbe2272477ec…（＝现行 v2 值）
· 去 generatedAt + receipts（重序列化）   = 9804fbe2272477ec…
⇒ **排除 `receipts` 是 no-op**（其前半句**成立**）；
⇒ **但 v2 确实改变了口径**（`febf9518…` ≠ `9804fbe2…`）—— **原因不是排除项，而是序列化方式**
   （v1＝**去行字节**；v2＝**json.dumps sort_keys 重序列化**）⇒ 其"no-op"结论**后半句不成立**
⇒ 且跨秒两次实测：**v1 本来就稳定**（`febf9518…` 恒定）⇒ **我方"v1 不稳"的理由不成立，撤回**
```

**规则**
> **"升版本"必须写清变更的实质**（"排除项变化" / "序列化变化" / "预防性排除，当前无该键"）——
> **否则后人会据"升了版本"推断"内容口径变了"（而可能没变），或反过来漏判**。

> **差异必须拆分到"排除项 vs 序列化"** —— 二者都会改变 body 值，**混在一起时无法判断哪个是主因**
> （本 run 实测：主因是**序列化**，而排除项恰为 no-op）。

**我方据此的两处更正**
1. `receipts` 的排除在当前正文上 **是 no-op** ⇒ 应标注为**预防性**（防将来嵌入 `receipts`）；
2. 版本必升的**真正理由是序列化口径变化** ⇒ 我方原始因果陈述**撤回**。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

print('\n=== 把"预防性"与"实质"写进 projectionSpec.note（诚实化）===')
src = io.open(GEN, encoding='utf-8-sig').read()
OLD = "'note': '跨秒不变；跨版本不可混用 —— 排除表一变就必须换版本号（v2），不得沿用同名键',"
NEW = ("'note': ('跨秒不变；跨版本不可混用 —— 排除表/序列化任一变化都必须换版本号。'\n"
       "                 '**v2 的实质变更是序列化口径**（v1=去行字节；v2=json.dumps sort_keys 重序列化）；'\n"
       "                 '新增的排除项 `receipts` 在当前正文中**不存在** ⇒ 该排除为**预防性**（防将来嵌入）。'),")
if "'v2 的实质变更是序列化口径'" in src:
    print('  已含（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    import ast
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已写入 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: note 锚点未命中')

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    print('  run%d: %s' % (i, ' | '.join(tl)[:80]))
rc = json.load(io.open(REC, encoding='utf-8-sig'))
print('\n  projectionSpec.note =', rc['projectionSpec']['note'][:120])
print('  body =', rc['reproducibleBodySha256'][:24])
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
