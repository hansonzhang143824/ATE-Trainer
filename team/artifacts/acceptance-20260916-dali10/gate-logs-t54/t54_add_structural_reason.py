# -*- coding: utf-8 -*-
"""核查报告措辞 + 为 B-7 的 behaviorEvidence 补"结构性原因"（--tm-scope 到不了断言）。幂等。"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN, 'build-report.json')
GEN = os.path.join(HERE, 't54_make_report.py')
MARK = '结构性原因（行级）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


rep = json.load(io.open(REPORT, encoding='utf-8-sig'))
g = rep['gateFailOpenForms']['forms'][0]
b7 = rep['capabilityLimitations'][0]
print('=== 核查现状 ===')
print('  形态1 含"不是\"不受影响\"" =', '不是"不受影响"' in g['affectsThisRunGate'])
print('  形态1 含"逐条校验"      =', '逐条校验' in g['affectsThisRunGate'])
print('  B-7 含结构性原因          =', MARK in b7['behaviorEvidence'])
print('  emptyPassGuard.rule 含 targets=N>0 =', 'targets=N>0' in rep['emptyPassGuard']['rule'])

STRUCT = ('【' + MARK + '】**任何 scope 参数都到不了断言**：早退 `L497-499 return 0` 早于 '
          '`L512 _scope = resolve_scope(args)` 与 `L515 check_contract_closures(...)` '
          '⇒ 不是"scope 值不对"，而是**代码路径根本走不到** ⇒ 用 `--tm-scope` 绕行'
          '**从设计上被封死**（把实测上升为结构性结论）。')

if MARK in b7['behaviorEvidence']:
    print('\n  B-7 已含（幂等）')
else:
    b7['behaviorEvidence'] = b7['behaviorEvidence'].rstrip() + ' ' + STRUCT
    io.open(REPORT, 'w', encoding='utf-8').write(json.dumps(rep, ensure_ascii=False, indent=2))
    print('\n  已补 B-7.behaviorEvidence → %d B' % os.path.getsize(REPORT))

    # 同步进生成器，避免下次重写丢失
    t = io.open(GEN, encoding='utf-8-sig').read()
    OLD = "'加 `--tm-scope TM600_HS_RDSON,TM601_LS_RDSON` 后仍空 PASS / exit 0** ⇒ `--tm-scope` 救不了。')"
    NEW = ("'加 `--tm-scope TM600_HS_RDSON,TM601_LS_RDSON` 后仍空 PASS / exit 0** ⇒ `--tm-scope` 救不了。')\n"
           "        + ' " + STRUCT.replace("'", "\\'") + "',")
    if "'加 `--tm-scope TM600_HS_RDSON,TM601_LS_RDSON` 后仍空 PASS / exit 0** ⇒ `--tm-scope` 救不了。')" in t:
        t = t.replace(OLD, NEW, 1)
        io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
        print('  已同步进生成器 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 生成器锚点未命中（请人工检查）')

print('\n=== 重生成验证 ===')
import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  ', (r.stdout or '').strip().splitlines()[0] if r.stdout else r.stderr[:150])
rep2 = json.load(io.open(REPORT, encoding='utf-8-sig'))
print('  B-7 含结构性原因 =', MARK in rep2['capabilityLimitations'][0]['behaviorEvidence'])
print('  报告 %d B ; verdict=%s' % (os.path.getsize(REPORT), rep2['verdict']))
