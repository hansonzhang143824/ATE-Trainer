import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';
import { createTrainingPipeline } from '../lib/training-pipeline.js';

const stages = ['INPUT_SYNC', 'STRATEGY', 'COMPILE'];
const registry = { stateMachine: [...stages, 'COMPLETE'], stages: {
  INPUT_SYNC: { owner: 'captain', gate: 'scripts/input.py', families: ['all'] },
  STRATEGY: { owner: 'test-strategy-architect', gate: 'scripts/strategy.py', families: ['all'] },
  COMPILE: { owner: 'compile-diagnostician', gate: 'scripts/compile.py', families: ['all'] },
} };
const terminals = (request) => ({ terminals: request.expectedRoles.map((role) => ({ role, status: 'done', testItems: request.testItems })) });
const passed = (request) => ({ status: 'passed', exitCode: 0, gate: request.gate });
function deferred() { let resolve; const promise = new Promise((done) => { resolve = done; }); return { promise, resolve }; }
function fixture(t, target = { kind: 'pipeline' }) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-pipeline-test-'));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  fs.mkdirSync(path.join(workspaceRoot, 'team/ptc'), { recursive: true });
  fs.writeFileSync(path.join(workspaceRoot, 'team/ptc/ptc_stage_registry.json'), JSON.stringify(registry));
  createTrainingRun(workspaceRoot, { runId: 'training-fixture', target });
  const calls = [];
  const options = { workspaceRoot, runId: 'training-fixture', testItems: ['TM109', 'TM110'], sourceRoles: ['dft-expert', 'schematic-expert'],
    dispatchStage: async (request) => { calls.push(`dispatch:${request.stage}`); return terminals(request); },
    runStageGate: async (request) => { calls.push(`gate:${request.stage}`); return passed(request); } };
  const progress = path.join(workspaceRoot, 'Training_Materials/runs/training-fixture/pipeline-progress.json');
  return { workspaceRoot, options, calls, progress };
}

test('whole-batch stage order uses registry owners and gates with run-local paths', async (t) => {
  const f = fixture(t);
  const controller = createTrainingPipeline({ ...f.options, dispatchStage: async (request) => {
    f.calls.push(`dispatch:${request.stage}`);
    assert.deepEqual(request.testItems, ['TM109', 'TM110']);
    assert.equal(request.owner, registry.stages[request.stage].owner);
    assert.equal(request.gate, registry.stages[request.stage].gate);
    assert.equal(request.mode, 'training');
    for (const directory of Object.values(request.addressBook)) assert.ok(directory.startsWith(path.join(f.workspaceRoot, 'Training_Materials/runs/training-fixture')));
    assert.equal(request.signal.aborted, false);
    return terminals(request);
  } });
  const result = await controller.start();
  assert.equal(result.status, 'completed');
  assert.deepEqual(f.calls, stages.flatMap((stage) => [`dispatch:${stage}`, `gate:${stage}`]));
  assert.equal(fs.existsSync(path.join(f.workspaceRoot, 'project')), false);
  const reopened = createTrainingPipeline(f.options);
  assert.equal((await reopened.start()).status, 'completed');
  assert.equal(f.calls.length, 6, 'completed stages are never redispatched');
});

test('source stage cannot gate or advance until every expected source role reports done for all TMs', async (t) => {
  for (const result of [
    { terminals: [{ role: 'dft-expert', status: 'done', testItems: ['TM109', 'TM110'] }] },
    { terminals: [{ role: 'dft-expert', status: 'done', testItems: ['TM109', 'TM110'] }, { role: 'schematic-expert', status: 'blocked', testItems: ['TM109', 'TM110'] }] },
    { terminals: [{ role: 'dft-expert', status: 'done', testItems: ['TM109'] }, { role: 'schematic-expert', status: 'done', testItems: ['TM109', 'TM110'] }] },
  ]) {
    const f = fixture(t);
    const controller = createTrainingPipeline({ ...f.options, dispatchStage: async () => result });
    assert.equal((await controller.start()).status, 'blocked');
    assert.deepEqual(f.calls, []);
    assert.equal((await controller.resume()).status, 'blocked', 'failed stage is not auto-retried');
  }
});

test('failed or wrong gate blocks at exact stage with no downstream dispatch', async (t) => {
  for (const result of [{ status: 'failed', exitCode: 1, gate: 'scripts/input.py' }, { status: 'passed', exitCode: 0, gate: 'scripts/other.py' }]) {
    const f = fixture(t);
    const controller = createTrainingPipeline({ ...f.options, runStageGate: async () => result });
    const final = await controller.start();
    assert.equal(final.status, 'blocked');
    assert.equal(final.stages[0].status, 'blocked');
    assert.equal(final.stages[1].status, 'pending');
    assert.deepEqual(f.calls, ['dispatch:INPUT_SYNC']);
  }
});

test('pause drains current dispatch and resumes at its gate without another dispatch', async (t) => {
  const f = fixture(t);
  const entered = deferred();
  const finish = deferred();
  const controller = createTrainingPipeline({ ...f.options, dispatchStage: async (request) => {
    f.calls.push(`dispatch:${request.stage}`);
    if (request.stage === 'INPUT_SYNC') { entered.resolve(); await finish.promise; }
    return terminals(request);
  } });
  const active = controller.start();
  await entered.promise;
  assert.equal(controller.pause().status, 'pausing');
  finish.resolve();
  assert.equal((await active).status, 'paused');
  assert.equal(controller.getState().stages[0].status, 'gate_pending');
  assert.deepEqual(f.calls, ['dispatch:INPUT_SYNC']);
  assert.equal((await controller.resume()).status, 'completed');
  assert.deepEqual(f.calls, stages.flatMap((stage) => [`dispatch:${stage}`, `gate:${stage}`]));
});

