# -*- coding: utf-8 -*-
"""**完整**清理"relay-trace 不受影响 / 未再参与数值比较"的过强表述（上一轮只改了 3 处，属部分修复）。

覆盖：
  gate-logs-t54/t54_relaytrace_settled.py     （源头脚本，L7 docstring + L52/L53 print）
  gate-logs-t54/t54-relaytrace-settled.log    （由该脚本生成的记录）
  gate-logs-t54/t54_settle_relaytrace_unknown.py（L9 docstring + L55 print）
  gate-logs-t54/t54_make_report.py            （报告生成器的旧值，已与产物不一致）
策略：源头脚本改为**正确的谓词**；历史 log **不改历史输出**，但**加显式更正横幅**（保证未来读者不被误导）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def patch(path, pairs, label):
    if not os.path.isfile(path):
        print('  MISSING %s' % label)
        return
    t = io.open(path, encoding='utf-8-sig', errors='replace').read()
    orig = t
    applied = 0
    for old, new in pairs:
        if new[:30] in t:
            continue
        if old in t:
            t = t.replace(old, new, 1)
            applied += 1
    if t != orig:
        io.open(path, 'w', encoding='utf-8', newline='').write(t)
        print('  %-48s 已改 %d 处 → %d B' % (label, applied, os.path.getsize(path)))
    else:
        print('  %-48s 无需改（幂等）' % label)


CORRECT = ('L376 `n = defines[r]` 之后，**L401 `if n in on_set` / L403 `if n in nc_set` 把 n 当数字使用**，'
           '而 `r` 来自 `parse_setons()`（原样取 SetOn 实参、不做宏展开）⇒ **多值宏只校验首值** '
           '⇒ 属**欠严（under-strict）**，**不是"不受影响"**；')
print('=== 更正源头脚本与报告生成器 ===')
patch(os.path.join(HERE, 't54_relaytrace_settled.py'), [
    ('L376-397  `n = defines[r]` 之后，功能规则用的是 `cap_pin(r)` / `is_pu(r)` / `is_p2p(r)`，**未再使用 n 做数值比较**',
     CORRECT),
    ("print('     L376 的 n 之后未再参与数值比较 ⇒ **relay-trace 的 PASS 不依赖被截断值** ⇒')",
     "print('     ⚠️ 更正：n 在 L401/L403 被当数字使用（只校验多值宏首值）⇒ 属**欠严**，不是\"不受影响\" ⇒')"),
    ('print(\'     该 PASS 可以作为"多值宏路线"的证据（不是被截断值造成的假通过）。\')',
     'print(\'     该 PASS **不是假通过**，但**不作为多值宏逐条校验的证据**（欠严）。\')'),
], 't54_relaytrace_settled.py')

patch(os.path.join(HERE, 't54_settle_relaytrace_unknown.py'), [
    ('⇒ 关键问题：这些"无通道号别名"是否落在**多值宏**里？若是 ⇒ 截断影响判据；若否 ⇒ PASS 不受影响。',
     '⇒ 关键问题：这些"无通道号别名"是否落在**多值宏**里？若是 ⇒ 截断可能进入判据。'
     '（⚠️ 事后更正：L401/L403 确实把 n 当数字用 ⇒ 多值宏**只校验首值** ⇒ 属**欠严**，不能称"不受影响"。）'),
    ("print('     其 PASS **可以**作为\"多值宏路线\"的证据（即：PASS 不是被截断值造成的假通过）。')",
     "print('     更正：该 PASS 不是假通过，但**不作为多值宏逐条校验的证据**（L401/L403 只覆盖首值 ⇒ 欠严）。')"),
], 't54_settle_relaytrace_unknown.py')

patch(os.path.join(HERE, 't54_make_report.py'), [
    ("'affectsThisRunGate': '**否** —— 其判据只消费 Cap 家族（19 个，多值宏 0）⇒ `relay-trace` 的 PASS 不受影响',",
     "'affectsThisRunGate': '" + CORRECT.replace("'", "\\'") + " Cap 映射路径（cap_defs/L316）确实不受影响，但整体属欠严',"),
], 't54_make_report.py')

print('\n=== 给历史 log 加更正横幅（不改历史输出）===')
BANNER = ('\n\n⚠️ **更正横幅（2026-09-16，之后复核发现）**：本日志上文"n 之后未再参与数值比较 / PASS 不受影响"'
          '**已作废** —— `n` 在 **L401 `if n in on_set` / L403 `if n in nc_set`** 被当数字使用，'
          '而 `r` 来自 `parse_setons()`（不做宏展开）⇒ **多值宏只校验首值 ⇒ 属欠严（under-strict）**。\n'
          '现口径见 `t54-gate-failopen-forms.md` 形态 1 与 `build-report.json` 的 `gateFailOpenForms` / `withdrawnClaims`。\n')
for f in ('t54-relaytrace-settled.log', 't54-failopen-verify.log'):
    p = os.path.join(HERE, f)
    if not os.path.isfile(p):
        continue
    t = io.open(p, encoding='utf-8-sig', errors='replace').read()
    if '更正横幅（2026-09-16，之后复核发现）' in t:
        print('  %-48s 已有横幅（幂等）' % f)
    else:
        io.open(p, 'w', encoding='utf-8', newline='').write(t.rstrip() + BANNER)
        print('  %-48s 已加横幅 → %d B' % (f, os.path.getsize(p)))
