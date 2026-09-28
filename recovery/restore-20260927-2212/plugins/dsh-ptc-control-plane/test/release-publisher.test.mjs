import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { activateStagedRelease, buildCandidateEntries, computeCandidateDigest, listReleases,
  rollbackRelease, stageRelease, validateReleaseManifest } from '../lib/release-publisher.js';
import { sha256Bytes, verifyReleaseDirectory } from '../lib/release-integrity.js';

function fixture(t) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-publisher-test-'));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sources = { profiles: [], orchestration: [], contracts: [], policies: [], verification: [] };
  const write = (name, value) => {
    const file = path.join(workspaceRoot, name);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, typeof value === 'object' && !Buffer.isBuffer(value) ? JSON.stringify(value) : value);
    return file;
  };
  const add = (category, sourcePath, targetPath, value) => {
    write(sourcePath, value);
    sources[category].push({ sourcePath, targetPath });
  };
  add('profiles', 'team/expert-profiles/ptc-dft-expert/instructions.md', 'profiles/ptc-dft-expert/instructions.md', 'draft\r\n');
  add('orchestration', 'team/ptc/ptc_stage_registry.json', 'orchestration/ptc_stage_registry.json', {
    stateMachine: ['INPUT_SYNC', 'COMPILE', 'COMPLETE'],
    stages: { INPUT_SYNC: { gate: 'scripts/input.py' }, COMPILE: { gate: 'scripts/compile.py' } },
  });
  add('contracts', 'team/ptc/contracts/handoff.json', 'contracts/handoff.json', '{}');
  add('policies', 'scripts/input.py', 'policies/input.py', 'print("check")');
  const candidateDigest = computeCandidateDigest({ workspaceRoot, sources });
  const check = (name, fields) => {
    const command = fields.gate ? `python ${fields.gate} --tm TM109` : 'node evaluate-dft.mjs';
    const evidencePath = `verification/${name}-command.json`;
    const content = JSON.stringify({ command, exitCode: 0, candidateDigest, stdout: 'fixture gate passed' });
    add('verification', `Training_Materials/runs/fixture/verification/${name}-command.json`, evidencePath, content);
    return { id: name, result: 'passed', exitCode: 0, command, evidencePath, sha256: sha256Bytes(Buffer.from(content)), ...fields };
  };
  const single = { kind: 'single-agent-evaluation', result: 'passed', candidateDigest,
    checks: [check('dft', { profileId: 'ptc-dft-expert' })] };
  const pipeline = { kind: 'pipeline-regression', result: 'passed', candidateDigest,
    checks: [check('input', { stage: 'INPUT_SYNC', gate: 'scripts/input.py' }), check('compile', { stage: 'COMPILE', gate: 'scripts/compile.py' })] };
  const singlePath = 'Training_Materials/runs/fixture/verification/single-agent-evaluation.json';
  const pipelinePath = 'Training_Materials/runs/fixture/verification/pipeline-regression.json';
  add('verification', singlePath, 'verification/single-agent-evaluation.json', single);
  add('verification', pipelinePath, 'verification/pipeline-regression.json', pipeline);
  const options = { workspaceRoot, releaseId: 'ptc-release-v1', createdBy: 'fixture-evaluator', sources };
  const pointer = () => fs.readFileSync(path.join(workspaceRoot, 'team/ptc/releases/active-release.json'), 'utf8');
  return { workspaceRoot, sources, options, write, single, pipeline, singlePath, pipelinePath, pointer };
}

test('stage preserves exact bytes and activates only a verified complete snapshot', (t) => {
  const f = fixture(t);
  const staged = stageRelease(f.options);
  assert.equal(validateReleaseManifest(staged.manifest), true);
  assert.equal(staged.candidateDigest, computeCandidateDigest(f.options));
  assert.deepEqual(buildCandidateEntries(f.options).map((entry) => entry.path), staged.manifest.files.filter((entry) => !entry.path.startsWith('verification/')).map((entry) => entry.path));
  assert.throws(f.pointer, { code: 'ENOENT' });
  const pointer = activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  assert.equal(pointer.releaseId, 'ptc-release-v1');
  assert.equal(pointer.previousReleaseId, null);
  const directory = path.join(f.workspaceRoot, 'team/ptc/releases/ptc-release-v1');
  assert.equal(verifyReleaseDirectory(directory, staged.manifest).ok, true);
  assert.deepEqual(fs.readFileSync(path.join(directory, 'profiles/ptc-dft-expert/instructions.md')), Buffer.from('draft\r\n'));
  f.write('team/expert-profiles/ptc-dft-expert/instructions.md', 'changed draft');
  assert.equal(verifyReleaseDirectory(directory, staged.manifest).ok, true);
  assert.equal(listReleases(f.options).releases[0].valid, true);
});

