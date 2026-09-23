"""Recompute route candidates and conflict fallbacks from signed material.

Current DALI material lacks routingConditions and source exclusivity metadata;
the report therefore remains UNKNOWN even when a structural route is found.
No exploratory route is represented as a completed eight-step design.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

try:
    from scripts.check_functional_relays import check_functional_relays
except ModuleNotFoundError:
    from check_functional_relays import check_functional_relays


SCARCE_TYPES = {"FPVIe", "QVM"}
NON_SCARCE_TYPES = {"FOVI", "FXVIe_PLUS", "ACM200"}


def _candidate(pair, lookup):
    force = pair.get("force_proof") or {}
    sense = pair.get("sense_proof") or {}
    f_matches = lookup.get((force.get("source"), force.get("dut")), [])
    s_matches = lookup.get((sense.get("source"), sense.get("dut")), [])
    if len(f_matches) != 1 or len(s_matches) != 1:
        return None
    legs = (f_matches[0], s_matches[0])
    if [leg.get("dut_role") for leg in legs] != ["F", "S"]:
        return None
    if any(not all((leg.get("validation") or {}).get(k) is True for k in
                   ("terminal_stop", "role_match", "cbit_complete")) for leg in legs):
        return None
    source_pairs = {(leg.get("source_meta") or {}).get("pair_key") for leg in legs}
    if len(source_pairs) != 1 or None in source_pairs:
        return None
    states = {}
    for leg in legs:
        for relay in leg.get("path") or []:
            number, state = relay.get("relay_number"), relay.get("state")
            if not isinstance(number, int) or state not in ("ON", "NC"):
                return None
            normalized = "ON" if state == "ON" else "OFF"
            if number in states and states[number] != normalized:
                return None
            states[number] = normalized
    source_type = (legs[0].get("source_meta") or {}).get("type")
    if source_type != (legs[1].get("source_meta") or {}).get("type"):
        return None
    return {
        "dutPin": pair.get("dut_base"), "sourcePair": next(iter(source_pairs)),
        "sourceType": source_type,
        "sourcePorts": [leg.get("source_port") for leg in legs],
        "dutLegs": [leg.get("dut_pin") for leg in legs],
        "requiredOn": sorted(number for number, state in states.items() if state == "ON"),
        "requiredOff": sorted(number for number, state in states.items() if state == "OFF"),
        "relayStates": states,
        "contactCount": sum(len(leg.get("path") or []) for leg in legs),
        "locators": ["Path-Proofs.json accepted_path_proofs[source_port=%s;dut_pin=%s]" %
                     (leg.get("source_port"), leg.get("dut_pin")) for leg in legs],
    }


def _routing_conditions(dft, endpoints, proof_data):
    conditions = dft.get("routingConditions")
    missing = []
    if not isinstance(conditions, dict):
        conditions = {}
        missing.append("dft.routingConditions: differentialPairs, highCurrentEndpoints, endpointPriority, simultaneousGroups, allowedSourceTypes")
    required = ("differentialPairs", "highCurrentEndpoints", "endpointPriority",
                "simultaneousGroups", "allowedSourceTypes")
    for key in required:
        if key not in conditions and not any(x.startswith("dft.routingConditions:") for x in missing):
            missing.append("dft.routingConditions." + key)
    priority = conditions.get("endpointPriority")
    if not isinstance(priority, list) or set(priority) != set(endpoints) or len(priority) != len(endpoints):
        missing.append("endpointPriority must list every DUT endpoint exactly once")
        priority = endpoints
    groups = conditions.get("simultaneousGroups")
    if not isinstance(groups, list) or not all(isinstance(g, list) for g in groups) or sorted(
        x for g in groups for x in g) != sorted(endpoints):
        missing.append("simultaneousGroups must partition all DUT endpoints")
        groups = [endpoints]
    allowed = conditions.get("allowedSourceTypes")
    if not isinstance(allowed, dict) or any(not isinstance(allowed.get(x), list) or not allowed[x] for x in endpoints):
        missing.append("allowedSourceTypes must name compatible instrument types for every endpoint")
        allowed = {}
    differentials = conditions.get("differentialPairs")
    if not isinstance(differentials, list):
        differentials = []
    high_current = conditions.get("highCurrentEndpoints")
    if not isinstance(high_current, list):
        high_current = []
    exclusions = (proof_data.get("contracts") or {}).get("exclusive_source_pairs")
    if not isinstance(exclusions, list):
        missing.append("Path-Proofs.contracts.exclusive_source_pairs (machine-readable source occupancy)")
        exclusions = []
    return conditions, priority, groups, allowed, differentials, high_current, set(exclusions), sorted(set(missing))


def _rank(candidate, pin, differentials, high_current):
    scarce = pin in high_current or any(pin in pair for pair in differentials if isinstance(pair, list))
    preferred = SCARCE_TYPES if scarce else NON_SCARCE_TYPES
    return (0 if candidate["sourceType"] in preferred else 1,
            candidate["contactCount"], candidate["sourcePair"])


def _conflict(candidate, chosen, exclusive_pairs):
    for previous in chosen.values():
        overlap = set(candidate["sourcePorts"]) & set(previous["sourcePorts"])
        if overlap:
            return "source port already assigned: " + ", ".join(sorted(overlap))
        if (candidate["sourcePair"] == previous["sourcePair"]
                and candidate["sourcePair"] in exclusive_pairs):
            return "exclusive source pair already assigned: " + candidate["sourcePair"]
        for relay, state in candidate["relayStates"].items():
            if relay in previous["relayStates"] and previous["relayStates"][relay] != state:
                return "K%s needs both ON and OFF" % relay
    return None


def _search_group(group, priority, candidates, exclusive_pairs, functional_required):
    order = [pin for pin in priority if pin in group]
    decisions = []
    def visit(index, chosen):
        if index == len(order):
            return dict(chosen)
        pin = order[index]
        for candidate in candidates.get(pin, []):
            functional_conflict = sorted(set(candidate["requiredOff"]) & functional_required)
            conflict = ("functional relay must be ON but route requires OFF: " +
                        ", ".join("K%s" % x for x in functional_conflict)) if functional_conflict else None
            conflict = conflict or _conflict(candidate, chosen, exclusive_pairs)
            if conflict:
                decisions.append({"dutPin": pin, "sourcePair": candidate["sourcePair"],
                                  "decision": "REJECT", "reason": conflict})
                continue
            chosen[pin] = candidate
            result = visit(index + 1, chosen)
            if result is not None:
                decisions.append({"dutPin": pin, "sourcePair": candidate["sourcePair"],
                                  "decision": "SELECT", "reason": "first feasible ranked candidate"})
                return result
            decisions.append({"dutPin": pin, "sourcePair": candidate["sourcePair"],
                              "decision": "BACKTRACK", "reason": "no feasible lower-priority endpoint route"})
            del chosen[pin]
        return None
    return visit(0, {}), decisions


def search_routes(contract, dft, schematic, proof_data, relays_rule, checklist_rule, manifest):
    functional = check_functional_relays(contract, dft, schematic, relays_rule,
                                         checklist_rule, proof_data, manifest)
    endpoints = [str(x.get("dutPin")) for x in contract.get("resourceAllocation") or []
                 if isinstance(x, dict) and x.get("dutPin")]
    conditions, priority, groups, allowed, differentials, high_current, exclusive, missing = (
        _routing_conditions(dft, endpoints, proof_data))
    lookup = defaultdict(list)
    for proof in proof_data.get("accepted_path_proofs") or []:
        if isinstance(proof, dict):
            lookup[(proof.get("source_port"), proof.get("dut_pin"))].append(proof)
    candidates = {pin: [] for pin in endpoints}
    for pair in proof_data.get("kelvin_pairs") or []:
        if not isinstance(pair, dict) or pair.get("status") != "PASS":
            continue
        pin = str(pair.get("dut_base") or "")
        if pin.upper() not in {x.upper() for x in endpoints}:
            continue
        pin = next(x for x in endpoints if x.upper() == pin.upper())
        candidate = _candidate(pair, lookup)
        if candidate is not None:
            if allowed and candidate["sourceType"] not in allowed.get(pin, []):
                candidate["eligibility"] = "REJECT: instrument type not declared compatible"
            else:
                candidate["eligibility"] = "CONDITIONALLY_ELIGIBLE" if missing else "ELIGIBLE"
            candidate["rank"] = list(_rank(candidate, pin, differentials, high_current))
            candidate["rankAuthority"] = "PROVISIONAL" if missing else "SIGNED_CONDITIONS"
            candidates[pin].append(candidate)
    for pin in endpoints:
        candidates[pin].sort(key=lambda item: item["rank"])
        if not candidates[pin]:
            missing.append("no canonical Force/Sense PASS route for " + pin)

    required_functional = {int(item["relay"][1:]) for item in functional["requirements"]
                           if item["applicability"] == "REQUIRED"}
    if any(item["applicability"] == "UNKNOWN" for item in functional["requirements"]):
        missing.append("functional relay applicability is UNKNOWN")
    group_results = []
    for group in groups:
        eligible = {pin: [x for x in candidates[pin] if not x["eligibility"].startswith("REJECT")]
                    for pin in group}
        chosen, decisions = _search_group(group, priority, eligible, exclusive, required_functional)
        route_on = sorted({relay for candidate in (chosen or {}).values()
                           for relay in candidate["requiredOn"]})
        closure = sorted(set(route_on) | required_functional) if chosen is not None else None
        group_results.append({
            "simultaneousEndpoints": group,
            "chosen": {pin: value["sourcePair"] for pin, value in (chosen or {}).items()},
            "fallbackTrace": decisions,
            "pathRequiredOn": route_on if chosen is not None else None,
            "functionalRequiredOn": sorted(required_functional),
            "proposedSetOn": closure,
            "status": "FOUND_STRUCTURAL_COMBINATION" if chosen is not None else "NO_STRUCTURAL_COMBINATION",
        })
    signed_selection = {str(item.get("dutPin")): sorted(
        str(x.get("sourcePort")) for x in item.get("physicalProofs") or [] if isinstance(x, dict))
        for item in contract.get("resourceAllocation") or [] if isinstance(item, dict)}
    proposed_selection = {pin: sorted(value["sourcePorts"])
                          for group in group_results for pin, pair in group["chosen"].items()
                          for value in candidates[pin] if value["sourcePair"] == pair}
    complete_inputs = not missing and functional["status"] == "PASS"
    all_found = all(group["status"] == "FOUND_STRUCTURAL_COMBINATION" for group in group_results)
    if not complete_inputs:
        status = "UNKNOWN"
        comparison = "INDETERMINATE"
    elif not all_found:
        status = "BLOCKED"
        comparison = "NO_FEASIBLE_COMBINATION"
    else:
        comparison = "MATCH" if signed_selection == proposed_selection else "MISMATCH"
        status = "PASS" if comparison == "MATCH" else "MISMATCH"
    return {
        "status": status, "scope": "candidate route search under explicit routingConditions",
        "missingMachineFields": sorted(set(missing)),
        "signedInputHashes": functional.get("workflowEvidence", {}).get("pinnedInputs"),
        "executionBoundary": {"groups": groups, "authoritative": "simultaneousGroups" in conditions,
                              "note": "different groups may be time-multiplexed; one group must work simultaneously"},
        "endpointPriority": priority,
        "candidates": candidates,
        "functionalRelays": functional["requirements"],
        "groupSearch": group_results,
        "strategyComparison": comparison,
        "signedSourcePorts": signed_selection,
        "proposedSourcePorts": proposed_selection,
        "globalElectricalConflict": "UNKNOWN",
        "eightStepCoverage": functional.get("workflowEvidence", {}).get("eightStepCoverage"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("dft_meta", type=Path)
    parser.add_argument("schematic_map", type=Path)
    parser.add_argument("path_proofs", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    load = lambda p: json.loads(p.read_text(encoding="utf-8"))
    result = search_routes(load(args.contract), load(args.dft_meta), load(args.schematic_map),
                           load(args.path_proofs),
                           Path("knowledge/hardware/relays.md").read_text(encoding="utf-8"),
                           Path("knowledge/standards/relay-checklist.md").read_text(encoding="utf-8"),
                           load(args.manifest))
    print(json.dumps(result, ensure_ascii=True, indent=2))
    raise SystemExit({"PASS": 0, "MISMATCH": 1, "BLOCKED": 2, "UNKNOWN": 3}[result["status"]])


if __name__ == "__main__":
    main()
