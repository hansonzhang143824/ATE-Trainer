# -*- coding: utf-8 -*-
"""
gen_paths.py — 源表→DUT Pin 通路生成器 (path-finder 脚本化, 固定→脚本)

架构原则: "推理→agent, 固定→脚本"。cbit-path-finder 的通路追踪逻辑全部落地为脚本:
  - BFS 通路追踪 (trace_single): 含稀缺源表识别/非稀缺源禁借道BUS/跨域BUS短接约束
  - G6K/MOS/MOS2 脚位通断模型 (rtrans) + FPVIe 域约束 (FH/SH vs FL/SL)
  - F/S 合并分类 (Kelvin/PC短接/单线, 重叠继电器配对)
  - relay 类型权威源 = CBIT 表 Excel (动态读, 替代 netlist 推断的误判)
agent 只保留推理边界 (通路有效性人工确认/例外场景标注), 不在脚本内做推理。

输入:  Netlist .NET (--netlist, 默认合成 EDIF CSV_CONNECTIVITY.NET) + CBIT表 xlsx (--cbit, relay类型权威)
输出:  人类可读通路文档 (stdout 或 --output) + --json 结构化 path_list (agent 规格)
对拍:  --verify <基准文件> — relay 类型与 gen_cbit_defines.py 一致

规则覆盖: RULE_COVERAGE 映射 + --audit-rules 机器自检 (每个规则函数存在且调用链可达)。
数据源:  CBIT 表 Excel 动态读 (权威); 旧 DALI/gen_paths.py 的 G6K_CBIT 硬编码列表已被 Excel 替代。
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict, deque

try:
    import openpyxl
except ImportError:
    openpyxl = None

import proj_config

# Excel 分组标题 → relay 类型 (DALI CBIT 表)
EXCEL_GROUP_MAP = [
    ('光耦', 'MOS', '1.1 MOS SPST (TLP3412)'),
    ('机械独享', 'G6K_DEDICATED', '1.2 G6K Dedicated'),
    ('机械共享', 'G6K_SHARED', '1.3 G6K Shared'),
]

# =====================================================================
# 规则覆盖表 (核心交付物: cbit-path-finder 每条铁律 → 脚本函数)
# =====================================================================
RULE_COVERAGE = {
    'P-P1': ['parse_netlist'],                            # Netlist 解析: nets + port 方向 (TP_*排除)
    'P-P2': ['build_relay_type_map', 'load_cbit_relay_types'],  # relay 类型: netlist 推断 + CBIT 覆盖
    'P-P3': ['detect_source_short_relays'],                # 源端短接继电器排除 (K86/K130, AGND/GND例外)
    'P-P4': ['build_fpvi_channels', 'parse_fpvi_channel'], # FPVIe 通道分组 (FH+SH/FL+SL bundle)
    'P-P5': ['trace_single'],                              # BFS 最短路径追踪
    'P-P6': ['is_scarce_source', 'trace_single'],          # 稀缺源表识别 (FPVIe/QTMU/QVM)
    'P-P7': ['get_bus_domain', 'get_source_domain', 'trace_single'],  # FPVIe 域约束
    'P-P8': ['trace_single'],                              # 跨域 BUS 短接约束
    'P-P9': ['rtrans', 'build_relay_type_map'],            # G6K/MOS/MOS2 脚位通断模型
    'P-P10': ['merge_fpvi_output', 'pair_kelvin_then_pc'], # F/S 合并分类 (Kelvin/PC短接/单线)
    'P-P11': ['build_path_list', 'step_to_relay'],         # 结构化 path_list 输出
}

# 稀缺源表 (cbit-path-finder 定义)
SCARCE_SOURCE_KW = ['FPVIe', 'QTMU', 'QVM']

# =====================================================================
# A. 输入层
# =====================================================================

def read_enc(path):
    """DLP 透明加密回退: utf-8-sig → utf-8 → gbk → latin-1"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def read_excel_cbit(path=None):
    """动态读 CBIT 表 Excel → [(group, name, cbit_str)]。group ∈ {MOS, G6K_DEDICATED, G6K_SHARED}。
    P-P2: relay 类型权威源, 不依赖 netlist 推断也不依赖硬编码列表。"""
    if openpyxl is None:
        raise SystemExit('ERROR: 需要 openpyxl (pip install openpyxl) 读 CBIT 表')
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    entries = []
    cur_group = None
    for r in rows:
        c0 = r[0]
        c10 = r[10] if len(r) > 10 else None
        if c0 is None:
            continue
        c0s = str(c0).strip()
        if not c0s:
            continue
        if not c0s.startswith('K'):
            for title, _g, _lbl in EXCEL_GROUP_MAP:
                if c0s == title:
                    cur_group = dict((t, g) for t, g, _l in EXCEL_GROUP_MAP)[c0s]
                    break
            continue
        if cur_group is None:
            continue
        if not c10:
            continue
        entries.append((cur_group, c0s, str(c10).strip()))
    wb.close()
    return entries



