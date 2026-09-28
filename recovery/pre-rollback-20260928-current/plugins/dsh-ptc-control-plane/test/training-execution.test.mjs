import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';
import { executeTrainingRun as executeRealTrainingRun, reconcileInterruptedTrainingRuns } from '../lib/training-execution.js';
import { trainingAddressBook } from '../lib/training-paths.js';

const executeTrainingRun = (root, input, options = {}) => executeRealTrainingRun(root, input, {
  prepareMaterials: async (_root, runId) => ({ ...trainingAddressBook(runId), cacheCompatible: true, cacheKey: 'test-cache' }),
  prepareSourceView: async (_root, testItems, materials) => ({ status: 'SOURCE_VIEW', runId: materials.runId,
    path: materials.sourceView, sha256: 'b'.repeat(64), sourceSha256: 'a'.repeat(64),
    testItems: [...testItems].sort(), reused: false, bytes: 1 }),
  prepareReviewInput: async (_root, testItems, materials) => ({ schemaVersion: 1, runId: materials.runId,
    sourceSha256: 'a'.repeat(64), items: testItems.map((tm) => ({ tm, mode: 'OVERWRITTEN',
      sourceSha256: 'a'.repeat(64), producerDigests: {
        'dft-meta.json': 'c'.repeat(64), 'dft-conditions.yaml': 'd'.repeat(64),
      }, sourceEvidence: {}, generatedMeta: {}, generatedConditionsYaml: '' })) }),
  bindReviews: async () => true,
  productHashes: () => ({}),
  verifyMaterials: async () => true,
  ...options,
});

function workspace() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-execution-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  return root;
}

function ready(tm) {
  return {
    tm, exitCode: 0, role: 'dft-expert', gate: 'DFT_OUTPUT', status: 'ready',
    canonicalInput: { path: 'input.xlsx', sha256: 'a'.repeat(64), sheet: 'OVERVIEW' },
    requiredOutputs: ['meta', 'yaml', 'review'], missingOrStaleOutputs: [],
  };
}

test('ready DFT candidate completes UNCHANGED without model dispatch', async () => {
  const root = workspace();
  const created = createTrainingRun(root, {
    runId: 'training-dft-unchanged', target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  }, { now: new Date('2026-09-22T10:00:00.000Z') });
  const result = await executeTrainingRun(root, {
    runId: created.context.runId, testItems: ['tm109'],
  }, { runDftGate: async (_root, tm) => ready(tm) });
  assert.equal(result.state.status, 'completed');
  assert.equal(result.state.outcome.mode, 'UNCHANGED');
  assert.equal(result.state.outcome.modelDispatched, false);
  assert.deepEqual(result.state.testItems, ['TM109']);
  assert.equal(fs.existsSync(result.evidenceFile), true);
  assert.equal(fs.existsSync(path.join(root, 'project')), false);
});

test('stale DFT candidate stops at needs_model and keeps evidence run-local', async () => {
  const root = workspace();
  const created = createTrainingRun(root, {
    runId: 'training-dft-stale', target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  });
  const stale = { ...ready('TM109'), exitCode: 2, status: 'stale', missingOrStaleOutputs: ['meta stale'] };
  const result = await executeTrainingRun(root, {
    runId: created.context.runId, testItems: ['TM109'],
  }, { runDftGate: async () => stale });
  assert.equal(result.state.status, 'needs_model');
  assert.equal(result.state.outcome.reason, 'candidate_outputs_require_isolated_model_execution');
  assert.equal(result.evidence.modelDispatched, false);
  assert.equal(path.relative(root, result.evidenceFile).startsWith(path.join('Training_Materials', 'runs', created.context.runId)), true);
});

