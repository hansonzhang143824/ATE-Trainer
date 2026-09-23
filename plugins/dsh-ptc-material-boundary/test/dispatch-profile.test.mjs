/**
 * P0-B: the host-side `dispatch_profile` dispatcher.
 *
 * The fixture copies the REAL published `ptc-dft-expert@v1` (written by
 * `publish_expert_profile.py`) into a temporary workspace, so the manifest
 * verification is exercised against genuine Python-written hashes rather than
 * hashes this test invented.
 */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { fileURLToPath } from 'node:url';
import {
  dispatchProfile,
  findReceiptForChild,
  listReceipts,
  registryOwnership,
  resolvePublishedProfile,
} from '../lib/dispatch-profile.js';
import { verifyDispatchReceipt, receiptDigest } from '../lib/dispatch-receipt.js';

const PLUGIN_DIR = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const REPO_ROOT = path.resolve(PLUGIN_DIR, '..', '..');
const PROFILE_ID = 'ptc-dft-expert';

const workspaces = [];
function freshWorkspace() {
  const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-dispatch-')));
  fs.mkdirSync(path.join(ws, 'team'), { recursive: true });
  fs.cpSync(path.join(REPO_ROOT, 'team', 'expert-profiles', PROFILE_ID), path.join(ws, 'team', 'expert-profiles', PROFILE_ID), { recursive: true });
  fs.cpSync(path.join(REPO_ROOT, 'team', 'ptc'), path.join(ws, 'team', 'ptc'), { recursive: true });
  workspaces.push(ws);
  ensureRuntimeLabel(ws);
  return ws;
}

/**
 * The fixture copies the REAL published snapshot (so the manifest hashes under
 * test were genuinely written by the Python publisher). If that snapshot predates
 * `runtimeLabel`, the fixture adds it and re-hashes, so this suite depends on its
 * own fixture rather than on which version happens to be published right now —
 * otherwise evaluating a draft would require the suite to pass, and the suite
 * would require the draft to be published first.
 */
function ensureRuntimeLabel(ws) {
  const file = snapshotFile(ws, 'profile.yaml');
  const text = fs.readFileSync(file, 'utf8');
  if (/^runtimeLabel:/m.test(text)) return;
  fs.writeFileSync(file, `${text.trimEnd()}\nruntimeLabel: PTC dft expert [<TM>]\n`, 'utf8');
  rehashSnapshot(ws);
}

const statusFile = (ws) => path.join(ws, 'team', 'expert-profiles', PROFILE_ID, 'status.json');
const readStatus = (ws) => JSON.parse(fs.readFileSync(statusFile(ws), 'utf8'));
const writeStatus = (ws, value) => fs.writeFileSync(statusFile(ws), `${JSON.stringify(value, null, 2)}\n`, 'utf8');
// Resolved from status.json, so the suite keeps working as versions are published.
const publishedVersion = (ws) => readStatus(ws).publishedVersion;
const snapshotRoot = (ws) => path.join(ws, 'team', 'expert-profiles', PROFILE_ID, 'versions', publishedVersion(ws));
const snapshotFile = (ws, relative) => path.join(snapshotRoot(ws), relative);

function fakeContext() {
  const captured = [];
  return {
    captured,
    subagents: {
      getProvider: (name) => (name === 'spawn' ? { name: 'spawn' } : undefined),
      start: async (provider, request) => {
        captured.push({ provider, request });
        return { id: 'child-session-uuid-1', result: Promise.resolve({ stopReason: 'completed' }) };
      },
    },
  };
}

const dispatch = (ws, ctx, overrides = {}) => dispatchProfile({
  ctx,
  workspaceRoot: ws,
  profileId: PROFILE_ID,
  runId: 'run-tm106',
  targetTms: ['TM106'],
  task: 'Produce the DFT artifacts for TM106.',
  parent: { id: 'parent-session' },
  createdAt: '2026-09-19T12:00:00.000Z',
  checkDftReuse: async () => ({ unchanged: false, reports: [] }),
  ...overrides,
});

