#!/usr/bin/env python3
"""Create and verify a byte-exact, immutable review snapshot.

This gate removes the t8/t10/t11 race: a reviewer works only from a copied source
snapshot, and its final verdict is invalid if the live file changes before closure.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_bytes().decode('utf-8-sig'))
    except Exception as exc:
        raise ValueError(f'cannot read JSON {path}: {exc}') from exc


def resolve(raw: str) -> Path:
    return Path(raw.replace('/', '\\'))


def fail(message: str) -> int:
    print(f'BLOCKED: {message}')
    return 2


def create(args: argparse.Namespace) -> int:
    manifest_path = Path(args.implementation_manifest)
    manifest = load_json(manifest_path)
    changes = manifest.get('changes')
    if not isinstance(changes, list) or not changes:
        return fail('implementation manifest has no changes[]')
    copy_dir = Path(args.copy_dir)
    copy_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for index, change in enumerate(changes, 1):
        if not isinstance(change, dict) or not isinstance(change.get('path'), str) or not isinstance(change.get('afterSha256'), str):
            return fail(f'changes[{index - 1}] needs path and afterSha256')
        source = resolve(change['path'])
        if not source.is_file():
            return fail(f'source missing: {source}')
        actual = sha256(source)
        expected = change['afterSha256'].lower()
        if actual != expected:
            return fail(f'source differs from implementation manifest: {source}; expected {expected}, got {actual}')
        copy_path = copy_dir / f'{index:02d}-{source.name}'
        shutil.copyfile(source, copy_path)
        copied = sha256(copy_path)
        if copied != actual:
            return fail(f'copy is not byte-identical: {copy_path}')
        items.append({'sourcePath': str(source), 'reviewCopyPath': str(copy_path), 'sha256': actual, 'bytes': source.stat().st_size})
    snapshot = {
        'schemaVersion': 1,
        'purpose': 'immutable-review-snapshot',
        'implementationManifestPath': str(manifest_path),
        'implementationManifestSha256': sha256(manifest_path),
        'runId': manifest.get('runId'),
        'sources': items,
    }
    out = Path(args.snapshot)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'PASS: created {out} with {len(items)} byte-exact review copy/copies')
    return 0


def verify(args: argparse.Namespace) -> int:
    snapshot_path = Path(args.snapshot)
    data = load_json(snapshot_path)
    if data.get('schemaVersion') != 1 or not isinstance(data.get('sources'), list) or not data['sources']:
        return fail('invalid snapshot: schemaVersion=1 and nonempty sources[] are required')
    manifest = Path(data.get('implementationManifestPath', ''))
    if not manifest.is_file() or sha256(manifest) != data.get('implementationManifestSha256'):
        return fail('implementation manifest changed after snapshot creation')
    for index, item in enumerate(data['sources']):
        required = ('sourcePath', 'reviewCopyPath', 'sha256')
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) for k in required):
            return fail(f'sources[{index}] is malformed')
        source, copy = resolve(item['sourcePath']), resolve(item['reviewCopyPath'])
        if not source.is_file() or not copy.is_file():
            return fail(f'sources[{index}] source or review copy is missing')
        expected = item['sha256'].lower()
        live, copied = sha256(source), sha256(copy)
        if copied != expected:
            return fail(f'review copy changed: {copy}')
        if live != expected:
            return fail(f'live source changed during review: {source}; do not issue a verdict, create a new snapshot')
    print(f'PASS: frozen snapshot is current and byte-exact: {snapshot_path}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True, dest='command')
    c = sub.add_parser('create')
    c.add_argument('--implementation-manifest', required=True)
    c.add_argument('--copy-dir', required=True)
    c.add_argument('--snapshot', required=True)
    v = sub.add_parser('verify')
    v.add_argument('--snapshot', required=True)
    args = parser.parse_args()
    try:
        return create(args) if args.command == 'create' else verify(args)
    except ValueError as exc:
        return fail(str(exc))

if __name__ == '__main__':
    sys.exit(main())

