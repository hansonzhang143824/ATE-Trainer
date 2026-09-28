import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { Readable } from 'node:stream';
import test from 'node:test';
import { apply } from '../lib/index.js';
import * as projects from '../lib/trainer-project.js';
import * as bundles from '../lib/trainer-bundle.js';
import * as releases from '../lib/trainer-release.js';
import { createFrameworkRunner } from '../lib/framework-agent-run.js';
import { createTrainerService } from '../lib/trainer-service.js';
import { validateJson } from '../lib/trainer-schema.js';

function request(body, headers = { 'content-type': 'application/json' }) {
  const input = Readable.from([JSON.stringify(body)]);
  input.method = 'POST'; input.headers = headers;
  const writes = [];
  return { input, response: {
    writeHead(status, responseHeaders) { writes.push({ status, responseHeaders }); },
    end(value) { writes.push({ body: value }); },
  }, writes };
}

function mounted(workspaceRoot, trainerEnabled) {
  const routes = []; let dispose; let injected;
  const ctx = {
    inject(names, callback) {
      injected = names;
      callback({
        webServer: { register(route) { routes.push(route); return () => {}; } },
        tools: { guard() { return () => {}; } },
        on() { return () => {}; },
        effect(factory) { dispose = factory(); },
      });
    },
    logger: { info() {}, warn() {}, error() {} },
  };
  apply(ctx, { workspaceRoot, trainerEnabled });
  return { routes, dispose, injected };
}

test('trainer runtime is opt-in and registers the complete page API when enabled', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-trainer-route-'));
  try {
    const disabled = mounted(root, false);
    assert.deepEqual(disabled.injected, ['webServer', 'agents', 'agentDefaultModel', 'agentPresets', 'subagents', 'tools']);
    assert.equal(disabled.routes.some(route => route.path.startsWith('/api/ptc-control/trainer/')), false);
    disabled.dispose?.();

    const enabled = mounted(root, true);
    assert.deepEqual(enabled.injected, ['webServer', 'agents', 'agentDefaultModel', 'agentPresets', 'subagents', 'tools', 'sessions', 'sessionPersistence']);
    const trainer = enabled.routes.filter(route => route.path.startsWith('/api/ptc-control/trainer/'));
    assert.equal(trainer.length, 15);
    assert.equal(trainer.find(route => route.path.endsWith('/context'))?.kind, 'exact');
    const contextRoute = trainer.find(route => route.path.endsWith('/context'));
    const context = request({});
    await contextRoute.handler(context.input, context.response);
    assert.equal(context.writes[0].status, 200);
    const payload = JSON.parse(context.writes[1].body);
    assert.equal(payload.ok, true);
    assert.equal(payload.value.project.projectId, 'synthetic-lab');
    assert.equal(payload.value.project.agents.length > 0, true);
    assert.equal(payload.value.project.workflows.length > 0, true);
    enabled.dispose?.();
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('trainer page API keeps mutation boundary JSON-only and same-origin', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-trainer-http-'));
  try {
    const { routes, dispose } = mounted(root, true);
    const contextRoute = routes.find(route => route.path.endsWith('/context'));
    const wrongType = request({}, { 'content-type': 'text/plain' });
    await contextRoute.handler(wrongType.input, wrongType.response);
    assert.equal(wrongType.writes[0].status, 415);
    const wrongOrigin = request({}, { 'content-type': 'application/json', origin: 'https://evil.invalid', host: '127.0.0.1' });
    await contextRoute.handler(wrongOrigin.input, wrongOrigin.response);
    assert.equal(wrongOrigin.writes[0].status, 403);
    dispose?.();
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('trainer service runs a registered workflow through the real runner boundary', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-trainer-run-'));
  let child = 0;
  try {
    const adapter = { async dispatch({ step, input, onStart }) {
      const childSessionId = `synthetic-child-${++child}`;
      onStart({ childSessionId, parentSessionId: 'synthetic-parent' });
      const output = step.stepId === 'produce'
        ? { value: input.seed + 1, marker: 'v1', scriptMarker: 'script-v1' }
        : { receivedValue: input.receivedValue };
      return { output, childSessionId, childTerminationConfirmed: true, stopReason: 'completed' };
    } };
    const runner = createFrameworkRunner({ workspaceRoot: root, adapter,
      verifyBundle: bundles.verifyBundle, validateJson });
    const service = createTrainerService({ workspaceRoot: root, runner,
      repositories: { ...projects, ...bundles, ...releases },
      modelResolver: () => ({ provider: 'fake', model: 'fake' }) });
    const page = (operation, input = {}) => service.invoke(operation,
      { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'lab-pair', ...input }, { kind: 'page' });
    const context = await page('context');
    assert.equal(context.ok, true);
    assert.equal(context.value.project.workflows.some(item => item.workflowId === 'lab-pair'), true);
    const changes = [
      { path: 'agents/lab-extra/instructions.md', content: 'Return the supplied value unchanged.\n' },
      { path: 'contracts/extra-input.schema.json', content: JSON.stringify({ type: 'object', properties: { value: { type: 'integer' } }, required: ['value'], additionalProperties: false }) },
      { path: 'contracts/extra-output.schema.json', content: JSON.stringify({ type: 'object', properties: { value: { type: 'integer' } }, required: ['value'], additionalProperties: false }) },
      { path: 'agents/lab-extra/agent.json', content: JSON.stringify({ agentId: 'lab-extra', name: 'Synthetic extra', instructionsRef: 'agents/lab-extra/instructions.md', skillRefs: [], toolIds: [], inputSchemaRef: 'contracts/extra-input.schema.json', outputSchemaRef: 'contracts/extra-output.schema.json' }) },
      { path: 'workflows/lab-extra.json', content: JSON.stringify({ workflowId: 'lab-extra', name: 'Synthetic extra workflow', steps: [{ stepId: 'single', agentId: 'lab-extra', inputBindings: {}, outputSchemaRef: 'contracts/extra-output.schema.json' }] }) },
    ];
    const saved = await page('apply-changes', { requestId: 'trainer-create-1', baseRevision: context.value.project.revisionId, changes, reason: 'create synthetic Agent and workflow' });
    assert.equal(saved.ok, true, JSON.stringify(saved));
    assert.equal((await page('context')).value.project.agents.some(item => item.agentId === 'lab-extra'), true);
    assert.equal((await page('context')).value.project.workflows.some(item => item.workflowId === 'lab-extra'), true);
    const started = await page('run', { requestId: 'trainer-run-1', input: { seed: 7 } });
    assert.equal(started.ok, true);
    await runner.waitForRun({ runId: started.value.runId });
    const result = await page('runs', { runId: started.value.runId });
    assert.equal(result.value.status, 'completed');
    assert.deepEqual(result.value.output, { receivedValue: 8 });
    assert.equal(result.value.businessGatePassed, false);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
