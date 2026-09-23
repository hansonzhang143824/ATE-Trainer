#!/usr/bin/env python3
"""Build team/artifacts/acceptance-20260916-dali10/schematic-ir.json.

Inputs (all hashed into the IR `sources` array):
  project/DALI/Dali-SCH.csv                     (authoritative schematic CSV, Altium v3)
  <validation dir>/path_proofs.json.txt         (fresh native_csv_graph_v2 PathProof run)
  <validation dir>/PATHPROOF-VALIDATION.txt
  <validation dir>/validation_manifest.json.txt
  <validation dir>/scope-paths.json             (per-scope-pin accepted proofs)
  <validation dir>/resource-conflicts.json      (relay reuse / shared resources)
  project/DALI/SCH-Connect-Map.txt              (six-gate connect map, regenerated identical)
  project/DALI/Component-Statistic.txt
  project/DALI/phase2_singlepoint_output.txt
  D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h
  D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h
  knowledge/... (rule text, cross-referenced only)
  project/DALI/input/DFT.csv + _archive/_dump_OVERVIEW.txt (DFT cross-reference only)

The IR records schematic facts only. DFT intent stays with the dft-expert artefact; where the
two touch, the schematic side is stated as a constraint and the DFT side is recorded as an
open question rather than resolved here.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(".").resolve()
RUN_ID = "acceptance-20260916-dali10"
OUT = ROOT / "team" / "artifacts" / RUN_ID
VAL = OUT / "schematic-validation"

CSV_PATH = ROOT / "project" / "DALI" / "Dali-SCH.csv"

SCORE = {
    "TM000": {"group": "foundation", "family": ["normal", "low-current"]},
    "TM001": {"group": "foundation", "family": ["normal", "low-current", "grouped-family"]},
    "TM102": {"group": "foundation", "family": ["normal", "voltage"]},
    "TM103": {"group": "foundation", "family": ["normal", "current", "atest"]},
    "TM108": {"group": "toggle-trim", "family": ["toggle"]},
    "TM109": {"group": "toggle-trim", "family": ["toggle"]},
    "TM135": {"group": "toggle-trim", "family": ["trim", "grouped"]},
    "TM600": {"group": "power-special", "family": ["normal", "high-current", "floating", "differential"]},
    "TM601": {"group": "power-special", "family": ["normal", "high-current", "differential"]},
    "TM1205": {"group": "power-special", "family": ["toggle", "bst-sw"]},
}

# DUT pins each TM is electrically forced/sensed on, derived from the DFT rail names it
# pokes (vset/iset objects) resolved against the netlist DUT-pin list.
TM_PINS = {
    "TM000": ["VBAT", "VCC", "VDRV"],
    "TM001": ["VBAT", "VCC", "VDRV"],
    "TM102": ["AMUX", "AGND", "VBAT"],
    "TM103": ["AMUX", "AGND", "VBAT"],
    "TM108": ["VAC1", "KLV1", "KLV2", "AGND", "VBAT"],
    "TM109": ["VAC2", "KLV1", "KLV2", "AGND", "VBAT"],
    "TM135": ["VDM", "SDA", "SCL", "VCC"],
    "TM600": ["PMID", "SW", "BST", "VBAT", "VDRV", "V1P5", "PGND", "AGND"],
    "TM601": ["SW", "PGND", "PMID", "VBUS", "VBAT", "VDRV", "V1P5", "AGND"],
    "TM1205": ["BST", "SW", "PMID", "VBUS"],
}
SCOPE_PINS = sorted({p for pins in TM_PINS.values() for p in pins})


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ev(path: str, locator: str) -> dict:
    p = Path(path)
    return {"path": path.replace("\\", "/"), "locator": locator, "sha256": sha(p)}


def dft_ir_anchor() -> dict:
    """Content anchor for the cross-owned DFT artefact.

    dft-ir.json is owned by dft-expert and is regenerated during the run, so a byte pin goes stale on
    every republish. Instead of re-pinning blindly, extract the specific claims this IR relies on and
    digest THOSE: if dft-expert changes the substance, the digest changes and the citation must be
    re-verified; if only unrelated fields move, the digest holds and the byte pin being stale is harmless.
    """
    path = ROOT / "team/artifacts/acceptance-20260916-dali10/dft-ir.json"
    claims: dict = {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        items = {i.get("tm"): i for i in doc.get("items", [])}
        for tm in ("TM600", "TM601"):
            chans = items.get(tm, {}).get("channels", [])
            claims[f"{tm}.forcePins"] = chans[0].get("pins") if chans else None
            claims[f"{tm}.iset"] = [
                {"pin": s.get("pin"), "value": s.get("value"), "unit": s.get("unit")}
                for s in items.get(tm, {}).get("stimuli", []) if s.get("kind") == "iset"
            ]
        claims["conflictIds"] = sorted(c.get("id") for c in doc.get("conflicts", []) if c.get("id"))
        claims["ruledPairMarker"] = "sw2pgnd" in path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - anchor must never break the build
        claims["error"] = str(exc)
    canonical = json.dumps(claims, ensure_ascii=False, sort_keys=True)
    return {
        "path": "team/artifacts/acceptance-20260916-dali10/dft-ir.json",
        "owner": "dft-expert",
        "sha256": DFT_IR_VERIFIED_REVISION_SHA256,
        "sha256Role": "revision whose claims this IR verified; expected to drift, see claimDigest",
        "claimDigest": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "claims": claims,
        "expectations": DFT_IR_EXPECT_EXACT,
        "expectationConflicts": DFT_IR_EXPECT_CONFLICTS,
        "expectationIset": DFT_IR_EXPECT_ISET,
        "expectationsAssertedBy": "selfcheck_schematic_ir.py (hard failure on mismatch)",
        "mutableByDesign": True,
    }


# ---------------------------------------------------------------- CSV primitives
with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as _fh:
    _TABLE = list(csv.reader(_fh))

H = _TABLE[0]
ROWS = _TABLE[1:]
I_NET, I_MN, I_PIN, I_DES, I_VAL, I_KIND = (H.index(x) for x in
    ("NetName", "MemberName", "PinNumber", "Designator", "ComponentValue", "ComponentKind"))

NET_MEMBERS: dict[str, list[str]] = {}
COMP_PINS: dict[str, list[dict]] = {}
COMP_META: dict[str, dict] = {}
for r in ROWS:
    if len(r) <= I_VAL:
        continue
    net, mn, des, pin, val, kind = r[I_NET], r[I_MN], r[I_DES], r[I_PIN], r[I_VAL], r[I_KIND]
    if net:
        NET_MEMBERS.setdefault(net, [])
        if mn and mn not in NET_MEMBERS[net]:
            NET_MEMBERS[net].append(mn)
    if des:
        COMP_PINS.setdefault(des, [])
        rec = {"pin": pin, "net": net, "member": mn}
        if rec not in COMP_PINS[des]:
            COMP_PINS[des].append(rec)
        COMP_META.setdefault(des, {"value": val, "kind": kind})

# ---------------------------------------------------------------- evidence-backed loads
proofs_doc = json.loads((VAL / "path_proofs.json.txt").read_text(encoding="utf-8"))
scope_paths = json.loads((VAL / "scope-paths.json").read_text(encoding="utf-8"))
conflicts = json.loads((VAL / "resource-conflicts.json").read_text(encoding="utf-8"))
manifest = json.loads((VAL / "validation_manifest.json.txt").read_text(encoding="utf-8-sig"))
pp_validation = (VAL / "PATHPROOF-VALIDATION.txt").read_text(encoding="utf-8").strip()

# ---------------------------------------------------------------- sources
SRC = [
    ("project/DALI/Dali-SCH.csv",
     f"inputs.csv_schematic; Altium unified circuit connectivity CSV v3; rows={manifest['input']['rows']}; "
     f"graph ports={manifest['graph']['ports']} dut_ports={manifest['graph']['dut_ports']} "
     f"relays={manifest['graph']['relays']} physical_nets={manifest['graph']['physical_nets']}"),
    ("team/artifacts/acceptance-20260916-dali10/schematic-validation/path_proofs.json.txt",
     f"native_csv_graph_v2 PathProof; status={proofs_doc['status']} accepted={proofs_doc['counts']['accepted_path_proofs']} "
     f"rejected={proofs_doc['counts']['rejected_paths']} kelvin_pairs={proofs_doc['counts']['kelvin_pairs']}; "
     f"contracts={','.join(k for k, v in proofs_doc['contracts'].items() if v)}"),
    ("team/artifacts/acceptance-20260916-dali10/schematic-validation/PATHPROOF-VALIDATION.txt",
     pp_validation.splitlines()[1] if len(pp_validation.splitlines()) > 1 else "status=PASS"),
    ("team/artifacts/acceptance-20260916-dali10/schematic-validation/validation_manifest.json.txt",
     f"six-gate parser manifest; parser_gate_status={manifest['parser_gate_status']}; gate_exit_code={manifest['gate_exit_code']}; "
     f"input.sha256={manifest['input']['sha256']}"),
    ("team/artifacts/acceptance-20260916-dali10/schematic-validation/scope-paths.json",
     "accepted PathProofs filtered to the ten-TM scope pins (per-pin relay chains + required_on)"),
    ("team/artifacts/acceptance-20260916-dali10/schematic-validation/resource-conflicts.json",
     "relay reuse across scope pins, per-TM relay sets, stabiliser relays on scope rails, net-short groups, P2P paths"),
    ("project/DALI/SCH-Connect-Map.txt",
     "six-gate connect map (966 lines): columns 1-10 source->PIN routes, col11 classification, DUT PIN->signal net appendix; "
     "regenerated byte-identical to the committed copy in this run"),
    ("project/DALI/Component-Statistic.txt",
     "component/passive inventory behind the connect map (272 components, gate PASS)"),
    ("project/DALI/phase2_singlepoint_output.txt",
     "single-point CBIT define baseline (161 unique CBIT values) used to resolve K<n> relay names"),
    ("D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h",
     "tester channel binding: _PIN_CHANNEL_DEFINE_*/_GROUP_CHANNEL_DEFINE_*/_PIN_SITE_BIND_DEFINE_* macros"),
    ("D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h",
     "published relay #defines + RELAY_ROLE section (K_<Pin>_Cap / _P2P / _PU / _PD / _ST)"),
    ("knowledge/hardware/bus-topology.md",
     "§2.2 FPVI floating connection, §4 BUS dual use, §5 BUS decision/thermal-switch, §7 Cap2 rule, §8 HS/LS merge ban, §9 E006 PMID-FET-SW"),
    ("knowledge/hardware/relays.md",
     "§MOS default-open vs G6K default-NC, §Cap/PU/P2P functional closure rules, §FPVIe domain constraint, §S1S2 site sharing"),
    ("knowledge/sources/hardware-specs.md",
     "line 9-32 module table (channels/ranges/floating); line 17 FPVIe +-100V/+-10A 2ch independent floating"),
    ("knowledge/sources/fpvie.md",
     "line 6 FPVIe high-current four-quadrant source meter, 2 channels/board, +-100V/+-10A"),
    ("scripts/schematic_parse/PATH_CONTRACT.md",
     "4 hardcoded path contracts enforced by the BFS PathProof engine"),
    ("scripts/schematic_parse/SKILL.md",
     "sole production pipeline; K25 (VCC<->ACDRV common rail) deliberately excluded from short definitions 2026-08-26"),
    ("project/DALI/input/DFT.csv",
     "DFT cross-reference only (dft-expert owns DFT intent): TM600 row L89, TM601 row L97; "
     "TM001/TM102/TM135/TM1205 are absent from this file"),
    ("project/DALI/_archive/_dump_OVERVIEW.txt",
     "DFT cross-reference only: TM600 L981 HS_RDSON 11 mohm, TM601 L994 LS_RDSON 7.5 mohm (older revision, values differ from DFT.csv)"),
]

# ---------------------------------------------------------------- tester channels
CHAN_MAP: dict[str, list[str]] = {}
for line in (ROOT / "D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h".replace("D:/", "D:/")).read_text(
        encoding="utf-8", errors="replace").splitlines():
    m = re.match(r"#define\s+(_PIN_CHANNEL_DEFINE_|_GROUP_CHANNEL_DEFINE_|_PIN_SITE_BIND_DEFINE_)(\S+?)\s+\"([^\"]*)\"", line)
    if m:
        CHAN_MAP[m.group(2)] = m.group(3).split(",")

CHANNEL_FACTS = [
    ("PID", "PMID", "FXVIe_PLUS", "PMID_HG2_FXVI", sorted(CHAN_MAP.get("PMID_HG2_FXVI_", [])),
     "PMID shares one FXVIe_PLUS channel with HG2"),
    ("PID", "SW1/SW2", "FXVIe_PLUS", "SW1_SW2_FXVI", sorted(CHAN_MAP.get("SW1_SW2_FXVI_", [])),
     "SW1/SW2 share one FXVIe_PLUS channel; the SW pin itself is NOT on this channel"),
    ("PID", "VCC/VMCU", "FXVIe_PLUS", "VCC_VMCU_FXVI", sorted(CHAN_MAP.get("VCC_VMCU_FXVI_", [])),
     "VCC and VMCU share one FXVIe_PLUS channel"),
    ("PID", "AMUX/PGND", "FXVIe_PLUS", "AMUX_PGND_FXVI", sorted(CHAN_MAP.get("AMUX_PGND_FXVI_", [])),
     "AMUX and PGND share one FXVIe_PLUS channel -> TM102/TM103 (AMUX) and TM601 (PGND) cannot share a site concurrently"),
    ("PID", "VBAT/PD3", "FXVIe_PLUS", "VBAT_PD3_FXVI", sorted(CHAN_MAP.get("VBAT_PD3_FXVI_", [])),
     "VBAT and PD3 share one FXVIe_PLUS channel"),
    ("PID", "V1P5/U34_PS", "FXVIe_PLUS", "V1P5_U34PS_FXVI", sorted(CHAN_MAP.get("V1P5_U34PS_FXVI_", [])),
     "V1P5 (and VDRV via TP_VDRV) share one FXVIe_PLUS channel"),
    ("SITE", "FPVIe site1", "FPVIe", "MD_FPVIE_SITE1", sorted(CHAN_MAP.get("MD_FPVIE_SITE1_", [])),
     "S1_0 and S1_1 = the two independently floating FPVIe channels of site 1 (FPVIe0/FPVIe1)"),
    ("SITE", "QTMU site1", "QTMUe", "MD_QTMUE_NOSITE", sorted(CHAN_MAP.get("MD_QTMUE_NOSITE", [])),
     "site-agnostic QTMUe group; only S10_CH0_A/S10_CH0_B exist on the netlist (1 line, low=DGND)"),
]

# ---------------------------------------------------------------- nets
NET_SPEC = {
    "NetCap1_PMID_S1_1": "PMID force node (FPVIe0 FH side); Cap1_PMID 10nF + K85-cap + R_PMID_KLV 10K",
    "NetK84_HG2_S1_7": "PMID sense node behind K84 (dut_pin PMID_S_S1)",
    "NetK57_CAP_BST_SW_S1S2_3": "BST side of the 220nF bootstrap cap (also K57 selector pole)",
    "NetCap_SW_BST_S1_1": "BST terminal of Cap_SW_BST_S1 (D_BST_SW cathode side)",
    "NetCap_SW_BST_S1_2": "SW terminal of Cap_SW_BST_S1 (D_BST_SW anode side); dut_pin SW_F_S1",
    "NetK61_SW_S1_4": "SW node behind K61 (dut_pin SW_S_S1)",
    "NetK76_ACM_BST_S1_4": "BST node on the ACM/BST side (R_BST_S1 connection)",
    "NetK60_BUSL_VCP_S1_4": "BUSL_VCP low bus node (K60 pole A/B throw) shared by VCP and SW",
    "NetK60_BUSL_VCP_S1_5": "BUSL_VCP low bus node (K60/K61 tie) shared by VCP and SW",
    "NetK93_AGND2PGND_S1_4": "PGND force node tied to AGND through K93_AGND2PGND",
    "NetK93_AGND2PGND_S1_5": "PGND sense node tied to AGND through K93_AGND2PGND",
    "NetCap1_VBAT_S1_1": "VBAT force node; Cap1_VBAT 10nF",
    "NetK8_PD3_S1_2": "VBAT sense node (dut_pin VBAT_S_S1)",
    "NetCap1_VCC_S1_1": "VCC force node; Cap1_VCC 10nF",
    "NetCap1_VBUS_S1_1": "VBUS force node; Cap1_VBUS 10nF",
    "NetK4_DRVH1_S1_2": "VBUS sense node behind K4 (dut_pin VBUS_S_S1)",
    "NetCap1_V1P5_S1_1": "V1P5/VDRV force node; Cap1_V1P5 10nF",
    "NetK125_U34_PS_S1_7": "VDRV/V1P5 sense node behind K125_U34_PS",
    "FPVIe0_FH_BUS_S1": "FPVIe0 high-force BUS wire - ONE shared wire: every closed high-side BUS relay on it (PMID K83 pin3, PGND K154 pin3, BST K46, VBAT K7, ...) ties its pin to it AND to each other",
    "FPVIe0_SH_BUS_S1": "FPVIe0 high-sense BUS wire (shared, same caveat)",
    "FPVIe0_FL_BUS_S1": "FPVIe0 low-force BUS wire (shared; SW K60 pin3, VBUS K3, VCP K60 ...)",
    "FPVIe0_SL_BUS_S1": "FPVIe0 low-sense BUS wire (shared)",
    "FPVIe1_FH_BUS_S1": "FPVIe1 high-force BUS wire (TM600 BST loop); K141 also bridges FPVIe0_FH_BUS <-> FPVIe1_FH_BUS",
    "FPVIe1_SH_BUS_S1": "FPVIe1 high-sense BUS wire; K134 pin7 sits on it",
    "FPVIe1_FL_BUS_S1": "FPVIe1 low-force BUS wire (TM600 SW loop); K142 also bridges FPVIe0_FL_BUS <-> FPVIe1_FL_BUS",
    "FPVIe1_SL_BUS_S1": "FPVIe1 low-sense BUS wire; K132 pin7 sits on it",
    "FPVIe0_FH_PC_S1": "FPVIe0 PC-channel high FORCE net (K90 pin4 / K91 pin4 / R1_CS / C2_CS). Alias-shorted to the shadow net FPVIe0_SH_PC_S1 (csvrow 125)",
    "FPVIe0_FL_PC_S1": "FPVIe0 PC-channel low force net (K90 pin5 / K91 pin5 / R1_CS / R2_CS). Alias-shorted to the shadow net FPVIe0_SL_PC_S1 (csvrow 149)",
    "NetK87_KELVIN0_S1S2_4": "FPVIe0 high-side Kelvin row behind K87 (feeds K90 pole A)",
    "NetK89_KELVIN0_S1S2_4": "FPVIe0 low-side Kelvin row behind K89 (feeds K90 pole B)",
    "NetK131_KELVIN1_S1S2_4": "FPVIe1 high-side Kelvin row behind K131 (feeds K134 pole A)",
    "NetK133_KELVIN1_S1S2_4": "FPVIe1 low-side Kelvin row behind K133 (feeds K134 pole B)",
    "NetK132_KELVIN1_S1_4": "FPVIe1 high-side Kelvin sense row (feeds K135 pole A)",
    "NetK132_KELVIN1_S1_5": "FPVIe1 low-side Kelvin sense row (feeds K135 pole B)",
    "NetK66_TMU_nQON_S1_2": "QTMU BUS-A line - reaches FPVIe0_FH_BUS and FPVIe1_FH_BUS through K141",
    "NetK142_QTMU_BUSB_S1S2_3": "QTMU BUS-B line - reaches FPVIe0_FL_BUS and FPVIe1_FL_BUS through K142",
    "NetK57_CAP_BST_SW_S1S2_3": "BST terminal of the bootstrap path (K57 pole pin3, R_BST_S1 pin1, K134 pin4)",
    "NetK76_ACM_BST_S1_4": "BST node on the ACM side (R_BST_S1 pin2, K135 pin4)",
    "NetCap_SW_BST_S1_1": "BST terminal of Cap_SW_BST_S1 (D_BST_SW cathode side); K57 pin2",
    "NetCap_SW_BST_S1_2": "SW terminal of Cap_SW_BST_S1 (D_BST_SW anode side); K61 pin5, K134 pin5, R_SW_S1 pin1",
    "NetK61_SW_S1_4": "SW sense node behind K61 (dut_pin SW_S_S1, K135 pin5)",
    "VCP_FORCE_S1": "VCP pin node - default destination of the K60/BUSL_VCP low bus through K61 pin7",
    "AGND": "instrument analogue ground",
    "AGND_F_S1": "site-1 force analogue ground (all Cap2 / 1kohm discharge resistors return here)",
    "DGND": "digital source return (QTMU/DCM low side)",
    "JGND": "CBIT / machine supply return (tied to DGND)",
}

# nets that exist only as CSV short-group aliases (no NET_MEMBER rows of their own)
ALIAS_ONLY_NETS = {
    "FPVIe0_SH_PC_S1": "csvrow 125 DIRECT_NET_ALIAS / DIRECT_WIRE / CONFIRMED: FPVIe0_FH_PC_S1 | FPVIe0_SH_PC_S1",
    "FPVIe0_SL_PC_S1": "csvrow 149 DIRECT_NET_ALIAS / DIRECT_WIRE / CONFIRMED: FPVIe0_FL_PC_S1 | FPVIe0_SL_PC_S1",
}

# relays that sit directly on an FPVIe BUS wire: closing two of them on the same side
# shorts the two DUT pins together through that wire.
BUS_WIRE_RELAYS = {
    "FPVIe0_FH_BUS_S1": [(83, 3), (154, 3)],
    "FPVIe0_SH_BUS_S1": [(83, 6), (154, 6)],
    "FPVIe0_FL_BUS_S1": [(60, 3), (142, 4)],
    "FPVIe0_SL_BUS_S1": [(60, 6)],
    "FPVIe1_FH_BUS_S1": [(131, 2), (141, 2)],
    "FPVIe1_SH_BUS_S1": [(132, 2), (134, 7)],
    "FPVIe1_FL_BUS_S1": [(133, 2), (142, 2)],
    "FPVIe1_SL_BUS_S1": [(132, 7)],
}

# ---------------------------------------------------------------- passive / relay extraction
PASSIVE_LIST = [
    "Cap1_PMID_S1", "Cap2_PMID_S1", "Cap_SW_BST_S1", "D_BST_SW_S1",
    "Cap1_VBAT_S1", "Cap2_VBAT_S1", "Cap1_VCC_S1", "Cap2_VCC_S1",
    "Cap1_VBUS_S1", "Cap2_VBUS_S1", "Cap1_V1P5_S1", "Cap2_V1P5_S1",
    "Cap2_VAC_S1", "C2_CS_S1", "C4_SVLP_S1(NC)",
    "R_PMID_S1", "R_PMID_KLV_S1", "R_BST_S1", "R_SW_S1", "R_SW1_KLV_S1",
    "R_VBAT_S1", "R_VCC_S1", "R_VBUS_S1", "R_V1P5_S1", "R_VAC_S1",
    "R1_CS_S1", "R2_CS_S1", "R_PGND_S1", "R_AMUX_S1",
]
RELAY_LIST = [0, 3, 4, 5, 7, 8, 13, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30, 31, 32,
              35, 36, 37, 41, 44, 45, 46, 47, 48, 57, 60, 61, 68, 70, 73, 76, 82, 83, 84,
              85, 86, 87, 88, 89, 90, 91, 93, 109, 110, 125, 126, 130, 131, 132, 133, 134,
              135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 149, 151, 154, 155]

S1S2_SHARED = sorted({int(m.group(1)) for d in COMP_PINS for m in [re.match(r"K(\d+)_.*_S1S2", d)] if m})
S1S2_SHARED = sorted(set(S1S2_SHARED))

def find_designator(prefix: str) -> str | None:
    for d in COMP_PINS:
        if d == prefix or d.startswith(prefix):
            return d
    return None


components = []
for des in PASSIVE_LIST:
    real = find_designator(des)
    if not real:
        continue
    meta = COMP_META.get(real, {})
    components.append({
        "designator": real,
        "value": meta.get("value", ""),
        "kind": meta.get("kind", ""),
        "pins": COMP_PINS[real],
        "evidence": [{"path": "project/DALI/Dali-SCH.csv", "locator": f"Designator={real}", "sha256": sha(CSV_PATH)}],
    })

relays = []
for n in RELAY_LIST:
    names = sorted({d for d in COMP_PINS if re.match(rf"K{n}_", d)})
    if not names:
        continue
    relay = {"number": n, "instances": names, "siteShared": n in S1S2_SHARED,
             "value": sorted({COMP_META[d].get("value", "") for d in names if d in COMP_META}),
             "pins": {d: COMP_PINS[d] for d in names}}
    relays.append(relay)

# ---------------------------------------------------------------- DUT pins
dut_pins = []
for pin in SCOPE_PINS:
    paths = scope_paths["paths"].get(pin, [])
    src_types = sorted({p["source_type"] for p in paths})
    dut_pins.append({
        "name": pin,
        "netlistPorts": sorted({p["dut_pin"] for p in paths}),
        "kelvin": any(p["dut_pin"].endswith(("_F_S1", "_S_S1")) for p in paths),
        "acceptedPathCount": len(paths),
        "reachableSourceTypes": src_types,
        "highCurrentCapableSourceTypes": [t for t in src_types if t in ("FPVIe", "FXVIe_PLUS", "FOVIe")],
        "sourcePortsForKelvinBusRouting": sorted({p["source_port"] for p in paths if p["source_type"] == "FPVIe"}),
        "netShortGroups": conflicts["netShortGroups"] if pin == "SW" else [],
        "evidence": [{"path": "team/artifacts/acceptance-20260916-dali10/schematic-validation/scope-paths.json",
                      "locator": f"paths.{pin}", "sha256": sha(VAL / "scope-paths.json")}],
    })

# ---------------------------------------------------------------- paths
paths = []
for pin in SCOPE_PINS:
    for p in scope_paths["paths"].get(pin, []):
        resources = [str(r) for r in p["required_on"]]
        pid = f"{p['source_port']}->{p['dut_pin']}"
        paths.append({
            "id": pid,
            "from": p["source_port"],
            "to": p["dut_pin"],
            "net": p["dut_net"],
            "resources": resources,
            "confidence": "direct",
            "sourceType": p["source_type"],
            "sourceRole": p["source_role"],
            "sourceDomain": p["source_domain"],
            "dutPin": pin,
            "relayChain": [{"relay": r, "state": s} for r, s in zip(p["relays"], p["states"])],
            "defaultClosedRelays": [r for r, s in zip(p["relays"], p["states"]) if s == "NC"],
            "requiredOnRelays": p["required_on"],
            "terminalStop": p["terminal_stop"],
            "kelvinRoleMatch": p["validation"]["role_match"],
            "cbitComplete": p["validation"]["cbit_complete"],
            "evidence": [{"path": "team/artifacts/acceptance-20260916-dali10/schematic-validation/path_proofs.json.txt",
                          "locator": f"accepted_path_proofs[{pid}]", "sha256": sha(VAL / "path_proofs.json.txt")}],
        })

# derived candidate loop paths (not raw BFS proofs) - assembled from the proofs above
derived_loops = [
    {
        "id": "LOOP_TM600_PMID2SW_1A",
        "from": "PMID", "to": "SW", "resources": ["83", "87", "88", "89", "60", "61"],
        "confidence": "derived",
        "net": "NetCap1_PMID_S1_1 -> NetK61_SW_S1_4",
        "sourceChannel": "S1_FPVIe channel 0 (FH0/SH0 -> PMID, FL0/SL0 -> SW)",
        "assertion": "FPVIe0 form the PMID<->SW floating 1 A loop requested by DFT iset[pmid2sw,1,1e-3,0]",
        "evidence": [{"path": "project/DALI/input/DFT.csv", "locator": "TM600 row: iset[pmid2sw,1,1e-3,0]", "sha256": sha(ROOT / "project/DALI/input/DFT.csv")},
                     {"path": "project/DALI/SCH-Connect-Map.txt", "locator": "列2 CH0 High -> PMID (K83), CH0 Low -> SW (K60,K61)", "sha256": sha(ROOT / "project/DALI/SCH-Connect-Map.txt")}],
    },
    {
        "id": "LOOP_TM600_BST2SW_5V",
        "from": "BST", "to": "SW", "resources": ["131", "132", "133", "134", "135"],
        "confidence": "derived",
        "net": "NetCap_SW_BST_S1_1 <-> NetCap_SW_BST_S1_2",
        "sourceChannel": "S1_FPVIe channel 1 (FH1/SH1 -> BST_F/S, FL1/SL1 -> SW_F/S)",
        "assertion": "FPVIe1 form the floating BST-SW 5 V loop requested by DFT vset[bst2sw,5,1e-3,0]; the loop closes across Cap_SW_BST_S1 (220nF) + D_BST_SW_S1",
        "evidence": [{"path": "project/DALI/input/DFT.csv", "locator": "TM600 row: vset[bst2sw,5,1e-3,0]", "sha256": sha(ROOT / "project/DALI/input/DFT.csv")},
                     {"path": "project/DALI/SCH-Connect-Map.txt", "locator": "列2 CH1 High -> BST (K131,K132,K134,K135), CH1 Low -> SW (K132,K133,K134,K135)", "sha256": sha(ROOT / "project/DALI/SCH-Connect-Map.txt")}],
    },
    {
        "id": "LOOP_TM601_SW2PGND_1A",
        "from": "SW", "to": "PGND", "resources": ["60", "61", "133", "134", "154", "155"],
        "confidence": "derived",
        "net": "NetK61_SW_S1_4 -> NetK93_AGND2PGND_S1_4",
        "sourceChannel": "S1_FPVIe channel 0 (FL0/SL0 -> SW) high side into PGND via K154+K155",
        "assertion": "FPVIe floating 1 A loop SW->PGND requested by DFT iset[sw2pgnd,1,1e-6,0]; the PGND terminal is tied to AGND through K93_AGND2PGND, so the loop return is a shared ground node",
        "evidence": [{"path": "project/DALI/input/DFT.csv", "locator": "TM601 row: iset[sw2pgnd,1,1e-6,0]", "sha256": sha(ROOT / "project/DALI/input/DFT.csv")},
                     {"path": "project/DALI/SCH-Connect-Map.txt", "locator": "列2 CH0 High -> PGND (K154,K155); CH0 Low -> SW (K60,K61)", "sha256": sha(ROOT / "project/DALI/SCH-Connect-Map.txt")}],
    },
]

# ---------------------------------------------------------------- hazards
def H(kind, desc, mit, tms, evidence, severity, extra=None):
    h = {"kind": kind, "description": desc, "mitigationRequired": True,
         "requiredMitigation": mit, "tmLinks": tms, "severity": severity,
         "evidence": [ev(p, l) for p, l in evidence]}
    if extra:
        h.update(extra)
    return h


# Revision of the cross-owned dft-ir.json whose claims this IR verified. Declared as a constant on
# purpose: the file is regenerated repeatedly by dft-expert, so a live read would rewrite this IR on
# every republish. Liveness is covered by claimDigest, re-derived by selfcheck_schematic_ir.py.
DFT_IR_VERIFIED_REVISION_SHA256 = "7c47dc20ae7fdd5f8db0bb8068bde8c92fad70e517ccbad4e4325c60992e2816"

# Revision of the cross-owned dft-ir.json whose claims this IR verified. Declared as a constant on
# purpose: dft-expert regenerates that file repeatedly during the run, so a live read would rewrite
# this IR on every republish and make the IR's own hash meaningless. Liveness is covered by
# claimDigest plus the expectations below, both re-derived by selfcheck_schematic_ir.py.
DFT_IR_VERIFIED_REVISION_SHA256 = "d8f900a41e6a30f2c7022a881f5636a652c0fe0a6189e0d42aeb43fe1388a31b"
# What this IR asserts about the DFT artefact. selfcheck_schematic_ir.py compares the live claims
# against these and fails hard on mismatch, so a later republish that reverts the ruled polarity is
# caught instead of silently invalidating a citation.
DFT_IR_EXPECT_EXACT = {
    "TM600.forcePins": ["PMID (High)", "SW (Low)"],
    "TM601.forcePins": ["PGND (High)", "SW (Low)"],
    "ruledPairMarker": True,
}
DFT_IR_EXPECT_CONFLICTS = ["C-01", "C-05"]
DFT_IR_EXPECT_ISET = [("TM600", "sw", 1.0, "A"), ("TM601", "pmid_sw", 1.0, "A")]

DFT_ANCHOR = dft_ir_anchor()


def H_anchored(kind, desc, mit, tms, evidence, severity, extra=None):
    """H() variant that attaches the DFT content anchor to any dft-ir.json citation."""
    h = H(kind, desc, mit, tms, evidence, severity, extra)
    for record in h["evidence"]:
        if record["path"].endswith("dft-ir.json"):
            for field in ("claimDigest", "claims", "expectations", "expectationConflicts",
                          "expectationIset", "expectationsAssertedBy", "sha256Role"):
                if field in DFT_ANCHOR:
                    record[field] = DFT_ANCHOR[field]
            record["mutableByDesign"] = True
            record["ownershipNote"] = ("owned by dft-expert and regenerated during the run; the sha256 is a "
                                       "build-time pin, the claimDigest is the authoritative cross-check")
    return h


hazards = [
    H("high-current",
      "TM600 forces 1 A between PMID and SW and TM601 forces 1 A between SW and PGND "
      "(DFT iset[pmid2sw,1,...] / iset[sw2pgnd,1,...]). ACM200 tops out at +-200mA and FXVIe_PLUS at "
      "+-1A pulse; only FPVIe (+-10A, 2 channels, independently floating) can source 1 A. Both ends of each "
      "loop must be routed through a BUS relay, otherwise the pin stays on its default source and the loop shorts two instruments.",
      "Route TM600/TM601 through FPVIe BUS: PMID via K83_BUSH_PMID, SW via K60_BUSL_VCP+K61_SW, "
      "PGND via K154_BUSH_AMUX+K155_FOVI_PGND; never leave default ACM200/FXVIe_PLUS sources enabled on SW/PGND.",
      ["TM600", "TM601"], [("project/DALI/input/DFT.csv", "TM600 row iset[pmid2sw,1,1e-3,0]; TM601 row iset[sw2pgnd,1,1e-6,0]"),
                            ("project/DALI/SCH-Connect-Map.txt", "L165-167 PMID K83; L174-176 SW K60,K61; L156-158 PGND K154,K155"),
                            ("knowledge/sources/hardware-specs.md", "L17 FPVIe +-10A/2A(pulse)/1A; L16 ACM200 max +-200mA; L13 FXVIe_PLUS +-1A(pulse)"),
                            ("knowledge/hardware/bus-topology.md", "L151 iset[AxB]>=1A only FPVI can do it, BUS mandatory")],
      "high"),
    H("e006-reverse-bias",
      "E006 PMID-FET-SW coupling: with the HS FET on, SW==PMID. If BST falls more than a diode drop below "
      "SW/PMID the 220nF bootstrap capacitor (Cap_SW_BST_S1) is reverse biased and can damage the die. "
      "TM600 drives vset[bst2sw,5] while also forcing iset[pmid2sw,1], so BST must lead PMID/SW by >=5V at "
      "all times, and the FET must stay on while the rails collapse.",
      "Power up with BST leading PMID by >=5V using synchronised ramps; power down keeping the FET on until "
      "both rails reach 0 (bus-topology.md 九). Note hardware secondary protection: D_BST_SW_S1 (Schottky, "
      "anode on the SW-side net NetCap_SW_BST_S1_2, cathode on the BST-side net NetCap_SW_BST_S1_1) clamps "
      "BST-SW to >= -Vf, but that is a clamp, not a substitute for the ramping rule.",
      ["TM600", "TM1205"], [("knowledge/hardware/bus-topology.md", "L264-281 section 九 E006 reverse-bias protection"),
                             ("project/DALI/input/DFT.csv", "TM600 row vset[bst2sw,5,1e-3,0] + iset[pmid2sw,1,1e-3,0]"),
                             ("project/DALI/Dali-SCH.csv", "D_BST_SW_S1 pin1(anode)=NetCap_SW_BST_S1_2 pin2(cathode)=NetCap_SW_BST_S1_1")],
      "high",
      {"schmitt": None, "polarityNote": "diode polarity derived from Altium pin convention pin1=anode, pin2=cathode; confidence=derived"}),
    H("shared-resource",
      "Each FPVIe channel has exactly one high-force/high-sense and one low-force/low-sense BUS wire "
      "(FPVIe0_FH_BUS_S1 / _SH_BUS_S1 / _FL_BUS_S1 / _SL_BUS_S1, same for FPVIe1), and the BUS relays sit "
      "directly on those wires: K83 pins 3/6 are on FPVIe0_FH_BUS/_SH_BUS, K60 pins 3/6 on "
      "FPVIe0_FL_BUS/_SL_BUS, K154 pins 3/6 back on FPVIe0_FH_BUS/_SH_BUS. Consequently every closed high-side "
      "BUS relay on a channel shorts its DUT pin to every other closed high-side BUS relay of that channel - "
      "e.g. closing K83 (PMID) and K154 (PGND) at the same time shorts PMID to PGND through FPVIe0_FH_BUS. "
      "This is the same failure mode bus-topology.md 五 describes with the previous revision's numbers.",
      "Close exactly the BUS relays of the active loop, one pin per BUS side, and prove the closed set against "
      "the DFT rail list before every force: for TM600 on FPVIe0 that is K83 (PMID, high) + K60/K61 (SW, low); "
      "for TM601 that is K60/K61 (SW, high) + K154/K155 (PGND, low); never leave a second pin attached to the "
      "same BUS wire.",
      ["TM600", "TM601", "TM000", "TM001", "TM102", "TM103", "TM135", "TM1205"],
      [("project/DALI/Dali-SCH.csv", "K83_BUSH_PMID_S1 pin3=FPVIe0_FH_BUS_S1 pin6=FPVIe0_SH_BUS_S1; K60_BUSL_VCP_S1 pin3=FPVIe0_FL_BUS_S1 pin6=FPVIe0_SL_BUS_S1; K154_BUSH_AMUX_S1 pin3=FPVIe0_FH_BUS_S1 pin6=FPVIe0_SH_BUS_S1"),
       ("knowledge/hardware/bus-topology.md", "L153-169 BUS use 2: closing several BUS relays shorts those pins; L192-199 BUS short risk")],
      "high"),
    H("shared-resource",
      "K141_QTMU_BUSA_S1S2 and K142_QTMU_BUSB_S1S2 BRIDGE the two FPVIe channels' BUS wires: K141 pin4 = "
      "FPVIe0_FH_BUS_S1, pin2 = FPVIe1_FH_BUS_S1, pin3 = the QTMU line; K142 pin4 = FPVIe0_FL_BUS_S1, pin2 = "
      "FPVIe1_FL_BUS_S1. The default QTMU routes the netlist uses for PMID (req K83+K141) and SW (req "
      "K60,K61,K142) therefore require exactly the relays that merge FPVIe0 and FPVIe1 into one node - which "
      "destroys TM600's two independent floating loops if left closed.",
      "Open K141 and K142 for TM600/TM601 whenever FPVIe owns the pins; do not reuse the QTMU default route "
      "relay set as the FPVIe relay set.",
      ["TM600", "TM601"], [("project/DALI/Dali-SCH.csv", "K141_QTMU_BUSA_S1S2 pin4=FPVIe0_FH_BUS_S1 pin2=FPVIe1_FH_BUS_S1 pin3=NetK66_TMU_nQON_S1_2; K142 pins 4/2 = FPVIe0_FL_BUS_S1 / FPVIe1_FL_BUS_S1"),
                            ("team/artifacts/acceptance-20260916-dali10/schematic-validation/scope-paths.json", "PMID path S10_CH0_A required_on=[83,141]; SW path S10_CH0_B required_on=[60,61,142]")],
      "high"),
    H("measurement-validity",
      "The FPVIe0 PC route (K87/K88/K90/K91 + K82_R_CS) runs the bus current through the on-board current-sense "
      "shunts R1_CS_S1 = 100mohm +-1% and R2_CS_S1 = 5mohm +-1%, which sit on net FPVIe0_FL_PC_S1. Those shunts "
      "are the same order as the TM600/TM601 limits (10mohm / 8mohm), so using the PC route makes the mOhm "
      "result dominate by the shunt instead of the DUT.",
      "Measure TM600/TM601 through the FPVIe BUS Kelvin route (K87/K88/K89 for channel 0, K131/K132/K133 for "
      "channel 1) and keep the PC route (K90/K91 + K82_R_CS) open for the RDSON items.",
      ["TM600", "TM601"], [("project/DALI/SCH-Connect-Map.txt", "L189-230 CH0 High -> VAC/VCP route contains K90,K91,K82; L165-167 PMID uses only K83"),
                            ("project/DALI/Dali-SCH.csv", "R1_CS_S1=100mohm 1%, R2_CS_S1=5mohm 1% on FPVIe0_FL_PC_S1")],
      "high"),
    H("kelvin-integrity",
      "Two net-short groups are hard-wired on the board: FPVIe0_FH_PC_S1 <-> FPVIe0_SH_PC_S1 and "
      "FPVIe0_FL_PC_S1 <-> FPVIe0_SL_PC_S1 (DIRECT_WIRE, CONFIRMED). Any route that passes through the FPVIe0 "
      "PC nets is therefore no longer 4-wire Kelvin - the sense line carries the force IR drop. At 1A and "
      "10mohm that is 10mV of signal being corrupted by the lead drop.",
      "Use the FPVIe0 BUS route (K87 force / K88 + K89 sense, which never enters the PC nets) for all "
      "mOhm-level force/sense items; do not rely on the PC channel for TM600/TM601.",
      ["TM600", "TM601"], [("project/DALI/SCH-Connect-Map.txt", "net短接 section: [DIRECT_NET_ALIAS] FPVIe0_FH_PC_S1 <-> FPVIe0_SH_PC_S1, FL_PC <-> SL_PC"),
                            ("knowledge/sources/fpvie.md", "L587-616 FPVIe_HIGH_SIDE/FPVIe_LOW_SIDE contact check semantics")],
      "high"),
    H("shared-resource",
      "SW and VCP share the BUSL_VCP low node: K60_BUSL_VCP selects the node and K61_SW decides whether it "
      "reaches SW (SetOn) or stays on the VCP branch (default NC path). Closing K61 while the VCP branch is "
      "active (K68_VCP_F with C2_CS_S1 100nF) couples VCP into SW.",
      "Keep K68/VCP branch inert while K61 is closed for TM600/TM601; if DFT for the same function needs VCP, "
      "split into separate functions (bus-topology.md 八 forbids merging different loops).",
      ["TM600", "TM601", "TM1205"], [("project/DALI/SCH-Connect-Map.txt", "L174-176 CH0 Low -> SW (K60,K61); L231-232 CH0 Low -> VCP (K60); K61(Relay-NC) is the VCP default path"),
                                      ("project/DALI/phase2_singlepoint_output.txt", "#define K60_BUSL_VCP 60 / #define K61_SW 61 / #define K68_VCP_F 68")],
      "high"),
    H("shared-resource",
      "VCC and ACDRV1/2/3 share the BUSH_ACDRV high bus: the VCC high path needs K30_BUSH_ACDRV + K25_VCC, and "
      "the ACDRV high paths also need K30 plus K22/K23/K24. With K30 and K25 closed the BUSH node is common, so "
      "only K22/K23/K24 separate VCC from the ACDRV pins. K25 was deliberately excluded from the short-relay "
      "definitions on 2026-08-26 (SKILL.md), so nothing in the published defines warns about it.",
      "Never drive ACDRV while VCC is being sensed/forced without an explicit review of K22/K23/K24 state; "
      "treat K25+K30 as one atomic shared resource for TM000/TM001 (Iq on VBAT, VCC sensed).",
      ["TM000", "TM001", "TM102", "TM103", "TM135"], [("project/DALI/SCH-Connect-Map.txt", "L216-218 CH0 High -> VCC (K25,K30); L18-20 ACDRV1 High uses K30+K22"),
                                                       ("scripts/schematic_parse/SKILL.md", "K25 (VCC<->ACDRV common rail) deliberately not defined as a short 2026-08-26")],
      "medium"),
    H("shared-resource",
      "PGND and AGND are tied together by K93_AGND2PGND (classified [Connect] by the six-gate parse). The "
      "TM601 1A loop returns through net NetK93_AGND2PGND while every AGND-referenced source (ACM200 / "
      "FXVIe_PLUS low side = AGND_F_S1) uses that same ground.",
      "Model the TM601 return as a shared ground: verify the 1A IR drop across the ground path (R_PGND_S1) does "
      "not shift AGND_F_S1 beyond the TM601 limit, and do not enable K93 unless the DFT rail set requires it.",
      ["TM601", "TM000", "TM001", "TM102", "TM103"], [("project/DALI/Component-Statistic.txt", "[Connect] K93_AGND2PGND; L156-158 PGND paths return on NetK93_AGND2PGND"),
                                                       ("project/DALI/SCH-Connect-Map.txt", "L156-158 CH0 High -> PGND dut_net NetK93_AGND2PGND_S1_4/_5")],
      "medium"),
    H("shared-resource",
      "AMUX and PGND are bound to one FXVIe_PLUS channel group: _PIN_CHANNEL_DEFINE_AMUX_PGND_FXVI_ = S3_3 (plus "
      "S4_3/S13_3/S14_3/S19_3/S20_3/S29_3/S30_3 across sites). K154_BUSH_AMUX and K155_FOVI_PGND hang off that "
      "same AMUX/PGND node pair.",
      "Do not run TM102/TM103 (AMUX voltage) and TM601 (PGND current return) on the same site concurrently; "
      "serialise them, and close only the BUS/K relay the active item needs.",
      ["TM102", "TM103", "TM601"], [("D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h", "L10 _PIN_CHANNEL_DEFINE_AMUX_PGND_FXVI_ \"S3_3,S4_3,...\""),
                                     ("project/DALI/SCH-Connect-Map.txt", "L154-158 PGND via K154,K155; AMUX via K154,K155,K17,K18,K20")],
      "medium"),
    H("shared-resource",
      "FPVIe hardware has only 2 channels per site, and both are consumed by a single TM600 item: channel 0 for "
      "the PMID-SW 1A loop and channel 1 for the BST-SW 5V loop. TM601 additionally needs a channel for the "
      "SW-PGND 1A loop. bus-topology.md 八 forbids merging HS and LS loops (different BUS pairs, mutually "
      "exclusive FET fields 0x59=0x01 vs 0x02, different PMID voltages, thermal-switch hazard).",
      "Implement TM600 and TM601 as separate functions, each owning both FPVIe channels; never merge them, and "
      "release the channels (FI=0 -> FV=0 -> OFF) before re-configuring the BUS relays.",
      ["TM600", "TM601"], [("knowledge/sources/hardware-specs.md", "L17 FPVIe 2 channels, each independently floating"),
                            ("knowledge/hardware/bus-topology.md", "L183-190 FPVI BUS priority, only 2 channels; L251-261 HS/LS must not merge"),
                            ("project/DALI/input/DFT.csv", "TM600 0x59=0x01 (HS); TM601 0x59=0x02 (LS)")],
      "high"),
    H("cross-site-coupling",
      "Several relays on the scope paths are mechanical G6K parts shared between sites 1 and 2 (designator "
      "suffix _S1S2), including the ones that gate the very capacitors and Kelvin rows TM600/TM601 depend on: "
      "K85_CAP_PMID_S1S2, K57_CAP_BST_SW_S1S2, K87/K89_KELVIN0_S1S2, K131/K133_KELVIN1_S1S2, plus "
      "K13_VBAT_Cap_S1S2, K0_VCC_Cap_S1S2, K5_VBUS_Cap_S1S2, K21_VAC_Cap_S1S2 for the foundation/toggle items. "
      "Two sites cannot independently open/close them.",
      "Treat the _S1S2 set as one atomic resource: parallel-site execution of TM600/TM601/TM000/TM001 is only "
      "valid when both sites request the identical state for every shared relay in the set.",
      ["TM000", "TM001", "TM102", "TM103", "TM108", "TM109", "TM135", "TM600", "TM601", "TM1205"],
      [("project/DALI/Dali-SCH.csv", "designators K0/K5/K13/K21/K44/K45/K57/K82/K85/K87/K89/K131/K133/K141/K142/K151 with _S1S2 suffix"),
       ("knowledge/hardware/relays.md", "L56-58 CBIT group 机械共享 = G6K-2G-Y, 2 sites share one relay, suffix _S1xS2")],
      "high"),
    H("measurement-validity",
      "QTMU low side is DGND and QTMU carries a single line (bus-topology.md 2.3: QTMU BUS has FH only, FL goes "
      "to machine ground, no Kelvin split). The default netlist routes for PMID (S10_CH0_A, K83+K141) and SW "
      "(S10_CH0_B, K60/K61/K142) are QTMU routes, which is fine for Iq/toggle DC work but invalid for a "
      "mOhm-level force/sense measurement.",
      "For TM600/TM601 use only FPVIe Kelvin routes; do not measure RDSON on the QTMU defaults.",
      ["TM600", "TM601"], [("knowledge/hardware/bus-topology.md", "L57-81 digital sources unify low to DGND; L75 QTMU BUS is 1 line, no Kelvin"),
                            ("project/DALI/SCH-Connect-Map.txt", "L505/L515 PMID and VCC via S10_CH0_A with K141; SW via S10_CH0_B with K142"),
                            ("project/DALI/Component-Statistic.txt", "QTMUe (2): S10_CH0_A, S10_CH0_B; note '推断为 QTMU, 需用户确认'")],
      "high"),
    H_anchored("thermal-switching",
      "Relay re-configuration must not hot-switch unequal potentials: a BUS relay carrying a pin at one rail "
      "voltage while the relay it replaces sits at another will arc the G6K contacts, and the G6K parts shared "
      "between sites (_S1S2) disturb the other site when they switch. DFT.csv asks PMID=15V/9V while reg_config "
      "asks PMID=5V and VBUS=5V; whatever setpoint is eventually used, the potential difference between the "
      "relays being swapped must be zeroed first.",
      "Before every cbite.SetOn/SetOff reconfiguration of a BUS relay, ramp the pin being disconnected to the "
      "same potential as the one being closed (or to 0); power down with FI=0 -> FV=0 -> OFF.",
      ["TM600", "TM601"], [("knowledge/hardware/bus-topology.md", "L201-208 relay thermal-switch rule"),
                            ("project/DALI/input/DFT.csv", "TM600 vset[pmid,15,...] / TM601 vset[pmid,9,...]"),
                            ("team/artifacts/acceptance-20260916-dali10/dft-ir.json", "TM600/TM601 stimuli resolved to PMID 5V / VBUS 5V from reg_config/*.sv (conflicts C-01/C-05)"),
                            ("knowledge/standards/relay-checklist.md", "relay checklist governing closure order")],
      "medium"),
    H_anchored("polarity",
      "BUS-side assignment for the TM601 loop: in this netlist SW is bound to the FPVIe0 LOW bus (K60 pins 3/6 = "
      "FPVIe0_FL_BUS_S1 / FPVIe0_SL_BUS_S1) while PMID and PGND are bound to the HIGH bus (K83 and K154 pins 3/6 "
      "= FPVIe0_FH_BUS_S1 / FPVIe0_SH_BUS_S1). A SW<->PGND 1A loop therefore has to drive SW as the low terminal "
      "and PGND as the high terminal - the inverse of the PMID<->SW orientation. Reversing it does not change the "
      "RDSON magnitude but it does reverse the current direction through the PGND node, which K93_AGND2PGND can "
      "tie to AGND_F, so the orientation and K93's state must be deliberate rather than incidental. "
      "STATUS 2026-09-16: the orientation conflict with the DFT record was raised by this IR and resolved by the "
      "captain as BD-02; dft-ir.json now reads TM601 force pins ['SW','PGND'] as the ruled pair sw2pgnd while "
      "keeping the reg_config/tm601.sv instrument node isrcPMID_SW as evidence. The hazard is retained because "
      "the netlist constraint it states (PGND = FPVIe0 ch0 HIGH, SW = ch0 LOW) is what makes the ruling "
      "physically realisable, and because an implementation that follows the .sv node name instead of the ruled "
      "pair would wire the wrong loop.",
      "Keep the orientation explicit per item in the setup contract: PMID<->SW = FPVIe0 high (K83) to low "
      "(K60/K61); SW<->PGND = FPVIe0 low (K60/K61) to high (K154/K155). Implement to the ruled pair sw2pgnd, not "
      "to the .sv instrument node name, and keep K93's state deliberate.",
      ["TM600", "TM601"], [("project/DALI/Dali-SCH.csv", "K60_BUSL_VCP_S1 pin3=FPVIe0_FL_BUS_S1 pin6=FPVIe0_SL_BUS_S1; K83 pin3/6=FPVIe0_FH_BUS_S1/_SH_BUS_S1; K154 pin3/6=FPVIe0_FH_BUS_S1/_SH_BUS_S1"),
                            ("team/artifacts/acceptance-20260916-dali10/dft-ir.json", "TM601 channels[0].pins=['PGND (High)','SW (Low)'] = the ruled pair sw2pgnd (BD-02 applied), which matches this netlist's polarity; the .sv node isrcPMID_SW is retained as evidence. TM600 channels[0].pins=['PMID (High)','SW (Low)'] also agrees. This citation is asserted, not merely quoted: see the expectations fields on this record"),
                            ("team/artifacts/acceptance-20260916-dali10/schematic-ir-sensing.json", "channelAllocationPerTm: TM600 ch0=PMID<->SW, ch1=BST<->SW; TM601 ch0=SW<->PGND (PGND high)")],
      "high"),
    H("relay-default-state",
      "Scope paths mix MOS opto relays (default OPEN, must SetOn) with mechanical G6K relays (default NC, must "
      "SetOff to open). Both appear in the same chain, e.g. K61_SW is MOS while K57_CAP_BST_SW / K85_CAP_PMID / "
      "K87_KELVIN0 / K89_KELVIN0 / K131_KELVIN1 / K133_KELVIN1 are G6K. Omitting a K on a MOS relay leaves the "
      "path open; omitting a K on a G6K relay leaves the isolation closed.",
      "Emit an explicit per-relay state table for every function, and explicitly SetOff (not merely 'not SetOn') "
      "the isolation relays K85_CAP_PMID, K57_CAP_BST_SW, K13_VBAT_Cap, K0_VCC_Cap, K5_VBUS_Cap, K21_VAC_Cap, "
      "and the unused Kelvin rows.",
      ["TM000", "TM001", "TM600", "TM601"], [("knowledge/hardware/relays.md", "L33-48 MOS default open; L56-58 G6K default NC"),
                                             ("project/DALI/phase2_singlepoint_output.txt", "group headers MOS / G6K_Dedicated / G6K_Shared for K85/K57/K87/K89/K131/K133/K61")],
      "high"),
    H("isolation-gap",
      "The current debug StdAfx.h publishes no discharge role at all: a grep of the RELAY_ROLE section returns "
      "K_*_Cap / K_*_P2P / K_*_PU / K_*_PD / K_*_ST but no DCHG entry, while knowledge/hardware/cbit-mapping.md "
      "still documents a legacy K_VBUSD_DCHG(115) on relay 115. The discharge path for the TM600/TM601 rails is "
      "therefore not a published define and must be built from the Cap relays plus passive bleed resistors.",
      "Express discharge explicitly per rail (see the `discharge` section of this IR) instead of relying on a "
      "named DCHG role; treat cbit-mapping.md K76 -> K_VBUSD_DCHG(115) as legacy and unverified for this netlist.",
      ["TM600", "TM601", "TM000", "TM001"], [("D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h", "L652-689 RELAY_ROLE section: no _DCHG define present"),
                                             ("knowledge/hardware/cbit-mapping.md", "L46 DCHG=Discharge; L176 K76 -> K_VBUSD_DCHG(115) legacy mapping")],
      "medium"),
    H("legacy-numbering",
      "The knowledge base still quotes the previous board revision's relay numbers for exactly the pins in "
      "scope: bus-topology.md 五/六 use K31_BUS_PMID / K15_BUS_SW / K17_BUS_BST / K33_PGND and "
      "pin-resource-map.md lists K31_BUS_PMID_S1 / K32_PMID_Cap / K15_BUS_SW_S1 / K17_BUS_BST_S1, whereas this "
      "netlist assigns K31_VMCU, K33_VAC_WL, K83_BUSH_PMID, K41_BUS_BST, K85_CAP_PMID, K60_BUSL_VCP, K61_SW, "
      "K154_BUSH_AMUX, K155_FOVI_PGND. Copying the doc numbers closes the wrong relays.",
      "Take relay numbers only from phase2_singlepoint_output.txt / StdAfx.h / SCH-Connect-Map.txt for this "
      "netlist; treat every number quoted in bus-topology.md and pin-resource-map.md as a legacy alias needing "
      "explicit re-mapping.",
      ["TM600", "TM601", "TM1205"], [("knowledge/hardware/bus-topology.md", "L148 K31_BUS_PMID, L166 K31/K17/K33, L219-221 K31/K15/K17"),
                                      ("knowledge/hardware/pin-resource-map.md", "L38-41 K31_BUS_PMID_S1 / K32_PMID_Cap / K15_BUS_SW_S1 / K17_BUS_BST_S1"),
                                      ("project/DALI/phase2_singlepoint_output.txt", "#define K31_VMCU 31 / #define K33_VAC_WL 33 / #define K83_BUSH_PMID 83 / #define K41_BUS_BST 41")],
      "high"),
    H("limit-inconsistency",
      "The DFT stimulus for the in-scope high-current items is numerically self-inconsistent with the instrument "
      "ranges: TM600 iset[pmid2sw,1,1e-3,0] asks for 1A with a 1mA compliance figure, and TM601 "
      "iset[sw2pgnd,1,1e-6,0] asks for 1A with 1uA; the companion vset[pmid,15,100e-6,0] / vset[pmid,9,...] "
      "likewise pair high voltages with 100uA compliance. The older archive revision of the same rows uses "
      "11mohm/7.5mohm and pmid 5V where DFT.csv uses 10mohm/8mohm and pmid 15V/9V. A 10mohm limit at 1A is a "
      "10mV signal, so the compliance/range choice decides whether the item can witness its limit at all.",
      "Resolve the current/compliance/range triple and the expected-value discrepancy before coding; this IR "
      "records the schematic capability boundary (FPVIe 1A range, +-100mV measure range, 10A clamp) and leaves "
      "the number selection to the DFT owner.",
      ["TM600", "TM601"], [("project/DALI/input/DFT.csv", "TM600 row: vset[pmid,15,...] vset[bst2sw,5,1e-3,0] iset[pmid2sw,1,1e-3,0] expect 10 mohm; TM601: vset[pmid,9,...] iset[sw2pgnd,1,1e-6,0] expect 8 mohm"),
                            ("project/DALI/_archive/_dump_OVERVIEW.txt", "L981 TM600 11 mohm with vset[pmid,5,...]; L994 TM601 7.5 mohm with I=1A SW-PGND=0.3"),
                            ("knowledge/sources/hardware-specs.md", "L17 FPVIe ranges +-10A/2A(pulse)/1A/... and +-100mV measure range; L40 current-force accuracy at 1A")],
      "medium"),
    H("floating-source-topology",
      "DFT names a floating rail 'bst2sw' but the netlist has no BST_SW DUT pin - it has separate BST_F_S1/BST_S1 "
      "and SW_F_S1/SW_S_S1 kelvin pairs joined only by Cap_SW_BST_S1 (220nF) and D_BST_SW_S1. The floating loop "
      "must be assembled from FPVIe1 FH1/SH1 -> BST and FL1/SL1 -> SW (K131/K132/K134/K135), and the loop current "
      "returns through the capacitor and the Schottky, not through a pin-to-pin wire.",
      "Do not model bst2sw (or pmid_sw) as a single net; build the loop from two pin routes on one FPVIe channel "
      "and let the 220nF cap carry the loop current (part of the measurement, not a decoupling element to drop).",
      ["TM600"], [("project/DALI/input/DFT.csv", "TM600 row vset[bst2sw,5,1e-3,0]"),
                   ("project/DALI/SCH-Connect-Map.txt", "L265-267 CH1 High -> BST; L391-393 CH1 Low -> SW"),
                   ("project/DALI/Dali-SCH.csv", "Cap_SW_BST_S1 220nF pin1=NetCap_SW_BST_S1_1 pin2=NetCap_SW_BST_S1_2")],
      "high"),
    H("shared-resource",
      "SW1/SW2 and PMID/HG2 are bound to single FXVIe_PLUS channels (_PIN_CHANNEL_DEFINE_SW1_SW2_FXVI_ = S3_0, "
      "_PIN_CHANNEL_DEFINE_PMID_HG2_FXVI_ = S3_1). FXVIe_PLUS reaches PMID through the default-closed K84_HG2 "
      "path (no SetOn needed), so the PMID default source is live unless K84 is explicitly opened; the same "
      "channel is used when the FXVIe_PLUS route is needed elsewhere.",
      "Decide explicitly whether K84_HG2 stays in its default state during TM600/TM601; if the FPVIe BUS owns "
      "PMID, the FXVIe_PLUS default must not fight it.",
      ["TM600", "TM601"], [("D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h", "L7 SW1_SW2_FXVI S3_0; L8 PMID_HG2_FXVI S3_1"),
                            ("project/DALI/SCH-Connect-Map.txt", "L820-822 FXVIe_PLUS -> PMID [Kelvin] 需闭合: 无(默认导通) via K84"),
                            ("team/artifacts/acceptance-20260916-dali10/schematic-validation/path_proofs.json.txt", "S3_FXVIe_PLUS_FH1/SH1 -> PMID_F_S1/PMID_S_S1 with required_on=[]")],
      "medium"),
    H("anti-short",
      "The netlist provides P2P short relays on VAC/KLV pins: K14_VAC1_P2P, K15_VAC2_P2P, K16_VAC3_P2P, "
      "K38_KLV1_2_short (KLV1 <-> KLV2, two DUT nodes), K39_KLV1_P2P, K40_KLV2_P2P, plus ACDRV/HG/LG to AGND. "
      "They are MOS parts that default open, so a stray SetOn of the wrong K number silently shorts a DUT pin "
      "(or two DUT pins together) with no path-proof entry to reveal it, because pins-to-ground attachments sit "
      "outside the source->PIN path segments.",
      "Close a P2P relay only when the item's DFT explicitly requires the pin-to-ground (or pin-to-pin) short, "
      "and verify K38/K39/K40 explicitly for the TM108/TM109 VAC-preset items since KLV1/KLV2 are the preset "
      "Kelvin terminals.",
      ["TM108", "TM109", "TM102", "TM103"], [("project/DALI/SCH-Connect-Map.txt", "列11 P2P-到地 K14/K15/K16/K39/K40; P2P-互短 KLV1<->KLV2 K38"),
                                              ("knowledge/hardware/relays.md", "L152-158 P2P relay is a pin-to-ground short, close only when the item requires it")],
      "medium"),
    H("force-sense",
      "59 Kelvin pairs cover the scope pins with 0 pair failures and 0 engine issues, but the FPVIe0 PC nets are "
      "board-shorted (see kelvin-integrity) and the Kelvin sense rows R_PMID_KLV_S1 / R_SW1_KLV_S1 are 10kohm "
      "series parts: a sense line resistance this high is only benign when the sense input is genuinely "
      "high-impedance, which must be confirmed against the FPVIe contact-check semantics.",
      "Run an FPVIe contact check (FPVIe_HIGH_SIDE/FPVIe_LOW_SIDE) before the mOhm items and confirm the sense "
      "line series resistance is inside the FPVIe sense-input specification.",
      ["TM600", "TM601"], [("team/artifacts/acceptance-20260916-dali10/schematic-validation/PATHPROOF-VALIDATION.txt", "kelvin_pairs=219, kelvin_pair_failures=0, issues=0"),
                            ("project/DALI/Dali-SCH.csv", "R_PMID_KLV_S1=10K on NetCap1_PMID_S1_1; R_SW1_KLV_S1 on the SW1 kelvin row"),
                            ("knowledge/sources/fpvie.md", "L587-616 FPVIe_HIGH_SIDE / FPVIe_LOW_SIDE contact check")],
      "medium"),
]

# ---------------------------------------------------------------- resource conflicts
fpvie_channels = [
    {"site": "S1 site1", "channels": ["S1_0 (FPVIe0)", "S1_1 (FPVIe1)"]},
]
res_conf = {
    "fpvieChannelBudget": {
        "perSiteChannels": 2,
        "tm600Requires": [{"loop": "PMID<->SW 1A", "channel": "FPVIe0"}, {"loop": "BST<->SW 5V", "channel": "FPVIe1"}],
        "tm601Requires": [{"loop": "SW<->PGND 1A", "channel": "FPVIe0-equivalent"}],
        "finding": "TM600 alone exhausts both FPVIe channels; TM600 and TM601 cannot share a function (also forbidden by bus-topology.md 八)",
        "evidence": [ev("knowledge/sources/hardware-specs.md", "L17 FPVIe 2 channels/site, independently floating")],
    },
    "sharedRelaysAcrossScopePins": conflicts["relaySharedAcrossScopePins"],
    "sharedRelayCount": len(conflicts["relaySharedAcrossScopePins"]),
    "crossSiteSharedRelaysOnScopePaths": [{"relay": n, "siteSharedDesignator": [d for d in COMP_PINS if re.match(rf"K{n}_.*_S1S2", d)]}
                                          for n in S1S2_SHARED
                                          if any(str(n) in conflicts["scopeRelaySets"][tm] if False else True for tm in [])],
    "crossSiteSharedRelaysAll": S1S2_SHARED,
    "tmRelaySets": conflicts["scopeRelaySets"],
    "scopePairOverlaps": conflicts["scopePairOverlaps"],
    "stabiliserRelaysOnScopeRails": conflicts["stabiliserRelaysOnScopeRails"],
    "pinToPinShortPaths": conflicts["pinToPinShortPaths"],
    "netShortGroups": conflicts["netShortGroups"],
    "agndPgndTie": {"relay": 93, "name": "K93_AGND2PGND", "classification": "Connect",
                    "evidence": [ev("project/DALI/Component-Statistic.txt", "[Connect] K93_AGND2PGND")]},
}

# ---------------------------------------------------------------- limits
limits = {
    "voltage": {
        "FPVIe": {"ranges": ["+-100V", "+-40V", "+-20V", "+-10V", "+-5V", "+-2V", "+-1V", "100mV (measure only)"],
                  "evidence": [ev("knowledge/sources/hardware-specs.md", "L17")]},
        "FXVIe_PLUS": {"ranges": ["+-40V", "+-30V", "+-20V", "+-10V", "+-3.6V"],
                       "evidence": [ev("knowledge/sources/hardware-specs.md", "L13")]},
        "ACM200": {"ranges": ["+-40V", "+-20V", "+-10V", "+-3.6V"], "evidence": [ev("knowledge/sources/hardware-specs.md", "L16")]},
        "DFTRequestedOnScopeRails": {"pmid_TM600": "15 V (DFT.csv)", "pmid_TM601": "9 V (DFT.csv)",
                                     "pmid_TM600_archive": "5 V (_dump_OVERVIEW.txt)",
                                     "bst2sw_TM600": "5 V", "vbat": "4.2 V", "vdrv": "5 V"},
        "boardRelayRating": "not stated in the available documentation - unresolved (see unresolvedTopology)",
    },
    "current": {
        "FPVIe": {"ranges": ["+-10A", "+-2A (pulse)", "+-1A", "+-100mA", "+-10mA", "+-1mA", "+-100uA", "+-10uA (measure)"],
                  "evidence": [ev("knowledge/sources/hardware-specs.md", "L17")]},
        "FXVIe_PLUS": {"ranges": ["+-1A (pulse)", "+-100mA", "+-10mA"], "evidence": [ev("knowledge/sources/hardware-specs.md", "L13")]},
        "ACM200": {"ranges": ["+-200mA", "+-100mA", "+-10mA", "+-1mA"], "evidence": [ev("knowledge/sources/hardware-specs.md", "L16")]},
        "QTMUe": {"ranges": ["time measurement only - cannot source a current"], "evidence": [ev("knowledge/sources/hardware-specs.md", "L26-L27")]},
        "QVM": {"ranges": ["voltmeter only - no current"], "evidence": [ev("knowledge/sources/hardware-specs.md", "L23")]},
        "DCM_PLUS": {"ranges": ["+-32mA / +-40mA digital"], "evidence": [ev("knowledge/sources/hardware-specs.md", "L29-L31")]},
        "rule_ge200mA_requires_fpvie": {"applied": True, "evidence": [ev("knowledge/sources/index.md", "L13 FPVIe >=200mA high current / floating source")]},
        "rule_ge1A_requires_10A_range_and_bus": {"applied": True, "evidence": [ev("knowledge/hardware/bus-topology.md", "L151 iset[AxB]>=1A only FPVI reachable, BUS mandatory")]},
        "dftRequestedOnScopeRails": {"TM600": "1 A PMID->SW", "TM601": "1 A SW->PGND"},
        "onBoardCurrentShunts": [{"designator": "R1_CS_S1", "value": "100mohm 1%", "net": "FPVIe0_FL_PC_S1"},
                                 {"designator": "R2_CS_S1", "value": "5mohm 1%", "net": "FPVIe0_FL_PC_S1"}],
        "accuracyNote": "FPVIe current force +-1A is +-(0.3mA+0.05%Rdg+10uA/V); at 1A with ~4.2V common mode that is about 0.84mA = 0.084% of reading, which is the same order as the RDSON tolerance budget",
        "accuracyEvidence": [ev("knowledge/sources/hardware-specs.md", "L40 current force accuracy table")],
    },
}

# ---------------------------------------------------------------- discharge
def _ohms(value: str) -> float | None:
    m = re.fullmatch(r"\s*([0-9.]+)\s*([kKmM]?)\s*", value or "")
    if not m:
        return None
    mult = {"": 1.0, "k": 1e3, "K": 1e3, "m": 1e-3, "M": 1e6}[m.group(2)]
    return float(m.group(1)) * mult


def _farads(value: str) -> float | None:
    m = re.fullmatch(r"\s*([0-9.]+)\s*([unp]?)F\s*", value or "")
    if not m:
        return None
    mult = {"": 1.0, "u": 1e-6, "n": 1e-9, "p": 1e-12}[m.group(2)]
    return float(m.group(1)) * mult


def cap_nets(des: str) -> list[str]:
    real = find_designator(des)
    return [p["net"] for p in COMP_PINS.get(real or "", []) if p["net"] and p["net"] != "AGND_F_S1"]


def resistor_ends() -> dict:
    out = {}
    for d, pins in COMP_PINS.items():
        if not re.match(r"R_\w+_S1$", d):
            continue
        rv = _ohms(COMP_META.get(d, {}).get("value", ""))
        if rv is None:
            continue
        out[d] = {"ohms": rv, "value": COMP_META[d].get("value", ""),
                  "nets": sorted({p["net"] for p in pins if p["net"]})}
    return out


RESISTORS = resistor_ends()


def bleed_for(nets: list[str]) -> dict:
    """Resistors reachable from the capacitor nets, split into real ground-bleed
    paths and series resistors that only lead to another source node."""
    expanded = set(nets)
    for d, pins in COMP_PINS.items():
        if re.match(r"K\d+_", d) and {p["net"] for p in pins} & set(nets):
            expanded |= {p["net"] for p in pins if p["net"]}
    ground, series = [], []
    for d, info in RESISTORS.items():
        hit = sorted(set(info["nets"]) & expanded)
        if not hit:
            continue
        rec = {"designator": d, "ohms": info["ohms"], "value": info["value"],
               "atNets": hit, "onCapNetDirectly": bool(set(hit) & set(nets)),
               "otherNets": sorted(set(info["nets"]) - set(hit))}
        if "AGND_F_S1" in info["nets"]:
            ground.append(rec)
        else:
            series.append(rec)
    return {"bleedToAgndF": ground, "seriesOnly": series}

DISCHARGE_SPEC = [
    ("PMID", "Cap2_PMID_S1", "K85_CAP_PMID", "TM600/TM601 PMID node"),
    ("VBAT", "Cap2_VBAT_S1", "K13_VBAT_Cap", "TM000/TM001 Iq node (must NOT be closed while I(VBAT) is measured)"),
    ("VCC", "Cap2_VCC_S1", "K0_VCC_Cap", "TM000/TM001/TM103/TM135 VCC node"),
    ("VBUS", "Cap2_VBUS_S1", "K5_VBUS_Cap", "TM601/TM1205 VBUS node"),
    ("VAC1 (VAC)", "Cap2_VAC_S1", "K21_VAC_Cap", "TM108/TM109/TM102/TM103 VAC nodes"),
    ("V1P5/VDRV", "Cap2_V1P5_S1", "K126_V1P5_CAP", "TM600/TM601 vdrv rail"),
    ("BST-SW", "Cap_SW_BST_S1", "K57_CAP_BST_SW", "TM600/TM1205 bootstrap capacitor - carries the BST-SW loop current"),
    ("VCP", "C2_CS_S1", "K68_VCP_F", "VCP node sharing BUSL_VCP with SW"),
]

def relay_default(des: str) -> str:
    part = COMP_META.get(des or "", {}).get("value", "") or ""
    if re.search(r"IM06|G6K", part, re.I):
        return f"mechanical G6K ({part}): NC default, SetOn routes the pin onto the BUS/other pole"
    if re.search(r"TLP|G3VM", part, re.I):
        return f"MOS opto ({part}): OPEN default, SetOn closes"
    return f"unknown part type ({part or 'n/a'}) - verify against the CBIT table group header"


def rc_from_ground_bleed(cap_value_str: str, ground: list[dict]) -> dict | None:
    c = _farads(cap_value_str)
    if c is None or not ground:
        return None
    r = sum(g["ohms"] for g in ground)
    tau_s = c * r
    return {"capacitance_F": c, "bleedResistance_ohm": r,
            "tau_ms": round(tau_s * 1e3, 3), "fiveTau_ms": round(tau_s * 5e3, 1),
            "basis": "series sum of the resistors tied between the capacitor net and AGND_F_S1"}


discharge = []
for rail, cap, gate, note in DISCHARGE_SPEC:
    des = find_designator(cap)
    nets = cap_nets(cap)
    bleed = bleed_for(nets)
    gate_des = find_designator(gate)
    rec = {"rail": rail,
           "cap": {"designator": des, "value": COMP_META.get(des or "", {}).get("value", ""), "nets": nets},
           "gatingRelay": gate_des,
           "gatingRelayDefaultState": relay_default(gate_des) if gate_des else None,
           "note": note,
           "bleedToAgndF": bleed["bleedToAgndF"],
           "seriesResistorsOnly": bleed["seriesOnly"],
           "evidence": [{"path": "project/DALI/Dali-SCH.csv", "locator": f"Designator={des}", "sha256": sha(CSV_PATH)}]}
    rc = rc_from_ground_bleed(rec["cap"]["value"], bleed["bleedToAgndF"])
    if rc:
        rec["rcViaBleedToGround"] = rc
    else:
        rec["rcViaBleedToGround"] = None
        c = _farads(rec["cap"]["value"])
        direct_r = sum(b["ohms"] for b in bleed["seriesOnly"] if b["onCapNetDirectly"])
        all_r = sum(b["ohms"] for b in bleed["seriesOnly"])
        if c and all_r:
            rec["rcUpperBoundViaSeriesPath"] = {
                "capacitance_F": c,
                "resistanceOnCapTerminalDirectly_ohm": direct_r,
                "resistanceIncludingRelayGatedTerminals_ohm": all_r,
                "tau_ms_direct": round(c * direct_r * 1e3, 3) if direct_r else None,
                "tau_ms_all": round(c * all_r * 1e3, 3),
                "fiveTau_ms_all": round(c * all_r * 5e3, 1),
                "basis": ("series resistors around the capacitor; the relay-gated ones only participate when the "
                          "gating relay is closed (default for the G6K parts), and the whole figure is only "
                          "realisable when both capacitor terminals are driven to the same potential"),
            }
        rec["dischargeRequirement"] = ("no resistor to AGND_F_S1 on this rail: discharge must be driven by the "
                                       "sources (ramp both terminals to equal potential, then FI=0 -> FV=0 -> OFF); "
                                       "the series resistors listed only lead to the other source node")
    discharge.append(rec)

# ---------------------------------------------------------------- unresolved topology / open questions
unresolved = [
    {"id": "U1", "topic": "relay contact current rating",
     "detail": "No available document states the G6K-2G-Y (IM06DJR) / TLP3412 contact current rating for the *_S1S2 and BUS relays that must carry 1A in TM600/TM601. The 1A requirement is derived from the FPVIe capability and the DFT stimulus, not from a relay datasheet in this workspace.",
     "impact": "high", "evidence": [ev("knowledge/hardware/relays.md", "L3-48 relay types only, no current rating")]},
    {"id": "U2", "topic": "sense-line series resistance vs FPVIe sense input",
     "detail": "R_PMID_KLV_S1 / R_SW1_KLV_S1 / R_VBST_KLV_S1 etc. are 10kohm Kelvin rows in series with the sense path. Whether the FPVIe sense input tolerates this is not documented here.",
     "impact": "medium", "evidence": [ev("project/DALI/Dali-SCH.csv", "R_PMID_KLV_S1=10K Designator row")]},
    {"id": "U3", "topic": "FPVIe0/FPVIe1 low terminals both on SW",
     "detail": "TM600 lands FPVIe0 FL0 and FPVIe1 FL1 on the same SW node. hardware-specs.md says each FPVIe channel is independently floating, and Pin_Channel_define binds S1_0+S1_1 to one site-1 board, which makes a common low plausible, but the netlist alone cannot prove the two low terminals may be paralleled on one DUT pin.",
     "impact": "high", "evidence": [ev("knowledge/sources/hardware-specs.md", "L17 每通道独立浮动"),
                                     ev("D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h", "L79 _PIN_SITE_BIND_DEFINE_MD_FPVIE_SITE1_ \"S1_0,S1_1\"")]},
    {"id": "U4", "topic": "source type for S10_CH0_A / S10_CH0_B",
     "detail": "The parser note in Component-Statistic.txt says S10_CH0_A/B are inferred to be QTMU from the slot name and still need user confirmation. Both PMID and SW default routes use them.",
     "impact": "medium", "evidence": [ev("project/DALI/Component-Statistic.txt", "任务二 注: S10_CH0_A/B 按槽位命名推断为 QTMU, 需用户确认")]},
    {"id": "U5", "topic": "K84_HG2 default state during FPVIe ownership",
     "detail": "PMID's FXVIe_PLUS route is default-conducting through K84_HG2 (required_on empty, state NC). The netlist does not say whether that default must be opened when FPVIe takes PMID over the BUS.",
     "impact": "medium", "evidence": [ev("project/DALI/SCH-Connect-Map.txt", "L820-822 FXVIe_PLUS -> PMID 需闭合: 无(默认导通)")]},
    {"id": "U6", "topic": "discharge role not published",
     "detail": "No DCHG role exists in the current debug StdAfx.h, while cbit-mapping.md documents a legacy K76 -> K_VBUSD_DCHG(115). The realisable discharge mechanism in this netlist is the Cap relay plus the 1kohm bleed resistors to AGND_F_S1.",
     "impact": "medium", "evidence": [ev("D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h", "L652-689 RELAY_ROLE section"),
                                     ev("knowledge/hardware/cbit-mapping.md", "L46,L176 DCHG legacy mapping")]},
    {"id": "U7", "topic": "provenance strings inside the committed intermediates",
     "detail": "project/DALI/validation_manifest.json.txt records input at D:\\Newtest\\DSH\\ATE-Coding-Platform\\... and project/DALI/path_proofs.json.txt records D:\\Newtest\\CLAUDE_PROCESS\\... with a different CSV sha256 (5FEAADA5...). Re-running the pipeline from the current CSV produced byte-identical connect map / component statistic / synthetic EDIF and identical 669/335/219 proof counts, so the conclusions hold, but the committed provenance strings are stale.",
     "impact": "medium", "evidence": [ev("project/DALI/path_proofs.json.txt", "input.path / input.sha256 (stale)"),
                                     ev("team/artifacts/acceptance-20260916-dali10/schematic-validation/path_proofs.json.txt", "input.path / input.sha256 (regenerated)")]},
    {"id": "U8", "topic": "unrouted FXVIe_PLUS / G6K cross path K90",
     "detail": "relays.md L184 warns that K90_PC0_Force's NC path cross-connects the high and low BUS domains and must be rejected during tracing for standard FPVIe DUT-pin routing. K90/K91 appear on the FPVIe0 PC routes only, which is consistent, but a formal cross-path rejection test is not part of the shipped pathproof contracts.",
     "impact": "low", "evidence": [ev("knowledge/hardware/relays.md", "L184 K90 cross path must be rejected for standard FPVIe routing")]},
]

open_questions = [
    "TM600/TM601 DFT rows in project/DALI/input/DFT.csv and the archived revision in project/DALI/_archive/_dump_OVERVIEW.txt disagree on expected value (10 vs 11 mohm, 8 vs 7.5 mohm) and on the PMID setpoint (15V/9V vs 5V): which revision governs? (owned by dft-expert)",
    "Both DFT revisions pair a 1A iset with a uA/mA compliance argument (1e-3 / 1e-6) and a 100uA compliance on vset[pmid,...]; what is the intended compliance and instrument range triple?",
    "TM600's register comment in DFT.csv names D2A_BUBO_TM_LSON while TM601's names D2A_BUBO_TM_HSON, but 0x59 is 0x01 for TM600 and 0x02 for TM601 - are the two field comments swapped? The schematic consequence is which FET (HS PMID->SW or LS SW->PGND) the 1A loop exercises.",
    "The TM109 row in project/DALI/input/DFT.csv drives vset[vac3,3.8V/4.4V/4.1V/3.5V] although the item's short name is VAC2_PRST (the neighbouring TM110 row is the VAC3 item) - confirm whether TM109 exercises VAC2 or VAC3, since the schematic bound pin changes (VAC2 via K15/K19, VAC3 via K16/K18/K20).",
    "Is TM601's 1A force loop PMID<->SW or SW<->PGND? RESOLVED 2026-09-16: the netlist binds SW to the FPVIe0 LOW bus and PGND to the HIGH bus, so the loop is SW<->PGND with PGND as the high terminal; the captain ruled BD-02 on this evidence and dft-ir.json now carries the ruled pair sw2pgnd while keeping the .sv node name isrcPMID_SW as evidence. Retained here only as a pointer: implement to the ruled pair, not to the .sv instrument node name.",
    "No relay contact current rating is available in this workspace for the 1A TM600/TM601 loops - needs a hardware answer before the 1A force is signed off.",
    "DFT.csv and reg_config/tm600.sv, tm601.sv disagree on PMID (15V/9V vs 5V) and on the iset pair (pmid2sw/sw2pgnd vs sw/pmid_sw); dft-ir.json has already resolved these to the reg_config values (C-01/C-05). The schematic side only needs the final loop orientation confirmed, not the voltage magnitude.",
    "Does the FPVIe sense input tolerate the 10kohm series Kelvin rows (R_PMID_KLV_S1 / R_SW1_KLV_S1)?",
    "May FPVIe0 FL0 and FPVIe1 FL1 both sit on the SW pin (TM600 uses channel 0 for PMID-SW and channel 1 for BST-SW)? hardware-specs.md says each channel is independently floating, which makes the shared low plausible but unproven from the netlist.",
    "Is S10_CH0_A/S10_CH0_B really QTMU (parser note in Component-Statistic.txt still asks for user confirmation)? Both the PMID and SW default routes depend on it.",
    "Must K84_HG2 (PMID default FXVIe_PLUS route, default-conducting) be opened when FPVIe takes PMID over the BUS?",
    "Which mechanism is the sanctioned discharge path for the TM600/TM601 rails, given the current StdAfx.h publishes no DCHG role? Candidate: Cap relay opened plus the 1kohm bleed resistors, giving tau ~ 4.7ms on a 4.7uF rail.",
    "TM001/TM102/TM135/TM1205 rows are absent from project/DALI/input/DFT.csv (the file only carries TM000/TM103/TM108/TM109/TM600/TM601 of the ten): confirm that Dali_testmode.xlsx is the governing DFT source for those four.",
    "Isolate the FPVIe0 PC route's board-level F/S shorts (FPVIe0_FH_PC <-> SH_PC, FL_PC <-> SL_PC): confirm they do not leak into the BUS route so the BUS route stays true-Kelvin for the mOhm items.",
    "The archived intermediates carry stale absolute paths (ATE-Coding-Platform / CLAUDE_PROCESS) and path_proofs.json.txt even records a different CSV sha256; should the committed intermediates be regenerated so provenance matches the workspace?",
]

# ---------------------------------------------------------------- assemble
ir = {
    "runId": RUN_ID,
    "generatedBy": "schematic-expert (AgentTeams ate-dali-acceptance, task t2)",
    "scope": sorted(SCORE),
    "scopeDefinition": SCORE,
    "scopePinsPerTm": TM_PINS,
    "sources": [ev(p, l) for p, l in SRC],
    "dutPins": dut_pins,
    "testerChannels": [
        {"role": role, "pin": pin, "sourceType": stype, "macro": macro, "channels": chans, "note": note}
        for role, pin, stype, macro, chans, note in CHANNEL_FACTS
    ],
    "fpvieChannelBudget": fpvie_channels,
    "components": components,
    "relays": relays,
    "nets": [
        {"name": name, "members": NET_MEMBERS.get(name, []), "purpose": purpose,
         "aliasOnly": name in ALIAS_ONLY_NETS,
         "aliasEvidence": ALIAS_ONLY_NETS.get(name),
         "relaysOnBusWire": [{"relay": n, "pin": p} for n, p in BUS_WIRE_RELAYS.get(name, [])],
         "evidence": ([{"path": "project/DALI/Dali-SCH.csv", "locator": ALIAS_ONLY_NETS[name], "sha256": sha(CSV_PATH)}]
                      if name in ALIAS_ONLY_NETS else
                      [{"path": "project/DALI/Dali-SCH.csv", "locator": f"NetName={name}", "sha256": sha(CSV_PATH)}])}
        for name, purpose in NET_SPEC.items()
    ],
    "paths": paths,
    "derivedPaths": derived_loops,
    "hazards": hazards,
    "resourceConflicts": res_conf,
    "limits": limits,
    "discharge": discharge,
    "polarity": [
        {"component": "D_BST_SW_S1", "kind": "Schottky clamp across the bootstrap capacitor",
         "connection": {"pin1": "NetCap_SW_BST_S1_2 (SW side)", "pin2": "NetCap_SW_BST_S1_1 (BST side)"},
         "conclusion": "clamps BST-SW to >= -Vf, i.e. hardware mitigation for the E006 reverse-bias hazard",
         "confidence": "derived",
         "assumption": "Altium diode pin convention pin1=anode, pin2=cathode (not stated in the CSV)",
         "evidence": [{"path": "project/DALI/Dali-SCH.csv", "locator": "Designator=D_BST_SW_S1 (PinNumber 1 -> NetCap_SW_BST_S1_2, 2 -> NetCap_SW_BST_S1_1)", "sha256": sha(CSV_PATH)}]},
        {"component": "Cap_SW_BST_S1", "kind": "bootstrap capacitor, the BST-SW floating loop load",
         "connection": {"pin1": "NetCap_SW_BST_S1_1 (BST)", "pin2": "NetCap_SW_BST_S1_2 (SW)"},
         "conclusion": "TM600's vset[bst2sw,5] drives this 220nF part; its stored charge is part of the item, not decoupling",
         "confidence": "direct",
         "evidence": [{"path": "project/DALI/Dali-SCH.csv", "locator": "Designator=Cap_SW_BST_S1 value=220nF", "sha256": sha(CSV_PATH)}]},
        {"component": "FPVIe force/sense domains", "kind": "bus domain mapping",
         "connection": {"FH/SH": "HIGH-domain bus (BUSH / _PC)", "FL/SL": "LOW-domain bus (BUSL / _PC)"},
         "conclusion": "PMID is reached from the HIGH domain and SW/PGND/VBUS from the LOW domain; FH must pair with SH and FL with SL (no crossing)",
         "confidence": "direct",
         "evidence": [{"path": "knowledge/hardware/relays.md", "locator": "L175-184 FPVIe domain constraint (FH/SH high, FL/SL low, K90 cross path rejected)", "sha256": sha(ROOT / "knowledge/hardware/relays.md")},
                      {"path": "team/artifacts/acceptance-20260916-dali10/schematic-validation/path_proofs.json.txt", "locator": "rejected_paths KELVIN_ROLE_CROSS examples (87 of them for scope pins)", "sha256": sha(VAL / "path_proofs.json.txt")}]},
        {"component": "Relay default polarity", "kind": "relay conduction model",
         "connection": {"MOS opto (TLP3412/G3VM/IM06DJR-MOS groups)": "default OPEN, SetOn closes", "G6K-2G-Y mechanical": "default NC (Pin<->BUS blocked), SetOn routes Pin<->BUS"},
         "conclusion": "each relay in a scope chain must carry an explicit intended state; 'not SetOn' is not a valid way to open a G6K",
         "confidence": "derived",
         "evidence": [{"path": "knowledge/hardware/relays.md", "locator": "L33-48 MOS default open; L56-58 G6K default NC", "sha256": sha(ROOT / "knowledge/hardware/relays.md")},
                      {"path": "project/DALI/phase2_singlepoint_output.txt", "locator": "group headers MOS / G6K_Dedicated / G6K_Shared", "sha256": sha(ROOT / "project/DALI/phase2_singlepoint_output.txt")}]},
    ],
    "validation": {
        "engine": proofs_doc["engine"],
        "status": proofs_doc["status"],
        "contracts": proofs_doc["contracts"],
        "counts": proofs_doc["counts"],
        "sixGateStatus": manifest["parser_gate_status"],
        "connectMapRegeneratedByteIdentical": conflicts["regeneratedMapMatchesCommitted"],
        "scopePinCoverage": {"scopePins": len(SCOPE_PINS), "pinsWithAcceptedPaths": len(scope_paths["paths"]),
                             "acceptedPathsInScope": sum(len(v) for v in scope_paths["paths"].values()),
                             "kelvinPairsInScope": len(scope_paths["kelvinPairs"]),
                             "rejectedPathsInScope": len(scope_paths["rejectedForScopePins"])},
        "runs": [
            {"command": "python scripts/schematic_parse/scripts/csv_schematic_adapter_v2.py --out-dir team/artifacts/acceptance-20260916-dali10/schematic-validation",
             "exitCode": 0, "evidence": "parser gate: PASS (exit=0); overall status: PASS (exit=0)",
             "log": "team/artifacts/acceptance-20260916-dali10/schematic-validation/adapter-run.log",
             "manifest": "team/artifacts/acceptance-20260916-dali10/schematic-validation/validation_manifest.json.txt",
             "produced": ["project/DALI/CSV_CONNECTIVITY.NET (byte-identical to before the run)",
                          "project/DALI/SCH-Connect-Map.txt (byte-identical to before the run)",
                          "project/DALI/Component-Statistic.txt (byte-identical to before the run)"]},
            {"command": "python scripts/schematic_parse/scripts/csv_pathproof_v2.py --out-dir team/artifacts/acceptance-20260916-dali10/schematic-validation",
             "exitCode": 0, "evidence": pp_validation.replace("\n", "; "),
             "log": "team/artifacts/acceptance-20260916-dali10/schematic-validation/pathproof-run.log",
             "summary": "team/artifacts/acceptance-20260916-dali10/schematic-validation/PATHPROOF-VALIDATION.txt"},
        ],
        "inputHashes": {
            "csvPlaintextSha256": manifest["input"]["sha256"],
            "note": "Dali-SCH.csv is DLP-transparent-encrypted: only a whitelisted process such as python reads plaintext. PowerShell Get-FileHash returns a ciphertext hash and must not be used as evidence for this file.",
        },
        "regeneratedIntermediateHashes": {
            "project/DALI/CSV_CONNECTIVITY.NET": sha(ROOT / "project/DALI/CSV_CONNECTIVITY.NET"),
            "project/DALI/SCH-Connect-Map.txt": sha(ROOT / "project/DALI/SCH-Connect-Map.txt"),
            "project/DALI/Component-Statistic.txt": sha(ROOT / "project/DALI/Component-Statistic.txt"),
        },
        "evidenceStability": {
            "note": ("Every evidence sha256 in this IR was correct at build time. Two classes of source are "
                     "NOT owned by this task and may advance afterwards: the DFT artefacts (dft-ir.json, owned "
                     "by dft-expert, actively regenerated during this run) and the regenerated DALI "
                     "intermediates. If a recorded hash no longer matches, re-verify the cited locator's content "
                     "before trusting the citation; do not re-hash silently."),
            "pinnedAt": "run acceptance-20260916-dali10 build of schematic-ir.json",
            "mutableEvidence": [
                {"path": "team/artifacts/acceptance-20260916-dali10/dft-ir.json",
                 "owner": "dft-expert", "sha256": sha(ROOT / "team/artifacts/acceptance-20260916-dali10/dft-ir.json"),
                 "verifiedClaims": ["TM600 channels[0].pins = ['PMID (High)','SW (Low)']",
                                    "TM601 channels[0].pins = ['SW','PGND'] ruled pair sw2pgnd",
                                    "conflicts C-01 and C-05 present; PMID/VBUS resolved to 5V from reg_config"],
                 "checkedBySelfcheck": "selfcheck_schematic_ir.py reports dft-ir.json mismatches when this file "
                                       "advances past the pin above"},
            ],
            "immutableEvidence": [
                "project/DALI/Dali-SCH.csv", "project/DALI/SCH-Connect-Map.txt",
                "project/DALI/Component-Statistic.txt", "project/DALI/phase2_singlepoint_output.txt",
                "D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h",
                "D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h",
                "team/artifacts/acceptance-20260916-dali10/schematic-validation/* (produced by this task)",
            ],
        },
    },
    "unresolvedTopology": unresolved,
    "openQuestions": open_questions,
}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "schematic-ir.json").write_text(json.dumps(ir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT / "schematic-ir.json")
print("paths:", len(paths), "hazards:", len(hazards), "components:", len(components),
      "relays:", len(relays), "nets:", len(ir["nets"]), "dutPins:", len(dut_pins))
