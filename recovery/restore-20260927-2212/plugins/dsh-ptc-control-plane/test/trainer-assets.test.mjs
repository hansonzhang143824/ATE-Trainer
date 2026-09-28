import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { ensureTrainerProject, readAssets, readProject, applyChanges, trainerSha } from '../lib/trainer-project.js';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';
import { validateJson, validateProjectFiles } from '../lib/trainer-schema.js';
import { resolveBundle, verifyBundle, freezeTarget, loadFrozenBundle, bundleManifestBytes } from '../lib/trainer-bundle.js';
import { stageRelease, activateRelease, loadReleaseBundle, listReleases } from '../lib/trainer-release.js';

const projectId = 'synthetic-lab';
const model = { provider: 'synthetic-test', model: 'fake-model', options: { temperature: 0 } };
function setup(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-assets-'));
  t.after(() => { assert.equal(path.dirname(root), fs.realpathSync(os.tmpdir())); assert.ok(path.basename(root).startsWith('trainer-assets-')); fs.rmSync(root, { recursive: true, force: true }); });
  const project = ensureTrainerProject(root, { projectId });
  return { root, project };
}
function bundle(root, extra = {}) { return resolveBundle(root, { projectId, targetKind: 'workflow', targetId: 'lab-pair', model, ...extra }); }
function freeze(root, b) { return freezeTarget(root, { projectId, targetKind: b.targetKind, targetId: b.targetId, bundle: b }); }
function evidence(b) { return { runId: 'fake-run-1', projectId, targetKind: b.targetKind, targetId: b.targetId, bundleSha256: b.bundleSha256, status: 'completed', validation: { ok: true }, businessGatePassed: false, steps: b.steps.map((s) => ({ stepId: s.stepId, agentId: s.agentId, status: 'completed' })) }; }
function edit(root, project, changes, requestId = 'edit-1') { return applyChanges(root, { projectId, requestId, baseRevision: project.revisionId, changes, reason: 'Synthetic test change' }); }

