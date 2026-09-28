import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';
import { createSimpleOrchestrationManager } from '../lib/simple-orchestration-manager.js';

const stageNames = ['INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD',
  'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION', 'COMPILE'];
const owners = ['captain', 'test-strategy-architect', 'test-method-expert', 'rule-reviewer',
  'ate-implementer', 'rule-reviewer', 'compile-diagnostician'];
const profiles = ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert', 'method-expert',
  'rule-reviewer', 'ate-implementer', 'compile-diagnostician', 'evolution-expert'];
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-simple-manager-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, 'team/ptc'), { recursive: true });
  fs.writeFileSync(path.join(root, 'team/ptc/ptc_stage_registry.json'), JSON.stringify({
    stateMachine: [...stageNames, 'COMPLETE'],
    stages: Object.fromEntries(stageNames.map((stage, i) => [stage,
      { owner: owners[i], gate: `scripts/gate-${i}.py` }])),
  }));
  const profileRunIds = {};
  for (const [i, profileId] of profiles.entries()) {
    const runId = `training-profile-${i}`;
    fs.mkdirSync(path.join(root, `team/expert-profiles/${profileId}`), { recursive: true });
    createTrainingRun(root, { runId, target: { kind: 'profile', profileId }, purpose: 'smoke-training' });
    const base = path.join(root, `Training_Materials/runs/${runId}`);
    fs.mkdirSync(path.join(base, 'profile'), { recursive: true });
    fs.writeFileSync(path.join(base, 'profile/snapshot.json'), JSON.stringify({
      kind: 'ptc-profile-smoke-snapshot', runId, profileId, files: [],
    }));
    const stateFile = path.join(base, 'state.json');
    const state = JSON.parse(fs.readFileSync(stateFile));
    fs.writeFileSync(stateFile, JSON.stringify({ ...state, status: 'completed',
      outcome: { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false } }));
    profileRunIds[profileId] = runId;
  }
  createTrainingRun(root, { runId: 'training-pipeline', target: { kind: 'pipeline' }, purpose: 'smoke-training' });
  return { root, profileRunIds };
}

test('manager requires eight distinct arithmetic profile runs including DFT and schematic', async t => {
  const f = fixture(t);
  const calls = [];
  const manager = createSimpleOrchestrationManager(f.root, { executeSmokeRole: async request => {
    calls.push(`${request.stage}/${request.role}`);
    const file = path.join(request.runRoot, `evidence-${calls.length}.json`);
    fs.writeFileSync(file, JSON.stringify({ runId: request.runId, dispatchId: request.dispatchId,
      stage: request.stage, role: request.role, executionKind: 'arithmetic-child',
      businessGatePassed: false, childSessionId: `child-${calls.length}`, answer: 3 }));
    return { status: 'done', executionKind: 'arithmetic-child', stage: request.stage,
      role: request.role, profileId: request.profileId, profileVersion: request.profileVersion,
      profileDigest: request.profileDigest, testItems: request.testItems,
      businessGatePassed: false, childReceiptId: `receipt-${calls.length}`,
      childEvidencePath: file, childEvidenceSha256: sha(fs.readFileSync(file)) };
  } });
  assert.throws(() => manager.start({ runId: 'training-pipeline', testItems: ['TM109'],
    profileRunIds: Object.fromEntries(Object.entries(f.profileRunIds).slice(2)) }), /eight completed/);
  const run = manager.start({ runId: 'training-pipeline', testItems: ['TM109'], profileRunIds: f.profileRunIds });
  const state = await run.completion;
  assert.equal(state.status, 'completed');
  assert.equal(calls.length, 9, 'eight unique experts, rule reviewer dispatched for two stages');
  assert.deepEqual(calls.slice(0, 2), ['INPUT_SYNC/dft-expert', 'INPUT_SYNC/schematic-expert']);
  assert.ok(state.stages.every(stage => stage.businessGatePassed === false));
});

test('manager accepts only the two completed source roles for an INPUT_SYNC pilot', async t => {
  const f = fixture(t);
  createTrainingRun(f.root, { runId: 'training-pilot', purpose: 'smoke-training',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' } });
  const pair = Object.fromEntries(Object.entries(f.profileRunIds).slice(0, 2));
  const calls = [];
  const manager = createSimpleOrchestrationManager(f.root, { executeSmokeRole: async request => {
    calls.push(request.role);
    const file = path.join(request.runRoot, `evidence-${calls.length}.json`);
    fs.writeFileSync(file, JSON.stringify({ runId: request.runId, dispatchId: request.dispatchId,
      stage: request.stage, role: request.role, executionKind: 'arithmetic-child',
      businessGatePassed: false, childSessionId: `pilot-child-${calls.length}`, answer: 3 }));
    return { status: 'done', executionKind: 'arithmetic-child', stage: request.stage,
      role: request.role, profileId: request.profileId, profileVersion: request.profileVersion,
      profileDigest: request.profileDigest, testItems: request.testItems,
      businessGatePassed: false, childReceiptId: `pilot-receipt-${calls.length}`,
      childEvidencePath: file, childEvidenceSha256: sha(fs.readFileSync(file)) };
  } });
  assert.throws(() => manager.start({ runId: 'training-pilot', pilot: true,
    testItems: ['TM109'], profileRunIds: f.profileRunIds }), /two completed/);
  const result = await manager.start({ runId: 'training-pilot', pilot: true,
    testItems: ['TM109'], profileRunIds: pair }).completion;
  assert.equal(result.scope, 'INPUT_SYNC_PILOT');
  assert.equal(result.status, 'completed');
  assert.deepEqual(calls, ['dft-expert', 'schematic-expert']);
  assert.deepEqual(result.stages[0].tasks.map(task => task.answer), [3, 3]);
  assert.equal(result.businessGatePassed, false);
});
