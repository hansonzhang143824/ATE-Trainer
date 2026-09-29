import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import test from 'node:test';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';
import * as projects from '../lib/trainer-project.js';
import * as bundles from '../lib/trainer-bundle.js';
import * as releases from '../lib/trainer-release.js';
import { createFrameworkRunner } from '../lib/framework-agent-run.js';
import { createTrainerService } from '../lib/trainer-service.js';
import { validateJson } from '../lib/trainer-schema.js';

function setup(t) {
  const root = fs.mkdtempSync(os.tmpdir() + '/trainer-d5-d6-');
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  let child = 0;
  const adapter = { async dispatch({ step, input, onStart }) {
    const childSessionId = `child-${++child}`;
    onStart({ childSessionId, parentSessionId: 'parent-1' });
    const output = step.agentId === 'lab-producer' || step.agentId === 'lab-producer-2'
      ? { value: input.seed + 1, marker: 'v1', scriptMarker: 'script-v1' } : { receivedValue: input.receivedValue };
    return { output, childSessionId, childTerminationConfirmed: true, stopReason: 'completed' };
  } };
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter, verifyBundle: bundles.verifyBundle, validateJson });
  const service = createTrainerService({ workspaceRoot: root, runner,
    repositories: { ...projects, ...bundles, ...releases }, modelResolver: () => ({ provider: 'fake', model: 'fake' }) });
  const page = (operation, input = {}) => service.invoke(operation, { projectId: 'pilot', targetKind: 'workflow', targetId: 'lab-pair', ...input }, { kind: 'page' });
  return { root, runner, page };
}

test('D5 fixes workflow order and Agent revisions in each run', async t => {
  const { root, runner, page } = setup(t);
  await projects.ensureTrainerProject(root, { projectId: 'pilot', seed: createSyntheticTrainerFixture() });
  const context = await page('context');
  const seeded = await page('apply-changes', { requestId: 'd5-seed-1', baseRevision: context.value.project.revisionId,
    reason: 'add a second compatible Agent for ordering validation', changes: [
      { path: 'agents/lab-producer-2/agent.json', content: JSON.stringify({ agentId: 'lab-producer-2', name: 'Synthetic producer 2', instructionsRef: 'agents/lab-producer/instructions.md', skillRefs: ['lab-marker'], toolIds: ['lab-marker'], inputSchemaRef: 'contracts/producer-input.schema.json', outputSchemaRef: 'contracts/producer-output.schema.json' }) },
      { path: 'workflows/lab-pair.json', content: JSON.stringify({ workflowId: 'lab-pair', name: 'Synthetic producer pair', steps: [
        { stepId: 'produce', agentId: 'lab-producer', inputBindings: { '': { source: 'input', pointer: '' } }, timeoutMs: 120000 },
        { stepId: 'produce-2', agentId: 'lab-producer-2', inputBindings: { '': { source: 'input', pointer: '' } }, timeoutMs: 120000 },
      ] }) },
      { path: 'tests/lab-pair.json', content: JSON.stringify({ testId: 'lab-pair', targetKind: 'workflow', targetId: 'lab-pair', cases: [{ input: { seed: 7 }, expected: { value: 8, marker: 'v1', scriptMarker: 'script-v1' } }] }) },
    ] });
  assert.equal(seeded.ok, true, JSON.stringify(seeded));
  const candidateRevision = seeded.value.revisionId;
  const first = await page('run', { requestId: 'd5-run-1', revisionId: candidateRevision, input: { seed: 7 } });
  assert.equal(first.ok, true, JSON.stringify(first));
  await runner.waitForRun({ runId: first.value.runId });
  const firstRun = (await page('runs', { runId: first.value.runId })).value;
  assert.equal(firstRun.status, 'completed', JSON.stringify(firstRun));
  assert.equal(firstRun.workflowRevision, candidateRevision);
  assert.ok(firstRun.steps.every(step => step.agentRevision === candidateRevision));
  assert.deepEqual(firstRun.steps.map(step => step.agentId), ['lab-producer', 'lab-producer-2']);

  const next = await page('apply-changes', { requestId: 'd5-reorder-1', baseRevision: candidateRevision,
    reason: 'reorder workflow steps', changes: [{ path: 'workflows/lab-pair.json', content: JSON.stringify({
      workflowId: 'lab-pair', name: 'Synthetic producer pair', steps: [
        { stepId: 'produce-2', agentId: 'lab-producer-2', inputBindings: { '': { source: 'input', pointer: '' } }, timeoutMs: 120000 },
        { stepId: 'produce', agentId: 'lab-producer', inputBindings: { '': { source: 'input', pointer: '' } }, timeoutMs: 120000 },
      ],
    }) }] });
  assert.equal(next.ok, true, JSON.stringify(next));
  assert.notEqual(next.value.revisionId, candidateRevision);
  const old = await page('run', { requestId: 'd5-run-old', revisionId: candidateRevision, input: { seed: 7 } });
  assert.equal(old.ok, true, JSON.stringify(old));
  await runner.waitForRun({ runId: old.value.runId });
  assert.deepEqual((await page('runs', { runId: old.value.runId })).value.steps.map(step => step.agentId), ['lab-producer', 'lab-producer-2']);
});

