# -*- coding: utf-8 -*-
"""复核 schematic-expert 的计数更正（8→4）与"6 函数经 K48+K76 到 BST"的先例论证。

关键区分：**总提及（含注释）** vs **SetOn 操作数中的调用点**。我此前在 t44 交叉验证里报的是 8 —— 本脚本判定它属于哪一类。
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
with open(cfg['derived']['test_cpp'], 'rb') as f:
    t = f.read().decode('utf-8-sig', errors='replace')
lines = t.splitlines()


def stats(tok):
    """返回 (SetOn 操作数中出现次数, 注释行出现次数, 其它, 调用点所在函数/行)"""
    in_seton, in_comment, other, sites = 0, 0, 0, []
    for i, ln in enumerate(lines, 1):
        if tok not in ln:
            continue
        stripped = ln.strip()
        if stripped.startswith('//') or stripped.startswith('*'):
            in_comment += 1
            continue
        m = re.search(r'cbite\.SetOn\(([^;]*)\);', ln)
        if m and tok in m.group(1):
            in_seton += 1
            sites.append(i)
        else:
            other += 1
    return in_seton, in_comment, other, sites


print('=== ① 逐 token 计数（总提及 vs SetOn 调用点）===')
for tok in ('K48_ACM5_AMP_REF', 'K76_ACM_BST', 'K_FPVIH_TO_BST_A', 'K_BST_ACM',
            'K_FPVIL_TO_BST_B', 'K110_ACM18_BST', 'K109_BUSL1_PB0'):
    s, c, o, sites = stats(tok)
    print('  %-20s SetOn操作数=%-3d 注释行=%-3d 其它=%-3d 总提及=%-3d 调用点行=%s'
          % (tok, s, c, o, s + c + o, sites))

print('\n=== ② 我此前报的"8"属于哪一类？ ===')
for tok in ('K48_ACM5_AMP_REF', 'K76_ACM_BST'):
    s, c, o, _ = stats(tok)
    print('  %-18s 总提及=%d（我报的 8）; SetOn 调用点=%d（对方更正后的 4）; 注释=%d'
          % (tok, s + c + o, s, c))

print('\n=== ③ "6 个函数经 K48+K76 到 BST" 复核（按函数块）===')
blocks = V.fn_blocks(t)
idx_of = {}
for i, ln in enumerate(lines, 1):
    idx_of[i] = ln
for name, blk in blocks:
    has48 = 'K48_ACM5_AMP_REF' in blk
    has76 = 'K76_ACM_BST' in blk
    hasA = 'K_FPVIH_TO_BST_A' in blk
    if has48 or has76 or hasA:
        # 统计该块内 SetOn 调用点数
        n48 = sum(1 for m in re.finditer(r'cbite\.SetOn\(([^;]*)\);', blk) if 'K48_ACM5_AMP_REF' in m.group(1))
        n76 = sum(1 for m in re.finditer(r'cbite\.SetOn\(([^;]*)\);', blk) if 'K76_ACM_BST' in m.group(1))
        nA = sum(1 for m in re.finditer(r'cbite\.SetOn\(([^;]*)\);', blk) if 'K_FPVIH_TO_BST_A' in m.group(1))
        print('  %-28s SetOn(48)=%-2d SetOn(76)=%-2d SetOn(K_FPVIH_TO_BST_A)=%-2d'
              % (name, n48, n76, nA))

print('\n=== ④ K110 / K76 是否共用两根网（pin 级）===')
import csv
rows = list(csv.DictReader(io.open(cfg['inputs']['csv_schematic'], encoding='utf-8-sig', errors='replace')))


def net_of(des, pin_suffix):
    for r in rows:
        if str(r.get('Designator') or '') == des and str(r.get('MemberName') or '').endswith('.' + pin_suffix):
            return str(r.get('NetName') or '')
    return None


for label, a, b in (('pin4', ('K110_BST_S1', '4'), ('K76_ACM_BST_S1', '4')),
                    ('pin5', ('K110_BST_S1', '5'), ('K76_ACM_BST_S1', '5'))):
    na, nb = net_of(*a), net_of(*b)
    print('  %s: %s=%s | %s=%s  同网=%s' % (label, a[0], na, b[0], nb, na == nb))
