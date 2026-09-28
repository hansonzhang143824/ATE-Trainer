import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';

const SHA = /^[a-f0-9]{64}$/;
const TM = /^TM\d+$/;
const SOURCE_NAMES = {
  schematic: ['SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
    'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json'],
  dft: ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'],
};
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const bytesOf = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);

function fail(message) { throw new Error(`framework rehearsal: ${message}`); }
function safe(root, ...parts) { return assertSafeRunPath(root, path.join(root, ...parts)); }
function read(file) { return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '')); }
function writeNew(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, bytesOf(value), { flag: 'wx' });
}
function items(value) {
  if (!Array.isArray(value) || !value.length || value.some(tm => typeof tm !== 'string' || !TM.test(tm))
      || new Set(value).size !== value.length) fail('unique explicit TM identifiers required');
  return [...value].sort((a, b) => Number(a.slice(2)) - Number(b.slice(2)));
}
function registryOf(root) {
  const file = safe(root, 'team', 'ptc', 'ptc_stage_registry.json');
  const bytes = fs.readFileSync(file);
  const registry = JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, ''));
  const stages = registry.stateMachine?.filter(stage => stage !== 'COMPLETE');
  if (!Array.isArray(stages) || stages.length !== 7 || stages[0] !== 'INPUT_SYNC'
      || stages.at(-1) !== 'COMPILE' || new Set(stages).size !== 7
      || stages.some(stage => typeof registry.stages?.[stage]?.owner !== 'string'
        || typeof registry.stages?.[stage]?.gate !== 'string')) fail('authoritative seven-stage registry is invalid');
  return { file, bytes, registry, stages, sha256: digest(bytes) };
}
function identity(root, runId, runDirectory, testItems) {
  if (typeof runId !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId)) fail('invalid run identity');
  const directory = safe(root, 'Training_Materials', 'runs', runId);
  if (path.resolve(runDirectory) !== directory) fail('run directory differs from isolated identity');
  const context = read(safe(root, 'Training_Materials', 'runs', runId, 'run.json'));
  const state = read(safe(root, 'Training_Materials', 'runs', runId, 'state.json'));
  if (context.runId !== runId || context.mode !== 'training' || context.releaseId !== null
      || context.projectId !== null || path.resolve(root, context.artifactRoot) !== directory
      || state.runId !== runId || state.purpose !== 'framework-rehearsal'
      || state.target?.kind !== 'pipeline' || state.target.fromStage !== 'INPUT_SYNC'
      || state.target.toStage !== 'COMPILE') fail('not a full-chain isolated rehearsal run');
  if (state.testItems && !same(items(state.testItems), items(testItems))) fail('run TM identity changed');
  return directory;
}
function sourceGroups(source, testItems) {
  if (source?.schemaVersion !== 1 || source.kind !== 'verified-source-products'
      || !same(items(source.testItems), items(testItems)) || !Array.isArray(source.dft)
      || source.dft.length !== testItems.length) fail('unverified source plan');
  const groups = [{ role: 'schematic-expert', tm: null, source: source.schematic, names: SOURCE_NAMES.schematic }];
  for (const tm of testItems) {
    const match = source.dft.filter(item => item.tm === tm);
    if (match.length !== 1) fail(`DFT source identity missing for ${tm}`);
    groups.push({ role: 'dft-expert', tm, source: match[0], names: SOURCE_NAMES.dft });
  }
  for (const group of groups) {
    const entry = group.source;
    if (entry?.role !== group.role || !SHA.test(entry.canonicalInput?.sha256)
        || !Array.isArray(entry.files) || entry.files.length !== group.names.length
        || !Array.isArray(entry.fileHashes) || entry.fileHashes.length !== group.names.length) {
      fail(`invalid ${group.role} source gate`);
    }
  }
  return groups;
}
function manifestFile(runDirectory) { return safe(runDirectory, 'framework-rehearsal', 'source-manifest.json'); }
function registryFile(runDirectory) { return safe(runDirectory, 'framework-rehearsal', 'stage-registry.json'); }
function receiptFile(runDirectory, stage) { return safe(runDirectory, 'framework-rehearsal', 'stages', stage, 'receipt.json'); }
function artifactFile(runDirectory, stage, tm) { return safe(runDirectory, 'framework-rehearsal', 'stages', stage, tm, 'handoff.json'); }

