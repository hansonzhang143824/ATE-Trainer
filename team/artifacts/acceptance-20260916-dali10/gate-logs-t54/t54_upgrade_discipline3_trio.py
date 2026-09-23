# -*- coding: utf-8 -*-
"""复核 schematic-expert ② 的"三件套"发现，并把纪律 #3 的粒度升级为"产物+生成器+哈希侧车"。

同时如实标注：**"可再生成 = 逐字节复现 rev 28"属未验证**（取决于生成器输入是否同版）。
"""
import hashlib
import io
import json
import os

RUN = 'team/artifacts/acceptance-20260916-dali10'
SNAP = os.path.join(RUN, 'backups', 't53-20260916-211719')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== ① 快照目录三件套（现算）===')
pairs = [('setup-contract.json', os.path.join(RUN, 'setup-contract.json')),
         ('setup-contract-build.py', os.path.join(RUN, 'setup-contract-build.py')),
         ('setup-contract-pin.json', os.path.join(RUN, 'setup-contract-pin.json'))]
snap_vals, live_vals = {}, {}
for name, live in pairs:
    sp = os.path.join(SNAP, name)
    print('  %-28s 快照 %8d B  /  现盘 %8d B  ⇒ 相同=%s'
          % (name,
             os.path.getsize(sp) if os.path.isfile(sp) else -1,
             os.path.getsize(live) if os.path.isfile(live) else -1,
             (os.path.isfile(sp) and os.path.isfile(live) and sha(sp) == sha(live))))
    if os.path.isfile(sp):
        snap_vals[name] = {'size': os.path.getsize(sp), 'sha256': sha(sp)}
    if os.path.isfile(live):
        live_vals[name] = {'size': os.path.getsize(live), 'sha256': sha(live)}

print('\n=== ② 纪律 #3 升级归档 ===')
MARK = '### 纪律 3·三件套粒度（schematic-expert 发现，我方现算复核）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）; 登记 %d B' % os.path.getsize(REG))
else:
    BLOCK = '''

''' + MARK + '''

**粒度升级（取代"只复制产物"）**
> **覆写被引用过的产物前，复制到 `backups/<task>-<timestamp>/`，且**至少含**：
> **① 产物本身、② 其生成器、③ 其哈希侧车**（凡有者）。
> **只复制产物 ＝ 可读**（能知道当时是什么）；**三件套 ＝ 可复现**（原则上还能再生成）。

**本 run 实证（`backups/t53-20260916-211719/`，我现算）**
| 文件 | 快照 | 现盘 |
| --- | --- | --- |
| `setup-contract.json` | 354,106 B | 377,694 B（不同） |
| `setup-contract-build.py` | 191,623 B | 213,515 B（不同） |
| `setup-contract-pin.json` | 8,555 B | 11,273 B（不同） |
⇒ 该目录**同一时刻**固定了"产物 + 生成器 + 侧车"三者 ⇒ 保存的不只是**状态**，还有**复现该状态的手段**。

**⚠️ UNKNOWN（如实标注，不主张）**：能否**逐字节**再生成 rev 28，还取决于**生成器的输入**（CSV / IR / DFT 等）
是否也处于相符版本 —— **此点未验证**。可确证的只是：**该目录把那一版的产物、生成器与侧车一并固定下来了**。

**配套动作**：覆写前**先问三句** ——"产物有副本吗？它的生成器呢？哈希侧车呢？"
留证：`gate-logs-t54/t54_verify_surviving_snapshot.py` / `t54-surviving-snapshot-verify.log`。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    t2 = io.open(REG, encoding='utf-8-sig').read()
    print('  已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
    for k in (MARK, '只复制产物 ＝ 可读', '三件套 ＝ 可复现', 'UNKNOWN'):
        print('    含 %-26s %s' % (k, k in t2))
