import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRunContext, persistRunContext } from '../lib/run-context.js';
import { createArithmeticRoleDispatcher } from '../lib/arithmetic-role-dispatch.js';

const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function fixture({ stage = 'STRATEGY', role = 'test-strategy-architect',
  profileId = 'strategy-expert', owner = role,
  registryGate = stage === 'STRATEGY' ? 'scripts/validate_strategy_contract.py' : null } = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-arithmetic-role-'));
  const runId = 'training-pipeline-smoke-1';
  const context = createRunContext(root, { mode: 'training', runId });
  persistRunContext(root, context);
  const runRoot = path.join(root, context.artifactRoot);
  fs.writeFileSync(path.join(runRoot, 'state.json'), `${JSON.stringify({ runId,
    purpose: 'smoke-training', target: { kind: 'pipeline' }, status: 'running' })}\n`);
  const registryFile = path.join(runRoot, 'simple-orchestration-registry.json');
  fs.writeFileSync(registryFile, '{"frozen":true}\n');
  const registryDigest = sha(fs.readFileSync(registryFile));
  const request = { runId, mode: 'SMOKE_ONLY', stage, owner,
    registryGate, role,
    profileId, profileVersion: 'draft-training-profile-1',
    profileDigest: 'a'.repeat(64), testItems: ['TM109'],
    dispatchId: `${runId}:${stage}:${role}:1`, runRoot,
    registryDigest, instruction: '1+2等于几，把答案写在JSON里', provisional: false };
  fs.writeFileSync(path.join(runRoot, 'simple-orchestration.json'), `${JSON.stringify({
    runId, mode: 'SMOKE_ONLY', registryDigest, testItems: ['TM109'],
    stages: stage === 'SMOKE_AUXILIARY' ? [] : [{ stage, owner: request.owner, gate: request.registryGate,
      tasks: [{ dispatchId: request.dispatchId, status: 'dispatching', role: request.role, profileId: request.profileId,
        profileVersion: request.profileVersion, profileDigest: request.profileDigest }] }],
    auxiliaryTasks: stage === 'SMOKE_AUXILIARY' ? [{ dispatchId: request.dispatchId, status: 'dispatching',
      role: request.role, profileId: request.profileId,
      profileVersion: request.profileVersion, profileDigest: request.profileDigest }] : [],
  })}\n`);
  return { root, runRoot, request, cleanup: () => fs.rmSync(root, { recursive: true, force: true }) };
}

function context(answer = 3, inspect = () => {}) {
  return {
    agentDefaultModel: { currentSelection: () => ({ provider: 'fake', model: 'fake' }) },
    agents: { create: async () => ({ agent: { whenIdle: async () => {} }, dispose: async () => {} }) },
    subagents: { start: async (_kind, request) => {
      inspect(request);
      return { id: 'session-real-child-1', result: Promise.resolve({ stopReason: 'completed',
        structured: { answer } }), dispose: async () => {} };
    } },
  };
}

test('real child numeric answer 3 creates current-run bound arithmetic evidence', async () => {
  const f = fixture();
  try {
    let started = false;
    const dispatcher = createArithmeticRoleDispatcher(context(3, request => {
      started = true;
      assert.equal(request.prompt[0].text, '1+2等于几，把答案写在JSON里');
      assert.deepEqual(request.toolFilter.allow, []);
      assert.ok(!JSON.stringify(request).includes('Dali_testmode'));
    }), f.root);
    const result = await dispatcher.executeSmokeRole(f.request);
    assert.equal(started, true);
    assert.equal(result.status, 'done');
    assert.equal(result.executionKind, 'arithmetic-child');
    assert.equal(result.businessGatePassed, false);
    assert.equal(result.childEvidenceSha256, sha(fs.readFileSync(result.childEvidencePath)));
    const evidence = JSON.parse(fs.readFileSync(result.childEvidencePath, 'utf8'));
    assert.equal(evidence.dispatchId, f.request.dispatchId);
    assert.equal(evidence.childSessionId, 'session-real-child-1');
    assert.equal(evidence.answer, 3);
    assert.equal(evidence.mode, 'SMOKE_ONLY');
    assert.equal(evidence.businessGatePassed, false);
    assert.equal(evidence.responseSha256, sha(fs.readFileSync(path.join(f.runRoot, 'evidence', 'roles', 'STRATEGY-test-strategy-architect-child.json'))));
  } finally { f.cleanup(); }
});

