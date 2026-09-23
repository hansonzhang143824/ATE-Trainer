/**
 * Second batch: the downstream experts (strategy / method / rule-reviewer)
 * dispatch through their published profiles with a receipt-scoped boundary,
 * and the reviewer's second stage is recorded on its receipt.
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
const DOWNSTREAM = ['strategy-expert', 'method-expert', 'rule-reviewer'];

const workspaces = [];
function workspaceWithProfiles() {
  const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-downstream-')));
  fs.mkdirSync(path.join(ws, 'team'), { recursive: true });
  for (const profileId of [...DOWNSTREAM, 'ptc-dft-expert']) {
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
  'test-strategy-architect': 'strategy-expert',
  'test-method-expert': 'method-expert',
  'rule-reviewer': 'rule-reviewer',
};

const stageInput = (role, stage) => ({
  state: stage,
  batchId: 'batch-tm106',
  dispatches: [{ role, tms: ['TM106'], trialDirs: [TRIAL_REL], stage }],
});

async function dispatchOnce(ws, role, stage) {
  const ctx = fakeContext();
  const runs = await startRequiredSourceDispatches(ctx, stageInput(role, stage), { id: 'captain' }, undefined, {
    workspaceRoot: ws,
    pinnedProfiles: PINNED,
  });
  return { ctx, runs, receipt: listReceipts(ws, 'batch-tm106').at(-1) };
}

after(() => {
  for (const ws of workspaces) fs.rmSync(ws, { recursive: true, force: true });
});

test('a downstream role is dispatched through its pinned published profile with the registry label', async () => {
  const ws = workspaceWithProfiles();
  const { ctx, runs, receipt } = await dispatchOnce(ws, 'test-strategy-architect', 'STRATEGY');
  assert.equal(ctx.calls.length, 1);
  const request = ctx.calls[0].request;
  assert.equal(request.maxDepth, 1, 'the child is a one-shot dispatch');
  assert.equal(request.label, 'PTC strategy expert [TM106]');
  assert.match(request.persona, /executionClass strategy-standard/);
  assert.ok(receipt, 'a receipt was pinned');
  assert.equal(receipt.profileId, 'strategy-expert');
  assert.equal(receipt.stage, 'STRATEGY', 'the receipt records the stage actually being worked');
  assert.ok(Array.isArray(receipt.trialDirs) && receipt.trialDirs.length === 1, 'the receipt pins the trial directories');
  assert.deepEqual(runs.unpinnedRoles, [], 'the role is pinned, not reported as a gap');
});

test('the reviewer dispatch records its SECOND stage instead of the profile primary stage', async () => {
  const ws = workspaceWithProfiles();
  const { ctx, receipt } = await dispatchOnce(ws, 'rule-reviewer', 'RULE_REVIEW_IMPLEMENTATION');
  assert.ok(receipt, 'a receipt was pinned');
  assert.equal(receipt.stage, 'RULE_REVIEW_IMPLEMENTATION');
  assert.equal(receipt.profileId, 'rule-reviewer');
  assert.equal(ctx.calls[0].request.label, 'PTC rule reviewer [TM106]');
});

test('the receipt-scoped boundary allows the strategy stage files and refuses everything else', async () => {
  const ws = workspaceWithProfiles();
  const { receipt } = await dispatchOnce(ws, 'test-strategy-architect', 'STRATEGY');
  const trial = path.resolve(ws, TRIAL_REL);
  const dft = path.join(ws, 'project', 'DALI', 'Output_Global_Material', 'dft', 'TM106', 'dft-meta.json');
  const schematicMap = path.join(ws, 'project', 'DALI', 'Output_Global_Material', 'schematic', 'Path-Proofs.json');
  fs.mkdirSync(path.dirname(dft), { recursive: true });
  fs.writeFileSync(dft, '{}');
  fs.mkdirSync(path.dirname(schematicMap), { recursive: true });
  fs.writeFileSync(schematicMap, '{}');
  fs.mkdirSync(path.join(trial, 'strategy'), { recursive: true });
  const agent = { id: receipt.childSessionId, session: { header: { cwd: ws } } };
  const guard = (name, args) => decision({ name, arguments: args, agent }, ws);

  assert.equal(guard('read', { file_path: dft }), undefined, 'strategy reads the accepted DFT output');
  assert.equal(guard('read', { file_path: schematicMap }), undefined, 'strategy reads the schematic map');
  assert.equal(guard('write', { file_path: path.join(trial, 'strategy', 'TM106-resource-config-contract.json') }), undefined, 'strategy writes its own stage output');
  assert.ok(guard('read', { file_path: path.join(ws, 'team', 'CURRENT_STATUS.md') }) !== undefined, 'captain status stays out of scope');
  assert.ok(guard('write', { file_path: dft }) !== undefined, 'the DFT output is not writable by strategy');
  assert.equal(guard('pwsh', { command: 'python scripts/validate_strategy_contract.py --tm TM106' }), undefined, 'the stage gate command is allowed');
  assert.ok(guard('pwsh', { command: 'python scripts/validate_dft_outputs.py --tm TM106' }) !== undefined, "another stage's gate is refused");
  assert.ok(guard('glob', { pattern: 'team/artifacts/**' }) !== undefined, 'directory enumeration is refused');
});

test('the method expert reads only strategy contracts and writes only method outputs', async () => {
  const ws = workspaceWithProfiles();
  const { receipt } = await dispatchOnce(ws, 'test-method-expert', 'METHOD');
  const trial = path.resolve(ws, TRIAL_REL);
  const strategyContract = path.join(trial, 'strategy', 'TM106-resource-config-contract.json');
  fs.mkdirSync(path.dirname(strategyContract), { recursive: true });
  fs.writeFileSync(strategyContract, '{}');
  const rawDft = path.join(ws, 'project', 'DALI', 'Output_Global_Material', 'dft', 'TM106', 'dft-meta.json');
  fs.mkdirSync(path.dirname(rawDft), { recursive: true });
  fs.writeFileSync(rawDft, '{}');
  const agent = { id: receipt.childSessionId, session: { header: { cwd: ws } } };
  const guard = (name, args) => decision({ name, arguments: args, agent }, ws);

  assert.equal(guard('read', { file_path: strategyContract }), undefined, 'method reads the strategy contract of its trial');
  assert.ok(guard('read', { file_path: rawDft }) !== undefined, 'raw DFT output is not a method input');
  assert.equal(guard('write', { file_path: path.join(trial, 'method', 'TM106-test-method-contract.json') }), undefined, 'method writes its own stage output');
  assert.ok(guard('write', { file_path: path.join(trial, 'strategy', 'x.json') }) !== undefined, 'the strategy contract is read-only for method');
});

test('the reviewer reads its trials but cannot modify what it reviews', async () => {
  const ws = workspaceWithProfiles();
  const { receipt } = await dispatchOnce(ws, 'rule-reviewer', 'RULE_REVIEW_METHOD');
  const trial = path.resolve(ws, TRIAL_REL);
  const methodContract = path.join(trial, 'method', 'TM106-test-method-contract.json');
  fs.mkdirSync(path.dirname(methodContract), { recursive: true });
  fs.writeFileSync(methodContract, '{}');
  const agent = { id: receipt.childSessionId, session: { header: { cwd: ws } } };
  const guard = (name, args) => decision({ name, arguments: args, agent }, ws);

  assert.equal(guard('read', { file_path: methodContract }), undefined, 'the reviewer reads the contract under review');
  assert.equal(guard('write', { file_path: path.join(trial, 'review', 'method-contract-review.json') }), undefined, 'the reviewer writes only review outputs');
  assert.ok(guard('write', { file_path: path.join(trial, 'method', 'TM106-test-method-contract.json') }) !== undefined, 'the contract under review is never writable');
});
