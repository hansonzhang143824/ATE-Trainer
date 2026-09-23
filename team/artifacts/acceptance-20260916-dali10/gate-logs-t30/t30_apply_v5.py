# -*- coding: utf-8 -*-
"""t30 patcher v5 (final) — 断言作用范围 = "本 run 实现所覆盖的 TM"（显式、可参数化、可审计）。

四轮判据选择（全部只读实测，证据 `t30-criteria-probe.txt` + 各版日志）:
  v1 用 pinRouteTable 并集        → 误报（它是"通往每个 PIN 的全部可能路线"枚举）
  v2 用 relaySet 整体             → 误报（它是资源预算池，含无路由依据的 K17/K18/K20/K86/K130/K142）
  v3 用门禁内部 targets（ZCD 家族）→ **断言失效**（TM600 根本不在那份列表里 ⇒ FAIL=0）
  v4 用契约 usedByTm 全量         → 过度归因：TM108/109 的 pgnd2sw 属 ramp 段、TM1205 走自己的
                                     path 别名（K_FPVIH_TO_SW1_A=46 / K_FPVIL_TO_BST1_A=41），
                                     并非 Step 1 必须闭合 ⇒ 11 条红（超出 t30"阴性对照"要求）
  v5（本版）= 契约别名集合判定 **+ 显式作用范围**（默认 = 本 run 实现在做的两个 TM 函数）

作用范围参数化（不硬编码继电器号；换 run/换裁定只改参数，不改判据）：
  默认 = `--tm-scope` 未给时取 **TM600_HS_RDSON,TM601_LS_RDSON**（t20/t23 实现对象的函数名）
  可覆盖 = `--tm-scope TM600_HS_RDSON,TM601_LS_RDSON,TM1205_TRX_BST_UV_GD`（若裁定要求覆盖更多）
  原理 = 范围必须覆盖"本 run 改动的函数"，否则门禁对**这轮改动**依旧失明（v3 的教训）
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')

OLD = "    scope = sorted(tm for tm in payload if _base_of(contract, tm) is not None)\n"
NEW = """    # 作用范围 = 本 run 实现所覆盖的函数（默认 t20/t23 的两个目标函数；--tm-scope 可覆盖）。
    # 理由（v3 实测教训）: 若范围取自门禁自身的 ZCD 家族 targets，则 TM600 不在其中 ⇒ 断言失效；
    # 若取自契约 usedByTm 全量，则 TM108/109（ramp 段用 pgnd2sw）、TM1205（走自己的 path 别名）会被
    # 过度归因 ⇒ 超出"阴性对照"要求。故范围显式化、可审计、可参数化。
    _scope_arg = None
    if '--tm-scope' in args:
        _i = args.index('--tm-scope')
        if _i + 1 < len(args):
            _scope_arg = args[_i + 1]
    if _scope_arg:
        scope = [x.strip() for x in _scope_arg.split(',') if x.strip()]
    else:
        scope = DEFAULT_TM_SCOPE
"""
OLD_DEFAULT = "CONTRACT_RULE_NOTE = ("
NEW_DEFAULT = """DEFAULT_TM_SCOPE = ["TM600_HS_RDSON", "TM601_LS_RDSON"]   # 本 run 实现的函数（--tm-scope 可覆盖）

CONTRACT_RULE_NOTE = ("""


def main():
    raw = open(TARGET, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    nl = '\r\n' if t.count('\r\n') else '\n'
    old = OLD.replace('\n', nl)
    new = NEW.replace('\n', nl)
    old_d = OLD_DEFAULT
    new_d = NEW_DEFAULT.replace('\n', nl)
    if '--verify-only' in sys.argv:
        print('  scope 块命中 %d 次; DEFAULT 锚点命中 %d 次' % (t.count(old), t.count(old_d)))
        return
    if t.count(old) != 1 or t.count(old_d) != 1:
        raise SystemExit('ERROR: 锚点命中异常 (scope=%d, default=%d)' % (t.count(old), t.count(old_d)))
    t = t.replace(old_d, new_d, 1).replace(old, new, 1)
    out = t.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    open(TARGET, 'wb').write(out)
    print('PATCHED(v5) %s\n  before=%s (%d B)\n  after =%s (%d B)'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw),
             hashlib.sha256(out).hexdigest(), len(out)))


if __name__ == '__main__':
    main()