/** Copy gate-ready products as opaque exact bytes; never hash canonical DLP input bytes here. */
export async function snapshotFrameworkSources({ workspaceRoot, runId, runDirectory, testItems, source, signal }) {
  const root = path.resolve(workspaceRoot);
  const normalized = items(testItems);
  const directory = identity(root, runId, runDirectory, normalized);
  const groups = sourceGroups(source, normalized);
  const registry = registryOf(root);
  const base = safe(directory, 'framework-rehearsal');
  if (fs.existsSync(base)) fail('source snapshot already exists; never overwrite a rehearsal run');
  fs.mkdirSync(base);
  fs.writeFileSync(registryFile(directory), registry.bytes, { flag: 'wx' });
  const files = [];
  for (const group of groups) {
    for (const [index, name] of group.names.entries()) {
      if (signal?.aborted) fail('source snapshot cancelled');
      const origin = assertSafeRunPath(root, group.source.files[index]);
      if (path.basename(origin) !== name || origin !== group.source.fileHashes[index]?.path) fail('source product name differs');
      const bytes = fs.readFileSync(origin);
      const sha256 = digest(bytes);
      if (sha256 !== group.source.fileHashes[index].sha256) fail(`source product changed before copy: ${name}`);
      const relative = group.tm ? `sources/dft/${group.tm}/${name}` : `sources/schematic/${name}`;
      const destination = safe(directory, 'framework-rehearsal', ...relative.split('/'));
      fs.mkdirSync(path.dirname(destination), { recursive: true });
      fs.writeFileSync(destination, bytes, { flag: 'wx' });
      files.push({ role: group.role, tm: group.tm, sourcePath: origin,
        path: relative, sha256, size: bytes.length, canonicalInputSha256: group.source.canonicalInput.sha256 });
    }
  }
  const manifest = { schemaVersion: 1, kind: 'framework-rehearsal-source-snapshot',
    disclaimer: 'Not a real business gate or expert delivery', runId, testItems: normalized,
    registrySha256: registry.sha256, stages: registry.stages, files };
  writeNew(manifestFile(directory), manifest);
  return Object.freeze({ runId, runDirectory: directory, manifestSha256: digest(bytesOf(manifest)),
    registrySha256: registry.sha256, testItems: normalized });
}

function loadSnapshot(root, snapshot) {
  const normalized = items(snapshot?.testItems);
  const directory = identity(root, snapshot.runId, snapshot.runDirectory, normalized);
  const manifestBytes = fs.readFileSync(manifestFile(directory));
  if (digest(manifestBytes) !== snapshot.manifestSha256) fail('source manifest binding changed');
  const manifest = JSON.parse(manifestBytes.toString('utf8'));
  const registryBytes = fs.readFileSync(registryFile(directory));
  if (digest(registryBytes) !== snapshot.registrySha256 || manifest.registrySha256 !== snapshot.registrySha256
      || manifest.kind !== 'framework-rehearsal-source-snapshot' || manifest.runId !== snapshot.runId
      || !same(manifest.testItems, normalized) || !Array.isArray(manifest.files)
      || manifest.files.length !== 7 + 3 * normalized.length) fail('source snapshot identity changed');
  const registry = JSON.parse(registryBytes.toString('utf8').replace(/^\uFEFF/, ''));
  const stages = registry.stateMachine?.filter(stage => stage !== 'COMPLETE');
  if (!same(stages, manifest.stages) || stages.length !== 7) fail('snapshot registry stage chain changed');
  const expectedPaths = [
    ...SOURCE_NAMES.schematic.map(name => `sources/schematic/${name}`),
    ...normalized.flatMap(tm => SOURCE_NAMES.dft.map(name => `sources/dft/${tm}/${name}`)),
  ];
  if (!same(manifest.files.map(entry => entry.path), expectedPaths)) fail('source snapshot file coverage changed');
  for (const entry of manifest.files) {
    if (!SHA.test(entry.sha256) || !SHA.test(entry.canonicalInputSha256)
        || !Number.isSafeInteger(entry.size) || entry.size < 0) fail('source snapshot digest invalid');
    const file = safe(directory, 'framework-rehearsal', ...entry.path.split('/'));
    const bytes = fs.readFileSync(file);
    if (bytes.length !== entry.size || digest(bytes) !== entry.sha256) fail(`source snapshot file changed: ${entry.path}`);
  }
  return { directory, manifest, registry, stages, sourceDigest: snapshot.manifestSha256 };
}