test('string 3 and wrong answers never produce successful arithmetic evidence', async () => {
  for (const answer of ['3', 4]) {
    const f = fixture();
    try {
      const dispatcher = createArithmeticRoleDispatcher(context(answer), f.root);
      await assert.rejects(dispatcher.executeSmokeRole(f.request), /numeric JSON answer 3/);
      const evidence = JSON.parse(fs.readFileSync(path.join(f.runRoot, 'evidence', 'roles', 'STRATEGY-test-strategy-architect.json'), 'utf8'));
      assert.equal(evidence.status, 'blocked');
      assert.equal(evidence.answer, null);
      assert.equal(evidence.businessGatePassed, false);
      assert.match(evidence.responseSha256, /^[a-f0-9]{64}$/);
    } finally { f.cleanup(); }
  }
});

test('pre-aborted request cannot start a child', async () => {
  const f = fixture();
  try {
    let spawned = false;
    const ctx = context();
    ctx.subagents.start = async () => { spawned = true; throw new Error('unexpected child'); };
    const controller = new AbortController(); controller.abort(new Error('user stopped'));
    const dispatcher = createArithmeticRoleDispatcher(ctx, f.root);
    await assert.rejects(dispatcher.executeSmokeRole({ ...f.request, signal: controller.signal }), /user stopped/);
    assert.equal(spawned, false);
  } finally { f.cleanup(); }
});

test('profile binding mismatch is rejected before external model launch', async () => {
  const f = fixture();
  try {
    let spawned = false;
    const ctx = context();
    ctx.subagents.start = async () => { spawned = true; throw new Error('unexpected child'); };
    const dispatcher = createArithmeticRoleDispatcher(ctx, f.root);
    await assert.rejects(dispatcher.executeSmokeRole({ ...f.request, profileDigest: 'b'.repeat(64) }), /binding differs/);
    assert.equal(spawned, false);
  } finally { f.cleanup(); }
});

test('auxiliary evolution profile gets its own current-run child evidence', async () => {
  const f = fixture({ stage: 'SMOKE_AUXILIARY', role: 'evolution-expert',
    profileId: 'evolution-expert', owner: null, registryGate: null });
  try {
    const dispatcher = createArithmeticRoleDispatcher(context(), f.root);
    const result = await dispatcher.executeSmokeRole(f.request);
    const evidence = JSON.parse(fs.readFileSync(result.childEvidencePath, 'utf8'));
    assert.equal(evidence.stage, 'SMOKE_AUXILIARY');
    assert.equal(evidence.role, 'evolution-expert');
    assert.equal(evidence.answer, 3);
    assert.equal(result.childEvidenceSha256, sha(fs.readFileSync(result.childEvidencePath)));
  } finally { f.cleanup(); }
});

test('INPUT_SYNC DFT and schematic each dispatch the same arithmetic child with no business gate', async () => {
  for (const [role, profileId] of [
    ['dft-expert', 'ptc-dft-expert'], ['schematic-expert', 'ptc-schematic-expert'],
  ]) {
    const f = fixture({ stage: 'INPUT_SYNC', role, profileId,
      owner: 'captain', registryGate: 'scripts/prepare_input_sync_v2.py' });
    try {
      let prompt;
      const dispatcher = createArithmeticRoleDispatcher(context(3, request => { prompt = request.prompt[0].text; }), f.root);
      const result = await dispatcher.executeSmokeRole(f.request);
      const evidence = JSON.parse(fs.readFileSync(result.childEvidencePath, 'utf8'));
      assert.equal(prompt, '1+2等于几，把答案写在JSON里');
      assert.equal(evidence.stage, 'INPUT_SYNC');
      assert.equal(evidence.profileId, profileId);
      assert.equal(evidence.answer, 3);
      assert.equal(evidence.businessGatePassed, false);
    } finally { f.cleanup(); }
  }
});

test('in-flight AbortSignal cancels child and records a blocked receipt', async () => {
  const f = fixture();
  try {
    const controller = new AbortController();
    let started;
    const didStart = new Promise(resolve => { started = resolve; });
    const ctx = context();
    ctx.subagents.start = async () => {
      started();
      return { id: 'session-stalled-child', result: new Promise(() => {}), dispose: async () => {} };
    };
    const dispatcher = createArithmeticRoleDispatcher(ctx, f.root, { timeoutMs: 2000 });
    const completion = dispatcher.executeSmokeRole({ ...f.request, signal: controller.signal });
    await didStart;
    controller.abort(new Error('user stopped orchestration'));
    await assert.rejects(completion, /user stopped orchestration/);
    const evidence = JSON.parse(fs.readFileSync(path.join(f.runRoot, 'evidence', 'roles',
      'STRATEGY-test-strategy-architect.json'), 'utf8'));
    assert.equal(evidence.status, 'blocked');
    // Cancellation can win the race before the host binds the returned child
    // identity; it must not invent a settled session ID in that case.
    assert.equal(evidence.childSessionId, null);
    assert.equal(evidence.businessGatePassed, false);
  } finally { f.cleanup(); }
});
