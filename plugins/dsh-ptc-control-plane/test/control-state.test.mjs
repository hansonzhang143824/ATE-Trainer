import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { buildControlState } from '../lib/control-state.js';

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

test('control state separates legacy mode from authoritative run identity', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-control-state-'));
  writeJson(path.join(root, 'Training_Materials/_expert_bindings.json'), { activeMode: 'training' });
  writeJson(path.join(root, 'team/expert-profiles/ptc-dft-expert/status.json'), {
    publishedVersion: 'v7', manifestDigest: 'abc', draftVerdict: 'pass',
  });
  writeJson(path.join(root, 'team/ptc/releases/active-release.json'), {
    releaseId: 'ptc-release-v1', manifestDigest: 'release-digest', activatedAt: '2026-09-22T00:00:00.000Z',
  });
  writeJson(path.join(root, 'Training_Materials/runs/training-001/run.json'), {
    mode: 'training', status: 'running', target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  });
  writeJson(path.join(root, 'team/artifacts/ptc-batches/dali-test.json'), {
    batchId: 'dali-test', state: 'INPUT_SYNC', releaseId: 'ptc-release-v1',
  });

  const state = buildControlState(root);
  assert.equal(state.identity, 'unbound');
  assert.equal(state.migration.legacyMode, 'training');
  assert.equal(state.migration.legacyModeAuthoritative, false);
  assert.equal(state.activeRelease.releaseId, 'ptc-release-v1');
  assert.equal(state.trainingRuns[0].runId, 'training-001');
  assert.equal(state.delivery.batchId, 'dali-test');
  assert.deepEqual(state.profiles[0], {
    profileId: 'ptc-dft-expert', publishedVersion: 'v7', manifestDigest: 'abc', draftVerdict: 'pass',
  });
});

test('control state is safe when no native release or runs exist yet', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-control-empty-'));
  const state = buildControlState(root);
  assert.equal(state.activeRelease, null);
  assert.equal(state.delivery, null);
  assert.deepEqual(state.trainingRuns, []);
  assert.deepEqual(state.profiles, []);
  assert.deepEqual(state.pipelineStages, []);
});

test('control state reads registry stages and run-local pipeline progress without inventing completion', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-pipeline-state-'));
  // Keep this small fixture, as the existing tests do: protected Windows hosts
  // can stall inside recursive Node cleanup after all assertions complete.
  writeJson(path.join(root, 'team/ptc/ptc_stage_registry.json'), {
    stateMachine: ['INPUT_SYNC', 'METHOD', 'COMPILE', 'COMPLETE'],
    stages: { INPUT_SYNC: { gate: 'source.py' }, METHOD: { gate: 'method.py' }, COMPILE: { gate: 'compile.py' } },
  });
  const runRoot = path.join(root, 'Training_Materials/runs/pipeline-1');
  writeJson(path.join(runRoot, 'run.json'), { mode: 'training', artifactRoot: runRoot });
  writeJson(path.join(runRoot, 'state.json'), {
    status: 'pausing', target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' }, testItems: ['TM109'],
  });
  const pipeline = { runId: 'pipeline-1', status: 'running', reason: null, stages: [
    { stage: 'INPUT_SYNC', status: 'completed', gateResult: { status: 'passed', exitCode: 0 } },
    { stage: 'METHOD', status: 'gating', gateResult: null },
  ] };
  writeJson(path.join(runRoot, 'pipeline-progress.json'), pipeline);
  const state = buildControlState(root);
  assert.deepEqual(state.pipelineStages, ['INPUT_SYNC', 'METHOD', 'COMPILE']);
  assert.deepEqual(state.trainingRuns[0].pipeline, pipeline);
  assert.equal(state.trainingRuns[0].status, 'pausing', 'host state retains lifecycle authority');
  writeJson(path.join(runRoot, 'pipeline-progress.json'), { ...pipeline, runId: 'another-run', status: 'completed' });
  assert.equal(buildControlState(root).trainingRuns[0].pipeline, null, 'wrong-run progress is not displayed');
});

test('control state offers only participating run-local source owners for training issues', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-control-issue-owners-'));
  const runRoot = path.join(root, 'Training_Materials/runs/pipeline-owners');
  writeJson(path.join(runRoot, 'run.json'), { mode: 'training' });
  writeJson(path.join(runRoot, 'state.json'), {
    status: 'blocked', purpose: 'business-training', target: { kind: 'pipeline', stages: ['INPUT_SYNC'] },
  });
  writeJson(path.join(runRoot, 'pipeline-progress.json'), {
    runId: 'pipeline-owners', sourceRoles: ['dft-expert', 'schematic-expert'], status: 'blocked',
  });
  writeJson(path.join(runRoot, 'pipeline-material-manifest.json'), {
    runId: 'pipeline-owners', ownerProfiles: {
      'dft-expert': 'ptc-dft-expert', 'schematic-expert': 'ptc-schematic-expert',
      'test-method-expert': 'method-expert',
    },
  });
  const [run] = buildControlState(root).trainingRuns;
  assert.deepEqual(run.issueOwners, [
    { sourceRole: 'dft-expert', profileId: 'ptc-dft-expert' },
    { sourceRole: 'schematic-expert', profileId: 'ptc-schematic-expert' },
  ]);
  writeJson(path.join(runRoot, 'pipeline-material-manifest.json'), {
    runId: 'another-run', ownerProfiles: { 'dft-expert': 'ptc-dft-expert' },
  });
  assert.deepEqual(buildControlState(root).trainingRuns[0].issueOwners, []);
});
