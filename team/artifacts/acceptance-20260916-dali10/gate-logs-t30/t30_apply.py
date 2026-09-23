# -*- coding: utf-8 -*-
"""t30 patcher — 在 verify_bst_sw_sequence.py 增加"SetOn 集合 vs 契约 needsClosed"断言。

设计（对应 t30 验收要点）：
  * 期望集合 **全部从冻结契约读取**，不硬编码任何本 run 的继电器号:
      needsClosed  = tmDeltas.<TM>.pinRouteTable[*][*].needsClosed        (逐路线)
      relaySet     = tmDeltas.<TM>.relaySet
      aliasClosed  = aliasResolution[a].resolution.closedRelayNumbers     (按 usedByTm / aliasesUsed 建 index)
      外部别名     = --tm-alias <TM>=<alias>[,<alias>]  (仅用于修补 tmDeltas.aliasesUsed 漏登记)
  * payload 的 SetOn 集合 = test.cpp 函数块内**所有** cbite.SetOn(...) 的 K 号/裸数字 (python 明文读取)
  * 缺失项 → errors[] → exit 1 (致命通道; 与既有 FAIL 同一出口) ⇒ run_gates.ps1 计为 NEW-RED
  * 可选 --check-extra: SetOn 中未在契约任何集合中声明的继电器 → errors[] (默认关闭, 待 K109 裁定)
  * 门禁零参数调用必须继续可用 (run_gates.ps1:82 不带参数)
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')

BLOCK = r'''

# =====================================================================
# t30: "SetOn 集合 vs 契约 needsClosed" 断言（门禁补盲）
# ---------------------------------------------------------------------
# 盲区根因（实测）: 本脚本原先 **完全不读契约** —— setup-contract / aliasResolution /
#   needsClosed / relaySet / K109 / K110 命中数均为 0 ⇒ 只校验"序列与 K57 电容"，
#   因此"**契约要求闭合的继电器没闭**"在结构上不可见（12 门全绿却漏 K110）。
# 判据（可复用，不硬编码本 run 的任何继电器号）:
#   对每个目标函数 TM，期望闭合集合 = 契约三源之并
#       ① tmDeltas.<TM>.pinRouteTable[*][*].needsClosed   （该 TM 每条被选通路的闭合集）
#       ② tmDeltas.<TM>.relaySet                          （该 TM 的资源预算集合）
#       ③ aliasResolution[a].resolution.closedRelayNumbers，其中 <TM> 以独立 token 出现在
#          该别名的 usedByTm 中（避免 "TM600" 被 "TM6000" 前缀误匹配）
#       + ④ 外部别名声明 --tm-alias <TM>=<a1>,<a2>（修补 tmDeltas.aliasesUsed 漏登记）
#   实测（本 run）: ③ 对 TM600 因 aliasesUsed 未登记 bst2sw 而**不生效**，但 ①② 已含 109/110
#   ⇒ 断言在"契约登记字段不全"时依然有效（这正是 t30 阳性对照成立的原因）。
# 缺失项 → errors[] ⇒ exit 1 ⇒ run_gates.ps1 的 exit!=0 ⇒ **NEW-RED**（非 warn）。
# =====================================================================

CONTRACT_RULE_NOTE = ("setup-contract.json tmDeltas.<TM>.pinRouteTable[*][*].needsClosed"
                      " / tmDeltas.<TM>.relaySet"
                      " / aliasResolution[*].resolution.closedRelayNumbers")


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
    root = cfg.get('_root') or ''
    base = os.path.join(root, 'team', 'artifacts')
    if os.path.isdir(base):
        cands = sorted(d for d in os.listdir(base) if d.startswith('acceptance-'))
        for d in reversed(cands):
            p = os.path.join(base, d, 'setup-contract.json')
            if os.path.isfile(p):
                return p
    return ''


def _numbers_from_payload(src_text):
    """{函数名: {"nums": set[int], "names": set[str], "lines": {name: lineno}}}

    payload 的 SetOn 集合 = 函数块内**所有** cbite.SetOn(...) 的参数
    （同时支持 K<num>_Name 与裸数字 126 两种写法）。
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
    """契约里的继电器表示可能是 int / "K110_ACM18_BST" / {"number":110,...} / [..] → 取数字集合。"""
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


def _alias_index(contract):
    """{alias: (nums, {TM base names from usedByTm})}"""
    idx = {}
    for e in (contract.get('aliasResolution') or []):
        a = str(e.get('alias', ''))
        nums = _nums_of_relay_entry((e.get('resolution') or {}).get('closedRelayNumbers'))
        users = set()
        for x in (e.get('usedByTm') or []):
            users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
        idx[a] = (nums, users)
    return idx


