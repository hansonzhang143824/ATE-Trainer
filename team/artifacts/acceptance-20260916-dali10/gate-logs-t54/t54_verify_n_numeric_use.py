# -*- coding: utf-8 -*-
"""复核 schematic-expert 的"欠严（under-strict）"更正：`n = defines[r]` 是否被当数字使用？

他说：L401 `if n in on_set` / L403 `if n in nc_set` ⇒ 多值宏只校验首值 ⇒ 欠严（而非"不受影响"）。
我此前结论"n 之后未再参与数值比较"——若他成立，则我的表述**过强**，须更正。
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(WS, 'scripts', 'verify_relay_trace.py')
src = io.open(SRC, encoding='utf-8-sig').read().splitlines()

print('=== ① n 的全部使用（逐行，含上下文）===')
for i, l in enumerate(src, 1):
    if re.search(r'(?<![\w])n(?![\w])', l) and i >= 370:
        print('  L%-4d %s' % (i, l.strip()[:130]))

print('\n=== ② L395-412 上下文 ===')
for i in range(395, 413):
    if i - 1 < len(src):
        print('  L%-4d %s' % (i, src[i - 1].strip()[:130]))

print('\n=== ③ parse_setons 是否做宏展开（L90-100）===')
for i in range(90, 101):
    if i - 1 < len(src):
        print('  L%-4d %s' % (i, src[i - 1].strip()[:130]))

print('\n=== ④ on_set / nc_set 的来源（parse_map_rels）===')
for i, l in enumerate(src, 1):
    if 'on_set' in l or 'nc_set' in l:
        print('  L%-4d %s' % (i, l.strip()[:130]))
