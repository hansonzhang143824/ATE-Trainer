import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createSyntheticTrainerFixture } from '../lib/trainer-synthetic-fixture.js';
import * as projects from '../lib/trainer-project.js';
import * as bundles from '../lib/trainer-bundle.js';
import * as releases from '../lib/trainer-release.js';
import { createFrameworkRunner } from '../lib/framework-agent-run.js';
import { createTrainerService, syntheticBusinessBundle, syntheticSmokeBundle, SYNTHETIC_BUSINESS_INSTRUCTIONS, SYNTHETIC_SMOKE_INSTRUCTIONS } from '../lib/trainer-service.js';
import { validateJson } from '../lib/trainer-schema.js';

const model = { provider: 'test', model: 'test' };
const target = { projectId: 'pilot', targetKind: 'agent', targetId: 'lab-producer' };

function setup(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-release-integrity-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  let child = 0;
  const adapter = { async dispatch({ step, bundle, onStart }) {
    const childSessionId = `child-${++child}`; onStart({ childSessionId, parentSessionId: 'parent-1' });
    const instruction = bundle.files.find((file) => file.path === step.instructionsRef)?.content || '';
    return { output: { answer: instruction.includes('BUSINESS_ONLY') ? 597 : 3 }, childSessionId, childTerminationConfirmed: true, stopReason: 'completed' };
  } };
  const runner = createFrameworkRunner({ workspaceRoot: root, adapter, verifyBundle: bundles.verifyBundle, validateJson });
  const service = createTrainerService({ workspaceRoot: root, runner,
    repositories: { ...projects, ...bundles, ...releases }, modelResolver: () => model });
  projects.ensureTrainerProject(root, { projectId: target.projectId, seed: createSyntheticTrainerFixture() });
  const source = bundles.resolveBundle(root, { ...target, model });
  const page = (operation, input = {}) => service.invoke(operation, { ...target, mode: 'training', ...input }, { kind: 'page' });
  return { root, runner, service, source, page };
}

async function serviceRun(s, executionMode, requestId) {
  const started = await s.page('run', { requestId, executionMode, input: { seed: 7 } });
  assert.equal(started.ok, true, JSON.stringify(started));
  await s.runner.waitForRun({ runId: started.value.runId });
  const result = await s.page('runs', { runId: started.value.runId });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(result.value.status, 'completed', JSON.stringify(result));
  return result.value;
}

test('D-1 smoke run stores source bundle and freeze uses authored instructions', async t => {
  const s = setup(t); const run = await serviceRun(s, 'SMOKE_ONLY', 'd-smoke-run');
  assert.ok(run.sourceBundle); assert.notEqual(run.sourceBundleSha256, run.bundleSha256);
  const frozen = await s.page('freeze', { requestId: 'd-smoke-freeze', runId: run.runId }); assert.equal(frozen.ok, true, JSON.stringify(frozen));
  assert.equal(frozen.value.bundleSha256, run.sourceBundleSha256); assert.equal(frozen.value.sequence, 1); assert.equal(frozen.value.validation.executionMode, 'SMOKE_ONLY'); assert.ok(frozen.value.createdAt);
  const manifest = JSON.parse(fs.readFileSync(path.join(s.root, 'Training_Materials/framework/projects/pilot/versions', frozen.value.frozenVersionId, 'bundle-manifest.json')));
  const ref = run.sourceBundle.steps[0].instructionsRef; assert.equal(manifest.files.find(file => file.path === ref).content, run.sourceBundle.files.find(file => file.path === ref).content);
});

test('D-1 business freeze records a second sequence', async t => {
  const s = setup(t); const smoke = await serviceRun(s, 'SMOKE_ONLY', 'd-sequence-smoke');
  const first = await s.page('freeze', { requestId: 'd-sequence-freeze-1', runId: smoke.runId }); assert.equal(first.ok, true, JSON.stringify(first));
  const business = await serviceRun(s, 'BUSINESS_ONLY', 'd-sequence-business');
  const second = await s.page('freeze', { requestId: 'd-sequence-freeze-2', runId: business.runId }); assert.equal(second.ok, true, JSON.stringify(second));
  assert.equal(second.value.sequence, first.value.sequence + 1); assert.notEqual(business.sourceBundleSha256, business.bundleSha256);
});

