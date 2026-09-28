import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { ensureTrainerProject, readProject, readAssets, applyChanges, trainerSha } from '../lib/trainer-project.js';
import { createEightRoleSyntheticFixture, SYNTHETIC_ROLE_CATALOG } from '../lib/trainer-synthetic-fixture.js';
import { resolveBundle, freezeTarget, verifyBundle, bundleManifestBytes, loadFrozenBundle, listFrozenVersions } from '../lib/trainer-bundle.js';
import { validateJson } from '../lib/trainer-schema.js';
import { stageRelease, activateRelease, loadReleaseBundle, listReleases } from '../lib/trainer-release.js';

const projectId = 'synthetic-lab';
const model = { provider: 'synthetic-test', model: 'fake-model' };
function fixture(t, seed) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-frozen-'));
  t.after(() => { assert.equal(path.dirname(root), fs.realpathSync(os.tmpdir())); assert.ok(path.basename(root).startsWith('trainer-frozen-')); fs.rmSync(root, { recursive: true, force: true }); });
  const project = ensureTrainerProject(root, { projectId, seed }); return { root, project };
}
const resolve = (root, targetKind, targetId) => resolveBundle(root, { projectId, targetKind, targetId, model });
const freeze = (root, bundle) => freezeTarget(root, { projectId, targetKind: bundle.targetKind, targetId: bundle.targetId, bundle });
function release(root, bundle) {
  const frozen = freeze(root, bundle);
  const runEvidence = { runId: 'fake-evidence', projectId, targetKind: bundle.targetKind, targetId: bundle.targetId, bundleSha256: bundle.bundleSha256, status: 'completed', validation: { ok: true }, businessGatePassed: false,
    steps: bundle.steps.map((step) => ({ stepId: step.stepId, agentId: step.agentId, status: 'completed' })) };
  const r = stageRelease(root, { projectId, frozenVersionId: frozen.frozenVersionId, runEvidence }); activateRelease(root, { projectId, releaseId: r.releaseId }); return r;
}
test('eight configured synthetic identities resolve and activate independently of the workflow', (t) => {
  const { root, project } = fixture(t, createEightRoleSyntheticFixture());
  assert.equal(project.agents.length, 8);
  const workflow = resolve(root, 'workflow', 'synthetic-eight');
  assert.deepEqual(workflow.steps.map((s) => s.agentId), SYNTHETIC_ROLE_CATALOG.map((a) => a.agentId));
  const workflowRelease = release(root, workflow);
  const releases = new Map();
  for (const { agentId } of project.agents) {
    const bundle = resolve(root, 'agent', agentId); const r = release(root, bundle); releases.set(agentId, r);
    assert.equal(bundle.steps.length, 1);
    assert.ok(bundle.files.every((f) => !f.path.startsWith('agents/') || f.path.startsWith(`agents/${agentId}/`)));
    assert.equal(loadReleaseBundle(root, { projectId, targetKind: 'agent', targetId: agentId }).bundleSha256, r.bundleSha256);
  }
  assert.equal(listReleases(root, { projectId }).active.length, 9);
  const role = project.agents[0].agentId; const file = `agents/${role}/instructions.md`;
  applyChanges(root, { projectId, requestId: 'edit-one-role', baseRevision: project.revisionId, reason: 'Synthetic role marker edit', changes: [{ path: file, content: 'Return value=input.value+1 and marker="v2".' }] });
  const next = release(root, resolve(root, 'agent', role));
  assert.notEqual(next.bundleSha256, releases.get(role).bundleSha256);
  assert.equal(loadReleaseBundle(root, { projectId, targetKind: 'workflow', targetId: 'synthetic-eight' }).bundleSha256, workflowRelease.bundleSha256);
  for (const [id, prior] of releases) if (id !== role) assert.equal(loadReleaseBundle(root, { projectId, targetKind: 'agent', targetId: id }).bundleSha256, prior.bundleSha256);
});

