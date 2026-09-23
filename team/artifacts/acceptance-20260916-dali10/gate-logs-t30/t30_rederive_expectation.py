# -*- coding: utf-8 -*-
"""重查：我的 t30 断言对 TM600/TM601 究竟派生什么期望？（现盘契约为准，不引记忆）

背景：schematic-expert 主张"TM601 不受 bst2sw 约束（其别名是 sw2pgnd），现行契约下 TM601 是绿的"，
      而我早前一次探针显示 TM601 缺 [83,110] —— 两者矛盾。本脚本按现盘契约逐条重算。
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
C = json.loads(open(os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10',
                                 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))

print('=== 现盘契约 aliasResolution（逐条）===')
for i, e in enumerate(C.get('aliasResolution') or []):
    r = e.get('resolution') or {}
    print('  [%2d] alias=%-12s closed=%-24s usedByTm=%s'
          % (i, e.get('alias'), r.get('closedRelayNumbers'),
             json.dumps(e.get('usedByTm'), ensure_ascii=False)[:80]))

print('\n=== tmDeltas 的 aliasesUsed ===')
for k in ('TM600', 'TM601', 'TM1205'):
    d = C['tmDeltas'].get(k) or {}
    print('  %-7s aliasesUsed=%s' % (k, json.dumps(d.get('aliasesUsed'), ensure_ascii=False)))
    afe = d.get('aliasFlatTable')
    if afe:
        print('           aliasFlatTable 条数 = %d' % len(afe))
        for row in afe[:4]:
            print('             %s' % json.dumps(row, ensure_ascii=False)[:160])

print('\n=== 部署态两函数实际闭合 vs 各别名期望 ===')
with open(cfg['derived']['test_cpp'], 'rb') as f:
    t = f.read().decode('utf-8-sig', errors='replace')
blocks = dict(V.fn_blocks(t))
idx = {}
for e in (C.get('aliasResolution') or []):
    a = str(e.get('alias', ''))
    nums = set()
    for x in ((e.get('resolution') or {}).get('closedRelayNumbers') or []):
        if isinstance(x, int):
            nums.add(x)
        else:
            nums |= {int(y) for y in re.findall(r'\d+', str(x))}
    users = set()
    for x in (e.get('usedByTm') or []):
        users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
    idx[a] = (nums, users)

for fn, base in (('TM600_HS_RDSON', 'TM600'), ('TM601_LS_RDSON', 'TM601'), ('TM1205_TRX_BST_UV_GD', 'TM1205')):
    nums = set()
    for r in V.parse_setons(blocks[fn]):
        m = re.match(r'K(\d+)_', r)
        if m:
            nums.add(int(m.group(1)))
        elif re.fullmatch(r'\d+', r):
            nums.add(int(r))
        else:
            # 别名型（K_FPVIH_TO_SW1_A 等）→ 通过 StdAfx.h 展开
            num = V.parse_defines(V.read_enc(cfg['derived']['stdafx_h'])) if False else None
    exp_union, srcs = set(), {}
    for a in [str(x) for x in (C['tmDeltas'][base].get('aliasesUsed') or [])]:
        n, _u = idx.get(a, (set(), set()))
        exp_union |= n
        srcs.setdefault(a, 'aliasesUsed')
    for a, (n, u) in idx.items():
        if base in u:
            exp_union |= n
            srcs.setdefault(a, 'usedByTm')
    print('  %-18s 实际=%s' % (fn, sorted(nums)))
    print('     %-14s 期望并集=%-22s 来源=%s 缺失=%s'
          % ('', sorted(exp_union), srcs, sorted(exp_union - nums)))
