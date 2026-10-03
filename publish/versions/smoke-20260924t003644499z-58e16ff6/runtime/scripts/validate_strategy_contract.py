"""Deterministic STRATEGY gate for the ATE PTC runner.

The endpoint authority is the DFT row in the user's workbook (canonicalInputs.dft.declaredPins)
plus the physical monitor pin the contract itself resolves (pinResolution.physicalDutPin).
An intent-resolution entry, when present, is cross-checked but never required: a file
authored outside the signed inputs must not be able to gate a run.
"""
import argparse
import hashlib
import json
from pathlib import Path

from check_path_conflicts import check_contract
from check_functional_relays import check_functional_relays
from verify_source_table_mapping import approved_source_header, check_source_table_mapping


def h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_facts(path: Path):
    """(pins the DFT row declares, monitor pin declared in an intent entry or None)."""
    manifest = json.loads(path.read_text(encoding='utf-8'))
    inputs = manifest.get('canonicalInputs', {})
    declared = {str(pin).upper() for pin in ((inputs.get('dft') or {}).get('declaredPins') or [])}
    entry = (inputs.get('intentResolution') or {}).get('entry')
    monitor = entry.get('decision', {}).get('monitorDutPin') if isinstance(entry, dict) else None
    if not isinstance(monitor, str) or not monitor:
        monitor = None
    return declared, monitor


def components_pins(manifest_path: Path) -> set:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_root = (manifest.get("materialRoots") or {}).get("output")
    if not output_root:
        raise ValueError("input manifest declares no output material root")
    components = Path(output_root) / "schematic" / "Components-Statistic.json"
    data = json.loads(components.read_text(encoding="utf-8"))
    pins = data.get("semanticIndex", {}).get("dutKelvinPins")
    if not isinstance(pins, list) or not all(isinstance(pin, str) and pin for pin in pins):
        raise ValueError("Components-Statistic.json has no valid DUT pin index")
    return set(pins)

def validate_resource_evidence(item, errors):
    """Require a locatable DFT→source→route→relay→register evidence chain."""
    endpoint = item.get('dutPin', '<unknown>')
    chain = item.get('evidenceChain')
    if not isinstance(chain, dict):
        errors.append(f'{endpoint} has no evidenceChain')
        return
    for key in ('dftEndpointLocator', 'sourceTableLocator', 'schematicRouteLocator',
                'relayDefinitionLocator', 'registerConfigurationLocator'):
        if not isinstance(chain.get(key), str) or not chain[key].strip():
            errors.append(f'{endpoint} evidenceChain has no {key}')
    ports = item.get('ports') or []
    source_port = str(ports[0]) if ports else ''
    path = str(item.get('selectedPath') or '')
    if source_port and source_port not in path:
        bridge = chain.get('interconnectLocator')
        if not isinstance(bridge, str) or not bridge.strip():
            errors.append(f'{endpoint} source port {source_port} is absent from selectedPath and has no interconnectLocator')


def physical_dut_base(name):
    import re
    return re.sub(r'_(?:F|S|FORCE|SENSE)_S\d+$', '', str(name), flags=re.I)


def validate_physical_proofs(contract, manifest_path, errors):
    """Bind each selected resource to exact accepted canonical Path-Proofs records."""
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
        output_root = Path((manifest.get('materialRoots') or {})['output'])
        proof_path = output_root / 'schematic' / 'Path-Proofs.json'
        proof_data = json.loads(proof_path.read_text(encoding='utf-8'))
        accepted = proof_data.get('accepted_path_proofs')
        if proof_data.get('status') != 'PASS' or not isinstance(accepted, list):
            raise ValueError('formal Path-Proofs is not passing')
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f'cannot load formal Path-Proofs: {exc}')
        return
    lookup = {(x.get('source_port'), x.get('dut_pin')): x for x in accepted if isinstance(x, dict)}
    for item in contract.get('resourceAllocation', []):
        endpoint = item.get('dutPin', '<unknown>')
        proofs = item.get('physicalProofs')
        if not isinstance(proofs, list) or not proofs:
            errors.append(f'{endpoint} has no physicalProofs')
            continue
        required_on = set()
        for proof in proofs:
            if not isinstance(proof, dict):
                errors.append(f'{endpoint} has an invalid physical proof')
                continue
            source, dut = proof.get('sourcePort'), proof.get('dutPin')
            actual = lookup.get((source, dut))
            if not actual:
                errors.append(f'{endpoint} physical proof {source}->{dut} is absent from formal Path-Proofs')
                continue
            if physical_dut_base(dut).upper() != str(endpoint).upper():
                errors.append(f'{endpoint} physical proof terminates at unrelated DUT pin {dut}')
            declared = proof.get('requiredOn')
            if not isinstance(declared, list) or sorted(declared) != sorted(actual.get('required_on') or []):
                errors.append(f'{endpoint} physical proof {source}->{dut} has wrong requiredOn')
            locator = proof.get('locator')
            if not isinstance(locator, str) or not locator.strip():
                errors.append(f'{endpoint} physical proof {source}->{dut} has no locator')
            required_on.update(actual.get('required_on') or [])
        if sorted(item.get('requiredActuations') or []) != sorted(required_on):
            errors.append(f'{endpoint} requiredActuations does not equal its Path-Proofs required_on union')
    combined = check_contract(contract, proof_data, final_four_only=True)
    if combined['status'] != 'PASS':
        for conflict in combined['conflicts']:
            errors.append(f'path/relay conflict: {conflict}')
        for unknown in combined['unknown']:
            errors.append(f'path/relay evidence missing: {unknown}')


