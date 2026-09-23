# -*- coding: utf-8 -*-
"""修 schematic-expert ② 指出的"两名混放"：`bst2sw_supersededRelaySet` 名字会被读成"旧闭集"，
但契约里它是**被取代的 CH1 变体集**；旧闭集另在 `closedRelayNumbersSuperseded = [110,61]`。
改法：改名 + 同时给出两个字段并各自注明语义。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = 'bst2sw_supersededCh1VariantRelaySet'

t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B ; 已含 %s = %s' % (os.path.getsize(GEN), MARK, MARK in t))
if MARK in t:
    print('已修（幂等）')
    raise SystemExit(0)

OLD = "        'bst2sw_supersededRelaySet': b2['resolution'].get('supersededRelaySet'),"
NEW = ("""        # ⚠️ 两名区分（schematic-expert 指出）：契约里"被取代"有两个不同概念，名字极易混读。
        'bst2sw_closedRelayNumbersSuperseded': {
            'value': b2['resolution'].get('closedRelayNumbersSuperseded'),
            'meaning': '**被取代的闭集**（旧 ch18 对 `[110,61]`）'),
        },
        'bst2sw_supersededCh1VariantRelaySet': {
            'value': b2['resolution'].get('supersededRelaySet'),
            'meaning': ('**被取代的 CH1 变体集**（`K_FPVIH_TO_BST_B` = `[131,132,134,135]`），'
                        '**不是**本项曾被要求的闭集 —— 旧闭集见上一字段 `[110,61]`'),
            'contractField': 'resolution.supersededRelaySet',
            'contractEvidence': (b2['resolution'] or {}).get('evidenceSupersededChannel1'),
        },
        # 旧名保留为**只读别名**（明确标注语义），避免已引用者落空
        'bst2sw_supersededRelaySet': {
            'value': b2['resolution'].get('supersededRelaySet'),
            'aliasOf': 'bst2sw_supersededCh1VariantRelaySet',
            'warning': '⚠️ 该名字**易被误读为"被取代的闭集"**；旧闭集实为 `[110,61]`（见 bst2sw_closedRelayNumbersSuperseded）',
        },""")
if OLD not in t:
    print('ERROR: 锚点未命中')
    raise SystemExit(1)
t = t.replace(OLD, NEW, 1)
io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
print('  已改 → %d B' % os.path.getsize(GEN))

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成:', (r.stdout or '').strip().replace('\n', ' | ')[:150] if r.stdout else r.stderr[:150])
