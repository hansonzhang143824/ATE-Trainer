import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

function findRoot() {
  let current = process.cwd();
  for (let i = 0; i < 5; i += 1) {
    if (fs.existsSync(path.join(current, 'team', 'ptc', 'ptc_stage_registry.json'))) return current;
    current = path.dirname(current);
  }
  throw new Error('repository root not found');
}

const root = findRoot();
const readJson = relative => JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'));
const sha256 = value => assert.match(value, /^[0-9a-f]{64}$/);
const run = relative => readJson(relative);

function stepMap(record) {
  return new Map(record.steps.map(step => [step.agentId, step]));
}

test('A-G acceptance artifacts prove persisted Agent Trainer behavior', () => {
  const registry = readJson('team/ptc/ptc_stage_registry.json');
  assert.deepEqual(registry.stateMachine, []);
  assert.deepEqual(registry.stages, {});

  const single = run('Training_Materials/runs/framework-a988a655-21b4-4898-93a0-9a082198891d/framework-run.json');
  assert.equal(single.status, 'completed');
  assert.equal(single.steps[0].agentId, 'agent-T1');
  assert.equal(single.steps[0].output.answer, 3);
  assert.equal(single.validation.ok, true);

  const optimized = run('Training_Materials/runs/framework-4daa41e0-09b0-42a9-9011-9d2eefaae7da/framework-run.json');
  assert.equal(optimized.steps[0].agentId, 'agent-T1');
  assert.equal(optimized.steps[0].output.answer, 5);
  assert.notEqual(optimized.steps[0].agentRevision, single.steps[0].agentRevision);
  assert.equal(optimized.businessGatePassed, false);

  const native = readJson('Training_Materials/framework/control/requests/agent-trainer/native-session-evidence-20260929.json');
  assert.equal(native.presetId, 'agent-trainer');
  assert.match(native.sessionId, /^white-native-/);
  assert.deepEqual(native.toolSequence.map(item => item.tool), [
    'trainer_context', 'trainer_assets', 'trainer_apply_changes', 'trainer_apply_changes',
  ]);
  assert.equal(native.ordinarySessionReuse, false);
  assert.equal(native.toolSequence[2].newRevision, optimized.steps[0].agentRevision);

  const two = run('Training_Materials/runs/framework-282d0db2-de6a-43db-872f-833bb4ff0d78/framework-run.json');
  assert.deepEqual(two.steps.map(step => step.agentId), ['agent-T1', 'agent-T2']);
  assert.deepEqual(two.steps.map(step => step.output.answer), [3, 5]);
  assert.ok(two.steps.every(step => step.status === 'completed' && step.validation.ok));

  const currentThree = run('Training_Materials/runs/framework-f75373f8-8022-4513-8cb8-0809bb593a08/framework-run.json');
  assert.deepEqual(currentThree.steps.map(step => step.agentId), ['agent-T1', 'agent-T2', 'agent-T3']);
  assert.deepEqual(currentThree.steps.map(step => step.output.answer), [3, 5, 7]);
  assert.ok(currentThree.steps.every(step => step.status === 'completed' && step.validation.ok));

  const reordered = run('Training_Materials/runs/framework-9ea1d10b-54e9-45d8-8425-537d4a4cefb9/framework-run.json');
  assert.deepEqual(reordered.steps.map(step => step.agentId), ['agent-T3', 'agent-T1', 'agent-T2']);
  assert.deepEqual(reordered.steps.map(step => step.output.answer), [7, 3, 5]);
  assert.notEqual(reordered.workflowRevision, currentThree.workflowRevision);

  const release = readJson('publish/versions/release-95a32837-bd2e-4929-9364-4d9c2165091d/release.json');
  assert.equal(release.businessGatePassed, false);
  assert.equal(release.targetId, 'workflow-T1');
  sha256(release.bundleSha256);
  sha256(release.evidenceSha256);
  assert.deepEqual(release.agentBindings.map(binding => binding.agentId), ['agent-T3', 'agent-T1', 'agent-T2']);

  for (const id of ['framework-7712f931-9f9e-4cf9-beca-982c4f3f71f9', 'framework-4ca40d40-433e-4b04-a7e2-a3a7420e8d70']) {
    const published = run(`publish/runs/${id}/framework-run.json`);
    assert.equal(published.mode, 'published');
    assert.equal(published.releaseId, release.releaseId);
    assert.equal(published.status, 'completed');
    assert.deepEqual(published.steps.map(step => step.agentId), ['agent-T3', 'agent-T1', 'agent-T2']);
    assert.deepEqual(published.steps.map(step => step.output.answer), [7, 3, 5]);
    assert.equal(published.validation.ok, true);
    assert.equal(published.businessGatePassed, false);
  }

  const evidence = readJson('docs/agent-trainer-acceptance-evidence-20260929.json');
  assert.equal(evidence.actualUiClicks.D.status, 'passed');
  assert.equal(evidence.actualUiClicks.G.isolationVerified, true);
  assert.equal(evidence.d7.status, 'passed_with_environment_note');
  assert.equal(evidence.d7.checkpointFiles.length, 6);
  for (const checkpoint of evidence.d7.checkpointFiles) assert.ok(fs.existsSync(path.join(root, checkpoint)), checkpoint);
});

test('D5-D6 persisted runs retain step-level revisions and release hashes', () => {
  const reordered = run('Training_Materials/runs/framework-9ea1d10b-54e9-45d8-8425-537d4a4cefb9/framework-run.json');
  const steps = stepMap(reordered);
  assert.equal(steps.get('agent-T3').agentRevision, reordered.workflowRevision);
  assert.equal(steps.get('agent-T1').agentRevision, reordered.workflowRevision);
  assert.equal(steps.get('agent-T2').agentRevision, reordered.workflowRevision);
  assert.ok(reordered.steps.every(step => step.inputValidation.ok && step.validation.ok));
  const verification = readJson('publish/versions/release-95a32837-bd2e-4929-9364-4d9c2165091d/verification.json');
  assert.equal(verification.status, 'completed');
  assert.equal(verification.validation.ok, true);
  assert.deepEqual(verification.steps.map(step => step.agentId), ['agent-T3', 'agent-T1', 'agent-T2']);
});