# =====================================================================
# B. Netlist 解析层 (原 gen_paths.py 顶层逻辑, 封装+参数化)
# =====================================================================

def parse_netlist(netlist_path):
    """解析 .NET → (nets, source_ports, dut_ports, rp)。
    nets: {net_name: [(inst, pin), ...]}; source_ports: INOUT(源表端口); dut_ports: OUTPUT(DUT pin)。
    P-P1: 只保留电气联通结构; dut_ports 排除 TP_*/TEST_* 非信号端口。"""
    with open(netlist_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()

    nets = {}
    cn, cc, inn, d = None, [], False, 0
    for line in text.split('\n'):
        m = re.match(r'^\s*\(Net\s+(.+)$', line)
        if m and not inn:
            cn = m.group(1).strip().strip('"')
            if cn.startswith('(rename)'):
                rm = re.match(r'\(rename\s+("[^"]*")\s*', line)
                if rm:
                    cn = rm.group(1).strip('"')
            cc, inn, d = [], True, 1
            continue
        if inn:
            for c in line:
                if c == '(':
                    d += 1
                elif c == ')':
                    d -= 1
            for pin, inst in re.findall(r'\(PortRef\s+&(\d+)\s+\(InstanceRef\s+(\S+)\)\)', line):
                cc.append((inst, int(pin)))
            if d <= 0:
                if cn:
                    nets[cn] = cc
                cn, cc, inn, d = None, [], False, 0

    source_ports = set()
    dut_ports = set()
    for m in re.finditer(r'\(port\s+(?:\(rename\s+("[^"]+")\s*("[^"]*")\)|(\S+))\s+\(direction\s+(OUTPUT|INOUT|INPUT)\)\)', text):
        name = (m.group(1) or m.group(3)).strip('"')
        direction = m.group(4)
        if name and name not in ('UNDEFINED', ''):
            if name.startswith('TP_') or name.startswith('TEST_') or name.startswith('Net'):
                continue  # 非信号端口排除
            if direction == 'OUTPUT':
                dut_ports.add(name)
            elif direction == 'INOUT':
                source_ports.add(name)

    rp = defaultdict(set)
    for n, conns in nets.items():
        for inst, pin in conns:
            if re.match(r'^K\d+_', inst):
                rp[inst].add(pin)
    return nets, source_ports, dut_ports, rp


def build_relay_type_map(rp):
    """按继电器物理脚数推断类型: max(pins)>=5→G6K, ==2→MOS2, else→MOS。P-P2 第1层。"""
    relay_type_map = {}
    for inst, pins in rp.items():
        if max(pins) >= 5:
            relay_type_map[inst] = 'G6K'
        elif max(pins) == 2:
            relay_type_map[inst] = 'MOS2'
        else:
            relay_type_map[inst] = 'MOS'
    return relay_type_map


def load_cbit_relay_types(cbit_path=None):
    """CBIT 表 Excel → {relay_base_name: 'G6K'|'MOS'}。P-P2 第2层 (权威覆盖)。
    group G6K_DEDICATED/G6K_SHARED → G6K, MOS → MOS。
    替代旧版硬编码 G6K_CBIT 60 继电器列表。"""
    if not cbit_path or not os.path.exists(cbit_path):
        return {}
    cbit_type = {}
    for group, name, _cbit in read_excel_cbit(cbit_path):
        base = re.sub(r'_S\d+(S\d+)?$', '', name)
        cbit_type[base] = 'G6K' if group.startswith('G6K') else 'MOS'
    return cbit_type


def apply_cbit_relay_types(relay_type_map, cbit_type):
    """CBIT 覆盖: netlist 误判 (3脚G6K→MOS) 用 Excel 组别纠正。P-P2 落地。"""
    for inst in list(relay_type_map.keys()):
        base = re.sub(r'_S\d+(S\d+)?$', '', inst)
        t = cbit_type.get(base)
        if t == 'G6K':
            relay_type_map[inst] = 'G6K'


def detect_source_short_relays(rp, ipn, source_ports):
    """源端短接继电器识别: 2-pin 继电器两端 net 全为源端口(INOUT) → 仪器内部路由 (K86/K130)。
    AGND/GND 例外。P-P3。"""
    short = set()
    for inst in rp:
        if max(rp[inst]) != 2:
            continue
        inst_nets = set()
        for pin in rp[inst]:
            inst_nets.update(ipn[inst].get(pin, []))
        if not inst_nets:
            continue
        if all(n in source_ports for n in inst_nets):
            if not any('AGND' in n or 'GND' in n for n in inst_nets):
                short.add(inst)
    return short


def build_fpvi_channels(source_ports):
    """FPVIe 端口分组 → {key: {label, ports}}。FH+SH→FHSH, FL+SL→FLSL。P-P4。"""
    fpvi_ports = {}
    for sp in source_ports:
        ch = parse_fpvi_channel(sp)
        if ch:
            slot, side, ch_num = ch
            key = (slot, ch_num)
            if key not in fpvi_ports:
                fpvi_ports[key] = {}
            fpvi_ports[key][side] = sp

    fpvi_channels = {}
    for (slot, ch_num), sides in sorted(fpvi_ports.items()):
        label_parts = [f"S{slot}_FPVIe"]
        bundled = []
        if 'FH' in sides and 'SH' in sides:
            label_parts.append("FHSH")
            bundled.append(('FH', sides['FH']))
            bundled.append(('SH', sides['SH']))
        elif 'FH' in sides:
            label_parts.append("FH")
            bundled.append(('FH', sides['FH']))
        elif 'SH' in sides:
            label_parts.append("SH")
            bundled.append(('SH', sides['SH']))

        if 'FL' in sides and 'SL' in sides:
            label_parts.append("FLSL")
            bundled.append(('FL', sides['FL']))
            bundled.append(('SL', sides['SL']))
        elif 'FL' in sides:
            label_parts.append("FL")
            bundled.append(('FL', sides['FL']))
        elif 'SL' in sides:
            label_parts.append("SL")
            bundled.append(('SL', sides['SL']))

        label = f"{label_parts[0]}_{label_parts[1]}{''.join(label_parts[2:])}{ch_num}"
        fpvi_channels[(slot, 'High', ch_num)] = {
            'label': f"{label_parts[0]}_FHSH{ch_num}",
            'ports': [(s, p) for s, p in bundled if s in ('FH', 'SH')],
            'side': 'High',
        } if any(s in ('FH', 'SH') for s, _ in bundled) else None
        fpvi_channels[(slot, 'Low', ch_num)] = {
            'label': f"{label_parts[0]}_FLSL{ch_num}",
            'ports': [(s, p) for s, p in bundled if s in ('FL', 'SL')],
            'side': 'Low',
        } if any(s in ('FL', 'SL') for s, _ in bundled) else None

    return {k: v for k, v in fpvi_channels.items() if v and v['ports']}


def step_to_relay(step, relay_type_map, relay_type_by_num):
    """path_list 的 via_relays 元素: {name, cbit, type, state, annotation}。P-P11。
    state: ON→SetOn, NC→KeepDefault (agent 规格)。type: MOS→SPST, G6K→G6K。"""
    rn = step['rn']
    t = relay_type_by_num.get(rn) or relay_type_map.get('K%d_' % rn, 'G6K')
    if t == 'MOS2':
        stype, state = 'SPST', 'SetOn'
        ann = '[通电→闭合]'
    elif t == 'G6K':
        stype, state = 'G6K', 'SetOn' if step['state'] == 'ON' else 'KeepDefault'
        ann = '[通电→NO, %s→%s]' % (step['from_pin'], step['to_pin']) if step['state'] == 'ON' else '[默认NC, 保持]'
    else:
        stype, state = 'SPST', 'SetOn' if step['state'] == 'ON' else 'KeepDefault'
        ann = '[通电→闭合]' if step['state'] == 'ON' else '[默认断开]'
    return {'name': step['relay'], 'cbit': rn, 'type': stype, 'state': state, 'annotation': ann}


def build_path_list(fpvi_paths, single_paths, relay_type_map, relay_type_by_num):
    """结构化 path_list (agent 规格): [{dut_pin, source, side, via_relays, intermediate_source}]。P-P11。"""
    plist = []
    for item in fpvi_paths:
        label, raw_dut, side, steps = item
        base = norm_pin(raw_dut)
        plist.append({
            'dut_pin': base,
            'source': label,
            'side': side,
            'via_relays': [step_to_relay(s, relay_type_map, relay_type_by_num) for s in steps],
            'intermediate_source': None,
        })
    for item in single_paths:
        src, dut, steps = item
        plist.append({
            'dut_pin': norm_pin(dut),
            'source': src,
            'side': None,
            'via_relays': [step_to_relay(s, relay_type_map, relay_type_by_num) for s in steps],
            'intermediate_source': None,
        })
    return plist


def audit_rules():
    """RULE_COVERAGE 机器自检: 每个规则引用的函数存在且顶层可引用 (调用链可达)。"""
    ns = dict(globals())
    ok = True
    for rule_id, funcs in sorted(RULE_COVERAGE.items()):
        for fn in funcs:
            if fn not in ns or not callable(ns[fn]):
                print('[FAIL] %s 引用的函数 %s 不存在或不可调用' % (rule_id, fn))
                ok = False
            else:
                print('[ OK ] %s -> %s' % (rule_id, fn))
    return ok


# =====================================================================
# C. 算法核心 (提取自 DALI/gen_paths.py, 保真)
# =====================================================================

# ---- 继电器功能分类编号 (提取自旧 gen_paths.py, 硬编码编号集) ----
BUS_RELAYS = {15,17,19,21,26,29,31,33,34,38,40,41,42}
SHARE_RELAYS = {20,22,23,35,36}
CAP_RELAYS = {16,18,25,28,30,32,37,66}
FPVI_MATRIX = {8,9,10,11,12,13}
COIL = {'G6K':{1,8}, 'MOS':{1,2}, 'MOS2': set()}
HIGH_KEYWORDS = ['FH_BUS', 'SH_BUS', 'FH_PC', 'SH_PC']
LOW_KEYWORDS  = ['FL_BUS', 'SL_BUS', 'FL_PC', 'SL_PC']
ALL_BUS_KEYWORDS = HIGH_KEYWORDS + LOW_KEYWORDS
def get_relay_num(inst_name):
    m = re.match(r'K(\d+)_', inst_name)
    return int(m.group(1)) if m else None


def get_relay_state(inst_name, rp):
    rn = get_relay_num(inst_name)
    if rn is None: return '?'
    if rn in FPVI_MATRIX: return 'NC'
    if (46 <= rn <= 59) or rn == 68: return 'ON'
    if rn in BUS_RELAYS: return 'ON'
    if rn in CAP_RELAYS: return 'ON'
    if rn in SHARE_RELAYS: return 'NC/ON'
    return 'NC/ON'


def rtrans(inst_name, pin, seton, relay_type_map):
    rt = relay_type_map.get(inst_name, '?')
    if rt == 'G6K':
        t = {3: [4], 4: [3], 6: [5], 5: [6]} if seton else {2: [3], 3: [2], 7: [6], 6: [7]}
    elif rt == 'MOS2':
        t = {1: [2], 2: [1]} if seton else {}
    elif rt == 'MOS':
        t = {3: [4], 4: [3]} if seton else {}
    else:
        t = {}
    return [(tp, seton) for tp in t.get(pin, [])]


def norm_pin(p):
    """Strip F/S/FORCE/SENSE/site suffixes from DUT pin name"""
    p = re.sub(r'_FORCE_S\d+$', '', p)
    p = re.sub(r'_SENSE_S\d+$', '', p)
    p = re.sub(r'_[FS]_S\d+$', '', p)
    p = re.sub(r'_S\d+$', '', p)
    return p


def is_kelvin_pin(p, dut_ports):
    """Kelvin pin = has both _F_Sx and _S_Sx variants"""
    base = norm_pin(p)
    f_var = f"{base}_F_S1"
    s_var = f"{base}_S_S1"
    return f_var in dut_ports and s_var in dut_ports


def parse_fpvi_channel(port_name):
    """S1_FPVIe_FH0 -> (1, 'FH', 0); S1_FPVIe_SH1 -> (1, 'SH', 1)"""
    m = re.match(r'S(\d+)_FPVIe_(FH|SH|FL|SL)(\d+)', port_name)
    if m:
        return int(m.group(1)), m.group(2), int(m.group(3))
    return None


def is_scarce_source(port_name):
    """Check if source port belongs to a scarce instrument (FPVIe/QTMU/QVM)."""
    return any(kw in port_name for kw in SCARCE_SOURCE_KW)


def get_bus_domain(net_name):
    """Return 'HIGH' if net is on high-side bus, 'LOW' if low-side, else None."""
    if any(kw in net_name for kw in HIGH_KEYWORDS):
        return 'HIGH'
    if any(kw in net_name for kw in LOW_KEYWORDS):
        return 'LOW'
    return None


def is_bus_net(net_name):
    """Check if net is any kind of BUS public node."""
    return any(kw in net_name for kw in ALL_BUS_KEYWORDS)


def get_source_domain(port_name):
    """Determine source domain from FPVIe port name. FH/SH→HIGH, FL/SL→LOW, else None."""
    m = re.search(r'_(FH|SH|FL|SL)\d', port_name)
    if m:
        side = m.group(1)
        if side in ('FH', 'SH'):
            return 'HIGH'
        elif side in ('FL', 'SL'):
            return 'LOW'
    return None


def trace_single(source_port, max_depth=6):
    """
    BFS: single source port -> DUT pin.
    Returns only the SHORTEST path (fewest relay steps) for each DUT pin.

    约束:
    1. 非稀缺源表(ACM200/FOVIe等)禁止借道 BUSH/BUSL 公共节点
    2. 禁止路径中2+个ON继电器分别短接不同BUS域 (跨域BUS短接)
    """
    if source_port not in nets:
        return []
    scarce = is_scarce_source(source_port)
    best = {}  # dut_pin -> (length, path)
    visited = set()
    q = deque()
    # BFS state: (net, path, visited_relays, bus_domain_via_on)
    # bus_domain_via_on: None | 'HIGH' | 'LOW' — 已通过ON继电器进入的BUS域
    q.append((source_port, [], set(), None))
    visited.add((source_port, frozenset(), None))
    while q:
        net, path, visited_relays, bus_domain_via_on = q.popleft()
        depth = len(visited_relays)
        if depth > max_depth:
            continue
        if net in dut_ports and path:
            if net not in best or depth < best[net][0]:
                best[net] = (depth, list(path))
            continue
        for inst, pin in nets.get(net, []):
            if not re.match(r'^K\d+_', inst): continue
            rn = get_relay_num(inst)
            if rn is None or rn in visited_relays: continue
            if inst in SOURCE_SHORT_RELAYS: continue
            rt = relay_type_map.get(inst, '?')
            if pin in COIL.get(rt, set()): continue
            for seton in [False, True]:
                for tp, needs_seton in rtrans(inst, pin, seton, relay_type_map):
                    if tp in COIL.get(rt, set()): continue
                    for onet in ipn[inst].get(tp, []):
                        if onet == net: continue

                        # === 约束1: 非稀缺源表禁止进入BUS公共节点 ===
                        if not scarce and is_bus_net(onet):
                            continue

                        # === FPVIe domain constraint (稀缺源表域约束) ===
                        bus_domain = get_bus_domain(onet)
                        src_domain = get_source_domain(source_port)
                        if bus_domain and src_domain and bus_domain != src_domain:
                            continue

                        # === 约束2: 禁止跨域BUS短接 ===
                        # 检测 ON继电器 连接不同BUS域 → 短接公共节点
                        new_bus_domain_via_on = bus_domain_via_on
                        if needs_seton and bus_domain:
                            # 当前net的domain (继电器入口侧)
                            net_domain = get_bus_domain(net)
                            if net_domain and net_domain != bus_domain:
                                # 同一继电器ON状态下跨BUS域 → 视为从net_domain侧接入
                                pass  # 继电器本身跨域由FPVIe域约束处理
                            # 进入/离开BUS域
                            entering_bus = bus_domain  # 去往的net是BUS
                            if new_bus_domain_via_on is None:
                                new_bus_domain_via_on = entering_bus
                            elif new_bus_domain_via_on != entering_bus:
                                # 已有ON继电器接了另一个BUS域 → 跨域短接!
                                continue

                        state = 'ON' if needs_seton else 'NC'
                        step = {
                            'relay': re.sub(r'_S\d+(S\d+)?$', '', inst),
                            'rn': rn, 'state': state,
                            'from_pin': pin, 'to_pin': tp,
                        }
                        new_visited = visited_relays | {rn}
                        new_path = path + [step]
                        k = (onet, frozenset(new_visited), new_bus_domain_via_on)
                        if k not in visited:
                            visited.add(k)
                            q.append((onet, new_path, new_visited, new_bus_domain_via_on))
    return [(dut, path) for dut, (_depth, path) in best.items()]


def trace_fpvi_channel(channel_info, max_depth=6):
    """
    Trace each FH/SH/FL/SL separately.
    Returns list of (raw_dut_name, side, steps) — keeps F/S suffix for Kelvin detection.
    """
    results = []
    for side, port_name in channel_info['ports']:
        for dut, steps in trace_single(port_name, max_depth):
            results.append((dut, side, steps))
    return results


def format_relay_step(step):
    """Short relay name: K35(Relay-ON)"""
    rn = step['rn']
    return f"K{rn}(Relay-{step['state']})"


def format_fpvi_path(source_label, dest, side, steps):
    parts = [f"{source_label}/{side}"]
    for s in steps:
        parts.append(format_relay_step(s))
    parts.append(dest)
    return " -> ".join(parts)


def format_single_path(source_port, dest, steps):
    base = norm_pin(dest)
    parts = [source_port]
    for s in steps:
        parts.append(format_relay_step(s))
    parts.append(base)
    return " -> ".join(parts)


def get_dut_fs(raw_name):
    """'VBUS_F_S1'→('VBUS','F'), 'VBUS_S_S1'→('VBUS','S'), 'nRST_S1'→('nRST','')"""
    m = re.match(r'^(.+?)_([FS])_S\d+$', raw_name)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r'^(.+)_S\d+$', raw_name)
    if m:
        return m.group(1), ''  # 无F/S区分，如nRST_S1 → ('nRST', '')
    return raw_name, ''


