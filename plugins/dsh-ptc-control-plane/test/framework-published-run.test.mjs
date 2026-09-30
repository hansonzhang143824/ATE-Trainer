import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { sha256Bytes } from '../lib/release-integrity.js';
import { createTrainingRun } from '../lib/training-run.js';
import { snapshotFrameworkSources, executeFrameworkStage, verifyFrameworkStage } from '../lib/framework-rehearsal.js';
import { stageFrameworkRelease, activateStagedFrameworkRelease, FRAMEWORK_RUNTIME_FILES } from '../lib/framework-release.js';
import { createFrameworkPublishedRun, readFrameworkPublishedRun } from '../lib/framework-published-run.js';

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const SCH = ['SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
  'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json'];
const DFT = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];
function put(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, Buffer.isBuffer(value) ? value : typeof value === 'string' ? value : `${JSON.stringify(value, null, 2)}\n`);
}

async function fixture() {
  // Deliberately retain small isolated fixtures: recursive cleanup on this
  // protected Windows host has previously stalled after assertions complete.
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-published-replay-'));
  for (const name of FRAMEWORK_RUNTIME_FILES) put(path.join(workspaceRoot, name), fs.readFileSync(path.join(repositoryRoot, name)));
  const registryBytes = fs.readFileSync(new URL('./fixtures/legacy-framework-stage-registry.json', import.meta.url));
  const registry = JSON.parse(registryBytes);
  put(path.join(workspaceRoot, 'team/ptc/ptc_stage_registry.json'), registryBytes);
  const runId = 'source-rehearsal';
  const testItems = ['TM109'];
  const { context, state } = createTrainingRun(workspaceRoot, { runId,
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' }, purpose: 'framework-rehearsal' });
  const runDirectory = path.join(workspaceRoot, context.artifactRoot);
  function group(role, names, tm = null) {
    const files = names.map(name => {
      const file = path.join(workspaceRoot, 'fixture-products', role, name);
      put(file, `opaque generated fixture product: ${name}\n`);
      return file;
    });
    return { role, ...(tm ? { tm } : {}), canonicalInput: { sha256: 'a'.repeat(64) }, files,
      fileHashes: files.map(file => ({ path: file, sha256: sha256Bytes(fs.readFileSync(file)) })) };
  }
  const source = { schemaVersion: 1, kind: 'verified-source-products', testItems,
    schematic: group('schematic-expert', SCH), dft: [group('dft-expert', DFT, 'TM109')] };
  const snapshot = await snapshotFrameworkSources({ workspaceRoot, runId, runDirectory, testItems, source });
  const stages = registry.stateMachine.filter(stage => stage !== 'COMPLETE');
  const progress = [];
  for (const stage of stages) {
    const request = { runId, mode: 'training', stage, owner: registry.stages[stage].owner,
      gate: registry.stages[stage].gate, testItems, registryDigest: snapshot.registrySha256,
      expectedRoles: stage === 'INPUT_SYNC' ? ['dft-expert', 'schematic-expert'] : [registry.stages[stage].owner],
      addressBook: { runRoot: runDirectory } };
    const terminal = await executeFrameworkStage(request, snapshot);
    const gateResult = await verifyFrameworkStage(request, snapshot);
    progress.push({ stage, status: 'completed', terminals: terminal.terminals, gateResult });
  }
  put(path.join(runDirectory, 'state.json'), { ...state, status: 'completed', testItems,
    snapshotBinding: { manifestSha256: snapshot.manifestSha256, registrySha256: snapshot.registrySha256 },
    outcome: { mode: 'FRAMEWORK_REHEARSAL', realBusinessGatesPassed: false } });
  put(path.join(runDirectory, 'pipeline-registry.json'), registryBytes);
  put(path.join(runDirectory, 'pipeline-progress.json'), { runId, status: 'completed', stages: progress });
  const releaseOptions = { workspaceRoot, releaseId: 'framework-v1', sourceRunId: runId, createdBy: 'fixture',
    verifyRehearsal: async () => ({ kind: 'framework-rehearsal', status: 'passed', runId, realBusinessGatesPassed: false }) };
  const staged = await stageFrameworkRelease(releaseOptions);
  activateStagedFrameworkRelease({ workspaceRoot, stagingId: staged.stagingId });
  const releaseRoot = path.join(workspaceRoot, 'team/ptc/framework-releases/framework-v1');
  return { workspaceRoot, runDirectory, stages, releaseRoot, releaseOptions,
    runRoot: id => path.join(workspaceRoot, 'Published_Materials/framework-runs', id) };
}

test('published replay verifies all seven frozen stages, isolates outputs and never mutates source runs', async () => {
  const f = await fixture();
  const sourceBefore = fs.readFileSync(path.join(f.runDirectory, 'state.json'));
  const controller = createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'replay-1' });
  const promise = controller.start();
  assert.equal(controller.getState().status, 'created', 'start yields before HTTP completion');
  const result = await promise;
  assert.equal(result.status, 'completed', result.reason);
  assert.equal(result.releaseId, 'framework-v1');
  assert.equal(result.outcome.mode, 'FRAMEWORK_PUBLISHED_REPLAY');
  assert.equal(result.outcome.realBusinessGatesPassed, false);
  assert.deepEqual(result.stages.map(stage => stage.stage), f.stages);
  for (const stage of result.stages) {
    assert.equal(stage.gateResult.realBusinessGatePassed, false);
    assert.equal(stage.gateResult.gateKind, 'framework-published-replay-only');
    const receiptBytes = fs.readFileSync(stage.gateResult.receiptPath);
    assert.equal(sha256Bytes(receiptBytes), stage.gateResult.receiptSha256);
    assert.deepEqual(fs.readFileSync(path.join(f.runRoot('replay-1'), 'stages', stage.stage, 'TM109/handoff.json')),
      fs.readFileSync(path.join(f.releaseRoot, 'snapshot/framework-rehearsal/stages', stage.stage, 'TM109/handoff.json')));
  }
  assert.deepEqual(fs.readFileSync(path.join(f.runDirectory, 'state.json')), sourceBefore);
  assert.equal(readFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'replay-1' }).status, 'completed');
  assert.throws(() => createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'replay-1' }), /already exists/);
});

