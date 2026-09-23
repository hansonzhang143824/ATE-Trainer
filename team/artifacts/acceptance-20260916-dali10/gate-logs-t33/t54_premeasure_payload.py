# -*- coding: utf-8 -*-
"""t54 预备：用**被审脚本自身的函数**对 payload 预演期望 vs 实际（不落盘、不改任何被审对象）。

为什么不能直接跑 `verify_bst_sw_sequence.py`：其目标路径是**写死**的
（`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`），CLI 无法覆盖 ⇒ 落盘前无法用它直接测 payload。
故本脚本 import 该脚本的解析函数，把 payload 当作输入做"预演"。

产出：对 t54 的**可执行预测**——落盘后 bst-sw 是否会 GREEN，以及缺什么。
"""
import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
sys.path.insert(0, os.path.join(WS, 'scripts'))
import verify_relay_trace as V   # noqa: E402
import proj_config  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


PAY = os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp')
DEP = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'
CONTRACT = os.path.join(RUN, 'setup-contract.json')

for label, p in (('payload (候选落盘件)', PAY), ('部署态（当前门禁输入）', DEP),
                 ('契约', CONTRACT)):
    print('  %-26s %8d B  %s' % (label, os.path.getsize(p), sha(p)))

pay = io.open(PAY, encoding='utf-8-sig', errors='replace').read()
dep = io.open(DEP, encoding='utf-8-sig', errors='replace').read()

import re
import json

C = json.loads(io.open(CONTRACT, encoding='utf-8-sig').read())

print('\n=== 契约里 bst2sw 的"声明必需"（我的断言即按此派生）===')
e = [x for x in C['aliasResolution'] if x.get('alias') == 'bst2sw'][0]
print('  resolvedClosed =', e['resolution'].get('closedRelayNumbers'))
print('  usedByTm =', e.get('usedByTm'))

print('\n=== 两态的实际闭合（TM600）===')
for label, txt in (('部署态', dep), ('payload', pay)):
    blk = dict(V.fn_blocks(txt)).get('TM600_HS_RDSON', '')
    nums = set()
    for r in V.parse_setons(blk):
        m = re.match(r'K(\d+)_', r)
        if m:
            nums.add(int(m.group(1)))
        elif re.fullmatch(r'\d+', r):
            nums.add(int(r))
    print('  %-8s = %s' % (label, sorted(nums)))
    declared = set(e['resolution'].get('closedRelayNumbers') or [])
    print('     相对 out 契约[110,61] 缺失 = %s' % sorted(declared - nums))

print('\n=== t54 的两条路径（取决于 t53 是否已把 ch5 读法落为权威）===')
print('  路径 1：t53 已把 bst2sw 改为 ch5 路线（期望含 48,76）⇒ payload 已闭 {48,60,61,76} ⇒ 预期 bst-sw GREEN ✓')
print('  路径 2：t53 仅"只增不翻"、resolvedClosed 仍 [110,61] ⇒ payload 未闭 110 ⇒ **bst-sw 仍 NEW-RED**')
print('          （注意：payload 现闭 {48,76,60,61}，**不含 110**）')
print('  ⇒ 故 t54 的判据必须**先现算契约 rev 与 resolvedClosed**，再据此解释 bst-sw 的红/绿；')
print('     不能假定"落盘即绿"。')
