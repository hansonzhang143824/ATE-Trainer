import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';
import { createSimpleOrchestration } from '../lib/simple-orchestration.js';
import { createSimpleOrchestrationSourceAdapters } from '../lib/simple-orchestration-source.js';

const names = ['INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD',
  'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION', 'COMPILE'];
const owners = ['captain', 'test-strategy-architect', 'test-method-expert', 'rule-reviewer',
  'ate-implementer', 'rule-reviewer', 'compile-diagnostician'];
const roles = ['dft-expert', 'schematic-expert', ...new Set(owners.slice(1)), 'evolution-expert'];
const profileId = role => role === 'dft-expert' ? 'ptc-dft-expert'
  : role === 'schematic-expert' ? 'ptc-schematic-expert' : role;
function fixture(t) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-simple-sources-'));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  fs.mkdirSync(path.join(workspaceRoot, 'team/ptc'), { recursive: true });
  fs.mkdirSync(path.join(workspaceRoot, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  fs.writeFileSync(path.join(workspaceRoot, 'team/ptc/ptc_stage_registry.json'), JSON.stringify({
    stateMachine: [...names, 'COMPLETE'],
    stages: Object.fromEntries(names.map((stage, i) => [stage,
      { owner: owners[i], gate: `scripts/gate-${i}.py` }])),
  }));
  createTrainingRun(workspaceRoot, { runId: 'parent-smoke', target: { kind: 'pipeline' }, purpose: 'smoke-training' });
  const profileBindings = Object.fromEntries(roles.map(role => [role, {
    profileId: profileId(role), profileVersion: 'v1',
    profileDigest: crypto.createHash('sha256').update(role).digest('hex'),
  }]));
  const controller = createSimpleOrchestration({ workspaceRoot, runId: 'parent-smoke',
    testItems: ['TM109'], sourceRoles: ['dft-expert', 'schematic-expert'], profileBindings,
    executeSmokeRole: async () => { throw new Error('not used'); } });
  const progress = controller.getState();
  const request = role => {
    const task = progress.stages[0].tasks.find(item => item.role === role);
    return { runId: 'parent-smoke', mode: 'SMOKE_ONLY', stage: 'INPUT_SYNC', owner: 'captain',
      registryGate: 'scripts/gate-0.py', role, profileId: task.profileId,
      profileVersion: task.profileVersion, profileDigest: task.profileDigest,
      testItems: ['TM109'], dispatchId: task.dispatchId,
      runRoot: path.join(workspaceRoot, 'Training_Materials/runs/parent-smoke'),
      registryDigest: progress.registryDigest, signal: new AbortController().signal };
  };
  return { workspaceRoot, request };
}
function completedDft(root, sourceRunId, gateStatus = 'ready') {
  const directory = path.join(root, 'Training_Materials/runs', sourceRunId);
  const stateFile = path.join(directory, 'state.json');
  const evidenceRelative = `Training_Materials/runs/${sourceRunId}/evidence/dft-preflight.json`;
  const evidence = { runId: sourceRunId, reports: [{ tm: 'TM109', gate: 'DFT_OUTPUT',
    status: gateStatus, exitCode: gateStatus === 'ready' ? 0 : 2 }] };
  fs.mkdirSync(path.dirname(path.join(root, evidenceRelative)), { recursive: true });
  fs.writeFileSync(path.join(root, evidenceRelative), JSON.stringify(evidence));
  const state = JSON.parse(fs.readFileSync(stateFile));
  fs.writeFileSync(stateFile, JSON.stringify({ ...state, status: 'completed',
    outcome: { mode: 'UNCHANGED', evidence: evidenceRelative, modelDispatched: false } }));
}
function completedStatistic(root, sourceRunId) {
  const directory = path.join(root, 'Training_Materials/runs', sourceRunId);
  const stateFile = path.join(directory, 'state.json');
  const evidenceFile = path.join(directory, 'evidence/component-statistic-only.json');
  fs.mkdirSync(path.dirname(evidenceFile), { recursive: true });
  fs.writeFileSync(evidenceFile, JSON.stringify({ runId: sourceRunId, purpose: 'schematic-statistic-only',
    gatePassed: false, modelDispatched: false }));
  const state = JSON.parse(fs.readFileSync(stateFile));
  fs.writeFileSync(stateFile, JSON.stringify({ ...state, status: 'completed',
    outcome: { mode: 'STATISTIC_ONLY', report: { path: evidenceFile,
      gatePassed: false, modelDispatched: false } } }));
}

test('DFT source creates a new run, checks real gate reports and seals parent evidence', async t => {
  const f = fixture(t);
  let dispatchedModel = false;
  const adapter = createSimpleOrchestrationSourceAdapters(f.workspaceRoot, {
    executeDftRun: async (root, input) => {
      completedDft(root, input.runId);
      return { state: JSON.parse(fs.readFileSync(path.join(root, 'Training_Materials/runs', input.runId, 'state.json'))) };
    },
    dispatchModel: () => { dispatchedModel = true; }, stopDftRun: () => {},
  });
  const result = await adapter.executeSmokeRole(f.request('dft-expert'));
  assert.equal(result.status, 'done');
  assert.equal(result.executionKind, 'dft-delivery');
  assert.equal(result.dftGateStatus, 'ready');
  assert.equal(dispatchedModel, false);
  assert.equal(JSON.parse(fs.readFileSync(result.childEvidencePath)).dispatchId, f.request('dft-expert').dispatchId);
  assert.deepEqual(adapter.recoverSmokeRole(f.request('dft-expert')), result);
});

test('a stale DFT gate blocks parent source receipt', async t => {
  const f = fixture(t);
  const adapter = createSimpleOrchestrationSourceAdapters(f.workspaceRoot, {
    executeDftRun: async (root, input) => { completedDft(root, input.runId, 'stale'); return {}; },
  });
  await assert.rejects(adapter.executeSmokeRole(f.request('dft-expert')), /not every DFT TM/);
});

test('schematic source only accepts statistic-only completion, never a full business gate', async t => {
  const f = fixture(t);
  const adapter = createSimpleOrchestrationSourceAdapters(f.workspaceRoot, {
    pipelineManager: { start(input) { completedStatistic(f.workspaceRoot, input.runId);
      return { completion: Promise.resolve() }; }, control() {} },
  });
  const result = await adapter.executeSmokeRole(f.request('schematic-expert'));
  assert.equal(result.executionKind, 'statistic-only');
  assert.equal(result.businessGatePassed, false);
  assert.equal(JSON.parse(fs.readFileSync(result.childEvidencePath)).sourceMode, 'STATISTIC_ONLY');
});
