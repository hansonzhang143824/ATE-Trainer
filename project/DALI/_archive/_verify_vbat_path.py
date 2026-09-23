"""Verify shortest path from FPVIe0 (CH0) to VBAT in the DALI relay matrix."""
import re
from collections import defaultdict, deque

NETLIST = r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\DALI_Net.NET"

with open(NETLIST, encoding="utf-8", errors="ignore") as f:
    text = f.read()

# ---- Parse nets (same as gen_paths.py) ----
nets = {}
cn, cc, inn, d = None, [], False, 0
for line in text.split("\n"):
    m = re.match(r'^\s*\(Net\s+(.+)$', line)
    if m and not inn:
        cn = m.group(1).strip().strip('"')
        if cn.startswith("(rename)"):
            rm = re.match(r'\(rename\s+("[^"]*")\s*', line)
            if rm:
                cn = rm.group(1).strip('"')
        cc, inn, d = [], True, 1
        continue
    if inn:
        for c in line:
            if c == "(": d += 1
            elif c == ")": d -= 1
        for pin, inst in re.findall(r'\(PortRef\s+&(\d+)\s+\(InstanceRef\s+(\S+)\)\)', line):
            cc.append((inst, int(pin)))
        if d <= 0:
            if cn: nets[cn] = cc
            cn, cc, inn, d = None, [], False, 0

source_ports, dut_ports = set(), set()
for m in re.finditer(r'\(port\s+(?:\(rename\s+("[^"]+")\s*("[^"]*")\)|(\S+))\s+\(direction\s+(OUTPUT|INOUT|INPUT)\)\)', text):
    name = (m.group(1) or m.group(3)).strip('"')
    direction = m.group(4)
    if name and name not in ("UNDEFINED", ""):
        if direction == "OUTPUT": dut_ports.add(name)
        elif direction == "INOUT": source_ports.add(name)

# ---- Relay type map (same as gen_paths.py) ----
rp = defaultdict(set)
for n, conns in nets.items():
    for inst, pin in conns:
        if re.match(r"^K\d+_", inst):
            rp[inst].add(pin)
relay_type_map = {}
for inst, pins in rp.items():
    if max(pins) >= 5: relay_type_map[inst] = "G6K"
    elif max(pins) == 2: relay_type_map[inst] = "MOS2"
    else: relay_type_map[inst] = "MOS"

def rtrans(inst, pin, seton, relay_type_map):
    rt = relay_type_map.get(inst, "?")
    if rt == "G6K":
        t = {3: [4], 4: [3], 6: [5], 5: [6]} if seton else {2: [3], 3: [2], 7: [6], 6: [7]}
    elif rt == "MOS2":
        t = {1: [2], 2: [1]} if seton else {}
    elif rt == "MOS":
        t = {3: [4], 4: [3]} if seton else {}
    else:
        t = {}
    return [(tp, seton) for tp in t.get(pin, [])]

# instance pin -> nets
ipn = defaultdict(lambda: defaultdict(list))
for n, conns in nets.items():
    for inst, pin in conns:
        ipn[inst][pin].append(n)

COIL = {"G6K": {1, 8}, "MOS": {1, 2}, "MOS2": set()}

# ---- CBIT G6K override (same as gen_paths.py) ----
G6K_CBIT = [
    "K3_BUSL_VBUS","K4_DRVH1","K7_BUSH_VBAT","K8_PD3","K17_BUSL_VAC","K18_VAC3","K19_VAC2","K20_AMUX",
    "K29_BUSL_VCC","K30_BUSH_ACDRV","K31_VMCU","K32_BUSL_SCL","K33_VAC_WL","K35_BUSH_KLV","K36_PGND_WL",
    "K37_KLV2","K42_AMP_PS","K43_BST2","K48_AMP_REF","K49_ACM_SW2","K50_FOVI_SW2","K51_BUSL_LG","K52_LG2",
    "K58_BUSH_VDM","K59_SDA","K60_BUSL_VCP","K61_SW","K64_HG1","K76_ACM_BST","K83_BUSH_PMID","K84_HG2",
    "K88_KELVIN0","K90_PC0_Force","K91_PC0_Sense","K93_AGND2PGND","K95_PC6","K97_Qpoint","K98_PB3",
    "K99_BUSL_PB5","K100_PC4","K102_PC3","K105_CC2","K107_PB1","K109_BUSL_PB0","K110_BST","K112_PC5",
    "K114_BUSL_PA5","K115_PB2","K117_PB6","K119_PB4","K121_PD2","K123_BUSL_PB5","K124_nRST","K125_U34_PS",
    "K126_V1P5_CAP","K132_KELVIN1","K134_PC1_Force","K135_PC1_Sense","K154_BUSH_AMUX","K155_FOVI_PGND",
    "K157_COMP","K0_VCC_Cap","K2_BUF","K5_VBUS_Cap","K13_VBAT_Cap","K21_VAC_Cap","K44_Cap_SW2_BST2",
    "K45_Cap_SW1_BST1","K57_CAP_BST_SW","K74_GAIN1_SEL","K75_GAIN2_SEL","K82_R_CS","K85_CAP_PMID",
    "K87_KELVIN0","K89_KELVIN0","K87_KELVIN0","K89_KELVIN0","K131_KELVIN1","K133_KELVIN1",
    "K141_QTMU_BUSA","K142_QTMU_BUSB","K151_NC_GND",
]
CBIT_RELAY_TYPE = {}
for name in G6K_CBIT:
    CBIT_RELAY_TYPE[name] = "G6K"

def get_cbit_relay_type(inst_name):
    base = re.sub(r"_S\d+(S\d+)?$", "", inst_name)
    return CBIT_RELAY_TYPE.get(base)

