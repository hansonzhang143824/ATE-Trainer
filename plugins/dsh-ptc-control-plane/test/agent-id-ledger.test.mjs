import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';
import { resolveBundle, verifyBundle, freezeTarget } from '../lib/trainer-bundle.js';
import { stageRelease } from '../lib/trainer-release.js';
import { AGENT_ID_LEDGER_PATH, applyChanges, ensureTrainerProject, parseAgentIdLedger, readAssets, readProject } from '../lib/trainer-project.js';

const ledger = (allocated) => JSON.stringify({ schemaVersion: 1, allocated }, null, 2) + '\n';
const contract = (id, direction) => `contracts/${id}-${direction}.schema.json`;
function agentFiles(id) {
  const input = contract(id, 'input'); const output = contract(id, 'output');
  const schema = JSON.stringify({ $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object', additionalProperties: true }, null, 2) + '\n';
  return [
    { path: `agents/${id}/instructions.md`, content: `Return ${id}.\n` },
    { path: `agents/${id}/agent.json`, content: JSON.stringify({ agentId: id, name: id, instructionsRef: `agents/${id}/instructions.md`, skillRefs: [], toolIds: [], inputSchemaRef: input, outputSchemaRef: output }, null, 2) + '\n' },
    { path: input, content: schema }, { path: output, content: schema },
  ];
}
function setup(t, { initialFiles = null, initialLedger = null } = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-agent-id-ledger-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const files = initialFiles ?? createSyntheticTrainerFixture().files;
  if (initialLedger !== null) files[AGENT_ID_LEDGER_PATH] = initialLedger;
  const projectId = 'ledger-test';
  const project = ensureTrainerProject(root, { projectId, seed: { files } });
  return { root, projectId, project };
}
function commit(root, projectId, reason, changes, requestId = `request-${Math.random().toString(16).slice(2)}`) {
  const baseRevision = readProject(root, { projectId }).revisionId;
  return applyChanges(root, { projectId, requestId, baseRevision, reason, changes });
}
function expectCode(fn, code) { assert.throws(fn, (error) => error.code === code, `expected ${code}`); }

test('base without a ledger only permits standalone ledger initialization', (t) => {
  const one = setup(t); const id = 'agent-new-one';
  const result = commit(one.root, one.projectId, 'initialize Agent ID ledger', [{ path: AGENT_ID_LEDGER_PATH, content: ledger(['lab-producer', 'lab-consumer']) }]);
  assert.notEqual(result.revisionId, one.project.revisionId);

  const two = setup(t); const base = readProject(two.root, { projectId: two.projectId }).revisionId;
  expectCode(() => applyChanges(two.root, { projectId: two.projectId, requestId: 'init-with-agent', baseRevision: base, reason: 'invalid combined initialization', changes: [{ path: AGENT_ID_LEDGER_PATH, content: ledger(['lab-producer', 'lab-consumer', id]) }, ...agentFiles(id)] }), 'TRAINER_AGENT_ID_LEDGER_MISSING');
  assert.equal(readProject(two.root, { projectId: two.projectId }).revisionId, base);

  const three = setup(t); const baseThree = three.project.revisionId;
  expectCode(() => applyChanges(three.root, { projectId: three.projectId, requestId: 'agent-before-init', baseRevision: baseThree, reason: 'invalid Agent creation before initialization', changes: agentFiles(id) }), 'TRAINER_AGENT_ID_LEDGER_MISSING');
  assert.equal(readProject(three.root, { projectId: three.projectId }).revisionId, baseThree);

  const four = setup(t); const baseFour = four.project.revisionId;
  expectCode(() => applyChanges(four.root, { projectId: four.projectId, requestId: 'edit-before-init', baseRevision: baseFour, reason: 'invalid edit before initialization', changes: [{ path: 'agents/lab-producer/instructions.md', content: 'changed\n' }] }), 'TRAINER_AGENT_ID_LEDGER_MISSING');
  assert.equal(readProject(four.root, { projectId: four.projectId }).revisionId, baseFour);
});

test('valid ledger allows registered creation and rejects reuse, missing registration, and shrink', (t) => {
  const f = setup(t); const ids = ['lab-producer', 'lab-consumer', 'agent-retired'];
  commit(f.root, f.projectId, 'initialize Agent ID ledger', [{ path: AGENT_ID_LEDGER_PATH, content: ledger(ids) }]);
  const fresh = 'agent-fresh-one';
  const created = commit(f.root, f.projectId, 'create registered Agent', [...agentFiles(fresh), { path: AGENT_ID_LEDGER_PATH, content: ledger([...ids, fresh]) }]);
  assert.equal(created.diff.filter((entry) => entry.path.startsWith(`agents/${fresh}/`) || entry.path.startsWith(`contracts/${fresh}-`)).length, 4);

  const base = readProject(f.root, { projectId: f.projectId }).revisionId;
  expectCode(() => applyChanges(f.root, { projectId: f.projectId, requestId: 'reuse', baseRevision: base, reason: 'reuse allocated ID', changes: agentFiles('agent-retired') }), 'TRAINER_AGENT_ID_REUSED');
  expectCode(() => applyChanges(f.root, { projectId: f.projectId, requestId: 'unregistered', baseRevision: base, reason: 'omit new ID from ledger', changes: agentFiles('agent-unregistered') }), 'TRAINER_AGENT_ID_UNREGISTERED');
  expectCode(() => applyChanges(f.root, { projectId: f.projectId, requestId: 'shrink', baseRevision: base, reason: 'shrink ledger', changes: [{ path: AGENT_ID_LEDGER_PATH, content: ledger(ids) }] }), 'TRAINER_AGENT_ID_LEDGER_SHRINK');
  assert.equal(readProject(f.root, { projectId: f.projectId }).revisionId, base);
});

test('every newly created Agent is checked in one change set and deletion preserves allocated IDs', (t) => {
  const f = setup(t); const ids = ['lab-producer', 'lab-consumer'];
  commit(f.root, f.projectId, 'initialize Agent ID ledger', [{ path: AGENT_ID_LEDGER_PATH, content: ledger(ids) }]);
  const a = 'agent-batch-a'; const b = 'agent-batch-b'; const base = readProject(f.root, { projectId: f.projectId }).revisionId;
  expectCode(() => applyChanges(f.root, { projectId: f.projectId, requestId: 'batch-one-missing', baseRevision: base, reason: 'register only one batch Agent', changes: [...agentFiles(a), ...agentFiles(b), { path: AGENT_ID_LEDGER_PATH, content: ledger([...ids, a]) }] }), 'TRAINER_AGENT_ID_UNREGISTERED');
  const ok = applyChanges(f.root, { projectId: f.projectId, requestId: 'batch-both', baseRevision: base, reason: 'register both batch Agents', changes: [...agentFiles(a), ...agentFiles(b), { path: AGENT_ID_LEDGER_PATH, content: ledger([...ids, a, b]) }] });
  assert.equal(ok.diff.filter((entry) => entry.path.startsWith(`agents/${a}/`) || entry.path.startsWith(`agents/${b}/`)).length, 4);
  const after = readProject(f.root, { projectId: f.projectId }).revisionId;
  const deleted = commit(f.root, f.projectId, 'delete A and create C', [
    ...agentFiles('agent-batch-c'),
    ...agentFiles(a).map(({ path }) => ({ path, content: null })),
    { path: AGENT_ID_LEDGER_PATH, content: ledger([...ids, a, b, 'agent-batch-c']) },
  ]);
  assert.notEqual(deleted.revisionId, after);
  assert.deepEqual(parseAgentIdLedger(readAssets(f.root, { projectId: f.projectId }).files[AGENT_ID_LEDGER_PATH]).allocated, [...ids, a, b, 'agent-batch-c']);
});

test('damaged ledger has a standalone repair channel only', (t) => {
  const malformed = JSON.stringify({ schemaVersion: 2, allocated: ['lab-producer'] });
  const f = setup(t, { initialLedger: malformed });
  const base = f.project.revisionId;
  expectCode(() => applyChanges(f.root, { projectId: f.projectId, requestId: 'bad-edit', baseRevision: base, reason: 'edit while ledger damaged', changes: [{ path: 'agents/lab-producer/instructions.md', content: 'changed\n' }] }), 'TRAINER_AGENT_ID_LEDGER_INVALID');
  const repaired = applyChanges(f.root, { projectId: f.projectId, requestId: 'repair-ledger', baseRevision: base, reason: 'repair Agent ID ledger', changes: [{ path: AGENT_ID_LEDGER_PATH, content: ledger(['lab-producer', 'lab-consumer']) }] });
  assert.notEqual(repaired.revisionId, base);
  assert.equal(parseAgentIdLedger(readAssets(f.root, { projectId: f.projectId }).files[AGENT_ID_LEDGER_PATH]).schemaVersion, 1);
});

test('ledger corruption forms are rejected and freeze/verify/stage release still regress', (t) => {
  for (const [name, content] of [
    ['schema', JSON.stringify({ schemaVersion: 2, allocated: ['lab-producer'] })],
    ['array', JSON.stringify({ schemaVersion: 1, allocated: 'lab-producer' })],
    ['id', JSON.stringify({ schemaVersion: 1, allocated: ['bad/id'] })],
    ['duplicate', ledger(['lab-producer', 'lab-producer'])],
    ['json', '{'],
  ]) {
    const f = setup(t); const base = f.project.revisionId;
    expectCode(() => applyChanges(f.root, { projectId: f.projectId, requestId: `bad-${name}`, baseRevision: base, reason: `bad ledger ${name}`, changes: [{ path: AGENT_ID_LEDGER_PATH, content }] }), 'TRAINER_AGENT_ID_LEDGER_INVALID');
  }
  const f = setup(t); const ids = ['lab-producer', 'lab-consumer'];
  commit(f.root, f.projectId, 'initialize Agent ID ledger', [{ path: AGENT_ID_LEDGER_PATH, content: ledger(ids) }]);
  const bundle = resolveBundle(f.root, { projectId: f.projectId, targetKind: 'workflow', targetId: 'lab-pair', model: { provider: 'test', model: 'test' } });
  assert.equal(verifyBundle(bundle).ok, true);
  const frozen = freezeTarget(f.root, { projectId: f.projectId, targetKind: 'workflow', targetId: 'lab-pair', bundle });
  const evidence = { runId: 'ledger-regression-run', projectId: f.projectId, targetKind: 'workflow', targetId: 'lab-pair', bundleSha256: bundle.bundleSha256, workflowRevision: bundle.workflowRevision, status: 'completed', validation: { ok: true }, businessGatePassed: false, steps: bundle.steps.map((step) => ({ stepId: step.stepId, agentId: step.agentId, agentRevision: step.agentRevision, status: 'completed' })) };
  const release = stageRelease(f.root, { projectId: f.projectId, frozenVersionId: frozen.frozenVersionId, runEvidence: evidence });
  assert.equal(release.businessGatePassed, false);
});
