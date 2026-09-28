import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { saveWorkflowTemplate, freezeWorkflowTemplate } from '../lib/workflow-template.js';
import { cloneAgentProfile } from '../lib/agent-profile-runtime.js';
import { createWorkflowTemplateRunner, readWorkflowTemplateRun } from '../lib/workflow-template-run.js';
import { stageWorkflowTemplateRelease, activateWorkflowTemplateRelease,
  loadWorkflowTemplateRelease } from '../lib/workflow-template-release.js';
import { createPublishedWorkflowRunner, readPublishedWorkflowRun } from '../lib/workflow-template-published.js';

const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const json = value => `${JSON.stringify(value, null, 2)}\n`;
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-workflow-run-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  for (const id of ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert', 'method-expert',
    'rule-reviewer', 'ate-implementer', 'compile-diagnostician', 'evolution-expert']) {
    fs.mkdirSync(path.join(root, 'team', 'expert-profiles', id), { recursive: true });
  }
  return root;
}

test('single and eight-Agent template runs use the exact selected step count', async t => {
  for (const ids of [
    ['ptc-dft-expert'],
    ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert', 'method-expert',
      'rule-reviewer', 'ate-implementer', 'compile-diagnostician', 'evolution-expert'],
  ]) {
    const root = fixture(t);
    const version = frozen(root, ids);
    const called = [];
    const started = createWorkflowTemplateRunner(root, fakeProfileSmoke(root, called))
      .start({ templateId: 'pilot', versionSha256: version.versionSha256 });
    await started.completion;
    assert.deepEqual(called, ids);
    assert.equal(readWorkflowTemplateRun(root, started.runId).steps.length, ids.length);
  }
});
function frozen(root, profileIds) {
  const saved = saveWorkflowTemplate(root, { expectedSha256: null, template: {
    templateId: 'pilot', name: 'Pilot', profileIds,
    instruction: '1+2等于几，把答案写在JSON里', expectedAnswer: 3,
  } });
  return freezeWorkflowTemplate(root, { templateId: 'pilot', sha256: saved.sha256 });
}
function fakeProfileSmoke(root, called, answer = 3) {
  return { start({ runId }) {
    const directory = path.join(root, 'Training_Materials', 'runs', runId);
    const stateFile = path.join(directory, 'state.json');
    const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    called.push(state.target.profileId);
    const evidencePath = `Training_Materials/runs/${runId}/evidence/profile-smoke.json`;
    const file = path.join(root, evidencePath);
    const snapshot = path.join(directory, 'profile', 'snapshot.json');
    fs.mkdirSync(path.dirname(snapshot), { recursive: true });
    fs.writeFileSync(snapshot, json({ runId, profileId: state.target.profileId }));
    fs.mkdirSync(path.dirname(file), { recursive: true });
    const evidence = { runId, profileId: state.target.profileId, status: answer === 3 ? 'completed' : 'blocked',
      mode: 'SMOKE_ONLY', businessGatePassed: false, answer,
      profileSnapshotSha256: sha(fs.readFileSync(snapshot)) };
    fs.writeFileSync(file, json(evidence));
    fs.writeFileSync(stateFile, json({ ...state, status: evidence.status,
      outcome: { smokePassed: answer === 3, evidence: evidencePath,
        evidenceSha256: sha(fs.readFileSync(file)) } }));
    return { completion: Promise.resolve() };
  }, stop() {} };
}

test('published workflow execution requires an activated release pointer', t => {
  const root = fixture(t);
  const ctx = {
    agentDefaultModel: { currentSelection: () => ({ provider: 'fake', model: 'fake' }) },
    agents: { create: async () => ({ agent: { whenIdle: async () => {} } }) },
    subagents: { start: async () => ({}) },
  };
  assert.throws(() => createPublishedWorkflowRunner(ctx, root).start(), /ENOENT|no active|workflow release/i);
});

test('ordered arbitrary subset creates fresh real-child references and verified handoffs', async t => {
  const root = fixture(t);
  const version = frozen(root, ['strategy-expert', 'ptc-dft-expert', 'ptc-schematic-expert']);
  const called = [];
  const runner = createWorkflowTemplateRunner(root, fakeProfileSmoke(root, called));
  const started = runner.start({ templateId: 'pilot', versionSha256: version.versionSha256 });
  await started.completion;
  assert.deepEqual(called, ['strategy-expert', 'ptc-dft-expert', 'ptc-schematic-expert']);
  const record = readWorkflowTemplateRun(root, started.runId);
  assert.equal(record.status, 'completed');
  assert.equal(record.smokePassed, true);
  assert.equal(record.businessGatePassed, false);
  assert.equal(record.steps[1].upstreamEvidenceSha256, record.steps[0].evidenceSha256);
  assert.equal(record.steps[2].upstreamEvidenceSha256, record.steps[1].evidenceSha256);
  fs.appendFileSync(path.join(root, record.steps[0].evidencePath), ' ');
  assert.throws(() => readWorkflowTemplateRun(root, started.runId), /evidence changed/);
});