function stageInput(view, stage) {
  const index = view.stages.indexOf(stage);
  if (index < 0) fail(`stage not in frozen registry: ${stage}`);
  if (index === 0) return { kind: 'source-snapshot', sha256: view.sourceDigest };
  const previous = view.stages[index - 1];
  const file = receiptFile(view.directory, previous);
  if (!fs.existsSync(file)) fail(`upstream receipt missing: ${previous}`);
  verifyOne(view, previous);
  return { kind: 'stage-receipt', stage: previous, sha256: digest(fs.readFileSync(file)) };
}

function expectedArtifact(view, stage, tm, upstream) {
  return { schemaVersion: 1, kind: 'framework-rehearsal-handoff',
    disclaimer: 'Not a real business expert artifact or gate', runId: view.manifest.runId,
    stage, role: view.registry.stages[stage].owner, tm, rehearsalIteration: 1,
    executed: true, result: 'PASS', registrySha256: view.manifest.registrySha256,
    sourceSnapshotSha256: view.sourceDigest, upstream,
    sourceFiles: view.manifest.files.filter(file => file.tm === null || file.tm === tm)
      .map(file => ({ path: file.path, sha256: file.sha256 })) };
}

function expectedReceipt(view, stage, upstream, products) {
  return { schemaVersion: 1, kind: 'framework-rehearsal-stage-receipt',
    disclaimer: 'Independent rehearsal gate only; real business gate not evaluated',
    runId: view.manifest.runId, stage, role: view.registry.stages[stage].owner,
    gateLabel: 'FRAMEWORK_REHEARSAL_ONLY', rehearsalIteration: 1,
    testItems: view.manifest.testItems, executed: true, result: 'PASS',
    registrySha256: view.manifest.registrySha256, sourceSnapshotSha256: view.sourceDigest,
    upstream, products };
}

function verifyOne(view, stage) {
  const index = view.stages.indexOf(stage);
  if (index < 0) fail(`unknown stage: ${stage}`);
  const upstream = index === 0 ? { kind: 'source-snapshot', sha256: view.sourceDigest }
    : { kind: 'stage-receipt', stage: view.stages[index - 1],
      sha256: digest(fs.readFileSync(receiptFile(view.directory, view.stages[index - 1]))) };
  const products = [];
  for (const tm of view.manifest.testItems) {
    const file = artifactFile(view.directory, stage, tm);
    const actual = fs.readFileSync(file);
    const expected = bytesOf(expectedArtifact(view, stage, tm, upstream));
    if (!actual.equals(expected)) fail(`artifact binding changed: ${stage}/${tm}`);
    products.push({ tm, path: `stages/${stage}/${tm}/handoff.json`, sha256: digest(actual) });
  }
  const file = receiptFile(view.directory, stage);
  if (!fs.readFileSync(file).equals(bytesOf(expectedReceipt(view, stage, upstream, products)))) {
    fail(`receipt binding changed: ${stage}`);
  }
  return { stage, receiptSha256: digest(fs.readFileSync(file)), products };
}

function checkRequest(request, snapshot) {
  if (request?.runId !== snapshot.runId || !same(items(request.testItems), snapshot.testItems)
      || request.registryDigest !== snapshot.registrySha256 || request.mode !== 'training') {
    fail('stage request identity or registry changed');
  }
  const view = loadSnapshot(path.resolve(request.addressBook.runRoot, '..', '..', '..'), snapshot);
  if (!view.stages.includes(request.stage) || request.owner !== view.registry.stages[request.stage].owner
      || request.gate !== view.registry.stages[request.stage].gate) fail('stage owner or gate differs from frozen registry');
  const expectedRoles = request.stage === 'INPUT_SYNC' ? ['dft-expert', 'schematic-expert'] : [request.owner];
  if (!same(request.expectedRoles, expectedRoles)) fail('stage source role plan changed');
  return view;
}

