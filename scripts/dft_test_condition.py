"""Deterministic DFT test-condition extraction from one OVERVIEW row."""
from __future__ import annotations

import re

VSET = re.compile(r"vset\[([^,\]]+)\s*,\s*([^\]]*)\]", re.I)
SCAN = re.compile(r"ramp\s+([^:,\s]+)\s*:\s*([+-]?[\d.]+)\s*->\s*([+-]?[\d.]+)", re.I)
INT_SCAN = re.compile(r"(?:INT\s+)?(rise|fall)\s*:\s*([+-]?[\d.]+)\s*->\s*([+-]?[\d.]+)", re.I)
# HELPER also declares ramps and internal transitions in words, without numeric
# endpoints (for example "ramp VBUS, INT toggle"). Those rows already carry
# hasRamp=true from their ordered vset pairs, so the declared intent must be
# reported as DECLARED; the missing endpoints stay NOT_DECLARED rather than
# being inferred.
SCAN_DECLARED = re.compile(r"\bramp\s+([^:,\s]+)", re.I)
INT_DECLARED = re.compile(r"\b(?:INT\s+)?(rise|fall|toggle)\b", re.I)


def vsets(row: dict) -> list[dict]:
    out: list[dict] = []
    source_order = 0
    for column in ("Code1", "Code2", "Code3", "Dynamic"):
        for order, match in enumerate(VSET.finditer(str(row.get(column, ""))), 1):
            source_order += 1
            args = [value.strip() for value in match.group(2).split(",")]
            out.append({
                "column": column,
                "order": order,
                "sourceOrder": source_order,
                "pin": match.group(1).strip(),
                "args": args,
                "raw": match.group(0),
                "directPowerOn": len(args) > 1 and args[1] == "100e-6",
            })
    return out


def dynamic_pins(row: dict) -> list[str]:
    """Dynamic is a declared pin list, not an inference from later vset commands."""
    raw = str(row.get("Dynamic", "")).strip()
    if not raw:
        return []
    return list(dict.fromkeys(re.findall(r"[A-Za-z][A-Za-z0-9_]*", raw)))


def scan_intent(helper: str, has_ramp: bool = True) -> dict:
    """Declare the HELPER ramp intent, with or without numeric endpoints.

    `has_ramp` is the ordered-vset evidence for a scan. The condition schema
    requires DECLARED whenever it is true and refuses DECLARED when it is false,
    so the declared state and the evidence are reconciled here instead of
    leaving the two halves of the handoff contradicting each other.
    """
    entries = []
    for match in SCAN.finditer(helper):
        entries.append({"kind": "ramp", "pin": match.group(1), "from": match.group(2), "to": match.group(3)})
    for match in INT_SCAN.finditer(helper):
        entries.append({"kind": "internal", "direction": match.group(1).upper(), "from": match.group(2), "to": match.group(3)})
    declared_pins = {entry["pin"].lower() for entry in entries if entry["kind"] == "ramp"}
    for match in SCAN_DECLARED.finditer(helper):
        pin = match.group(1)
        if pin.lower() not in declared_pins:
            declared_pins.add(pin.lower())
            entries.append({"kind": "ramp", "pin": pin, "from": "NOT_DECLARED", "to": "NOT_DECLARED"})
    directions = {entry["direction"] for entry in entries if entry["kind"] == "internal"}
    for match in INT_DECLARED.finditer(helper):
        direction = match.group(1).upper()
        if direction not in directions:
            directions.add(direction)
            entries.append({"kind": "internal", "direction": direction, "from": "NOT_DECLARED", "to": "NOT_DECLARED"})
    if not has_ramp:
        # No ordered ramp vset pair exists, so nothing may claim a scan; the
        # HELPER text itself is still preserved verbatim in `raw`.
        entries = []
    return {"state": "DECLARED" if entries else "NOT_DECLARED", "source": "HELPER", "raw": helper, "entries": entries}


