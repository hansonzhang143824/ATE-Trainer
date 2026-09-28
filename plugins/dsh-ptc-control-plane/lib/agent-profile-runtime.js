import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';

/**
 * Configuration driven Agent profile runtime.
 *
 * A profile is the complete, host owned definition under team/expert-profiles.
 * A clone gets a new profile id and its own revision manifest; it never shares
 * files with the source profile.  The arithmetic eight-expert smoke path has
 * its own fixed contract and deliberately does not use this resolver.
 */
export const PROFILE_ID = /^[a-z][a-z0-9-]{1,63}$/;
export const REVISION_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const DEVICE = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;
const POINTER_FILE = 'agent-manifest.json';
const GENERATED_DIR = 'versions';
const MANIFEST_FILE = 'manifest.json';
const MANIFEST_SCHEMA = 1;

const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const jsonBytes = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));

function fail(message) { throw new Error(`agent profile: ${message}`); }

function id(value, label = 'profile id') {
  if (typeof value !== 'string' || !PROFILE_ID.test(value) || DEVICE.test(value)
      || /[. ]$/.test(value)) fail(`invalid ${label}`);
  return value;
}

function revision(value) {
  if (typeof value !== 'string' || !REVISION_ID.test(value) || DEVICE.test(value)
      || /[. ]$/.test(value)) fail('invalid revision id');
  return value;
}

function rootFor(workspaceRoot, profileId) {
  const root = path.resolve(workspaceRoot);
  const profileRoot = assertSafeRunPath(root, path.join(root, 'team', 'expert-profiles', id(profileId)));
  try {
    const stat = fs.lstatSync(profileRoot);
    if (!stat.isDirectory() || stat.isSymbolicLink()) fail('profile root must be a regular directory');
  } catch (error) {
    if (error?.code === 'ENOENT') fail(`unknown expert profile: ${profileId}`);
    throw error;
  }
  return { root, profileRoot };
}

function assertNoLinks(file) {
  const stat = fs.lstatSync(file);
  if (stat.isSymbolicLink()) fail(`profile contains a link: ${file}`);
  if (stat.isDirectory()) for (const entry of fs.readdirSync(file)) assertNoLinks(path.join(file, entry));
}

function parseProfileYaml(file) {
  let text = '';
  try { text = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''); } catch { return {}; }
  const fields = {};
  for (const name of ['id', 'displayName', 'executionClass', 'stage', 'ownerRole', 'presetId']) {
    const match = text.match(new RegExp(`^${name}\\s*:\\s*([^#\\r\\n]+)`, 'mi'));
    if (match) fields[name] = match[1].trim().replace(/^['"]|['"]$/g, '');
  }
  return fields;
}

function collectFiles(profileRoot) {
  const files = [];
  function visit(directory, relative = '') {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      // Revisions are immutable history, not part of the current definition.
      // The pointer is generated metadata and is excluded to avoid a cycle.
      if (!relative && (entry.name === GENERATED_DIR || entry.name === POINTER_FILE)) continue;
      const absolute = path.join(directory, entry.name);
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isSymbolicLink()) fail(`profile contains a link: ${absolute}`);
      if (entry.isDirectory()) visit(absolute, child);
      else if (entry.isFile()) {
        const bytes = fs.readFileSync(absolute);
        files.push({ path: child.replaceAll('\\', '/'), bytes: bytes.length, sha256: digest(bytes) });
      } else fail(`profile contains unsupported file: ${absolute}`);
    }
  }
  visit(profileRoot);
  return files;
}

function manifestValue(profileRoot, profileId, revisionId, baseProfileId = profileId) {
  const profile = parseProfileYaml(path.join(profileRoot, 'profile.yaml'));
  const files = collectFiles(profileRoot);
  const contentDigest = digest(jsonBytes(files));
  const value = {
    schemaVersion: MANIFEST_SCHEMA,
    kind: 'agent-profile-manifest',
    profileId,
    baseProfileId,
    revisionId,
    contentDigest,
    files,
    executionClass: profile.executionClass ?? null,
    ownerRole: profile.ownerRole ?? null,
    generatedAt: new Date().toISOString(),
  };
  const manifestDigest = digest(jsonBytes(value));
  return { ...value, manifestDigest };
}

function validateManifest(manifest, expectedProfileId, expectedRevision) {
  if (!manifest || manifest.schemaVersion !== MANIFEST_SCHEMA || manifest.kind !== 'agent-profile-manifest'
      || manifest.profileId !== expectedProfileId || !REVISION_ID.test(manifest.revisionId ?? '')
      || (expectedRevision !== undefined && manifest.revisionId !== expectedRevision)
      || !/^[a-f0-9]{64}$/.test(manifest.contentDigest ?? '')
      || !/^[a-f0-9]{64}$/.test(manifest.manifestDigest ?? '') || !Array.isArray(manifest.files)) {
    fail('invalid profile manifest');
  }
  const withoutDigest = { ...manifest };
  delete withoutDigest.manifestDigest;
  if (digest(jsonBytes(withoutDigest)) !== manifest.manifestDigest) fail('profile manifest digest mismatch');
  if (digest(jsonBytes(manifest.files)) !== manifest.contentDigest) fail('profile content digest mismatch');
  return manifest;
}

function manifestPath(profileRoot, revisionId) {
  return path.join(profileRoot, GENERATED_DIR, revision(revisionId), MANIFEST_FILE);
}

