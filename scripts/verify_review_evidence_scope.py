#!/usr/bin/env python3
"""Validate bounded review evidence and reject hollow zero-candidate passes."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ALLOWED_KINDS = {'presence', 'capability', 'absence'}
ALLOWED_STATUS = {'pass', 'fail', 'needs-revision', 'blocked'}

def blocked(message: str) -> int:
    print(f'BLOCKED: {message}')
    return 2

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', required=True, help='review-evidence-scope.json')
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.evidence).read_bytes().decode('utf-8-sig'))
    except Exception as exc:
        return blocked(f'cannot read evidence JSON: {exc}')
    if data.get('schemaVersion') != 1 or not isinstance(data.get('snapshotPath'), str):
        return blocked('schemaVersion=1 and snapshotPath are required')
    checks = data.get('checks')
    if not isinstance(checks, list) or not checks:
        return blocked('nonempty checks[] is required')
    for index, check in enumerate(checks):
        prefix = f'checks[{index}]'
        if not isinstance(check, dict): return blocked(f'{prefix} must be an object')
        if not isinstance(check.get('id'), str) or not check['id']:
            return blocked(f'{prefix}.id is required')
        kind, status = check.get('assertionKind'), check.get('status')
        if kind not in ALLOWED_KINDS or status not in ALLOWED_STATUS:
            return blocked(f'{prefix} has invalid assertionKind or status')
        scope = check.get('scope')
        if not isinstance(scope, dict) or not isinstance(scope.get('files'), list) or not scope['files'] or any(not isinstance(x, str) or not x for x in scope['files']):
            return blocked(f'{prefix}.scope.files must name every searched file')
        if not isinstance(scope.get('query'), str) or not scope['query']:
            return blocked(f'{prefix}.scope.query is required')
        count = check.get('candidateCount')
        if not isinstance(count, int) or count < 0:
            return blocked(f'{prefix}.candidateCount must be a nonnegative integer')
        evidence = check.get('evidence')
        if not isinstance(evidence, list) or not evidence or any(not isinstance(x, str) or not x for x in evidence):
            return blocked(f'{prefix}.evidence must cite output files or line records')
        if count == 0 and status == 'pass' and kind != 'absence':
            return blocked(f'{prefix} is a hollow pass: zero candidates cannot prove a {kind} assertion')
        if count == 0 and kind == 'absence' and status not in {'pass', 'fail'}:
            return blocked(f'{prefix}: absence assertion with zero candidates needs an explicit pass/fail conclusion')
    print(f'PASS: {len(checks)} bounded review evidence checks are valid')
    return 0

if __name__ == '__main__':
    sys.exit(main())