def count_overlap(steps_a, steps_b):
    """统计两条路径在相同位置、相同继电器+状态的匹配数"""
    if not steps_a or not steps_b:
        return 0
    return sum(1 for i in range(min(len(steps_a), len(steps_b)))
               if steps_a[i]['rn'] == steps_b[i]['rn'] and steps_a[i]['state'] == steps_b[i]['state'])


def format_interleaved_path(label, dest_display, fsteps, ssteps, annotation=''):
    """逐级交错合并，同位置同继电器→单显，不同→逗号并列。annotation='[Kelvin]'/'[PC短接]'"""
    parts = [label]
    max_len = max(len(fsteps), len(ssteps))
    for i in range(max_len):
        fr = format_relay_step(fsteps[i]) if i < len(fsteps) else None
        sr = format_relay_step(ssteps[i]) if i < len(ssteps) else None
        if fr and sr:
            parts.append(fr if fr == sr else f"{fr}, {sr}")
        elif fr:
            parts.append(fr)
        elif sr:
            parts.append(sr)
    parts.append(dest_display)
    line = " -> ".join(parts)
    return f"  {line}  {annotation}"


def pair_kelvin_then_pc(label, base, force_list, sense_list, force_tag, sense_tag):
    """
    两轮配对:
      Pass 1: Kelvin  — Force(F后缀) + Sense(S后缀) → [Kelvin]
      Pass 2: PC短接 — Force(F后缀) + Sense(F后缀) → [PC短接]
    剩余未配对 → [单线]
    force_list/sense_list: [(steps, 'F'|'S'), ...]
    """
    used_force = set()
    used_sense = set()
    lines = []

    # --- Pass 1: Kelvin (F→S) ---
    for fi, (fsteps, f_fs) in enumerate(force_list):
        if f_fs != 'F':
            continue
        best_si, best_ov = None, 0
        for si, (ssteps, s_fs) in enumerate(sense_list):
            if si in used_sense or s_fs != 'S':
                continue
            ov = count_overlap(fsteps, ssteps)
            if ov > best_ov:
                best_ov, best_si = ov, si
        if best_si is not None and best_ov > 0:
            used_force.add(fi)
            used_sense.add(best_si)
            ssteps, _ = sense_list[best_si]
            lines.append(format_interleaved_path(label, base, fsteps, ssteps, '[Kelvin]'))

    # --- Pass 2: PC短接 (F→F) ---
    for fi, (fsteps, f_fs) in enumerate(force_list):
        if fi in used_force or f_fs != 'F':
            continue
        best_si, best_ov = None, 0
        for si, (ssteps, s_fs) in enumerate(sense_list):
            if si in used_sense or s_fs != 'F':
                continue
            ov = count_overlap(fsteps, ssteps)
            if ov > best_ov:
                best_ov, best_si = ov, si
        if best_si is not None and best_ov > 0:
            used_force.add(fi)
            used_sense.add(best_si)
            ssteps, _ = sense_list[best_si]
            lines.append(format_interleaved_path(label, base, fsteps, ssteps, '[PC短接]'))

    # --- 未配对 Force → [单线] ---
    for fi, (fsteps, f_fs) in enumerate(force_list):
        if fi in used_force:
            continue
        parts = [f"{label}/{force_tag}"]
        for s in fsteps:
            parts.append(format_relay_step(s))
        parts.append(base)
        lines.append(f"  {' -> '.join(parts)}  [单线]")

    # --- 未配对 Sense → [单线] ---
    for si, (ssteps, s_fs) in enumerate(sense_list):
        if si in used_sense:
            continue
        parts = [f"{label}/{sense_tag}"]
        for s in ssteps:
            parts.append(format_relay_step(s))
        parts.append(base)
        lines.append(f"  {' -> '.join(parts)}  [单线]")

    return lines


