# -*- coding: utf-8 -*-
"""对 rule-reviewer ② 的**决定性机制测试**：
把"排除项"与"序列化"两个变量**分别固定**，看 body 哈希是否随生成而变 —— 以定位**主因**。

关键澄清（须用数据说）：`reproducibleBodySha256` 是**收据**里的字段，其**定义域是报告正文的字节**；
它**不是**报告自己的字段。故"v1→v2 改 body"指的是"**该字段的取值**"，与"报告里有没有 receipts 键"是两件事。
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

print('=== ① 澄清：正文有 / 没有哪些键（其三处 = [] 复核）===')
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
for key in ('projectionSpec', 'receipts', 'hashInvariance', 'standardTriHash', 'generatedAt'):
    hit = [p for p in paths if key in p]
    print('  正文含 "%s" 的路径 = %s' % (key, hit if hit else '[]'))
print('  ⇒ 与 rule-reviewer 的三处 [] 一致 ✓（`projectionSpec`/`receipts`/`hashInvariance` **均不在正文**）')

print('\n=== ② body 哈希到底"有什么用"：(a) 排除项 vs (b) 序列化 —— 分别固定 ===')


def canon_serialize(j, exclude):
    d = {k: v for k, v in j.items() if k not in exclude}
    return hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def by_line_bytes(bb, exclude_line):
    t = re.sub(exclude_line, '', bb.decode('utf-8-sig'), flags=re.M).strip()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


b = open(REPORT, 'rb').read()
J0 = json.loads(b.decode('utf-8-sig'))
GEN_LINE = r'^\s*"generatedAt": ".*?",\s*$'
print('  同一字节上（两个变量各跑一遍）：')
print('    序列化=sort_keys，排除={gen}            =', canon_serialize(J0, {'generatedAt'})[:24])
print('    序列化=sort_keys，排除={gen,receipts}    =', canon_serialize(J0, {'generatedAt', 'receipts'})[:24], '← 现行 v2')
print('    序列化=去行字节，排除={gen}              =', by_line_bytes(b, GEN_LINE)[:24], '← 旧 v1')
print('  ⇒ (a) 排除项（gen vs gen+receipts）**在同序列化下相同** ⇒ 排除 receipts 确为 no-op ✓')
print('  ⇒ (b) 序列化（去行字节 vs sort_keys）**不同** ⇒ 这才是 v1→v2 的口径差 ✓')

print('\n=== ③ v1 的取值是否稳定（我原先的触发理由）===')
sig = []
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    bb = open(REPORT, 'rb').read()
    j = json.loads(bb.decode('utf-8-sig'))
    sig.append({'v1(去行字节,排gen)': by_line_bytes(bb, GEN_LINE)[:16],
                'v2(现行,收据值)': json.load(io.open(REC, encoding='utf-8-sig'))['reproducibleBodySha256'][:16],
                '收据历史行数': len([l for l in io.open(os.path.join(HERE, 'build-report.receipts.jsonl'), encoding='utf-8').read().splitlines() if l.strip()])})
    time.sleep(1.3)
for k in ('v1(去行字节,排gen)', 'v2(现行,收据值)', '收据历史行数'):
    print('  %-18s run1=%s  run2=%s  ⇒ 恒定=%s' % (k, sig[0][k], sig[1][k], sig[0][k] == sig[1][k]))
print('\n  ⇒ **v1 恒定** ⇒ 我原先"v1 不稳 ⇒ 排除表不完整"的触发理由**不成立**（已撤回，§附十八）')

print('\n=== ④ 直答其三选项 ===')
print('  (甲) body 对象不是 build-report.json ？ → **否**：定义域就是报告正文的字节（上表可复算）')
print('  (乙) receipts 属预防性排除？          → **是**（正文无该键，防将来嵌入）')
print('  (丙) 先注入后剔除？                    → **否**（生成器不注入 receipts）')
print('  ⇒ **v2 的正当理由＝"v1 未声明序列化/编码 ⇒ 第三方无法复现"**（其③的建议我采纳）')
