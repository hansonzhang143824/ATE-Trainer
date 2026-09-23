# -*- coding: utf-8 -*-
"""t25 证据清单: 对改动文件/日志/产物统一用 python 计算 sha256 (DLP 授权读者)。

铁律 (本轮实测): **不要**用 Get-FileHash / pwsh 文本工具对受保护源做前后比对或内容判断。
本脚本标注每个文件的 plaintext/binary 判定 (python rb 读到的头字节)。
"""
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

TARGETS = [
    # 被修文件 (inScope)
    'scripts/run_gates.ps1',
    'scripts/verify_relay_trace.py',
    # 明令未改 (inScope 中禁止改内容 / 未被本任务触碰)
    'scripts/gate_baseline.json',
    'project/DALI/meta/dali_tm_meta.json',
    'team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp',
    # 只读上游权威
    'project/DALI/SCH-Connect-Map.txt',
    'project_config.json',
    # 目标树 (本轮未编译未改)
    'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',
    'D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h',
    # 生产树 (只读)
    'D:/PROJECT6-DALI/devel/source/test.cpp',
    'D:/PROJECT6-DALI/devel/source/StdAfx.h',
]


def info(path):
    p = path if os.path.isabs(path) else os.path.join(ROOT, path.replace('/', os.sep))
    if not os.path.isfile(p):
        return {'path': path, 'exists': False}
    with open(p, 'rb') as f:
        d = f.read()
    head = d[:24]
    is_tsz = head.startswith(b'%TSD-Header-###%') or head.startswith(b'TSZ#')
    try:
        d.decode('utf-8-sig')
        text = True
    except UnicodeDecodeError:
        text = False
    return {'path': path, 'exists': True, 'size': len(d),
            'sha256': hashlib.sha256(d).hexdigest(),
            'readsAs': 'binary-TSZ-container' if is_tsz else 'plaintext',
            'utf8Decodable': text, 'head': repr(head[:16])}


rows = [info(t) for t in TARGETS]

# 门禁日志 (verify 命令产物)
logdir = os.path.join(ROOT, 'team', 'artifacts', 'acceptance-20260916-dali10', 'gate-logs-t25')
logs = []
if os.path.isdir(logdir):
    for fn in sorted(os.listdir(logdir)):
        fp = os.path.join(logdir, fn)
        if os.path.isfile(fp):
            logs.append(info(os.path.relpath(fp, ROOT)))

# 本轮 t25 证据文件
evidence = []
for fn in sorted(os.listdir(HERE)):
    fp = os.path.join(HERE, fn)
    if os.path.isfile(fp):
        evidence.append(info(os.path.relpath(fp, ROOT)))

out = {'generatedBy': 'python 3.12 (DLP-authorized reader)', 'root': ROOT,
       'targets': rows, 'gateLogs': logs, 'evidence': evidence}
p = os.path.join(HERE, 't25-hashes.json')
io.open(p, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=2))

w = max(len(r['path']) for r in rows)
for r in rows:
    if not r['exists']:
        print('%-*s  MISSING' % (w, r['path']))
    else:
        print('%-*s  %7d B  %s  %s' % (w, r['path'], r['size'], r['sha256'][:16], r['readsAs']))
print('\nlogs: %d 条, evidence: %d 条 → %s' % (len(logs), len(evidence), p))
for r in logs:
    if r['exists']:
        print('  LOG %-46s %s' % (os.path.basename(r['path']), r['sha256'][:16]))
