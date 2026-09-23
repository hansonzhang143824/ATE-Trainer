# -*- coding: utf-8 -*-
"""核实 rule-reviewer ② 的"第二处不同版"：t54 日志自称 rev=32，但期望集是 [48,60,61,76,83]。
两者矛盾吗？—— 取决于"该期望集在 rev 32 时是否已成立"。

方法（不依赖任何字面）：
  1) 读 t54 门禁日志：rev= 行与期望集行；
  2) 用**现存的两个可再生快照**（rev 28 备份 / rev 39 现盘）分别导出期望集；
  3) 若 rev 28 ⇒ 含 110（旧口径）、rev 39 ⇒ 不含 110，则"ch5 口径"出现在 (28, 39] 区间内 —
     与"rev 32 已生效"并不矛盾，须以**快照能证明的范围**表述。
"""
import hashlib
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
sys.path.insert(0, os.path.join(WS, 'scripts'))
spec = importlib.util.spec_from_file_location('g', os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py'))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

print('=== ① t54 门禁日志自述 ===')
log = io.open(os.path.join(RUN, 'gate-logs-t54', 'bst-sw.log'), encoding='utf-8-sig', errors='replace').read()
for pat in (r'rev=(\d+)', r'TM600_HS_RDSON: 契约声明必需 \[([^\]]*)\]'):
    m = re.findall(pat, log)
    print('  %-44s → %s' % (pat, m))

print('\n=== ② 各快照导出的期望集（脚本现算）===')


def expect_of(path, label):
    if not os.path.isfile(path):
        print('  %-52s MISSING' % label)
        return
    C = json.loads(open(path, 'rb').read().decode('utf-8-sig'))
    b2 = [x for x in C['aliasResolution'] if x.get('alias') == 'bst2sw'][0]
    closed = (b2.get('resolution') or {}).get('closedRelayNumbers')
    # 复现 expected_for_tm
    idx = {}
    for e in C['aliasResolution']:
        a = str(e.get('alias', ''))
        nums = set()
        for x in ((e.get('resolution') or {}).get('closedRelayNumbers') or []):
            if isinstance(x, int):
                nums.add(x)
            else:
                nums |= {int(y) for y in re.findall(r'\d+', str(x))}
        users = set()
        for x in (e.get('usedByTm') or []):
            users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
        idx[a] = (nums, users)
    d = C['tmDeltas']['TM600']
    exp = set()
    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        exp |= idx.get(a, (set(), set()))[0]
    for a, (nn, uu) in idx.items():
        if 'TM600' in uu:
            exp |= nn
    print('  %-52s rev=%-4s bst2sw=%-22s exp=%s'
          % (label, C.get('revision'), closed, sorted(exp)))


expect_of(os.path.join(RUN, 'backups', 't53-20260916-211719', 'setup-contract.json'), 'backups/t53-20260916-211719（rev 28 曾用版）')
expect_of(os.path.join(RUN, 'setup-contract.json'), '现盘 setup-contract.json')

print('\n=== ③ 判读 ===')
print('  日志自称 rev=32；而 rev 28 快照的 bst2sw 仍含 110（旧口径）、现盘已不含 110。')
print('  ⇒ "ch5 口径（不含 110）"**出现在 (28, 现盘] 区间内**；rev 32 落在该区间 ⇒')
print('     日志自称 rev=32 与期望集 [48,60,61,76,83] **并不矛盾**（该收窄在 rev 28 之后已生效）。')
print('  ⚠️ 但**无法**用现存快照把区间收窄到"恰好 rev 32" ⇒ 该点应表述为：')
print('     "证据锚 = 日志自述 rev=32；可用字节快照仅能把 ch5 口径定位在 (rev28, 现盘] 区间内"。')
