import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import crypto from 'node:crypto';
import { signTrainingReceipt, trainingDispatchLabel, trainingGuardDecision, verifyTrainingReceipt } from '../lib/training-guard.js';
import { trainingAddressBook, trainingDftCommands } from '../lib/training-paths.js';
import { TRAINING_POLICY_FILES } from '../lib/training-materials.js';

const address = trainingAddressBook('training-guard');
function workspace(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-guard-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  for (const dir of [address.inputRoot, `${address.dftRoot}/TM109`, `${address.dftRoot}/TM110`, address.verificationRoot]) fs.mkdirSync(path.join(root, dir), { recursive: true });
  fs.writeFileSync(path.join(root, address.workbook), 'fixture');
  fs.writeFileSync(path.join(root, address.rules), 'rules');
  fs.mkdirSync(path.join(root, address.profileRoot), { recursive: true });
  fs.writeFileSync(path.join(root, address.instructions), 'instructions');
  fs.mkdirSync(path.join(root, 'scripts'));
  const hash = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
  const policies = TRAINING_POLICY_FILES.map((file) => {
    fs.writeFileSync(path.join(root, file), `# policy ${file}\n`);
    const sha256 = hash(fs.readFileSync(path.join(root, file)));
    return { path: file, sha256, diskSha256: sha256 };
  });
  const files = [
    { source: 'Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx', path: address.workbook, sha256: hash('fixture'), view: 'python-plaintext' },
    { source: 'team/expert-profiles/ptc-dft-expert/instructions.md', path: address.instructions, sha256: hash('instructions'), view: 'exact-bytes' },
  ];
  const cacheKey = hash(JSON.stringify({ materials: files.map(({ source, sha256 }) => ({ source, sha256 })), policies: policies.map(({ path, sha256 }) => ({ path, sha256 })) }));
  fs.writeFileSync(path.join(root, address.runRoot, 'material-manifest.json'), JSON.stringify({ schemaVersion: 2, runId: 'training-guard', testItems: ['TM109'], files, policies, cacheKey }));
  return root;
}

function setup(root, childSessionId = 'session-training-child') {
  const label = trainingDispatchLabel('training-guard', ['TM109']);
  const receipt = signTrainingReceipt({
    schemaVersion: 1, kind: 'ptc-training-dispatch', runId: 'training-guard',
    profileId: 'ptc-dft-expert', profileSource: 'draft', testItems: ['TM109'],
    label, parentSessionId: 'parent', childSessionId, addressBook: address,
    materialCacheKey: JSON.parse(fs.readFileSync(path.join(root, address.runRoot, 'material-manifest.json'), 'utf8')).cacheKey,
    createdAt: '2026-09-22T00:00:00.000Z',
  });
  fs.writeFileSync(path.join(root, address.runRoot, 'dispatch.json'), `${JSON.stringify(receipt)}\n`);
  const agent = { id: childSessionId, session: { header: { cwd: root }, events: [{ type: 'subagent/descriptor', data: { label } }] } };
  return { receipt, agent };
}

function decide(root, agent, name, arguments_) { return trainingGuardDecision({ name, arguments: arguments_, agent }, root); }

test('training receipt binds one child to private run inputs and assigned products', (t) => {
  const root = workspace(t);
  const { receipt, agent } = setup(root);
  assert.equal(verifyTrainingReceipt(receipt), true);
  assert.equal(verifyTrainingReceipt({ ...receipt, testItems: ['TM110'] }), false);
  assert.equal(decide(root, agent, 'read', { file_path: address.workbook }), undefined);
  assert.equal(decide(root, agent, 'read', { file_path: address.rules }), undefined);
  assert.equal(decide(root, agent, 'write', { file_path: `${address.dftRoot}/TM109/dft-meta.json` }), undefined);
  for (const file of ['project/DALI/Output_Global_Material/dft/TM109/dft-meta.json', 'Training_Materials/Output_Global_Material/dft/TM109/dft-meta.json', `${address.dftRoot}/TM110/dft-meta.json`, address.workbook, address.instructions, 'Training_Materials/runs/other/input-sync/dft/TM109/dft-meta.json']) {
    assert.match(decide(root, agent, 'write', { file_path: file }), /training execution boundary/);
  }
});

test('verification writes require assigned TM names and reject cross-TM filenames', (t) => {
  const root = workspace(t);
  const { agent } = setup(root);
  assert.equal(decide(root, agent, 'write', { file_path: `${address.verificationRoot}/dft-schema-TM109.json` }), undefined);
  for (const name of ['schema-TM109.json', 'dft-schema.json', 'dft-schema-TM110.json', 'dft-TM109-TM110.json', 'dft-TM109-tm110.json']) {
    assert.match(decide(root, agent, 'write', { file_path: `${address.verificationRoot}/${name}` }), /training execution boundary/);
  }
});

