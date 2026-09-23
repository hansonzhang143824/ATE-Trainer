# -*- coding: utf-8 -*-
"""t25 —— F3 (VBUS) 的"代码侧不可修"反证 + 沙箱提案验证。

反证: 三种 fam_intersect 语义 (修复前 / t25 已落地 / reviewer 建议版) 下,
      `TM601_LS_RDSON -> K5_VBUS_Cap` 的需求**恒定存在** ⇒ F3 不是匹配语义缺陷。

沙箱提案: 只在**副本** meta 上按 BD-08 把 TM601_LS_RDSON 的 powered_pins 里的 VBUS
          移除 (副本写在 team/artifacts/<run>/gate-logs-t25/sandbox-f3/), 跑完整规则,
          与线上 meta 的完整输出逐条对照 —— 证明"只影响 F3 目标, 不产生任何新告警/新红"。
          **不写 project/DALI/meta/dali_tm_meta.json** (不在 t25 inScope, 需授权)。
"""
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SB = os.path.join(HERE, 'sandbox-f3')
os.makedirs(SB, exist_ok=True)
META = os.path.join(ROOT, 'project', 'DALI', 'meta', 'dali_tm_meta.json')

# ---------- 1. 反证: 需求矩阵 (引自 t25-variant-matrix.json) ----------
vm = json.load(io.open(os.path.join(HERE, 't25-variant-matrix.json'), encoding='utf-8'))
target = 'TM601_LS_RDSON -> K5_VBUS_Cap'
print('=== F3 反证: 三种匹配语义下该需求是否存在 ===')
for tag, name in (('v1', '修复前 (startswith 双向)'), ('v2', 't25 已落地 (对称 token 边界)'),
                  ('v3', 'reviewer 建议 (只正方向边界)')):
    print('  %-34s 含该需求 = %s' % (name, target in vm[tag]))
constant = all(target in vm[t] for t in ('v1', 'v2', 'v3'))
print('  ⇒ 恒定存在 = %s ⇒ F3 不能在 fam_intersect / 规则侧修掉\n' % constant)

# ---------- 2. 沙箱提案 meta (副本) ----------
meta = json.load(io.open(META, encoding='utf-8-sig'))
before_pp = None
out_meta = json.loads(json.dumps(meta))
for f in out_meta['functions']:
    if f['functionName'] == 'TM601_LS_RDSON':
        before_pp = list(f['capAuthority']['powered_pins'])
        f['capAuthority']['powered_pins'] = [p for p in before_pp if str(p).upper() != 'VBUS']
        f['capAuthority']['_t25ProposalNote'] = (
            'SANDBOX PROPOSAL ONLY (t25): VBUS removed from powered_pins because BD-08 makes '
            'vset vbus 5.0 a simulationDomainReference, not an ATE stimulus for this item '
            '(setup-contract.json tmDeltas.TM601.simulationDomainReference; DFT.csv TM601 row '
            'contains no vbus token). VBUS arrival on the schematic needs K3 '
            '(SCH-Connect-Map.txt:213/421), which this item does not close.')
print('=== 沙箱提案: TM601_LS_RDSON.powered_pins ===')
print('  before =', before_pp)
print('  after  =', [f for f in out_meta['functions']
                     if f['functionName'] == 'TM601_LS_RDSON'][0]['capAuthority']['powered_pins'])
prop_meta = os.path.join(SB, 'dali_tm_meta.t25proposal.json')
io.open(prop_meta, 'w', encoding='utf-8').write(
    json.dumps(out_meta, ensure_ascii=False, indent=2))

# ---------- 3. A/B: 线上 meta vs 沙箱提案 meta, 完整规则输出 ----------
def run(meta_path, tag):
    log = os.path.join(SB, tag + '.relay-trace.log')
    with io.open(log, 'w', encoding='utf-8') as fh:
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'verify_relay_trace.py'),
                            '--meta', meta_path],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=os.path.join(ROOT, 'scripts'))
    t = io.open(log, encoding='utf-8').read()
    summary = re.search(r'^\[relay\].*$', t, re.M)
    return {'exit': r.returncode, 'log': log, 'summary': summary.group(0) if summary else '',
            'lines': sorted(re.findall(r'^  - (.*)$', t, re.M))}


a = run(META, 'live')
b = run(prop_meta, 'proposal')
removed = sorted(set(a['lines']) - set(b['lines']))
added = sorted(set(b['lines']) - set(a['lines']))
print('=== 沙箱 A/B 全树对照 (live meta vs proposal meta) ===')
print('  live    :', a['summary'])
print('  proposal:', b['summary'])
print('  exit: live=%d proposal=%d' % (a['exit'], b['exit']))
print('  消除的告警 (%d):' % len(removed))
for x in removed:
    print('    -', x)
print('  新增的告警 (%d, 必须为 0):' % len(added))
for x in added:
    print('    +', x)
res = {'constantUnderAllFamIntersectVariants': constant,
       'proposal': {'field': 'TM601_LS_RDSON.capAuthority.powered_pins',
                    'before': before_pp,
                    'after': [p for p in before_pp if str(p).upper() != 'VBUS'],
                    'file': prop_meta},
       'ab': {'live': a, 'proposal': b, 'removed': removed, 'added': added}}
io.open(os.path.join(HERE, 't25-f3-sandbox.json'), 'w', encoding='utf-8').write(
    json.dumps(res, ensure_ascii=False, indent=2))
print('\nWROTE', os.path.join(HERE, 't25-f3-sandbox.json'))
