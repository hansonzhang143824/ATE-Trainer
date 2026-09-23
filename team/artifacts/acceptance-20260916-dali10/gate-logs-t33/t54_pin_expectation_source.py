# -*- coding: utf-8 -*-
"""把"门禁期望集的实际构成"钉进 t33-transition-plan.md（幂等）。

依据：直接读 `scripts/verify_bst_sw_sequence.py::expected_for_tm()` 的**实际代码路径**（非推断）：
  1) 遍历 `tmDeltas.<base>.aliasesUsed` 中每个别名的 `resolution.closedRelayNumbers`
  2) 遍历所有别名，凡 `usedByTm` 文案里出现 `<base>`（正则 \\b(TM\\d+)\\b）者也取其 closedRelayNumbers
  ⇒ 期望集**只**由该两源构成；`pinRouteTable` 仅作**定位说明**、`relaySet` 仅作**预算池**（不作为要求）。

据此给出落盘后必须现算的三项，避免 t54 用错集合解释红/绿。
"""
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PLAN = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t33', 't33-transition-plan.md'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
MARK = '### 门禁期望集的**实际构成**（读源码取得，非推断）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


C = json.loads(io.open(os.path.join(RUN, 'setup-contract.json'), encoding='utf-8-sig').read())
idx = {}
for e in (C.get('aliasResolution') or []):
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

base = 'TM600'
d = C['tmDeltas'][base]
exp = {}
for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
    for n in sorted(idx.get(a, (set(), set()))[0]):
        exp.setdefault(n, 'aliasesUsed:%s' % a)
for a, (nums, users) in idx.items():
    if base in users:
        for n in sorted(nums):
            exp.setdefault(n, 'usedByTm:%s' % a)

print('现盘契约 revision = %s ; size = %d B' % (C.get('revision'), os.path.getsize(os.path.join(RUN, 'setup-contract.json'))))
print('TM600 期望集（按源码路径现算）= %s' % sorted(exp))
for n in sorted(exp):
    print('   K%-4d ← %s' % (n, exp[n]))

BLOCK = '''

---

''' + MARK + '''

`verify_bst_sw_sequence.py::expected_for_tm()` 的**实际代码路径**（直读源码，非推断）：
1. 遍历 `tmDeltas.<base>.aliasesUsed` 里每个别名的 `resolution.closedRelayNumbers`；
2. 遍历**所有**别名，凡 `usedByTm` 文案中经 `\\b(TM\\d+)\\b` 命中 `<base>` 者，取其 `closedRelayNumbers`。
⇒ **期望集只由这两源构成**；`pinRouteTable` 仅供**定位说明**（locator），`relaySet` 仅供**预算池**（不作为要求）。

**现盘实测（契约 revision %s）**：TM600 期望集 = **`%s`**
（逐项来源：%s）

⇒ **落盘后必须现算且并列记录三项**，不得凭记忆解释红/绿：
1. `setup-contract.json` 的 **revision** 与 `aliasResolution[bst2sw].resolution.closedRelayNumbers`；
2. 上式**现算**出的 TM600 期望集（以及 TM601 的对应集合）；
3. 落盘后 `test.cpp` 的 `compiledRevision`（现算）与其 TM600/TM601 SetOn。
**判据**：期望集 ⊆ SetOn ⇒ `bst-sw` 应 GREEN；若期望集仍含 `110` 而 payload 不含 ⇒ 红因是"**契约权威值未消歧**"，
须按此归因（**不得**记为缺陷、**不得**为迎合门禁补 `110`）。**阳性对照重建后**应为"缺 `48/76` ⇒ 红"。
''' % (C.get('revision'), sorted(exp), '; '.join('K%d←%s' % (n, exp[n]) for n in sorted(exp)))

t = io.open(PLAN, encoding='utf-8-sig').read()
if MARK in t:
    print('\n已写入过（幂等）: %d B' % os.path.getsize(PLAN))
else:
    io.open(PLAN, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('\n已写入 transition-plan: %d B / %s' % (os.path.getsize(PLAN), sha(PLAN)))