test('D6 freezes a verified workflow and engineering reads the release snapshot', async t => {
  const { root, runner, page } = setup(t);
  await projects.ensureTrainerProject(root, { projectId: 'pilot', seed: createSyntheticTrainerFixture() });
  const before = await page('context');
  const training = await page('run', { requestId: 'd6-run-1', input: { seed: 7 } });
  await runner.waitForRun({ runId: training.value.runId });
  const frozen = await page('freeze', { requestId: 'd6-freeze-1', runId: training.value.runId });
  assert.equal(frozen.ok, true, JSON.stringify(frozen));
  const staged = await page('stage-release', { requestId: 'd6-stage-1', frozenVersionId: frozen.value.frozenVersionId, runId: training.value.runId });
  assert.equal(staged.ok, true, JSON.stringify(staged));
  const activated = await page('activate-release', { requestId: 'd6-activate-1', releaseId: staged.value.releaseId });
  assert.equal(activated.ok, true, JSON.stringify(activated));

  const changed = await page('apply-changes', { requestId: 'd6-change-1', baseRevision: before.value.project.revisionId,
    reason: 'candidate rename after publish', changes: [{ path: 'agents/lab-producer/agent.json', content: JSON.stringify({
      agentId: 'lab-producer', name: 'Candidate renamed', instructionsRef: 'agents/lab-producer/instructions.md', skillRefs: ['lab-marker'], toolIds: ['lab-marker'], inputSchemaRef: 'contracts/producer-input.schema.json', outputSchemaRef: 'contracts/producer-output.schema.json',
    }) }] });
  assert.equal(changed.ok, true, JSON.stringify(changed));
  const engineering = await serviceContext(page);
  assert.equal(engineering.value.project.workflows[0].name, 'Synthetic producer → consumer');
  assert.equal(engineering.value.project.agents.find(agent => agent.agentId === 'lab-producer').name, 'Synthetic producer');
  const replay = await page('run', { mode: 'engineering', requestId: 'd6-engineering-1', input: { seed: 7 } });
  assert.equal(replay.ok, true, JSON.stringify(replay));
  await runner.waitForRun({ runId: replay.value.runId });
  const result = (await page('runs', { runId: replay.value.runId })).value;
  assert.equal(result.mode, 'published');
  assert.equal(result.status, 'completed');
  assert.equal(result.releaseId, staged.value.releaseId);
  assert.deepEqual(result.output, { receivedValue: 8 });
});

async function serviceContext(page) { return page('context', { mode: 'engineering' }); }
