import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { sha256Bytes } from './release-integrity.js';
import { assertSafeRunPath } from './run-context.js';

const ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const SHA = /^[a-f0-9]{64}$/;
const MANIFEST = 'framework-release-manifest.json';
const POINTER = 'active-framework-release.json';
const MAX_FILES = 10_000;
const MAX_BYTES = 256 * 1024 * 1024;
export const FRAMEWORK_RUNTIME_FILES = Object.freeze([
  'plugins/dsh-ptc-control-plane/client/panel.js',
  'plugins/dsh-ptc-control-plane/client/state.js',
  'plugins/dsh-ptc-control-plane/lib/client.js',
  'plugins/dsh-ptc-control-plane/lib/control-state.js',
  'plugins/dsh-ptc-control-plane/lib/framework-release.js',
  'plugins/dsh-ptc-control-plane/lib/framework-published-run.js',
  'plugins/dsh-ptc-control-plane/lib/framework-rehearsal.js',
  'plugins/dsh-ptc-control-plane/lib/framework-rehearsal-manager.js',
  'plugins/dsh-ptc-control-plane/lib/framework-rehearsal-source.js',
  'plugins/dsh-ptc-control-plane/lib/host-command.js',
  'plugins/dsh-ptc-control-plane/lib/index.js',
  'plugins/dsh-ptc-control-plane/lib/pipeline-dispatch.js',
  'plugins/dsh-ptc-control-plane/lib/pipeline-execution.js',
  'plugins/dsh-ptc-control-plane/lib/pipeline-guard.js',
  'plugins/dsh-ptc-control-plane/lib/pipeline-materials.js',
  'plugins/dsh-ptc-control-plane/lib/release-integrity.js',
  'plugins/dsh-ptc-control-plane/lib/run-context.js',
  'plugins/dsh-ptc-control-plane/lib/training-paths.js',
  'plugins/dsh-ptc-control-plane/lib/training-pipeline.js',
  'plugins/dsh-ptc-control-plane/lib/training-compile.js',
  'plugins/dsh-ptc-control-plane/lib/training-dispatch.js',
  'plugins/dsh-ptc-control-plane/lib/training-execution.js',
  'plugins/dsh-ptc-control-plane/lib/training-materials.js',
  'plugins/dsh-ptc-control-plane/lib/training-model.js',
  'scripts/dft_source.py',
  'scripts/material_plaintext_hash.py',
  'scripts/ptc_contract_schema.py',
  'scripts/ptc_trim_validation.py',
  'scripts/validate_dft_outputs.py',
  'scripts/validate_schematic_outputs.py',
].sort());
// Schema v1 releases made before the real-pipeline runtime was added retain
// their original coverage. They remain readable, but cannot execute when the
// current runtime file set differs (verifyFrameworkRuntimeCompatibility).
const LEGACY_FRAMEWORK_RUNTIME_FILES = Object.freeze([
  'plugins/dsh-ptc-control-plane/client/panel.js',
  'plugins/dsh-ptc-control-plane/client/state.js',
  'plugins/dsh-ptc-control-plane/lib/client.js',
  'plugins/dsh-ptc-control-plane/lib/control-state.js',
  'plugins/dsh-ptc-control-plane/lib/framework-published-run.js',
  'plugins/dsh-ptc-control-plane/lib/framework-rehearsal-manager.js',
  'plugins/dsh-ptc-control-plane/lib/framework-rehearsal-source.js',
  'plugins/dsh-ptc-control-plane/lib/framework-rehearsal.js',
  'plugins/dsh-ptc-control-plane/lib/framework-release.js',
  'plugins/dsh-ptc-control-plane/lib/host-command.js',
  'plugins/dsh-ptc-control-plane/lib/index.js',
  'plugins/dsh-ptc-control-plane/lib/release-integrity.js',
  'plugins/dsh-ptc-control-plane/lib/run-context.js',
  'plugins/dsh-ptc-control-plane/lib/training-paths.js',
  'plugins/dsh-ptc-control-plane/lib/training-pipeline.js',
  'scripts/dft_source.py',
  'scripts/material_plaintext_hash.py',
  'scripts/ptc_contract_schema.py',
  'scripts/ptc_trim_validation.py',
  'scripts/validate_dft_outputs.py',
  'scripts/validate_schematic_outputs.py',
].sort());