test('a cloned Agent can replace a workflow step and the release records its immutable revision', async t => {
  const root = fixture(t);
  const clone = cloneAgentProfile(root, {
    sourceProfileId: 'ptc-dft-expert', targetProfileId: 'custom-dft-agent', revisionId: 'draft-1',
  });
  assert.equal(clone.profileId, 'custom-dft-agent');
  assert.equal(clone.baseProfileId, 'ptc-dft-expert');
  const version = frozen(root, ['ptc-schematic-expert', 'custom-dft-agent']);
  const called = [];
  const training = createWorkflowTemplateRunner(root, fakeProfileSmoke(root, called))
    .start({ templateId: 'pilot', versionSha256: version.versionSha256 });
  await training.completion;
  const record = readWorkflowTemplateRun(root, training.runId);
  assert.equal(record.status, 'completed');
  assert.equal(record.steps[1].profileId, 'custom-dft-agent');
  assert.equal(record.steps[1].agentRevision, 'draft-1');
  assert.match(record.steps[1].agentManifestSha256, /^[a-f0-9]{64}$/);
  assert.match(record.steps[1].agentContentSha256, /^[a-f0-9]{64}$/);
  assert.deepEqual(called, ['ptc-schematic-expert', 'custom-dft-agent']);

  const staged = stageWorkflowTemplateRelease(root, training.runId);
  const manifest = loadWorkflowTemplateRelease(root, staged.releaseId).manifest;
  assert.equal(manifest.steps[1].profileId, 'custom-dft-agent');
  assert.equal(manifest.steps[1].agentRevision, 'draft-1');
  assert.equal(manifest.businessGatePassed, false);
  activateWorkflowTemplateRelease(root, staged.releaseId, staged.manifestSha256);
  let children = 0;
  const published = createPublishedWorkflowRunner({
    agentDefaultModel: { currentSelection: () => ({ provider: 'fake', model: 'fake' }) },
    agents: { create: async () => ({ agent: { whenIdle: async () => {} }, dispose: async () => {} }) },
    subagents: { start: async () => ({ id: `child-${++children}`,
      result: Promise.resolve({ stopReason: 'completed', structured: { answer: 3 } }), dispose: async () => {} }) },
  }, root).start();
  await published.completion;
  const replay = readPublishedWorkflowRun(root, published.runId);
  assert.equal(replay.status, 'completed');
  assert.equal(replay.steps[1].agentRevision, 'draft-1');
  assert.equal(replay.steps[1].agentManifestSha256, manifest.steps[1].agentManifestSha256);
  assert.equal(replay.steps[1].agentContentSha256, manifest.steps[1].agentContentSha256);
});

test('wrong numeric answer blocks downstream Agent', async t => {
  const root = fixture(t);
  const version = frozen(root, ['ptc-dft-expert', 'strategy-expert']);
  const called = [];
  const runner = createWorkflowTemplateRunner(root, fakeProfileSmoke(root, called, 4));
  const started = runner.start({ templateId: 'pilot', versionSha256: version.versionSha256 });
  const result = await started.completion;
  assert.equal(result.status, 'blocked');
  assert.deepEqual(called, ['ptc-dft-expert']);
});

test('completed arbitrary template freezes, activates and replays from release only', async t => {
  const root = fixture(t);
  const version = frozen(root, ['strategy-expert', 'ptc-dft-expert']);
  const runner = createWorkflowTemplateRunner(root, fakeProfileSmoke(root, []));
  const training = runner.start({ templateId: 'pilot', versionSha256: version.versionSha256 });
  await training.completion;
  const staged = stageWorkflowTemplateRelease(root, training.runId);
  assert.equal(loadWorkflowTemplateRelease(root, staged.releaseId).manifest.steps.length, 2);
  activateWorkflowTemplateRelease(root, staged.releaseId, staged.manifestSha256);
  assert.equal(loadWorkflowTemplateRelease(root).manifest.releaseId, staged.releaseId);
  let children = 0;
  const ctx = {
    agentDefaultModel: { currentSelection: () => ({ provider: 'fake', model: 'fake' }) },
    agents: { create: async () => ({ agent: { whenIdle: async () => {} }, dispose: async () => {} }) },
    subagents: { start: async () => ({ id: `child-${++children}`,
      result: Promise.resolve({ stopReason: 'completed', structured: { answer: 3 } }), dispose: async () => {} }) },
  };
  const published = createPublishedWorkflowRunner(ctx, root).start();
  await published.completion;
  const replay = readPublishedWorkflowRun(root, published.runId);
  assert.equal(replay.status, 'completed');
  assert.equal(replay.smokePassed, true);
  assert.equal(replay.steps.length, 2);
  assert.equal(children, 2);
  assert.equal(replay.steps[1].upstreamEvidenceSha256, replay.steps[0].evidenceSha256);
});

test('pause drains the current child and resume does not repeat it', async t => {
  const root = fixture(t);
  const version = frozen(root, ['ptc-dft-expert', 'strategy-expert']);
  const called = [];
  const fast = fakeProfileSmoke(root, called);
  let releaseFirst;
  const manager = createWorkflowTemplateRunner(root, { start(input) {
    const started = fast.start(input);
    if (called.length === 1) return { completion: new Promise(resolve => { releaseFirst = resolve; }) };
    return started;
  }, stop: fast.stop });
  const first = manager.start({ templateId: 'pilot', versionSha256: version.versionSha256 });
  while (!releaseFirst) await new Promise(resolve => setTimeout(resolve, 0));
  manager.control(first.runId, 'pause');
  releaseFirst();
  await first.completion;
  assert.equal(readWorkflowTemplateRun(root, first.runId).status, 'paused');
  assert.deepEqual(called, ['ptc-dft-expert']);
  const resumed = manager.control(first.runId, 'resume');
  await resumed.completion;
  assert.equal(readWorkflowTemplateRun(root, first.runId).status, 'completed');
  assert.deepEqual(called, ['ptc-dft-expert', 'strategy-expert']);
});
