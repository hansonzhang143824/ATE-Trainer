import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';
import { createSimpleOrchestration } from '../lib/simple-orchestration.js';

const names = ['INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD',
  'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION', 'COMPILE'];
const owners = ['captain', 'test-strategy-architect', 'test-method-expert', 'rule-reviewer',
  'ate-implementer', 'rule-reviewer', 'compile-diagnostician'];
const registry = { stateMachine: [...names, 'COMPLETE'], stages: Object.fromEntries(names.map((stage, i) =>
  [stage, { owner: owners[i], gate: `scripts/gate-${i}.py`, families: ['all'], outputs: [] }])) };
const roles = ['dft-expert', 'schematic-expert', ...new Set(owners.slice(1)), 'evolution-expert'];
const bindings = Object.fromEntries(roles.map(role => [role, {
  profileId: role === 'dft-expert' ? 'ptc-dft-expert' : role === 'schematic-expert' ? 'ptc-schematic-expert' : role,
  profileVersion: 'v1', profileDigest: crypto.createHash('sha256').update(role).digest('hex'),
}]));
function deferred() { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; }
function fixture(t, pilot = false) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-simple-orchestration-'));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  fs.mkdirSync(path.join(workspaceRoot, 'team/ptc'), { recursive: true });
  fs.writeFileSync(path.join(workspaceRoot, 'team/ptc/ptc_stage_registry.json'), JSON.stringify(registry));
  createTrainingRun(workspaceRoot, { runId: 'training-smoke',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: pilot ? 'INPUT_SYNC' : 'COMPILE' }, purpose: 'smoke-training' });
  const root = path.join(workspaceRoot, 'Training_Materials/runs/training-smoke');
  const calls = [];
  const executeSmokeRole = async request => {
    assert.equal(request.instruction, '1+2等于几，把答案写在JSON里');
    assert.equal(request.mode, 'SMOKE_ONLY');
    assert.equal(request.provisional, false);
    calls.push(`${request.stage}/${request.role}`);
    const executionKind = 'arithmetic-child';
    const childEvidencePath = path.join(root, `evidence-${request.stage}-${request.role}.json`);
    fs.writeFileSync(childEvidencePath, JSON.stringify({ runId: request.runId, dispatchId: request.dispatchId,
      stage: request.stage, role: request.role, executionKind, businessGatePassed: false,
      childSessionId: `session-${calls.length}`, answer: 3 }));
    return { status: 'done', executionKind, stage: request.stage, role: request.role,
      profileId: request.profileId, profileVersion: request.profileVersion, profileDigest: request.profileDigest,
      testItems: request.testItems, childReceiptId: `receipt-${calls.length}`,
      businessGatePassed: false,
      childEvidencePath, childEvidenceSha256: crypto.createHash('sha256').update(fs.readFileSync(childEvidencePath)).digest('hex') };
  };
  const options = { workspaceRoot, runId: 'training-smoke', testItems: ['TM109'], pilot,
    sourceRoles: ['dft-expert', 'schematic-expert'], profileBindings: pilot
      ? Object.fromEntries(['dft-expert', 'schematic-expert'].map(role => [role, bindings[role]])) : bindings, executeSmokeRole };
  return { workspaceRoot, root, calls, options, executeSmokeRole };
}

test('INPUT_SYNC pilot dispatches only DFT then schematic and verifies both numeric answers', async t => {
  const f = fixture(t, true);
  const state = await createSimpleOrchestration(f.options).start();
  assert.equal(state.scope, 'INPUT_SYNC_PILOT');
  assert.equal(state.status, 'completed');
  assert.equal(state.smokePassed, true);
  assert.equal(state.businessGatePassed, false);
  assert.deepEqual(f.calls, ['INPUT_SYNC/dft-expert', 'INPUT_SYNC/schematic-expert']);
  assert.deepEqual(state.stages.map(stage => stage.stage), ['INPUT_SYNC']);
  assert.deepEqual(state.stages[0].tasks.map(task => task.answer), [3, 3]);
  assert.deepEqual(state.auxiliaryTasks, []);
  assert.equal((await createSimpleOrchestration(f.options).start()).status, 'completed');
  assert.equal(f.calls.length, 2);
});

