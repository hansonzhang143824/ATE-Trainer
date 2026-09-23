# -*- coding: utf-8 -*-
"""并入 rule-reviewer ②（幂等）：
**一个布尔断言若因实现差异而反转（0/53），它就不是"事实断言"，而是"实现断言"。**
并收录其自我披露：其复算"恰好"用了正确变体 ⇒ **算术正确但定义未声明 ⇒ 是"运气正确"而非"结构正确"**。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附卅三｜能因实现差异反转的布尔断言是"实现断言"，不是"事实断言"'


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

**来源**：rule-reviewer 在字节层按三种定义复算同一 CRLF 文件后，**实测确认其此前用的正是我方那条可执行定义**
（故双方"早已同算术"），并**自我披露一处潜在风险**。

**三种定义的实测对照（同一文件、同一数据）**
```
A) 哈希"**不含 CRLF**"的行（＝我方可执行定义 `sha256(prev.rstrip(b'\\r\\n'))`）⇒ **53/53 全有效** ✓
B) 哈希"含 CRLF"的行 ⇒ **0/53**
C) **只去 `\\n` 的 bug 实现** ⇒ **0/53** ← **正是我方那次"53/53 假 mismatch"的形态**
```
**★ 规则（其给出，我方采纳）**
> **一个布尔断言若能因实现差异而反转（0 / 53），它就不是"事实断言"，而是"实现断言"。**
> ⇒ **这是"定义须写成可执行式"这一族最极端的形式：同一个文件、同一份数据、两个相反的结论。**

**其自我披露（如实收录）**
```
其复算"**恰好**"用了正确变体 ⇒ 若当初按二进制整体读、或按 `\\n` 拆行，就会得到 **0/53**（与我方同样的假 mismatch）
⇒ 故其此前"链自洽 = 0 breaks"是**算术正确、但定义未被声明**的结论 ⇒
  ⇒ **它是"运气正确"，不是"结构正确"** ✓
⇒ 而我方把定义写成**可执行式**（`executableDefinitionRule` + `metaVersion`）
  **正是把"依人的做法"换成"依可执行的式子"** ✓
```

**同源（本 run）**：**"定义写在使用处"**（§附十九）｜**"前提式域声明"**（R3）｜**"等价也是带域的主张"**（§附十九·补）——
**本条是它们的最极端形式。**
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
