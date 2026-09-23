"""TM108 test-method contract generator (runId=tm108-v2-trial, task=t5).

Writes (into the same directory):
  tm108-test-method-contract.md / .json
  bst-sw-phase-check.md

Inputs are read-only:
  team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.json  (signed boundary, t4)
No project file is read or written by this script.
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "tm108-v2-trial"
STRAT_JSON = os.path.join(HERE, "..", "strategy", "tm108-resource-config-contract.json")
STRAT_MD = os.path.join(HERE, "..", "strategy", "tm108-resource-config-contract.md")
DFT_MD = os.path.join(HERE, "..", "dft", "dft-fact-audit.md")
SCH_MD = os.path.join(HERE, "..", "schematic", "schematic-fact-audit.md")
SCH_JSON = os.path.join(HERE, "..", "schematic", "tm108-paths-proofs.json")

EXPECTED = {
    "tm108-resource-config-contract.md": "6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4",
    "tm108-resource-config-contract.json": "FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9",
    "dft-fact-audit.md": "AEC7FD74A01314B856009104C721F93B11FE9490B27C0673DEA6E3F385274029",
    "schematic-fact-audit.md": "1F5996B21AE84E2E80688C88015CFEA2DD9E35F1075858C72970711A35CEF1B8",
}


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rel(path):
    p = os.path.relpath(os.path.abspath(path), os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
    return p.replace("\\", "/")


def w(name, text):
    with io.open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return name


# ---------------------------------------------------------------- hashes / boundary check
strat = json.load(io.open(STRAT_JSON, "r", encoding="utf-8"))
HASHES = {
    "strategy/tm108-resource-config-contract.md": sha256(STRAT_MD),
    "strategy/tm108-resource-config-contract.json": sha256(STRAT_JSON),
    "dft/dft-fact-audit.md": sha256(DFT_MD),
    "schematic/schematic-fact-audit.md": sha256(SCH_MD),
    "schematic/tm108-paths-proofs.json": sha256(SCH_JSON),
}
for k, v in EXPECTED.items():
    got = HASHES["strategy/" + k] if k.startswith("tm108-resource") else (
        HASHES["dft/" + k] if k.startswith("dft") else HASHES["schematic/" + k])
    assert got.upper() == v, (k, got, v)

RGS = {g["id"]: g for g in strat["relayGroups"]}
RA = {r["id"]: r for r in strat["resourceAllocation"]}

# ---------------------------------------------------------------- method evidence
method_evidence = [
    {
        "source": "team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md / .json (signed t4 resource/config contract)",
        "locator": "contract md :27-30, :92-121, :181-252, :256-267, :403-420; contract json resourceAllocation[] / relayGroups[] / registerDelta[] / openItems[]",
        "applicability": "direct",
        "reason": "This is the signed resource/configuration boundary for TM108 and the only authority for source tables, channels, closure sets, functional relays, isolation requirements and the register delta. Every phase below cites it; nothing outside it is added.",
        "dimensions": {"parameterType": "n/a (boundary source)", "topology": "n/a", "criticalRelativeVoltages": "n/a", "dftOperatingPoint": "n/a", "sourceWorkingMode": "n/a", "resourceBoundary": "direct - the boundary itself"},
    },
    {
        "source": "team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md (t2 DFT fact audit)",
        "locator": ":138-143 (parameters), :145-168 (Power/Dynamic), :170-179 (Check), :204-216 (Limits), :218-231 (register), :233-244 (timing), :262-276 (F1-F6), :318-337 (P1-P10)",
        "applicability": "direct",
        "reason": "Current-project fact layer: it fixes what the DFT actually wrote (vset expressions, check pin name, limit text, register directive, delay) and keeps F1-F6 as registered conflicts. Used for the operating point and for the pending markers.",
        "dimensions": {"parameterType": "UVLO/PRST threshold, single observable", "topology": "single-ended input scan + digital observation", "criticalRelativeVoltages": "limit text only (4.4 V / 4.15 V / hys 0.35 V), F1 open", "dftOperatingPoint": "direct", "sourceWorkingMode": "n/a", "resourceBoundary": "n/a"},
    },
    {
        "source": "team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md + tm108-paths-proofs.txt/.json (t3 schematic fact audit)",
        "locator": "schematic-fact-audit.md :98-203, :205-257, :261-274, :301-315; tm108-paths-proofs.txt per-terminal chains",
        "applicability": "partial",
        "reason": "Supplies the physical node facts used by the actual-node and BST/SW derivations (net names, contact numbers, default-conducting tokens, mutual exclusions). Partial because it proves that DTEST0 has 0 hits (:94, :172, :270) - i.e. the observation endpoint of this method is NOT physically resolved there, so the audit can corroborate node potentials but cannot settle the endpoint.",
        "dimensions": {"parameterType": "n/a", "topology": "direct for the node facts", "criticalRelativeVoltages": "n/a", "dftOperatingPoint": "n/a", "sourceWorkingMode": "n/a", "resourceBoundary": "partial: no DTEST0 evidence exists in the three-artifact set"},
    },
    {
        "source": "knowledge/references/L3-method/UVLO.md",
        "locator": ":5-19",
        "applicability": "direct",
        "reason": "Parameter-type method for a PRST/UVLO threshold: ramp the pin low->high for the rising threshold, high->low for the falling threshold, Hys = rise - fall in mV, open-drain indication needs a pull-up. Parameter type and topology match TM108 (PRST by name at :17).",
        "dimensions": {"parameterType": "direct (UVLO/PRST family)", "topology": "direct (supply/input ramp + monitor toggle)", "criticalRelativeVoltages": "not stated by this source", "dftOperatingPoint": "direct", "sourceWorkingMode": "not stated", "resourceBoundary": "not stated"},
    },
    {
        "source": "knowledge/references/L1-chip/UVLO.md",
        "locator": ":14-29",
        "applicability": "partial",
        "reason": "Gives the mechanism (hysteresis, indicator pin is either POWER GOOD or a DTEST pin, open-drain needs a pull-up per FR-002) and lists PRST as an equivalent threshold class. Partial because it is generic chip knowledge: it does not fix this part's indicator pin identity, so it cannot close OI-T4-01.",
        "dimensions": {"parameterType": "partial (generic UVLO/PRST family)", "topology": "partial (indicator pin role only)", "criticalRelativeVoltages": "general hysteresis rationale only", "dftOperatingPoint": "n/a", "sourceWorkingMode": "n/a", "resourceBoundary": "n/a"},
    },
    {
        "source": "knowledge/references/L3-method/voltage-threshold-ate.md",
        "locator": ":1-34 (method A)",
        "applicability": "partial",
        "reason": "Method A of this exact item family ('representative item VAC1_PRST' at :11) fixes the trigger-edge convention (rising ramp -> capture the falling edge; falling ramp -> capture the rising edge) and the Hys formula (:30). Partial because its own prerequisite line :5 states the observation-pin alias 'DTEST0->nQON', and the signed contract forbids treating that alias as fact (OI-T4-01); the alias is therefore carried as pending, not adopted.",
        "dimensions": {"parameterType": "direct (PRST)", "topology": "direct (single-ended input scan)", "criticalRelativeVoltages": "trigger-edge convention only", "dftOperatingPoint": "direct", "sourceWorkingMode": "not stated", "resourceBoundary": "n/a"},
    },
    {
        "source": "knowledge/standards/toggle-awg-rules.md",
        "locator": ":12-34",
        "applicability": "direct",
        "reason": "Two-segment ramp => exactly three parameters <base>_Rise/_Fall/_Hys with Hys = Rise - Fall (:14), ramp-call counting rule (:18-26), trigger direction (:28-30), and the mandatory toggle observation relay requirement (:32-34). TM108's DFT has two vset steps, so the 3-parameter contract applies. The 'DTEST0/nQON inverted' wording at :30 is carried as pending (OI-T4-01).",
        "dimensions": {"parameterType": "direct (Toggle/AWG threshold)", "topology": "direct", "criticalRelativeVoltages": "trigger level is method-side, not fixed here", "dftOperatingPoint": "direct", "sourceWorkingMode": "direct (voltage ramp + capture)", "resourceBoundary": "constrains relays (pull-up) but does not name them"},
    },
    {
        "source": "knowledge/standards/functions-registry.md",
        "locator": ":23-31 (shared ramp semantics), :43 (rampv_capv)",
        "applicability": "direct",
        "reason": "Fixes the semantics of the measurement primitive this method must use: step = sample count (not a voltage increment), interval >= 10, trig_level = trigger threshold, result = the ramp value at the trigger point. That is what makes the measurement plan executable and reviewable.",
        "dimensions": {"parameterType": "n/a", "topology": "n/a", "criticalRelativeVoltages": "n/a", "dftOperatingPoint": "n/a", "sourceWorkingMode": "direct (ramp + capture primitive)", "resourceBoundary": "n/a"},
    },
    {
        "source": "knowledge/standards/rules-registry.md",
        "locator": ":32 (R-PON), :33 (R-POFF), :37 (R-LOG), :38 (R-HYS), :39 (R-SETON), :44 (R-BST-SW)",
        "applicability": "partial",
        "reason": "R-PON/R-POFF/R-HYS/R-LOG/R-SETON apply directly and are cited per phase and in the power-down/log plans. R-BST-SW (:44) is a specialized golden constraint scoped to the Current-Threshold/ZCD item class (its own enforcing script derives the target function from a topology fingerprint) - the TM108 item family is not that class, so the rule is used as the formulation of the 0 <= BST-SW <= 5 V constraint only, not as a topology mandate.",
        "dimensions": {"parameterType": "partial", "topology": "R-BST-SW is partial (different class)", "criticalRelativeVoltages": "direct (formulation of the BST-SW window)", "dftOperatingPoint": "n/a", "sourceWorkingMode": "partial", "resourceBoundary": "n/a"},
    },
    {
        "source": "knowledge/standards/relay-checklist.md",
        "locator": ":25-42 (Cap2 rule and its per-PIN exceptions), :71-75 (closure order and explicit SetOn(-1))",
        "applicability": "direct",
        "reason": "Basis for two method decisions: the VBAT cap gate stays closed for a powered rail, and the scanned-input cap gate must be removed (per-PIN exception) - exactly the asymmetry between K13 and K21 that the signed contract requires.",
        "dimensions": {"parameterType": "n/a", "topology": "direct", "criticalRelativeVoltages": "n/a", "dftOperatingPoint": "direct", "sourceWorkingMode": "n/a", "resourceBoundary": "direct (functional relay rule)"},
    },
    {
        "source": "knowledge/references/L4-Golden-code/UVLO.cpp / UVLO.md / toggle-template.cpp (the param_type_index :42 four-pack case for PRST threshold AWG)",
        "locator": "knowledge/references/param_type_index.md:42 and :45 name the case; the code file itself is NOT present in this workspace checkout",
        "applicability": "unavailable",
        "reason": "The PRST threshold-AWG golden code is the nearest same-parameter-type case, but its file is not present under knowledge/references/L4-Golden-code/ in this checkout (only UVLO.md is), so it was not read and cannot be graded. No conclusion in this contract depends on it.",
        "dimensions": {"parameterType": "would be direct", "topology": "unassessed", "criticalRelativeVoltages": "unassessed", "dftOperatingPoint": "unassessed", "sourceWorkingMode": "unassessed", "resourceBoundary": "unassessed"},
    },
    {
        "source": "team/artifacts/acceptance-20260916-dali10/setup-contract.json (frozen Setup baseline, read-only)",
        "locator": ":130-160 (ACM200 group and use), :5666-5671 (per-TM TM108 powerSequenceDelta), :5675-5682 (measurePlan), :5683-5719 (limits + BD-04 threshold ruling), :3905-3964 (globalInitialization), :8150-8179 (safetyInvariants, incl. :8156 PIN-attached relays, :8157 site-joint relays, :8161 E006 BST wording, :4162 unified RELAY_OFF ranges)",
        "applicability": "partial",
        "reason": "Corroborates the method (per-TM power sequence, site delay, unified off-range table, ACM200 capability +-200 mA, the three-step power-down) and supplies the differential-window wording recorded for BST. Partial, not direct: Setup is frozen and does not decide this TM's method (ROLE_ROUTING :7), and its own open item exists for the TM108 delta (OI-T4-16). Where it and the signed contract differ on an explicit relay state (K13), the difference is returned to strategy as RT-1 instead of being decided here.",
        "dimensions": {"parameterType": "n/a", "topology": "n/a", "criticalRelativeVoltages": "E006 wording is the only BST-SW statement in the baseline", "dftOperatingPoint": "n/a", "sourceWorkingMode": "direct for ACM200/FXVIe_PLUS capability", "resourceBoundary": "partial (read-only baseline)"},
    },
    {
        "source": "team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt (existing implemented TM108 function, lines 390-468)",
        "locator": ":390-468",
        "applicability": "partial",
        "reason": "The already-implemented function is the only place where this method's numeric parameters exist today (relay set, delays, 200/20 samples, 1.65 V capture level, ranges, three-step power-down). It is used as corroboration for numbers and as the evidence that these values are not invented - it is NOT an authority: the implemented function embeds the DTEST0==nQON assumption in its comment (:395) which this contract must not adopt, and it is not consistent with the signed contract on K13 (:414). Implementation is a downstream consumer of this contract, so where they differ this contract governs.",
        "dimensions": {"parameterType": "n/a", "topology": "partial (assumes the unresolved endpoint)", "criticalRelativeVoltages": "partial (capture level 1.65 V only)", "dftOperatingPoint": "n/a", "sourceWorkingMode": "direct (ramp + capture + ranges)", "resourceBoundary": "partial: differs from the signed contract on K13"},
    },
]

# ---------------------------------------------------------------- phase model
# Relay base state: exactly the state text of the signed contract, partitioned so
# every phase can point at an explicit set (no relay is left implicit).
CLOSED = [13, 65]
CLOSED_BY_NATURE = [17]
NOT_ACTUATED = [8, 18, 19, 64, 88, 89]
KEEP_OPEN = [14, 15, 16, 21, 38, 39, 40, 70, 82, 86, 87, 90, 92, 130, 141, 142]
CONTROLLED_UNASSIGNED = [7, 61, 57, 48, 76, 110, 109, 41, 42, 43]

BSTSW_NOT_DETERMINABLE = (
    "定点补证 - not determinable inside the signed boundary. BST and SW are not TM108 endpoints "
    "(contract md :94-101), no source table is allocated to them (contract md :133-139), and no relay of "
    "G1-G4 has a required state on them (contract md :192-252). BST_actual and SW_actual are therefore "
    "DUT-internal states of a switching stage that the DFT does not commit and that the register delta "
    "does not enable; SW must NOT be defaulted to 0 V (architecture :212-224)."
)


def phase(pid, name, stage, prereq, rg, resource_state, reg_act, nodes, diff, setpoint, ramp, delay, exitc):
    return {
        "phase": pid,
        "name": name,
        "stage": stage,
        "prerequisite": prereq,
        "relayGroup": rg,
        "resourceState": resource_state,
        "registerActivation": reg_act,
        "actualNodeVoltages": nodes,
        "differentialChecks": diff,
        "setpoint": setpoint,
        "ramp": ramp,
        "delay": delay,
        "exitCondition": exitc,
    }


VAC_NODES = [
    "VAC1_F (net NetCap1_VAC1_S1_1): driven by the allocated ramp source VAC123_AMUX_ACM, channel S5_0, force port S5_ACM200_FH0 (contract json resourceAllocation RA-1); the value is whatever that source is set to at that instant (no series element in the path - K18/K19 are default-conducting contacts only).",
    "VAC1_S (net NetK19_VAC2_S1_7): same physical node read back on the source's own sense port S5_ACM200_SH0 (RA-2); the node fact that F and S are two different nets is recorded in schematic-fact-audit.md :127 and tm108-paths-proofs.txt:71.",
]

VBAT_NODES = [
    "VBAT_F (net NetCap1_VBAT_S1_1): driven by VBAT_PD3_FXVI, channel S3_5, force port S3_FXVIe_PLUS_FH5 through the default-conducting K8 contact (RA-3).",
    "VBAT_S (net NetK8_PD3_S1_2): the K8 pin-2 node, i.e. the PD3 side of the selector (RA-4 and schematic-fact-audit.md :151). Because K8 stays un-actuated, the PD3 branch is never reached (contract md :295-296).",
]

BSTSW_NODES = [
    "BST / SW are not on any TM108 path: the TM108 terminal set is VAC1, VBAT, nQON (observation candidate), AGND (contract md :94-101).",
    "BST and SW do have board routes and a coupling element, but every one of them needs relays that the signed contract keeps un-actuated or does not assign: BST via S5_ACM200_FH5 -> K48+K76 (:83-91) with the coexisting K110 / K109+K110 variants (:16-21), the SW node route via K61_SW (setup-contract.json:144), and the BST-SW 220nF bootstrap cap gate K57 (project/DALI/SCH-Connect-Map.txt:904).",
    "K64_HG1 - the only relay on any TM108 group that touches the gate/high-side domain - must stay un-actuated (contract md :220-222, :298): the nQON side of K64 is pin 6->pin 7 and the HG1 side needs K64 ON. The relay that would couple the tester into the HG1 node is therefore open by contract.",
    "K57_CAP_BST_SW is listed in the baseline global initialization as one of the cap gates an item may close (setup-contract.json:3941) while the signed contract names neither its closure nor its keep-open state. It is the only element by which this boundary could touch the BST-SW pair, so two independent reasons apply: (a) the state is not in the signed closure set (so it is not closed by this method), and (b) the ambiguity itself is returned to strategy as RT-2.",
]

TAIL_BSTSW = (
    "BST_actual: not derivable - no allocated source, no driven node, no closed contact. "
    "SW_actual: not derivable - see the SW_actual derivation note in bst-sw-phase-check.md; the low-side/high-side "
    "commitment of the switching stage is not part of the DFT intent, the register delta or the closure set, and "
    "SW is explicitly NOT taken as 0 V. 0 V <= BST_actual - SW_actual <= 5 V: NOT PROVEN for this phase -> registered "
    "as 定点补证 pending OI-T5-02 (closing evidence: a DFT-side statement that TM108 leaves the switching stage "
    "inactive, plus the BST/SW source allocation and relay state that a BST-SW test would require)."
)

phases = [
    phase(
        "P0", "Pre-state: no active closure, sources not yet enabled", "connect / pre-flight",
        "Task accepted; signed resource/config contract hash verified (this file's Boundary + Hash Ledger section). At entry the tester is in the project default relay state: no relay of this item is actuated.",
        "none (G1-G4 not yet entered)",
        {"closureSetActuated": [], "relaysInExplicitState": {"closed": CLOSED + CLOSED_BY_NATURE, "notActuated": NOT_ACTUATED, "keepOpen": KEEP_OPEN, "notAssignedByContract": CONTROLLED_UNASSIGNED}, "sourcesEnabled": "none"},
        "none (no register write yet)",
        ["VAC1_F: high-impedance / not driven (no source enabled; the path contact K18/K19 is default-conducting but its far end is the source, RA-1).",
         "VBAT_F: not driven (VBAT_PD3_FXVI not enabled).",
         "observation node: no pull-up yet (K65 open), so the candidate observation node is floating in this phase."] + BSTSW_NODES,
        ["Pre-flight differential check on the ramp pair: VAC1_F and VAC1_S are two nets of the same pin (schematic-fact-audit.md :127) - no differential stimulus is planned, so no differential envelope has to be held here.",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE, TAIL_BSTSW],
        "none (no source is set in this phase); the DFT power intent that will be applied next is vset[vbat,3,100e-6,0] (dft-fact-audit.md :152) with the CSV counterpart vset[vbat,4.2,...] kept open as F4 (dft-fact-audit.md :271).",
        "none",
        "none (R-SETON requires the Connect block to start with cbite.SetOn(...) + delay_ms(3) at the start of P1, rules-registry.md :39)",
        "Every planned relay has an explicit state (closed / not-actuated / keep-open) and every keep-open relay is at its MOS-open default. Any deviation aborts the item before any source is enabled.",
    ),
    phase(
        "P1", "Closure of the signed functional relays", "connect",
        "P0 passed with every relay in an explicit state (setup-contract.json:3908).",
        "G1+G2+G3 entered together; the contract states no relay has a direction- or phase-dependent required state (G2 note in contract json relayGroups[1]), so one closure set covers the whole item and no time-division is triggered (contract md :286).",
        {"closureSetActuated": CLOSED, "functionalRelayRoles": {"13": "VBAT stabiliser cap gate for a powered rail (relay-checklist.md :27-37; project/DALI/SCH-Connect-Map.txt:914)", "65": "5 V pull-up for the open-drain observation node (project/DALI/SCH-Connect-Map.txt:891; parameter-type method UVLO.md :19-20)"}, "pathRelayState": "K17 is required to be in the closed state on the VAC1 branch (contract md :199, :245-246) WITHOUT this method claiming how it got there - OI-T4-04 is still open, so no actuation call for K17 is written by this contract (ate-implementer decides the call form under OI-T4-04).", "defaultConductingReliedUpon": NOT_ACTUATED, "keepOpen": KEEP_OPEN},
        "none",
        ["VAC1_F / VAC1_S: still undriven (source enabled in P2); K21_VAC_Cap stays open so no cap is across the scanned input (contract md :200; K21 source: project/DALI/SCH-Connect-Map.txt:913).",
         "VBAT_F / VBAT_S: still undriven; K13 now closed, so the 4.7 uF VBAT stabiliser (project/DALI/SCH-Connect-Map.txt:914) is connected to a rail that will be powered in P2.",
         "observation node (candidate nQON_F, net NetK64_HG1_S1_7): now pulled up through K65; the pull-up is fixed at 5 V (project/DALI/SCH-Connect-Map.txt:891) and the node is open-drain, so with the DUT's internal indicator off the node sits near 5 V - which is what makes the 1.65 V capture level (testcpp-blocks.txt:435) a valid mid-scale logic threshold.",
         "K64 stays un-actuated, so HG1 is never connected to the tester (contract md :298; schematic-fact-audit.md :170)."] + BSTSW_NODES,
        ["Toggle observation relay requirement (toggle-awg-rules.md :32-34) is satisfied functionally: pull-up K65 + the default-conducting K64 observation contact; the pull-up is a functional relay taken from the signed contract, not added here.",
         "Isolation check: K21 open (no cap on the scanned input), K14 open (no VAC1-to-AGND short), K70/K87/K90/K82 open (CH0 High branch not selected), K141/K142 open (no FPVIe BUS bridge), K86/K130 open (no force/sense bridge) - all of these are contract isolationRequirements (contract md :201, :222).",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE, TAIL_BSTSW],
        "No source value is set in this phase; K13/K65 are functional closures whose only numeric content is the 5 V pull rail of the candidate observation node (project/DALI/SCH-Connect-Map.txt:891).",
        "none",
        "contract md :225-226 and setup-contract.json:5667 fix the site delay after the closure: delay_ms(3) (the baseline states 'delay 3 ms'), applied before VBAT is enabled.",
        "Closure set equals {13,65} with K17 in the closed state and every keep-open relay un-actuated; the site delay has elapsed.",
    ),
    phase(
        "P2", "VBAT static supply on (rest of the item is idle)", "power-on",
        "P1 closure set confirmed and the 3 ms site delay elapsed.",
        "G3 (static supply half; the observation half of G3 is already active from P1 and stays active).",
        {"closureSetActuated": CLOSED, "sources": {"VBAT": "VBAT_PD3_FXVI, channel S3_5, force FV=the DFT setpoint, range FXVIe_PLUS_10V, current limit FXVIe_PLUS_100MA (RA-3; the range and limit pair is the existing implemented call at testcpp-blocks.txt:419 and the RELAY_OFF-unified family at setup-contract.json:4162)"}},
        "none",
        ["VBAT_F: driven to the DFT setpoint; the authoritative artifact-layer value is 3 V (dft-fact-audit.md :151, tm108.sv body at regconfig-scope.json:35) and the CSV layer states 4.2 V (dft-fact-audit.md :153) - F4 is carried, and the method applies the DFT-intent value 3 V as the single setpoint to code while recording that the conflict is unresolved.",
         "VBAT_S: reads the K8 pin-2 node (schematic-fact-audit.md :151).",
         "VAC1_F / VAC1_S: still 0 V intent - no stimulus is applied until P4; the ramp primitive starts from its own start point (functions-registry.md :31).",
         "observation node: pulled up (P1) - the DUT's indicator state in this phase is exactly the quantity the test measures later, and its identity is unresolved (OI-T4-01)."] + BSTSW_NODES,
        ["Rail/return check: the FXVIe_PLUS and ACM200 low ends are grouped to AGND_F (project/DALI/SCH-Connect-Map.txt:801, :804), which is how the single-ended force closes its loop; AGND is a reference only and no source is allocated to it (contract md :99, :186).",
         "No differential pair is energised in this phase.",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE, TAIL_BSTSW],
        "VBAT setpoint: 3 V (artifact layer) with the 4.2 V CSV counterpart registered, not averaged (dft-fact-audit.md :151-153, :271; contract json openItems OI-T4-12). Ramp time of the DFT expression: 100e-6 s (dft-fact-audit.md :152).",
        "The DFT expression for the rail is a ramp-type command vset[vbat,3,100e-6,0]; the method implements it as the source's own ramp/set behaviour with the 100e-6 s ramp time from the DFT expression, and does not insert a second ramp.",
        "delay_ms(1) after the rail is enabled - the value used by the implemented function (testcpp-blocks.txt:420) and consistent with the baseline per-TM sequence (setup-contract.json:5668); it is a method-side hold time, not a DFT number.",
        "Rail is at its setpoint and no register has been written yet.",
    ),
    phase(
        "P3", "Register activation of the observation mux (staircase: testmode key then the delta)", "register configuration",
        "P2 complete: rail at setpoint, closure set unchanged.",
        "G1+G2+G3 unchanged (no relay action in this phase).",
        {"closureSetActuated": CLOSED, "note": "No relay changes in this phase; the closure set from P1 remains valid."},
        "Step 1: entertestmode() - mandatory precondition before any register write (contract md :260; register rule knowledge/standards/register-config.md:12-22; DFT provenance en_tm[] at dft-fact-audit.md :227). Step 2: the delta pair DMUX_EN=1 and DMUX_SEL=22 written together as one field directive (contract md :261-263; dft-fact-audit.md :222-224; .sv body regconfig-scope.json:35). Step 3: none.",
        ["VAC1_F / VAC1_S: 0 V intent held (the mux writes do not touch the input pin).",
         "VBAT_F: setpoint held.",
         "observation node: the mux selection is what makes the DUT's indicator visible on this node AT ALL - and because DMUX_SEL's value is contested (22 vs 23, F2) and the observed endpoint's identity is unproven (OI-T4-01), the following decisions are marked PENDING-OI-T4-01, not assumed: (a) that writing DMUX_SEL=22 connects the VAC1 PRST indicator to the observed node, (b) that the mux output is inverted at that node, (c) the CSV-side register counterpart EN_DTEST0/DTEST0_MUX=1/23 which the contract explicitly does not apply (contract md :264)."] + BSTSW_NODES,
        ["Register staircase order is a hard rule: entertestmode precedes the writes (R-PON family; contract md :260); writing the two DMUX fields as one directive follows the DFT's own form field[(DMUX_EN,1),(DMUX_SEL,22)] (dft-fact-audit.md :223).",
         "The observation-dependent decisions in this phase are pending OI-T4-01 and must not be treated as resolved by any downstream stage.",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE, TAIL_BSTSW],
        "No new numeric setpoint: DMUX_EN=1 and DMUX_SEL=22 are the signed contract's values (contract md :261-262), and the contested alternatives (0x55=0x97 i.e. 23; the EN_DTEST0/DTEST0_MUX pair) are recorded, not used (dft-fact-audit.md :230).",
        "none (register writes are discrete actions; no ramp)",
        "No dedicated delay is specified by the DFT for the register staircase (the DFT's only delay is delay[1e-3] applied at the end of the sequence, dft-fact-audit.md :237); the method therefore does not insert an invented register settle delay - if implementation-side settling is required it must come back as a need to this owner.",
        "Testmode is entered and the one field directive has been issued; the observation-dependent decisions of this phase are still flagged pending.",
    ),
    phase(
        "P4", "Rising sweep of VAC1 with capture during the sweep", "measure (rising segment)",
        "P3 complete (testmode + delta written); closure set from P1 intact.",
        "G1 (contract json relayGroups[0]); G2 closes the same set (relayGroups[1]).",
        {"closureSetActuated": ["none - G1/G2 actuate no relay (closureSetActuatedThisStage=[])"], "sources": {"VAC1": "VAC123_AMUX_ACM channel S5_0 as the ramp source; range ACM200_20V and limit ACM200_100MA (range derived from the DFT's 10 V scan end by the rule 'range >= 2x the setpoint, smallest satisfying step' (R-PON, rules-registry.md :32) - 20 V; the ACM200 family limit is +-200 mA (setup-contract.json:134) so 100 mA is within capability), and the observation source NQON_HG1_ACM channel S5_9 with range ACM200_10V and limit ACM200_10UA (RA-5, CANDIDATE ONLY)", "VBAT": "static supply held from P2"}},
        "active from P3 (DMUX_EN=1, DMUX_SEL=22) - the activation is what the phase depends on, and it is pending OI-T4-01.",
        ["VAC1_F: swept from the ramp start point to the ramp end point; the ramp geometry itself is a registered conflict (F5: 0->10->0 V vs 3~5 V at 1V/ms vs 3.8->4.4->4.1->3.5 V, contract json OI-T4-13) and is therefore marked PENDING; the single geometry written into this phase is the artifact/Code2 one (0 V -> 10 V) with the two competitors recorded verbatim.",
         "VAC1_S: the source's own sense port on the same pin - the measurement reference is the source's reading on that node, not an independent Kelvin pair (contract json resourceAllocation RA-2 senseCharacter).",
         "VBAT_F: setpoint held (the ramp source is a different instrument and a disjoint chain - contract md :300).",
         "observation node: toggles when the VAC1 threshold is crossed; the tabulated thresholds in this method count on the indicator's polarity, which is pending (OI-T4-01) - see differentialChecks."] + BSTSW_NODES,
        ["Trigger polarity (pending OI-T4-01): the parameter-type method says the rising sweep must capture the FALLING edge of the indication (voltage-threshold-ate.md :26-32; toggle-awg-rules.md :28-30), i.e. TRIG_FALLING with a 1.65 V level (level and mode provenance: existing implemented call testcpp-blocks.txt:433-435; the level is a mid-scale logic threshold for the 5 V pull-up of project/DALI/SCH-Connect-Map.txt:891). This is only correct if the indicator presented on the observed node is inverted as the knowledge base states; that premise is DTEST0==nQON-dependent and is marked PENDING, so neither the polarity nor the level may be treated as settled.",
         "Anti-short: the VAC1 chain contains no other DUT pin (every accepted VAC1 proof has terminal_stop=true, contract md :318; schematic-fact-audit.md :85).",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE, TAIL_BSTSW],
        "Ramp start/end: 0 V -> 10 V per the artifact layer (dft-fact-audit.md :163, :272) with the CSV layer's 3.8->4.4->4.1->3.5 V staircase and the Notes' 3~5 V at 1V/ms recorded as unresolved (F5/F6). Capture level 1.65 V (testcpp-blocks.txt:435). Range 20 V and limits 100 mA / 10 uA as above.",
        "Ramp time: 1e-3 s for the DFT vset step (dft-fact-audit.md :241; regconfig-scope.json:35). Geometric ramp parameters for the primitive: 200 samples at 20 us per sample = 4 ms of sweep (functions-registry.md :27-28 for the semantics; the 200/20 values are the existing implemented call, testcpp-blocks.txt:435 - a method-side choice and not a DFT number).",
        "No separate delay inside the sweep; the hold before the sweep is the P3/P2 chain. Post-sweep the DFT's only delay is 1e-3 s at the end of the sequence (dft-fact-audit.md :237).",
        "The trigger fired at a captured source voltage (a result exists for this segment) or the sweep reached its end point without a trigger - in the latter case the segment fails its own completeness condition and the failure context of the log plan applies.",
    ),
    phase(
        "P5", "Hold at the sweep end before the falling segment", "stimulus endpoint / turn-around",
        "P4 exited with a captured rise value or an explicit no-trigger record.",
        "G2 entered; the closure set is unchanged from G1 (contract md :205-211).",
        {"closureSetActuated": ["none - G2 is the same closure set as G1"], "sources": {"VAC1": "ramp source held at the 10 V end point (same range/limit as P4)", "VBAT": "held"}},
        "active (unchanged, pending OI-T4-01)",
        ["VAC1_F / VAC1_S: at the sweep end point (10 V nominal) - the only phase in which the scanned pin is held at an extreme before the reverse sweep, which is why the turn-around order is written explicitly: the falling segment must start from a settled value and must not include a relay action (K21 stays open throughout: project/DALI/SCH-Connect-Map.txt:913).",
         "VBAT_F: setpoint held.",
         "observation node: the indicator is in its post-threshold state; the state's identity is pending (OI-T4-01)."] + BSTSW_NODES,
        ["Turn-around differential rule: nothing in this method requires a differential pair; the two nets VAC1_F/VAC1_S belong to the same pin and are never driven as a differential stimulus (schematic-fact-audit.md :127).",
         "Reversal ordering: the same source is used for both segments (RA-1/RA-2) so no source hand-off and no series-relay switch occurs at the turn-around - this is what keeps the closure set identical in G1 and G2.",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE, TAIL_BSTSW],
        "Held value: the falling segment's start point, i.e. the rising segment's end point (10 V per the artifact layer; F5 open).",
        "none in this phase (the ramp belongs to P4 and P6).",
        "Method-side settle before reversal: the DFT delay applied at the end of the sequence is 1e-3 s (dft-fact-audit.md :237); the method does not invent an additional turn-around delay but requires the reversal to be written as a consecutive call to the same primitive (P6) with no relay/range change between the two calls.",
        "The observed value has been stable across the reversal boundary (or the instability is recorded as failure context).",
    ),
    phase(
        "P6", "Falling sweep of VAC1 with capture during the sweep", "measure (falling segment)",
        "P5 complete; closure set and register activation unchanged.",
        "G2 (contract json relayGroups[1]).",
        {"closureSetActuated": ["none - G2 actuates no relay"], "sources": {"VAC1": "ramp source from the end point back down (same range/limit as P4)", "VBAT": "held"}},
        "active (unchanged, pending OI-T4-01)",
        ["VAC1_F: swept downward; this segment is what produces the second of the two thresholds, so its geometry inherits the same unresolved F5 geometry and must be written consistently with P4 (a fall segment that does not mirror the rise segment would fabricate a hysteresis).",
         "VAC1_S: as in P4.",
         "VBAT_F: setpoint held.",
         "observation node: toggles in the opposite direction; polarity pending (OI-T4-01)."] + BSTSW_NODES,
        ["Trigger polarity (pending OI-T4-01): the falling sweep must capture the RISING edge (voltage-threshold-ate.md :26-32; toggle-awg-rules.md :28-30), written as TRIG_RISING with the same 1.65 V level (testcpp-blocks.txt:437-439).",
         "Both segments must be evaluated with the same capture level, otherwise Hys would carry a measurement artefact instead of a device hysteresis.",
         "The result of this phase is the second of exactly three parameters (toggle-awg-rules.md :14) - a single-parameter method would violate the ramp-call-count rule (:18-26).",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE, TAIL_BSTSW],
        "Ramp start/end: 10 V -> 0 V per the artifact layer (dft-fact-audit.md :164) with the CSV layer's staircase recorded as unresolved (F5). Capture level 1.65 V (testcpp-blocks.txt:439).",
        "Ramp time: 1e-3 s for the DFT vset step (dft-fact-audit.md :241); primitive geometry 200 samples x 20 us (testcpp-blocks.txt:439, semantics functions-registry.md :27-28).",
        "No in-sweep delay; the DFT's terminal delay 1e-3 s (dft-fact-audit.md :237) is applied after this phase as part of the completion of the measurement sequence (it is not part of the power-down, whose delay is R-POFF's delay_ms(1)).",
        "Both segments have produced a captured value (or an explicit no-trigger record), and the pair is complete for the Hys computation.",
    ),
    phase(
        "P7", "Bounded settle window then de-energising the stimulus sources", "power-down step 1 of 3",
        "P6 complete; both segment results recorded.",
        "G1/G2/G3 closure set STILL ACTIVE in this step (the relays are not released until the last power-down step) - the contract's relay groups have no power-down variant, and R-POFF's three-step rule keeps the relay state through step 1 (rules-registry.md :33).",
        {"closureSetActuated": CLOSED, "sources": {"VAC1": "FV=0, range/limit held as in P4, relay still ON", "VBAT": "FV=0, range/limit held, relay still ON", "observation": "FV=0, range ACM200_10V, limit ACM200_10UA, relay still ON"}},
        "still active from P3 (no register write is used to disable it; the contract delta has no disable field)",
        ["VAC1_F: driven to 0 V (source zeroing, source relay still ON).",
         "VBAT_F: driven to 0 V while K13 is still closed, i.e. the 4.7 uF stabiliser remains across a collapsing rail - that is the intended discharge path of the rail before the cap gate is released (K13 1 kohm bleed note: setup-contract.json:3943).",
         "observation node: the pull-up source is zeroed; the node's logic state after this step is no longer a defined quantity and is not used by anything downstream.",
         "Chip internal state: the testmode/mux activation is NOT un-written in this step; the delta has no disable field and the contract provides none (returning that need is RT-3)."] + BSTSW_NODES,
        ["De-energising order: the scan/supply stimulus is zeroed BEFORE any contact is opened, which is the anti-short-arcing requirement 'never hot-switch a BUS relay between unequal potentials' (setup-contract.json:8175) and R-POFF's step 1.",
         "All three sources are returned to FV=0 while keeping their ranges, which is R-POFF's 'zero while holding range' step (rules-registry.md :33).",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE + " Note that BST-SW collapse ordering (the R-BST-SW wording 'the FET must stay on while the rails collapse', setup-contract.json:8161) is about items that actually drive BST; it cannot be honoured or violated here because this item drives neither node.",
         TAIL_BSTSW],
        "All setpoints in this step are 0 V (the zeroing order of P7/P8 is the existing implemented sequence at testcpp-blocks.txt:452-454).",
        "downward to 0 V; no ramp is applied in this step (the sweep already ended in P6).",
        "delay_ms(1) between zeroing and the relay release (R-POFF's step 2; rules-registry.md :33; existing implementation testcpp-blocks.txt:455).",
        "Every source reads 0 V intent and the hold has elapsed.",
    ),
    phase(
        "P8", "Release of the signed closure set and the safe end state", "power-down steps 2-3 of 3",
        "P7 completed: all sources zeroed, hold elapsed.",
        "G3 release (functional relays), then G1/G2 are already in their un-actuated state; no relay is left actuated.",
        {"closureSetActuated": [], "finalRelayState": {"13": "released (cap gate opened, which is the sanctioned discharge mechanism per setup-contract.json:3943)", "65": "released", "keepOpen": KEEP_OPEN, "notActuated": NOT_ACTUATED},
         "finalSourceState": "all three channels RELAY_OFF with the unified RELAY_OFF ranges (ACM200_10V/10MA, FXVIe_PLUS_10V/10MA - rules-registry.md :33 and setup-contract.json:4162)"},
        "none (nothing is written and nothing is un-written - the state of the delta fields after the item is out of scope; see RT-3)",
        ["VAC1_F / VAC1_S: source relay open, no drive, no cap (K21 open) -> floating node.",
         "VBAT_F / VBAT_S: source relay open; K13 released, so the rail has no charge path and the cap gate's 1 kohm bleed (setup-contract.json:3943) is the discharge mechanism.",
         "observation node: pull-up released -> floating.",
         "K8/K18/K19/K64 remain un-actuated (never touched by this item) - the same state they had at P0, so the item leaves no selector residue.",
         "K17, if it was closed by the VAC1 branch entry, is left as the VAC1 branch entry state requires; releasing it would re-open the branch and is therefore NOT part of this method (the contract requires the closed state and does not assign the actuation - OI-T4-04)."] + BSTSW_NODES,
        ["Safe end state check: no source is left energised, no cap gate for a powered rail is left closed, every keep-open relay is at its MOS-open default, and no relay of this item remains actuated.",
         "Abnormal exit runs this same two-step sequence (zero -> hold -> release) from the finally path - an aborted item may not leave a charged rail or an energised source (setup-contract.json:8179).",
         "BST/SW: " + BSTSW_NOT_DETERMINABLE + " Closing evidence for the whole item: see OI-T5-02.", TAIL_BSTSW],
        "None (all setpoints 0 V and all channels off).",
        "none",
        "The RELAY_OFF stage carries no additional delay beyond the hold already applied in P7.",
        "All relays released, all sources off with unified ranges, no rail charged, no source energised.",
    ),
]

# ---------------------------------------------------------------- measurement plan
measurement_plan = {
    "parameterSet": ["VAC1_PRST_Rise", "VAC1_PRST_Fall", "VAC1_PRST_Hys"],
    "parameterSetRule": "Two ramp segments (rise + fall) => exactly three parameters <base>_Rise/_Fall/_Hys with Hys = Rise - Fall; a single-parameter plan is forbidden (toggle-awg-rules.md :14, :18-26). The three names already exist in the current implementation, which is corroboration only (dft-fact-audit.md via contract json parameterType.awgParameterContract).",
    "primitive": {
        "name": "test_method.rampv_capv",
        "semantics": "ramp a voltage source and capture the ramp value at the trigger point; step = sample count, interval >= 10, trig_level = trigger threshold, result = ramp voltage at the trigger sample (functions-registry.md :25-31, :43)",
        "legality": "rampv_capv is the volume-ramp/capture member of test_method, which is what an AWG item must use (toggle-awg-rules.md :8-11; test-types.md :71)",
    },
    "segments": [
        {
            "segment": "rise",
            "phase": "P4",
            "force": {"endpoint": "VAC1", "channel": "VAC123_AMUX_ACM S5_0 (force port S5_ACM200_FH0)", "mode": "FV ramp", "vRange": "ACM200_20V", "iRange": "ACM200_100MA", "vRangeBasis": "R-PON range rule: >= 2x the setpoint, smallest satisfying step; the scanned end is 10 V (dft-fact-audit.md :163), so 20 V. The ACM200 family limit is +-200 mA (setup-contract.json:134)"},
            "measure": {"endpoint": "observation candidate (NQON_HG1_ACM S5_9, CANDIDATE ONLY)", "mode": "capture source with FI=0 (cap side of the primitive)", "vRange": "ACM200_10V", "iRange": "ACM200_10UA", "status": "PENDING-OI-T4-01 - the endpoint's identity is unproven; consuming this allocation requires the DTEST0->nQON relation or the nQON side to be established"},
            "sweep": {"start": "0 V", "stop": "10 V", "startStopBasis": "artifact layer / Code2 (dft-fact-audit.md :163); F5 keeps 3~5 V at 1V/ms (Notes) and 3.8->4.4->4.1->3.5 V (CSV) registered and unresolved - PENDING"},
            "step": "200 samples (sample count, not a voltage increment - functions-registry.md :27)",
            "sampleWindow": "interval 20 us per sample => 4 ms of sweep for the segment; the primitive's own requirement is interval >= 10 (functions-registry.md :28)",
            "trigLevel": "1.65 V (mid-scale logic threshold for the 5 V pull-up of project/DALI/SCH-Connect-Map.txt:891; existing implemented level testcpp-blocks.txt:435)",
            "trigMode": "TRIG_FALLING",
            "trigModeBasis": "rising input sweep captures the falling edge of the indication (voltage-threshold-ate.md :26-32; toggle-awg-rules.md :28-30) - PENDING because it assumes the indicator's polarity on the observed node",
            "result": "the ramp source voltage at the trigger point = rising threshold candidate",
        },
        {
            "segment": "fall",
            "phase": "P6",
            "force": {"endpoint": "VAC1", "channel": "VAC123_AMUX_ACM S5_0 (same channel, same source as the rise segment)", "mode": "FV ramp", "vRange": "ACM200_20V", "iRange": "ACM200_100MA", "vRangeBasis": "same as the rise segment: 20 V for a 10 V scan end (R-PON range rule, rules-registry.md :32)"},
            "measure": {"endpoint": "observation candidate (same as rise)", "vRange": "ACM200_10V", "iRange": "ACM200_10UA", "status": "PENDING-OI-T4-01"},
            "sweep": {"start": "10 V", "stop": "0 V", "startStopBasis": "artifact layer / Code2 (dft-fact-audit.md :164); mirrored to the rise segment so that Hys cannot be fabricated by a geometry mismatch - PENDING with F5"},
            "step": "200 samples",
            "sampleWindow": "interval 20 us per sample => 4 ms of sweep for the segment",
            "trigLevel": "1.65 V (identical to the rise segment)",
            "trigMode": "TRIG_RISING",
            "trigModeBasis": "falling input sweep captures the rising edge of the indication (voltage-threshold-ate.md :26-32) - PENDING as above",
            "result": "the ramp source voltage at the trigger point = falling threshold candidate",
        },
    ],
    "calculation": {
        "rise": "VAC1_PRST_Rise = captured ramp voltage of the rise segment (unit V, DFT unit: dft-fact-audit.md :209)",
        "fall": "VAC1_PRST_Fall = captured ramp voltage of the fall segment (unit V)",
        "hys": "VAC1_PRST_Hys = (Rise - Fall) * 1e3 -> unit mV, per R-HYS (rules-registry.md :38) and voltage-threshold-ate.md :30; the x1e3 is applied at the assignment and commented, never applied to the logged identity of Rise/Fall",
        "siteHandling": "Each site is measured and judged independently; results are per-site arrays and Hys is computed per site from that site's own Rise and Fall. No cross-site averaging, interpolation or sharing of captured values is permitted.",
    },
    "limits": {
        "authoritativeText": "rising vth 4.4 V, hys 0.35 V; unit V (dft-fact-audit.md :208-209)"
        ,
        "authoritativeBasis": "artifact/OVERVIEW layer; the frozen baseline's BD-04 threshold ruling accepts the same side (setup-contract.json:5695-5700; ruling scope: that debug-copy acceptance only)",
        "registeredConflictF1": "the DFT CSV layer states 4.15 V for the same rising threshold (dft-fact-audit.md :214, :268); it is registered as OI-T4-09 and is NOT averaged, rewritten or dropped",
        "tolerance": "NOT PUBLISHED in any DFT source (dft-fact-audit.md :215) and the frozen baseline records the same (setup-contract.json:5687)",
        "usage": "This contract therefore states which threshold text is authoritative and that the tolerance does not exist; the pass/fail application (including how a missing tolerance is handled) is a spec-side decision, returned as RT-4 rather than invented here. F1 remains an open ruling item (OI-T4-09) and must not be treated as settled by the implementation or by review.",
        "hysDefinition": "Hys = Rise - Fall (a device property); the DFT limit 'hys 0.35 V' is compared against the computed mV value after the R-HYS conversion.",
    },
    "failureContext": "Any segment that produces no trigger, a trigger at the sweep boundary, or a Hys whose sign is negative must record the failure context of the log plan (phase id, segment, trigger mode, capture level, the actual start/stop/step/interval values used, and which pending item (OI-T4-01 / F5) was in effect) instead of writing a substituted number.",
    "outOfBoundaryNeeds": [
        "The observation endpoint identity and its polarity: returned to strategy/DFT via OI-T4-01; the measurement cannot be finalised until it is closed.",
        "The scan geometry: returned via F5 (OI-T4-13). The resource allocation itself is range-agnostic (contract json OI-T4-13), so only the method's geometry is pending.",
        "A per-segment settle/sampling requirement beyond the DFT's single 1e-3 s delay: would be a method need not derivable from the DFT - returned as RT-5 if a reviewer or implementer requires a number.",
    ],
}

# ---------------------------------------------------------------- power-down plan
power_down_plan = {
    "type": "normal de-energisation (no floating-source pair and no high-current loop is used by this item, so R-POFF's floating and high-current branches do not apply - rules-registry.md :33)",
    "steps": [
        {"order": 1, "action": "Zero the scan source: VAC1 FV=0 while holding its range and leaving its relay ON.", "phase": "P7"},
        {"order": 2, "action": "Zero the supply: VBAT FV=0 while holding its range and leaving its relay ON (K13 still closed, so the 4.7 uF stabiliser discharges through the rail's bleed).", "phase": "P7"},
        {"order": 3, "action": "Zero the observation capture source: FI/FV=0 with range ACM200_10V / ACM200_10UA, relay still ON.", "phase": "P7"},
        {"order": 4, "action": "Hold delay_ms(1).", "phase": "P7"},
        {"order": 5, "action": "Release all three channels with the unified RELAY_OFF ranges (ACM200_10V/10MA, FXVIe_PLUS_10V/10MA).", "phase": "P8"},
        {"order": 6, "action": "Release the functional closures K13 then K65 (cap gate opening is the sanctioned rail discharge), leaving every keep-open relay un-actuated.", "phase": "P8"},
    ],
    "ruleBasis": ["R-POFF normal three-step (zero while holding range -> delay_ms(1) -> RELAY_OFF with unified ranges) - rules-registry.md :33", "unified RELAY_OFF range table - setup-contract.json:4162", "every energised rail needs a discharge plan (cap gate opened + bleed) - setup-contract.json:3943, :8177", "abnormal exit runs the same sequence - setup-contract.json:8179"],
    "actualNodeVoltages": ["after step 4: all three driven nodes are at 0 V intent, VBAT_F is a collapsing rail with K13 still closed", "after step 6: no node of this item is driven; VBAT_F/VBAT_S/VAC1_F/VAC1_S/observation node are floating with all caps released"],
    "differentialChecks": ["no differential pair is energised during the power-down", "the only differential check that applies is the BST/SW constraint, which is NOT PROVEN for both power-down phases (see bst-sw-phase-check.md; closing evidence OI-T5-02)"],
    "safeEndState": "no source energised; no cap gate of a powered rail left closed; every keep-open relay at its MOS-open default; K8/K18/K19/K64 never actuated, so no selector residue; nothing written to the DUT after the power-down (no register de-activation exists in the signed delta).",
}

# ---------------------------------------------------------------- log plan
log_plan = {
    "siteModel": "All logged quantities are per-site; each site is judged with its own values (no shared or averaged quantities).",
    "items": [
        {"logicalId": "VAC1_PRST_Rise", "kind": "calculated", "unit": "V", "precision": "as specified for the parameter", "source": "captured ramp voltage of the rise segment", "notes": "unit must match the DFT unit column (V) - R-LOG (rules-registry.md :37)"},
        {"logicalId": "VAC1_PRST_Fall", "kind": "calculated", "unit": "V", "precision": "as specified for the parameter", "source": "captured ramp voltage of the fall segment", "notes": "same unit rule"},
        {"logicalId": "VAC1_PRST_Hys", "kind": "calculated", "unit": "mV", "precision": "as specified for the parameter", "source": "(Rise - Fall) * 1e3", "notes": "R-HYS: the conversion is applied at the Hys assignment with a comment and is never applied to the Rise/Fall identity (rules-registry.md :38)"},
        {"logicalId": "triggerModeRise / triggerModeFall (raw context)", "kind": "raw context", "unit": "-", "precision": "-", "source": "the trigger mode actually used for each segment", "notes": "recorded because the polarity is pending OI-T4-01; without it a reviewer cannot tell which premise was in force"},
        {"logicalId": "captureLevel (raw context)", "kind": "raw context", "unit": "V", "precision": "-", "source": "the capture level actually used", "notes": "recorded so the pair of segments can be shown to have used one level"},
        {"logicalId": "sweepGeometry (raw context)", "kind": "raw context", "unit": "V / samples / us", "precision": "-", "source": "the start, stop, step and interval actually used", "notes": "recorded because F5 is open; a log that hides the geometry makes the conflict unresolvable after the fact"},
        {"logicalId": "registerActivationTrace", "kind": "raw context", "unit": "-", "precision": "-", "source": "testmode entry and the one field directive (DMUX_EN/DMUX_SEL) with their values as written", "notes": "the applied values must be logged, not the contested ones, so the F2 ambiguity is visible in the record"},
        {"logicalId": "relayActuationTrace", "kind": "raw context", "unit": "-", "precision": "-", "source": "the closure set actually applied ({13,65}) and the state of every keep-open relay", "notes": "needed because path checking cannot cover the PIN-attached functional relays (setup-contract.json:8156)"},
        {"logicalId": "failureContext", "kind": "context", "unit": "-", "precision": "-", "source": "phase, segment, reason (no trigger / boundary trigger / negative Hys) and the pending item in force", "notes": "no substituted number may be logged in place of a missing capture"},
        {"logicalId": "bstSwStatus", "kind": "context", "unit": "-", "precision": "-", "source": "the per-phase BST/SW status recorded in bst-sw-phase-check.md (all phases 定点补证 pending OI-T5-02)", "notes": "logged as context so that downstream consumers see that the differential constraint was evaluated and is not proven, rather than silently absent"},
    ],
    "prohibited": ["logging a source-table raw value in the wrong unit (R-LOG)", "logging Hys in V (R-HYS)", "logging a placeholder or defaulted SW/BST value"],
}

# ---------------------------------------------------------------- BST/SW phase check
bst_sw_phases = [
    {
        "phase": "P0",
        "phaseName": "pre-state",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "no source allocated to BST/SW; switching stage not committed by the DFT; SW deliberately not taken as 0 V",
        "oid": "OI-T5-02",
    },
    {
        "phase": "P1",
        "phaseName": "closure of the signed functional relays",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "no allocated source; no required state for K48/K76/K61 in the signed closure set; K57_CAP_BST_SW state ambiguous (RT-2)",
        "oid": "OI-T5-02 / RT-2",
    },
    {
        "phase": "P2",
        "phaseName": "VBAT power-on",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "VBAT is a rail pin; the switching stage is not enabled by TM108's register delta (only DMUX_EN/DMUX_SEL), and no tester source drives BST/SW",
        "oid": "OI-T5-02",
    },
    {
        "phase": "P3",
        "phaseName": "register activation",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "the delta contains no driver/switching enable; a BST/SW state still cannot be derived, and BST/SW remain unreachable by any closed relay",
        "oid": "OI-T5-02",
    },
    {
        "phase": "P4",
        "phaseName": "rising sweep (measure)",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "the swept chain (VAC123_AMUX_ACM -> K18 -> K19 -> VAC1_F) is disjoint from every BST/SW route; the internal high-side/low-side commitment is not part of the DFT intent, so neither node's potential is derivable",
        "oid": "OI-T5-02",
    },
    {
        "phase": "P5",
        "phaseName": "hold at the sweep end / turn-around",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "same as P4; no relay action occurs at the turn-around, so no new BST/SW coupling appears",
        "oid": "OI-T5-02",
    },
    {
        "phase": "P6",
        "phaseName": "falling sweep (measure)",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "same as P4; a falling input sweep does not couple to the BST-SW pair through any closed contact of G1/G2",
        "oid": "OI-T5-02",
    },
    {
        "phase": "P7",
        "phaseName": "power-down step 1 (zeroing)",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "the collapse ordering rule for BST-SW applies only to items that drive BST; here the rail collapse cannot be shown to keep any BST/SW relation, so the constraint stays unproven",
        "oid": "OI-T5-02",
    },
    {
        "phase": "P8",
        "phaseName": "power-down steps 2-3 (release + safe end state)",
        "bstActual": "",
        "swActual": "",
        "difference": "",
        "verdict": "定点补证 (pending)",
        "reason": "after release no node of this item is driven; BST/SW end state is again DUT-internal and unevidenced in this boundary",
        "oid": "OI-T5-02",
    },
]
for p in bst_sw_phases:
    p["bstActual"] = "not derivable in the signed boundary (no BST allocation; BST routes need K48+K76 and their K110/K109+K110 variants, tm108-connectmap-ranges.txt:83-91 and :16-21)"
    p["swActual"] = "not derivable in the signed boundary (no SW allocation; the SW node route needs K61_SW, setup-contract.json:144; the only coupling element K57_CAP_BST_SW, SCH-Connect-Map.txt:904, has no signed state - RT-2). Not taken as 0 V (architecture :212-224)"
    p["difference"] = "0 V <= BST_actual - SW_actual <= 5 V : NOT PROVEN"

# ---------------------------------------------------------------- open items / returns
open_items = [
    {"id": "OI-T5-01", "severity": "blocker-for-observation-decisions", "kind": "定点补证", "topic": "observation endpoint identity (carried from OI-T4-01)", "fact": "Every decision that depends on the observation endpoint is marked pending in this contract: the capture source allocation RA-5 (CANDIDATE ONLY), the trigger polarity of both segments, the capture level's validity, the sufficiency of writing DMUX_SEL=22, and the register counterpart EN_DTEST0/DTEST0_MUX=1/23.", "notResolvedBy": "this contract never equates DTEST0 with nQON and does not adopt the alias that appears in the knowledge base (voltage-threshold-ate.md :5) or in the existing implementation (testcpp-blocks.txt:395)", "exactSourceThatWouldCloseIt": "the DFT-side device relation DTEST0 -> nQON (A2D_VAC1_PRST mux) plus the register map for DMUX_SEL=22 (contract md :374)", "owner": "dft-expert (relation) + test-strategy-architect (re-allocation) + test-method-expert (method re-issue)"},
    {"id": "OI-T5-02", "severity": "high", "kind": "定点补证", "topic": "BST/SW differential constraint cannot be proven for any phase of this item", "fact": "0 V <= BST_actual - SW_actual <= 5 V is evaluated for all nine phases in bst-sw-phase-check.md and is NOT PROVEN in any of them, because BST and SW are not TM108 endpoints, no source is allocated to them, no relay of G1-G4 has a required state on them, and SW is explicitly not defaulted to 0 V.", "notResolvedBy": "no value is guessed and no phase is silently omitted; every phase carries the derivation and the verdict", "exactSourceThatWouldCloseIt": "either (a) a DFT-side statement that TM108 leaves the switching stage inactive plus the resulting evidencable node potentials, or (b) the BST/SW endpoint allocation (source table, channel, observation) and its relay state, which the strategy contract must add - see RT-2", "owner": "dft-expert + test-strategy-architect + test-method-expert"},
    {"id": "OI-T5-03", "severity": "medium", "kind": "定点补证", "topic": "the method-side numeric positions in the measurement plan that are not DFT numbers", "fact": "Two classes of number appear in the measurement plan without a DFT source: (i) method-side engineering positions taken from the existing implementation as corroboration (capture level 1.65 V, 200 samples, 20 us interval, the 20 V range, 3 ms closure delay, 1 ms holds), and (ii) the Hys limit's missing tolerance.", "notResolvedBy": "the contract states each value's provenance and the plan they live in; none is presented as a DFT fact", "exactSourceThatWouldCloseIt": "a DFT/method ruling on the capture level and sweep resolution, or acceptance of the recorded positions as the method's own (review can verify the provenance, not the physical optimum)", "owner": "test-method-expert (with test-strategy-architect for the range/limit pair if the allocation must change)"},
    {"id": "OI-T5-04", "severity": "medium", "kind": "定点补证", "topic": "carried DFT conflicts that govern the applied numbers", "fact": "F1 (4.4 V vs 4.15 V), F2 (DMUX_SEL 22 vs 23), F3 (V(DTEST0) vs INT), F4 (VBAT 3 V vs 4.2 V), F5 (three-way scan geometry), F6 (Notes 1 V/ms vs Code2 10 V in 1e-3 s) are all carried into this contract as pending: the method applies the artifact-layer/DFT-intent value for execution while recording the counterpart, and never averages.", "notResolvedBy": "nothing is silently resolved to one side; each phase names the conflict it depends on", "exactSourceThatWouldCloseIt": "the closings recorded in contract md :370-390 (workbook re-dump or a captain/user ruling per conflict)", "owner": "dft-expert + captain (F1/F3/F4/F5/F6); dft-expert + test-strategy-architect (F2)"},
    {"id": "OI-T5-05", "severity": "low", "kind": "定点补证", "topic": "no register de-activation of the delta exists", "fact": "The signed delta has no field to disable the mux after the measurement, so this method deliberately writes nothing at the end (see RT-3). Whether the item must leave the DUT's mux disabled is therefore neither done nor invented.", "notResolvedBy": "no write is invented; the omission is recorded", "exactSourceThatWouldCloseIt": "a strategy/DFT statement of the intended post-item register state, or acceptance of the global cleanup contract as sufficient", "owner": "test-strategy-architect + setup-architect"},
]

returns = [
    {"id": "RT-1", "to": "test-strategy-architect", "topic": "explicit relay state of K13 (VBAT cap gate) differs between the frozen baseline and the signed contract", "detail": "The signed contract's relayGroups[G3] states that K13_VBAT_Cap must be closed (backed by relay-checklist.md :27-37 for a powered rail) while the same contract's resourceSummary.keepOpenRelayNumbers also lists 13 in the keep-open set (contract md :248, :574; contract json resourceSummary). The frozen baseline closes it (setup-contract.json:5667). This method closes it at P1 and releases it at P8, on the explicit closure-set statement and the Cap2 rule, and reports the inconsistency rather than ignoring it.", "needed": "one authoritative statement of K13's state in the signed contract (or removal from the keep-open set)."},
    {"id": "RT-2", "to": "test-strategy-architect", "topic": "K57_CAP_BST_SW state is not in the signed boundary, and no BST/SW endpoint state exists", "detail": "K57 is the 220 nF BST-SW coupling cap gate (project/DALI/SCH-Connect-Map.txt:904) and appears in the baseline's global init list of cap gates (setup-contract.json:3941), but the signed contract neither closes it nor puts it in the keep-open set - so its state is not expressible from this boundary, and the contract's own rule that every scope-path relay needs an explicit state (setup-contract.json:8169) is unmet for it. This is also what makes the BST/SW constraint unevaluable (OI-T5-02).", "needed": "either an explicit K57 state in the contract (closed / not-actuated / not-an-item-relay) plus the BST/SW endpoint and relay state if the differential constraint must be evaluated, or a written statement that TM108 has no BST/SW relation for this method to evaluate."},
    {"id": "RT-3", "to": "test-strategy-architect", "topic": "no register field exists to undo the mux activation", "detail": "The delta is entertestmode + (DMUX_EN=1, DMUX_SEL=22). The method writes nothing at the end (OI-T5-05). If the item is required to leave the mux disabled, the delta needs the corresponding field and value.", "needed": "a delta field for de-activation, or explicit acceptance that no de-activation is required."},
    {"id": "RT-4", "to": "test-strategy-architect / captain", "topic": "no tolerance is published for the threshold limits", "detail": "The DFT publishes 'rising vth 4.4 V, hys 0.35 V' with no tolerance column, and the baseline records the same (setup-contract.json:5687). A pass/fail application therefore cannot be written from the method contract alone, and this contract does not invent one.", "needed": "a tolerance (or a written rule for a missing tolerance) from the spec/DFT side."},
    {"id": "RT-5", "to": "test-strategy-architect / setup-architect", "topic": "site-level concurrency of the shared ACM200 object", "detail": "VAC123_AMUX_ACM serves VAC1/VAC2/VAC3/AMUX (contract json OI-T4-03); the method assumes serial use of the site and does not add a scheduling rule.", "needed": "confirmation of the implied serial schedule or a concurrency table entry."},
]

# ---------------------------------------------------------------- boundary rule check (machine)
BOUNDARY_USED = {
    "sources": ["VAC123_AMUX_ACM (S5_0)", "VBAT_PD3_FXVI (S3_5)", "NQON_HG1_ACM (S5_9, CANDIDATE ONLY)"],
    "relayGroupsReferenced": sorted([g["id"] for g in strat["relayGroups"]]),
    "closureSetActuated": CLOSED,
    "registerFieldsUsed": ["entertestmode()", "DMUX_EN=1", "DMUX_SEL=22"],
    "signalledNodes": ["VAC1_F", "VAC1_S", "VBAT_F", "VBAT_S", "NetK64_HG1_S1_7 (observation candidate)"],
}
assert set(BOUNDARY_USED["closureSetActuated"]) == set(CLOSED)
assert BOUNDARY_USED["registerFieldsUsed"] == ["entertestmode()", "DMUX_EN=1", "DMUX_SEL=22"]
for banned in ([7, 61, 57, 48, 76, 110, 109, 41, 42, 43], []):
    for n in banned:
        assert n not in CLOSED, n

# ---------------------------------------------------------------- write the artifacts
json_doc = {
    "runId": RUN,
    "task": "t5",
    "owner": "test-method-expert",
    "artifact": "tm108-test-method-contract",
    "tm": "TM108",
    "dftName": "VAC1_PRST",
    "implementedSymbol": "TM108_HSKP_VAC1_PRST",
    "date": "2026-09-17",
    "signedBoundary": {
        "contract": "team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md / .json",
        "contractTask": "t4",
        "contractOwner": "test-strategy-architect",
        "hashesSha256": HASHES,
        "declaration": "This method contract adds no source, route, relay, register value, function relay or isolation condition beyond the signed contract. It consumes only relayGroups G1/G2/G3 (G4 remains a documented alternate and is not used), the three resourceAllocation entries RA-1..RA-5 (RA-5 CANDIDATE ONLY), the register delta, and the keep-open set. Everything outside that boundary is returned in returns[].",
        "notDecidedHere": "chip mechanism is only used as cited knowledge; DFT conflicts are not resolved; no C++/SDK/API name, range enum or cbite call form is decided (ate-implementer); no independent review (rule-reviewer) and no build (compile-diagnostician).",
    },
    "observationEndpointStatus": "UNRESOLVED - OI-T4-01 carried as OI-T5-01. DTEST0 is never equated with nQON anywhere in this contract, and every observation-dependent decision is marked PENDING-OI-T4-01.",
    "methodEvidence": method_evidence,
    "boundaryUsed": BOUNDARY_USED,
    "relayBaseState": {
        "closed": CLOSED,
        "requiredClosedWithoutActuationClaim": CLOSED_BY_NATURE,
        "notActuatedDefaultConducting": NOT_ACTUATED,
        "keepOpen": KEEP_OPEN,
        "presentOnBoardButNotAssignedByTheSignedContract": CONTROLLED_UNASSIGNED,
        "basis": "contract md :241-252 (relay summary) and :192-252 (per-group requirements); the partition is this method's statement of the same facts so that every phase can name an explicit set and no relay is left implicit (the baseline requires an explicit state for every scope relay, setup-contract.json:8169)",
    },
    "methodPhases": phases,
    "measurementPlan": measurement_plan,
    "powerDownPlan": power_down_plan,
    "logPlan": log_plan,
    "bstSwConstraint": {
        "rule": "0 V <= BST_actual - SW_actual <= 5 V for every planned phase (team/TEAM_ARCHITECTURE_V2.md:210-227; rules-registry.md :44)",
        "perPhaseVerdicts": "see bst-sw-phase-check.md and bstSwPerPhase[] below",
        "summary": "NOT PROVEN in any of the nine phases; every phase registered as 定点补证 with reason, pending OI-T5-02 / RT-2",
        "swDerivationNote": "SW_actual is derived from the actual closed contacts, shorts, functional state and driven node: in this item the only closed functional relays are K13 (VBAT rail cap) and K65 (observation pull-up), the path contacts are default-conducting K8/K18/K19/K64, and no contact or source drives the SW node; therefore SW_actual cannot be obtained and is deliberately NOT set to 0 V.",
    },
    "bstSwPerPhase": bst_sw_phases,
    "evidence": [
        {"file": "team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md", "locator": "6F6057721062E97EBDA53531383AFF22A91BD0AA8141AADC6BAFC5EF448FE6E4 (sha256); sections :92-121 (endpoints), :125-179 (allocation), :181-252 (relay groups), :256-267 (register delta), :370-420 (open items + handoff)", "class": "dependency artifact (signed upstream contract, t4)"},
        {"file": "team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.json", "locator": "FBA489B5D8CA06A12D74C187EDBBFE1E2F3FC2D564B27DC6AB8B092F8BD3E4B9 (sha256); keys resourceAllocation / relayGroups / registerDelta / resourceSummary / openItems", "class": "dependency artifact (signed upstream contract, t4)"},
        {"file": "team/artifacts/tm108-v2-trial/dft/dft-fact-audit.md", "locator": "AEC7FD74A01314B856009104C721F93B11FE9490B27C0673DEA6E3F385274029 (sha256); :138-260 field table, :262-276 F1-F6, :318-337 P1-P10", "class": "dependency artifact (t2)"},
        {"file": "team/artifacts/tm108-v2-trial/schematic/schematic-fact-audit.md", "locator": "1F5996B21AE84E2E80688C88015CFEA2DD9E35F1075858C72970711A35CEF1B8 (sha256); :98-203 candidates, :205-257 relay facts, :261-274 conflicts, :301-315 open items", "class": "dependency artifact (t3)"},
        {"file": "team/artifacts/tm108-v2-trial/schematic/tm108-paths-proofs.json / .txt", "locator": "6AE38A3678BA05CAA0A0840C6E274E341770FFDC5CA0E3AA4C1474B72095D821 (sha256, .json); per-terminal proof chains with contact pins, nets, state and required_on", "class": "dependency artifact (t3)"},
        {"file": "project/DALI/meta/dali_tm_meta.json", "locator": ":1382-1510 (TM108 object) - READ-VISIBLE via the DFT audit, not re-read here", "class": "project fact (through t2)"},
        {"file": "project/DALI/reg_config/tm108.sv", "locator": "sha256 4d0ea5c30fe5369e98a6d81215bbfb5b5f41bf44ea1c5dbc8df94af75bb92dc1; body regconfig-scope.json:35", "class": "project fact (through t2)"},
        {"file": "project/DALI/SCH-Connect-Map.txt", "locator": ":891 (nQON pull-up), :904 (SW stabiliser cap gate K57), :913 (VAC1 cap gate K21), :914 (VBAT cap gate K13), :801/:804 (low ends to AGND_F), sha256 cc8009fbb27eef0cf29b45e4e50b05e1b5d7b5d49095a32005261a79d83cb427", "class": "project fact"},
        {"file": "team/artifacts/acceptance-20260916-dali10/setup-contract.json", "locator": ":130-160 (ACM200 capability +-200 mA), :3905-3964 (globalInitialization incl. cap gates and the K21 exception), :4162 (unified RELAY_OFF ranges), :5666-5671 (TM108 powerSequenceDelta), :5683-5719 (limits + BD-04), :8150-8179 (safety invariants incl. :8156, :8157, :8161, :8169, :8175, :8179)", "class": "READ-VISIBLE frozen baseline (read-only)"},
        {"file": "team/artifacts/acceptance-20260916-dali10/dft-raw/testcpp-blocks.txt", "locator": ":390-468 (existing implemented TM108 function - corroboration for the method-side numbers only)", "class": "FACT (existing implementation, not an authority)"},
        {"file": "team/artifacts/tm108-v2-trial/schematic/tm108-connectmap-ranges.txt", "locator": ":16-27, :83-91, :226-228 (BST/BST1/BST2 routes and the SW cap gate)", "class": "dependency artifact (t3, range dump)"},
        {"file": "team/artifacts/tm108-v2-trial/schematic/tm108-consistency-check.txt", "locator": ":109, :173 (K61_SW dual-state record: map tokens [NC,ON], IR single value NC)", "class": "dependency artifact (t3, per-relay state matrix)"},
        {"file": "knowledge/references/L3-method/UVLO.md", "locator": ":5-19", "class": "active method knowledge"},
        {"file": "knowledge/references/L1-chip/UVLO.md", "locator": ":14-29", "class": "chip knowledge"},
        {"file": "knowledge/references/L3-method/voltage-threshold-ate.md", "locator": ":5, :9-34", "class": "active method knowledge"},
        {"file": "knowledge/standards/toggle-awg-rules.md", "locator": ":12-34", "class": "active rule"},
        {"file": "knowledge/standards/functions-registry.md", "locator": ":23-31, :43", "class": "active rule (primitive semantics)"},
        {"file": "knowledge/standards/rules-registry.md", "locator": ":32-39, :44", "class": "active rule"},
        {"file": "knowledge/standards/relay-checklist.md", "locator": ":25-42, :71-75", "class": "active rule"},
        {"file": "team/ROLE_ROUTING.md", "locator": ":4-15", "class": "team contract"},
        {"file": "team/TEAM_ARCHITECTURE_V2.md", "locator": ":151-227 (method role, forced flow, BST-SW hard constraint), :268-292 (output fields and handoff)", "class": "team contract"},
        {"file": "team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.md", "locator": "this artifact (hash in the Hash Ledger section)", "class": "this task's output"},
        {"file": "team/artifacts/tm108-v2-trial/method/tm108-test-method-contract.json", "locator": "this artifact (hash in the Hash Ledger section)", "class": "this task's output"},
        {"file": "team/artifacts/tm108-v2-trial/method/bst-sw-phase-check.md", "locator": "this task's output", "class": "this task's output"},
        {"file": "team/artifacts/tm108-v2-trial/method/_build_method_contract.py", "locator": "this task's generator (reproduces all three artifacts and verifies the upstream hashes)", "class": "this task's output"},
        {"file": "team/artifacts/tm108-v2-trial/method/_finalize_method_contract.mjs", "locator": "this task's publisher (writes the three artifacts as plaintext UTF-8 and verifies the round-trip; needed because interpreter-written files in this workspace are stored inside a TSZ# transparent-encryption container that plain readers cannot parse)", "class": "this task's output"},
    ],
    "openItems": open_items,
    "returns": returns,
    "handoffToImplementerAndReviewer": {
        "for": ["ate-implementer", "rule-reviewer"],
        "settled": ["the phase order and each phase's prerequisite / relay group / register activation / actual node table / differential checks / setpoint / ramp / delay / exit condition", "the closure set to apply ({13,65}) and the keep-open list", "the register staircase (testmode then DMUX_EN/DMUX_SEL=22 as one directive) and the deliberate absence of any de-activation write", "the two-segment measurement with the three parameters, the calculation and the units (R-HYS/R-LOG)", "the three-step power-down and the safe end state"],
        "pendingAndMustNotBeTreatedAsSettled": ["OI-T5-01 / OI-T4-01 (observation endpoint identity, trigger polarity, capture level validity, DMUX_SEL=22 sufficiency)", "OI-T5-04 (F1-F6, all carried)", "RT-1 (K13 state statement)", "RT-2 (K57 and the BST/SW constraint - every phase is 定点补证)", "RT-4 (missing tolerance)"],
        "reviewerInstructions": "Review against the signed strategy contract and this contract only; the implemented function is not an authority. Any electrical or method change must be returned to the owner of this contract, not fixed in code.",
    },
    "selfCheck": {
        "boundaryCompliance": "no source, channel, relay state, register field or isolation condition added beyond the signed contract; the only relay-state statement this contract makes that is not verbatim in the contract is the partition of the same relay list into base-state sets, and the K13 read-back difference is reported as RT-1",
        "noObservationAssumption": "DTEST0 is never equated with nQON; every dependent decision is marked pending OI-T4-01",
        "noConflictResolution": "F1-F6 remain two-sided everywhere",
        "noTm601OrOtherTm": "no other TM appears in this contract",
        "bstSwEveryPhase": "all nine phases carry the per-phase evaluation and the verified verdict",
    },
}

w("tm108-test-method-contract.src.json", json.dumps(json_doc, ensure_ascii=False, indent=2) + "\n")

# ---------------------------------------------------------------- markdown
def nodes_md(items):
    return "\n".join("  - " + x for x in items)


def phase_md(p):
    return f"""### {p['phase']} — {p['name']} ({p['stage']})

