# -*- coding: utf-8 -*-
"""t30 patcher v7 (hardening) — 缺失清单不再靠字符串匹配，改为结构化返回。

问题: v6 的打印行用 `('K%d ' % n) in e` 反推缺失号 ⇒ 若某号是另一号的前缀 (如 K61 与 K610)
      会误判。改为: check_contract_closures 返回 {TM: {"expected":[..], "missing":[..]}}。
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')

OLD_1 = '''        checked[tm] = sorted(exp)
        for n in sorted(set(exp) - data['nums']):
            line = min(data['lines'].values()) if data['lines'] else 0
            loc = _locators_for(contract, base, n)'''
NEW_1 = '''        missing = sorted(set(exp) - data['nums'])
        checked[tm] = {'expected': sorted(exp), 'missing': missing}
        for n in missing:
            line = min(data['lines'].values()) if data['lines'] else 0
            loc = _locators_for(contract, base, n)'''

OLD_2 = '''        for _tm, _nums in sorted(_cc_checked.items()):
            _miss = sorted({n for n in _nums
                            if any(e.startswith(_tm + ':') and ('K%d ' % n) in e for e in _cc_errors)})
            print(f"[t30] {_tm}: 契约声明必需 {_nums} vs payload SetOn 比对完成, 缺失={_miss}")'''
NEW_2 = '''        for _tm, _info in sorted(_cc_checked.items()):
            print(f"[t30] {_tm}: 契约声明必需 {_info['expected']} vs payload SetOn 比对完成, "
                  f"缺失={_info['missing']} (缺失数 {len(_info['missing'])})")'''

# check_extra 循环里 checked 现在是 dict，需相应取 expected
OLD_3 = '''        if check_extra:
            allowed = set(exp) | set(budget)'''
NEW_3 = '''        if check_extra:
            allowed = set(exp) | set(budget)  # exp 为本轮该 TM 的期望集合'''


def main():
    raw = open(TARGET, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    nl = '\r\n' if t.count('\r\n') else '\n'
    pairs = [(OLD_1, NEW_1), (OLD_2, NEW_2)]
    if '--verify-only' in sys.argv:
        for i, (o, _n) in enumerate(pairs, 1):
            print('  锚点 %d 命中 %d 次' % (i, t.count(o.replace('\n', nl))))
        return
    for i, (o, n) in enumerate(pairs, 1):
        o2, n2 = o.replace('\n', nl), n.replace('\n', nl)
        if t.count(o2) != 1:
            raise SystemExit('ERROR: 锚点 %d 命中 %d 次' % (i, t.count(o2)))
        t = t.replace(o2, n2, 1)
    out = t.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    open(TARGET, 'wb').write(out)
    print('PATCHED(v7) %s\n  before=%s (%d B)\n  after =%s (%d B)'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw),
             hashlib.sha256(out).hexdigest(), len(out)))


if __name__ == '__main__':
    main()
