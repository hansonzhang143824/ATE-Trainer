#!/usr/bin/env python3
"""Training-only schematic inventory. No path parser, semantic reviewer or stage gate.

The full seven-product schematic workflow is retained separately for later
incremental training. This command deliberately emits only the statistic TXT.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import defaultdict
from pathlib import Path

from material_plaintext_hash import sha256_plaintext


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'scripts/schematic_parse/scripts/csv_schematic_adapter_v2.py'


def adapter_module():
    spec = importlib.util.spec_from_file_location('schematic_csv_inventory_adapter', ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def numbered(base: str) -> str:
    match = re.match(r'^K(\d+)', base)
    return f'{int(match.group(1)):04d}:{base}' if match else base


def statistic(source: Path, confirmed: Path, channelmap: Path) -> str:
    adapter = adapter_module()
    rows, warnings = adapter.load_csv(source)
    graph = adapter.build_graph(rows)
    ports = graph['ports']
    dut = sorted(name for name, direction in ports.items() if direction == 'OUTPUT')
    source_ports = sorted(name for name, direction in ports.items() if direction == 'INOUT')
    pin_ports = defaultdict(set)
    for port in dut:
        match = re.fullmatch(r'(.+)_([FS])_S\d+', port)
        pin_ports[match.group(1) if match else port].add(match.group(2) if match else '-')
    kelvin = sorted(pin for pin, sides in pin_ports.items() if {'F', 'S'} <= sides)
    non_kelvin = sorted(set(pin_ports) - set(kelvin))
    source_groups = defaultdict(list)
    for port in source_ports:
        slot = re.match(r'^S(\d+)_', port)
        slot = slot.group(1) if slot else ''
        kind = {'1': 'FPVIe', '3': 'FXVIe_PLUS', '5': 'ACM200', '8': 'QVMe',
                '10': 'QTMUe', '24': 'DCM'}.get(slot)
        if slot == '34':
            kind = '电源' if '5V' in port.upper() else 'DIO(数字)'
        source_groups[kind or 'OTHER'].append(port)
    relays = sorted((name for name in graph['instances'] if re.match(r'^K\d+_', name)), key=numbered)
    components = defaultdict(list)
    for name, kind in graph['instances'].items():
        if name not in relays:
            components[kind].append(name)
    try:
        confirmation = json.loads(confirmed.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as error:
        raise ValueError(f'confirmed schematic input is unreadable: {error}') from error
    if not isinstance(confirmation, dict):
        raise ValueError('confirmed schematic input must be an object')
    # Retain the confirmed override identities without inferring relay routes.
    overrides = confirmation.get('relay_class') or {}
    if not isinstance(overrides, dict):
        raise ValueError('relay_class confirmation must be an object')
    header = channelmap.read_text(encoding='utf-8', errors='ignore')
    channel_names = sorted(set(re.findall(r'^\s*extern\s+\w+\s+(\w+)\s*;', header, re.M)))
    lines = [
        '=' * 70,
        'Component-Statistic — 原理图 CSV 组件清单（单项训练）',
        '范围: 只统计输入；未生成 SCH-Connect-Map，未做通路/语义/INPUT_SYNC 门禁',
        '=' * 70, '',
        f'## 任务一: DUT PIN ({len(pin_ports)}个, {len(dut)}个端口)',
        f'  Kelvin ({len(kelvin)}):',
        '    ' + ', '.join(f'{name}(Kelvin)' for name in kelvin),
        f'  Non-Kelvin ({len(non_kelvin)}):',
        '    ' + ', '.join(f'{name}(Non-Kelvin)' for name in non_kelvin), '',
        f'## 任务二: 源表 ({len(source_ports)}个端口)',
    ]
    for kind, names in sorted(source_groups.items()):
        lines.extend((f'  {kind} ({len(names)}):', '    ' + ', '.join(sorted(names))))
    lines.extend(('', f'## 任务二b: 源表名映射 ({len(channel_names)}个声明)',
                  '    ' + ', '.join(channel_names), '',
                  f'## 任务三: 继电器 ({len(relays)}个)',
                  '    ' + ', '.join(relays),
                  f'  已确认分类覆盖 ({len(overrides)}):',
                  '    ' + ', '.join(f'{name}={value}' for name, value in sorted(overrides.items())),
                  '  自动通路分类: 暂不执行；将在后续单项训练中恢复', '',
                  f'## 任务四: 元器件 ({sum(map(len, components.values()))}个)'))
    for kind, names in sorted(components.items()):
        lines.extend((f'  {kind} ({len(names)}):', '    ' + ', '.join(sorted(names))))
    lines.extend(('', f'## 任务五: NET ({len(graph["nets"])}个)',
                  '    ' + ', '.join(sorted(graph['nets'])), '',
                  f'## CSV 解析警告 ({len(warnings)})'))
    lines.extend('  - ' + warning for warning in warnings)
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'confirmed', 'channelmap', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    for item in (args.source, args.confirmed, args.channelmap):
        if not item.is_file():
            parser.error(f'missing frozen input: {item}')
    if args.out.name != 'Component-Statistic.txt':
        parser.error('output must be Component-Statistic.txt')
    content = statistic(args.source, args.confirmed, args.channelmap)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(content, encoding='utf-8')
    import hashlib
    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    print(json.dumps({'status': 'STATISTIC_ONLY', 'sourceSha256': sha256_plaintext(args.source),
                      'confirmedSha256': sha256_plaintext(args.confirmed),
                      'channelmapSha256': sha256_plaintext(args.channelmap),
                      'outputPath': str(args.out.resolve()), 'outputSha256': digest}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
