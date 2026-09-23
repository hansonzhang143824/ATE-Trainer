# -*- coding: utf-8 -*-
"""并入 schematic-expert ② 的综合：把 `corollary`（过去不可补）与 `gateInputSnapshot`（将来可证）
并列成一句 —— **"没做快照的过去不可追，做了快照的将来可证"**。幂等。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = 'epistemicPair'

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器含 %s = %s' % (MARK, MARK in t))
if MARK not in t:
    INS = """        'epistemicPair': {
            'synthesis': ('**没做快照的过去不可追，做了快照的将来可证。**'
                          '（schematic-expert 指出：`corollary` 与 `gateInputSnapshot` 是'
                          '**同一 epistemic 缺陷的"过去"与"未来"两半**，合起来才闭环。）'),
            'past': ('**过去（不可补）**：某个历史修订究竟写了什么，只有**当时的字节快照**能独立说明；'
                     '本 run 唯一幸存的是 rev 28（`[110,61]`）⇒ **24–28 之间的其余状态永久只能靠自述/推断**。'),
            'future': ('**未来（可保）**：`gateInputSnapshot` ⇒ **从下一次运行起**，'
                       '输入的归属由"日志自述"变为"**字节可证**"。'),
            'exception': ('**rev 28 是唯一一次"事后仍可补"的例外** —— 因为当时有人复制了字节'
                          '（`backups/t53-20260916-211719/`，含产物 + 生成器 + 哈希侧车三件套）。'),
            'explains': ('它同时解释了：① 为什么 rev 28 那两条判定能升级为可复核；'
                         '② 为什么下次重跑会自带证据。'),
        },
"""
    anchor = "        'corollary':"
    if anchor not in t:
        # corollary 在 baselineTriad 内，找其父级锚点
        anchor = "            'pairsWith': '本条与 `gateExpectationSet.residualCaveat` 是**同一条 epistemic 边界**，两条并列留档。',"
        if anchor in t:
            t = t.replace(anchor, anchor + "\n        },\n" + INS.rstrip().rstrip(','), 1)
            io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
            print('  已插入（经 pairsWith 路径）→ %d B' % os.path.getsize(GEN))
            raise SystemExit(0)
        print('  ERROR: 锚点未命中')
        raise SystemExit(1)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t.replace(anchor, INS + anchor, 1))
    print('  已插入 → %d B' % os.path.getsize(GEN))

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成末行:', (r.stdout or '').strip().splitlines()[-1][:80] if r.stdout else (r.stderr or '')[:150])
