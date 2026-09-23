import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import test from 'node:test';
import { setTimeout as delay } from 'node:timers/promises';
import { createPipelineDispatcher } from '../lib/pipeline-dispatch.js';
import { signStageReceipt } from '../lib/pipeline-guard.js';

const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const json = file => JSON.parse(fs.readFileSync(file, 'utf8'));
function write(file, data) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, JSON.stringify(data)); }
function deferred() { let resolve; const promise = new Promise(yes => { resolve = yes; }); return { promise, resolve }; }

function fixture(stage = 'STRATEGY') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-pipeline-dispatch-'));
  const runId = 'training-pipeline-fixture';
  const runRelative = `Training_Materials/runs/${runId}`;
  const runRoot = path.join(root, runRelative);
  const role = stage === 'INPUT_SYNC' ? 'schematic-expert' : 'test-strategy-architect';
  const profileId = stage === 'INPUT_SYNC' ? 'ptc-schematic-expert' : 'test-strategy-architect';
  const profileRoot = `${runRelative}/profiles/${profileId}`;
  const instructionsFile = path.join(root, profileRoot, 'instructions.md');
  fs.mkdirSync(path.dirname(instructionsFile), { recursive: true });
  fs.writeFileSync(instructionsFile, 'Frozen expert instructions\r\n');
  const gate = stage === 'INPUT_SYNC' ? 'scripts/prepare_input_sync_v2.py' : 'scripts/validate_strategy_contract.py';
  const registry = { stateMachine: ['INPUT_SYNC', 'STRATEGY'], stages: {
    INPUT_SYNC: { owner: 'captain', gate: 'scripts/prepare_input_sync_v2.py', outputs: ['input-manifest.json'] },
    STRATEGY: { owner: 'test-strategy-architect', gate: 'scripts/validate_strategy_contract.py', outputs: ['strategy/deliverable-ready.json'] },
  } };
  write(path.join(runRoot, 'pipeline-registry.json'), registry);
  write(path.join(runRoot, 'run.json'), { runId, mode: 'training', releaseId: null });
  const addressBook = { profileRoots: { [profileId]: profileRoot }, input: { schematic: `${runRelative}/input/Dali-SCH.csv` },
    schematicRoot: `${runRelative}/input-sync/schematic`, trials: { TM109: `${runRelative}/trials/tm109`, TM110: `${runRelative}/trials/tm110` },
    registerRoot: `${runRelative}/register`, knowledgeRoot: `${runRelative}/knowledge`, programSourceRoot: `${runRelative}/vs-project/source` };
  const manifest = { schemaVersion: 1, kind: 'ptc-pipeline-materials', runId, testItems: ['TM109', 'TM110'], pipelineCacheKey: 'a'.repeat(64),
    ownerProfiles: { [role]: profileId }, addressBook,
    files: [{ snapshotPath: `${profileRoot}/instructions.md`, sha256: sha(fs.readFileSync(instructionsFile)), view: 'python-plaintext' }] };
  write(path.join(runRoot, 'pipeline-material-manifest.json'), manifest);
  const materials = { runId, testItems: [...manifest.testItems], ...addressBook, pipelineCacheKey: manifest.pipelineCacheKey, ownerProfiles: manifest.ownerProfiles };
  const request = { runId, stage, owner: role, gate, registryDigest: sha(fs.readFileSync(path.join(runRoot, 'pipeline-registry.json'))), testItems: stage === 'INPUT_SYNC' ? [...manifest.testItems] : ['TM109'] };
  return { root, runRoot, request, materials, instructionsFile, receipt: path.join(runRoot, 'receipts', `${stage}-${role}.json`), terminal: path.join(runRoot, 'receipts', `${stage}-${role}-terminal.json`) };
}

function context(result = { stopReason: 'completed', structured: { status: 'done', outputs: ['strategy/deliverable-ready.json'] } }) {
  const observed = { created: 0, started: 0, disposed: 0 };
  const ctx = {
    agentDefaultModel: { currentSelection: () => ({ provider: 'fixture', model: 'test-model' }) },
    agentPresets: { async mount(_ctx, preset) { observed.preset = preset; } },
    agents: { async create(options) { observed.created += 1; observed.create = options; await options.setup({}); return { agent: { async whenIdle() {} }, dispose() { observed.disposed += 1; } }; } },
    subagents: { async start(provider, options) { observed.started += 1; observed.provider = provider; observed.child = options;
      return { id: 'fixture-child', result: Promise.resolve(result), dispose() { observed.disposed += 1; } }; } },
  };
  return { ctx, observed };
}

