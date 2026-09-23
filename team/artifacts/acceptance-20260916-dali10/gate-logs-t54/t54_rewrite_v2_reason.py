# -*- coding: utf-8 -*-
"""按 rule-reviewer ③ 改写 v2 的**正当理由**（幂等）：
  ✔ 成立：**"v1 只声明排除项、未声明序列化与编码 ⇒ 第三方即便拿到同字节也无法复现"**
  ✘ 修正：删去"history 行 sha 仍在变 ⇒ 排除表不完整"（那是**收据历史文件**的字段，**不是报告正文的 body 输入**）
  ✔ 标注：`receipts` 属**预防性排除**（正文无此键）
"""
import ast
import collections
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))

OLD_NOTE = ("'note': ('跨秒不变；跨版本不可混用 —— 排除表/序列化任一变化都必须换版本号。'\n"
            "                 '**v2 的实质变更是序列化口径**（v1=去行字节；v2=json.dumps sort_keys 重序列化）；'\n"
            "                 '新增的排除项 `receipts` 在当前正文中**不存在** ⇒ 该排除为**预防性**（防将来嵌入）。'),")
NEW_NOTE = ("'note': ('跨秒不变；跨版本不可混用 —— 排除项/序列化/编码任一变化都必须换版本号。'\n"
            "                 '**升 v2 的正当理由＝v1 只声明了排除项、未声明序列化与编码 ⇒ '\n"
            "                 '第三方即便拿到同字节也无法复现 body 哈希** ⇒ 故补 serialization/encoding/bodyDefinition 并升版本。'\n"
            "                 '⚠️ 新增的排除项 `receipts` 在当前正文中**不存在**（正文键路径穷举：0 命中）⇒ '\n"
            "                 '该排除为**预防性**（防将来嵌入），**它本身不构成升版本理由**。'\n"
            "                 '⚠️ 已修正的旧表述：曾以『收据历史 `.jsonl` 各行 sha256 在变 ⇒ v1 排除表不完整』为理由 —— '\n"
            "                 '**该理由不成立**（`.jsonl` 是**收据历史文件**的字段，**不是报告正文的 body 输入**）。'),")
if '升 v2 的正当理由' in src:
    print('  已含（幂等）')
elif OLD_NOTE in src:
    out = src.replace(OLD_NOTE, NEW_NOTE, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已改写 note → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: note 锚点未命中')

ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

print('\n=== 登记：收录"已修正的旧表述" ===')
MARK = '## 附廿一｜v2 正当理由的改写（成立的理由 vs 已修正的旧表述）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer **第三次**给出同一处实测（`projectionSpec`/`receipts`/`hashInvariance` 均**不在报告正文**），
并建议**用真正成立的那条**作为 v2 的正当理由；我方做**决定性机制测试**（分别固定两个变量）后采纳。

**决定性测试（同一字节上，两个变量各跑一遍）**
```
序列化=sort_keys，排除={gen}         = 9804fbe2272477ec…
序列化=sort_keys，排除={gen,receipts} = 9804fbe2272477ec…  ← 现行 v2（**与前一行相同 ⇒ 排除 receipts 是 no-op**）
序列化=去行字节，排除={gen}           = febf9518df45f3aa…  ← 旧 v1
⇒ **(a) 排除项**：在同序列化下**不改变**取值 ⇒ `receipts` 排除为 no-op（**预防性**）
⇒ **(b) 序列化**：**改变**取值 ⇒ **这才是 v1→v2 的口径差** ✓
```
**并复核 v1 的稳定性**：跨秒两次 **v1 恒定**（`febf9518…`）⇒ **"v1 不稳"的旧理由不成立**。

**结论（采纳其建议的改写）**
> **升 v2 的正当理由 ＝ v1 只声明了排除项、未声明序列化与编码 ⇒ 第三方即便拿到同字节也无法复现 body 哈希**
> ⇒ 故补 `serialization`/`encoding`/`bodyDefinition` 并升版本 ✓
> **`receipts` 排除项本身不构成升版本理由**（正文无此键，属预防性）✓

**已修正的旧表述（留痕，防后人据错因推断）**
```
✘ "跨秒生成时 history 行的 sha256 仍在变 ⇒ v1 排除表不完整"
⇒ **不成立**：`.jsonl` 各行 `sha256`/`at` 确实不同，**但那是"收据历史文件"自身的字段**，
  **不是报告正文的 body 输入** ⇒ **两者被混在一起**（我方错误，已撤回）✓
```

**判据（沿用并确认）**：**凡使 body 哈希口径变化的改动都要升版本** ——
**补序列化/编码声明确实改变口径 ⇒ 升版本正确** ✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    print('  run%d: %s' % (i, ' | '.join(tl)[:70]))
rc = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n  note 现文 =', rc['projectionSpec']['note'][:130])
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
