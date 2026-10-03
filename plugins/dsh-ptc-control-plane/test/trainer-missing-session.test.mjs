import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { inspectPersistedSession, isMissingPersistedSession, verifyPersistedTrainerSession } from '../lib/trainer-host.js';
import { createTrainerService } from '../lib/trainer-service.js';
import * as projects from '../lib/trainer-project.js';
import * as bundles from '../lib/trainer-bundle.js';
import * as releases from '../lib/trainer-release.js';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';

// B acceptance 8: a target's fixed DSH session disappears (its persisted log is
// gone). DSH SessionPersistence.inspect() then rejects with
// `session "<id>" not found`; the Trainer must treat that as "session gone" and
// re-create the target session instead of failing the request.

const notFound = id => new Error(`session "${id}" not found`);
const TOOLS = ['trainer_context', 'trainer_assets', 'trainer_runs', 'trainer_events', 'trainer_apply_changes', 'trainer_validate', 'trainer_run', 'trainer_control', 'trainer_compare'];
const args = { projectId: 'agent-trainer', mode: 'training', targetKind: 'agent', targetId: 'lab-producer', presetId: 'agent-trainer' };

test('inspectPersistedSession maps DSH "session not found" to null and keeps other errors', async () => {
  const inspection = { meta: { id: 'session-a', agentPreset: 'agent-trainer' }, events: [] };
  const ctx = { sessionPersistence: { inspect: async id => {
    if (id === 'session-a') return inspection;
    if (id === 'session-gone') throw notFound(id);
    if (id === 'session-other-message') throw notFound('session-unrelated');
    throw new Error('EACCES: permission denied, open session.jsonl.zstd');
  } } };
  assert.equal(await inspectPersistedSession(ctx, 'session-a'), inspection);
  assert.equal(await inspectPersistedSession(ctx, 'session-gone'), null);
  await assert.rejects(inspectPersistedSession(ctx, 'session-other-message'), /session-unrelated/);
  await assert.rejects(inspectPersistedSession(ctx, 'session-io'), /EACCES/);
  assert.equal(await inspectPersistedSession({}, 'session-a'), null);
  assert.equal(isMissingPersistedSession(notFound('session-x'), 'session-x'), true);
  assert.equal(isMissingPersistedSession(new Error('timeout'), 'session-x'), false);
});

test('persisted session existence wins over a stale in-memory workspace shell', async () => {
  const sessionId = 'session-gone';
  const missingPath = path.join(os.tmpdir(), `ptc-missing-${sessionId}.jsonl.zstd`);
  const ctx = {
    sessions: new Map([[sessionId, { header: { id: sessionId, cwd: 'C:\\workspace', agentPreset: 'agent-trainer' } }]]),
    sessionPersistence: {
      locate: () => ({ kind: 'jsonl', path: missingPath }),
      // DSH's inspect() returns the live object before it checks disk. This is
      // the stale-shell condition that the location check must override.
      inspect: async () => ({ meta: { id: sessionId, agentPreset: 'agent-trainer' }, events: [] }),
    },
  };
  const result = await verifyPersistedTrainerSession(ctx, sessionId, new Set([sessionId]));
  assert.equal(result.authoritative, true);
  assert.equal(result.persisted, null);
  assert.equal(result.exists, false);
  const fresh = await verifyPersistedTrainerSession(ctx, sessionId, new Set());
  assert.equal(fresh.exists, true, 'a newly created live session may not have materialized its log yet');
});

test('a removed fixed session is re-created: target-session answers null, open creates a new session, old binding stays', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-missing-session-'));
  const persisted = new Set();
  // Same verification shape as trainer-host: a persisted log that DSH cannot find is "not this preset".
  const ctx = { sessionPersistence: { inspect: async id => {
    if (!persisted.has(id)) throw notFound(id);
    return { meta: { id, agentPreset: 'agent-trainer' }, events: [] };
  } } };
  const sessionVerifier = async (id, presetId) => (await inspectPersistedSession(ctx, id))?.meta?.agentPreset === presetId;
  let created = 0;
  try {
    await projects.ensureTrainerProject(root, { projectId: 'agent-trainer', seed: createSyntheticTrainerFixture() });
    const service = createTrainerService({ workspaceRoot: root, runner: { listRuns: () => ({ runs: [] }) },
      repositories: { ...projects, ...bundles, ...releases }, modelResolver: () => ({ provider: 'fake', model: 'fake' }),
      sessionVerifier, sessionToolCatalog: async () => TOOLS,
      sessionFactory: async () => { created += 1; const id = `session-${created}`; persisted.add(id); return id; },
    });
    const first = await service.invoke('open-native-session', args, { kind: 'page' });
    assert.equal(first.ok, true, JSON.stringify(first));
    const oldId = first.value.sessionId;
    const bindingPath = path.join(root, 'Training_Materials/framework/control/bindings', `${oldId}.json`);
    const oldBinding = fs.readFileSync(bindingPath, 'utf8');

    persisted.delete(oldId); // the session log disappears from DSH

    const lookup = await service.invoke('target-session', args, { kind: 'page' });
    assert.equal(lookup.ok, true, `target-session must not fail: ${JSON.stringify(lookup)}`);
    assert.equal(lookup.value, null);
    const unbound = await service.invoke('bind-session', { projectId: args.projectId, mode: args.mode, sessionId: oldId }, { kind: 'page' });
    assert.equal(unbound.ok, false);
    assert.equal(unbound.error?.code, 'session_unbound', JSON.stringify(unbound));

    const reopened = await service.invoke('open-native-session', args, { kind: 'page' });
    assert.equal(reopened.ok, true, JSON.stringify(reopened));
    assert.equal(reopened.value.reused, false);
    assert.notEqual(reopened.value.sessionId, oldId);
    assert.equal(created, 2);
    const record = await service.invoke('target-session', args, { kind: 'page' });
    assert.equal(record.value.sessionId, reopened.value.sessionId);
    assert.equal(fs.readFileSync(bindingPath, 'utf8'), oldBinding, 'the old binding file is kept unchanged');

    const again = await service.invoke('open-native-session', args, { kind: 'page' });
    assert.equal(again.value.reused, true);
    assert.equal(again.value.sessionId, reopened.value.sessionId);
    assert.equal(created, 2);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
