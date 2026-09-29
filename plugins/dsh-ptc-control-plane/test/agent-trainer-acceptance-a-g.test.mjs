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

  const three = run('Training_Materials/runs/framework-c87b035e-e425-4725-b500-82763857fbf4/framework-run.json');
  assert.deepEqual(three.steps.map(step => step.agentId), ['agent-T1', 'agent-T2', 'agent-T3']);
  assert.deepEqual(three.steps.map(step => step.output.answer), [3, 5, 7]);
  assert.ok(three.steps.every(step => step.status === 'completed' && step.validation.ok));

  const reordered = run('Training_Materials/runs/framework-785f9dae-153c-4a83-8639-bbe93a66e646/framework-run.json');
  assert.deepEqual(reordered.steps.map(step => step.agentId), ['agent-T3', 'agent-T1', 'agent-T2']);
  assert.deepEqual(reordered.steps.map(step => step.output.answer), [7, 3, 5]);
  assert.notEqual(reordered.workflowRevision, three.workflowRevision);

  const release = readJson('publish/versions/release-9403c386-05d9-49bb-a562-2a920efb28cc/release.json');
  assert.equal(release.businessGatePassed, false);
  assert.equal(release.targetId, 'workflow-T1');
  sha256(release.bundleSha256);
  sha256(release.evidenceSha256);
  assert.deepEqual(release.agentBindings.map(binding => binding.agentId), ['agent-T3', 'agent-T1', 'agent-T2']);

  for (const id of ['framework-21edf523-af52-4a3a-9de4-d8cd5dc5ba10', 'framework-08b87c84-02a1-4b91-98b0-b29e4835ec92']) {
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
  assert.equal(evidence.actualUiClicks.D.status, 'blocked_missing_independent_two_agent_run');
  assert.equal(evidence.actualUiClicks.G.isolationVerified, true);
  assert.equal(evidence.d7.status, 'blocked_by_native_host_and_missing_d_run');
  assert.equal(evidence.d7.checkpointFiles.length, 6);
  for (const checkpoint of evidence.d7.checkpointFiles) assert.ok(fs.existsSync(path.join(root, checkpoint)), checkpoint);
});

test('D5-D6 persisted runs retain step-level revisions and release hashes', () => {
  const reordered = run('Training_Materials/runs/framework-785f9dae-153c-4a83-8639-bbe93a66e646/framework-run.json');
  const steps = stepMap(reordered);
  assert.equal(steps.get('agent-T3').agentRevision, reordered.workflowRevision);
  assert.equal(steps.get('agent-T1').agentRevision, reordered.workflowRevision);
  assert.equal(steps.get('agent-T2').agentRevision, reordered.workflowRevision);
  assert.ok(reordered.steps.every(step => step.inputValidation.ok && step.validation.ok));
  const verification = readJson('publish/versions/release-9403c386-05d9-49bb-a562-2a920efb28cc/verification.json');
  assert.equal(verification.status, 'completed');
  assert.equal(verification.validation.ok, true);
  assert.deepEqual(verification.steps.map(step => step.agentId), ['agent-T3', 'agent-T1', 'agent-T2']);
});