test('D-1 release stores validation mode and both bundle digests', async t => {
  const s = setup(t); const run = await serviceRun(s, 'SMOKE_ONLY', 'd-release-run');
  const frozen = await s.page('freeze', { requestId: 'd-release-freeze', runId: run.runId }); assert.equal(frozen.ok, true, JSON.stringify(frozen));
  const staged = await s.page('stage-release', { requestId: 'd-release-stage', frozenVersionId: frozen.value.frozenVersionId, runId: run.runId }); assert.equal(staged.ok, true, JSON.stringify(staged));
  assert.equal(staged.value.validationMode, 'SMOKE_ONLY'); assert.equal(staged.value.sequence, 1); assert.ok(staged.value.createdAt);
  const verification = projects.trainerRead(s.root, 'publish', 'versions', staged.value.releaseId, 'verification.json');
  assert.equal(verification.bundleSha256, run.sourceBundleSha256); assert.equal(verification.executionBundleSha256, run.bundleSha256);
  assert.equal((await s.page('activate-release', { requestId: 'd-release-activate', releaseId: staged.value.releaseId })).ok, true);
});

test('D-1d old synthetic records fail with validation_source_unavailable', async t => {
  const s = setup(t); const execution = syntheticSmokeBundle(s.source);
  const started = await s.runner.startRun({ runId: 'legacy-synthetic-run', requestId: 'legacy-synthetic-run', mode: 'training', bundle: execution, input: { seed: 7 }, executionMode: 'SMOKE_ONLY' });
  await s.runner.waitForRun(started);
  const recordFile = path.join(s.root, 'Training_Materials/runs', started.runId, 'framework-run.json'); const record = JSON.parse(fs.readFileSync(recordFile)); delete record.sourceBundleSha256; delete record.sourceBundleArtifact; fs.writeFileSync(recordFile, `${JSON.stringify(record, null, 2)}\n`);
  const result = await s.page('freeze', { requestId: 'legacy-synthetic-freeze', runId: started.runId }); assert.equal(result.ok, false); assert.equal(result.error.code, 'validation_source_unavailable');
});

test('D-2 contaminated frozen versions are listed and cannot be staged', async t => {
  const s = setup(t); const contaminated = bundles.freezeTarget(s.root, { ...target, bundle: syntheticSmokeBundle(s.source) });
  const listed = bundles.listFrozenVersions(s.root, target).versions.find(item => item.frozenVersionId === contaminated.frozenVersionId); assert.equal(listed.contaminated, true); assert.ok(listed.contaminatedRefs.length);
  assert.throws(() => releases.stageRelease(s.root, { projectId: target.projectId, frozenVersionId: contaminated.frozenVersionId, runEvidence: {} }), error => error.code === 'TRAINER_FROZEN_SYNTHETIC');
});

test('D-2 workflow references to contaminated frozen Agents are rejected', async t => {
  const s = setup(t); const contaminated = bundles.freezeTarget(s.root, { ...target, bundle: syntheticSmokeBundle(s.source) });
  const project = projects.readProject(s.root, target); const workflow = JSON.parse(createSyntheticTrainerFixture().files['workflows/lab-pair.json']); workflow.steps[0].agentVersion = { kind: 'frozen', frozenVersionId: contaminated.frozenVersionId };
  const changed = projects.applyChanges(s.root, { projectId: target.projectId, requestId: 'contaminated-workflow', baseRevision: project.revisionId, reason: 'test contaminated frozen dependency', changes: [{ path: 'workflows/lab-pair.json', content: JSON.stringify(workflow) }] });
  assert.throws(() => bundles.resolveBundle(s.root, { projectId: target.projectId, targetKind: 'workflow', targetId: 'lab-pair', revisionId: changed.revisionId, model }), error => error.code === 'TRAINER_FROZEN_SYNTHETIC');
});