/** Build an immutable manifest from the current profile definition. */
export function readAgentProfileManifest(workspaceRoot, profileId, options = {}) {
  const { profileRoot } = rootFor(workspaceRoot, profileId);
  const pointerFile = path.join(profileRoot, POINTER_FILE);
  let pointer;
  try { pointer = readJson(pointerFile); } catch { pointer = undefined; }
  const requested = options.revisionId ?? pointer?.revisionId;
  let manifest;
  let file;
  if (requested !== undefined) {
    revision(requested);
    file = manifestPath(profileRoot, requested);
    try {
      manifest = validateManifest(readJson(file), profileId, requested);
      const currentFiles = collectFiles(profileRoot);
      if (JSON.stringify(currentFiles) !== JSON.stringify(manifest.files)) fail('profile files changed since revision was sealed');
    }
    catch (error) {
      const pinned = options.requireManifest === true || options.revisionId !== undefined
        || pointer?.revisionId === requested;
      if (pinned) throw error;
      if (options.requireManifest) throw error;
      // A legacy profile can be resolved before it has a generated manifest.
      manifest = manifestValue(profileRoot, profileId, requested, pointer?.baseProfileId ?? profileId);
      file = null;
    }
  } else {
    const fallback = pointer?.revisionId ?? 'draft';
    manifest = manifestValue(profileRoot, profileId, fallback, pointer?.baseProfileId ?? profileId);
    file = null;
  }
  const profile = parseProfileYaml(path.join(profileRoot, 'profile.yaml'));
  return Object.freeze({
    ...manifest,
    profileRoot,
    manifestPath: file,
    profileRevision: manifest.revisionId,
    displayName: profile.displayName ?? profileId,
  });
}

/** Resolve any configured profile id; no built-in profile allow-list is used. */
export function resolveAgentProfile(workspaceRoot, profileId, options = {}) {
  return readAgentProfileManifest(workspaceRoot, id(profileId), options);
}

function writeExclusive(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, jsonBytes(value), { flag: 'wx' });
  return digest(fs.readFileSync(file));
}

function writeReplace(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(temporary, jsonBytes(value), { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}

function pointerValue(manifest, manifestRelative) {
  return {
    schemaVersion: 1,
    kind: 'agent-profile-pointer',
    profileId: manifest.profileId,
    baseProfileId: manifest.baseProfileId,
    revisionId: manifest.revisionId,
    manifestPath: manifestRelative.replaceAll('\\', '/'),
    contentDigest: manifest.contentDigest,
    manifestDigest: manifest.manifestDigest,
    updatedAt: new Date().toISOString(),
  };
}

/** Write a new independent revision manifest for an existing profile. */
export function createAgentProfileRevision(workspaceRoot, profileId, options = {}) {
  const { root, profileRoot } = rootFor(workspaceRoot, profileId);
  const revisionId = revision(options.revisionId ?? `draft-${Date.now()}`);
  const baseProfileId = options.baseProfileId ? id(options.baseProfileId, 'base profile id') : profileId;
  const manifest = manifestValue(profileRoot, profileId, revisionId, baseProfileId);
  const file = manifestPath(profileRoot, revisionId);
  writeExclusive(file, manifest);
  const pointer = pointerValue(manifest, path.relative(root, file));
  writeReplace(path.join(profileRoot, POINTER_FILE), pointer);
  return resolveAgentProfile(root, profileId, { revisionId, requireManifest: true });
}

/**
 * Clone every active profile definition into a new directory and seal a new
 * revision. Existing source history is intentionally excluded; it cannot be
 * mistaken for the clone's own revision history.
 */
export function cloneAgentProfile(workspaceRoot, options = {}) {
  const sourceProfileId = id(options.sourceProfileId, 'source profile id');
  const targetProfileId = id(options.targetProfileId, 'target profile id');
  if (sourceProfileId === targetProfileId) fail('clone target must differ from source');
  const { root, profileRoot: sourceRoot } = rootFor(workspaceRoot, sourceProfileId);
  const targetRoot = assertSafeRunPath(root, path.join(root, 'team', 'expert-profiles', targetProfileId));
  if (fs.existsSync(targetRoot)) fail(`target profile already exists: ${targetProfileId}`);
  assertNoLinks(sourceRoot);
  fs.mkdirSync(targetRoot, { recursive: true });
  for (const entry of fs.readdirSync(sourceRoot, { withFileTypes: true })) {
    if (entry.name === GENERATED_DIR || entry.name === POINTER_FILE || entry.name === 'status.json') continue;
    fs.cpSync(path.join(sourceRoot, entry.name), path.join(targetRoot, entry.name), { recursive: entry.isDirectory(), errorOnExist: true });
  }
  const profileFile = path.join(targetRoot, 'profile.yaml');
  if (fs.existsSync(profileFile)) {
    const text = fs.readFileSync(profileFile, 'utf8');
    let rewritten = /^id\s*:/mi.test(text) ? text.replace(/^id\s*:\s*[^#\r\n]+/mi, `id: ${targetProfileId}`) : `id: ${targetProfileId}\n${text}`;
    if (typeof options.displayName === 'string' && options.displayName.trim()) {
      const displayName = options.displayName.trim().replace(/[\r\n]/g, ' ').slice(0, 160);
      rewritten = /^displayName\s*:/mi.test(rewritten)
        ? rewritten.replace(/^displayName\s*:\s*[^#\r\n]+/mi, `displayName: ${displayName}`)
        : `displayName: ${displayName}\n${rewritten}`;
    }
    fs.writeFileSync(profileFile, rewritten, { flag: 'w' });
  }
  const revisionId = revision(options.revisionId ?? 'draft-1');
  const manifest = manifestValue(targetRoot, targetProfileId, revisionId, sourceProfileId);
  const file = manifestPath(targetRoot, revisionId);
  writeExclusive(file, manifest);
  writeExclusive(path.join(targetRoot, POINTER_FILE), pointerValue(manifest, path.relative(root, file)));
  return resolveAgentProfile(root, targetProfileId, { revisionId, requireManifest: true });
}
