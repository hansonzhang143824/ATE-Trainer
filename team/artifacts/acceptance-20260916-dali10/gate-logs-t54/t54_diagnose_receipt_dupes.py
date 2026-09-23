# -*- coding: utf-8 -*-
"""按 schematic-expert ③ 复核 `receipts.jsonl` 的"4 行 = 2 个状态"：
判定属 (a) 同秒两次（合法）还是 (b) 生成器每次多写一行（缺陷）。**以行为为准。**
并给链加"计数单位"字段（声明的计数单位＝状态数，不是行数）。
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
H = os.path.join(HERE, 'build-report.receipts.jsonl')


def rows():
    return [json.loads(l) for l in io.open(H, encoding='utf-8').read().strip().splitlines() if l.strip()]


print('=== ① 现有 4 行的四元组 ===')
for i, r in enumerate(rows(), 1):
    print('  行%d at=%s size=%s file=%s body=%s'
          % (i, r['at'], r['size'], r['sha256'][:12], r['reproducibleBodySha256'][:12]))
try:
    import collections
    key = lambda r: (r['size'], r['sha256'], r['reproducibleBodySha256'], r['at'])
    c = collections.Counter(key(r) for r in rows())
    print('  不同状态数 =', len(c), '｜ 行数 =', len(rows()))
    dup = [k for k, v in c.items() if v > 1]
    print('  重复组 =', len(dup), '（每组次数 =', [c[k] for k in dup], '）')
except Exception as e:
    print('  统计失败:', e)

print('\n=== ② 判定 (a) 同秒两次 还是 (b) 每次多写一行 ===')
n0 = len(rows())
# 跨秒跑一次：若新增 **1 行** ⇒ 每次运行只写一行 ⇒ (a)；若新增 2 行 ⇒ (b)
time.sleep(1.2)
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
n1 = len(rows())
print('  跑一次前 %d 行 → 跑一次后 %d 行 ⇒ 本次新增 **%d 行**' % (n0, n1, n1 - n0))
verdict = '(a) 每次运行只写 1 行 ⇒ 原 4 行 = 同秒内真跑了两次（合法）' if (n1 - n0) == 1 \
    else '(b) 每次运行写 %d 行 ⇒ 生成器有重复写入缺陷' % (n1 - n0)
print('  ⇒ 判定 =', verdict)
print('  末行 =', {k: (str(v)[:22] if k in ('sha256', 'reproducibleBodySha256') else v)
                    for k, v in rows()[-1].items() if k in ('at', 'size', 'sha256', 'reproducibleBodySha256')})

print('\n=== ③ 给链加"计数单位"声明 ===')
src = io.open(GEN, encoding='utf-8-sig').read()
if 'countUnitNote' in src:
    print('  已含（幂等）')
else:
    OLD = "_line['lineCount'] = len(_prev_lines) + 1"
    NEW = ("_line['lineCount'] = len(_prev_lines) + 1   # **行的条数**（不是状态数）\n"
           "_line['countUnitNote'] = ('计数单位：`lineCount` 是**行的条数**；'\n"
           "                          '**状态数须按 (size, sha256, bodySha, at) 去重后计**。'\n"
           "                          '同秒内两次运行 ⇒ 同 `at`（只到秒）⇒ **同 at 不构成同一性**（见纪律』同一性需证据』）。')")
    if OLD in src:
        out = src.replace(OLD, NEW, 1)
        import ast
        ast.parse(out)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
        print('  已加入 countUnitNote → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 锚点未命中')

print('\n=== ④ 记录"投影"实例证据（schematic-expert 提议）===')
rec = rows()
pairs = [(r['at'], r['sha256'][:12], r['reproducibleBodySha256'][:12]) for r in rec]
print('  （at, 整文件sha12, bodySha12）最近 4 条：')
for p in pairs[-4:]:
    print('    ', p)
bodies = {r['reproducibleBodySha256'] for r in rec}
files = {r['sha256'] for r in rec}
print('  不同 body 哈希 = %d ｜ 不同整文件 sha = %d ⇒ %s'
      % (len(bodies), len(files),
         '**内容未变、仅被投影排除的部分变** ⇒ 投影价值实证' if len(bodies) == 1 and len(files) > 1 else '（需人工判读）'))
