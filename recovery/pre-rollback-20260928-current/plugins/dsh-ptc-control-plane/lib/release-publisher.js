import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { buildReleaseFileEntries, digestReleaseEntries, sha256Bytes, verifyReleaseDirectory } from './release-integrity.js';

const CATEGORIES = ['profiles', 'orchestration', 'contracts', 'policies', 'verification'];
const ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const SHA256 = /^[a-f0-9]{64}$/;
const SOURCES = {
  profiles: ['team/expert-profiles/'],
  orchestration: ['team/ptc/', 'scripts/'],
  contracts: ['team/ptc/', 'team/expert-profiles/'],
  policies: ['plugins/', 'scripts/', 'team/ptc/'],
  verification: ['Training_Materials/runs/', 'team/ptc/native-control-plane/verification/'],
};

function fail(message) { throw new Error(`release publisher: ${message}`); }
function id(value) {
  if (typeof value !== 'string' || !ID.test(value) || /[. ]$/.test(value)
    || value.toLowerCase() === 'active-release.json'
    || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)/i.test(value)) fail('invalid identity');
  return value;
}
function relative(value) {
  if (typeof value !== 'string' || value === '' || value.includes('\\') || value.includes(':')
    || value.startsWith('/') || value.split('/').some((part) => !part || part === '.' || part === '..'
      || /[. ]$/.test(part) || /[\x00-\x1f<>"|?*]/.test(part)
      || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)/i.test(part))) fail(`unsafe path: ${value}`);
  return value;
}