test('pipeline dispatcher binds frozen registry/profile and reports only an observed real child terminal', async () => {
  const f = fixture(); const { ctx, observed } = context();
  const terminal = await createPipelineDispatcher(ctx, f.root).dispatch(f.request, f.materials);
  assert.equal(terminal.status, 'done');
  assert.equal(terminal.kind, 'ptc-training-stage-terminal');
  assert.equal(terminal.childSessionId, 'fixture-child');
  assert.equal(terminal.registryDigest, f.request.registryDigest);
  assert.equal(observed.preset, 'ate-ptc');
  assert.equal(observed.provider, 'spawn');
  assert.deepEqual(observed.child.toolFilter, { allow: ['read', 'write'] });
  assert.match(observed.child.persona, /Frozen expert instructions/);
  assert.match(observed.child.persona, /host independently executes the registry gate/i);
  assert.equal(terminal.gateResult, undefined);
  assert.equal(json(f.receipt).executionStatus, 'closed');
  assert.equal(json(f.terminal).digest, signStageReceipt(json(f.terminal)).digest);
});

test('pipeline dispatcher refuses changed owner, gate, registry, mode, profile bytes and unassigned TMs before model creation', async () => {
  const cases = [
    f => { f.request.owner = 'other-expert'; },
    f => { f.request.gate = 'different-gate'; },
    f => { f.request.registryDigest = '0'.repeat(64); },
    f => { f.request.runId = '../outside'; },
    f => { f.request.testItems = ['TM999']; },
    f => { f.request.testItems = ['TM109', 'TM109']; },
    f => { f.materials.testItems = ['TM999']; },
    f => { f.materials.ownerProfiles = { ...f.materials.ownerProfiles, [f.request.owner]: 'different-profile' }; },
    f => { f.materials.profileRoots = { ...f.materials.profileRoots, [f.request.owner]: 'team/expert-profiles/live' }; },
    f => { f.materials.pipelineCacheKey = 'b'.repeat(64); },
    f => { fs.appendFileSync(f.instructionsFile, 'tampered'); },
    f => { write(path.join(f.runRoot, 'run.json'), { runId: f.request.runId, mode: 'delivery', releaseId: 'r1' }); },
  ];
  for (const change of cases) {
    const f = fixture(); const { ctx, observed } = context(); change(f);
    await assert.rejects(createPipelineDispatcher(ctx, f.root).dispatch(f.request, f.materials));
    assert.equal(observed.created, 0);
    assert.equal(observed.started, 0);
    assert.equal(fs.existsSync(f.receipt), false);
  }
});

test('only completed plus structured done can produce done; blocked, truncated and provider errors do not pass', async () => {
  for (const result of [undefined, { stopReason: 'timeout', structured: { status: 'done' } }, { stopReason: 'completed' },
    { stopReason: 'completed', structured: { status: 'blocked', reason: 'source conflict' } }, { stopReason: 'max_steps', structured: { status: 'done' } }]) {
    const f = fixture(); const { ctx } = context(null);
    ctx.subagents.start = async () => ({ id: 'fixture-child', result: Promise.resolve(result), dispose() {} });
    const terminal = await createPipelineDispatcher(ctx, f.root).dispatch(f.request, f.materials);
    assert.equal(terminal.status, 'blocked');
  }
  const f = fixture(); const { ctx } = context();
  ctx.subagents.start = async () => ({ id: 'fixture-child', result: Promise.reject(new Error('provider failed')), dispose() {} });
  assert.equal((await createPipelineDispatcher(ctx, f.root).dispatch(f.request, f.materials)).status, 'blocked');
});

test('abort during startup closes receipt, returns blocked promptly and disposes late parent without starting child', async () => {
  const f = fixture(); const { ctx, observed } = context();
  const pending = deferred(); const started = deferred(); const controller = new AbortController();
  ctx.agents.create = () => { started.resolve(); return pending.promise; };
  const dispatcher = createPipelineDispatcher(ctx, f.root);
  const execution = dispatcher.dispatch({ ...f.request, signal: controller.signal }, f.materials);
  await started.promise; controller.abort('user stopped startup');
  const terminal = await execution;
  assert.equal(terminal.status, 'blocked');
  assert.equal(terminal.stopReason, 'aborted');
  assert.equal(terminal.childSessionId, null);
  assert.equal(json(f.receipt).executionStatus, 'closed');
  let disposed = false;
  pending.resolve({ agent: { async whenIdle() {} }, dispose() { disposed = true; } });
  await delay(0);
  assert.equal(disposed, true);
  assert.equal(observed.started, 0);
});

