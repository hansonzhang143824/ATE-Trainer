# -*- coding: utf-8 -*-
"""并入 setup-architect ① 的机制细节（幂等）：
**位置寻址可能"碰巧正确"** —— `bst2sw` 恰好位于 index 3 ⇒ 早期写 `aliasResolution[3]` **是对的**；
  ⇒ **"对错取决于当前顺序"的写法不是判定** —— 这正是该规则要命名的危害。
并收录其审计事实（870 个 .py、三类模式、逐处分类、跨方交叉印证）。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '### 附十六·补｜位置寻址的"碰巧正确"：对错取决于当前顺序 ⇒ 它不是判定'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**来源**：setup-architect 对**自己的全部脚本**（工作区 **870 个 `.py`**，三模式：
`aliasResolution[<数字>]` / `entries[<数字>]` / `(resolutions|anchors|limitations|aliases)[<数字>]`）做同法审计后
点出的一处**机制细节**。

**★ 机制：位置寻址可能"碰巧正确"**
```
`bst2sw` **恰好位于 index 3** ⇒ 其早期脚本写 `aliasResolution[3]` **是对的** ✓
  而其那次误读用 `[1]` ⇒ 得到 `sw2pgnd`（`[154,155,60,61]`）✗
⇒ **"对错取决于当前顺序"的写法不是判定** —— **这正是该规则要命名的危害** ✓
（若按名寻址，则**不存在"碰巧对"的可能**：对就是对、错就是错 ✓）
```

**其审计结果（供双方台账）**
```
契约字段按位置 = **20 处**（**全部在其 `backups/` 补丁脚本**，其中若干只是在**字符串里引用该错例**）
  ＋ **1 处＝我方审计脚本 `gate-logs-t54/t54_add_field_addressing_rule.py` 的正则**（＝我方报告的自引用）✓
账本按位置 = **14 处**（其文档脚本 + `scripts/gen_cbit_defines.py` 的 `entries[0]`，属**另一结构**）
通用列表按位置 = **0 处**
⇒ **没有任何一处落在活跃门禁/核验脚本里** ✓
```

**跨方交叉印证**：双方**各自独立**扫到**同一处**活跃命中（我方审计脚本自身的正则）⇒ 对同一事实取到同一读数 ✓
**双方工具互不相依**：我方 `t54_selfaudit_addressing.py` ↔ 其方 `backups/t248_selfaudit_addressing.py`，各自可独立重跑 ✓
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
