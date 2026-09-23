import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { createRunContext, persistRunContext, runWriteDecision } from '../lib/run-context.js';
import { createTrainingRun } from '../lib/training-run.js';
import {
  buildReleaseFileEntries,
  digestReleaseEntries,
  verifyReleaseDirectory,
} from '../lib/release-integrity.js';

/*
 * Run-boundary failure matrix (release mode vs training mode).
 * Zero external dependencies: node:test + node:assert + node:fs only.
 * All fixtures live in per-test temp directories removed in the after() hook.
 */

const roots = [];
after(() => {
  for (const root of roots) fs.rmSync(root, { recursive: true, force: true });
});

function temp(prefix) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), `ptc-boundary-${prefix}-`));
  roots.push(root);
  return root;
}

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

const CREATED_AT = '2026-09-22T00:00:00.000Z';

function trainingContext(root, runId = 'training-matrix-001') {
  return createRunContext(root, { mode: 'training', runId, createdAt: CREATED_AT });
}

function deliveryContext(root, runId = 'dali-matrix-001') {
  return createRunContext(root, {
    mode: 'delivery',
    runId,
    releaseId: 'rel-2026-001',
    projectId: 'DALI',
    createdAt: CREATED_AT,
  });
}

/* ------------------------------------------------------------------ */
/* 1. Identity roots: where each mode is allowed to live             */
/* ------------------------------------------------------------------ */

test('matrix: training run is pinned to Training_Materials/runs/<runId>', () => {
  const root = temp('identity');
  const context = trainingContext(root, 'training-fixed-001');
  assert.equal(context.mode, 'training');
  assert.equal(context.artifactRoot, path.join('Training_Materials', 'runs', 'training-fixed-001'));
  assert.equal(context.profileSource, 'draft');
  assert.equal(context.orchestrationSource, 'draft');
  assert.equal(context.releaseId, null);
  assert.equal(context.projectId, null);
  assert.equal(Object.isFrozen(context), true);

  fs.mkdirSync(path.join(root, 'team', 'expert-profiles', 'ptc-dft-expert'), { recursive: true });
  const result = createTrainingRun(root, {
    runId: 'training-fixed-002',
    target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  }, { now: new Date(CREATED_AT) });
  assert.equal(result.runFile, path.join(root, 'Training_Materials', 'runs', 'training-fixed-002', 'run.json'));
  assert.equal(result.stateFile, path.join(root, 'Training_Materials', 'runs', 'training-fixed-002', 'state.json'));
  assert.equal(JSON.parse(fs.readFileSync(result.runFile, 'utf8')).mode, 'training');
  const runRoot = path.join(root, 'Training_Materials', 'runs');
  // createRunContext only builds the frozen identity; only createTrainingRun persists.
  assert.deepEqual(fs.readdirSync(runRoot), ['training-fixed-002']);
});

test('matrix: delivery run is pinned to team/artifacts/<runId> and pins release/project', () => {
  const root = temp('identity');
  const context = deliveryContext(root, 'dali-fixed-001');
  assert.equal(context.mode, 'delivery');
  assert.equal(context.artifactRoot, path.join('team', 'artifacts', 'dali-fixed-001'));
  assert.equal(context.releaseId, 'rel-2026-001');
  assert.equal(context.projectId, 'DALI');
  assert.equal(context.profileSource, 'team/ptc/releases/rel-2026-001/profiles');
  assert.equal(context.orchestrationSource, 'team/ptc/releases/rel-2026-001/orchestration');
  assert.equal(Object.isFrozen(context), true);
  assert.throws(() => { context.releaseId = 'rel-2026-002'; }, TypeError);
});

/* ------------------------------------------------------------------ */
/* 2. Mode confusion and invalid identity rejection                   */
/* ------------------------------------------------------------------ */

