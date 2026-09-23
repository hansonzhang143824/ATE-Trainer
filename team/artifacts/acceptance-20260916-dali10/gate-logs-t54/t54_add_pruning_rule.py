# -*- coding: utf-8 -*-
"""并入 setup-architect ② 立名的规则（幂等）：`identityBasedPruningRule`
—— 并收录其指出的**前置条件**：**稳定投影是按身份去重的前提**（不是独立加分项）
   ⇒ 与本项目"同 size 不同 sha 属正常"是同一体系的两端。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附三十｜`identityBasedPruningRule`：按身份去重（及其前置条件＝稳定投影）'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：setup-architect 将我方处置立名为 **`identityBasedPruningRule`**，并采纳我方指出的**前置条件**。

**规则（照录其陈述）**
> **记录产物身份的 append-only 日志应"仅在身份变化时追加"，并在 `reason` 里说明**
> （`identity-change` vs `routine-reverify-未追加`）
> ⇒ **增长被"不同身份数"而非"检查次数"限定** ✓

**★ 前置条件（我方洞察，其照录）**
```
**按身份去重的前提是"身份投影稳定"** —— 本 run 验证：body 哈希（`projectionSpec v2`，已声明
  serialization/encoding/bodyDefinition）**跨秒稳定 = True**；
  **若无 v2 投影，就无从判定"身份是否变化"** ⇒
  ⇒ **稳定投影是去重的前置条件，不是独立的加分项** ✓
```
**与本项目另一端的关系**：**"同 size 不同 sha 属正常"** 与 **"按身份去重"** 是**同一体系的两端** ——
**先有稳定投影 ⇒ 才谈得上按身份去重 / 比对** ✓

**归族**：**"少写一次＝少一次漂移"在自动化日志上的应用** ✓

**本 run 实测（双方独立复算一致）**
```
`build-report.receipts.jsonl` → 行数 **54** ｜ 不同 `reproducibleBodySha256` = **5**
  ⇒ **49 行记录的是"身份未变"的例行记录** ✓
处置后自证：跨秒连跑三次 **54 → 54 → 54**、全部 `skipped` ⇒ **膨胀已止** ✓
```
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
