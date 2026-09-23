# -*- coding: utf-8 -*-
"""t30 patcher v2 (可重复执行) — 断言改为只比对**契约声明必需的闭合集合**。

实测教训（v1 之错，已撤回）:
  契约为每个 PIN 枚举了**通往它的所有可能路线**（`pinRouteTable[BST]` 给出 7 条路线，
  含 CH0 High=[46,48,76] / CH1 Low=[109,110] / QTMUe=[141,46,48,76] …）。若把**枚举**的并集
  当作"必需闭合集合"，则 TM601 会因闭不了 K136..K146 等**未被选中的路线**而被大面积误报
  ⇒ 违反 t30 的"阴性对照不得新增红"。故 v2 **只**用契约中**被显式声明为必需/预算**的两个集合：
    ① tmDeltas.<TM>.relaySet                         （该 TM 的资源预算闭合集合）
    ② aliasResolution[a].resolution.closedRelayNumbers，a ∈ tmDeltas.<TM>.aliasesUsed
       或 <TM> 以独立 token 出现在该别名 usedByTm 中
    （`pinRouteTable` 仍被读取并在输出中**引用为来源 locator**，但不参与判定）
  另: 可选 --check-extra —— SetOn 中出现不在 ①∪②∪角色继电器 中的继电器即红（默认关闭，
      待 K109 是否必需的裁定；由 --tm-alias 参数化，无需改代码）。
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')
START = '\n# =====================================================================\n# t30: '
END_MARK = "\n\ndef main() -> int:"


def block_for(nl):
    return r'''
# =====================================================================
# t30: "SetOn 集合 vs 契约声明闭合集合" 断言（门禁补盲）
# ---------------------------------------------------------------------
# 盲区根因（实测）: 本脚本原先 **完全不读契约** —— setup-contract / aliasResolution /
#   needsClosed / relaySet / K109 / K110 命中数均为 0 ⇒ 只校验"序列 + K57 电容"，
#   因此"**契约要求闭合的继电器没闭**"在结构上不可见（12 门全绿却漏 K110）。
# 判据（可复用，不硬编码本 run 的任何继电器号）: 对每个目标函数 TM，取契约**声明必需**的两个集合
#     ① tmDeltas.<TM>.relaySet                            —— 该 TM 的资源预算闭合集合
#     ② aliasResolution[a].resolution.closedRelayNumbers  —— a ∈ tmDeltas.<TM>.aliasesUsed，
#        或 <TM> 以独立 token 出现在该别名的 usedByTm 中（避免 TM600 被 TM6000 前缀误匹配）
#   + ③ 外部别名声明 --tm-alias <TM>=<a1>,<a2>（修补 tmDeltas.aliasesUsed 漏登记；参数化，无需改代码）
#   **不**使用 tmDeltas.<TM>.pinRouteTable 的并集作判据: 它是"通往每个 PIN 的**全部可能路线**"的
#   枚举（实测 pinRouteTable[BST] 列出 7 条路线，含 CH0 High=[46,48,76]、QTMUe=[141,46,48,76] 等），
#   并入判定会把**未被选中的路线**也当成必需 ⇒ 大面积误报（违反阴性对照）。它仅用作来源 locator。
# 缺失项 → errors[] ⇒ exit 1（与既有 FAIL 同一出口）⇒ run_gates.ps1 的 exit!=0 ⇒ **NEW-RED**（非 warn）。
# 实测（本 run）: 当时据 relaySet 判"TM600 缺 109/110、TM601 缺 86"。
#   ⚠️ **该口径已撤**（t42/t43 终局：109/110 属 ch18 路线、**本不该闭**）：
#   0 命中是对的，不是缺口。部署态真实缺件 = BST 侧 **48/76**（真因·活危害：源被改道 SW1_F/SW2_F）。
#   本行保留为"当时口径"的留痕，现口径见 t33-revision-attribution.md §1.3 与 build-report.json 的 attributionThreeStates。
# =====================================================================

CONTRACT_RULE_NOTE = ("setup-contract.json tmDeltas.<TM>.relaySet / "
                      "aliasResolution[*].resolution.closedRelayNumbers "
                      "(route enumerations in tmDeltas.<TM>.pinRouteTable are used as locators only)")


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


def _pin_route_note(contract, base, num):
    """给失败信息附上"该继电器在契约路由枚举中的出现处"（纯 locator，不参与判定）。"""
    d = (contract.get('tmDeltas') or {}).get(base) or {}
    for pin, routes in (d.get('pinRouteTable') or {}).items():
        if not isinstance(routes, dict):
            continue
        for route, rv in routes.items():
            if isinstance(rv, dict) and num in _nums_of_relay_entry(rv.get('needsClosed')):
                return f"pinRouteTable[{pin}][{route}] L{rv.get('line')}"
    return None


def _contract_required_for_tm(contract, tm, extra_aliases=None):
    """{num: 来源描述}; 契约未登记该 TM → None。"""
    base = None
    for k in (contract.get('tmDeltas') or {}):
        if tm == k or tm.startswith(str(k) + '_'):
            base = k
            break
    if base is None:
        return None, None
    d = contract['tmDeltas'][base]
    exp = {}
    for n in sorted(_nums_of_relay_entry(d.get('relaySet'))):
        exp.setdefault(n, 'tmDeltas.%s.relaySet' % base)

    idx = {}
    for e in (contract.get('aliasResolution') or []):
        a = str(e.get('alias', ''))
        nums = _nums_of_relay_entry((e.get('resolution') or {}).get('closedRelayNumbers'))
        users = set()
        for x in (e.get('usedByTm') or []):
            users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
        idx[a] = (nums, users)
    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        for n in sorted(idx.get(a, (set(), set()))[0]):
            exp.setdefault(n, 'aliasResolution[%s].resolution.closedRelayNumbers '
                              '(declared by tmDeltas.%s.aliasesUsed)' % (a, base))
    for a, (nums, users) in idx.items():
        if base in users:
            for n in sorted(nums):
                exp.setdefault(n, 'aliasResolution[%s].resolution.closedRelayNumbers '
                                  '(usedByTm lists %s)' % (a, base))
    for a in (extra_aliases or []):
        for n in sorted(idx.get(a, (set(), set()))[0]):
            exp.setdefault(n, 'aliasResolution[%s].resolution.closedRelayNumbers '
                              '(--tm-alias override)' % a)
    return exp, base


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


def check_contract_closures(src_text, contract, extra_alias_cfg=None, check_extra=False):
    """契约声明必需集合 ⊆ payload SetOn 集合；缺失 → errors[]（供 main 走致命通道）。"""
    errors, checked = [], {}
    payload = _numbers_from_payload(src_text)
    for tm, data in sorted(payload.items()):
        exp, base = _contract_required_for_tm(contract, tm, (extra_alias_cfg or {}).get(tm))
        if not exp:
            continue
        checked[tm] = sorted(exp)
        for n in sorted(set(exp) - data['nums']):
            line = min(data['lines'].values()) if data['lines'] else 0
            note = _pin_route_note(contract, base, n)
            errors.append(
                "%s: 契约声明必需的继电器 K%d **未出现在 cbite.SetOn 中** (契约来源: %s%s; "
                "payload locator: test.cpp:%d; 该函数实际闭合=%s)"
                % (tm, n, exp[n], (' | 路由枚举处: ' + note) if note else '', line,
                   sorted(data['names'])))
        if check_extra:
            for n in sorted(data['nums'] - set(exp)):
                if re.match(r'^K\d+_', ''):
                    pass
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
    crlf = t.count('\r\n') > 0
    nl = '\r\n' if crlf else '\n'
    block = block_for(nl).replace('\r\n', '\n').replace('\n', nl)

    start_anchor = nl + '# =====================================================================' + nl + '# t30: '
    end_anchor = nl + nl + 'def main() -> int:'
    has_old = start_anchor in t and end_anchor in t

    if '--verify-only' in sys.argv:
        print('  crlf=%s' % crlf)
        print('  旧 t30 块存在(可替换): %s' % has_old)
        print('  main 锚点: %d ; errors 锚点: %d'
              % (t.count(end_anchor), t.count('    errors: list[str] = []' + nl)))
        return
    if not has_old:
        raise SystemExit('ERROR: 找不到 t30 块 (需先跑 v1 或已回滚)')

    i = t.index(start_anchor)
    j = t.index(end_anchor, i)
    t = t[:i] + block + t[j:]

    # 重写 main 内接线（把 v1 的接线整体换成 v2）
    call_start = '    # ---- t30: 契约闭合集合断言（致命通道: 与既有 FAIL 同一出口）----'
    call_end = '| 判据: {CONTRACT_RULE_NOTE}")' + nl
    if call_start in t:
        ci = t.index(call_start)
        cj = t.index(call_end, ci) + len(call_end)
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
            text, contract, _extra_alias, check_extra=('--check-extra' in args))
        errors.extend(_cc_errors)
        for _tm, _nums in sorted(_cc_checked.items()):
            _miss = sorted({int(x.split('K')[-1].split(' ')[0])
                            for x in _cc_errors if x.startswith(_tm + ':')})
            print(f"[t30] {_tm}: 契约声明必需 {len(_nums)} 个 K 号 (共 {len(_nums)}) vs payload "
                  f"SetOn 比对完成, 缺失={_miss}")
        print(f"[t30] 契约来源: {os.path.basename(contract_path)} rev={contract.get('revision')} "
              f"| 判据: {CONTRACT_RULE_NOTE}")
''').replace('\n', nl) + t[cj:]

    out = t.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    open(TARGET, 'wb').write(out)
    print('PATCHED(v2) %s\n  before=%s (%d B)\n  after =%s (%d B)\n  bom=%s crlf=%d'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw),
             hashlib.sha256(out).hexdigest(), len(out), bom, out.count(b'\r\n')))


if __name__ == '__main__':
    main()
