# -*- coding: utf-8 -*-
"""t30 判据选择探针（只读）—— 用**真实**契约 + **真实** payload 算出各判据源的命中面。

目的：在不改动任何脚本的前提下，确定"哪一组契约集合既抓得到真缺口、又零误报"。
输出：每个候选判据源对每个目标 TM 的 expected/missing 计数与具体 K 号。
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

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
contract = json.loads(open(os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10/setup-contract.json'), 'rb').read().decode('utf-8-sig'))
src, _ = read_enc(cfg['derived']['test_cpp'])


def numbers_from_payload(text):
    out = {}
    fn_re = re.compile(r'int\s+(\w+)\s*\(short\s+funcindex')
    starts = [(m.start(), m.group(1)) for m in fn_re.finditer(text)]
    for idx, (start, name) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(text)
        block = text[start:end]
        nums = set()
        for call in re.finditer(r'cbite\.SetOn\(([^;]*)\)', block, re.DOTALL):
            for arg in call.group(1).split(','):
                arg = arg.strip()
                if not arg or arg == '-1':
                    continue
                if re.fullmatch(r'\d+', arg):
                    nums.add(int(arg))
                else:
                    m = re.match(r'K(\d+)_', arg)
                    if m:
                        nums.add(int(m.group(1)))
        out[name] = nums
    return out


def nums_of(entry):
    out = set()
    if isinstance(entry, bool):
        return out
    if isinstance(entry, (int, float)):
        out.add(int(entry))
    elif isinstance(entry, str):
        out |= {int(t) for t in re.findall(r'\d+', entry)}
    elif isinstance(entry, dict):
        for k in ('number', 'relay', 'relays'):
            if entry.get(k) is not None:
                out |= nums_of(entry.get(k))
    elif isinstance(entry, (list, tuple)):
        for x in entry:
            out |= nums_of(x)
    return out


payload = numbers_from_payload(src)
alias_idx = {}
for e in contract.get('aliasResolution') or []:
    a = str(e.get('alias', ''))
    users = set()
    for x in e.get('usedByTm') or []:
        users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
    alias_idx[a] = (nums_of((e.get('resolution') or {}).get('closedRelayNumbers')), users)


def base_of(tm):
    for k in contract['tmDeltas']:
        if tm == k or tm.startswith(str(k) + '_'):
            return k
    return None


def source_sets(tm):
    base = base_of(tm)
    if base is None:
        return {}
    d = contract['tmDeltas'][base]
    s = {}
    s['A:pinRouteTable union'] = set()
    for pin, routes in (d.get('pinRouteTable') or {}).items():
        if isinstance(routes, dict):
            for _r, rv in routes.items():
                if isinstance(rv, dict) and rv.get('needsClosed'):
                    s['A:pinRouteTable union'] |= nums_of(rv['needsClosed'])
    s['B:relaySet'] = nums_of(d.get('relaySet'))
    s['C:alias usedByTm/aliasesUsed'] = set()
    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        s['C:alias usedByTm/aliasesUsed'] |= alias_idx.get(a, (set(), set()))[0]
    for a, (nums, users) in alias_idx.items():
        if base in users:
            s['C:alias usedByTm/aliasesUsed'] |= nums
    s['D:relaySet ∩ alias-closed'] = s['B:relaySet'] & s['C:alias usedByTm/aliasesUsed']
    a_keys = set()
    for a, (nums, users) in alias_idx.items():
        if base in users:
            a_keys |= nums
    s['E:pinRouteTable ∩ alias-closed'] = s['A:pinRouteTable union'] & a_keys
    return s


targets = [t for t in payload if t.startswith(('TM600', 'TM601', 'TM1205'))]
print('=== 候选判据源命中面（只读实测）===')
for tm in sorted(targets):
    got = payload[tm]
    print('\n%s  payload SetOn 数字集合 = %s' % (tm, sorted(got)))
    for name, exp in source_sets(tm).items():
        miss = sorted(exp - got) if exp else []
        print('   %-34s expected=%-3d missing=%-3d %s'
              % (name, len(exp), len(miss), miss if len(miss) <= 12 else str(miss[:12]) + '...'))

print('\n=== 契约 relaySet 里哪些 K 号在任何 pinRouteTable 出现? (判定"是否有路由依据") ===')
for tm in ('TM600_HS_RDSON', 'TM601_LS_RDSON'):
    base = base_of(tm)
    d = contract['tmDeltas'][base]
    rs = nums_of(d.get('relaySet'))
    got = payload[tm]
    for n in sorted(rs - got):
        in_routes = []
        for pin, routes in (d.get('pinRouteTable') or {}).items():
            if isinstance(routes, dict):
                for r, rv in routes.items():
                    if isinstance(rv, dict) and n in nums_of(rv.get('needsClosed')):
                        in_routes.append('%s/L%s' % (pin, rv.get('line')))
        print('  %s K%-4d 在路由枚举中: %s' % (tm, n, in_routes if in_routes else '**无**（仅 relaySet 提及）'))