/**
 * Re-hash a published snapshot after a deliberate edit, mirroring the Python
 * publisher's digest (sha256 over canonical JSON of the file map). Used to test
 * the checks that run AFTER snapshot integrity — an unrehashed edit is caught by
 * the drift check first, which is a different refusal.
 */
function rehashSnapshot(ws) {
  const snapshot = snapshotRoot(ws);
  const manifestPath = path.join(snapshot, 'manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const files = {};
  for (const relative of Object.keys(manifest.files)) {
    files[relative] = sha256File(path.join(snapshot, relative));
  }
  const digest = createHash('sha256').update(JSON.stringify(files), 'utf8').digest('hex');
  fs.writeFileSync(manifestPath, `${JSON.stringify({ ...manifest, files, digest }, null, 2)}\n`, 'utf8');
  writeStatus(ws, { ...readStatus(ws), manifestDigest: digest });
  return digest;
}

function sha256File(file) {
  return createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

after(() => {
  for (const ws of workspaces) fs.rmSync(ws, { recursive: true, force: true });
});

// ── resolution and snapshot integrity ──────────────────────────────────────

test('a published profile resolves against the publisher-written manifest hashes', () => {
  const ws = freshWorkspace();
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, true, resolved.reason);
  assert.equal(resolved.version, publishedVersion(ws));
  assert.match(resolved.version, /^v[0-9]+$/);
  assert.equal(resolved.executionClass, 'input-dft');
  assert.equal(resolved.declaredStage, 'INPUT_SYNC');
  assert.match(resolved.persona, /executionClass input-dft/);
  assert.match(resolved.persona, /may read only/i);
  assert.ok(resolved.policy.writable.includes('project/DALI/Output_Global_Material/dft/<TM>'));
});

test('a published profile without a boundary-recognisable runtimeLabel is refused, not defaulted', () => {
  const ws = freshWorkspace();
  const file = snapshotFile(ws, 'profile.yaml');
  const text = fs.readFileSync(file, 'utf8').split('\n').filter((line) => !line.startsWith('runtimeLabel:')).join('\n');
  fs.writeFileSync(file, text, 'utf8');
  rehashSnapshot(ws);
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /runtimeLabel/);
  assert.equal(fs.existsSync(snapshotFile(ws, 'profile.yaml')), true, 'the profile file itself is untouched by the refusal');
});

test('a profile with nothing published is refused, and never falls back to the draft', () => {
  const ws = freshWorkspace();
  writeStatus(ws, { ...readStatus(ws), publishedVersion: null });
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /nothing is published/);
});

test('a published snapshot that drifted from its manifest is refused', () => {
  const ws = freshWorkspace();
  fs.writeFileSync(snapshotFile(ws, 'instructions.md'), 'tampered after publish\n', 'utf8');
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /drifted/);
  assert.match(resolved.reason, /instructions\.md/);
});

test('a status digest that disagrees with the manifest is refused', () => {
  const ws = freshWorkspace();
  writeStatus(ws, { ...readStatus(ws), manifestDigest: 'f'.repeat(64) });
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /digest does not match the manifest/);
});

test('an executionClass that the code registry does not map to this profile is refused', () => {
  const ws = freshWorkspace();
  const file = snapshotFile(ws, 'profile.yaml');
  const text = fs.readFileSync(file, 'utf8').replace('executionClass: input-dft', 'executionClass: input-schematic');
  fs.writeFileSync(file, text, 'utf8');
  rehashSnapshot(ws); // so the refusal is the class check, not the drift check
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /policy registry maps it to input-dft/);
});

test('an unrehashed edit to a published snapshot is caught by the drift check first', () => {
  const ws = freshWorkspace();
  const file = snapshotFile(ws, 'profile.yaml');
  fs.writeFileSync(file, fs.readFileSync(file, 'utf8').replace('executionClass: input-dft', 'executionClass: input-schematic'), 'utf8');
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /drifted/);
});

test('an unknown profile is refused', () => {
  const ws = freshWorkspace();
  const resolved = resolvePublishedProfile(ws, 'someone-elses-expert');
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /no expert profile/);
});