function fail(message) { throw new Error(`framework release: ${message}`); }
function exactKeys(value, keys) {
  return value && typeof value === 'object' && !Array.isArray(value)
    && Object.keys(value).sort().join('|') === [...keys].sort().join('|');
}
function identity(value, label) {
  if (typeof value !== 'string' || !ID.test(value) || /[. ]$/.test(value)
      || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)/i.test(value)
      || value === POINTER || value.startsWith('stage-')) fail(`invalid ${label}`);
  return value;
}
function safe(root, ...parts) { return assertSafeRunPath(root, path.join(root, ...parts)); }
function releaseRoot(workspaceRoot) { return safe(path.resolve(workspaceRoot), 'team', 'ptc', 'framework-releases'); }
function readJson(file) {
  const stat = fs.lstatSync(file);
  if (!stat.isFile() || stat.nlink > 1) fail(`not a private regular file: ${file}`);
  return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
}
function writeNew(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
}
function withLock(root, action) {
  fs.mkdirSync(root, { recursive: true });
  const lock = safe(root, '.publisher-lock');
  try { fs.mkdirSync(lock); }
  catch (error) {
    if (error.code === 'EEXIST') fail('another framework publisher holds the lock');
    throw error;
  }
  try { return action(); }
  finally { fs.rmdirSync(lock); }
}
function walk(root, relative = '') {
  const directory = relative ? safe(root, relative) : safe(root);
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name, 'en'))) {
    if (!entry.name || entry.name === '.' || entry.name === '..' || entry.name.includes('\\')
        || /[<>:"|?*]/.test(entry.name) || /[. ]$/.test(entry.name)) fail('unsafe snapshot entry');
    const name = relative ? `${relative}/${entry.name}` : entry.name;
    const absolute = safe(root, ...name.split('/'));
    const stat = fs.lstatSync(absolute);
    if (stat.isSymbolicLink() || (stat.isFile() && stat.nlink > 1)) fail(`linked snapshot entry: ${name}`);
    if (stat.isDirectory()) files.push(...walk(root, name));
    else if (stat.isFile()) files.push(name);
    else fail(`unsupported snapshot entry: ${name}`);
    if (files.length > MAX_FILES) fail('too many snapshot files');
  }
  return files;
}
function entries(root, prefix = '') {
  let total = 0;
  const result = walk(root).map(name => {
    const bytes = fs.readFileSync(safe(root, ...name.split('/')));
    total += bytes.length;
    if (total > MAX_BYTES) fail('snapshot exceeds size limit');
    return { path: `${prefix}${name}`, size: bytes.length, sha256: sha256Bytes(bytes) };
  });
  return result.sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
}
function runtimeEntries(workspaceRoot) {
  const workspace = path.resolve(workspaceRoot);
  return FRAMEWORK_RUNTIME_FILES.map(name => {
    const file = safe(workspace, ...name.split('/'));
    const stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.nlink > 1) fail(`runtime implementation is not a private file: ${name}`);
    const bytes = fs.readFileSync(file);
    return { path: `runtime/${name}`, size: bytes.length, sha256: sha256Bytes(bytes) };
  });
}
function digest(files) {
  return sha256Bytes(Buffer.from(files.map(file => `${file.path}\0${file.size}\0${file.sha256}\n`).join(''), 'utf8'));
}
function equal(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
function sourceIdentity(runDirectory, runId) {
  if (fs.existsSync(safe(runDirectory, 'framework-rehearsal.lock'))) fail('source rehearsal has not finished cleanup');
  const context = readJson(safe(runDirectory, 'run.json'));
  const state = readJson(safe(runDirectory, 'state.json'));
  const progress = readJson(safe(runDirectory, 'pipeline-progress.json'));
  const registry = readJson(safe(runDirectory, 'pipeline-registry.json'));
  const expectedStages = registry.stateMachine?.filter(stage => stage !== 'COMPLETE');
  if (context.schemaVersion !== 1 || context.runId !== runId || context.mode !== 'training'
      || context.releaseId !== null || context.projectId !== null
      || state.runId !== runId || state.purpose !== 'framework-rehearsal'
      || state.status !== 'completed' || state.target?.kind !== 'pipeline'
      || state.target.fromStage !== 'INPUT_SYNC' || state.target.toStage !== 'COMPILE'
      || state.outcome?.mode !== 'FRAMEWORK_REHEARSAL'
      || state.outcome?.realBusinessGatesPassed !== false
      || progress.runId !== runId || progress.status !== 'completed'
      || !Array.isArray(expectedStages) || expectedStages.length === 0
      || expectedStages[0] !== 'INPUT_SYNC' || expectedStages.at(-1) !== 'COMPILE'
      || !equal(state.target.stages, expectedStages)
      || !equal(progress.stages?.map(stage => stage.stage), expectedStages)
      || progress.stages.some(stage => stage.status !== 'completed' || stage.gateResult?.status !== 'passed'
        || stage.gateResult.exitCode !== 0 || stage.gateResult.gate !== registry.stages?.[stage.stage]?.gate)) {
    fail('source is not a completed full-chain framework rehearsal');
  }
  return { context, state, progress, expectedStages };
}
function readPointer(root) {
  const file = safe(root, POINTER);
  if (!fs.existsSync(file)) return null;
  const pointer = readJson(file);
  if (!exactKeys(pointer, ['schemaVersion', 'kind', 'releaseId', 'bundleDigest', 'previousReleaseId', 'activatedAt'])
      || pointer.schemaVersion !== 1 || pointer.kind !== 'framework-rehearsal'
      || !SHA.test(pointer.bundleDigest) || typeof pointer.activatedAt !== 'string') fail('invalid active framework pointer');
  identity(pointer.releaseId, 'active releaseId');
  if (pointer.previousReleaseId !== null) identity(pointer.previousReleaseId, 'previous releaseId');
  return pointer;
}
function validateManifest(manifest) {
  if (!exactKeys(manifest, ['schemaVersion', 'kind', 'realBusinessGatesPassed', 'releaseId', 'sourceRunId',
    'sourceRunDigest', 'runtimeDigest', 'createdAt', 'createdBy', 'previousReleaseId', 'files', 'bundleDigest', 'verification'])
      || manifest.schemaVersion !== 1 || manifest.kind !== 'framework-rehearsal'
      || manifest.realBusinessGatesPassed !== false || manifest.verification?.kind !== 'framework-rehearsal'
      || manifest.verification?.status !== 'passed' || manifest.verification?.runId !== manifest.sourceRunId
      || !exactKeys(manifest.verification, ['kind', 'status', 'runId'])
      || !SHA.test(manifest.sourceRunDigest) || !SHA.test(manifest.runtimeDigest) || !SHA.test(manifest.bundleDigest)
      || !Array.isArray(manifest.files) || manifest.files.length < 4) fail('invalid framework manifest');
  identity(manifest.releaseId, 'releaseId');
  identity(manifest.sourceRunId, 'sourceRunId');
  if (manifest.previousReleaseId !== null) identity(manifest.previousReleaseId, 'previousReleaseId');
  if (typeof manifest.createdBy !== 'string' || !manifest.createdBy.trim()
      || !Number.isFinite(Date.parse(manifest.createdAt))) fail('invalid publisher metadata');
  let previous = '';
  for (const file of manifest.files) {
    if (!exactKeys(file, ['path', 'size', 'sha256']) || typeof file.path !== 'string'
        || !(file.path.startsWith('snapshot/') || file.path.startsWith('runtime/'))
        || file.path <= previous || file.path.split('/').some(part => !part || part === '.' || part === '..')
        || !Number.isSafeInteger(file.size) || file.size < 0 || !SHA.test(file.sha256)) fail('invalid framework file manifest');
    previous = file.path;
  }
  const required = ['snapshot/run.json', 'snapshot/state.json', 'snapshot/pipeline-progress.json', 'snapshot/pipeline-registry.json'];
  const runtime = manifest.files.filter(file => file.path.startsWith('runtime/'));
  const runtimePaths = runtime.map(file => file.path);
  const supportedRuntimeSet = [LEGACY_FRAMEWORK_RUNTIME_FILES, FRAMEWORK_RUNTIME_FILES]
    .some(names => equal(runtimePaths, names.map(name => `runtime/${name}`)));
  if (required.some(name => !manifest.files.some(file => file.path === name))
      || !supportedRuntimeSet
      || manifest.runtimeDigest !== digest(runtime)
      || manifest.bundleDigest !== digest(manifest.files)) fail('framework snapshot coverage or digest mismatch');
  return manifest;
}
function verifiedDirectory(directory) {
  const top = fs.readdirSync(directory).sort();
  if (!equal(top, [MANIFEST, 'snapshot', 'runtime'].sort())) fail('framework release has unlisted top-level entries');
  const manifest = validateManifest(readJson(safe(directory, MANIFEST)));
  if (path.basename(directory) !== manifest.releaseId && !path.basename(directory).startsWith('stage-')) fail('release identity mismatch');
  const snapshot = safe(directory, 'snapshot');
  const runtimeRoot = safe(directory, 'runtime');
  const actual = [...entries(runtimeRoot, 'runtime/'), ...entries(snapshot, 'snapshot/')]
    .sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  if (!equal(actual, manifest.files)) fail('framework snapshot file list or sha256 mismatch');
  sourceIdentity(snapshot, manifest.sourceRunId);
  if (digest(actual.filter(file => file.path.startsWith('snapshot/'))
    .map(file => ({ ...file, path: file.path.slice('snapshot/'.length) }))) !== manifest.sourceRunDigest) {
    fail('framework source digest mismatch');
  }
  return { directory, snapshotRoot: snapshot, runtimeRoot, manifest };
}
function verifiedActive(root) {
  const pointer = readPointer(root);
  if (!pointer) return null;
  const release = verifiedDirectory(safe(root, pointer.releaseId));
  if (release.manifest.bundleDigest !== pointer.bundleDigest) fail('active framework pointer digest mismatch');
  return { pointer, release };
}

/** Freeze an independently verified rehearsal. Never touches a real business release. */
export async function stageFrameworkRelease({ workspaceRoot, releaseId, sourceRunId, createdBy, verifyRehearsal }) {
  const workspace = path.resolve(workspaceRoot);
  identity(releaseId, 'releaseId');
  identity(sourceRunId, 'sourceRunId');
  if (typeof verifyRehearsal !== 'function') fail('trusted full-chain rehearsal verifier is required');
  const runDirectory = safe(workspace, 'Training_Materials', 'runs', sourceRunId);
  const context = sourceIdentity(runDirectory, sourceRunId).context;
  if (path.resolve(workspace, context.artifactRoot) !== runDirectory) fail('source run directory binding mismatch');
  const before = entries(runDirectory);
  const sourceRunDigest = digest(before);
  const runtimeBefore = runtimeEntries(workspace);
  const verdict = await verifyRehearsal({ workspaceRoot: workspace, runId: sourceRunId, runDirectory, sourceRunDigest });
  if (verdict?.kind !== 'framework-rehearsal' || verdict?.status !== 'passed'
      || verdict?.runId !== sourceRunId || verdict?.realBusinessGatesPassed === true) {
    fail('trusted full-chain rehearsal verification did not pass');
  }
  if (!equal(entries(runDirectory), before)) fail('source changed during verification');
  if (!equal(runtimeEntries(workspace), runtimeBefore)) fail('runtime implementation changed during verification');
  const root = releaseRoot(workspace);
  return withLock(root, () => {
    const active = verifiedActive(root);
    if (fs.existsSync(safe(root, releaseId))) fail('release identity already exists');
    if (!equal(entries(runDirectory), before)) fail('source changed before snapshot');
    if (!equal(runtimeEntries(workspace), runtimeBefore)) fail('runtime implementation changed before snapshot');
    const stagingId = `stage-${randomUUID()}`;
    const stagingRoot = safe(root, '.staging');
    fs.mkdirSync(stagingRoot, { recursive: true });
    const directory = safe(stagingRoot, stagingId);
    fs.mkdirSync(directory);
    try {
      const snapshot = safe(directory, 'snapshot');
      fs.mkdirSync(snapshot);
      const runtimeRoot = safe(directory, 'runtime');
      fs.mkdirSync(runtimeRoot);
      for (const file of before) {
        const destination = safe(snapshot, ...file.path.split('/'));
        fs.mkdirSync(path.dirname(destination), { recursive: true });
        fs.copyFileSync(safe(runDirectory, ...file.path.split('/')), destination, fs.constants.COPYFILE_EXCL);
      }
      for (const file of runtimeBefore) {
        const name = file.path.slice('runtime/'.length);
        const destination = safe(runtimeRoot, ...name.split('/'));
        fs.mkdirSync(path.dirname(destination), { recursive: true });
        fs.copyFileSync(safe(workspace, ...name.split('/')), destination, fs.constants.COPYFILE_EXCL);
      }
      if (!equal(entries(runDirectory), before)) fail('source changed during snapshot');
      if (!equal(runtimeEntries(workspace), runtimeBefore)) fail('runtime implementation changed during snapshot');
      const files = [...entries(snapshot, 'snapshot/'), ...entries(runtimeRoot, 'runtime/')]
        .sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
      const expected = [...before.map(file => ({ ...file, path: `snapshot/${file.path}` })), ...runtimeBefore]
        .sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
      if (!equal(files, expected)) fail('copied bytes differ from source or runtime');
      const manifest = {
        schemaVersion: 1, kind: 'framework-rehearsal', realBusinessGatesPassed: false,
        releaseId, sourceRunId, sourceRunDigest, runtimeDigest: digest(runtimeBefore),
        createdAt: new Date().toISOString(), createdBy,
        previousReleaseId: active?.pointer.releaseId ?? null, files, bundleDigest: digest(files),
        verification: { kind: 'framework-rehearsal', status: 'passed', runId: sourceRunId },
      };
      validateManifest(manifest);
      writeNew(safe(directory, MANIFEST), manifest);
      verifiedDirectory(directory);
      return { stagingId, manifest };
    } catch (error) {
      fs.rmSync(directory, { recursive: true });
      throw error;
    }
  });
}

/** Activate only after rechecking frozen bytes and the still-current predecessor. */
export function activateStagedFrameworkRelease({ workspaceRoot, stagingId }) {
  if (typeof stagingId !== 'string' || !/^stage-[a-f0-9-]{36}$/.test(stagingId)) fail('invalid staging identity');
  const root = releaseRoot(workspaceRoot);
  return withLock(root, () => {
    const staged = verifiedDirectory(safe(root, '.staging', stagingId));
    const active = verifiedActive(root);
    if ((active?.pointer.releaseId ?? null) !== staged.manifest.previousReleaseId) fail('active framework release changed since staging');
    const destination = safe(root, staged.manifest.releaseId);
    if (fs.existsSync(destination)) fail('release identity already exists');
    fs.renameSync(staged.directory, destination);
    const release = verifiedDirectory(destination);
    const pointer = { schemaVersion: 1, kind: 'framework-rehearsal', releaseId: release.manifest.releaseId,
      bundleDigest: release.manifest.bundleDigest, previousReleaseId: active?.pointer.releaseId ?? null,
      activatedAt: new Date().toISOString() };
    const temporary = safe(root, `.pointer-${randomUUID()}.tmp`);
    try {
      writeNew(temporary, pointer);
      const fd = fs.openSync(temporary, 'r+');
      try { fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
      fs.renameSync(temporary, safe(root, POINTER));
    } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
    return pointer;
  });
}

/** Refuse tampered snapshots before a published-mode runner can use them. */
export function loadFrameworkRelease({ workspaceRoot, releaseId }) {
  const root = releaseRoot(workspaceRoot);
  const wanted = releaseId === undefined ? readPointer(root)?.releaseId : identity(releaseId, 'releaseId');
  if (!wanted) fail('no active framework release');
  const release = verifiedDirectory(safe(root, wanted));
  if (releaseId === undefined) {
    const pointer = readPointer(root);
    if (pointer.bundleDigest !== release.manifest.bundleDigest) fail('active framework pointer digest mismatch');
  }
  return release;
}

/** Call immediately before dispatch; a changed host implementation cannot run a frozen version. */
export function verifyFrameworkRuntimeCompatibility({ workspaceRoot, releaseId }) {
  const release = loadFrameworkRelease({ workspaceRoot, releaseId });
  const expected = release.manifest.files.filter(file => file.path.startsWith('runtime/'));
  const actual = runtimeEntries(workspaceRoot);
  if (!equal(actual, expected)) {
    const mismatch = expected.find((file, index) => !equal(file, actual[index]));
    fail(`current runtime implementation differs from frozen version: ${mismatch?.path ?? 'file list'}`);
  }
  return { compatible: true, releaseId: release.manifest.releaseId, runtimeDigest: release.manifest.runtimeDigest };
}

export function listFrameworkReleases({ workspaceRoot }) {
  const root = releaseRoot(workspaceRoot);
  if (!fs.existsSync(root)) return { active: null, releases: [] };
  const active = readPointer(root);
  const releases = fs.readdirSync(root, { withFileTypes: true })
    .filter(entry => entry.isDirectory() && !entry.name.startsWith('.'))
    .map(entry => {
      try { return { releaseId: entry.name, valid: true, manifest: verifiedDirectory(safe(root, entry.name)).manifest }; }
      catch (error) { return { releaseId: entry.name, valid: false, error: error.message }; }
    });
  if (active) loadFrameworkRelease({ workspaceRoot });
  return { active, releases };
}
