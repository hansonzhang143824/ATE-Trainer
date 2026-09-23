# -*- coding: utf-8 -*-
"""把 rule-reviewer ② 的"第二处不同版"结论写入报告（幂等、生成器自有）。

结论（我方实测）：
  · 日志自称 rev=32，期望集 [48,60,61,76,83]；
  · rev 28 快照 bst2sw=[110,61] ⇒ exp=[60,61,83,110]（旧口径）；现盘 rev 39 ⇒ exp=[48,60,61,76,83]；
  · ⇒ ch5 口径出现在 **(rev28, 现盘] 区间**内，rev 32 落在区间 ⇒ **自称与期望集并不矛盾**；
  · ⚠️ 但现存快照**无法**把区间收窄到"恰好 rev 32" ⇒ 该点如实表述；
  · ⚠️ 门禁当初**实际读入的那份 32 号文件已不存在**（无字节快照）⇒ 归属只能到"日志自述 + 区间相容"这一级。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = 'gateExpectationSet'

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B ; 已含 %s = %s' % (os.path.getsize(GEN), MARK, MARK in t))
if MARK in t:
    print('已写入（幂等）')
    raise SystemExit(0)

ANCHOR = "        'bst2sw_closedRelayNumbers': b2['resolution'].get('closedRelayNumbers'),"
INS = ("""        'gateExpectationSet': {
            'value': ['由日志自述取得：TM600 期望 [48,60,61,76,83]'],
            'consistencyCheck': ('rule-reviewer 指出"日志自称 rev=32 但期望集像是 ch5 口径"可能自相矛盾；'
                                 '我方实测：**rev 28 快照的 bst2sw=[110,61]** ⇒ exp=[60,61,83,110]（旧口径），'
                                 '**现盘 rev 39** ⇒ exp=[48,60,61,76,83]。⇒ ch5 口径出现在 **(rev28, 现盘] 区间**内，'
                                 'rev 32 落在该区间 ⇒ **自称与期望集并不矛盾**。'),
            'residualCaveat': ('⚠️ 现存字节快照**无法**把区间收窄到"恰好 rev 32"；且门禁当初**实际读入的那份 32 号文件'
                              '已不存在**（无字节快照）⇒ 该次运行的契约归属只能到'
                              '"**日志自述 + 区间相容**"这一级，不能声称"已用字节证明读的是 rev 32"。'),
            'evidence': 'gate-logs-t54/t54_verify_rev_vs_expectation.py / t54-rev-vs-expectation.log',
        },
""")
if ANCHOR not in t:
    print('ERROR: 锚点未命中')
    raise SystemExit(1)
t = t.replace(ANCHOR, INS + ANCHOR, 1)
io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
print('  已插入 gateExpectationSet → %d B' % os.path.getsize(GEN))

import subprocess
import sys
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    print('  run%d: %s' % (i, (r.stdout or '').strip().replace('\n', ' | ')[:160] if r.stdout else r.stderr[:160]))
