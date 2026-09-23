# -*- coding: utf-8 -*-
"""并入 rule-reviewer ②③（幂等）：
 ② "5 个身份"的**谓词须声明** ⇒ 收录六谓词表（同一账本 54 行，六个不同的数）。
 ③ **"记录频率"也是记录语义的一部分 —— 改了频率必须声明**（我方的 appendPolicy 即该声明）。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附廿四｜同一账本按不同谓词给出六个数；且"记录频率"是记录语义的一部分'


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

**来源**：rule-reviewer 指出"身份计数"须**声明谓词**（其按**整文件 `sha256`** 得 **39**，我方报 **5** ⇒ 须注明谓词）；
并就我方"止膨胀"处置指出**语义已变**。

**① 六谓词表（同一账本，54 行，六个都正确、且互不冲突）**
| 谓词 | 唯一值个数 |
| --- | --- |
| 行数（`lineCount` 上界） | **54** |
| **内容身份**（`reproducibleBodySha256`） | **5** ← 我方所称"5 个身份" |
| **整文件身份**（`sha256`） | **39** ← rule-reviewer 独立测得，逐位一致 |
| 行尾归一身份（`sha256_lf_normalized`） | **39** |
| 时间点（`at`，秒粒度） | **39** |
| **运行序号**（`runSeq`） | **11**（旧行无该字段 ⇒ **不可追溯**） |

**② 规则：记录频率是记录语义的一部分**
```
我方处置（例行复验不追加 ⇒ 连跑三次 0 增长）**修掉了膨胀**，但**把该账本从
  "每次运行的记录" 变成 "每次内容/口径变更的记录"** ⇒ **两段语义不同**：
  · **旧语义**：每次运行 ⇒ 能答"某时刻跑过没有、当时现盘是什么"（**审计面更宽**）
  · **新语义**：每次内容/口径变更 ⇒ 能答"内容变过几次、每次前后是什么"（**信息密度更高、且不再自放大**）
⇒ **两者都不是缺陷**，但**读者若不知道语义已变，会把"没有行"读成"没跑过"**。
⇒ **判据**：**"记录频率"也是记录语义的一部分 —— 改了频率必须声明。**
   （与"**幂等 ≠ 内容未变**"同源：**过程**与**产物**是两个断言。）
```
**⇒ 我方已声明**：收据 `appendPolicy`（"仅在身份变化时追加；**『一段时间无增长』不等于『无运行』**；运行计数查 `runSeq`"）✓
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
