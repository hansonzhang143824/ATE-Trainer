#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_bst_sw_sequence.py — BST-SW 台阶黄金约束门 (生成后, R-BST-SW)。

目标函数不再硬编码, 从 meta (outputs.meta) 按 capAuthority.powered_pins 拓扑指纹派生:
  - HS (BOOST, PMID-SW): powered_pins 含 BST-SW/BST_SW  → BST 5V→10V 台阶
  - LS (BUCK, SW-PGND):  powered_pins 含 IPMID2SW/PMID-SW → BST=5V (禁 10V)
电流量程: max |iset| ≥ 1A → FPVIe_10A, 否则 FPVIe_2A
寄存器: LS → I2C 0x01, HS → I2C 0x02

规则源: rules-registry R-BST-SW (codex 黄金约束, TM607-609 根因)。
用法:
  python verify_bst_sw_sequence.py [--src <test.cpp>] [--config <json>] [--list]
判定: 任一 FAIL → exit 1; meta 无 BST-SW 目标 → 空 PASS (不误伤非 ZCD 项目)。
"""

from __future__ import annotations

import json
import os
import re
import sys

import proj_config
from gen_path_defines import read_enc


# ---- 契约常量（2026-09-13 修正两处与现网脱节的硬编码）----
#  · BST_SRC: 原写 "SW12_U1REF_BST_ACM"（已废弃）→ 现网用 "SW12_U1REF_BST_ACM"
#  · BST_CAP_RELAY: 原写 "K45_Cap_SW1_BST1"（SCH-Connect-Map L905 = Cap_SW1_BST1_S1,
#    那是 TRX 的 BST1/SW1 电容）→ BUBO 的 BST−SW 对电容是 L904 "Cap_SW_BST_S1" 需闭合 K57,
#    源码闭的也正是 K57_CAP_BST_SW。
#  改名/换继电器时只改这里; 若与源码脱节, main 里的 SRC 守卫会报出来（不会静默 0 命中）。
BST_SRC = "SW12_U1REF_BST_ACM"
BST_CAP_RELAY = "K57_CAP_BST_SW"


def iter_functions(text: str):
    """扫描 test.cpp → [{'name','block'}]（按函数体花括号配平切分）。"""
    out = []
    for m in re.finditer(r'DUT_API\s+int\s+(\w+)\s*\(short\s+funcindex', text):
        d, j = 0, m.start()
        while j < len(text):
            if text[j] == '{':
                d += 1
            elif text[j] == '}':
                d -= 1
                if d == 0:
                    break
            j += 1
        out.append({'name': m.group(1), 'block': text[m.start():j + 1]})
    return out


def _norm(s: str) -> str:
    """归一化 PIN 名: 大写 + 去非字母 (含 '-'/'_'/数字), 供拓扑指纹匹配。"""
    return re.sub(r'[^A-Z]', '', (s or '').upper())


def load_meta(cfg):
    """读 meta JSON → functions 列表; 缺失/坏文件返回 []。"""
    path = cfg.get('outputs', {}).get('meta', '')
    if not path or not os.path.isfile(path):
        return []
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            data = json.loads(raw.decode(enc))
            break
        except (UnicodeDecodeError, ValueError):
            continue
    else:
        return []
    return data.get('functions', [])


def derive_targets(functions):
    """R-BST-SW 适用对象 = **做电流斜坡的测试项**（Current Threshold / ZCD / OCP 家族）。

    2026-09-13 重写。原实现用 meta `capAuthority.powered_pins` 指纹, 三处失真:
      · `_norm` 把非字母全删（**含数字**）→ 'BST1_SW1' 归一成 'BSTSW' → 把 rampv 类的
        TM641/TM643/TM1205 **误判**为本家族目标（TM1205 还因此多出 1 条假 FAIL）;
      · 'PMIDSW' 在现网 powered_pins 里**无人匹配** → 真正的主目标 TM607(BUCK_LS) **被漏掉**;
      · 目标集合随 meta 漂移, 每加一个 TM 就可能多几条假 FAIL。

    新判据（**行为自证**, 不依赖 meta 字段名）:
      函数体内含 `rampi_capv(` → 电流斜坡 → 本家族。
      实测: TM607/608/609/640 均 rampi=1 / rampv=0;
            TM641/643/1205 均 rampi=0 / rampv>=2 → 正确排除。

    拓扑 topo 同样由代码自证（取该函数 SetOn 里的 FPVIe 高端继电器）:
      `K_FPVIH_TO_PGND` → 'LS'(BUCK, SW↔PGND); `K_FPVIH_TO_PMID` → 'HS'(BOOST, PMID↔SW)。
    两者都判不出 → 跳过并 WARN（**不猜**）。
    """
    targets = []
    for fn in functions:
        name = fn.get('name') or ''
        block = fn.get('block') or ''
        if not name or not re.search(r'\brampi_capv\s*\(', block):
            continue
        rm = re.search(r'\brampi_capv\s*\([^;]*?FPVIe_(2A|10A)', block)
        irange = 'FPVIe_%s' % rm.group(1) if rm else 'FPVIe_2A'
        seton = re.search(r'cbite\.SetOn\((.*?)\);', block, re.DOTALL)
        so = seton.group(1) if seton else ''
        if 'K_FPVIH_TO_PGND' in so:
            topo = 'LS'
        elif 'K_FPVIH_TO_PMID' in so:
            topo = 'HS'
        else:
            print('[warn] %s: 含 rampi_capv 但 SetOn 判不出 LS/HS 拓扑 → 跳过（不猜）' % name)
            continue
        targets.append((name, topo, irange))
    return targets


def find_function(text: str, name: str):
    """返回函数块文本; 未找到返回 None (不抛异常)。"""
    header = re.compile(r'\bDUT_API\s+int\s+' + re.escape(name) + r'\s*\(')
    match = header.search(text)
    if not match:
        return None
    brace = text.find('{', match.end())
    if brace < 0:
        return text[match.start():]
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == '{':
            depth += 1
        elif text[pos] == '}':
            depth -= 1
            if depth == 0:
                return text[match.start():pos + 1]
    return text[match.start():]


def ordered(block: str, tokens, label: str, errors) -> None:
    cursor = -1
    for token in tokens:
        position = block.find(token, cursor + 1)
        if position < 0:
            errors.append(f"{label}: missing sequence token {token}")
            return
        cursor = position


def require_exact_count(section: str, token: str, expected: int, label: str, errors) -> None:
    actual = section.count(token)
    if actual != expected:
        errors.append(f"{label}: expected {expected} occurrence(s) of {token}, found {actual}")


def check_ls(name: str, block: str, errors) -> None:
    """LS (BUCK, SW-PGND): BST=5V (禁 10V), I2C 0x01。"""
    ramp = block.find('test_method.rampi_capv')
    if ramp < 0:
        errors.append(f"{name}: missing test_method.rampi_capv")
        return
    power_on = block[:ramp]
    power_off = block[ramp:]
    ordered(
        block,
        [
            "FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A",
            "SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V",
            "PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V",
            "entertestmode();",
            "I2CWriteSameData(DEV_ADDR, 0x5A, 0x01)",
            "FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A",
            "test_method.rampi_capv",
        ],
        f"{name} power-on/measure", errors,
    )
    if "SW12_U1REF_BST_ACM.Set(FV, 10" in block:
        errors.append(f"{name}: LS topology SW=PGND=0 must use BST=5V, not 10V")
    require_exact_count(power_on, "FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A", 1, f"{name} power-on", errors)
    require_exact_count(power_on, "SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V", 1, f"{name} power-on", errors)
    require_exact_count(power_on, "PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V", 1, f"{name} power-on", errors)
    ordered(
        power_off,
        [
            "FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A",
            "FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A",
            "PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V",
            "SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V",
        ],
        f"{name} power-off", errors,
    )


def check_hs(name: str, irange: str, block: str, errors) -> None:
    """HS (BOOST, PMID-SW): BST 5V→10V 台阶, I2C 0x02。"""
    ramp = block.find('test_method.rampi_capv')
    if ramp < 0:
        errors.append(f"{name}: missing test_method.rampi_capv")
        return
    power_on = block[:ramp]
    power_off = block[ramp:]
    require_exact_count(power_on, f"FPVI0.Set(FV, 0, FPVIe_1V, {irange}", 1, f"{name} power-on", errors)
    require_exact_count(power_on, "SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V", 1, f"{name} power-on", errors)
    require_exact_count(power_on, "PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V", 1, f"{name} power-on", errors)
    require_exact_count(power_on, "SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_10V", 1, f"{name} power-on", errors)
    ordered(
        block,
        [
            f"FPVI0.Set(FV, 0, FPVIe_1V, {irange}",
            "SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V",
            "PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V",
            "SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_10V",
            "entertestmode();",
            "I2CWriteSameData(DEV_ADDR, 0x5A, 0x02)",
            f"FPVI0.Set(FI, 0, FPVIe_1V, {irange}",
            "test_method.rampi_capv",
        ],
        f"{name} power-on/measure", errors,
    )
    ordered(
        power_off,
        [
            f"FPVI0.Set(FI, 0, FPVIe_1V, {irange}",
            f"FPVI0.Set(FV, 0, FPVIe_1V, {irange}",
            "SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V",
            "PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V",
            "SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V",
        ],
        f"{name} power-off", errors,
    )
    require_exact_count(power_off, f"FPVI0.Set(FV, 0, FPVIe_1V, {irange}", 1, f"{name} power-off", errors)
    require_exact_count(power_off, "SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V", 1, f"{name} power-off", errors)
    require_exact_count(power_off, "PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON", 1, f"{name} power-off", errors)
    require_exact_count(power_off, "SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON", 1, f"{name} power-off", errors)



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

DEFAULT_TM_SCOPE = ["TM600_HS_RDSON", "TM601_LS_RDSON"]   # 本 run 实现的函数（--tm-scope 可覆盖）

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


def resolve_scope(args):
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


def check_contract_closures(src_text, contract, targets, extra_alias_cfg=None, check_extra=False,
                            scope=None):
    """契约声明必需集合 ⊆ payload SetOn 集合；缺失 → errors[]（致命通道）。

    scope: 参与判定的函数名列表；None ⇒ DEFAULT_TM_SCOPE（由 --tm-scope 参数化）。
    """
    errors, checked = [], {}
    payload = _numbers_from_payload(src_text)
    alias_idx = _alias_index(contract)
    # 作用范围 = 契约自身声明的使用方（不限于门禁内部 ZCD 家族列表 —— 否则会漏掉本缺陷的 TM600）
    if scope is None:
        scope = DEFAULT_TM_SCOPE
    for tm in scope:
        data = payload.get(tm)
        if data is None:
            continue
        exp, base, budget = expected_for_tm(contract, alias_idx, tm, (extra_alias_cfg or {}).get(tm))
        if not exp:
            continue
        missing = sorted(set(exp) - data['nums'])
        checked[tm] = {'expected': sorted(exp), 'missing': missing}
        for n in missing:
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




def main() -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    args = sys.argv[1:]
    cfg = proj_config.load(proj_config.config_from_argv(args))
    src = cfg["derived"]["test_cpp"]
    if '--src' in args:
        i = args.index('--src')
        if i + 1 < len(args):
            src = args[i + 1]

    if not os.path.exists(src):
        print(f'*** FAIL: 源文件不存在 {src}')
        return 1

    text, _enc = read_enc(src)
    targets = derive_targets(iter_functions(text))

    if '--list' in args:
        for name, topo, irange in targets:
            print(f"{name}\t{topo}\t{irange}")
        return 0

    if not targets:
        print("[scan] test.cpp 无 rampi_capv 电流斜坡测试项 (非 ZCD/OCP 家族), 空 PASS")
        return 0
    errors: list[str] = []

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
        _scope = resolve_scope(args)
        if '--list-scope' in args:
            print(f"[t30] 生效作用范围 = {_scope}")
        _cc_errors, _cc_checked = check_contract_closures(
            text, contract, targets, _extra_alias, check_extra=('--check-extra' in args),
            scope=_scope)
        errors.extend(_cc_errors)
        for _tm, _info in sorted(_cc_checked.items()):
            print(f"[t30] {_tm}: 契约声明必需 {_info['expected']} vs payload SetOn 比对完成, "
                  f"缺失={_info['missing']} (缺失数 {len(_info['missing'])})")
        print(f"[t30] 契约来源: {os.path.basename(contract_path)} rev={contract.get('revision')} "
              f"| 判据: {CONTRACT_RULE_NOTE}")


    src_seen = 0
    for name, topo, irange in targets:
        block = find_function(text, name)
        if block is None:
            errors.append(f"{name}: 函数不存在于 test.cpp")
            continue
        if BST_SRC in block:
            src_seen += 1
        seton = re.search(r"cbite\.SetOn\((.*?)\);", block, re.DOTALL)
        if seton is None or BST_CAP_RELAY not in seton.group(1):
            errors.append(f"{name}: missing BST-SW differential capacitor relay {BST_CAP_RELAY}"
                          f" (BUBO 的 BST-SW 对 = SCH-Connect-Map L904 Cap_SW_BST_S1 需闭合 K57;"
                          f" K45/K44 是 TRX 的 BST1/SW1、BST2/SW2, 属 rampv 线, 不适用本家族)")
        if topo == 'LS':
            check_ls(name, block, errors)
        else:
            check_hs(name, irange, block, errors)

    print(f"[scan] {src}")
    print("[contract] BST>=SW and 0<=BST-SW<=5V; operating target BST-SW=5V")
    print(f"[scan] targets={len(targets)} FAIL={len(errors)}")
    if src_seen == 0 and targets:
        errors.append("所有目标都搜不到 BST_SRC ⇒ 源表名疑似已改名（契约常量与源码脱节），请核对 scripts/verify_bst_sw_sequence.py 的 BST_SRC")

    if errors:
        print("\n*** FAIL (BST-SW GOLDEN SEQUENCE) ***")
        for error in errors:
            print("  - " + error)
        return 1
    print("\nBST-SW SEQUENCE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
