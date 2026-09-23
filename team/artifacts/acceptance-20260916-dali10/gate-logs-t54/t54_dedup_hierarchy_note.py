# -*- coding: utf-8 -*-
"""去重：我插入层级说明时用的哨兵与实际文本不符（markdown 里是 ``**`读序提示（层级）`**``），
导致误判"未并入"并重复插入。本脚本：**保留第一份、删除重复份**（幂等）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
HEAD = '### 附五·层级说明（rule-reviewer 指出，供排序）— 读序：**附五·补 → 附五 → 时序/状态断言**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('修复前: %d B ; 该节出现 %d 次' % (os.path.getsize(REG), t.count(HEAD)))

if t.count(HEAD) <= 1:
    print('无需去重（幂等）')
    raise SystemExit(0)

# 定位两处，删除第二处（连同其后的代码块，直到下一个 '---' 或文件末尾）
parts = []
idx = t.find(HEAD)
while idx != -1:
    parts.append(idx)
    idx = t.find(HEAD, idx + 1)
print('  出现位置 =', parts)

# 第二份开始处：从第二个 HEAD 起，删到下一个顶层分隔（'\n---\n'）或文末
start = parts[1]
# 向前回退到其前的 '\n---\n'（保持分隔整洁）
back = t.rfind('\n---\n', 0, start)
cut_from = back if back != -1 else start
# 向后找下一个 '\n---\n'（作为其结束）；若无则到文末
nxt = t.find('\n---\n', start)
cut_to = nxt if nxt != -1 else len(t)
t2 = t[:cut_from] + t[cut_to:]
io.open(REG, 'w', encoding='utf-8', newline='').write(t2)
t3 = io.open(REG, encoding='utf-8-sig').read()
print('修复后: %d B ; 该节出现 %d 次 / %s' % (os.path.getsize(REG), t3.count(HEAD), sha(REG)))
print('  关键句仍在 =', all(k in t3 for k in ('同一性是粒度比较的前提', '先认同一对象', '附五·补 → 附五 → 时序/状态断言')))
