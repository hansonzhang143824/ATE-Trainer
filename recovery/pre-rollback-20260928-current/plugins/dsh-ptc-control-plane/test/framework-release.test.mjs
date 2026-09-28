import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { createTrainingRun } from '../lib/training-run.js';
import { sha256Bytes } from '../lib/release-integrity.js';
import { activateStagedFrameworkRelease, FRAMEWORK_RUNTIME_FILES, listFrameworkReleases, loadFrameworkRelease,
  verifyFrameworkRuntimeCompatibility,
  stageFrameworkRelease } from '../lib/framework-release.js';

function fixture(t) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-framework-release-'));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const write = (name, value) => {
    const file = path.join(workspaceRoot, name);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, Buffer.isBuffer(value) ? value : typeof value === 'object' ? `${JSON.stringify(value)}\n` : value);
    return file;
  };
  const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
  for (const name of FRAMEWORK_RUNTIME_FILES) {
    write(name, fs.readFileSync(path.join(repositoryRoot, name)));
  }
  const registry = {
    stateMachine: ['INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD', 'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION', 'COMPILE', 'COMPLETE'],
    stages: Object.fromEntries(['INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD', 'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION', 'COMPILE']
      .map(stage => [stage, { gate: `framework/${stage.toLowerCase()}` }])),
  };
  write('team/ptc/ptc_stage_registry.json', registry);
  const sourceRunId = 'training-rehearsal-1';
  const { context, state } = createTrainingRun(workspaceRoot, { runId: sourceRunId,
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' }, purpose: 'framework-rehearsal' });
  const runRelative = context.artifactRoot;
  write(`${runRelative}/state.json`, { ...state, status: 'completed',
    outcome: { mode: 'FRAMEWORK_REHEARSAL', result: '流程演练通过', realBusinessGatesPassed: false } });
  write(`${runRelative}/pipeline-registry.json`, registry);
  write(`${runRelative}/pipeline-progress.json`, { runId: sourceRunId, status: 'completed',
    stages: registry.stateMachine.filter(stage => stage !== 'COMPLETE').map(stage => ({ stage, status: 'completed',
      gateResult: { status: 'passed', exitCode: 0, gate: registry.stages[stage].gate } })) });
  const payload = Buffer.from([0, 10, 13, 255, 42]);
  write(`${runRelative}/rehearsal/COMPILE/TM109/handoff.bin`, payload);
  const root = path.join(workspaceRoot, 'team/ptc/framework-releases');
  const pointer = () => fs.readFileSync(path.join(root, 'active-framework-release.json'), 'utf8');
  const options = (releaseId = 'framework-v1') => ({ workspaceRoot, releaseId, sourceRunId,
    createdBy: 'native-training-controller', verifyRehearsal: async ({ runId }) => ({
      kind: 'framework-rehearsal', status: 'passed', runId,
    }) });
  return { workspaceRoot, sourceRunId, runRelative, root, pointer, options, write, payload };
}

test('freeze exact bytes, activate separately, and ignore later training draft changes', async t => {
  const f = fixture(t);
  const staged = await stageFrameworkRelease(f.options());
  assert.equal(staged.manifest.kind, 'framework-rehearsal');
  assert.equal(staged.manifest.realBusinessGatesPassed, false);
  assert.throws(f.pointer, { code: 'ENOENT' });
  const activated = activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  assert.equal(activated.releaseId, 'framework-v1');
  assert.equal(activated.previousReleaseId, null);
  const frozen = loadFrameworkRelease({ workspaceRoot: f.workspaceRoot });
  assert.equal(verifyFrameworkRuntimeCompatibility({ workspaceRoot: f.workspaceRoot }).compatible, true);
  assert.deepEqual(fs.readFileSync(path.join(frozen.snapshotRoot, 'rehearsal/COMPILE/TM109/handoff.bin')), f.payload);
  f.write('team/expert-profiles/ptc-dft-expert/draft.md', 'changed after framework publication\n');
  f.write(`${f.runRelative}/rehearsal/COMPILE/TM109/handoff.bin`, 'changed source');
  assert.deepEqual(fs.readFileSync(path.join(loadFrameworkRelease({ workspaceRoot: f.workspaceRoot }).snapshotRoot,
    'rehearsal/COMPILE/TM109/handoff.bin')), f.payload);
  assert.equal(fs.existsSync(path.join(f.workspaceRoot, 'team/ptc/releases/active-release.json')), false);
  assert.equal(listFrameworkReleases({ workspaceRoot: f.workspaceRoot }).releases[0].valid, true);
});

test('reject failed or missing trusted rehearsal verifier without publishing', async t => {
  const f = fixture(t);
  await assert.rejects(stageFrameworkRelease({ ...f.options(), verifyRehearsal: undefined }), /verifier is required/);
  await assert.rejects(stageFrameworkRelease({ ...f.options(), verifyRehearsal: () => ({
    kind: 'framework-rehearsal', status: 'failed', runId: f.sourceRunId,
  }) }), /did not pass/);
  assert.throws(f.pointer, { code: 'ENOENT' });
});

test('reject wrong run purpose or incomplete chain', async t => {
  const f = fixture(t);
  const stateFile = path.join(f.workspaceRoot, f.runRelative, 'state.json');
  const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
  f.write(`${f.runRelative}/state.json`, { ...state, purpose: 'business-training' });
  await assert.rejects(stageFrameworkRelease(f.options()), /not a completed full-chain/);
  f.write(`${f.runRelative}/state.json`, state);
  const progress = JSON.parse(fs.readFileSync(path.join(f.workspaceRoot, f.runRelative, 'pipeline-progress.json'), 'utf8'));
  progress.stages[2].status = 'pending';
  f.write(`${f.runRelative}/pipeline-progress.json`, progress);
  await assert.rejects(stageFrameworkRelease(f.options()), /not a completed full-chain/);
});

test('tampered staged or active bytes fail closed and keep the previous pointer', async t => {
  const f = fixture(t);
  const first = await stageFrameworkRelease(f.options());
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: first.stagingId });
  const before = f.pointer();
  const second = await stageFrameworkRelease(f.options('framework-v2'));
  f.write(`team/ptc/framework-releases/.staging/${second.stagingId}/snapshot/rehearsal/COMPILE/TM109/handoff.bin`, 'tampered');
  assert.throws(() => activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: second.stagingId }), /mismatch/);
  assert.equal(f.pointer(), before);
  assert.equal(fs.existsSync(path.join(f.root, 'framework-v2')), false);
  f.write('team/ptc/framework-releases/framework-v1/snapshot/rehearsal/COMPILE/TM109/handoff.bin', 'tampered active');
  assert.throws(() => loadFrameworkRelease({ workspaceRoot: f.workspaceRoot }), /mismatch/);
});

