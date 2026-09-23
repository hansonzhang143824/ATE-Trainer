# -*- coding: utf-8 -*-
"""复核 rule-reviewer 的 ②：anchors 的 size 差异是否**纯粹来自序列化/换行**（而非内容或重写）。

并据此决定：是否把生成器的输出换行统一（避免 size 口径混乱）。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, 't28-anchors.json')

d = open(LIVE, 'rb').read()
crlf = d.count(b'\r\n')
lone = d.count(b'\n') - crlf
print('=== 现盘 anchors 特征 ===')
print('  路径 =', os.path.relpath(LIVE, os.path.dirname(os.path.dirname(HERE))).replace('\\', '/'))
print('  size = %d B' % len(d))
print('  BOM =', d[:3] == b'\xef\xbb\xbf')
print('  CRLF = %d ; 孤立 LF = %d' % (crlf, lone))
A = json.loads(d.decode('utf-8-sig'))
print('  条目数 =', len(A['anchors']))

print('\n=== 同一逻辑内容的两种序列化 size ===')
text = d.decode('utf-8-sig')
lf = text.replace('\r\n', '\n')
print('  LF  版 = %d B' % len(lf.encode('utf-8')))
print('  CRLF版 = %d B' % len(lf.replace('\n', '\r\n').encode('utf-8')))
print('  差   = %d B（纯换行差异）' % (len(lf.replace('\n', '\r\n').encode('utf-8')) - len(lf.encode('utf-8'))))
print('  现盘实际 = %d B ⇒ 换行口径 = %s' % (len(d), 'CRLF' if crlf and not lone else ('LF' if lone and not crlf else '混合')))

print('\n=== 我此前提过的几个 size 与本文件的对应 ===')
for s in (11854, 11609, 13276, 14567, 13388, 12294, 11931, 11142):
    print('  报过的 size %-6d → %s' % (s, '与 LF 版吻合' if s == 11854 and False else
                                        ('与现盘吻合' if s == len(d) else '需按换行/版本另行解释')))
print('\n  ⇒ 采纳其结论：**size 不能作身份**；引用一律「全路径 + sha256 + 条目数」。')
print('  ⇒ 我方补充：本生成器当前输出换行已可判定（见上），若其测得 CRLF 而本脚本写 LF，')
print('     则两处副本可能各自被不同工具重排过 ⇒ 引用时**必须带全路径 + 现算哈希**。')

print('\n=== 另存"现盘 payload 版"期望日志的对象信息（供后续生成）===')
RUN = os.path.dirname(HERE)
PAY = os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp')
pd = open(PAY, 'rb').read()
print('  payload 全路径 = team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp')
print('  payload size = %d B ; sha256 = %s' % (len(pd), hashlib.sha256(pd).hexdigest()))
