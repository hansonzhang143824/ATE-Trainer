# -*- coding: utf-8 -*-
"""核查并更正 build-report.json 中"relay-trace 不受影响"的过强表述（SUPERVISOR GATE 要求）。"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REPORT = os.path.join(RUN, 'build-report.json')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


rep = json.load(io.open(REPORT, encoding='utf-8-sig'))
s_before = json.dumps(rep, ensure_ascii=False)
print('=== 更正前核查 ===')
print('  build-report %d B' % os.path.getsize(REPORT))
print('  含"不受影响"        =', '不受影响' in s_before)
print('  含 "L401/L403"      =', ('L401' in s_before or 'L403' in s_before))
print('  含"欠严"            =', '欠严' in s_before)

form1 = rep['gateFailOpenForms']['forms'][0]
print('  形态1 affectsThisRunGate =', form1['affectsThisRunGate'][:120])

NEW_AFFECT = ('**部分/欠严（under-strict）** —— `cap_defs` 只收录 Cap 家族（多值宏 = 0）'
              '⇒ **Cap 别名↔规范名映射这条路不受影响**；'
              '但 `n = defines[r]` 在 **L401 `if n in on_set` / L403 `if n in nc_set`** 被**当数字使用**，'
              '而 `r` 来自 `parse_setons()`（原样取 SetOn 实参、不做宏展开）⇒ '
              '当 SetOn 写**多值宏名**时**只校验其首值那一个继电器**'
              '（例 `K_FPVIH_TO_PGND_A=154,155` ⇒ 只校验 154；`K_FPVIH_TO_BST_A=46,48,76` ⇒ 只校验 46）。'
              '⇒ **不是假通过，但不得作为"多值宏逐条校验"的证据。**')

if '欠严' in s_before and 'L401' in s_before:
    print('\n  已是最新（幂等）')
else:
    form1['affectsThisRunGate'] = NEW_AFFECT
    form1['guardrail'] = ('先测展开器再信展开；判"宏闭了哪些 K"用 StdAfx.h 原文逐字展开。'
                          '另：该门的成员性检查对多值宏只覆盖首值 ⇒ **欠严**，'
                          '不得作为"多值宏逐条校验"的证据。')
    rep['withdrawnClaims'] = rep.get('withdrawnClaims', []) + [{
        'claim': ('"`relay-trace` 的判据不受 `parse_defines()` 截断影响"（我早前结论）'),
        'status': '**已撤回（方向对但过强）**',
        'supersededBy': ('**欠严（under-strict）**：`cap_defs`/L316 这条 Cap 映射路径确实不受影响；'
                         '但 `n = defines[r]` 在 L401/L403 被当数字使用，而 `r` 不做宏展开 ⇒ '
                         '多值宏只校验首值。'),
        'evidence': ('逐行复核 `verify_relay_trace.py` L376/L401/L403/L406 + L92-98 `parse_setons()`；'
                     'log: gate-logs-t54/t54-n-numeric-verify.log'),
        'raisedBy': 'schematic-expert（我复核确认）',
    }]
    io.open(REPORT, 'w', encoding='utf-8').write(json.dumps(rep, ensure_ascii=False, indent=2))
    print('\n=== 已更正 ===')
    print('  %d B / %s' % (os.path.getsize(REPORT), sha(REPORT)))

rep2 = json.load(io.open(REPORT, encoding='utf-8-sig'))
s2 = json.dumps(rep2, ensure_ascii=False)
print('  含"欠严" =', '欠严' in s2, '| 含 L401 =', 'L401' in s2,
      '| withdrawnClaims 条数 =', len(rep2.get('withdrawnClaims') or []))
print('  verdict 仍 =', rep2['verdict'])