test('an already-aborted request never creates a model and its blocked receipt is recoverable', async () => {
  const f = fixture(); const { ctx, observed } = context(); const controller = new AbortController(); controller.abort('already stopped');
  const dispatcher = createPipelineDispatcher(ctx, f.root);
  const terminal = await dispatcher.dispatch({ ...f.request, signal: controller.signal }, f.materials);
  assert.equal(terminal.status, 'blocked');
  assert.equal(observed.created, 0);
  assert.equal(dispatcher.recover(f.request).status, 'blocked');
});

test('deadline includes hung startup and does not claim underlying termination', async () => {
  const f = fixture(); const { ctx } = context(); ctx.agents.create = () => new Promise(() => {});
  const dispatcher = createPipelineDispatcher(ctx, f.root, { timeoutMs: 10 });
  const [terminal] = await Promise.all([dispatcher.dispatch(f.request, f.materials), delay(40)]);
  assert.equal(terminal.status, 'blocked');
  assert.equal(terminal.stopReason, 'timeout');
  const lifecycle = json(path.join(f.runRoot, 'evidence', `${f.request.stage}-${f.request.owner}-lifecycle.json`));
  assert.equal(lifecycle.childSettlement, 'unknown');
  assert.equal(lifecycle.cancellationRequested, true);
});

test('recovery validates original dispatch and child bindings without repeating dispatch', async () => {
  const f = fixture(); const { ctx, observed } = context();
  const first = createPipelineDispatcher(ctx, f.root);
  await first.dispatch(f.request, f.materials);
  const restored = createPipelineDispatcher(ctx, f.root);
  assert.equal(restored.recover(f.request).status, 'done');
  await assert.rejects(restored.dispatch(f.request, f.materials), /already exists/);
  assert.equal(observed.started, 1);
  const terminal = json(f.terminal);
  write(f.terminal, signStageReceipt({ ...terminal, childSessionId: 'different-child' }));
  assert.throws(() => restored.recover(f.request), /unbound/);
  write(f.terminal, terminal);
  const receipt = json(f.receipt);
  write(f.receipt, signStageReceipt({ ...receipt, executionStatus: 'running' }));
  assert.throws(() => restored.recover(f.request), /unbound/);
});

test('parallel attempts for the same receipt cannot launch a second child', async () => {
  const f = fixture(); const { ctx, observed } = context(); const pending = deferred(); const started = deferred();
  ctx.subagents.start = async () => { observed.started += 1; started.resolve(); return { id: 'child', result: pending.promise, dispose() {} }; };
  const dispatcher = createPipelineDispatcher(ctx, f.root);
  const execution = dispatcher.dispatch(f.request, f.materials);
  await started.promise;
  await assert.rejects(dispatcher.dispatch(f.request, f.materials), /already exists/);
  pending.resolve({ stopReason: 'completed', structured: { status: 'done' } });
  await execution;
  assert.equal(observed.started, 1);
});

test('initial receipt reservation rejects an exists-check race instead of replacing the winning receipt', async () => {
  const f = fixture(); const { ctx, observed } = context();
  const original = fs.writeFileSync;
  let reserved;
  fs.writeFileSync = (file, data, options) => {
    if (path.resolve(file) === f.receipt && options?.flag === 'wx') {
      reserved = '{"otherDispatcher":"already reserved"}';
      original(file, reserved, { flag: 'wx' });
    }
    return original(file, data, options);
  };
  try { await assert.rejects(createPipelineDispatcher(ctx, f.root).dispatch(f.request, f.materials), /already exists/); }
  finally { fs.writeFileSync = original; }
  assert.equal(fs.readFileSync(f.receipt, 'utf8'), reserved);
  assert.equal(observed.created, 0);
});

test('only the schematic INPUT_SYNC exception gets a read-only source review child for all TMs', async () => {
  const f = fixture('INPUT_SYNC'); const { ctx, observed } = context();
  const terminal = await createPipelineDispatcher(ctx, f.root).dispatch(f.request, f.materials);
  assert.equal(terminal.status, 'done');
  assert.deepEqual(observed.child.toolFilter, { allow: ['read'] });
  assert.match(observed.child.prompt[0].text, /seven schematic products/);
  assert.match(observed.child.prompt[0].text, /do not run a gate yourself/);
  assert.match(observed.child.prompt[0].text, /TM109, TM110/);
  assert.match(observed.child.prompt[0].text, /input-sync\/schematic/);
  for (const change of [f => { f.request.testItems = ['TM109']; }, f => { f.request.owner = 'dft-expert'; }, f => { f.request.owner = 'captain'; }]) {
    const rejected = fixture('INPUT_SYNC'); const model = context(); change(rejected);
    await assert.rejects(createPipelineDispatcher(model.ctx, rejected.root).dispatch(rejected.request, rejected.materials));
    assert.equal(model.observed.started, 0);
  }
});
