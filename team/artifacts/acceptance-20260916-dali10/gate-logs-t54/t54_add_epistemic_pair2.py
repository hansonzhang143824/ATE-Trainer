# -*- coding: utf-8 -*-
"""把 `epistemicPair`（过去不可追／将来可证）并入 `baselineTriad` 内（幂等，锚点明确）。"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = 'epistemicPair'

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B ; 已含 %s = %s' % (os.path.getsize(GEN), MARK, MARK in t))

ANCHOR = "            'pairsWith': '本条与 `gateExpectationSet.residualCaveat` 是**同一条 epistemic 边界**，两条并列留档。',"
if MARK in t:
    print('  已含（幂等）')
elif ANCHOR in t:
    INS = ANCHOR + """
            'epistemicPair': {
                'synthesis': ('**没做快照的过去不可追，做了快照的将来可证。**'
                              '（`corollary` 与 `gateInputSnapshot` 是同一 epistemic 缺陷的'
                              '"过去"与"未来"两半，合起来才闭环 —— schematic-expert 指出。）'),
                'past': ('**过去（不可补）**：某历史修订究竟写了什么，只有**当时的字节快照**能独立说明；'
                         '本 run 唯一幸存的是 rev 28（`[110,61]`）⇒ 24–28 之间其余状态**
                         永久只能靠自述/推断**。'),
                'future': ('**未来（可保）**：`gateInputSnapshot` ⇒ **从下一次运行起**，'
                           '输入的归属由"日志自述"变为"**字节可证**"。'),
                'exception': ('**rev 28 是唯一"事后仍可补"的例外** —— 因为当时有人复制了字节'
                              '（`backups/t53-20260916-211719/` 三件套）。'),
            },"""
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t.replace(ANCHOR, INS, 1))
    print('  已插入 → %d B' % os.path.getsize(GEN))
else:
    print('  ERROR: 锚点未命中')
    sys.exit(1)

r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成:', (r.stdout or '').strip().splitlines()[-1][:80] if r.stdout else (r.stderr or '')[:200])
