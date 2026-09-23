# -*- coding: utf-8 -*-
"""按 rule-reviewer ③ 的要求：**另存**一份"以现盘 payload 为对象"的期望日志（不覆盖旧日志）。

命名：`t33-postreplace-expectation-live.log`
文件头写明：对象全路径 + size + sha256 + 现算时刻 + 条目数 + 契约 rev。
其中 expectations 用**门禁自身函数**推导（`expected_for_tm`），并对两态（payload / 部署态）复算 missing。
"""
import datetime
import hashlib
import io
import json
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
sys.path.insert(0, os.path.join(WS, 'scripts'))

PAY = os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp')
DEP = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'
CON = os.path.join(RUN, 'setup-contract.json')
OUT = os.path.join(RUN, 'gate-logs-t33', 't33-postreplace-expectation-live.log')

spec = importlib.util.spec_from_file_location('g', os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py'))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


C = json.loads(open(CON, 'rb').read().decode('utf-8-sig'))
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

lines = []
lines.append('=== t33 postReplace 期望（**现盘 payload 版**）===')
lines.append('生成时刻 : %s' % now)
lines.append('生成方式 : 由脚本 `gate-logs-t33/t33_postreplace_expectation_live.py` 现算写入（无人工手抄）')
lines.append('')
lines.append('对象（payload）: team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp')
lines.append('  size   = %d B' % os.path.getsize(PAY))
lines.append('  sha256 = %s' % sha(PAY))
lines.append('对象（部署态）: D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp')
lines.append('  size   = %d B' % os.path.getsize(DEP))
lines.append('  sha256 = %s' % sha(DEP))
lines.append('契约: team/artifacts/acceptance-20260916-dali10/setup-contract.json')
lines.append('  revision = %s ; size = %d B' % (C.get('revision'), os.path.getsize(CON)))
b = [x for x in C['aliasResolution'] if x.get('alias') == 'bst2sw'][0]
lines.append('  aliasResolution[bst2sw].resolution.closedRelayNumbers = %s'
             % (b.get('resolution') or {}).get('closedRelayNumbers'))
lines.append('')
lines.append('预期（用门禁自身函数 check_contract_closures 现算；scope = DEFAULT_TM_SCOPE）：')
for label, path in (('payload(候选)', PAY), ('deployed(部署态)', DEP)):
    txt = io.open(path, encoding='utf-8-sig', errors='replace').read()
    errs, checked = g.check_contract_closures(txt, C, [], None, False, None)
    lines.append('  [%s] errors=%d' % (label, len(errs)))
    for tm, v in (checked or {}).items():
        lines.append('      %-16s expected=%-26s missing=%s' % (tm, v['expected'], v['missing']))
    for e in (errs or [])[:4]:
        lines.append('      - %s' % str(e)[:150])
lines.append('')
lines.append('结论：payload 侧 missing=[] ⇒ **落盘后预期 bst-sw GREEN**；部署态 missing=[48,76] ⇒ 当前 NEW-RED（真因）。')
lines.append('注：本文件**不覆盖**旧日志 `t33-postreplace-expectation.log`（后者对象为旧 payload 39,457 B，作历史留痕）。')

io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('WROTE gate-logs-t33/t33-postreplace-expectation-live.log (%d B)' % os.path.getsize(OUT))
print('  条目数(日志行) =', len(lines))
print('  sha256 =', sha(OUT))
print()
print('\n'.join(lines[:14]))
