import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { TextDecoder } from 'node:util';

export const TRAINING_DRAFT_FILES = Object.freeze(['instructions.md', 'profile.yaml', 'output-contract.schema.json']);
export const TRAINING_DRAFT_MAX_BYTES = 256 * 1024;
const PROFILE = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
const DEVICE = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');

function fail(code, message) { throw Object.assign(new Error(message), { code }); }

function assertSafe(root, target, { missing = false, directory = false } = {}) {
  const resolved = path.resolve(target);
  const relative = path.relative(root, resolved);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) fail('DRAFT_UNSAFE_PATH', 'draft path escapes workspace');
  let cursor = resolved;
  let leaf;
  while (true) {
    let stat;
    try { stat = fs.lstatSync(cursor); } catch (error) {
      if (error.code !== 'ENOENT' || !missing) throw error;
    }
    if (stat?.isSymbolicLink()) fail('DRAFT_UNSAFE_PATH', 'draft paths cannot contain links or junctions');
    if (stat?.isFile() && stat.nlink !== 1) fail('DRAFT_UNSAFE_PATH', 'draft files cannot be hardlinked');
    if (cursor === resolved) leaf = stat;
    else if (stat && !stat.isDirectory()) fail('DRAFT_UNSAFE_PATH', 'draft ancestor is not a directory');
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  if (!leaf && !missing) fail('DRAFT_NOT_FOUND', 'draft path does not exist');
  if (leaf && (directory ? !leaf.isDirectory() : !leaf.isFile())) fail('DRAFT_UNSAFE_PATH', 'unexpected draft path type');
  return resolved;
}

function profilePath(root, profileId) {
  if (typeof profileId !== 'string' || !PROFILE.test(profileId) || DEVICE.test(profileId)) fail('DRAFT_INVALID_PROFILE', 'invalid profile id');
  return assertSafe(root, path.join(root, 'team/expert-profiles', profileId), { directory: true });
}

function filePath(root, input) {
  if (!TRAINING_DRAFT_FILES.includes(input?.file)) fail('DRAFT_INVALID_FILE', 'file is not an editable draft');
  return assertSafe(root, path.join(profilePath(root, input.profileId), input.file));
}

function readBytes(root, file) {
  assertSafe(root, file);
  const descriptor = fs.openSync(file, fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0));
  try {
    const opened = fs.fstatSync(descriptor);
    const current = fs.lstatSync(assertSafe(root, file));
    if (!opened.isFile() || opened.nlink !== 1 || opened.dev !== current.dev || opened.ino !== current.ino) fail('DRAFT_UNSAFE_PATH', 'draft changed while opening');
    if (opened.size > TRAINING_DRAFT_MAX_BYTES) fail('DRAFT_TOO_LARGE', 'draft exceeds 256 KiB');
    const bytes = fs.readFileSync(descriptor);
    if (bytes.length > TRAINING_DRAFT_MAX_BYTES) fail('DRAFT_TOO_LARGE', 'draft exceeds 256 KiB');
    return bytes;
  } finally { fs.closeSync(descriptor); }
}

function text(bytes) {
  try { return new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes); }
  catch { fail('DRAFT_INVALID_TEXT', 'draft is not valid UTF-8 text'); }
}

export function readTrainingDraft(workspaceRoot, input) {
  const root = path.resolve(workspaceRoot);
  const bytes = readBytes(root, filePath(root, input));
  return { profileId: input.profileId, file: input.file, content: text(bytes), sha256: sha(bytes), sizeBytes: bytes.length };
}

