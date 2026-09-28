import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { setTimeout as delay } from 'node:timers/promises';
import { createFrameworkRunner } from '../lib/framework-agent-run.js';
import { createDshFrameworkAdapter } from '../lib/framework-dsh-adapter.js';
import { ensureTrainerProject } from '../lib/trainer-project.js';
import { resolveBundle, bundleManifestBytes } from '../lib/trainer-bundle.js';
import { frameworkSha } from '../lib/trainer-run-events.js';

function fixture(t, targetId = 'lab-producer') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-adapter-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  ensureTrainerProject(root, { projectId: 'synthetic-lab' });
  const bundle = resolveBundle(root, { projectId: 'synthetic-lab', targetKind: 'agent', targetId, model: { provider: 'fake', model: 'fake', options: { maxTokens: 1000 } } });
  return { root, bundle };
}
function fakeDsh({ result, disposal, script = false, extraTools = [] } = {}) {
  const registered = new Map(); const listeners = new Map(); let guard; let createOptions; let request; let disposed = 0;
  const scope = { on(name, callback) { listeners.set(name, callback); return () => listeners.delete(name); }, tools: {
    register(tool) { registered.set(tool.name, tool); }, guard(value) { guard = value; },
    schemas() { return ['structured_output', ...registered.keys(), ...extraTools].map(name => ({ name, parameters: { type: 'object' } })); },
  } };
  const ctx = {
    on: scope.on,
    agentPresets: { async mount(_scope, preset) { assert.equal(preset, 'framework-worker'); } },
    agents: { async create(options) { createOptions = options; await options.setup(scope); return { agent: { ctx: scope }, async dispose() { disposed++; } }; } },
    subagents: { async start(provider, input) {
      assert.equal(provider, 'spawn'); request = input;
      assert.equal(registered.size, 0, 'parent-local tools must not be assumed to propagate');
      listeners.get('agent/created')?.({ agent: { id: 'unrelated-child', session: { header: { parentSession: 'unrelated-parent' } }, ctx: scope } });
      assert.equal(registered.size, 0, 'unrelated child must not receive tools');
      listeners.get('agent/created')?.({ agent: { id: 'synthetic-child', session: { header: { parentSession: createOptions.sessionId } }, ctx: scope } });
      listeners.get('subagent/start')?.({ id: 'synthetic-child', runId: 'host-run-distinct' });
      const childResult = (async () => {
        if (result) return result;
        const scriptResult = script ? JSON.parse((await registered.get('lab-marker').execute({}, { signal: input.signal })).json) : { scriptMarker: 'script-v1' };
        return { stopReason: 'completed', structured: { payload: { value: 8, marker: 'v1', ...scriptResult } } };
      })();
      return { id: 'synthetic-child', result: childResult, async dispose() { if (disposal) await disposal; disposed++; } };
    } },
  };
  return { ctx, registered, get guard() { return guard; }, get request() { return request; }, get createOptions() { return createOptions; }, get disposed() { return disposed; } };
}

test('fake DSH: worker scope, resolved model, prompt/Skills and start evidence precede result', async t => {
  const { root, bundle } = fixture(t); let release; const pending = new Promise(resolve => { release = resolve; });
  const host = fakeDsh({ result: pending });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-unit', requestId: 'req-1', bundle, input: { seed: 7 }, mode: 'training' });
  for (let i = 0; !host.request && i < 100; i++) await delay(5);
  const running = runner.readRun({ runId: 'dsh-unit' }); assert.equal(running.steps[0].childSessionId, 'synthetic-child'); assert.equal(running.status, 'running');
  assert.equal(host.createOptions.meta.agentPreset, 'framework-worker'); assert.ok(host.createOptions.meta.cwd.includes('workers'));
  assert.equal(host.request.agentOptions.model, 'fake'); assert.equal(host.request.agentOptions.maxTokens, 1000);
  assert.deepEqual(running.steps[0].effectiveTools, ['lab-marker', 'structured_output']);
  assert.match(running.steps[0].toolSchemasSha256, /^[a-f0-9]{64}$/);
  assert.deepEqual(host.request.toolFilter, { allow: [] });
  assert.equal(host.guard({ name: 'lab-marker' }), undefined); assert.equal(host.guard({ name: 'structured_output' }), undefined); assert.match(host.guard({ name: 'trainer_apply_changes' }), /outside/);
  const prompt = JSON.parse(host.request.prompt[0].text); assert.equal(prompt.input.seed, 7); assert.match(prompt.instructions, /input.seed/); assert.ok(prompt.skills.some(file => file.path.endsWith('marker.json')));
  release({ stopReason: 'completed', structured: { payload: { value: 8, marker: 'v1', scriptMarker: 'script-v1' } } });
  const completed = await runner.waitForRun({ runId: 'dsh-unit' }); assert.equal(completed.status, 'completed'); assert.equal(completed.childTerminationConfirmed, true);
  assert.ok(runner.readEvents({ runId: 'dsh-unit' }).events.some(event => event.hostSubagentRunId === 'host-run-distinct'));
});

test('unexpected effective child capability fails composition before result acceptance', async t => {
  const { root, bundle } = fixture(t); const host = fakeDsh({ extraTools: ['trainer_apply_changes'] });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-extra-tool', requestId: 'req-extra', bundle, input: { seed: 7 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'dsh-extra-tool' });
  assert.equal(run.status, 'failed'); assert.match(run.error.message, /effective child tools differ/);
  assert.ok(run.steps[0].effectiveTools.includes('trainer_apply_changes'));
});

