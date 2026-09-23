# -*- coding: utf-8 -*-
"""t30 patcher v3 (可重复执行) — 断言只比对**契约显式声明的别名闭合集合**，并**限定在门禁目标函数**内。

判据选择过程（三步实测，全部只读；证据 `t30_source_probe.py` 输出 + `t30-criteria-probe.txt`）：
  A. `tmDeltas.<TM>.pinRouteTable[*][*].needsClosed` 并集 —— **弃用**：它是"通往每个 PIN 的
     **全部可能路线**"枚举（TM600[BST] 列出 7 条，含 CH0 High/QTMUe/QVMe/ACM200），并入判定会把
     未选中的路线当必需 ⇒ TM600 missing=23 / TM601 missing=18（大面积误报）。
  B. `tmDeltas.<TM>.relaySet` 整体 —— **弃用**：它是**资源预算池**，含大量只被 relaySet 提及、
     无任何路由依据的 K 号（实测 K17/K18/K20/K86/K130/K142 "仅 relaySet 提及"）⇒ TM600 missing=29。
  C. `aliasResolution[a].resolution.closedRelayNumbers`（a 的 `usedByTm` 含该 TM 基准名，
     或 a ∈ `tmDeltas.<TM>.aliasesUsed`）—— **采用**：实测 TM600 missing=[110]（正是真缺口），
     TM601 missing=[]（阴性对照零误报）。
  再加**门禁原生 scope**：只在门禁自身 `targets`（读 meta powered_pins 拓扑指纹得出的 BST-SW 家族
  函数）内断言 ⇒ 不牵连 TM000 等非本家族 TM。

保留的泛化开关（均**不硬编码继电器号**）：
  --tm-alias <TM>=<a1>,<a2>   修补 `tmDeltas.aliasesUsed` 漏登记（K109 裁定后可参数化收紧/放宽）
  --check-extra               SetOn 出现不在"契约别名闭合并集 ∪ relaySet ∪ 角色继电器"中的 K 号即红
                              （默认关闭；开关由契约/裁定控制，无需改代码）
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')
START_ANCHOR = '\n# =====================================================================\n# t30: '
END_ANCHOR = '\n\ndef main() -> int:'
CALL_START = '    # ---- t30: 契约闭合集合断言（致命通道: 与既有 FAIL 同一出口）----'
CALL_END = '| 判据: {CONTRACT_RULE_NOTE}")'

BLOCK = r'''
# =====================================================================
# t30: "SetOn 集合 vs 契约声明闭合集合" 断言（门禁补盲）
# ---------------------------------------------------------------------
# 盲区根因（实测）: 本脚本原先 **完全不读契约** —— setup-contract / aliasResolution /
#   needsClosed / relaySet / K109 / K110 命中数均为 0 ⇒ 只校验"序列 + K57 电容"，
#   因此"**契约要求闭合的继电器没闭**"在结构上不可见（12 门全绿却漏 K110）。
#
# 判据（可复用，不硬编码本 run 的任何继电器号）——取契约**显式声明的别名闭合集合**:
#     期望集合 = ∪ aliasResolution[a].resolution.closedRelayNumbers
#                a ∈ { 使 <TM> 以独立 token 出现在其 usedByTm 中的别名 }
#                  ∪ { tmDeltas.<TM>.aliasesUsed 声明的别名 }
#                  ∪ { --tm-alias <TM>=<a>,... 外部声明 }
#     比对对象 = 该函数块内**所有** cbite.SetOn(...) 的 K 号/裸数字（payload 明文）
#     作用范围 = 门禁自身 targets（BST-SW 家族函数）内的 TM —— 不牵连其它 TM
#   缺失项 → errors[] ⇒ exit 1（与既有 FAIL 同一出口）⇒ run_gates.ps1 exit!=0 ⇒ **NEW-RED**（非 warn）
#
# **为什么不并入** pinRouteTable / relaySet 整体（实测证据，避免后人重犯）:
#   · pinRouteTable 是"通往每个 PIN 的全部可能路线"枚举（TM600[BST] 有 7 条，含 CH0 High、
#     QTMUe、QVMe、ACM200 等），并入判定会把**未被选中的路线**当必需 ⇒ missing 23/18（误报）。
#   · relaySet 是**资源预算池**，含只被它提及、无任何路由依据的 K 号（实测 K17/K18/K20/K86/K130/K142
#     "仅 relaySet 提及"）⇒ missing 29（误报）。
#   两者仅作为**来源 locator** 附在失败信息里。
# =====================================================================

CONTRACT_RULE_NOTE = ("setup-contract.json aliasResolution[*].resolution.closedRelayNumbers "
                      "(indexed by usedByTm / tmDeltas.<TM>.aliasesUsed); route enumerations "
                      "(pinRouteTable) and the relaySet budget pool are locators only")


def _load_contract(path):
    """rb 读 + utf-8-sig（DLP 透明加密下必须这样读）。"""
    if not path or not os.path.isfile(path):
        return None
    with open(path, 'rb') as f:
        try:
            return json.loads(f.read().decode('utf-8-sig'))
        except (ValueError, UnicodeDecodeError):
            return None


def resolve_contract_path(cfg, args):
    """契约路径: --contract > proj_config 覆盖段 > <workspace>/team/artifacts/<run>/setup-contract.json。"""
    if '--contract' in args:
        i = args.index('--contract')
        if i + 1 < len(args) and not args[i + 1].startswith('--'):
            return args[i + 1]
    for key in ('setup_contract', 'setupContract'):
        v = (cfg.get('outputs') or {}).get(key) or (cfg.get('intermediates') or {}).get(key)
        if v:
            return v
    base = os.path.join(cfg.get('_root') or '', 'team', 'artifacts')
    if os.path.isdir(base):
        for d in reversed(sorted(x for x in os.listdir(base) if x.startswith('acceptance-'))):
            p = os.path.join(base, d, 'setup-contract.json')
            if os.path.isfile(p):
                return p
    return ''


def _numbers_from_payload(src_text):
    """{函数名: {"nums": set[int], "names": set[str], "lines": {arg: lineno}}}

    SetOn 集合 = 函数块内**所有** cbite.SetOn(...) 的参数（同时支持 K<num>_Name 与裸数字 126）。
    """
    out = {}
    fn_re = re.compile(r'int\s+(\w+)\s*\(short\s+funcindex')
    starts = [(m.start(), m.group(1)) for m in fn_re.finditer(src_text)]
    for idx, (start, name) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(src_text)
        block = src_text[start:end]
        base_line = src_text.count('\n', 0, start) + 1
        nums, names, lines = set(), set(), {}
        for call in re.finditer(r'cbite\.SetOn\(([^;]*)\)', block, re.DOTALL):
            line = base_line + block.count('\n', 0, call.start())
            for arg in call.group(1).split(','):
                arg = arg.strip()
                if not arg or arg == '-1':
                    continue
                names.add(arg)
                lines[arg] = line
                if re.fullmatch(r'\d+', arg):
                    nums.add(int(arg))
                else:
                    dm = re.match(r'K(\d+)_', arg)
                    if dm:
                        nums.add(int(dm.group(1)))
        out[name] = {"nums": nums, "names": names, "lines": lines}
    return out


def _nums_of_relay_entry(entry):
    """契约的继电器表示: int / "K110_ACM18_BST" / {"number":110,...} / 列表 → 数字集合。"""
    out = set()
    if isinstance(entry, bool):
        return out
    if isinstance(entry, (int, float)):
        out.add(int(entry))
    elif isinstance(entry, str):
        out |= {int(t) for t in re.findall(r'\d+', entry)}
    elif isinstance(entry, dict):
        for key in ('number', 'relay', 'relays'):
            if entry.get(key) is not None:
                out |= _nums_of_relay_entry(entry.get(key))
    elif isinstance(entry, (list, tuple)):
        for x in entry:
            out |= _nums_of_relay_entry(x)
    return out


def _base_of(contract, tm):
    for k in (contract.get('tmDeltas') or {}):
        if tm == k or tm.startswith(str(k) + '_'):
            return k
    return None


def _locators_for(contract, base, num):
    """纯 locator: 该继电器在路由枚举 / relaySet 中的出现处（不参与判定）。"""
    d = (contract.get('tmDeltas') or {}).get(base) or {}
    bits = []
    for pin, routes in (d.get('pinRouteTable') or {}).items():
        if not isinstance(routes, dict):
            continue
        for route, rv in routes.items():
            if isinstance(rv, dict) and num in _nums_of_relay_entry(rv.get('needsClosed')):
                bits.append('pinRouteTable[%s][%s] L%s' % (pin, route, rv.get('line')))
    if num in _nums_of_relay_entry(d.get('relaySet')):
        bits.append('relaySet')
    return '; '.join(bits)


def _alias_index(contract):
    idx = {}
    for e in (contract.get('aliasResolution') or []):
        a = str(e.get('alias', ''))
        nums = _nums_of_relay_entry((e.get('resolution') or {}).get('closedRelayNumbers'))
        users = set()
        for x in (e.get('usedByTm') or []):
            users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
        idx[a] = (nums, users)
    return idx


def expected_for_tm(contract, alias_idx, tm, extra_aliases=None):
    """(期望数字→来源, base, 预算池数字集合) ；契约未登记该 TM → (None, None, set())"""
    base = _base_of(contract, tm)
    if base is None:
        return None, None, set()
    d = contract['tmDeltas'][base]
    exp = {}
    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        for n in sorted(alias_idx.get(a, (set(), set()))[0]):
            exp.setdefault(n, 'aliasResolution[%s].closedRelayNumbers (declared by tmDeltas.%s.aliasesUsed)'
                           % (a, base))
    for a, (nums, users) in alias_idx.items():
        if base in users:
            for n in sorted(nums):
                exp.setdefault(n, 'aliasResolution[%s].closedRelayNumbers (usedByTm lists %s)'
                               % (a, base))
    for a in (extra_aliases or []):
        for n in sorted(alias_idx.get(a, (set(), set()))[0]):
            exp.setdefault(n, 'aliasResolution[%s].closedRelayNumbers (--tm-alias override)' % a)
    return exp, base, _nums_of_relay_entry(d.get('relaySet'))


def parse_alias_overrides(args):
    """--tm-alias TM600=bst2sw,pmid2sw （可多次）→ {TM: [alias, ...]}"""
    out = {}
    for i, a in enumerate(args):
        if a == '--tm-alias' and i + 1 < len(args):
            spec = args[i + 1]
            if '=' in spec:
                tm, aliases = spec.split('=', 1)
                out.setdefault(tm.strip(), [])
                out[tm.strip()] += [x.strip() for x in aliases.split(',') if x.strip()]
    return out


def check_contract_closures(src_text, contract, targets, extra_alias_cfg=None, check_extra=False):
    """契约声明必需集合 ⊆ payload SetOn 集合（限定在门禁 targets 内）；缺失 → errors[]。"""
    errors, checked = [], {}
    payload = _numbers_from_payload(src_text)
    alias_idx = _alias_index(contract)
    scope = [name for name, _topo, _ir in targets]
    for tm in scope:
        data = payload.get(tm)
        if data is None:
            continue
        exp, base, budget = expected_for_tm(contract, alias_idx, tm, (extra_alias_cfg or {}).get(tm))
        if not exp:
            continue
        checked[tm] = sorted(exp)
        for n in sorted(set(exp) - data['nums']):
            line = min(data['lines'].values()) if data['lines'] else 0
            loc = _locators_for(contract, base, n)
            errors.append(
                "%s: 契约声明必需的继电器 K%d **未出现在 cbite.SetOn 中** (契约来源: %s%s; "
                "payload locator: test.cpp:%d; 该函数实际闭合=%s)"
                % (tm, n, exp[n], (' | 契约侧 locator: ' + loc) if loc else '', line,
                   sorted(data['names'])))
        if check_extra:
            allowed = set(exp) | set(budget)
            for n in sorted(data['nums'] - allowed):
                if n in (13, 21, 44, 45, 57, 85, 126, 0, 5):   # 角色/仪表电容继电器（K*_Cap）
                    continue
                line = min(data['lines'].values()) if data['lines'] else 0
                errors.append("%s: cbite.SetOn 出现契约未声明必需的继电器 K%d "
                              "(payload locator: test.cpp:%d) —— --check-extra 已开启"
                              % (tm, n, line))
    return errors, checked


'''


def main():
    raw = open(TARGET, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    nl = '\r\n' if t.count('\r\n') else '\n'
    block = BLOCK.replace('\r\n', '\n').replace('\n', nl)
    start_anchor = START_ANCHOR.replace('\n', nl)
    end_anchor = END_ANCHOR.replace('\n', nl)

    if '--verify-only' in sys.argv:
        print('  crlf=%s ; 块存在=%s ; 接线存在=%s'
              % (bool(t.count('\r\n')), (start_anchor in t and end_anchor in t), CALL_START in t))
        return
    if not (start_anchor in t and end_anchor in t):
        raise SystemExit('ERROR: 找不到 t30 块')
    i = t.index(start_anchor)
    j = t.index(end_anchor, i)
    t = t[:i] + block + t[j:]

    ci = t.index(CALL_START)
    cj = t.index(CALL_END, ci) + len(CALL_END)
    t = t[:ci] + ('''    # ---- t30: 契约闭合集合断言（致命通道: 与既有 FAIL 同一出口）----
    contract_path = resolve_contract_path(cfg, args)
    contract = _load_contract(contract_path)
    if contract is None:
        errors.append("t30 契约断言无法执行: 读不到 setup-contract.json (path=%r) —— "
                      "契约是高电流路线闭合集合的权威, 缺失必须红而不是静默跳过" % (contract_path,))
    elif '--skip-contract-closures' in args:
        print("[t30] 契约闭合集合断言被 --skip-contract-closures 跳过（仅调试用）")
    else:
        _extra_alias = parse_alias_overrides(args)
        _cc_errors, _cc_checked = check_contract_closures(
            text, contract, targets, _extra_alias, check_extra=('--check-extra' in args))
        errors.extend(_cc_errors)
        for _tm, _nums in sorted(_cc_checked.items()):
            _miss = sorted({n for n in _nums
                            if any(e.startswith(_tm + ':') and ('K%d ' % n) in e for e in _cc_errors)})
            print(f"[t30] {_tm}: 契约声明必需 {_nums} vs payload SetOn 比对完成, 缺失={_miss}")
        print(f"[t30] 契约来源: {os.path.basename(contract_path)} rev={contract.get('revision')} "
              f"| 判据: {CONTRACT_RULE_NOTE}")
''').replace('\n', nl) + t[cj:]

    out = t.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    open(TARGET, 'wb').write(out)
    print('PATCHED(v3) %s\n  before=%s (%d B)\n  after =%s (%d B)\n  crlf=%d'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw),
             hashlib.sha256(out).hexdigest(), len(out), out.count(b'\r\n')))


if __name__ == '__main__':
    main()