test('stale candidate dispatches one model and completes only after the host gate is ready', async () => {
  const root = workspace();
  const created = createTrainingRun(root, {
    runId: 'training-dft-model', target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  });
  let gateCalls = 0;
  const stale = { ...ready('TM109'), exitCode: 2, status: 'stale', missingOrStaleOutputs: ['meta stale'] };
  const receiptFile = path.join(root, 'Training_Materials/runs', created.context.runId, 'dispatch.json');
  fs.writeFileSync(receiptFile, '{}');
  const result = await executeTrainingRun(root, {
    runId: created.context.runId, testItems: ['TM109'],
  }, {
    runDftGate: async () => (++gateCalls === 1 ? stale : ready('TM109')),
    dispatchModel: async (request) => {
      assert.equal(request.runId, created.context.runId);
      return ({
      childSessionId: 'session-training-child', receiptFile,
      result: Promise.resolve({ stopReason: 'completed', structured: { status: 'done', reviews: [
        { tm: 'TM109', verdict: 'PASS', findings: ['source and generated facts match'] },
      ] } }),
      });
    },
  });
  assert.equal(result.state.status, 'running');
  assert.equal(result.state.outcome.modelDispatched, true);
  const terminal = await result.completion;
  assert.equal(terminal.state.status, 'completed');
  assert.equal(terminal.state.outcome.mode, 'OVERWRITTEN');
  assert.equal(terminal.state.outcome.childSessionId, 'session-training-child');
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/runs', created.context.runId, 'evidence/dft-terminal.json')), true);
});

test('exact deterministic source binding completes stale DFT without dispatching a model', async () => {
  const root = workspace();
  const created = createTrainingRun(root, {
    runId: 'training-dft-deterministic-review', target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  });
  const stale = { ...ready('TM109'), exitCode: 2, status: 'stale', missingOrStaleOutputs: ['review stale'] };
  let gateCalls = 0;
  let dispatchCalls = 0;
  let bound;
  const result = await executeTrainingRun(root, {
    runId: created.context.runId, testItems: ['TM109'],
  }, {
    runDftGate: async () => (++gateCalls === 1 ? stale : ready('TM109')),
    prepareReviewInput: async (_root, _items, materials) => ({
      schemaVersion: 1, runId: materials.runId, sourceSha256: 'a'.repeat(64), items: [{
        tm: 'TM109', mode: 'OVERWRITTEN', sourceSha256: 'a'.repeat(64),
        producerDigests: { 'dft-meta.json': 'c'.repeat(64), 'dft-conditions.yaml': 'd'.repeat(64) },
        sourceEvidence: { sheet: 'OVERVIEW', row: 12, facts: {
          Item: 'TM109', Name: 'VAC2_PRST', Notes: 'source notes', ExpectValue: '4.4V', Check: 'V(DTEST0)',
        } },
        metaProjection: { sourceLocation: { sheet: 'OVERVIEW', row: 12 }, parseStatus: 'ok', openItems: [],
          rawIntentMatchesSource: true, testCondition: { identity: 'VAC2_PRST', remarks: 'source notes',
            expectedValue: '4.4V', measurement: 'V(DTEST0)' } },
        conditionsProjection: { tm: 'TM109', sourceSha256: 'a'.repeat(64), semanticFieldsMatchMeta: true },
      }] }),
    bindReviews: async (_root, _materials, _reviewInput, structured) => { bound = structured; },
    dispatchModel: async () => { dispatchCalls++; throw new Error('model should not be dispatched'); },
  });
  assert.equal(result.state.status, 'completed');
  assert.equal(result.state.outcome.mode, 'OVERWRITTEN');
  assert.equal(result.state.outcome.modelDispatched, false);
  assert.equal(result.state.outcome.reviewMethod, 'deterministic-source-binding');
  assert.equal(dispatchCalls, 0);
  assert.equal(bound.reviews[0].verdict, 'PASS');
  assert.equal(result.evidence.reviewMethod, 'deterministic-source-binding');
});

test('training execution rejects wrong profile, duplicate starts and invalid TM values', async () => {
  const root = workspace();
  fs.mkdirSync(path.join(root, 'team/expert-profiles/method-expert'), { recursive: true });
  const wrong = createTrainingRun(root, {
    runId: 'training-method', target: { kind: 'profile', profileId: 'method-expert' },
  });
  await assert.rejects(executeTrainingRun(root, { runId: wrong.context.runId, testItems: ['TM109'] }), /supports only/);
  const dft = createTrainingRun(root, {
    runId: 'training-dft-once', target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  });
  await assert.rejects(executeTrainingRun(root, { runId: dft.context.runId, testItems: ['../TM109'] }), /TM<digits>/);
  await executeTrainingRun(root, { runId: dft.context.runId, testItems: ['TM109'] }, { runDftGate: async () => ready('TM109') });
  await assert.rejects(executeTrainingRun(root, { runId: dft.context.runId, testItems: ['TM109'] }), /not startable/);
});

