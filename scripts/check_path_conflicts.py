"""Check a strategy's simultaneous routes against canonical schematic proofs.

Only facts present in Path-Proofs and the signed strategy are decidable here.
The electrical compatibility of distinct instruments remains UNKNOWN unless
an explicit, machine-readable exclusion is provided by the proof artifact.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


def _relay_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    match = re.fullmatch(r"K?(\d+)", str(value or ""), re.I)
    return int(match.group(1)) if match else None


def _relay_set(value, label, unknown):
    if not isinstance(value, list):
        unknown.append(f"{label} is missing or is not a list")
        return set()
    result = set()
    for item in value:
        number = _relay_id(item)
        if number is None:
            unknown.append(f"{label} contains an unrecognized relay: {item!r}")
        else:
            result.add(number)
    return result


def _state(value):
    value = str(value or "").upper()
    if value in ("ON", "RELAY-ON"):
        return "ON"
    if value in ("NC", "RELAY-NC", "OFF", "RELAY-OFF"):
        return "OFF"
    return None


def _role(proof):
    source = (proof.get("source_meta") or {}).get("role")
    dut = proof.get("dut_role")
    return source, dut


def check_contract(contract, proof_data, *, final_four_only=False):
    """Return a deterministic report; UNKNOWN facts never become a clean PASS.

    ``status`` concerns the declared paths and relay closure. Separate
    ``electricalCompatibility`` records the limit of those proofs, so a
    formally proved route is not blocked merely because analog operating
    ranges are absent from the schematic artifact.
    """
    conflicts, unknown = [], []
    selected = contract.get("resourceAllocation")
    accepted = proof_data.get("accepted_path_proofs")
    if proof_data.get("status") != "PASS" or not isinstance(accepted, list):
        unknown.append("canonical Path-Proofs is unavailable or not PASS")
        accepted = []
    if not isinstance(selected, list):
        unknown.append("strategy resourceAllocation is missing")
        selected = []

    lookup = defaultdict(list)
    for proof in accepted:
        if isinstance(proof, dict):
            lookup[(proof.get("source_port"), proof.get("dut_pin"))].append(proof)

    relay_states = defaultdict(set)
    source_owners = defaultdict(set)
    pair_owners = defaultdict(set)
    endpoint_path_on = {}
    endpoint_functional_on = {}
    selected_pairs = set()
    selected_sources = set()

    for item in selected:
        if not isinstance(item, dict):
            unknown.append("resourceAllocation contains a non-object entry")
            continue
        endpoint = str(item.get("dutPin") or "")
        if not endpoint:
            unknown.append("resourceAllocation entry has no dutPin")
            continue
        proofs = item.get("physicalProofs")
        if not isinstance(proofs, list) or not proofs:
            unknown.append(f"{endpoint} has no physicalProofs")
            continue
        declared_ports = item.get("ports")
        if not isinstance(declared_ports, list):
            unknown.append(f"{endpoint} has no source ports")
            declared_ports = []
        proof_ports = []
        actual_on = set()
        roles = []
        endpoint_pairs = set()
        for entry in proofs:
            if not isinstance(entry, dict):
                unknown.append(f"{endpoint} has an invalid physical proof entry")
                continue
            source, dut = entry.get("sourcePort"), entry.get("dutPin")
            matches = lookup.get((source, dut), [])
            if len(matches) != 1:
                unknown.append(f"{endpoint}: {source}->{dut} has {len(matches)} canonical proofs; expected one")
                continue
            proof = matches[0]
            validation = proof.get("validation") or {}
            if not all(proof.get("terminal_stop") is True and validation.get(key) is True
                       for key in ("terminal_stop", "role_match", "cbit_complete")):
                unknown.append(f"{endpoint}: {source}->{dut} is not a complete PASS proof")
            if str(proof.get("dut_base", "")).upper() != endpoint.upper():
                conflicts.append(f"{endpoint}: {source}->{dut} ends at another DUT pin")
            source_role, dut_role = _role(proof)
            if source_role != dut_role or dut_role not in ("F", "S"):
                unknown.append(f"{endpoint}: {source}->{dut} has no proven Force/Sense match")
            roles.append(dut_role)
            proof_ports.append(source)
            selected_sources.add(source)
            source_owners[source].add(endpoint.upper())
            pair_key = (proof.get("source_meta") or {}).get("pair_key")
            if pair_key:
                pair_owners[pair_key].add(endpoint.upper())
                selected_pairs.add(pair_key)
                endpoint_pairs.add(pair_key)
            else:
                unknown.append(f"{endpoint}: {source}->{dut} has no source pair key")
            required_on = _relay_set(proof.get("required_on"), f"{source}->{dut} required_on", unknown)
            declared_on = _relay_set(entry.get("requiredOn"), f"{endpoint} declared requiredOn", unknown)
            if declared_on != required_on:
                conflicts.append(f"{endpoint}: {source}->{dut} requiredOn differs from canonical proof")
            actual_on |= required_on
            for relay in proof.get("path") or []:
                if not isinstance(relay, dict):
                    unknown.append(f"{endpoint}: {source}->{dut} has invalid relay path data")
                    continue
                number = _relay_id(relay.get("relay_number"))
                state = _state(relay.get("state"))
                if number is None or state is None:
                    unknown.append(f"{endpoint}: {source}->{dut} has incomplete relay state")
                    continue
                relay_states[number].add(state)
        if sorted(proof_ports) != sorted(declared_ports):
            conflicts.append(f"{endpoint}: ports do not match selected physicalProofs")
        if sorted(roles) != ["F", "S"]:
            unknown.append(f"{endpoint}: selected paths do not prove one Force and one Sense leg")
        if len(endpoint_pairs) > 1:
            conflicts.append(f"{endpoint}: Force and Sense use different source pairs")
        declared_union = _relay_set(item.get("requiredActuations"), f"{endpoint} requiredActuations", unknown)
        if declared_union != actual_on:
            conflicts.append(f"{endpoint}: requiredActuations differs from path required_on union")
        endpoint_path_on[endpoint] = actual_on

        functional_on = set()
        for relay in item.get("functionalRelays") or []:
            if not isinstance(relay, dict):
                unknown.append(f"{endpoint}: invalid functional relay")
                continue
            number = _relay_id(relay.get("id"))
            state = _state(relay.get("state"))
            if number is None or state is None:
                unknown.append(f"{endpoint}: functional relay has incomplete state")
                continue
            if not final_four_only:
                relay_states[number].add(state)
            if state == "ON":
                functional_on.add(number)
        endpoint_functional_on[endpoint] = functional_on

    for source, owners in sorted(source_owners.items()):
        if len(owners) > 1:
            conflicts.append(f"source port {source} is assigned to multiple DUT pins: {', '.join(sorted(owners))}")
    for pair, owners in sorted(pair_owners.items()):
        if len(owners) > 1:
            conflicts.append(f"source pair {pair} is assigned to multiple DUT pins: {', '.join(sorted(owners))}")
    for number, states in sorted(relay_states.items()):
        if len(states) > 1:
            conflicts.append(f"K{number} needs both ON and OFF in the same configuration")

    # Optional explicit exclusions are authoritative only when carried by the
    # canonical proof artifact. The current DALI proof file has no such list.
    exclusions = (proof_data.get("contracts") or {}).get("mutually_exclusive_source_pairs", [])
    if not isinstance(exclusions, list):
        unknown.append("canonical source-pair exclusions have invalid structure")
    else:
        for pair in exclusions:
            if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) for x in pair):
                unknown.append("canonical source-pair exclusion has invalid structure")
            elif set(pair) <= selected_pairs and not final_four_only:
                conflicts.append(f"canonical source pairs are mutually exclusive: {pair[0]}, {pair[1]}")

    path_union = set().union(*endpoint_path_on.values()) if endpoint_path_on else set()
    functional_union = set().union(*endpoint_functional_on.values()) if endpoint_functional_on else set()
    total_union = path_union | functional_union
    summary = contract.get("resourceSummary") or {}
    if not isinstance(summary, dict):
        summary = {}
    for key, expected in (("pathRequiredOnUnion", path_union),
                          ("functionalRelayUnion", functional_union),
                          ("setOnRelayUnion", total_union)):
        if key in summary:
            declared = _relay_set(summary[key], f"resourceSummary.{key}", unknown)
            if declared != expected:
                conflicts.append(f"resourceSummary.{key} differs from selected relay closure")
        elif key == "setOnRelayUnion":
            unknown.append("resourceSummary.setOnRelayUnion is missing")

    groups = contract.get("relayGroups") or []
    if not isinstance(groups, list):
        unknown.append("relayGroups is not a list")
        groups = []
    group_union = set()
    for group in groups:
        if not isinstance(group, dict):
            unknown.append("relayGroups contains an invalid entry")
            continue
        endpoint = group.get("endpointId")
        declared = _relay_set(group.get("setOnRelayIds"), f"relayGroup {group.get('groupId')} setOnRelayIds", unknown)
        group_union |= declared
        if not declared <= total_union:
            conflicts.append(f"relayGroup {group.get('groupId')} contains relay outside selected closure")
        if endpoint:
            endpoint_closure = endpoint_path_on.get(endpoint, set()) | endpoint_functional_on.get(endpoint, set())
            if not declared <= endpoint_closure:
                conflicts.append(f"relayGroup {group.get('groupId')} contains relay outside {endpoint} closure")
    if groups and group_union != total_union:
        conflicts.append("relayGroups setOnRelayIds union differs from selected relay closure")

    # Exact source-end reuse and selected-path relay-state contradictions are
    # decidable. Broader analog compatibility is absent from Path-Proofs.
    electrical = "UNKNOWN" if len(selected_pairs) > 1 else "NOT_APPLICABLE"
    status = "CONFLICT" if conflicts else ("UNKNOWN" if unknown else "PASS")
    return {
        "status": status,
        "scope": "selected physical paths and declared relay closure",
        "conflicts": sorted(set(conflicts)),
        "unknown": sorted(set(unknown)),
        "electricalCompatibility": electrical,
        "functionalRelayCompleteness": "UNKNOWN",
        "functionalRelayReason": (
            "Path-Proofs contains physical routes but no machine-readable list of "
            "functional relays required by each test; declared functional relays "
            "are checked for state and closure, but omissions cannot be detected"
        ),
        "pathRequiredOnUnion": sorted(path_union),
        "functionalRelayUnion": sorted(functional_union),
        "setOnRelayUnion": sorted(total_union),
        "selectedSourcePorts": sorted(selected_sources),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("path_proofs", type=Path)
    args = parser.parse_args()
    result = check_contract(json.loads(args.contract.read_text(encoding="utf-8")),
                            json.loads(args.path_proofs.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit({"PASS": 0, "CONFLICT": 1, "UNKNOWN": 2}[result["status"]])


if __name__ == "__main__":
    main()