test('matrix: mode confusion is rejected', () => {
  const root = temp('mode-confusion');
  const rejected = [
    { input: { mode: 'Training', runId: 'x' }, pattern: /mode must be training or delivery/ },
    { input: { runId: 'x' }, pattern: /mode must be training or delivery/ },
    { input: { mode: 'production', runId: 'x' }, pattern: /mode must be training or delivery/ },
    { input: { mode: 'training', runId: 'x', releaseId: 'rel-1' }, pattern: /cannot bind releaseId/ },
    { input: { mode: 'training', runId: 'x', releaseId: null, projectId: 'DALI' }, pattern: /cannot bind projectId/ },
    { input: { mode: 'delivery', runId: 'x', projectId: 'DALI' }, pattern: /releaseId/ },
    { input: { mode: 'delivery', runId: 'x', releaseId: 'rel-1' }, pattern: /projectId/ },
    { input: { mode: 'delivery', runId: 'x', releaseId: '../other', projectId: 'DALI' }, pattern: /releaseId/ },
    { input: { mode: 'delivery', runId: 'x', releaseId: 'rel-1', projectId: '../other' }, pattern: /projectId/ },
  ];
  for (const { input, pattern } of rejected) {
    assert.throws(() => createRunContext(root, input), pattern, JSON.stringify(input));
  }
});

test('matrix: illegal runId shapes and path escapes are rejected', () => {
  const root = temp('runid');
  const invalid = ['../escape', 'foo/bar', '.hidden', '-lead', 'has space', '', 'a'.repeat(129), 'tab\tchar'];
  for (const runId of invalid) {
    assert.throws(() => createRunContext(root, { mode: 'training', runId }), /runId/, `runId=${JSON.stringify(runId)}`);
  }
  assert.equal(trainingContext(root, 'a').runId, 'a');
  assert.equal(trainingContext(root, 'A1._-z9').runId, 'A1._-z9');

  const context = trainingContext(root, 'training-escape-001');
  const escapes = [
    '..\\escape.txt',
    path.join('..', 'sibling', 'x.json'),
    path.resolve(os.tmpdir(), 'boundary-outside.json'),
  ];
  for (const candidate of escapes) {
    const decision = runWriteDecision(root, context, candidate);
    assert.equal(decision.allowed, false, `candidate=${candidate}`);
    assert.match(decision.reason, /escapes the workspace/);
  }
});

/* ------------------------------------------------------------------ */
/* 3. Immutable run.json                                              */
/* ------------------------------------------------------------------ */

test('matrix: existing immutable run.json cannot be replaced', () => {
  const root = temp('immutable');
  const context = trainingContext(root, 'training-immutable-001');
  const file = persistRunContext(root, context);
  assert.equal(path.basename(file), 'run.json');
  const wanted = `${JSON.stringify(context, null, 2)}\n`;
  assert.equal(fs.readFileSync(file, 'utf8'), wanted);

  assert.equal(persistRunContext(root, context), file, 'identical persistence is idempotent');

  fs.writeFileSync(file, '{"mode":"delivery"}\n', 'utf8');
  assert.throws(() => persistRunContext(root, context), /different content/);

  fs.writeFileSync(file, wanted, 'utf8'); // restore
  const drift = createRunContext(root, {
    mode: 'training', runId: 'training-immutable-001', createdAt: '2026-09-23T00:00:00.000Z',
  });
  assert.throws(() => persistRunContext(root, drift), /different content/);

  const modeSwap = createRunContext(root, {
    mode: 'delivery', runId: 'training-immutable-001', releaseId: 'rel-2026-001', projectId: 'DALI',
    createdAt: CREATED_AT,
  });
  // Characterization of a real gap: the runId namespace is split per mode, so the
  // same runId can hold a training identity AND a delivery identity at once
  // (different roots). persistRunContext cannot detect this collision.
  const swappedFile = persistRunContext(root, modeSwap);
  assert.equal(swappedFile, path.join(root, 'team', 'artifacts', 'training-immutable-001', 'run.json'));
  assert.equal(fs.readFileSync(file, 'utf8'), wanted, 'original training run.json is untouched');
  assert.equal(fs.readFileSync(file, 'utf8'), wanted, 'original run.json is untouched after failed persists');
});

/* ------------------------------------------------------------------ */
/* 4. Cross-mode write authority matrix                               */
/* ------------------------------------------------------------------ */

