import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';
import { createFrameworkRehearsalManager } from '../lib/framework-rehearsal-manager.js';
import { createFrameworkRehearsalAdapters, verifyFrameworkChain } from '../lib/framework-rehearsal.js';

const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const SCH = ['SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
  'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json'];
const DFT = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];

function fixture(t, runId = 'framework-test-1') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-framework-chain-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const registry = path.join(root, 'team/ptc/ptc_stage_registry.json');
  fs.mkdirSync(path.dirname(registry), { recursive: true });
  fs.copyFileSync(new URL('../../../team/ptc/ptc_stage_registry.json', import.meta.url), registry);
  const created = createTrainingRun(root, { runId, purpose: 'framework-rehearsal',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' } });
  const output = path.join(root, 'project/DALI/Output_Global_Material');
  const make = (dir, names, role, tm) => {
    fs.mkdirSync(dir, { recursive: true });
    const files = names.map(name => {
      const file = path.join(dir, name);
      fs.writeFileSync(file, `${role}/${tm ?? 'ALL'}/${name}\n`);
      return file;
    });
    return { role, tm, gate: role === 'dft-expert' ? 'DFT_OUTPUT' : 'SCHEMATIC_OUTPUT',
      canonicalInput: { path: `fixture-${role}`, sha256: 'a'.repeat(64) },
      files, fileHashes: files.map(file => ({ path: file, sha256: sha(fs.readFileSync(file)) })) };
  };
  const source = { schemaVersion: 1, kind: 'verified-source-products', testItems: ['TM109'],
    schematic: make(path.join(output, 'schematic'), SCH, 'schematic-expert', null),
    dft: [make(path.join(output, 'dft/TM109'), DFT, 'dft-expert', 'TM109')] };
  return { root, created, source };
}

test('all seven framework stages execute with separate exact-byte handoffs and independent gates', async t => {
  const { root, created, source } = fixture(t);
  let snapshot;
  const adapters = createFrameworkRehearsalAdapters();
  const original = adapters.snapshot;
  adapters.snapshot = async input => { snapshot = await original(input); return snapshot; };
  const manager = createFrameworkRehearsalManager(root, adapters, { preflight: async () => source });
  const result = await manager.start({ runId: created.context.runId, testItems: ['TM109'] }).completion;
  assert.equal(result.status, 'completed', result.outcome?.reason);
  assert.equal(result.outcome.realBusinessGatesPassed, false);
  const base = path.join(root, 'Training_Materials/runs', created.context.runId, 'framework-rehearsal');
  const stages = JSON.parse(fs.readFileSync(path.join(base, 'stage-registry.json'), 'utf8')).stateMachine.filter(stage => stage !== 'COMPLETE');
  assert.equal(stages.length, 7);
  for (const stage of stages) {
    const receipt = JSON.parse(fs.readFileSync(path.join(base, 'stages', stage, 'receipt.json'), 'utf8'));
    assert.equal(receipt.kind, 'framework-rehearsal-stage-receipt');
    assert.equal(receipt.result, 'PASS');
    assert.equal(receipt.gateLabel, 'FRAMEWORK_REHEARSAL_ONLY');
    assert.equal(receipt.products.length, 1);
    assert.equal(fs.existsSync(path.join(base, 'stages', stage, 'TM109', 'handoff.json')), true);
  }
  assert.equal((await verifyFrameworkChain({ workspaceRoot: root, runId: created.context.runId,
    testItems: ['TM109'], snapshot })).status, 'passed');
  assert.equal((await verifyFrameworkChain({ workspaceRoot: root, runId: 'wrong-run',
    testItems: ['TM109'], snapshot })).status, 'failed');
  assert.equal((await verifyFrameworkChain({ workspaceRoot: root, runId: created.context.runId,
    testItems: ['TM110'], snapshot })).status, 'failed');
  fs.appendFileSync(path.join(base, 'stages', 'METHOD', 'TM109', 'handoff.json'), 'tamper');
  assert.match((await verifyFrameworkChain({ workspaceRoot: root, runId: created.context.runId,
    testItems: ['TM109'], snapshot })).reason, /artifact binding changed/);
});

test('missing stage receipt fails closed', async t => {
  const { root, created, source } = fixture(t);
  let snapshot;
  const adapters = createFrameworkRehearsalAdapters();
  const original = adapters.snapshot;
  adapters.snapshot = async input => { snapshot = await original(input); return snapshot; };
  const manager = createFrameworkRehearsalManager(root, adapters, { preflight: async () => source });
  assert.equal((await manager.start({ runId: created.context.runId, testItems: ['TM109'] }).completion).status, 'completed');
  fs.unlinkSync(path.join(root, 'Training_Materials/runs', created.context.runId,
    'framework-rehearsal/stages/RULE_REVIEW_METHOD/receipt.json'));
  assert.equal((await verifyFrameworkChain({ workspaceRoot: root, runId: created.context.runId,
    testItems: ['TM109'], snapshot })).status, 'failed');
});

test('explicit restart recovery rechecks completed receipts without writing stage artifacts', async t => {
  const { root, created, source } = fixture(t);
  const runId = created.context.runId;
  const manager = createFrameworkRehearsalManager(root, createFrameworkRehearsalAdapters(), { preflight: async () => source });
  assert.equal((await manager.start({ runId, testItems: ['TM109'] }).completion).status, 'completed');
  const directory = path.join(root, 'Training_Materials/runs', runId);
  const artifact = path.join(directory, 'framework-rehearsal/stages/COMPILE/TM109/handoff.json');
  const before = fs.readFileSync(artifact);
  const stateFile = path.join(directory, 'state.json');
  fs.writeFileSync(stateFile, JSON.stringify({ ...JSON.parse(fs.readFileSync(stateFile, 'utf8')), status: 'interrupted' }));
  const recovered = createFrameworkRehearsalManager(root, createFrameworkRehearsalAdapters(), { preflight: async () => {
    throw new Error('recovery must not rerun source preflight');
  } });
  assert.equal((await recovered.recover(runId).completion).status, 'completed');
  assert.deepEqual(fs.readFileSync(artifact), before);
  fs.writeFileSync(stateFile, JSON.stringify({ ...JSON.parse(fs.readFileSync(stateFile, 'utf8')), status: 'interrupted' }));
  fs.appendFileSync(artifact, 'tamper');
  const blocked = await recovered.recover(runId).completion;
  assert.equal(blocked.status, 'blocked');
  assert.match(blocked.outcome.reason, /artifact binding changed/);
});
