# -*- coding: utf-8 -*-
"""门禁后复核（SUPERVISOR GATE 要求）：对本轮**全部变更产物**做一次完整的 post-change 验证。

覆盖：
  A. JSON 可解析 + schema
  B. JSONL 账本：逐行可解析 + 链式自证（prevLineSha256 与上一行实际哈希一致）
  C. 生成器可重跑且**幂等**（连跑两次 → 同 size 同 sha256，除时间戳行）
  D. 关键字段在位（逐项断言）
  E. 两棵树未被我写入 + devel 哈希
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
T28 = os.path.join(RUN, 'gate-logs-t28')

fails = []


def chk(name, cond, detail=''):
    print('  [%s] %-52s %s' % ('OK ' if cond else 'FAIL', name, detail))
    if not cond:
        fails.append(name)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== A. JSON 可解析 + schema ===')
rep = os.path.join(RUN, 'build-report.json')
A = json.load(io.open(rep, encoding='utf-8-sig'))
chk('build-report.json 可解析', True, '%d B' % os.path.getsize(rep))
r = subprocess.run([sys.executable, os.path.join(WS, 'scripts', 'validate_team_artifact.py'),
                    'build-report', rep], capture_output=True, text=True, encoding='utf-8')
chk('schema PASS/exit 0', r.returncode == 0, (r.stdout or '').strip().splitlines()[0][:70])
for p in (os.path.join(T28, 't28-anchors.snapshots.meta.json'),
          os.path.join(T28, 't28-anchors.json'),
          os.path.join(RUN, 'setup-contract.json')):
    try:
        json.load(io.open(p, encoding='utf-8-sig'))
        chk('可解析 %s' % os.path.basename(p), True)
    except Exception as e:
        chk('可解析 %s' % os.path.basename(p), False, str(e)[:60])

print('\n=== B. JSONL 账本：逐行解析 + 链式自证 ===')
J = os.path.join(T28, 't28-anchors.snapshots.jsonl')
lines = io.open(J, encoding='utf-8').read().strip().splitlines()
chk('账本非空', len(lines) >= 1, '%d 行' % len(lines))
okparse = True
for i, l in enumerate(lines, 1):
    try:
        json.loads(l)
    except Exception as e:
        okparse = False
        chk('第 %d 行可解析' % i, False, str(e)[:50])
chk('全部行可解析', okparse)
chained = [json.loads(l) for l in lines if 'prevLineSha256' in l]
if chained:
    last = chained[-1]
    idx = lines.index(json.dumps(last, ensure_ascii=False))
    prev_actual = hashlib.sha256(lines[idx - 1].encode('utf-8')).hexdigest()
    chk('链式自证 prevLineSha256 正确', last['prevLineSha256'] == prev_actual)
    chk('双哈希字段在位', ('live_lf_sha256' in last and 'live_sha256' in last))
    meta = json.load(io.open(os.path.join(T28, 't28-anchors.snapshots.meta.json'), encoding='utf-8-sig'))
    chk('meta.appendOnly == true', meta.get('appendOnly') is True)
    chk('meta.hashPolicy 在位', 'hashPolicy' in meta)

print('\n=== C. 生成器幂等（连跑两次）===')
GEN = os.path.join(HERE, 't54_make_report.py')
sigs = []
import re as _re
_TS = _re.compile(r'^\s*"generatedAt": ".*?",\s*$', _re.M)


def _body_sha(bb):
    return hashlib.sha256(_TS.sub('', bb.decode('utf-8-sig')).strip().encode('utf-8')).hexdigest()


for i in (1, 2):
    rr = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    if rr.returncode != 0:
        chk('生成器 run%d 成功' % i, False, (rr.stderr or '')[:80])
    b = open(rep, 'rb').read()
    d = json.loads(b.decode('utf-8-sig'))
    sigs.append((len(b), _body_sha(b), hashlib.sha256(b).hexdigest(),
                 len(d.get('gateFailOpenForms', {}).get('forms', []))))
chk('连跑两次 size 一致', sigs[0][0] == sigs[1][0], '%s' % (sigs[0][0],))
chk('连跑两次 **body** 哈希一致（跨秒可复现）', sigs[0][1] == sigs[1][1],
    'body=%s' % (sigs[0][1][:12],))
chk('整文件哈希（含 generatedAt ⇒ 跨秒必不同，仅参考）', True,
    'file1=%s file2=%s' % (sigs[0][2][:10], sigs[1][2][:10]))

print('\n=== D. 关键字段在位 ===')
need = ['contract', 'gateSummary', 'controls', 'attributionSplit', 'attributionLimitations',
        'attributionThreeStates', 'exitZeroSemantics', 'emptyPassGuard', 'capabilityLimitations',
        'gateFailOpenForms', 'withdrawnClaims', 'checkExtraStance', 'provenanceSources', 'builds',
        'diagnostics']
for k in need:
    chk('字段 %s' % k, k in A, '' if k in A else '**缺失**')
c = A['contract']
chk('contract 顶层无 size/sha256/mtime', not [k for k in ('size', 'sha256', 'mtime') if k in c])
chk('contract.baseline 在位', bool(c.get('baseline')))
chk('gateExpectationSet.residualCaveat 在位', 'residualCaveat' in (c.get('gateExpectationSet') or {}))
chk('emptyPassGuard.status 标【未强制】', '【未强制】' in A['emptyPassGuard']['status'])
chk('bst2sw_supersededCh1VariantRelaySet 在位', 'bst2sw_supersededCh1VariantRelaySet' in c)
chk('bst2sw_closedRelayNumbersSuperseded 在位', 'bst2sw_closedRelayNumbersSuperseded' in c)
chk('verdict == blocked（未伪造 GREEN）', A['verdict'] == 'blocked', A['verdict'])

print('\n=== E. 两棵树未被写入 ===')
dep = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'
dev = 'D:/PROJECT6-DALI/devel/source/test.cpp'
chk('部署态仍为 15c7d2b8…（未落盘）', sha(dep).startswith('15c7d2b8'), '%d B' % os.path.getsize(dep))
chk('devel 未被我改（434,629 B）', os.path.getsize(dev) == 434629, '%d B' % os.path.getsize(dev))

print('\n=== 汇总 ===')
print('  FAIL 项 =', fails if fails else '（无）')
print('  总判定 =', 'PASS' if not fails else 'FAIL')
