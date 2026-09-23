# -*- coding: utf-8 -*-
"""并入 rule-reviewer ②（幂等）：
**"字段住在哪个产物"与"字段度量什么"是两个声明；引用一个取值时必须同时给出这两个。**
并收录其自纠：把"域 A：报告里有没有 `receipts` 键"与"域 B：`reproducibleBodySha256` 的取值变没变"
混成一个域 ⇒ 用"域 A 的 no-op"去反驳"域 B 的取值变了"。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附卅五｜"字段住在哪个产物"与"字段度量什么"是两个声明'


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

**来源**：rule-reviewer 复核我方机制澄清后**撤回其第二层主张**（自纠），并把根源归到"两个域被混成一个"。

**规则**
> **"字段住在哪个产物"与"字段度量什么"是两个声明；引用一个取值时必须同时给出这两个。**

**本 run 实例（其自纠）**
```
域 A：**"报告里有没有 `receipts` 键"**（穷举键路径 ⇒ []）⇒ **排除项 no-op** ✓
域 B：**"`reproducibleBodySha256` 这个字段的取值变没变"**（它**住在收据里**、**度量报告字节**）⇒ **变了** ✓
⇒ 其错误：**用"域 A 的 no-op"去反驳"域 B 的取值变了"** ——
   **把谓词用到了它不成立的域上**（与其"body 谓词跨版"同型）✓
⇒ 修正后的准确说法：**"v2 的口径差来自序列化，与排除项无关"** ✓
```

**为何这条要紧（双方同型）**：我方亦曾被同一形态绊过两处 ——
`reproducibleBodySha256`（**住收据、度量报告**）｜ `.jsonl` 的 `sha256`（**历史文件的字段、不是报告 body 的输入**）✓
⇒ **"定义域（住在哪 / 度量什么）"应作为"框架要素"再添一项** ✓

**同源（本 run）**：**"0 命中必须带域"**（§纪律）｜**"声明的覆盖面须与使用面一致"**（§附十四）｜
**"计数须带域/单位/谓词"**（§附廿四）—— **本条是它们在"字段"上的形态。**
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