for inst in list(relay_type_map.keys()):
    if get_cbit_relay_type(inst) == "G6K":
        relay_type_map[inst] = "G6K"

def short_name(inst):
    return re.sub(r"_S\d+(S\d+)?$", "", inst)

def bfs_shortest(src, target, constraints=True):
    """BFS; returns shortest path as list of (relay, state) or None."""
    if src not in nets:
        return None
    q = deque()
    visited = set()
    q.append((src, [], set()))
    visited.add((src, frozenset()))
    best = None
    while q:
        net, path, visited_relays = q.popleft()
        depth = len(visited_relays)
        if best and depth >= best[0]:
            continue
        if net == target and path:
            best = (depth, list(path))
            continue
        for inst, pin in nets.get(net, []):
            if not re.match(r"^K\d+_", inst):
                continue
            rn = int(re.match(r"K(\d+)_", inst).group(1))
            if rn in visited_relays:
                continue
            rt = relay_type_map.get(inst, "?")
            if pin in COIL.get(rt, set()):
                continue
            for seton in [False, True]:
                for tp, needs_seton in rtrans(inst, pin, seton, relay_type_map):
                    if tp in COIL.get(rt, set()):
                        continue
                    for onet in ipn[inst].get(tp, []):
                        if onet == net:
                            continue
                        state = "ON" if needs_seton else "NC"
                        step = (short_name(inst), rn, state, pin, tp, net, onet)
                        nv = visited_relays | {rn}
                        k = (onet, frozenset(nv))
                        if k not in visited:
                            visited.add(k)
                            q.append((onet, path + [step], nv))
    return best

def fmt(path):
    return " -> ".join(f"{r}(Relay-{s})" for r, _rn, s, _p, _t, _f, _t2 in path)


def all_paths(src, target, max_depth=7):
    results = []
    def dfs(net, path, visited_relays):
        if net == target and path:
            results.append(list(path)); return
        if len(visited_relays) >= max_depth:
            return
        for inst, pin in nets.get(net, []):
            if not re.match(r"^K\d+_", inst): continue
            rn = int(re.match(r"K(\d+)_", inst).group(1))
            if rn in visited_relays: continue
            rt = relay_type_map.get(inst, "?")
            if pin in COIL.get(rt, set()): continue
            for seton in [False, True]:
                for tp, needs_seton in rtrans(inst, pin, seton, relay_type_map):
                    if tp in COIL.get(rt, set()): continue
                    for onet in ipn[inst].get(tp, []):
                        if onet == net: continue
                        state = "ON" if needs_seton else "NC"
                        step = (short_name(inst), rn, state, net, onet)
                        dfs(onet, path + [step], visited_relays | {rn})
    dfs(src, [], set())
    seen, uniq = set(), []
    for p in results:
        key = tuple((r, s) for r, _rn, s, _f, _t in p)
        if key not in seen:
            seen.add(key); uniq.append(p)
    uniq.sort(key=len)
    return uniq


if __name__ == "__main__":
    # ---------- Trace CH0 (FPVIe0) FH0 -> VBAT_F, SH0 -> VBAT_S ----------
    print("=== S1_FPVIe_FH0 -> VBAT_F_S1 ===")
    r = bfs_shortest("S1_FPVIe_FH0", "VBAT_F_S1")
    print("hops:", r[0] if r else None)
    print(fmt(r[1]) if r else "NO PATH")
    print()
    print("=== S1_FPVIe_SH0 -> VBAT_S_S1 ===")
    r = bfs_shortest("S1_FPVIe_SH0", "VBAT_S_S1")
    print("hops:", r[0] if r else None)
    print(fmt(r[1]) if r else "NO PATH")
    print()

    # ---------- Compare: CH1 direct, QVM direct ----------
    print("=== S1_FPVIe_FH1 -> VBAT_F_S1 (CH1 reference) ===")
    r = bfs_shortest("S1_FPVIe_FH1", "VBAT_F_S1")
    print("hops:", r[0] if r else None)
    print(fmt(r[1]) if r else "NO PATH")
    print()
    print("=== S1_FPVIe_SH1 -> VBAT_S_S1 (CH1 reference) ===")
    r = bfs_shortest("S1_FPVIe_SH1", "VBAT_S_S1")
    print("hops:", r[0] if r else None)
    print(fmt(r[1]) if r else "NO PATH")
    print()
    print("=== S8_QVM_CH0+ -> VBAT_S_S1 (QVM reference, SH side) ===")
    r = bfs_shortest("S8_QVM_CH0+", "VBAT_S_S1")
    print("hops:", r[0] if r else None)
    print(fmt(r[1]) if r else "NO PATH")
    print()

    # ---------- Enumerate ALL simple paths FH0 -> VBAT_F ----------
    print("=== All simple paths S1_FPVIe_FH0 -> VBAT_F_S1 (depth<=7) ===")
    paths = all_paths("S1_FPVIe_FH0", "VBAT_F_S1", 7)
    for p in paths:
        print(f"len={len(p)}: " + " -> ".join(f"{r}(Relay-{s})" for r, _rn, s, _f, _t in p))
    print(f"total unique paths: {len(paths)}")
    print()

    # ---------- Enumerate ALL simple paths SH0 -> VBAT_S ----------
    print("=== All simple paths S1_FPVIe_SH0 -> VBAT_S_S1 (depth<=7) ===")
    paths = all_paths("S1_FPVIe_SH0", "VBAT_S_S1", 7)
    for p in paths:
        print(f"len={len(p)}: " + " -> ".join(f"{r}(Relay-{s})" for r, _rn, s, _f, _t in p))
    print(f"total unique paths: {len(paths)}")

