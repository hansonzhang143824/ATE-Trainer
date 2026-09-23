"""
V8: Shorted-pin aware. PA0+INT→PA0_INT, PA7+DMA→PA7_DMA, PC6+DMO→PC6_DMO.
Port without net → find signal net → merge names.
Direct 2-level index: BUS relay → L1 net → L2 relay → DUT signal net.
"""
import re
from collections import defaultdict

# ===== CBIT =====
RAW_CBIT = [
    ("K1_COMP_AMP","S34_CBIT1","MOS"),("K6_VBUS_LP","S34_CBIT6","MOS"),
    ("K9_COMP_SVLP1","S34_CBIT9","MOS"),("K10_COMP_SVLP2","S34_CBIT10","MOS"),
    ("K11_VBUS_SVLP","S34_CBIT11","MOS"),("K12_VBAT_SVLP","S34_CBIT12","MOS"),
    ("K14_VAC1_P2P","S34_CBIT14","MOS"),("K15_VAC2_P2P","S34_CBIT15","MOS"),
    ("K16_VAC3_P2P","S34_CBIT16","MOS"),
    ("K22_ACDRV1_F","S34_CBIT22","MOS"),("K22_ACDRV1_S","S34_CBIT22","MOS"),
    ("K23_ACDRV2_F","S34_CBIT23","MOS"),("K23_ACDRV2_S","S34_CBIT23","MOS"),
    ("K24_ACDRV3_F","S34_CBIT24","MOS"),("K24_ACDRV3_S","S34_CBIT24","MOS"),
    ("K25_VCC_F","S34_CBIT25","MOS"),("K25_VCC_S","S34_CBIT25","MOS"),
    ("K26_ACDRV1_P2P","S34_CBIT26","MOS"),("K27_ACDRV2_P2P","S34_CBIT27","MOS"),
    ("K28_ACDRV3_P2P","S34_CBIT28","MOS"),
    ("K34_SCL_PU","S34_CBIT34","MOS"),("K38_KLV1_2_short","S34_CBIT38","MOS"),
    ("K39_KLV1_P2P","S34_CBIT39","MOS"),("K40_KLV2_P2P","S34_CBIT40","MOS"),
    ("K41_BUS_FL_BST","S34_CBIT41","MOS"),("K41_BUS_SL_BST","S34_CBIT41","MOS"),
    ("K46_BUS_FH_SW1","S34_CBIT46","MOS"),("K46_BUS_SH_SW1","S34_CBIT46","MOS"),
    ("K47_BUS_FL_SW1","S34_CBIT47","MOS"),("K47_BUS_SL_SW1","S34_CBIT47","MOS"),
    ("K53_LG2_P2P","S34_CBIT53","MOS"),("K54_LG1_P2P","S34_CBIT54","MOS"),
    ("K55_HG2_P2P","S34_CBIT55","MOS"),("K56_HG1_P2P","S34_CBIT56","MOS"),
    ("K62_BUS_FH_QON","S34_CBIT62","MOS"),("K62_BUS_SH_QON","S34_CBIT62","MOS"),
    ("K63_SDA_PU","S34_CBIT63","MOS"),("K65_nQON_PU","S34_CBIT65","MOS"),
    ("K66_TMU_nQON","S34_CBIT66","MOS"),
    ("K68_VCP_F","S34_CBIT68","MOS"),("K69_PB5_F","S34_CBIT69","MOS"),
    ("K70_VAC_F","S34_CBIT70","MOS"),("K71_KLV_F","S34_CBIT71","MOS"),
    ("K72_PA5_F","S34_CBIT72","MOS"),("K73_VCN_F","S34_CBIT73","MOS"),
    ("K77_VAC_S","S34_CBIT77","MOS"),("K78_PB5_S","S34_CBIT78","MOS"),
    ("K79_KLV_S","S34_CBIT79","MOS"),("K80_PA5_S","S34_CBIT80","MOS"),
    ("K81_AMPOUT_QVM","S34_CBIT81","MOS"),
    ("K86_KELVIN0_F","S34_CBIT86","MOS"),("K86_KELVIN0_S","S34_CBIT86","MOS"),
    ("K92_AGND_F2S","S34_CBIT92","MOS"),
    ("K94_BUS_FL_PC8","S34_CBIT94","MOS"),("K94_BUS_SL_PC8","S34_CBIT94","MOS"),
    ("K96_BUS_FH_CC1","S34_CBIT96","MOS"),("K96_BUS_SH_CC1","S34_CBIT96","MOS"),
    ("K101_BUS_FH_PA0","S34_CBIT101","MOS"),("K101_BUS_SH_PA0","S34_CBIT101","MOS"),
    ("K103_PA0_PU","S34_CBIT103","MOS"),
    ("K104_BUS_FL_PD5","S34_CBIT104","MOS"),("K104_BUS_SL_PD5","S34_CBIT104","MOS"),
    ("K106_BUS_FH_PA1","S34_CBIT106","MOS"),("K106_BUS_SH_PA1","S34_CBIT106","MOS"),
    ("K108_PA1_PU","S34_CBIT108","MOS"),
    ("K111_BUS_FH_PA6","S34_CBIT111","MOS"),("K111_BUS_SH_PA6","S34_CBIT111","MOS"),
    ("K113_PA6_PU","S34_CBIT113","MOS"),
    ("K116_BUS_FH_PB7","S34_CBIT116","MOS"),("K116_BUS_SH_PB7","S34_CBIT116","MOS"),
    ("K118_BUS_FL_PA4","S34_CBIT118","MOS"),("K118_BUS_SL_PA4","S34_CBIT118","MOS"),
    ("K120_BUS_FH_PA7","S34_CBIT120","MOS"),("K120_BUS_SH_PA7","S34_CBIT120","MOS"),
    ("K122_PA7_PU","S34_CBIT122","MOS"),
    ("K127_U2_PS","S34_CBIT127","MOS"),
    ("K128_PU_PS","S36_CBIT0","MOS"),("K129_Backup","S36_CBIT1","MOS"),
    ("K130_KELVIN1_F","S36_CBIT2","MOS"),("K130_KELVIN1_S","S36_CBIT2","MOS"),
    ("K136_QVMH_BUS0","S36_CBIT8","MOS"),("K137_QVMH_BUS1","S36_CBIT9","MOS"),
    ("K138_QVML_BUS0","S36_CBIT10","MOS"),("K139_QVML_BUS1","S36_CBIT11","MOS"),
    ("K140_QVML_AGND","S36_CBIT12","MOS"),
    ("K143_DCM_BUS0_H","S36_CBIT15","MOS"),("K144_DCM_BUS1_H","S36_CBIT16","MOS"),
    ("K145_DCM_BUS0_L","S36_CBIT17","MOS"),("K146_DCM_BUS1_L","S36_CBIT18","MOS"),
    ("K147_PB0_OSC","S36_CBIT19","MOS"),("K147_PB1_OSC","S36_CBIT19","MOS"),
    ("K148_PC4_PD","S36_CBIT20","MOS"),("K149_PA1_PD","S36_CBIT21","MOS"),
    ("K150_PA4_PD","S36_CBIT22","MOS"),
    ("K152_VDM_TMU","S36_CBIT24","MOS"),("K153_PA4","S36_CBIT25","MOS"),
    ("K156_BUS_FH_VCN","S36_CBIT28","MOS"),("K156_BUS_SH_VCN","S36_CBIT28","MOS"),
    ("K158_AMPOUT","S36_CBIT30","MOS"),
    ("K168_VCP_F","S36_CBIT31","MOS"),("K169_PB5_F","S36_CBIT32","MOS"),
    ("K170_VAC_F","S36_CBIT33","MOS"),
    # G6K
    ("K3_BUSL_VBUS","S34_CBIT3","G6K"),("K4_DRVH1","S34_CBIT4","G6K"),
    ("K7_BUSH_VBAT","S34_CBIT7","G6K"),("K8_PD3","S34_CBIT8","G6K"),
    ("K17_BUSL_VAC","S34_CBIT17","G6K"),("K18_VAC3","S34_CBIT18","G6K"),
    ("K19_VAC2","S34_CBIT19","G6K"),("K20_AMUX","S34_CBIT20","G6K"),
    ("K29_BUSL_VCC","S34_CBIT29","G6K"),("K30_BUSH_ACDRV","S34_CBIT30","G6K"),
    ("K31_VMCU","S34_CBIT31","G6K"),("K32_BUSL_SCL","S34_CBIT32","G6K"),
    ("K33_VAC_WL","S34_CBIT33","G6K"),("K35_BUSH_KLV","S34_CBIT35","G6K"),
    ("K36_PGND_WL","S34_CBIT36","G6K"),("K37_KLV2","S34_CBIT37","G6K"),
    ("K42_AMP_PS","S34_CBIT42","G6K"),("K43_BST2","S34_CBIT43","G6K"),
    ("K48_AMP_REF","S34_CBIT48","G6K"),("K49_ACM_SW2","S34_CBIT49","G6K"),
    ("K50_FOVI_SW2","S34_CBIT50","G6K"),("K51_BUSL_LG","S34_CBIT51","G6K"),
    ("K52_LG2","S34_CBIT52","G6K"),("K58_BUSH_VDM","S34_CBIT58","G6K"),
    ("K59_SDA","S34_CBIT59","G6K"),("K60_BUSL_VCP","S34_CBIT60","G6K"),
    ("K61_SW","S34_CBIT61","G6K"),("K64_HG1","S34_CBIT64","G6K"),
    ("K76_ACM_BST","S34_CBIT76","G6K"),("K83_BUSH_PMID","S34_CBIT83","G6K"),
    ("K84_HG2","S34_CBIT84","G6K"),("K88_KELVIN0","S34_CBIT88","G6K"),
    ("K90_PC0_Force","S34_CBIT90","G6K"),("K91_PC0_Sense","S34_CBIT91","G6K"),
    ("K93_AGND2PGND","S34_CBIT93","G6K"),("K95_PC6","S34_CBIT95","G6K"),
    ("K97_Qpoint","S34_CBIT97","G6K"),("K98_PB3","S34_CBIT98","G6K"),
    ("K99_BUSL_PB5","S34_CBIT99","G6K"),("K100_PC4","S34_CBIT100","G6K"),
    ("K102_PC3","S34_CBIT102","G6K"),("K105_CC2","S34_CBIT105","G6K"),
    ("K107_PB1","S34_CBIT107","G6K"),("K109_BUSL_PB0","S34_CBIT109","G6K"),
    ("K110_BST","S34_CBIT110","G6K"),("K112_PC5","S34_CBIT112","G6K"),
    ("K114_BUSL_PA5","S34_CBIT114","G6K"),("K115_PB2","S34_CBIT115","G6K"),
    ("K117_PB6","S34_CBIT117","G6K"),("K119_PB4","S34_CBIT119","G6K"),
    ("K121_PD2","S34_CBIT121","G6K"),("K123_BUSL_PB5","S34_CBIT123","G6K"),
    ("K124_nRST","S34_CBIT124","G6K"),("K125_U34_PS","S34_CBIT125","G6K"),
    ("K126_V1P5_CAP","S34_CBIT126","G6K"),
    ("K132_KELVIN1","S36_CBIT4","G6K"),("K134_PC1_Force","S36_CBIT6","G6K"),
    ("K135_PC1_Sense","S36_CBIT7","G6K"),("K154_BUSH_AMUX","S36_CBIT26","G6K"),
    ("K155_FOVI_PGND","S36_CBIT27","G6K"),("K157_COMP","S36_CBIT29","G6K"),
    # Shared
    ("K0_VCC_Cap","S34_CBIT0","SHARED"),("K2_BUF","S34_CBIT2","SHARED"),
    ("K5_VBUS_Cap","S34_CBIT5","SHARED"),("K13_VBAT_Cap","S34_CBIT13","SHARED"),
    ("K21_VAC_Cap","S34_CBIT21","SHARED"),("K44_Cap_SW2_BST2","S34_CBIT44","SHARED"),
    ("K45_Cap_SW1_BST1","S34_CBIT45","SHARED"),("K57_CAP_BST_SW","S34_CBIT57","SHARED"),
    ("K74_GAIN1_SEL","S34_CBIT74","SHARED"),("K75_GAIN2_SEL","S34_CBIT75","SHARED"),
    ("K82_R_CS","S34_CBIT82","SHARED"),("K85_CAP_PMID","S34_CBIT85","SHARED"),
    ("K87_KELVIN0","S34_CBIT87","SHARED"),("K89_KELVIN0","S34_CBIT89","SHARED"),
    ("K131_KELVIN1","S36_CBIT3","SHARED"),("K133_KELVIN1","S36_CBIT5","SHARED"),
    ("K141_QTMU_BUSA","S36_CBIT13","SHARED"),("K142_QTMU_BUSB","S36_CBIT14","SHARED"),
    ("K151_NC_GND","S36_CBIT23","SHARED"),
]
def pcbit(s):
    m=re.match(r'S(\d+)_CBIT(\d+)',s)
    if m: b,n=int(m.group(1)),int(m.group(2)); return n if b==34 else n+128
    return None

