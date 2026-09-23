# -*- coding: utf-8 -*-
"""清理 t33-transition-plan.md 中重复插入的"闭集更正 + 三情形"段（幂等），并修正 t30-summary 的一处残句。"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TP = os.path.join(HERE, '..', 'gate-logs-t33', 't33-transition-plan.md')
T30 = os.path.join(HERE, 't30-summary.md')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== 诊断 transition-plan ===')
t = io.open(TP, encoding='utf-8-sig').read()
n_block = t.count('闭集更正（Captain 2026-09-16）')
n_case = t.count('三情形')
print('  %d B ; "闭集更正" 出现 %d 次 ; "三情形" 出现 %d 次' % (len(t.encode()), n_block, n_case))
for i, l in enumerate(t.splitlines(), 1):
    if '闭集更正' in l or '三情形' in l or '据此更新的落盘后期望' in l:
        print('  %3d| %s' % (i, l[:130]))

print('\n=== 清理重复块（保留第一份）===')
BLOCK_RE = re.compile(
    r'\*\*闭集更正（Captain 2026-09-16）\*\*：BST–SW 闭集 = \*\*`\[48,60,61,76\]`\*\*.*?本分支\)。\n\n',
    re.S)
matches = BLOCK_RE.findall(t)
print('  匹配到 %d 块' % len(matches))
if len(matches) > 1:
    first = matches[0]
    t2 = t.replace(BLOCK_RE, '', 1)          # 先全删
    t2 = t.replace('**据此更新的落盘后期望**', first + '**据此更新的落盘后期望**', 1)  # 再插回一份
    io.open(TP, 'w', encoding='utf-8', newline='').write(t2)
    print('  已清理: %d B / %s' % (os.path.getsize(TP), sha(TP)[:16]))
    t3 = io.open(TP, encoding='utf-8-sig').read()
    print('  现 "闭集更正" 出现 %d 次' % t3.count('闭集更正（Captain 2026-09-16）'))
else:
    print('  无需清理')

print('\n=== 修正 t30-summary 残句 ===')
s = io.open(T30, encoding='utf-8-sig').read()
bad = '闭集更正（Captain 2026-09-16）**：BST–SW 闭集应为 **`[48,60,61,76]`**（不是我先前给的 `[48,60,61,76]`）——'
good = ('**闭集更正（Captain 2026-09-16）**：BST–SW 闭集应为 **`[48,60,61,76]`**'
        '（我先前给的是 `[48,61,76]`，已更正）——')
if good in s:
    print('  已修正（幂等）')
elif bad in s:
    s = s.replace(bad, good, 1)
    io.open(T30, 'w', encoding='utf-8', newline='').write(s)
    print('  已修正: %d B / %s' % (os.path.getsize(T30), sha(T30)[:16]))
else:
    print('  ERROR: 未找到待修残句')
