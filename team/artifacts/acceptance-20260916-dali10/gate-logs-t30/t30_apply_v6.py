# -*- coding: utf-8 -*-
"""t30 patcher v6 — 修 v5 的接线错误: `args` 不在 check_contract_closures 作用域内。

改法: `--tm-scope` 在 main() 里解析 → 把 scope **作为参数**传入 check_contract_closures；
      并新增 `--list-scope` 便于审计实际生效范围。
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')

OLD_SIG = '''def check_contract_closures(src_text, contract, targets, extra_alias_cfg=None, check_extra=False):
    """契约声明必需集合 ⊆ payload SetOn 集合（限定在门禁 targets 内）；缺失 → errors[]。"""
    errors, checked = [], {}
    payload = _numbers_from_payload(src_text)
    alias_idx = _alias_index(contract)
'''
NEW_SIG = '''def check_contract_closures(src_text, contract, targets, extra_alias_cfg=None, check_extra=False,
                            scope=None):
    """契约声明必需集合 ⊆ payload SetOn 集合；缺失 → errors[]（致命通道）。

    scope: 参与判定的函数名列表；None ⇒ DEFAULT_TM_SCOPE（由 --tm-scope 参数化）。
    """
    errors, checked = [], {}
    payload = _numbers_from_payload(src_text)
    alias_idx = _alias_index(contract)
'''

OLD_SCOPE = '''    # 作用范围 = 本 run 实现所覆盖的函数（默认 t20/t23 的两个目标函数；--tm-scope 可覆盖）。
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
'''
NEW_SCOPE = '''    if scope is None:
        scope = DEFAULT_TM_SCOPE
'''

HELPER_ANCHOR = 'def parse_alias_overrides(args):'
HELPER = '''def resolve_scope(args):
    """--tm-scope <TM_x,TM_y> 覆盖默认作用范围；未给 ⇒ DEFAULT_TM_SCOPE。

    作用范围的语义（v3/v4 实测教训）: 必须覆盖**本 run 实现在做的函数**，否则断言对本次改动失明；
    又不应把"契约 usedByTm 提及但实际在 ramp/后续段使用"的函数一并判红（TM108/109 的 pgnd2sw、
    TM1205 的 path 别名），故范围显式、可审计、可参数化。
    """
    if '--tm-scope' in args:
        i = args.index('--tm-scope')
        if i + 1 < len(args) and not args[i + 1].startswith('--'):
            return [x.strip() for x in args[i + 1].split(',') if x.strip()]
    return DEFAULT_TM_SCOPE


'''

OLD_CALL = '''        _cc_errors, _cc_checked = check_contract_closures(
            text, contract, targets, _extra_alias, check_extra=('--check-extra' in args))'''
NEW_CALL = '''        _scope = resolve_scope(args)
        if '--list-scope' in args:
            print(f"[t30] 生效作用范围 = {_scope}")
        _cc_errors, _cc_checked = check_contract_closures(
            text, contract, targets, _extra_alias, check_extra=('--check-extra' in args),
            scope=_scope)'''


def main():
    raw = open(TARGET, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    nl = '\r\n' if t.count('\r\n') else '\n'
    pairs = [(OLD_SIG, NEW_SIG), (OLD_SCOPE, NEW_SCOPE), (HELPER_ANCHOR, HELPER + HELPER_ANCHOR),
             (OLD_CALL, NEW_CALL)]
    if '--verify-only' in sys.argv:
        for i, (o, _n) in enumerate(pairs, 1):
            print('  锚点 %d 命中 %d 次' % (i, t.count(o.replace('\n', nl))))
        return
    for i, (o, n) in enumerate(pairs, 1):
        o2, n2 = o.replace('\n', nl), n.replace('\n', nl)
        if t.count(o2) != 1:
            raise SystemExit('ERROR: 锚点 %d 命中 %d 次 (应 1)' % (i, t.count(o2)))
        t = t.replace(o2, n2, 1)
    out = t.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    open(TARGET, 'wb').write(out)
    print('PATCHED(v6) %s\n  before=%s (%d B)\n  after =%s (%d B)'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw),
             hashlib.sha256(out).hexdigest(), len(out)))


if __name__ == '__main__':
    main()