test('training child runs exact scoped commands without shell overrides', (t) => {
  const root = workspace(t);
  const { agent } = setup(root);
  const commands = trainingDftCommands(address, 'TM109', 'a'.repeat(64));
  for (const command of Object.values(commands)) assert.equal(decide(root, agent, 'pwsh', { command }), undefined);
  for (const arguments_ of [{ command: commands.validate.replace('TM109', 'TM110') }, { command: `${commands.validate}; whoami` }, { command: commands.validate, workdir: root }, { command: commands.validate, run_in_background: true }, { command: commands.validate, sandbox_permissions: 'require_escalated' }]) {
    assert.match(decide(root, agent, 'pwsh', arguments_), /training execution boundary/);
  }
  assert.match(decide(root, agent, 'glob', { pattern: '**/*' }), /training execution boundary/);
});

test('unbound child and same-label wrong-id fail closed, unrelated sessions pass through', (t) => {
  const root = workspace(t);
  const { agent } = setup(root, null);
  agent.id = 'session-early-child';
  assert.match(decide(root, agent, 'run_code', {}), /not yet bound/);
  setup(root);
  agent.id = 'session-impostor';
  assert.match(decide(root, agent, 'read', { file_path: address.workbook }), /names a different child/);
  const unrelated = { id: 'x', session: { header: { cwd: root }, events: [] } };
  assert.equal(decide(root, unrelated, 'write', { file_path: 'anywhere' }), undefined);
});

test('closed, misplaced, duplicated and malformed receipts fail closed', (t) => {
  const root = workspace(t);
  const { receipt, agent } = setup(root);
  const file = path.join(root, address.runRoot, 'dispatch.json');
  fs.writeFileSync(file, JSON.stringify(signTrainingReceipt({ ...receipt, executionStatus: 'closed' })));
  assert.match(decide(root, agent, 'write', { file_path: `${address.dftRoot}/TM109/dft-meta.json` }), /ended/);
  fs.writeFileSync(file, JSON.stringify(receipt));
  fs.mkdirSync(path.join(root, 'Training_Materials/runs/other'));
  fs.copyFileSync(file, path.join(root, 'Training_Materials/runs/other/dispatch.json'));
  assert.match(decide(root, agent, 'run_code', {}), /ambiguous/);
  fs.unlinkSync(file);
  assert.match(decide(root, agent, 'run_code', {}), /invalid/);
  assert.equal(verifyTrainingReceipt(signTrainingReceipt({ ...receipt, label: 'wrong label' })), false);
});

test('workspace ancestor junction and redirected output junction are rejected', (t) => {
  const root = workspace(t);
  const { agent } = setup(root);
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-guard-outside-'));
  t.after(() => fs.rmSync(outside, { recursive: true, force: true }));
  const alias = path.join(outside, 'workspace-alias');
  fs.symlinkSync(root, alias, process.platform === 'win32' ? 'junction' : 'dir');
  assert.match(decide(alias, agent, 'write', { file_path: `${address.dftRoot}/TM109/dft-meta.json` }), /training execution identity|training execution boundary/);
  const tmRoot = path.join(root, address.dftRoot, 'TM109');
  fs.rmdirSync(tmRoot);
  fs.symlinkSync(outside, tmRoot, process.platform === 'win32' ? 'junction' : 'dir');
  assert.match(decide(root, agent, 'write', { file_path: `${address.dftRoot}/TM109/dft-meta.json` }), /training execution boundary/);
  assert.match(decide(root, agent, 'pwsh', { command: trainingDftCommands(address, 'TM109', 'a'.repeat(64)).validate }), /training execution boundary/);
});

test('hard-linked products cannot mutate an outside file', (t) => {
  const root = workspace(t);
  const { agent } = setup(root);
  const source = path.join(root, 'other.json');
  fs.writeFileSync(source, 'outside');
  fs.linkSync(source, path.join(root, address.dftRoot, 'TM109/dft-meta.json'));
  assert.match(decide(root, agent, 'write', { file_path: `${address.dftRoot}/TM109/dft-meta.json` }), /training execution boundary/);
});

test('changed live policy is denied even for an otherwise valid receipt', (t) => {
  const root = workspace(t);
  const { agent } = setup(root);
  fs.appendFileSync(path.join(root, 'scripts/dft_test_condition.py'), '# changed\n');
  assert.match(decide(root, agent, 'pwsh', { command: trainingDftCommands(address, 'TM109', 'a'.repeat(64)).refresh }), /policy changed/);
  assert.match(decide(root, agent, 'write', { file_path: `${address.dftRoot}/TM109/dft-meta.json` }), /policy changed/);
});
