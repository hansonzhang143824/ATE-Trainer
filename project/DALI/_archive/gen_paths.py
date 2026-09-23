"""
gen_paths.py — 生成源表→DUT Pin 通路文档
FPVIe: FH+SH 配对追踪, FL+SL 配对追踪
输出格式: S1_FPVIe_FHSH0 -> K87(Relay-NC),K88(Relay-NC) -> K58(Relay-ON) -> SDA
"""
import re
from collections import defaultdict, deque

# ===== CONFIG =====
NETLIST = r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\SCH-DALI.NET"
OUTPUT = r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\paths.txt"

BUS_RELAYS = {15,17,19,21,26,29,31,33,34,38,40,41,42}
SHARE_RELAYS = {20,22,23,35,36}
CAP_RELAYS = {16,18,25,28,30,32,37,66}
FPVI_MATRIX = {8,9,10,11,12,13}
COIL = {'G6K':{1,8}, 'MOS':{1,2}, 'MOS2': set()}

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

# ===== PARSE NETLIST =====
with open(NETLIST, encoding="utf-8", errors="ignore") as f:
    text = f.read()

nets = {}
cn, cc, inn, d = None, [], False, 0
for line in text.split('\n'):
    m = re.match(r'^\s*\(Net\s+(.+)$', line)
    if m and not inn:
        cn = m.group(1).strip().strip('"')
        if cn.startswith('(rename)'):
            rm = re.match(r'\(rename\s+("[^"]*")\s*', line)
            if rm: cn = rm.group(1).strip('"')
        cc, inn, d = [], True, 1
        continue
    if inn:
        for c in line:
            if c == '(': d += 1
            elif c == ')': d -= 1
        for pin, inst in re.findall(r'\(PortRef\s+&(\d+)\s+\(InstanceRef\s+(\S+)\)\)', line):
            cc.append((inst, int(pin)))
        if d <= 0:
            if cn: nets[cn] = cc
            cn, cc, inn, d = None, [], False, 0

source_ports = set()
dut_ports = set()
for m in re.finditer(r'\(port\s+(?:\(rename\s+("[^"]+")\s*("[^"]*")\)|(\S+))\s+\(direction\s+(OUTPUT|INOUT|INPUT)\)\)', text):
    name = (m.group(1) or m.group(3)).strip('"')
    direction = m.group(4)
    if name and name not in ('UNDEFINED', ''):
        if direction == 'OUTPUT': dut_ports.add(name)
        elif direction == 'INOUT': source_ports.add(name)

rp = defaultdict(set)
for n, conns in nets.items():
    for inst, pin in conns:
        if re.match(r'^K\d+_', inst):
            rp[inst].add(pin)

relay_type_map = {}
for inst, pins in rp.items():
    if max(pins) >= 5:
        relay_type_map[inst] = 'G6K'
    elif max(pins) == 2:
        relay_type_map[inst] = 'MOS2'
    else:
        relay_type_map[inst] = 'MOS'

# === CBIT-based relay type override ===
# K87/K89/K131/K133 are G6K but only expose 3 pins in netlist → misdetected as MOS
# Override with CBIT table data: G6K_DEDICATED and G6K_SHARED → G6K, MOS → MOS
CBIT_RELAY_TYPE = {}  # relay_base_name → 'G6K' or 'MOS'
# Data from CBIT表-DALI.xlsx (group determines type)
G6K_CBIT = [
    'K3_BUSL_VBUS','K4_DRVH1','K7_BUSH_VBAT','K8_PD3','K17_BUSL_VAC','K18_VAC3','K19_VAC2','K20_AMUX',
    'K29_BUSL_VCC','K30_BUSH_ACDRV','K31_VMCU','K32_BUSL_SCL','K33_VAC_WL','K35_BUSH_KLV','K36_PGND_WL',
    'K37_KLV2','K42_AMP_PS','K43_BST2','K48_AMP_REF','K49_ACM_SW2','K50_FOVI_SW2','K51_BUSL_LG','K52_LG2',
    'K58_BUSH_VDM','K59_SDA','K60_BUSL_VCP','K61_SW','K64_HG1','K76_ACM_BST','K83_BUSH_PMID','K84_HG2',
    'K88_KELVIN0','K90_PC0_Force','K91_PC0_Sense','K93_AGND2PGND','K95_PC6','K97_Qpoint','K98_PB3',
    'K99_BUSL_PB5','K100_PC4','K102_PC3','K105_CC2','K107_PB1','K109_BUSL_PB0','K110_BST','K112_PC5',
    'K114_BUSL_PA5','K115_PB2','K117_PB6','K119_PB4','K121_PD2','K123_BUSL_PB5','K124_nRST','K125_U34_PS',
    'K126_V1P5_CAP','K132_KELVIN1','K134_PC1_Force','K135_PC1_Sense','K154_BUSH_AMUX','K155_FOVI_PGND',
    'K157_COMP','K0_VCC_Cap','K2_BUF','K5_VBUS_Cap','K13_VBAT_Cap','K21_VAC_Cap','K44_Cap_SW2_BST2',
    'K45_Cap_SW1_BST1','K57_CAP_BST_SW','K74_GAIN1_SEL','K75_GAIN2_SEL','K82_R_CS','K85_CAP_PMID',
    'K87_KELVIN0','K89_KELVIN0','K87_KELVIN0','K89_KELVIN0','K131_KELVIN1','K133_KELVIN1',
    'K141_QTMU_BUSA','K142_QTMU_BUSB','K151_NC_GND',
]
for name in G6K_CBIT:
    CBIT_RELAY_TYPE[name] = 'G6K'