test('matrix: training and delivery write boundaries never overlap', () => {
  const root = temp('write-matrix');
  const training = trainingContext(root, 'training-cross-001');
  const delivery = deliveryContext(root, 'dali-cross-001');

  const matrix = [
    // [candidate, allowedForTraining, allowedForDelivery, denialPattern]
    ['Training_Materials/runs/training-cross-001/dft/out.json', true, false, /training boundary|delivery boundary/],
    ['Training_Materials/runs/training-cross-002/out.json', false, false, /boundary/],
    ['team/artifacts/dali-cross-001/method/contract.json', false, true, /training boundary|delivery boundary/],
    ['team/artifacts/other-run/state.json', false, false, /boundary/],
    ['project/DALI/Output_Global_Material/dft/TM109/dft-meta.json', false, true, /training boundary|delivery boundary/],
    ['project/OTHER/Output/x.json', false, false, /boundary/],
    ['team/ptc/releases/rel-2026-001/profiles/dft/instructions.md', false, false, /release snapshots are immutable/],
    ['team/ptc/releases/rel-2026-001/orchestration/stages.json', false, false, /release snapshots are immutable/],
    ['team/expert-profiles/ptc-dft-expert/instructions.md', false, false, /boundary/],
    ['team/expert-profiles/ptc-dft-expert/versions/v7/instructions.md', false, false, /boundary/],
  ];
  for (const [candidate, trainingAllowed, deliveryAllowed, pattern] of matrix) {
    const trainingDecision = runWriteDecision(root, training, candidate);
    assert.equal(trainingDecision.allowed, trainingAllowed, `training candidate=${candidate} => ${trainingDecision.reason}`);
    const deliveryDecision = runWriteDecision(root, delivery, candidate);
    assert.equal(deliveryDecision.allowed, deliveryAllowed, `delivery candidate=${candidate} => ${deliveryDecision.reason}`);
    if (!trainingAllowed) assert.match(trainingDecision.reason, pattern, `training candidate=${candidate}`);
    if (!deliveryAllowed) assert.match(deliveryDecision.reason, pattern, `delivery candidate=${candidate}`);
  }
});

/* ------------------------------------------------------------------ */
/* 5. Release integrity failure matrix                                */
/* ------------------------------------------------------------------ */

function releaseFixture() {
  const root = temp('release');
  fs.mkdirSync(path.join(root, 'profiles', 'dft'), { recursive: true });
  fs.mkdirSync(path.join(root, 'orchestration'), { recursive: true });
  fs.writeFileSync(path.join(root, 'profiles', 'dft', 'instructions.md'), 'DFT\r\n', 'utf8');
  fs.writeFileSync(path.join(root, 'orchestration', 'stages.json'), '{"stages":["INPUT_SYNC"]}\n', 'utf8');
  const files = buildReleaseFileEntries(root);
  return { root, manifest: { files, bundleDigest: digestReleaseEntries(files) } };
}

test('matrix: intact release directory verifies cleanly', () => {
  const { root, manifest } = releaseFixture();
  const result = verifyReleaseDirectory(root, manifest);
  assert.deepEqual(result, {
    ok: true,
    errors: [],
    actualDigest: manifest.bundleDigest,
    actualFiles: manifest.files,
  });
});

test('matrix: any changed byte in the release directory fails closed', () => {
  const { root, manifest } = releaseFixture();
  // append one byte -> size and sha drift
  fs.appendFileSync(path.join(root, 'profiles', 'dft', 'instructions.md'), 'x', 'utf8');
  const appended = verifyReleaseDirectory(root, manifest);
  assert.equal(appended.ok, false);
  assert.equal(appended.errors.includes('size mismatch: profiles/dft/instructions.md'), true);
  assert.equal(appended.errors.includes('sha256 mismatch: profiles/dft/instructions.md'), true);
  assert.equal(appended.errors.includes('bundleDigest mismatch'), true);
});

test('matrix: same-size byte substitution still fails on the digest', () => {
  const { root, manifest } = releaseFixture();
  const file = path.join(root, 'profiles', 'dft', 'instructions.md');
  const bytes = fs.readFileSync(file);
  bytes[0] = bytes[0] === 0x58 ? 0x59 : 0x58; // same length, different byte
  fs.writeFileSync(file, bytes);
  const result = verifyReleaseDirectory(root, manifest);
  assert.equal(result.ok, false);
  assert.equal(result.errors.includes('sha256 mismatch: profiles/dft/instructions.md'), true);
  assert.equal(result.errors.includes('bundleDigest mismatch'), true);
});

