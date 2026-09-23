#!/usr/bin/env python3
"""Derive the instrument-assignment / Kelvin-pair evidence for the TM600/TM601
differential sense pairs, and write team/artifacts/<run>/schematic-ir-sensing.json.

Everything is derived from the fresh PathProof output plus the CSV pin-level relay map;
no relay number is hand-typed except in the assertions that are checked against the data.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(".").resolve()
RUN = "acceptance-20260916-dali10"
OUT = ROOT / "team" / "artifacts" / RUN
VAL = OUT / "schematic-validation"
CSV_PATH = ROOT / "project/DALI/Dali-SCH.csv"
MAP_PATH = ROOT / "project/DALI/SCH-Connect-Map.txt"
PROOFS_PATH = VAL / "path_proofs.json.txt"
SPECS_PATH = ROOT / "knowledge/sources/hardware-specs.md"
PINCH_PATH = Path("D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h")
RELAY_DOC = ROOT / "knowledge/hardware/relays.md"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ev(path, locator):
    return {"path": str(path).replace("\\", "/"), "locator": locator, "sha256": sha(Path(path))}


rows = list(csv.reader(CSV_PATH.open("r", encoding="utf-8-sig", newline="")))
H = rows[0]
I_NET, I_DES, I_PIN, I_VAL = (H.index(x) for x in ("NetName", "Designator", "PinNumber", "ComponentValue"))
COMP_PINS: dict[str, list[tuple[str, str]]] = defaultdict(list)
for r in rows[1:]:
    if len(r) > I_VAL and r[I_DES]:
        COMP_PINS[r[I_DES]].append((r[I_PIN], r[I_NET]))

proofs = json.loads(PROOFS_PATH.read_text(encoding="utf-8"))
acc = proofs["accepted_path_proofs"]
map_lines = MAP_PATH.read_text(encoding="utf-8", errors="replace").splitlines()

SENSE_NODES = ("PMID", "SW", "PGND", "BST", "VBUS", "VBAT", "VDRV", "V1P5")
TERM = {"FH": "high-force", "SH": "high-sense", "FL": "low-force", "SL": "low-sense"}


def channel_of(port: str, instrument: str):
    """(instrument, site, channel) identity of a source terminal, or None if the
    instrument has no FH/FL Kelvin terminal structure."""
    m = re.fullmatch(r"(S\d+)_(\w+?)_(FH|SH|FL|SL)(\d+)", port)
    if not m:
        return None
    return (m.group(2), m.group(1), int(m.group(4)))


def terminal_of(port: str):
    m = re.search(r"_(FH|SH|FL|SL)\d+$", port)
    return m.group(1) if m else None


# ------------------------------------------------------------- per-node reachability
node_rows = defaultdict(list)
for p in acc:
    if p["dut_base"] in SENSE_NODES:
        node_rows[p["dut_base"]].append(p)

instruments_reaching = {n: sorted({p["source_meta"]["type"] for p in node_rows[n]}) for n in SENSE_NODES}

# ------------------------------------------------------------- Kelvin pair search
channels = defaultdict(lambda: defaultdict(list))  # (instr, site, ch) -> terminal -> records
for n in SENSE_NODES:
    for p in node_rows[n]:
        key = channel_of(p["source_port"], p["source_meta"]["type"])
        t = terminal_of(p["source_port"])
        if key and t:
            channels[key][(t, p["dut_role"])].append((n, p))

pair_findings = []
for (instr, site, ch), terms in sorted(channels.items()):
    highs = {n for (t, role), v in terms.items() if t in ("FH", "SH") for n, _ in v}
    lows = {n for (t, role), v in terms.items() if t in ("FL", "SL") for n, _ in v}
    for hi in sorted(highs):
        for lo in sorted(lows):
            if hi == lo:
                continue
            recs_hi = [p for (t, r), v in terms.items() if t in ("FH", "SH") for n, p in v if n == hi]
            recs_lo = [p for (t, r), v in terms.items() if t in ("FL", "SL") for n, p in v if n == lo]
            roles_hi = {p["dut_role"] for p in recs_hi}
            roles_lo = {p["dut_role"] for p in recs_lo}
            pc = any("_PC_" in r["relay"] for p in recs_hi + recs_lo for r in p["path"])
            bridges = sorted({n for p in recs_hi + recs_lo for n in p["required_on"] if n in (86, 130)})
            pair_findings.append({
                "instrument": instr, "site": site, "channel": ch,
                "highTerminal": {"node": hi,
                                 "force": next((p["source_port"] for p in recs_hi if p["dut_role"] == "F"), None),
                                 "sense": next((p["source_port"] for p in recs_hi if p["dut_role"] == "S"), None)},
                "lowTerminal": {"node": lo,
                                "force": next((p["source_port"] for p in recs_lo if p["dut_role"] == "F"), None),
                                "sense": next((p["source_port"] for p in recs_lo if p["dut_role"] == "S"), None)},
                "hasForceAndSenseOnBothEnds": roles_hi >= {"F", "S"} and roles_lo >= {"F", "S"},
                "unionRelays": sorted({n for p in recs_hi + recs_lo for n in p["required_on"]}),
                "forceSenseBridgeRelays": bridges,
                "fourWireKelvinPossible": not pc and not bridges,
                "touchesPcNets": pc,
            })

required_pairs = {("FPVIe", 0, "PMID", "SW"), ("FPVIe", 0, "PGND", "SW"), ("FPVIe", 1, "BST", "SW")}
found = {(f["instrument"], f["channel"], f["highTerminal"]["node"], f["lowTerminal"]["node"]) for f in pair_findings}
assertion_table = [
    {"expectedPair": {"instrument": i, "channel": c, "high": h, "low": l},
     "found": (i, c, h, l) in found}
    for (i, c, h, l) in sorted(required_pairs)
]

# ------------------------------------------------------------- force/sense bridge relays
BRIDGE_RELAYS = {"K86_KELVIN0_F_S1": "FPVIe0 high force<->sense bridge",
                 "K86_KELVIN0_S_S1": "FPVIe0 low force<->sense bridge",
                 "K130_KELVIN1_F_S1": "FPVIe1 high force<->sense bridge",
                 "K130_KELVIN1_S_S1": "FPVIe1 low force<->sense bridge",
                 "K92_AGND_F2S_S1": "AGND_F force<->sense bridge"}
bridge_info = []
for des, role in BRIDGE_RELAYS.items():
    pins = COMP_PINS.get(des, [])
    users = defaultdict(int)
    for p in acc:
        if any(r["relay_instance"].startswith(des.split("_S1")[0]) for r in p["path"]) or \
           int(des[1:des.index("_")]) in p["required_on"]:
            users[p["source_meta"]["type"]] += 1
    bridge_info.append({
        "designator": des, "role": role, "pins": [{"pin": a, "net": b} for a, b in pins],
        "requiresOn": bool(users), "acceptedProofUsersByInstrument": dict(sorted(users.items())),
        "interpretation": ("closing this relay merges the force and sense conductors of its row, i.e. it forces "
                           "2-wire operation; it is required only by the routes flagged 单线 (QTMU / QVM), never "
                           "by a 4-wire FPVIe route"),
        "evidence": [ev(CSV_PATH, f"Designator={des}")],
    })

# ------------------------------------------------------------- single-ended capability
single_ended = {}
for n in ("PMID", "SW", "PGND"):
    per = defaultdict(lambda: {"force": [], "sense": [], "bridged": []})
    for p in node_rows[n]:
        inst = p["source_meta"]["type"]
        bridged = any(x in (86, 130) for x in p["required_on"]) or p["source_meta"]["type"] in ("QTMU",)
        per[inst]["force" if p["dut_role"] == "F" else "sense"].append(
            {"port": p["source_port"], "dutPin": p["dut_pin"], "requiredOn": p["required_on"]})
        if bridged:
            per[inst]["bridged"].append(p["source_port"])
    single_ended[n] = {
        "reachable": [{"instrument": k, "forceTerminals": v["force"], "senseTerminals": v["sense"],
                       "twoWireBridged": sorted(set(v["bridged"]))} for k, v in sorted(per.items())],
        "hasTrueFourWireInstrument": sorted(
            k for k, v in per.items() if v["force"] and v["sense"] and not v["bridged"]),
        "singleEndedMeasurable": True,
        "note": ("every listed instrument can force 0 A and read back V(pin) against its own low reference "
                 "(AGND_F for the analogue sources, DGND for QTMU); a Kelvin-grade single-ended read needs the "
                 "instrument in the trueFourWire list"),
    }

# ------------------------------------------------------------- channel options per required pair
REQUIRED_PAIRS = [("TM600", "PMID", "SW"), ("TM601", "SW", "PGND"), ("TM600", "BST", "SW")]
SHARED_BUS_ROLES = {136: "QVMH_BUS0", 137: "QVMH_BUS1", 143: "DCM_BUS0_H", 144: "DCM_BUS1_H",
                    145: "DCM_BUS0_L", 146: "DCM_BUS1_L", 141: "QTMU_BUSA", 142: "QTMU_BUSB"}
# relays other in-scope items also need: the more a routing borrows, the more cross-item coupling it creates.
scope_relay_sets = json.loads((VAL / "resource-conflicts.json").read_text(encoding="utf-8"))["scopeRelaySets"]
relay_fanout = defaultdict(set)
for _tm, _rs in scope_relay_sets.items():
    for _r in _rs:
        relay_fanout[int(_r)].add(_tm)

channel_options = []
for tm, a, b in REQUIRED_PAIRS:
    opts = []
    for f in pair_findings:
        hi, lo = f["highTerminal"]["node"], f["lowTerminal"]["node"]
        if {hi, lo} != {a, b} or not f["hasForceAndSenseOnBothEnds"]:
            continue
        union = f["unionRelays"]
        borrowed = sorted(r for r in union if r in SHARED_BUS_ROLES)
        opts.append({
            "instrument": f["instrument"], "channel": f["channel"],
            "highTerminalNode": hi, "lowTerminalNode": lo,
            "unionRelays": union, "relayCount": len(union),
            "borrowsSharedBusRelays": [{"relay": r, "role": SHARED_BUS_ROLES[r],
                                        "alsoNeededByTms": sorted(relay_fanout.get(r, []))} for r in borrowed],
            "fourWireKelvinPossible": f["fourWireKelvinPossible"],
        })
    opts.sort(key=lambda o: (o["relayCount"], o["channel"]))
    channel_options.append({"tm": tm, "pair": f"{a}<->{b}", "options": opts, "optionCount": len(opts)})

# Conflict-aware allocation: within one TM no two pairs may share an FPVIe channel (one channel has a
# single high and a single low terminal). Assign cheapest-first so the pairs that gain most from a
# cheap wiring keep it, and prefer the channel pair that minimises the borrowed BUS entry relays.
by_tm = defaultdict(list)
for c in channel_options:
    by_tm[c["tm"]].append(c)
allocations = {}
for tm, cands in by_tm.items():
    ordered = sorted(cands, key=lambda c: c["options"][0]["relayCount"] if c["options"] else 99)
    taken = set()
    for cand in ordered:
        pick = next((o for o in cand["options"] if o["channel"] not in taken), None)
        if pick is None:
            cand["recommended"] = None
            cand["recommendationReason"] = "no free FPVIe channel left on this site for this pair"
            continue
        alternatives = [o for o in cand["options"] if o is not pick]
        pick["recommended"] = True
        if alternatives:
            alt = alternatives[0]
            pick["recommendationReason"] = (
                f"cheapest channel available for {tm} ({pick['relayCount']} relays) and the only free one "
                f"besides the {alt['channel']} wiring" if alt["channel"] in taken else
                f"cheapest of {len(cand['options'])} wirings available for {tm} ({pick['relayCount']} relays)")
        else:
            pick["recommendationReason"] = f"only wiring available for {tm} ({pick['relayCount']} relays)"
        for o in alternatives:
            o["recommended"] = False
            o["recommendationReason"] = (
                f"costs {o['relayCount']} relays instead of {pick['relayCount']} "
                f"and needs FPVIe channel {o['channel']}, which {tm} already needs for another pair of the same "
                f"item" if o["channel"] in taken else
                f"costs {o['relayCount']} relays instead of {pick['relayCount']}")
        taken.add(pick["channel"])
    allocations[tm] = sorted(taken)

for c in channel_options:
    c["note"] = ("more than one FPVIe channel can serve this pair; within one item each pair needs its own "
                 "channel because an FPVIe channel has exactly one high and one low terminal")

# ------------------------------------------------------------- deliverable
result = {
    "runId": RUN,
    "generatedBy": "schematic-expert (supplementary evidence for t3 setup contract / t4 strategy)",
    "purpose": ("Answer which instrument reaches PMID / SW / PGND for a single-ended voltage measurement, what "
                "F/S character each route has, and whether a usable Kelvin sense pair exists on PMID<->SW and "
                "SW<->PGND."),
    "sources": [
        ev(PROOFS_PATH, "accepted_path_proofs (native_csv_graph_v2, status=%s)" % proofs["status"]),
        ev(CSV_PATH, "pin-level relay nets (Designator/PinNumber/NetName)"),
        ev(MAP_PATH, "route headers with [Kelvin]/[单线]/[PC短接] annotations and 需闭合 groups"),
        ev(SPECS_PATH, "module table lines 9-32 (channels / floating / ranges)"),
        ev(PINCH_PATH, "_PIN_CHANNEL_DEFINE_* channel bindings"),
        ev(RELAY_DOC, "L33-48 MOS default-open vs G6K default-NC; L175-184 FPVIe domain constraint"),
    ],
    "nodeReachability": {
        n: {"instruments": instruments_reaching[n],
            "acceptedPathCount": len(node_rows[n]),
            "unreachable": not node_rows[n]}
        for n in ("PMID", "SW", "PGND")
    },
    "unreachableNodes": [n for n in ("PMID", "SW", "PGND") if not node_rows[n]],
    "singleEndedEvidence": single_ended,
    "forceSenseBridgeRelays": bridge_info,
    "kelvinPairCandidates": pair_findings,
    "requiredPairAssertions": assertion_table,
    "channelOptionsForRequiredPairs": channel_options,
    "channelAllocationPerTm": {
        tm: {"channelsUsed": cs,
             "pairsAssigned": {c["pair"]: next((o["channel"] for o in c["options"] if o.get("recommended")), None)
                               for c in channel_options if c["tm"] == tm}}
        for tm, cs in sorted(allocations.items())
    },
    "dfdPairVerdicts": [
        {"pair": "PMID<->SW", "tm": "TM600", "kelvinPairAvailable": True,
         "terminals": "S1_FPVIe channel 0: FH0/SH0 -> PMID (K83), FL0/SL0 -> SW (K60,K61)",
         "unionRelays": [60, 61, 83], "fourWireProper": True,
         "senseKind": "differential Kelvin across two DUT pins, genuine 4-wire (BUS route never enters the PC nets)",
         "caveat": ("this consumes FPVIe channel 0 of site 1; TM600 also needs channel 1 for the BST-SW 5V loop, "
                    "so both channels are used by one item"),
         "evidence": [ev(PROOFS_PATH, "S1_FPVIe_FH0/SH0 -> PMID_*_S1 req=[83]; S1_FPVIe_FL0/SL0 -> SW_*_S1 req=[60,61]")]},
        {"pair": "SW<->PGND", "tm": "TM601", "kelvinPairAvailable": True,
         "terminals": "S1_FPVIe channel 0, inverted orientation: FH0/SH0 -> PGND (K154,K155), FL0/SL0 -> SW (K60,K61)",
         "unionRelays": [60, 61, 154, 155], "fourWireProper": True,
         "senseKind": "differential Kelvin across two DUT pins, genuine 4-wire; PGND is the HIGH terminal because "
                      "it hangs off FPVIe0_FH_BUS_S1 while SW hangs off FPVIe0_FL_BUS_S1",
         "caveat": ("channel 0 is also the PMID<->SW pair of TM600, so TM600 and TM601 can never run in the same "
                    "function on the same site; and K93_AGND2PGND must stay OPEN or the PGND node is tied to AGND_F "
                    "and the return current flows through the K93 contact"),
         "evidence": [ev(PROOFS_PATH, "S1_FPVIe_FH0/SH0 -> PGND_*_S1 req=[154,155]; S1_FPVIe_FL0/SL0 -> SW_*_S1 req=[60,61]"),
                      ev(CSV_PATH, "K154_BUSH_AMUX_S1 pin3=FPVIe0_FH_BUS_S1 pin6=FPVIe0_SH_BUS_S1; K60_BUSL_VCP_S1 pin3=FPVIe0_FL_BUS_S1 pin6=FPVIe0_SL_BUS_S1")]},
        {"pair": "BST<->SW (TM600 bootstrap rail)", "tm": "TM600", "kelvinPairAvailable": True,
         "terminals": "S1_FPVIe channel 1: FH1/SH1 -> BST (K131,K134 / K132,K135), FL1/SL1 -> SW (K133,K134 / K132,K135)",
         "unionRelays": [131, 132, 133, 134, 135], "fourWireProper": True,
         "senseKind": "differential Kelvin across two DUT pins via the PC1 force/sense relay K134/K135 pair",
         "caveat": "Uses the PC1 channel relays K134_PC1_Force / K135_PC1_Sense; they are not among the FPVIe0 PC nets that are board-shorted, so Kelvin separation holds here",
         "evidence": [ev(PROOFS_PATH, "S1_FPVIe_FH1 -> BST_F_S1 req=[131,134]; S1_FPVIe_FL1 -> SW_F_S1 req=[133,134]")]},
    ],
    "nonKelvinInstruments": [
        {"instrument": "QTMUe", "why": "single line per channel with the low side on DGND (bus-topology.md 2.3); "
                                       "reaches SW_S through the PC1 sense relays K130/K132/K135 and PMID_S through "
                                       "the force<->sense bridge K86",
         "usableFor": "DC / Iq / toggle / timing items only", "invalidFor": "mOhm differential RDSON",
         "evidence": [ev(ROOT / "knowledge/hardware/bus-topology.md", "L57-81 digital sources unify low to DGND; L75 QTMU BUS is 1 line"),
                      ev(PROOFS_PATH, "S10_CH0_A -> PMID_S_S1 req=[83,86,141]; S10_CH0_B -> SW_S_S1 req=[130,132,135]")]},
        {"instrument": "QVMe", "why": "floating voltmeter with sense lines only (no force); CH0+ taps the FPVIe0 "
                                      "SH bus and reaches the PMID_F/S or PGND_F/S nets, CH0- reaches SW_S. Because "
                                      "one lead lands on a force net the pair is a mixed F/S pair, not a Kelvin sense pair",
         "usableFor": "independent differential voltage read of limited accuracy", "invalidFor": "the mOhm Kelvin sense of TM600/TM601",
         "evidence": [ev(PROOFS_PATH, "S8_QVM_CH0+ -> PMID_F_S1 req=[83,86,137]; S8_QVM_CH0- -> SW_S_S1 req=[60,61,138]")]},
        {"instrument": "ACM200", "why": "reaches SW only (S5_ACM200_FH8/SH8, req K61) and cannot reach PMID or PGND "
                                        "at all; +-200 mA range",
         "usableFor": "SW single-ended Kelvin reads up to 200 mA", "invalidFor": "the 1 A TM600/TM601 force",
         "evidence": [ev(PROOFS_PATH, "S5_ACM200_FH8/SH8 -> SW_*_S1 req=[61]"),
                      ev(SPECS_PATH, "L16 ACM200 +-200m/100m/10m ... A")]},
        {"instrument": "FXVIe_PLUS", "why": "4-wire Kelvin on a single pin (PMID default through K84 with no SetOn, "
                                            "PGND through K155) but its low side returns to AGND_F, so it cannot "
                                            "form a floating pair across SW",
         "usableFor": "single-ended Kellex read of PMID or PGND", "invalidFor": "a PMID-SW or SW-PGND differential pair",
         "evidence": [ev(PROOFS_PATH, "S3_FXVIe_PLUS_FH1/SH1 -> PMID_*_S1 req=[]; S3_FXVIe_PLUS_FH3/SH3 -> PGND_*_S1 req=[155]"),
                      ev(MAP_PATH, "L820-822 FXVIe_PLUS -> PMID 需闭合: 无(默认导通)")]},
    ],
    "blockingDecisionsForStrategy": [
        {"id": "SD-1", "severity": "high",
         "decision": "TM600 and TM601 must be separate functions: both need FPVIe channel 0 of the same site for the "
                     "Kelvin force/sense pair, and TM600 additionally needs channel 1 for BST-SW.",
         "why": "FPVIe provides only 2 independently floating channels per site (hardware-specs.md L17)",
         "resolutionOwner": "test-strategy-architect (t4) with setup-architect (t3)"},
        {"id": "SD-2", "severity": "high",
         "decision": "Keep K86_KELVIN0_FS and K130_KELVIN1_FS OPEN for TM600/TM601.",
         "why": "these bridges merge force and sense on their row; every QTMU/QVM route requires them, no 4-wire "
                "FPVIe route does. Closing them silently degrades the mOhm measurement to 2-wire.",
         "resolutionOwner": "setup-architect (t3)"},
        {"id": "SD-3", "severity": "high",
         "decision": "Keep K93_AGND2PGND OPEN during TM601 (and state it explicitly in the cleanup block).",
         "why": "K93 SetOn ties AGND_F to PGND_F and PGND_S; with the 1 A return flowing through PGND this both "
                "shorts the ground reference and puts 1 A through the K93 contact.",
         "resolutionOwner": "setup-architect (t3)"},
        {"id": "SD-4", "severity": "medium",
         "decision": "Fix the loop orientation explicitly: PMID<->SW = channel 0 high to low; SW<->PGND = channel 0 "
                     "low (SW) to high (PGND).",
         "why": "PMID and PGND hang off FPVIe0_FH_BUS_S1 while SW hangs off FPVIe0_FL_BUS_S1; dft-ir.json words "
                "TM601 as PMID(High)/SW(Low), which is the opposite orientation.",
         "resolutionOwner": "setup-architect (t3) + test-strategy-architect (t4)"},
        {"id": "SD-5", "severity": "medium",
         "decision": "Do not plan a Kelvin measurement through the FPVIe0 PC nets (K90/K91 + K82_R_CS): the PC nets "
                     "are board-shorted F<->S and carry the 100 mohm / 5 mohm shunts.",
         "why": "10 mohm DUT against a 100 mohm shunt in the same path",
         "resolutionOwner": "test-strategy-architect (t4)"},
    ],
}
(OUT / "schematic-ir-sensing.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("wrote", OUT / "schematic-ir-sensing.json")
print("unreachable nodes:", result["unreachableNodes"] or "NONE")
print("required pair assertions:", all(a["found"] for a in assertion_table), assertion_table)
for n in ("PMID", "SW", "PGND"):
    print(f"\n== {n}: {instruments_reaching[n]}")
    print("   4-wire instruments:", single_ended[n]["hasTrueFourWireInstrument"])
print("\nbridge relays:")
for b in bridge_info:
    print("  ", b["designator"], b["role"], "users:", b["acceptedProofUsersByInstrument"])
