# -*- coding: utf-8 -*-
"""t3 setup-contract generator (setup-architect).

Inputs (all read-only):
  team/artifacts/acceptance-20260916-dali10/dft-ir.json          (t1)
  team/artifacts/acceptance-20260916-dali10/schematic-ir.json    (t2)
  team/artifacts/acceptance-20260916-dali10/sch-paths.json       (scripts/gen_paths.py --json)
  project/DALI/SCH-Connect-Map.txt                               ("需闭合" authoritative lists)
  project/DALI/reg_config/tm600.sv, tm601.sv                     (BD-03 register evidence)
  project_config.json                                            (channel map / relay defs / TReg)

Output:
  team/artifacts/acceptance-20260916-dali10/setup-contract.json
"""
import datetime
import hashlib
import json
import os
import re

RUN = "team/artifacts/acceptance-20260916-dali10"
RUN_ID = "acceptance-20260916-dali10"
# Monotonic contract revision. BUMP THIS on every content change: consumers (test-plan, t5, gates)
# reference it instead of a hash, because the hash changes on every regeneration.
CONTRACT_REVISION = 28
# generatedAt is DERIVED FROM the revision (not wall-clock) so that two consecutive
# generator runs are byte-identical - a requirement of the freeze (t16). Bump both together.
GENERATED_AT = "2026-09-16 19:30:00 (revision 28)"
CONNECT_MAP = "project/DALI/SCH-Connect-Map.txt"

SCOPE = ["TM000", "TM001", "TM102", "TM103", "TM108", "TM109", "TM135", "TM600", "TM601", "TM1205"]


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def ev(path, locator, digest=None):
    return {"path": path, "locator": locator, "sha256": digest or sha(path)}


dft = load(os.path.join(RUN, "dft-ir.json"))
sir = load(os.path.join(RUN, "schematic-ir.json"))
paths = load(os.path.join(RUN, "sch-paths.json"))

HASH = {p: sha(p) for p in [
    "project/DALI/input/DFT.csv", "project/DALI/Dali-SCH.csv", CONNECT_MAP,
    "project/DALI/reg_config/tm600.sv", "project/DALI/reg_config/tm601.sv",
    "project_config.json", os.path.join(RUN, "dft-ir.json"), os.path.join(RUN, "schematic-ir.json"),
    os.path.join(RUN, "sch-paths.json"), os.path.join(RUN, "sch-paths.txt"),
    os.path.join(RUN, "schematic-ir-sensing.json"), os.path.join(RUN, "schematic-ir-handoff.md"),
    "C:/AccoTEST/AccoTEST System/INCLude/FPVIe.h", "C:/AccoTEST/AccoTEST System/INCLude/FXVIe.h",
]}

E_DFT = lambda loc: ev("project/DALI/input/DFT.csv", loc, HASH["project/DALI/input/DFT.csv"])
E_CMAP = lambda loc: ev(CONNECT_MAP, loc, HASH[CONNECT_MAP])
E_IR = lambda loc: ev(os.path.join(RUN, "schematic-ir.json"), loc, HASH[os.path.join(RUN, "schematic-ir.json")])
E_SP = lambda loc: ev(os.path.join(RUN, "sch-paths.json"), loc, HASH[os.path.join(RUN, "sch-paths.json")])
E_TM600SV = lambda loc: ev("project/DALI/reg_config/tm600.sv", loc, HASH["project/DALI/reg_config/tm600.sv"])
E_TM601SV = lambda loc: ev("project/DALI/reg_config/tm601.sv", loc, HASH["project/DALI/reg_config/tm601.sv"])
E_FPVIEH = lambda loc: ev("C:/AccoTEST/AccoTEST System/INCLude/FPVIe.h", loc, HASH["C:/AccoTEST/AccoTEST System/INCLude/FPVIe.h"])
E_FXVIEH = lambda loc: ev("C:/AccoTEST/AccoTEST System/INCLude/FXVIe.h", loc, HASH["C:/AccoTEST/AccoTEST System/INCLude/FXVIe.h"])
E_RULES = lambda loc: ev("knowledge/standards/rules-registry.md", loc)

# --------------------------------------------------------------------------------------
# 1. Parse SCH-Connect-Map "需闭合" groups (authoritative relay actuation lists)
# --------------------------------------------------------------------------------------
GROUPS = []
section = None
with open(CONNECT_MAP, encoding="utf-8", errors="replace") as fh:
    for lineno, raw in enumerate(fh, 1):
        line = raw.rstrip("\n")
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            section = m.group(1).strip()
            continue
        if "需闭合:" not in line:
            continue
        head, tail = line.split("需闭合:", 1)
        head = head.strip()
        gap = re.match(r"^(?:(CH\d)\s+(High|Low)|(S\d+_[A-Za-z0-9_]+))\s*->\s*([A-Za-z0-9_]+)", head)
        detail = None
        if not gap:
            # header form without an arrow: "<PIN> <role/detail> 需闭合: ..." (e.g. "V1P5_VDRV [Kelvin]", "V1P5_VDRV 稳压 Cap2_V1P5_S1 C=2.2uF")
            m2 = re.match(r"^([A-Za-z0-9_]+)\s+(.*)$", head)
            if not m2:
                continue
            gap = m2
            chan = None
            side = None
            src = None
            pin = m2.group(1)
            detail = m2.group(2).strip()
        else:
            chan = gap.group(1)
            side = gap.group(2)
            src = gap.group(3)
            pin = gap.group(4)
        kind = "[Kelvin]"
        for tag in ("[Kelvin]", "[PC短接]", "[单线]"):
            if tag in head:
                kind = tag
        ks = [int(x) for x in re.findall(r"K(\d+)", tail)]
        GROUPS.append({
            "section": section, "channel": chan, "side": side, "source": src, "pin": pin,
            "detail": detail,
            "kind": kind, "needsClosed": ks, "defaultConducting": "无" in tail,
            "warning": "⚠F/S未同时连通,非有效通路" in line,
            "line": lineno, "raw": line.strip(),
        })


# Scope pin names vs connect-map node names (L936/L952-L953 prove VDRV and V1P5_F/S are one node via TP_VDRV)
PIN_SYNONYM = {
    "VDRV": ["V1P5_VDRV"],
    "V1P5": ["V1P5_VDRV"],
    "AGND": ["AGND", "AGND_F"],
    "PGND_WL": ["PGND_WL"],
    "VAC1": ["VAC1", "VAC"],
    "VAC2": ["VAC2"],
    "VAC3": ["VAC3"],
}


def groups_for_pin(pin):
    out = {}
    wanted = PIN_SYNONYM.get(pin, [pin])
    for g in GROUPS:
        if g["pin"] not in wanted:
            continue
        key = "%s | %s" % (g["section"], g["channel"] if g["channel"] else g["source"])
        if g["side"]:
            key += " %s" % g["side"]
        out.setdefault(key, g)
    return out


# --------------------------------------------------------------------------------------
# 2. resources
# --------------------------------------------------------------------------------------
RELAY_RES = [
    # number, name, kind, role, definitionSource
    (86, "K86_KELVIN0_F", "relay", "FPVIe0 force-side Kelvin relay (FH0 -> FPVIe0_FH_BUS_S1)", "SCH-Connect-Map L9"),
    (87, "K87_KELVIN0", "relay", "FPVIe0 FH/SH Kelvin relay, Relay-NC default-conducting (需闭合: 无)", "SCH-Connect-Map L8-L9"),
    (88, "K88_KELVIN0", "relay", "FPVIe0 SH/SL sense Kelvin relay, Relay-NC", "SCH-Connect-Map L10/L13"),
    (89, "K89_KELVIN0", "relay", "FPVIe0 FL/SL Kelvin relay, Relay-NC", "SCH-Connect-Map L11-L12"),
    (130, "K130_KELVIN1_F", "relay", "FPVIe1 force-side Kelvin relay (FH1)", "SCH-Connect-Map L15"),
    (131, "K131_KELVIN1", "relay", "FPVIe1 FH Kelvin relay, Relay-NC", "SCH-Connect-Map L14-L15"),
    (132, "K132_KELVIN1", "relay", "FPVIe1 SH/SL Kelvin relay, Relay-NC (serves both SH1 and SL1)", "SCH-Connect-Map L16/L19"),
    (133, "K133_KELVIN1", "relay", "FPVIe1 FL Kelvin relay, Relay-NC", "SCH-Connect-Map L17-L18"),
    (83, "K83_BUSH_PMID", "relay", "BUSH BUS relay for PMID (FPVIe0 CH0 High -> PMID)", "SCH-Connect-Map L165"),
    (60, "K60_BUSL_VCP", "relay", "BUSL BUS relay shared by SW and VCP", "SCH-Connect-Map L174"),
    (61, "K61_SW", "relay", "SW select relay (MOS opto): SetOn to reach SW, VCP branch otherwise", "SCH-Connect-Map L174"),
    (154, "K154_BUSH_AMUX", "relay", "BUSH BUS relay shared by AMUX and PGND", "SCH-Connect-Map L156"),
    (155, "K155_FOVI_PGND", "relay", "PGND select relay off the AMUX/PGND node pair", "SCH-Connect-Map L156"),
    (110, "K110_BST", "relay", "BST select relay (ACM200 and FPVIe low-domain share it)", "SCH-Connect-Map L268"),
    (134, "K134_PC1_Force", "relay", "PC1 force relay used by FPVIe1 BST/SW routes", "SCH-Connect-Map L265/L391"),
    (135, "K135_PC1_Sense", "relay", "PC1 sense relay used by FPVIe1 BST/SW routes", "SCH-Connect-Map L265/L391"),
    (90, "K90_PC0_Force", "relay", "PC0 force relay on the FPVIe0 PC route (K90 NC path cross-links high/low BUS per relays.md L184)", "schematic-ir unresolvedTopology U8"),
    (82, "K82_R_CS_S1S2", "relay", "PC route current-sense shunt pair gate (R1_CS 100mohm / R2_CS 5mohm on FPVIe0_FL_PC_S1)", "schematic-ir hazards measurement-validity"),
    (93, "K93_AGND2PGND", "relay", "hard tie AGND <-> PGND ([Connect] classified); TM601 loop return shares it", "schematic-ir resourceConflicts.agndPgndTie"),
    (7, "K7_BUSH_VBAT", "relay", "VBAT BUS relay", "SCH-Connect-Map L210/L418"),
    (3, "K3_BUSL_VBUS", "relay", "VBUS BUS relay", "SCH-Connect-Map L213/L421"),
    (25, "K25_VCC_F", "relay", "VCC force select off the BUSH_ACDRV bus", "SCH-Connect-Map L216/L424"),
    (30, "K30_BUSH_ACDRV", "relay", "BUSH bus shared by VCC and ACDRV1/2/3", "SCH-Connect-Map L216/L424"),
    (29, "K29_BUSL_VCC", "relay", "VCC low-domain BUS relay", "SCH-Connect-Map L219/L427"),
    (31, "K31_VMCU", "relay", "VMCU select off the VCC low bus", "SCH-Connect-Map L219"),
    (17, "K17_BUSL_VAC", "relay", "VAC low-domain BUS relay (VAC1/2/3)", "SCH-Connect-Map L192-L204"),
    (18, "K18_VAC3", "relay", "VAC3 branch relay", "SCH-Connect-Map L201/L204"),
    (19, "K19_VAC2", "relay", "VAC2 branch relay", "SCH-Connect-Map L195/L198"),
    (20, "K20_AMUX", "relay", "AMUX branch relay off the VAC low bus", "SCH-Connect-Map L36"),
    (70, "K70_VAC_F", "relay", "VAC force select relay", "SCH-Connect-Map L189/L195/L201"),
    (35, "K35_BUSH_KLV", "relay", "KLV force BUS relay", "SCH-Connect-Map L78/L84"),
    (36, "K36_PGND_WL", "relay", "PGND_WL/KLV branch relay", "SCH-Connect-Map L159"),
    (37, "K37_KLV2", "relay", "KLV2 branch relay (KLV1 when default)", "SCH-Connect-Map L84"),
    (73, "K73_VCN_F", "relay", "VCN force relay used by KLV low-domain routes", "SCH-Connect-Map L81/L87"),
    (58, "K58_BUSH_VDM", "relay", "VDM/SDA BUS relay", "SCH-Connect-Map L171/L234"),
    (59, "K59_SDA", "relay", "SDA select relay, Relay-NC default-conducting to VDM pad", "SCH-Connect-Map L171"),
    (32, "K32_BUSL_SCL", "relay", "SCL low-domain BUS relay", "SCH-Connect-Map L168/L385"),
    (152, "K152_VDM_TMU", "relay", "VDM QTMU select relay", "SCH-Connect-Map L237"),
    (5, "K5_VBUS_Cap_S1S2", "relay", "VBUS stabiliser cap gate (Cap2_VBUS 4.7uF)", "SCH-Connect-Map 稳压 L898+"),
    (13, "K13_VBAT_Cap_S1S2", "relay", "VBAT stabiliser cap gate (Cap2_VBAT 4.7uF); must stay OPEN while I(VBAT) is measured (TM000/TM001)", "schematic-ir discharge[VBAT]"),
    (0, "K0_VCC_Cap_S1S2", "relay", "VCC stabiliser cap gate (Cap2_VCC 4.7uF)", "schematic-ir discharge[VCC]"),
    (21, "K21_VAC_Cap_S1S2", "relay", "VAC stabiliser cap gate (Cap2_VAC 4.7uF); must stay OPEN while VAC1/2 is the scanned toggle input", "schematic-ir discharge[VAC1]"),
    (126, "K126_V1P5_CAP_S1", "relay", "V1P5/VDRV stabiliser cap gate (Cap2_V1P5 2.2uF)", "schematic-ir discharge[V1P5/VDRV]"),
    (85, "K85_CAP_PMID_S1S2", "relay", "PMID stabiliser cap gate (Cap2_PMID 4.7uF)", "schematic-ir discharge[PMID]"),
    (57, "K57_CAP_BST_SW_S1S2", "relay", "BST-SW bootstrap cap gate (Cap_SW_BST 220nF); part of the TM600 BST-SW loop load", "schematic-ir discharge[BST-SW]"),
    (45, "K45_Cap_SW1_BST1_S1S2", "relay", "SW1/BST1 bootstrap cap gate", "schematic-ir resourceConflicts.stabiliserRelaysOnScopeRails"),
    (44, "K44_Cap_SW2_BST2_S1S2", "relay", "SW2/BST2 bootstrap cap gate", "schematic-ir resourceConflicts.stabiliserRelaysOnScopeRails"),
    (46, "K46_BUS_FH_SW1", "relay", "FPVIe0 CH0 High -> BST high-domain route relay", "SCH-Connect-Map L39"),
    (48, "K48_AMP_REF", "relay", "FPVIe0 CH0 High -> BST route relay", "SCH-Connect-Map L39"),
    (76, "K76_ACM_BST", "relay", "BST node relay (FMVIe0 CH0 High -> BST and legacy BTST_ACM route)", "SCH-Connect-Map L39"),
    (109, "K109_BUSL_PB0", "relay", "BST low-domain route relay", "SCH-Connect-Map L42/L268"),
    (84, "K84_HG2_S1", "relay", "PMID default FXVIe_PLUS route relay (Relay-NC default-conducting; see open item U5)", "SCH-Connect-Map L72"),
    (68, "K68_VCP_F_S1", "relay", "VCP force relay sharing BUSL_VCP with SW (do not co-close with K61)", "schematic-ir hazards shared-resource"),
    (141, "K141_QTMU_BUSA_S1S2", "relay", "QTMU bridge across FPVIe0/FPVIe1 high BUS wires", "schematic-ir hazards shared-resource"),
    (142, "K142_QTMU_BUSB_S1S2", "relay", "QTMU bridge across FPVIe0/FPVIe1 low BUS wires", "schematic-ir hazards shared-resource"),
]


def relay_name(num):
    for r in sir["relays"]:
        if r["number"] == num:
            return r["instances"][0]
    for g in GROUPS:
        for k in g["needsClosed"]:
            if k == num:
                m = re.search(r"K%d[_A-Za-z0-9]*" % num, g["raw"])
                if m:
                    return m.group(0)
    return "K%d" % num


resources = [
    {
        "name": "FPVIe0 (site1 channel S1_0)",
        "kind": "source",
        "definitionSource": "SCH-Connect-Map 列1 (L7-L13) + project_config.json inputs.channelmap",
        "instances": ["FPVI0"],
        "capability": {"voltageRanges": ["100V", "40V", "20V", "10V", "5V", "2V", "1V", "100mV(measure only)"],
                       "currentRanges": ["10A", "2A", "1A", "100MA", "10MA", "1MA", "100UA", "10UA"],
                       "evidence": [E_FPVIEH("FPVIe.h:6 FPVIe_VRNG, :17 FPVIe_IRNG, :19 FPVIe_10A, :20 FPVIe_2A")]},
        "terminals": {"high": "FH0/SH0 -> FPVIe0_FH_BUS_S1 / FPVIe0_SH_BUS_S1", "low": "FL0/SL0 -> FPVIe0_FL_BUS_S1 / FPVIe0_SL_BUS_S1"},
        "usedBy": ["TM600 (PMID<->SW 1A)", "TM601 (SW<->PGND 1A)"],
        "note": "independently floating channel; 1A force is only possible on the FPVIe family",
    },
    {
        "name": "FPVIe1 (site1 channel S1_1)",
        "kind": "source",
        "definitionSource": "SCH-Connect-Map 列1 (L14-L19) + project_config.json inputs.channelmap",
        "instances": ["FPVI1"],
        "capability": {"currentRanges": ["10A", "2A", "1A", "100MA", "10MA", "1MA", "100UA", "10UA"],
                       "evidence": [E_FPVIEH("FPVIe.h:17-20")]},
        "terminals": {"high": "FH1/SH1 -> FPVIe1_FH_BUS_S1 / FPVIe1_SH_BUS_S1", "low": "FL1/SL1 -> FPVIe1_FL_BUS_S1 / FPVIe1_SL_BUS_S1"},
        "usedBy": ["TM600 (BST<->SW 5V)", "TM1205 (BST/SW differential ramp candidate)"],
        "note": "site has exactly 2 FPVIe channels -> TM600 exhausts both (schematic-ir resourceConflicts.fpvieChannelBudget)",
    },
    {
        "name": "ACM200 group (S5 share relays)",
        "kind": "source",
        "definitionSource": "SCH-Connect-Map 列6 (L662+)",
        "capability": {"currentLimit": "+-200mA", "evidence": [E_IR("hazards[0] high-current: ACM200 tops out at +-200mA")]},
        "channelsInScope": {"SW": "S5_ACM200_FH8/SH8 (K61_SW)", "BST": "S5_ACM200_FH18/SH18 (K110_BST)",
                            "INT": "S5_ACM200_FH15/SH15 (K102_PC3)", "VDM": "S5_ACM200_FH7/SH7 (K59_SDA)"},
        "usedBy": ["TM108/TM109 ramp source (VAC)", "non-high-current items", "documented fallback for BST-SW if FPVIe1 must be freed"],
    },
    {
        "name": "QTMU S10_CH0_A / S10_CH0_B",
        "kind": "source",
        "definitionSource": "SCH-Connect-Map 列3 (L451+)",
        "usedBy": ["default netlist routes for PMID and SW (K83+K141 / K60,K61,K142)"],
        "status": "UNKNOWN — Component-Statistic.txt note infers QTMU from slot naming and asks for user confirmation (schematic-ir unresolvedTopology U4)",
    },
    {
        "name": "FXVIe_PLUS share-relay groups",
        "kind": "source",
        "definitionSource": "SCH-Connect-Map 列7 (L803+) + schematic-ir testerChannels",
        "groups": [
            {"macro": "PMID_HG2_FXVI", "channels": ["S3_1"], "note": "PMID shares one FXVIe_PLUS channel with HG2; reaches PMID through default-conducting K84_HG2"},
            {"macro": "SW1_SW2_FXVI", "channels": ["S3_0"], "note": "the SW pin itself is NOT on this channel"},
            {"macro": "VCC_VMCU_FXVI", "channels": ["S3_2"], "note": "VCC and VMCU share one channel"},
            {"macro": "AMUX_PGND_FXVI", "channels": ["S3_3"], "note": "AMUX and PGND share one channel -> TM102/TM103 and TM601 cannot share a site concurrently"},
            {"macro": "VBAT_PD3_FXVI", "channels": ["S3_5", "S13_5", "S14_5", "S19_5", "S20_5", "S29_5", "S30_5", "S4_5"]},
            {"macro": "V1P5_U34PS_FXVI", "channels": ["S3_6"], "note": "V1P5 and VDRV (via TP_VDRV) share one channel"},
        ],
        "capability": {"currentLimit": "+-1A pulse (zero margin for a 1A force)", "evidence": [E_FXVIEH("FXVIe.h:348 enum FXVIe_PLUS_IRNG, :350 FXVIe_PLUS_1A")]},
    },
    {
        "name": "TReg NU1201",
        "kind": "treg",
        "definitionSource": "project_config.json inputs.treg = D:/PROJECT6-DALI/ForCodexDebug/NU1201.treg",
        "usedBy": ["TM135 trim (measure_bg_res_div / EFUSE_REG_F1)"],
        "note": "trim node must be initialised before TRIM_NODE.execute (see globalInitialization)",
    },
]

for num, name, kind, role, src in RELAY_RES:
    nm = relay_name(num)
    resources.append({
        "name": nm, "kind": kind, "definitionSource": src,
        "relayNumber": num, "role": role,
        "usedByTm": sorted([tm for tm, ks in sir["resourceConflicts"]["tmRelaySets"].items() if num in ks]),
    })

instr_aliases = [
    {"name": e["source"], "kind": "source", "definitionSource": "scripts/gen_paths.py --json build_path_list (sch-paths.json)",
     "usedBy": ["alias resolution table"], "side": e["side"]}
    for e in paths if e["source"].startswith("S1_FPVIe")
]
# channel / resource ownership
CHANNEL_RES = [
    ("FPVIe0 BUS wires (FPVIe0_FH_BUS_S1 / _SH_BUS_S1 / _FL_BUS_S1 / _SL_BUS_S1)",
     "one high and one low BUS wire per FPVIe channel; the BUS relays K83/K154 (high) and K60 (low) sit directly on them"),
    ("FPVIe1 BUS wires (FPVIe1_FH_BUS_S1 / _SH_BUS_S1 / _FL_BUS_S1 / _SL_BUS_S1)",
     "BUS relays K131/K132 (high) and K132/K133 (low); K132 is shared by SH1 and SL1 per SCH-Connect-Map L16/L19"),
    ("QTMU lines S10_CH0_A / S10_CH0_B",
     "default netlist routes for PMID and SW; bridged onto the FPVIe BUS wires by K141/K142"),
    ("QVM lines (QVMH_BUS0/1 S1, QVML_BUS0/1 S1 via K136,K137,K138,K139)",
     "used as the default QVM route in the IR path list; not used by the TM600/TM601 force loops"),
    ("Pin_Channel_define.h channel map",
     "project_config.json inputs.channelmap = D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h"),
]
for nm, note in CHANNEL_RES:
    resources.append({"name": nm, "kind": "channel", "definitionSource": "schematic-ir hazards/testerChannels + SCH-Connect-Map", "role": note,
                      "usedBy": ["channel ownership / mutual exclusion"]})

# deduplicate instrument-channel resources
seen = set()
for r in instr_aliases:
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    resources.append(r)

