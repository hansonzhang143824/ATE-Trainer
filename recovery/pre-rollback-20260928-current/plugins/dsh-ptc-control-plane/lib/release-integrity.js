import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const SHA256 = /^[a-f0-9]{64}$/;

export function sha256Bytes(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function normalizeRelative(file) {
  return file.split(path.sep).join('/');
}

function walk(directory, relative = '') {
  const entries = fs.readdirSync(path.join(directory, relative), { withFileTypes: true })
    .sort((left, right) => left.name < right.name ? -1 : left.name > right.name ? 1 : 0);
  const files = [];
  for (const entry of entries) {
    const child = relative === '' ? entry.name : path.join(relative, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`release bundles cannot contain symbolic links: ${normalizeRelative(child)}`);
    if (entry.isDirectory()) files.push(...walk(directory, child));
    else if (entry.isFile()) files.push(child);
    else throw new Error(`unsupported release entry: ${normalizeRelative(child)}`);
  }
  return files;
}

/** Hash every exact on-disk byte in a release snapshot except its manifest. */
export function buildReleaseFileEntries(releaseDirectory) {
  const root = path.resolve(releaseDirectory);
  return walk(root)
    .filter((file) => normalizeRelative(file) !== 'release-manifest.json')
    .map((file) => {
      const bytes = fs.readFileSync(path.join(root, file));
      return { path: normalizeRelative(file), sha256: sha256Bytes(bytes), size: bytes.length };
    });
}

/** Digest the canonical file list, not the JSON rendering of the manifest. */
export function digestReleaseEntries(entries) {
  const canonical = entries.map((entry) => `${entry.path}\0${entry.size}\0${entry.sha256}\n`).join('');
  return sha256Bytes(Buffer.from(canonical, 'utf8'));
}

function validateExpected(entries) {
  if (!Array.isArray(entries)) throw new Error('release manifest files must be an array');
  let previous = '';
  for (const entry of entries) {
    if (typeof entry?.path !== 'string' || entry.path === '' || entry.path.includes('\\') || entry.path.startsWith('/') || entry.path.split('/').includes('..')) {
      throw new Error('release manifest contains an invalid file path');
    }
    if (entry.path <= previous) throw new Error('release manifest files must be unique and sorted');
    if (!Number.isSafeInteger(entry.size) || entry.size < 0) throw new Error(`invalid size for ${entry.path}`);
    if (typeof entry.sha256 !== 'string' || !SHA256.test(entry.sha256)) throw new Error(`invalid sha256 for ${entry.path}`);
    previous = entry.path;
  }
}

export function verifyReleaseDirectory(releaseDirectory, manifest) {
  validateExpected(manifest?.files);
  const actual = buildReleaseFileEntries(releaseDirectory);
  const expected = manifest.files;
  const errors = [];
  const count = Math.max(actual.length, expected.length);
  for (let index = 0; index < count; index += 1) {
    const wanted = expected[index];
    const found = actual[index];
    if (wanted?.path !== found?.path) {
      errors.push(`file list mismatch at ${index}: expected ${wanted?.path ?? '<none>'}, found ${found?.path ?? '<none>'}`);
      continue;
    }
    if (wanted.size !== found.size) errors.push(`size mismatch: ${wanted.path}`);
    if (wanted.sha256 !== found.sha256) errors.push(`sha256 mismatch: ${wanted.path}`);
  }
  const actualDigest = digestReleaseEntries(actual);
  if (typeof manifest.bundleDigest !== 'string' || !SHA256.test(manifest.bundleDigest)) {
    errors.push('bundleDigest is not lowercase SHA-256');
  } else if (manifest.bundleDigest !== actualDigest) {
    errors.push('bundleDigest mismatch');
  }
  return { ok: errors.length === 0, errors, actualDigest, actualFiles: actual };
}