// Reject links at every existing component, including ancestors of the workspace.
// The host must also deny concurrent untrusted writes to these directories.
function safePath(root, name = '') {
  const target = name ? path.join(root, relative(name)) : path.resolve(root);
  const parsed = path.parse(target);
  let current = parsed.root;
  for (const part of target.slice(parsed.root.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    try {
      if (fs.lstatSync(current).isSymbolicLink()) fail(`symbolic link is forbidden: ${current}`);
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
  return target;
}
function rootOf(workspaceRoot) { return safePath(path.resolve(workspaceRoot), 'team/ptc/releases'); }
function readJson(file) {
  if (!fs.lstatSync(file).isFile() || fs.statSync(file).nlink > 1) fail(`not a private regular file: ${file}`);
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}
function writeJson(file, data) { fs.writeFileSync(file, `${JSON.stringify(data, null, 2)}\n`, { flag: 'wx' }); }
function readPointer(root) {
  const file = safePath(root, 'active-release.json');
  if (!fs.existsSync(file)) return null;
  const pointer = readJson(file);
  id(pointer.releaseId);
  if (!SHA256.test(pointer.bundleDigest)) fail('invalid active pointer digest');
  return pointer;
}
function withLock(root, work) {
  fs.mkdirSync(root, { recursive: true });
  const lock = safePath(root, '.publisher-lock');
  try { fs.mkdirSync(lock); } catch (error) {
    if (error.code === 'EEXIST') fail('another publisher holds the lock; inspect a stale lock before recovery');
    throw error;
  }
  try { return work(); } finally { fs.rmdirSync(lock); }
}

function sourceEntries(workspaceRoot, sources, includeVerification) {
  const root = safePath(path.resolve(workspaceRoot));
  const entries = [];
  const targets = new Set();
  for (const category of CATEGORIES.filter((item) => includeVerification || item !== 'verification')) {
    if (!Array.isArray(sources?.[category]) || sources[category].length === 0) fail(`missing ${category} sources`);
    for (const mapping of sources[category]) {
      const source = relative(mapping.sourcePath);
      const target = relative(mapping.targetPath);
      const normalizedSource = source.toLowerCase();
      if (!SOURCES[category].some((prefix) => normalizedSource.startsWith(prefix.toLowerCase()))
        || normalizedSource.startsWith('team/ptc/releases/') || normalizedSource.split('/').includes('versions')) fail(`source not allowed: ${source}`);
      if (!target.startsWith(`${category}/`)) fail(`wrong snapshot category: ${target}`);
      const folded = target.toLowerCase();
      if (targets.has(folded)) fail(`duplicate target: ${target}`);
      targets.add(folded);
      const absolute = safePath(root, source);
      const stat = fs.lstatSync(absolute);
      if (!stat.isFile() || stat.nlink > 1) fail(`source must be a private regular file: ${source}`);
      const bytes = fs.readFileSync(absolute);
      entries.push({ path: target, size: bytes.length, sha256: sha256Bytes(bytes), bytes });
    }
  }
  return entries.sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
}

/** Exact-byte candidate digest excludes verification to avoid an evidence/hash cycle. */
export function buildCandidateEntries({ workspaceRoot, sources }) {
  return sourceEntries(workspaceRoot, sources, false).map(({ bytes, ...entry }) => entry);
}
export function computeCandidateDigest(options) { return digestReleaseEntries(buildCandidateEntries(options)); }

/** Enforces the frozen manifest v1 shape and semantic coverage; no schema dependency at runtime. */
export function validateReleaseManifest(manifest) {
  const exactKeys = (value, keys) => value && typeof value === 'object' && !Array.isArray(value)
    && Object.keys(value).sort().join('|') === [...keys].sort().join('|');
  if (!exactKeys(manifest, ['schemaVersion', 'releaseId', 'createdAt', 'createdBy', 'previousReleaseId',
    'snapshots', 'files', 'bundleDigest', 'releaseVerification']) || manifest.schemaVersion !== 1) fail('invalid manifest v1 shape');
  id(manifest.releaseId);
  if (manifest.previousReleaseId !== null) id(manifest.previousReleaseId);
  if (manifest.previousReleaseId === manifest.releaseId) fail('release cannot precede itself');
  if (typeof manifest.createdBy !== 'string' || !manifest.createdBy.trim()
    || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/i.test(manifest.createdAt)
    || !Number.isFinite(Date.parse(manifest.createdAt))) fail('invalid publisher metadata');
  if (!exactKeys(manifest.snapshots, CATEGORIES) || !Array.isArray(manifest.files) || !manifest.files.length) fail('invalid snapshots');
  const declared = [];
  for (const category of CATEGORIES) {
    const names = manifest.snapshots[category];
    if (!Array.isArray(names) || !names.length) fail(`empty snapshot category: ${category}`);
    for (const name of names) {
      relative(name);
      if (!name.startsWith(`${category}/`)) fail('snapshot category mismatch');
      declared.push(name);
    }
  }
  let previous = '';
  for (const entry of manifest.files) {
    if (!exactKeys(entry, ['path', 'size', 'sha256'])) fail('invalid file entry');
    relative(entry.path);
    if (entry.path <= previous || !Number.isSafeInteger(entry.size) || entry.size < 0 || !SHA256.test(entry.sha256)) fail('invalid file ordering, size or digest');
    previous = entry.path;
  }
  if (new Set(declared.map((item) => item.toLowerCase())).size !== declared.length
    || JSON.stringify(declared.sort()) !== JSON.stringify(manifest.files.map((entry) => entry.path))) fail('snapshot coverage mismatch');
  if (manifest.bundleDigest !== digestReleaseEntries(manifest.files)) fail('bundle digest mismatch');
  if (!exactKeys(manifest.releaseVerification, ['result', 'singleAgentEvaluation', 'pipelineRegression'])
    || Object.values(manifest.releaseVerification).some((result) => result !== 'passed')) fail('verification not passed');
  return true;
}

/**
 * Reports are supplied by the trusted evaluator, never synthesized by this service.
 * Required files: verification/{single-agent-evaluation,pipeline-regression}.json.
 * Each: {kind,result:'passed',candidateDigest,checks:[{id,result:'passed',exitCode:0,
 * command,evidencePath,sha256,profileId? or stage?}]}. Each evidencePath names a
 * bundled verification JSON command result with the same command, candidateDigest
 * and exitCode:0.
 * Single-agent checks cover every profiles/<profileId>/ identity. Pipeline checks
 * follow every executable stage of orchestration/ptc_stage_registry.json in order,
 * with gate equal to the registry's gate and command containing that gate.
 * This checks result provenance/binding, not whether an external runner lied.
 */
function verifyEvidence(directory, manifest) {
  const candidateDigest = digestReleaseEntries(manifest.files.filter((entry) => !entry.path.startsWith('verification/')));
  const profiles = [...new Set(manifest.snapshots.profiles.map((file) => {
    const parts = file.split('/');
    if (parts.length < 3) fail('profiles must use profiles/<profileId>/<file>');
    return id(parts[1]);
  }))].sort();
  const registryPath = 'orchestration/ptc_stage_registry.json';
  if (!manifest.snapshots.orchestration.includes(registryPath)) fail('stage registry snapshot missing');
  const registry = readJson(safePath(directory, registryPath));
  const stages = registry.stateMachine?.filter((stage) => stage !== 'COMPLETE');
  if (!Array.isArray(stages) || !stages.length || new Set(stages).size !== stages.length
    || stages.some((stage) => typeof registry.stages?.[stage]?.gate !== 'string' || !registry.stages[stage].gate)) fail('invalid stage registry');
  for (const kind of ['single-agent-evaluation', 'pipeline-regression']) {
    const name = `verification/${kind}.json`;
    if (!manifest.snapshots.verification.includes(name)) fail(`${kind} evidence missing`);
    const report = readJson(safePath(directory, name));
    if (report.kind !== kind || report.result !== 'passed' || report.candidateDigest !== candidateDigest
      || !Array.isArray(report.checks) || !report.checks.length) fail(`${kind} evidence failed or stale`);
    const checkIds = new Set();
    for (const check of report.checks) {
      if (typeof check.id !== 'string' || !check.id || checkIds.has(check.id) || check.result !== 'passed'
        || check.exitCode !== 0 || typeof check.command !== 'string' || !check.command.trim()) fail(`${kind} has a failed or invalid check`);
      checkIds.add(check.id);
      const evidencePath = relative(check.evidencePath);
      const file = manifest.files.find((entry) => entry.path === evidencePath);
      if (!evidencePath.startsWith('verification/') || evidencePath === name || !file || file.sha256 !== check.sha256) fail('command evidence binding missing or stale');
      const evidence = readJson(safePath(directory, evidencePath));
      if (evidence.command !== check.command || evidence.exitCode !== 0
        || evidence.candidateDigest !== candidateDigest) fail('command evidence does not prove success for this candidate');
    }
    if (kind === 'single-agent-evaluation') {
      const covered = [...new Set(report.checks.map((check) => check.profileId))].sort();
      if (JSON.stringify(covered) !== JSON.stringify(profiles)) fail('single-agent evidence does not cover every profile');
    } else {
      if (JSON.stringify(report.checks.map((check) => check.stage)) !== JSON.stringify(stages)) fail('pipeline evidence does not cover ordered stages');
      for (const check of report.checks) {
        const gate = registry.stages[check.stage].gate;
        if (check.gate !== gate || !check.command.includes(gate)) fail(`pipeline gate mismatch: ${check.stage}`);
      }
    }
  }
  return candidateDigest;
}

function verified(root, releaseId) {
  const directory = safePath(root, id(releaseId));
  const manifest = readJson(safePath(directory, 'release-manifest.json'));
  validateReleaseManifest(manifest);
  if (manifest.releaseId !== releaseId) fail('release identity mismatch');
  const result = verifyReleaseDirectory(directory, manifest);
  if (!result.ok) fail(result.errors.join('; '));
  verifyEvidence(directory, manifest);
  return { directory, manifest };
}

/** Copy only the explicit source list. No real release/pointer changes until activation. */
export function stageRelease({ workspaceRoot, releaseId, createdBy, sources }) {
  id(releaseId);
  const entries = sourceEntries(workspaceRoot, sources, true);
  const root = rootOf(workspaceRoot);
  return withLock(root, () => {
    if (fs.existsSync(safePath(root, releaseId))) fail('release identity already exists');
    const pointer = readPointer(root);
    if (pointer) {
      const current = verified(root, pointer.releaseId);
      if (current.manifest.bundleDigest !== pointer.bundleDigest) fail('active pointer digest mismatch');
    }
    const stagingId = `stage-${randomUUID()}`;
    const stagingRoot = safePath(root, '.staging');
    fs.mkdirSync(stagingRoot, { recursive: true });
    const directory = safePath(stagingRoot, stagingId);
    fs.mkdirSync(directory);
    try {
      for (const entry of entries) {
        const destination = safePath(directory, entry.path);
        fs.mkdirSync(path.dirname(destination), { recursive: true });
        fs.writeFileSync(destination, entry.bytes, { flag: 'wx' });
      }
      const files = buildReleaseFileEntries(directory);
      const manifest = {
        schemaVersion: 1, releaseId, createdAt: new Date().toISOString(), createdBy,
        previousReleaseId: pointer?.releaseId ?? null,
        snapshots: Object.fromEntries(CATEGORIES.map((category) => [category, files.filter((entry) => entry.path.startsWith(`${category}/`)).map((entry) => entry.path)])),
        files, bundleDigest: digestReleaseEntries(files),
        releaseVerification: { result: 'passed', singleAgentEvaluation: 'passed', pipelineRegression: 'passed' },
      };
      validateReleaseManifest(manifest);
      const candidateDigest = verifyEvidence(directory, manifest);
      writeJson(path.join(directory, 'release-manifest.json'), manifest);
      if (!verifyReleaseDirectory(directory, manifest).ok) fail('staging integrity failed');
      return { stagingId, manifest, candidateDigest };
    } catch (error) {
      // Only this fresh, validated UUID directory belongs to this attempt.
      fs.rmSync(directory, { recursive: true });
      throw error;
    }
  });
}

function switchPointer(root, release, previousReleaseId) {
  const pointer = { schemaVersion: 1, releaseId: release.manifest.releaseId,
    bundleDigest: release.manifest.bundleDigest, previousReleaseId, activatedAt: new Date().toISOString() };
  const temporary = safePath(root, `.pointer-${randomUUID()}.tmp`);
  try {
    writeJson(temporary, pointer);
    const fd = fs.openSync(temporary, 'r+');
    try { fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
    fs.renameSync(temporary, safePath(root, 'active-release.json'));
  } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
  return pointer;
}

/** Revalidate everything, reserve a never-reused identity, then atomically replace the pointer. */
export function activateStagedRelease({ workspaceRoot, stagingId }) {
  if (!/^stage-[a-f0-9-]{36}$/.test(stagingId)) fail('invalid staging identity');
  const root = rootOf(workspaceRoot);
  return withLock(root, () => {
    const directory = safePath(root, `.staging/${stagingId}`);
    const manifest = readJson(safePath(directory, 'release-manifest.json'));
    validateReleaseManifest(manifest);
    const integrity = verifyReleaseDirectory(directory, manifest);
    if (!integrity.ok) fail(integrity.errors.join('; '));
    verifyEvidence(directory, manifest);
    const pointer = readPointer(root);
    if ((pointer?.releaseId ?? null) !== manifest.previousReleaseId) fail('active release changed since staging; restage');
    if (pointer && verified(root, pointer.releaseId).manifest.bundleDigest !== pointer.bundleDigest) fail('active pointer digest mismatch');
    const destination = safePath(root, manifest.releaseId);
    if (fs.existsSync(destination)) fail('release identity already exists');
    fs.renameSync(directory, destination);
    // A pointer-write failure can leave a complete inactive release, never a half-active release.
    return switchPointer(root, verified(root, manifest.releaseId), pointer?.releaseId ?? null);
  });
}

export function listReleases({ workspaceRoot }) {
  const root = rootOf(workspaceRoot);
  if (!fs.existsSync(root)) return { active: null, releases: [] };
  const active = readPointer(root);
  const releases = fs.readdirSync(root, { withFileTypes: true }).filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
    .map((entry) => {
      try { return { releaseId: entry.name, valid: true, manifest: verified(root, entry.name).manifest }; }
      catch (error) { return { releaseId: entry.name, valid: false, error: error.message }; }
    });
  return { active, releases };
}

export function rollbackRelease({ workspaceRoot, releaseId }) {
  const root = rootOf(workspaceRoot);
  return withLock(root, () => {
    const pointer = readPointer(root);
    if (!pointer) fail('no active release to roll back');
    const targetId = releaseId ?? pointer.previousReleaseId;
    if (!targetId || targetId === pointer.releaseId) fail('no different rollback target');
    return switchPointer(root, verified(root, targetId), pointer.releaseId);
  });
}
