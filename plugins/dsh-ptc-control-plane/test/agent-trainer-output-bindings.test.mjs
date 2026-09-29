import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';
import { ensureTrainerProject, applyChanges, readProject } from '../lib/trainer-project.js';
import { resolveBundle, verifyBundle, freezeTarget } from '../lib/trainer-bundle.js';
import { stageRelease, activateRelease, loadReleaseBundle } from '../lib/trainer-release.js';
import { createFrameworkRunner, resolveFrameworkOutput } from '../lib/framework-agent-run.js';
import { validateJson } from '../lib/trainer-schema.js';

const model = { provider: 'test', model: 'test' };
const target = { projectId: 'output-bindings', targetKind: 'workflow', targetId: 'lab-pair' };
function setup(t, { mapped = true, frozen = false, missing = false } = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-output-bindings-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const { files } = createSyntheticTrainerFixture();
  const workflow = JSON.parse(files['workflows/lab-pair.json']);
  if (mapped) {
    workflow.steps[0].outputBindings = { '/handoff/value': { source: 'output', pointer: missing ? '/absent' : '/value' } };
    workflow.steps[1].inputBindings['/receivedValue'].pointer = '/handoff/value';
    workflow.steps[1].outputBindings = { '/answer': { source: 'output', pointer: '/receivedValue' } };
    files['tests/lab-pair.json'] = JSON.stringify({ testId: 'lab-pair', targetKind: 'workflow', targetId: 'lab-pair', cases: [{ input: { seed: 7 }, expected: { answer: 8 } }] });
  }
  files['workflows/lab-pair.json'] = JSON.stringify(workflow);
  const project = ensureTrainerProject(root, { projectId: target.projectId, seed: { files } });
  if (frozen) {
    const agent = resolveBundle(root, { ...target, targetKind: 'agent', targetId: 'lab-producer', model });
    const version = freezeTarget(root, { ...target, targetKind: 'agent', targetId: 'lab-producer', bundle: agent });
    workflow.steps[0].agentVersion = { kind: 'frozen', frozenVersionId: version.frozenVersionId };
    applyChanges(root, { projectId: target.projectId, requestId: 'pin-agent', baseRevision: project.revisionId, reason: 'test frozen Agent mapping', changes: [{ path: 'workflows/lab-pair.json', content: JSON.stringify(workflow) }] });
  }
  const dispatches = [];
  const runner = createFrameworkRunner({ workspaceRoot: root, verifyBundle, validateJson, adapter: {
    async dispatch({ step, input, onStart }) {
      dispatches.push({ agentId: step.agentId, input });
      const childSessionId = `child-${dispatches.length}`;
      onStart({ childSessionId });
      return { childSessionId, childTerminationConfirmed: true, stopReason: 'completed',
        output: step.agentId === 'lab-producer' ? { value: input.seed + 1, marker: 'v1', scriptMarker: 'script-v1' } : { receivedValue: input.receivedValue } };
    },
  } });
  const bundle = resolveBundle(root, { ...target, model });
  const run = async (runId, chosenBundle = bundle, mode = 'training') => {
    await runner.startRun({ runId, requestId: runId, mode, bundle: chosenBundle, input: { seed: 7 } });
    await runner.waitForRun({ runId });
    return runner.readRun({ runId });
  };
  return { root, bundle, run, dispatches, workflow };
}

for (const frozen of [false, true]) test(`output mapping reaches downstream input and preserves raw output (${frozen ? 'frozen' : 'candidate'} Agent)`, async t => {
  const { root, bundle, run, dispatches, workflow } = setup(t, { frozen });
  assert.deepEqual(bundle.steps[0].outputBindings, workflow.steps[0].outputBindings);
  assert.equal(verifyBundle(bundle).ok, true);
  const result = await run('mapped-run');
  assert.equal(result.status, 'completed', JSON.stringify(result.error));
  assert.deepEqual(dispatches[1].input, { receivedValue: 8 });
  assert.deepEqual(result.steps[0].output, { value: 8, marker: 'v1', scriptMarker: 'script-v1' });
  assert.deepEqual(result.steps[0].handoffOutput, { handoff: { value: 8 } });
  assert.deepEqual(result.steps[1].output, { receivedValue: 8 });
  assert.deepEqual(result.output, { answer: 8 });
  assert.deepEqual(result.steps[0].outputBindings, workflow.steps[0].outputBindings);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root, result.steps[0].handoffArtifact.path), 'utf8')), result.steps[0].handoffOutput);
  assert.equal(result.steps[0].validation.ok, true);
  assert.equal(result.steps[1].inputValidation.ok, true);
});