test('duplicate version and stale staging cannot replace an active pointer', async t => {
  const f = fixture(t);
  const first = await stageFrameworkRelease(f.options());
  const second = await stageFrameworkRelease(f.options('framework-v2'));
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: first.stagingId });
  const before = f.pointer();
  await assert.rejects(stageFrameworkRelease(f.options()), /already exists/);
  assert.throws(() => activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: second.stagingId }), /changed since staging/);
  assert.equal(f.pointer(), before);
});

test('linked source files cannot enter a frozen version', async t => {
  const f = fixture(t);
  const link = path.join(f.workspaceRoot, f.runRelative, 'rehearsal/linked.bin');
  try { fs.linkSync(path.join(f.workspaceRoot, f.runRelative, 'rehearsal/COMPILE/TM109/handoff.bin'), link); }
  catch (error) { if (error.code === 'EPERM') return t.skip('hard links unavailable'); throw error; }
  await assert.rejects(stageFrameworkRelease(f.options()), /linked snapshot entry|hard-linked/);
});

test('every source filename is snapshotted and source mutation during verification fails', async t => {
  const f = fixture(t);
  f.write(`${f.runRelative}/framework-release-manifest.json`, 'ordinary source bytes');
  await assert.rejects(stageFrameworkRelease({ ...f.options(), verifyRehearsal: ({ runId }) => {
    f.write(`${f.runRelative}/rehearsal/COMPILE/TM109/handoff.bin`, 'changed while verifying');
    return { kind: 'framework-rehearsal', status: 'passed', runId };
  } }), /source changed during verification/);
  const staged = await stageFrameworkRelease(f.options());
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  const release = loadFrameworkRelease({ workspaceRoot: f.workspaceRoot });
  assert.equal(fs.readFileSync(path.join(release.snapshotRoot, 'framework-release-manifest.json'), 'utf8'), 'ordinary source bytes');
});

