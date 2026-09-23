# -*- coding: utf-8 -*-
"""按 schematic-expert ③ 落地（幂等）：
**账本的追加策略必须被写下** —— 否则"链条停止增长"会被读成"这些小时没有运行"，
而新策略下**运行可以发生而有意不记**。
  落地：收据新增兄弟字段 **`appendPolicy`**（不改任何历史行、不改任何值）。
  判据（其建议）：**"账本的追加策略是其语义的一部分 ⇒ 策略变化必须与语义同时声明"**。
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

ANCHOR = "    'countUnitNote': ("
NEW = ('''    'appendPolicy': ('**本账本仅在身份（body 哈希，`projectionSpec` 口径）变化时追加**；'
                     '**因此"一段时间无增长"不等于"无运行"** —— 新策略下**运行可以发生而有意不记**。'
                     '**运行计数一律查 `runSeq`**（单调序号）。'
                     '⚠️ 本策略于本轮启用；此前（1–54 行）为**旧制度：每次运行都追加** ⇒ '
                     '故 **54 行里只有 5 个身份**，且**行数 ≠ 运行次数**（新旧两段口径不同）。'),
''' + ANCHOR)
if "'appendPolicy'" in src:
    print('  appendPolicy 已含（幂等）')
elif ANCHOR in src:
    out = src.replace(ANCHOR, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已加 appendPolicy → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')

ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    print('  run%d: %s' % (i, ' | '.join(tl)[:70]))

rec = json.load(io.open(os.path.join(HERE, 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  收据键 =', list(rec.keys()))
print('  appendPolicy 在 =', 'appendPolicy' in rec)
print('  文 =', rec.get('appendPolicy', '')[:150])

print('\n=== 按候选措辞搜检（其用于证明"0 命中"的那组）===')
H = os.path.join(HERE, 'build-report.receipts.jsonl')
REC = os.path.join(HERE, 'build-report.receipt.json')
blob = io.open(H, encoding='utf-8').read() + io.open(REC, encoding='utf-8').read()
for k in ('identity change', 'only when', 'append only', '仅身份', '身份变化', '变化才追加', 'appendPolicy', '无增长'):
    print('  %-18s 命中 = %d' % (k, blob.count(k)))

print('\n=== 规则入册 ===')
MARK = '## 附廿二｜账本的追加策略是其语义的一部分，必须与语义同时声明'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 按候选措辞逐一搜检（`identity change`/`only when`/`append only`/`仅身份`/`身份变化`/`变化才追加`）
⇒ **全部 0 命中** ⇒ **"仅在身份变化时追加"这一行为，链条与收据里没有一处声明**。

**为什么会咬人（具体、可检）**
```
旧制度：**"无新行" ⇒ "无运行"**（成立）
新制度：**运行可以发生而有意不记** ⇒ **"无新行" ≠ "无运行"** ✗
⇒ 读者看到"链条停止增长"，会得出"**这些小时没有运行**"——而事实是**运行发生了、只是未记** ✓
```
`countUnitNote` 已答"**哪一行算同一身份**"与"**精确运行数用 `runSeq`**"，**但没有答"什么时候才会新增一行"** ⇒
**缺的正是追加策略本身**。

**规则**
> **账本的追加策略是其语义的一部分 ⇒ 策略变化必须与语义同时声明。**

**落地**：收据新增兄弟字段 **`appendPolicy`**（**只增不翻**：不改任何历史行、不改任何值）✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