export function listTrainingDrafts(workspaceRoot) {
  const root = path.resolve(workspaceRoot);
  const directory = assertSafe(root, path.join(root, 'team/expert-profiles'), { directory: true });
  return fs.readdirSync(directory).filter((name) => PROFILE.test(name) && !DEVICE.test(name)).sort().flatMap((profileId) => {
    const target = path.join(directory, profileId);
    if (!fs.lstatSync(target).isDirectory()) {
      if (fs.lstatSync(target).isSymbolicLink()) fail('DRAFT_UNSAFE_PATH', 'profile listing contains a link');
      return [];
    }
    profilePath(root, profileId);
    const files = [];
    for (const file of TRAINING_DRAFT_FILES) {
      try {
        const { sha256, sizeBytes } = readTrainingDraft(root, { profileId, file });
        files.push({ file, sha256, sizeBytes });
      } catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
    return files.length ? [{ profileId, files }] : [];
  });
}

/** Writes only an existing draft. A prepared history entry survives any failure
 * so a crash between replacement and audit completion is never called success. */
export function saveTrainingDraft(workspaceRoot, input) {
  if (input?.mode !== 'training') fail('DRAFT_MODE_REQUIRED', 'draft editing requires training mode');
  if (typeof input.content !== 'string') fail('DRAFT_INVALID_TEXT', 'draft content must be text');
  const after = Buffer.from(input.content, 'utf8');
  if (after.length > TRAINING_DRAFT_MAX_BYTES) fail('DRAFT_TOO_LARGE', 'draft exceeds 256 KiB');
  if (text(after) !== input.content) fail('DRAFT_INVALID_TEXT', 'draft contains invalid Unicode');
  if (!/^[a-f0-9]{64}$/.test(input.expectedSha256 ?? '')) fail('DRAFT_CONFLICT', 'expectedSha256 must be a lowercase SHA-256 digest');
  const root = path.resolve(workspaceRoot);
  const target = filePath(root, input);
  const lockFile = assertSafe(root, path.join(path.dirname(target), '.training-draft.lock'), { missing: true });
  let lock;
  try { lock = fs.openSync(lockFile, 'wx'); } catch (error) {
    if (error.code === 'EEXIST') fail('DRAFT_BUSY', 'another edit owns this profile draft');
    throw error;
  }
  let temporary;
  try {
    const before = readBytes(root, target);
    const previousSha256 = sha(before);
    if (previousSha256 !== input.expectedSha256) fail('DRAFT_CONFLICT', 'draft changed since it was read; reload before saving');
    const nextSha256 = sha(after);
    if (nextSha256 === previousSha256) return { profileId: input.profileId, file: input.file, sha256: nextSha256, previousSha256, sizeBytes: after.length, historyId: null, changed: false };
    const historyId = crypto.randomUUID();
    const historyRoot = assertSafe(root, path.join(root, 'Training_Materials/draft-history'), { missing: true, directory: true });
    fs.mkdirSync(historyRoot, { recursive: true });
    assertSafe(root, historyRoot, { directory: true });
    const historyDirectory = assertSafe(root, path.join(historyRoot, historyId), { missing: true, directory: true });
    fs.mkdirSync(historyDirectory);
    const auditFile = path.join(historyDirectory, 'audit.json');
    const audit = { schemaVersion: 1, historyId, mode: 'training', profileId: input.profileId, file: input.file,
      expectedSha256: input.expectedSha256, previousSha256, sha256: nextSha256,
      status: 'prepared', preparedAt: new Date().toISOString() };
    fs.writeFileSync(path.join(historyDirectory, 'before.bin'), before, { flag: 'wx' });
    fs.writeFileSync(path.join(historyDirectory, 'after.bin'), after, { flag: 'wx' });
    fs.writeFileSync(auditFile, `${JSON.stringify(audit, null, 2)}\n`, { flag: 'wx' });
    temporary = assertSafe(root, path.join(path.dirname(target), `.training-draft-${historyId}.tmp`), { missing: true });
    fs.writeFileSync(temporary, after, { flag: 'wx' });
    if (sha(readBytes(root, target)) !== previousSha256) fail('DRAFT_CONFLICT', 'draft changed during save');
    assertSafe(root, temporary);
    fs.renameSync(temporary, target);
    temporary = undefined;
    if (sha(readBytes(root, target)) !== nextSha256) fail('DRAFT_SAVE_FAILED', 'saved draft bytes do not match requested content');
    assertSafe(root, auditFile);
    fs.writeFileSync(auditFile, `${JSON.stringify({ ...audit, status: 'applied', appliedAt: new Date().toISOString() }, null, 2)}\n`);
    return { profileId: input.profileId, file: input.file, sha256: nextSha256, previousSha256, sizeBytes: after.length, historyId, changed: true };
  } finally {
    if (temporary) { try { assertSafe(root, temporary); fs.unlinkSync(temporary); } catch {} }
    fs.closeSync(lock);
    assertSafe(root, lockFile);
    fs.unlinkSync(lockFile);
  }
}
