# -*- coding: utf-8 -*-
"""t25 变体对照: 三种 fam_intersect 语义在同一规则位点上的输出差异 (frozen evidence)。

V1 = 修复前线上实现:       p == fam or p.startswith(fam) or fam.startswith(p)
V2 = t25 已落地 (对称边界): 上式的两侧都加 token 边界约束
V3 = 另一候选 (仅正方向):  p==fam or p.startswith(fam)   <- reviewer t22-02 的建议
对照口径: 规则位点 L318 (fam_intersect(powered, ptok)) —— powered 是 meta 的 pin 集合,
          ptok 是电容家族的 token。**注意方向**: 只有当 powered 侧存在 "ptok 的前缀"
          (如 powered 含 'SW', ptok='SW1_BST1') 或严格相等时才会命中; 因此
          V1/V3 在该位点等价, VBUS 警告在 V3 下同样保留。
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import proj_config  # noqa: E402
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(ROOT, 'project_config.json'))
meta = json.load(io.open(cfg['outputs']['meta'], encoding='utf-8-sig'))
stdafx = io.open(cfg['derived']['stdafx_h'], encoding='utf-8-sig', errors='replace').read()

cap_defs = {}
for m in re.finditer(r'#define\s+(K\d*_\w+)\s+(\d+)', stdafx):
    pt = V.cap_pin(m.group(1))
    if pt and pt not in cap_defs:
        cap_defs[pt] = m.group(1)


def v1(pins, fam):
    return {p for p in pins if p == fam or p.startswith(fam) or fam.startswith(p)}


def v3(pins, fam):
    """reviewer t22-02 建议的 'token-boundary' 写法 (只约束正方向)"""
    return {p for p in pins if p == fam or p.startswith(fam + '_')}


V2 = V.fam_intersect

rows = []
for fn in meta['functions']:
    ca = fn.get('capAuthority') or {}
    powered = {str(p).upper() for p in (ca.get('powered_pins') or [])}
    mi = {str(p).upper() for p in (ca.get('mi_pins') or [])}
    ramp = {str(p).upper() for p in (ca.get('ramp_pins') or [])}
    testpad = {str(p).upper() for p in (ca.get('testpad_pins') or [])}
    for ptok, relay in sorted(cap_defs.items()):
        rec = {'fn': fn['functionName'], 'cap': relay, 'ptok': ptok}
        for tag, f in (('v1', v1), ('v2', V2), ('v3', v3)):
            pw = f(powered, ptok)
            rec[tag + '_required'] = bool(pw) and not f(testpad, ptok) and not f(mi, ptok) and not f(ramp, ptok)
            rec[tag + '_pw'] = sorted(pw)
        rows.append(rec)

req = {tag: sorted('%s -> %s' % (r['fn'], r['cap']) for r in rows if r[tag + '_required'])
       for tag in ('v1', 'v2', 'v3')}

print('=== 三种语义下"该闭的稳压电容"总需求 ===')
for tag in ('v1', 'v2', 'v3'):
    print('%s: %d 条' % (tag, len(req[tag])))
print('\nV1 - V2 (消除了什么):')
for x in sorted(set(req['v1']) - set(req['v2'])):
    print('   ', x)
print('V2 - V1 (新增了什么, 必须为空):')
for x in sorted(set(req['v2']) - set(req['v1'])):
    print('   ', x)
print('V1 vs V3 差异:', '空 (该位点上二者等价)' if set(req['v1']) == set(req['v3']) else
      sorted(set(req['v1']) ^ set(req['v3'])))
print('\nVBUS 相关需求在各语义下:')
for x in sorted(set(req['v1']) | set(req['v2']) | set(req['v3'])):
    if 'VBUS' in x:
        which = [t for t in ('v1', 'v2', 'v3') if x in req[t]]
        print('   %-46s 命中于 %s' % (x, which))

out = {'v1': req['v1'], 'v2': req['v2'], 'v3': req['v3'],
       'removed_by_v2': sorted(set(req['v1']) - set(req['v2'])),
       'added_by_v2': sorted(set(req['v2']) - set(req['v1'])),
       'v1_equals_v3': set(req['v1']) == set(req['v3'])}
io.open(os.path.join(HERE, 't25-variant-matrix.json'), 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=2))
print('\nWROTE', os.path.join(HERE, 't25-variant-matrix.json'))
