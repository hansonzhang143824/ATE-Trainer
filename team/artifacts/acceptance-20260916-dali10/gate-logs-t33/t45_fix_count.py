# -*- coding: utf-8 -*-
"""更正 t33-revision-attribution.md §2.1 的引用计数（10/10，非 11/10），并加一条计数差异说明。

我实测：TM600 段 `SW12_U1REF_BST_ACM` 出现 **10** 次，且**全部**为 `.Set(` 调用
（10 处 `.Set`，其中 9 处 `ACM200_RELAY_ON`、1 处 `ACM200_RELAY_OFF`）。
Captain 通报为"引用 11 / .Set 10" ⇒ 引用计数差 1（我未能在该段内找到第 11 处引用）。
**实质结论不变**：该段**正在驱动 ch5 源而 `K48` 未闭** ⇒ 活危害。
"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ATTR = os.path.join(HERE, 't33-revision-attribution.md')
MARK = '计数差异说明（我方实测 vs Captain 通报）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(ATTR, encoding='utf-8-sig').read()
if MARK in t:
    print('已更正过（幂等）: %d B / %s' % (os.path.getsize(ATTR), sha(ATTR)))
    raise SystemExit(0)

old_row = '| TM600 段 `SW12_U1REF_BST_ACM` 引用 | 11 |'
new_row = ('| TM600 段 `SW12_U1REF_BST_ACM` 引用 | **10**（我方现算；Captain 通报 11，差 1，见下） |\n'
           '| 其中 `.Set(FV,…)` 调用 | **10**（即该段内**每一处引用**都是 `.Set` 调用：'
           '9 处 `ACM200_RELAY_ON` + 1 处 `ACM200_RELAY_OFF`） |')
if old_row not in t:
    print('ERROR: 未找到待更正的引用计数行')
    raise SystemExit(1)
t = t.replace(old_row, new_row, 1)

anchor = '⇒ **本行归属仍为 `compiledRevision = 15c7d2b8…`**'
note = ('**' + MARK + '**：Captain 通报"引用 11 / `.Set` 10"，我方现算为"引用 **10** / `.Set` **10**" ——\n'
        '第 11 处引用我在 `TM600_HS_RDSON` 块内**未找到**（块内每一处 `SW12_U1REF_BST_ACM` 都是 `.Set(...)` 形式；\n'
        '全文另有 37 处属其它函数）。**计数差 1 不改变实质结论**：该段**正在驱动 ch5 源而 `K48` 未闭** ⇒ 活危害。\n\n')
t = t.replace(anchor, note + anchor, 1)
io.open(ATTR, 'w', encoding='utf-8', newline='').write(t)
print('已更正: %d B / %s' % (os.path.getsize(ATTR), sha(ATTR)))
t2 = io.open(ATTR, encoding='utf-8-sig').read()
for k in ('**10**（我方现算', '计数差异说明', '活危害'):
    print('  含 %-16s %s' % (k, k in t2))