test('startup reconciliation closes orphaned running states after a host restart', () => {
  const root = workspace();
  const created = createTrainingRun(root, {
    runId: 'training-orphaned', target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  });
  const stateFile = path.join(root, 'Training_Materials/runs', created.context.runId, 'state.json');
  fs.writeFileSync(stateFile, `${JSON.stringify({ ...created.state, status: 'running', outcome: { mode: 'MODEL', modelDispatched: true } }, null, 2)}\n`);
  const names = reconcileInterruptedTrainingRuns(root, { now: new Date('2026-09-22T14:30:00.000Z') });
  assert.deepEqual(names, ['training-orphaned']);
  const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
  assert.equal(state.status, 'interrupted');
  assert.equal(state.outcome.mode, 'INTERRUPTED');
  assert.equal(state.finishedAt, '2026-09-22T14:30:00.000Z');
});

test('timeout becomes blocked without revalidating potentially partial products', async () => {
  const root = workspace();
  const created = createTrainingRun(root, { runId: 'training-cancelled', target: { kind: 'profile', profileId: 'ptc-dft-expert' } });
  let calls = 0;
  const result = await executeTrainingRun(root, { runId: created.context.runId, testItems: ['TM109'] }, {
    runDftGate: async () => {
      calls++;
      if (calls > 1) throw new Error('cancelled output must not be certified');
      return { ...ready('TM109'), status: 'stale', exitCode: 2, missingOrStaleOutputs: ['old'] };
    },
    dispatchModel: async () => ({ childSessionId: 'cancelled-child', receiptFile: path.join(root, 'receipt.json'),
      result: Promise.resolve({ stopReason: 'timeout', structured: { status: 'blocked', question: 'deadline reached' } }) }),
  });
  const terminal = await result.completion;
  assert.equal(terminal.state.status, 'blocked');
  assert.equal(terminal.state.outcome.reason, 'deadline reached');
  assert.equal(calls, 1);
  assert.deepEqual(terminal.evidence.reports, []);
});

test('ready legacy products do not bypass changed or unbound draft evaluation', async () => {
  const root = workspace();
  const runId = 'training-unbound-draft';
  createTrainingRun(root, { runId, target: { kind: 'profile', profileId: 'ptc-dft-expert' } });
  const materials = { ...trainingAddressBook(runId), cacheCompatible: false, cacheKey: 'new-draft' };
  const result = await executeTrainingRun(root, { runId, testItems: ['TM109'] }, {
    prepareMaterials: async () => materials,
    runDftGate: async (_root, tm, snapshot) => { assert.equal(snapshot, materials); return ready(tm); },
  });
  assert.equal(result.state.status, 'needs_model');
  assert.equal(result.evidence.cacheCompatible, false);
});

test('same TM concurrent executions use distinct frozen address books at both gates', async () => {
  const root = workspace();
  const observed = [];
  const run = async (runId) => {
    createTrainingRun(root, { runId, target: { kind: 'profile', profileId: 'ptc-dft-expert' } });
    let calls = 0;
    const result = await executeTrainingRun(root, { runId, testItems: ['TM109'] }, {
      runDftGate: async (_root, tm, material) => {
        observed.push(material.dftRoot);
        return ++calls === 1 ? { ...ready(tm), status: 'stale' } : ready(tm);
      },
      dispatchModel: async (request) => {
        assert.equal(request.materials.runRoot, trainingAddressBook(runId).runRoot);
        return { childSessionId: runId, receiptFile: path.join(root, request.materials.runRoot, 'dispatch.json'),
          result: Promise.resolve({ stopReason: 'completed', structured: { status: 'done', reviews: [
            { tm: 'TM109', verdict: 'PASS', findings: ['source and generated facts match'] },
          ] } }) };
      },
    });
    return result.completion;
  };
  const results = await Promise.all([run('training-a'), run('training-b')]);
  assert.ok(results.every((result) => result.state.status === 'completed'));
  assert.equal(new Set(observed).size, 2);
  assert.equal(observed.length, 4);
});
