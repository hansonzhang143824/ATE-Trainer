#!/usr/bin/env python3
"""Create the required DFT YAML companion from the project workbook OVERVIEW sheet.

Standard library plus openpyxl only; no YAML parser dependency.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
import dft_source
import dft_test_condition
from material_plaintext_hash import sha256_plaintext


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def yaml_scalar(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def multi(value: str) -> list:
    return [part.strip() for part in re.split(r'[\n;]+', str(value)) if part.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tm', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--expected-sha')
    ap.add_argument('--workbook', type=Path)
    args = ap.parse_args()
    tm = args.tm.upper()

    try:
        if args.workbook is not None:
            workbook = args.workbook.resolve()
            if not workbook.is_file():
                raise ValueError(f'--workbook is not a file: {workbook}')
            dft_source.ensure_within(args.out, workbook.parent.parent)
        else:
            workbook = dft_source.discover_workbook()
    except ValueError as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        return 2
    digest = sha256_plaintext(workbook)
    if args.expected_sha and digest != args.expected_sha:
        print(f'BLOCKED: workbook SHA-256 {digest} != expected {args.expected_sha}', file=sys.stderr)
        return 2
    rows = dft_source.rows_for(workbook, tm)
    if len(rows) != 1:
        print(f'BLOCKED: expected one {dft_source.OVERVIEW_SHEET} row for {tm}; found {len(rows)}', file=sys.stderr)
        return 2
    row = rows[0]

    pins = []
    for column in ('Code1', 'Code2', 'Code3', 'Dynamic'):
        pins.extend(re.findall(r'\bvset\[([^,\]]+)', str(row.get(column, '')), flags=re.I))
    lines = ['schemaVersion: 1', 'artifact: "dft-conditions"', 'projectId: "DALI"', f'tm: {yaml_scalar(tm)}',
             f'sourcePath: {yaml_scalar(str(workbook))}',
             f'sourceSheet: {yaml_scalar(dft_source.OVERVIEW_SHEET)}',
             f'sourceSha256: {yaml_scalar(digest)}', 'rawIntent:']
    for key, value in row.items():
        if key:
            lines.append(f'  {str(key).replace(" ", "_").replace(chr(10), "_")}: {yaml_scalar(value)}')
    condition=dft_test_condition.derive(row)['testCondition']
    lines += ['derivedTokens:', f'  vsetPins: {yaml_scalar(pins)}', 'testCondition:']
    for key,value in condition.items(): lines.append(f'  {key}: {yaml_scalar(value)}')
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(f'DONE: {out}; sourceSha256={digest}; tm={tm}; outputSha256={sha256(out)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
