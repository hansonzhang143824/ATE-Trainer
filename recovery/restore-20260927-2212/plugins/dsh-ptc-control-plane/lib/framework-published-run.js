import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { loadFrameworkRelease, verifyFrameworkRuntimeCompatibility } from './framework-release.js';
import { assertSafeRunPath } from './run-context.js';
import { sha256Bytes } from './release-integrity.js';

const MODE = 'FRAMEWORK_PUBLISHED_REPLAY';
const CORE = 'runtime/plugins/dsh-ptc-control-plane/lib/framework-published-run.js';
const SHA = /^[a-f0-9]{64}$/;
const ACTIVE = new Map();
const DFT = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];
const SCH = ['SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
  'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json'];
const clone = value => JSON.parse(JSON.stringify(value));
const bytes = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const safe = (root, ...parts) => assertSafeRunPath(root, path.join(root, ...parts));
const fail = message => { throw new Error(`framework published replay: ${message}`); };
const turn = () => new Promise(resolve => setImmediate(resolve));

function runRoot(workspaceRoot, runId) {
  if (typeof runId !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId)) fail('invalid runId');
  return safe(path.resolve(workspaceRoot), 'Published_Materials', 'framework-runs', runId);
}
function read(file) { return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '')); }
function writeNew(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, Buffer.isBuffer(value) ? value : bytes(value), { flag: 'wx' });
}
function atomicState(root, state) {
  const target = safe(root, 'state.json');
  const temporary = safe(root, `.state-${randomUUID()}.tmp`);
  writeNew(temporary, state);
  const fd = fs.openSync(temporary, 'r+');
  try { fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
  fs.renameSync(temporary, target);
}

/** All reads below are generated snapshot bytes, never canonical DLP inputs. */
function frozenBytes(release, relative) {
  if (typeof relative !== 'string' || relative.split('/').some(part => !part || part === '.' || part === '..')) fail('invalid frozen path');
  const entry = release.manifest.files.find(file => file.path === `snapshot/${relative}`);
  if (!entry) fail(`frozen file absent from manifest: ${relative}`);
  const value = fs.readFileSync(safe(release.snapshotRoot, ...relative.split('/')));
  if (value.length !== entry.size || sha256Bytes(value) !== entry.sha256) fail(`frozen file changed: ${relative}`);
  return value;
}
function frozenJson(release, relative) { return JSON.parse(frozenBytes(release, relative).toString('utf8')); }

function inspect(release) {
  if (!release.manifest.files.some(file => file.path === CORE)) fail('published replay runtime was not frozen; publish a new framework version');
  const state = frozenJson(release, 'state.json');
  const registryBytes = frozenBytes(release, 'pipeline-registry.json');
  const registry = JSON.parse(registryBytes.toString('utf8'));
  const registrySha256 = sha256Bytes(registryBytes);
  if (!registryBytes.equals(frozenBytes(release, 'framework-rehearsal/stage-registry.json'))) fail('frozen registries differ');
  const sourceBytes = frozenBytes(release, 'framework-rehearsal/source-manifest.json');
  const source = JSON.parse(sourceBytes.toString('utf8'));
  const sourceDigest = sha256Bytes(sourceBytes);
  const stages = registry.stateMachine?.filter(stage => stage !== 'COMPLETE');
  const testItems = source.testItems;
  if (!Array.isArray(stages) || stages.length !== 7 || new Set(stages).size !== 7
      || stages[0] !== 'INPUT_SYNC' || stages.at(-1) !== 'COMPILE'
      || stages.some(stage => !/^[A-Z_]+$/.test(stage) || typeof registry.stages?.[stage]?.owner !== 'string'
        || typeof registry.stages?.[stage]?.gate !== 'string')
      || source.schemaVersion !== 1 || source.kind !== 'framework-rehearsal-source-snapshot'
      || source.runId !== release.manifest.sourceRunId || !equal(source.stages, stages)
      || source.registrySha256 !== registrySha256 || state.snapshotBinding?.registrySha256 !== registrySha256
      || state.snapshotBinding?.manifestSha256 !== sourceDigest
      || !Array.isArray(testItems) || !testItems.length || testItems.length > 1000
      || testItems.some(tm => !/^TM\d+$/.test(tm)) || new Set(testItems).size !== testItems.length
      || !equal(state.testItems, testItems)) fail('frozen rehearsal identity or stage chain invalid');
  const paths = [...SCH.map(name => `sources/schematic/${name}`),
    ...testItems.flatMap(tm => DFT.map(name => `sources/dft/${tm}/${name}`))];
  if (!Array.isArray(source.files) || !equal(source.files.map(file => file.path), paths)) fail('frozen source coverage invalid');
  for (const entry of source.files) {
    const content = frozenBytes(release, `framework-rehearsal/${entry.path}`);
    const tm = entry.path.startsWith('sources/dft/') ? entry.path.split('/')[2] : null;
    if (entry.tm !== tm || entry.role !== (tm ? 'dft-expert' : 'schematic-expert')
        || !SHA.test(entry.canonicalInputSha256) || content.length !== entry.size
        || sha256Bytes(content) !== entry.sha256) fail(`source binding mismatch: ${entry.path}`);
  }
  const view = { release, state, registry, registrySha256, source, sourceDigest, stages, testItems };
  // A publisher verdict is not enough: independently rederive every frozen
  // rehearsal receipt/artifact before creating any published output directory.
  for (const stage of stages) verifyStage(view, stage);
  return view;
}

function verifyStage(view, stage) {
  const { release, source, sourceDigest, registrySha256, testItems } = view;
  const index = view.stages.indexOf(stage);
  const previous = view.stages[index - 1];
  const upstream = index === 0 ? { kind: 'source-snapshot', sha256: sourceDigest }
    : { kind: 'stage-receipt', stage: previous, sha256: sha256Bytes(frozenBytes(release, `framework-rehearsal/stages/${previous}/receipt.json`)) };
  const products = [];
  const artifacts = [];
  for (const tm of testItems) {
    const relative = `stages/${stage}/${tm}/handoff.json`;
    const content = frozenBytes(release, `framework-rehearsal/${relative}`);
    const expected = { schemaVersion: 1, kind: 'framework-rehearsal-handoff',
      disclaimer: 'Not a real business expert artifact or gate', runId: source.runId,
      stage, role: view.registry.stages[stage].owner, tm, rehearsalIteration: 1,
      executed: true, result: 'PASS', registrySha256, sourceSnapshotSha256: sourceDigest, upstream,
      sourceFiles: source.files.filter(file => file.tm === null || file.tm === tm).map(file => ({ path: file.path, sha256: file.sha256 })) };
    if (!content.equals(bytes(expected))) fail(`frozen artifact binding mismatch: ${stage}/${tm}`);
    const product = { tm, path: relative, sha256: sha256Bytes(content) };
    products.push(product); artifacts.push({ ...product, content });
  }
  const receipt = frozenBytes(release, `framework-rehearsal/stages/${stage}/receipt.json`);
  const expected = { schemaVersion: 1, kind: 'framework-rehearsal-stage-receipt',
    disclaimer: 'Independent rehearsal gate only; real business gate not evaluated', runId: source.runId,
    stage, role: view.registry.stages[stage].owner, gateLabel: 'FRAMEWORK_REHEARSAL_ONLY',
    rehearsalIteration: 1, testItems, executed: true, result: 'PASS', registrySha256,
    sourceSnapshotSha256: sourceDigest, upstream, products };
  if (!receipt.equals(bytes(expected))) fail(`frozen receipt binding mismatch: ${stage}`);
  return { receipt, artifacts };
}

/** Display only. This does not authorize continuation after host restart. */
export function readFrameworkPublishedRun({ workspaceRoot, runId }) {
  const root = runRoot(workspaceRoot, runId);
  const context = read(safe(root, 'run.json'));
  const state = read(safe(root, 'state.json'));
  if (context.runId !== runId || context.mode !== 'published' || context.purpose !== 'framework-published-replay'
      || state.runId !== runId || state.releaseId !== context.releaseId || state.bundleDigest !== context.bundleDigest
      || state.outcome?.mode !== MODE || state.outcome.realBusinessGatesPassed !== false) fail('published run identity changed');
  return state;
}

/**
 * No caller-supplied stage, TM, receipt, release or executor override exists.
 * The frozen version determines the whole replay. start yields before work so
 * an HTTP caller can return 202. Synchronous filesystem verification has elapsed
 * budget checkpoints; host process isolation is required for an OS-I/O hard stop.
 */
export function createFrameworkPublishedRun(options) {
  const allowed = ['workspaceRoot', 'runId', 'onState', 'signal', 'budgetMs'];
  if (!options || Object.keys(options).some(key => !allowed.includes(key))) fail('unsupported published run override');
  const { workspaceRoot, runId, onState, signal, budgetMs = 30_000 } = options;
  if (!Number.isFinite(budgetMs) || budgetMs <= 0 || budgetMs > 30_000) fail('budget must be within 30 seconds');
  const workspace = path.resolve(workspaceRoot);
  const root = runRoot(workspace, runId);
  if (ACTIVE.has(root) || fs.existsSync(root)) fail('published run already exists; never overwrite or blindly resume');
  let view;
  let promise;
  let activeMs = 0;
  let segmentStart;
  let contextSha256;
  let registrySha256;
  let ownsRoot = false;
  const state = { schemaVersion: 1, runId, mode: 'published', purpose: 'framework-published-replay',
    artifactRoot: path.relative(workspace, root).replaceAll('\\', '/'), releaseId: null, bundleDigest: null,
    status: 'created', reason: null, stages: [], testItems: [], createdAt: new Date().toISOString(),
    outcome: { mode: MODE, realBusinessGatesPassed: false, disclaimer: 'Frozen framework replay only; no real business gates, experts, compiler or hardware executed' } };
  const snapshot = () => clone(state);
  function save() {
    state.updatedAt = new Date().toISOString();
    if (ownsRoot) atomicState(root, state);
    try { onState?.(snapshot()); } catch { /* Observers cannot trigger re-execution. */ }
  }
  function check() {
    if (signal?.aborted) { state.status = 'cancelled'; state.reason = 'aborted by host'; }
    if (state.status === 'cancelled') fail(state.reason ?? 'stopped');
    if (activeMs + (segmentStart === undefined ? 0 : Date.now() - segmentStart) > budgetMs) fail('30-second bounded replay budget exceeded');
  }
  function verifyFrozen() {
    check();
    // The active pointer selects a version only when the run is first bound.
    // Subsequent stages verify the run's pinned snapshot, even after a newer
    // framework release becomes active.
    const release = loadFrameworkRelease({ workspaceRoot: workspace,
      ...(view ? { releaseId: state.releaseId } : {}) });
    verifyFrameworkRuntimeCompatibility({ workspaceRoot: workspace, releaseId: release.manifest.releaseId });
    if (view && (release.manifest.releaseId !== state.releaseId || release.manifest.bundleDigest !== state.bundleDigest)) fail('active framework release changed; frozen run cannot switch versions');
    if (view && (sha256Bytes(fs.readFileSync(safe(root, 'run.json'))) !== contextSha256
        || sha256Bytes(fs.readFileSync(safe(root, 'pipeline-registry.json'))) !== registrySha256)) fail('published run context or choreography changed');
    check();
    return release;
  }
  async function drive() {
    await turn();
    if (state.status === 'cancelled' || state.status === 'paused') return snapshot();
    segmentStart = Date.now();
    try {
      if (!view) {
        const release = verifyFrozen();
        const candidate = inspect(release);
        check();
        fs.mkdirSync(path.dirname(root), { recursive: true });
        fs.mkdirSync(root);
        ownsRoot = true;
        view = candidate;
        state.releaseId = release.manifest.releaseId; state.bundleDigest = release.manifest.bundleDigest;
        state.runtimeDigest = release.manifest.runtimeDigest;
        state.sourceRunId = release.manifest.sourceRunId;
        state.testItems = [...view.testItems];
        state.stages = view.stages.map(stage => ({ stage, status: 'pending', owner: view.registry.stages[stage].owner, gateResult: null }));
        writeNew(safe(root, 'run.json'), { ...snapshot(), choreographyEditable: false });
        writeNew(safe(root, 'pipeline-registry.json'), frozenBytes(release, 'pipeline-registry.json'));
        contextSha256 = sha256Bytes(fs.readFileSync(safe(root, 'run.json')));
        registrySha256 = sha256Bytes(fs.readFileSync(safe(root, 'pipeline-registry.json')));
      }
      state.status = 'running'; save();
      for (const stage of state.stages) {
        await turn();
        check();
        if (state.status === 'paused') break;
        if (stage.status === 'completed') continue;
        verifyFrozen();
        const frozen = verifyStage(view, stage.stage);
        check();
        stage.status = 'running'; save();
        check();
        if (state.status === 'paused') { stage.status = 'pending'; save(); break; }
        const products = [];
        for (const artifact of frozen.artifacts) {
          check();
          const target = safe(root, ...artifact.path.split('/'));
          writeNew(target, artifact.content);
          const actual = fs.readFileSync(target);
          if (!actual.equals(artifact.content)) fail('replayed artifact bytes differ');
          products.push({ tm: artifact.tm, path: artifact.path, sha256: sha256Bytes(actual) });
        }
        const stageRoot = safe(root, 'stages', stage.stage);
        writeNew(safe(stageRoot, 'frozen-receipt.json'), frozen.receipt);
        const previous = state.stages[state.stages.indexOf(stage) - 1];
        const receipt = { schemaVersion: 1, kind: 'framework-published-replay-stage', runId,
          releaseId: state.releaseId, bundleDigest: state.bundleDigest, sourceRunId: state.sourceRunId,
          stage: stage.stage, owner: stage.owner, mode: MODE, realBusinessGatePassed: false,
          frozenReceiptSha256: sha256Bytes(frozen.receipt), products,
          upstreamReplayReceiptSha256: previous?.gateResult?.receiptSha256 ?? null };
        const receiptPath = safe(stageRoot, 'replay-receipt.json');
        writeNew(receiptPath, receipt);
        check();
        stage.gateResult = { status: 'passed', exitCode: 0, gate: view.registry.stages[stage.stage].gate,
          gateKind: 'framework-published-replay-only', realBusinessGatePassed: false,
          receiptPath, receiptSha256: sha256Bytes(fs.readFileSync(receiptPath)) };
        stage.status = 'completed'; save();
      }
      if (state.stages.every(stage => stage.status === 'completed')) {
        verifyFrozen();
        // Recheck output bindings before terminal success, including earlier stages.
        for (const stage of state.stages) {
          check();
          const receipt = fs.readFileSync(safe(root, 'stages', stage.stage, 'replay-receipt.json'));
          if (sha256Bytes(receipt) !== stage.gateResult.receiptSha256) fail('replay receipt changed');
          const parsed = JSON.parse(receipt);
          if (sha256Bytes(fs.readFileSync(safe(root, 'stages', stage.stage, 'frozen-receipt.json'))) !== parsed.frozenReceiptSha256) fail('copied frozen receipt changed');
          for (const product of parsed.products) {
            if (sha256Bytes(fs.readFileSync(safe(root, ...product.path.split('/')))) !== product.sha256) fail('replay artifact changed');
          }
        }
        check(); state.status = 'completed'; save();
      }
    } catch (error) {
      if (state.status !== 'cancelled') state.status = 'blocked';
      state.reason = error.message;
      const stage = state.stages.find(entry => entry.status !== 'completed');
      if (stage) stage.status = state.status;
      // Keep a visible blocked receipt even if no release could be verified.
      // Null identity is intentional; never invent a release binding. Exclusive
      // creation prevents a raced controller from overwriting another run.
      if (!ownsRoot && !fs.existsSync(root)) {
        fs.mkdirSync(path.dirname(root), { recursive: true });
        fs.mkdirSync(root); ownsRoot = true;
        writeNew(safe(root, 'run.json'), { ...snapshot(), releaseVerified: false, choreographyEditable: false });
      }
      save();
    } finally {
      activeMs += Date.now() - segmentStart; segmentStart = undefined;
    }
    return snapshot();
  }
  const controller = {
    getState: snapshot,
    start() {
      if (promise) return promise;
      if (['completed', 'blocked', 'cancelled'].includes(state.status)) return Promise.resolve(snapshot());
      if (state.status === 'paused') fail('use resume for a paused replay');
      ACTIVE.set(root, controller);
      promise = drive().finally(() => { promise = undefined; ACTIVE.delete(root); });
      return promise;
    },
    pause() {
      if (!['created', 'running'].includes(state.status)) return snapshot();
      state.status = 'paused'; state.reason = 'paused at a deterministic stage boundary'; save(); return snapshot();
    },
    resume() {
      if (promise) fail('wait for current replay operation to settle');
      if (state.status !== 'paused') fail('only a paused in-memory replay can resume');
      state.status = 'created'; state.reason = null; return controller.start();
    },
    stop(reason = 'stopped by user') {
      if (['completed', 'blocked', 'cancelled'].includes(state.status)) return snapshot();
      state.status = 'cancelled'; state.reason = String(reason); save(); return snapshot();
    },
  };
  return controller;
}