# Override via base name matching
def get_cbit_relay_type(inst_name):
    """Look up relay type from CBIT table by matching base name."""
    base = re.sub(r'_S\d+(S\d+)?$', '', inst_name)
    if base in CBIT_RELAY_TYPE:
        return CBIT_RELAY_TYPE[base]
    return None

for inst in list(relay_type_map.keys()):
    cbit_type = get_cbit_relay_type(inst)
    if cbit_type == 'G6K':
        relay_type_map[inst] = 'G6K'  # override

ipn = defaultdict(lambda: defaultdict(list))
for n, conns in nets.items():
    for inst, pin in conns:
        ipn[inst][pin].append(n)

# === Source-side shorting relays (skip in FPVIe BFS) ===
# Rule: 2-pin relays where ALL connected nets are source ports (INOUT)
# are internal instrument routing (e.g. K86: FH↔SH, K130: FH↔SH)
# Exception: AGND/GND Force↔Sense shorting is allowed
SOURCE_SHORT_RELAYS = set()
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
            SOURCE_SHORT_RELAYS.add(inst)

# ===== Group FPVIe ports by channel =====
def parse_fpvi_channel(port_name):
    """S1_FPVIe_FH0 -> (1, 'FH', 0); S1_FPVIe_SH1 -> (1, 'SH', 1)"""
    m = re.match(r'S(\d+)_FPVIe_(FH|SH|FL|SL)(\d+)', port_name)
    if m:
        return int(m.group(1)), m.group(2), int(m.group(3))
    return None

fpvi_ports = {}
for sp in source_ports:
    ch = parse_fpvi_channel(sp)
    if ch:
        slot, side, ch_num = ch
        key = (slot, ch_num)
        if key not in fpvi_ports:
            fpvi_ports[key] = {}
        fpvi_ports[key][side] = sp

# Build FPVIe channel bundles: FH+SH -> 'FHSH', FL+SL -> 'FLSL'
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
        'ports': [(s, p) for s, p in bundled if s in ('FH', 'SH')]
    } if any(s in ('FH', 'SH') for s, _ in bundled) else None
    fpvi_channels[(slot, 'Low', ch_num)] = {
        'label': f"{label_parts[0]}_FLSL{ch_num}",
        'ports': [(s, p) for s, p in bundled if s in ('FL', 'SL')]
    } if any(s in ('FL', 'SL') for s, _ in bundled) else None

fpvi_channels = {k: v for k, v in fpvi_channels.items() if v and v['ports']}

# ===== Bus domain helpers =====
HIGH_KEYWORDS = ['FH_BUS', 'SH_BUS', 'FH_PC', 'SH_PC']
LOW_KEYWORDS  = ['FL_BUS', 'SL_BUS', 'FL_PC', 'SL_PC']
ALL_BUS_KEYWORDS = HIGH_KEYWORDS + LOW_KEYWORDS
SCARCE_SOURCE_KW = ['FPVIe', 'QTMU', 'QVM']  # 稀缺源表 — 可使用BUS公共节点

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

# ===== Trace single port -> DUT =====
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

# ===== Trace FPVIe channel -> DUT (simplified: show FH/SH separately) =====
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

# ===== Format =====
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

# ===== FS Merge (Force+Sense 逐级交错合并，区分Kelvin/PC短接) =====
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

# ===== MAIN =====
lines = []
lines.append("=" * 80)
lines.append("DALI 源表 → DUT Pin 通路文档")
lines.append("=" * 80)
lines.append("")

# --- FPVIe paths: FH+SH 和 FL+SL 合并输出 ---
lines.append("## FPVIe 通路")
lines.append("")
fpvi_count = 0
for key in sorted(fpvi_channels.keys()):
    ch = fpvi_channels[key]
    if not ch['ports']: continue
    results = trace_fpvi_channel(ch)
    if not results: continue

    lines.append(f"### {ch['label']}")
    lines.append("")
    merged = merge_fpvi_output(ch['label'], results)
    for line in merged:
        lines.append(line)
        fpvi_count += 1
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
    lines.append(f"## {title}")
    lines.append("")
    count = 0
    for src in sorted(connected):
        if keyword not in src.upper(): continue
        paths = trace_single(src)
        for dut, steps in paths:
            base = norm_pin(dut)
            line = format_single_path(src, dut, steps)
            lines.append(f"  {line}")
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
    if rn in BUS_RELAYS: func = "BUS"; default = "Pin↛BUS"; seton = "Pin↔BUS"
    elif rn in SHARE_RELAYS: func = "Share"; default = "默认通道"; seton = "备用通道"
    elif rn in CAP_RELAYS: func = "Cap"; default = "Cap断开"; seton = "Cap接入"
    elif rn in FPVI_MATRIX: func = "FPVIe矩阵"; default = "FPVI→BUS"; seton = "保持NC"
    elif 46 <= rn <= 59 or rn == 68: func = "MOS P2P"; default = "断开"; seton = "闭合"
    else: func = "通用G6K"; default = "视设计"; seton = "视设计"
    lines.append(f"| K{rn} | {func} | {default} | {seton} |")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Done! Output: {OUTPUT}")
print(f"FPVIe paired paths: {fpvi_count}")
