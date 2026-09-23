# -*- coding: utf-8 -*-
"""落实 rule-reviewer ② 的建议：为单一真源加一道**稳定性约束**——
活档 `t28-anchors.json` 保持"可被重生成"，但**每轮另存带时间戳的只读快照**，
且**历史快照只增不删**（append-only journal），使"某轮当时的值"事后仍可复核。

产物：
  gate-logs-t28/t28-anchors.snapshots.jsonl   每行 = 一次生成的 {at, size, sha256, entries, bodySha}
（jsonl 只追加；不覆盖历史。）
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
LIVE = os.path.join(HERE, 't28-anchors.json')
JOURNAL = os.path.join(HERE, 't28-anchors.snapshots.jsonl')
GEN = os.path.join(HERE, 't28_make_anchors.py')
TS_LINE = re.compile(r'^\s*"anchorsObservedAt": ".*",\s*$', re.M)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def body_sha(p):
    t = TS_LINE.sub('', io.open(p, encoding='utf-8-sig').read()).strip()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def snapshot(reason):
    if not os.path.isfile(LIVE):
        print('  活档不存在，跳过')
        return
    A = json.load(io.open(LIVE, encoding='utf-8-sig'))
    rec = {
        'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        'reason': reason,
        'live_size': os.path.getsize(LIVE),
        'live_sha256': sha(LIVE),
        'live_body_sha256': body_sha(LIVE),
        'entries': len(A.get('anchors') or []),
        'preservedPeerKeys': list((A.get('preservedPeerNamespaces') or {}).keys()),
    }
    with io.open(JOURNAL, 'a', encoding='utf-8') as f:      # append-only
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('  已追加快照：%s | %d B | %d 条' % (rec['at'], rec['live_size'], rec['entries']))
    return rec


print('=== 1) 先跑生成器（确认活档可重生成）===')
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  ', (r.stdout or '').strip().splitlines()[0] if r.stdout else r.stderr[:120])
print('=== 2) 追加两份快照（验证 append-only 累积）===')
snapshot('after-generate-run-1')
snapshot('after-generate-run-2')

print('\n=== 3) 账本累积检查 ===')
lines = io.open(JOURNAL, encoding='utf-8').read().strip().splitlines()
print('  %s = %d 行 / %d B' % (os.path.basename(JOURNAL), len(lines), os.path.getsize(JOURNAL)))
for l in lines[-3:]:
    d = json.loads(l)
    print('    %-26s size=%-7d entries=%-3d peerKeys=%s'
          % (d['at'], d['live_size'], d['entries'], d['preservedPeerKeys']))
print('\n  ⇒ 历史行**不被覆盖**；即使活档后续被重生成/变小，"某轮当时的值"仍可从这里复核。')