test('cancel aborts live work and ignores late model completion', async (t) => {
  const f = fixture(t);
  const entered = deferred();
  const finish = deferred();
  let signal;
  const controller = createTrainingPipeline({ ...f.options, dispatchStage: async (request) => {
    signal = request.signal; entered.resolve(); await finish.promise; return terminals(request);
  } });
  const active = controller.start();
  await entered.promise;
  assert.equal(controller.cancel().status, 'cancelled');
  assert.equal(signal.aborted, true);
  assert.equal((await active).status, 'cancelled');
  finish.resolve();
  await Promise.resolve();
  assert.equal(controller.getState().status, 'cancelled');
  assert.deepEqual(f.calls, []);
});

test('gate deadline aborts callback and leaves downstream pending', async (t) => {
  const f = fixture(t);
  let signal;
  const controller = createTrainingPipeline({ ...f.options, gateTimeoutMs: 15,
    runStageGate: async (request) => { signal = request.signal; return new Promise(() => {}); } });
  const final = await controller.start();
  assert.equal(final.status, 'blocked');
  assert.match(final.reason, /scripts\/input.py/);
  assert.equal(signal.aborted, true);
  assert.deepEqual(f.calls, ['dispatch:INPUT_SYNC']);
});

test('restart resumes persisted gate_pending without repeating completed source dispatch', async (t) => {
  const f = fixture(t);
  let controller;
  controller = createTrainingPipeline({ ...f.options, dispatchStage: async (request) => {
    f.calls.push(`dispatch:${request.stage}`); controller.pause(); return terminals(request);
  } });
  assert.equal((await controller.start()).status, 'paused');
  const reopened = createTrainingPipeline(f.options);
  assert.equal((await reopened.resume()).status, 'completed');
  assert.deepEqual(f.calls, stages.flatMap((stage) => [`dispatch:${stage}`, `gate:${stage}`]));
});

test('unknown interrupted dispatch requires recovery receipt and is never blindly sent again', async (t) => {
  for (const allowRecovery of [false, true]) {
    const f = fixture(t);
    createTrainingPipeline(f.options);
    const saved = JSON.parse(fs.readFileSync(f.progress, 'utf8'));
    saved.status = 'running'; saved.stages[0].status = 'dispatching';
    fs.writeFileSync(f.progress, JSON.stringify(saved));
    let recoveries = 0;
    const reopened = createTrainingPipeline({ ...f.options, recoverStage: allowRecovery ? async (request) => { recoveries += 1; return terminals(request); } : undefined });
    assert.equal(reopened.getState().status, 'interrupted');
    assert.equal((await reopened.resume()).status, allowRecovery ? 'completed' : 'blocked');
    assert.equal(f.calls.includes('dispatch:INPUT_SYNC'), false);
    assert.equal(recoveries, allowRecovery ? 1 : 0);
  }
});

test('resume pins registry snapshot and rejects changes to run identity or requested TM set', async (t) => {
  const f = fixture(t);
  const first = createTrainingPipeline(f.options);
  first.pause();
  fs.writeFileSync(path.join(f.workspaceRoot, 'team/ptc/ptc_stage_registry.json'), '{}');
  const reopened = createTrainingPipeline(f.options);
  assert.equal((await reopened.resume()).status, 'completed');
  assert.throws(() => createTrainingPipeline({ ...f.options, testItems: ['TM109'] }), /cannot change/);
  const contextFile = path.join(path.dirname(f.progress), 'run.json');
  const context = JSON.parse(fs.readFileSync(contextFile));
  context.mode = 'delivery';
  fs.writeFileSync(contextFile, JSON.stringify(context));
  assert.throws(() => createTrainingPipeline(f.options), /isolated training identity/);
});

test('source-only range stops after INPUT_SYNC gate and missing real adapters fail closed', async (t) => {
  const f = fixture(t, { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' });
  assert.throws(() => createTrainingPipeline({ ...f.options, runStageGate: undefined }), /adapters are required/);
  assert.throws(() => createTrainingPipeline({ ...f.options, sourceRoles: [] }), /source-role plan/);
  const controller = createTrainingPipeline(f.options);
  assert.equal((await controller.start()).status, 'completed');
  assert.deepEqual(f.calls, ['dispatch:INPUT_SYNC', 'gate:INPUT_SYNC']);
});

test('persisted completed status without gate evidence cannot skip a stage', (t) => {
  const f = fixture(t);
  createTrainingPipeline(f.options);
  const saved = JSON.parse(fs.readFileSync(f.progress, 'utf8'));
  saved.stages[0].status = 'completed';
  saved.stages[0].terminals = terminals({ expectedRoles: f.options.sourceRoles, testItems: f.options.testItems }).terminals;
  fs.writeFileSync(f.progress, JSON.stringify(saved));
  assert.throws(() => createTrainingPipeline(f.options), /missing passing gate evidence/);
});

test('stale second controller cannot overwrite persisted progress or dispatch twice', async (t) => {
  const f = fixture(t);
  const stale = createTrainingPipeline(f.options);
  const current = createTrainingPipeline(f.options);
  assert.equal((await current.start()).status, 'completed');
  await assert.rejects(stale.start(), /stale controller/);
  assert.deepEqual(f.calls, stages.flatMap((stage) => [`dispatch:${stage}`, `gate:${stage}`]));
  assert.equal(JSON.parse(fs.readFileSync(f.progress)).status, 'completed');
});
