/**
 * P0-B: Captain's INPUT_SYNC source dispatch, pinned to a published expert
 * profile where one is configured — and explicitly refused (never silently
 * unpinned) where pinning is configured but cannot be satisfied.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { fileURLToPath } from 'node:url';
import { startRequiredSourceDispatches } from '../lib/captain-entry.js';
import { listReceipts } from '../lib/dispatch-profile.js';

const PLUGIN_DIR = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const REPO_ROOT = path.resolve(PLUGIN_DIR, '..', '..');
const PROFILE_ID = 'ptc-dft-expert';

const workspaces = [];
function workspaceWithProfile(withProfile = true) {
  const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-pinned-')));
  fs.mkdirSync(path.join(ws, 'team'), { recursive: true });
  if (withProfile) {
    fs.cpSync(path.join(REPO_ROOT, 'team', 'expert-profiles', PROFILE_ID), path.join(ws, 'team', 'expert-profiles', PROFILE_ID), { recursive: true });
  }
  fs.cpSync(path.join(REPO_ROOT, 'team', 'ptc'), path.join(ws, 'team', 'ptc'), { recursive: true });
  workspaces.push(ws);
  return ws;
}

function fakeContext() {
  const calls = [];
  const warnings = [];
  return {
    calls,
    warnings,
    logger: { warn: (message) => warnings.push(message), info() {}, error() {} },
    subagents: {
      getProvider: (name) => (name === 'spawn' ? { name: 'spawn' } : undefined),
      start: async (provider, request) => {
        calls.push({ provider, request });
        return { id: `child-${calls.length}`, result: Promise.resolve({ stopReason: 'completed' }) };
      },
    },
  };
}

const dispatchInput = () => ({
  state: 'INPUT_SYNC',
  batchId: 'batch-tm106',
  dispatches: [
    { role: 'dft-expert', tms: ['TM106'], trialDirs: { TM106: 'team/artifacts/tm106-ptc' } },
    { role: 'schematic-expert', tms: ['TM106'], trialDirs: { TM106: 'team/artifacts/tm106-ptc' } },
  ],
});

after(() => {
  for (const ws of workspaces) fs.rmSync(ws, { recursive: true, force: true });
});

test('with no pinnedProfiles configured the dispatch is unchanged and the gap is reported', async () => {
  const ws = workspaceWithProfile();
  const ctx = fakeContext();
  const runs = await startRequiredSourceDispatches(ctx, dispatchInput(), { id: 'captain' }, undefined, { workspaceRoot: ws });
  assert.equal(ctx.calls.length, 2);
  assert.deepEqual(ctx.calls.map(({ request }) => request.label), ['PTC dft expert [TM106]', 'PTC schematic expert']);
  assert.deepEqual(runs.unpinnedRoles, ['dft-expert', 'schematic-expert'], 'unpinned roles must be reported, not assumed');
  assert.equal(listReceipts(ws).length, 0, 'an unpinned dispatch writes no receipt');
});

test('a configured role is dispatched through the pinned published profile', async () => {
  const ws = workspaceWithProfile();
  const ctx = fakeContext();
  const runs = await startRequiredSourceDispatches(ctx, dispatchInput(), { id: 'captain' }, undefined, {
    workspaceRoot: ws,
    pinnedProfiles: { 'dft-expert': PROFILE_ID },
    checkDftReuse: async () => ({ unchanged: false, reports: [] }),
  });
  assert.equal(ctx.calls.length, 2, 'the schematic role still dispatches');
  const pinned = ctx.calls.find(({ request }) => request.maxDepth === 1)?.request;
  assert.ok(pinned, 'the pinned child is the one dispatched with maxDepth 1');
  assert.equal(pinned.label, 'PTC dft expert [TM106]');
  assert.match(pinned.persona, /executionClass input-dft/);
  assert.ok(pinned.outputSchema?.required, 'the pinned dispatch must carry an outputSchema');
  const unpinned = ctx.calls.find(({ request }) => request.maxDepth !== 1)?.request;
  assert.equal(unpinned.label, 'PTC schematic expert', 'the unpinned role keeps the historical label dispatch');
  assert.deepEqual(runs.unpinnedRoles, ['schematic-expert']);
  const receipts = listReceipts(ws, 'batch-tm106');
  assert.equal(receipts.length, 1);
  assert.equal(receipts[0].profileId, PROFILE_ID);
  assert.deepEqual(receipts[0].targetTms, ['TM106']);
  assert.ok(receipts[0].childSessionId, 'the receipt records which child it pins');
});

test('when a configured role cannot be pinned, no unpinned child starts and the stage must not advance', async () => {
  const ws = workspaceWithProfile(false); // no expert profiles in this workspace
  const ctx = fakeContext();
  const runs = await startRequiredSourceDispatches(ctx, dispatchInput(), { id: 'captain' }, undefined, {
    workspaceRoot: ws,
    pinnedProfiles: { 'dft-expert': PROFILE_ID },
    checkDftReuse: async () => ({ unchanged: false, reports: [] }),
  });
  assert.deepEqual(ctx.calls.map(({ request }) => request.label), ['PTC schematic expert'], 'the DFT role must not fall back to an unpinned child');
  assert.match(ctx.warnings.join('\n'), /pinned dispatch refused/);
  const settled = await runs[0].result;
  assert.equal(settled.stopReason, 'refused');
  assert.match(settled.diagnostic, /no expert profile/);
  assert.deepEqual(runs.unpinnedRoles, ['schematic-expert']);
});

test('a pinned dispatch carries the receipt into the run it returns so the guard can match it', async () => {
  const ws = workspaceWithProfile();
  const ctx = fakeContext();
  await startRequiredSourceDispatches(ctx, dispatchInput(), { id: 'captain' }, undefined, {
    workspaceRoot: ws,
    pinnedProfiles: { 'dft-expert': PROFILE_ID },
    checkDftReuse: async () => ({ unchanged: false, reports: [] }),
  });
  const pinnedChild = ctx.calls.findIndex(({ request }) => request.maxDepth === 1) + 1;
  const receipts = listReceipts(ws);
  assert.equal(receipts.length, 1);
  assert.equal(receipts[0].childSessionId, `child-${pinnedChild}`, 'the receipt must pin the child that was actually started');
});
