# -*- coding: utf-8 -*-
"""② 按 rule-reviewer 的建议给快照账本加**自完整性**：链式自证 + appendOnly 声明（向前生效）。

设计（不回头改写既有 2 行 —— 那本身会破坏"只增不改"）：
  · 从下一条起，每行新增：lineCount / prevLineSha256 / ledger_self_sha256；
  · 另写一份**头文件** `t28-anchors.snapshots.meta.json`：appendOnly=true + rule + 既有行数与哈希；
  · 追加一条新快照以示范新格式（并自证链成立）。
判据（采纳其措辞）：**记录不能替代强制**；账本解决"可复核"，链式自证解决"不可篡改"。
"""
import datetime
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, 't28-anchors.json')
J = os.path.join(HERE, 't28-anchors.snapshots.jsonl')
META = os.path.join(HERE, 't28-anchors.snapshots.meta.json')
TS_LINE = re.compile(r'^\s*"anchorsObservedAt": ".*",\s*$', re.M)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def body_sha(p):
    t = TS_LINE.sub('', io.open(p, encoding='utf-8-sig').read()).strip()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


# 1) 头文件：appendOnly 声明 + 既有行数与哈希
lines = io.open(J, encoding='utf-8').read().strip().splitlines()
meta = {
    'appendOnly': True,
    'rule': ('**任何对本账本的整篇重写视为违规，须登记**；只允许追加行。'
             '每行须含 lineCount / prevLineSha256 / ledger_self_sha256 以链式自证。'),
    'existingRowsAtDeclaration': len(lines),
    'existingRowsSha256': hashlib.sha256(('\n'.join(lines) + '\n').encode('utf-8')).hexdigest(),
    'declaredAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'note': ('按 rule-reviewer 建议补"自完整性"：账本给出**可复核性**，链式自证给出**不可篡改性**，两者都要。'
             '既有 2 行保持原样（回头改写会破坏"只增不改"）；自第 3 行起采用带链字段的新格式。'),
}
io.open(META, 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=False, indent=2))
print('WROTE meta = %d B / %s' % (os.path.getsize(META), sha(META)))

# 2) 追加一条示范行：带 lineCount / prevLineSha256 / ledger_self_sha256
A = json.load(io.open(LIVE, encoding='utf-8-sig'))
prev_line_sha = hashlib.sha256(lines[-1].encode('utf-8')).hexdigest()
rec = {
    'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'reason': 'chain-self-proof-enabled (rule-reviewer suggestion)',
    'live_size': os.path.getsize(LIVE),
    'live_sha256': sha(LIVE),
    'live_body_sha256': body_sha(LIVE),
    'entries': len(A.get('anchors') or []),
    'preservedPeerKeys': list((A.get('preservedPeerNamespaces') or {}).keys()),
    'lineCount': len(lines) + 1,
    'prevLineSha256': prev_line_sha,
}
# ledger_self_sha256 = 含本行（不含该字段）内容的哈希 —— 写入前一并计算
rec['ledger_self_sha256'] = hashlib.sha256(
    ('\n'.join(lines) + '\n' + json.dumps(rec, ensure_ascii=False)).encode('utf-8')).hexdigest()
with io.open(J, 'a', encoding='utf-8') as f:
    f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print('APPENDED → 账本现 %d 行 / %d B' % (
    len(io.open(J, encoding='utf-8').read().strip().splitlines()), os.path.getsize(J)))

# 3) 自证：链字段是否齐备、链是否一致
now_lines = io.open(J, encoding='utf-8').read().strip().splitlines()
last = json.loads(now_lines[-1])
print('\n=== 自证 ===')
print('  新行键 =', list(last.keys()))
print('  含 lineCount / prevLineSha256 / ledger_self_sha256 =',
      all(k in last for k in ('lineCount', 'prevLineSha256', 'ledger_self_sha256')))
print('  prevLineSha256 与上一行实际哈希一致 =',
      last['prevLineSha256'] == hashlib.sha256(now_lines[-2].encode('utf-8')).hexdigest())
print('  头文件 appendOnly =', json.load(io.open(META, encoding='utf-8-sig')).get('appendOnly'))
