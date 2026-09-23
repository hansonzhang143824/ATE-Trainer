"""Deterministic stage gate for ATE PTC sessions. It never dispatches agents."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STAGE_REGISTRY_PATH = ROOT / "team" / "ptc" / "ptc_stage_registry.json"
# A correction returns to the registered STRATEGY stage; it is not a separate
# specialist stage with an independent contract or gate. This is the ONLY place
# the alias is declared: the batch runner derives its ranking from here instead
# of restating a stage table of its own.
STAGE_ALIASES = {"CORRECTION_STRATEGY": "STRATEGY"}


def canonical_stage(state: str) -> str:
    """The registered stage a runner state belongs to."""
    return STAGE_ALIASES.get(state, state)


def stage_order(registry: dict | None = None) -> dict[str, int]:
    """Rank every state by its position in the registry's own stateMachine.

    The registry is the single state source, so nothing else restates this
    table. A legacy alias is folded onto the rank of the stage it returns to, so
    a CORRECTION_STRATEGY result ranks with the STRATEGY work it belongs to.
    """
    if registry is None:
        registry, error = load_stage_registry()
        if registry is None:
            raise ValueError(error or "PTC stage registry is unavailable")
    order = {state: rank for rank, state in enumerate(registry["stateMachine"])}
    for alias, stage in STAGE_ALIASES.items():
        if stage in order:
            order.setdefault(alias, order[stage])
    return order


def dispatch_roles(result: dict) -> list[str]:
    """The roles a stage result asks for, always as a list.

    The plural ``dispatchableRoles`` is the authority; the singular ``dispatch``
    is kept for older callers and is only a fallback. Normalising here is what
    stops a stage from ending early because its singular field happened to be
    empty while the plural list named real work.
    """
    roles = result.get("dispatchableRoles") if isinstance(result, dict) else None
    if not roles:
        only = result.get("dispatch") if isinstance(result, dict) else None
        roles = [only] if only else []
    ordered: list[str] = []
    for role in roles:
        if isinstance(role, str) and role and role not in ordered:
            ordered.append(role)
    return ordered


def load_stage_registry() -> tuple[dict | None, str | None]:
    """Load the Captain's only dispatch registry and reject partial configs."""
    registry = read_json(STAGE_REGISTRY_PATH)
    if registry is None:
        return None, f"PTC stage registry is missing or invalid JSON: {STAGE_REGISTRY_PATH}"
    states, stages = registry.get("stateMachine"), registry.get("stages")
    if not isinstance(states, list) or not states or not all(isinstance(value, str) and value for value in states):
        return None, "PTC stage registry has no valid stateMachine"
    if len(states) != len(set(states)) or not isinstance(stages, dict):
        return None, "PTC stage registry has duplicate states or no stages object"
    required = {state for state in states if state != "COMPLETE"}
    if set(stages) != required:
        return None, "PTC stage registry stages do not exactly match its dispatchable stateMachine stages"
    for name, config in stages.items():
        if not isinstance(config, dict):
            return None, f"PTC stage registry entry {name} is not an object"
        owner, gate = config.get("owner"), config.get("gate")
        families, outputs = config.get("families"), config.get("outputs")
        if not isinstance(owner, str) or not owner or not isinstance(gate, str) or not gate:
            return None, f"PTC stage registry entry {name} has no valid owner or gate"
        if not isinstance(families, list) or not families or not all(isinstance(value, str) and value for value in families):
            return None, f"PTC stage registry entry {name} has no valid families"
        if not isinstance(outputs, list) or not all(isinstance(value, str) and value for value in outputs):
            return None, f"PTC stage registry entry {name} has no valid outputs"
        gate_path = ROOT / gate
        if Path(gate).is_absolute() or not gate_path.is_file():
            return None, f"PTC stage registry entry {name} references a missing or unsafe gate: {gate}"
    return registry, None


