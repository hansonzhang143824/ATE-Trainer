# -*- coding: utf-8 -*-
"""t30 patcher v4 — 断言作用范围改为**契约自身声明的使用方**（而非门禁内部 ZCD 家族列表）。

v3 之错（实测自纠）: v3 把断言限定在门禁自身 `targets`（TM607/608/609/640，由 meta powered_pins
拓扑指纹派生）内 —— 而**本缺陷恰好在 TM600 上**，它根本不在那份列表里 ⇒ 阳性对照跑出 FAIL=0/exit 0
（**断言失效**）。这正说明"门禁为何看不见 K110"：它的目标集是按 BST-SW 家族指纹算的，不含
高电流 RDSON 项。故作用范围必须由**契约自己的声明**决定：
    对每个 payload 函数 TM，若契约里存在别名 a 使 <TM> 以独立 token 出现在 `usedByTm` 中，
    或 <TM> 在 `tmDeltas.<TM>.aliasesUsed` 中声明了 a ⇒ 用 a 的 `closedRelayNumbers` 作期望集合。
判据源选择仍为 v3 结论（只取别名闭合并集；pinRouteTable/relaySet 仅作 locator）。
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')

OLD = '''    scope = [name for name, _topo, _ir in targets]
    for tm in scope:
        data = payload.get(tm)
        if data is None:
            continue'''
NEW = '''    # 作用范围 = 契约自身声明的使用方（不限于门禁内部 ZCD 家族列表 —— 否则会漏掉本缺陷的 TM600）
    scope = sorted(tm for tm in payload if _base_of(contract, tm) is not None)
    for tm in scope:
        data = payload.get(tm)
        if data is None:
            continue'''


def main():
    raw = open(TARGET, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    nl = '\r\n' if t.count('\r\n') else '\n'
    old = OLD.replace('\n', nl)
    new = NEW.replace('\n', nl)
    if '--verify-only' in sys.argv:
        print('  v3 scope 块命中 %d 次' % t.count(old))
        return
    if t.count(old) != 1:
        raise SystemExit('ERROR: v3 scope 块命中 %d 次 (应 1)' % t.count(old))
    out = t.replace(old, new, 1).encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    open(TARGET, 'wb').write(out)
    print('PATCHED(v4) %s\n  before=%s (%d B)\n  after =%s (%d B)'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw),
             hashlib.sha256(out).hexdigest(), len(out)))


if __name__ == '__main__':
    main()
