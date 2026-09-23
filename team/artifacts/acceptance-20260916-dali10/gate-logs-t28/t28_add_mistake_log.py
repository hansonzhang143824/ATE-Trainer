# -*- coding: utf-8 -*-
"""按 rule-reviewer 建议，把"该哈希的修正方向曾出错并被照录"记入 t28-summary.md §8（幂等）。

所有哈希**由本脚本从产物现算后写入**，不使用任何手写字面量。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
SUM = os.path.join(HERE, 't28-summary.md')
MARK = '第 5 项（哈希修正方向）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


red = os.path.join(RUN, 'gate-logs-t28', 't28-red-proof.json')
cis = os.path.join(WS, 'scripts', 'check_input_sync.py')
h_red = sha(red)
h_cis = sha(cis)
h_neg = sha(os.path.join(HERE, 'redproof-before-fix.log'))

BLOCK = """

---

### 8.1 失误登记补记（rule-reviewer 建议，2026-09-16）：哈希"修正方向"曾出错

| # | 失误 | 真相（现算） | 归口 |
| --- | --- | --- | --- |
| %s | **我"自纠"时把 `t28-red-proof.json` 的哈希第 42 位从 `c` 改成 `b`，方向搞反** —— 我**最初**给出的值（pos42=`c`）**才是对的** | 现算 = `%s`（len=64, pos42=`c`）；把 pos42 置 `c` 者与现算**差异位为空**、置 `b` 者差异位 = `[42]` | **我方**（消息文本）；复核方据我的错值照录其表，属连带 |
| — | `scripts/check_input_sync.py` 的哈希，我在消息里写成 **65 位**（在 `…3111` 后多打一个 `1`） | 现算 = `%s`（len=64）；我消息里那串 len=**65** ⇒ 长度异常 | **我方**（消息文本） |

**教训（本 run 通用口径，已被双方采纳）**
1. **不手抄长哈希**：需要引用时只给「路径 + size + 现算命令」，值一律由工具取得；
2. **单一真源必须由工具生成** —— 本文所引的 `gate-logs-t28/t28-anchors.json` 即由脚本生成，
   **本文件 §8 末尾那批锚点值与其一致且正确**（错的只有我的消息文本）；
3. **"自纠"亦须现算** —— 若凭记忆改动某一位，会把原本正确的值改错（本次即如此）；
4. **不能因自己探针报 `False` 就改认他方值**（rule-reviewer 自加的对应纪律）；
   正确做法是"从文件现算 + 逐字符 diff"。
"""

t = io.open(SUM, encoding='utf-8-sig').read()
if MARK in t:
    print('已登记过（幂等）: %d B' % os.path.getsize(SUM))
    raise SystemExit(0)
t = t.rstrip() + (BLOCK % (MARK, h_red, h_cis))
io.open(SUM, 'w', encoding='utf-8', newline='').write(t)
print('已登记: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
s = io.open(SUM, encoding='utf-8-sig').read()
print('  含 8.1 补记 =', '### 8.1 失误登记补记' in s)
print('  含"方向搞反" =', '方向搞反' in s)
print('  含正确 hash(现算) =', h_red in s)
