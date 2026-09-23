#!/usr/bin/env python3
"""Project_Info: the user-confirmed input locations for this project.

Read at the start of every project run. If the file is missing, incomplete or not
approved, the run stops and the user is asked to approve or modify it.

Material layout inside the project directory is fixed:
  Input_GlobalMaterial/    the only source material a parsing role may read
  Output_Global_Material/  the only place a parsing role may write
  ErrorLog/                the only place a parsing role may write an error log
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
PROJECT_INFO = ROOT / 'Project_Info.json'
KEYS = ('dft', 'schematic', 'cbit', 'program')
LABELS = {'dft': 'DFT material (workbook)', 'schematic': 'schematic material',
          'cbit': 'CBIT table', 'program': 'program source'}
MATERIAL_KEYS = ('dft', 'schematic', 'cbit')
ROOT_KEYS = ('input', 'output', 'errorLog')
ROOT_LABELS = {'input': 'input material root', 'output': 'parsing output root', 'errorLog': 'error log root'}
ROOT_ATTRS = {'input': 'INPUT_ROOT', 'output': 'OUTPUT_ROOT', 'errorLog': 'ERROR_ROOT'}


def load() -> dict | None:
    try:
        data = json.loads(PROJECT_INFO.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def inputs_digest(info: dict) -> str:
    payload = {'project': info.get('project'), 'projectDir': info.get('projectDir'),
               'roots': info.get('roots'), 'inputs': info.get('inputs')}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def resolve(path_value: str) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else (ROOT / path)


def relative(path) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace('\\', '/')
    except ValueError:
        return str(path)


def material_root(kind: str) -> Path:
    import dft_source
    return getattr(dft_source, ROOT_ATTRS[kind])


def propose() -> dict:
    """Candidate locations discovered on disk, offered to the user for approval."""
    import dft_source
    roots = {key: relative(material_root(key)) for key in ROOT_KEYS}
    inputs = {}
    try:
        inputs['dft'] = relative(dft_source.discover_workbook())
    except Exception:
        inputs['dft'] = ''
    try:
        inputs['schematic'] = relative(dft_source.discover_schematic())
    except Exception:
        inputs['schematic'] = ''
    cbits = dft_source.cbit_candidates()
    inputs['cbit'] = relative(cbits[0]) if len(cbits) == 1 else ([relative(c) for c in cbits] if cbits else '')
    try:
        config = json.loads((ROOT / 'project_config.json').read_text(encoding='utf-8'))
    except Exception:
        config = {}
    inputs['program'] = str((config.get('inputs') or {}).get('vs_src_dir', ''))
    return {'schemaVersion': 2, 'project': 'DALI',
            'description': 'User-confirmed project input locations. Read at the start of every project run.',
            'projectDir': 'project/DALI', 'roots': roots, 'inputs': inputs,
            'approval': {'approvedBy': None, 'approvedAt': None, 'inputsDigest': None}}


def problems(info: dict | None) -> list:
    """Everything that makes this Project_Info unusable, in plain sentences."""
    if info is None:
        return ['%s is missing or is not valid JSON' % PROJECT_INFO.name]
    found = []
    project_dir = info.get('projectDir')
    if not project_dir:
        found.append('projectDir is empty')
    elif not resolve(project_dir).is_dir():
        found.append('projectDir does not exist: %s' % project_dir)
    roots = info.get('roots')
    if not isinstance(roots, dict):
        found.append('roots is missing')
        roots = {}
    for key in ROOT_KEYS:
        value = roots.get(key)
        if not value:
            found.append('%s (%s) is not set' % (ROOT_LABELS[key], key))
        elif not resolve(value).is_dir():
            found.append('%s (%s) does not exist: %s' % (ROOT_LABELS[key], key, value))
    inputs = info.get('inputs')
    if not isinstance(inputs, dict):
        return found + ['inputs is missing']
    input_root = resolve(roots.get('input')) if roots.get('input') else None
    for key in KEYS:
        entry = inputs.get(key)
        values = entry if isinstance(entry, list) else [entry]
        values = [v for v in values if v]
        if not values:
            found.append('%s (%s) is not set' % (LABELS[key], key))
            continue
        for value in values:
            path = resolve(value)
            if not path.exists():
                found.append('%s (%s) does not exist: %s' % (LABELS[key], key, value))
            elif key in MATERIAL_KEYS and input_root is not None:
                try:
                    resolved, base = path.resolve(), input_root.resolve()
                except OSError:
                    continue
                if resolved != base and base not in resolved.parents:
                    found.append('%s (%s) is outside the input material root: %s' % (LABELS[key], key, value))
    approval = info.get('approval') or {}
    if approval.get('inputsDigest') != inputs_digest(info):
        found.append('the locations are not approved yet, or were changed since the last approval')
    return found


def stamp_approval(info: dict, approver: str, timestamp: str) -> dict:
    info['approval'] = {'approvedBy': approver, 'approvedAt': timestamp, 'inputsDigest': inputs_digest(info)}
    return info


def write(info: dict) -> Path:
    PROJECT_INFO.write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return PROJECT_INFO