# --------------------------------------------------------------------------------------
# 3. alias resolution table (mandatory deliverable of t3)
# --------------------------------------------------------------------------------------
ALIASES = [
    {
        "alias": "pmid2sw",
        "kindOfStimulus": ["iset (current force)", "vset (voltage force)"],
        "nodes": {"from": "PMID", "to": "SW"},
        "dftSenseLabel": "PMID-SW",
        "usedByTm": ["TM600"],
        "firstSource": {
            "source": "DFT.csv row-inline sense-path label column",
            "evidence": [E_DFT("line 97: iset[pmid2sw,1,1e-3,0] -> PMID-SW, Check=MV&MI")],
        },
        "resolution": {
            "forceInstrument": "FPVIe0 (site1 channel S1_0)",
            "terminalAssignment": {"high": "FH0/SH0", "low": "FL0/SL0"},
            "nodeOnHighTerminal": "PMID",
            "nodeOnLowTerminal": "SW",
            "relayChainHigh": [{"relay": "K87_KELVIN0", "number": 87, "state": "Relay-NC default-conducting (需闭合: 无)"},
                               {"relay": "K83_BUSH_PMID", "number": 83, "state": "SetOn"}],
            "relayChainLow": [{"relay": "K89_KELVIN0", "number": 89, "state": "Relay-NC default-conducting (需闭合: 无)"},
                              {"relay": "K60_BUSL_VCP", "number": 60, "state": "SetOn"},
                              {"relay": "K61_SW", "number": 61, "state": "SetOn"}],
            "closedRelayNumbers": [83, 60, 61],
            "irDerivedLoop": "LOOP_TM600_PMID2SW_1A (resources 83,87,88,89,60,61)",
            "evidence": [E_CMAP("L165 CH0 High -> PMID 需闭合: K83; L174 CH0 Low -> SW 需闭合: K60,K61"),
                         E_IR("derivedPaths[LOOP_TM600_PMID2SW_1A]"),
                         E_SP("FPVIe FHSH0 -> PMID = K87,K83,K84; FPVIe FLSL0 -> SW = K89,K60,K61")],
        },
        "crossCheck": {
            "bfsAgrees": True,
            "divergence": "BFS shortest chain reaches PMID with K87,K83,K84 (K84_HG2 is the default-conducting FXVIe_PLUS route, state KeepDefault). The 需闭合 list publishes only K83. Recorded, not averaged: K84 must be evaluated by the relay-trace gate (open item U5).",
        },
        "alternatives": [
            {"option": "dual independent single-ended sources (ACM200 FH18 -> BST style) instead of a floating source",
             "rejectedBecause": "DFT requests 'pmid2sw' = a cross-pin floating source (R-PON-02: pin containing '2' is a floating source), and the required current is 1A which no ACM200 channel can source (ACM200 limit +-200mA).",
             "evidence": [E_IR("hazards[0] high-current")]},
            {"option": "FPVIe1 (channel S1_1)", "rejectedBecause": "FPVIe1 is the only remaining channel and is allocated to BST<->SW 5V for the same TM600 item (schematic-ir resourceConflicts.fpvieChannelBudget)."},
        ],
        "polarity": {
            "terminalAssignmentBasis": "schematic-ir polarity[FPVIe force/sense domains]: FH/SH = HIGH domain, FL/SL = LOW domain, no crossing; PMID is on the HIGH bus, SW on the LOW bus (K60 pins 3/6)",
            "forceSignConvention": "UNKNOWN — no source in this workspace states the FI sign that corresponds to DFT's positive value; must be signed off with hardware. Golden tm600-normal-highcurrent uses positive FI on the PMID-side force.",
            "evidence": [E_IR("polarity[FPVIe force/sense domains]; hazards[polarity]")],
        },
        "limits": {"force": "1 A (DFT iset[pmid2sw,1,...])", "compliance": "BD-05 OPEN — no source value; clamp mechanism available",
                   "rangeRule": "current range >= 2x force -> FPVIe_2A (never FXVIe_PLUS_10MA)"},
    },
    {
        "alias": "sw2pgnd",
        "kindOfStimulus": ["iset (current force)", "vset"],
        "nodes": {"from": "SW", "to": "PGND"},
        "dftSenseLabel": "PGND-SW",
        "usedByTm": ["TM601"],
        "firstSource": {"source": "DFT.csv row-inline sense-path label column",
                        "evidence": [E_DFT("line 104: iset[sw2pgnd,1,1e-6,0] -> PGND-SW, Check=MV&MI")]},
        "resolution": {
            "forceInstrument": "FPVIe0 (site1 channel S1_0)",
            "terminalAssignment": {"high": "FH0/SH0", "low": "FL0/SL0"},
            "nodeOnHighTerminal": "PGND",
            "nodeOnLowTerminal": "SW",
            "relayChainHigh": [{"relay": "K87_KELVIN0", "number": 87, "state": "Relay-NC default-conducting"},
                               {"relay": "K154_BUSH_AMUX", "number": 154, "state": "SetOn"},
                               {"relay": "K155_FOVI_PGND", "number": 155, "state": "SetOn"}],
            "relayChainLow": [{"relay": "K89_KELVIN0", "number": 89, "state": "Relay-NC default-conducting"},
                              {"relay": "K60_BUSL_VCP", "number": 60, "state": "SetOn"},
                              {"relay": "K61_SW", "number": 61, "state": "SetOn"}],
            "closedRelayNumbers": [154, 155, 60, 61],
            "irDerivedLoop": "LOOP_TM601_SW2PGND_1A (resources 60,61,133,134,154,155)",
            "evidence": [E_CMAP("L156 CH0 High -> PGND 需闭合: K154,K155; L174 CH0 Low -> SW 需闭合: K60,K61"),
                         E_IR("derivedPaths[LOOP_TM601_SW2PGND_1A]")],
        },
        "crossCheck": {
            "bfsAgrees": True,
            "divergence": "The IR loop's resource list also carries 133 and 134 (FPVIe1 relays); the connect-map group for CH0 High->PGND does not require them. Recorded as a divergence for the relay-trace gate; the union must be proven non-conflicting before either is adopted.",
        },
        "alternatives": [
            {"option": "FPVIe1 (channel S1_1)",
             "rejectedBecause": "SW is bound to the FPVIe0 LOW bus (K60 pins 3/6 = FPVIe0_FL_BUS_S1 / FPVIe0_SL_BUS_S1); routing SW from FPVIe1 needs the K142 QTMU bridge, which is not an allowed cross-channel route for a mOhm loop."},
        ],
        "polarity": {
            "terminalAssignmentBasis": "schematic-ir hazards[polarity]: SW is on the FPVIe0 LOW bus while PMID and PGND are on the HIGH bus",
            "forceSignConvention": "UNKNOWN — 'sw2pgnd' names the intended direction (SW -> PGND); the FI sign that realises it is not published by any source.",
            "evidence": [E_IR("hazards[polarity]")],
        },
        "limits": {"force": "1 A (DFT iset[sw2pgnd,1,...])", "compliance": "BD-05 OPEN", "rangeRule": "FPVIe_2A"},
    },
    {
        "alias": "pgnd2sw",
        "kindOfStimulus": ["iset (current force)", "vset"],
        "nodes": {"from": "PGND", "to": "SW"},
        "dftSenseLabel": "INT / AMUX-NTC (per row)",
        "usedByTm": ["TM108/TM109 toggle ramps (DFT.csv lines 121-122, 208-210)", "other DFT rows using pgnd2sw"],
        "firstSource": {"source": "DFT.csv row-inline label + value sign",
                        "evidence": [E_DFT("line 121-122: iset[pgnd2sw,0.5,0,0] / iset[pgnd2sw,-0.1,1e-3,0] -> INT, Check='Toggle, MI'")]},
        "resolution": {
            "forceInstrument": "FPVIe0 (site1 channel S1_0) — same physical node pair as sw2pgnd",
            "terminalAssignment": {"high": "FH0/SH0", "low": "FL0/SL0"},
            "nodeOnHighTerminal": "PGND",
            "nodeOnLowTerminal": "SW",
            "closedRelayNumbers": [154, 155, 60, 61],
            "evidence": [E_CMAP("L156, L174"), E_DFT("line 210: (Ipmid2sw+Ipgnd2sw)/2 -> the two aliases are one bidirectional loop pair")],
        },
        "crossCheck": {
            "bfsAgrees": True,
            "divergence": "'pgnd2sw' and 'sw2pgnd' resolve to the SAME instrument/terminal/relay assignment; the alias name encodes current direction, not a different route. No source in this workspace defines which sign of FI realises which name — recorded as an open polarity item rather than being averaged away.",
        },
        "alternatives": [
            {"option": "treat as a distinct route (e.g. SW on the high terminal)",
             "rejectedBecause": "SW is only reachable from the FPVIe0 LOW domain in the connect-map; the high-domain SW route requires the K90_PC0 cross path that relays.md L184 says must be rejected for standard routing."},
        ],
        "polarity": {"forceSignConvention": "UNKNOWN (BD-05-adjacent): the sign of the FI ramp (0.5 A -> -0.1 A per DFT line 122) must be confirmed against the DUT's intended current direction."},
    },
    {
        "alias": "bst2sw",
        "kindOfStimulus": ["vset (voltage force)"],
        "nodes": {"from": "BST", "to": "SW"},
        "dftSenseLabel": "BST-SW",
        "usedByTm": ["TM600 (BST must lead PMID)", "TM1205 (BST1-SW1 / BST2-SW2 ramps)"],
        "firstSource": {"source": "DFT.csv row-inline sense-path label column",
                        "evidence": [E_DFT("line 92: vset[bst2sw,5,1e-3,0]; lines 125/137/150/164/175/213/251/285 repeat it")]},
        "resolution": {
            "forceInstrument": "SW12_U1REF_BST_ACM (ground-referenced ACM200, StdAfx.h:69 extern ACM200 SW12_U1REF_BST_ACM; channel macro _PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = 'S5_5,S6_5,S11_5,S12_5,S21_5,S22_5,S27_5,S28_5', Pin_Channel_define.h:20) - per captain ruling (ii) the BST-SW 5 V is NOT carried by FPVIe1 CH1",
            "bstRuling_ii": "BST-SW stays the ground-referenced SW12_U1REF_BST_ACM form. The FPVIe1 CH1 variant (composite macro K_FPVIH_TO_BST_B = 131,132,134,135, StdAfx.h:378) is recorded as 'intended but currently unrealisable': K131/K132/K134/K135 are FPVI1_FH_SL_SHORT / FPVI1_Sense_FLOAT / FPVI1_PC_Force / FPVI1_PC_Sense - the same sense-float/PC class as ch0's 87/88/89/90/91, which the negative list forbids as stimulus relays; ch1 has no simple endpoint macro and FPVI1 is used only for zero-value initialisation in test.cpp. Precondition to revisit: provide a ch1 minimal end-point relay set with evidence.",
            "terminalAssignment": {"high": "BST", "low": "SW (SW12_U1REF_BST_ACM is ground-referenced, so the BST-SW differential is set by the ACM output level)"},
            "nodeOnHighTerminal": "BST",
            "nodeOnLowTerminal": "SW",
            "relayChain": [{"relay": "K110_ACM18_BST", "number": 110, "state": "SetOn (ACM200 S5_FH18 -> BST)"},
                           {"relay": "K61_ACM8_SW", "number": 61, "state": "SetOn (ACM200 S5_FH8 -> SW)"}],
            "closedRelayNumbers": [110, 61],
            "supersededRelaySet": [131, 132, 134, 135],
            "irDerivedLoop": "LOOP_TM600_BST2SW_5V (resources 131,132,133,134,135)",
            "loadNote": "the loop closes across Cap_SW_BST_S1 (220nF) + D_BST_SW_S1; the cap is part of the item, not decoupling (schematic-ir polarity[Cap_SW_BST_S1])",
            "evidence": [E_CMAP("L265 CH1 High -> BST 需闭合: K131,K132,K134,K135; L391 CH1 Low -> SW 需闭合: K132,K133,K134,K135"),
                         E_IR("derivedPaths[LOOP_TM600_BST2SW_5V]")],
        },
        "crossCheck": {
            "bfsAgrees": True,
            "divergence": "K134/K135 appear in BOTH the CH1 High->BST and the CH1 Low->SW 需闭合 lists (and K132 serves both SH1 and SL1 per L16/L19). Whether the published lists are a merged force/sense notation or a real shared relay must be settled by the relay-trace gate before code is written; recorded, not averaged.",
        },
        "alternatives": [
            {"option": "two independent single-ended sources (ACM200 FH18 -> BST via K110_BST, ACM200 FH8 -> SW via K61_SW)",
             "rejectedBecause": "Not rejected on capability grounds - it is the golden's scarce-source arbitration for a single-FPVI board (knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md:16). This board has two FPVIe channels, and the schematic IR already allocates channel 1 to this loop, so FPVIe1 is the primary resolution. The dual-ACM200 form is retained as the documented fallback and must carry BST-SW <= 5V per step.",
             "evidence": [E_CMAP("L268 CH1 Low -> BST 需闭合: K109,K110; S5_ACM200_FH18 -> BST = K110_BST; S5_ACM200_FH8 -> SW = K61_SW")]},
        ],
        "polarity": {"constraint": "BST - SW >= -Vf at all times (D_BST_SW_S1 Schottky clamp is the hardware mitigation); each ramp step <= 5V (R-PON-05)", },
        "limits": {"voltage": "5 V above SW (DFT vset[bst2sw,5,...])", "compliance": "BD-05 OPEN", "rangeRule": "FPVIe_5V or FPVIe_10V (>= 2x 5V ceiling)"},
    },
]

# --------------------------------------------------------------------------------------
# 3b. sense / measurement plan per alias (requested by test-strategy-architect, t4)
#     Every entry below is a route published by SCH-Connect-Map; the CHOICE between the
#     differential candidates is left open for t4 (recorded, not silently picked).
# --------------------------------------------------------------------------------------
SENSE_PLAN = {
    "pmid2sw": {
        "current": {"instrument": "FPVIe0 (own MIRET)", "expression": "fabs(FPVI0.GetMeasResult(site, MIRET))",
                    "note": "R-VIR: use the measured current, never the programmed value",
                    "evidence": [ev("D:/PROJECT6-DALI/ForCodexDebug/source/sub.cpp", "sub.cpp:3266 Imeas1[site] = fabs(FPVI0.GetMeasResult(site, MIRET));"),
                                 E_DFT("TM600 measurements: MI on SW (A), 'R-VIR' note")]},
        "voltageDifferentialCandidateDisputed": {
            "instrument": "QVM channel 0 at S8 (S8_QVM_CH0+ / CH0-)",
            "status": "candidate, disputed with t2 - NOT the primary and NOT registered for this run",
            "isKelvinPair": False,
            "dispute": "t2 verdict (schematic-ir nonKelvinInstruments[QVMe]): 'CH0+ taps the FPVIe0 SH bus and reaches the PMID_F/S or PGND_F/S nets, CH0- reaches SW_S - one lead lands on a force net, so the pair is a mixed F/S pair, not a Kelvin sense pair' (invalidFor: mOhm Kelvin sense of TM600/TM601). The observation that motivated this candidate was connect-map L525 ('QVM is a 2-wire sense meter, CH0+/CH0- must each reach a measurement node') plus the published routes; the two readings cannot be reconciled from the current evidence. Registered as an unresolved evidence conflict for the relay-trace gate / t6. No unilateral upgrade to 'primary' in this contract.",
            "primaryStands": "form (a) - the FPVIe channel's own Kelvin pair - remains the primary candidate per the Captain ruling, which explicitly does not reopen on this observation.",
            "highNodeRoute": {"node": "PMID", "chain": "S8_QVM_CH0+ -> K137(ON) -> K83(ON) -> K84(NC) -> PMID", "closedRelayNumbers": [137, 83]},
            "lowNodeRoute": {"node": "SW", "chain": "S8_QVM_CH0- -> K138(ON) -> K60(ON) -> K61(ON) -> SW", "closedRelayNumbers": [138, 60, 61]},
            "claimedAdvantageIfAccepted": "one instrument, one differential reading across the 1A loop - the only candidate that does not subtract two independently referenced single-ended readings for an ~11 mV signal",
            "evidence": [E_CMAP("L525 QVM 2-wire note; L614-615 PMID <- QVM high; L620-621 SW <- QVM low"), E_IR("nonKelvinInstruments[QVMe]; paths[] S8_QVM_CH0+->PMID_F_S1 role=F / CH0-->SW_S_S1 role=S")],
            "openItem": "U10: QVM ch0 concurrent use while FPVIe0 forces the same nodes is NOT documented; relay sets are compatible (K83 / K60,K61 are shared, not exclusive) but instrument-level concurrency needs confirmation",
        },
        "voltageAlternativeA": {
            "instrument": "FPVIe0 own Kelvin sense pair (SH0/SL0) read as the channel's differential MVRET",
            "chain": "S1_FPVIe_SH0 -> K88(NC) -> K83(ON) -> K84(NC) -> PMID_S ; S1_FPVIe_SL0 -> K88(NC) -> K60(ON) -> K61(ON) -> SW_S",
            "caveat": "the FPVIe0 PC nets are board-shorted (FPVIe0_FH_PC<->SH_PC and FL_PC<->SL_PC) so any route through the PC nets is not true 4-wire Kelvin; the BUS route above is the one that keeps F and S distinct",
            "evidence": [E_CMAP("L165-167, L174-176"), E_IR("resourceConflicts.netShortGroups; hazards[kelvin-integrity]")],
        },
        "voltageAlternativeB": {
            "instrument": "two single-ended reads subtracted",
            "highNode": {"instrument": "FXVIe_PLUS PMID_HG2 group (S3_FH1/SH1)", "chain": "S3_FXVIe_PLUS_FH1 -> K84(NC) -> PMID_F (需闭合: 无, default conducting)"},
            "lowNode": {"instrument": "ACM200 S5_FH8/SH8", "chain": "S5_ACM200_FH8 -> K61(ON) -> SW_F (需闭合: K61)"},
            "precedent": "sub.cpp:3260-3266 (two single-ended MeasureVI(50,5) reads then MVRET subtraction) - the live precedent form",
            "weakness": "two different instruments referenced to AGND_F_S1; their offset mismatch is the same order as the 11 mOhm limit implies (~11 mV at 1 A)",
            "evidence": [E_CMAP("L771-773, L820-822"), ev("D:/PROJECT6-DALI/ForCodexDebug/source/sub.cpp", "sub.cpp:3260-3266")],
        },
    },
    "sw2pgnd": {
        "current": {"instrument": "FPVIe0 (own MIRET)", "expression": "fabs(FPVI0.GetMeasResult(site, MIRET))",
                    "note": "the DFT 'MI pin' string for TM601 is PMID_SW while the sense label is PGND-SW - record the divergence, use the measured current",
                    "evidence": [E_IR("items[TM601].measurements"), E_DFT("line 104: iset[sw2pgnd,1,1e-6,0] -> PGND-SW")]},
        "voltageDifferentialCandidateDisputed": {
            "instrument": "QVM channel 0 at S8 (S8_QVM_CH0+ / CH0-)",
            "status": "CANDIDATE - DISPUTED, NOT the primary and NOT registered for this run (t2: mixed F/S pair, not a Kelvin sense pair - see the pmid2sw entry for the full dispute record)",
            "isKelvinPair": False,
            "highNodeRoute": {"node": "PGND", "chain": "S8_QVM_CH0+ -> K137(ON) -> K154(ON) -> K155(ON) -> PGND", "closedRelayNumbers": [137, 154, 155]},
            "lowNodeRoute": {"node": "SW", "chain": "S8_QVM_CH0- -> K138(ON) -> K60(ON) -> K61(ON) -> SW", "closedRelayNumbers": [138, 60, 61]},
            "note": "the PGND terminal is tied to AGND through K93_AGND2PGND, so the loop return is a shared ground node (schematic-ir hazards[shared-resource])",
            "evidence": [E_CMAP("L610-611 PGND <- QVM high; L620-621 SW <- QVM low"), E_IR("resourceConflicts.agndPgndTie")],
        },
        "voltageAlternativeA": {
            "instrument": "FPVIe0 own Kelvin pair (SH0/SL0)",
            "chain": "S1_FPVIe_SH0 -> K88(NC) -> K154(ON) -> K155(ON) -> PGND_S ; S1_FPVIe_SL0 -> K88(NC) -> K60(ON) -> K61(ON) -> SW_S",
            "evidence": [E_CMAP("L156-158, L174-176")],
        },
    },
    "bst2sw": {
        "voltage": {"instrument": "FPVIe1 own Kelvin pair (SH1/SL1)",
                    "chain": "S1_FPVIe_SH1 -> K132(ON) -> K135(ON) -> BST_S ; S1_FPVIe_SL1 -> K132(ON) -> K135(ON) -> SW_S",
                    "note": "CH1 High->BST and CH1 Low->SW both list K132/K134/K135; the sense pair (K132/K135) and the force pair (K131/K134) are distinct wires, which is consistent with a merged [Kelvin] notation rather than a real short - to be proven by the relay-trace gate",
                    "evidence": [E_CMAP("L265-267, L391-393")]},
        "alternative": {"instrument": "QVM channel 0", "note": "no QVM group publishes a BST endpoint in section 4; only SW is reachable on CH0-, so QVM cannot read BST-SW differentially with the published routes.",
                        "evidence": [E_CMAP("列4: no BST <- QVM低端 row; SW <- QVM低端 at L620")]},
    },
}
# --------------------------------------------------------------------------------------
# 3c. sense reachability (Captain question set, t3 addendum 3)
# --------------------------------------------------------------------------------------
sense_reachability = {
    "questions": "1) are the FPVIe sense terminals reachable to both ends of the DFT Check pair? 2) if not, which instrument can read PMID/SW/PGND single-ended? 3) what is the F/S classification of the pair?",
    "apiFacts": {
        "FPVIe_OUT_RELAY": {"members": ["FPVIe_RELAY_HOLD", "FPVIe_RELAY_ON", "FPVIe_RELAY_OFF", "FPVIe_RELAY_SENSE_ON"],
                            "reachable": True,
                            "how": "FPVIe::Set(viMode, setValue, vRange, iRange, relayStatus = FPVIe_RELAY_HOLD, risingTime) accepts it as a parameter",
                            "evidence": [E_FPVIEH("FPVIe.h:29-35 enum FPVIe_OUT_RELAY; :86-91 Set(... FPVIe_OUT_RELAY relayStatus ...)")]},
        "FPVIe_CONTACTMODE": {"members": ["FPVIe_HIGH_SIDE", "FPVIe_LOW_SIDE", "FPVIe_ALL_SIDE"],
                              "reachable": True,
                              "how": "FPVIe::ContactCheck(FPVIe_CONTACTMODE) - contact check only, NOT a measurement-path selector",
                              "evidence": [E_FPVIEH("FPVIe.h:53-58 enum; :167 int ContactCheck(FPVIe_CONTACTMODE checkMode)")]},
        "FPVIe_RET_RESULT": {"members": ["FPVIe_MV", "FPVIe_MI", "FPVIe_HIGH_MV", "FPVIe_LOW_MV"],
                             "reachable": False,
                             "finding": "DECLARED BUT NOT REACHABLE through the public API: no FPVIe method takes FPVIe_RET_RESULT. GetMeasResult(siteCount, MeasRet retType = MVRET, ...) and BlockRead(...) take the generic MeasRet enum, whose only members are MEASTYPERET / MVRET / MIRET.",
                             "consequence": "a same-channel single-ended readback (FPVIe_HIGH_MV / FPVIe_LOW_MV) must NOT be planned for. Do not assume it works; treat as unavailable/UNKNOWN until a header shows a signature that accepts it.",
                             "evidence": [E_FPVIEH("FPVIe.h:60-66 enum FPVIe_RET_RESULT; :114-117 GetMeasResult(... MeasRet retType ...); :119-123 BlockRead(... MeasRet retType ...)"),
                                          ev("C:/AccoTEST/AccoTEST System/INCLude/ATDriverPackGlobal.h", "enum MeasRet { MEASTYPERET, MVRET, MIRET } (no HIGH_MV/LOW_MV member)")]},
        "projectUsage": {"measured": "0 occurrences of FPVIe_RELAY_SENSE_ON / FPVIe_CONTACTMODE / FPVIe_HIGH_MV / FPVIe_LOW_MV / FPVIe_RET_RESULT anywhere under D:/PROJECT6-DALI/ForCodexDebug/source (.cpp/.h, python walk)",
                         "note": "Test_Method.h:21 contains the string SENSE_ON only inside a comment about fovi_cap.Set"},
    },
    "q1_senseTerminalsReachable": {
        "answer": "YES - reachable for BOTH Check pairs, through the BUS route, and the connect-map classifies those groups [Kelvin].",
        "TM600_PMID_SW": {
            "highSideSenseTerminal": {"terminal": "SH0", "route": "S1_FPVIe_SH0 -> K88(Relay-NC) -> K83(Relay-ON) -> K84(Relay-NC) -> PMID_S",
                                      "relaysAndRequiredStates": [{"relay": "K88_KELVIN0_S1", "required": "KEEP DEFAULT - Relay-NC = default conducting; must NOT be SetOn (topology only)"},
                                                                 {"relay": "K83_BUSH_PMID", "required": "CLOSED (SetOn) - this is the only relay in the 需闭合 list"},
                                                                 {"relay": "K84_HG2_S1", "required": "KEEP DEFAULT - Relay-NC default-conducting; whether it must be OPENED while FPVIe owns PMID is open item U5"}],
                                      "actuationSet": [83], "topologyOnly": False,
                                      "evidence": E_CMAP("L165 group head 'CH0 High -> PMID [Kelvin] 需闭合: K83'; L167 sense detail line")},
            "lowSideSenseTerminal": {"terminal": "SL0", "route": "S1_FPVIe_SL0 -> K88(Relay-NC) -> K60(Relay-ON) -> K61(Relay-ON) -> SW_S",
                                     "relaysAndRequiredStates": [{"relay": "K88_KELVIN0_S1", "required": "KEEP DEFAULT - Relay-NC = default conducting; must NOT be SetOn (topology only)"},
                                                                {"relay": "K60_BUSL_VCP", "required": "CLOSED (SetOn)"},
                                                                {"relay": "K61_SW", "required": "CLOSED (SetOn)"}],
                                     "actuationSet": [60, 61], "topologyOnly": False,
                                     "evidence": E_CMAP("L174 group head 'CH0 Low -> SW [Kelvin] 需闭合: K60,K61'; L176 sense detail line")},
            "conclusion": "SH0 and SL0 both reach the two ends of the Check pair, so the channel's own differential reading (SH0-SL0) spans PMID-SW.",
        },
        "TM601_SW_PGND": {
            "highSideSenseTerminal": {"terminal": "SH0", "route": "S1_FPVIe_SH0 -> K88(Relay-NC) -> K154(Relay-ON) -> K155(Relay-ON) -> PGND_S",
                                      "relaysAndRequiredStates": [{"relay": "K88_KELVIN0_S1", "required": "KEEP DEFAULT - Relay-NC = default conducting; must NOT be SetOn (topology only)"},
                                                                 {"relay": "K154_BUSH_AMUX", "required": "CLOSED (SetOn)"},
                                                                 {"relay": "K155_FOVI_PGND", "required": "CLOSED (SetOn)"}],
                                      "actuationSet": [154, 155], "topologyOnly": False,
                                      "evidence": E_CMAP("L156 group head 'CH0 High -> PGND [Kelvin] 需闭合: K154,K155'; L158 sense detail line")},
            "lowSideSenseTerminal": {"terminal": "SL0", "route": "S1_FPVIe_SL0 -> K88(Relay-NC) -> K60(Relay-ON) -> K61(Relay-ON) -> SW_S", "evidence": E_CMAP("L176")},
            "conclusion": "same channel, sense terminals on PGND and SW respectively.",
        },
        "caveats": [
            "READING RULE: the chains above list relays that are ROUTED THROUGH, not relays to be closed. K87/K88/K89 (and K131/K132/K133) are Relay-NC default-conducting and must NOT be SetOn; the only relays to close are the actuationSet of each route. Reading K88 as 'to be closed' would collapse the 4-wire measurement to 2-wire.",
            "K88_KELVIN0 carries BOTH SH0 and SL0 (L167 and L176) - one KELVIN0 sense relay serves both poles of channel 0. Consistent with a 2-pole part, but it is the reason a per-pole SENSE_ON handshake cannot be assumed.",
            "The route must be the BUS route. The PC route (K90/K91 + R1_CS 100mohm / R2_CS 5mohm) is a different path and is board-shorted F/S.",
            "SENSE_ON / CONTACTMODE are callable but unused by this project (0 hits), so switching the sense path is not exercised by any existing test - treat the first use as unvalidated behaviour.",
        ],
    },
    "q2_singleEndedAlternatives": {
        "answer": "Provided for completeness; they are only needed if the FPVIe sense path is rejected.",
        "PMID": [{"instrument": "FXVIe_PLUS PMID_HG2 group (S3_FH1/SH1)", "route": "S3_FXVIe_PLUS_FH1 -> K84(Relay-NC) -> PMID_F", "needsClosed": [], "line": 820},
                 {"instrument": "QVM ch0+ (S8_QVM_CH0+)", "route": "S8_QVM_CH0+ -> K137(ON) -> K83(ON) -> K84(NC) -> PMID", "needsClosed": [137, 83], "line": 614},
                 {"instrument": "ACM200", "route": "none - no ACM200 PMID group exists in SCH-Connect-Map (measured)", "needsClosed": None, "line": None}],
        "SW": [{"instrument": "ACM200 S5_FH8/SH8", "route": "S5_ACM200_FH8 -> K61(Relay-ON) -> SW_F", "needsClosed": [61], "line": 771},
               {"instrument": "QVM ch0- (S8_QVM_CH0-)", "route": "S8_QVM_CH0- -> K138(ON) -> K60(ON) -> K61(ON) -> SW", "needsClosed": [138, 60, 61], "line": 620},
               {"instrument": "FXVIe_PLUS", "route": "the SW1_SW2_FXVI group does NOT cover the SW pin (testerChannels note: 'the SW pin itself is NOT on this channel')", "needsClosed": None, "line": None}],
        "PGND": [{"instrument": "FXVIe_PLUS PGND group (S3_FH3/SH3)", "route": "S3_FXVIe_PLUS_FH3 -> K155(Relay-ON) -> PGND_F", "needsClosed": [155], "line": 817},
                 {"instrument": "QVM ch0+ (S8_QVM_CH0+)", "route": "S8_QVM_CH0+ -> K137(ON) -> K154(ON) -> K155(ON) -> PGND", "needsClosed": [137, 154, 155], "line": 610},
                 {"instrument": "ACM200", "route": "none - no ACM200 PGND group exists in SCH-Connect-Map (measured)", "needsClosed": None, "line": None}],
        "sameChannelSingleEnded": "NOT AVAILABLE - see apiFacts.FPVIe_RET_RESULT (MeasRet has no HIGH_MV/LOW_MV member).",
    },
    "q3_fsClassification": {
        "answer": "Both Check pairs are [Kelvin] on the BUS route, so a four-wire differential Delta-V IS permissible there.",
        "pairs": [
            {"pair": "PMID (TM600, CH0 High)", "classification": "[Kelvin]", "forceLine": "S1_FPVIe_FH0 -> K87 -> K83 -> K84 -> PMID_F", "senseLine": "S1_FPVIe_SH0 -> K88 -> K83 -> K84 -> PMID_S", "verdict": "4-wire OK on this route"},
            {"pair": "SW (TM600 low end / TM601 low end, CH0 Low)", "classification": "[Kelvin]", "forceLine": "S1_FPVIe_FL0 -> K89 -> K60 -> K61 -> SW_F", "senseLine": "S1_FPVIe_SL0 -> K88 -> K60 -> K61 -> SW_S", "verdict": "4-wire OK on this route"},
            {"pair": "PGND (TM601 high end, CH0 High)", "classification": "[Kelvin]", "forceLine": "S1_FPVIe_FH0 -> K87 -> K154 -> K155 -> PGND_F", "senseLine": "S1_FPVIe_SH0 -> K88 -> K154 -> K155 -> PGND_S", "verdict": "4-wire OK on this route"},
        ],
        "counterExamples": [
            "PC route: FPVIe0_FH_PC_S1 <-> FPVIe0_SH_PC_S1 and FPVIe0_FL_PC_S1 <-> FPVIe0_SL_PC_S1 are DIRECT_WIRE board shorts (schematic-ir resourceConflicts.netShortGroups) => [PC短接]; a Delta-V taken there is a two-wire reading.",
            "CH0 Low -> AGND is [单线-仅SL] and CH0 Low -> VDM is [单线-仅FL] (flagged in the connect map as 'F/S未同时连通,非有效通路') - neither is in the two Check pairs, but the same notation would invalidate a differential if it appeared.",
        ],
        "extraConstraint": "R_PMID_KLV_S1 / R_SW1_KLV_S1 are 10kohm rows in series with the Kelvin sense path (schematic-ir unresolvedTopology U2) - classification unaffected, but the sense-input tolerance is unconfirmed by hardware.",
    },
    "recommendationForT4": {
        "optionA": "FPVIe0 own Kelvin differential (SH0-SL0) via the BUS route - [Kelvin] at BOTH ends of both Check pairs and uses the instrument already forcing the loop (this is the only candidate with a same-instrument differential).",
        "optionB": "two-instrument single-ended subtraction (FXVIe_PLUS PMID_HG2 + ACM200 S5_FH8 for SW) - live precedent (sub.cpp:3260-3266) but mixes two AGND-referenced instruments whose offsets are the same order as the ~11 mV signal.",
        "optionC": "QVM ch0 single-instrument differential (S8_QVM_CH0+/CH0-) - CANDIDATE, DISPUTED: t2 rates the pair as a mixed F/S landing (one lead on a force net) and therefore not a Kelvin sense pair, while connect-map L525 calls QVM a 2-wire sense meter; unresolved and referred to the relay-trace gate / t6. NOT recommended, and NOT a fallback for this run.",
        "decisionOwner": "test-strategy-architect (t4). This contract states the evidence and the recommendation; it does not silently pick one. Recommended: optionA as the primary (Captain ruling, not reopened); optionC is a disputed candidate only.",
    },
}