function change(root, requestId, changes) {
  return applyChanges(root, { projectId, requestId, baseRevision: readProject(root, { projectId }).revisionId, reason: 'Synthetic frozen dependency fixture', changes });
}
function frozenPair(root) {
  const schema = (minimum) => JSON.stringify({ $schema: 'https://json-schema.org/draft/2020-12/schema', $id: 'urn:synthetic:producer-input', type: 'object', properties: { seed: { type: 'integer', minimum } }, required: ['seed'], additionalProperties: false });
  change(root, 'schema-v1', [{ path: 'contracts/producer-input.schema.json', content: schema(0) }]);
  const a = resolveBundle(root, { projectId, targetKind: 'agent', targetId: 'lab-producer', model: { provider: 'source-provider', model: 'pinned-one' } }); const v1 = freeze(root, a);
  change(root, 'schema-v2', [{ path: 'contracts/producer-input.schema.json', content: schema(10) },
    { path: 'agents/lab-producer/instructions.md', content: 'Second version instructions.' },
    { path: 'skills/lab-marker/references/marker.json', content: '{"marker":"v2"}' },
    { path: 'skills/lab-marker/scripts/marker.mjs', content: 'process.stdout.write(JSON.stringify({scriptMarker:"script-v2"}));\n' }]);
  const b = resolveBundle(root, { projectId, targetKind: 'agent', targetId: 'lab-producer', model: { provider: 'source-provider', model: 'pinned-two' } }); const v2 = freeze(root, b);
  const steps = [v1, v2, v1].map((v, i) => ({ stepId: `frozen-${i + 1}`, agentId: 'lab-producer', agentVersion: { kind: 'frozen', frozenVersionId: v.frozenVersionId }, inputBindings: { '/seed': { source: 'input', pointer: '/seed' } } }));
  steps.push({ stepId: 'candidate-4', agentId: 'lab-producer', agentVersion: { kind: 'candidate' }, inputBindings: { '/seed': { source: 'input', pointer: '/seed' } } });
  change(root, 'frozen-workflow', [{ path: 'workflows/frozen-pair.json', content: JSON.stringify({ workflowId: 'frozen-pair', name: 'Pinned variants', steps }) }]);
  return { a, b, v1, v2, workflow: resolve(root, 'workflow', 'frozen-pair') };
}

test('same Agent frozen versions keep exact source bytes, models, schemas, tools and repeat identities isolated', (t) => {
  const { root } = fixture(t); const { a, b, v1, v2, workflow } = frozenPair(root);
  assert.equal(verifyBundle(workflow).ok, true);
  assert.equal(Object.keys(workflow.dependencyBundles).length, 2);
  assert.equal(workflow.dependencyBundles[a.bundleSha256].manifestContent, bundleManifestBytes(a).toString('utf8'));
  assert.equal(workflow.frozenDependencies[v1.frozenVersionId], a.bundleSha256);
  assert.equal(workflow.frozenDependencies[v2.frozenVersionId], b.bundleSha256);
  assert.deepEqual(workflow.steps.map((s) => s.model?.model ?? workflow.model.model), ['pinned-one', 'pinned-two', 'pinned-one', 'fake-model']);
  assert.ok(workflow.steps.every((s) => s.agentId === 'lab-producer'));
  const files = Object.fromEntries(workflow.files.map((f) => [f.path, f.content]));
  for (const original of [a, b]) for (const f of original.files) {
    const imported = workflow.files.find((x) => x.path === `dependencies/${original.bundleSha256}/${f.path}`);
    assert.equal(imported.content, f.content); assert.equal(imported.sha256, f.sha256); assert.equal(imported.size, f.size);
  }
  const [first, second, repeated, candidate] = workflow.steps;
  assert.equal(first.instructionsRef, repeated.instructionsRef); assert.notEqual(first.instructionsRef, second.instructionsRef); assert.notEqual(first.instructionsRef, candidate.instructionsRef);
  assert.equal(files[second.instructionsRef], 'Second version instructions.');
  assert.deepEqual([first, second].map((s) => workflow.tools[s.toolIds[0]].toolId), ['lab-marker', 'lab-marker']);
  assert.notEqual(first.toolIds[0], second.toolIds[0]);
  assert.ok(files[workflow.tools[first.toolIds[0]].scriptRef].includes('script-v1'));
  assert.ok(files[workflow.tools[second.toolIds[0]].scriptRef].includes('script-v2'));
  assert.equal(validateJson(JSON.parse(files[first.inputSchemaRef]), { seed: 3 }, { files, schemaRef: first.inputSchemaRef }).ok, true);
  assert.equal(validateJson(JSON.parse(files[second.inputSchemaRef]), { seed: 3 }, { files, schemaRef: second.inputSchemaRef }).ok, false);
  assert.equal(validateJson(JSON.parse(files[second.inputSchemaRef]), { seed: 12 }, { files, schemaRef: second.inputSchemaRef }).ok, true);
});

