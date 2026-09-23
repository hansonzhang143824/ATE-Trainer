# -*- coding: utf-8 -*-
"""裁定"他方命名空间是否只回来 1/8 条"——以**现盘 + 全部历史副本**为准（不采信任何一方字面）。

同时核实 rule-reviewer ② 的自完整性风险：账本当前**无链式自证/无 appendOnly 声明**？
"""
import hashlib
import io
import json
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


LIVE = os.path.join(RUN, 'gate-logs-t28', 't28-anchors.json')
A = json.load(io.open(LIVE, encoding='utf-8-sig'))
pp = A.get('preservedPeerNamespaces') or {}
saa = pp.get('setupArchitectFreezeAnchors') or {}
print('=== ① 现盘活档中的他方命名空间 ===')
print('  活档 = %d B / %d 条' % (os.path.getsize(LIVE), len(A['anchors'])))
print('  preservedPeerNamespaces 键 =', list(pp.keys()))
print('  setupArchitectFreezeAnchors 子键 =', list(saa.keys()))
print('  **anchors 条数 = %d**' % len(saa.get('anchors') or {}))
print('  anchors 子键名 =', list((saa.get('anchors') or {}).keys())[:12])
print('  mirrorOf =', saa.get('mirrorOf'), '| mirrorSize =', saa.get('mirrorSize'))

print('\n=== ② 是否存在可复原"8 条"的历史副本 ===')
cands = []
for dp, dn, fn in os.walk(RUN):
    for f in fn:
        if f == 't28-anchors.json' or 'snapshot' in f.lower() or 'anchors' in f.lower():
            p = os.path.join(dp, f)
            if os.path.isfile(p):
                cands.append(p)
for p in sorted(cands):
    rel = os.path.relpath(p, RUN).replace('\\', '/')
    try:
        d = json.load(io.open(p, encoding='utf-8-sig'))
        ppx = d.get('preservedPeerNamespaces') or {}
        n = len((ppx.get('setupArchitectFreezeAnchors') or {}).get('anchors') or {})
        print('  %-56s %8d B  他方条数=%s' % (rel, os.path.getsize(p), n))
    except Exception:
        try:
            txt = io.open(p, encoding='utf-8-sig', errors='replace').read()
            cnt = txt.count('"lineCount"') + txt.count('"prevLineSha256"')
            print('  %-56s %8d B  (非 anchors JSON；链式字段=%d)' % (rel, os.path.getsize(p), cnt))
        except Exception:
            print('  %-56s %8d B  (不可解析)' % (rel, os.path.getsize(p)))

print('\n=== ③ 账本自完整性检查（rule-reviewer ②）===')
J = os.path.join(RUN, 'gate-logs-t28', 't28-anchors.snapshots.jsonl')
lines = io.open(J, encoding='utf-8').read().strip().splitlines()
print('  账本 = %d 行 / %d B' % (len(lines), os.path.getsize(J)))
keys0 = list(json.loads(lines[0]).keys())
print('  行内键 =', keys0)
print('  含 lineCount        =', 'lineCount' in keys0)
print('  含 prevLineSha256   =', 'prevLineSha256' in keys0)
print('  含 ledger_self_sha256 =', 'ledger_self_sha256' in keys0)
print('  头部含 appendOnly   =', 'appendOnly' in '\n'.join(lines[:1]))
