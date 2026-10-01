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
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';

function request(body, headers = { 'content-type': 'application/json' }) {
  const input = Readable.from([JSON.stringify(body)]);
  input.method = 'POST'; input.headers = headers;
  const writes = [];
  return { input, response: {
    writeHead(status, responseHeaders) { writes.push({ status, responseHeaders }); },
    end(value) { writes.push({ body: value }); },
  }, writes };
}


function initializeAgentLedger(root, projectId) {
  const project = projects.readProject(root, { projectId });
  const files = projects.readAssets(root, { projectId, revisionId: project.revisionId }).files;
  const allocated = Object.entries(files).filter(([file]) => /^agents\/[^/]+\/agent\.json$/.test(file)).map(([, content]) => JSON.parse(content).agentId);
  return projects.applyChanges(root, { projectId, requestId: `seed-ledger-${projectId}`, baseRevision: project.revisionId, reason: '初始化 Agent ID 台账', changes: [{ path: 'contracts/agent-ids.json', content: `${JSON.stringify({ schemaVersion: 1, allocated }, null, 2)}\n` }] });
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
    fs.mkdirSync(path.join(root, 'docs', 'prototypes'), { recursive: true });
    fs.writeFileSync(path.join(root, 'docs', 'prototypes', 'agent-trainer-user-guide.html'), '<title>从零开始使用 Agent Trainer</title><h2>自己点击验证 Agent 和工作流</h2>');
    fs.writeFileSync(path.join(root, 'docs', 'agent-trainer-empty-system-acceptance-evidence-20260930.json'), '{"status":"passed"}');
    const disabled = mounted(root, false);
    assert.deepEqual(disabled.injected, ['webServer', 'agents', 'agentDefaultModel', 'agentPresets', 'subagents', 'tools', 'workspaceRegistry']);
    assert.equal(disabled.routes.some(route => route.path.startsWith('/api/ptc-control/trainer/')), false);
    disabled.dispose?.();

    const enabled = mounted(root, true);
    assert.deepEqual(enabled.injected, ['webServer', 'agents', 'agentDefaultModel', 'agentPresets', 'subagents', 'tools', 'workspaceRegistry', 'sessions', 'sessionPersistence']);
    const trainer = enabled.routes.filter(route => route.path.startsWith('/api/ptc-control/trainer/'));
    assert.equal(trainer.length, 18);
    const guideRoute = enabled.routes.find(route => route.path === '/agent-trainer-guide');
    assert.equal(guideRoute?.kind, 'exact');
    const guide = request({});
    guide.input.method = 'GET';
    await guideRoute.handler(guide.input, guide.response);
    assert.equal(guide.writes[0].status, 200);
    assert.match(String(guide.writes[1].body), /从零开始使用 Agent Trainer/);
    assert.match(String(guide.writes[1].body), /自己点击验证 Agent 和工作流/);
    const evidenceRoute = enabled.routes.find(route => route.path === '/agent-trainer-evidence.json');
    assert.equal(evidenceRoute?.kind, 'exact');
    const evidence = request({});
    evidence.input.method = 'GET';
    await evidenceRoute.handler(evidence.input, evidence.response);
    assert.equal(evidence.writes[0].status, 200);
    assert.deepEqual(JSON.parse(String(evidence.writes[1].body)), { status: 'passed' });
    assert.equal(trainer.find(route => route.path.endsWith('/context'))?.kind, 'exact');
    assert.equal(trainer.find(route => route.path.endsWith('/session-workspace'))?.kind, 'exact');
    assert.equal(trainer.find(route => route.path.endsWith('/session-tool'))?.kind, 'exact');
    const contextRoute = trainer.find(route => route.path.endsWith('/context'));
    const context = request({});
    await contextRoute.handler(context.input, context.response);
    assert.equal(context.writes[0].status, 200);
    const payload = JSON.parse(context.writes[1].body);
    assert.equal(payload.ok, true);
    assert.equal(payload.value.project.projectId, 'agent-trainer');
    assert.deepEqual(payload.value.project.agents, []);
    assert.deepEqual(payload.value.project.workflows, []);
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
    await projects.ensureTrainerProject(root, { projectId: 'synthetic-lab', seed: createSyntheticTrainerFixture() });
    initializeAgentLedger(root, 'synthetic-lab');
    const adapter = { async dispatch({ step, bundle, input, onStart }) {
      const childSessionId = `synthetic-child-${++child}`;
      onStart({ childSessionId, parentSessionId: 'synthetic-parent' });
      const instruction = bundle.files.find(file => file.path === step.instructionsRef)?.content ?? '';
      const output = instruction.includes('Synthetic SMOKE_ONLY')
        ? { answer: 3 }
        : instruction.includes('Synthetic BUSINESS_ONLY')
        ? { answer: 597 }
        : step.stepId === 'produce'
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
    const currentAssets = projects.readAssets(root, { projectId: 'synthetic-lab', revisionId: context.value.project.revisionId }).files;
    const allocated = Object.entries(currentAssets).filter(([file]) => /^agents\/[^/]+\/agent\.json$/.test(file)).map(([, content]) => JSON.parse(content).agentId);
    const changes = [
      { path: 'agents/lab-extra/instructions.md', content: 'Return the supplied value unchanged.\n' },
      { path: 'contracts/extra-input.schema.json', content: JSON.stringify({ type: 'object', properties: { value: { type: 'integer' } }, required: ['value'], additionalProperties: false }) },
      { path: 'contracts/extra-output.schema.json', content: JSON.stringify({ type: 'object', properties: { value: { type: 'integer' } }, required: ['value'], additionalProperties: false }) },
      { path: 'agents/lab-extra/agent.json', content: JSON.stringify({ agentId: 'lab-extra', name: 'Synthetic extra', instructionsRef: 'agents/lab-extra/instructions.md', skillRefs: [], toolIds: [], inputSchemaRef: 'contracts/extra-input.schema.json', outputSchemaRef: 'contracts/extra-output.schema.json' }) },
      { path: 'workflows/lab-extra.json', content: JSON.stringify({ workflowId: 'lab-extra', name: 'Synthetic extra workflow', steps: [{ stepId: 'single', agentId: 'lab-extra', inputBindings: {}, outputSchemaRef: 'contracts/extra-output.schema.json' }] }) },
      { path: 'contracts/agent-ids.json', content: `${JSON.stringify({ schemaVersion: 1, allocated: [...allocated, 'lab-extra'] }, null, 2)}\n` },
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

    const smokeStarted = await page('run', { requestId: 'trainer-smoke-run-1', executionMode: 'SMOKE_ONLY', input: { receivedValue: '1+2' } });
    assert.equal(smokeStarted.ok, true, JSON.stringify(smokeStarted));
    await runner.waitForRun({ runId: smokeStarted.value.runId });
    const smokeResult = await page('runs', { runId: smokeStarted.value.runId });
    assert.equal(smokeResult.value.executionMode, 'SMOKE_ONLY');
    assert.equal(smokeResult.value.status, 'completed', JSON.stringify(smokeResult.value));
    assert.deepEqual(smokeResult.value.output, { answer: 3 });
    assert.equal(smokeResult.value.businessGatePassed, false);
    assert.ok(smokeResult.value.steps.every(step => step.output && step.output.answer === 3));

    const businessFiles = [
      { path: 'agents/business-agent/instructions.md', content: 'Candidate task must remain separate from synthetic BUSINESS_ONLY execution.\n' },
      { path: 'agents/business-agent/agent.json', content: JSON.stringify({ agentId: 'business-agent', name: 'Synthetic business Agent', instructionsRef: 'agents/business-agent/instructions.md', skillRefs: [], toolIds: [], inputSchemaRef: 'contracts/business-input.schema.json', outputSchemaRef: 'contracts/business-output.schema.json' }) },
      { path: 'contracts/business-input.schema.json', content: JSON.stringify({ type: 'object', additionalProperties: true }) },
      { path: 'contracts/business-output.schema.json', content: JSON.stringify({ type: 'object', properties: { answer: { type: 'number' } }, required: ['answer'], additionalProperties: false }) },
      { path: 'workflows/business-workflow.json', content: JSON.stringify({ workflowId: 'business-workflow', name: 'Synthetic business workflow', steps: [{ stepId: 'business-step', agentId: 'business-agent', inputBindings: {}, outputSchemaRef: 'contracts/business-output.schema.json' }] }) },
    ];
    const businessContext = await page('context');
    const businessAssets = projects.readAssets(root, { projectId: 'synthetic-lab', revisionId: businessContext.value.project.revisionId }).files;
    const businessIds = Object.entries(businessAssets).filter(([file]) => /^agents\/[^/]+\/agent\.json$/.test(file)).map(([, content]) => JSON.parse(content).agentId);
    businessFiles.push({ path: 'contracts/agent-ids.json', content: `${JSON.stringify({ schemaVersion: 1, allocated: [...businessIds, 'business-agent'] }, null, 2)}\n` });
    const businessSaved = await page('apply-changes', { requestId: 'trainer-business-create-1', baseRevision: businessContext.value.project.revisionId, changes: businessFiles, reason: 'create synthetic BUSINESS_ONLY regression fixture' });
    assert.equal(businessSaved.ok, true, JSON.stringify(businessSaved));
    const businessPage = (operation, input = {}) => service.invoke(operation,
      { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'business-workflow', ...input }, { kind: 'page' });
    const businessStarted = await businessPage('run', { requestId: 'trainer-business-run-1', executionMode: 'BUSINESS_ONLY', input: { receivedValue: '23*24+45' } });
    assert.equal(businessStarted.ok, true, JSON.stringify(businessStarted));
    await runner.waitForRun({ runId: businessStarted.value.runId });
    const businessResult = await businessPage('runs', { runId: businessStarted.value.runId });
    assert.equal(businessResult.value.executionMode, 'BUSINESS_ONLY');
    assert.deepEqual(businessResult.value.output, { answer: 597 });
    assert.deepEqual(businessResult.value.steps[0].output, { answer: 597 });
    assert.equal(businessResult.value.validation.ok, true);
    assert.equal(businessResult.value.businessGatePassed, false);
    const unchanged = await page('assets', { revisionId: businessSaved.value.revisionId });
    assert.match(unchanged.value.files['agents/business-agent/instructions.md'], /Candidate task must remain separate/);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});



test('engineering mode exposes Agents bound by a published workflow', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-trainer-published-binding-'));
  try {
    await projects.ensureTrainerProject(root, { projectId: 'synthetic-lab', seed: createSyntheticTrainerFixture() });
    const adapter = { async dispatch() { throw new Error('dispatch not used'); } };
    const runner = createFrameworkRunner({ workspaceRoot: root, adapter,
      verifyBundle: bundles.verifyBundle, validateJson });
    const service = createTrainerService({ workspaceRoot: root, runner,
      repositories: {
        ...projects, ...bundles, ...releases,
        listReleases: () => ({ projectId: 'synthetic-lab', releases: [], active: [
          { targetKind: 'workflow', targetId: 'lab-pair', releaseId: 'release-published-workflow' },
        ] }),
        loadReleaseBundle: () => ({ steps: [
          { stepId: 'produce', agentId: 'lab-producer' },
          { stepId: 'consume', agentId: 'lab-consumer' },
        ] }),
      },
      modelResolver: () => ({ provider: 'fake', model: 'fake' }),
    });
    const context = await service.invoke('context', { projectId: 'synthetic-lab', mode: 'engineering' }, { kind: 'page' });
    assert.equal(context.ok, true, JSON.stringify(context));
    assert.deepEqual(context.value.project.agents.map(item => item.agentId).sort(), ['lab-consumer', 'lab-producer']);
    assert.deepEqual(context.value.project.workflows.map(item => item.workflowId), ['lab-pair']);
    const binding = await service.invoke('bind-session', {
      projectId: 'synthetic-lab', mode: 'engineering', targetKind: 'agent', targetId: 'lab-producer', presetId: 'framework-observer',
    }, { kind: 'page' });
    assert.equal(binding.ok, true, JSON.stringify(binding));
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('Agent optimization records an independent 2+3 candidate run', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-trainer-optimization-'));
  let child = 0;
  const arithmeticFiles = {
    'agents/arithmetic-agent/instructions.md': 'v1: add input.a and input.b and return numeric value.\n',
    'agents/arithmetic-agent/agent.json': JSON.stringify({ agentId: 'arithmetic-agent', name: 'Arithmetic Agent', instructionsRef: 'agents/arithmetic-agent/instructions.md', skillRefs: [], toolIds: [], inputSchemaRef: 'contracts/arithmetic-input.schema.json', outputSchemaRef: 'contracts/arithmetic-output.schema.json' }),
    'contracts/arithmetic-input.schema.json': JSON.stringify({ $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object', properties: { a: { type: 'integer' }, b: { type: 'integer' } }, required: ['a', 'b'], additionalProperties: false }),
    'contracts/arithmetic-output.schema.json': JSON.stringify({ $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object', properties: { value: { type: 'integer' }, revisionLabel: { type: 'string' } }, required: ['value', 'revisionLabel'], additionalProperties: false }),
    'tests/arithmetic-agent.json': JSON.stringify({ testId: 'arithmetic-agent', targetKind: 'agent', targetId: 'arithmetic-agent', cases: [{ input: { a: 1, b: 2 }, expected: { value: 3, revisionLabel: 'v1' } }] }),
  };
  try {
    const adapter = { async dispatch({ step, input, bundle, onStart }) {
      const childSessionId = `optimization-child-${++child}`;
      onStart({ childSessionId, parentSessionId: 'optimization-parent' });
      const instructions = bundle.files.find(file => file.path === step.instructionsRef).content;
      const revisionLabel = instructions.includes('v2') ? 'v2' : 'v1';
      return { output: { value: input.a + input.b, revisionLabel }, childSessionId, childTerminationConfirmed: true, stopReason: 'completed' };
    } };
    const runner = createFrameworkRunner({ workspaceRoot: root, adapter, verifyBundle: bundles.verifyBundle, validateJson });
    const service = createTrainerService({ workspaceRoot: root, runner,
      repositories: { ...projects, ...bundles, ...releases }, modelResolver: () => ({ provider: 'fake', model: 'fake' }) });
    await projects.ensureTrainerProject(root, { projectId: 'optimization-lab', seed: { files: arithmeticFiles } });
    initializeAgentLedger(root, 'optimization-lab');
    const page = (operation, input = {}) => service.invoke(operation,
      { projectId: 'optimization-lab', targetKind: 'agent', targetId: 'arithmetic-agent', ...input }, { kind: 'page' });

    const v1Started = await page('run', { requestId: 'optimization-v1', input: { a: 1, b: 2 } });
    assert.equal(v1Started.ok, true, JSON.stringify(v1Started));
    await runner.waitForRun({ runId: v1Started.value.runId });
    const v1 = (await page('runs', { runId: v1Started.value.runId })).value;
    assert.equal(v1.status, 'completed');
    assert.equal(v1.purpose, 'FRAMEWORK_TRAINING');
    assert.deepEqual(v1.output, { value: 3, revisionLabel: 'v1' });

    const context = await page('context');
    const saved = await page('apply-changes', { requestId: 'optimization-change-1', baseRevision: context.value.project.revisionId,
      linkedRunId: v1.runId, reason: 'optimize arithmetic Agent executable behavior', changes: [
        { path: 'agents/arithmetic-agent/instructions.md', content: 'v2: optimized arithmetic path; add input.a and input.b and return numeric value.\n' },
        { path: 'tests/arithmetic-agent.json', content: JSON.stringify({ testId: 'arithmetic-agent', targetKind: 'agent', targetId: 'arithmetic-agent', cases: [{ input: { a: 1, b: 2 }, expected: { value: 3, revisionLabel: 'v1' } }, { input: { a: 2, b: 3 }, expected: { value: 5, revisionLabel: 'v2' } }] }) },
      ] });
    assert.equal(saved.ok, true, JSON.stringify(saved));
    assert.notEqual(saved.value.revisionId, v1.revisionId);

    const v2Started = await page('run', { requestId: 'optimization-v2', input: { a: 2, b: 3 }, purpose: 'agent-optimization', derivedFromRunId: v1.runId, changeSetId: saved.value.changeSetId });
    assert.equal(v2Started.ok, true, JSON.stringify(v2Started));
    await runner.waitForRun({ runId: v2Started.value.runId });
    const v2 = (await page('runs', { runId: v2Started.value.runId })).value;
    assert.equal(v2.status, 'completed');
    assert.equal(v2.purpose, 'agent-optimization');
    assert.equal(v2.derivedFromRunId, v1.runId);
    assert.equal(v2.changeSetId, saved.value.changeSetId);
    assert.notEqual(v2.revisionId, v1.revisionId);
    assert.deepEqual(v2.output, { value: 5, revisionLabel: 'v2' });
    assert.deepEqual(v2.testResults, [{ testId: 'arithmetic-agent', caseIndex: 1, ok: true, errors: [] }]);
    const v1Again = (await page('runs', { runId: v1.runId })).value;
    assert.deepEqual(v1Again.output, { value: 3, revisionLabel: 'v1' });
    assert.notEqual(v1Again.bundleSha256, v2.bundleSha256);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
