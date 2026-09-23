"""Deterministic Trim contract and implementation validation for DALI PTC."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _error(errors: list[str], path: str, detail: str) -> None:
    errors.append(f"{path} {detail}")


def validate_trim_execution_declaration(trim: Any, errors: list[str], *, path: str = "measurementPlan.trimExecution") -> Mapping[str, Any] | None:
    """Validate the signed fields a Trim method must declare."""
    if not isinstance(trim, Mapping):
        _error(errors, path, "must be an object for trim")
        return None
    if trim.get("required") is not True:
        _error(errors, f"{path}.required", "must be true")
    for key in ("node", "nodeVariable", "trimKey", "executeCallPrefix"):
        if not _nonempty(trim.get(key)):
            _error(errors, f"{path}.{key}", "must be a non-empty string")
    treg = trim.get("treg")
    if not isinstance(treg, Mapping):
        _error(errors, f"{path}.treg", "must be an object")
    else:
        for key in ("sourcePath", "sourceSha256", "key", "targetUnit"):
            if not _nonempty(treg.get(key)):
                _error(errors, f"{path}.treg.{key}", "must be a non-empty string")
        if treg.get("targetUnit") != "mV":
            _error(errors, f"{path}.treg.targetUnit", "must be mV")
        if not isinstance(treg.get("targetMillivolts"), (int, float)) or isinstance(treg.get("targetMillivolts"), bool):
            _error(errors, f"{path}.treg.targetMillivolts", "must be numeric")
        if not isinstance(treg.get("stepCount"), int) or isinstance(treg.get("stepCount"), bool) or treg.get("stepCount", 0) < 1:
            _error(errors, f"{path}.treg.stepCount", "must be a positive integer")
        mappings = treg.get("registerBitMappings")
        if not isinstance(mappings, list) or not mappings:
            _error(errors, f"{path}.treg.registerBitMappings", "must be a non-empty list")
        else:
            for index, mapping in enumerate(mappings):
                item_path = f"{path}.treg.registerBitMappings[{index}]"
                if not isinstance(mapping, Mapping):
                    _error(errors, item_path, "must be an object")
                    continue
                register = mapping.get("register")
                bits = mapping.get("bits")
                if not isinstance(register, str) or not re.fullmatch(r"F[0-9A-F]{1,2}", register.upper()):
                    _error(errors, f"{item_path}.register", "must be an EFUSE register such as F8")
                if not isinstance(bits, list) or not bits or any(not isinstance(bit, int) or isinstance(bit, bool) or bit < 0 or bit > 7 for bit in bits):
                    _error(errors, f"{item_path}.bits", "must be a non-empty list of bit numbers 0..7")
    callback = trim.get("callback")
    if not isinstance(callback, Mapping):
        _error(errors, f"{path}.callback", "must be an object")
    else:
        for key in ("sourcePath", "sourceSha256", "symbol", "resultUnit"):
            if not _nonempty(callback.get(key)):
                _error(errors, f"{path}.callback.{key}", "must be a non-empty string")
        if callback.get("resultUnit") != "mV":
            _error(errors, f"{path}.callback.resultUnit", "must be mV to match the .treg target")
    return trim


def _strip_cxx_comments(text: str) -> str:
    """Remove comments; a commented callback is deliberately invisible."""
    output: list[str] = []
    index = 0
    state = "code"
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == "code" and char == "/" and nxt == "/":
            state = "line"; index += 2; continue
        if state == "code" and char == "/" and nxt == "*":
            state = "block"; index += 2; continue
        if state == "line":
            if char == "\n":
                state = "code"; output.append(char)
            index += 1; continue
        if state == "block":
            if char == "*" and nxt == "/":
                state = "code"; index += 2
            else:
                index += 1
            continue
        output.append(char); index += 1
    return "".join(output)


def _function_body(source: str, symbol: str) -> tuple[str | None, bool]:
    cleaned = _strip_cxx_comments(source)
    signature = re.compile(
        r"\bvoid\s+" + re.escape(symbol)
        + r"\s*\(\s*TRIM_NODE\s*\*\s*[A-Za-z_]\w*\s*,\s*"
        + r"TREG_MEASURE_FLAG\s+[A-Za-z_]\w*\s*,\s*double\s*\*\s*[A-Za-z_]\w*\s*\)\s*\{"
    )
    match = signature.search(cleaned)
    if not match:
        return None, False
    index, depth = match.end(), 1
    while index < len(cleaned) and depth:
        if cleaned[index] == "{":
            depth += 1
        elif cleaned[index] == "}":
            depth -= 1
        index += 1
    return cleaned[match.start():index], True


def _parse_treg(path: Path, key: str) -> tuple[dict[str, Any] | None, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"\s*\[([^]]+)\]\s*$", line)
        if match:
            current = match.group(1).strip(); sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    section = sections.get(key)
    if section is None:
        return None, [f".treg key [{key}] is missing"]
    target_value: float | None = None
    target_unit: str | None = None
    table_count: int | None = None
    for line in section:
        target = re.match(r"\s*Target\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))", line, re.I)
        if target:
            target_value = float(target.group(1))
        comment_target = re.match(r"\s*;\s*Target\s*=\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)\s*([A-Za-zµ]+)", line, re.I)
        if comment_target:
            target_unit = comment_target.group(1)
        table = re.match(r"\s*Table\s*=\s*(.+?)\s*$", line, re.I)
        if table:
            table_count = len([item for item in table.group(1).split(",") if item.strip()])
    mappings: dict[str, list[int]] = {}
    for name, content in sections.items():
        reg = re.fullmatch(r"_EFUSE_REG_(F[0-9A-F]{1,2})", name, re.I)
        if not reg:
            continue
        for line in content:
            bit = re.match(r"\s*(\d+)\s*:\s*([^=;]+?)\s*=\s*\d+\s*$", line)
            if bit and bit.group(2).strip().lower() == key.lower():
                mappings.setdefault(reg.group(1).upper(), []).append(int(bit.group(1)))
    return {
        "targetMillivolts": target_value, "targetUnit": target_unit,
        "stepCount": table_count,
        "registerBitMappings": [{"register": register, "bits": sorted(bits)}
                                for register, bits in sorted(mappings.items())],
    }, []


def _expected_mappings(raw: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [{"register": str(item["register"]).upper(), "bits": sorted(item["bits"])}
         for item in (raw.get("registerBitMappings") or [])
         if isinstance(item, Mapping) and isinstance(item.get("bits"), list)],
        key=lambda item: item["register"],
    )


def _project_compiles_sub_cpp(path: Path) -> bool:
    # DALI keeps F12011.vcxproj beside source/sub.cpp.  A one-level fallback
    # supports the older project-root layout without scanning arbitrary paths.
    directories = (path.parent, path.parent.parent)
    for directory in directories:
        for project in directory.glob("*.vcxproj"):
            text = project.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(r'<ClCompile\s+Include="(?:[^"]*\\)?sub\.cpp"', text, re.I):
                return True
    return False


def validate_trim_project_evidence(trim: Mapping[str, Any], *, source_body: str | None = None) -> list[str]:
    """Check signed Trim facts against active .treg, sub.cpp and test.cpp binding."""
    errors: list[str] = []
    declaration_errors: list[str] = []
    if validate_trim_execution_declaration(trim, declaration_errors) is None or declaration_errors:
        return declaration_errors
    treg = trim["treg"]; callback = trim["callback"]
    treg_path = Path(treg["sourcePath"]); callback_path = Path(callback["sourcePath"])
    if not treg_path.is_file():
        _error(errors, "measurementPlan.trimExecution.treg.sourcePath", "does not exist")
    else:
        if _sha(treg_path) != treg["sourceSha256"]:
            _error(errors, "measurementPlan.trimExecution.treg.sourceSha256", "does not match active .treg")
        if treg["key"] != trim["trimKey"]:
            _error(errors, "measurementPlan.trimExecution.treg.key", "must equal trimKey")
        actual, parse_errors = _parse_treg(treg_path, treg["key"])
        errors.extend("measurementPlan.trimExecution.treg: " + item for item in parse_errors)
        if actual is not None:
            if actual["targetUnit"] != "mV":
                _error(errors, "measurementPlan.trimExecution.treg", "does not declare an mV target")
            if actual["targetMillivolts"] != float(treg["targetMillivolts"]):
                _error(errors, "measurementPlan.trimExecution.treg.targetMillivolts", "does not match active .treg")
            if actual["stepCount"] != treg["stepCount"]:
                _error(errors, "measurementPlan.trimExecution.treg.stepCount", "does not match active .treg Table length")
            if actual["registerBitMappings"] != _expected_mappings(treg):
                _error(errors, "measurementPlan.trimExecution.treg.registerBitMappings", "does not match active .treg EFUSE mapping")
    if callback_path.name.lower() != "sub.cpp":
        _error(errors, "measurementPlan.trimExecution.callback.sourcePath", "must name sub.cpp")
    if not callback_path.is_file():
        _error(errors, "measurementPlan.trimExecution.callback.sourcePath", "does not exist")
        return errors
    if _sha(callback_path) != callback["sourceSha256"]:
        _error(errors, "measurementPlan.trimExecution.callback.sourceSha256", "does not match active sub.cpp")
    if not _project_compiles_sub_cpp(callback_path):
        _error(errors, "measurementPlan.trimExecution.callback.sourcePath", "is not listed in a participating .vcxproj")
    callback_body, signature_ok = _function_body(callback_path.read_text(encoding="utf-8-sig", errors="replace"), callback["symbol"])
    if not signature_ok or callback_body is None:
        _error(errors, "measurementPlan.trimExecution.callback", "has no active implementation with signature void fn(TRIM_NODE*, TREG_MEASURE_FLAG, double*)")
        return errors
    expected_regs = {item["register"] for item in _expected_mappings(treg)}
    assy_regs = {item.upper() for item in re.findall(r'trim_reg\.assy\s*\(\s*"EFUSE_REG_(F[0-9A-F]{1,2})"\s*\)', callback_body, re.I)}
    write_regs = {item.upper() for item in re.findall(r'I2CWriteData\s*\([^;]*?\b0x(F[0-9A-F]{1,2})\b', callback_body, re.I)}
    if assy_regs != expected_regs:
        _error(errors, "measurementPlan.trimExecution.callback", f"EFUSE reads {sorted(assy_regs)} do not match signed .treg mapping {sorted(expected_regs)}")
    if write_regs != expected_regs:
        _error(errors, "measurementPlan.trimExecution.callback", f"EFUSE writes {sorted(write_regs)} do not match signed .treg mapping {sorted(expected_regs)}")
    if callback["resultUnit"] == "mV":
        result_lines = [line for line in callback_body.splitlines() if re.search(r"\bresults\s*\[[^]]+\]\s*=", line)]
        if not any(re.search(r"\*\s*1e3\b", line) for line in result_lines):
            _error(errors, "measurementPlan.trimExecution.callback.resultUnit", "mV requires an explicit results conversion by *1e3")
    if source_body is not None:
        bind = re.compile(re.escape(trim["nodeVariable"]) + r"\s*\.\s*execute\s*\(\s*" + re.escape(callback["symbol"]) + r"\s*,")
        if not bind.search(_strip_cxx_comments(source_body)):
            _error(errors, "measurementPlan.trimExecution", "test.cpp does not bind the signed callback through nodeVariable.execute")
    return errors
