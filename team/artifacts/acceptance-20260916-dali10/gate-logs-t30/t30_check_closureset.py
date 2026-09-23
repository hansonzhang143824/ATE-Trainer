# -*- coding: utf-8 -*-
"""核对 Captain ② 的闭集更正：BST–SW 闭集应为 `[48,60,61,76]` 而非 `[48,61,76]`。

做法：按现盘契约逐源推导 TM600 的期望并集，并核对 48/60/61/76 各自的来源；
再看部署态已闭哪些、缺哪些 ⇒ 确定"红色叙事的目标"该写成缺什么。
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
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
C = json.loads(open(os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10',
                                 'setup-contract.json'), 'rb').read().decode('utf-8-sig'))

print('=== ① 现盘契约里各别名的闭集（来源标注）===')
src = {}
for e in (C.get('aliasResolution') or []):
    a = str(e.get('alias', ''))
    nums = [x for x in ((e.get('resolution') or {}).get('closedRelayNumbers') or []) if isinstance(x, int)]
    users = set()
    for x in (e.get('usedByTm') or []):
        users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
    if nums:
        print('  %-10s closed=%-22s usedByTm=%s' % (a, nums, sorted(users)))
    for n in nums:
        src.setdefault(n, []).append(a)

print('\n=== ② TM600 期望并集（aliasesUsed ∪ usedByTm 命中项）===')
d = C['tmDeltas']['TM600']
exp = set()
for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
    row = [e for e in C['aliasResolution'] if str(e.get('alias')) == a]
    if row:
        exp |= {x for x in ((row[0].get('resolution') or {}).get('closedRelayNumbers') or []) if isinstance(x, int)}
for e in (C.get('aliasResolution') or []):
    users = set()
    for x in (e.get('usedByTm') or []):
        users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
    if 'TM600' in users:
        exp |= {x for x in ((e.get('resolution') or {}).get('closedRelayNumbers') or []) if isinstance(x, int)}
print('  期望并集 = %s' % sorted(exp))
for n in sorted(exp):
    print('     K%-4d 来源 = %s' % (n, src.get(n, ['?'])))

print('\n=== ③ Captain 给的 BST–SW 闭集 [48,60,61,76] 与推导的对照 ===')
claim = {48, 60, 61, 76}
print('  Captain 值 = %s' % sorted(claim))
print('  现盘推导值 = %s' % sorted(exp))
print('  一致 = %s' % (claim == exp))
if claim - exp:
    print('  Captain 多出 = %s' % sorted(claim - exp))
if exp - claim:
    print('  现在推导多出 = %s' % sorted(exp - claim))

print('\n=== ④ 部署态 TM600 已闭 / 缺失 ===')
with open(cfg['derived']['test_cpp'], 'rb') as f:
    t = f.read().decode('utf-8-sig', errors='replace')
nums = set()
for r in V.parse_setons(dict(V.fn_blocks(t))['TM600_HS_RDSON']):
    m = re.match(r'K(\d+)_', r)
    if m:
        nums.add(int(m.group(1)))
    elif re.fullmatch(r'\d+', r):
        nums.add(int(r))
print('  已闭 = %s' % sorted(nums))
print('  相对 Captain 值 [48,60,61,76]: 已闭 = %s ; **缺 = %s**'
      % (sorted(claim & nums), sorted(claim - nums)))
print('  ⇒ **红色叙事的目标应写成"缺 %s"**' % sorted(claim - nums))

print('\n=== ⑤ 三情形表（Captain 定的最终口径）核对 ===')
print('  · rev 24 + t29 payload ⇒ 契约期望 %s ⇒ 补 110 后缺失=[] ⇒ GREEN' % sorted(exp))
print('  · rev 25 而 payload 未同批 ⇒ TM600 缺 %s ⇒ 仍 NEW-RED（第二处真缺陷）' % sorted(claim - nums))
print('  · rev 25 + payload 同批 ⇒ payload 补 %s ⇒ 期望 GREEN（本 run 实际分支）' % sorted(claim - nums))
