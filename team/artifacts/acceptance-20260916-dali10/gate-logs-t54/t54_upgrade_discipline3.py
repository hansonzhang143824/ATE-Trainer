# -*- coding: utf-8 -*-
"""把纪律 #3 升级为**可操作形式**，并登记"唯一幸存快照"作为反例式证明（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 纪律 3·可操作形式（schematic-expert 建议 + 我方实测取证）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B' % os.path.getsize(REG))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**可操作形式（指定时机 / 位置 / 命名）**
> **凡将原地覆写某个已被引用过的产物，先复制到 `backups/<task>-<timestamp>/`；**
> 此后该状态**可复核**，否则**永久只能靠消息**（＝不可复核）。

**反例式证明（本 run 实测，比正面陈述更有力）**
全树按已知旧尺寸复查五个中间态，**只有一个幸存**：
| 中间态 | 是否有字节副本 |
| --- | --- |
| `setup-contract.json` **rev 28**（354,106 B / `78cfc954…` / `closedRelayNumbers=[110,61]`） | **有** — `backups/t53-20260916-211719/setup-contract.json` |
| `setup-contract.json` rev 24（328,805 B） | 无（0 命中） |
| payload `6034af71…`（41,797 B，union 版） | 无 |
| payload `2d0984d9…`（39,457 B） | 无 |
| payload `c03632d9…`（42,998 B） | 无 |

**该快照我独立现算复核通过**（未采信任何字面）：
```
路径   = team/artifacts/acceptance-20260916-dali10/backups/t53-20260916-211719/setup-contract.json
size   = 354,106 B ; sha256 = 78cfc954b73a007e8cc210c1033ec35b23e7dec1724eec6665717a4dcb111388
revision = 28 ; aliasResolution[bst2sw].resolution.closedRelayNumbers = [110, 61]
```
⇒ **其 rev 28 的两项判定现在有字节级证据、可第三方复核**（此前只有其字面）：
(a) "门禁当时真正读取的字段仍是 `[110,61]`"；(b) "该次修订当时只加未撤（add-only）"。
⇒ **同时也是本 run 唯一"当时态仍可复核"的中间态** —— 能被复核的原因**正是"覆写前先复制了字节"**。
⇒ **结论**：不是"哈希不可靠"，而是"**哈希不保存字节**"。
留证：`gate-logs-t54/t54_verify_surviving_snapshot.py` / `t54-surviving-snapshot-verify.log`。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '反例式证明', '哈希不保存字节', 'backsups/<task>' if False else 'backups/<task>-<timestamp>/'):
    print('  含 %-34s %s' % (k[:32], k in t2))
