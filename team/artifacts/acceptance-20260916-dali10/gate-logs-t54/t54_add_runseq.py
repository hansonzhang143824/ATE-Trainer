# -*- coding: utf-8 -*-
"""按 schematic-expert ③ 落地（幂等）：
  **(a) 事件日志需单调序号**：秒级 `at` **既不能排序同秒事件、也不能分离它们** ⇒ 加 `runSeq`（单调递增）。
     同秒内"内容相同"的两次运行 ⇒ 四元组完全相同 ⇒ **状态数是运行次数的下界**（非等值）。
  **(b) `countUnitNote` 的自证须按行计**（"含该字段的行数 = N / M"），不得用"历史行含 = True"这种按文件计的说法。
  **(c) 记录规则**：**从"静态形态"推断"逐次行为"** 与"由意图推值/由位置推归属/由 size 推身份/由名字推文件"同根
     ⇒ **用某个表征去回答它回答不了的问题**；正确方法＝**跑一次、看增量**（行为证据 > 静态形态）。
"""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
H = os.path.join(HERE, 'build-report.receipts.jsonl')
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))

# (a) 加 runSeq
OLD = "_line['lineCount'] = len(_prev_lines) + 1   # **行的条数**（不是状态数）"
NEW = ("_line['lineCount'] = len(_prev_lines) + 1   # **行的条数**（不是状态数）\n"
       "_line['runSeq'] = (len(_prev_lines) + 1)   # **单调序号**：秒级 at 无法分离同秒事件（schematic-expert ③）")
if "'runSeq'" in src:
    print('  runSeq 已含（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已加 runSeq → %d B' % os.path.getsize(GEN))
else:
    # 宽松定位
    i = src.find("lineCount']")
    print('  WARN: 锚点未命中；上下文 =', repr(src[i - 60:i + 120]) if i > 0 else '（未找到）')

# (b) countUnitNote 补一句：状态数是运行次数的**下界**
OLDC = "'⚠️ `at` 只到**秒** ⇒ 同秒两次运行得到**同 at 同 sha** 的两行 ⇒ '\n                      '**同 at 不构成同一性**（见纪律『同一性本身需要证据』）。'"
NEWC = ("'⚠️ `at` 只到**秒** ⇒ 同秒两次运行得到**同 at 同 sha** 的两行 ⇒ '\n"
        "                      '**同 at 不构成同一性**（见纪律『同一性本身需要证据』）。'\n"
        "                      '⚠️ 故 **状态数是运行次数的下界**（非等值）；'\n"
        "                      '**精确的运行计数请用 `runSeq`**（单调序号）；秒级 `at` 不是计数装置。'\n"
        "                      '⚠️ 自证请**按行计**（如“含 countUnitNote 的行数 = N / M”），'\n"
        "                      '**不得用“历史行含 = True”这种按文件计的说法**（否则会被读成“全部含”）。'")
src2 = io.open(GEN, encoding='utf-8-sig').read()
if 'runSeq' in src2 and '状态数是运行次数的下界' in src2:
    print('  countUnitNote 已补（幂等）')
elif OLDC in src2:
    out2 = src2.replace(OLDC, NEWC, 1)
    ast.parse(out2)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out2)
    print('  已补 countUnitNote → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: countUnitNote 锚点未命中（可能已被上一处改写）')
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

# (c) 纪律登记
MARK = '## 附十二｜事件日志需单调序号；秒级时间戳不是计数装置'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('\n  登记已含（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 指出我方 `countUnitNote` 仍缺一句 —— **秒级 `at` 不能承担计数职责**。

**规则**
> **事件日志需要"序号"或"更细的时钟"；秒级时间戳既不能排序同秒事件、也不能分离它们。**
> ⇒ **"状态数"是"运行次数"的**下界**（非等值）**；**精确运行计数须用单调序号**（本 run 已加 `runSeq`）。

**同位：计数口径必须**连同单位**声明，且**度量手段须能分辨目标量
```
本 run 两次同族：① "行数" vs "状态数"；② "按文件计" vs "按行计"
  ⇒ 写法示例（正确）："含 `countUnitNote` 的行数 = N / M"（**按行计**）
  ✗ 反例（会被读成"全部含"）："历史行含 = True"（**按文件计**）
```

**新形态（其自领，提议一并入册）：从"静态形态"推断"逐次行为"**
```
其失误：只看累积文件里的"成对"，就断言"每次运行追加两次"
  但**静态形态无法区分**："1 次追加 × 2 次运行" 与 "2 次追加 × 1 次运行"
⇒ 与"由意图推值""由位置推归属""由 size 推身份""由名字推文件"**同根**：
  **用某个表征去回答它回答不了的问题**（＝"未声明框架/作用域"那一族）
⇒ **正确方法：跑一次、看增量**（**行为证据 > 静态形态**，与本 run 证据分层一致）
```
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入登记 → %d B' % os.path.getsize(REG))

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tl[-1][:55] if tl else (r.stderr or '')[:120]))

lines = [json.loads(l) for l in io.open(H, encoding='utf-8').read().splitlines() if l.strip()]
print('\n=== 自证（按行计）===')
print('  总行数 = %d' % len(lines))
print('  含 countUnitNote 的行数 = %d / %d' % (sum(1 for x in lines if 'countUnitNote' in x), len(lines)))
print('  含 runSeq 的行数 = %d / %d' % (sum(1 for x in lines if 'runSeq' in x), len(lines)))
seqs = [x['runSeq'] for x in lines if 'runSeq' in x]
print('  runSeq 单调递增 = %s（示例 %s…）' % (seqs == sorted(seqs), seqs[:6]))
