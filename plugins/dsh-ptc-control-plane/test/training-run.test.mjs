import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createTrainingRun } from '../lib/training-run.js';

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

test('single-profile training creates an isolated immutable identity', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-profile-training-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  const result = createTrainingRun(root, {
    target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  }, { now: new Date('2026-09-22T01:02:03.000Z'), suffix: 'test0001' });
  assert.equal(result.context.runId, 'training-20260922t010203z-test0001');
  assert.equal(result.context.mode, 'training');
  assert.equal(result.state.status, 'created');
  assert.deepEqual(result.state.target, { kind: 'profile', profileId: 'ptc-dft-expert' });
  assert.equal(fs.existsSync(result.runFile), true);
  assert.equal(fs.existsSync(result.stateFile), true);
});

test('pipeline training freezes the selected ordered stage range', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-pipeline-training-'));
  writeJson(path.join(root, 'team/ptc/ptc_stage_registry.json'), {
    stateMachine: ['INPUT_SYNC', 'STRATEGY', 'METHOD', 'COMPILE', 'COMPLETE'],
  });
  const result = createTrainingRun(root, {
    runId: 'training-pipeline-001',
    target: { kind: 'pipeline', fromStage: 'STRATEGY', toStage: 'COMPILE' },
  }, { now: new Date('2026-09-22T01:02:03.000Z') });
  assert.deepEqual(result.state.target, {
    kind: 'pipeline', fromStage: 'STRATEGY', toStage: 'COMPILE', stages: ['STRATEGY', 'METHOD', 'COMPILE'],
  });
});

test('unknown profiles and invalid pipeline order fail before creating a run', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-invalid-training-'));
  writeJson(path.join(root, 'team/ptc/ptc_stage_registry.json'), {
    stateMachine: ['INPUT_SYNC', 'STRATEGY', 'COMPLETE'],
  });
  assert.throws(() => createTrainingRun(root, {
    runId: 'training-unknown', target: { kind: 'profile', profileId: 'missing-expert' },
  }), /unknown expert profile/);
  assert.throws(() => createTrainingRun(root, {
    runId: 'training-reversed', target: { kind: 'pipeline', fromStage: 'STRATEGY', toStage: 'INPUT_SYNC' },
  }), /ordered stage range/);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/runs')), false);
});

test('duplicate run creation preserves terminal state and all existing run data', (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-duplicate-training-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  const input = { runId: 'training-duplicate', target: { kind: 'profile', profileId: 'ptc-dft-expert' } };
  const options = { now: new Date('2026-09-22T01:02:03.000Z') };
  const created = createTrainingRun(root, input, options);
  const runBytes = fs.readFileSync(created.runFile);
  fs.writeFileSync(created.stateFile, JSON.stringify({ ...created.state, status: 'completed', outcome: { mode: 'UNCHANGED' } }));
  const stateBytes = fs.readFileSync(created.stateFile);
  const product = path.join(path.dirname(created.runFile), 'evidence.json');
  fs.writeFileSync(product, 'keep evidence');
  assert.throws(() => createTrainingRun(root, input, options), /already exists/);
  assert.deepEqual(fs.readFileSync(created.runFile), runBytes);
  assert.deepEqual(fs.readFileSync(created.stateFile), stateBytes);
  assert.equal(fs.readFileSync(product, 'utf8'), 'keep evidence');
});

test('preexisting empty or partial run directories stay reserved', (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-reserved-training-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  for (const runId of ['training-empty', 'training-partial']) {
    const directory = path.join(root, 'Training_Materials/runs', runId);
    fs.mkdirSync(directory, { recursive: true });
    if (runId === 'training-partial') fs.writeFileSync(path.join(directory, 'state.json'), 'partial');
    assert.throws(() => createTrainingRun(root, { runId, target: { kind: 'profile', profileId: 'ptc-dft-expert' } }), /already exists/);
    assert.equal(fs.existsSync(path.join(directory, 'run.json')), false);
  }
  assert.equal(fs.readFileSync(path.join(root, 'Training_Materials/runs/training-partial/state.json'), 'utf8'), 'partial');
});
