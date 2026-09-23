"""Check DALI functional relays that physical path proofs cannot require.

This gate uses the signed DFT projection, strategy closure, current project
rules, and the lossless schematic map. It does not infer functional relays
from Path-Proofs.required_on. Missing or contradictory evidence is UNKNOWN.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from scripts.check_path_conflicts import check_contract
except ModuleNotFoundError:  # Direct ``python scripts/check_functional_relays.py``.
    from check_path_conflicts import check_contract


def _line(text, pattern):
    matches = [(number, value.strip()) for number, value in enumerate(text.splitlines(), 1)
               if re.search(pattern, value, re.I)]
    return matches[0] if len(matches) == 1 else None


def _relay_set(values):
    if not isinstance(values, list):
        return None
    result = set()
    for value in values:
        match = re.fullmatch(r"K?(\d+)", str(value), re.I)
        if not match or isinstance(value, bool):
            return None
        result.add(int(match.group(1)))
    return result


def _closure(contract):
    summary = contract.get("resourceSummary")
    groups = contract.get("relayGroups")
    if not isinstance(summary, dict) or not isinstance(groups, list) or not groups:
        return None, "strategy has no final SetOn summary and relayGroups"
    declared = _relay_set(summary.get("setOnRelayUnion"))
    if declared is None:
        return None, "strategy resourceSummary.setOnRelayUnion is not a relay list"
    group_union = set()
    for group in groups:
        if not isinstance(group, dict):
            return None, "strategy relayGroups contains an invalid entry"
        relays = _relay_set(group.get("setOnRelayIds"))
        if relays is None:
            return None, "strategy relayGroup.setOnRelayIds is not a relay list"
        group_union |= relays
    if group_union != declared:
        return None, "strategy summary and relayGroups disagree on final SetOn relays"
    functional = summary.get("functionalRelayUnion")
    if functional is not None:
        functional_set = _relay_set(functional)
        if functional_set is None or not functional_set <= declared:
            return None, "strategy functionalRelayUnion is invalid or outside final SetOn"
    return declared, None


def _map_relay(schematic, pin, kind, expected):
    raw = schematic.get("rawText") if isinstance(schematic, dict) else None
    if not isinstance(raw, str):
        return None
    row = _line(raw, rf"^\s*{re.escape(pin)}\s+{kind}\b.*需闭合:\s*K{expected}\b")
    return f"SCH-Connect-Map.json:rawText line {row[0]}" if row else None


def _rule_line(text, pattern, name):
    row = _line(text, pattern)
    return f"{name}:{row[0]}" if row else None


def _classify_k13(raw):
    power = raw.get("Power")
    if not isinstance(power, str) or not power.strip():
        return "UNKNOWN", "DFT Power is missing"
    power_pins = {token.upper() for token in re.findall(r"[A-Za-z][A-Za-z0-9_]*", power)}
    if "VBAT" not in power_pins:
        return "NOT_APPLICABLE", "DFT Power does not name VBAT"
    codes = "\n".join(str(raw.get(key) or "") for key in ("Code1", "Code2", "Code3"))
    vbat_vsets = re.findall(r"\bvset\s*\[\s*vbat\s*,", codes, re.I)
    if not vbat_vsets:
        return "UNKNOWN", "DFT names VBAT power but has no explicit VBAT vset"
    dynamic = raw.get("Dynamic")
    check = raw.get("Check")
    if not isinstance(dynamic, str) or not isinstance(check, str) or not check.strip():
        return "UNKNOWN", "DFT Dynamic or Check is not explicit"
    if re.search(r"\bVBAT\b", dynamic, re.I):
        return "EXEMPT", "VBAT is the declared swept pin"
    if re.search(r"\b(?:I|MI|MIRET)\s*\(\s*VBAT\s*\)", check, re.I):
        return "EXEMPT", "the check measures current through VBAT"
    if re.search(r"\b(?:ramp\w*|capi\w*|miret|iset)\s*\[\s*vbat\s*[,\]]", codes, re.I):
        return "EXEMPT", "the code explicitly sweeps or captures current on VBAT"
    if len(vbat_vsets) != 1:
        return "UNKNOWN", "multiple VBAT vset operations need a ramp decision"
    if not re.search(r"\bvset\s*\[\s*vbat\s*,\s*(?!0(?:\.0*)?\s*,)[^,\]]+", codes, re.I):
        return "UNKNOWN", "VBAT vset does not prove a nonzero supply"
    return "REQUIRED", "VBAT is a direct supply, not the measured-current or swept pin"


def _classify_k65(raw, contract):
    check = raw.get("Check")
    if not isinstance(check, str) or not check.strip():
        return "UNKNOWN", "DFT Check is missing"
    if not re.search(r"\bDTEST0\b", check, re.I):
        return "NOT_APPLICABLE", "DFT Check does not observe DTEST0"
    resolution = contract.get("pinResolution")
    if not isinstance(resolution, dict) or resolution.get("resolutionState") != "RESOLVED":
        return "UNKNOWN", "DTEST0 physical pin is not resolved in strategy"
    signal = str(resolution.get("logicalSignal") or "").upper()
    physical = str(resolution.get("physicalDutPin") or "").upper()
    if "DTEST0" not in signal or physical != "NQON":
        return "UNKNOWN", "DFT DTEST0 and strategy nQON mapping disagree"
    return "REQUIRED", "DFT observes DTEST0, resolved to the nQON open-drain pad"


def _workflow_evidence(contract, dft, schematic, path_proofs, requirements, manifest=None):
    """Show what was recomputed, and name steps outside machine coverage."""
    physical = check_contract(contract, path_proofs, final_four_only=True)
    schematic_reads = schematic.get("readSources") or []
    proof_reads = path_proofs.get("readSources") or []
    schematic_csv = next((x for x in schematic_reads if isinstance(x, dict)
                          and str(x.get("path", "")).endswith("/Dali-SCH.csv")), None)
    proof_csv = next((x for x in proof_reads if isinstance(x, dict)
                      and str(x.get("path", "")).endswith("/Dali-SCH.csv")), None)
    pins_agree = bool(schematic_csv and proof_csv and schematic_csv.get("sha256")
                      and schematic_csv.get("sha256") == proof_csv.get("sha256"))
    manifest_dft = ((manifest.get("canonicalInputs") or {}).get("dft") or {}) if isinstance(manifest, dict) else {}
    manifest_rows = manifest_dft.get("rawRows") or []
    manifest_dft_agrees = (manifest_dft.get("sha256") == dft.get("sourceSha256")
                           and any(isinstance(row, dict) and row.get("Item") == dft.get("tm")
                                   and all(row.get(key) == value for key, value in (dft.get("rawIntent") or {}).items())
                                   for row in manifest_rows)) if manifest is not None else None
    candidate_pairs = {}
    for pair in path_proofs.get("kelvin_pairs") or []:
        if not isinstance(pair, dict) or pair.get("status") != "PASS":
            continue
        endpoint = str(pair.get("dut_base") or "").upper()
        source = pair.get("source_pair")
        if endpoint and isinstance(source, str):
            candidate_pairs.setdefault(endpoint, set()).add(source)
    selections = []
    for item in contract.get("resourceAllocation") or []:
        if not isinstance(item, dict):
            continue
        selections.append({
            "dutPin": item.get("dutPin"), "sourceTable": item.get("sourceTable"),
            "sourcePorts": item.get("ports"),
            "physicalProofs": [{"sourcePort": x.get("sourcePort"), "dutPin": x.get("dutPin"),
                                "requiredOn": x.get("requiredOn"), "locator": x.get("locator")}
                               for x in item.get("physicalProofs") or [] if isinstance(x, dict)],
        })
    steps = [
        {"step": 1, "coverage": "DECLARED_ONLY", "detail": "classification is signed in strategy; project and parameter choice is not independently rederived"},
        {"step": 2, "coverage": "RECOMPUTED", "detail": "canonical accepted Kelvin candidate pairs are enumerated by DUT pin"},
        {"step": 3, "coverage": "NOT_FORMALIZED", "detail": "instrument scarcity and electrical operating range need machine-readable rules"},
        {"step": 4, "coverage": "RECOMPUTED", "detail": "selected source ports and DUT legs are checked against canonical path proofs"},
        {"step": 5, "coverage": "PARTIAL", "detail": "requiredOn closure is recomputed; shortest-path preference is not proved"},
        {"step": 6, "coverage": "PARTIAL", "detail": "duplicate occupancy and relay-state conflicts are checked; analog compatibility is unknown"},
        {"step": 7, "coverage": "PARTIAL", "detail": "path conflict need is identified; a timed execution schedule is not proved"},
        {"step": 8, "coverage": "RECOMPUTED", "detail": "path and declared functional relay closure are compared with final SetOn"},
    ]
    return {
        "pinnedInputs": {
            "dftWorkbookPlaintextSha256": dft.get("sourceSha256"),
            "manifestDftPlaintextSha256": manifest_dft.get("sha256"),
            "manifestDftRowAgrees": manifest_dft_agrees,
            "schematicCsvPlaintextSha256": schematic_csv.get("sha256") if schematic_csv else None,
            "pathProofCsvPlaintextSha256": proof_csv.get("sha256") if proof_csv else None,
            "schematicAndProofSourceAgree": pins_agree,
            "schematicSources": schematic_reads,
            "pathProofSources": proof_reads,
        },
        "candidateSourcePairs": {pin: sorted(pairs) for pin, pairs in sorted(candidate_pairs.items())
                                 if pin in {str(x.get('dutPin', '')).upper() for x in selections}},
        "selectedPaths": selections,
        "functionalRelayDecisions": requirements,
        "relayClosure": {"pathRequiredOn": physical["pathRequiredOnUnion"],
                         "declaredFunctionalOn": physical["functionalRelayUnion"],
                         "finalSetOn": physical["setOnRelayUnion"]},
        "conflictAndTiming": {
            "selectedPathStatus": physical["status"],
            "conflicts": physical["conflicts"], "unknown": physical["unknown"],
            "timeMultiplexing": ("NEEDS_DESIGN_OR_RESELECTION" if physical["status"] == "CONFLICT"
                                 else "UNKNOWN" if physical["status"] == "UNKNOWN"
                                 else "NOT_REQUIRED_BY_PROVEN_PATHS"),
            "globalElectricalConflict": "UNKNOWN",
            "reason": "distinct instruments' voltage, current, impedance, and timing compatibility are not formalized",
        },
        "eightStepCoverage": steps,
    }


def check_functional_relays(contract, dft, schematic, relays_rule, checklist_rule,
                            path_proofs=None, manifest=None):
    """Return applicability and final-closure verdict for K13 and K65."""
    signed = (contract.get("tm") == dft.get("tm") and contract.get("verdict") == "deliverable_ready"
              and dft.get("verdict") in (None, "generated", "deliverable_ready")
              and re.fullmatch(r"[0-9a-fA-F]{64}", str(dft.get("sourceSha256") or "")) is not None
              and isinstance(dft.get("rawIntent"), dict))
    if manifest is not None:
        manifest_dft = ((manifest.get("canonicalInputs") or {}).get("dft") or {}) if isinstance(manifest, dict) else {}
        rows = manifest_dft.get("rawRows") or []
        signed = signed and manifest_dft.get("sha256") == dft.get("sourceSha256") and any(
            isinstance(row, dict) and row.get("Item") == dft.get("tm")
            and all(row.get(key) == value for key, value in (dft.get("rawIntent") or {}).items())
            for row in rows)
    closure, closure_problem = _closure(contract)
    raw = dft.get("rawIntent") if isinstance(dft.get("rawIntent"), dict) else {}
    rules = {
        13: [
            _rule_line(relays_rule, r"\*\*总原则 \(FR-001\)\*\*.*Cap", "knowledge/hardware/relays.md"),
            _rule_line(checklist_rule, r"\*\*总原则 \(FR-001,.*Cap", "knowledge/standards/relay-checklist.md"),
            _map_relay(schematic, "VBAT", "稳压", 13),
        ],
        65: [
            _rule_line(relays_rule, r"DALI 实例.*K65_nQON_PU", "knowledge/hardware/relays.md"),
            _rule_line(relays_rule, r"观测开漏输出.*必须闭合", "knowledge/hardware/relays.md"),
            _map_relay(schematic, "nQON", "上拉", 65),
        ],
    }
    classifications = {13: _classify_k13(raw), 65: _classify_k65(raw, contract)}
    requirements = []
    for number in (13, 65):
        applicability, reason = classifications[number]
        evidence = [item for item in rules[number] if item]
        if not signed:
            applicability, reason = "UNKNOWN", "strategy and DFT are not matching signed projections"
        elif applicability == "REQUIRED" and len(evidence) != len(rules[number]):
            applicability, reason = "UNKNOWN", "the current relay rule or schematic map is missing"
        if applicability == "REQUIRED":
            closure_state = "UNKNOWN" if closure is None else ("PRESENT" if number in closure else "MISSING")
        else:
            closure_state = "NOT_APPLICABLE"
        requirements.append({
            "relay": f"K{number}", "applicability": applicability,
            "closure": closure_state, "reason": reason,
            "evidence": evidence,
            "dftEvidence": f"{dft.get('tm', '<unknown>')} dft-meta.json:rawIntent",
        })
    if any(item["closure"] == "MISSING" for item in requirements):
        status = "MISSING"
    elif any(item["applicability"] == "UNKNOWN" or item["closure"] == "UNKNOWN" for item in requirements):
        status = "UNKNOWN"
    else:
        status = "PASS"
    result = {"status": status, "scope": "K13/K65 functional requirements and declared SetOn closure",
            "tm": contract.get("tm"),
            "finalSetOn": sorted(closure) if closure is not None else None,
            "closureProblem": closure_problem, "requirements": requirements}
    if path_proofs is not None:
        workflow = _workflow_evidence(contract, dft, schematic, path_proofs, requirements, manifest)
        result["workflowEvidence"] = workflow
        if not workflow["pinnedInputs"]["schematicAndProofSourceAgree"]:
            result["status"] = "UNKNOWN"
            result["sourceProblem"] = "schematic map and path proofs do not have the same canonical CSV hash"
        elif workflow["conflictAndTiming"]["selectedPathStatus"] == "CONFLICT" and result["status"] == "PASS":
            result["status"] = "CONFLICT"
        elif workflow["conflictAndTiming"]["selectedPathStatus"] == "UNKNOWN" and result["status"] == "PASS":
            result["status"] = "UNKNOWN"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("dft_meta", type=Path)
    parser.add_argument("schematic_map", type=Path)
    parser.add_argument("--path-proofs", type=Path,
                        default=Path("project/DALI/Output_Global_Material/schematic/Path-Proofs.json"))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--relays-rule", type=Path, default=Path("knowledge/hardware/relays.md"))
    parser.add_argument("--checklist-rule", type=Path, default=Path("knowledge/standards/relay-checklist.md"))
    args = parser.parse_args()
    result = check_functional_relays(
        json.loads(args.contract.read_text(encoding="utf-8")),
        json.loads(args.dft_meta.read_text(encoding="utf-8")),
        json.loads(args.schematic_map.read_text(encoding="utf-8")),
        args.relays_rule.read_text(encoding="utf-8"),
        args.checklist_rule.read_text(encoding="utf-8"),
        json.loads(args.path_proofs.read_text(encoding="utf-8")),
        json.loads(args.manifest.read_text(encoding="utf-8")) if args.manifest else None,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    raise SystemExit({"PASS": 0, "MISSING": 1, "UNKNOWN": 2, "CONFLICT": 3}[result["status"]])


if __name__ == "__main__":
    main()
