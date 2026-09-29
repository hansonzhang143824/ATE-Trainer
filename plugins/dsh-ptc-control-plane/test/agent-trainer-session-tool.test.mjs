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

test('agent-trainer session-tool requires the bound preset and authorizes Trainer tools', async t => {
  const root = fs.mkdtempSync(os.tmpdir() + '/trainer-session-tool-');
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const runner = createFrameworkRunner({
    workspaceRoot: root,
    adapter: { async dispatch() { throw new Error('dispatch is not part of this test'); } },
    verifyBundle: bundles.verifyBundle,
    validateJson,
  });
  const service = createTrainerService({
    workspaceRoot: root,
    runner,
    repositories: { ...projects, ...bundles, ...releases },
    modelResolver: () => ({ provider: 'fake', model: 'fake' }),
    sessionVerifier: async (sessionId, presetId) => sessionId.startsWith('white-native-') && presetId === 'agent-trainer',
  });
  await projects.ensureTrainerProject(root, { projectId: 'pilot', seed: createSyntheticTrainerFixture() });
  const sessionId = 'white-native-session-tool-test';
  const bound = await service.invoke('bind-session', {
    projectId: 'pilot', targetKind: 'agent', targetId: 'lab-producer', mode: 'training',
    presetId: 'agent-trainer', sessionId,
  }, { kind: 'page' });
  assert.equal(bound.ok, true, JSON.stringify(bound));

  const context = await service.invoke('session-tool', { sessionId, presetId: 'agent-trainer', toolOperation: 'context' }, { kind: 'tool', sessionId, presetId: 'agent-trainer' });
  assert.equal(context.ok, true, JSON.stringify(context));
  assert.equal(context.value.binding.targetId, 'lab-producer');
  assert.equal(context.value.project.projectId, 'pilot');

  const assets = await service.invoke('session-tool', { sessionId, presetId: 'agent-trainer', toolOperation: 'assets' }, { kind: 'tool', sessionId, presetId: 'agent-trainer' });
  assert.equal(assets.ok, true, JSON.stringify(assets));
  assert.ok(assets.value.files['agents/lab-producer/instructions.md']);

  const changed = await service.invoke('session-tool', {
    sessionId, presetId: 'agent-trainer', toolOperation: 'apply-changes',
    requestId: 'session-tool-apply-1', baseRevision: context.value.project.revisionId,
    reason: 'session tool authorization test', changes: [{ path: 'agents/lab-producer/instructions.md', content: 'Return the same synthetic value.\n' }],
  }, { kind: 'tool', sessionId, presetId: 'agent-trainer' });
  assert.equal(changed.ok, true, JSON.stringify(changed));
  assert.notEqual(changed.value.revisionId, context.value.project.revisionId);

  const ordinary = await service.invoke('session-tool', { sessionId, presetId: 'standard', toolOperation: 'context' }, { kind: 'tool', sessionId, presetId: 'standard' });
  assert.equal(ordinary.ok, false);
  assert.equal(ordinary.error.code, 'forbidden');
});