# --------------------------------------------------------------------------------------
# 3d. Kelvin routing decision, polarity decision, legacy K conversion (t3 addendum 4)
# --------------------------------------------------------------------------------------
kelvin_routing_decision = {
    "ruling": "The 10 mOhm / 7.5 mOhm items MUST use the BUS Kelvin route (K87/K88/K89 for FPVIe0, K131/K132/K133 for FPVIe1). The PC route (K90/K91 + K82_R_CS) is FORBIDDEN for these items.",
    "whyForbidden": {
        "seriesShunts": "the PC route runs the bus current through the on-board shunts R1_CS_S1 = 100 mohm +-1% and R2_CS_S1 = 5 mohm +-1% (schematic-ir hazards[measurement-validity])",
        "quantitative": "at 1 A the 100 mohm shunt alone drops 100 mV - 9x the TM600 signal (11 mohm x 1 A = 11 mV) and 13x the TM601 signal (7.5 mV); the 5 mohm shunt alone is 45-67% of the signal",
        "kelvinLoss": "FPVIe0_FH_PC_S1 <-> FPVIe0_SH_PC_S1 and FPVIe0_FL_PC_S1 <-> FPVIe0_SL_PC_S1 are DIRECT_WIRE board shorts, so the PC route is not 4-wire at all",
        "evidence": [E_IR("hazards[measurement-validity]; hazards[kelvin-integrity]; resourceConflicts.netShortGroups"), E_CMAP("列2 groups used by the BUS route")],
    },
    "perItemKelvinRoute": {
        "TM600_PMID_SW": {
            "forceRoute": {"high": "S1_FPVIe_FH0 -> K87(NC) -> K83(ON) -> K84(NC) -> PMID_F", "low": "S1_FPVIe_FL0 -> K89(NC) -> K60(ON) -> K61(ON) -> SW_F"},
            "senseRoute": {"high": "S1_FPVIe_SH0 -> K88(NC) -> K83(ON) -> K84(NC) -> PMID_S", "low": "S1_FPVIe_SL0 -> K88(NC) -> K60(ON) -> K61(ON) -> SW_S"},
            "kelvinRelays": [87, 88, 89], "evidence": [E_CMAP("L165-167 (PMID), L174-176 (SW)")],
        },
        "TM601_SW_PGND": {
            "forceRoute": {"high": "S1_FPVIe_FH0 -> K87(NC) -> K154(ON) -> K155(ON) -> PGND_F", "low": "S1_FPVIe_FL0 -> K89(NC) -> K60(ON) -> K61(ON) -> SW_F"},
            "senseRoute": {"high": "S1_FPVIe_SH0 -> K88(NC) -> K154(ON) -> K155(ON) -> PGND_S", "low": "S1_FPVIe_SL0 -> K88(NC) -> K60(ON) -> K61(ON) -> SW_S"},
            "kelvinRelays": [87, 88, 89, 154, 155], "evidence": [E_CMAP("L156-158 (PGND), L174-176 (SW)")],
        },
    },
    "terminatingInstrument": {
        "answer": "BOTH forms exist; the BUS Kelvin route terminates on the FPVIe channel's OWN sense terminals.",
        "fpvieSenseTerminals": {"terminal": "SH0 / SL0 of FPVIe0 (FH0/FL0 are the force terminals)",
                                "componentEvidence": "K86_KELVIN0_F_S1 and K86_KELVIN0_S_S1 are two separate TLP3412 parts (force and sense); K87_KELVIN0_S1S2 joins FPVIe0_FH_BUS_S1 to K86_F; K88_KELVIN0_S1 joins BOTH FPVIe0_SH_BUS_S1 and FPVIe0_SL_BUS_S1 to K86_S; K89_KELVIN0_S1S2 joins FPVIe0_FL_BUS_S1 to K86_S - the [Kelvin] F/S split is two independent relays, not a merged pair",
                                "evidence": [ev("project/DALI/Dali-SCH.csv", "component rows K86_KELVIN0_F_S1 / K86_KELVIN0_S_S1 (TLP3412) and K87/K88/K89 (IM06DJR) with their net members")]},
        "independentVoltmeter": {"instrument": "QVM ch0 at S8 (2-wire sense meter, connect-map L525)",
                                 "highNode": "S8_QVM_CH0+ -> K137(ON) -> K83(ON) -> K84(NC) -> PMID (TM600) | -> K137,K154,K155 -> PGND (TM601)",
                                 "lowNode": "S8_QVM_CH0- -> K138(ON) -> K60(ON) -> K61(ON) -> SW",
                                 "note": "the QVM route reuses the SAME BUS relays (K83 / K60,K61): an independent METER on the same Kelvin BUS, not an independent route",
                                 "evidence": [E_CMAP("L525, L610-611, L614-615, L620-621")]},
        "noAcmVdmTerminalOnTheseNodes": "no ACM200 group exists for PMID or PGND (measured); ACM200 reaches SW only (S5_FH8/SH8 -> K61). The ACM/VDM-class single-ended option therefore covers SW only.",
    },
    "tenKiloOhmKelvinRowDisposition": {
        "measuredTopology": "R_PMID_KLV_S1 = 10K between NetCap1_PMID_S1_1 (PMID rail node: PMID_F_S1 / Cap1_PMID / K84 pin2 / K85 / TP_PMID_F) and NetK84_HG2_S1_7 (K84 pin 7). No Kelvin series resistor exists for the SW pin itself: R_SW1_KLV_S1 = 11K and R_SW2_KLV_S1 = 10K belong to SW1/SW2 (K49 poles). The same rail-tap pattern repeats on VBAT 11K, VCC 12K, VBUS 10K, V1P5 10K, SCL 11K.",
        "evidence": [ev("project/DALI/Dali-SCH.csv", "R_PMID_KLV_S1 value 10K, net members NetCap1_PMID_S1_1 + NetK84_HG2_S1_7; R_SW1_KLV_S1 11K on NetCap_SW1_BST1_S1_2 + NetK49_ACM_SW2_S1_2")],
        "openBothDirections": [
            "if the sense line enters PMID through the K84 rail pole (pin 2), the 10 kOhm is NOT in series with the sense path and the row is harmless",
            "if it enters through K84 pin 7, the 10 kOhm IS in series and the row is compatible only with a high-impedance input",
        ],
        "quantitativeCompatibilityBound": {
            "TM600": "signal = 11 mohm x 1 A = 11 mV; a 1% error budget (0.11 mV) allows I_bias <= 11 nA; a 1 uA-class bias would add 10 mV (~90% of the signal)",
            "TM601": "signal = 7.5 mohm x 1 A = 7.5 mV; 1% budget = 75 uV allows I_bias <= 7.5 nA",
            "conclusion": "the disposition is a numeric condition on the sense-input bias current, which is not published in this workspace",
        },
        "disposition": "Route selection does not depend on this row (the BUS route is mandatory either way). Required: (1) resolve the K84 pole question by pole-level net trace or on hardware, (2) obtain the sense-input bias-current spec, (3) if the input is uA-class, prefer a route that does not traverse the tap. Registered as open item U2b with the bound above - not waved through.",
    },
}

polarity_decision = {
    "ruling": "The forced pin pair and direction stay as DFT intent: TM600 force/sense across PMID<->SW; TM601 across SW<->PGND. The sign is never silently inverted.",
    "deviceLevelImplementation": {
        "TM600": {"channel": "FPVIe0 (site1 channel S1_0)", "highSideBus": "FPVIe0_FH_BUS_S1 / _SH_BUS_S1", "lowSideBus": "FPVIe0_FL_BUS_S1 / _SL_BUS_S1",
                  "highTerminalTo": "PMID", "lowTerminalTo": "SW", "closedRelays": [83, 60, 61],
                  "satisfiesDftBecause": "DFT iset[pmid2sw,1,...] with PMID on the high terminal drives current out of the high terminal into PMID, through the HS FET to SW, and back into the low terminal - pair and device (BD-03: 0x5A=0x02, HS path) agree."},
        "TM601": {"channel": "FPVIe0 (site1 channel S1_0)", "highSideBus": "FPVIe0_FH_BUS_S1 / _SH_BUS_S1", "lowSideBus": "FPVIe0_FL_BUS_S1 / _SL_BUS_S1",
                  "highTerminalTo": "PGND", "lowTerminalTo": "SW", "closedRelays": [154, 155, 60, 61],
                  "satisfiesDftBecause": "the SW<->PGND pair is satisfied and the low-side FET (BD-03: 0x5A=0x01, LS path) is the device under test; which way current flows through it depends on the FI sign convention (below).",
                  "cannotSwapTerminals": "PGND is published only on the HIGH side of both FPVIe channels (CH0 L156, CH1 L376) and SW only on the LOW side (CH0 L174, CH1 L391); no published group puts PGND on a low bus or SW on a high bus, so the terminal assignment is fixed by the netlist and direction can only be set by the FI sign."},
    },
    "signConventionFinding": {
        "status": "CLOSED by captain ruling - implement the DFT literal direction, derive the command sign, do NOT flip silently and do NOT escalate to the user; verified at bring-up as U11.",
        "captainRuling": "1) implement strictly the DFT literal direction (pmid2sw = PMID->SW, sw2pgnd = SW->PGND) and derive the required COMMAND sign from the instrument's HIGH/LOW terminal assignment; 2) never invert silently or on intuition, and raise no wiring blocking decision for this; 3) no user escalation: this delivery is code + compilation, the direction semantics cannot be adjudicated before bring-up, R = |dV|/|dI| is magnitude-only, and for a conducting MOSFET the channel conducts both ways so the direction only changes the BODY-DIODE state - which device conducts is already fixed by the BD-03 0x5A bit (HS 0x02 / LS 0x01); 4) register as U11 bring-up verification with the three criteria below.",
        "derivationChain": {
            "step1_aliasDirection": {"TM600": "pmid2sw = PMID -> SW", "TM601": "sw2pgnd = SW -> PGND"},
            "step2_instrumentTerminals": {"TM600": "FPVIe0 CH0: HIGH terminal = PMID (K83), LOW terminal = SW (K60,K61)",
                                          "TM601": "FPVIe0 CH0: HIGH terminal = PGND (K154,K155), LOW terminal = SW (K60,K61)"},
            "step3_commandSign": {"TM600": "+1 A (DFT literal) - assumed convention: positive FI drives current out of the HIGH terminal, so PMID -> SW through the DUT is the physical result",
                                  "TM601": "-1 A (derived, NOT the DFT literal +1 A) - to obtain SW -> PGND with PGND on the HIGH terminal the command must take the opposite sign"},
            "assumptionToVerify": "the convention 'positive FI = current out of the HIGH terminal' is inferred from the golden case (PMID on the high terminal with iset[pmid2sw,1A] driving the HS FET); it is NOT stated in any header or manual in this workspace, so it is the U11 bring-up check, not an established fact.",
            "whereItMustAppear": "this three-step chain must be reproduced verbatim in the test plan and the implementation manifest so t6 can review the sign derivation.",
        },
        "requiredBringUpCheck": "at first bring-up confirm (i) the FET enabled by BD-03 is the one conducting, (ii) |MVRET|/|MIRET| lands near 11 mohm (TM600) / 7.5 mohm (TM601) rather than a body-diode drop (~0.6-0.7 V), (iii) MIRET magnitude matches the programmed value. If the driven device is wrong, flip the sign FOR THAT ITEM ONLY, record the evidence and report it - a targeted correction with hardware evidence, not an a-priori guess.",
        "escalation": "explicitly NOT escalated to the user (captain ruling); recorded as U11 in openItems and in the final report's limitations.",
    },
    "rCalculation": "R = |dV| / |dI|, so sign does not change the reported R; it decides which FET conducts, which is why it must match the DFT.",
}

legacy_k_map = {
    "note": "knowledge-base documents still use the previous board revision's numbers (schematic-ir hazards[legacy-numbering]). Current equivalents measured from SCH-Connect-Map and Dali-SCH.csv component rows:",
    "mapping": [
        {"legacy": "K31_BUS_PMID / K31_VBUSL_PMID", "current": "K83_BUSH_PMID_S1", "evidence": "SCH-Connect-Map L165; Dali-SCH.csv K83 nets include FPVIe0_FH_BUS_S1"},
        {"legacy": "K15_BUS_SW", "current": "K60_BUSL_VCP_S1 + K61_SW_S1", "evidence": "SCH-Connect-Map L174 - SW needs both the BUSL node (K60) and the SW select (K61)"},
        {"legacy": "K17_BUS_BST / K17_BUSH_SW", "current": "K46_BUS_FH_SW1 + K48_AMP_REF + K76_ACM_BST (FPVIe0 CH0 high) or K109_BUSL_PB0 + K110_BST (FPVIe1 CH1 low)", "evidence": "SCH-Connect-Map L39 and L268"},
        {"legacy": "K33_PGND", "current": "K154_BUSH_AMUX_S1 + K155_FOVI_PGND_S1", "evidence": "SCH-Connect-Map L156"},
        {"legacy": "K18_BST_SW_Cap", "current": "K57_CAP_BST_SW_S1S2", "evidence": "SCH-Connect-Map L904"},
        {"legacy": "K30_VBAT_Cap", "current": "K13_VBAT_Cap_S1S2", "evidence": "SCH-Connect-Map 稳压 section L902-905"},
        {"legacy": "BTST_ACM / PMID_FOVI (golden source/instrument names)", "current": "none - old-generation instrument bindings; the current tree reaches BST/SW through the BUS relays above and ACM200 S5 channels", "evidence": "0 hits for BTST_ACM / PMID_FOVI under D:/PROJECT6-DALI/ForCodexDebug/source"},
        {"legacy": "tm600.sv isrcSW / tm601.sv isrcPMID_SW", "current": "not used; ATE stimuli are the DFT vset/iset rows mapped through the alias table", "evidence": "tm600.sv:38-39, tm601.sv:33-34"},
    ],
    "rule": "Any K number quoted from knowledge/, goldens or _archive must be converted through this table before it reaches code.",
}

# --------------------------------------------------------------------------------------
# 3e. sense-form decision (t3 addendum 5): project-side relay names + the three questions
# --------------------------------------------------------------------------------------
relay_name_map = {
    "source": "D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h (python plaintext read)",
    "finding": "One relay NUMBER can carry TWO project-side names because the part is 2-pole (one pole per force/sense line). This is why a single number such as K88 serves both SH and SL in the netlist.",
    "entries": [
        {"number": 83, "stdafx": ["K83_BUSH0_PMID"], "netlist": ["K83_BUSH_PMID_S1"], "role": "PMID BUS (high domain)", "evidence": "StdAfx.h:246; SCH-Connect-Map L165"},
        {"number": 84, "stdafx": ["K84_FOVI1_HG2"], "netlist": ["K84_HG2_S1"], "role": "PMID default FXVIe_PLUS route (Relay-NC default-conducting)", "evidence": "StdAfx.h:247; SCH-Connect-Map L72/L820-822"},
        {"number": 85, "stdafx": ["K85_CAP_PMID"], "netlist": ["K85_CAP_PMID_S1S2"], "role": "PMID stabiliser cap gate", "evidence": "StdAfx.h:248; SCH-Connect-Map L902"},
        {"number": 86, "stdafx": ["K86_FPVI0_H_SHORT", "K86_FPVI0_L_SHORT"], "netlist": ["K86_KELVIN0_F_S1", "K86_KELVIN0_S_S1"], "role": "FPVI0 force/sense short hooks (two poles: H and L) - the 2-wire mode hooks", "evidence": "StdAfx.h:249-250; Dali-SCH.csv rows K86_KELVIN0_F_S1 / K86_KELVIN0_S_S1 (TLP3412), each with nets to K87/K88 and K88/K89 respectively"},
        {"number": 87, "stdafx": ["K87_FPVI0_FH_SL_SHORT"], "netlist": ["K87_KELVIN0_S1S2"], "role": "FPVI0 FH/SL short hook AND the FH force path relay; netlist nets = FPVIe0_FH_BUS_S1 + K86_F + its own pin 4", "evidence": "StdAfx.h:251; Dali-SCH.csv K87_KELVIN0_S1S2 nets; SCH-Connect-Map L166 (FH0 -> K87 -> K83 -> ... -> PMID_F)"},
        {"number": 88, "stdafx": ["K88_FPVI0_Sense_FLOAT"], "netlist": ["K88_KELVIN0_S1"], "role": "FPVI0 sense relay - the name says the SENSE pair is allowed to FLOAT; netlist nets = FPVIe0_SH_BUS_S1 AND FPVIe0_SL_BUS_S1 + K86_F + K86_S", "evidence": "StdAfx.h:252; Dali-SCH.csv K88_KELVIN0_S1 nets; SCH-Connect-Map L167/L176 (SH0 -> K88 -> ... -> PMID_S / SW_S)"},
        {"number": 89, "stdafx": ["K89_FPVI0_FL_SH_SHORT"], "netlist": ["K89_KELVIN0_S1S2"], "role": "FPVI0 FL/SH short hook AND the FL force path relay", "evidence": "StdAfx.h:253; SCH-Connect-Map L175"},
        {"number": 90, "stdafx": ["K90_FPVI0_PC_Force"], "netlist": ["K90_PC0_Force_S1"], "role": "FPVI0 instrument-side (PC) FORCE route relay - PC nets are F/S board-shorted and carry R1_CS 100mohm", "evidence": "StdAfx.h:254; schematic-ir hazards[kelvin-integrity], resourceConflicts.netShortGroups"},
        {"number": 91, "stdafx": ["K91_FPVI0_PC_Sense"], "netlist": ["K91 (no designator row found in the schematic CSV relay rows)"], "role": "FPVI0 instrument-side (PC) SENSE route relay", "evidence": "StdAfx.h:255; absent from the netlist relay rows, so the project header is the only source"},
        {"number": 92, "stdafx": ["K92_AGND_F2S_SHORT"], "netlist": ["K92_KELVIN0 ... (AGND force-to-sense short)"], "role": "AGND force-to-sense short hook", "evidence": "StdAfx.h:256"},
        {"number": 93, "stdafx": ["K93_AGND2PGND_SHORT"], "netlist": ["K93_AGND2PGND_S1"], "role": "AGND <-> PGND tie", "evidence": "StdAfx.h:257; schematic-ir resourceConflicts.agndPgndTie"},
        {"number": 130, "stdafx": ["K130_FPVI1_H_SHORT", "K130_FPVI1_L_SHORT"], "netlist": ["K130_KELVIN1_F_S1", "K130_KELVIN1_S_S1"], "role": "FPVI1 short hooks (two poles)", "evidence": "StdAfx.h:303-304"},
        {"number": 131, "stdafx": ["K131_FPVI1_FH_SL_SHORT"], "netlist": ["K131_KELVIN1_S1S2"], "role": "FPVI1 FH/SL short hook + FH force path", "evidence": "StdAfx.h:305; SCH-Connect-Map L266"},
        {"number": 132, "stdafx": ["K132_FPVI1_Sense_FLOAT"], "netlist": ["K132_KELVIN1_S1"], "role": "FPVI1 sense relay (sense pair may float); netlist nets = FPVIe1_SH_BUS_S1 AND FPVIe1_SL_BUS_S1", "evidence": "StdAfx.h:306; Dali-SCH.csv K132_KELVIN1_S1 nets; SCH-Connect-Map L267/L393"},
        {"number": 133, "stdafx": ["K133_FPVI1_FL_SH_SHORT"], "netlist": ["K133_KELVIN1_S1S2"], "role": "FPVI1 FL/SH short hook + FL force path", "evidence": "StdAfx.h:307; SCH-Connect-Map L392"},
        {"number": 134, "stdafx": ["K134_FPVI1_PC_Force"], "netlist": ["K134_PC1_Force_S1"], "role": "FPVI1 instrument-side (PC) force route", "evidence": "StdAfx.h:308; SCH-Connect-Map L266/L392"},
        {"number": 135, "stdafx": ["K135_FPVI1_PC_Sense"], "netlist": ["K135_PC1_Sense_S1"], "role": "FPVI1 instrument-side (PC) sense route", "evidence": "StdAfx.h:309; SCH-Connect-Map L267/L393"},
    ],
    "implication": "The FPVI0/FPVI1 block is a mode-selection network: the *_SHORT hooks (K86/K87/K89 and K130/K131/K133) are the local 2-wire hooks (they tie force to sense at the instrument side), the sensed pair is released by the *_Sense_FLOAT relay (K88/K132), and K90/K91 (K134/K135) are the instrument-side PC force/sense route through the current-sense shunts. Remote 4-wire Kelvin therefore requires the FLOAT relay in its sense-releasing state and the SHORT hooks NOT acting as shorts - which is exactly the state the SDK's FPVIe_RELAY_SENSE_ON is meant to command.",
}