test('fake DSH: completed text without structured payload is failure', async t => {
  const { root, bundle } = fixture(t); const host = fakeDsh({ result: { stopReason: 'completed', output: [{ type: 'text', text: '{"value":8}' }] } });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-no-capture', requestId: 'req-2', bundle, input: { seed: 7 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'dsh-no-capture' }); assert.equal(run.status, 'failed'); assert.match(run.error.message, /captured payload/); assert.equal(run.childTerminationConfirmed, true);
});

test('fake DSH: model errors remain failures even with valid payload', async t => {
  const { root, bundle } = fixture(t); const host = fakeDsh({ result: { stopReason: 'error', structured: { payload: { value: 8, marker: 'v1', scriptMarker: 'script-v1' } } } });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-error', requestId: 'req-3', bundle, input: { seed: 7 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'dsh-error' }); assert.equal(run.status, 'failed'); assert.equal(run.error.code, 'MODEL_EXECUTION_FAILED');
});

test('fake DSH with real synthetic Node tool: executes the bundle script bytes', async t => {
  const { root, bundle } = fixture(t); const host = fakeDsh({ script: true });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-script', requestId: 'req-4', bundle, input: { seed: 7 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'dsh-script' }); assert.equal(run.status, 'completed', run.error?.message); assert.equal(run.output.scriptMarker, 'script-v1');
  const events = runner.readEvents({ runId: run.runId }).events;
  assert.ok(events.some(event => event.type === 'tool-started' && event.toolId === 'lab-marker'));
  assert.ok(events.some(event => event.type === 'tool-completed'));
});

test('fake DSH ignores abort: runner returns stopping without pretending cleanup succeeded', async t => {
  const { root, bundle } = fixture(t); let releaseResult; let releaseDisposal;
  const result = new Promise(resolve => { releaseResult = resolve; });
  const disposal = new Promise(resolve => { releaseDisposal = resolve; });
  const host = fakeDsh({ result, disposal });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-ignored-abort', requestId: 'req-5', bundle, input: { seed: 7 }, mode: 'training' });
  for (let i = 0; !host.request && i < 100; i++) await delay(5);
  runner.controlRun({ runId: 'dsh-ignored-abort', action: 'stop' });
  const stopped = await runner.waitForRun({ runId: 'dsh-ignored-abort' }); assert.equal(stopped.status, 'stopping'); assert.equal(stopped.childTerminationConfirmed, false);
  releaseResult({ stopReason: 'aborted' }); await delay(5);
  assert.equal(runner.readRun({ runId: stopped.runId }).status, 'stopping');
  releaseDisposal();
  for (let i = 0; runner.readRun({ runId: stopped.runId }).status === 'stopping' && i < 100; i++) await delay(5);
  assert.equal(runner.readRun({ runId: stopped.runId }).status, 'cancelled');
});

test('real synthetic script timeout is bounded and recorded without a successful child', async t => {
  const { root, bundle } = fixture(t);
  const script = bundle.files.find(file => file.path.endsWith('marker.mjs'));
  script.content = 'setInterval(() => {}, 1000);'; script.size = Buffer.byteLength(script.content); script.sha256 = frameworkSha(Buffer.from(script.content));
  bundle.tools['lab-marker'].timeoutMs = 100;
  // Keep the tool-definition asset consistent with the resolved metadata.
  const definition = bundle.files.find(file => file.path === 'tools/lab-marker.json');
  definition.content = JSON.stringify(bundle.tools['lab-marker']); definition.size = Buffer.byteLength(definition.content); definition.sha256 = frameworkSha(Buffer.from(definition.content));
  bundle.bundleSha256 = frameworkSha(bundleManifestBytes(bundle));
  const host = fakeDsh({ script: true });
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  const started = Date.now();
  await runner.startRun({ runId: 'dsh-script-timeout', requestId: 'req-6', bundle, input: { seed: 7 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'dsh-script-timeout' });
  assert.equal(run.status, 'failed'); assert.match(run.error.message, /script timed out/); assert.equal(run.childTerminationConfirmed, true); assert.ok(Date.now() - started < 5000);
});

test('adapter unit: internal namespaced tool key registers the original short tool name', async t => {
  const { root, bundle } = fixture(t); const host = fakeDsh({ script: true });
  const internalKey = `frozen-${'a'.repeat(64)}-lab-marker`;
  bundle.tools[internalKey] = bundle.tools['lab-marker']; delete bundle.tools['lab-marker']; bundle.steps[0].toolIds = [internalKey];
  // Deliberately test the adapter seam only; full namespace bundle construction
  // and verification belong to B's separate integration tests.
  const runner = createFrameworkRunner({ workspaceRoot: root, verifyBundle: () => ({ ok: true }), adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-tool-alias', requestId: 'req-7', bundle, input: { seed: 7 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'dsh-tool-alias' }); assert.equal(run.status, 'completed', run.error?.message);
  assert.deepEqual(run.steps[0].effectiveTools, ['lab-marker', 'structured_output']);
  const event = runner.readEvents({ runId: run.runId }).events.find(event => event.type === 'tool-started');
  assert.equal(event.toolId, internalKey); assert.equal(event.toolName, 'lab-marker');
});

test('adapter unit: two internal definitions with the same public tool name reject before dispatch', async t => {
  const { root, bundle } = fixture(t); const host = fakeDsh();
  bundle.tools['frozen-other-lab-marker'] = bundle.tools['lab-marker']; bundle.steps[0].toolIds.push('frozen-other-lab-marker');
  const runner = createFrameworkRunner({ workspaceRoot: root, verifyBundle: () => ({ ok: true }), adapter: createDshFrameworkAdapter(host.ctx, { workspaceRoot: root }) });
  await runner.startRun({ runId: 'dsh-name-conflict', requestId: 'req-8', bundle, input: { seed: 7 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'dsh-name-conflict' }); assert.equal(run.status, 'failed'); assert.match(run.error.message, /duplicate/); assert.equal(host.request, undefined);
});
