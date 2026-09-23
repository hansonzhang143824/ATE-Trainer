# -*- coding: utf-8 -*-
"""复核 rule-reviewer ①：**`receipts` 是否真在报告正文里？v2 是否为 no-op？我原来的因果是否成立？**

判定法（行为级）：
  ① 穷举报告的键路径，找含 "receipt" 的路径；
  ② 在**同一文件**上分别按 v1（仅排 generatedAt）与 v2（排 generatedAt+receipts）算 body 哈希 ⇒ 若相同 ⇒ v2 对当前正文为 no-op；
  ③ 跨秒跑两次，分别算 v1 与 v2 的 body ⇒ 看**哪个**才稳定（这才是我原来声称的因果）。
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.abspath(os.path.join(HERE, '..', 'build-report.json'))
REC = os.path.join(HERE, 'build-report.receipt.json')

print('=== ① 穷举键路径：报告里有没有 receipts ===')
A = json.load(io.open(REPORT, encoding='utf-8-sig'))


def walk(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield p + '/' + str(k)
            yield from walk(v, p + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, p + '[%d]' % i)


paths = list(walk(A))
hits = [p for p in paths if 'receipt' in p.lower()]
print('  顶层键数 = %d ｜ 键路径总数 = %d' % (len(A), len(paths)))
print('  含 "receipt" 的路径 = %d 个：%s' % (len(hits), hits[:5]))
raw = open(REPORT, 'rb').read().decode('utf-8-sig')
print('  字面出现 "receipts" 次数 =', raw.count('"receipts"'))
print('  字面出现 "generatedAt" 次数 =', raw.count('"generatedAt"'))


def body_v1(b):
    t = re.sub(r'^\s*"generatedAt": ".*?",\s*$', '', b.decode('utf-8-sig'), flags=re.M).strip()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def body_v2(b):
    J = json.loads(b.decode('utf-8-sig'))
    d = {k: v for k, v in J.items() if k not in ('generatedAt', 'receipts')}
    return hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


print('\n=== ② 同一文件上 v1 vs v2 ===')
b = open(REPORT, 'rb').read()
print('  v1 =', body_v1(b)[:24])
print('  v2 =', body_v2(b)[:24])
print('  **相同 = %s** ⇒ %s' % (body_v1(b) == body_v2(b),
      'v2 对当前正文是 **no-op** ⇒ 我的原始因果不成立' if body_v1(b) == body_v2(b)
      else 'v2 确实改变了口径'))

print('\n=== ③ 跨秒跑两次：哪个投影才稳定（我原来的声称）===')
sig = []
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    bb = open(REPORT, 'rb').read()
    r = json.load(io.open(REC, encoding='utf-8-sig'))
    sig.append((body_v1(bb)[:16], body_v2(bb)[:16], r['reproducibleBodySha256'][:16], r['sha256'][:16]))
    time.sleep(1.3)
print('  run1: v1=%s  v2=%s  收据body=%s  file=%s' % sig[0])
print('  run2: v1=%s  v2=%s  收据body=%s  file=%s' % sig[1])
print('  **v1 跨次稳定 = %s**' % (sig[0][0] == sig[1][0]))
print('  **v2 跨次稳定 = %s**' % (sig[0][1] == sig[1][1]))
print('  收据 body 与 v2 一致 = %s' % (sig[0][2] == sig[0][1]))
print('\n  ⇒ 结论：%s' % ('**v1 本来就稳定** ⇒ 升 v2 的真实理由是"**预防性**"（防将来嵌入 receipts），'
                          '**不是**"v1 不稳"；我原先的因果陈述**应撤回**'
                          if sig[0][0] == sig[1][0] else '**v1 确实不稳** ⇒ 我的原始因果成立'))