test('a runtimeLabel that is not the one the policy registry declares is refused', () => {
  const ws = freshWorkspace();
  const file = snapshotFile(ws, 'profile.yaml');
  fs.writeFileSync(file, fs.readFileSync(file, 'utf8').replace('runtimeLabel: PTC dft expert [<TM>]', 'runtimeLabel: PTC dft expert'), 'utf8');
  rehashSnapshot(ws);
  const resolved = resolvePublishedProfile(ws, PROFILE_ID);
  assert.equal(resolved.ok, false);
  assert.match(resolved.reason, /is not the label the policy registry declares/);
});

// ── stage registry ownership ───────────────────────────────────────────────

test('registry ownership is recorded, including the gap it exposes', () => {
  const ws = freshWorkspace();
  const ownership = registryOwnership(ws, 'INPUT_SYNC');
  assert.equal(ownership.ok, true);
  assert.equal(ownership.registryOwner, 'captain');
  assert.match(ownership.ownershipNote, /source role/);
});

test('a stage the registry does not contain is refused', () => {
  const ws = freshWorkspace();
  const registryFile = path.join(ws, 'team', 'ptc', 'ptc_stage_registry.json');
  const registry = JSON.parse(fs.readFileSync(registryFile, 'utf8'));
  fs.writeFileSync(registryFile, JSON.stringify({ ...registry, stateMachine: registry.stateMachine.filter((s) => s !== 'INPUT_SYNC') }), 'utf8');
  const ownership = registryOwnership(ws, 'INPUT_SYNC');
  assert.equal(ownership.ok, false);
  assert.match(ownership.reason, /no stage INPUT_SYNC/);
});

// ── dispatch ───────────────────────────────────────────────────────────────

test('dispatch pins the profile and passes persona, toolFilter, maxDepth 1 and an outputSchema', async () => {
  const ws = freshWorkspace();
  const ctx = fakeContext();
  const result = await dispatch(ws, ctx);
  assert.equal(result.dispatched, true, result.reason);
  assert.equal(ctx.captured.length, 1);
  const { provider, request } = ctx.captured[0];
  assert.equal(provider, 'spawn');
  assert.equal(request.maxDepth, 1);
  assert.equal(request.label, 'PTC dft expert [TM106]', 'the label must be the one the material boundary recognises');
  assert.ok(request.persona.includes('executionClass input-dft'));
  assert.deepEqual(request.toolFilter, { allow: ['read', 'write', 'pwsh', 'glob', 'grep'] });
  assert.equal(request.outputSchema.type, 'object');
  assert.ok(Array.isArray(request.outputSchema.required));
  assert.equal(request.parent.id, 'parent-session');

  const receipt = JSON.parse(fs.readFileSync(result.receiptPath, 'utf8'));
  assert.equal(receipt.profileVersion, publishedVersion(ws));
  assert.equal(receipt.executionClass, 'input-dft');
  assert.deepEqual(receipt.targetTms, ['TM106']);
  assert.equal(receipt.childSessionId, 'child-session-uuid-1');
  assert.equal(receipt.stage, 'INPUT_SYNC');
  assert.equal(verifyDispatchReceipt(receipt).ok, true);
  assert.equal(listReceipts(ws, 'run-tm106').length, 1);
});

test('dispatching the same run twice is refused instead of racing two children', async () => {
  const ws = freshWorkspace();
  const ctx = fakeContext();
  assert.equal((await dispatch(ws, ctx)).dispatched, true);
  const again = await dispatch(ws, ctx);
  assert.equal(again.dispatched, false);
  assert.match(again.reason, /already exists/);
  assert.equal(ctx.captured.length, 1, 'the second attempt must not start a child');
});

test('a refused dispatch starts no child and writes no receipt', async () => {
  const ws = freshWorkspace();
  writeStatus(ws, { ...readStatus(ws), publishedVersion: null });
  const ctx = fakeContext();
  const result = await dispatch(ws, ctx);
  assert.equal(result.dispatched, false);
  assert.equal(ctx.captured.length, 0);
  assert.deepEqual(listReceipts(ws), []);
});

