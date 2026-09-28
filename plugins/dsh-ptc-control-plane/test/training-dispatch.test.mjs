import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { setTimeout as delay } from 'node:timers/promises';
import { createTrainingDispatcher, TRAINING_DEADLINE_MS } from '../lib/training-dispatch.js';
import { verifyTrainingReceipt, trainingGuardDecision } from '../lib/training-guard.js';
import { trainingAddressBook } from '../lib/training-paths.js';

function fixture(runId) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-dispatch-'));
  const materials = { runId, testItems: ['TM109'], ...trainingAddressBook(runId), cacheCompatible: false, cacheKey: 'a'.repeat(64) };
  const sourceView = { status: 'SOURCE_VIEW', runId, path: materials.sourceView, sha256: 'b'.repeat(64),
    sourceSha256: 'c'.repeat(64), testItems: ['TM109'], reused: false, bytes: 1 };
  const runDirectory = path.join(root, materials.runRoot);
  const reviewInput = { schemaVersion: 1, runId, sourceSha256: 'c'.repeat(64), items: [{
    tm: 'TM109', mode: 'OVERWRITTEN', sourceSha256: 'c'.repeat(64),
    producerDigests: { 'dft-meta.json': 'd'.repeat(64), 'dft-conditions.yaml': 'e'.repeat(64) },
    sourceEvidence: { tm: 'TM109' }, metaProjection: { tm: 'TM109' }, conditionsProjection: { tm: 'TM109' },
  }] };
  const reviewInputFile = path.join(runDirectory, 'evidence', 'dft-review-input.json');
  fs.mkdirSync(path.join(root, materials.profileRoot), { recursive: true });
  fs.writeFileSync(path.join(root, materials.instructions), 'FROZEN DFT INSTRUCTIONS');
  fs.mkdirSync(path.dirname(reviewInputFile), { recursive: true });
  fs.writeFileSync(reviewInputFile, `${JSON.stringify(reviewInput, null, 2)}\n`);
  return { root, materials, sourceView, reviewInput, reviewInputFile, runDirectory,
    input: { runId, testItems: ['TM109'], reports: [], sourceView, reviewInput, reviewInputFile, runDirectory, materials } };
}

function mockContext(overrides = {}) {
  return {
    agentDefaultModel: { currentSelection: () => ({ provider: 'test', model: 'test' }) },
    agentPresets: { async mount() {} },
    agents: { async create() { return { agent: { async whenIdle() {} }, async dispose() {} }; } },
    subagents: { getProvider: () => ({}), async start() { return { id: 'child', result: new Promise(() => {}), async dispose() {} }; } },
    ...overrides,
  };
}

function deferred() {
  let resolve;
  const promise = new Promise((yes) => { resolve = yes; });
  return { promise, resolve };
}

test('training child has a local 2048 response budget without changing default model selection', async () => {
  const setup = fixture('training-budget'); let selected;
  const ctx = mockContext({ subagents: { getProvider: () => ({}), async start(_name, request) {
    selected = request.agentOptions;
    return { id: 'budget-child', result: Promise.resolve({ stopReason: 'completed', structured: { status: 'done' } }), dispose() {} };
  } } });
  const dispatcher = createTrainingDispatcher(ctx, setup.root);
  const run = await dispatcher.dispatch(setup.input); await run.result;
  assert.equal(selected.maxTokens, 2048);
  assert.deepEqual(ctx.agentDefaultModel.currentSelection(), { provider: 'test', model: 'test' });
});

test('selected DeepSeek business reviewer receives a bounded structured-response budget', async () => {
  const setup = fixture('training-deepseek-budget'); let selected; let prompt;
  const ctx = mockContext({
    agentDefaultModel: { currentSelection: () => ({ provider: 'zai-coding-cn', model: 'glm-5.3-flash' }) },
    subagents: { getProvider: () => ({}), async start(_name, request) {
      selected = request.agentOptions;
      prompt = `${request.persona}\n${request.prompt[0].text}`;
      return { id: 'deepseek-child', result: Promise.resolve({ stopReason: 'completed', structured: { status: 'done' } }), dispose() {} };
    } },
  });
  const dispatcher = createTrainingDispatcher(ctx, setup.root);
  const run = await dispatcher.dispatch({ ...setup.input, modelChoice: 'deepseek-v4-flash' }); await run.result;
  assert.equal(selected.maxTokens, 8192);
  assert.match(prompt, /call structured_output as your next action/i);
  assert.match(prompt, /each finding <=240 characters/i);
});