sense_form_decision = {
    "question": "Is the FPVIe self-MVRET form (a) or the two-single-ended-subtraction form (b) the valid sense form for the mOhm items?",
    "status": "PENDING - deliberately left as an explicit, single, decidable slot (see criterion). t4 may publish its sense-instrument slot as PENDING and t5 can use the same skeleton; this item does not block the rest of the contract.",
    "a_connectivity": {
        "question": "Do the FPVI0 sense terminals land on the PMID/SW PINS (true Kelvin) or only on the instrument-side PC nets?",
        "answer": "They land on the DUT PINS, through the sense relay whose project name is FPVI0_Sense_FLOAT.",
        "evidence": [
            "SCH-Connect-Map L167: S1_FPVIe_SH0 -> K88(Relay-NC) -> K83(Relay-ON) -> K84(Relay-NC) -> PMID_S",
            "SCH-Connect-Map L176: S1_FPVIe_SL0 -> K88(Relay-NC) -> K60(Relay-ON) -> K61(Relay-ON) -> SW_S",
            "SCH-Connect-Map L158: S1_FPVIe_SH0 -> K88(Relay-NC) -> K154(Relay-ON) -> K155(Relay-ON) -> PGND_S",
            "StdAfx.h:252 names K88 as FPVI0_Sense_FLOAT, i.e. the sense pair is meant to FLOAT while the DUT-side Kelvin pins carry it",
            "Dali-SCH.csv: K88_KELVIN0_S1 nets = FPVIe0_SH_BUS_S1 + FPVIe0_SL_BUS_S1 + K86_F + K86_S (2-pole part; both sense BUS wires)",
            "contrast: StdAfx.h:254-255 name K90/K91 as FPVI0_PC_Force / FPVI0_PC_Sense, and the PC nets are the board-shorted, shunt-carrying route (schematic-ir netShortGroups: FPVIe0_FH_PC_S1 <-> FPVIe0_SH_PC_S1 and FL_PC <-> SL_PC, DIRECT_WIRE)",
        ],
        "conclusion": "Remote Kelvin at the DUT pins is physically available; the PC route is a different, F/S-shorted path that must not be used.",
        "residualUnknown": "Whether the state that actually releases the sense pair is commanded by FPVIe_RELAY_SENSE_ON, or by explicitly driving K88/K90/K91, is NOT stated anywhere in the workspace (see c).",
    },
    "b_singleEndedPerNode": {
        "PMID": [{"instrument": "FXVIe_PLUS PMID_HG2 (S3_FH1/SH1)", "route": "-> K84(Relay-NC, default conducting) -> PMID", "needsClosed": [], "line": 820},
                 {"instrument": "QVM ch0+ (S8_QVM_CH0+)", "route": "-> K137(ON) -> K83(ON) -> K84(NC) -> PMID", "needsClosed": [137, 83], "line": 614},
                 {"instrument": "ACM200", "route": "none - no ACM200 PMID group exists", "needsClosed": None, "line": None}],
        "SW": [{"instrument": "ACM200 S5_FH8/SH8", "route": "-> K61(Relay-ON) -> SW_F/S", "needsClosed": [61], "line": 771},
               {"instrument": "QVM ch0- (S8_QVM_CH0-)", "route": "-> K138(ON) -> K60(ON) -> K61(ON) -> SW", "needsClosed": [138, 60, 61], "line": 620},
               {"instrument": "FXVIe_PLUS", "route": "the SW1_SW2_FXVI group does not cover the SW pin", "needsClosed": None, "line": None}],
        "PGND": [{"instrument": "FXVIe_PLUS PGND group (S3_FH3/SH3)", "route": "-> K155(Relay-ON) -> PGND_F/S", "needsClosed": [155], "line": 817},
                 {"instrument": "QVM ch0+ (S8_QVM_CH0+)", "route": "-> K137,K154,K155 -> PGND", "needsClosed": [137, 154, 155], "line": 610},
                 {"instrument": "ACM200", "route": "none - no ACM200 PGND group exists", "needsClosed": None, "line": None}],
        "note": "form (b) is only as good as its grounding: the FXVIe_PLUS and ACM200 channels are both referenced to AGND_F_S1, so subtracting them still leaves a two-instrument offset mismatch unless both are read at their Kelvin points.",
    },
    "c_relayActionPerOutRelay": {
        "question": "What do FPVIe_RELAY_ON vs FPVIe_RELAY_SENSE_ON actually actuate inside the instrument?",
        "answer": "NOT DETERMINABLE from this workspace.",
        "whatIsProvable": [
            "the enum exists with four members (FPVIe_OUT_RELAY: HOLD / ON / OFF / SENSE_ON, FPVIe.h:29-35) and is passed to Set(...) as relayStatus (FPVIe.h:86-91)",
            "project source usage of FPVIe_RELAY_SENSE_ON = 0 occurrences (python walk of D:/PROJECT6-DALI/ForCodexDebug/source)",
            "the only RELAY_SENSE mention in the whole tree is a comment: Test_Method.h:21 'Change \"fovi_cap.Set\" from RELAY_SENSE_ON to RELAY_ON' - i.e. this project once deliberately moved FROM sense-on TO relay-on",
            "no header, manual mirror or knowledge file documents the per-member relay action of the FPVIe driver",
        ],
        "consequence": "the criterion the Captain stated is the correct one: with only RELAY_ON the self-MVRET may include lead + relay drops, and a few mOhm of parasitics is tens of percent of an 7.5-11 mOhm target - so form (a) is only valid if the remote sense is actually engaged.",
    },
    "decisionCriterion": {
        "if": "it can be shown (SDK manual mirror, vendor contact, or a first-article measurement) that FPVIe_RELAY_SENSE_ON engages the remote sense (K88/K132 FLOAT relays, SHORT hooks not shorting) - or that the same state is reached by explicitly driving K88 and keeping K86/K87/K89 non-shorting",
        "then": "form (a) FPVIe self-Kelvin MVRET is valid and is the primary sense form",
        "else": "form (a) is INVALID for the mOhm items and - after the corrected Delta-V ruling - this run has NO signed-off Delta-V form: the two-single-ended subtraction (b) is not deliverable without a signed-off instrument table, QTMU is excluded by the IR mitigation, and QVM ch0 is a DISPUTED candidate (t2: mixed F/S landing) rather than a fallback. That consequence is escalated to the Captain rather than papered over.",
        "eitherWay": "the PC route (K90/K91 + K82 + R1_CS/R2_CS) stays forbidden, and whichever form is chosen must be validated at bring-up by |MVRET|/|MIRET| landing near 11 / 7.5 mohm",
        "notBlocking": "this slot is explicitly PENDING; t4 may publish it as PENDING and t5 may reuse the same skeleton.",
    },
}


# --------------------------------------------------------------------------------------
# 3f. IR path cross-reference (t4 request: give path ids + relays, source-traceable)
# --------------------------------------------------------------------------------------
ir_path_crossref = {
    "purpose": "t4 asked for the sense/force paths by IR path id so the test plan can cite the same objects. These entries are read from schematic-ir.json paths[] (182 accepted, sourceType=FPVIe) of the revision recorded in inputs[].",
    "reconciliation": {
        "apparentConflict": "The IR path entries list only the ACTIONABLE relays ([83] for PMID, [60,61] for SW, [154,155] for PGND), while SCH-Connect-Map prints K87/K88/K89 in the same chains.",
        "resolution": "Not a conflict: K87_KELVIN0_S1S2 / K88_KELVIN0_S1 / K89_KELVIN0_S1S2 are Relay-NC = default conducting (connect-map L8-L19 '需闭合: 无(默认导通)'), so they appear in the [Kelvin] chain but are not part of the '需闭合' (must-SetOn) set. Both forms are recorded; neither is dropped.",
        "evidence": [E_IR("paths[] FPVIe entries (resources field)"), E_CMAP("L8-L19 default conducting; L165/L174/L156 需闭合 lists")],
    },
    "paths": [
        {"id": "S1_FPVIe_FH0->PMID_F_S1", "role": "F", "domain": "HIGH", "relays": [83], "confidence": "direct", "usedBy": "TM600 force (PMID end)"},
        {"id": "S1_FPVIe_SH0->PMID_S_S1", "role": "S", "domain": "HIGH", "relays": [83], "confidence": "direct", "usedBy": "TM600 sense (PMID end)"},
        {"id": "S1_FPVIe_FL0->SW_F_S1", "role": "F", "domain": "LOW", "relays": [60, 61], "confidence": "direct", "usedBy": "TM600/TM601 force (SW end)"},
        {"id": "S1_FPVIe_SL0->SW_S_S1", "role": "S", "domain": "LOW", "relays": [60, 61], "confidence": "direct", "usedBy": "TM600/TM601 sense (SW end)"},
        {"id": "S1_FPVIe_FH0->PGND_F_S1", "role": "F", "domain": "HIGH", "relays": [154, 155], "confidence": "direct", "usedBy": "TM601 force (PGND end)"},
        {"id": "S1_FPVIe_SH0->PGND_S_S1", "role": "S", "domain": "HIGH", "relays": [154, 155], "confidence": "direct", "usedBy": "TM601 sense (PGND end)"},
        {"id": "S1_FPVIe_FL1->SW_F_S1", "role": "F", "domain": "LOW", "relays": [133, 134], "confidence": "direct", "usedBy": "FPVIe1 alternative SW force"},
        {"id": "S1_FPVIe_SL1->SW_S_S1", "role": "S", "domain": "LOW", "relays": [132, 135], "confidence": "direct", "usedBy": "FPVIe1 alternative SW sense"},
        {"id": "S1_FPVIe_FH1->PGND_F_S1", "role": "F", "domain": "HIGH", "relays": [143, 144, 154, 155], "confidence": "direct", "usedBy": "FPVIe1 alternative PGND force"},
        {"id": "S1_FPVIe_SH1->PGND_S_S1", "role": "S", "domain": "HIGH", "relays": [136, 137, 154, 155], "confidence": "direct", "usedBy": "FPVIe1 alternative PGND sense"},
    ],
    "conclusionForT4": "both FPVIe0 F and S paths reach the DUT pins of each Check pair (PMID_F/PMID_S, SW_F/SW_S, PGND_F/PGND_S), all confidence=direct - the Kelvin routing question at fixture level is settled; only the driver-level sense-selection question (senseFormDecision.c) remains PENDING.",
    "excludedRoutes": [
        {"route": "FPVIe0 PC route (K87/K88/K90/K91 + K82_R_CS)", "why": "IR hazards[measurement-validity]: carries R1_CS_S1 100 mohm +-1% and R2_CS_S1 5 mohm +-1% on net FPVIe0_FL_PC_S1 - same order as the acceptance limits, so the shunt would dominate the result"},
        {"route": "QTMU default routes (PMID via S10_CH0_A + K83,K141; SW via S10_CH0_B + K60,K61,K142)", "why": "IR hazards[measurement-validity]: QTMU carries a single line with no Kelvin split (FL to machine ground) - fine for DC Iq/toggle work, invalid for a mOhm-level force/sense measurement. This is the second reason K141/K142 must be open when an FPVIe channel owns the pins."},
    ],
}


# --------------------------------------------------------------------------------------
# 3g. sense-form options after the Captain's (a)/(b) ruling, with net-level PC-route evidence
# --------------------------------------------------------------------------------------
sense_form_options = {
    "captainRuling": "DV-01: (a) FPVIe floating four-wire = implemented form; (b) = candidate only; QTMU variants BLOCKED for TM600 by K141/K142. Detail: the Delta-V PRIMARY is form (a) - the FPVIe floating four-wire pair. Form (b) is an ALTERNATE that is NOT deliverable for this run unless an instrument table with independent Kelvin splitting is first produced and the t2-vs-t3 disagreement about QVM is settled; the QTMU variant is blocked for TM600 by K141/K142. Either way the PC route stays forbidden. NOTE ON PROVENANCE: an earlier captain message in this run instructed that (b) become the fallback if (a)'s driver layer stayed unevidenced; that instruction was recorded here verbatim at the time and is now SUPERSEDED by this correction.",
    "pcRouteDefinition": {
        "operationRule": "A measurement may not traverse the PC nets. Operationally: close the BUS-side relays (K83 / K60,K61 / K154,K155), do NOT close K90_FPVI0_PC_Force or K91_FPVI0_PC_Sense, and do not leave K82_R_CS engaged.",
        "netEvidence": [
            "K90_PC0_Force_S1 nets: FPVIe0_FH_PC_S1, FPVIe0_FL_PC_S1, FPVIe0_SH_BUS_S1, FPVIe0_SL_BUS_S1, NetK87_KELVIN0_S1S2_4, NetK89_KELVIN0_S1S2_4",
            "K91_PC0_Sense_S1 nets: FPVIe0_FH_PC_S1, FPVIe0_FL_PC_S1, NetK88_KELVIN0_S1_4, NetK88_KELVIN0_S1_5, its own pins",
            "the shunts R1_CS_S1 100 mohm +-1% / R2_CS_S1 5 mohm +-1% sit on net FPVIe0_FL_PC_S1, which appears ONLY on K90/K91 (and K82) - not on K87/K88/K89",
        ],
        "namingDivision": "SCH-Connect-Map prints K87/K88/K89 inside the BUS [Kelvin] chains, and schematic-ir hazards[measurement-validity] lumps them together with K90/K91 as 'the PC route'. Measured division (authoritative): K87_FPVI0_FH_SL_SHORT and K89_FPVI0_FL_SH_SHORT are the BUS-side force relays that double as the local 2-wire short hooks, K88_FPVI0_Sense_FLOAT is the sense-release relay, and ONLY K90/K91 (+K82) connect the shunted PC nets. The IR's parenthetical is imprecise; this contract cites the net evidence.",
        "evidence": [ev("project/DALI/Dali-SCH.csv", "net membership of K90_PC0_Force_S1 / K91_PC0_Sense_S1 / K141_QTMU_BUSA_S1S2 / K142_QTMU_BUSB_S1S2"), ev("D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h", "StdAfx.h:249-255 FPVI0 relay names"), E_IR("hazards[measurement-validity]")],
    },
    "namedInstrumentsForFormB": [
        {"instrument": "S10_CH0_A (QTMU)", "paths": ["S10_CH0_A->PMID_S_S1 [83,86,141]", "S10_CH0_A->PGND_S_S1 [86,141,154,155]", "S10_CH0_A->AMUX_S_S1 [86,141,154]", "S10_CH0_A->PMID_F_S1 [83,141]"],
         "blocker": "every path carries K141", "verdict": "BLOCKED - see qtmuBridgeConflict and the IR hazard below", "evidence": [E_IR("paths[] from=S10_CH0_A")]},
        {"instrument": "S10_CH0_B (QTMU)", "paths": ["S10_CH0_B->SW_F_S1 [60,61,142]", "S10_CH0_B->VBUS_F_S1 [3,142]", "S10_CH0_B->VAC1_F_S1 [17,142]"],
         "blocker": "every path carries K142", "verdict": "BLOCKED - see qtmuBridgeConflict and the IR hazard below", "evidence": [E_IR("paths[] from=S10_CH0_B")]},
        {"instrument": "S8_QVM_CH0+ / CH0- (QVM)", "paths": ["S8_QVM_CH0+->PMID_F_S1 [83,86,137]", "S8_QVM_CH0+->PGND_F_S1 [86,137,154,155]", "S8_QVM_CH0- ->SW_S_S1 [60,61,138]"],
         "verdict": "NOT A KELVIN PAIR - the + leg lands on the FORCE pin (PMID_F_S1, role=F) while the - leg lands on the sense pin (SW_S_S1, role=S). A mixed F/S landing means one end carries the lead/relay drop, so it is not a valid Delta-V source for a 7.5-11 mOhm item.",
         "supersedes": "This contract's earlier phrasing that QVM is 'an independent meter on the same Kelvin BUS' assumed both legs land on sense pins. The IR path roles show otherwise; that phrasing is withdrawn.",
         "evidence": [E_IR("paths[] from=S8_QVM_CH0+: PMID_F_S1 role=F / PGND_F_S1 role=F; from=S8_QVM_CH0-: SW_S_S1 role=S")]},
        {"instrument": "FXVIe_PLUS PMID_HG2 (sense leg) + ACM200 S5_FH8/SH8 (sense leg)", "paths": ["S3_FXVIe_PLUS_SH1 -> PMID_S_S1 (relays [] - K84 is Relay-NC default conducting)", "S5_ACM200_SH8 -> SW_S_S1 (relays [61])", "for TM601: S3_FXVIe_PLUS_SH3 -> PGND_S_S1 (relays [155]) + S5_ACM200_SH8 -> SW_S_S1 (relays [61])"],
         "verdict": "AVAILABLE - both legs land on SENSE pins, so each read is a Kelvin-point single-ended read (no lead drop in the reading itself). The residual error is the offset mismatch between two independently referenced meters.",
         "note": "ALTERNATE, not a baseline: it needs no K141/K142 and no PC nets (live precedent sub.cpp:3260-3266), but per DV-01 the primary is still (a) and this form is only usable after a signed-off instrument table with independent Kelvin splitting exists.",
         "evidence": [E_IR("paths[] S3_FXVIe_PLUS_SH1->PMID_S_S1 relays=[] role=S dom=HIGH; S5_ACM200_SH8->SW_S_S1 relays=[61] role=S; S3_FXVIe_PLUS_SH3->PGND_S_S1 relays=[155] role=S")]},
    ],
    "qtmuExclusion": {
        "hazardId": "schematic-ir hazards[measurement-validity] (severity high, mitigationRequired, tmLinks TM600+TM601)",
        "verbatim": "QTMU low side is DGND and QTMU carries a single line (bus-topology.md 2.3: QTMU BUS has FH only, FL goes to machine ground, no Kelvin split). The default netlist routes for PMID (S10_CH0_A, K83+K141) and SW (S10_CH0_B, K60/K61/K142) are QTMU routes, which is fine for Iq/toggle DC work but invalid for a mOhm-level force/sense measurement.",
        "requiredMitigationVerbatim": "For TM600/TM601 use only FPVIe Kelvin routes; do not measure RDSON on the QTMU defaults.",
        "conclusion": "the IR's own mitigation agrees with the net-level finding: QTMU is excluded from the mOhm Delta-V slot for TM600/TM601.",
        "evidence": [E_IR("hazards[measurement-validity] requiredMitigation"), ev("project/DALI/Dali-SCH.csv", "K141/K142 net memberships")],
    },
    "qtmuBridgeConflict": {
        "finding": "Using a QTMU single-ended sense path for TM600 is NOT possible while TM600 also uses FPVIe1 for the BST-SW loop: every QTMU path needs K141 and/or K142, and those relays are hard-wired across the two FPVIe channels' BUS wires.",
        "netEvidence": ["K141_QTMU_BUSA_S1S2 nets = FPVIe0_FH_BUS_S1 + FPVIe1_FH_BUS_S1 + (QTMU line via K66_TMU_nQON)",
                        "K142_QTMU_BUSB_S1S2 nets = FPVIe0_FL_BUS_S1 + FPVIe1_FL_BUS_S1 + its own pin 3"],
        "consequence": "for TM600, closing K141 would tie PMID (on FPVIe0_FH_BUS) to BST (on FPVIe1_FH_BUS) - a direct 1 A/5 V path between two rails at different potentials. So the QTMU candidates listed above are blocked for TM600 unless FPVIe1 is freed (BST-SW demoted to the dual-ACM200 route) so that FPVIe1's BUS relays stay open.",
        "forTM601": "TM601 needs only one FPVIe channel (SW<->PGND 1 A on FPVIe0) and does not drive FPVIe1, so K141/K142 closure does not tie two live rails together - the QTMU candidates are usable there, subject to the IR's own warning that a QTMU line has no Kelvin split (its low side is machine ground).",
        "evidence": [ev("project/DALI/Dali-SCH.csv", "K141/K142 net memberships"), E_IR("hazards[shared-resource] K141/K142 bridge; resourceConflicts.fpvieChannelBudget")],
    },
    "perItemAvailability": {
        "TM600": {
            "a": "candidate (FPVIe0 SH0/SL0 via K83 / K60,K61) - blocked on senseFormDecision.c (driver layer)",
            "b_classic_two_instruments": "NOT DELIVERABLE for this run (ruling): the two-instrument sense-pin routes exist in the path list (S3_FXVIe_PLUS_SH1->PMID_S_S1 requiredOn [], S5_ACM200_SH8->SW_S_S1 requiredOn [61]) but have NOT been signed off as an instrument table with independent Kelvin splitting, and the two meters are independently referenced - so it cannot be used as the fallback in this run",
            "b_qtmu": "BLOCKED (K141 would tie PMID to BST while FPVIe1 runs the BST-SW loop; IR requiredMitigation says do not measure RDSON on the QTMU defaults; its routes also need the K86/K130 bridges that SD-2 keeps open)",
            "c_qvm_differential": "NOT A KELVIN PAIR and not registered - QVM lands on PMID_F (force net) at one end and SW_S (sense net) at the other",
        },
        "TM601": {
            "a": "candidate (FPVIe0 SH0/SL0 via K154,K155 / K60,K61) - blocked on senseFormDecision.c",
            "b_classic_two_instruments": "NOT DELIVERABLE for this run (same condition as TM600: S3_FXVIe_PLUS_SH3->PGND_S_S1 [155] + S5_ACM200_SH8->SW_S_S1 [61] exist but are unsigned)",
            "b_qtmu": "BLOCKED by the IR requiredMitigation for TM600/TM601 (same hazard tmLinks both items)",
            "c_qvm_differential": "NOT A KELVIN PAIR - S8_QVM_CH0+ lands on PGND_F (force net) and CH0- on SW_S (sense net): mixed F/S landing",
        },
    },
    "baselineDecision": "DV-01 (corrected): (a) = the implementation form (FPVIe floating four-wire, ruling already landed in test-plan.json and implemented in the t5 payload); (b) = ALTERNATE, deliverable only after the t2-vs-t3 disagreement about QVM is settled and an instrument table with independent Kelvin splitting is signed off; the QTMU variant is blocked for TM600 by K141/K142 (measured: those relays bridge FPVIe0_FH_BUS with FPVIe1_FH_BUS, and TM600 occupies both channels, so closing K141 would tie PMID to BST). The sense-instrument slot therefore stays PENDING (U9 bring-up criteria), and the PC route stays forbidden.",
    "aliasTableConvergence": "The alias table's (b) candidates are converged to the capability table in sensingDecisions.instrumentCapabilities: PMID/PGND single-ended Kelvin reads only from FPVIe or FXVIe_PLUS; SW single-ended Kelvin reads only from FPVIe or ACM200 (ACM200 is SW-only and limited to +-200 mA, so it may never carry the 1 A force); FXVIe_PLUS cannot form a floating pair across SW because its low side returns to AGND_F. S10_CH0_B and S8_QVM_CH0- are reachable to SW but are recorded as corroborating evidence only (QTMU: DGND single line and its routes depend on the K86/K130 bridges; QVM: one lead lands on a force net, so the pair is mixed F/S).",
}


# --------------------------------------------------------------------------------------
# 3h. sensing decisions SD-1..SD-5 (t2 sensing evidence) + PIN-attached relay policy
# --------------------------------------------------------------------------------------
sensing_decisions = {
    "evidenceBase": {
        "schematic-ir-sensing.json": "team/artifacts/acceptance-20260916-dali10/schematic-ir-sensing.json (python plaintext hash recorded in inputs[])",
        "schematic-ir-handoff.md": "team/artifacts/acceptance-20260916-dali10/schematic-ir-handoff.md (python plaintext hash recorded in inputs[])",
        "hashCaveat": "The sizes/digests quoted in the task mail (39,593 B / dc52dca4... and 82d566e1...) do NOT match the files on disk at build time (47,446 B and 11,374 B, mtimes 14:07:07 and 14:18:01). This contract pins the python/plaintext digests of the revisions actually read; the quoted values are withdrawn as stale.",
    },
    "decisions": [
        {"id": "SD-1", "severity": "high", "decision": "TM600 and TM601 must be separate functions: both need FPVIe channel 0 of the same site for the Kelvin force/sense pair, and TM600 additionally needs channel 1 for BST<->SW.",
         "why": "an FPVIe site provides only 2 independently floating channels; channelAllocationPerTm confirms TM600 uses channels 0+1 while TM601 uses channel 0.",
         "contractPlacement": "safetyInvariants + conflicts (parallel-site note) + tmDeltas(TM600/TM601).mutualExclusion",
         "evidence": [E_IR("schematic-ir-sensing.json channelAllocationPerTm; resourceConflicts.fpvieChannelBudget")]},
        {"id": "SD-2", "severity": "high", "decision": "Keep the force<->sense bridge relays OPEN for TM600/TM601: K86_KELVIN0_F_S1, K86_KELVIN0_S_S1 (FPVIe0) and K130_KELVIN1_F_S1, K130_KELVIN1_S_S1 (FPVIe1).",
         "why": "these bridges merge force and sense on their row: only QTMU/QVM proofs require them (K86 F/S used by 27 QTMU + 14 QVM proofs; K130 F/S by 33 QTMU + 18 QVM), while no FPVIe / ACM200 / FXVIe_PLUS 4-wire route needs any of them. Closing them silently degrades a 4-wire measurement to 2-wire.",
         "contractPlacement": "safetyInvariants",
         "evidence": [E_IR("schematic-ir-sensing.json forceSenseBridgeRelays")]},
        {"id": "SD-3", "severity": "high", "decision": "Keep K93_AGND2PGND OPEN during TM601 and state it explicitly in the cleanup block.",
         "why": "K93 SetOn ties AGND_F directly to PGND_F/PGND_S: the differential reference is shorted to AGND_F and the 1 A return would flow through the K93 contact.",
         "contractPlacement": "safetyInvariants + globalCleanup",
         "evidence": [E_IR("schematic-ir-sensing.json blockingDecisionsForStrategy SD-3; resourceConflicts.agndPgndTie")]},
        {"id": "SD-4", "severity": "medium", "decision": "Fix the loop orientation explicitly: PMID<->SW = channel 0 high(PMID) to low(SW); SW<->PGND = channel 0 low(SW) to high(PGND), i.e. PGND is the HIGH terminal.",
         "why": "PMID and PGND hang off FPVIe0_FH_BUS_S1 while SW hangs off FPVIe0_FL_BUS_S1; dfdPairVerdicts records SW<->PGND as an inverted orientation and fourWireProper=true. The dft-ir wording 'PMID(High)/SW(Low)' for TM601 is NOT applicable.",
         "contractPlacement": "polarityDecision + tmDeltas(TM601)",
         "evidence": [E_IR("schematic-ir-sensing.json dfdPairVerdicts[SW<->PGND]: inverted orientation, unionRelays [60,61,154,155]; paths[] FH0->PGND_F_S1 [154,155], FL0->SW_F_S1 [60,61]")]},
        {"id": "SD-5", "severity": "medium", "decision": "Do not plan a Kelvin measurement through the FPVIe0 PC nets (K90/K91 + K82_R_CS): the PC nets are board-shorted F<->S and carry the 100 mohm / 5 mohm shunts.",
         "why": "a 10 mohm DUT measured against a 100 mohm shunt in the same path is dominated by the shunt.",
         "contractPlacement": "safetyInvariants + kelvinRoutingDecision + senseFormOptions.pcRouteDefinition",
         "evidence": [E_IR("hazards[measurement-validity]; resourceConflicts.netShortGroups")]},
    ],
    "kelvinPairVerdicts": [
        {"pair": "PMID<->SW", "tm": "TM600", "available": True, "fourWireProper": True, "terminals": "S1_FPVIe ch0: FH0/SH0->PMID (K83), FL0/SL0->SW (K60,K61)", "unionRelays": [60, 61, 83]},
        {"pair": "SW<->PGND", "tm": "TM601", "available": True, "fourWireProper": True, "terminals": "S1_FPVIe ch0 inverted orientation: FH0/SH0->PGND (K154,K155), FL0/SL0->SW (K60,K61)", "unionRelays": [60, 61, 154, 155]},
        {"pair": "BST<->SW", "tm": "TM600", "available": True, "fourWireProper": True, "terminals": "S1_FPVIe ch1: FH1/SH1->BST, FL1/SL1->SW", "unionRelays": [131, 132, 133, 134, 135]},
    ],
    "instrumentCapabilities": {
        "FPVIe": "genuine floating 4-wire Kelvin pair; the only family that can carry the 1 A force; reaches PMID, SW, PGND",
        "ACM200": "reaches SW only (S5_ACM200_FH8/SH8, requiredOn K61), +-200 mA; usable for the SW single-ended Kelvin read, NOT for the 1 A force and cannot reach PMID/PGND at all",
        "FXVIe_PLUS": "4-wire Kelvin on ONE pin (PMID via K84 with no SetOn; PGND via K155) but its low side returns to AGND_F, so it cannot form a floating pair across SW",
        "QTMUe": "single line per channel with the low side on DGND; reaches SW_S through the FPVIe1 sense relays K130/K132/K135 and PMID_S through the K86 bridge - i.e. its routes DEPEND on the very bridges SD-2 requires to stay open (a third, independent reason to exclude it, on top of K141/K142 and the DGND/low-line character). Usable only for DC/Iq/toggle-class work.",
        "QVMe": "sense lines only (no force); CH0+ taps the FPVIe0 SH bus and lands on the PMID_F/PGND_F nets while CH0- lands on SW_S - a mixed F/S pair, not a Kelvin sense pair; not registered for the mOhm Delta-V slot.",
        "evidence": [E_IR("schematic-ir-sensing.json nonKelvinInstruments; nodeReachability; singleEndedEvidence")],
    },
    "convergedFormBCandidates": [
        "PMID sense leg: S3_FXVIe_PLUS_SH1 -> PMID_S_S1 (requiredOn [])",
        "PGND sense leg: S3_FXVIe_PLUS_SH3 -> PGND_S_S1 (requiredOn [155])",
        "SW sense leg: S5_ACM200_SH8 -> SW_S_S1 (requiredOn [61], +-200 mA class)",
        "FPVIe0 alternative for either end: SH0 -> PMID_S_S1 / PGND_S_S1, SL0 -> SW_S_S1 (this is form (a))",
    ],
    "pinAttachedRelayPolicy": {
        "methodologyFinding": "K85_CAP_PMID, K57_CAP_BST_SW, K92_AGND_F2S and K93_AGND2PGND are PIN-attached parts that appear in NO proof required_on list (the sensing evidence mentions K92 3x and K93 5x but zero times as a routing requirement), so path checking cannot cover them - their state must be decided by functional rule, never assumed safe because they are absent from required_on.",
        "explicitStates": [
            {"relay": "K85_CAP_PMID", "requiredState": "SetOn when the PMID rail must be stabilised; OPEN while I(PMID) is a measured quantity and during discharge", "rule": "CT1: cap gate follows the item's measurement intent, and opening it is part of the discharge plan (4.7 uF + 1 kohm bleed)", "evidence": [E_IR("discharge[PMID]")]},
            {"relay": "K57_CAP_BST_SW", "requiredState": "SetOn for TM600 (the 220 nF bootstrap cap is part of the BST-SW item); OPEN when the BST-SW rail must be left floating free of the cap", "rule": "CT1 + E006: the cap is the loop load, not decoupling", "evidence": [E_IR("polarity[Cap_SW_BST_S1]; discharge[BST-SW]")]},
            {"relay": "K92_AGND_F2S_S1", "requiredState": "OPEN for the mOhm items (it bridges AGND_F force to sense, i.e. it would degrade that row to 2-wire); may be closed only for DC-class items that need the AGND_F tie", "rule": "same family as SD-2 (force<->sense bridge)", "evidence": [E_IR("schematic-ir-sensing.json forceSenseBridgeRelays[K92_AGND_F2S_S1]")]},
            {"relay": "K93_AGND2PGND", "requiredState": "OPEN during TM600/TM601 (SD-3); if a DC item needs AGND=PGND, it may be closed only there, and never while a 1 A return flows through PGND", "rule": "SD-3", "evidence": [E_IR("blockingDecisionsForStrategy SD-3")]},
        ],
    },
}


