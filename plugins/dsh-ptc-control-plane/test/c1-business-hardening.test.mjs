import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { validateProjectFiles } from '../lib/trainer-schema.js';
import { createFrameworkRunner, formatStepTimeoutMessage } from '../lib/framework-agent-run.js';
import { resolveBundle, verifyBundle } from '../lib/trainer-bundle.js';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';
import * as projects from '../lib/trainer-project.js';

const json = value => `${JSON.stringify(value)}\n`;
function workflowFiles(timeoutMs, extra = {}) {
  return {
    'agents/demo/agent.json': json({ agentId: 'demo', name: 'Demo', instructionsRef: 'agents/demo/instructions.md', inputSchemaRef: 'contracts/input.schema.json', outputSchemaRef: 'contracts/output.schema.json' }),
    'agents/demo/instructions.md': 'Return a JSON answer.\n',
    'contracts/input.schema.json': json({ type: 'object', additionalProperties: true }),
    'contracts/output.schema.json': json({ type: 'object', additionalProperties: true }),
    'workflows/demo.json': json({ workflowId: 'demo', steps: [{ stepId: 'step-1', agentId: 'demo', inputBindings: {}, timeoutMs, ...extra }] }),
  };
}

test('C1 schema rejects archived businessPipeline and enforces 30 minute timeout ceiling', () => {
  const archived = validateProjectFiles({ ...workflowFiles(1800000), 'workflows/demo.json': json({ workflowId: 'demo', businessPipeline: {}, steps: [{ stepId: 'step-1', agentId: 'demo', inputBindings: {}, timeoutMs: 1800000 }] }) });
  assert.equal(archived.ok, false);
  assert.ok(archived.errors.some(item => item.message.includes('businessPipeline is archived')));
  assert.equal(validateProjectFiles(workflowFiles(1800000)).ok, true);
  const tooLong = validateProjectFiles(workflowFiles(1800001));
  assert.equal(tooLong.ok, false);
  assert.ok(tooLong.errors.some(item => item.message === 'invalid timeoutMs'));
  const zero = validateProjectFiles(workflowFiles(0));
  assert.equal(zero.ok, false);
  assert.ok(zero.errors.some(item => item.message === 'invalid timeoutMs'));
});

test('C1 runner marks a never-settling child as STEP_TIMEOUT and keeps the run failed', { timeout: 3000 }, async t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'c1-timeout-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  await projects.ensureTrainerProject(root, { projectId: 'c1', seed: createSyntheticTrainerFixture() });
  const before = projects.readProject(root, { projectId: 'c1' });
  const files = projects.readAssets(root, { projectId: 'c1', revisionId: before.revisionId }).files;
  const workflow = JSON.parse(files['workflows/lab-pair.json']);
  workflow.steps[0].timeoutMs = 50;
  const saved = projects.applyChanges(root, { projectId: 'c1', requestId: 'c1-timeout-seed', baseRevision: before.revisionId, reason: 'C1 timeout fixture', changes: [{ path: 'workflows/lab-pair.json', content: json(workflow) }] });
  const bundle = resolveBundle(root, { projectId: 'c1', targetKind: 'workflow', targetId: 'lab-pair', revisionId: saved.revisionId, model: { provider: 'fake', model: 'fake' } });
  assert.equal(verifyBundle(bundle).ok, true);
  const adapter = { async dispatch({ onStart }) { onStart({ childSessionId: 'never-child', parentSessionId: 'test-parent' }); return new Promise(() => {}); } };
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter, verifyBundle, validateJson: (schema, value) => ({ ok: true, errors: [] }) });
  const started = await runner.startRun({ runId: 'c1-timeout-run', requestId: 'c1-timeout-run', mode: 'training', executionMode: 'BUSINESS_ONLY', bundle, input: { seed: 7 } });
  const result = await runner.waitForRun({ runId: started.runId });
  assert.equal(result.status, 'failed', JSON.stringify(result));
  assert.equal(result.error.code, 'STEP_TIMEOUT');
  assert.match(result.error.message, /^第 1 步 \S+（\S+）超过 .+未完成，已判失败$/);
  assert.equal(result.steps[0].error.code, 'STEP_TIMEOUT');
  assert.equal(result.steps[0].error.message, result.error.message);
});

test('C1 timeout formatter uses minutes for exact minute durations', () => {
  assert.equal(formatStepTimeoutMessage({ stepNumber: 1, stepId: 'step-1', agentId: 'demo', timeoutMs: 60000 }), '第 1 步 step-1（demo）超过 1 分钟未完成，已判失败');
});

test('C1 reconcileInterrupted marks a persisted paused run as HOST_RESTARTED', { timeout: 3000 }, async t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'c1-reconcile-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  await projects.ensureTrainerProject(root, { projectId: 'c1', seed: createSyntheticTrainerFixture() });
  const project = projects.readProject(root, { projectId: 'c1' });
  const bundle = resolveBundle(root, { projectId: 'c1', targetKind: 'workflow', targetId: 'lab-pair', revisionId: project.revisionId, model: { provider: 'fake', model: 'fake' } });
  let runner;
  const adapter = { async dispatch({ step, input, onStart }) {
    onStart({ childSessionId: `paused-child-${step.stepId}`, parentSessionId: 'test-parent' });
    await new Promise(resolve => setTimeout(resolve, 30));
    return { childSessionId: `paused-child-${step.stepId}`, childTerminationConfirmed: true, stopReason: 'completed', output: step.stepId === 'produce' ? { value: input.seed + 1, marker: 'v1', scriptMarker: 'script-v1' } : { receivedValue: input.receivedValue } };
  } };
  runner = createFrameworkRunner({ workspaceRoot: root, adapter, verifyBundle, validateJson: (schema, value) => ({ ok: true, errors: [] }) });
  const started = await runner.startRun({ runId: 'c1-paused-run', requestId: 'c1-paused-run', mode: 'training', bundle, input: { seed: 7 } });
  setTimeout(() => { try { runner.controlRun({ runId: started.runId, action: 'pause' }); } catch {} }, 5);
  let paused;
  for (let i = 0; i < 40; i++) { await new Promise(resolve => setTimeout(resolve, 10)); paused = runner.readRun({ runId: started.runId }); if (paused.status === 'paused') break; }
  assert.equal(paused?.status, 'paused', JSON.stringify(paused));
  const restarted = createFrameworkRunner({ workspaceRoot: root, adapter, verifyBundle, validateJson: (schema, value) => ({ ok: true, errors: [] }) });
  assert.deepEqual(restarted.reconcileInterrupted(), [started.runId]);
  const interrupted = restarted.readRun({ runId: started.runId });
  assert.equal(interrupted.status, 'interrupted');
  assert.equal(interrupted.error.code, 'HOST_RESTARTED');
});
