# -*- coding: utf-8 -*-
"""落实 setup-architect ②③：
  ② 引用他方档时标注 **peer ledger (owner=…), cited by path + recomputed sha256**，**不称"中立基准"**；
     中立基准 = setup-contract.json（FROZEN）。
  ③ 与 `t34` L45 双向交叉引用（门禁完整性：零目标不得作覆盖证据）。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.join(RUN, 'build-report.json')
MARK = 'provenanceSources'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# 现算两个候选读物（不采信任何字面）
ARCH = os.path.join(RUN, 'gate-logs-t28', 'setupArchitect-anchors.json')
MINE = os.path.join(RUN, 'gate-logs-t28', 't28-anchors.json')
CON = os.path.join(RUN, 'setup-contract.json')
arch = {'path': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/setupArchitect-anchors.json',
        'owner': 'setup-architect', 'size': os.path.getsize(ARCH), 'sha256': sha(ARCH)}
mine = {'path': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json',
        'owner': 'compile-diagnostician', 'size': os.path.getsize(MINE), 'sha256': sha(MINE)}
cons = {'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',
        'owner': 'setup-architect (契约)', 'size': os.path.getsize(CON), 'sha256': sha(CON)}

print('=== 现算 ===')
for d in (arch, mine, cons):
    print('  %-32s %8d B' % (d['owner'], d['size']))

t = io.open(GEN, encoding='utf-8-sig').read()
print('\n生成器已含 %s = %s' % (MARK, MARK in t))
if MARK not in t:
    INS = """    'provenanceSources': {
        'rule': ('**引用他方产物时必须标注来源与归属**：'
                 '`peer ledger (owner=<name>), cited by path + recomputed sha256`；'
                 '**不得称其为"中立基准"**（复核方因独立性不宜依赖被审方自档）。'),
        'neutralBaseline': {
            'which': '`setup-contract.json`（FROZEN）',
            'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',
            'why': '契约是**权威输入**，非任何一方的自档 ⇒ 作中立基准',
        },
        'peerLedgers': [{
            'label': 'peer ledger (owner=setup-architect)',
            'path': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/setupArchitect-anchors.json',
            'note': ('cited by path + recomputed sha256；**非中立基准**。'
                     'reviewer 拒绝将其作复核依据（独立性 / 其同样在变）；实施方交叉核对可用。'),
        }, {
            'label': 'own ledger (owner=compile-diagnostician)',
            'path': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json',
            'note': 'cited by path + recomputed sha256；我方自档，同样**非中立基准**。',
        }],
        'crossReference': {
            't34L45': ('`t34` 新增 L45（binding）：**bst-sw 的 PASS 不得作为覆盖证据，'
                       '除非同次输出亦显示 `[scan] targets=N` 且 N>0** —— 与本报告 `emptyPassGuard`/'
                       '`exitZeroSemantics` **同源**；我方 `run_gates.ps1` 零引用 `targets` 的实测与其一致。'),
            'note': 'Captain 若批"编排器兜底（run_gates.ps1 断言 targets>0）"，本方 re-run 前置可直接复用该断言。',
        },
    },
"""
    anchor = "    'withdrawnClaims': ["
    if anchor not in t:
        print('ERROR: 锚点未命中')
        raise SystemExit(1)
    t = t.replace(anchor, INS + anchor, 1)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
    print('  已插入 provenanceSources → %d B' % os.path.getsize(GEN))

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成:', (r.stdout or '').strip().replace('\n', ' | ')[:140] if r.stdout else r.stderr[:160])

A = json.load(io.open(REPORT, encoding='utf-8-sig'))
ps = A.get(MARK) or {}
print('\n=== 报告内 ===')
print('  provenanceSources 在 =', bool(ps))
print('  peerLedgers 条数     =', len(ps.get('peerLedgers') or []))
print('  含"非中立基准"        =', '非中立基准' in json.dumps(ps, ensure_ascii=False))
print('  含 t34 L45 交叉引用   =', 'L45' in json.dumps(ps, ensure_ascii=False))
print('  报告 %d B ; verdict=%s' % (os.path.getsize(REPORT), A['verdict']))