# --------------------------------------------------------------------------------------
# 3i. BD-05 clamp ruling (provisional) + corrected Delta-V form ruling + forbidden routes
# --------------------------------------------------------------------------------------
clamp_ruling = {
    "id": "BD-05",
    "status": "CLOSED - provisional engineering default",
    "provisional": True,
    "scope": "acceptance-20260916-dali10 debug code and compilation ONLY. No hardware authorization: no bench execution may be derived from this value, and the production tree must not be touched.",
    "setting": {
        "call": "FPVIe.SetClamp(50, 50)",
        "ranges": "FPVIe_1V voltage range with FPVIe_2A current range for the 1 A force",
        "resultingCompliance": "+-0.5 V (50% of the 1 V full scale on each polarity; = 0.5 V at 1 A equivalent to a 500 mOhm ceiling)",
        "reissueRule": "the clamp is CLEARED by any FV/FI mode switch, so it must be re-issued after every switch (before the FI target is applied)",
    },
    "rationale": {
        "whyProvisional": "this is the golden case's default (knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md:19), NOT a value from this DUT's datasheet",
        "whyNotATestLimit": "the normal drop is only ~11 mV (TM600, 11 mohm x 1 A) / ~7.5 mV (TM601); 0.5 V is 45-67x that, so it cannot act as a measurement limit - its only role is to bound an open-circuit or mis-wiring event",
        "explicitlyNotPassFail": "the clamp value must never be used as a pass/fail criterion in the test plan; pass/fail comes from BD-01 (11 / 7.5 mohm)",
    },
    "evidence": [E_FPVIEH("FPVIe.h:101 int SetClamp(double percent_PFS, double percent_NFS)"),
                 ev("knowledge/sources/fpvie.md", "fpvie.md:141-168 SetClamp signature + 'switching FV/FI mode clears the clamp'"),
                 ev("knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md", "L19: FV0 -> FI0 -> SetClamp(50,50) (0.5V compliance -> max measurable 500 mOhm) -> FI=1A -> delay 2ms -> MeasureVI -> immediately FI=0")],
    "retainedRisks": [
        {"id": "U1", "risk": "no datasheet evidence for the G6K-2G-Y / TLP3412 contact current rating at 1 A", "consequence": "hardware sign-off risk before any bench run; must appear in the final report's limitations"},
        {"id": "U2", "risk": "the 10 kOhm Kelvin series row (R_PMID_KLV_S1) in series with the FPVIe sense input", "consequence": "unconfirmed sense-input bias current; numeric criterion in U2b (<= 11 nA for TM600, <= 7.5 nA for TM601 at 1% error); must appear in the final report's limitations"},
    ],
}

delta_v_ruling = {
    "id": "DELTA-V-FORM",
    "status": "corrected - option (a) is the only ΔV candidate for this run",
    "primary": "form (a): the FPVIe channel's own Kelvin pair - S1_FPVIe_SH0->PMID_S_S1 [83] (TM600) / ->PGND_S_S1 [154,155] (TM601) and S1_FPVIe_SL0->SW_S_S1 [60,61]; both legs land on sense pins, fourWireProper=true per dfdPairVerdicts",
    "secondaryRelegated": "form (b), two single-ended reads subtracted, is NOT DELIVERABLE for this run unless an instrument table with independent Kelvin splitting is produced and signed off. Recorded with its counter-evidence, not deleted: the counter-evidence is that the earlier named (b) candidates (S10_CH0_A/B QTMU and S8_QVM_CH0+/-) are invalid - QTMU is single-line with its low side on DGND and its routes need K141/K142 and the K86/K130 bridges; QVM lands one lead on a force net (mixed F/S).",
    "partialEvidenceForRevisitingB": "the two-instrument sense-pin form does exist in the path list: S3_FXVIe_PLUS_SH1->PMID_S_S1 (requiredOn []) and S5_ACM200_SH8->SW_S_S1 (requiredOn [61]) / S3_FXVIe_PLUS_SH3->PGND_S_S1 ([155]) - i.e. both instruments publish SEPARATE force and sense ports. This is recorded as unevidenced-for-approval, NOT as an approved fallback: it has not been signed off and its two meters are independently referenced, so it cannot be relied on in this run.",
    "consequenceOfRelegation": "with (b) off the table, the senseFormDecision.c driver-layer question (does FPVIe_RELAY_SENSE_ON, or an explicit K88 state, engage the remote sense?) becomes the single point of failure for the mOhm ΔV measurement. If it cannot be evidenced, this run has NO signed-off ΔV form - that is a blocking-level consequence and is flagged to the Captain rather than papered over.",
    "forbiddenRoutes": [
        {"route": "FPVIe0 PC route: K90_FPVI0_PC_Force / K91_FPVI0_PC_Sense + K82_R_CS", "basis": "schematic-ir hazards[measurement-validity] + resourceConflicts.netShortGroups: the PC nets are board-shorted F<->S (DIRECT_WIRE) and carry R1_CS_S1 100 mohm +-1% / R2_CS_S1 5 mohm +-1% on net FPVIe0_FL_PC_S1 - 9x-13x the measured value at 1 A", "evidence": [E_IR("hazards[measurement-validity]; resourceConflicts.netShortGroups"), ev("project/DALI/Dali-SCH.csv", "K90/K91 net membership includes FPVIe0_FL_PC_S1")]},
        {"route": "QTMU defaults for PMID/SW: S10_CH0_A [83,86,141] / S10_CH0_B [60,61,142]", "basis": "IR requiredMitigation 'For TM600/TM601 use only FPVIe Kelvin routes; do not measure RDSON on the QTMU defaults' (hazard severity high, tmLinks TM600+TM601); QTMU is single-line with its low side on DGND (no Kelvin split); its PMID_S route also needs the K86 bridge and its SW_S route the K130/K132/K135 relays, i.e. it depends on the very bridges SD-2 keeps open", "evidence": [E_IR("hazards[measurement-validity] requiredMitigation; schematic-ir-sensing.json nonKelvinInstruments[QTMUe]")]},
        {"route": "K141_QTMU_BUSA / K142_QTMU_BUSB bridging (any use while an FPVIe channel owns a pin)", "basis": "measured nets: K141 ties FPVIe0_FH_BUS_S1 to FPVIe1_FH_BUS_S1 and K142 ties FPVIe0_FL_BUS_S1 to FPVIe1_FL_BUS_S1; for TM600, which occupies both channels, closing K141 shorts PMID to BST and destroys the two independent floating loops", "evidence": [ev("project/DALI/Dali-SCH.csv", "K141/K142 net memberships"), E_IR("hazards[shared-resource] K141/K142 bridge")]},
        {"route": "QVM ch0 as a Kelvin pair (S8_QVM_CH0+ / CH0-)", "basis": "CH0+ lands on PMID_F_S1 / PGND_F_S1 (role=F) while CH0- lands on SW_S_S1 (role=S): a mixed F/S pair, so one end carries the lead/relay drop", "evidence": [E_IR("paths[] S8_QVM_CH0+->PMID_F_S1 role=F; S8_QVM_CH0- ->SW_S_S1 role=S; nonKelvinInstruments[QVMe]")]},
        {"route": "force-pin single-ended reads used as the ΔV ends", "basis": "a reading taken on the force pin carries that row's lead and relay drop; both ends must land on sense pins", "evidence": [E_IR("singleEndedEvidence[PMID].forceTerminals vs senseTerminals")]},
    ],
}


# --------------------------------------------------------------------------------------
# BD-08 (captain ruling, user-overridable): ATE stimulus voltages follow DFT/OVERVIEW;
# the reg_config .sv values are demoted to simulationDomainReference (kept, not deleted).
# Scope note: this ruling changes ONLY the TM600/TM601 stimulus voltage fields and their
# source annotation. Register map (BD-03), alias table, power-sequence structure and
# safetyInvariants are untouched.
# --------------------------------------------------------------------------------------
ATE_STIMULUS_RULING = {
    "ruling": "BD-08 (captain ruling; user-overridable) - TM600/TM601 ATE stimulus voltages follow DFT/OVERVIEW",
    "ateStimulus": {
        "TM600": {"vbat": "4.2 V", "pmid": "15 V", "bst2sw": "5 V", "vdrv": "5 V"},
        "TM601": {"vbat": "4.2 V", "pmid": "9 V", "vdrv": "5 V"},
    },
    "simulationDomainReference": {
        "TM600": {"vbat": "3.5 V", "pmid": "5 V", "bstSimSw": "5 V", "vdrv": "5 V"},
        "TM601": {"vbat": "3.5 V", "vdrv": "5 V", "vbus": "5 V"},
        "status": "retained, NOT deleted, NOT adopted as an ATE stimulus",
        "whyNotAdopted": "the .sv files carry 'generate time: 2026-05-15', earlier than the LS/HS bit-fix backup (PROGRESS.md 20260819 / 20260826), so their voltages were not set for this board's ATE conditions. BD-03 made .sv authoritative for the REGISTER MAP only - never for stimulus voltages (BD-02/BD-08).",
    },
    "evidence": [E_TM600SV("tm600.sv:31-33 registers + the simulation-domain vbat/PMID values"), E_TM601SV("tm601.sv:26-28 registers + the simulation-domain vbat/vbus values"),
                 E_DFT("TM600 row: vset[vbat,4.2,100e-6,0] and pmid 15 V; TM601 row: vset[vbat,4.2,...] and pmid 9 V")],
    # BD-08 as written also fixes the supply rail: DFT.csv declares 4.2 V for the standby/supply
    # items while their reg_config .sv values are 3.0 / 4.0 / 3.5 V. Recorded per item below.
    "supplyRailItems": {
        "TM102": {"ateVbat": "4.2 V", "irVbat": "4.0 V", "dftLine": "the DFT.csv row for TM102 is not among L12/L25/L30", "divergence": "A-side DFT.csv hardware_initial 4.2 V vs B-side IR/OVERVIEW Code1 + reg_config/tm102.sv 4.0 V"},
        "TM103": {"ateVbat": "4.2 V", "irVbat": "4.0 V", "dftLine": "DFT.csv L12 (TM103)", "divergence": "A-side DFT.csv L12 4.2 V vs B-side IR/OVERVIEW Code1 + reg_config/tm103.sv 4.0 V"},
        "TM108": {"ateVbat": "4.2 V", "irVbat": "3.0 V", "dftLine": "DFT.csv L25 (TM108)", "divergence": "A-side DFT.csv L25 4.2 V vs B-side IR/OVERVIEW Code1 + reg_config/tm108.sv 3.0 V"},
        "TM109": {"ateVbat": "4.2 V", "irVbat": "3.0 V", "dftLine": "DFT.csv L30 (TM109)", "divergence": "A-side DFT.csv L30 4.2 V vs B-side IR/OVERVIEW Code1 + reg_config/tm109.sv 3.0 V"},
    },
}

# BD-04 (user adjudication): TM108/TM109 toggle threshold = OVERVIEW 4.4 V; DFT.csv 4.15 V and the
# TM109 row's own vac3/DMUX contradiction are retained as registered conflicts.
THRESHOLD_RULING = {
    "TM108": {"ruling": "BD-04 (closed-by-user-adjudication)", "accepted": "rising Vth 4.4 V, Hys 0.35 V (OVERVIEW + meta)",
              "conflictSide": "DFT.csv record 9: 'rising vth 4.15V, hys 0.35V' (250 mV lower)",
              "policy": "OVERVIEW/meta govern the acceptance threshold; the DFT.csv value is retained as a registered conflict and must not be rewritten, averaged or deleted."},
    "TM109": {"ruling": "BD-04 (closed-by-user-adjudication)", "accepted": "rising Vth 4.4 V, Hys 0.35 V (OVERVIEW + meta)",
              "conflictSide": "DFT.csv record 10: 'rising vth 4.15V, hys 0.35V'; PLUS an intra-row contradiction - the TM109 row drives vset[vac3,...] although the item is VAC2_PRST (the VAC3 item is the neighbouring TM110 row), so the row's pin and its DMUX_SEL disagree",
              "policy": "OVERVIEW/meta govern; both the 250 mV delta and the vac3/DMUX intra-row contradiction are retained as registered conflicts for the final report."},
}




# naming variants measured in the DFT sources (t4 asked for these explicitly)
VARIANT_ALIASES = [
    {
        "alias": "sw2pmid", "variantOf": "pmid2sw", "direction": "reverse of pmid2sw",
        "measured": "7 hits in project/DALI/input/DFT.csv; 0 hits for pmid_sw there",
        "resolution": {"note": "same physical node pair as pmid2sw (PMID <-> SW on FPVIe0 CH0); the token encodes the opposite current direction. No source in this workspace defines which FI sign realises which name - registered as a polarity open item, not averaged."},
        "evidence": [E_DFT("sw2pmid x7 in DFT.csv (python count)"), E_CMAP("L165 CH0 High -> PMID; L174 CH0 Low -> SW")],
    },
    {
        "alias": "pmid_sw", "variantOf": "pmid2sw", "direction": "same node pair, legacy spelling",
        "measured": "0 hits in DFT.csv; 10 hits in project/DALI/_archive/_dump_OVERVIEW.txt",
        "resolution": {"note": "OVERVIEW-only spelling of the PMID<->SW pair (same as the .sv simulation token isrcPMID_SW, which is old-generation and not adopted as a stimulus). Map it to the pmid2sw resolution; do NOT copy the .sv stimulus."},
        "evidence": [ev("project/DALI/_archive/_dump_OVERVIEW.txt", "pmid_sw x10 (python count)"), E_TM601SV("tm601.sv:33-34 isrcPMID_SW - simulation domain, not adopted")],
    },
    {
        "alias": "bst1_sw1", "variantOf": "bst2sw", "direction": "BST1 <-> SW1 (TM1205)",
        "measured": "4 hits in _dump_OVERVIEW.txt (TM1205 vset[bst1_sw1,4,1000e-6,0])",
        "resolution": {"forceInstrument": "FPVIe0 CH0 (primary, relays below) or FPVIe1 CH1",
                        "terminalAssignment": {"high": "SW1", "low": "BST1"},
                        "closedRelayNumbers": [46, 41],
                        "relayPath": "CH0 High -> SW1 需闭合 K46 ; CH0 Low -> BST1 需闭合 K41",
                        "alternativeChains": ["CH1 High -> SW1 需闭合 K136,K137,K143,K144,K46", "CH1 Low -> BST1 需闭合 K138,K139,K145,K146,K41"]},
        "divergence": "POLARITY: for bst1_sw1 the connect-map puts SW1 on the HIGH terminal and BST1 on the LOW terminal, i.e. the opposite of bst2sw (BST high / SW low). The 'BST must lead SW' invariant therefore cannot be satisfied by terminal assignment alone - the sign of the applied voltage matters. Registered, not averaged; must be settled by t4/relay-trace.",
        "evidence": [E_CMAP("L45 CH0 Low -> BST1 (K41); L177 CH0 High -> SW1 (K46); L271/L394 CH1 equivalents")],
    },
    {
        "alias": "bst2_sw2", "variantOf": "bst2sw", "direction": "BST2 <-> SW2 (TM1205)",
        "measured": "5 hits in _dump_OVERVIEW.txt",
        "resolution": {"forceInstrument": "FPVIe0 CH0 (primary) or FPVIe1 CH1",
                        "terminalAssignment": {"high": "SW2", "low": "BST2"},
                        "closedRelayNumbers": [46, 49, 41, 43],
                        "relayPath": "CH0 High -> SW2 需闭合 K46,K49 ; CH0 Low -> BST2 需闭合 K41,K43",
                        "alternativeChains": ["CH1 High -> SW2 需闭合 K136,K137,K143,K144,K46,K49", "CH1 Low -> BST2 需闭合 K138,K139,K145,K146,K41,K43"]},
        "divergence": "same polarity divergence as bst1_sw1 (SW on the HIGH terminal).",
        "evidence": [E_CMAP("L48, L183, L274, L400")],
    },
]

for _a in ALIASES:
    if _a["alias"] in SENSE_PLAN:
        _a["sensePlan"] = SENSE_PLAN[_a["alias"]]

# NOTE: alias_flat (flat table for t4) is built after single_aliases is defined, further below.

measurement_plan = {
    "requestedBy": "test-strategy-architect (t4 message), answered by setup-architect (t3 addendum 2)",
    "currentSense": "FPVIe0 MIRET on the forcing channel (R-VIR: measured I, never the programmed value) - precedent sub.cpp:3266",
    "voltageSenseCandidates": [
        "QVM ch0 differential (S8_QVM_CH0+/CH0-): CANDIDATE DISPUTED with t2 (mixed F/S landing vs the L525 2-wire-sense claim) - not registered, referred to the relay-trace gate / t6",
        "FPVIe0/FPVIe1 own SH/SL Kelvin pair via the BUS route (PC nets excluded - they are board-shorted)",
        "two single-ended reads subtracted (FXVIe_PLUS PMID_HG2 + ACM200 S5_FH8 for SW): live precedent, worst offset match at 10 mV",
    ],
    "openForT4": [
        "which voltage sense candidate t4 signs off (the contract does not pick one silently)",
        "U10: QVM ch0 concurrency with FPVIe0 force on the same nodes",
        "BD-07 assumption: OVERVIEW's 'Y / 2 FLOAT' for TM600 is interpreted as two floating nodes (PMID and SW); recorded as an assumption to be confirmed, not as a measured fact",
    ],
    "rangesProvided": {
        "FPVIe_IRNG": ["10A", "2A", "1A", "100MA", "10MA", "1MA", "100UA", "10UA"],
        "FPVIe_VRNG": ["100V", "40V", "20V", "10V", "5V", "2V", "1V", "100MV"],
        "FPVIe_MV_GAIN": ["X1", "X2", "X5", "X10"],
        "FPVIe_MI_GAIN": ["X1", "X2", "X5", "X10"],
        "evidence": [E_FPVIEH("FPVIe.h:6-16 FPVIe_VRNG; :17-27 FPVIe_IRNG; :37-43 FPVIe_MI_GAIN; :45-51 FPVIe_MV_GAIN; :29-35 FPVIe_OUT_RELAY")],
    },
    "livePrecedent": {"code": "FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON); delay_ms(2); ...MeasureVI(50,5); fabs(FPVI0.GetMeasResult(site, MIRET))",
                      "evidence": [ev("D:/PROJECT6-DALI/ForCodexDebug/source/sub.cpp", "sub.cpp:3258-3266")]},
}


SINGLE = [
    ("vbat", "VBAT", "project/DALI/input/DFT.csv lines 90/98 etc.", "FXVIe_PLUS VBAT_PD3 group / FPVIe CH0 High->VBAT 需闭合 K136,K137,K143,K144,K7"),
    ("pmid", "PMID", "DFT.csv TM600 vset[pmid,5,...]", "FPVIe CH0 High->PMID 需闭合 K83 (or FXVIe_PLUS via default-conducting K84_HG2)"),
    ("vdrv", "VDRV/V1P5", "DFT.csv TM600/TM601 vset[vdrv,5,...]", "FXVIe_PLUS V1P5_U34PS group + K126_V1P5_CAP"),
    ("vbus", "VBUS", "DFT.csv TM601 vset[vbus,5,...]", "FPVIe CH0 Low->VBUS 需闭合 K3 / CH1 Low->VBUS 需闭合 K138,K139,K145,K146,K3"),
    ("vac1", "VAC1", "DFT.csv TM108 rampv_vac1", "FPVIe CH0 High->VAC1 需闭合 K70,K87,K88,K90,K91; CH0 Low->VAC1 需闭合 K17"),
    ("vac2", "VAC2", "DFT.csv TM109 rampv_vac2", "FPVIe CH0 High->VAC2 需闭合 K19,K70,K87,K88,K90,K91; CH0 Low->VAC2 需闭合 K17,K19"),
    ("vac3", "VAC3", "DFT.csv TM103/TM109 adjacent rows", "FPVIe CH0 High->VAC3 需闭合 K18,K70,K87,K88,K90,K91; CH0 Low->VAC3 需闭合 K17,K18"),
    ("vdm", "VDM", "DFT.csv TM102/TM103/TM135", "FPVIe CH0 High->VDM 需闭合 K58; CH0 Low->VDM is [单线-仅FL] NOT a valid path; ACM200 S5_FH7 -> VDM via K59_SDA (Relay-NC)"),
]
single_aliases = [{
    "alias": a, "kindOfStimulus": ["vset / ramp / MV"],
    "nodes": {"from": pin, "to": "AGND (single-ended reference)"},
    "usedByTm": sorted([tm for tm in SCOPE if pin.split("/")[0] in sir["scopePinsPerTm"].get(tm, [])]),
    "firstSource": {"source": src, "evidence": [E_DFT(src.split("lines ")[-1] if "lines " in src else src)]},
    "resolution": {"note": route},
    "crossCheck": {"bfsAgrees": True, "divergence": None},
} for a, pin, src, route in SINGLE]

alias_table = ALIASES + single_aliases

# flat, machine-consumable form requested by t4: alias -> {forceInstrument, senseInstruments, relayPath, kNumbers}
alias_flat = []
for _a in alias_table + VARIANT_ALIASES:
    res = _a.get("resolution", {}) or {}
    sp = SENSE_PLAN.get(_a["alias"], {})
    sense = []
    for key in ("voltageDifferentialCandidateDisputed", "voltageAlternativeA", "voltageAlternativeB",
                "voltage", "alternative", "current", "highNode", "lowNode"):
        blk = sp.get(key)
        if isinstance(blk, dict) and blk.get("instrument"):
            sense.append({"role": key, "instrument": blk["instrument"]})
    relay_path = res.get("relayPath")
    if not relay_path and res.get("relayChainHigh"):
        relay_path = "high: %s | low: %s" % (
            " -> ".join(r["relay"] for r in res["relayChainHigh"]),
            " -> ".join(r["relay"] for r in res.get("relayChainLow", [])))
    if not relay_path and res.get("relayChain"):
        relay_path = " -> ".join(r["relay"] for r in res["relayChain"])
    if _a in ALIASES:
        kind = "path-alias"
    elif _a in VARIANT_ALIASES:
        kind = "naming-variant"
    else:
        kind = "single-ended"
    alias_flat.append({
        "alias": _a["alias"], "kind": kind, "variantOf": _a.get("variantOf"), "nodes": _a.get("nodes"),
        "forceInstrument": res.get("forceInstrument") or res.get("note"),
        "senseInstruments": sense, "relayPath": relay_path,
        "kNumbers": res.get("closedRelayNumbers") or [r["number"] for r in res.get("relayChain", [])],
        "usedByTm": _a.get("usedByTm"),
        "openItems": (sp.get("voltageDifferentialCandidateDisputed") or {}).get("openItem") if isinstance(sp.get("voltageDifferentialCandidateDisputed"), dict) else None,
        "divergence": _a.get("divergence"),
    })

# --------------------------------------------------------------------------------------
# 4. register map (BD-03)
# --------------------------------------------------------------------------------------
register_map = {
    "ruling": "BD-03 (per-TM .sv mapping governs; DFT.csv register comments are registered conflicts)",
    "TM600": {"registers": {"0x59": "0x20", "0x5A": "0x02", "0x61": "0x4B"},
              "purpose": "HS FET test-mode path (D2A_BUBO_TM_HSON family)",
              "evidence": [E_TM600SV("tm600.sv:31-33 I2CWriteSameData(DEV_ADDR,0x59,0x20) / 0x5A,0x02 / 0x61,0x4B")]},
    "TM601": {"registers": {"0x59": "0x20", "0x5A": "0x01", "0x61": "0x4B"},
              "purpose": "LS FET test-mode path (D2A_BUBO_TM_LSON family)",
              "evidence": [E_TM601SV("tm601.sv:26-28 I2CWriteSameData(DEV_ADDR,0x59,0x20) / 0x5A,0x01 / 0x61,0x4B")]},
    "prerequisite": "entertestmode() before any register write (R034/H011); WAKE_UP=1 then the D2A_BUBO_* fields",
    "notAdopted": {
        "svStimuli": "tm600.sv isrcSW / tm601.sv isrcPMID_SW (tm600.sv:38-39, tm601.sv:33-34) are old-generation simulation-domain current sources and MUST NOT be written into the ATE setup (BD-02).",
    },
}

