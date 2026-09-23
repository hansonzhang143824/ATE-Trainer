# -*- coding: utf-8 -*-
"""t25 复核回复 2: 逐字重建 cap_defs (含 L274-286 别名规范化) 并复算 FR-001 四个条件。

目的: 判定 rule-reviewer F-1 的"可观测后果"是否如其所言 ——
      他证明的是 `fam_intersect({'SW_BST'},'SW')` 语义仍命中;
      这里判定的是**该命中在真实数据上是否产生告警** (cap_defs 规范化的作用)。
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import verify_relay_trace as V  # noqa: E402

CFG = os.path.join(ROOT, 'project_config.json')
src = V.read_enc(V.SRC)
defines = V.parse_defines(V.read_enc(V.DEFS))
meta = json.load(io.open(V.META, encoding='utf-8-sig'))

# ---- 逐字重建 cap_defs (verify_relay_trace.py L273-286) ----
cap_defs = {}
canon_by_ch = {}
for r, ch in defines.items():
    pt = V.cap_pin(r)
    if pt is None:
        continue
    if re.match(r'^K\d+_', r):
        canon_by_ch.setdefault(ch, r)
    if pt not in cap_defs or (re.match(r'^K\d+_', r) and not re.match(r'^K\d+_', cap_defs[pt])):
        cap_defs[pt] = r
for pt, name in list(cap_defs.items()):
    if not re.match(r'^K\d+_', name) and defines[name] in canon_by_ch:
        cap_defs[pt] = canon_by_ch[defines[name]]

# cap_defs 中指向 SW_BST / BST_SW 相关通道 57 的所有 token
ch57 = {pt: nm for pt, nm in cap_defs.items() if defines.get(nm) == 57}
print('=== cap_defs 中通道 57 (K_SW_BST_Cap / K57_CAP_BST_SW) 的 token ===')
for pt, nm in sorted(ch57.items()):
    print('  token %-8s -> cap_defs=%s  (#define 值=%d)' % (pt, nm, defines[nm]))
print('  cap_defs 总 token 数 =', len(cap_defs))

# ---- 取 TM601_LS_RDSON 的 relay 列表与 meta ----
blocks = dict(V.fn_blocks(src))
blk = blocks['TM601_LS_RDSON']
relays = V.parse_setons(blk)
meta_fn = {f['functionName']: f for f in meta['functions']}['TM601_LS_RDSON']
ca = meta_fn['capAuthority']
powered = {p.upper() for p in ca.get('powered_pins', [])}
mi = {p.upper() for p in ca.get('mi_pins', [])}
ramp = {p.upper() for p in ca.get('ramp_pins', [])}
testpad = {p.upper() for p in ca.get('testpad_pins', [])}
print('\n=== TM601_LS_RDSON ===')
print('  SetOn relays =', relays)
print('  powered=%s mi=%s ramp=%s testpad=%s' % (sorted(powered), sorted(mi), sorted(ramp), sorted(testpad)))

print('\n=== 逐 token 复算 FR-001 四条件 (L317-328) ===')
rows = []
for ptok, cap_relay in sorted(cap_defs.items()):
    fam_powered = V.fam_intersect(powered, ptok)
    if not fam_powered:
        continue
    row = {'token': ptok, 'cap_relay': cap_relay, 'fam_powered': sorted(fam_powered)}
    row['skip_testpad'] = bool(V.fam_intersect(testpad, ptok))
    row['closed'] = cap_relay in relays
    row['skip_mi_ramp'] = bool(V.fam_intersect(mi, ptok) or V.fam_intersect(ramp, ptok))
    row['WARNS'] = not (row['skip_testpad'] or row['closed'] or row['skip_mi_ramp'])
    rows.append(row)
    print('  %-9s -> %-22s fam=%-10s testpadSkip=%s closed=%s miRampSkip=%s  => %s'
          % (ptok, cap_relay, row['fam_powered'], row['skip_testpad'], row['closed'],
             row['skip_mi_ramp'], 'WARN' if row['WARNS'] else 'no warn'))

warn_tokens = [r['token'] for r in rows if r['WARNS']]
print('\n  当前会告警的 token =', warn_tokens)

# ---- 同数据下, 用旧 fam_intersect 复算, 看 SW_BST 是否会多出告警 ----
def old_fam(pins, fam):
    return {p for p in pins if p == fam or p.startswith(fam) or fam.startswith(p)}


old_warn = []
for ptok, cap_relay in sorted(cap_defs.items()):
    fam_powered = old_fam(powered, ptok)
    if not fam_powered:
        continue
    if old_fam(testpad, ptok) or cap_relay in relays or old_fam(mi, ptok) or old_fam(ramp, ptok):
        continue
    old_warn.append((ptok, cap_relay))
print('  旧语义下会告警的 (token, relay) =', old_warn)
print('  ⇒ SW_BST 在旧/新语义下是否产生告警: 旧=%s 新=%s'
      % (any(t == 'SW_BST' for t, _ in old_warn), 'SW_BST' in warn_tokens))

out = {'cap_defs_ch57': ch57, 'cap_defs_count': len(cap_defs),
       'TM601_relays': relays, 'TM601_powered': sorted(powered),
       'per_token': rows, 'warn_tokens_now': warn_tokens,
       'warn_old': [list(x) for x in old_warn],
       'SW_BST_warns_old': any(t == 'SW_BST' for t, _ in old_warn),
       'SW_BST_warns_now': 'SW_BST' in warn_tokens}
p = os.path.join(HERE, 't25-capdefs-and-branch.json')
io.open(p, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=2))
print('\nWROTE', p)