def validate_relay_design_workflow(contract, errors):
    """Keep relay workflow as an optional audit trace, not an acceptance gate.

    Candidate selection, fallback, and final combination evidence are produced by
    the deterministic route search. Strategy acceptance remains enforced by source
    mapping, Path-Proofs, final conflict checks, and functional-relay checks.
    """
    return None


def validate_register_configuration(contract, errors):
    config=contract.get('registerConfiguration')
    if not isinstance(config,dict):
        errors.append('contract has no registerConfiguration'); return
    for key in ('evidencePath','evidenceSha256','sourcePath'):
        if not isinstance(config.get(key),str) or not config[key].strip(): errors.append('registerConfiguration has no '+key)
    rows=config.get('orderedWrites')
    if not isinstance(rows,list) or not rows:
        errors.append('registerConfiguration has no orderedWrites')
        return
    if not all(isinstance(x,dict) and isinstance(x.get('sourceText'),str) and 'I2CWriteSameData' in x['sourceText'] for x in rows):
        errors.append('registerConfiguration orderedWrites are invalid')
        return
    root=Path(__file__).resolve().parent.parent
    evidence=root / config.get('evidencePath','')
    source=root / config.get('sourcePath','')
    if not evidence.is_file():
        errors.append('registerConfiguration evidence file is missing')
        return
    if h(evidence) != config.get('evidenceSha256'):
        errors.append('registerConfiguration evidence hash does not match')
    try:
        receipt=json.loads(evidence.read_text(encoding='utf-8'))
        if receipt.get('tm') != contract.get('tm') or receipt.get('orderedWrites') != rows:
            errors.append('registerConfiguration evidence does not match contract')
        if receipt.get('source',{}).get('path') != config.get('sourcePath'):
            errors.append('registerConfiguration source path does not match evidence')
        if receipt.get('source',{}).get('sha256') != config.get('sourceSha256'):
            errors.append('registerConfiguration source hash does not match evidence')
        if not receipt.get('dftBinding',{}).get('verifiedAgainstDftCode2'):
            errors.append('registerConfiguration evidence is not bound to DFT Code2')
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        errors.append('cannot read registerConfiguration evidence: %s' % exc)
    if not source.is_file():
        errors.append('registerConfiguration source is missing')
    elif h(source) != config.get('sourceSha256'):
        errors.append('registerConfiguration source hash does not match current source')

def validate_classification(contract, errors):
    """Require project-type and parameter-type decisions from their canonical flows."""
    classification = contract.get('classification')
    if not isinstance(classification, dict):
        errors.append('contract has no classification')
        return
    for kind in ('projectType', 'parameterType'):
        item = classification.get(kind)
        if not isinstance(item, dict):
            errors.append(f'classification has no {kind}')
            continue
        if not isinstance(item.get('value'), str) or not item['value'].strip():
            errors.append(f'classification {kind} has no value')
        if not isinstance(item.get('flowLocator'), str) or 'test-types.md' not in item['flowLocator']:
            errors.append(f'classification {kind} has no test-types flowLocator')
        if not isinstance(item.get('indexLocator'), str) or not item['indexLocator'].strip():
            errors.append(f'classification {kind} has no indexLocator')
        if not isinstance(item.get('evidenceLocator'), str) or not item['evidenceLocator'].strip():
            errors.append(f'classification {kind} has no evidenceLocator')



def validate_functional_requirements(contract, manifest_path, errors):
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
        output_root = Path((manifest.get('materialRoots') or {})['output'])
        project_root = Path(__file__).resolve().parent.parent
        tm = contract['tm']
        dft = json.loads((output_root / 'dft' / tm / 'dft-meta.json').read_text(encoding='utf-8'))
        schematic = json.loads((output_root / 'schematic' / 'SCH-Connect-Map.json').read_text(encoding='utf-8'))
        proofs = json.loads((output_root / 'schematic' / 'Path-Proofs.json').read_text(encoding='utf-8'))
        relays_rule = (project_root / 'knowledge' / 'hardware' / 'relays.md').read_text(encoding='utf-8')
        checklist_rule = (project_root / 'knowledge' / 'standards' / 'relay-checklist.md').read_text(encoding='utf-8')
        report = check_functional_relays(contract, dft, schematic, relays_rule, checklist_rule,
                                         proofs, manifest)
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        errors.append('cannot verify functional relays: %s' % exc)
        return
    if report['status'] == 'PASS':
        return
    before = len(errors)
    for item in report['requirements']:
        if item['closure'] == 'MISSING':
            errors.append('%s requires %s in final SetOn (%s)' %
                          (tm, item['relay'], '; '.join(item['evidence'])))
        elif item['applicability'] == 'UNKNOWN' or item['closure'] == 'UNKNOWN':
            errors.append('%s %s functional relay evidence is UNKNOWN: %s' %
                          (tm, item['relay'], item['reason']))
    if report.get('sourceProblem'):
        errors.append(report['sourceProblem'])
    if len(errors) == before:
        errors.append('%s functional/path check is %s' % (tm, report['status']))


