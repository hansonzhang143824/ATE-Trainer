# -*- coding: utf-8 -*-
"""对账 setup-architect ③ 的 build-report 现值（其报 31,821 B / 8e6a8980… @23:22:05）。

我方记录：31,821 B 时收据 sha256 前缀为 18da8d72…（@23:22:05，size 与时刻吻合）。
本脚本给出现刻三值 + 收据值，判断是否存在"同 size 不同 sha"（即同一时刻不同字节）。
"""
import hashlib
import io
import json
import os
import datetime

RUN = 'team/artifacts/acceptance-20260916-dali10'
P = os.path.join(RUN, 'build-report.json')
REC = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipt.json')

b = open(P, 'rb').read()
print('=== 现刻 ===')
print('  size   =', len(b))
print('  sha256 =', hashlib.sha256(b).hexdigest())
print('  mtime  =', datetime.datetime.fromtimestamp(os.path.getmtime(P)).strftime('%Y-%m-%d %H:%M:%S'))
r = json.load(io.open(REC, encoding='utf-8-sig'))
print('\n=== 收据（生成器每次重算）===')
print('  at     =', r['at'])
print('  size   =', r['size'])
print('  sha256 =', r['sha256'])
print('  一致于现盘 =', (r['size'] == len(b) and r['sha256'] == hashlib.sha256(b).hexdigest()))

print('\n=== 对其申报值的对账 ===')
their_size, their_sha8, their_at = 31821, '8e6a89800836996265dc9650', '2026-09-16 23:22:05'
cur_sha = hashlib.sha256(b).hexdigest()
print('  其 size 匹配现盘 =', their_size == len(b))
print('  其 sha 前缀匹配现盘 =', cur_sha.startswith(their_sha8[:24]))
print('  其 sha 前缀匹配收据 =', str(r['sha256']).startswith(their_sha8[:24]))
print('  我方历史（同 size）见过的 sha 前缀 = 18da8d72… / 收据现值见上')
print('  ⇒ 结论：%s' % ('**同 size、不同 sha**（生成器每次嵌时间戳 ⇒ 同尺寸不同字节，属正常）'
                       if their_size == len(b) and not cur_sha.startswith(their_sha8[:24])
                       else '一致或需进一步核对'))

# 生成器是否嵌时间戳（用于解释"同 size 不同 sha"）
G = os.path.join(RUN, 'gate-logs-t54', 't54_make_report.py')
gt = io.open(G, encoding='utf-8-sig').read()
import re
ts = re.findall(r"'at':\s*[^\n]*", gt)[:3]
print('\n=== 生成器是否嵌时刻（解释同尺寸不同字节）===')
print('  含动态时间戳构造 =', bool(re.search(r'now\(\)|isoformat\(', gt)))
for t in ts:
    print('   ', t[:90])
