import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { setTimeout as delay } from 'node:timers/promises';
import { createFrameworkRunner, resolveFrameworkInput } from '../lib/framework-agent-run.js';
import { ensureTrainerProject, applyChanges } from '../lib/trainer-project.js';
import { resolveBundle, bundleManifestBytes } from '../lib/trainer-bundle.js';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';
import { frameworkSha } from '../lib/trainer-run-events.js';

const deferred = () => { let resolve; const promise = new Promise(yes => { resolve = yes; }); return { promise, resolve }; };
async function until(check) { for (let i = 0; i < 200; i++) { if (check()) return; await delay(5); } throw new Error('condition timed out'); }
function fixture(t, edit) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-c-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const seed = createSyntheticTrainerFixture(); edit?.(seed.files);
  const project = ensureTrainerProject(root, { projectId: 'synthetic-lab', seed });
  const bundle = resolveBundle(root, { projectId: project.projectId, targetKind: 'workflow', targetId: 'lab-pair', model: { provider: 'fake', model: 'synthetic-only' } });
  return { root, bundle, project };
}
function fakeAdapter(before = async () => {}) {
  const calls = [];
  return { calls, async dispatch(args) {
    calls.push(args);
    const identity = { parentSessionId: `parent-${args.runId}`, childSessionId: `child-${args.runId}-${args.step.stepId}` };
    args.onStart(identity);
    await before(args);
    const output = args.step.agentId === 'lab-producer' ? { value: args.input.seed + 1, marker: 'v1', scriptMarker: 'script-v1' } : { receivedValue: args.input.receivedValue };
    return { ...identity, output, stopReason: 'completed', childTerminationConfirmed: true };
  } };
}
const start = (runner, bundle, runId = 'framework-test', seed = 7, mode = 'training') => runner.startRun({ runId, requestId: `request-${runId}`, bundle, input: { seed }, mode });

test('fake adapter: real payload handoff, immutable snapshot, durable history and cursor', async t => {
  const { root, bundle } = fixture(t); const adapter = fakeAdapter();
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter });
  const accepted = await start(runner, bundle);
  assert.equal(accepted.status, 'queued'); assert.equal(JSON.stringify(accepted).includes('completion'), false);
  bundle.steps[1].inputBindings['/receivedValue'].pointer = '/missing';
  const run = await runner.waitForRun(accepted);
  assert.equal(run.status, 'completed'); assert.deepEqual(run.output, { receivedValue: 8 });
  assert.equal(run.businessGatePassed, false); assert.equal(run.testResults[0].ok, true);
  assert.equal(adapter.calls[1].input.receivedValue, 8);
  assert.equal(Object.isFrozen(adapter.calls[0].bundle), true);
  assert.equal(run.steps[0].actualLoadedRefs.some(ref => ref.path.endsWith('marker.json')), true);
  const reloaded = createFrameworkRunner({ workspaceRoot: root, adapter });
  assert.equal(reloaded.readRun(accepted).bundle.steps[1].inputBindings['/receivedValue'].pointer, '/value');
  const events = reloaded.readEvents(accepted);
  assert.equal(events.events[0].seq, 1);
  assert.ok(events.events.some(event => event.type === 'child-started'));
  assert.equal(reloaded.readEvents({ ...accepted, cursor: events.cursor }).events.length, 0);
  assert.equal(reloaded.listRuns({ projectId: 'synthetic-lab' }).nextCursor, null);
  assert.equal(reloaded.listRuns({ projectId: 'other' }).runs.length, 0);
  await assert.rejects(start(runner, run.bundle), /already exists/);
});

test('missing upstream field fails before downstream dispatch', async t => {
  const { root, bundle } = fixture(t, files => {
    const flow = JSON.parse(files['workflows/lab-pair.json']); flow.steps[1].inputBindings['/receivedValue'].pointer = '/missing'; files['workflows/lab-pair.json'] = JSON.stringify(flow);
  });
  const adapter = fakeAdapter(); const runner = createFrameworkRunner({ workspaceRoot: root, adapter });
  await start(runner, bundle); const run = await runner.waitForRun({ runId: 'framework-test' });
  assert.equal(run.status, 'failed'); assert.equal(run.error.code, 'INPUT_BINDING_MISSING'); assert.equal(adapter.calls.length, 1);
});

test('running draft edits affect only the next bundle', async t => {
  const { root, bundle, project } = fixture(t); const gate = deferred();
  const adapter = fakeAdapter(args => args.step.stepId === 'produce' ? gate.promise : undefined);
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter }); await start(runner, bundle);
  await until(() => adapter.calls.length === 1);
  applyChanges(root, { projectId: project.projectId, requestId: 'change-1', baseRevision: project.revisionId, reason: 'synthetic version edit', changes: [{ path: 'agents/lab-consumer/instructions.md', content: 'New version instruction' }] });
  gate.resolve(); const run = await runner.waitForRun({ runId: 'framework-test' });
  assert.equal(run.status, 'completed');
  assert.notEqual(adapter.calls[1].bundle.files.find(file => file.path === 'agents/lab-consumer/instructions.md').content, 'New version instruction');
  const changed = resolveBundle(root, { projectId: project.projectId, targetKind: 'workflow', targetId: 'lab-pair', model: bundle.model });
  assert.notEqual(changed.bundleSha256, run.bundleSha256);
});

test('pause takes effect at boundary, then resume dispatches next step', async t => {
  const { root, bundle } = fixture(t); const gate = deferred(); const adapter = fakeAdapter(args => args.step.stepId === 'produce' ? gate.promise : undefined);
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter }); await start(runner, bundle); await until(() => adapter.calls.length === 1);
  assert.equal(runner.controlRun({ runId: 'framework-test', action: 'pause' }).status, 'pausing');
  gate.resolve(); await until(() => runner.readRun({ runId: 'framework-test' }).status === 'paused');
  assert.equal(adapter.calls.length, 1); runner.controlRun({ runId: 'framework-test', action: 'resume' });
  assert.equal((await runner.waitForRun({ runId: 'framework-test' })).status, 'completed'); assert.equal(adapter.calls.length, 2);
});