test('synthetic fixture is valid; project bootstrap is idempotent and indexes declared agents', (t) => {
  const { root, project } = setup(t);
  assert.deepEqual(validateProjectFiles(createSyntheticTrainerFixture().files), { ok: true, errors: [] });
  assert.equal(ensureTrainerProject(root, { projectId }).revisionId, project.revisionId);
  assert.deepEqual(project.agents.map((a) => a.agentId), ['lab-consumer', 'lab-producer']);
  assert.equal(project.workflows[0].workflowId, 'lab-pair');
});
test('atomic multi-asset edit preserves old revision, records diff and replays request', (t) => {
  const { root, project } = setup(t); const before = readAssets(root, { projectId });
  const changes = [{ path: 'skills/lab-marker/references/marker.json', content: '{"marker":"v2"}\n' }, { path: 'agents/lab-producer/instructions.md', content: 'Changed synthetic instruction\r\n' }];
  const result = edit(root, project, changes);
  assert.notEqual(result.revisionId, project.revisionId); assert.equal(result.diff.length, 2);
  assert.deepEqual(edit(root, project, changes), result);
  assert.deepEqual(readAssets(root, { projectId, revisionId: project.revisionId }).files, before.files);
  assert.throws(() => edit(root, project, changes, 'stale-request'), { code: 'TRAINER_REVISION_CONFLICT' });
  assert.throws(() => edit(root, project, [{ ...changes[0], content: '{}' }]), { code: 'TRAINER_REQUEST_CONFLICT' });
});
test('invalid group or failed pointer replacement never exposes half a revision', (t) => {
  const { root, project } = setup(t);
  assert.throws(() => edit(root, project, [{ path: 'contracts/producer-input.schema.json', content: null }]), { code: 'TRAINER_PROJECT_INVALID' });
  assert.equal(readProject(root, { projectId }).revisionId, project.revisionId);
  const rename = fs.renameSync; fs.renameSync = () => { throw new Error('simulated pointer commit failure'); };
  try { assert.throws(() => edit(root, project, [{ path: 'agents/lab-producer/instructions.md', content: 'new' }]), /simulated/); }
  finally { fs.renameSync = rename; }
  assert.equal(readProject(root, { projectId }).revisionId, project.revisionId);
  assert.ok(readAssets(root, { projectId }).files['agents/lab-producer/instructions.md'].includes('input.seed'));
});
test('committed save recovers a lost receipt before another save and still deduplicates original request', (t) => {
  const { root, project } = setup(t); const changes = [{ path: 'agents/lab-producer/instructions.md', content: 'first' }];
  const write = fs.writeFileSync;
  fs.writeFileSync = (file, ...args) => { if (String(file).includes(`${path.sep}requests${path.sep}`)) throw new Error('simulated receipt failure'); return write(file, ...args); };
  try { assert.throws(() => edit(root, project, changes), /receipt failure/); } finally { fs.writeFileSync = write; }
  const committed = readProject(root, { projectId }); assert.notEqual(committed.revisionId, project.revisionId);
  edit(root, committed, [{ path: 'agents/lab-producer/instructions.md', content: 'second' }], 'edit-2');
  const replay = edit(root, project, changes); assert.equal(replay.revisionId, committed.revisionId);
  assert.equal(readAssets(root, { projectId }).files['agents/lab-producer/instructions.md'], 'second');
});
test('malformed definitions are rejected rather than silently dropping declared settings', (t) => {
  const { root, project } = setup(t); const files = readAssets(root, { projectId }).files;
  const agent = JSON.parse(files['agents/lab-producer/agent.json']); agent.skillRefs = 'wrong-type';
  assert.throws(() => edit(root, project, [{ path: 'agents/lab-producer/agent.json', content: JSON.stringify(agent) }]), { code: 'TRAINER_PROJECT_INVALID' });
  const workflow = JSON.parse(files['workflows/lab-pair.json']); workflow.steps[0].agentVersion = 'unimplemented-reference';
  assert.throws(() => edit(root, project, [{ path: 'workflows/lab-pair.json', content: JSON.stringify(workflow) }]), { code: 'TRAINER_PROJECT_INVALID' });
});
test('test expectations require a JSON object and invalid saves preserve the candidate revision', (t) => {
  const { root, project } = setup(t); const original = readAssets(root, { projectId }).files['tests/lab-pair.json'];
  for (const expected of [null, 0, 3, false, true, 'text', [], [1]]) {
    const definition = JSON.parse(original); definition.cases[0].expected = expected;
    assert.throws(() => edit(root, project, [{ path: 'tests/lab-pair.json', content: JSON.stringify(definition) }]), (error) => {
      assert.equal(error.code, 'TRAINER_PROJECT_INVALID');
      assert.ok(error.details.some((item) => item.path === 'tests/lab-pair.json/cases/0/expected' && item.keyword === 'type'));
      return true;
    });
    assert.equal(readProject(root, { projectId }).revisionId, project.revisionId);
  }
  const definition = JSON.parse(original); definition.cases[0].expected = { receivedValue: 8, nested: { values: [1, 2], nullable: null } };
  const saved = edit(root, project, [{ path: 'tests/lab-pair.json', content: JSON.stringify(definition) }]);
  assert.notEqual(saved.revisionId, project.revisionId);
  assert.deepEqual(JSON.parse(readAssets(root, { projectId }).files['tests/lab-pair.json']).cases[0].expected, definition.cases[0].expected);
});
test('links, path traversal and duplicate edits fail closed', (t) => {
  const { root, project } = setup(t);
  for (const p of ['../outside', 'agents/../outside', 'agents/CON/instructions.md', 'agents/a/instructions.md:stream', 'agents/a./instructions.md']) assert.throws(() => edit(root, project, [{ path: p, content: 'x' }]), { code: 'TRAINER_INVALID_CHANGE' });
  assert.throws(() => edit(root, project, [{ path: 'agents/a/x', content: 'x' }, { path: 'agents/a/x', content: 'y' }]), { code: 'TRAINER_INVALID_CHANGE' });
  const draft = path.join(root, 'Training_Materials/framework/projects', projectId, 'revisions', project.revisionId, 'agents/lab-producer/instructions.md');
  fs.linkSync(draft, path.join(root, 'linked.md'));
  assert.throws(() => readAssets(root, { projectId }), { code: 'TRAINER_UNSAFE_PATH' });
});
test('complete bundle locks later step, skill document, reference and script bytes', (t) => {
  const { root, project } = setup(t); const old = bundle(root);
  assert.equal(verifyBundle(old).ok, true); assert.equal(old.bundleSha256, trainerSha(bundleManifestBytes(old)));
  assert.ok(old.files.some((f) => f.path.endsWith('marker.mjs')));
  edit(root, project, [{ path: 'agents/lab-consumer/instructions.md', content: 'new consumer' }, { path: 'skills/lab-marker/scripts/marker.mjs', content: 'process.stdout.write("new")' }]);
  assert.ok(old.files.find((f) => f.path.endsWith('lab-consumer/instructions.md')).content.includes('exactly'));
  assert.notEqual(bundle(root).bundleSha256, old.bundleSha256);
  const modified = structuredClone(old); modified.files[0].content += 'x'; assert.equal(verifyBundle(modified).ok, false);
});
test('rehashed resolved projections must still match packaged authored definitions', (t) => {
  const { root } = setup(t); const b = bundle(root);
  for (const mutate of [
    (value) => { value.steps[0].instructionsRef = value.steps[1].instructionsRef; },
    (value) => { value.steps.reverse(); },
    (value) => { value.steps[1].inputBindings = {}; },
    (value) => { value.steps[0].toolIds = []; },
    (value) => { value.tools['lab-marker'].adapterVersion = 'unregistered-version'; },
    (value) => { value.skills['lab-marker'].referenceRefs = []; },
    (value) => { value.tests = []; },
  ]) {
    const changed = structuredClone(b); mutate(changed); changed.bundleSha256 = trainerSha(bundleManifestBytes(changed));
    const result = verifyBundle(changed); assert.equal(result.ok, false); assert.ok(result.errors.some((e) => e.code === 'TRAINER_BUNDLE_DEFINITION_MISMATCH'));
    assert.throws(() => freeze(root, changed), { code: 'TRAINER_INTEGRITY' });
  }
});
test('single-agent bundle excludes unrelated role and workflow; repeat roles preserve step order', (t) => {
  const { root, project } = setup(t);
  const single = bundle(root, { targetKind: 'agent', targetId: 'lab-consumer' });
  assert.equal(single.steps.length, 1); assert.ok(single.files.every((f) => !f.path.includes('producer') && !f.path.startsWith('workflows/') && !f.path.startsWith('skills/')));
  const w = JSON.parse(readAssets(root, { projectId }).files['workflows/lab-pair.json']);
  w.steps.push({ stepId: 'produce-again', agentId: 'lab-producer', inputBindings: { '/seed': { source: 'step', stepId: 'consume', pointer: '/receivedValue' } } });
  edit(root, project, [{ path: 'workflows/lab-pair.json', content: JSON.stringify(w) }]);
  assert.deepEqual(bundle(root).steps.map((s) => s.agentId), ['lab-producer', 'lab-consumer', 'lab-producer']);
});
test('new configured agent is discoverable without a JavaScript registry change', (t) => {
  const { root, project } = setup(t);
  edit(root, project, [
    { path: 'agents/ninth/agent.json', content: JSON.stringify({ agentId: 'ninth', name: 'New synthetic role', instructionsRef: 'agents/ninth/instructions.md', skillRefs: [], toolIds: [], inputSchemaRef: 'contracts/empty.schema.json', outputSchemaRef: 'contracts/empty.schema.json' }) },
    { path: 'agents/ninth/instructions.md', content: 'Return any JSON object.' }, { path: 'contracts/empty.schema.json', content: '{"type":"object"}' },
  ]);
  assert.ok(readProject(root, { projectId }).agents.some((a) => a.agentId === 'ninth'));
  assert.equal(bundle(root, { targetKind: 'agent', targetId: 'ninth' }).steps[0].agentId, 'ninth');
});
test('Draft 2020-12 validates conditionals, formats, unevaluated fields and local refs without mutation', () => {
  const schema = { type: 'object', properties: { value: { type: 'integer' }, stamp: { type: 'string', format: 'date-time' } }, required: ['value', 'stamp'], if: { properties: { value: { minimum: 2, type: 'integer' } } }, then: { properties: { value: { maximum: 5, type: 'integer' } } }, unevaluatedProperties: false };
  const input = { value: '3', stamp: 'bad', extra: true }; const saved = structuredClone(input);
  const result = validateJson(schema, input); assert.equal(result.ok, false); assert.ok(result.errors.some((e) => e.path === '/value')); assert.deepEqual(input, saved);
  assert.equal(validateJson(schema, { value: 3, stamp: '2026-09-25T00:00:00Z' }).ok, true);
  assert.equal(validateJson({ $ref: 'https://outside.invalid/schema' }, {}).ok, false);
  assert.equal(validateJson({ nonsenseKeyword: true }, {}).ok, false);
  const files = { 'contracts/a.schema.json': '{"type":"integer","minimum":2}', 'contracts/b.schema.json': '{"$ref":"a.schema.json"}' };
  assert.equal(validateJson(JSON.parse(files['contracts/b.schema.json']), 3, { files }).ok, true);
  assert.equal(validateJson(JSON.parse(files['contracts/b.schema.json']), 1, { files }).ok, false);
});
test('schema dependency closure follows local refs and rejects missing dependency on save', (t) => {
  const { root, project } = setup(t);
  edit(root, project, [{ path: 'contracts/producer-input.schema.json', content: '{"$ref":"shared.schema.json"}' }, { path: 'contracts/shared.schema.json', content: '{"type":"object"}' }]);
  assert.ok(bundle(root).files.some((f) => f.path === 'contracts/shared.schema.json'));
  assert.throws(() => edit(root, readProject(root, { projectId }), [{ path: 'contracts/shared.schema.json', content: null }], 'remove-dependency'), { code: 'TRAINER_PROJECT_INVALID' });
});
test('freeze preserves exact tested bytes after candidate changes and detects disk tampering', (t) => {
  const { root, project } = setup(t); const b = bundle(root);
  edit(root, project, [{ path: 'agents/lab-producer/instructions.md', content: 'future' }]);
  const f = freeze(root, b); assert.equal(f.bundleSha256, b.bundleSha256);
  assert.deepEqual(loadFrozenBundle(root, { projectId, frozenVersionId: f.frozenVersionId }), b);
  const file = path.join(root, 'Training_Materials/framework/projects', projectId, 'versions', f.frozenVersionId, 'bundle-manifest.json');
  assert.deepEqual(fs.readFileSync(file), bundleManifestBytes(b)); fs.appendFileSync(file, ' ');
  assert.throws(() => loadFrozenBundle(root, { projectId, frozenVersionId: f.frozenVersionId }), { code: 'TRAINER_INTEGRITY' });
});
test('release rejects wrong bundle, target, step status and failed framework validation', (t) => {
  const { root } = setup(t); const b = bundle(root); const f = freeze(root, b); const e = evidence(b);
  for (const patch of [{ status: 'failed' }, { bundleSha256: '0'.repeat(64) }, { projectId: 'other' }, { targetId: 'other' }, { businessGatePassed: true }, { validation: { ok: false } }, { steps: [] }]) assert.throws(() => stageRelease(root, { projectId, frozenVersionId: f.frozenVersionId, runEvidence: { ...e, ...patch } }), { code: 'TRAINER_RELEASE_EVIDENCE' });
});
test('release is self-contained; active pointers separate single agent and workflow', (t) => {
  const { root, project } = setup(t); const b = bundle(root); const agent = bundle(root, { targetKind: 'agent', targetId: 'lab-consumer' });
  const releases = [b, agent].map((item) => stageRelease(root, { projectId, frozenVersionId: freeze(root, item).frozenVersionId, runEvidence: evidence(item) }));
  for (const r of releases) activateRelease(root, { projectId, releaseId: r.releaseId });
  edit(root, project, [{ path: 'agents/lab-consumer/instructions.md', content: 'future' }]);
  assert.equal(loadReleaseBundle(root, { projectId, targetKind: 'workflow', targetId: 'lab-pair' }).bundleSha256, b.bundleSha256);
  assert.equal(listReleases(root, { projectId }).active.length, 2);
  fs.renameSync(path.join(root, 'Training_Materials'), path.join(root, 'unavailable-training'));
  const isolated = path.join(root, 'isolated'); fs.mkdirSync(path.join(isolated, 'publish/versions'), { recursive: true });
  fs.cpSync(path.join(root, 'publish/versions', releases[0].releaseId), path.join(isolated, 'publish/versions', releases[0].releaseId), { recursive: true });
  const replay = loadReleaseBundle(isolated, { projectId, releaseId: releases[0].releaseId });
  assert.deepEqual(replay, b); assert.equal(verifyBundle(replay).ok, true);
});