test('published runtime rejects implementation drift while keeping frozen bytes', async t => {
  const f = fixture(t);
  const staged = await stageFrameworkRelease(f.options());
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  const before = f.pointer();
  const implementation = FRAMEWORK_RUNTIME_FILES.find(name => name.endsWith('/framework-rehearsal.js'));
  const frozen = fs.readFileSync(path.join(loadFrameworkRelease({ workspaceRoot: f.workspaceRoot }).runtimeRoot, implementation));
  f.write(implementation, 'changed mutable implementation');
  assert.throws(() => verifyFrameworkRuntimeCompatibility({ workspaceRoot: f.workspaceRoot }), /current runtime implementation differs/);
  assert.deepEqual(fs.readFileSync(path.join(loadFrameworkRelease({ workspaceRoot: f.workspaceRoot }).runtimeRoot, implementation)), frozen);
  assert.equal(f.pointer(), before);
});

test('a legacy runtime file set remains verifiable but cannot execute or block a new publication', async t => {
  const f = fixture(t);
  const staged = await stageFrameworkRelease(f.options());
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  const releaseRoot = path.join(f.root, 'framework-v1');
  const manifestFile = path.join(releaseRoot, 'framework-release-manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestFile, 'utf8'));
  const legacy = new Set([
    'plugins/dsh-ptc-control-plane/client/panel.js',
    'plugins/dsh-ptc-control-plane/client/state.js',
    'plugins/dsh-ptc-control-plane/lib/client.js',
    'plugins/dsh-ptc-control-plane/lib/control-state.js',
    'plugins/dsh-ptc-control-plane/lib/framework-published-run.js',
    'plugins/dsh-ptc-control-plane/lib/framework-rehearsal-manager.js',
    'plugins/dsh-ptc-control-plane/lib/framework-rehearsal-source.js',
    'plugins/dsh-ptc-control-plane/lib/framework-rehearsal.js',
    'plugins/dsh-ptc-control-plane/lib/framework-release.js',
    'plugins/dsh-ptc-control-plane/lib/host-command.js',
    'plugins/dsh-ptc-control-plane/lib/index.js',
    'plugins/dsh-ptc-control-plane/lib/release-integrity.js',
    'plugins/dsh-ptc-control-plane/lib/run-context.js',
    'plugins/dsh-ptc-control-plane/lib/training-paths.js',
    'plugins/dsh-ptc-control-plane/lib/training-pipeline.js',
    'scripts/dft_source.py',
    'scripts/material_plaintext_hash.py',
    'scripts/ptc_contract_schema.py',
    'scripts/ptc_trim_validation.py',
    'scripts/validate_dft_outputs.py',
    'scripts/validate_schematic_outputs.py',
  ]);
  for (const name of FRAMEWORK_RUNTIME_FILES.filter(name => !legacy.has(name))) {
    fs.unlinkSync(path.join(releaseRoot, 'runtime', name));
  }
  const digest = files => sha256Bytes(Buffer.from(files.map(file => `${file.path}\0${file.size}\0${file.sha256}\n`).join(''), 'utf8'));
  manifest.files = manifest.files.filter(file => !file.path.startsWith('runtime/') || legacy.has(file.path.slice('runtime/'.length)));
  manifest.runtimeDigest = digest(manifest.files.filter(file => file.path.startsWith('runtime/')));
  manifest.bundleDigest = digest(manifest.files);
  fs.writeFileSync(manifestFile, `${JSON.stringify(manifest)}\n`);
  const pointerFile = path.join(f.root, 'active-framework-release.json');
  const pointer = JSON.parse(fs.readFileSync(pointerFile, 'utf8'));
  pointer.bundleDigest = manifest.bundleDigest;
  fs.writeFileSync(pointerFile, `${JSON.stringify(pointer)}\n`);
  assert.equal(loadFrameworkRelease({ workspaceRoot: f.workspaceRoot }).manifest.runtimeDigest, manifest.runtimeDigest);
  assert.throws(() => verifyFrameworkRuntimeCompatibility({ workspaceRoot: f.workspaceRoot }), /current runtime implementation differs/);
  const next = await stageFrameworkRelease(f.options('framework-v2'));
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: next.stagingId });
  assert.equal(verifyFrameworkRuntimeCompatibility({ workspaceRoot: f.workspaceRoot }).compatible, true);
});

test('tampering with frozen runtime implementation is detected before dispatch', async t => {
  const f = fixture(t);
  const staged = await stageFrameworkRelease(f.options());
  activateStagedFrameworkRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  const name = FRAMEWORK_RUNTIME_FILES.find(file => file.endsWith('/framework-rehearsal-manager.js'));
  f.write(`team/ptc/framework-releases/framework-v1/runtime/${name}`, 'tampered frozen runtime');
  assert.throws(() => loadFrameworkRelease({ workspaceRoot: f.workspaceRoot }), /mismatch/);
  assert.throws(() => verifyFrameworkRuntimeCompatibility({ workspaceRoot: f.workspaceRoot }), /mismatch/);
});