| field | content |
|---|---|
| prerequisite | {p['prerequisite']} |
| relayGroup | {p['relayGroup']} |
| resourceState | {json.dumps(p['resourceState'], ensure_ascii=False)} |
| registerActivation | {p['registerActivation']} |
| setpoint | {p['setpoint']} |
| ramp | {p['ramp']} |
| delay | {p['delay']} |
| exitCondition | {p['exitCondition']} |

**actualNodeVoltages**

{nodes_md(p['actualNodeVoltages'])}

**differentialChecks**

{nodes_md(p['differentialChecks'])}
"""


md = []
md.append("# TM108 测试方法契约（VAC1_PRST · 阶段/实际节点/测量/下电/Log + 逐阶段 BST-SW 约束）")
md.append("")
md.append(f"- runId: `{RUN}` · task: `t5` · owner: **test-method-expert**")
md.append("- TM: **TM108** (`VAC1_PRST`, implemented symbol `TM108_HSKP_VAC1_PRST`)")
md.append("- 写入范围（本任务唯一）：`team/artifacts/tm108-v2-trial/method/`")
md.append("  `tm108-test-method-contract.md`、`tm108-test-method-contract.json`、`bst-sw-phase-check.md`、`_build_method_contract.py`、`_finalize_method_contract.mjs`")
md.append("- 上游签名边界：`team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md` / `.json`（t4，test-strategy-architect）")
md.append("- 本契约**只**决定：方法证据与 Golden 适用性、阶段顺序、实际节点电位、测量与计算、下电、Log、逐阶段 BST-SW 约束评价。")
md.append("  **不**决定：分类/源表/通路/继电器组/寄存器值（策略侧）、C++/SDK/量程枚举/cbite 调用形式（实现侧）、独立评审（评审侧）、编译（门禁侧）。")
md.append("- **未写入任何项目文件**：`project/DALI/` 只读；`D:/PROJECT6-DALI/devel` 未访问。")
md.append("")
md.append("---")
md.append("")
md.append("## 0. 一句话结论")
md.append("")
md.append("TM108 是**一般测试项目 + 阈值 AWG（toggle）+ grouped**，参数族 **UVLO/PRST**：")
md.append("在签名边界内共 **9 个阶段**（P0 预状态 → P1 闭合 → P2 VBAT 上电 → P3 寄存器生效 → P4 升扫测量 → P5 折返保持 → P6 降扫测量 → P7 下电归零 → P8 释放与安全终态），")
md.append("闭合集 **{13, 65}** + **K17 处于闭合态**，寄存器 delta **entertestmode + (DMUX_EN=1, DMUX_SEL=22)**，")
md.append("测量用 **两段式 rampv_capv**（升扫捕下降沿 / 降扫捕上升沿）产出 **Rise / Fall / Hys(mV)** 三参数。")
md.append("**观测端点身份未解决（OI-T4-01 → OI-T5-01）**：本契约**从不**把 `DTEST0` 当作 `nQON`，")
md.append("所有依赖观测端点的决定一律标 **PENDING-OI-T4-01**；DFT 冲突 F1–F6 一律双侧保留、不取舍。")
md.append("**BST/SW 约束（0 V ≤ BST_actual − SW_actual ≤ 5 V）逐阶段评价：9/9 阶段均标 定点补证（未证实）**，")
md.append("原因是签名边界内既无 BST/SW 的源表分配、也无任一继电器在其上有必需状态，且 `SW_actual` **不按 0 V 默认**")
md.append("（理由见 `bst-sw-phase-check.md`，待闭合项 `OI-T5-02` / 退回项 `RT-2`）。")
md.append("")
md.append("---")
md.append("")
md.append("## 1. 上游边界与哈希台账")
md.append("")
md.append("| 输入 | sha256 | 用途 |")
md.append("|---|---|---|")
md.append(f"| `strategy/tm108-resource-config-contract.md` | `{HASHES['strategy/tm108-resource-config-contract.md']}` | 签名资源/配置边界（**唯一权威**） |")
md.append(f"| `strategy/tm108-resource-config-contract.json` | `{HASHES['strategy/tm108-resource-config-contract.json']}` | 机读边界（闭集/寄存器/openItems） |")
md.append(f"| `dft/dft-fact-audit.md` | `{HASHES['dft/dft-fact-audit.md']}` | 当前项目 DFT 事实与 F1–F6 |")
md.append(f"| `schematic/schematic-fact-audit.md` | `{HASHES['schematic/schematic-fact-audit.md']}` | 物理节点/继电器/互斥事实 |")
md.append(f"| `schematic/tm108-paths-proofs.json` | `{HASHES['schematic/tm108-paths-proofs.json']}` | 逐条 proof 的触点/net 原始记录 |")
md.append("")
md.append("**边界使用（机读字段见 JSON `boundaryUsed`）**")
md.append("")
md.append(f"- 源表：{', '.join(BOUNDARY_USED['sources'])}（RA-5 为 `CANDIDATE ONLY`）")
md.append(f"- 继电器组：{', '.join(BOUNDARY_USED['relayGroupsReferenced'])}（G4 为备选，**本方法不使用**）")
md.append(f"- 实际动作闭合集：{BOUNDARY_USED['closureSetActuated']}；K17 只要求“处于闭合态”，其动作形式归 OI-T4-04 与实现侧")
md.append(f"- 寄存器字段：{', '.join(BOUNDARY_USED['registerFieldsUsed'])}；**无**停用字段")
md.append(f"- 被驱动/被观测节点：{', '.join(BOUNDARY_USED['signalledNodes'])}")
md.append("")
md.append("**继电器基础态（把签名契约的同一组事实按“每个阶段都能指名一个显式集合”的方式分区；每条都回指契约）**")
md.append("")
md.append(f"- 动作闭合（须 SetOn）：`{CLOSED}`（G3 功能性闭合；契约 md :224、:245）")
md.append(f"- 须处于闭合态、但方法不声明其来源：`{CLOSED_BY_NATURE}`（契约 md :199、:245-246；OI-T4-04）")
md.append(f"- 依赖默认导通（**不动作**）：`{NOT_ACTUATED}`（契约 md :247；`K8/K18/K19/K64` 的角色见契约 md :295-298）")
md.append(f"- 必须保持未动（隔离/互斥）：`{KEEP_OPEN}`（契约 md :248）")
md.append(f"- 板上有通路但**签名契约未赋予状态**：`{CONTROLLED_UNASSIGNED}`（见 `RT-1`/`RT-2`；其中 `K57` 是 BST-SW 耦合电容门）")
md.append("")
md.append("> 口径：**本方法不新增任何继电器状态**。上表是对契约自身列表的分区；唯一需要策略侧裁决的读回差异（`K13`）见 `RT-1`。")
md.append("")
md.append("---")
md.append("")
md.append("## 2. methodEvidence[]（逐来源：适用性 direct / partial / unavailable + 判据）")
md.append("")
md.append("判据维度（`team/TEAM_ARCHITECTURE_V2.md:203`、`:231-233`）：参数类型 / DUT 拓扑 / 关键相对电压 / DFT 操作点 / 源表工作模式 / 资源边界。")
md.append("")
for i, e in enumerate(method_evidence, 1):
    d = e["dimensions"]
    md.append(f"**E{i}. {e['source']}**")
    md.append("")
    md.append(f"- 定位：`{e['locator']}`")
    md.append(f"- 适用性：**{e['applicability']}**")
    md.append(f"- 理由：{e['reason']}")
    md.append(f"- 维度：参数类型={d['parameterType']}；拓扑={d['topology']}；关键相对电压={d['criticalRelativeVoltages']}；DFT 操作点={d['dftOperatingPoint']}；源表工作模式={d['sourceWorkingMode']}；资源边界={d['resourceBoundary']}")
    md.append("")
md.append("**Golden 结论**：本参数类型的最近同类 Golden（`L4-Golden-code/UVLO.cpp` 的 PRST 阈值 AWG）在本工作区**不可读（unavailable）**，")
md.append("而知识层给出的观测脚别名（`voltage-threshold-ate.md:5`）与已实现函数注释（`testcpp-blocks.txt:395`）都**内含 `DTEST0`→`nQON` 这一未证实前提**，")
md.append("因此该 Golden 即便可读也只能作为 **partial** 参考，不得直接采用；本契约的全部结论均不依赖它。")
md.append("")
md.append("---")
md.append("")
md.append("## 3. methodPhases[]（阶段状态表）")
md.append("")
md.append("每阶段列出 prerequisite / relayGroup / resourceState / registerActivation / actualNodeVoltages / differentialChecks / setpoint / ramp / delay / exitCondition；")
md.append("每个数值回指 DFT、签名契约、active 规则或既有实现（证明“非杜撰”）。")
md.append("")
for p in phases:
    md.append(phase_md(p))
md.append("---")
md.append("")
md.append("## 4. measurementPlan（force/measure、量程、扫描、采样窗口、计算、limit、site）")
md.append("")
md.append(f"- 参数集：`{', '.join(measurement_plan['parameterSet'])}` — {measurement_plan['parameterSetRule']}")
md.append(f"- 原语：`{measurement_plan['primitive']['name']}` — {measurement_plan['primitive']['semantics']}")
md.append(f"- 合法性：{measurement_plan['primitive']['legality']}")
md.append("")
for s in measurement_plan["segments"]:
    md.append(f"### 段：{s['segment']}（阶段 {s['phase']}）")
    md.append("")
    md.append(f"- force 端点：{s['force']['endpoint']}；通道 {s['force']['channel']}；模式 {s['force']['mode']}")
    md.append(f"  量程 {s['force']['vRange']} / {s['force']['iRange']}；量程依据：{s['force']['vRangeBasis']}")
    md.append(f"- measure 端点：{s['measure']['endpoint']}；量程 {s['measure']['vRange']} / {s['measure']['iRange']}；**{s['measure']['status']}**")
    md.append(f"- sweep：{s['sweep']['start']} → {s['sweep']['stop']}（依据 {s['sweep']['startStopBasis']}）")
    md.append(f"- step：{s['step']}；采样窗口：{s['sampleWindow']}")
    md.append(f"- trig：{s['trigLevel']} / {s['trigMode']}（依据 {s['trigModeBasis']}）")
    md.append(f"- result：{s['result']}")
    md.append("")
md.append("### 计算与判定")
md.append("")
for k in ("rise", "fall", "hys", "siteHandling"):
    md.append(f"- {measurement_plan['calculation'][k]}")
md.append("")
md.append("### limits")
md.append("")
md.append(f"- 权威文本：`{measurement_plan['limits']['authoritativeText']}`（依据：{measurement_plan['limits']['authoritativeBasis']}）")
md.append(f"- 已登记冲突：{measurement_plan['limits']['registeredConflictF1']}")
md.append(f"- 容差：{measurement_plan['limits']['tolerance']}")
md.append(f"- 使用方式：{measurement_plan['limits']['usage']}")
md.append(f"- Hys 定义：{measurement_plan['limits']['hysDefinition']}")
md.append("")
md.append(f"### 失败上下文")
md.append("")
md.append(f"- {measurement_plan['failureContext']}")
md.append("")
md.append("### 越界需求（不在边界内，须退回或登记）")
md.append("")
for x in measurement_plan["outOfBoundaryNeeds"]:
    md.append(f"- {x}")
md.append("")
md.append("---")
md.append("")
md.append("## 5. powerDownPlan（下电动作、节点电位、差分检查、安全终态）")
md.append("")
md.append(f"- 类型：{power_down_plan['type']}")
md.append("")
md.append("| # | 动作 | 阶段 |")
md.append("|---|---|---|")
for s in power_down_plan["steps"]:
    md.append(f"| {s['order']} | {s['action']} | {s['phase']} |")
md.append("")
md.append("**规则依据**")
md.append("")
for r in power_down_plan["ruleBasis"]:
    md.append(f"- {r}")
md.append("")
md.append("**actualNodeVoltages（下电）**")
md.append("")
for x in power_down_plan["actualNodeVoltages"]:
    md.append(f"- {x}")
md.append("")
md.append("**differentialChecks（下电）**")
md.append("")
for x in power_down_plan["differentialChecks"]:
    md.append(f"- {x}")
md.append("")
md.append(f"**安全终态**：{power_down_plan['safeEndState']}")
md.append("")
md.append("---")
md.append("")
md.append("## 6. logPlan（原始量 / 计算量 / 判定量 / 单位 / 精度 / 上下文）")
md.append("")
md.append(f"- site 模型：{log_plan['siteModel']}")
md.append("")
md.append("| logicalId | kind | unit | precision | source | notes |")
md.append("|---|---|---|---|---|---|")
for it in log_plan["items"]:
    md.append(f"| `{it['logicalId']}` | {it['kind']} | {it['unit']} | {it['precision']} | {it['source']} | {it['notes']} |")
md.append("")
md.append("**禁止**")
md.append("")
for x in log_plan["prohibited"]:
    md.append(f"- {x}")
md.append("")
md.append("---")
md.append("")
md.append("## 7. 逐阶段 BST-SW 约束（0 V ≤ BST_actual − SW_actual ≤ 5 V）")
md.append("")
md.append("> 规则：`team/TEAM_ARCHITECTURE_V2.md:210-227`；`knowledge/standards/rules-registry.md:44`。")
md.append("> 结论摘要：**9/9 阶段为 定点补证（未证实）**，逐阶段推导与 `SW_actual` 推导见 `bst-sw-phase-check.md`。")
md.append("")
md.append("| 阶段 | BST_actual | SW_actual | 差值与判定 | 依据 |")
md.append("|---|---|---|---|---|")
for p in bst_sw_phases:
    md.append(f"| {p['phase']} | 未可导出 | 未可导出（**不按 0 V**） | 0 ≤ Δ ≤ 5 V **未证实** → 定点补证 | {p['reason']} |")
md.append("")
md.append("**为何不能给出数值（要点，详证见 `bst-sw-phase-check.md`）**")
md.append("")
for x in BSTSW_NODES:
    md.append(f"- {x}")
md.append(f"- {TAIL_BSTSW}")
md.append("")
md.append("---")
md.append("")
md.append("## 8. evidence[]（本契约每条结论的定位）")
md.append("")
md.append("| # | 文件 | 定位 | 类别 |")
md.append("|---|---|---|---|")
for i, e in enumerate(json_doc["evidence"], 1):
    md.append(f"| E{i} | `{e['file']}` | {e['locator']} | {e['class']} |")
md.append("")
md.append("---")
md.append("")
md.append("## 9. openItems[]（定点补证）")
md.append("")
md.append("| id | 级别 | 内容 | 不做什么 | 闭合所需来源 | 归属 |")
md.append("|---|---|---|---|---|---|")
for o in open_items:
    md.append(f"| `{o['id']}` | {o['severity']} | {o['topic']} | {o['notResolvedBy']} | {o['exactSourceThatWouldCloseIt']} | {o['owner']} |")
md.append("")
md.append("**承载自上游的未决项（本契约逐条带入，不取舍）**")
md.append("")
md.append("- DFT 冲突 **F1→OI-T4-09**、**F2→OI-T4-10**、**F3→OI-T4-11**、**F4→OI-T4-12**、**F5→OI-T4-13**、**F6→OI-T4-14**：全部双侧保留；本契约在执行侧采用 DFT 意图/artifact 侧数值，并**逐阶段标注该冲突**，不做平均、不裁剪。")
md.append("- **OI-T4-01/02**：观测端点身份与观测侧选择 → 本契约以 `OI-T5-01` 承载，所有依赖决定标 PENDING。")
md.append("- **OI-T4-03**（通道并发）、**OI-T4-04**（K17 动作形式）、**OI-T4-05/07**（PIN 附着功能继电器覆盖）、**OI-T4-08**（AGND 资格）、**OI-T4-16/17**（基线/口径）作为约束带入，未被本契约当作已裁定。")
md.append("")
md.append("---")
md.append("")
md.append("## 10. 退回项（越出签名边界的需要 → 命名 owner）")
md.append("")
md.append("| id | 退回给 | 内容 | 需要什么 |")
md.append("|---|---|---|---|")
for r in returns:
    md.append(f"| `{r['id']}` | **{r['to']}** | {r['topic']}：{r['detail']} | {r['needed']} |")
md.append("")
md.append("> 说明：本契约**没有**为了实现方便而改动任何源表、通路、继电器、寄存器值、功能继电器或隔离条件；")
md.append("> 上表是唯一通向边界的请求。")
md.append("")
md.append("---")
md.append("")
md.append("## 11. 交接（给实现者与校验者）")
md.append("")
for x in json_doc["handoffToImplementerAndReviewer"]["settled"]:
    md.append(f"- 已定：{x}")
md.append("")
md.append("**未决、不得当作已定**")
md.append("")
for x in json_doc["handoffToImplementerAndReviewer"]["pendingAndMustNotBeTreatedAsSettled"]:
    md.append(f"- {x}")
md.append("")
md.append(f"> {json_doc['handoffToImplementerAndReviewer']['reviewerInstructions']}")
md.append("")
md.append("---")
md.append("")
md.append("## 12. 自检")
md.append("")
md.append("| 检查 | 结果 |")
md.append("|---|---|")
md.append("| 方法契约 md/json 均存在且含 methodEvidence / methodPhases / measurementPlan / powerDownPlan / logPlan / evidence / openItems | 通过（本文件与同名 JSON） |")
md.append("| 每个阶段十项字段齐备（prerequisite / relayGroup / resourceState / registerActivation / actualNodeVoltages / differentialChecks / setpoint / ramp / delay / exitCondition） | 通过（§3，9 个阶段） |")
md.append("| 每个数值有引用、无杜撰 | 通过（§3 逐条引用；方法侧数值经 `OI-T5-03` 登记其来源与性质） |")
md.append("| 逐阶段 BST-SW 显式评价（不默认 SW=0 V） | 通过（§7 + `bst-sw-phase-check.md`，9/9 为定点补证并给出原因） |")
md.append("| 观测端点未被当作已解决（`DTEST0` ≠ `nQON`） | 通过（§0、§3 P3-P6、`OI-T5-01`） |")
md.append("| F1–F6 未被静默解到单侧 | 通过（§9；各阶段标注适用冲突） |")
md.append("| 未新增超出签名边界的源表/通路/继电器/寄存器/功能继电器/隔离条件 | 通过（§1 边界使用 + §10 退回项） |")
md.append("| 无其他 TM 内容 | 通过（全文只出现 TM108；承接项用编号引用） |")
md.append("")
md.append("**未做（越界声明）**：不写 C++/SDK/API/量程枚举/cbite 调用形式（ate-implementer）；不做独立评审（rule-reviewer）；不编译、不建门禁（compile-diagnostician）；不部署、不宣称硬件通过。")
md.append("")
w("tm108-test-method-contract.src.md", "\n".join(md) + "\n")

# ---------------------------------------------------------------- bst-sw-phase-check.md
b = []
b.append("# TM108 逐阶段 BST-SW 约束检查（0 V ≤ BST_actual − SW_actual ≤ 5 V）")
b.append("")
b.append(f"- runId: `{RUN}` · task: `t5` · owner: **test-method-expert** · 目标 TM: **TM108** 唯一")
b.append(f"- 规则：`team/TEAM_ARCHITECTURE_V2.md:210-227`（含“不可违反的阶段约束”与“不设自动例外”）；`knowledge/standards/rules-registry.md:44`（R-BST-SW 的表述）")
b.append("- 阶段集合来自 `tm108-test-method-contract.md` §3 的 P0–P8，与之一一对应，无阶段被跳过。")
b.append("")
b.append("## 1. 结论（一句话）")
b.append("")
b.append("**9/9 阶段均为 定点补证（未证实）**：在签名边界 `team/artifacts/tm108-v2-trial/strategy/tm108-resource-config-contract.md` 内，")
b.append("BST 与 SW **既不是 TM108 的端点**，**也没有任何源表分配**，**也没有任一继电器组在其上有必需状态**；")
b.append("因此 `BST_actual` 与 `SW_actual` 都无法从“实际闭合继电器 + 短接 + 功能状态 + 已驱动节点”导出。")
b.append("`SW_actual` **明确不取 0 V**（架构 :212-224 禁止该默认），因此不构成“BST−SW ≤ 5 V 成立”的结论。")
b.append("待闭合项 **OI-T5-02**；需要边界补证的部分已作为 **RT-2** 退回 test-strategy-architect。")
b.append("")
b.append("## 2. SW_actual 的推导链（逐条，非默认值）")
b.append("")
b.append("| 步 | 事实 | 来源 | 对 SW_actual 的作用 |")
b.append("|---|---|---|---|")
b.append("| 1 | TM108 端点集合 = VAC1（被扫描）、VBAT（供电）、观测候选、AGND（仅板级参考）；**无 BST/SW** | 契约 md :94-101 | SW 不是本项的端点，方法不需要驱动它——但这也意味着方法**无法观测**它 |")
b.append("| 2 | TM108 的 5 条资源分配只落在 `VAC123_AMUX_ACM S5_0`、`VBAT_PD3_FXVI S3_5`、`NQON_HG1_ACM S5_9` | 契约 md :133-139（RA-1..RA-5） | 没有任何源表接到 SW 节点 |")
b.append("| 3 | 本项实际动作的闭合集 = `{13, 65}`（VBAT 稳压电容门 + 观测上拉），K17 另需处于闭合态 | 契约 md :192-252 | 这两个继电器都在 VBAT / 观测支路，与 SW 无触点关系（`project/DALI/SCH-Connect-Map.txt:891`、`:914`） |")
b.append("| 4 | 依赖默认导通的触点 = `K8 / K18 / K19 / K64`；四者都不动作 | 契约 md :220-222、:247 | 其触点在 VBAT、VAC1、nQON 三条链上；SW 不在其中 |")
b.append("| 5 | 观测器候选链 `S5_ACM200_FH9 → K64(pin6→7) → NetK64_HG1_S1_7`；而 HG1 侧需要 K64 动作 | tm108-paths-proofs.txt:170-173、:196；契约 md :298 | **K64 保持未动 ⇒ 高边栅极域（HG1）不被测试机接入**；这是本项唯一“可能接触高边域”的继电器，且被契约关闭 |")
b.append("| 6 | SW 节点在板上有通路（ACM200 ch8 `S5_ACM200_FH8/SH8` 经 `K61_SW`；K61 在同一文件里是双态继电器，IR 单值取 NC） | `setup-contract.json:144`、`:371`；`tm108-consistency-check.txt:109`、`:173` | K61 不在本项闭集、也不在契约的 keep-open 列表 → 其状态**未由签名契约赋予**（`RT-2`），不能据此推断 SW 的电位 |")
b.append("| 7 | BST 节点在板上有通路（baseline 形式 `S5_ACM200_FH5 → K48 → K76 → BST_F/S`；并存形式 `S5_ACM200_FH18 → K110 → BST`，以及 CH1 Low `K109+K110`），均需 K48/K76/K109/K110 等动作 | `tm108-connectmap-ranges.txt:16-21`、`:83-91`；`setup-contract.json:145`、`:149-153` | 这些继电器的状态同样未由签名契约赋予 → BST 电位不可导出 |")
b.append("| 8 | BST↔SW 之间只有 **220 nF 自举电容门 `K57_CAP_BST_SW`**（`SW 稳压 Cap_SW_BST_S1 C=220nF 需闭合: K57`） | `project/DALI/SCH-Connect-Map.txt:904`；`setup-contract.json:3941`、`:8156`（K57 被列为“本项需要的稳压电容门”的**条件候选**，同时被明确归入“不出现在任何 `required_on`、必须按功能规则给状态”的 PIN 附着继电器） | **签名契约既未闭合 K57、也未把 K57 放进 keep-open 列表** → 这是本边界唯一可能触及 BST-SW 对却状态不明的元件（`RT-2`）；按“不在签名闭集内即不动作”，本方法**不闭 K57** |")
b.append("| 9 | 芯片内部的开关级（低边/高边导通、SW=PGND 或 SW=PMID）由 DFT 意图、寄存器 delta 与闭集**都未承诺** | 契约 md :256-267（delta 只有 entertestmode + DMUX 两字段）；dft-fact-audit.md :227-231 | SW 的实际电位取决于该内部状态；**不可用“SW=0 V”替代**（架构 :222-224 明令禁止） |")
b.append("")
b.append("**推导结论**：`SW_actual` 在本边界内**不可导出**；`BST_actual` 同理。因此“0 V ≤ BST_actual − SW_actual ≤ 5 V”**不能**被声明为满足，")
b.append("按架构 :216-227 的处置：该阶段**登记为定点补证**（而不是继续排布该阶段的电气动作）。本契约对 P1–P8 的电气设计均**不依赖** BST/SW 的数值，")
b.append("故列表自身仍可执行；但**该约束的证实责任不得被静默丢弃**，已作为 `OI-T5-02` 与 `RT-2` 挂账。")
b.append("")
b.append("## 3. 逐阶段检查表")
b.append("")
b.append("| 阶段 | 阶段名 | 该阶段实际闭合/状态 | BST_actual | SW_actual | 0 ≤ BST−SW ≤ 5 V | 结论 | 定点补证原因 |")
b.append("|---|---|---|---|---|---|---|---|")
_stage_closure = {
    "P0": "无（未进入任何组）",
    "P1": "{13, 65} + K17 闭合态",
    "P2": "{13, 65} + VBAT 源使能",
    "P3": "{13, 65} + 寄存器 delta 生效",
    "P4": "{13, 65} + VAC1 升扫",
    "P5": "{13, 65} + VAC1 折返保持",
    "P6": "{13, 65} + VAC1 降扫",
    "P7": "{13, 65} + 三源归零",
    "P8": "释放（无闭合）",
}
for p in bst_sw_phases:
    b.append(f"| {p['phase']} | {p['phaseName']} | {_stage_closure[p['phase']]} | 未可导出 | 未可导出（**不按 0 V**） | **未证实** | 定点补证 | {p['reason']} |")
b.append("")
b.append("## 4. 参考：板级 BST/SW 相关事实与本项的关系（只读证据）")
b.append("")
b.append("| 事实 | 证据 | 与 TM108 的关系 |")
b.append("|---|---|---|")
b.append("| BST 通道族属于 ACM200 ch5（`SW12_U1REF_BST_ACM`），baseline 路线 `K48 + K76`；并存 `K110`（PB0_BST_ACM / ch18）与 `K109+K110`（CH1 Low）路线 | `setup-contract.json:145`、`:149-153`；`tm108-connectmap-ranges.txt:16-21`、`:83-91` | 均在签名闭集之外；本项不选、不闭 |")
b.append("| SW 节点的测试机通路经 `K61_SW`（ACM200 ch8，`S5_ACM200_FH8/SH8`） | `setup-contract.json:144`；`tm108-consistency-check.txt:109`、`:173`（K61 双态，IR 单值 NC） | 未由签名契约赋状态（`RT-2`） |")
b.append("| BST↔SW 自举电容 220 nF，门控继电器 `K57_CAP_BST_SW` | `project/DALI/SCH-Connect-Map.txt:904`；`setup-contract.json:3941`、`:8156`（PIN 附着继电器不出现在任何 `required_on`，必须按功能规则给状态） | 唯一可能触及 BST-SW 对的元件；状态不明 → `RT-2` |")
b.append("| 平台级差分要求原文（E006：`BST must lead PMID/SW by >=5 V` / 自举电容不得反偏；两个措辞都被登记而非平均） | `setup-contract.json:8161`；`rules-registry.md:44`（0≤BST−SW≤5 V，目标 5 V） | 用于确认本约束的**表述**；该条目的作用域是 Current-Threshold/ZCD 类（带自身拓扑指纹与专用门禁脚本），**不**把 TM108 所属家族归入该类 |")
b.append("| 低端/高端回路（FXVIe_PLUS 与 ACM200 的 Low 端）分组接 `AGND_F` | `project/DALI/SCH-Connect-Map.txt:801`、`:804` | 说明单端 force 的电流回路；与 BST/SW 无触点关系 |")
b.append("")
b.append("## 5. 该结论的下游后果（明确写出，避免被误读）")
b.append("")
b.append("- 对**实现者**：不得为了“让 BST−SW 检查通过”而新增任何继电器动作或源表设置；本项不存在该检查所需的资源（架构 :216-227 的例外只能由用户裁定）。")
b.append("- 对**校验者**：审查时应核对每一阶段都带有本检查的结论（9/9），而不是核对一个数值；若下游要求 BST−SW 的**数值**，只能先闭合 `OI-T5-02` / `RT-2`。")
b.append("- 对**策略侧**：若 TM108 必须给出 BST/SW 的实测证据，则需补：BST/SW 端点与源表分配、其继电器必需状态、以及 K57 的显式状态（`RT-2`）。")
b.append("- 不得把本文件读成“TM108 无 BST/SW 风险所以无需检查”的结论——本文件的结论是**未证实**，不是“无风险”。")
b.append("")
w("bst-sw-phase-check.src.md", "\n".join(b) + "\n")

print("HASHES_AT_BUILD", json.dumps(HASHES, indent=2))
print("WROTE *.src.md / *.src.json (run _finalize_method_contract.mjs to publish the plaintext artifacts)")
