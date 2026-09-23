/**
 * Third batch: the implementer / compile diagnostician / evolution expert
 * dispatch through their published profiles with receipt-scoped boundaries.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { fileURLToPath } from 'node:url';
import { startRequiredSourceDispatches } from '../lib/captain-entry.js';
import { listReceipts } from '../lib/dispatch-profile.js';
import { decision } from '../lib/policy.js';

const PLUGIN_DIR = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const REPO_ROOT = path.resolve(PLUGIN_DIR, '..', '..');
const PROFILES = ['ate-implementer', 'compile-diagnostician', 'evolution-expert'];
const TARGET_SOURCE_ROOT = 'D:/PROJECT6-DALI/ForCodexDebug';

const workspaces = [];
function workspaceWithProfiles() {
  const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-batch3-')));
  fs.mkdirSync(path.join(ws, 'team'), { recursive: true });
  for (const profileId of PROFILES) {
    fs.cpSync(path.join(REPO_ROOT, 'team', 'expert-profiles', profileId), path.join(ws, 'team', 'expert-profiles', profileId), { recursive: true });
  }
  fs.cpSync(path.join(REPO_ROOT, 'team', 'ptc'), path.join(ws, 'team', 'ptc'), { recursive: true });
  workspaces.push(ws);
  return ws;
}

function fakeContext() {
  const calls = [];
  return {
    calls,
    logger: { warn() {}, info() {}, error() {} },
    subagents: {
      getProvider: (name) => (name === 'spawn' ? { name: 'spawn' } : undefined),
      start: async (provider, request) => {
        calls.push({ provider, request });
        return { id: `child-${calls.length}`, result: Promise.resolve({ stopReason: 'completed' }) };
      },
    },
  };
}

const TRIAL_REL = path.join('team', 'artifacts', 'batch-tm106', 'tm106');
const PINNED = {
  'ate-implementer': 'ate-implementer',
  'compile-diagnostician': 'compile-diagnostician',
  'evolution-expert': 'evolution-expert',
};

const stageInput = (role, stage, tms = ['TM106'], trialDirs = [TRIAL_REL]) => ({
  state: stage,
  batchId: 'batch-tm106',
  dispatches: [{ role, tms, trialDirs, stage }],
});

async function dispatchOnce(ws, role, stage, tms, trialDirs) {
  const ctx = fakeContext();
  const runs = await startRequiredSourceDispatches(ctx, stageInput(role, stage, tms, trialDirs), { id: 'captain' }, undefined, {
    workspaceRoot: ws,
    pinnedProfiles: PINNED,
  });
  return { ctx, runs, receipt: listReceipts(ws, 'batch-tm106').at(-1) };
}

after(() => {
  for (const ws of workspaces) fs.rmSync(ws, { recursive: true, force: true });
});

test('the implementer is dispatched through its pinned published profile with the registry label', async () => {
  const ws = workspaceWithProfiles();
  const { ctx, receipt } = await dispatchOnce(ws, 'ate-implementer', 'IMPLEMENTATION');
  assert.equal(ctx.calls.length, 1);
  const request = ctx.calls[0].request;
  assert.equal(request.maxDepth, 1, 'the child is a one-shot dispatch');
  assert.equal(request.label, 'PTC implementer [TM106]');
  assert.match(request.persona, /executionClass implementation-standard/);
  assert.ok(receipt, 'a receipt was pinned');
  assert.equal(receipt.profileId, 'ate-implementer');
  assert.equal(receipt.stage, 'IMPLEMENTATION');
  assert.ok(Array.isArray(receipt.trialDirs) && receipt.trialDirs.length === 1);
});

test('the implementer reads its signed contracts and standards, writes implementation outputs and approved target sources only', async () => {
  const ws = workspaceWithProfiles();
  const { receipt } = await dispatchOnce(ws, 'ate-implementer', 'IMPLEMENTATION');
  const trial = path.resolve(ws, TRIAL_REL);
  for (const rel of [path.join('method', 'TM106-test-method-contract.json'), path.join('strategy', 'TM106-resource-config-contract.json')]) {
    fs.mkdirSync(path.join(trial, path.dirname(rel)), { recursive: true });
    fs.writeFileSync(path.join(trial, rel), '{}');
  }
  fs.mkdirSync(path.join(ws, 'knowledge', 'standards'), { recursive: true });
  fs.writeFileSync(path.join(ws, 'knowledge', 'standards', 'treg.md'), 'standard');
  const agent = { id: receipt.childSessionId, session: { header: { cwd: ws } } };
  const guard = (name, args) => decision({ name, arguments: args, agent }, ws);

  assert.equal(guard('read', { file_path: path.join(trial, 'method', 'TM106-test-method-contract.json') }), undefined, 'implementer reads the signed method contract');
  assert.equal(guard('read', { file_path: path.join(ws, 'knowledge', 'standards', 'treg.md') }), undefined, 'implementer reads the TRIM standard');
  assert.equal(guard('read', { file_path: 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp' }), undefined, 'implementer reads the approved target source');
  assert.equal(guard('write', { file_path: path.join(trial, 'implementation', 'implementation-manifest.json') }), undefined, 'implementer writes its stage output');
  assert.equal(guard('write', { file_path: 'D:/PROJECT6-DALI/ForCodexDebug/source/__ptc-probe.tmp' }), undefined, 'implementer writes inside the approved target source root');
  assert.ok(guard('write', { file_path: path.join(trial, 'method', 'TM106-test-method-contract.json') }) !== undefined, 'the signed method contract is never writable');
  assert.ok(guard('write', { file_path: path.join(ws, 'knowledge', 'standards', 'treg.md') }) !== undefined, 'standards are not writable');
  assert.equal(guard('pwsh', { command: 'python scripts/verify_implementation_batch.py team/artifacts/batch-tm106/tm106' }), undefined, 'the implementation gate is allowed');
  assert.ok(guard('pwsh', { command: 'python scripts/validate_strategy_contract.py --tm TM106' }) !== undefined, "another stage's gate is refused");
});

test('the compile diagnostician is dispatched pinned and reads implementation evidence, writes compile outputs only', async () => {
  const ws = workspaceWithProfiles();
  const { ctx, receipt } = await dispatchOnce(ws, 'compile-diagnostician', 'COMPILE');
  assert.equal(ctx.calls.length, 1);
  assert.equal(ctx.calls[0].request.label, 'PTC compile diagnostician [TM106]');
  assert.equal(receipt.profileId, 'compile-diagnostician');
  assert.equal(receipt.stage, 'COMPILE');
  const trial = path.resolve(ws, TRIAL_REL);
  const manifest = path.join(trial, 'implementation', 'implementation-manifest.json');
  fs.mkdirSync(path.dirname(manifest), { recursive: true });
  fs.writeFileSync(manifest, '{}');
  const agent = { id: receipt.childSessionId, session: { header: { cwd: ws } } };
  const guard = (name, args) => decision({ name, arguments: args, agent }, ws);

  assert.equal(guard('read', { file_path: manifest }), undefined, 'compile reads the implementation manifest');
  assert.equal(guard('write', { file_path: path.join(trial, 'compile', 'build-report.json') }), undefined, 'compile writes its stage output');
  assert.ok(guard('write', { file_path: manifest }) !== undefined, 'implementation outputs are not writable by compile');
  assert.equal(guard('pwsh', { command: 'python scripts/run_ptc_incremental_compile.py --project P --source S --report R' }), undefined, 'the bounded compile gate is allowed');
  assert.ok(guard('pwsh', { command: 'python scripts/verify_implementation_batch.py team/artifacts/batch-tm106/tm106' }) !== undefined, "the implementation gate is not compile's to run");
});

test('the evolution expert is dispatched pinned and works on closed evidence and proposals only', async () => {
  const ws = workspaceWithProfiles();
  const { ctx, receipt } = await dispatchOnce(ws, 'evolution-expert', 'EVOLUTION', [], []);
  assert.equal(ctx.calls.length, 1);
  assert.equal(ctx.calls[0].request.label, 'PTC evolution expert');
  assert.equal(receipt.profileId, 'evolution-expert');
  assert.equal(receipt.stage, 'EVOLUTION');
  const closed = path.join(ws, 'team', 'artifacts', 'closed-batch', 'tm106', 'method', 'tm106-test-method-contract.json');
  fs.mkdirSync(path.dirname(closed), { recursive: true });
  fs.writeFileSync(closed, '{}');
  const agent = { id: receipt.childSessionId, session: { header: { cwd: ws } } };
  const guard = (name, args) => decision({ name, arguments: args, agent }, ws);

  assert.equal(guard('read', { file_path: closed }), undefined, 'evolution reads closed run evidence');
  assert.equal(guard('read', { file_path: path.join(ws, 'team', 'ptc', 'legacy_migration_ledger.json') }), undefined, 'evolution reads the governance documents');
  assert.equal(guard('write', { file_path: path.join(ws, 'team', 'expert-profiles', 'evolution-expert', 'proposals', 'p-001.json') }), undefined, 'evolution writes proposals only');
  assert.ok(guard('write', { file_path: path.join(ws, 'team', 'ptc', 'legacy_migration_ledger.json') }) !== undefined, 'governance documents are not writable');
  assert.ok(guard('write', { file_path: closed }) !== undefined, 'closed run evidence is never writable');
  assert.ok(guard('read', { file_path: `${TARGET_SOURCE_ROOT}/source/test.cpp` }) !== undefined, 'project source code stays out of scope');
  assert.equal(guard('pwsh', { command: 'python scripts/validate_evolution_proposal.py team/expert-profiles/evolution-expert/proposals/p-001.json' }), undefined, 'the proposal gate is allowed');
});