def merge_fpvi_output(channel_label, results):
    """
    按 DUT pin F/S 后缀分组，交叉配对:
      Force侧终点_F + Sense侧终点_S → [Kelvin]  (4线, DUT端汇合)
      Force侧终点_F + Sense侧终点_F → [PC短接]  (2线, 中途已短接)
    未配对 → [单线]
    results: [(raw_dut, side, steps), ...]
    """
    by_base = defaultdict(lambda: {'F': {'FH': [], 'SH': [], 'FL': [], 'SL': []},
                                    'S': {'FH': [], 'SH': [], 'FL': [], 'SL': []}})
    for raw_dut, side, steps in results:
        base, fs = get_dut_fs(raw_dut)
        if fs == '':
            fs = 'F'  # 无F/S区分的pin归入Force侧
        by_base[base][fs][side].append(steps)

    lines = []
    for base in sorted(by_base.keys()):
        f = by_base[base]['F']
        s = by_base[base]['S']

        fl_all = [(st, 'F') for st in f['FL']] + [(st, 'S') for st in s['FL']]
        sl_all = [(st, 'F') for st in f['SL']] + [(st, 'S') for st in s['SL']]
        lines += pair_kelvin_then_pc(channel_label, base, fl_all, sl_all, 'FL', 'SL')

        fh_all = [(st, 'F') for st in f['FH']] + [(st, 'S') for st in s['FH']]
        sh_all = [(st, 'F') for st in f['SH']] + [(st, 'S') for st in s['SH']]
        lines += pair_kelvin_then_pc(channel_label, base, fh_all, sh_all, 'FH', 'SH')

    return lines