test('D-2 contaminated releases are listed and cannot change active pointer', async t => {
  const s = setup(t); const run = await serviceRun(s, 'SMOKE_ONLY', 'd-clean-run'); const cleanFrozen = await s.page('freeze', { requestId: 'd-clean-freeze', runId: run.runId }); const cleanRelease = await s.page('stage-release', { requestId: 'd-clean-stage', frozenVersionId: cleanFrozen.value.frozenVersionId, runId: run.runId }); await s.page('activate-release', { requestId: 'd-clean-activate', releaseId: cleanRelease.value.releaseId });
  const synthetic = syntheticSmokeBundle(s.source); const releaseId = 'release-synthetic-test'; const evidence = { runId: 'legacy', projectId: target.projectId, targetKind: target.targetKind, targetId: target.targetId, bundleSha256: synthetic.bundleSha256, workflowRevision: null, status: 'completed', validation: { ok: true }, businessGatePassed: false, steps: synthetic.steps.map(step => ({ stepId: step.stepId, agentId: step.agentId, agentRevision: step.agentRevision ?? null, status: 'completed' })) };
  const bytes = Buffer.from(projects.trainerJson(evidence)); const directory = path.join(s.root, 'publish', 'versions', releaseId); fs.mkdirSync(directory, { recursive: true }); fs.writeFileSync(path.join(directory, 'bundle-manifest.json'), bundles.bundleManifestBytes(synthetic)); fs.writeFileSync(path.join(directory, 'verification.json'), bytes); projects.trainerWrite(path.join(s.root, 'publish'), `versions/${releaseId}/release.json`, projects.trainerJson({ schemaVersion: 1, runtimeApiVersion: 'trainer-api-v1', projectId: target.projectId, releaseId, frozenVersionId: 'legacy', targetKind: target.targetKind, targetId: target.targetId, revisionId: synthetic.revisionId, workflowRevision: null, agentBindings: synthetic.steps.map(step => ({ stepId: step.stepId, agentId: step.agentId, agentRevision: step.agentRevision ?? null })), bundleSha256: synthetic.bundleSha256, evidenceSha256: projects.trainerSha(bytes), verifiedRunId: evidence.runId, businessGatePassed: false }));
  const listed = releases.listReleases(s.root, { projectId: target.projectId }).releases.find(item => item.releaseId === releaseId); assert.equal(listed.contaminated, true); assert.throws(() => releases.activateRelease(s.root, { projectId: target.projectId, releaseId }), error => error.code === 'TRAINER_RELEASE_SYNTHETIC'); assert.equal(releases.listReleases(s.root, { projectId: target.projectId }).active[0].releaseId, cleanRelease.value.releaseId);
});

test('D-3 frozen versions sort by sequence descending', async t => {
  const s = setup(t); const ids = [];
  for (let i = 0; i < 3; i++) { const run = await serviceRun(s, 'SMOKE_ONLY', `d-order-run-${i}`); ids.push((await s.page('freeze', { requestId: `d-order-freeze-${i}`, runId: run.runId })).value.frozenVersionId); }
  const listed = bundles.listFrozenVersions(s.root, target).versions.filter(item => ids.includes(item.frozenVersionId)); assert.deepEqual(listed.map(item => item.sequence), [3, 2, 1]);
});

test('D-1 source identity and source artifact integrity are enforced', async t => {
  const s = setup(t); projects.ensureTrainerProject(s.root, { projectId: 'other', seed: createSyntheticTrainerFixture() }); const foreign = bundles.resolveBundle(s.root, { ...target, projectId: 'other', model }); const execution = syntheticSmokeBundle(s.source);
  await assert.rejects(() => s.runner.startRun({ runId: 'mismatch-run', requestId: 'mismatch-run', mode: 'training', bundle: execution, sourceBundle: foreign, input: { seed: 7 }, executionMode: 'SMOKE_ONLY' }), error => error.code === 'SOURCE_BUNDLE_MISMATCH');
  const started = await s.runner.startRun({ runId: 'tamper-run', requestId: 'tamper-run', mode: 'training', bundle: execution, sourceBundle: s.source, input: { seed: 7 }, executionMode: 'SMOKE_ONLY' }); await s.runner.waitForRun(started); fs.appendFileSync(path.join(s.root, 'Training_Materials/runs', started.runId, 'source-bundle.json'), 'tampered'); assert.throws(() => s.runner.readRun(started), error => error.code === 'RUN_BUNDLE_CHANGED');
});

test('D-4 synthetic marker exports match both synthetic bundles', t => {
  const s = setup(t); assert.match(SYNTHETIC_SMOKE_INSTRUCTIONS, /^# Synthetic (SMOKE_ONLY|BUSINESS_ONLY) verification/); assert.match(SYNTHETIC_BUSINESS_INSTRUCTIONS, /^# Synthetic (SMOKE_ONLY|BUSINESS_ONLY) verification/); assert.ok(bundles.syntheticInstructionRefs(syntheticSmokeBundle(s.source)).length); assert.ok(bundles.syntheticInstructionRefs(syntheticBusinessBundle(s.source)).length);
});
