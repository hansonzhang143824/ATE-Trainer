# -*- coding: utf-8 -*-
"""t25 复核回复证据: 验证 rule-reviewer 的 F-1 更正 + R2 结论 (独立复算, 只读)。"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import verify_relay_trace as V  # noqa: E402

out = {}

print('=== F-1 复核: SW_BST 是否仍被 SW 家族命中 ===')
a1 = sorted(V.fam_intersect({'SW'}, 'SW_BST'))      # 规则真实调用形态: 迭代 powered, fam = cap token
a2 = sorted(V.fam_intersect({'SW_BST'}, 'SW'))      # 反方向
print('  fam_intersect({"SW"}, "SW_BST")     =', a1, '  <- 规则形态')
print('  fam_intersect({"SW_BST"}, "SW")     =', a2)
print('  判据: "SW_BST".startswith("SW") -> 下一字符 "_" 非字母数字 = 合法 token 边界 ⇒ 命中')
out['F1_recheck'] = {'fam_intersect_powered_SW_token_SW_BST': a1,
                     'reverse': a2,
                     'reviewer_correction_holds': a1 == ['SW_BST'],
                     'my_original_claim_wrong': a1 == ['SW_BST']}

meta = json.load(io.open(os.path.join(ROOT, 'project', 'DALI', 'meta', 'dali_tm_meta.json'),
                         encoding='utf-8-sig'))
sa = io.open(os.path.join(ROOT, 'D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h')
             if False else os.path.join('D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h'),
             encoding='utf-8-sig', errors='replace').read()
caps = {}
for m in re.finditer(r'#define\s+(K\d*_\w+)\s+(\d+)', sa):
    pt = V.cap_pin(m.group(1))
    if pt:
        caps.setdefault(pt, []).append((m.group(1), int(m.group(2))))

print('\n=== 真实数据: powered 含 SW 的函数 ===')
rows = []
for f in meta['functions']:
    ca = f.get('capAuthority') or {}
    pp = {str(x).upper() for x in (ca.get('powered_pins') or [])}
    if 'SW' in pp:
        row = {'fn': f['functionName'], 'powered': sorted(pp)}
        for pt in ('SW_BST', 'BST_SW', 'SW1_BST1', 'SW2_BST2', 'PMID', 'VBAT', 'VBUS', 'VDRV'):
            if pt in caps:
                row[pt] = {'hit': sorted(V.fam_intersect(pp, pt)), 'defines': caps[pt]}
        rows.append(row)
        print('  %-26s powered=%s' % (row['fn'], row['powered']))
        for k, v in row.items():
            if k not in ('fn', 'powered'):
                print('      %-9s hit=%-12s defines=%s' % (k, v['hit'], v['defines']))
out['powered_SW_functions'] = rows

print('\n=== R2 复核: cap token -> define -> 通道号 ===')
r2 = {}
for pt in ('SW_BST', 'BST_SW', 'SW1_BST1', 'SW2_BST2', 'VAC', 'VAC1'):
    r2[pt] = caps.get(pt)
    print('  token %-9s -> %s' % (pt, caps.get(pt)))
print('  规范化规则 (verify_relay_trace.py L274-286): 无通道号别名 → 同通道的 K\\d+_ 权威名')
canon = {}
for r, ch in [(n, c) for pt, lst in caps.items() for (n, c) in lst]:
    if re.match(r'^K\d+_', r):
        canon.setdefault(ch, r)
print('  canon_by_ch =', canon)
resolved = {}
for pt, lst in (('SW_BST', caps.get('SW_BST', [])), ('BST_SW', caps.get('BST_SW', []))):
    names = []
    for n, c in lst:
        names.append(canon.get(c, n) if not re.match(r'^K\d+_', n) else n)
    resolved[pt] = names
print('  规范化后目标:', resolved)
out['R2'] = {'token_defines': r2, 'canon_by_ch': canon, 'resolved': resolved,
             'same_physical_relay': resolved.get('SW_BST') == resolved.get('BST_SW')}

print('\n=== 结论 ===')
print('  F-1: rule-reviewer 的更正成立 =', out['F1_recheck']['reviewer_correction_holds'],
      '(我原表述"K_SW_BST_Cap 修复后不再被 SW 触发"错误, 须更正)')
print('  R2 : 同一物理继电器 =', out['R2']['same_physical_relay'])

p = os.path.join(HERE, 't25-reviewer-response-evidence.json')
io.open(p, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=2))
print('WROTE', p)