test('mixed frozen workflow release remains fully verifiable without any training root', (t) => {
  const { root } = fixture(t); const { workflow } = frozenPair(root); const r = release(root, workflow);
  fs.renameSync(path.join(root, 'Training_Materials'), path.join(root, 'unavailable-training'));
  const replay = loadReleaseBundle(root, { projectId, releaseId: r.releaseId });
  assert.deepEqual(replay, workflow); assert.equal(verifyBundle(replay).ok, true);
  for (const step of replay.steps) {
    const files = Object.fromEntries(replay.files.map((f) => [f.path, f.content]));
    assert.equal(validateJson(JSON.parse(files[step.inputSchemaRef]), { seed: 20 }, { files, schemaRef: step.inputSchemaRef }).ok, true);
  }
});

test('rehashed imported files and swapped source manifests cannot bypass source-to-projection binding', (t) => {
  const { root } = fixture(t); const { workflow, a } = frozenPair(root);
  for (const modify of [
    (w) => { const f = w.files.find((f) => f.path === w.steps[0].instructionsRef); f.content = 'tampered'; f.size = Buffer.byteLength(f.content); f.sha256 = trainerSha(Buffer.from(f.content)); },
    (w) => { w.dependencyBundles[a.bundleSha256].manifestContent += ' '; },
    (w) => { w.steps[0].model.model = 'current-default'; },
    (w) => { w.steps[0].toolIds = [...w.steps[0].toolIds, ...w.steps[1].toolIds]; },
  ]) {
    const changed = structuredClone(workflow); modify(changed); changed.bundleSha256 = trainerSha(bundleManifestBytes(changed));
    assert.equal(verifyBundle(changed).ok, false); assert.throws(() => freeze(root, changed), { code: 'TRAINER_INTEGRITY' });
  }
});

test('frozen workflow references reject missing/wrong-target sources and survive candidate Agent removal', (t) => {
  const { root } = fixture(t); const a = resolve(root, 'agent', 'lab-producer'); const frozen = freeze(root, a);
  const make = (agentId, frozenVersionId) => ({ workflowId: 'pinned-only', steps: [{ stepId: 'pinned', agentId, agentVersion: { kind: 'frozen', frozenVersionId }, inputBindings: { '/seed': { source: 'input', pointer: '/seed' } } }] });
  change(root, 'missing-source', [{ path: 'workflows/pinned-only.json', content: JSON.stringify(make('lab-producer', 'frozen-does-not-exist')) }]);
  assert.throws(() => resolve(root, 'workflow', 'pinned-only'), { code: 'ENOENT' });
  change(root, 'wrong-source', [{ path: 'workflows/pinned-only.json', content: JSON.stringify(make('lab-consumer', frozen.frozenVersionId)) }]);
  assert.throws(() => resolve(root, 'workflow', 'pinned-only'), { code: 'TRAINER_TARGET_MISMATCH' });
  change(root, 'remove-candidate', [
    { path: 'workflows/pinned-only.json', content: JSON.stringify(make('lab-producer', frozen.frozenVersionId)) },
    { path: 'workflows/lab-pair.json', content: null }, { path: 'tests/lab-pair.json', content: null },
    { path: 'agents/lab-producer/agent.json', content: null }, { path: 'agents/lab-producer/instructions.md', content: null },
  ]);
  assert.ok(!readProject(root, { projectId }).agents.some((agent) => agent.agentId === 'lab-producer'));
  assert.equal(resolve(root, 'workflow', 'pinned-only').steps[0].sourceBundleSha256, a.bundleSha256);
});

test('frozen version listing restores metadata, filters targets and verifies every completed package', (t) => {
  const { root } = fixture(t);
  assert.deepEqual(listFrozenVersions(root, { projectId }), { projectId, versions: [] });
  const one = freeze(root, resolve(root, 'agent', 'lab-producer'));
  const two = freeze(root, resolve(root, 'agent', 'lab-consumer'));
  const three = freeze(root, resolve(root, 'workflow', 'lab-pair'));
  const all = listFrozenVersions(root, { projectId }).versions;
  assert.deepEqual(new Set(all.map((v) => v.frozenVersionId)), new Set([one.frozenVersionId, two.frozenVersionId, three.frozenVersionId]));
  assert.deepEqual(listFrozenVersions(root, { projectId, targetKind: 'agent', targetId: 'lab-producer' }).versions, [one]);
  assert.deepEqual(listFrozenVersions(root, { projectId, targetKind: 'workflow' }).versions, [three]);
  const file = path.join(root, 'Training_Materials/framework/projects', projectId, 'versions', two.frozenVersionId, 'bundle-manifest.json'); fs.appendFileSync(file, ' ');
  // Filtering may not hide corruption in another completed snapshot.
  assert.throws(() => listFrozenVersions(root, { projectId, targetKind: 'workflow' }), { code: 'TRAINER_INTEGRITY' });
});
