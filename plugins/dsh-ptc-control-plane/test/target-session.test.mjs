import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createTrainerService } from '../lib/trainer-service.js';
import * as projects from '../lib/trainer-project.js';
import * as bundles from '../lib/trainer-bundle.js';
import * as releases from '../lib/trainer-release.js';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';

const args = { projectId: 'agent-trainer', mode: 'training', targetKind: 'agent', targetId: 'lab-producer', presetId: 'agent-trainer' };

test('target-session persists, reads, and forgets without deleting bindings', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-target-session-'));
  const sessions = new Set();
  try {
    await projects.ensureTrainerProject(root, { projectId: 'agent-trainer', seed: createSyntheticTrainerFixture() });
    const service = createTrainerService({ workspaceRoot: root, runner: { listRuns: () => ({ runs: [] }) },
      repositories: { ...projects, ...bundles, ...releases }, modelResolver: () => ({ provider: 'fake', model: 'fake' }),
      sessionVerifier: async id => sessions.has(id),
      sessionToolCatalog: async () => ['trainer_context','trainer_assets','trainer_runs','trainer_events','trainer_apply_changes','trainer_validate','trainer_run','trainer_control','trainer_compare'],
      sessionFactory: async () => { const id = `session-${sessions.size + 1}`; sessions.add(id); return id; },
    });
    const opened = await service.invoke('open-native-session', args, { kind: 'page' });
    assert.equal(opened.ok, true, JSON.stringify(opened));
    const record = await service.invoke('target-session', args, { kind: 'page' });
    assert.equal(record.ok, true); assert.equal(record.value.sessionId, opened.value.sessionId);
    assert.equal(record.value.targetKind, 'agent'); assert.equal(record.value.lastResolved.source, 'candidate');
    const bindingPath = path.join(root, 'Training_Materials/framework/control/bindings', `${opened.value.sessionId}.json`);
    assert.equal(fs.existsSync(bindingPath), true);
    const forgotten = await service.invoke('forget-target-session', args, { kind: 'page' });
    assert.deepEqual(forgotten.value, { forgotten: true });
    assert.equal(fs.existsSync(bindingPath), true);
    assert.equal((await service.invoke('target-session', args, { kind: 'page' })).value, null);
    assert.deepEqual((await service.invoke('forget-target-session', args, { kind: 'page' })).value, { forgotten: false });
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