test('caller cannot override frozen release, TM set, choreography or inject stage executors', () => {
  for (const option of ['releaseId', 'testItems', 'stages', 'fromStage', 'executeStage', 'runDirectory']) {
    assert.throws(() => createFrameworkPublishedRun({ workspaceRoot: repositoryRoot, runId: 'forbidden', [option]: 'override' }), /unsupported/);
  }
  for (const runId of ['../escape', 'NUL', 'trailing.']) assert.throws(() => createFrameworkPublishedRun({ workspaceRoot: repositoryRoot, runId }));
  assert.throws(() => createFrameworkPublishedRun({ workspaceRoot: repositoryRoot, runId: 'test', budgetMs: 30001 }), /30 seconds/);
});

test('missing active version and runtime drift persist blocked evidence without false release binding', async () => {
  const empty = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-replay-empty-'));
  const absent = await createFrameworkPublishedRun({ workspaceRoot: empty, runId: 'missing' }).start();
  assert.equal(absent.status, 'blocked');
  assert.equal(readFrameworkPublishedRun({ workspaceRoot: empty, runId: 'missing' }).releaseId, null);
  const f = await fixture();
  fs.appendFileSync(path.join(f.workspaceRoot, 'plugins/dsh-ptc-control-plane/lib/framework-published-run.js'), '\n// drift');
  const result = await createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'drift' }).start();
  assert.equal(result.status, 'blocked');
  assert.match(result.reason, /runtime implementation differs/);
  assert.equal(readFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'drift' }).bundleDigest, null);
});

test('tampered active snapshot and pointer are rejected before replay', async () => {
  const f = await fixture();
  const pointerFile = path.join(f.workspaceRoot, 'team/ptc/framework-releases/active-framework-release.json');
  const pointerBytes = fs.readFileSync(pointerFile);
  put(pointerFile, { ...JSON.parse(pointerBytes), bundleDigest: '0'.repeat(64) });
  const pointerResult = await createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'bad-pointer' }).start();
  assert.equal(pointerResult.status, 'blocked');
  assert.match(pointerResult.reason, /digest mismatch/);
  put(pointerFile, pointerBytes);
  fs.appendFileSync(path.join(f.releaseRoot, 'snapshot/framework-rehearsal/stages/METHOD/receipt.json'), ' ');
  const artifactResult = await createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'bad-snapshot' }).start();
  assert.equal(artifactResult.status, 'blocked');
  assert.match(artifactResult.reason, /sha256 mismatch/);
});

