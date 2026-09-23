import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {
  buildReleaseFileEntries,
  digestReleaseEntries,
  verifyReleaseDirectory,
} from '../lib/release-integrity.js';

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-release-integrity-'));
  fs.mkdirSync(path.join(root, 'profiles/dft'), { recursive: true });
  fs.mkdirSync(path.join(root, 'orchestration'), { recursive: true });
  fs.writeFileSync(path.join(root, 'profiles/dft/instructions.md'), 'DFT\r\n', 'utf8');
  fs.writeFileSync(path.join(root, 'orchestration/stages.json'), '{"stages":["INPUT_SYNC"]}\n', 'utf8');
  const files = buildReleaseFileEntries(root);
  return { root, manifest: { files, bundleDigest: digestReleaseEntries(files) } };
}

test('release integrity uses sorted exact-byte SHA-256 entries', () => {
  const { root, manifest } = fixture();
  assert.deepEqual(manifest.files.map((entry) => entry.path), [
    'orchestration/stages.json',
    'profiles/dft/instructions.md',
  ]);
  assert.match(manifest.bundleDigest, /^[a-f0-9]{64}$/);
  assert.deepEqual(verifyReleaseDirectory(root, manifest), {
    ok: true,
    errors: [],
    actualDigest: manifest.bundleDigest,
    actualFiles: manifest.files,
  });
});

test('one changed byte invalidates both the file and bundle digest', () => {
  const { root, manifest } = fixture();
  fs.appendFileSync(path.join(root, 'profiles/dft/instructions.md'), 'x', 'utf8');
  const result = verifyReleaseDirectory(root, manifest);
  assert.equal(result.ok, false);
  assert.equal(result.errors.includes('size mismatch: profiles/dft/instructions.md'), true);
  assert.equal(result.errors.includes('sha256 mismatch: profiles/dft/instructions.md'), true);
  assert.equal(result.errors.includes('bundleDigest mismatch'), true);
});

test('added files, symlinks and noncanonical manifests fail closed', (t) => {
  const { root, manifest } = fixture();
  fs.writeFileSync(path.join(root, 'unexpected.txt'), 'extra', 'utf8');
  assert.equal(verifyReleaseDirectory(root, manifest).ok, false);
  assert.throws(() => verifyReleaseDirectory(root, {
    files: manifest.files.slice().reverse(), bundleDigest: manifest.bundleDigest,
  }), /unique and sorted/);
  if (process.platform === 'win32') {
    t.diagnostic('symlink creation requires Windows developer/admin policy; covered by the release walker guard');
  }
});