test('undeclared and empty output mappings preserve the original handoff', async t => {
  const { run } = setup(t, { mapped: false });
  const result = await run('default-run');
  assert.equal(result.status, 'completed');
  assert.deepEqual(result.output, { receivedValue: 8 });
  for (const step of result.steps) assert.deepEqual(step.handoffOutput, step.output);
  const raw = { nested: { value: 3 } };
  const mapped = resolveFrameworkOutput({ outputBindings: {} }, raw);
  assert.deepEqual(mapped, raw);
  mapped.nested.value = 9;
  assert.equal(raw.nested.value, 3);
});

test('a missing output field fails at its producer and never dispatches downstream', async t => {
  const { run, dispatches } = setup(t, { missing: true });
  const result = await run('missing-run');
  assert.equal(result.status, 'failed');
  assert.equal(result.error.code, 'OUTPUT_BINDING_MISSING');
  assert.equal(dispatches.length, 1);
  assert.equal(result.steps[0].status, 'failed');
  assert.equal(result.steps[1].status, 'pending');
  assert.equal(result.steps[0].output.value, 8);
  assert.equal(result.steps[0].handoffOutput, undefined);
});

test('output mapping enforces root, escape, unsafe path and overlap rules', () => {
  assert.deepEqual(resolveFrameworkOutput({ outputBindings: { '': { source: 'output', pointer: '/payload' } } }, { payload: { answer: 3 } }), { answer: 3 });
  assert.deepEqual(resolveFrameworkOutput({ outputBindings: { '/a~1b': { source: 'output', pointer: '/x~0y' } } }, { 'x~y': 3 }), { 'a/b': 3 });
  for (const outputBindings of [
    { '': { source: 'output', pointer: '' }, '/value': { source: 'output', pointer: '/value' } },
    { '/__proto__/polluted': { source: 'output', pointer: '/value' } },
    { '/nested': { source: 'output', pointer: '/value' }, '/nested/value': { source: 'output', pointer: '/value' } },
    { '/value': { source: 'input', pointer: '/value' } },
  ]) assert.throws(() => resolveFrameworkOutput({ outputBindings }, { value: 3 }), error => error.code === 'OUTPUT_BINDING_INVALID');
});

test('published output mapping remains frozen after candidate mapping changes', async t => {
  const { root, bundle, run, workflow } = setup(t);
  const training = await run('training-run');
  const frozen = freezeTarget(root, { ...target, bundle });
  const release = stageRelease(root, { projectId: target.projectId, frozenVersionId: frozen.frozenVersionId, runEvidence: training });
  activateRelease(root, { projectId: target.projectId, releaseId: release.releaseId });
  workflow.steps[1].outputBindings = { '/candidateAnswer': { source: 'output', pointer: '/receivedValue' } };
  applyChanges(root, { projectId: target.projectId, requestId: 'change-mapping', baseRevision: readProject(root, target).revisionId,
    reason: 'candidate-only mapping change', changes: [{ path: 'workflows/lab-pair.json', content: JSON.stringify(workflow) }] });
  const published = loadReleaseBundle(root, target);
  const replay = await run('published-run', published, 'published');
  assert.equal(replay.status, 'completed');
  assert.deepEqual(replay.output, { answer: 8 });
  assert.deepEqual(replay.steps[1].handoffOutput, { answer: 8 });
  assert.equal(published.bundleSha256, bundle.bundleSha256);
});
