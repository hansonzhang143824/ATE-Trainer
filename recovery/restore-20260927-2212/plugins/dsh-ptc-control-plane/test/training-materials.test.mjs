import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { prepareTrainingMaterials, verifyTrainingMaterials, verifyTrainingPolicySync, TRAINING_POLICY_FILES } from '../lib/training-materials.js';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const products = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-materials-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  for (const dir of ['scripts', 'Training_Materials/Input_GlobalMaterial', 'Training_Materials/Output_Global_Material/dft/TM109', 'team/expert-profiles/ptc-dft-expert']) fs.mkdirSync(path.join(root, dir), { recursive: true });
  for (const file of ['hash_ate_plaintext.py', 'material_plaintext_hash.py']) fs.copyFileSync(path.join(repo, 'scripts', file), path.join(root, 'scripts', file));
  for (const file of TRAINING_POLICY_FILES.slice(2)) fs.writeFileSync(path.join(root, file), `# fixture policy ${file}\n`);
  fs.writeFileSync(path.join(root, 'Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx'), Buffer.from([0, 128, 255, 13, 10]));
  fs.writeFileSync(path.join(root, 'team/expert-profiles/ptc-dft-expert/instructions.md'), 'draft v1');
  for (const name of products) fs.writeFileSync(path.join(root, 'Training_Materials/Output_Global_Material/dft/TM109', name), `original ${name}\r\n`);
  return root;
}

function seal(root, materials) {
  const finalProducts = { TM109: Object.fromEntries(products.map((name) => [name,
    crypto.createHash('sha256').update(fs.readFileSync(path.join(materials.absolute.dftRoot, 'TM109', name))).digest('hex'),
  ])) };
  const evidence = `${materials.runRoot}/evidence/dft-terminal.json`;
  fs.mkdirSync(path.dirname(path.join(root, evidence)), { recursive: true });
  fs.writeFileSync(path.join(root, evidence), JSON.stringify({ runId: materials.runId, cacheKey: materials.cacheKey,
    reports: [{ tm: 'TM109', status: 'ready', exitCode: 0 }], finalProducts }));
  fs.writeFileSync(path.join(root, materials.runRoot, 'state.json'), JSON.stringify({ status: 'completed', finishedAt: '2026-09-22T12:00:00Z', outcome: { evidence } }));
}

test('same-TM runs own distinct snapshots and products; legacy remains unchanged', async (t) => {
  const root = fixture(t);
  const first = await prepareTrainingMaterials(root, 'run-one', ['TM109']);
  const second = await prepareTrainingMaterials(root, 'run-two', ['TM109']);
  assert.notEqual(first.dftRoot, second.dftRoot);
  assert.equal(first.cacheCompatible, false);
  assert.equal(first.candidateSources.TM109.kind, 'legacy');
  assert.match(first.cacheKey, /^[a-f0-9]{64}$/);
  assert.deepEqual(fs.readFileSync(first.absolute.workbook), Buffer.from([0, 128, 255, 13, 10]));
  fs.writeFileSync(path.join(first.absolute.dftRoot, 'TM109/dft-meta.json'), 'changed');
  assert.equal(fs.readFileSync(path.join(second.absolute.dftRoot, 'TM109/dft-meta.json'), 'utf8'), 'original dft-meta.json\r\n');
  assert.equal(fs.readFileSync(path.join(root, 'Training_Materials/Output_Global_Material/dft/TM109/dft-meta.json'), 'utf8'), 'original dft-meta.json\r\n');
  fs.writeFileSync(path.join(root, 'Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx'), 'new source');
  const reentered = await prepareTrainingMaterials(root, 'run-one', ['TM109']);
  assert.equal(reentered.cacheKey, first.cacheKey);
  assert.equal(fs.readFileSync(path.join(first.absolute.dftRoot, 'TM109/dft-meta.json'), 'utf8'), 'changed');
});

