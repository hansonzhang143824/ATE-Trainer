# -*- coding: utf-8 -*-
"""落实 rule-reviewer ② 的可选建议（我方自评为"必要的自一致性修正"）：

收据当前**每次覆写** ⇒ 只保留**最近一版**身份，与我方对 anchors 主张的"**只增不改**"精神不一致。
修法（仿 anchors 账本）：
  · `build-report.receipt.json`  —— **保持为"最新版便利指针"**（便利性）；
  · 新增 `build-report.receipts.jsonl` —— **append-only 历史账本**（每次生成追加一行，含链式字段）
     ⇒ "**某一版身份**"永久可复核。
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
SENT = 'RECEIPT_HISTORY_V1'

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B ; 已含历史账本 = %s' % (os.path.getsize(GEN), SENT in t))
if SENT not in t:
    TAIL = '''

# ==== RECEIPT_HISTORY_V1：收据历史账本（append-only）====
# rule-reviewer 指出：收据若每次覆写 ⇒ 只留"最近一版"身份，与"只增不改"精神不一致。
#   故：`receipt.json` 仍作最新版便利指针；另设 `receipts.jsonl` 追加历史行（含链式字段）。
_hist_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.jsonl')
_prev_lines = []
if os.path.isfile(_hist_p):
    _prev_lines = [l for l in io.open(_hist_p, encoding='utf-8').read().splitlines() if l.strip()]
_line = dict(_rec)
_line['lineCount'] = len(_prev_lines) + 1
_line['prevLineSha256'] = (_hl.sha256(_prev_lines[-1].encode('utf-8')).hexdigest() if _prev_lines else None)
_line['ledger_self_sha256'] = _hl.sha256(
    ('\\n'.join(_prev_lines) + '\\n' + _json.dumps(_line, ensure_ascii=False)).encode('utf-8')
).hexdigest()
with io.open(_hist_p, 'a', encoding='utf-8') as _f:
    _f.write(_json.dumps(_line, ensure_ascii=False) + '\\n')
print('RECEIPT-HISTORY %s (%d 行)' % (_hist_p, len(_prev_lines) + 1))
'''
    io.open(GEN, 'a', encoding='utf-8', newline='').write(TAIL)
    print('  已追加历史账本逻辑 → %d B' % os.path.getsize(GEN))

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tail = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tail[-1][:90] if tail else (r.stderr or '')[:130]))

H = os.path.join(HERE, 'build-report.receipts.jsonl')
print('\n=== 历史账本自证 ===')
lines = io.open(H, encoding='utf-8').read().strip().splitlines()
print('  %s = %d 行 / %d B' % (os.path.basename(H), len(lines), os.path.getsize(H)))
import hashlib
import json
last = json.loads(lines[-1])
print('  末行键 =', list(last.keys()))
print('  lineCount =', last['lineCount'])
if last.get('prevLineSha256'):
    ok = last['prevLineSha256'] == hashlib.sha256(lines[-2].encode('utf-8')).hexdigest()
    print('  链式自证 prevLineSha256 正确 =', ok)
print('  含 reproducibleBodySha256 =', 'reproducibleBodySha256' in last)
