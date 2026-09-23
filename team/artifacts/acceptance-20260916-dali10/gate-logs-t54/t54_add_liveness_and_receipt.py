# -*- coding: utf-8 -*-
"""落实 rule-reviewer ① 的建议：
  (a) 报告属**活档**，**明确不标 FROZEN**；
  (b) 同步"自算哈希/条目数"—— 因为自引用哈希不可写在文件自身，故另出**外部哈希收据**。

产物：`gate-logs-t54/build-report.receipt.json`（每次生成后重算；由生成器负责）。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.join(RUN, 'build-report.json')
MARK = 'livenessDeclaration'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器含 %s = %s' % (MARK, MARK in t))
if MARK not in t:
    INS = """    'livenessDeclaration': {
        'status': '**LIVE (活档)** — **不得标 FROZEN**',
        'why': ('本文件由 `gate-logs-t54/t54_make_report.py` 反复重生成；'
                '其 size/sha256 会随每次追加而变（本轮已多次）。'),
        'citeRule': ('引用一律「全路径 + **当次现算 sha256** + 现算时刻」；'
                     '**不得引用本文件内的任何自算哈希**（自引用会立刻过期）。'),
        'receiptInstead': ('如需"某一版的字节身份"，读外部收据 '
                           '`gate-logs-t54/build-report.receipt.json`（生成后重算，含 size/sha256/entries/at）。'),
    },
"""
    anchor = "    'withdrawnClaims': ["
    if anchor not in t:
        print('ERROR: 锚点未命中')
        raise SystemExit(1)
    t = t.replace(anchor, INS + anchor, 1)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
    print('  已插入 livenessDeclaration → %d B' % os.path.getsize(GEN))

# 生成器末尾追加"写收据"逻辑（幂等）
if 'build-report.receipt.json' not in t:
    t = io.open(GEN, encoding='utf-8-sig').read()
    TAIL = '''

# ---- 外部哈希收据（rule-reviewer 建议：报告为活档，自引用哈希会过期）----
import hashlib as _hl
import json as _json
import os as _os
import datetime as _dt
_rep_p = os.path.join(RUN, 'build-report.json')
_b = open(_rep_p, 'rb').read()
_rec = {
    'subject': 'team/artifacts/acceptance-20260916-dali10/build-report.json',
    'at': _dt.datetime.now().astimezone().isoformat(timespec='seconds'),
    'size': len(_b),
    'sha256': _hl.sha256(_b).hexdigest(),
    'sha256_lf_normalized': _hl.sha256(_b.replace(b"\\r\\n", b"\\n")).hexdigest(),
    'topLevelEntries': len(_json.loads(_b.decode('utf-8-sig'))),
    'note': ('报告为**活档**，本收据在每次生成后重算；引用某一版身份请用本文件（勿用报告内的自算哈希）。'),
}
_rec_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipt.json')
open(_rec_p, 'w', encoding='utf-8').write(_json.dumps(_rec, ensure_ascii=False, indent=2))
print('RECEIPT %s (%d B)' % (_rec_p, _os.path.getsize(_rec_p)))
'''
    io.open(GEN, 'a', encoding='utf-8', newline='').write(TAIL)
    print('  已追加收据逻辑 → %d B' % os.path.getsize(GEN))

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('\n  重生成输出尾部:', (r.stdout or '').strip().splitlines()[-1][:110] if r.stdout else r.stderr[:150])

A = json.load(io.open(REPORT, encoding='utf-8-sig'))
rec = json.load(io.open(os.path.join(RUN, 'gate-logs-t54', 'build-report.receipt.json'), encoding='utf-8-sig'))
print('\n=== 结果 ===')
print('  livenessDeclaration 在 =', MARK in A)
print('  status =', A[MARK]['status'])
print('  收据 = size %d / sha256 %s… / topLevelEntries %d' % (rec['size'], rec['sha256'][:24], rec['topLevelEntries']))
print('  收据 size 与现盘一致 =', rec['size'] == os.path.getsize(REPORT))
print('  收据 sha256 与现盘一致 =', rec['sha256'] == sha(REPORT))
