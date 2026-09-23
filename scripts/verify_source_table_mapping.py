"""Bind a selected source-table object to exact VS header ports."""

from __future__ import annotations

import json
import re
from pathlib import Path


MACRO = re.compile(r'^\s*#define\s+_PIN_CHANNEL_DEFINE_([A-Za-z0-9_]+)_\s+"([^"\r\n]+)"\s*$')
EXTERN = re.compile(r'^\s*extern\s+([A-Za-z][A-Za-z0-9_]*)\s+([A-Za-z][A-Za-z0-9_]*)\s*;')
PORT = re.compile(r'^S(?P<slot>\d+)_(?P<instrument>[A-Za-z0-9_]+)_(?P<role>FH|SH|FL|SL)(?P<channel>\d+)$')


def _header_index(header_text):
    macros, externs = {}, {}
    for line_number, line in enumerate(header_text.splitlines(), 1):
        macro = MACRO.match(line)
        if macro:
            name, value = macro.groups()
            macros.setdefault(name, []).append((line_number, value.split(',')))
        external = EXTERN.match(line)
        if external:
            category, name = external.groups()
            externs.setdefault(name, []).append((line_number, category))
    return macros, externs


def check_source_table_mapping(contract, header_text):
    """Return exact mapping errors; no fuzzy name matching or fallback."""
    macros, externs = _header_index(header_text)
    errors, evidence = [], []
    for resource in contract.get('resourceAllocation') or []:
        if not isinstance(resource, dict):
            errors.append('resourceAllocation contains an invalid entry')
            continue
        pin = str(resource.get('dutPin') or '<unknown>')
        name = resource.get('sourceTable')
        category = resource.get('instrumentCategory')
        ports = resource.get('ports')
        if not isinstance(name, str) or not name or not isinstance(category, str) or not category:
            errors.append(f'{pin}: sourceTable or instrumentCategory is missing')
            continue
        declarations = externs.get(name, [])
        definitions = macros.get(name, [])
        if len(declarations) != 1 or len(definitions) != 1:
            errors.append(f'{pin}: {name} needs one exact extern and one exact _PIN_CHANNEL_DEFINE_ macro')
            continue
        extern_line, actual_category = declarations[0]
        macro_line, macro_ports = definitions[0]
        if actual_category != category:
            errors.append(f'{pin}: {name} extern type {actual_category} differs from {category}')
        if not isinstance(ports, list) or len(ports) != 2:
            errors.append(f'{pin}: expected exactly one Force and one Sense source port')
            continue
        parsed = [PORT.fullmatch(str(port)) for port in ports]
        if any(match is None for match in parsed):
            errors.append(f'{pin}: source port cannot be parsed as slot/instrument/role/channel')
            continue
        values = [match.groupdict() for match in parsed]
        roles = {value['role'][0] for value in values}
        if roles != {'F', 'S'}:
            errors.append(f'{pin}: source ports must contain one Force and one Sense leg')
        coordinates = {(value['slot'], value['channel'], value['instrument']) for value in values}
        if len(coordinates) != 1:
            errors.append(f'{pin}: Force and Sense do not name the same slot, channel and instrument')
            continue
        slot, channel, instrument = next(iter(coordinates))
        if instrument != actual_category:
            errors.append(f'{pin}: source port instrument {instrument} differs from extern type {actual_category}')
        coordinate = f'S{slot}_{channel}'
        if coordinate not in macro_ports:
            errors.append(f'{pin}: {name} macro does not contain {coordinate}')
        evidence.append({'dutPin': pin, 'sourceTable': name, 'sourcePorts': ports,
                         'macroCoordinate': coordinate, 'macroLine': macro_line,
                         'externLine': extern_line, 'externType': actual_category})
    return {'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'evidence': evidence}


def approved_source_header(project_info_path):
    info = json.loads(Path(project_info_path).read_text(encoding='utf-8'))
    if info.get('project') != 'DALI' or not (info.get('approval') or {}).get('approvedBy'):
        raise ValueError('Project_Info.json does not approve the DALI project')
    program_root = (info.get('inputs') or {}).get('program')
    if not isinstance(program_root, str) or not program_root:
        raise ValueError('Project_Info.json has no approved program source root')
    header = Path(program_root) / 'Pin_Channel_define.h'
    if not header.is_file():
        raise FileNotFoundError(f'approved VS source header is missing: {header}')
    return header