# --------------------------------------------------------------------------------------
# 5. global initialization / cleanup (R-PON / R-POFF)
# --------------------------------------------------------------------------------------
global_init = [
    {"order": 1, "action": "Pre-flight: enumerate the relay actuation set of the item from SCH-Connect-Map '需闭合' lists and assert every relay gets an EXPLICIT state",
     "resource": "all relays on the item's paths", "reason": "the connect-map legend states Relay-ON = 需SetOn闭合 and Relay-NC = 默认导通; 'not SetOn' is not a valid way to open a MOS opto part",
     "rule": "R-PON / relay-default-state", "evidence": [E_CMAP("L4 legend; L8-L19 Relay-NC default-conducting")]},
    {"order": 2, "action": "Anti-short pre-check: keep all P2P / pull-up / pull-down / NC-to-AGND relays at their MOS-open default (e.g. K14_VAC1_P2P, K15_VAC2_P2P, K16_VAC3_P2P, K38_KLV1_2_short, K39, K40, K26-K28, K53-K56, K151)",
     "resource": "K14,K15,K16,K38,K39,K40,K26,K27,K28,K53,K54,K55,K56,K151", "reason": "a stray SetOn of a P2P relay shorts a DUT node to AGND or to another DUT node before any source is current-limited",
     "rule": "anti-short (P006/H009)", "evidence": [E_CMAP("L866-L897 P2P/上拉/下拉 sections"), E_IR("hazards[anti-short]")]},
    {"order": 3, "action": "Close only the stabiliser cap gates the item needs (vbat K13, vcc K0, vbus K5, vac K21, v1p5/vdrv K126, pmid K85, bst-sw K57)",
     "resource": "K13,K0,K5,K21,K126,K85,K57", "reason": "each cap gate has a 1kohm bleed to AGND; opening it is also the sanctioned discharge mechanism",
     "rule": "R-PON", "evidence": [E_IR("discharge[]; resourceConflicts.stabiliserRelaysOnScopeRails")]},
    {"order": 4, "action": "Exception: keep K13_VBAT_Cap OPEN while I(VBAT) is the measured quantity; keep K21_VAC_Cap OPEN while VAC1/VAC2 is the scanned toggle input",
     "resource": "K13_VBAT_Cap, K21_VAC_Cap", "reason": "the cap would shunt the measured standby/suspend current and would slow the toggle ramp",
     "rule": "R-PON / DFT intent", "evidence": [E_IR("discharge[VBAT].note; discharge[VAC1].note"), E_DFT("TM000/TM001 sequence steps")]},
    {"order": 5, "action": "Open the QTMU channel bridges K141_QTMU_BUSA / K142_QTMU_BUSB before an FPVIe channel takes ownership of PMID/SW/PGND, and open the PC route relays K90/K91 (plus K82) so the mOhm loop cannot be sensed through the shunts",
     "resource": "K141, K142, K90, K91, K82_R_CS",
     "reason": "K141/K142 bridge the FPVIe0 and FPVIe1 BUS wires (TM600's two floating loops would merge); K90/K91 + K82 are the PC route carrying R1_CS 100 mohm / R2_CS 5 mohm and board-shorted F/S nets",
     "rule": "t3 ruling: BUS Kelvin route mandatory", "evidence": [E_IR("hazards[shared-resource] K141/K142; hazards[kelvin-integrity]; hazards[measurement-validity]")]},
    {"order": 7, "action": "Release the PIN-attached relays by functional rule (SD-2/SD-3): K86_KELVIN0_F/S and K130_KELVIN1_F/S OPEN, K92_AGND_F2S OPEN, K93_AGND2PGND OPEN during the mOhm items - these parts never appear in a proof required_on list, so their state comes from the rule, not from path checking",
     "resource": "K86, K130, K92, K93", "reason": "closing a force<->sense bridge degrades 4-wire to 2-wire (SD-2); K93 ties AGND_F to PGND_F/PGND_S and would carry the 1 A return (SD-3)",
     "rule": "SD-2, SD-3, PIN-attached relay policy", "evidence": [E_IR("schematic-ir-sensing.json forceSenseBridgeRelays; blockingDecisionsForStrategy SD-2/SD-3")]},
    {"order": 8, "action": "Initialize every source: FV=0 with RELAY_ON for power pins, FI=0 everywhere; MV-without-FI pins get FI=0 on the smallest current range (10UA)",
     "resource": "all ACM200 / FXVIe_PLUS / FPVIe sources", "reason": "R-PON-01/02: vset->FV, iset->FI, MV without FI -> FI=0 + 10UA",
     "rule": "R-PON-01, R-PON-02", "evidence": [E_RULES("L32 R-PON: vset->FV/iset->FI, MV无FI->FI=0+最小量程10UA")]},
    {"order": 6, "action": "Range selection: for each forced value pick the smallest range >= 2x the value and keep the programmed value <= 90% of that range",
     "resource": "range enums of every source", "reason": "R-PON-03/04; 1A force -> FPVIe_2A; 5V BST-SW -> FPVIe_5V/FPVIe_10V; FXVIe_PLUS caps at 1A with zero margin",
     "rule": "R-PON-03, R-PON-04, R-RNG", "evidence": [E_RULES("L32 R-PON: 量程≥2×取最小档"), E_FXVIEH("FXVIe.h:350 FXVIe_PLUS_1A")]},
    {"order": 7, "action": "FPVIe equal-potential stage: set FPVIe FV=0 on its intended range with FI=0 before any floating ramp",
     "resource": "FPVIe0 / FPVIe1", "reason": "R-PON-05 stage 2 — prevents a step onto the DUT before both terminals are defined",
     "rule": "R-PON-05", "evidence": [E_RULES("L32 R-PON: FPVI等电位、浮动源三阶段≤5V")]},
    {"order": 8, "action": "Floating-source ramp in three stages: drive the reference pin (PinB) first, then the FPVIe terminal, then step PinA in increments <= 5V with delay_us(200) between steps",
     "resource": "FPVIe0 (PMID/SW, SW/PGND), FPVIe1 (BST/SW)", "reason": "R-PON-05 / E006 reverse-bias protection",
     "rule": "R-PON-05, E006", "evidence": [E_RULES("L32"), E_IR("hazards[e006-reverse-bias]")]},
    {"order": 9, "action": "BST lead invariant: for TM600/TM1205 keep BST >= SW - Vf at every instant and never step BST-SW by more than 5V (D_BST_SW_S1 clamps the reverse direction)",
     "resource": "FPVIe1 / BST,SW", "reason": "E006: with the HS FET on SW==PMID and a BST below SW reverse-biases the 220nF bootstrap cap",
     "rule": "E006, R-PON-05", "evidence": [E_IR("hazards[e006-reverse-bias]"), E_IR("polarity[D_BST_SW_S1]")]},
    {"order": 10, "action": "High-current three-stage init: FV=0 -> FI=0 -> SetClamp(percent_PFS, percent_NFS) -> FI=target, then settle (delay >= 2ms) before measuring",
     "resource": "FPVIe0", "reason": "R-PON-08 three-stage rule; SetClamp is an SDK method (FPVIe.h:101) and is CLEARED by any FV/FI mode switch, so it must be re-issued after each switch",
     "rule": "R-PON-08", "evidence": [E_RULES("L32 R-PON: 大电流三段式(FV=0→FI=0→Clamp→FI)"), E_FPVIEH("FPVIe.h:101 int SetClamp(double percent_PFS, double percent_NFS)")]},
    {"order": 11, "action": "Clamp value policy (BD-05 closed, provisional): set SetClamp(50,50) on the FPVIe_1V range before the 1 A FI target -> +-0.5 V compliance; RE-ISSUE it after every FV/FI mode switch. Mark it provisional (golden default, not this DUT's datasheet), never a pass/fail criterion; scope is debug code/compilation only, no hardware authorization.",
     "resource": "FPVIe0 clamp", "reason": "the golden's value bounds an open-circuit/mis-wiring event (the normal drop is only ~11 mV / 7.5 mV, so 0.5 V cannot be a measurement limit); a mode switch clears the clamp, so it must be re-armed",
     "rule": "BD-05 (provisional)", "evidence": [E_FPVIEH("FPVIe.h:101"), ev("knowledge/sources/fpvie.md", "fpvie.md:141-168 '切换FV/FI模式时会清除箝位设置'"), ev("knowledge/references/L4-Golden-code/tm600-normal-highcurrent.md", "L19 SetClamp(50,50) on the 1V range")]},
    {"order": 12, "action": "TReg initialization for trim items: load the trim node before TRIM_NODE.execute (TM135 measures EFUSE_REG_F1 / measure_bg_res_div)",
     "resource": "TReg NU1201", "reason": "trim requires the register/EFUSE path to be initialised after entertestmode()",
     "rule": "R-TRIM", "evidence": [E_DFT("TM135 sequence: TRIM_NODE.execute(measure_bg_res_div, spec, ...)")]},
]

global_cleanup = [
    {"order": 1, "action": "Classify the item's power-off type from PowerState: floatingPairs non-empty + vset -> floating; FI >= 1A -> high-current; otherwise normal",
     "resource": "PowerState", "reason": "R-POFF-01 decides which teardown template applies", "rule": "R-POFF-01",
     "evidence": [E_RULES("L33 R-POFF: 类型判定")]},
    {"order": 2, "action": "Normal teardown (three steps, none may be skipped): zero every source while KEEPING its range and RELAY_ON -> delay_ms(1) -> unified RELAY_OFF ranges",
     "resource": "all sources", "reason": "R-POFF-02; R-POFF-06 unified ranges: ACM200_10V/10MA, FXVIe_PLUS_10V/10MA, FPVIe_1V/10MA (NOT 10A)",
     "rule": "R-POFF-02, R-POFF-06", "evidence": [E_RULES("L33: 普通三步(归零→delay_ms(1)→RELAY_OFF)、RELAY_OFF统一量程(FPVI用1V/10MA非10A)")]},
    {"order": 3, "action": "Floating teardown: reverse the up-sequence (PinA down first -> PinB -> other rails -> PinA to zero), each step <= 5V with delay_us(200)",
     "resource": "FPVIe0 / FPVIe1", "reason": "R-POFF-03/04; FPVIe must be the LAST RELAY_OFF",
     "rule": "R-POFF-03, R-POFF-04", "evidence": [E_RULES("L33: 浮动反转台阶、FPVI最后RELAY_OFF")]},
    {"order": 4, "action": "High-current teardown: FI=0 -> FV=0 -> RELAY_OFF, with the measurement pulse kept short",
     "resource": "FPVIe0", "reason": "R-POFF-05; a 1A pulse must not be left on the DUT (self-heating + relay contact load)",
     "rule": "R-POFF-05", "evidence": [E_RULES("L33: 大电流FI=0→FV=0→OFF")]},
    {"order": 5, "action": "Discharge plan per rail: open the rail's cap gate (K85 PMID, K57 BST-SW, K13 VBAT, K0 VCC, K5 VBUS, K21 VAC, K126 V1P5) and let the 1kohm bleed resistors to AGND_F_S1 discharge the stored charge",
     "resource": "K85,K57,K13,K0,K5,K21,K126 + R_*_S1 1kohm bleed rows",
     "reason": "the current StdAfx.h publishes NO discharge (DCHG) role (schematic-ir U6); the realisable mechanism is cap-gate + bleed, tau ~ 4.7ms on a 4.7uF rail",
     "rule": "discharge plan (t3 required content)", "evidence": [E_IR("discharge[]; unresolvedTopology U6; hazards[isolation-gap]")]},
    {"order": 6, "action": "K93_AGND2PGND handling (SD-3): keep it OPEN for the whole of TM600/TM601 and release it explicitly in cleanup; it may only be closed for a DC-class item that genuinely needs AGND=PGND, and never while a 1 A return flows through PGND",
     "resource": "K93_AGND2PGND", "reason": "classified [Connect]: AGND and PGND become one electrical node, which shorts the differential reference to AGND_F and puts the 1 A return through the K93 contact (SD-3)",
     "rule": "SD-3, relay model", "evidence": [E_IR("blockingDecisionsForStrategy SD-3; resourceConflicts.agndPgndTie; hazards[shared-resource] AGND/PGND")]},
    {"order": 7, "action": "Guaranteed abnormal-exit teardown: on any error/timeout run the same sequence from the finally block - FI=0 on every source, FV=0, then unified RELAY_OFF, with FPVIe last",
     "resource": "all sources + all relays actuated by the item",
     "reason": "an aborted item must not leave 1A on the DUT, a charged rail, or a bridged QTMU/PC route",
     "rule": "R-POFF + abnormal-exit cleanup (t3 required content)", "evidence": [E_RULES("L33"), E_IR("hazards[]")]},
    {"order": 8, "action": "Relay release without hot switching: never open a BUS relay while it carries one rail voltage and the relay replacing it sits at another; respect the _S1S2 joint-site relays",
     "resource": "K83,K60,K61,K154,K155 and all _S1S2 relays", "reason": "G6K contacts arc on unequal potentials and shared-site relays disturb the other site",
     "rule": "thermal-switching hazard", "evidence": [E_IR("hazards[thermal-switching]; hazards[cross-site-coupling]")]},
]

# --------------------------------------------------------------------------------------
# 6. tmDeltas
# --------------------------------------------------------------------------------------
dft_by_tm = {it["tm"]: it for it in dft["items"]}

LIMIT_RULING = {
    "TM600": {"accepted": "11 mOhm (OVERVIEW)", "acceptedSource": "project/DALI/_archive/_dump_OVERVIEW.txt:981 'TM600 BUBO HS_RDSON high side powerfet rdson 11 mΩ direct Y'",
              "conflicting": "10 mohm (DFT.csv, unit string 'mohm')", "conflictingLocator": "DFT.csv:90"},
    "TM601": {"accepted": "7.5 mOhm (OVERVIEW)", "acceptedSource": "project/DALI/_archive/_dump_OVERVIEW.txt:994 'TM601 BUBO LS_RDSON low side powerfet rdson 7.5 mΩ direct SCM'",
              "conflicting": "8 mohm (DFT.csv, unit string 'mohm')", "conflictingLocator": "DFT.csv:98"},
}


def limit_block(tm):
    it = dft_by_tm[tm]
    prim = (it.get("limits") or [{}])[0]
    block = {"authoritative": prim.get("expression"), "unit": prim.get("unit"),
             "source": "dft-ir.json limits[0] (sourceRank 1)", "tolerance": "NOT PUBLISHED in any DFT source",
             "evidence": [E_IR("items[%s].limits" % tm)]}
    if tm in LIMIT_RULING:
        r = LIMIT_RULING[tm]
        block["ruling"] = {
            "decision": "BD-01 (user ruling, reproduced verbatim in the contract)",
            "acceptanceLimit": r["accepted"],
            "acceptanceLimitEvidence": r["acceptedSource"],
            "registeredConflict": r["conflicting"],
            "registeredConflictEvidence": r["conflictingLocator"],
            "policy": "OVERVIEW is the acceptance limit for this debug-copy run; the DFT.csv derived/legacy values (10 / 8 mohm) are preserved as a registered conflict in the IR and the final report - they must NOT be rewritten, averaged or deleted.",
            "scope": "applies ONLY to the acceptance-20260916-dali10 debug-copy acceptance",
            "reopenCondition": "if a newer revision or an approved record is found, this decision MUST be reopened",
        }
    if tm in THRESHOLD_RULING:
        t = THRESHOLD_RULING[tm]
        block["thresholdRuling"] = {
            "decision": t["ruling"], "acceptanceThreshold": t["accepted"], "registeredConflict": t["conflictSide"],
            "policy": t["policy"], "scope": "applies ONLY to the acceptance-20260916-dali10 debug-copy acceptance",
            "evidence": [E_IR("items[%s].limits" % tm), E_DFT("TM108 record 9 / TM109 record 10 ExpectValue 'rising vth 4.15V, hys 0.35V'"),
                         E_IR("openQuestions: TM109 row drives vset[vac3,...] although the item is VAC2_PRST")],
        }
    return block


tm_deltas = {}
for tm in SCOPE:
    it = dft_by_tm.get(tm, {})
    pins = sir["scopePinsPerTm"].get(tm, [])
    pin_routes = {}
    for p in pins:
        g = groups_for_pin(p)
        pin_routes[p] = {k: {"needsClosed": v["needsClosed"], "pairKind": v["kind"],
                             "defaultConducting": v.get("defaultConducting"),
                             "warning": v["warning"], "line": v["line"], "detail": v.get("detail")}
                         for k, v in sorted(g.items())}
        if not pin_routes[p]:
            pin_routes[p] = {"notFound": "no 需闭合 group carries this pin name in SCH-Connect-Map"}
    delta = {
        "objective": it.get("name"),
        "methodFamilies": it.get("testType"),
        "scopePins": pins,
        "relaySet": sir["resourceConflicts"]["tmRelaySets"].get(tm, []),
        "aliasesUsed": [a["alias"] for a in ALIASES if tm in a.get("usedByTm", [])],
        "pinRouteTable": pin_routes,
        "powerSequenceDelta": it.get("sequence"),
        "stimuli": [s.get("note") or s.get("pin") for s in (it.get("stimuli") or [])][:8],
        "measurePlan": it.get("measurements"),
        "limits": limit_block(tm) if tm in dft_by_tm else {"authoritative": None, "note": "not in dft-ir"},
        "cleanupDelta": "none beyond the global contract" if tm not in ("TM600", "TM601") else
                        "high-current teardown FI=0 -> FV=0 -> OFF, then FPVIe LAST RELAY_OFF with the unified FPVIe_1V/FPVIe_10MA range; the 1A pulse must be short",
    }
    if tm in register_map:
        delta["registerDelta"] = register_map[tm]
    if tm == "TM600":
        delta["forceSenseTopology"] = "force PMID<->SW (FPVIe0 CH0), sense PMID-SW Kelvin pair (Check=MV&MI, R-VIR)"
        delta["resourceBudget"] = "TM600 uses FPVIe0 for the PMID-SW 1 A loop. It does NOT use FPVIe1 for BST-SW 5 V: per captain ruling (ii) the BST-SW rail stays the ground-referenced SW12_U1REF_BST_ACM form, and the FPVIe1 CH1 variant is intended but currently unrealisable (K131/K132/K134/K135 are the ch1 sense-float/PC class relays). Channel-budget note retained: a site has only two FPVIe channels, so TM600 and TM601 still cannot share a function."
        delta["mutualExclusion"] = ["TM601 (needs an FPVIe channel)", "TM102/TM103 (AMUX shares the FXVIe_PLUS channel with PGND)"]
    if tm == "TM601":
        delta["forceSenseTopology"] = "force SW<->PGND (FPVIe0 CH0, PGND on the high terminal), sense SW-PGND Kelvin pair"
        delta["resourceBudget"] = "needs an FPVIe channel for the 1A loop; cannot share a function with TM600 (bus-topology.md 八)"
        delta["mutualExclusion"] = ["TM600", "TM102/TM103 (AMUX/PGND share one FXVIe_PLUS channel)"]
    if tm in ("TM600", "TM601"):
        # BD-08: the ATE stimulus fields carry DFT/OVERVIEW values ONLY - no .sv value may appear
        # as a stimulus. The IR/.sv-derived texts are replaced here (not merely annotated).
        if tm == "TM600":
            delta["stimuli"] = [
                "vset[vbat,4.2,100e-6,0] - ATE value per BD-08 / DFT.csv TM600 row",
                "vset[pmid,15,...] - ATE value per BD-08 / OVERVIEW TM600 (the simulation-domain PMID value is recorded under simulationDomainReference and is not a stimulus)",
                "vset[bst2sw,5,1e-3,0] - ATE value (BST-SW differential rail held at 5 V)",
                "vset[vdrv,5,...] - ATE value",
                "en_tm[] entertestmode(); field[(WAKE_UP,1)] + field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)] - register writes (register-map evidence per BD-03)",
                "iset[pmid2sw,1,1e-3,0] - 1 A force across PMID<->SW (alias table)",
            ]
            delta["powerSequenceDelta"] = [
                "Step 1 connect: floating-high-current + Kelvin pair relays, VBAT/BST-SW/VDRV caps, bootstrap pair held at 5 V (BST-SW differential, ATE value)",
                "Step 2 power on (ATE values, BD-08): VBAT=4.2 V, PMID=15 V, BST-SW=5 V, VDRV=5 V (BST must lead/swing with PMID so BST-SW stays positive)",
            ] + list(it.get("sequence") or [])[2:]
        else:
            delta["stimuli"] = [
                "vset[vbat,4.2,100e-6,0] - ATE value per BD-08 / DFT.csv TM601 row (the simulation-domain value is recorded under simulationDomainReference and is not a stimulus)",
                "vset[vdrv,5,...] - ATE value",
                "vset[pmid,9,...] - ATE value per BD-08 / OVERVIEW TM601 (no other rail is a stimulus for this item; simulation-domain values live under simulationDomainReference)",
                "en_tm[] entertestmode(); field[(WAKE_UP,1)] + field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)] - register writes (register-map evidence per BD-03)",
                "iset[sw2pgnd,1,1e-6,0] - 1 A force across SW<->PGND (alias table)",
                "delay 5e-3 before applying the current (longer than TM600's 1 ms)",
            ]
            delta["powerSequenceDelta"] = [
                "Step 1 connect: floating force pair (PMID/SW) + Kelvin SW-PGND sense pair + VBAT/VDRV caps",
                "Step 2 power on (ATE values, BD-08): VBAT=4.2 V, PMID=9 V, VDRV=5 V. Simulation-domain values are recorded under simulationDomainReference and are not stimuli.",
            ] + list(it.get("sequence") or [])[2:]
        delta["ateStimulus"] = ATE_STIMULUS_RULING["ateStimulus"][tm]
        delta["ateStimulusSource"] = ATE_STIMULUS_RULING["ruling"]
        delta["simulationDomainReference"] = ATE_STIMULUS_RULING["simulationDomainReference"][tm]
        delta["simulationDomainReferenceStatus"] = ATE_STIMULUS_RULING["simulationDomainReference"]["status"] + " - " + ATE_STIMULUS_RULING["simulationDomainReference"]["whyNotAdopted"]
        delta["noMixingRule"] = "ATE stimulus values and simulation-domain values must never be mixed: no stimulus field above contains a .sv voltage, and the .sv numbers appear only under simulationDomainReference (retained for provenance and for the register-map evidence chain)."
        delta["commandSign"] = {
            "aliasDirection": "pmid2sw = PMID -> SW" if tm == "TM600" else "sw2pgnd = SW -> PGND",
            "instrumentTerminals": "FPVIe0 CH0 HIGH = PMID (K83), LOW = SW (K60,K61)" if tm == "TM600" else "FPVIe0 CH0 HIGH = PGND (K154,K155), LOW = SW (K60,K61)",
            "command": "+1 A" if tm == "TM600" else "-1 A",
            "basis": "DFT literal direction, command sign derived from the terminal assignment. TM601 needs the opposite sign because PGND is on the HIGH terminal.",
            "assumption": "'positive FI = current out of the HIGH terminal' is inferred from the golden case and is NOT stated in any header/manual here - verified at bring-up as U11 (criteria: BD-03-enabled FET conducts; |MVRET|/|MIRET| near 11 / 7.5 mohm not a body-diode drop; MIRET magnitude matches the programmed value).",
            "escalation": "none (captain ruling) - no silent inversion, no wiring blocking decision",
        }
        delta["senseInstrumentSlot"] = {
            "status": "PENDING",
            "definition": "one slot, consumed by t4 and reused verbatim by t5; the alternatives are enumerated in senseFormDecision (a/b/c) and the criterion for choosing is stated there",
            "primaryIfSenseOnEngagesRemoteSense": "FPVIe0 own Kelvin pair SH0/SL0 via the BUS route (K87/K88/K89 + K83 / K60,K61)",
            "primaryIfNot": "none signed off - per the corrected Delta-V ruling, form (b) is not deliverable for this run, and QVM ch0 is a DISPUTED candidate (t2: mixed F/S, not a Kelvin pair) rather than a fallback",
            "forbidden": "any route through the PC nets (K90/K91 + K82) or through the board shunts R1_CS 100mohm / R2_CS 5mohm",
            "validateAtBringUp": "|MVRET| / |MIRET| must land near 11 mohm (TM600) / 7.5 mohm (TM601); anything near a body-diode drop means the sense form or the FI sign is wrong",
            "clamp": {"status": "BD-05 CLOSED (provisional engineering default)", "value": "SetClamp(50,50) on FPVIe_1V for the 1 A force => +-0.5 V compliance", "reissue": "after every FV/FI mode switch (a switch clears the clamp)", "provisional": True, "notPassFail": "the clamp is a protection against open-circuit/mis-wiring only - never a pass/fail criterion", "scope": "debug code and compilation for this run only; no hardware authorization, no production-tree change"},
            "deltaVForm": {"primary": "(a) FPVIe own Kelvin pair (SH0/SL0)", "relegated": "(b) two single-ended reads subtracted is NOT DELIVERABLE for this run unless an instrument table with independent Kelvin splitting is produced and signed off", "consequence": "if senseFormDecision.c cannot be evidenced, this run has no signed-off Delta-V form (flagged to the Captain)"},
        }
    if tm in ATE_STIMULUS_RULING["supplyRailItems"]:
        # t18 (T2/T3 revised acceptance): the t12 BD-08 extension to these four items is RETRACTED.
        # No ateStimulus, no stimuliSourceNote, no "(revised per ...)" rewrite; the ORIGINAL IR-derived
        # stimulus is restored AND its ATE value is stated explicitly (4.0 V for TM102/TM103, 3.0 V for
        # TM108/TM109, per OVERVIEW Code1 + reg_config/tm10x.sv). The DFT.csv 4.2 V side is a registered
        # conflict and is never averaged or deleted.
        s = ATE_STIMULUS_RULING["supplyRailItems"][tm]
        delta["simulationDomainReference"] = {"vbat": s["irVbat"], "status": "retained as the simulation-domain reference (reg_config .sv / OVERVIEW Code1 value); NOT an ATE stimulus in its own right"}
        _dft_note = s.get("dftLine", "the DFT.csv row is not among L12/L25/L30")
        delta["stimuli"] = ["vset[vbat," + s["irVbat"].replace(" V", "") + ",100e-6,0] - ATE stimulus per OVERVIEW Code1 + reg_config/" + tm.lower() + ".sv (IR/OVERVIEW value " + s["irVbat"] + "); " + _dft_note + " declares 4.2 V - see conflicts (both sides retained)"]
    tm_deltas[tm] = delta

