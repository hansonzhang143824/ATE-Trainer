import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createRunContext, persistRunContext, runWriteDecision } from '../lib/run-context.js';

test('training identity is immutable and binds one isolated run directory', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-context-'));
  const context = createRunContext(root, {
    mode: 'training', runId: 'training-001', createdAt: '2026-09-22T00:00:00.000Z',
  });
  assert.equal(context.profileSource, 'draft');
  assert.equal(context.releaseId, null);
  assert.equal(context.artifactRoot, path.join('Training_Materials', 'runs', 'training-001'));
  assert.equal(Object.isFrozen(context), true);
  assert.throws(() => { context.mode = 'delivery'; }, TypeError);

  assert.equal(runWriteDecision(root, context, 'Training_Materials/runs/training-001/dft/output.json').allowed, true);
  assert.equal(runWriteDecision(root, context, 'Training_Materials/runs/training-002/output.json').allowed, false);
  assert.equal(runWriteDecision(root, context, 'project/DALI/Output_Global_Material/dft/TM109/dft-meta.json').allowed, false);
  assert.equal(runWriteDecision(root, context, 'team/expert-profiles/ptc-dft-expert/versions/v7/instructions.md').allowed, false);
});

test('delivery identity pins release and project for its lifetime', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-delivery-context-'));
  const context = createRunContext(root, {
    mode: 'delivery', runId: 'dali-001-tm109', releaseId: 'ptc-release-v1', projectId: 'DALI',
    createdAt: '2026-09-22T00:00:00.000Z',
  });
  assert.equal(context.releaseId, 'ptc-release-v1');
  assert.equal(context.profileSource, 'team/ptc/releases/ptc-release-v1/profiles');
  assert.equal(runWriteDecision(root, context, 'project/DALI/Output_Global_Material/dft/TM109/dft-meta.json').allowed, true);
  assert.equal(runWriteDecision(root, context, 'team/artifacts/dali-001-tm109/method/contract.json').allowed, true);
  assert.equal(runWriteDecision(root, context, 'Training_Materials/runs/training-001/output.json').allowed, false);
  assert.equal(runWriteDecision(root, context, 'team/expert-profiles/ptc-dft-expert/instructions.md').allowed, false);
});

test('invalid or mixed identities fail closed', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-invalid-context-'));
  assert.throws(() => createRunContext(root, { mode: 'training', runId: '../escape' }), /runId/);
  assert.throws(() => createRunContext(root, { mode: 'training', runId: 'x', releaseId: 'v1' }), /cannot bind releaseId/);
  assert.throws(() => createRunContext(root, { mode: 'delivery', runId: 'x', projectId: 'DALI' }), /releaseId/);
});

test('persisted run identity is atomic and cannot be replaced', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-persist-context-'));
  const context = createRunContext(root, {
    mode: 'training', runId: 'training-001', createdAt: '2026-09-22T00:00:00.000Z',
  });
  const file = persistRunContext(root, context);
  assert.equal(path.basename(file), 'run.json');
  assert.equal(JSON.parse(fs.readFileSync(file, 'utf8')).mode, 'training');
  assert.equal(persistRunContext(root, context), file, 'identical persistence is idempotent');
  fs.writeFileSync(file, '{"mode":"delivery"}\n', 'utf8');
  assert.throws(() => persistRunContext(root, context), /different content/);
});

test('forged or incomplete context cannot redirect run writes or persistence', (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-context-forgery-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const context = createRunContext(root, { mode: 'training', runId: 'safe-run' });
  for (const forged of [null, {}, { ...context, mode: 'other' }, { ...context, artifactRoot: '.' }, { ...context, artifactRoot: 'project/DALI' }, { ...context, projectId: 'DALI' }, { ...context, profileSource: 'published' }, { ...context, schemaVersion: 0 }, { ...context, createdAt: 'invalid' }, { ...context, runId: 'different' }]) {
    assert.equal(runWriteDecision(root, forged, 'project/DALI/owned.txt').allowed, false);
    assert.throws(() => persistRunContext(root, forged));
  }
  for (const name of ['CON', 'com1.json', 'safe.', 'NUL', 'name:stream']) {
    assert.throws(() => createRunContext(root, { mode: 'training', runId: name }), /runId/);
  }
  assert.equal(fs.existsSync(path.join(root, 'project')), false);
});

test('coarse write boundary rejects root and target junctions plus hardlinks', (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-context-links-'));
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-context-outside-'));
  t.after(() => fs.rmSync(outside, { recursive: true, force: true }));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const context = createRunContext(root, { mode: 'training', runId: 'safe-run' });
  const runRoot = path.join(root, context.artifactRoot);
  fs.mkdirSync(runRoot, { recursive: true });
  const alias = path.join(outside, 'workspace-alias');
  fs.symlinkSync(root, alias, process.platform === 'win32' ? 'junction' : 'dir');
  assert.equal(runWriteDecision(alias, context, `${context.artifactRoot}/new.txt`).allowed, false);
  assert.throws(() => persistRunContext(alias, context), /link|junction/);
  fs.symlinkSync(outside, path.join(runRoot, 'escape'), process.platform === 'win32' ? 'junction' : 'dir');
  assert.equal(runWriteDecision(root, context, `${context.artifactRoot}/escape/new.txt`).allowed, false);
  const other = path.join(outside, 'outside.txt');
  fs.writeFileSync(other, 'untouched');
  fs.linkSync(other, path.join(runRoot, 'linked.txt'));
  assert.equal(runWriteDecision(root, context, `${context.artifactRoot}/linked.txt`).allowed, false);
  assert.equal(fs.readFileSync(other, 'utf8'), 'untouched');
});

test('Windows case variants keep the same boundary and cannot unlock releases', (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-context-case-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const context = createRunContext(root, { mode: 'training', runId: 'safe-run' });
  if (process.platform === 'win32') assert.equal(runWriteDecision(root, context, 'training_materials/RUNS/SAFE-RUN/output.json').allowed, true);
  assert.equal(runWriteDecision(root, context, 'TEAM/PTC/RELEASES/r1/profile.json').allowed, false);
  assert.equal(runWriteDecision(root, context, `${context.artifactRoot}/VERSIONS/v1/profile.json`).allowed, process.platform !== 'win32');
});
