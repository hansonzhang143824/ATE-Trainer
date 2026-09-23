# -*- coding: utf-8 -*-
"""复核 schematic-expert 的三点：divergence 字段、宏展开更正、以及我的产物里需同步之处。

只读 + 幂等小幅更正（仅动我自己的 gate-logs-t33 产物）。
"""
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402

C = json.loads(open(os.path.join(RUN, 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))
print('契约 revision = %s ; size = %d B' % (C.get('revision'), os.path.getsize(os.path.join(RUN, 'setup-contract.json'))))

print('\n=== ① divergence 字段（逐字）===')
for i in (14, 15):
    e = C['aliasFlatTable'][i]
    print('  [%d] %-10s kNumbers=%s' % (i, e.get('alias'), e.get('kNumbers')))
    print('       divergence = %s' % (e.get('divergence') or '<无>'))

print('\n=== ② 宏展开复核（他的更正）===')
stdx, _ = read_enc(proj_config.load(os.path.join(WS, 'project_config.json'))['derived']['stdafx_h'])
defs = {}
for ln in stdx.splitlines():
    m = re.match(r'\s*#define\s+(K_\w+)\s+([\d,\s]+)', ln)
    if m:
        defs[m.group(1)] = [int(x) for x in re.findall(r'\d+', m.group(2))]
for k in ('K_FPVIH_TO_SW1_A', 'K_FPVIL_TO_BST1_A', 'K_FPVIH_TO_SW2_A', 'K_FPVIL_TO_BST2_A'):
    print('  %-22s = %s' % (k, defs.get(k)))
print('  L8791 展开 = %s' % sorted(set(defs.get('K_FPVIH_TO_SW1_A', []) + defs.get('K_FPVIL_TO_BST1_A', []) + [13, 65])))
print('  L8835 展开 = %s' % sorted(set(defs.get('K_FPVIH_TO_SW2_A', []) + defs.get('K_FPVIL_TO_BST2_A', []) + [13, 65])))
print('  [14].kNumbers = %s ; [15].kNumbers = %s'
      % (C['aliasFlatTable'][14].get('kNumbers'), C['aliasFlatTable'][15].get('kNumbers')))

print('\n=== ③ 我哪些产物写了不全的展开 ===')
for rel in ('gate-logs-t33/t33-transition-plan.md', 'gate-logs-t33/t44-count-correction.md',
            'gate-logs-t30/t30-summary.md'):
    p = os.path.join(RUN, rel)
    if not os.path.isfile(p):
        continue
    t = io.open(p, encoding='utf-8-sig').read()
    for i, line in enumerate(t.splitlines(), 1):
        if 'K_FPVIL_TO_BST2_A' in line or 'K_FPVIH_TO_SW2_A' in line:
            print('  %-40s L%-4d %s' % (os.path.basename(rel), i, line.strip()[:130]))