# --------------------------------------------------------------------------------------
# 7. safety invariants / conflicts / open items
# --------------------------------------------------------------------------------------
safety = [
    "BD-05 CLOSED (provisional engineering default): during the 1 A force the clamp is SetClamp(50,50) on the FPVIe_1V range, i.e. compliance = +-0.5 V, and it must be RE-ISSUED after every FV/FI mode switch because a mode switch clears it. It is provisional (golden default, not this DUT's datasheet value), it is not a test limit (the normal drop is ~11 mV / 7.5 mV), and it must never be used as a pass/fail criterion. Scope: debug code and compilation for acceptance-20260916-dali10 only - no hardware authorization, no production-tree change.",
    "SD-2: the force<->sense bridge relays K86_KELVIN0_F_S1 / K86_KELVIN0_S_S1 (FPVIe0) and K130_KELVIN1_F_S1 / K130_KELVIN1_S_S1 (FPVIe1) must stay OPEN for TM600/TM601 - closing any of them merges force and sense on that row and silently degrades a 4-wire Kelvin measurement to 2-wire. Only QTMU/QVM routes require them; no FPVIe/ACM200/FXVIe_PLUS 4-wire route does.",
    "SD-3: K93_AGND2PGND must stay OPEN during TM600/TM601 (and be explicitly released in cleanup): closing it ties AGND_F to PGND_F/PGND_S, shorting the differential reference and putting the 1 A return through the K93 contact.",
    "SD-5: never take the mOhm Delta-V through the FPVIe0 PC nets (K90/K91 + K82_R_CS): those nets are board-shorted force<->sense and carry R1_CS 100 mohm +-1% / R2_CS 5 mohm +-1%.",
    "SD-1: TM600 and TM601 must be separate functions - both need FPVIe channel 0 of the same site, and TM600 additionally occupies channel 1 (BST<->SW). They can never run concurrently on one site or be merged into one test function.",
    "PIN-attached relays (K85_CAP_PMID, K57_CAP_BST_SW, K92_AGND_F2S, K93_AGND2PGND) appear in NO proof required_on list, so path checking cannot cover them: their state must be set by functional rule (see sensingDecisions.pinAttachedRelayPolicy) and never assumed safe because they are absent from required_on. K92 must be OPEN for the mOhm items (it is an AGND_F force<->sense bridge).",
    "Each FPVIe BUS side may close AT MOST ONE DUT pin: K83 (PMID) and K154+K155 (PGND) both sit on FPVIe0_FH_BUS_S1 / _SH_BUS_S1, so closing both shorts PMID to PGND through the BUS. The same rule applies to K60's low BUS side (K61_SW selects SW; K68_VCP_F must not be closed at the same time).",
    "K141_QTMU_BUSA_S1S2 and K142_QTMU_BUSB_S1S2 must be OPEN whenever an FPVIe channel owns a pin: they bridge the FPVIe0 and FPVIe1 BUS wires, and the default QTMU routes for PMID and SW ({K83,K141} and {K60,K61,K142}) depend on them - if left closed, TM600's two floating loops collapse into one node.",
    "A 10 / 7.5 mOhm item must NEVER be routed through the FPVIe0 PC route (K90/K91 + K82_R_CS): it carries the board shunts R1_CS 100 mohm +-1% and R2_CS 5 mohm +-1% (9x-13x the measured value at 1 A) and its F/S nets are board-shorted DIRECT_WIRE.",
    "The BUS Kelvin relays are the only sanctioned sense path for the mOhm items: K87/K88/K89 (FPVIe0) and K131/K132/K133 (FPVIe1).",
    "E006: BST must never be below SW/PMID by more than a diode drop (the 220nF Cap_SW_BST_S1 would be reverse biased). Two wordings are recorded rather than averaged: IR hazards[e006-reverse-bias] states the operating requirement 'BST must lead PMID/SW by >=5 V at all times'. Read this as a DIFFERENTIAL requirement, not a setpoint: BST-SW = 5 V comes from the DFT ATE stimulus vset[bst2sw,5,1e-3,0] (DFT.csv:92), and because SW == PMID while the HS FET is on it also means BST = PMID + 5 V - so with the ATE PMID of 15 V (BD-08) the expected BST node is 20 V, not 5 V. The transition rule in R-PON-05 caps each ramp step at 5 V; during teardown the FET must stay on while the rails collapse.",
    "1A force is only realisable on the FPVIe family: FPVIe_IRNG reaches 10A/2A while FXVIe_PLUS tops out at exactly 1A (zero margin). Never use FXVIe_PLUS_10MA for a 1A item.",
    "High-current sequence is fixed: FV=0 -> FI=0 -> SetClamp -> FI=target; teardown is FI=0 -> FV=0 -> RELAY_OFF.",
    "SetClamp is cleared by any FV/FI mode switch, so it must be re-issued after each switch; the numeric clamp value is OPEN (BD-05) and must never be invented.",
    "FPVIe has exactly 2 channels per site; TM600 consumes both, therefore TM600 and TM601 may not share a function and must not run concurrently.",
    "AMUX and PGND share one FXVIe_PLUS channel: TM102/TM103 (AMUX) and TM601 (PGND) cannot share a site concurrently.",
    "Site-joint relays (_S1S2: K85, K57, K87, K89, K131, K133, K141, K142, K0, K2, K5, K13, K21, K44, K45, K74, K75, K82, K151) re-configuring them disturbs the other site - never reconfigure while another site is running.",
    "K141_QTMU_BUSA / K142_QTMU_BUSB bridge the two FPVIe channels' BUS wires; they must stay in the state that does not bridge the channel being used.",
    "Every relay on a scope path must carry an explicit state; the connect-map legend defines Relay-ON = SetOn closed and Relay-NC = default conducting.",
    "Anti-short: P2P / pull-up / pull-down relays (K14, K15, K16, K38, K39, K40, K26-K28, K53-K56, K151) default open and must not be closed incidentally.",
    "K93_AGND2PGND ties AGND and PGND into one node; all AGND-referenced sources share that ground, so a TM601 loop return is a shared node, not an isolated one.",
    "Kelvin integrity: FPVIe0_FH_PC_S1<->FPVIe0_SH_PC_S1 and FPVIe0_FL_PC_S1<->FPVIe0_SL_PC_S1 are board-wired shorts, so any route through the FPVIe0 PC nets is NOT true 4-wire Kelvin.",
    "The PC route carries the on-board current-sense shunts R1_CS=100mohm and R2_CS=5mohm; R2_CS is the same order as the 5-11 mOhm acceptance limits, so the shunt drop must be handed off (measured V and measured I per R-VIR).",
    "High-current items use a short pulse: apply FI, settle, measure, then FI=0 immediately (self-heating and relay contact load).",
    "Never hot-switch a BUS relay between unequal potentials.",
    "Do not close the VBAT cap gate (K13) while I(VBAT) is measured, and do not close the VAC cap gate (K21) while VAC1/VAC2 is the ramped input.",
    "Every energised rail needs a discharge plan (cap gate opened + 1kohm bleed to AGND) before its RELAY_OFF; there is no DCHG role in the current StdAfx.h.",
    "Teardown always ends with the FPVIe channel LAST RELAY_OFF, using the unified FPVIe_1V/FPVIe_10MA range (not 10A).",
    "Abnormal exit runs the same teardown from the finally block - an aborted item may not leave 1A on the DUT or a charged rail.",
]

conflicts = [
    "BD-08 (closed-by-captain-ruling, later reaffirmed by user adjudication; user-overridable, both sides preserved): ATE stimuli come from DFT/OVERVIEW ONLY - TM600 PMID 15 V, TM601 PMID 9 V, standby/supply 4.2 V. DFT.csv ground truth for the two rows: TM600 = vset[vbat,4.2] / vset[pmid,15] / vset[bst2sw,5] / vset[vdrv,5] + iset[pmid2sw,1,1e-3] (DFT.csv:90-97); TM601 = vset[vbat,4.2] / vset[pmid,9] / vset[vdrv,5] + iset[sw2pgnd,1,1e-6] (DFT.csv:98-104) - note the TM601 row contains NO vbus token at all. RETIRED-FROM-STIMULUS / SIMULATION-DOMAIN (quoted here only because the conflict must be preserved, never to be programmed): reg_config tm600.sv / tm601.sv carry VBAT 3.5 V and PMID 5 V, whose files are headed 'generate time: 2026-05-15', earlier than the LS/HS bit-fix backup; those numbers are admissible for the REGISTER MAP evidence chain only (BD-03) and MUST NOT override an ATE stimulus. Mixing the two vocabularies is forbidden - no stimulus field in this contract contains a .sv voltage. Also retained: DFT.csv's own 4.2 V declarations and TM601's VBUS 5 V path, which is not adopted as a stimulus at all. The user ruling may still be revised.",
    "TM102/TM103/TM108/TM109 VBAT divergence (registered, both sides retained, t18): DFT.csv lines 12 (TM103), 25 (TM108), 30 (TM109) each declare vset[vbat,4.2,100e-6,0], while the B side carries 4.0 V for TM102/TM103 and 3.0 V for TM108/TM109 - locator: dft-ir.json items[TM102].stimuli[0].vbat = 4.0 V, items[TM103] = 4.0 V, items[TM108] = 3.0 V, items[TM109] = 3.0 V (each note cites OVERVIEW Code1 + reg_config/tm10x.sv and says 'DFT.csv says 4.2 V - see conflicts'). A-side locator: project/DALI/input/DFT.csv L12 (TM103), L25 (TM108), L30 (TM109), each vset[vbat,4.2,100e-6,0]. Neither side is averaged or deleted. The restored stimulus text follows the IR/OVERVIEW Code1 + reg_config value (4.0 V for TM102/TM103, 3.0 V for TM108/TM109); the DFT.csv rows declare 4.2 V. The two readings are registered side by side and NEITHER is adopted as the sole authority here - the choice belongs to the user (a later user instruction would update this entry).was out of scope and has been retracted (t18); BD-08 applies to TM600/TM601 only. PROVENANCE OF THE RULING (recorded so no contradictory pair remains): the captain's earlier keep-ruling (T1) was superseded by the user's blocking correction (T2/T3), which requires that the extension not be silently kept; the user's correction governs, so the retraction stands and both sides above are retained as evidence. The earlier keep-ruling is SUPERSEDED, not pending.",
    "BD-04 (closed-by-user-adjudication): TM108/TM109 toggle threshold = rising Vth 4.4 V, Hys 0.35 V (OVERVIEW + meta). Conflict side retained: DFT.csv records 9/10 read 'rising vth 4.15V, hys 0.35V' (250 mV lower), and the TM109 row additionally contradicts itself - it drives vset[vac3,...] while the item is VAC2_PRST (VAC3 belongs to the neighbouring TM110 row), so the row's pin and its DMUX_SEL disagree. Both are preserved for the final report; neither is averaged.",
    "BD-01 limit conflict, preserved not averaged: TM600 OVERVIEW 11 mOhm vs DFT.csv 10 mohm; TM601 OVERVIEW 7.5 mOhm vs DFT.csv 8 mohm. Acceptance uses OVERVIEW; the DFT.csv values stay in the IR and the final report.",
    "TM601 current alias: OVERVIEW:994 writes the formula as Rds,on=(SW-PGND)/IPMID2SW while the DFT.csv row uses sw2pgnd and the row-inline sense label is PGND-SW. Same family as the historically recorded 'IPMID2SW' DFT defect (knowledge/claude-history/absorbed/34-b55b4f8d.md:58/83, TM607 case).",
    "TM601 polarity reading divergence: dft-ir describes the force as PMID(High)->SW(Low) while the netlist binds SW to the FPVIe0 LOW bus and PMID/PGND to the HIGH bus (schematic-ir openQuestions + hazards[polarity]). BD-02 (SW<->PGND force, SW-PGND sense) governs for this run.",
    "Legacy relay numbering in the knowledge base: bus-topology.md 五/六 and pin-resource-map.md still cite K31_BUS_PMID / K15_BUS_SW / K17_BUS_BST / K33_PGND, which have 0 hits in the current tree. Golden files cite K31_VBUSL_PMID and K17_BUSH_SW; both are old-generation names and must be converted before use (see the alias table's current K sets).",
    "Clamp API scope: team/EXECUTION_PLAN.md:81/129 states 'no SetClamp in this generation (0 hits)'. Measured: 0 hits only because the search root was the project tree; the SDK header FPVIe.h:101 and FXVIe.h:117/458 do declare SetClamp. RUN-LEDGER.md:220-222 is the correct record; the value itself remains open (BD-05).",
    "TM601 polarity wording: SD-4 (severity medium) fixes SW<->PGND as channel-0 low(SW) to high(PGND); dft-ir words TM601 as PMID(High)/SW(Low), which is not applicable. schematic-ir-sensing.json dfdPairVerdicts records it as an inverted orientation with fourWireProper=true. SD-4 governs.",
    "Parallel-site / shared-function note (SD-1): TM600 uses FPVIe channels 0+1 of a site while TM601 uses channel 0, so the two items can never be merged into one function or run concurrently on the same site; the same _S1S2 joint relays also mean a reconfiguration on one site disturbs the other.",
    "QTMU bridge vs TM600: every QTMU single-ended sense path needs K141 and/or K142, and those relays are hard-wired across FPVIe0_FH_BUS and FPVIe1_FH_BUS (K141 nets measured). For TM600, which occupies BOTH FPVIe channels, closing K141 would tie PMID to BST. A third, independent reason: the QTMU routes also depend on the K86/K130 force<->sense bridges that SD-2 requires to stay open. Registered so no one silently treats the QTMU variant as a usable alternate for TM600.",
    "PC route attribution: SCH-Connect-Map prints K87/K88/K89 inside the BUS [Kelvin] chains while schematic-ir hazards[measurement-validity] groups them with K90/K91 as 'the PC route'. Measured net membership puts the shunted PC nets (R1_CS/R2_CS on FPVIe0_FL_PC_S1) ONLY on K90/K91 (+K82); K87/K89 are the BUS-side force relays that double as 2-wire short hooks and K88 is the sense-release relay. Three sources, two wordings - recorded, with the net evidence preferred.",
    "Relay default-state semantics: SCH-Connect-Map L4 says 'Relay-NC = 默认导通', while schematic-ir polarity[Relay default polarity] says G6K mechanical default NC means 'Pin<->BUS blocked'. The connect-map legend and its per-line 需闭合 lists are treated as authoritative for actuation; the IR wording needs correction.",
    "FI command-sign convention (decided, recorded as U11): implementing the DFT literal direction means the COMMAND sign is derived from the terminal assignment - TM600 +1 A (HIGH = PMID) and TM601 -1 A (HIGH = PGND). The captain ruling is explicit that this is NOT escalated to the user and NOT a wiring blocking decision, because the delivery is code + compilation, R = |dV|/|dI| is magnitude-only, and direction only changes the body-diode state while the conducting device is fixed by the BD-03 0x5A bit. The three-step derivation chain must be reproduced in the plan and manifest for t6 review; the bring-up check is U11.",
    "Sense-path grade: the IR notes the Kelvin rows as '10 kOhm' but the measured values differ (R_PMID_KLV 10K, R_SW1_KLV 11K, R_SW2_KLV 10K, R_VCC_Kelvin 12K, R_VBAT_KLV 11K); and no Kelvin series resistor exists for the SW pin itself - the SW1/SW2 parts are on different nodes. Registered so downstream does not inherit the imprecise wording.",
    "DFT stimulus numeric self-inconsistency: TM600 iset[pmid2sw,1,1e-3,0] pairs 1A with a 1e-3 compliance argument and TM601 iset[sw2pgnd,1,1e-6,0] pairs 1A with 1e-6; the companion vset[pmid,...] carries a 100uA compliance. The intended compliance/range triple is unresolved (schematic-ir hazards[limit-inconsistency]).",
    "PMID setpoint divergence (now governed by BD-08): DFT.csv/OVERVIEW carry 15 V (TM600) / 9 V (TM601) while reg_config/tm600.sv, tm601.sv use 5 V; dft-ir had resolved to the reg_config values, but BD-08 (closed-by-user-adjudication) fixes the ATE stimulus at the DFT/OVERVIEW values and demotes the .sv 5 V to simulationDomainReference. The dft-ir resolution recorded here is therefore superseded for the ATE stimulus - the divergence itself is retained.",
    "Register comment vs value: DFT.csv comments name D2A_BUBO_TM_LSON for TM600 and D2A_BUBO_TM_HSON for TM601 while the .sv values are 0x5A=0x02 (TM600) / 0x5A=0x01 (TM601). BD-03 adopts the .sv mapping; the DFT comments stay registered as a suspected swap.",
    "bst2sw relay lists: K134/K135 appear in BOTH the CH1 High->BST and CH1 Low->SW 需闭合 lists, and K132 serves both SH1 and SL1 per SCH-Connect-Map L16/L19. Whether this is merged force/sense notation or a real shared relay is unresolved and must be settled by the relay-trace gate.",
    "sw2pgnd loop resource list: the IR's LOOP_TM601_SW2PGND_1A lists 133 and 134 (FPVIe1 relays) which the CH0 High->PGND 需闭合 group does not require. The union is recorded, not collapsed.",
    "FPVIe0 low terminals: TM600 lands FPVIe0 FL0 and FPVIe1 FL1 on the same SW node (schematic-ir U3); a common low is plausible but unproven from the netlist.",
    "Committed intermediates carry stale provenance: validation_manifest.json.txt records D:\\Newtest\\DSH\\ATE-Coding-Platform and path_proofs.json.txt records D:\\Newtest\\CLAUDE_PROCESS with a different CSV sha256 (schematic-ir U7), although the connect map regenerates byte-identically.",
]

# ============================ OPEN-ITEM NUMBERING (AUTHORITATIVE) ============================
# Captain ruling (latest, superseding two earlier statements):
#   U10 = QVM ch0 / FPVIe0 same-node concurrency   (test-plan.json already uses this id)
#   U11 = SIGN-CONVENTION - FI command-sign convention, bring-up item (not escalated to the user)
# History: the assignment was stated in the opposite order earlier in the run and the generator
# was edited by more than one member, so it flipped twice. This banner + the single-writer rule
# exist to stop that. Changing it again requires a Captain ruling plus a broadcast hash, because
# test-plan.json and the final acceptance report cross-reference these ids.
# =============================================================================================
open_items = [
    {"id": "BD-05", "topic": "clamp / compliance numeric value", "status": "CLOSED - provisional engineering default (see clampRuling)", "detail": "SetClamp(50,50) on the FPVIe_1V range during the 1 A force => +-0.5 V compliance, re-issued after every FV/FI mode switch. Provisional: it is the golden case's default, not this DUT's datasheet value; it bounds open-circuit/mis-wiring only and is never a pass/fail criterion. Scope: debug code and compilation for acceptance-20260916-dali10 only - no hardware authorization, no production-tree change. The two hardware risks it does NOT close are retained as U1 and U2 and must be listed in the final report's limitations."},
    {"id": "U1", "topic": "relay contact current rating for the 1A loops", "status": "OPEN (hardware)", "detail": "No datasheet in the workspace states the G6K-2G-Y (IM06DJR) / TLP3412 contact rating for the _S1S2 and BUS relays that must carry 1A."},
    {"id": "U2", "topic": "10kohm Kelvin rows in series with the FPVIe sense input", "status": "OPEN (hardware)"},
    {"id": "U3", "topic": "FPVIe0 FL0 and FPVIe1 FL1 both on the SW pin", "status": "OPEN"},
    {"id": "U4", "topic": "S10_CH0_A / S10_CH0_B source type (inferred QTMU, unconfirmed)", "status": "OPEN"},
    {"id": "U5", "topic": "must K84_HG2 (PMID default FXVIe_PLUS route) be opened while FPVIe owns PMID", "status": "OPEN"},
    {"id": "U6", "topic": "sanctioned discharge mechanism (no DCHG role in the current StdAfx.h)", "status": "OPEN", "detail": "Contract assumes cap-gate open + 1kohm bleed (~4.7ms tau on a 4.7uF rail)."},
    {"id": "U7", "topic": "provenance strings inside the committed intermediates", "status": "OPEN - noted, non-blocking for this run", "detail": "schematic-ir unresolvedTopology U7: validation_manifest.json.txt records an input path under ATE-Coding-Platform and path_proofs.json.txt records a CLAUDE_PROCESS path with a different CSV sha256 (5FEAADA5...), while re-running the pipeline from the current CSV produced a byte-identical connect map. Registered so the provenance mismatch is not mistaken for a content difference."},
    {"id": "U8", "topic": "formal rejection test for the K90_PC0 cross path (NC path cross-links high/low BUS)", "status": "OPEN"},
    {"id": "TM1205", "topic": "no numeric limit exists in any DFT source for TM1205 (TRX_BST_UV_GD)", "status": "OPEN"},
    {"id": "BD-01-SCOPE", "topic": "TM600/TM601 acceptance limits", "status": "CLOSED for this run", "detail": "OVERVIEW 11 / 7.5 mOhm govern this debug-copy acceptance only; reopen if a newer revision or approved record appears."},
    {"id": "BD-07", "topic": "'Y / 2 FLOAT' special flag on the TM600 OVERVIEW row", "status": "ASSUMPTION (recorded per test-strategy-architect, t4)", "detail": "Interpreted as two floating nodes (PMID and SW). Recorded as an assumption, not as a measured fact; the TM600 force/sense plan does not depend on any other reading of the flag."},
    {"id": "U10", "topic": "QVM ch0 concurrency (verbatim captain text)", "status": "OPEN - registered, NOT assumed", "detail": "U10 = QVM ch0 concurrency: the two-wire sense meter's channel 0 and the floating FPVIe0 channel can be forced onto the same nodes concurrently; the documentation does not state whether that is permitted, so it is registered as an open item and is NOT assumed. QVM ch0 is additionally recorded as NOT A KELVIN PAIR (mixed F/S landing)."},
    {"id": "U11", "topic": "SIGN-CONVENTION (verbatim captain text)", "status": "DECIDED - not escalated; OPEN only as a bring-up check", "detail": "U11 = SIGN-CONVENTION: the FPVIe ch0 terminal assignment is fixed by the netlist (PGND appears only on the HIGH side, SW only on the LOW side), so the iset sign semantics must be derived as alias direction -> instrument terminal -> command sign. Implement the DFT literal direction and never invert silently. Bring-up criteria: (1) the FET enabled by BD-03 0x5A is the conducting device; (2) |MVRET|/|MIRET| falls in 11 / 7.5 mohm rather than a body-diode drop; (3) MIRET magnitude matches the commanded value. Not escalated to the user (R uses |dV|/|I|; no hardware run in this scope)."},
    {"id": "U9", "topic": "sense-slot / driver-layer activation (RELAY_ON vs RELAY_SENSE_ON) and the DV-01 Delta-V form slot [formerly SENSE-FORM]", "status": "PENDING with bring-up criteria - decidable, not open-ended; DV-01 (corrected) fixes (a) as the implementation form", "alsoKnownAs": "SENSE-FORM", "detail": "Exclusions are now settled with two independent lines of evidence: QTMU is out (IR hazards[measurement-validity] severity high, mitigationRequired for TM600+TM601: 'do not measure RDSON on the QTMU defaults'; every QTMU path also carries K141/K142 which net-level data show bridging FPVIe0_FH_BUS with FPVIe1_FH_BUS and FPVIe0_FL_BUS with FPVIe1_FL_BUS) and QVM is out as a Kelvin pair (S8_QVM_CH0+ lands on PMID_F_S1/PGND_F_S1 with role=F while CH0- lands on SW_S_S1 with role=S - a mixed F/S landing). That leaves exactly two registered Delta-V forms: (a) the FPVIe sense pair SH0/SL0 (both legs role=S, true Kelvin at both ends) gated on the unevidenced driver-layer selection, and (b) two single-ended sense-pin reads from independent meters (S3_FXVIe_PLUS_SH1->PMID_S_S1 with no relays, S5_ACM200_SH8->SW_S_S1 via K61; TM601 uses S3_FXVIe_PLUS_SH3->PGND_S_S1 via K155), whose residual error is the offset mismatch between two independently referenced meters. Per DV-01 (corrected), (a) is the implementation form and (b) is only an alternate pending the QVM dispute and a signed-off instrument table. t4 may publish the sense-instrument slot as PENDING and t5 reuses the same skeleton."},
    {"id": "U2b", "topic": "R_PMID_KLV_S1 (10 kOhm) may sit in series with the PMID sense line", "status": "OPEN (pole-level trace or hardware)", "detail": "R_PMID_KLV_S1 = 10K connects the PMID rail node (K84 pin 2 side) to NetK84_HG2_S1_7 (K84 pin 7). If the sense line uses the pin-7 pole it traverses the tap: then error = I_bias x 10 kOhm, and a 1% budget on an 11 mV (TM600) / 7.5 mV (TM601) signal allows I_bias <= 11 nA / 7.5 nA - a uA-class input would add ~10 mV. No Kelvin series resistor exists for the SW pin (R_SW1/SW2 11K/10K belong to SW1/SW2)."},
    {"id": "DFT-COVERAGE", "topic": "TM001/TM102/TM135/TM1205 rows are absent from project/DALI/input/DFT.csv", "status": "OPEN", "detail": "project_config.json makes Dali_testmode.xlsx the authoritative DFT input, which is what dft-ir used."},
]

# normalize action ordering (1..N) so schema 'order' is dense and monotone
for _i, _a in enumerate(global_init, 1):
    _a["order"] = _i
for _i, _a in enumerate(global_cleanup, 1):
    _a["order"] = _i

