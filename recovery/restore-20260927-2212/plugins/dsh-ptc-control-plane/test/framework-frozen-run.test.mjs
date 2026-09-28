import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createFrameworkRunner } from '../lib/framework-agent-run.js';
import { ensureTrainerProject, applyChanges } from '../lib/trainer-project.js';
import { resolveBundle, freezeTarget } from '../lib/trainer-bundle.js';
import { createSyntheticTrainerFixture, createEightRoleSyntheticFixture, SYNTHETIC_ROLE_CATALOG } from '../lib/trainer-synthetic-fixture.js';

function rootFor(t) { const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-frozen-run-')); t.after(() => fs.rmSync(root, { recursive: true, force: true })); return root; }
const model = name => ({ provider: 'fake', model: name });

test('B/C integration: two frozen versions of the same Agent isolate matching schema IDs and model configuration', async t => {
  const root = rootFor(t); const seed = createSyntheticTrainerFixture();
  const outputRef = 'contracts/producer-output.schema.json';
  const schema = JSON.parse(seed.files[outputRef]); schema.$id = 'urn:synthetic:producer-output'; schema.properties.marker.const = 'v1'; seed.files[outputRef] = JSON.stringify(schema);
  let project = ensureTrainerProject(root, { projectId: 'synthetic-lab', seed });
  const target = { projectId: project.projectId, targetKind: 'agent', targetId: 'lab-producer' };
  const one = resolveBundle(root, { ...target, model: model('model-v1') });
  const frozenOne = freezeTarget(root, { ...target, bundle: one });
  schema.properties.marker.const = 'v2';
  const changed = applyChanges(root, { projectId: project.projectId, baseRevision: project.revisionId, requestId: 'marker-v2', reason: 'synthetic version two', changes: [
    { path: outputRef, content: JSON.stringify(schema) },
    { path: 'skills/lab-marker/references/marker.json', content: JSON.stringify({ marker: 'v2' }) },
  ] });
  const two = resolveBundle(root, { ...target, model: model('model-v2') });
  const frozenTwo = freezeTarget(root, { ...target, bundle: two });
  const workflow = { workflowId: 'frozen-pair', name: 'Two versions of one role', steps: [
    { stepId: 'old', agentId: 'lab-producer', agentVersion: { kind: 'frozen', frozenVersionId: frozenOne.frozenVersionId }, inputBindings: { '/seed': { source: 'input', pointer: '/seed' } } },
    { stepId: 'new', agentId: 'lab-producer', agentVersion: { kind: 'frozen', frozenVersionId: frozenTwo.frozenVersionId }, inputBindings: { '/seed': { source: 'step', stepId: 'old', pointer: '/value' } } },
  ] };
  applyChanges(root, { projectId: project.projectId, baseRevision: changed.revisionId, requestId: 'frozen-flow', reason: 'synthetic frozen workflow', changes: [{ path: 'workflows/frozen-pair.json', content: JSON.stringify(workflow) }] });
  const bundle = resolveBundle(root, { projectId: project.projectId, targetKind: 'workflow', targetId: 'frozen-pair', model: model('unused-default') });
  assert.equal(bundle.steps[0].model.model, 'model-v1'); assert.equal(bundle.steps[1].model.model, 'model-v2');
  fs.rmSync(path.join(root, 'Training_Materials'), { recursive: true });
  const calls = [];
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: { async dispatch(args) {
    calls.push(args);
    const childSessionId = `frozen-child-${args.step.stepId}`; args.onStart({ parentSessionId: 'synthetic-parent', childSessionId });
    const skill = args.bundle.skills[args.step.skillRefs[0]];
    const marker = JSON.parse(args.bundle.files.find(file => file.path === skill.referenceRefs[0]).content).marker;
    return { childSessionId, childTerminationConfirmed: true, stopReason: 'completed', output: { value: args.input.seed + 1, marker, scriptMarker: 'fake-script' } };
  } } });
  await runner.startRun({ runId: 'two-frozen', requestId: 'run-frozen', bundle, mode: 'published', input: { seed: 7 } });
  const run = await runner.waitForRun({ runId: 'two-frozen' });
  assert.equal(run.status, 'completed', JSON.stringify(run.error));
  assert.deepEqual(run.steps.map(step => step.output.marker), ['v1', 'v2']); assert.equal(run.output.value, 9);
  assert.deepEqual(run.steps.map(step => step.model.model), ['model-v1', 'model-v2']); assert.equal(calls.length, 2);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials')), false);
});

test('B/C integration: configured eight roles and a ninth role need no runner whitelist', async t => {
  const root = rootFor(t);
  const roles = [...SYNTHETIC_ROLE_CATALOG, { agentId: 'lab-ninth', name: 'Ninth synthetic role' }];
  ensureTrainerProject(root, { projectId: 'synthetic-scale', seed: createEightRoleSyntheticFixture({ roles }) });
  const bundle = resolveBundle(root, { projectId: 'synthetic-scale', targetKind: 'workflow', targetId: 'synthetic-eight', model: model('scale-fake') });
  const seen = [];
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter: { async dispatch(args) {
    seen.push(args.step.agentId); const childSessionId = `scale-${args.step.stepId}`; args.onStart({ parentSessionId: 'scale-parent', childSessionId });
    return { childSessionId, childTerminationConfirmed: true, output: { value: args.input.value + 1, marker: `${args.step.agentId}-v1` } };
  } } });
  await runner.startRun({ runId: 'nine-roles', requestId: 'run-nine', bundle, input: { value: 10 }, mode: 'training' });
  const run = await runner.waitForRun({ runId: 'nine-roles' }); assert.equal(run.status, 'completed', JSON.stringify(run.error));
  assert.deepEqual(seen, roles.map(role => role.agentId)); assert.equal(run.output.value, 19); assert.equal(new Set(run.steps.map(step => step.childSessionId)).size, 9);
});
