# -*- coding: utf-8 -*-
"""t42 相关：ACM200 引脚归属（_5 vs FH18）对"到 BST 应闭集合"的**实测取证**。

背景：Captain 通报 t42 正在判定 `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,..."` 的
      宏 `_5` 是否即 ACM200 的 FH18/SH18 通道 —— 它决定"到 BST 需 `[48,76]` 还是 `[110,61]`"。
本脚本只做**只读取证**，给出两套候选各自的可复核依据，供 t42/schematic-expert 裁决。
"""
import csv
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
CSV = cfg['inputs']['csv_schematic']
rows = list(csv.DictReader(io.open(CSV, encoding='utf-8-sig', errors='replace')))
print('Dali-SCH.csv %d B / %s' % (os.path.getsize(CSV),
                                  hashlib.sha256(open(CSV, 'rb').read()).hexdigest()))

# 全字段包含式搜索（避免按列名猜错导致的假阴性）
def find(sub):
    out = set()
    for r in rows:
        blob = ' | '.join(str(v) for v in r.values())
        if sub in blob:
            out.add((str(r.get('Designator') or ''), str(r.get('MemberName') or ''),
                     str(r.get('NetName') or '')))
    return sorted(out)


print('\n=== ① 源侧标识在网表里的出现（决定性）===')
for sub in ('S5_5', 'S5_FH18', 'S5_SH18', 'SW12_U1REF_BST_ACM', 'FH18', 'SH18', 'S24_P10'):
    hits = find(sub)
    print('  [%-22s] %d hit(s)' % (sub, len(hits)))
    for h in hits[:5]:
        print('       %-22s %-22s %s' % h)

print('\n=== ② StdAfx.h 的角色宏（既有权威定性）===')
_t, _enc = read_enc(cfg['derived']['stdafx_h'])
t = _t
for pat in (r'#define\s+K_FPVIH_TO_BST_A.*', r'#define\s+K_FPVIL_TO_BST_B.*',
            r'#define\s+K_BST_ACM.*', r'#define\s+K(48|76|109|110)_\w+\s+\d+.*'):
    for m in re.finditer(pat, t):
        s = m.group(0).strip()
        if '//' in s:
            s = s.split('//', 1)[0].rstrip() + '   // ' + s.split('//', 1)[1].strip()
        print('  ', s[:150])

print('\n=== ③ 契约侧（rev 24）对同一问题的表述 ===')
import json
c = json.loads(open(os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10/setup-contract.json'), 'rb').read().decode('utf-8-sig'))
bst = c['tmDeltas']['TM600']['pinRouteTable']['BST']
for r, rv in bst.items():
    print('  %-58s needsClosed=%-30s line=%s' % (r, rv.get('needsClosed'), rv.get('line')))
al = [e for e in c['aliasResolution'] if e.get('alias') == 'bst2sw'][0]
print('  aliasResolution[bst2sw].closedRelayNumbers =', al['resolution']['closedRelayNumbers'])
print('  aliasResolution[bst2sw].relayChain =',
      [(x.get('relay'), x.get('state')) for x in al['resolution']['relayChain']])

print('\n=== ④ 判读（供 t42 裁决；两套候选各有依据，本脚本不选边）===')
print('  候选甲 [48,76]（ACM200 直接路线）依据：')
print('    · StdAfx.h: K_BST_ACM = 48,76  // ACM200[] -> BST: K48_ACM5_AMP_REF + K76_ACM_BST')
print('    · StdAfx.h: K48_ACM5_AMP_REF 命名含 ACM5；K76_ACM_BST 为 BST 侧件')
print('    · 契约 pinRouteTable.BST["列6: ACM200 → PIN (Share继电器)"] needsClosed=[48,76] (L672)')
print('    · 宏 Pin_Channel_define.h: _PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,S6_5,..." ⇒ 通道 5')
print('  候选乙 [110,61]（FPVIe 低侧路线）依据：')
print('    · SCH:42/43/44 CH0 Low -> BST 需闭合 K109,K110,...（K109(ON) -> K110(ON) -> BST_F）')
print('    · 契约 aliasResolution[bst2sw].closedRelayNumbers=[110,61] 与 pinRouteTable CH0 Low')
print('    · StdAfx.h: K_FPVIL_TO_BST_B = 109,110  // FPVIe[L] -> BST')
print('  ⚠️ 关键判别点（t42 的实质问题）：**SW12_U1REF_BST_ACM 这一台仪器实例实际落在哪条链上**——')
print('     若它 = ACM200 的通道 5（宏字面 S5_5），则 [48,76] 生效、[110,61] 属 FPVIe 低侧而非本实例；')
print('     若夹具把该实例接到 ACM200 FH18/SH18，则 [110,61] 生效。')
print('     ⇒ 这决定 t29（补 K109/K110）是**必需**还是**依约保守**，也决定 t30 断言的期望集合。')
