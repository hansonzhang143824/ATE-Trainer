#!/usr/bin/env python3
"""Run authoritative stage validators against verified run-owned training copies.

This is a host command, never a model-chosen Python snippet. Original validators
are imported from this repository, not executed from writable training snapshots.
The caller enforces a 30-second process-tree deadline for this one command.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib
import io
import json
import os
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

from material_plaintext_hash import sha256_plaintext
from training_schematic import secure_path

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = {'INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD', 'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION'}
GATES = {'INPUT_SYNC': 'scripts/prepare_input_sync_v2.py', 'STRATEGY': 'scripts/validate_strategy_contract.py',
         'METHOD': 'scripts/validate_method_contract.py', 'RULE_REVIEW_METHOD': 'scripts/review_method_batch.py',
         'IMPLEMENTATION': 'scripts/verify_implementation_batch.py', 'RULE_REVIEW_IMPLEMENTATION': 'scripts/verify_implementation_batch.py'}
PATH_KEYS = {'path', 'sourcePath', 'evidencePath', 'dftMetaPath', 'strategyContractPath', 'methodContractPath',
             'manifestPath', 'inputManifestPath', 'projectFile', 'sourceFile', 'headerPath', 'sourceRoot',
             'outputRoot', 'inputRoot', 'programSourceRoot', 'vsProjectRoot'}


def read_json(file):
    return json.loads(Path(file).read_text(encoding='utf-8-sig'))


def digest(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


def identifier(value):
    if (not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', value)
            or value.endswith('.') or re.match(r'(?i)^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)', value)):
        raise ValueError('invalid training run identity')
    return value


def load_context(run_id, test_items, *, root=None):
    root = Path(root or ROOT).resolve()
    run = secure_path(root / 'Training_Materials' / 'runs' / identifier(run_id), root)
    context = read_json(secure_path(run / 'run.json', run, True))
    if (context.get('mode') != 'training' or context.get('runId') != run_id
            or context.get('releaseId') is not None or context.get('projectId') is not None
            or (root / context.get('artifactRoot', '')).resolve() != run):
        raise ValueError('not a matching isolated training run')
    if (not test_items or len(set(test_items)) != len(test_items)
            or any(not re.fullmatch(r'TM[0-9]+', tm) for tm in test_items)):
        raise ValueError('test items must be explicit unique TM identities')
    manifest = read_json(secure_path(run / 'pipeline-material-manifest.json', run, True))
    if (manifest.get('schemaVersion') != 1 or manifest.get('kind') != 'ptc-pipeline-materials'
            or manifest.get('runId') != run_id or sorted(manifest.get('testItems', [])) != sorted(test_items)
            or not re.fullmatch(r'[a-f0-9]{64}', manifest.get('pipelineCacheKey', ''))):
        raise ValueError('pipeline material manifest identity differs')
    base_file = secure_path(root / manifest.get('baseMaterialManifest', ''), run, True)
    base = read_json(base_file)
    if base.get('runId') != run_id or base.get('cacheKey') != manifest.get('baseCacheKey'):
        raise ValueError('base material provenance differs')
    entries = list(manifest.get('files', [])) + list(manifest.get('generatedFiles', [])) + [dict(entry, snapshotPath=entry.get('path')) for entry in base.get('files', [])]
    lookup = {}
    for entry in entries:
        name = entry.get('snapshotPath')
        if not isinstance(name, str) or not name or name in lookup or not re.fullmatch(r'[a-f0-9]{64}', entry.get('sha256', '')):
            raise ValueError('invalid or duplicate material snapshot record')
        working = secure_path(root / name, run, True)
        checked = secure_path(root / entry.get('baselinePath', ''), run, True) if entry.get('mutable') is True else working
        if entry.get('mutable') is True and not str(entry.get('kind', '')).startswith('vs-'):
            raise ValueError('only VS working copies may be mutable')
        actual = sha256_plaintext(checked) if entry.get('view') == 'python-plaintext' else digest(checked) if entry.get('view') == 'exact-bytes' else None
        if actual != entry['sha256']:
            raise ValueError(f'immutable material snapshot differs: {name}')
        lookup[name] = entry
    address = manifest.get('addressBook', {})

    def frozen(name):
        if name not in lookup:
            raise ValueError(f'path is not a registered material snapshot: {name}')
        return secure_path(root / name, run, True)

    approved_path = frozen(address.get('approvedProjectInfoPath'))
    approved = read_json(approved_path)
    from project_info import inputs_digest
    approval = approved.get('approval') or {}
    if (approved.get('project') != 'DALI' or not approval.get('approvedBy') or not approval.get('approvedAt')
            or approval.get('inputsDigest') != inputs_digest(approved)
            or manifest.get('approvedConfiguration', {}).get('sha256') != lookup[address['approvedProjectInfoPath']]['sha256']):
        raise ValueError('original approved Project_Info provenance is invalid')
    registry = read_json(frozen(address.get('registry')))
    stages = registry.get('stateMachine', [])
    if not isinstance(stages, list) or not stages or len(set(stages)) != len(stages):
        raise ValueError('authoritative registry is invalid')
    inputs = {key: frozen(value) for key, value in address.get('input', {}).items() if value is not None}
    if not all(key in inputs for key in ['dft', 'schematic', 'confirmed', 'cbit']):
        raise ValueError('complete source input snapshot is required')
    input_root = run / 'input'
    if any(not file.is_relative_to(input_root) for file in inputs.values()):
        raise ValueError('source input is outside run/input')
    output = secure_path(root / address.get('outputRoot', address.get('inputSyncRoot', '')), run)
    if output != run / 'input-sync':
        raise ValueError('output must be run/input-sync')
    knowledge = secure_path(root / address.get('knowledgeRoot', ''), run)
    if knowledge != run / 'knowledge':
        raise ValueError('original validators require the frozen run/knowledge layout')
    trials = {tm: secure_path(root / address.get('trials', {}).get(tm, ''), run) for tm in test_items}
    if any(trial != run / 'trials' / tm.lower() for tm, trial in trials.items()):
        raise ValueError('trial path must match its TM under run/trials')
    program = secure_path(root / address.get('programSourceRoot', ''), run)
    original_program = Path(approved.get('inputs', {}).get('program', ''))
    if not original_program.is_absolute():
        original_program = root / original_program
    expected_header = os.path.normcase(os.path.abspath(original_program / 'Pin_Channel_define.h'))
    matching = [entry for entry in entries if entry.get('source') and os.path.normcase(os.path.abspath(entry['source'])) == expected_header]
    if len(matching) != 1:
        raise ValueError('approved source-table header has no unique snapshot provenance')
    header = frozen(matching[0]['snapshotPath'])
    if not header.is_relative_to(program):
        raise ValueError('source-table header is not inside the training program snapshot')
    return dict(root=root, run=run, run_id=run_id, test_items=list(test_items), manifest=manifest, address=address,
                registry=registry, inputs=inputs, input_root=input_root, output=output, knowledge=knowledge,
                trials=trials, program=program, header=header, frozen=frozen, entries=entries)


def validate_embedded_paths(value, run, *, parent=''):
    """Validate filesystem fields; selectedPath is an electrical route, not a filename."""
    if isinstance(value, list):
        for child in value:
            validate_embedded_paths(child, run, parent=parent)
    elif isinstance(value, dict):
        for key, child in value.items():
            is_path = key in PATH_KEYS or (key.endswith('Path') and key != 'selectedPath') or parent == 'materialRoots'
            is_locator = key.endswith('Locator') and isinstance(child, str) and bool(re.search(r'\.(json|ya?ml|csv|xlsx|sv|cpp|h|md|txt)(?:[#:]|$)', child, re.I))
            if (is_path or is_locator) and isinstance(child, str) and child:
                file_value = re.split(r'#|:(?=\d+(?::|$))', child, maxsplit=1)[0] if is_locator else child
                candidate = Path(file_value)
                if not candidate.is_absolute():
                    candidate = Path(run) / candidate
                secure_path(candidate, run)
            validate_embedded_paths(child, run, parent=key)


def checked_json(context, file):
    data = read_json(secure_path(file, context['run'], True))
    validate_embedded_paths(data, context['run'])
    return data


def sha_facts(context):
    """Deterministic digests supplied to experts, never computed by the model."""
    files = set()
    for trial in context['trials'].values():
        for file in trial.rglob('*'):
            if file.is_file() and file.suffix.lower() in ('.json', '.yaml', '.cpp', '.txt'):
                files.add(secure_path(file, context['run'], True))
    for tm in context['test_items']:
        for name in ('dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'):
            file = context['output'] / 'dft' / tm / name
            if file.is_file():
                files.add(secure_path(file, context['run'], True))
        source = context['address'].get('registerSources', {}).get(tm)
        if source:
            files.add(context['frozen'](source))
    for name in ('test.cpp', 'sub.cpp'):
        file = context['program'] / name
        if file.is_file():
            files.add(secure_path(file, context['run'], True))
    return [{'path': str(file), 'sha256': digest(file)} for file in sorted(files)]


def prepare_register(context):
    module = importlib.import_module('extract_register_config')
    results = []
    for tm, trial in context['trials'].items():
        manifest = checked_json(context, trial / 'input-manifest.json')
        if manifest.get('status') != 'ready':
            raise ValueError('register preparation requires ready INPUT_SYNC')
        source = context['frozen'](context['address'].get('registerSources', {}).get(tm))

        class RegisterRoot:
            def __init__(self, parts=()):
                self.parts = parts

            def __truediv__(self, part):
                parts = self.parts + (str(part),)
                expected = ('project', 'DALI', 'reg_config', tm.lower() + '.sv')
                if parts != expected[:len(parts)]:
                    raise ValueError('original register extractor requested an unapproved source')
                return source if parts == expected else RegisterRoot(parts)

        target = secure_path(trial / 'strategy' / 'register-config-evidence.json', context['run'])
        with patched(module, ROOT=RegisterRoot()):
            invoke_main(module, ['--tm', tm, '--manifest', trial / 'input-manifest.json', '--out', target])
        evidence = read_json(target)
        if evidence.get('source', {}).get('sha256') != digest(source) or evidence.get('tm') != tm:
            raise ValueError('register extractor source binding differs')
        # Correct the old extractor's hardcoded display locator to the exact file
        # it actually read. All electrical facts/ordered writes remain untouched.
        evidence['source']['path'] = str(source)
        target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        validate_embedded_paths(evidence, context['run'])
        results.append({'tm': tm, 'status': 'passed', 'sourcePath': str(source), 'sourceSha256': digest(source),
                        'evidencePath': str(target), 'evidenceSha256': digest(target), 'orderedWrites': evidence['orderedWrites']})
    return results


@contextlib.contextmanager
def configured(context):
    import dft_source
    values = {'ROOT': context['root'], 'PROJECT_DIR': context['run'], 'INPUT_ROOT': context['input_root'],
              'OUTPUT_ROOT': context['output'], 'ERROR_ROOT': context['run'] / 'errorLog',
              'discover_workbook': lambda root=None: context['inputs']['dft'],
              'discover_schematic': lambda root=None: context['inputs']['schematic']}
    previous = {key: getattr(dft_source, key) for key in values}
    cwd = Path.cwd()
    try:
        for key, value in values.items():
            setattr(dft_source, key, value)
        os.chdir(context['run'])
        yield
    finally:
        for key, value in previous.items():
            setattr(dft_source, key, value)
        os.chdir(cwd)


@contextlib.contextmanager
def patched(module, **values):
    previous = {key: getattr(module, key) for key in values}
    try:
        for key, value in values.items():
            setattr(module, key, value)
        yield
    finally:
        for key, value in previous.items():
            setattr(module, key, value)


def invoke_main(module, arguments):
    previous = sys.argv
    output = io.StringIO()
    try:
        sys.argv = [module.__name__, *map(str, arguments)]
        with contextlib.redirect_stdout(output):
            try:
                result = module.main()
                code = result if isinstance(result, int) else 0
            except SystemExit as error:
                code = error.code or 0
        if code != 0:
            raise ValueError(f'{module.__name__} failed ({code}): {output.getvalue().strip()}')
        return output.getvalue()
    finally:
        sys.argv = previous


def schematic(context):
    import training_schematic
    return training_schematic.execute('validate', run_root=context['run'], input_root=context['input_root'],
        out_dir=context['output'] / 'schematic', source=context['inputs']['schematic'],
        confirmed=context['inputs']['confirmed'], cbit=context['inputs']['cbit'])


def input_sync(context):
    import prepare_input_sync as collector
    import validate_dft_outputs
    address = context['address']
    intent = context['frozen'](address['intentResolutions']) if address.get('intentResolutions') else context['run'] / 'input' / 'absent-intent-resolutions.json'
    special = context['inputs'].get('special', context['run'] / 'input' / 'absent-special-information.json')
    schematic_report = schematic(context)
    results = []
    with patched(collector, ROOT=context['run'], INTENT_RESOLUTIONS=intent, SPECIAL_INFORMATION=special,
                 validate_schematic_outputs=lambda *args, **kwargs: schematic_report):
        for tm, trial in context['trials'].items():
            invoke_main(collector, ['--tm', tm, '--trial-dir', trial])
            manifest_file = trial / 'input-manifest.json'
            manifest = checked_json(context, manifest_file)
            dft = validate_dft_outputs.validate(tm, workbook=context['inputs']['dft'], output_dir=context['output'] / 'dft' / tm)
            reports = {'dft-expert': dft, 'schematic-expert': schematic_report}
            for key, report in [('dft', dft), ('schematic', schematic_report)]:
                manifest['canonicalInputs'][key].update(path=report['canonicalInput']['path'], sha256=report['canonicalInput']['sha256'],
                    requiredOutputs=report['requiredOutputs'], missingOrStaleOutputs=report['missingOrStaleOutputs'], status=report['status'])
            ready = all(report.get('status') == 'ready' for report in reports.values())
            manifest.update(schemaVersion=8, roleGates=reports, status='ready' if ready else 'needs-derived-artifacts',
                globalGate={'name': 'INPUT_SYNC_AGGREGATE', 'status': 'ready' if ready else 'pending'},
                dispatchableRoles=[role for role, report in reports.items() if report.get('status') != 'ready'])
            manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            results.append({'tm': tm, 'status': 'passed' if ready else 'blocked', 'roleGates': reports})
    if any(result['status'] != 'passed' for result in results):
        raise ValueError('INPUT_SYNC source gate is not ready: ' + json.dumps(results, ensure_ascii=False))
    return results


def downstream(context, stage):
    results = []
    for tm, trial in context['trials'].items():
        checked_json(context, trial / 'input-manifest.json')
        strategy_file = trial / 'strategy' / f'{tm.lower()}-resource-config-contract.json'
        checked_json(context, strategy_file)
        if stage == 'STRATEGY':
            module = importlib.import_module('validate_strategy_contract')
            checked_json(context, trial / 'strategy' / 'deliverable-ready.json')
            with patched(module, __file__=str(context['run'] / 'scripts' / 'validate_strategy_contract.py'),
                         approved_source_header=lambda ignored: context['header']):
                output = invoke_main(module, [strategy_file, trial / 'strategy' / 'deliverable-ready.json', '--manifest', trial / 'input-manifest.json'])
            results.append({'tm': tm, 'stdout': output, 'status': 'passed'})
            continue
        method_file = trial / 'method' / f'{tm.lower()}-test-method-contract.json'
        method = checked_json(context, method_file)
        if stage == 'METHOD':
            output = invoke_main(importlib.import_module('validate_method_contract'), [method_file, '--strategy-sha', digest(strategy_file)])
            results.append({'tm': tm, 'stdout': output, 'status': 'passed'})
            continue
        checked_json(context, trial / 'strategy' / 'register-config-evidence.json')
        if stage == 'RULE_REVIEW_METHOD':
            module = importlib.import_module('review_method_batch')
            with patched(module, ROOT=context['run'], OUT=context['output']):
                result = module.one(str(trial))
            if result.get('status') != 'PASS':
                raise ValueError('method review failed: ' + json.dumps(result, ensure_ascii=False))
            results.append(result)
            continue
        implementation = checked_json(context, trial / 'implementation' / 'implementation-manifest.json')
        changes = implementation.get('changes')
        if not isinstance(changes, list) or not changes:
            raise ValueError(f'{tm}: implementation has no actual source changes')
        for change in changes:
            source = Path(change.get('path', ''))
            if not source.is_absolute():
                source = context['run'] / source
            secure_path(source, context['program'], True)
            if not change.get('symbols'):
                raise ValueError(f'{tm}: implementation has no verified symbols')
        if method.get('methodFamily') == 'trim':
            context['frozen']((context['run'] / 'scripts' / 'ptc_trim_validation.py').relative_to(context['root']).as_posix())
    if stage in ('IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION'):
        module = importlib.import_module('verify_implementation_batch')
        with patched(module, PROJECT_ROOT=context['run']):
            output = invoke_main(module, list(context['trials'].values()))
        report = json.loads(output)
        if report.get('status') != 'PASS' or not report.get('checks'):
            raise ValueError('implementation gate returned no actual passing checks')
        covered = {item.get('tm') for item in report['checks']}
        if not set(context['test_items']).issubset(covered):
            raise ValueError('implementation gate omitted a TM')
        return [report]
    if stage == 'RULE_REVIEW_METHOD':
        module = importlib.import_module('review_method_batch')
        # Write only after the entire batch passed; use original artifact writer.
        with patched(module, ROOT=context['run'], OUT=context['output']):
            for tm, result in zip(context['test_items'], results):
                module.write(context['trials'][tm], result)
    return results


def execute(run_id, stage, test_items, action='gate'):
    context = load_context(run_id, test_items)
    if stage not in SUPPORTED or stage not in context['registry'].get('stateMachine', []):
        raise ValueError('stage has no supported training adapter or is absent from the registry')
    definition = context['registry'].get('stages', {}).get(stage, {})
    if definition.get('gate') != GATES.get(stage) or not definition.get('owner'):
        raise ValueError('stage owner/gate is not registered')
    if action not in ('gate', 'prepare-register') or (action == 'prepare-register' and stage != 'STRATEGY'):
        raise ValueError('unsupported stage preparation action')
    command = 'python scripts/training_stage_gate.py --run-id ' + run_id + ' --stage ' + stage + ' --action ' + action + ''.join(' --tm ' + tm for tm in test_items)
    report = {'schemaVersion': 1, 'kind': 'training-stage-gate', 'runId': run_id, 'stage': stage, 'gate': definition['gate'],
              'owner': definition['owner'], 'action': action, 'command': command, 'testItems': list(test_items), 'pipelineCacheKey': context['manifest']['pipelineCacheKey'],
              'startedAt': datetime.now(timezone.utc).isoformat(), 'status': 'blocked', 'exitCode': 2}
    try:
        with configured(context):
            report['results'] = prepare_register(context) if action == 'prepare-register' else input_sync(context) if stage == 'INPUT_SYNC' else downstream(context, stage)
        # Re-verify immutable snapshot inputs before recording success. Mutable VS
        # working files are independently checked by implementation signed hashes.
        load_context(run_id, test_items)
        report['shaFacts'] = sha_facts(context)
        report.update(status='passed', exitCode=0)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        report['error'] = str(error)
    report['finishedAt'] = datetime.now(timezone.utc).isoformat()
    receipt = secure_path(context['run'] / 'verification' / f'stage-{stage.lower()}-{secrets.token_hex(8)}.json', context['run'])
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open('x', encoding='utf-8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    report['receiptPath'] = str(receipt)
    report['receiptSha256'] = digest(receipt)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--stage', required=True)
    parser.add_argument('--tm', action='append', required=True)
    parser.add_argument('--action', choices=['gate', 'prepare-register'], default='gate')
    args = parser.parse_args()
    try:
        report = execute(args.run_id, args.stage, args.tm, args.action)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        report = {'status': 'blocked', 'exitCode': 2, 'error': str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report['exitCode']


if __name__ == '__main__':
    raise SystemExit(main())