/** Generate one real, run-local handoff per TM and a separate stage receipt. */
export async function executeFrameworkStage(request, snapshot) {
  const view = checkRequest(request, snapshot);
  const upstream = stageInput(view, request.stage);
  const products = [];
  for (const tm of view.manifest.testItems) {
    if (request.signal?.aborted) fail('stage cancelled');
    const file = artifactFile(view.directory, request.stage, tm);
    const artifact = expectedArtifact(view, request.stage, tm, upstream);
    writeNew(file, artifact);
    products.push({ tm, path: `stages/${request.stage}/${tm}/handoff.json`, sha256: digest(bytesOf(artifact)) });
  }
  if (request.signal?.aborted) fail('stage cancelled');
  writeNew(receiptFile(view.directory, request.stage), expectedReceipt(view, request.stage, upstream, products));
  return { terminals: request.expectedRoles.map(role => ({ role, status: 'done', testItems: [...request.testItems],
    executionKind: 'framework-rehearsal', realBusinessGatePassed: false })) };
}

/** Independent exact-byte gate for the stage and all preceding handoffs. */
export async function verifyFrameworkStage(request, snapshot) {
  const view = checkRequest(request, snapshot);
  for (const stage of view.stages.slice(0, view.stages.indexOf(request.stage) + 1)) verifyOne(view, stage);
  return { status: 'passed', exitCode: 0, gate: request.gate,
    gateKind: 'framework-rehearsal-only', realBusinessGatePassed: false,
    receiptSha256: digest(fs.readFileSync(receiptFile(view.directory, request.stage))) };
}

/** In-flight recovery never re-executes; only a fully verified receipt is reusable. */
export async function recoverFrameworkStage(request, snapshot) {
  await verifyFrameworkStage(request, snapshot);
  return { terminals: request.expectedRoles.map(role => ({ role, status: 'done', testItems: [...request.testItems],
    executionKind: 'framework-rehearsal-recovered', realBusinessGatePassed: false })) };
}

/** Reverify all seven exact-byte handoffs before terminal rehearsal PASS. */
export async function verifyFrameworkChain({ workspaceRoot, runId, testItems, snapshot }) {
  try {
    const root = path.resolve(workspaceRoot);
    if (runId !== snapshot.runId || !same(items(testItems), snapshot.testItems)) fail('full-chain run/TM identity differs');
    const view = loadSnapshot(root, snapshot);
    for (const stage of view.stages) verifyOne(view, stage);
    return { status: 'passed', result: '流程演练通过', runId, testItems: [...snapshot.testItems],
      stages: [...view.stages], gateKind: 'framework-rehearsal-only', realBusinessGatesPassed: false };
  } catch (error) {
    return { status: 'failed', reason: error.message, realBusinessGatesPassed: false };
  }
}

/** Reopen a persisted run using the digest binding written outside its snapshot. */
export function openFrameworkRehearsalSnapshot(workspaceRoot, runId) {
  const root = path.resolve(workspaceRoot);
  const directory = safe(root, 'Training_Materials', 'runs', runId);
  const state = read(safe(directory, 'state.json'));
  if (state.runId !== runId || state.purpose !== 'framework-rehearsal'
      || !SHA.test(state.snapshotBinding?.manifestSha256)
      || !SHA.test(state.snapshotBinding?.registrySha256)) fail('persisted snapshot binding is missing');
  const snapshot = { runId, runDirectory: directory, testItems: items(state.testItems),
    manifestSha256: state.snapshotBinding.manifestSha256,
    registrySha256: state.snapshotBinding.registrySha256 };
  loadSnapshot(root, snapshot);
  return snapshot;
}

export function createFrameworkRehearsalAdapters() {
  return { snapshot: snapshotFrameworkSources, executeStage: executeFrameworkStage,
    verifyStage: verifyFrameworkStage, recoverStage: recoverFrameworkStage, verifyChain: verifyFrameworkChain };
}