test('missing, failed, stale and incomplete regression evidence never changes active release', (t) => {
  const mutations = [
    (f) => { f.sources.verification = f.sources.verification.filter((entry) => !entry.targetPath.endsWith('pipeline-regression.json')); },
    (f) => { f.pipeline.result = 'failed'; f.write(f.pipelinePath, f.pipeline); },
    (f) => { f.single.checks[0].result = 'failed'; f.write(f.singlePath, f.single); },
    (f) => { f.single.candidateDigest = '0'.repeat(64); f.write(f.singlePath, f.single); },
    (f) => { f.pipeline.checks.reverse(); f.write(f.pipelinePath, f.pipeline); },
    (f) => { f.pipeline.checks.pop(); f.write(f.pipelinePath, f.pipeline); },
    (f) => { f.single.checks[0].profileId = 'another-profile'; f.write(f.singlePath, f.single); },
    (f) => { f.single.checks[0].sha256 = '0'.repeat(64); f.write(f.singlePath, f.single); },
    (f) => { f.pipeline.checks[0].gate = 'scripts/other.py'; f.write(f.pipelinePath, f.pipeline); },
    (f) => { f.write('Training_Materials/runs/fixture/verification/dft-command.json', { command: 'node evaluate-dft.mjs', exitCode: 1 }); },
  ];
  for (const mutate of mutations) {
    const f = fixture(t);
    const staged = stageRelease(f.options);
    activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
    const before = f.pointer();
    mutate(f);
    assert.throws(() => stageRelease({ ...f.options, releaseId: 'ptc-release-v2' }));
    assert.equal(f.pointer(), before);
    assert.equal(fs.existsSync(path.join(f.workspaceRoot, 'team/ptc/releases/ptc-release-v2')), false);
  }
});

test('a later draft write invalidates evaluation binding', (t) => {
  const f = fixture(t);
  f.write('team/expert-profiles/ptc-dft-expert/instructions.md', 'new candidate');
  assert.throws(() => stageRelease(f.options), /failed or stale/);
  assert.throws(f.pointer, { code: 'ENOENT' });
});

test('staged tampering is rejected before any active pointer is created', (t) => {
  const f = fixture(t);
  const staged = stageRelease(f.options);
  f.write(`team/ptc/releases/.staging/${staged.stagingId}/contracts/handoff.json`, '{"tampered":true}');
  assert.throws(() => activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId }), /mismatch/);
  assert.throws(f.pointer, { code: 'ENOENT' });
});

test('never overwrite release identity; stale concurrent staging requires restage', (t) => {
  const f = fixture(t);
  const first = stageRelease(f.options);
  const concurrent = stageRelease({ ...f.options, releaseId: 'ptc-release-v2' });
  activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: first.stagingId });
  const before = f.pointer();
  assert.throws(() => stageRelease(f.options), /already exists/);
  assert.throws(() => activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: concurrent.stagingId }), /changed since staging/);
  assert.equal(f.pointer(), before);
});

test('rollback verifies target bytes and preserves release snapshots', (t) => {
  const f = fixture(t);
  for (const releaseId of ['ptc-release-v1', 'ptc-release-v2']) {
    const staged = stageRelease({ ...f.options, releaseId });
    activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  }
  const rolledBack = rollbackRelease({ workspaceRoot: f.workspaceRoot });
  assert.equal(rolledBack.releaseId, 'ptc-release-v1');
  assert.equal(rolledBack.previousReleaseId, 'ptc-release-v2');
  const before = f.pointer();
  f.write('team/ptc/releases/ptc-release-v2/contracts/handoff.json', 'tampered');
  assert.throws(() => rollbackRelease({ workspaceRoot: f.workspaceRoot }), /mismatch/);
  assert.equal(f.pointer(), before);
  assert.equal(listReleases(f.options).releases.find((release) => release.releaseId === 'ptc-release-v2').valid, false);
});