test('semantic review has a 60-second-class deadline independent of the total lifecycle', async () => {
  const setup = fixture('training-no-progress');
  const dispatcher = createTrainingDispatcher(mockContext(), setup.root, { timeoutMs: 1000, progressTimeoutMs: 20 });
  const run = await dispatcher.dispatch(setup.input);
  const result = await run.result;
  assert.equal(result.stopReason, 'timeout');
  assert.match(result.structured.question, /semantic review did not finish/);
  assert.equal(JSON.parse(fs.readFileSync(run.receiptFile, 'utf8')).executionStatus, 'closed');
});

test('semantic-review child cannot start material tools', async () => {
  const setup = fixture('training-material-progress');
  const dispatcher = createTrainingDispatcher(mockContext(), setup.root, { timeoutMs: 1000, progressTimeoutMs: 100 });
  const run = await dispatcher.dispatch(setup.input);
  dispatcher.noteToolStart({ name: 'read', agent: { id: 'unrelated' } });
  dispatcher.noteToolStart({ name: 'read', agent: { id: 'child' } });
  const result = await run.result;
  assert.match(result.structured.question, /unauthorized tool/);
  const lifecycle = JSON.parse(fs.readFileSync(run.lifecycleFile, 'utf8'));
  assert.equal(lifecycle.phase, 'semantic_review');
});

test('failed receipt close cannot restore tool access after in-memory revocation', async () => {
  const setup = fixture('training-close-failure');
  const dispatcher = createTrainingDispatcher(mockContext(), setup.root);
  const run = await dispatcher.dispatch(setup.input);
  const receipt = JSON.parse(fs.readFileSync(run.receiptFile, 'utf8'));
  const rename = fs.renameSync;
  fs.renameSync = (from, to) => {
    if (to === run.receiptFile) throw new Error('injected receipt disk failure');
    return rename(from, to);
  };
  try {
    dispatcher.stop(setup.input.runId);
    const agent = { id: receipt.childSessionId, session: { events: [{ type: 'subagent/descriptor', data: { label: receipt.label } }] } };
    assert.match(trainingGuardDecision({ agent, name: 'run_code', arguments: {} }, setup.root), /revoked in host memory/);
    await assert.rejects(run.result, /receipt disk failure/);
    assert.notEqual(JSON.parse(fs.readFileSync(run.receiptFile, 'utf8')).executionStatus, 'closed');
  } finally { fs.renameSync = rename; }
});

test('dispatcher creates an ate-ptc parent and one receipt-bound draft DFT child', async () => {
  const { root, runDirectory, materials, sourceView, reviewInput, reviewInputFile } = fixture('training-dispatch');
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  fs.mkdirSync(runDirectory, { recursive: true });
  fs.writeFileSync(path.join(root, 'team/expert-profiles/ptc-dft-expert/instructions.md'), 'DRAFT DFT INSTRUCTIONS');
  let createOptions;
  let request;
  let parentDisposed = false;
  let mountedPreset;
  const parent = { async whenIdle() {} };
  const ctx = {
    agentDefaultModel: { currentSelection: () => ({ provider: 'test-provider', model: 'test-model' }) },
    agentPresets: { async mount(_agentCtx, id) { mountedPreset = id; } },
    agents: { async create(options) { createOptions = options; await options.setup({ scope: 'parent' }); return { agent: parent, async dispose() { parentDisposed = true; } }; } },
    subagents: {
      getProvider: () => ({}),
      async start(_name, value) {
        request = value;
        return { id: 'session-training-dft', result: Promise.resolve({ stopReason: 'completed', structured: {
          status: 'done', reviews: [{ tm: 'TM109', verdict: 'PASS', findings: ['all facts match'] }],
        } }), async dispose() {} };
      },
    },
  };
  const dispatcher = createTrainingDispatcher(ctx, root);
  const dispatched = await dispatcher.dispatch({
    runId: 'training-dispatch', testItems: ['TM109'], sourceView, reviewInput, reviewInputFile, runDirectory, materials,
  });
  assert.equal(createOptions.meta.agentPreset, 'ate-ptc');
  assert.equal(mountedPreset, 'ate-ptc');
  assert.equal(createOptions.meta.cwd, root);
  assert.equal(request.parent, parent);
  assert.deepEqual(request.toolFilter, { allow: [] });
  assert.equal(request.maxDepth, 1);
  assert.match(request.persona, /semantic-review step/);
  assert.match(request.persona, /Do not use tools/);
  assert.match(request.persona, /sourceEvidence against metaProjection/);
  assert.doesNotMatch(request.persona, /FROZEN DFT INSTRUCTIONS/);
  assert.doesNotMatch(request.persona, /DRAFT DFT INSTRUCTIONS/);
  assert.match(request.prompt[0].text, /Semantic-review input/);
  assert.match(request.prompt[0].text, /conditionsProjection/);
  assert.equal(request.outputSchema.required[0], 'status');
  const receipt = JSON.parse(fs.readFileSync(dispatched.receiptFile, 'utf8'));
  assert.equal(verifyTrainingReceipt(receipt), true);
  assert.equal(receipt.childSessionId, 'session-training-dft');
  await dispatched.result;
  assert.equal(parentDisposed, true);
  assert.equal(TRAINING_DEADLINE_MS, 300_000);
});

