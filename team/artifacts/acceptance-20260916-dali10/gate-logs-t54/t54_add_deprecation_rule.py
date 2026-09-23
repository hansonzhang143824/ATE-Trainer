# -*- coding: utf-8 -*-
"""并入 rule-reviewer ② 的独立机制洞见（幂等）：
**弃用字段须双向处置** —— ① 输出侧不再产生它；② **累积侧显式抑制**它被"并集/历史累积"重新注入。
否则"弃用"只是表面：历史层的旧值会把它复活。
判据：**"我在当前写码里删掉了" ≠ "它已从产物里消失"**。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附十三｜弃用字段须双向处置（输出侧不再产生 + 累积侧显式抑制）'


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

**来源**：rule-reviewer 将我方的"额外发现"（**改名后旧键仍被并集累积从历史层带回**）建议立为独立机制洞见。
**我方事实**
```
`t28-anchors.json` 的 `mirrorSize` 改名为 `mirrorSizeAtMirrorTime` 后
  ⇒ 旧键 **仍出现在输出里**（被并集累积从历史层带回）⇒ 等于**留着一个记死的旧尺寸**
  ⇒ 处方：生成器加 `pop('mirrorSize', None)` ⇒ **旧键在输出中消失**（连跑两次自证）✓
```

**规则**
> **"弃用一个字段"必须同时做两件事**：
> **① 当前输出不再产生它**；**② 显式抑制它被"并集 / 历史累积"重新注入**。
> ⇒ **否则"弃用"只是表面：历史层的旧值会把它复活。**

**判据**
> **"我在当前写码里删掉了" ≠ "它已从产物里消失"。**
> （与本 run `RECEIPT_WRITER_V1` 那次同族：**都属"只看当前的写码、没看产物的实际状态"**。）

**归族（三条同源）**
1. **`preservedPeerNamespaces` 的并集累积**（为**保留他方内容**而设计）**同时会把已弃用的键带回**
   ⇒ **"保留"与"弃用"在同一机制里冲突**；
2. **R1 的"更正不删原文"**（历史须留痕）与"弃用字段"之间的张力
   ⇒ **正解：历史留在历史层（账本 / legacyEntries），当前输出必须干净**；
3. 本条：**弃用的处置面在"输出"与"累积"两侧**，只做一侧即失效。

**附带（其观察，我方确认）**：`mirrorSizeAtMirrorTime = 175,358` 仍小于镜像现盘（200,758 B），
**但已不再构成缺陷** —— 字段名已声明"镜像时刻"、且配 `mirrorAt` 与失效声明
⇒ **它现在回答的是"那次是多大"，不是"现在多大"** ⇒ **"改名 + 声明"能止住漂移** ✓
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '双向处置', '历史层的旧值会把它复活', '当前输出必须干净'):
    print('  含 %-22s %s' % (k, k in t2))
import collections
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
