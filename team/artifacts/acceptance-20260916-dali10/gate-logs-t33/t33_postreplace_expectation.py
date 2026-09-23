# -*- coding: utf-8 -*-
"""复核 setup-architect 的四项数值断言 + 固化「落盘后预期」的两种口径（避免 t35/t34 沿用已被否证的前提）。

只读取证；不改任何他方产物。所有值现算，不手抄。
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')


def line(label, p, keys=()):
    d = open(p, 'rb').read()
    t = d.decode('utf-8-sig', errors='replace')
    print('  %-34s %8d B  %s' % (label, len(d), hashlib.sha256(d).hexdigest()))
    for k in keys:
        print('       内容键 %-28s ×%d' % (k, t.count(k)))
    return t


print('=== ① 他方四项数值断言复核（现算）===')
line('t35-contract-reconciliation.md', os.path.join(RUN, 't35-contract-reconciliation.md'))
line('payload (DELIVERED)', os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp'),
     ('t29 PER-FUNCTION JUSTIFICATION', 'K109_BUSL1_PB0', 'K110_ACM18_BST', 'SW12_U1REF_BST_ACM'))
line('DEPLOYED test.cpp', 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',
     ('K109_BUSL1_PB0', 'K110_ACM18_BST'))

print('\n=== ② 我方判据：现行 SetOn vs 两种契约口径（复核我上一条的结论）===')
import sys
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
t, _e = read_enc(cfg['derived']['test_cpp'])
blocks = dict(V.fn_blocks(t))
# ⚠️ 更正（schematic-expert 指出、我按现盘契约重算确认）：
#   bst2sw.usedByTm = [TM600, TM1205]，**不含 TM601**；TM601 走自己的别名 sw2pgnd=[154,155,60,61]。
#   ⇒ pin-5（[48,76]）口径只约束 **TM600**；先前把该期望套到 TM601 上会制造**假红**。
cases = {
    'TM600_HS_RDSON': {
        'pin-18 口径（契约 rev 24 现状）': {60, 61, 83, 110},
        'pin-5  口径（t42 判定后, 建议 rev 25）': {48, 61, 76},
    },
    'TM601_LS_RDSON': {
        'rev 24 口径（其自身别名 sw2pgnd）': {60, 61, 154, 155},
        # rev 25 不应改变 TM601 的期望：它不属 bst2sw.usedByTm
        'rev 25 口径（仍为 sw2pgnd，不应被 bst2sw 污染）': {60, 61, 154, 155},
    },
}
for fn, exp_map in cases.items():
    nums = set()
    for r in V.parse_setons(blocks[fn]):
        m = re.match(r'K(\d+)_', r)
        if m:
            nums.add(int(m.group(1)))
        elif re.fullmatch(r'\d+', r):
            nums.add(int(r))
    print('  %s 实际=%s' % (fn, sorted(nums)))
    for label, exp in exp_map.items():
        print('     %-44s 期望=%-18s 缺失=%s' % (label, sorted(exp), sorted(exp - nums)))

print('\n=== ③ 结论：落盘后「bst-sw 是否转绿」取决于契约口径（且仅 TM600 受影响）===')
print('  · 若契约仍为 rev 24（pin-18 口径 [110,61]）⇒ t29 落盘后 TM600 缺失=[] ⇒ bst-sw 转 GREEN')
print('  · 若契约已 rev 25（pin-5 口径 [48,76]）  ⇒ TM600 仍缺 [48,76]')
print('    ⚠️ 但按 Captain 裁定 (i)「rev 25 + payload 同一批」，payload 的 TM600 将闭 [48,76] ⇒ 批后应 GREEN')
print('  · **TM601 不受 bst2sw 约束**（其别名 sw2pgnd 在 rev 24 下已满足）⇒ 不得把 [48,76] 套给它（否则假红，')
print('    且会把实现推向 t38 已明确移除的"TM601 ACM 驱动"方向）')