def apply_stage_registry(result: dict, registry: dict) -> dict:
    """Bind every dispatchable result to its registered stage, owner and gate."""
    state = result.get("state")
    if state in {"BLOCKED", "PROJECT_INFO", "COMPLETE"}:
        return result
    registered_stage = canonical_stage(state)
    states = registry["stateMachine"]
    config = registry["stages"].get(registered_stage)
    if registered_stage not in states or not isinstance(config, dict):
        return {
            "state": "BLOCKED", "dispatch": None,
            "reason": f"PTC stage registry has no dispatchable entry for runner state {state}",
            "evidence": str(STAGE_REGISTRY_PATH),
        }
    # INPUT_SYNC is owned by Captain. Its DFT/SCH roles are source producers
    # named by the input manifest, so they deliberately differ from owner.
    dispatch = result.get("dispatch")
    if registered_stage != "INPUT_SYNC" and dispatch is not None and dispatch != config["owner"]:
        return {
            "state": "BLOCKED", "dispatch": None,
            "reason": f"runner dispatch {dispatch} does not match registered owner {config['owner']} for {registered_stage}",
            "evidence": str(STAGE_REGISTRY_PATH),
        }
    bound = dict(result)
    bound.update({
        "registeredStage": registered_stage,
        "registeredOwner": config["owner"],
        "registeredGate": config["gate"],
    })
    return bound
sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_info
import trial_directory

def project_info_gate() -> dict | None:
    """Every run starts by reading Project_Info; an unconfirmed file stops the run."""
    found = project_info.problems(project_info.load())
    if not found:
        return None
    return {"state": "PROJECT_INFO", "dispatch": None,
            "reason": "project input locations are not confirmed",
            "problems": found,
            "action": "Ask the user to approve or modify Project_Info.json, then run the gate again.",
            "evidence": str(project_info.PROJECT_INFO)}

