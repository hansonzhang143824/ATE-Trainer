# -*- coding: utf-8 -*-
"""回应 schematic-expert ④⑤：核对三值 + **判定"每次运行追加两行"的真实成因**（以行为为准）。

关键假设（其候选解释）：**写入一遍 + 校验/复跑再追加一遍** ⇒ 每次 `import`/重复调用追加两行。
检测法：单次运行一次、数新增行数；并检查 `_line` 里是否含**可变的时间戳**（这会让 history 行不稳定）。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
H = os.path.join(HERE, 'build-report.receipts.jsonl')
REPORT = os.path.abspath(os.path.join(HERE, '..', 'build-report.json'))
REC = os.path.join(HERE, 'build-report.receipt.json')


def rows():
    return [json.loads(l) for l in io.open(H, encoding='utf-8').read().splitlines() if l.strip()]


print('=== ① 现刻三值（核对其 ④）===')
print('  build-report.json = %d B' % os.path.getsize(REPORT))
print('  收据 = %d B' % os.path.getsize(REC))
print('  账本 = %d 行 / %d B' % (len(rows()), os.path.getsize(H)))
r = json.load(io.open(REC, encoding='utf-8-sig'))
print('  收据 self-report: size=%s topLevelEntries=%s' % (r['size'], r['topLevelEntries']))
print('  收据与现盘一致 =', r['size'] == os.path.getsize(REPORT)
      and r['sha256'] == hashlib.sha256(open(REPORT, 'rb').read()).hexdigest())

print('\n=== ② 行为判定：跑一次，数新增行数 ===')
n0 = len(rows())
subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
n1 = len(rows())
print('  单次运行新增行数 = %d' % (n1 - n0))
print('  ⇒ 若为 1 ⇒ **不是**"每次追加两行"（"成对"另有他因，如我此前确曾成对调用）')

print('\n=== ③ 检查 history 行是否含**可变**字段（这会让它不稳定）===')
k = list(rows()[-1].keys())
print('  行键 =', k)
print('  含动态字段 receipts / generatedAt 之类 =',
      [x for x in k if x in ('receipts', 'generatedAt', 'countUnitNote', 'standardTriHash')])

print('\n=== ④ 跨秒跑两次：history 行的**内容**（除 at/lineCount/链）是否稳定 ===')


def norm(d):
    d = dict(d)
    for x in ('at', 'lineCount', 'prevLineSha256', 'ledger_self_sha256'):
        d.pop(x, None)
    return json.dumps(d, ensure_ascii=False, sort_keys=True)


import time
time.sleep(1.2)
subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
a = rows()[-1]
time.sleep(1.2)
subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
b = rows()[-1]
print('  两次 history 行（去 at/链字段后）相同 =', norm(a) == norm(b))
if norm(a) != norm(b):
    da, db = json.loads(norm(a)), json.loads(norm(b))
    diff = [k2 for k2 in set(da) | set(db) if da.get(k2) != db.get(k2)]
    print('  **不稳定字段 = %s**' % diff)
    for k2 in diff:
        print('    %s: %s  →  %s' % (k2, str(da.get(k2))[:60], str(db.get(k2))[:60]))

print('\n=== ⑤ projectionSpec 是否覆盖这些可变字段 ===')
print('  projectionSpec.exclude =', (r.get('projectionSpec') or {}).get('exclude'))
print('  version =', (r.get('projectionSpec') or {}).get('version'))
