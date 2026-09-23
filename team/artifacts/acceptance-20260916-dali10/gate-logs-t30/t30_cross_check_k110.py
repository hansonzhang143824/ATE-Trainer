# -*- coding: utf-8 -*-
"""t30 交叉验证补充（只读）——用 rule-reviewer 的决定性 locator 复核 t30 断言语义是否仍成立。

背景: 我此前对 SCH L109/L110 的定性有误（写成 K110 的 NC 触点通往 PB0 ⇒ 被误读为"不该闭"）。
      实测 L43/L44 显示**到 BST 的路线**上 K110 是 `(Relay-ON)`，而 L109/L110 是**另一条到 PB0 的路线**
      上 K110 为 `(Relay-NC)`；L724/L725 是 ACM 仪器侧经 K110 NC 落 PB0 的**决定性**证据
      （即：不闭 K110 时 AC 源到不了 BST）。
本脚本逐条复算，确认:
  ① 契约期望集合（aliasResolution[bst2sw].closedRelayNumbers=[110,61]）与 SCH 需闭合串是否一致方向;
  ② payload 实际闭合集合与两者比对结果;
  ③ 结论: 断言"K110 应闭而未闭"方向正确（不是把该闭的判成不该闭）。
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
contract = json.loads(open(os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10/setup-contract.json'), 'rb').read().decode('utf-8-sig'))
sch = io.open(os.path.join(WS, 'project', 'DALI', 'SCH-Connect-Map.txt'), encoding='utf-8-sig').read().splitlines()

print('=== ① 到 BST 的需闭合串 (L42/43/44) ===')
for n in (42, 43, 44):
    print('  L%-4d %s' % (n, sch[n - 1].strip()))
print('\n=== ② 到 PB0 的两组路线 (L109/110 = FPVIe 侧; L724/725 = ACM 仪器侧) ===')
for n in (109, 110, 724, 725):
    print('  L%-4d %s' % (n, sch[n - 1].strip()))

k110_states = set()
for n in (42, 43, 44, 109, 110, 724, 725):
    for m in re.finditer(r'K110\(Relay-(ON|NC)\)', sch[n - 1]):
        k110_states.add((n, m.group(1)))
print('\n  → K110 在各行的状态:', sorted(k110_states))
print('  → 判读: 到 BST 的串上 K110 = Relay-ON（需激磁）; 到 PB0 的串上 K110 = Relay-NC（未激磁时落 PB0）')

print('\n=== ③ 契约期望 vs payload 实际 ===')
alias = [e for e in contract['aliasResolution'] if e.get('alias') == 'bst2sw'][0]
exp = alias['resolution']['closedRelayNumbers']
print('  aliasResolution[bst2sw].closedRelayNumbers =', exp)
print('  relayChain =', json.dumps(alias['resolution']['relayChain'], ensure_ascii=False))
src, _ = read_enc(cfg['derived']['test_cpp'])
import verify_relay_trace as V  # noqa: E402
blocks = dict(V.fn_blocks(src))
relays = V.parse_setons(blocks['TM600_HS_RDSON'])
defines = V.parse_defines(V.read_enc(cfg['derived']['stdafx_h']))
declared = set()
for r in relays:
    m = re.match(r'K(\d+)_', r)
    if m:
        declared.add(int(m.group(1)))
    elif re.fullmatch(r'\d+', r):
        declared.add(int(r))
    elif r in defines:
        declared.add(int(defines[r]))
print('  TM600_HS_RDSON 实际闭合数字集合 =', sorted(declared))
print('  契约期望 ⊆ 实际 ?', set(exp) <= declared, ' 缺失 =', sorted(set(exp) - declared))
_bst_routes = contract['tmDeltas']['TM600']['pinRouteTable']['BST']
_hits = [(r, rv.get('needsClosed'), rv.get('line')) for r, rv in _bst_routes.items()
         if isinstance(rv, dict) and 110 in (rv.get('needsClosed') or [])]
print('  pinRouteTable.BST 中 needsClosed 含 K110 的路线 = %s' % [(r, n, l) for r, n, l in _hits])
print('  ⇒ 路由枚举侧亦要求 K110（与 aliasResolution 同向）:', bool(_hits))

print('\n=== ④ t30 断言输出（K110 方向核对）===')
import subprocess
r = subprocess.run([sys.executable, os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py'), '--list-scope'],
                   capture_output=True, text=True, cwd=os.path.join(WS, 'scripts'),
                   encoding='utf-8', errors='replace')
for line in r.stdout.splitlines():
    if '[t30]' in line:
        print('  ' + line.strip())
print('  exit =', r.returncode)
print('\n  结论: 断言要求"契约声明必需的 K110 必须出现在 SetOn 中" —— 与 SCH L42/43/L724 的方向一致，')
print('        不是把"该闭的"判成"不该闭"。我此前对 L109/110 的定性错误已在此更正。')