test('all seven registry stages dispatch real children in order but never claim business gates', async t => {
  const f = fixture(t);
  const state = await createSimpleOrchestration(f.options).start();
  assert.equal(state.status, 'completed');
  assert.equal(state.mode, 'SMOKE_ONLY');
  assert.equal(state.smokePassed, true);
  assert.equal(state.businessGatePassed, false);
  assert.deepEqual(state.stages.map(stage => stage.stage), names);
  assert.deepEqual(f.calls, [...names.flatMap((stage, i) =>
    (i === 0 ? ['dft-expert', 'schematic-expert'] : [owners[i]]).map(role => `${stage}/${role}`)),
    'SMOKE_AUXILIARY/evolution-expert']);
  assert.equal(state.stages[0].tasks[1].provisional, false);
  assert.ok(state.stages.every(stage => stage.smokePassed && stage.businessGatePassed === false && stage.businessGateResult === null));
  assert.ok(state.stages.every(stage => stage.tasks.every(task => /^[a-f0-9]{64}$/.test(task.childEvidenceSha256))));
  assert.ok(state.stages.every(stage => stage.tasks.every(task => task.captainVerified && task.answer === 3)));
  assert.equal(state.auxiliaryTasks[0].captainVerified, true);
  const displayed = JSON.parse(fs.readFileSync(path.join(f.root, 'state.json')));
  assert.equal(displayed.status, 'completed');
  assert.equal(displayed.outcome.mode, 'SMOKE_ONLY');
  assert.equal(displayed.outcome.businessGatePassed, false);
  const reopened = createSimpleOrchestration(f.options);
  assert.equal((await reopened.start()).status, 'completed');
  assert.equal(f.calls.length, 9, 'terminal smoke chain must not redispatch');
});

test('pause drains one child and resume dispatches the next without duplicate', async t => {
  const f = fixture(t);
  const entered = deferred(); const finish = deferred();
  const controller = createSimpleOrchestration({ ...f.options, executeSmokeRole: async request => {
    if (request.role === 'dft-expert') { entered.resolve(); await finish.promise; }
    return f.executeSmokeRole(request);
  } });
  const running = controller.start(); await entered.promise;
  assert.equal(controller.pause().status, 'pausing');
  finish.resolve();
  assert.equal((await running).status, 'paused');
  assert.deepEqual(f.calls, ['INPUT_SYNC/dft-expert']);
  assert.equal((await controller.resume()).status, 'completed');
  assert.equal(f.calls.filter(call => call === 'INPUT_SYNC/dft-expert').length, 1);
});

test('failed child blocks exact task and does not dispatch downstream', async t => {
  const f = fixture(t);
  const controller = createSimpleOrchestration({ ...f.options, executeSmokeRole: async request => {
    f.calls.push(`${request.stage}/${request.role}`);
    return { status: 'done', sentence: '完成。' }; // No real-child receipt or evidence.
  } });
  const state = await controller.start();
  assert.equal(state.status, 'blocked');
  assert.equal(state.stages[0].tasks[0].status, 'blocked');
  assert.ok(state.stages.slice(1).every(stage => stage.status === 'pending'));
  assert.equal(f.calls.length, 1);
});

test('restart does not resend an uncertain child without explicit receipt recovery', async t => {
  const f = fixture(t);
  createSimpleOrchestration(f.options);
  const file = path.join(f.root, 'simple-orchestration.json');
  const state = JSON.parse(fs.readFileSync(file));
  state.status = 'running'; state.stages[0].status = 'running'; state.stages[0].tasks[0].status = 'dispatching';
  fs.writeFileSync(file, JSON.stringify(state));
  const reopened = createSimpleOrchestration(f.options);
  assert.equal(reopened.getState().status, 'interrupted');
  const result = await reopened.start();
  assert.equal(result.status, 'blocked');
  assert.match(result.reason, /receipt recovery required/);
  assert.deepEqual(f.calls, []);
});

test('profile version and registry snapshot are fixed across resume', t => {
  const f = fixture(t);
  createSimpleOrchestration(f.options);
  assert.throws(() => createSimpleOrchestration({ ...f.options,
    profileBindings: { ...bindings, 'dft-expert': { ...bindings['dft-expert'], profileVersion: 'v2' } } }), /profile versions changed/);
  fs.writeFileSync(path.join(f.root, 'simple-orchestration-registry.json'), '{}');
  assert.throws(() => createSimpleOrchestration(f.options), /registry|binding/);
});

