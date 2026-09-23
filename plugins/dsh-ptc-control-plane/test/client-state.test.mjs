import assert from 'node:assert/strict';
import test from 'node:test';
import { createPtcStateStore, formatTarget, normalizeState } from '../client/state.js';

test('client state follows the server schema and formats structured targets', () => {
  const state = normalizeState({
    schemaVersion: 1,
    identity: 'unbound',
    activeRelease: { releaseId: 'r1', manifestDigest: 'a'.repeat(64), activatedAt: 'now' },
    trainingRuns: [{
      runId: 't1', mode: 'training', status: 'created',
      target: { kind: 'profile', profileId: 'ptc-dft-expert' }, updatedAt: 'now',
    }],
    delivery: null,
    profiles: [],
    migration: { legacyConsoleAbandoned: true, legacyMode: 'training', legacyModeAuthoritative: false },
  });
  assert.equal(state.activeRelease.manifestDigest, 'a'.repeat(64));
  assert.equal(formatTarget(state.trainingRuns[0].target), 'ptc-dft-expert');
  assert.equal(state.delivery, null);
});

test('client store revision changes on data and error notifications', async () => {
  let mode = 'ok';
  const store = createPtcStateStore({
    fetchImpl: async () => mode === 'ok'
      ? { ok: true, json: async () => ({ identity: 'unbound', trainingRuns: [], delivery: null }) }
      : { ok: false, status: 500 },
  });
  assert.equal(store.getRevision(), 0);
  await store.refresh();
  assert.equal(store.getRevision(), 1);
  await store.refresh();
  assert.equal(store.getRevision(), 1, 'unchanged payload must not repaint');
  mode = 'error';
  await store.refresh();
  assert.equal(store.getRevision(), 2, 'errors must repaint the panel');
  assert.match(store.getLastError(), /HTTP 500/);
});
