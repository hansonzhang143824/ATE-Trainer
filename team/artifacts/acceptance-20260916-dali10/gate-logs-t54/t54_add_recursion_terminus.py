# -*- coding: utf-8 -*-
"""并入 rule-reviewer ③（幂等）：
**"框架本身须带版本；版本号即递归的终止条件"** —— 把"未声明框架"一族推到**自指层**后的上界。
  普通情形：值缺框架 ⇒ 读者不知按哪个口径读
  自指情形：**框架自身也在变** ⇒ 读者不知按哪个**版本的框架**读 ⇒ **若不加版本，框架就是下一个"未声明框架"（无限后退）**
  ⇒ 以一个**带版本号且版本号被外部引用**的层终止 ✓
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附廿七｜框架本身须带版本；版本号即递归的终止条件'


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

**来源**：rule-reviewer 点明我方解决的那个递归问题（`schematic-expert` 指出"定义档自身也会漂"），并给出该族的**上界**。

**为什么这条重要：它把"未声明框架"这一族推到**自指层****
```
普通情形：**值缺框架** ⇒ 读者不知道该按哪个口径读 ✓
自指情形：**框架自身也在变** ⇒ 读者不知道该按哪个**版本的框架**读
        ⇒ **若不加版本，框架就成了下一个"未声明框架"**（**无限后退**）✓
```
**规则**
> **框架本身须带版本；版本号即递归的终止条件。**
> ⇒ **该族的上界被钉死：到一个"带版本号、且版本号被外部引用"的层，就不必再往上。** ✓

**本 run 落地**：`build-report.receipts.meta.json` 的 **`metaVersion`（=1）** ＋ **`metaIdentity`**（`metaAt` / `metaSha256_atWrite` / `metaSize_atWrite`）。
**关键复核（rule-reviewer 实测）**：**`metaSha256_atWrite` ≠ 本档现 sha**（`metaSize_atWrite = 1,519` vs 现 1,645）
⇒ **这正是"指向写入时刻"的正确形态**：**若把本档自身现哈希写进本档，就永远无法满足（写前不知、写后即变）** ✓

**与"投影须带版本"的关系**：**同源** —— 但**作用对象不同**：
- **投影须带版本**：作用对象是**单次取值**（哈希口径）✓
- **本条**：作用对象是**规则/定义本身** ✓

**一句话形态（rule-reviewer 采纳）**：**"定义按版本引用；递归以被钉定的版本号终止"** ✓
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