test('bad inputs are refused before anything is started', async () => {
  const ws = freshWorkspace();
  const ctx = fakeContext();
  for (const overrides of [{ targetTms: [] }, { targetTms: ['tm106'] }, { runId: '' }, { task: '   ' }]) {
    const result = await dispatch(ws, ctx, overrides);
    assert.equal(result.dispatched, false, JSON.stringify(overrides));
  }
  assert.equal(ctx.captured.length, 0);
});

test('without a spawn provider the dispatcher refuses instead of dispatching unlabelled work', async () => {
  const ws = freshWorkspace();
  const ctx = { subagents: { getProvider: () => undefined, start: async () => { throw new Error('must not be called'); } } };
  const result = await dispatch(ws, ctx);
  assert.equal(result.dispatched, false);
  assert.match(result.reason, /provider is unavailable/);
});

// ── matching a live child back to exactly one receipt ─────────────────────

test('ready DFT products complete UNCHANGED without starting any model', async () => {
  const ws = freshWorkspace();
  const ctx = fakeContext();
  const outcome = await dispatch(ws, ctx, { checkDftReuse: async () => ({ unchanged: true, reports: [{ tm: 'TM106', requiredOutputs: ['meta', 'yaml', 'review'], canonicalInput: { sha256: 'a'.repeat(64) } }] }) });
  assert.equal(outcome.dispatched, true);
  assert.equal(ctx.captured.length, 0);
  assert.equal(outcome.childSessionId, null);
  assert.equal(outcome.receipt.executionMode, 'UNCHANGED');
  assert.equal(verifyDispatchReceipt(outcome.receipt).ok, true);
  assert.equal((await outcome.run.result).structured.mode, 'UNCHANGED');
});

test('failed preflight starts no child and writes no receipt', async () => {
  const ws = freshWorkspace();
  const ctx = fakeContext();
  const outcome = await dispatch(ws, ctx, { checkDftReuse: async () => { throw new Error('gate timeout'); } });
  assert.equal(outcome.dispatched, false);
  assert.equal(ctx.captured.length, 0);
  assert.equal(listReceipts(ws).length, 0);
});

test('a live child matches exactly one receipt by its session id', async () => {
  const ws = freshWorkspace();
  await dispatch(ws, fakeContext());
  const match = findReceiptForChild(ws, { childSessionId: 'child-session-uuid-1' });
  assert.equal(match.ok, true, match.reason);
  assert.equal(match.receipt.profileVersion, publishedVersion(ws));
});

test('an unmatched child is refused (fail-closed, never "allowed")', () => {
  const ws = freshWorkspace();
  const match = findReceiptForChild(ws, { childSessionId: 'no-such-child' });
  assert.equal(match.ok, false);
  assert.match(match.reason, /no pinned dispatch receipt/);
});

test('an ambiguous child identity is refused rather than resolved', async () => {
  const ws = freshWorkspace();
  const result = await dispatch(ws, fakeContext());
  const original = JSON.parse(fs.readFileSync(result.receiptPath, 'utf8'));
  // A SECOND receipt that is internally valid and claims the same child: the
  // digest is recomputed, so this is a genuine ambiguity, not a broken file.
  const duplicate = { ...original, dispatchId: 'ptc-dft-expert-run-tm106-dup' };
  duplicate.digest = receiptDigest(duplicate);
  assert.equal(verifyDispatchReceipt(duplicate).ok, true);
  fs.writeFileSync(path.join(path.dirname(result.receiptPath), 'duplicate.json'), `${JSON.stringify(duplicate, null, 2)}\n`, 'utf8');
  const match = findReceiptForChild(ws, { childSessionId: 'child-session-uuid-1' });
  assert.equal(match.ok, false);
  assert.match(match.reason, /ambiguous/);
});

test('a tampered receipt stops matching', async () => {
  const ws = freshWorkspace();
  const result = await dispatch(ws, fakeContext());
  const receipt = JSON.parse(fs.readFileSync(result.receiptPath, 'utf8'));
  fs.writeFileSync(result.receiptPath, `${JSON.stringify({ ...receipt, targetTms: ['TM106', 'TM110'] }, null, 2)}\n`, 'utf8');
  const match = findReceiptForChild(ws, { childSessionId: 'child-session-uuid-1' });
  assert.equal(match.ok, false, 'a receipt whose digest no longer matches must not authorise a child');
});
