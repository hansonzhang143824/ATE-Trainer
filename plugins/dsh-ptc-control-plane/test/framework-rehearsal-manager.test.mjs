import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';
import { createFrameworkRehearsalManager } from '../lib/framework-rehearsal-manager.js';

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-framework-manager-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const registry = path.join(root, 'team/ptc/ptc_stage_registry.json');
  fs.mkdirSync(path.dirname(registry), { recursive: true });
  fs.copyFileSync(new URL('./fixtures/legacy-framework-stage-registry.json', import.meta.url), registry);
  const created = createTrainingRun(root, { runId: 'framework-test-1', purpose: 'framework-rehearsal',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' } });
  const runDirectory = path.dirname(created.stateFile);
  const source = { schemaVersion: 1, kind: 'verified-source-products', testItems: ['TM109'],
    schematic: { canonicalInput: 'schematic-source', files: [], fileHashes: [] },
    dft: [{ tm: 'TM109', canonicalInput: 'dft-source', files: [], fileHashes: [] }] };
  return { root, created, runDirectory, source };
}

function adapters() {
  return {
    snapshot: async ({ runId }) => ({ runId }),
    executeStage: async (request, snapshot) => {
      assert.equal(snapshot.runId, request.runId);
      return { terminals: request.expectedRoles.map(role => ({ role, status: 'done', testItems: request.testItems })) };
    },
    recoverStage: async () => { throw new Error('unexpected recovery'); },
    verifyStage: async request => ({ status: 'passed', exitCode: 0, gate: request.gate }),
    verifyChain: async () => ({ status: 'passed' }),
  };
}

test('framework manager completes only after independent full-chain verification', async t => {
  const { root, created, runDirectory, source } = fixture(t);
  let verified = false;
  const bounded = adapters();
  bounded.verifyChain = async () => { verified = true; return { status: 'passed' }; };
  const manager = createFrameworkRehearsalManager(root, bounded, { preflight: async () => source });
  const accepted = manager.start({ runId: created.context.runId, testItems: ['TM109'] });
  assert.equal(accepted.status, 'preparing');
  const result = await accepted.completion;
  assert.equal(verified, true);
  assert.equal(result.status, 'completed');
  assert.equal(result.outcome.result, '流程演练通过');
  assert.equal(result.outcome.realBusinessGatesPassed, false);
  assert.equal(fs.existsSync(path.join(runDirectory, 'framework-rehearsal.lock')), false);
  const progress = JSON.parse(fs.readFileSync(path.join(runDirectory, 'pipeline-progress.json'), 'utf8'));
  assert.equal(progress.stages.length, 7);
  assert.ok(progress.stages.every(stage => stage.status === 'completed'));
});

test('framework manager blocks after a failed full-chain verifier', async t => {
  const { root, created, source } = fixture(t);
  const bounded = adapters();
  bounded.verifyChain = async () => ({ status: 'failed', reason: 'tampered stage' });
  const manager = createFrameworkRehearsalManager(root, bounded, { preflight: async () => source });
  const result = await manager.start({ runId: created.context.runId, testItems: ['TM109'] }).completion;
  assert.equal(result.status, 'blocked');
  assert.match(result.outcome.reason, /tampered stage/);
});

test('stop during preflight waits for the pending step before releasing the run lock', async t => {
  const { root, created, runDirectory, source } = fixture(t);
  let release;
  const pending = new Promise(resolve => { release = resolve; });
  const manager = createFrameworkRehearsalManager(root, adapters(), {
    preflight: async () => { await pending; return source; },
  });
  const accepted = manager.start({ runId: created.context.runId, testItems: ['TM109'] });
  const stopped = manager.control(created.context.runId, 'stop');
  assert.equal(stopped.status, 'cancelled');
  assert.equal(fs.existsSync(path.join(runDirectory, 'framework-rehearsal.lock')), true);
  release();
  assert.equal((await accepted.completion).status, 'cancelled');
  assert.equal(fs.existsSync(path.join(runDirectory, 'framework-rehearsal.lock')), false);
});

test('stop during final verification cannot be overwritten by a late PASS', async t => {
  const { root, created, runDirectory, source } = fixture(t);
  let release;
  let entered;
  const enteredVerification = new Promise(resolve => { entered = resolve; });
  const pending = new Promise(resolve => { release = resolve; });
  const bounded = adapters();
  bounded.verifyChain = async () => { entered(); await pending; return { status: 'passed' }; };
  const manager = createFrameworkRehearsalManager(root, bounded, { preflight: async () => source });
  const accepted = manager.start({ runId: created.context.runId, testItems: ['TM109'] });
  await enteredVerification;
  assert.equal(manager.control(created.context.runId, 'stop').status, 'cancelled');
  assert.equal(fs.existsSync(path.join(runDirectory, 'framework-rehearsal.lock')), true);
  release();
  const result = await accepted.completion;
  assert.equal(result.status, 'cancelled');
  assert.equal(fs.existsSync(path.join(runDirectory, 'framework-rehearsal.lock')), false);
});

test('uncertain host-command termination remains visible and retains the inspection lock', async t => {
  const { root, created, runDirectory } = fixture(t);
  const error = new Error('python gate timed out');
  error.commandEvidence = { command: 'python gate', stopReason: 'timeout', terminationConfirmed: false };
  const manager = createFrameworkRehearsalManager(root, adapters(), { preflight: async () => { throw error; } });
  const result = await manager.start({ runId: created.context.runId, testItems: ['TM109'] }).completion;
  assert.equal(result.status, 'blocked');
  assert.equal(result.outcome.commandEvidence.command, 'python gate');
  assert.equal(result.outcome.terminationConfirmed, false);
  assert.equal(fs.existsSync(path.join(runDirectory, 'framework-rehearsal.lock')), true);
});
