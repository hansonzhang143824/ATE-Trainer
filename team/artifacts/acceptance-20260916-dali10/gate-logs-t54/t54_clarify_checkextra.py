# -*- coding: utf-8 -*-
"""按 setup-architect ④(c) 澄清 `--check-extra` 口径（幂等）。

要点：禁用要求**自 rev 29 起已解除**；是否启用属**独立决定**（需 budget 池 + 实测）；
本轮**未启用**属"本次核验口径"而非"禁令"；**不得写成 RE-ENABLED**。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = 'checkExtraStance'


def add_marker(t):
    if MARK in t:
        return t, False
    INS = """    'checkExtraStance': {
        'currentRule': ('**禁用要求自 rev 29 起已解除**（本版闭合单路线，多余闭合不再产生）。'
                        '⇒ 是否启用 `--check-extra` 属**独立决定**：需先定义 budget 池并实测，'
                        '**不得顺手打开**，**也不得写成 "RE-ENABLED"**。'),
        'thisRunChoice': ('本轮 t54 **未启用** `--check-extra` —— 这是**本次核验选择走默认判据**，'
                          '**不是**在执行任何现行禁令；故本报告的行文一律为"未启用（本次选择）"。'),
        'whyItMatters': ('`bst-sw` 默认＝**子集判定**（`missing = exp − actual`）⇒ **多余闭合不可见** '
                         '⇒ "GREEN ≠ 闭合集被约束"（见 attributionLimitations[0]）。'),
        'unchanged': '未改门禁脚本、未动 `scripts/gate_baseline.json`（28 B / `021015da…02cb1d`）。',
    },
"""
    anchor = "    'attributionThreeStates': {"
    if anchor not in t:
        return t, False
    return t.replace(anchor, INS + anchor, 1), True


t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B ; 已含 %s = %s' % (os.path.getsize(GEN), MARK, MARK in t))
t2, changed = add_marker(t)
if changed:
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t2)
    print('  已加 checkExtraStance → %d B' % os.path.getsize(GEN))
else:
    print('  无需改（幂等或锚点未命中）')

# 同时把两条可能被误读为"禁令"的措辞加上"（本次选择）"
t3 = io.open(GEN, encoding='utf-8-sig').read()
for old, new in (
    ("'未启用 --check-extra、未动 gate_baseline.json。'", "'未启用 --check-extra（**本次核验选择**；禁用要求自 rev 29 起已解除）、未动 gate_baseline.json。'"),
    ("未改脚本、未启用 --check-extra、未动 gate_baseline.json。',", "未改脚本、**未启用 --check-extra（本次选择）**、未动 gate_baseline.json。',"),
):
    if old in t3 and new not in t3:
        t3 = t3.replace(old, new, 1)
        print('  已澄清措辞: %s…' % old[:40])
io.open(GEN, 'w', encoding='utf-8', newline='').write(t3)

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('\n  重生成:', (r.stdout or '').strip().splitlines()[0] if r.stdout else r.stderr[:150])
