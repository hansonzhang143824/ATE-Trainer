# -*- coding: utf-8 -*-
"""（三引号常量，彻底避开引号嵌套）并入 rule-reviewer 三条建议：
  ① `mustNotBeCitedAs` 升为通用约定；② 第二条结论；③ 标准三哈希。
"""
import ast
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))
changed = []

# ② 第二条结论（插在 conclusion 之前）
OLD2 = "        'conclusion': ('**(ii) 不丢当前内容：成立**；且**第三方前缀同样走并集路径** '"
NEW2 = '''        'secondaryConclusion': {
            'claim': '**第三方前缀（非 `setupArchitect-`）同样走并集累积路径** ⇒ 该机制**不限于**受保护前缀。',
            'whyItMatters': ('解释了**为什么该机制对一般他方键也安全**：'
                             '`DO_NOT_TOUCH_PREFIXES` 只管『直通保留』，**并集逻辑对所有他方键生效**。'),
            'notedBy': 'rule-reviewer：该结论是其『必须用第三方前缀』设计约束的**正当性证明**（不只方法学必要）。',
        },
''' + OLD2
if 'secondaryConclusion' in src:
    print('② 已含（幂等）')
elif OLD2 in src:
    src = src.replace(OLD2, NEW2, 1)
    changed.append('secondaryConclusion')
else:
    print('② WARN: 锚点未命中')

# ③ 标准三哈希
OLD3 = "    'hashInvariance': {"
NEW3 = ('''    'standardTriHash': ('**活档产物的标准三哈希**（rule-reviewer 建议；用途不同、不可互换）：'
                        '① `sha256` = **身份**（逐字节同盘）；'
                        '② `sha256_lf_normalized` = **跨序列化可比重**（行尾无关）；'
                        '③ `reproducibleBodySha256` = **幂等判定**（剔除 `generatedAt`、跨次可比）。'),
''' + OLD3)
if 'standardTriHash' in src:
    print('③ 已含（幂等）')
elif OLD3 in src:
    src = src.replace(OLD3, NEW3, 1)
    changed.append('standardTriHash')
else:
    print('③ WARN: 锚点未命中')

if changed:
    ast.parse(src)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(src)
    print('  已加入 %s → %d B' % (changed, os.path.getsize(GEN)))
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

# ① 通用约定 → 登记
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 通用约定｜凡实验结果，必附『不得引作什么』（`mustNotBeCitedAs`）'
t = io.open(REG, encoding='utf-8-sig').read()
print('\n① 登记已含 =', MARK in t)
if MARK not in t:
    BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 采纳我方 `mustNotBeCitedAs` 字段并建议**升为通用约定**。
> **许证据、禁越权**：**同一份实验结果，既可用作其证明范围内的证据，又明文列出『不得引作哪些结论的证据』。**

**本 run 实例（`build-report.unionPreservationExperiment.mustNotBeCitedAs`）**
```
(ii)  不丢当前内容        ← **可用**（行为级：3 条他方条目跑生成器后全在）
(iii) 恢复历史            ← **不得**（那 8 条无字节副本、原理上不可测）
(iv)  历史 8→1 丢失的原因  ← **不得**（本实验只测当前生成器行为）
```
**理由**：实验结果的意义**受其时域与设计约束**；不写"禁用范围"，读者极易把它外推到
"历史原因"或"恢复能力"上 —— 正是本 run `revision`/`size`/`preservedKey` 同族越权的另一形态。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tl[-1][:60] if tl else (r.stderr or '')[:120]))