contract = {
    "runId": RUN_ID,
    "revision": CONTRACT_REVISION,
    "generatedAt": GENERATED_AT,
    "idempotency": "Re-running this generator twice on unchanged inputs produces a BYTE-IDENTICAL artifact (generatedAt is derived from revision, not from the clock). Verified in t16 by comparing two consecutive runs.",
    "hashPolicy": "A sha256 of this file is only a build-time snapshot. Consumers must RECOMPUTE it (python, plaintext view, hashed over file BYTES) at reference time; cross-member messages must not use a hash as an anchor - use revision + generatedAt instead. PowerShell Get-FileHash reads ciphertext for files inside this run directory and will not match.",
    "generatedBy": "setup-architect (t3, attempt 1)",
    "integrityNotes": {
        "hashMethod": "Every sha256 in this file (inputs[], evidence[].sha256) was computed by reading the file with python (plaintext view).",
        "measuredToolDiscrepancy": "For files under team/artifacts/<run-id>/ the SHA256 read by PowerShell (Get-FileHash) DIFFERS from the SHA256 read by python for the same path and same byte length - consistent with the TSZ transparent-encryption layer being active in the run directory. Control measurement: team/schemas/setup-contract.schema.json (outside the run dir) gave the SAME digest from both tools (C7A84550E108AEBD26BA8B7D5DEFBAF247FCA521CB89CD4659B938EB111DEA9D).",
        "instructionToConsumers": "Pin the PYTHON/plaintext sha256 of this file (and of any run-dir artifact). A PowerShell-computed digest of a run-dir artifact will not match and is not evidence of tampering.",
        "inputsMovedDuringBuild": "dft-ir.json (mtime 09-16 14:15:18) and schematic-ir.json (mtime 09-16 14:15:05) were revised AFTER their tasks (t1/t2) completed and AFTER the first two revisions of this contract. This revision re-derives every per-TM table from that IR revision and re-reads all input hashes; inputs[] therefore carries the hashes of the revision actually consumed. Consumers must re-verify inputs[] before relying on the derived tables.",
        "frozenAuthorities": "SCH-Connect-Map.txt (sha cc8009fb..., mtime 09-16 13:45) and DFT.csv (sha b92d203f...) were unchanged across the whole build, so the authored alias table does not depend on the IR churn.",
        "builderEditedByThirdParty": "The generator was edited by more than one member during the run and the U10/U11 assignment flipped twice. FINAL and unified assignment (t16): U9 = sense-slot / driver-layer activation + the DV-01 form slot; U10 = QVM ch0 concurrency; U11 = SIGN-CONVENTION (FI command-sign, bring-up item). Every cross-reference in this artifact now uses that assignment; changing it again requires a captain ruling plus a broadcast of the new revision.",
        "tokenSearchDiscipline": "A 0-hit token search is never evidence of absence: the DFT sources use several spellings for the same path (pmid2sw / pmid_sw / sw2pmid; bst2sw / bst1_sw1 / bst2_sw2; pgnd2sw vs sw2pgnd). Every token search must declare its spelling set (arrow form, hyphen form, underscore form) and, where possible, be cross-checked against a second source. Measured example: pmid2sw = 10 hits in DFT.csv but 0 for pmid_sw there, while pmid_sw = 10 hits in _dump_OVERVIEW.txt - the same path, two vocabularies.",
    },
    "scope": SCOPE,
    "scopeNote": "global setup is defined once; every TM carries an explicit delta (no copied setup code)",
    "inputs": {p: h for p, h in HASH.items()},
    "resources": resources,
    "aliasResolution": alias_table,
    "aliasFlatTable": alias_flat,
    "aliasNamingVariants": VARIANT_ALIASES,
    "senseReachability": sense_reachability,
    "senseFormDecision": sense_form_decision,
    "senseFormOptions": sense_form_options,
    "sensingDecisions": sensing_decisions,
    "clampRuling": clamp_ruling,
    "deltaVFormRuling": delta_v_ruling,
    "irPathCrossReference": ir_path_crossref,
    "relayNameMap": relay_name_map,
    "kelvinRoutingDecision": kelvin_routing_decision,
    "polarityDecision": polarity_decision,
    "legacyKMap": legacy_k_map,
    "measurementPlan": measurement_plan,
    "registerMap": register_map,
    "relayStatePolicy": {        "legend": "SCH-Connect-Map L4: Relay-ON = 需SetOn闭合, Relay-NC = 默认导通, pairing tagged [Kelvin]/[PC短接]/[单线]",
        "rule": "the per-line 需闭合 list of the chosen group is the authoritative actuation set; every relay in an item's path must be given an explicit state",
        "kelvinBusRelaysArePassThroughNotActuated": "K87_KELVIN0_S1S2 / K88_KELVIN0_S1 / K89_KELVIN0_S1S2 (FPVIe0) and K131/K132/K133 (FPVIe1) are ROUTED THROUGH and kept at their DEFAULT state - they must NOT be SetOn. Evidence: L4 legend 'Relay-NC = 默认导通' plus the per-line listings L8-L19 '需闭合: 无(默认导通)'; the closedRelayNumbers of every mOhm route are only [83] / [60,61] / [154,155]. StdAfx.h:251-253 names them from the driven side (K87_FPVI0_FH_SL_SHORT, K88_FPVI0_Sense_FLOAT, K89_FPVI0_FL_SH_SHORT), which describes their hardware role, not an actuation requirement. Confirmed by captain ruling.",
        "connectMapVACReconciliation": "The connect-map VAC groups (L189/L195/L201) print '需闭合: K70,K87,K88,K90,K91', quoted verbatim in the vac1/vac2/vac3 alias entries. That list mixes two Relay-NC relays (K87/K88) with two PC-domain relays (K90/K91): acceptable for the DC/toggle ramp items, but it must NOT be read as a template for the mOhm Kelvin routes, where the rule is route-through K87/K88/K89 at default state and never K90/K91.",
        "kelvinPairs": "59 Kelvin pairs in scope with 0 pair failures (schematic-ir validation.counts)",
    },
    "globalInitialization": global_init,
    "globalCleanup": global_cleanup,
    "tmDeltas": tm_deltas,
    "safetyInvariants": safety,
    "conflicts": conflicts,
    "openItems": open_items,
    "evidence": [
        E_DFT("DFT.csv (alias rows 90-308)"),
        E_CMAP("需闭合 groups for every scope pin"),
        E_IR("dft/schematic IR cross-references"),
        E_SP("gen_paths.py --json build_path_list"),
        E_TM600SV("BD-03 register evidence"),
        E_TM601SV("BD-03 register evidence"),
        E_FPVIEH("SetClamp / ranges / MeasureVI"),
        E_FXVIEH("FXVIe_PLUS 1A ceiling"),
        E_RULES("R-PON L32 / R-POFF L33"),
        ev(os.path.join(RUN, "sch-paths.txt"), "human-readable path document", HASH[os.path.join(RUN, "sch-paths.txt")]),
    ],
}

# ==================== rev 25 (t49) - ADD-ONLY route-closure additions ====================
# Principle: ADD-ONLY. No existing value is deleted or flipped. Attestations that are in
# dispute are annotated as contested with both sides' locators, pending the owner ruling.
_rc = {
    "principle": "ADD-ONLY (t49): existing values are preserved verbatim; contested attributions gain annotations only.",
    "instrumentSplit": {
        "SW12_U1REF_BST_ACM": {"acm200Channel": 5,
            "locator": "Pin_Channel_define.h:20 _PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = 'S5_5,S6_5,S11_5,S12_5,S21_5,S22_5,S27_5,S28_5'"},
        "PB0_BST_ACM": {"acm200Channel": 18,
            "locator": "Pin_Channel_define.h:33 (S5_18,...) - a DIFFERENT instrument object"},
        "note": ("AUTHORITATIVE LINE (t43): the channel attribution is UNKNOWN (constrainable). t43 accepts and strengthens step 1 "
                 "(the trailing token is a CHANNEL INDEX: 192 _GROUP_CHANNEL_DEFINE_ACM_GRP_ tokens whose second token set is exactly {0..23}) "
                 "but does NOT endorse the inference that [48,76] is therefore required, and records a netlist counter-view in which the three "
                 "channels use disjoint relays (FH5->K48/K76->BST ; FH8->K60/K61->SW ; FH18->K109/K110). BOTH routes coexist; this batch uses the "
                 "INTERSECTION treatment (TM600 gains K48/K76 while K109/K110 are retained this round). Any earlier wording stating t42/t44 as a "
                 "settled channel-5 determination is superseded by this note. See review/t43-t42-review-and-unknown-ruling.md.")},

    "acm200ChannelSplit": {
        "acm5": {"instrument": "SW12_U1REF_BST_ACM",
                 "bstSide": {"relays": ["K48_ACM5_AMP_REF", "K76_ACM_BST"], "needsClosed": [48, 76],
                             "locators": ["StdAfx.h:620 #define K_BST_ACM 48,76",
                                          "SCH-Connect-Map.txt:672-674 (BST need-closed K48,K76; FH5->K48->K76->BST_F)",
                                          "IR accepted_path_proofs[S5_ACM200_FH5->BST_F_S1].required_on=[48,76]",
                                          "test.cpp:7000/7085/7087/7170/7513 (production SetOn closes K48_ACM5_AMP_REF+K76_ACM_BST)",
                                          "test.cpp:6997/7085 comment 'BST <- SW12_U1REF_BST_ACM: K48_ACM5_AMP_REF + K76_ACM_BST (FH5->BST)"]},
                 "swSide": {"relays": ["K60_BUSL0_VCP", "K61_ACM8_SW"], "needsClosed": [60, 61],
                            "locators": ["StdAfx.h:490 #define K_FPVIL_TO_SW_A 60,61",
                                         "IR accepted_path_proofs[S1_FPVIe_FL0->SW_F_S1].required_on=[60,61]"]},
                 "crossDomainClosure": [48, 60, 61, 76],
                 "crossDomainNote": "composite of two families: BST side is ACM200 family, SW side is FPVIe[L] family"},
        "acm18_PB0_BST": {"instrument": "PB0_BST_ACM",
                          "relays": ["K110_ACM18_BST"], "needsClosed": [110],
                          "locators": ["Pin_Channel_define.h:33", "SCH-Connect-Map.txt:724/725 (FH18 -> K110(NC) -> PB0_F/PB0_S)",
                                       "IR accepted_path_proofs[S5_ACM200_FH18->BST_F_S1].required_on=[110]"],
                          "note": "listed separately for its own use; not this baseline instrument's BST route"},
    },
    "contestedAttribution": {
        "field": "aliasResolution[bst2sw].resolution.closedRelayNumbers",
        "existingValue": [110, 61],
        "status": "CONTESTED - preserved (add-only) pending owner ruling",
        "sideA_channel5": {"claim": "channel-5 reading (side A): the bst2sw instrument is channel 5; BST side needs [48,76]; BST-SW closure [48,60,61,76] - CONTESTED, not settled (t43: UNKNOWN/constrainable)",
                            "locators": ["t42 (requirements, pass)", "t44 addendum", "compile-diagnostician control group 5/5",
                                         "Pin_Channel_define.h:20", "StdAfx.h:620", "test.cpp:7000/7085/7087/7170/7513"]},
        "sideB_channel18": {"claim": "channel-18 reading (side B): the existing mapping [110,61] (K110_ACM18_BST) applies - preserved verbatim; t43 rules the choice UNKNOWN/constrainable",
                             "locators": ["aliasResolution[bst2sw].resolution.relayChain (this artifact)",
                                          "IR accepted_path_proofs[S5_ACM200_FH18/BST] required_on=[110] (channel 18)"]},
        "pendingOwnerRuling": "t43 (independent review of the t42 channel ruling) - remit also covers the K109/K110 disposition and whether a channel-18 closure is permitted.",
    },
    "relayChainDerivation": {"relayChainHigh": None, "relayChainLow": None,
        "note": "no derivation is asserted for the side-by-side split; recorded as null rather than guessed (add-only)."},
    "pendingRegistrations": [
        {"id": "R1", "item": "tmDeltas.TM600.aliasesUsed += 'bst2sw'",
         "evidence": "DFT.csv TM600 row (csv row 19) declares vset[bst2sw,5,1e-3,0]; aliasResolution[bst2sw].usedByTm already lists TM600",
         "status": "pending owner disposition (add-only: current value ['pmid2sw'] preserved)"},
        {"id": "R2", "item": "TM1205 moved out of aliasResolution[bst2sw].usedByTm into bst1_sw1 / bst2_sw2 variant entries",
         "evidence": "IR: 16 accepted paths ending at BST1_*/BST2_* with NO 110 in required_on; deployed TM1205 paths use K_FPVIH_TO_SW1_A + K_FPVIL_TO_BST1_A variants",
         "status": "pending owner disposition (add-only: current usedByTm preserved)"},
        {"id": "R3", "item": "tmDeltas.TM1205.aliasesUsed is EMPTY while usedByTm lists TM1205",
         "evidence": "tmDeltas.TM1205.aliasesUsed = []", "status": "pending owner disposition"},
        {"id": "R4", "item": "TM601 explicit registration: no BST node/route; ACM200 BST drive not used",
         "evidence": "TM601.aliasesUsed=[sw2pgnd]; scopePins has no BST; pinRouteTable has no BST key; relaySet has no 109/110; DFT.csv TM601 row declares no bst2sw; t39/t40 both determined the removed ACM drive must not reach BST",
         "status": "registered here (add-only)"},
    ],
    "tm601BstRegistration": {"tm": "TM601_LS_RDSON", "bstRail": "NONE - not applicable",
        "statement": "TM601 has no BST node/route and must not use the ACM200 BST drive; its excitation is SW-PGND via FPVIe0 CH0 with closure [60,61] + [154,155] (= aliasResolution[sw2pgnd]).",
        "addedBy": "t49 (rev 25), add-only"},
    "legacyKMapAdditionalLeg": {"entry": "legacyKMap.mapping[2] (K17_BUS_BST / K17_BUSH_SW)",
        "addedLeg": {"leg": "ACM200 channel 5 -> BST", "relays": ["K48_ACM5_AMP_REF", "K76_ACM_BST"], "needsClosed": [48, 76],
                     "locator": "StdAfx.h:620; SCH-Connect-Map.txt:672-674"},
        "note": "the existing two legs are preserved verbatim; this third leg is appended (add-only)."},
    "alternativesDisambiguation": {"entry": "aliasResolution[bst2sw].alternatives[0]",
        "annotation": "this alternative is the channel-18 form (ACM200 FH18 -> BST via K110_BST; FH8 -> SW via K61_SW); it is the only place where [110,61] legitimately applies. The channel-5 form (SW12_U1REF_BST_ACM) is the baseline and is listed in acm200ChannelSplit above.",
        "addedBy": "t49 (rev 25), add-only"},
}
contract["_t30ExpectationNote"] = {"tm": "TM600_HS_RDSON",
    "expectedUnion": [48, 60, 61, 76, 83],
    "derivation": "three-source union: K_BST_ACM (48,76) + K_FPVIL_TO_SW_A (60,61) + pmid2sw (83,60,61); recorded so the gate expectation can be recomputed after t43 without re-deriving it from prose.",
    "status": "annotation only (add-only); the t30 gate script itself is outside this task scope"}
contract["routeClosureMapping"] = _rc
# in-place ANNOTATIONS (never deleting or rewriting existing values)
for _a in contract.get("aliasResolution", []):
    if _a.get("alias") == "bst2sw":
        _a["contestedAttribution"] = _rc["contestedAttribution"]
        _a["relayChainDerivation"] = _rc["relayChainDerivation"]
        for _alt in (_a.get("alternatives") or []):
            _alt["channel18Disambiguation"] = _rc["alternativesDisambiguation"]["annotation"]
for _tm, _reg in (("TM601", _rc["tm601BstRegistration"]),):
    if _tm in contract.get("tmDeltas", {}):
        contract["tmDeltas"][_tm]["bstRegistration"] = _reg
for _m in (contract.get("legacyKMap", {}) or {}).get("mapping", []) or []:
    if isinstance(_m, dict) and str(_m.get("legacy", "")).startswith("K17_BUS_BST"):
        _m.setdefault("additionalLegs", []).append(_rc["legacyKMapAdditionalLeg"]["addedLeg"])
        _m["additionalLegsNote"] = _rc["legacyKMapAdditionalLeg"]["note"]
# structured alias -> TM ownership (add-only view)
_own = {}
for _a in contract.get("aliasResolution", []):
    _own[_a.get("alias")] = {"declaredByUsedByTm": _a.get("usedByTm"),
                             "closedRelayNumbers": (_a.get("resolution") or {}).get("closedRelayNumbers")}
for _tm, _d in (contract.get("tmDeltas", {}) or {}).items():
    for _al in (_d.get("aliasesUsed") or []):
        _own.setdefault(_al, {}).setdefault("declaredByTmDeltasAliasesUsed", []).append(_tm)
contract["aliasOwnership"] = {"builtFrom": "aliasResolution[].usedByTm + tmDeltas[].aliasesUsed",
                              "entries": _own, "pendingCorrections": _rc["pendingRegistrations"][:3],
                              "note": "view only - no existing registration is modified by rev 25 (add-only)."}
contract["terminologyNote"] = {
    "derivedMapLabels": "In the derived connect map, '(Relay-NC)' denotes the relay's UN-ACTUATED path and '(Relay-ON)' the ACTUATED path - they do NOT denote contact types. Recommended wording: 'un-actuated' / 'actuated'.",
    "terminalTableSelfConsistency": "relays.md L21/L26 table rows (pin 2/7 = NO conducts when unpowered), L29 mnemonic and L31 warning are MUTUALLY CONSISTENT; the misreading risk comes from the label semantics, not from an internal contradiction.",
    "negativeListRule": "Default-conducting relays (e.g. K87/K88/K89) must NOT be added to any required-on/SetOn set and must not be actuated; 'force open' is not achievable through a SetOn list.",
    "addedBy": "t49 (rev 25), add-only"}
# acc2/acc4/acc5 refinements (still add-only)
contract["closedRelayNumbersByRoute"] = {
    "acm200_ch5_bst": [48, 76],
    "acm200_ch5_sw": [60, 61],
    "acm200_ch5_bst_sw_closure": [48, 60, 61, 76],
    "acm200_ch18_pb0_bst": [110],
    "fpvie_ch0_low_to_bst": [109, 110, 138, 139, 145, 146],
    "s10_ch0_b_to_bst": [109, 110],
    "locators": {"acm200_ch5_bst": ["StdAfx.h:620 K_BST_ACM", "SCH-Connect-Map.txt:672-674",
                                     "IR accepted_path_proofs[S5_ACM200_FH5/SH5 -> BST_F/S].required_on=[48,76]",
                                     "test.cpp:6997 comment + L7000/L7085/L7087/L7170/L7513 SetOn"],
                 "acm200_ch5_sw": ["StdAfx.h:490 K_FPVIL_TO_SW_A", "IR accepted_path_proofs[S1_FPVIe_FL0/SL0 -> SW_F/S].required_on=[60,61]"],
                 "acm200_ch18_pb0_bst": ["Pin_Channel_define.h:33 (S5_18)", "SCH-Connect-Map.txt:724/725", "IR accepted_path_proofs[S5_ACM200_FH18->BST_F_S1].required_on=[110]"]},
    "note": "route-split view (add-only). The aliasResolution[bst2sw] value [110,61] is preserved and annotated as contested.",
    "addedBy": "t49 (rev 25)"}
for _r in (contract.get("resources") or []):
    _cs = _r.get("channelsInScope") if isinstance(_r, dict) else None
    if isinstance(_cs, dict) and "BST" in _cs:
        _cs["BST_routes"] = {"acm200_ch5": "S5_ACM200_FH5/SH5 (SW12_U1REF_BST_ACM) -> K48+K76 -> BST_F/S",
                             "acm200_ch18": "S5_ACM200_FH18/SH18 (PB0_BST_ACM) -> K110 -> BST_F/S",
                             "note": "both routes coexist; this label does not exclude either reading (add-only; the original BST string is preserved verbatim)"}
for _pr in contract["routeClosureMapping"]["pendingRegistrations"]:
    if _pr["id"] == "R2":
        _pr["variantRows"] = {"bst1_sw1": [46, 41], "bst2_sw2": [46, 49, 41, 43],
            "locator": "deployed TM1205-family SetOn uses K_FPVIH_TO_SW1_A / K_FPVIL_TO_BST1_A / K_FPVIL_TO_BST2_A variants (test.cpp:8791/8835); IR: 16 accepted BST1_*/BST2_* paths with no 110"}
# ===== rev 27 (t49 follow-up): guardrails, locator verification, relay release semantics =====
contract["revision27Bindings"] = {
    "guardrail_usedByTm": {
        "rule": "When aliasResolution[bst2sw].usedByTm is finally revised it must contain ONLY TM600; TM1205 moves out; TM601 must NEVER be added.",
        "tm601Rationale": "TM601's rail is carried by its own alias sw2pgnd = [154,155,60,61] (deployed TM601 setOn already superset-satisfies it) so under the CURRENT contract TM601 evaluates GREEN. Adding TM601 to bst2sw would make the gate demand [48,76] for TM601 => a FALSE RED, and would push the implementation to re-add an ACM drive for TM601 - the very drive t38 removed because TM601 has no BST requirement.",
        "recordedBy": "t49 follow-up (captain binding 1)"},
    "locatorVerification_tm1205": {
        "claimUnderTest": "schematic-expert: TM1205's expectation comes from aliasFlatTable[14] bst1_sw1 / [15] bst2_sw2",
        "claimedPathVerified": False,
        "claimedPathProblem": "the claimed parent path 'tmDeltas.TM1205.aliasFlatTable' does NOT exist (tmDeltas.TM1205 has no aliasFlatTable key) - the entries live in the TOP-LEVEL aliasFlatTable",
        "actualPaths": {"aliasFlatTable[14]": {"alias": "bst1_sw1", "kNumbers": [46, 41], "relayPath": "CH0 High -> SW1 needs K46 ; CH0 Low -> BST1 needs K41"},
                        "aliasFlatTable[15]": {"alias": "bst2_sw2", "kNumbers": [46, 49, 41, 43], "relayPath": "CH0 High -> SW2 needs K46,K49 ; CH0 Low -> BST2 needs K41,K43"}},
        "negativeFindingNotReproducible": "a claim that the contract contains NO bst1_sw1 / bst2_sw2 rows is NOT reproducible: the literals occur 14 and 7 times respectively in this artifact (the top-level table holds them).",
        "conclusion": "the variant rows EXIST and TM1205 can be bound to aliasFlatTable[14]/[15]; no unverifiable locator is used in this artifact.",
        "supportingFacts": ["deployed TM1205 setOn = {13,65} (K_FPVIH_TO_SW1_A=46, K_FPVIL_TO_BST1_A=41) => unrelated to [110,61]",
                            "the default gate scope --tm-scope is TM600/TM601 only and excludes TM1205, so no false red arises here",
                            "tmDeltas.TM1205.aliasesUsed is EMPTY while aliasResolution[bst2sw].usedByTm lists TM1205 (registration item R2/R3)"],
        "recordedBy": "t49 follow-up (captain binding 2)"},
    "relayReleaseSemantics": {
        "principle": "RELEASE != NON-CONDUCTING: the semantic of an un-actuated relay depends on its class (relays.md:29/95/96 + Component-Statistic class + CSV part number).",
        "classes": {"BUS + TLP3412 (MOS)": {"relays": ["K46", "K41"], "releaseMeans": "OPEN (no conducting path)",
                                            "codes": ["K46_BUS0_FH_SW1", "K41"]},
                    "Share + IM06DJR (G6K changeover)": {"relays": ["K48", "K49", "K76", "K110", "K43"], "releaseMeans": "the DEFAULT channel conducts",
                                                          "codes": ["K48_ACM5_AMP_REF", "K49", "K76_ACM_BST", "K110_ACM18_BST", "K43"]},
                    "BUS + G6K": {"relays": ["K109"], "releaseMeans": "default channel conducts (BUS-class G6K)"}},
        "mechanismConsequence": ("TM600 omitting K48 does NOT open the channel-5 source: it leaves it at K48's default destination -> K49 -> SW1 (that is the 're-routed, not opened' mechanism). "
                                 "K46 is MOS, so omitting it DOES open the FPVIe0 high-side BUS (not connected). K110 defaults to the PB0 side, so channel 18 is likewise not on the BST node."),
        "recordedBy": "t49 follow-up (captain binding 3)"},
    "pairedRelayOffRuling": {
        "ruling": "For TM600 a paired explicit RELAY_OFF alongside closing 48/76 is NOT a load-bearing obligation: the other relays sharing this source are already exclusively released by their own releasers, and MOS-class omissions are open by nature.",
        "therefore": "adding [48,76] (and the later removal of K109/K110) is sufficient; do NOT elevate 'paired RELAY_OFF' into a general contract invariant - that is a wider decision and must be taken separately.",
        "recordedBy": "t49 follow-up (captain binding 4)"},
}
# ===== rev 28: captain-authorised TM1205 binding (locator now verified) =====
_pre_used = None
for _a in contract.get("aliasResolution", []):
    if _a.get("alias") == "bst2sw":
        _pre_used = list(_a.get("usedByTm") or [])
        _a["usedByTm"] = ["TM600 (BST must lead PMID)"]
        _a["usedByTmProvenance"] = {"previousValue": _pre_used,
            "changedIn": "rev 28 (t49 follow-up, captain-authorised once the variant locator was verified)",
            "why": "TM1205's expectation comes from the aliasFlatTable[14]/[15] variant rows (bst1_sw1 / bst2_sw2), not from bst2sw; deployed TM1205 setOn = {13,65} (K_FPVIH_TO_SW1_A=46, K_FPVIL_TO_BST1_A=41) is unrelated to [110,61].",
            "guardrail": "TM601 MUST NEVER be added to this list: TM601's rail is carried by sw2pgnd=[154,155,60,61] (deployed setOn already satisfies it), so including TM601 would make a gate that reads this field demand [48,76] and produce a FALSE RED - and would push the implementation to re-add the ACM drive that t38 removed."}
if "TM1205" in contract.get("tmDeltas", {}):
    _t = contract["tmDeltas"]["TM1205"]
    _t["aliasesUsed"] = ["bst1_sw1", "bst2_sw2"]
    _t["aliasBinding"] = {
        "aliasesUsedProvenance": {"previousValue": [], "changedIn": "rev 28 (t49 follow-up)"},
        "source": "aliasFlatTable[14] / aliasFlatTable[15] (TOP-LEVEL table; the earlier claim of a per-TM tmDeltas.TM1205.aliasFlatTable path was wrong-parent)",
        "binding": {"bst1_sw1": {"aliasFlatTableIndex": 14, "kNumbers": [46, 41],
                                 "relayPath": "CH0 High -> SW1 needs K46 ; CH0 Low -> BST1 needs K41",
                                 "deployedLocator": "test.cpp:8791 = K_FPVIH_TO_SW1_A(=46) + K_FPVIL_TO_BST1_A(=41)"},
                    "bst2_sw2": {"aliasFlatTableIndex": 15, "kNumbers": [46, 49, 41, 43],
                                 "relayPath": "CH0 High -> SW2 needs K46,K49 ; CH0 Low -> BST2 needs K41,K43",
                                 "deployedLocator": "test.cpp:8835 = K_FPVIH_TO_SW2_A(=46) + K_FPVIL_TO_BST2_A(=41)"}},
        "polarityDivergenceRecordOnly": {"bst1_sw1": "aliasFlatTable[14].divergence records the OPPOSITE polarity to bst2sw (SW1 on the HIGH terminal, BST1 on the LOW terminal)",
                                          "bst2_sw2": "aliasFlatTable[15] shares bst1_sw1's polarity divergence",
                                          "note": "RECORDED ONLY - no electrical conclusion is drawn here; any electrical meaning belongs to the owner / bench evidence."},
        "verificationNote": "the pair also confirms why no [110] appears in TM1205's paths: IR shows 16 accepted BST1_*/BST2_* endpoint paths with no 110 in required_on.",
        "recordedBy": "rev 28 (t49 follow-up)"}
contract["registrationApplication"] = {
    "R1": {"status": "PENDING (not applied)", "item": "tmDeltas.TM600.aliasesUsed += bst2sw"},
    "R2": {"status": "APPLIED in rev 28", "item": "TM1205 moved out of aliasResolution[bst2sw].usedByTm and bound to the aliasFlatTable[14]/[15] variant rows"},
    "R3": {"status": "APPLIED in rev 28", "item": "tmDeltas.TM1205.aliasesUsed filled ([] -> [bst1_sw1, bst2_sw2])"},
    "R4": {"status": "APPLIED in rev 25", "item": "TM601 registration: no BST node/route; ACM200 BST drive not used"},
    "note": "R1 remains pending because the captain has not yet dispositioned it; R2/R3 are applied here under the captain's explicit instruction for t49, with the previous values preserved in *Provenance keys."}
# ================== end rev 25 additions ==================

out = os.path.join(RUN, "setup-contract.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(contract, fh, ensure_ascii=False, indent=2)
print("wrote", out, os.path.getsize(out), "bytes")
print("resources", len(resources), "aliases", len(alias_table), "tmDeltas", len(tm_deltas),
      "init", len(global_init), "cleanup", len(global_cleanup), "safety", len(safety))