test('invalid source roots, traversal, Windows aliases, duplicate targets and links fail closed', (t) => {
  for (const [sourcePath, targetPath] of [
    ['project/DALI/Input_GlobalMaterial/source.xlsx', 'profiles/ptc-dft-expert/source.xlsx'],
    ['team/expert-profiles/ptc-dft-expert/instructions.md', 'profiles/../escape.md'],
    ['team/expert-profiles/ptc-dft-expert/instructions.md', 'profiles/CON/file.md'],
    ['team/expert-profiles/ptc-dft-expert/instructions.md', 'profiles/dft /file.md'],
    ['team/expert-profiles/ptc-dft-expert/instructions.md', 'profiles/dft/file.md:stream'],
  ]) {
    const f = fixture(t);
    f.sources.profiles[0] = { sourcePath, targetPath };
    assert.throws(() => stageRelease(f.options), /unsafe path|source not allowed/);
  }
  const f = fixture(t);
  f.sources.profiles.push({ ...f.sources.profiles[0], targetPath: f.sources.profiles[0].targetPath.toUpperCase().replace('PROFILES/', 'profiles/') });
  assert.throws(() => stageRelease(f.options), /duplicate target/);
  f.sources.profiles.pop();
  const target = path.join(f.workspaceRoot, f.sources.profiles[0].sourcePath);
  const alternate = f.write('team/expert-profiles/alternate.md', 'alternate');
  fs.unlinkSync(target);
  fs.linkSync(alternate, target);
  assert.throws(() => stageRelease(f.options), /private regular file/);
});

test('junction in release root rejects writes before escaping workspace', (t) => {
  const f = fixture(t);
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-publisher-outside-'));
  t.after(() => fs.rmSync(outside, { recursive: true, force: true }));
  const releaseRoot = path.join(f.workspaceRoot, 'team/ptc/releases');
  fs.symlinkSync(outside, releaseRoot, process.platform === 'win32' ? 'junction' : 'dir');
  assert.throws(() => stageRelease(f.options), /symbolic link/);
  assert.deepEqual(fs.readdirSync(outside), []);
});

test('existing publisher lock fails without deleting someone else lock', (t) => {
  const f = fixture(t);
  const lock = path.join(f.workspaceRoot, 'team/ptc/releases/.publisher-lock');
  fs.mkdirSync(lock, { recursive: true });
  assert.throws(() => stageRelease(f.options), /publisher holds the lock/);
  assert.equal(fs.existsSync(lock), true);
});

test('manifest shape rejects added fields and inconsistent snapshot coverage', (t) => {
  const f = fixture(t);
  assert.throws(() => stageRelease({ ...f.options, releaseId: 'active-release.json' }), /invalid identity/);
  const { manifest } = stageRelease(f.options);
  assert.throws(() => validateReleaseManifest({ ...manifest, untrusted: true }), /manifest v1 shape/);
  const malformed = structuredClone(manifest);
  malformed.snapshots.profiles = ['profiles/missing.md'];
  assert.throws(() => validateReleaseManifest(malformed), /coverage mismatch/);
});

test('atomic pointer failure leaves the old pointer and a complete inactive snapshot', (t) => {
  const f = fixture(t);
  const first = stageRelease(f.options);
  activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: first.stagingId });
  const before = f.pointer();
  const second = stageRelease({ ...f.options, releaseId: 'ptc-release-v2' });
  const rename = fs.renameSync;
  t.mock.method(fs, 'renameSync', (source, destination) => {
    if (destination.endsWith('active-release.json')) throw new Error('injected pointer replacement failure');
    return rename(source, destination);
  });
  assert.throws(() => activateStagedRelease({ workspaceRoot: f.workspaceRoot, stagingId: second.stagingId }), /injected pointer/);
  assert.equal(f.pointer(), before);
  const secondDirectory = path.join(f.workspaceRoot, 'team/ptc/releases/ptc-release-v2');
  assert.equal(verifyReleaseDirectory(secondDirectory, second.manifest).ok, true);
  assert.equal(fs.readdirSync(path.dirname(secondDirectory)).some((name) => name.startsWith('.pointer-')), false);
});
