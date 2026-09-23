# -*- coding: utf-8 -*-
"""对 rule-reviewer ② 的**直答**：择一（(a)/(b)/(c)）＋数据。

我的实验结论：**(a) 成立**（排除项对当前正文是 no-op），**但"v2 无实质变化"不成立** ——
因为 v2 同时把**序列化**从"去行字节"改成"json.dumps sort_keys 重序列化"，**这才是哈希改变的主因**；
且我原先"v1 不稳"的理由**被实测否证**（v1 跨次恒定）⇒ 已撤回。
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
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.join(RUN, 'build-report.json')
REC = os.path.join(HERE, 'build-report.receipt.json')

b = open(REPORT, 'rb').read()
J = json.loads(b.decode('utf-8-sig'))


def walk(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield p + '/' + str(k)
            yield from walk(v, p + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, p + '[%d]' % i)


paths = list(walk(J))
raw = b.decode('utf-8-sig')
print('=== 直答的数据 ===')
print('  键路径总数 = %d（其测 307、我测 %d ⇒ 报告已增长）' % (len(paths), len(paths)))
print('  含 "receipt" 的路径 = %s' % [p for p in paths if 'receipt' in p.lower()])
print('  字面 "receipts" = %d 次 ｜ 字面 "generatedAt" = %d 次'
      % (raw.count('"receipts"'), raw.count('"generatedAt"')))


def v1_asis(bb):      # v1 的真算法：删 generatedAt 行（行字节级）
    return hashlib.sha256(re.sub(r'^\s*"generatedAt": ".*?",\s*$', '',
                                 bb.decode('utf-8-sig'), flags=re.M).strip().encode('utf-8')).hexdigest()


def ser(j):
    return hashlib.sha256(json.dumps(j, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


exg = {k: v for k, v in J.items() if k != 'generatedAt'}
exgr = {k: v for k, v in J.items() if k not in ('generatedAt', 'receipts')}
print('  v1 真算法（去行字节）            = %s' % v1_asis(b)[:24])
print('  去 gen（sort_keys 重序列化）      = %s' % ser(exg)[:24])
print('  去 gen+receipts（重序列化）       = %s' % ser(exgr)[:24])
print('  ⇒ 去 gen vs 去 gen+receipts 相同 = %s ⇒ **排除 receipts 是 no-op（(a) 成立）**'
      % (ser(exg) == ser(exgr)))
print('  ⇒ v1真算法 vs 去gen重序列化 相同  = %s ⇒ **改变主因 = 序列化口径**'
      % (v1_asis(b) == ser(exg)))

print('\n=== 我原先"v1 不稳"的理由是否成立 ===')
sig = []
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    bb = open(REPORT, 'rb').read()
    sig.append(v1_asis(bb)[:16])
    time.sleep(1.3)
print('  跨秒两次 v1 值 = %s / %s ⇒ **恒定 = %s**' % (sig[0], sig[1], sig[0] == sig[1]))
print('  ⇒ 我原先"v1 下内容未变不成立"**不成立** ⇒ 已撤回（记 §附十八）')

print('\n=== note 现状（已含诚实化说明）===')
rc = json.load(io.open(REC, encoding='utf-8-sig'))
print('  ', rc['projectionSpec']['note'])
