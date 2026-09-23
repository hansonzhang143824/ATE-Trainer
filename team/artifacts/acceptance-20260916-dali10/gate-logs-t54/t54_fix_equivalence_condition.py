# -*- coding: utf-8 -*-
"""🔴 我方自纠：前一步我测错了条件，并写了"其实测为空 ⇒ 与其实测一致"——**该一致句不成立**。

正确条件分析：
  `rstrip(b'\r\b')` vs `rstrip(b'\r\n')` 在本文件（**CRLF**）上**等价**，因为**两者都剥掉末尾的 CR**；
  **两式分歧的真正条件**是：某行**去掉行终止符后**的内容**仍以 CR 结尾**（即出现 `…\r\r\n` 这种双 CR）
⇒ 我先前测的"行是否以 CR 结尾"在 CRLF 文件里**恒为真**（54/54）⇒ **测的是无关条件** ✗
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
META = os.path.join(HERE, 'build-report.receipts.meta.json')
H = os.path.join(HERE, 'build-report.receipts.jsonl')

raw = open(H, 'rb').read()
lines = [l for l in raw.split(b'\n') if l.strip()]
print('=== ① 正确条件：去掉行终止符后，内容是否仍以 CR 结尾（即双 CR）===')
double = [i for i, l in enumerate(lines, 1) if l.rstrip(b'\r\n').endswith(b'\r')]
print('  CRLF = %d ｜ 行数 = %d' % (raw.count(b'\r\n'), len(lines)))
print('  **双 CR 行 = %s** ⇒ 该条件集合%s' % (double if double else '[]', '为空 ⇒ 两式等价 ✓' if not double else '非空'))
print()
print('=== ② 直接实测两式结果（决定性）===')
import hashlib
a = all(hashlib.sha256(l.rstrip(b'\r')).hexdigest() == hashlib.sha256(l.rstrip(b'\r\n')).hexdigest() for l in lines)
print('  对全部 %d 行：rstrip(CR) 与 rstrip(CRLF) 结果相同 = %s' % (len(lines), a))
print()
print('=== ③ 我方前一步的错误（如实）===')
print('  我测的是"行是否以 CR 结尾" ⇒ 在 CRLF 文件里**恒真（54/54）** ⇒ **测的是无关条件** ✗')
print('  我却据此写了"与其实测一致（为空）" ⇒ **该一致句不成立** ✗ ⇒ 现纠正为：')
print('    **等价性成立，其真正条件是"双 CR 行 = 空"（实测为空 ⇒ 今日等价 ✓）**')

print('\n=== ④ 纠正 meta 中的表述 ===')
m = json.load(open(META, encoding='utf-8-sig'))
m['fieldDefinitions']['prevLineSha256'] = (
    'sha256( 上一行的字节，去掉其行终止符 )；本文件为 CRLF ⇒ CR 一并去掉。'
    '等价实现（带成立条件）：hashlib.sha256(prev_line_bytes.rstrip(b"\\r\\n"))；'
    '另一式 rstrip(b"\\r") 同解 —— **其成立条件是"去掉行终止符后内容仍以 CR 结尾（即双 CR）的行 = 空"**'
    '（本 run 实测：双 CR 行 = 空 ⇒ 两式今日等价 ✓）；'
    '⚠️ 若出现双 CR 行，则 rstrip(CR) 会多剥一格 ⇒ 两式分歧 ⇒ 『等价』是带域的主张。')
m['equivalenceIsDomainBound'] = (
    '『等价实现』必须连同其成立条件（域）声明；本 run 中该条件为"双 CR 行 = 空"。'
    '⚠️ 自纠留痕：我方曾错误地以"行是否以 CR 结尾"为条件（在 CRLF 文件上恒真 ⇒ 无关条件），已更正。')
open(META, 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=2))
print('  meta 已更正 → %d B' % os.path.getsize(META))
print('  现在的定义 =', m['fieldDefinitions']['prevLineSha256'][:130], '…')
