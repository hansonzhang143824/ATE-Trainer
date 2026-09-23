# -*- coding: utf-8 -*-
"""把 schematic-expert ② 的建议落成 `build-report.gateInputSnapshot`（机制已实测）。

要点：**跑门禁前，把该次运行的输入固化为字节快照** ⇒ 归属从"日志自述"升级为"字节可证"。
不改脚本、不动基线（纯 copy）。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = 'gateInputSnapshot'

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器已含 %s = %s' % (MARK, MARK in t))
if MARK not in t:
    INS = """    'gateInputSnapshot': {
        'status': ('**已机制验证（本轮实测通过）** —— 但**尚未在真实重跑中执行**（该次运行还未发生）。'),
        'rule': ('**跑门禁前，把该次运行的输入复制到** `backups/<task>-<timestamp>-gateinputs/` **并与门禁日志同放**。'
                 '⇒ 该次运行的归属从"**日志自述**"升级为"**字节可证**"。'),
        'why': ('正是纪律 3 的补救手段，只是**把应用对象从"被覆写的产物"扩展到"每次门禁运行的输入"**；'
                '将来若被质疑"那次到底读的是哪一版"，**有字节可证**，不必再靠日志自述。'),
        'tool': 'gate-logs-t54/t54_snapshot_gate_inputs.py（`python <script> <task-tag> [--dry-run]`）',
        'captures': ['setup-contract.json（门禁读取的契约）',
                     'implementation-payload-TM600-TM601.cpp（候选交付件）',
                     'scripts/gate_baseline.json（基线，应始终 28 B）'],
        'mechanismEvidence': ('本轮机制测试：dry-run 先冒烟（不写盘）→ 真跑一次 ⇒ 生成 '
                              '`backups/t54-mechtest-20260916-231923-gateinputs/`；'
                              '核对三项快照与源**逐位一致**（377,694 / 43,806 / 28 B）✓'),
        'cost': '零风险（两条 copy）；**不改任何脚本、不改门禁、不动基线**。',
        'appliesTo': 't54 的最后一次重跑（落盘后）。',
    },
"""
    anchor = "    'livenessDeclaration': {"
    if anchor not in t:
        print('ERROR: 锚点未命中')
        raise SystemExit(1)
    t = t.replace(anchor, INS + anchor, 1)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
    print('  已插入 → %d B' % os.path.getsize(GEN))

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成末行:', (r.stdout or '').strip().splitlines()[-1][:100] if r.stdout else r.stderr[:150])