def emit(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("state") != "BLOCKED" else 2

def read_json(path: Path) -> dict | None:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None

def byte_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None

def expected_monitor(trial: Path) -> str | None:
    state = read_json(trial / "input-manifest.json") or {}
    entry = (state.get("canonicalInputs", {}).get("intentResolution", {}) or {}).get("entry")
    return entry.get("decision", {}).get("monitorDutPin") if isinstance(entry, dict) else None

def validate_strategy(trial: Path, tm: str) -> tuple[bool, str]:
    contract = trial / "strategy" / f"{tm.lower()}-resource-config-contract.json"
    handoff = trial / "strategy" / "deliverable-ready.json"
    monitor=expected_monitor(trial)
    if not contract.is_file() or not handoff.is_file():
        return False, "strategy contract or handoff is missing"
    check = ROOT / "scripts" / "validate_strategy_contract.py"
    command = [sys.executable, str(check), str(contract), str(handoff), "--manifest", str(trial / "input-manifest.json")]
    if isinstance(monitor, str) and monitor:
        command += ["--expected-monitor", monitor]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode == 0, (result.stdout + result.stderr).strip()

def implementation_is_current(path: Path, method_sha: str | None) -> bool:
    payload=read_json(path)
    if payload is None:
        return False
    if (payload.get('signedInputs') or {}).get('methodContractSha256') != method_sha:
        return False
    # Current manifest schema: every changed file records its post-write hash and symbols.
    changes=payload.get('changes')
    if isinstance(changes,list) and changes:
        for change in changes:
            if not isinstance(change,dict):
                return False
            source,expected=change.get('path'),change.get('afterSha256')
            symbols=change.get('symbols')
            if not isinstance(source,str) or not isinstance(expected,str) or not isinstance(symbols,list) or not symbols:
                return False
            target=Path(source)
            if not target.is_file() or byte_sha256(target) != expected:
                return False
            try:
                body=target.read_text(encoding='utf-8', errors='replace')
            except OSError:
                return False
            if not all(isinstance(symbol,str) and symbol in body for symbol in symbols):
                return False
        return True
    # Legacy schema is accepted only when its one source and symbol still verify.
    source,expected,symbol=payload.get('source'),payload.get('sourceSha256'),payload.get('symbol')
    if not isinstance(source,str) or not isinstance(expected,str) or not isinstance(symbol,str):
        return False
    target=Path(source)
    if not target.is_file() or byte_sha256(target) != expected:
        return False
    try:
        return symbol in target.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

def compile_is_current(path: Path) -> bool:
    payload=read_json(path)
    if payload is None:
        return False
    source,expected=payload.get('source'),payload.get('sourceSha256')
    if not isinstance(source,str) or not isinstance(expected,str):
        return False
    target=Path(source)
    return target.is_file() and byte_sha256(target) == expected

def validate_method_contract(path: Path, strategy_sha: str | None) -> bool:
    if not strategy_sha or not path.is_file():
        return False
    check=ROOT / 'scripts' / 'validate_method_contract.py'
    result=subprocess.run([sys.executable,str(check),str(path),'--strategy-sha',strategy_sha],cwd=ROOT,text=True,capture_output=True)
    return result.returncode == 0

def is_ready(path: Path, stage: str) -> bool:
    payload=read_json(path)
    if payload is None: return False
    return (payload.get("status") == "success" or payload.get("event") == "deliverable_ready") and payload.get("stage") == stage and payload.get("verdict") == "deliverable_ready"

def route(state: str, dispatch: str | None, reason: str, inputs: list[Path], output: Path, **extra: object) -> dict:
    result={"state":state,"dispatch":dispatch,"reason":reason,"inputs":[str(p) for p in inputs],"outputDir":str(output)}
    result.update(extra)
    return result

def validate_output_abi() -> tuple[bool, str]:
    check=ROOT / "scripts" / "validate_ptc_output_contracts.py"
    result=subprocess.run([sys.executable,str(check)],cwd=ROOT,text=True,capture_output=True)
    return result.returncode==0,(result.stdout+result.stderr).strip()

def routed_correction(trial: Path, tm: str, manifest: Path, contract: Path, handoff: Path) -> dict | None:
    blocked=trial / "method" / f"{tm.lower()}-method-blocked.json"
    finding=read_json(blocked)
    if not finding or finding.get("status") != "BLOCKED" or finding.get("verdict") != "blocked_routed_to_owner": return None
    owner=finding.get("requiredOwnerAction",{}).get("owner")
    finding_id=finding.get("finding",{}).get("id")
    if owner != "test-strategy-architect" or not isinstance(finding_id,str) or not finding_id:
        return {"state":"BLOCKED","dispatch":None,"reason":"method routed finding has no supported unique owner","evidence":str(blocked)}
    strategy=read_json(contract) or {}
    resolved=set(strategy.get("resolvedFindings",[]))
    if finding_id in resolved: return None
    boundary=finding.get("signedInputBoundary",[])
    prior_sha=(boundary[0].get("sha256") if isinstance(boundary,list) and boundary and isinstance(boundary[0],dict) else None)
    current_sha=byte_sha256(contract)
    if isinstance(prior_sha,str) and prior_sha and current_sha and current_sha != prior_sha:
        return {"state":"BLOCKED","dispatch":None,"reason":"strategy contract changed after routed finding but did not acknowledge it; do not redispatch","evidence":str(blocked)}
    return route("CORRECTION_STRATEGY", "test-strategy-architect", "method supplied an evidence-backed route correction to its sole owner", [manifest,contract,handoff,blocked], trial / "strategy", correction={"findingId":finding_id,"owner":owner,"evidence":str(blocked),"requiredAcknowledgement":f"resolvedFindings must include {finding_id}"})

def stage_unchecked(trial: Path, tm: str) -> dict:
    info_gate=project_info_gate()
    if info_gate is not None: return info_gate
    abi_ok,abi_note=validate_output_abi()
    if not abi_ok: return {"state":"BLOCKED","dispatch":None,"reason":"PTC role output ABI is invalid; do not dispatch a specialist","evidence":str(ROOT / "scripts" / "validate_ptc_output_contracts.py"),"details":abi_note}
    manifest=trial / "input-manifest.json"
    input_state=read_json(manifest)
    if input_state is None:
        return {"state":"INPUT_SYNC","dispatch":None,"action":"Run command prepare-input.","reason":"input-manifest.json is missing or invalid"}
    if input_state.get("status") != "ready":
        roles=input_state.get("dispatchableRoles") or []
        return {"state":"INPUT_SYNC","dispatch":roles[0] if len(roles)==1 else None,"dispatchableRoles":roles,"reason":"upstream artifacts are stale or missing","evidence":str(manifest),"roleGates":input_state.get("roleGates", {}),"globalGate":input_state.get("globalGate", {})}
    strategy=trial / "strategy"; method=trial / "method"; review=trial / "review"; implementation=trial / "implementation"; compile_dir=trial / "compile"
    strategy_contract=strategy / f"{tm.lower()}-resource-config-contract.json"; strategy_ready=strategy / "deliverable-ready.json"
    strategy_ok,strategy_note=validate_strategy(trial,tm)
    if not strategy_ok: return route("STRATEGY","test-strategy-architect",strategy_note,[manifest],strategy)
    correction=routed_correction(trial,tm,manifest,strategy_contract,strategy_ready)
    if correction is not None: return correction
    method_contract=method / f"{tm.lower()}-test-method-contract.json"; method_ready=method / "deliverable-ready.json"
    method_review_ready=review / "method-contract-review-deliverable-ready.json"
    implementation_manifest=implementation / "implementation-manifest.json"; implementation_ready=implementation / "deliverable-ready.json"
    implementation_review_ready=review / "implementation-review-deliverable-ready.json"; compile_ready=compile_dir / "deliverable-ready.json"
    method_data=read_json(method_contract) if method_contract.is_file() else None
    strategy_sha=byte_sha256(strategy_contract)
    method_strategy_sha=((method_data or {}).get("signedInputs") or {}).get("strategyContractSha256")
    if not is_ready(method_ready,"METHOD") or not method_contract.is_file() or method_strategy_sha != strategy_sha or not validate_method_contract(method_contract,strategy_sha): return route("METHOD","test-method-expert","method is missing, stale, or incomplete for the current signed strategy contract",[strategy_contract,strategy_ready],method)
    review_data=read_json(review / "method-contract-review.json")
    method_sha=byte_sha256(method_contract)
    review_method_sha=((review_data or {}).get("signedInputs") or {}).get("methodContractSha256")
    if not is_ready(method_review_ready,"RULE_REVIEW_METHOD") or review_method_sha != method_sha: return route("RULE_REVIEW_METHOD","rule-reviewer","current method contract requires independent rule review",[strategy_contract,strategy_ready,method_contract,method_ready],review)
    if not is_ready(implementation_ready,"IMPLEMENTATION") or not implementation_manifest.is_file() or not implementation_is_current(implementation_manifest, method_sha): return route("IMPLEMENTATION","ate-implementer","implementation is missing or its recorded source file no longer has the signed hash and function",[strategy_contract,strategy_ready,method_contract,method_ready,method_review_ready],implementation)
    implementation_review=review / "implementation-review.json"
    implementation_review_data=read_json(implementation_review)
    implementation_manifest_sha=byte_sha256(implementation_manifest)
    reviewed_implementation_sha=((implementation_review_data or {}).get("signedInputs") or {}).get("implementationManifestSha256")
    if not is_ready(implementation_review_ready,"RULE_REVIEW_IMPLEMENTATION") or reviewed_implementation_sha != implementation_manifest_sha: return route("RULE_REVIEW_IMPLEMENTATION","rule-reviewer","current implementation requires independent rule review",[implementation_manifest,implementation_ready],review)
    compile_report=compile_dir / "build-report.json"
    if not is_ready(compile_ready,"COMPILE") or not compile_is_current(compile_report): return route("COMPILE","compile-diagnostician","current implementation review passed; a build tied to the current source is required",[implementation_manifest,implementation_ready,implementation_review_ready],compile_dir)
    return route("COMPLETE",None,"all PTC stages delivered and independently reviewed",[compile_ready],compile_dir)


def stage(trial: Path, tm: str) -> dict:
    registry, registry_error = load_stage_registry()
    if registry_error is not None:
        return {
            "state": "BLOCKED", "dispatch": None, "reason": registry_error,
            "evidence": str(STAGE_REGISTRY_PATH),
        }
    return apply_stage_registry(stage_unchecked(trial, tm), registry)


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--tm",required=True); parser.add_argument("--trial-dir"); parser.add_argument("--command",choices=("next","prepare-input"),default="next"); args=parser.parse_args()
    try:
        trial=trial_directory.resolve(args.tm,args.trial_dir)
    except ValueError as exc:
        return emit({"state":"BLOCKED","dispatch":None,"reason":str(exc)})
    if args.command == "prepare-input":
        result=subprocess.run([sys.executable,str(ROOT / "scripts" / "prepare_input_sync_v2.py"),"--tm",args.tm,"--trial-dir",str(trial)],cwd=ROOT,text=True,capture_output=True)
        payload=stage(trial,args.tm); payload.update(command="prepare-input",scriptExitCode=result.returncode,scriptOutput=(result.stdout+result.stderr).strip()); return emit(payload)
    return emit(stage(trial,args.tm))
if __name__ == "__main__": raise SystemExit(main())