test('matrix: extra or missing files in the release directory fail closed', () => {
  const { root, manifest } = releaseFixture();
  fs.writeFileSync(path.join(root, 'unexpected.txt'), 'extra', 'utf8');
  assert.equal(verifyReleaseDirectory(root, manifest).ok, false);

  const clean = releaseFixture();
  fs.rmSync(path.join(clean.root, 'orchestration', 'stages.json'));
  const removed = verifyReleaseDirectory(clean.root, clean.manifest);
  assert.equal(removed.ok, false);
  assert.equal(removed.errors.some((error) => error.includes('file list mismatch')), true);
});

test('matrix: noncanonical or corrupt manifests fail closed before any write', () => {
  const { root, manifest } = releaseFixture();
  assert.throws(() => verifyReleaseDirectory(root, {
    files: manifest.files.slice().reverse(), bundleDigest: manifest.bundleDigest,
  }), /unique and sorted/);
  assert.throws(() => verifyReleaseDirectory(root, {
    files: [...manifest.files, { ...manifest.files[0] }], bundleDigest: manifest.bundleDigest,
  }), /unique and sorted/);
  assert.throws(() => verifyReleaseDirectory(root, {
    files: [...manifest.files, { path: 'profiles\\backslash.md', size: 1, sha256: manifest.files[0].sha256 }],
    bundleDigest: manifest.bundleDigest,
  }), /invalid file path/);
  assert.throws(() => verifyReleaseDirectory(root, {
    files: [{ path: 'a.md', size: -1, sha256: manifest.files[0].sha256 }], bundleDigest: manifest.bundleDigest,
  }), /invalid size/);
  assert.throws(() => verifyReleaseDirectory(root, { files: 'nope', bundleDigest: manifest.bundleDigest }), /must be an array/);
  assert.throws(() => verifyReleaseDirectory(root, {
    files: [{ path: 'a.md', size: 1, sha256: manifest.bundleDigest.toUpperCase() }],
    bundleDigest: manifest.bundleDigest,
  }), /invalid sha256/);
});

test('matrix: wrong or malformed bundleDigest fails closed', () => {
  const { root, manifest } = releaseFixture();
  const wrongValue = verifyReleaseDirectory(root, {
    files: manifest.files,
    bundleDigest: '0'.repeat(64), // well-formed, wrong value
  });
  assert.equal(wrongValue.ok, false);
  assert.equal(wrongValue.errors.includes('bundleDigest mismatch'), true);

  const malformed = verifyReleaseDirectory(root, {
    files: manifest.files,
    bundleDigest: manifest.bundleDigest.toUpperCase(), // not lowercase
  });
  assert.equal(malformed.ok, false);
  assert.equal(malformed.errors.includes('bundleDigest is not lowercase SHA-256'), true);
});

test('matrix: symbolic link inside a release directory fails closed', (t) => {
  const { root, manifest } = releaseFixture();
  fs.writeFileSync(path.join(root, 'anchor.txt'), 'anchor', 'utf8');
  let linked = true;
  try {
    fs.symlinkSync(path.join(root, 'anchor.txt'), path.join(root, 'profiles', 'dft', 'link.md'));
  } catch (error) {
    linked = false;
    t.diagnostic(`symlink creation unavailable here (${error?.code ?? error?.message}); walker guard not exercised end-to-end`);
  }
  if (linked) {
    assert.throws(() => buildReleaseFileEntries(root), /symbolic links/);
    assert.throws(() => verifyReleaseDirectory(root, manifest), /symbolic links/);
  }
});

/* ------------------------------------------------------------------ */
/* 6. Documented defect: walk order vs validation order divergence    */
/* ------------------------------------------------------------------ */

test('matrix: producer and verifier share codepoint ordering for mixed-case release names', () => {
  const root = temp('collation');
  fs.mkdirSync(root, { recursive: true });
  fs.writeFileSync(path.join(root, 'B.txt'), 'upper', 'utf8');
  fs.writeFileSync(path.join(root, 'a.txt'), 'lower', 'utf8');
  const files = buildReleaseFileEntries(root);
  assert.deepEqual(files.map((entry) => entry.path), ['B.txt', 'a.txt']);
  const manifest = { files, bundleDigest: digestReleaseEntries(files) };
  assert.equal(verifyReleaseDirectory(root, manifest).ok, true);
});