def _contract_relays_for_tm(contract, tm, alias_idx, extra_aliases=None):
    """返回 {num: 来源描述}；契约未登记该 TM → None。"""
    base = None
    for k in (contract.get('tmDeltas') or {}):
        if tm == k or tm.startswith(str(k) + '_'):
            base = k
            break
    if base is None:
        return None
    d = contract['tmDeltas'][base]
    exp = {}

    for pin, routes in (d.get('pinRouteTable') or {}).items():
        if not isinstance(routes, dict):
            continue
        for route, rv in routes.items():
            if isinstance(rv, dict) and rv.get('needsClosed'):
                for n in _nums_of_relay_entry(rv.get('needsClosed')):
                    exp.setdefault(n, 'tmDeltas.%s.pinRouteTable[%s][%s].needsClosed (SCH-Connect-Map L%s)'
                                   % (base, pin, route, rv.get('line')))
    for n in _nums_of_relay_entry(d.get('relaySet')):
        exp.setdefault(n, 'tmDeltas.%s.relaySet' % base)

    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        nums, _u = alias_idx.get(a, (set(), set()))
        for n in nums:
            exp.setdefault(n, 'aliasResolution[%s].resolution.closedRelayNumbers '
                              '(declared by tmDeltas.%s.aliasesUsed)' % (a, base))
    for a, (nums, users) in alias_idx.items():
        if base in users:
            for n in nums:
                exp.setdefault(n, 'aliasResolution[%s].resolution.closedRelayNumbers '
                                  '(usedByTm lists %s)' % (a, base))
    for a in (extra_aliases or []):
        nums, _u = alias_idx.get(a, (set(), set()))
        for n in nums:
            exp.setdefault(n, 'aliasResolution[%s].resolution.closedRelayNumbers '
                              '(--tm-alias override)' % a)
    return exp


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
    """契约期望闭合集合 ⊆ payload SetOn 集合；缺失 → errors[]（供 main 走致命通道）。"""
    errors = []
    payload = _numbers_from_payload(src_text)
    alias_idx = _alias_index(contract)
    checked = {}
    for tm, data in sorted(payload.items()):
        exp = _contract_relays_for_tm(contract, tm, alias_idx, (extra_alias_cfg or {}).get(tm))
        if not exp:
            continue
        checked[tm] = sorted(exp)
        for n in sorted(set(exp) - data['nums']):
            line = min(data['lines'].values()) if data['lines'] else 0
            errors.append(
                "%s: 契约要求闭合的继电器 K%d **未出现在 cbite.SetOn 中** (契约来源: %s; "
                "payload locator: test.cpp:%d; 该函数实际闭合=%s)"
                % (tm, n, exp[n], line, sorted(data['names'])))
    if check_extra:
        for tm, _exp in sorted(checked.items()):
            exp = _contract_relays_for_tm(contract, tm, alias_idx, (extra_alias_cfg or {}).get(tm))
            for n in sorted(payload[tm]['nums'] - set(exp)):
                errors.append("%s: cbite.SetOn 出现契约未声明的继电器 K%d "
                              "(payload locator: test.cpp:%d) —— --check-extra 已开启"
                              % (tm, n, min(payload[tm]['lines'].values()) if payload[tm]['lines'] else 0))
    return errors, checked


'''


def main():
    raw = open(TARGET, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    # 本文件为 CRLF（实测 crlf=298）⇒ 锚点与插入块统一用 CRLF，避免行尾混用
    crlf = t.count('\r\n') > 0
    nl = '\r\n' if crlf else '\n'
    block = BLOCK.replace('\r\n', '\n').replace('\n', nl)

    main_anchor = nl + 'def main() -> int:' + nl
    err_anchor = '    errors: list[str] = []' + nl

    if '--verify-only' in sys.argv:
        print('  crlf=%s → 使用行尾 %r' % (crlf, nl))
        print('  main 锚点命中 %d 次' % t.count(main_anchor))
        print('  errors 列表锚点命中 %d 次' % t.count(err_anchor))
        print('  已含 check_contract_closures: %s' % ('check_contract_closures' in t))
        return
    if 'check_contract_closures' in t:
        raise SystemExit('ERROR: 目标已含 check_contract_closures, 拒绝重复插入')
    if t.count(main_anchor) != 1:
        raise SystemExit('ERROR: main 锚点不唯一 (%d)' % t.count(main_anchor))
    if t.count(err_anchor) != 1:
        raise SystemExit('ERROR: errors 锚点不唯一 (%d)' % t.count(err_anchor))

    t = t.replace(main_anchor, block + main_anchor, 1)

    # ---- 接线: main 内解析契约路径与开关, 并把结果并入 errors (致命通道) ----
    new_call = ('''    errors: list[str] = []

    # ---- t30: 契约闭合集合断言（致命通道: 与既有 FAIL 同一出口）----
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
            _miss = len([e for e in _cc_errors if e.startswith(_tm + ':')])
            print(f"[t30] {_tm}: 契约期望闭合 {len(_nums)} 个 K 号 {_nums[:12]}"
                  f"{'...' if len(_nums) > 12 else ''} vs payload SetOn 比对完成 (缺失 {_miss})")
        print(f"[t30] 契约来源: {os.path.basename(contract_path)} rev={contract.get('revision')} "
              f"| 判据: {CONTRACT_RULE_NOTE}")
''').replace('\n', nl)
    t = t.replace(err_anchor, new_call, 1)

    out = t.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    open(TARGET, 'wb').write(out)
    print('PATCHED %s\n  before=%s (%d B)\n  after =%s (%d B)\n  bom=%s lf=%d crlf=%d'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw),
             hashlib.sha256(out).hexdigest(), len(out), bom,
             out.count(b'\n') - out.count(b'\r\n'), out.count(b'\r\n')))


if __name__ == '__main__':
    main()