# ===== PARSE NETLIST =====
with open(r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\SCH-DALI.NET",encoding="utf-8",errors="ignore") as f:
    text=f.read()
nets={};cn,cc,inn,d=None,[],False,0
for line in text.split('\n'):
    m=re.match(r'^\s*\(Net\s+(.+)$',line)
    if m and not inn:
        cn=m.group(1).strip().strip('"')
        if cn.startswith('(rename)'):
            rm=re.match(r'\(rename\s+("[^"]*")\s*',line)
            if rm:cn=rm.group(1).strip('"')
        cc,inn,d=[],True,1;continue
    if inn:
        for c in line:
            if c=='(':d+=1
            elif c==')':d-=1
        refs=re.findall(r'\(PortRef\s+&(\d+)\s+\(InstanceRef\s+(\S+)\)\)',line)
        for pin,inst in refs:cc.append((inst,int(pin)))
        if d<=0:
            if cn:nets[cn]=cc
            cn,cc,inn,d=None,[],False,0

# ===== RELAYS =====
rp=defaultdict(set)
for n,conns in nets.items():
    for inst,pin in conns:
        if re.match(r'^K\d+_',inst):rp[inst].add(pin)
relay_type={inst:'G6K' if max(pins)>=5 else 'MOS' for inst,pins in rp.items()}
COIL={'G6K':{1,8},'MOS':{1,2}}
ipn=defaultdict(lambda:defaultdict(list))
for n,conns in nets.items():
    for inst,pin in conns:ipn[inst][pin].append(n)

def rtrans(inst,pin,seton):
    rt=relay_type.get(inst,'?')
    if rt=='G6K':return {3:[4],4:[3],6:[5],5:[6]} if seton else {2:[3],3:[2],7:[6],6:[7]}
    elif rt=='MOS':return {3:[4],4:[3]} if seton else {}
    return {}

# ===== DUT PORTS + SHORTED-PAIR DETECTION =====
dut_raw=set()
for m in re.finditer(r'\(port\s+(?:\(rename\s+("[^"]+")\s*("[^"]*")\)|(\S+))\s+\(direction\s+OUTPUT\)\)',text):
    name=(m.group(1) or m.group(3)).strip('"')
    if name and name not in ('UNDEFINED',''):dut_raw.add(name)

def norm(p):return re.sub(r'_[FS]_S\d+$','',p)

# Build: port → signal net mapping (for ports without their own net)
# Strategy: find instances named like the port, see which nets they're on
port_signal_net = {}  # port_base → signal_net_name
port_merged_name = {} # port_base → merged_display_name

# First pass: ports with matching nets
for p in dut_raw:
    base = norm(p)
    if p in nets:
        port_signal_net[base] = p
        port_merged_name[base] = base

# Second pass: ports without nets → find signal nets via instance matching
for p in sorted(dut_raw):
    base = norm(p)
    if base in port_signal_net:
        continue

    # Find instances named with this port base
    signal_nets = defaultdict(int)  # net → count of instances
    for net_name, conns in nets.items():
        for inst, pin in conns:
            inst_base = re.sub(r'_S\d+(S\d+)?$','',inst)
            # Check if instance name contains the port base
            if base in inst_base.split('_'):
                signal_nets[net_name] += 1

    # Pick the net with most matching instances
    if signal_nets:
        best_net = max(signal_nets, key=signal_nets.get)

        # Determine the other port on this net (for merged naming)
        other_port = None
        for p2 in dut_raw:
            b2 = norm(p2)
            if b2 != base and b2 in port_signal_net and port_signal_net[b2] == best_net:
                other_port = b2
                break
            if b2 != base and p2 == best_net:
                other_port = b2

        # Also check if best_net itself is a port name
        if other_port is None and best_net in dut_raw:
            other_port = norm(best_net)

        # Check if another port already maps to this net
        for b2, sn in port_signal_net.items():
            if sn == best_net and b2 != base:
                other_port = b2
                break

        port_signal_net[base] = best_net
        if other_port:
            # Create merged name (shorter first alphabetically)
            names = sorted([base, other_port])
            port_merged_name[base] = f"{names[0]}_{names[1]}"
            port_merged_name[other_port] = f"{names[0]}_{names[1]}"
        else:
            port_merged_name[base] = base

# Build reverse: signal_net → list of ports
net_to_ports = defaultdict(list)
for base, sn in port_signal_net.items():
    net_to_ports[sn].append(base)

print("=== SHORTED PAIRS ===")
for base in sorted(port_merged_name):
    sn = port_signal_net.get(base,'')
    merged = port_merged_name[base]
    if merged != base:
        others = [b for b in net_to_ports.get(sn,[]) if b != base]
        print(f"  {base:15s} ↔ {others}  → net:{sn}  → merged:{merged}")

# ===== SINGLE-POINT CBIT =====
by_cbit={}
for name,cs,group in RAW_CBIT:
    val=pcbit(cs)
    if val is None:continue
    if val not in by_cbit:by_cbit[val]={"names":[],"group":group}
    by_cbit[val]["names"].append(name)

def merge(names):
    kfs=[n for n in names if re.match(r'K\d+_KELVIN\d+_[FS]$',n)]
    if len(kfs)==2:return re.sub(r'_[FS]$','',kfs[0])+"_FS"
    if any('K147' in n for n in names):
        pins=[re.search(r'K147_(\w+)_OSC',n).group(1) for n in names if re.search(r'K147_(\w+)_OSC',n)]
        if pins:return f"K_{'_'.join(sorted(pins))}_OSC"
    fh=[n for n in names if '_FH_' in n];sh=[n for n in names if '_SH_' in n]
    if fh and sh and len(fh)==1 and len(sh)==1:
        fb,sb=fh[0].replace('_FH_','_'),sh[0].replace('_SH_','_')
        if fb==sb:return fb
    fl=[n for n in names if '_FL_' in n];sl=[n for n in names if '_SL_' in n]
    if fl and sl and len(fl)==1 and len(sl)==1:
        fb,sb=fl[0].replace('_FL_','_'),sl[0].replace('_SL_','_')
        if fb==sb:return fb
    f=[n for n in names if n.endswith('_F')];s=[n for n in names if n.endswith('_S')]
    if f and s and len(f)==1 and len(s)==1:
        fb,sb=re.sub(r'_F$','',f[0]),re.sub(r'_S$','',s[0])
        if fb==sb:return fb if 'KELVIN' not in fb else fb+"_FS"
    return names[0]

single={}
for val,info in sorted(by_cbit.items()):
    nms,grp=info["names"],info["group"]
    merged=merge(nms) if len(nms)>1 else nms[0]
    single[merged]=(val,grp)
r2cbit={n:v for n,(v,_) in single.items()}

# ===== BUS NETS =====
BUS_KW=['FH_BUS','FL_BUS','SH_BUS','SL_BUS','FH_PC','FL_PC','SH_PC','SL_PC']
bus_nets={}
for n in nets:
    for kw in BUS_KW:
        if kw in n:
            bus_nets[n]=[(inst,pin) for inst,pin in nets[n] if re.match(r'^K\d+_',inst)]
            break

# ===== DIRECT INDEX: BUS → L1 → L2 → DUT =====
def infer_target(rbase):
    for pat in [r'^K\d+_BUS_F[HL]_(\w+)$',r'^K\d+_BUS_S[HL]_(\w+)$',
                r'^K\d+_BUS_(\w+)$',r'^K\d+_BUSH_(\w+)$',r'^K\d+_BUSL_(\w+)$']:
        m=re.match(pat,rbase)
        if m:return m.group(1)
    return None

def expand(group):
    """Expand group name to all matching DUT pin names (use merged names)"""
    # Check all port bases for matching
    matches = set()
    for base in port_signal_net:
        if base.startswith(group) or base == group:
            matches.add(port_merged_name[base])
    if not matches:
        # Direct match
        for base in port_signal_net:
            mn = port_merged_name[base]
            if mn.startswith(group) or mn == group:
                matches.add(mn)
    return sorted(matches) if matches else []

# Build: signal net name → merged DUT name(s)
signal_to_dut = defaultdict(set)
for base, sn in port_signal_net.items():
    signal_to_dut[sn].add(port_merged_name[base])

path_defines = {}

for bus_net in sorted(bus_nets):
    ch = '0' if 'FPVIe0' in bus_net else '1'
    side = ''
    if any(h in bus_net for h in ['FH','SH']):side='H'
    elif any(l in bus_net for l in ['FL','SL']):side='L'

    for inst, bus_pin in bus_nets[bus_net]:
        rbase = re.sub(r'_S\d+(S\d+)?$','',inst)
        group = infer_target(rbase)
        if not group:continue
        target_merged_names = expand(group)
        if not target_merged_names:continue

        # Level 1: BUS relay SetOn → output net
        tmap = rtrans(inst, bus_pin, True)
        if bus_pin not in tmap:continue
        for out_pin in tmap[bus_pin]:
            for l1_net in ipn[inst].get(out_pin,[]):
                if l1_net == bus_net:continue

                # Check L1 net for direct DUT match
                for mn in signal_to_dut.get(l1_net,set()):
                    if mn in target_merged_names:
                        cbits=[r2cbit[rbase]] if rbase in r2cbit else[]
                        if cbits:
                            key=f"K_FPVI{side}_TO_{mn}"
                            if key not in path_defines:path_defines[key]=(cbits,ch,side,bus_net)

                # Level 2: secondary relays on L1 net
                for si,sp in nets.get(l1_net,[]):
                    if not re.match(r'^K\d+_',si):continue
                    if sp in COIL.get(relay_type.get(si,'?'),set()):continue
                    s_rbase=re.sub(r'_S\d+(S\d+)?$','',si)

                    # Try both NC and SetOn
                    for seton in [False,True]:
                        t2=rtrans(si,sp,seton)
                        if sp not in t2:continue
                        for op2 in t2[sp]:
                            for l2_net in ipn[si].get(op2,[]):
                                if l2_net==l1_net:continue
                                for mn in signal_to_dut.get(l2_net,set()):
                                    if mn in target_merged_names:
                                        rels=[rbase]
                                        if seton and s_rbase in r2cbit:rels.append(s_rbase)
                                        cbits=[r2cbit[r] for r in rels if r in r2cbit]
                                        if cbits:
                                            # Only add if the BUS relay name's group matches the target
                                            # (prevents K35→VCN etc.)
                                            key=f"K_FPVI{side}_TO_{mn}"
                                            # Verify: the L2 relay name should contain or match the DUT pin
                                            if key not in path_defines:
                                                path_defines[key]=(cbits,ch,side,bus_net)

# ===== Type 3: PIN_SOURCE =====
for name,(val,group) in single.items():
    m=re.match(r'K\d+_(ACM|FOVI)_(\w+)',name)
    if m:
        pin,src=m.group(2),m.group(1)
        # Check if pin has a merged name
        mn=port_merged_name.get(pin,pin)
        key=f"K_{mn}_{src}"
        if key not in path_defines:path_defines[key]=([val],'0','','')

for name,(val,group) in single.items():
    m=re.match(r'K\d+_(\w+)$',name)
    if m:
        pin=m.group(1)
        if pin not in ('Cap','BUF','PS','PU','PD','P2P','LP','short','SVLP','SVLP1','SVLP2','FS'):
            mn=port_merged_name.get(pin,pin)
            if mn in port_merged_name.values():
                key=f"K_{mn}"
                if key not in path_defines:path_defines[key]=([val],'0','','')

# Grouped
for pfx in ['KELVIN0','KELVIN1']:
    cbs=sorted(set(v for n,(v,_) in single.items() if pfx in n))
    if cbs:path_defines[f'K_{pfx}']=(cbs,'0','','')
for n,(v,g) in single.items():
    if ('Cap' in n or 'CAP' in n) and n not in path_defines:path_defines[n]=([v],'0','','')
gain=sorted(set(v for n,(v,_) in single.items() if 'GAIN' in n and 'SEL' in n))
if gain:path_defines['K_GAIN_SEL']=(gain,'0','','')
svlp=sorted(set(v for n,(v,_) in single.items() if 'COMP_SVLP' in n))
if svlp:path_defines['K_COMP_SVLP']=(svlp,'0','','')

# ===== GENERATE =====
mos,g6k,shared=[],[],[]
for name,(val,group) in sorted(single.items(),key=lambda x:x[1][0]):
    brd,bit=(34,val) if val<128 else (36,val-128)
    line=f"#define {name:<40} {val:<6} // S{brd}_CBIT{bit}"
    if group=="MOS":mos.append(line)
    elif group=="G6K":g6k.append(line)
    else:shared.append(line)

out=[]
out.append("// relay.h — DALI project (shorted-pin aware)")
out.append(f"// Single: {len(single)} | Path: {len(path_defines)}")
out.append("")
out.append("#ifndef _RELAY_H_\n#define _RELAY_H_\n")
out.append("// === 1. Single-Point Defines ===")
out.append("// 1.1 MOS");out.extend(mos);out.append("")
out.append("// 1.2 G6K");out.extend(g6k);out.append("")
out.append("// 1.3 Shared");out.extend(shared);out.append("")
out.append("// === 2. Path Defines ===")
out.append("")

fh,fl,kel,qtm,qvm,dcm,oth=[],[],[],[],[],[],[]
for key,(cbits,ch,side,_) in sorted(path_defines.items()):
    cs=", ".join(str(c) for c in cbits)
    rn=[]
    for c in cbits:
        for sn,(sv,_) in single.items():
            if sv==c:rn.append(sn);break
    line=f"#define {key:<40} {cs:<12} // {'+'.join(rn)}"
    if key.startswith('K_FPVIH'):fh.append(line)
    elif key.startswith('K_FPVIL'):fl.append(line)
    elif 'KELVIN' in key:kel.append(line)
    elif 'QTMU' in key:qtm.append(line)
    elif 'QVM' in key:qvm.append(line)
    elif 'DCM' in key:dcm.append(line)
    else:oth.append(line)

out.append("// 2.1 FPVIe High-side");out.extend(fh);out.append("")
out.append("// 2.2 FPVIe Low-side");out.extend(fl);out.append("")
out.append("// 2.3 KELVIN");out.extend(kel);out.append("")
out.append("// 2.4 QTMU");out.extend(qtm);out.append("")
out.append("// 2.5 QVM");out.extend(qvm);out.append("")
out.append("// 2.6 DCM");out.extend(dcm);out.append("")
out.append("// 2.7 Other");out.extend(oth);out.append("")
out.append("#endif")

result="\n".join(out)
with open(r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\relay.h","w",encoding="utf-8") as f:
    f.write(result)

print(f"\nrelay.h: {len(result.split(chr(10)))} lines | Single: {len(single)} | Path: {len(path_defines)}")
sv=[v for v,_ in single.values()]
print(f"Dup CBIT: {'NONE' if not set(v for v in sv if sv.count(v)>1) else 'FOUND'}")
bad=[(k,c) for k,(cbs,_,_,_) in path_defines.items() for c in cbs if c not in sv]
print(f"Bad refs: {'NONE' if not bad else bad}")

print("\n=== FPVI PATHS ===")
for key,(cbits,ch,side,_) in sorted(path_defines.items()):
    if key.startswith('K_FPVI'):
        rn=[]
        for c in cbits:
            for sn,(sv,_) in single.items():
                if sv==c:rn.append(sn);break
        print(f"  {key:35s} = {cbits}  // {'+'.join(rn)}")
