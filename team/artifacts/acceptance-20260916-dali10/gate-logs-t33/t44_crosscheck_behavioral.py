# -*- coding: utf-8 -*-
"""交叉验证 schematic-expert 的 §1 行为证据与 §4 归因区分（应其请求）。

复核项：
  A) §4：payload vs 部署态 的 SetOn 差异（"闭错+漏闭" vs "仅漏闭"）
  B) §1：他们称"最强（行为层）"证据 —— test.cpp:7000/7087/7170/7513 闭 K48+K76，
     且 :6997/:7598/:7621 注释逐字含 `SW12_U1REF_BST_ACM` 与 `ACM200_FH5`
  C) 附：`K_BST_ACM` 的调用点计数（他们称 1 定义 / 0 调用点 ⇒ 降级为文档证据）
"""
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
DEP = cfg['derived']['test_cpp']
PAY = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10',
                   'implementation-payload-TM600-TM601.cpp')


def load(p):
    d = open(p, 'rb').read()
    return d.decode('utf-8-sig', errors='replace'), d


dep_t, dep_b = load(DEP)
pay_t, pay_b = load(PAY)
print('部署态 test.cpp  %d B / %s' % (len(dep_b), hashlib.sha256(dep_b).hexdigest()))
print('payload          %d B / %s' % (len(pay_b), hashlib.sha256(pay_b).hexdigest()))

print('\n=== A) §4 交叉验证：payload vs 部署态 SetOn 的"闭错/漏闭"区分 ===')


def setons(text):
    out = []
    for m in re.finditer(r'cbite\.SetOn\(([^;]*)\);', text):
        line = text.count('\n', 0, m.start()) + 1
        args = [a.strip() for a in m.group(1).split(',') if a.strip() and a.strip() != '-1']
        nums = set()
        for a in args:
            mm = re.match(r'K(\d+)_', a)
            if mm:
                nums.add(int(mm.group(1)))
            elif re.fullmatch(r'\d+', a):
                nums.add(int(a))
        out.append((line, args, nums))
    return out


pay603 = [x for x in setons(pay_t) if 'K154_BUSH0_AMUX' in ' '.join(x[1]) or 'K83_BUSH0_PMID' in ' '.join(x[1])]
print('  payload SetOn 行: %s' % [(l, sorted(n)) for l, _a, n in pay603])
for l, a, n in pay603:
    print('     L%-5d 含48/76=%-5s 含109/110=%-5s' % (l, {48, 76} <= n, bool({109, 110} & n)))
    break
print('  payload 全部 SetOn: %s' % [(l, sorted(n)) for l, _a, n in setons(pay_t)])

print('\n  部署态 TM600/TM601 SetOn（按函数块）:')
import verify_relay_trace as V  # noqa: E402
blocks = dict(V.fn_blocks(dep_t))
for fn in ('TM600_HS_RDSON', 'TM601_LS_RDSON'):
    n = set()
    for r in V.parse_setons(blocks[fn]):
        mm = re.match(r'K(\d+)_', r)
        if mm:
            n.add(int(mm.group(1)))
        elif re.fullmatch(r'\d+', r):
            n.add(int(r))
    print('     %-16s %s  含48/76=%-5s 含109/110=%-5s' % (fn, sorted(n), {48, 76} <= n, bool({109, 110} & n)))

print('\n=== B) §1 行为证据核对：所引行号与内容 ===')
for ln in (6997, 7000, 7087, 7170, 7513, 7598, 7621):
    lines = dep_t.splitlines()
    if 0 < ln <= len(lines):
        print('  L%-5d %s' % (ln, ' '.join(lines[ln - 1].split())[:170]))
    else:
        print('  L%-5d <超出文件行数>' % ln)

print('\n  —— 这些行是否同时出现 SW12_U1REF_BST_ACM 与 ACM200_FH5 / K48 / K76 ——')
for ln in (6997, 7000, 7087, 7170, 7513, 7598, 7621):
    lines = dep_t.splitlines()
    if 0 < ln <= len(lines):
        s = lines[ln - 1]
        print('  L%-5d 宏名=%-5s FH5=%-5s K48=%-5s K76=%s'
              % (ln, 'SW12_U1REF_BST_ACM' in s, 'ACM200_FH5' in s, 'K48' in s, 'K76' in s))

print('\n=== C) K_BST_ACM / K48_ACM5_AMP_REF 的调用点计数（文档证据 vs 行为证据）===')
for label, txt in (('部署态 test.cpp', dep_t), ('payload', pay_t)):
    print('  %-14s K_BST_ACM=%-3d K48_ACM5_AMP_REF=%-3d K76_ACM_BST=%-3d K110_ACM18_BST=%d'
          % (label, txt.count('K_BST_ACM'), txt.count('K48_ACM5_AMP_REF'),
             txt.count('K76_ACM_BST'), txt.count('K110_ACM18_BST')))
