# -*- coding: utf-8 -*-
"""并入 rule-reviewer ① 的自我更正 → §附五 补：**"同一性"本身需要证据**（幂等）。

其类型学：把"两次观测不同"（可确证）当成了"同一文件的连续状态"（未证）
⇒ **"我先后看过"不等于"它是同一个在演化的对象"**，同一性须有字节副本或可复核记录。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '**"同一性"本身需要证据**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

OLD = ('**配套动作**：**写结论前先问"我这条记录声称到哪一级？"**；'
       '若声称粒度 < 断言粒度 ⇒ **要么补证据、要么降断言**。')
NEW = OLD + '''

### 附五·补 — ''' + MARK + '''（rule-reviewer 自证的第二处）

**其自我更正**：把"**两次观测不同**"（可确证）当成了"**同一文件的连续状态**"（未证）：
```
可确证：两次读数 entries 均为 32；现盘 CRLF=247 / lone LF=0
属推断：断言"11,854 B（CRLF 245）是**同一文件**的更早瞬间" —— 无字节副本、账本最早记录即 11,931
⇒ 正确表述：**我先后观测到 11,854 与 11,931 两个状态、中间发生过变化**；
  **但"它是同一个在演化的对象"属推断** ⇒ 记 **UNVERIFIED**（我方即为该标注的提出方）。
```
**规则**
> **"同一性"本身需要证据**（字节副本或可复核记录）；**"我先后看过" ≠ "它是同一个在演化的对象"**。
⇒ 与附五主条同源：**"同一性"是一条比"粒度"更基础的声称** ——
要断言"对象 A 变成了状态 B"，须先有证据说"两次观测的是**同一个 A**"。
**配套**：**凡做时序比较，先声明"我凭什么认这两个读数是同一对象"**；无证据 ⇒ 记 **UNVERIFIED**、并保留该标注。
'''
if OLD not in t:
    print('ERROR: 锚点未命中')
    raise SystemExit(1)
t = t.replace(OLD, NEW, 1)
io.open(REG, 'w', encoding='utf-8', newline='').write(t)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '同一性', 'UNVERIFIED', '我先后看过'):
    print('  含 %-16s %s' % (k, k in t2))