test('stop prevents downstream and stays stopping until late termination confirmation', async t => {
  const { root, bundle } = fixture(t); const gate = deferred(); const adapter = fakeAdapter(() => gate.promise);
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter }); await start(runner, bundle); await until(() => adapter.calls.length === 1);
  const stopped = runner.controlRun({ runId: 'framework-test', action: 'stop' });
  assert.equal(stopped.status, 'stopping'); assert.equal(stopped.childTerminationConfirmed, false);
  await runner.waitForRun({ runId: 'framework-test' });
  await assert.rejects(start(runner, bundle, 'framework-duplicate'), { code: 'TERMINATION_UNCONFIRMED' });
  gate.resolve(); await until(() => runner.readRun({ runId: 'framework-test' }).status === 'cancelled');
  assert.equal(adapter.calls.length, 1); assert.equal(runner.readRun({ runId: 'framework-test' }).childTerminationConfirmed, true);
});

test('startup timeout is visible and late settlement cannot make it successful', async t => {
  const { root, bundle } = fixture(t, files => {
    const flow = JSON.parse(files['workflows/lab-pair.json']); flow.steps[0].timeoutMs = 20; files['workflows/lab-pair.json'] = JSON.stringify(flow);
  });
  const gate = deferred(); const adapter = fakeAdapter(() => gate.promise);
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter }); await start(runner, bundle);
  await delay(40); const pending = await runner.waitForRun({ runId: 'framework-test' });
  assert.equal(pending.status, 'stopping'); assert.equal(pending.error.code, 'TRAINING_CANCELLED');
  gate.resolve(); await until(() => runner.readRun({ runId: 'framework-test' }).status === 'failed');
  assert.equal(adapter.calls.length, 1);
});

test('repeated role steps dispatch independent children', async t => {
  const { root, bundle } = fixture(t, files => {
    const flow = JSON.parse(files['workflows/lab-pair.json']); flow.steps.push({ stepId: 'produce-again', agentId: 'lab-producer', inputBindings: { '/seed': { source: 'step', stepId: 'consume', pointer: '/receivedValue' } } });
    files['workflows/lab-pair.json'] = JSON.stringify(flow); delete files['tests/lab-pair.json'];
  });
  const adapter = fakeAdapter(); const runner = createFrameworkRunner({ workspaceRoot: root, adapter }); await start(runner, bundle);
  const run = await runner.waitForRun({ runId: 'framework-test' }); assert.equal(run.output.value, 9); assert.equal(new Set(run.steps.map(step => step.childSessionId)).size, 3);
});

test('release replay reads only bundle and writes publish output', async t => {
  const { root, bundle } = fixture(t); fs.rmSync(path.join(root, 'Training_Materials'), { recursive: true });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: fakeAdapter() }); await start(runner, bundle, 'framework-replay', 19, 'published');
  const run = await runner.waitForRun({ runId: 'framework-replay' }); assert.equal(run.status, 'completed'); assert.equal(run.output.receivedValue, 20); assert.equal(run.purpose, 'FRAMEWORK_REPLAY');
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials')), false);
});

test('invalid bundle is rejected before dispatch', async t => {
  const { root, bundle } = fixture(t); bundle.files[0].content += 'tamper'; const adapter = fakeAdapter(); const runner = createFrameworkRunner({ workspaceRoot: root, adapter });
  await assert.rejects(start(runner, bundle), { code: 'BUNDLE_INVALID' }); assert.equal(adapter.calls.length, 0);
});

test('restart marks persisted paused run interrupted without dispatch', async t => {
  const { root, bundle } = fixture(t); const gate = deferred(); const adapter = fakeAdapter(() => gate.promise);
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter }); await start(runner, bundle); await until(() => adapter.calls.length === 1);
  runner.controlRun({ runId: 'framework-test', action: 'pause' }); gate.resolve(); await until(() => runner.readRun({ runId: 'framework-test' }).status === 'paused');
  const secondAdapter = fakeAdapter(); const reloaded = createFrameworkRunner({ workspaceRoot: root, adapter: secondAdapter });
  assert.deepEqual(reloaded.reconcileInterrupted(), ['framework-test']); assert.equal(reloaded.readRun({ runId: 'framework-test' }).status, 'interrupted'); assert.equal(secondAdapter.calls.length, 0);
  // Simulated old host is released only to avoid leaving a pending test promise.
  runner.controlRun({ runId: 'framework-test', action: 'stop' }); await runner.waitForRun({ runId: 'framework-test' });
});

test('JSON pointer escaping and unsafe destinations', () => {
  assert.deepEqual(resolveFrameworkInput({ inputBindings: { '/value': { source: 'input', pointer: '/a~1b/~0' } } }, { 'a/b': { '~': 42 } }, new Map()), { value: 42 });
  assert.deepEqual(resolveFrameworkInput({ inputBindings: { '': { source: 'input', pointer: '' } } }, { seed: 7, nested: { ok: true } }, new Map()), { seed: 7, nested: { ok: true } });
  assert.deepEqual(resolveFrameworkInput({ inputBindings: { '': { source: 'step', stepId: 'upstream', pointer: '' } } }, {}, new Map([['upstream', { value: 8 }]])), { value: 8 });
  assert.throws(() => resolveFrameworkInput({ inputBindings: { '/__proto__/x': { source: 'literal', value: 1 } } }, {}, new Map()), /unsafe/);
});
