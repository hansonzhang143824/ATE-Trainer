#!/usr/bin/env python3
"""Validate that every signed-method requirement has a reachable code primitive before t7 writes source."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

EXIT_PASS = 0
EXIT_INVALID = 1
EXIT_BLOCKED = 2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    print(f"INVALID: {message}")
    raise SystemExit(EXIT_INVALID)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('artifact', type=Path, help='preflight-capability.json')
    args = parser.parse_args()
    try:
        doc = json.loads(args.artifact.read_text(encoding='utf-8'))
    except Exception as error:
        fail(f"cannot parse artifact: {error}")
    if not isinstance(doc, dict): fail('artifact root must be an object')
    for key in ('runId', 'methodContract', 'targetSources', 'requirements', 'verdict'):
        if key not in doc: fail(f'missing {key}')
    if doc['verdict'] not in ('pass', 'blocked'): fail('verdict must be pass or blocked')
    if not isinstance(doc['requirements'], list) or not doc['requirements']: fail('requirements must be a non-empty array')
    contract = doc['methodContract']
    if not isinstance(contract, dict) or not isinstance(contract.get('path'), str) or not isinstance(contract.get('sha256'), str):
        fail('methodContract requires path and sha256')
    contract_path = Path(contract['path'])
    if not contract_path.is_file(): fail(f'methodContract path missing: {contract_path}')
    if sha256(contract_path) != contract['sha256']: fail('methodContract hash mismatch')
    source_bytes: dict[str, bytes] = {}
    for item in doc['targetSources']:
        if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not isinstance(item.get('sha256'), str):
            fail('every target source requires path and sha256')
        path = Path(item['path'])
        if not path.is_file(): fail(f'target source missing: {path}')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']: fail(f'target source hash mismatch: {path}')
        source_bytes[str(path)] = data
    api_bytes: dict[str, bytes] = {}
    api_sources = doc.get('apiSources', [])
    if not isinstance(api_sources, list): fail('apiSources must be an array when present')
    for item in api_sources:
        if not isinstance(item, dict): fail('api source must be an object')
        for key in ('path', 'sha256', 'role', 'compilerIncludeEvidence'):
            if not isinstance(item.get(key), str) or not item[key].strip(): fail(f'api source requires non-empty {key}')
        path = Path(item['path'])
        if path.suffix.lower() not in ('.h', '.hpp', '.inl'): fail(f'api source is not a header: {path}')
        if not path.is_file(): fail(f'api source missing: {path}')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']: fail(f'api source hash mismatch: {path}')
        api_bytes[str(path)] = data
    evidence_bytes = tuple(source_bytes.values()) + tuple(api_bytes.values())
    statuses = []
    for item in doc['requirements']:
        if not isinstance(item, dict): fail('requirement must be object')
        for key in ('id', 'contractEvidence', 'requiredSymbols', 'verdict'):
            if key not in item: fail(f'requirement missing {key}')
        if item['verdict'] not in ('supported', 'blocked'): fail(f"bad verdict for {item.get('id')}")
        if not isinstance(item['contractEvidence'], str) or not item['contractEvidence'].strip(): fail(f"empty contractEvidence for {item['id']}")
        symbols = item['requiredSymbols']
        if not isinstance(symbols, list) or not symbols or not all(isinstance(s, str) and s for s in symbols): fail(f"bad requiredSymbols for {item['id']}")
        found = [symbol for symbol in symbols if any(symbol.encode('utf-8') in data for data in evidence_bytes)]
        if item.get('requiresSemanticMapping') is True:
            mapping = item.get('semanticMapping')
            if not isinstance(mapping, dict): fail(f'readback requirement needs semanticMapping: {item["id"]}')
            for key in ('apiSymbol', 'relayBankBitMapping', 'sourceReadbackMethod', 'evidence'):
                if not mapping.get(key): fail(f'readback semanticMapping missing {key}: {item["id"]}')
        if item['verdict'] == 'supported' and len(found) != len(symbols):
            fail(f"supported requirement has no reachable declared symbol: {item['id']}")
        statuses.append(item['verdict'])
    expected = 'pass' if all(status == 'supported' for status in statuses) else 'blocked'
    if doc['verdict'] != expected: fail(f"verdict must be {expected}")
    print(f"{doc['verdict'].upper()}: {len(statuses)} requirements; method hash and target hashes verified")
    return EXIT_PASS if expected == 'pass' else EXIT_BLOCKED

if __name__ == '__main__':
    raise SystemExit(main())
