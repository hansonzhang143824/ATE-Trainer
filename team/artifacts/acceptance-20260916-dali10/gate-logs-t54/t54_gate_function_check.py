# -*- coding: utf-8 -*-
"""① 复核 setup-architect 的"命名空间只剩 1 条"；② 用**门禁自身函数**对候选 payload 独立复算
（绕开 `--src` 的空 targets 早退 —— 它比我此前的"等价复现"更硬）。
"""
import hashlib
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')

print('=== ① preservedPeerNamespaces 现状 ===')
p = os.path.join(RUN, 'gate-logs-t28', 't28-anchors.json')
A = json.load(io.open(p, encoding='utf-8-sig'))
pp = A.get('preservedPeerNamespaces') or {}
sa = pp.get('setupArchitectFreezeAnchors')
print('  锚点文件 %d B ; 条目 %d' % (os.path.getsize(p), len(A['anchors'])))
print('  他方命名空间键 =', list(pp.keys()))
if isinstance(sa, dict):
    print('  setupArchitectFreezeAnchors 子键 =', list(sa.keys()))
    print('  其 anchors 条数 =', len(sa.get('anchors') or {}))
print('  他方是否已迁自有文件 =',
      os.path.isfile(os.path.join(RUN, 'gate-logs-t28', 'setupArchitect-anchors.json')))

print('\n=== ② 用门禁自身函数复算（不跑 CLI、不落盘）===')
spec = importlib.util.spec_from_file_location('g', os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py'))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

C = json.loads(io.open(os.path.join(RUN, 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))
print('  契约现盘 revision =', C.get('revision'))

PAY = os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp')
DEP = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'
scope = list(getattr(g, 'DEFAULT_TM_SCOPE', []) or [])
print('  DEFAULT_TM_SCOPE =', scope)

for label, path in (('payload(候选)', PAY), ('deployed(部署态)', DEP)):
    txt = io.open(path, encoding='utf-8-sig', errors='replace').read()
    errs, checked = g.check_contract_closures(txt, C, [], None, False, None)
    print('  %-16s errors=%d' % (label, len(errs)))
    for tm, v in (checked or {}).items():
        print('      %-16s expected=%-24s missing=%s' % (tm, v['expected'], v['missing']))

print('\n=== ③ K109/K110 可执行计数（payload）===')
pt = io.open(PAY, encoding='utf-8-sig', errors='replace').read()
import re
import verify_relay_trace as V
blk = dict(V.fn_blocks(pt))['TM600_HS_RDSON']
for tok in ('K109_BUSL1_PB0', 'K110_ACM18_BST', 'K48_ACM5_AMP_REF', 'K76_ACM_BST'):
    raw = blk.count(tok)
    exe = sum(1 for m in re.finditer(r'cbite\.SetOn\(([^;]*)\)', blk) if tok in m.group(1))
    print('  %-18s raw=%-3d executable=%d' % (tok, raw, exe))