test('dispatcher deadline settles and revokes tools even when disposal never finishes', { timeout: 1500 }, async () => {
  const { root, runDirectory, materials, sourceView, reviewInput, reviewInputFile } = fixture('training-timeout');
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  fs.mkdirSync(runDirectory, { recursive: true });
  fs.writeFileSync(path.join(root, 'team/expert-profiles/ptc-dft-expert/instructions.md'), 'DRAFT');
  let observedSignal;
  const ctx = {
    agentDefaultModel: { currentSelection: () => ({ provider: 'test-provider', model: 'test-model' }) },
    agentPresets: { async mount() {} },
    agents: { async create(options) { await options.setup({}); return { agent: { async whenIdle() {} }, async dispose() {} }; } },
    subagents: {
      getProvider: () => ({}),
      async start(_name, request) {
        observedSignal = request.signal;
        return { id: 'session-timeout', result: new Promise(() => {}), dispose: () => new Promise(() => {}) };
      },
    },
  };
  const dispatcher = createTrainingDispatcher(ctx, root, { timeoutMs: 25, disposeTimeoutMs: 10 });
  const dispatched = await dispatcher.dispatch({
    runId: 'training-timeout', testItems: ['TM109'], sourceView, reviewInput, reviewInputFile, runDirectory, materials,
  });
  const result = await dispatched.result;
  assert.equal(result.stopReason, 'timeout');
  assert.equal(result.structured.status, 'blocked');
  assert.equal(observedSignal.aborted, true);
  const receipt = JSON.parse(fs.readFileSync(dispatched.receiptFile, 'utf8'));
  assert.equal(receipt.executionStatus, 'closed');
  const agent = { id: receipt.childSessionId, session: { events: [{ type: 'subagent/descriptor', data: { label: receipt.label } }] } };
  assert.match(trainingGuardDecision({ agent, name: 'run_code', arguments: {} }, root), /tool access revoked/);
  assert.equal(dispatcher.stop('training-timeout'), false);
  await delay(25);
  const evidence = JSON.parse(fs.readFileSync(dispatched.lifecycleFile, 'utf8'));
  assert.equal(evidence.childSettled, false);
  assert.equal(evidence.disposals.some((entry) => entry.status === 'timed_out'), true);
});

test('explicit stop settles when a provider ignores the abort signal', { timeout: 1500 }, async () => {
  const { root, runDirectory, materials, sourceView, reviewInput, reviewInputFile } = fixture('training-stop');
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  fs.mkdirSync(runDirectory, { recursive: true });
  fs.writeFileSync(path.join(root, 'team/expert-profiles/ptc-dft-expert/instructions.md'), 'DRAFT');
  const ctx = {
    agentDefaultModel: { currentSelection: () => ({ provider: 'test', model: 'test' }) },
    agentPresets: { async mount() {} },
    agents: { async create() { return { agent: { async whenIdle() {} }, dispose: () => new Promise(() => {}) }; } },
    subagents: { getProvider: () => ({}), async start() { return { id: 'stopped-child', result: new Promise(() => {}), async dispose() {} }; } },
  };
  const dispatcher = createTrainingDispatcher(ctx, root);
  const dispatched = await dispatcher.dispatch({ runId: 'training-stop', testItems: ['TM109'], sourceView, reviewInput, reviewInputFile, runDirectory, materials });
  assert.equal(dispatcher.stop('training-stop', 'user stopped training'), true);
  const result = await dispatched.result;
  assert.equal(result.stopReason, 'aborted');
  assert.equal(result.structured.question, 'user stopped training');
  assert.equal(result.lifecycle.childSettled, false);
});