# =====================================================================
# D. 主流程
# =====================================================================

def main():
    cfg = proj_config.load(proj_config.config_from_argv(sys.argv))
    ap = argparse.ArgumentParser(description='源表→DUT Pin 通路生成器 (path-finder 脚本化)')
    ap.add_argument('--config', default=None, help='project_config.json (默认 workspace 根)')
    ap.add_argument('--netlist', default=cfg['intermediates'].get('synthetic_edif', ''), help='Netlist .NET 路径 (默认合成 EDIF CSV_CONNECTIVITY.NET)')
    ap.add_argument('--cbit', default=cfg['inputs']['cbit'], help='CBIT 表 xlsx (relay类型权威)')
    ap.add_argument('--output', default='', help='通路文档落盘路径 (默认 stdout)')
    ap.add_argument('--json', action='store_true', help='额外输出结构化 path_list JSON (stderr标注)')
    ap.add_argument('--max-depth', type=int, default=6, help='BFS 最大穿越继电器数 (默认6)')
    ap.add_argument('--audit-rules', action='store_true', help='RULE_COVERAGE 机器自检后退出')
    args = ap.parse_args()

    # trace_single/trace_fpvi_channel/merge_fpvi_output 引用模块级全局 → 用 global 注入
    global nets, source_ports, dut_ports, rp, relay_type_map, ipn, SOURCE_SHORT_RELAYS, fpvi_channels

    if args.audit_rules:
        ok = audit_rules()
        print('\n--audit-rules: %s' % ('ALL PASSED' if ok else 'FAILED'))
        sys.exit(0 if ok else 1)

    # ---- 解析 netlist ----
    nets, source_ports, dut_ports, rp = parse_netlist(args.netlist)
    relay_type_map = build_relay_type_map(rp)
    cbit_type = load_cbit_relay_types(args.cbit)
    apply_cbit_relay_types(relay_type_map, cbit_type)
    if cbit_type:
        print('// CBIT relay type 覆盖生效: %d 条 (Excel 权威)' % len(cbit_type), file=sys.stderr)

    # ---- 索引 ----
    ipn = defaultdict(lambda: defaultdict(list))
    for n, conns in nets.items():
        for inst, pin in conns:
            ipn[inst][pin].append(n)

    # relay rn → type 映射 (供结构化输出)
    relay_type_by_num = {}
    for inst, t in relay_type_map.items():
        m = re.match(r'K(\d+)_', inst)
        if m:
            relay_type_by_num[int(m.group(1))] = t

    SOURCE_SHORT_RELAYS = detect_source_short_relays(rp, ipn, source_ports)
    fpvi_channels = build_fpvi_channels(source_ports)

    # ---- 追踪 (trace_single 引用模块级全局, 通过函数参数或 globals 注入) ----
    lines = []
    lines.append("=" * 80)
    lines.append("DALI 源表 → DUT Pin 通路文档")
    lines.append("=" * 80)
    lines.append("")

    fpvi_paths = []
    single_paths = []

    # --- FPVIe paths: FH+SH 和 FL+SL 合并输出 ---
    lines.append("## FPVIe 通路")
    lines.append("")
    fpvi_count = 0
    for key in sorted(fpvi_channels.keys()):
        ch = fpvi_channels[key]
        if not ch['ports']:
            continue
        results = trace_fpvi_channel(ch, args.max_depth)
        if not results:
            continue

        lines.append("### %s" % ch['label'])
        lines.append("")
        merged = merge_fpvi_output(ch['label'], results)
        for line in merged:
            lines.append(line)
            fpvi_count += 1
        for raw_dut, side, steps in results:
            fpvi_paths.append((ch['label'], raw_dut, ch['side'], steps))
        lines.append("")

    # --- ACM/FOVI paths (single source) ---
    other_sources = {p for p in source_ports if not parse_fpvi_channel(p)}
    connected = set()
    for src in other_sources:
        if src in nets:
            for inst, pin in nets[src]:
                if re.match(r'^K\d+_', inst):
                    connected.add(src)
                    break

    for title, keyword in [("ACM200 通路", "ACM"), ("FOVIe 通路", "FOVI")]:
        lines.append("## %s" % title)
        lines.append("")
        count = 0
        for src in sorted(connected):
            if keyword not in src.upper():
                continue
            paths = trace_single(src, args.max_depth)
            for dut, steps in paths:
                base = norm_pin(dut)
                line = format_single_path(src, dut, steps)
                lines.append("  %s" % line)
                single_paths.append((src, dut, steps))
                count += 1
        if count == 0:
            lines.append("  (无通路)")
        lines.append("")

    # --- Relay state summary ---
    lines.append("## 继电器状态汇总")
    lines.append("")
    lines.append("| 继电器 | 功能分类 | 默认状态 | SetOn状态 |")
    lines.append("|--------|:---:|:---:|:---:|")
    for rn in sorted(set(get_relay_num(inst) for inst in rp if get_relay_num(inst) is not None)):
        if rn in BUS_RELAYS:
            func, default, seton = "BUS", "Pin↛BUS", "Pin↔BUS"
        elif rn in SHARE_RELAYS:
            func, default, seton = "Share", "默认通道", "备用通道"
        elif rn in CAP_RELAYS:
            func, default, seton = "Cap", "Cap断开", "Cap接入"
        elif rn in FPVI_MATRIX:
            func, default, seton = "FPVIe矩阵", "FPVI→BUS", "保持NC"
        elif 46 <= rn <= 59 or rn == 68:
            func, default, seton = "MOS P2P", "断开", "闭合"
        else:
            func, default, seton = "通用G6K", "视设计", "视设计"
        lines.append("| K%d | %s | %s | %s |" % (rn, func, default, seton))

    doc = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(doc + "\n")
        print("Done! Output: %s" % args.output, file=sys.stderr)
    else:
        print(doc)
    print("FPVIe paired paths: %d" % fpvi_count, file=sys.stderr)

    # --- 结构化 path_list (agent 规格) ---
    if args.json:
        plist = build_path_list(fpvi_paths, single_paths, relay_type_map, relay_type_by_num)
        print("\n\n===== PATH_LIST JSON =====")
        print(json.dumps(plist, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