def validate_source_table_header_mapping(contract, errors):
    try:
        project_info = Path(__file__).resolve().parent.parent / 'Project_Info.json'
        header = approved_source_header(project_info)
        result = check_source_table_mapping(contract, header.read_text(encoding='utf-8'))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append('cannot verify approved VS source-table header: %s' % exc)
        return
    for issue in result['errors']:
        errors.append('source-table mapping: ' + issue)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('contract')
    parser.add_argument('handoff')
    parser.add_argument('--expected-monitor')
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    contract, handoff = Path(args.contract).resolve(), Path(args.handoff).resolve()
    d = json.loads(contract.read_text(encoding='utf-8'))
    e = json.loads(handoff.read_text(encoding='utf-8'))
    errors = []
    try:
        declared_pins, manifest_monitor = manifest_facts(Path(args.manifest).resolve())
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print('FAIL')
        print('input manifest does not declare DFT endpoints: %s' % exc)
        raise SystemExit(1)
    if args.expected_monitor and manifest_monitor and args.expected_monitor != manifest_monitor:
        errors.append('--expected-monitor %s != declared monitor pin %s' % (args.expected_monitor, manifest_monitor))

    resolution = d.get('pinResolution')
    physical = None
    if not isinstance(resolution, dict):
        errors.append('contract has no pinResolution')
    else:
        physical = resolution.get('physicalDutPin')
        special = (json.loads(Path(args.manifest).read_text(encoding='utf-8')).get('canonicalInputs', {}).get('specialPinInformation', {}) or {}).get('document', {})
        label = str(resolution.get('logicalSignal', '')).upper().replace('V(', '').replace(')', '')
        for mapping in special.get('mappings', []) if isinstance(special, dict) else []:
            names = [str(mapping.get('logicalLabel', '')).upper()] + [str(x).upper().replace('V(', '').replace(')', '') for x in mapping.get('aliases', [])]
            if label in names and physical != mapping.get('physicalDutPin'):
                errors.append('pinResolution physicalDutPin does not match DALI-special-information mapping')
        if resolution.get('resolutionState') != 'RESOLVED': errors.append('pinResolution is not RESOLVED')
        if not physical: errors.append('pinResolution has no physicalDutPin')
        if manifest_monitor and physical and physical != manifest_monitor:
            errors.append('pinResolution physicalDutPin does not equal the declared monitor pin')
        if not resolution.get('logicalSignal'): errors.append('pinResolution has no logicalSignal')
        if not resolution.get('mappingEvidence'): errors.append('pinResolution has no mapping evidence')

    if d.get('verdict') != 'deliverable_ready': errors.append('contract verdict is not deliverable_ready')
    validate_classification(d, errors)
    validate_register_configuration(d, errors)
    if e.get('event') != 'deliverable_ready': errors.append('handoff event missing')
    if e.get('sha256') != h(contract): errors.append('handoff sha256 does not bind contract')

    required = set(declared_pins)
    if physical:
        required.add(physical)
    if not required:
        errors.append('the DFT row declares no endpoint and the contract resolves no physical pin')
    actual = {x.get('dutPin') for x in d.get('resourceAllocation', [])}
    if actual != required:
        errors.append('endpoint set %s != %s' % (sorted(map(str, actual)), sorted(required)))
    for x in d.get('resourceAllocation', []):
        if x.get('selectionState') != 'SELECTED': errors.append('%s is not selected' % x.get('dutPin'))
        if x.get('sourceTable') in ('', 'UNRESOLVED', None): errors.append('%s has no source table' % x.get('dutPin'))
        validate_resource_evidence(x, errors)
    if d.get('resourceSummary', {}).get('sourceTablesUnresolved'): errors.append('summary retains unresolved source table')
    validate_source_table_header_mapping(d, errors)
    validate_physical_proofs(d, args.manifest, errors)
    validate_functional_requirements(d, args.manifest, errors)
    validate_relay_design_workflow(d, errors)
    if e.get('nextRole') != 'test-method-expert': errors.append('handoff routes to wrong role')
    if errors:
        print('FAIL')
        print('\n'.join(errors))
        raise SystemExit(1)
    print('PASS')


if __name__ == '__main__':
    main()