test('matching completed run is reused; changing draft invalidates prior cache', async (t) => {
  const root = fixture(t);
  const first = await prepareTrainingMaterials(root, 'run-one', ['TM109']);
  seal(root, first);
  const second = await prepareTrainingMaterials(root, 'run-two', ['TM109']);
  assert.equal(second.cacheCompatible, true);
  assert.equal(second.candidateSources.TM109.runId, 'run-one');
  fs.writeFileSync(path.join(root, 'team/expert-profiles/ptc-dft-expert/instructions.md'), 'draft v2');
  const third = await prepareTrainingMaterials(root, 'run-three', ['TM109']);
  assert.notEqual(third.cacheKey, first.cacheKey);
  assert.equal(third.cacheCompatible, false);
});

test('live policy changes invalidate the run and the next candidate cache', async (t) => {
  const root = fixture(t);
  const first = await prepareTrainingMaterials(root, 'run-one', ['TM109']);
  seal(root, first);
  assert.equal(verifyTrainingPolicySync(root, first.runId, first.cacheKey), true);
  fs.appendFileSync(path.join(root, 'scripts/dft_test_condition.py'), '# changed semantics\n');
  assert.throws(() => verifyTrainingPolicySync(root, first.runId, first.cacheKey), /policy changed/);
  await assert.rejects(verifyTrainingMaterials(root, first), /policy changed/);
  const second = await prepareTrainingMaterials(root, 'run-two', ['TM109']);
  assert.notEqual(second.cacheKey, first.cacheKey);
  assert.equal(second.cacheCompatible, false);
});

test('completed state without sealed evidence or changed review cannot authorize reuse', async (t) => {
  const root = fixture(t);
  const first = await prepareTrainingMaterials(root, 'run-one', ['TM109']);
  fs.writeFileSync(path.join(root, first.runRoot, 'state.json'), JSON.stringify({ status: 'completed' }));
  const second = await prepareTrainingMaterials(root, 'run-two', ['TM109']);
  assert.equal(second.cacheCompatible, false);
  seal(root, first);
  fs.appendFileSync(path.join(first.absolute.dftRoot, 'TM109/dft-semantic-review.json'), '\nchanged review');
  const third = await prepareTrainingMaterials(root, 'run-three', ['TM109']);
  assert.equal(third.cacheCompatible, false);
});

test('immutable snapshot tampering and identity changes fail closed', async (t) => {
  const root = fixture(t);
  const first = await prepareTrainingMaterials(root, 'run-one', ['TM109']);
  await assert.rejects(prepareTrainingMaterials(root, 'run-one', ['TM110']), /identity differs/);
  fs.writeFileSync(first.absolute.instructions, 'tampered');
  await assert.rejects(prepareTrainingMaterials(root, 'run-one', ['TM109']), /snapshot changed/);
});

test('traversal, Windows device names and run-root junctions are rejected', async (t) => {
  const root = fixture(t);
  for (const value of ['../escape', 'CON', 'com1.txt', 'run.', 'run:ads', 'run\\escape']) await assert.rejects(prepareTrainingMaterials(root, value, ['TM109']), /unsafe/);
  await assert.rejects(prepareTrainingMaterials(root, 'valid', ['../TM109']), /invalid testItems/);
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-materials-outside-'));
  t.after(() => fs.rmSync(outside, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, 'Training_Materials/runs'), { recursive: true });
  fs.symlinkSync(outside, path.join(root, 'Training_Materials/runs/linked-run'), process.platform === 'win32' ? 'junction' : 'dir');
  await assert.rejects(prepareTrainingMaterials(root, 'linked-run', ['TM109']), /links are forbidden/);
  assert.deepEqual(fs.readdirSync(outside), []);
  const alias = path.join(outside, 'workspace-alias');
  fs.symlinkSync(root, alias, process.platform === 'win32' ? 'junction' : 'dir');
  await assert.rejects(prepareTrainingMaterials(alias, 'fresh-run', ['TM109']), /links are forbidden/);
});