def derive(row: dict) -> dict:
    commands = vsets(row)
    code1 = [item for item in commands if item["column"] == "Code1"]
    direct_power = [item for item in commands if item["directPowerOn"]]
    later_vsets = [item for item in commands if item["column"] in ("Code2", "Code3")]
    check = str(row.get("Check", ""))
    notes = str(row.get("Notes", ""))
    helper = str(row.get("HELPER", row.get("Helper", ""))).replace("：", ":")
    description = str(row.get("Description", ""))
    text = " ".join(str(row.get(key, "")) for key in ("Name", "Description", "Notes", "Test", "Special", "Dynamic", "HELPER", "Helper"))
    pins: list[str] = []
    for command in commands:
        if command["pin"] not in pins:
            pins.append(command["pin"])
    quantity = "CURRENT" if re.search(r"\bI\s*\(", check, re.I) else ("VOLTAGE" if re.search(r"\bV\s*\(", check, re.I) else "NOT_DECLARED")
    toggle = bool(re.search(r"toggle|dtest|dest", text + " " + check, re.I))
    ramps = []
    for pin in dict.fromkeys(command["pin"] for command in later_vsets):
        sequence = [command for command in later_vsets if command["pin"] == pin]
        if len(sequence) >= 2:
            ramps.append({"pin": pin, "orderedVset": sequence})
    internal_comparison = bool(re.search(r"VAC\s*-\s*VDIO", description, re.I) and re.search(r"VBAT", description, re.I))
    source_result_types = ["Rise", "Fall"] if toggle and bool(ramps) else ["Measurement"]
    result_provenance = [{"type": kind, "state": "SOURCE_DECLARED"} for kind in source_result_types]
    if toggle and bool(ramps):
        result_provenance.append({"type": "Hys", "state": "DERIVED", "derivation": "rising threshold minus falling threshold"})

    # The v5 gate consumes a compact six-field contract.  Preserve the rich
    # deterministic facts under *Details/rawPowerSequence, but never put those
    # legacy shapes in the six canonical fields.
    gate_power_sequence = []
    for command in commands:
        args = command["args"]
        if not args:
            continue
        try:
            numeric_value = float(args[0])
        except (TypeError, ValueError):
            continue
        value = int(numeric_value) if numeric_value.is_integer() else numeric_value
        try:
            status = int(args[2]) if len(args) > 2 else 0
        except (TypeError, ValueError):
            status = -1
        gate_power_sequence.append({
            "cmd": "vset",
            "pin": command["pin"],
            "value": value,
            "pluseTime": str(args[1]) if len(args) > 1 and str(args[1]).strip() else "0",
            "status": status,
        })

    register_fields = []
    for match in re.finditer(r"\ben_tm\s*\[[^]]*\]|\bfield\s*\[[^]]*\]", str(row.get("Code2", "")), re.I):
        raw = match.group(0).strip()
        register_fields.append({"kind": "en_tm" if raw.lower().startswith("en_tm") else "field", "raw": raw})

    for expression in re.findall(r"\b[VI]\(([^)]+)\)", check, re.I):
        for pin in re.findall(r"[A-Za-z][A-Za-z0-9_]*", expression):
            if pin not in pins:
                pins.append(pin)

    identity = str(row.get("Name", "")).strip() or str(row.get("Item", "")).strip()
    return {
        "schemaVersion": 1,
        "testCondition": {
            "identity": identity,
            "identityDetails": {
                "testItem": row.get("Item", ""), "level": row.get("Level", ""),
                "parameterName": row.get("Name", ""), "description": row.get("Description", ""),
                "purpose": row.get("Purpose", ""), "unit": row.get("Unit", ""),
            },
            "remarks": row.get("Notes", ""), "expectedValue": row.get("ExpectValue", ""),
            "isTrim": bool(str(row.get("Trim", "")).strip() or re.search(r"\bTRIM\b", str(row.get("Level", "")), re.I)),
            "powerSequence": gate_power_sequence,
            "rawPowerSequence": commands,
            "staticPower": code1,
            "directPowerActions": direct_power,
            "hasRamp": bool(ramps), "ramps": ramps,
            "helperIntent": helper,
            "scanIntent": scan_intent(helper, bool(ramps)),
            "dynamicPins": dynamic_pins(row),
            "highCurrent": {"state": "DECLARED" if re.search(r"high.?current|\bHC\b", text, re.I) else "NOT_DECLARED", "evidenceColumns": ["Name", "Description", "Notes", "Special"]},
            "differentialVoltage": {"state": "DECLARED" if re.search(r"differential|diff|vdiff", text, re.I) else "NOT_DECLARED", "evidenceColumns": ["Name", "Description", "Notes", "Special"]},
            "internalComparison": {"state": "DECLARED" if internal_comparison else "NOT_DECLARED", "expression": "VAC-VDIO vs VBAT" if internal_comparison else "", "sourceText": description if internal_comparison else ""},
            "involvedPins": pins,
            "involvedPinsDetails": {"vsetPins": pins, "logicalCheck": check},
            "measurement": check,
            "measurementDetails": {"check": check, "quantity": quantity, "isToggle": toggle, "resultTypes": source_result_types, "resultTypeProvenance": result_provenance},
            "registerFieldIntent": register_fields,
            "referenceValue": row.get("ExpectValue", ""), "notes": notes,
        },
    }