for (const phase of ['create', 'idle', 'start']) {
  test(`five-minute lifecycle includes stalled ${phase} startup`, { timeout: 1500 }, async () => {
    const { root, input } = fixture(`training-hung-${phase}`);
    const pending = () => new Promise(() => {});
    const ctx = mockContext();
    if (phase === 'create') ctx.agents.create = pending;
    if (phase === 'idle') ctx.agents.create = async () => ({ agent: { whenIdle: pending }, async dispose() {} });
    if (phase === 'start') ctx.subagents.start = pending;
    const dispatcher = createTrainingDispatcher(ctx, root, { timeoutMs: 20 });
    const [record] = await Promise.all([dispatcher.dispatch(input), delay(40)]);
    const result = await record.result;
    assert.equal(result.stopReason, 'timeout');
    assert.equal(result.structured.status, 'blocked');
    assert.equal(record.childSessionId, null);
    assert.equal(JSON.parse(fs.readFileSync(record.receiptFile, 'utf8')).executionStatus, 'closed');
    assert.equal(dispatcher.stop(input.runId), false);
  });
}

test('stop is available immediately during create and disposes late parent without starting child', async () => {
  const { root, input } = fixture('training-stop-create');
  const pending = deferred();
  let disposed = false;
  let childStarted = false;
  const ctx = mockContext({ agents: { create: () => pending.promise } });
  ctx.subagents.start = async () => { childStarted = true; };
  const dispatcher = createTrainingDispatcher(ctx, root);
  const dispatch = dispatcher.dispatch(input);
  await delay(0);
  assert.equal(dispatcher.stop(input.runId, 'stop during create'), true);
  const record = await dispatch;
  assert.equal((await record.result).stopReason, 'aborted');
  pending.resolve({ agent: { async whenIdle() {} }, dispose() { disposed = true; } });
  await delay(10);
  assert.equal(disposed, true);
  assert.equal(childStarted, false);
  assert.equal(record.childSessionId, null);
});

test('late child after stopped launch is disposed and its identity never receives access', async () => {
  const { root, input } = fixture('training-late-child');
  const pending = deferred();
  const started = deferred();
  let disposed = false;
  const ctx = mockContext();
  ctx.subagents.start = () => { started.resolve(); return pending.promise; };
  const dispatcher = createTrainingDispatcher(ctx, root);
  const dispatch = dispatcher.dispatch(input);
  await started.promise;
  dispatcher.stop(input.runId, 'stop during launch');
  const record = await dispatch;
  assert.equal((await record.result).stopReason, 'aborted');
  pending.resolve({ id: 'too-late', result: Promise.resolve({ stopReason: 'completed' }), dispose() { disposed = true; } });
  await delay(10);
  const receipt = JSON.parse(fs.readFileSync(record.receiptFile, 'utf8'));
  assert.equal(receipt.childSessionId, null);
  assert.equal(receipt.executionStatus, 'closed');
  assert.equal(disposed, true);
  assert.equal((await record.result).stopReason, 'aborted');
});

test('dispatch fails closed before creation without matching prepared materials', async () => {
  const { root, input } = fixture('training-materials-required');
  let called = false;
  const ctx = mockContext({ agents: { create() { called = true; } } });
  const dispatcher = createTrainingDispatcher(ctx, root);
  await assert.rejects(dispatcher.dispatch({ ...input, materials: undefined }), /prepared training materials/);
  await assert.rejects(dispatcher.dispatch({ ...input, materials: { ...input.materials, workbook: 'project/DALI/input.xlsx' } }), /prepared training materials/);
  assert.equal(called, false);
});
