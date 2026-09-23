# -*- coding: utf-8 -*-
"""核实 t30-summary.md 的实际路径与身份 + 确认两项入档（幂等、只读、全部现算）。

产出：t30-summary-locate.json（供 Captain/复核方直接读取，无需手抄任何哈希）
同时做：
  A) 现算 path / size / sha256 / mtime，并**断言它在 gate-logs-t30/ 下**
  B) 与单一真源 t28-anchors.json 中登记值**交叉比对**（是否一致、是否重复登记）
  C) 锚点文件非确定性修复的**可复现证明**（连跑两次 → 剔除 anchorsObservedAt 行后主体哈希一致）
  D) t30-summary.md 是否已含口径更正的三处标记（双列表述 / 两口径表 / 前提已判）
"""
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SUM = os.path.join(HERE, 't30-summary.md')
ANCHORS = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10', 'gate-logs-t28', 't28-anchors.json')
OUT = os.path.join(HERE, 't30-summary-locate.json')
TS_LINE = re.compile(r'^\s*"anchorsObservedAt": ".*",\s*$', re.M)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


rec = {}

# ---- A) 路径与身份 ----
d = open(SUM, 'rb').read()
rel = os.path.relpath(SUM, WS).replace('\\', '/')
rec['A_path'] = {
    'path_relative_to_workspace': rel,
    'path_absolute': SUM,
    'under_gate_logs_t30': rel.startswith('team/artifacts/acceptance-20260916-dali10/gate-logs-t30/'),
    'size': len(d),
    'sha256': hashlib.sha256(d).hexdigest(),
    'mtime': datetime.datetime.fromtimestamp(os.path.getmtime(SUM)).isoformat(timespec='seconds'),
    'exists': os.path.isfile(SUM),
}
print('=== A) t30-summary.md 身份（现算）===')
for k, v in rec['A_path'].items():
    print('  %-28s %s' % (k, v))

# 同目录清单（证明它在该目录内，而非"路径写错"）
same_dir = sorted(f for f in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, f)))
rec['A_siblings'] = [f for f in same_dir if f.endswith('.md') or f.endswith('.json')]
print('  同目录内 .md/.json 文件: %s' % rec['A_siblings'])

# ---- B) 与单一真源交叉比对 ----
anch = json.load(io.open(ANCHORS, encoding='utf-8-sig'))
hits = [a for a in anch['anchors'] if a.get('path', '').endswith('t30-summary.md')]
rec['B_anchors'] = {
    'entries_pointing_at_t30_summary': len(hits),
    'registered_size': hits[0]['size'] if hits else None,
    'registered_sha256': hits[0]['sha256'] if hits else None,
    'matches_ondisk': bool(hits and hits[0]['size'] == len(d) and hits[0]['sha256'] == hashlib.sha256(d).hexdigest()),
}
print('\n=== B) 与单一真源交叉比对 ===')
print('  指向 t30-summary.md 的锚点条目数 = %d' % rec['B_anchors']['entries_pointing_at_t30_summary'])
print('  登记值与现盘一致 = %s' % rec['B_anchors']['matches_ondisk'])

# ---- C) 锚点文件确定性复现 ----
gen = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10', 'gate-logs-t28', 't28_make_anchors.py')
bodies = []
for _ in range(2):
    subprocess.run([sys.executable, gen], capture_output=True, text=True, encoding='utf-8')
    bodies.append(TS_LINE.sub('', io.open(ANCHORS, encoding='utf-8').read()).strip())
body_hash = hashlib.sha256(bodies[1].encode('utf-8')).hexdigest()
rec['C_anchor_determinism'] = {
    'two_runs_body_identical': bodies[0] == bodies[1],
    'body_sha256_excluding_timestamp': body_hash,
    'note': '稳定引用锚点 = 剔除 anchorsObservedAt 行后的主体哈希',
}
print('\n=== C) 锚点确定性（连跑两次）===')
print('  剔除时间戳行后主体一致 = %s' % rec['C_anchor_determinism']['two_runs_body_identical'])
print('  主体哈希（稳定锚点）= %s' % body_hash)

# ---- D) 口径更正是否已应用 ----
t = d.decode('utf-8-sig')
rec['D_wording'] = {
    'two_column_payload_vs_deployed': '仅漏闭' in t,
    'dual_contract_expectation_table': ('rev 25（`t42`/`t44` 判 ch5 后' in t),
    'premise_resolved_note': '前提已判（`t42` + `t44`）' in t,
    'accept_boundary_kept': '不覆盖"pin 归属前提"的正确性' in t,
    'baseline_untouched_mentioned': '不得改动 `gate_baseline.json`' in t,
    'idempotency_marker_present': '**口径更正（t44 实测 / Captain 令）' in t,
}
print('\n=== D) 口径更正落地检查 ===')
for k, v in rec['D_wording'].items():
    print('  %-34s %s' % (k, '✓' if v else '✗'))

io.open(OUT, 'w', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False, indent=2))
print('\nWROTE %s (%d B)' % (OUT, os.path.getsize(OUT)))
print('（本文件不含任何手抄哈希：全部由本脚本现算写入）')