test('stop aborts active child and ignores a late completion', async t => {
  const f = fixture(t);
  const entered = deferred(); const finish = deferred();
  let signal;
  const controller = createSimpleOrchestration({ ...f.options, executeSmokeRole: async request => {
    signal = request.signal; entered.resolve(); await finish.promise; return f.executeSmokeRole(request);
  } });
  const running = controller.start(); await entered.promise;
  assert.equal(controller.cancel().status, 'cancelled');
  assert.equal(signal.aborted, true);
  assert.equal((await running).status, 'cancelled');
  finish.resolve(); await Promise.resolve();
  assert.equal(controller.getState().status, 'cancelled');
  assert.equal(controller.getState().stages[0].tasks[0].status, 'cancelled');
});

test('Captain rejects a child-reported PASS when its actual JSON answer is a string', async t => {
  const f = fixture(t);
  const state = await createSimpleOrchestration({ ...f.options, executeSmokeRole: async request => {
    const result = await f.executeSmokeRole(request);
    if (request.stage === 'STRATEGY') {
      const evidence = JSON.parse(fs.readFileSync(result.childEvidencePath));
      fs.writeFileSync(result.childEvidencePath, JSON.stringify({ ...evidence, answer: '3', smokePassed: true }));
      result.childEvidenceSha256 = crypto.createHash('sha256').update(fs.readFileSync(result.childEvidencePath)).digest('hex');
    }
    return result;
  } }).start();
  assert.equal(state.status, 'blocked');
  assert.match(state.reason, /numeric 3/);
  assert.equal(state.stages[0].status, 'completed');
  assert.equal(state.stages[1].status, 'blocked');
  assert.ok(state.stages.slice(2).every(stage => stage.status === 'pending'));
});

test('a historical single-agent answer cannot be reused as this dispatch evidence', async t => {
  const f = fixture(t);
  const state = await createSimpleOrchestration({ ...f.options, executeSmokeRole: async request => {
    const result = await f.executeSmokeRole(request);
    if (request.stage === 'STRATEGY') {
      const evidence = JSON.parse(fs.readFileSync(result.childEvidencePath));
      fs.writeFileSync(result.childEvidencePath, JSON.stringify({ ...evidence,
        runId: 'historical-profile-run', dispatchId: 'historical-dispatch' }));
      result.childEvidenceSha256 = crypto.createHash('sha256').update(fs.readFileSync(result.childEvidencePath)).digest('hex');
    }
    return result;
  } }).start();
  assert.equal(state.status, 'blocked');
  assert.match(state.reason, /exact dispatch/);
});

test('an unpublished profile binds the exact frozen draft snapshot, not a published version', t => {
  const f = fixture(t);
  const sourceId = 'training-candidate-1';
  const relative = `Training_Materials/runs/${sourceId}/profile/snapshot.json`;
  const file = path.join(f.workspaceRoot, relative);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify({ kind: 'ptc-profile-smoke-snapshot', runId: sourceId,
    profileId: 'strategy-expert', files: [] }));
  const profileDigest = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  const draft = { ...bindings, 'test-strategy-architect': { profileId: 'strategy-expert',
    profileVersion: `draft-${sourceId}`, profileDigest, profileSnapshotPath: relative } };
  const controller = createSimpleOrchestration({ ...f.options, profileBindings: draft });
  assert.equal(controller.getState().profileBindings['test-strategy-architect'].profileVersion, `draft-${sourceId}`);
  fs.writeFileSync(file, '{"tampered":true}');
  assert.throws(() => createSimpleOrchestration({ ...f.options, profileBindings: draft }), /draft profile digest/);
});

test('DFT arithmetic smoke draft binds the frozen profile snapshot', t => {
  const f = fixture(t);
  const sourceId = 'training-dft-candidate';
  const relative = `Training_Materials/runs/${sourceId}/profile/snapshot.json`;
  const file = path.join(f.workspaceRoot, relative);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify({ kind: 'ptc-profile-smoke-snapshot',
    runId: sourceId, profileId: 'ptc-dft-expert', files: [] }));
  const profileDigest = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  const draft = { ...bindings, 'dft-expert': { profileId: 'ptc-dft-expert',
    profileVersion: `draft-${sourceId}`, profileDigest, profileSnapshotPath: relative } };
  assert.equal(createSimpleOrchestration({ ...f.options, profileBindings: draft })
    .getState().profileBindings['dft-expert'].profileDigest, profileDigest);
});
