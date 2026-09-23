# -*- coding: utf-8 -*-
"""把 rule-reviewer 裁定的对照实验结果写入报告（幂等）：证明 (ii)，并明确不涉及 (iii)。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = 'unionPreservationExperiment'

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器含 %s = %s' % (MARK, MARK in t))
if MARK not in t:
    INS = """    'unionPreservationExperiment': {
        'ruledBy': 'rule-reviewer（裁定"做一次"，并要求用**第三方前缀**以真正走到并集路径）',
        'design': ('**离线副本**上放入 3 条键到**第三方命名空间** `qaProbeAnchors`'
                   '（**非** `setupArchitect-` 前缀 ⇒ 才走"他方键 ⇒ 并集累积"那条路径），'
                   '随后跑生成器，再现算结果。'),
        'result': {
            'qaProbeAnchors.anchors': 3,
            'allThreeKept': True,
            'setupArchitectFreezeAnchors.anchors': 1,
            'protectedNamespaceUntouched': True,
            'generatorExit': 0,
        },
        'conclusion': ('**(ii) 不丢当前内容：成立**；且**第三方前缀同样走并集路径** '
                       '⇒ 该机制**不限于**受保护前缀。'),
        'mustNotBeCitedAs': ('⚠️ **不得**引作 **(iii) 恢复历史** 的证据 —— 那 8 条无字节副本，'
                             '属**原理上不可测**。'),
        'restored': '实验后**已还原活档**（含 PROBE 检查 = False ⇒ 真源未被污染）。',
        'evidence': 'gate-logs-t54/t54-reviewer-experiment-union.log（1,448 B，含副本路径/键名/条数/跑后现算）',
    },
"""
    anchor = "    'withdrawnClaims': ["
    if anchor not in t:
        print('ERROR: 锚点未命中')
        raise SystemExit(1)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t.replace(anchor, INS + anchor, 1))
    print('  已插入 → %d B' % os.path.getsize(GEN))

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成:', (r.stdout or '').strip().splitlines()[-1][:80] if r.stdout else (r.stderr or '')[:150])