test('pause preserves completed receipts; resume continues without rewriting previous stages', async () => {
  const f = await fixture();
  let paused = false;
  let controller;
  controller = createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'pause', onState(state) {
    if (!paused && state.stages[0]?.status === 'completed') { paused = true; controller.pause(); }
  } });
  const first = await controller.start();
  assert.equal(first.status, 'paused');
  assert.equal(first.stages[1].status, 'pending');
  const before = fs.readFileSync(first.stages[0].gateResult.receiptPath);
  const last = await controller.resume();
  assert.equal(last.status, 'completed', last.reason);
  assert.deepEqual(fs.readFileSync(first.stages[0].gateResult.receiptPath), before);
});

test('paused replay continues on its pinned release after a successor becomes active', async () => {
  const f = await fixture();
  let paused = false;
  let controller;
  controller = createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'pinned', onState(state) {
    if (!paused && state.stages[0]?.status === 'completed') { paused = true; controller.pause(); }
  } });
  const first = await controller.start();
  assert.equal(first.status, 'paused');
  assert.equal(first.releaseId, 'framework-v1');
  const firstReceipt = fs.readFileSync(first.stages[0].gateResult.receiptPath);
  const staged = await stageFrameworkRelease({ ...f.releaseOptions, releaseId: 'framework-v2' });
  const active = activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  assert.equal(active.releaseId, 'framework-v2');
  const result = await controller.resume();
  assert.equal(result.status, 'completed', result.reason);
  assert.equal(result.releaseId, 'framework-v1');
  assert.deepEqual(fs.readFileSync(first.stages[0].gateResult.receiptPath), firstReceipt);
  assert.ok(result.stages.every(stage => stage.gateResult.realBusinessGatePassed === false));
});

test('tampering with the pinned old release blocks replay after active release changes', async () => {
  const f = await fixture();
  let paused = false;
  let controller;
  controller = createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'pinned-tamper', onState(state) {
    if (!paused && state.stages[0]?.status === 'completed') { paused = true; controller.pause(); }
  } });
  const first = await controller.start();
  assert.equal(first.status, 'paused');
  const staged = await stageFrameworkRelease({ ...f.releaseOptions, releaseId: 'framework-v2' });
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  fs.appendFileSync(path.join(f.releaseRoot, 'snapshot/framework-rehearsal/stages/METHOD/receipt.json'), ' ');
  const result = await controller.resume();
  assert.equal(result.status, 'blocked');
  assert.equal(result.releaseId, 'framework-v1');
  assert.match(result.reason, /sha256 mismatch/);
  assert.equal(result.stages[1].status, 'blocked');
});

test('stop and host abort never automatically advance or resume', async () => {
  const f = await fixture();
  let controller;
  controller = createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'stop', onState(state) {
    if (state.stages[0]?.status === 'completed' && state.status === 'running') controller.stop('operator stop');
  } });
  const result = await controller.start();
  assert.equal(result.status, 'cancelled');
  assert.equal(result.stages[1].status, 'cancelled');
  assert.equal(result.stages[2].status, 'pending');
  assert.throws(() => controller.resume(), /only a paused/);
  const signal = AbortSignal.abort();
  const aborted = await createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'abort', signal }).start();
  assert.equal(aborted.status, 'cancelled');
  assert.equal(readFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'abort' }).status, 'cancelled');
});

test('runtime or copied choreography changed between stages blocks remaining stages', async () => {
  const f = await fixture();
  let mutated = false;
  const controller = createFrameworkPublishedRun({ workspaceRoot: f.workspaceRoot, runId: 'mutation', onState(state) {
    if (!mutated && state.stages[0]?.status === 'completed') {
      mutated = true;
      fs.appendFileSync(path.join(f.runRoot('mutation'), 'pipeline-registry.json'), ' ');
    }
  } });
  const result = await controller.start();
  assert.equal(result.status, 'blocked');
  assert.match(result.reason, /choreography changed/);
  assert.equal(result.stages[1].status, 'blocked');
});
