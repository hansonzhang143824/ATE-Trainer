import fs from 'node:fs';
import { randomUUID } from 'node:crypto';
import { bundleManifestBytes, loadFrozenBundle, syntheticInstructionRefs, verifyBundle } from './trainer-bundle.js';
import { trainerFail, trainerId, trainerJson, trainerLock, trainerRead, trainerSafe, trainerSha, trainerWrite } from './trainer-project.js';

const releaseRoot = (root) => trainerSafe(root, 'publish');
function evidenceCheck(bundle, evidence) {
  if (!evidence || evidence.projectId !== bundle.projectId || evidence.targetKind !== bundle.targetKind || evidence.targetId !== bundle.targetId
    || (evidence.sourceBundleSha256 ?? evidence.bundleSha256) !== bundle.bundleSha256 || (evidence.workflowRevision ?? null) !== (bundle.workflowRevision ?? null)
    || evidence.status !== 'completed' || evidence.validation?.ok !== true || evidence.businessGatePassed !== false
    || !Array.isArray(evidence.steps) || evidence.steps.length !== bundle.steps.length || evidence.steps.some((s, i) =>
      s.stepId !== bundle.steps[i].stepId || s.agentId !== bundle.steps[i].agentId
      || (s.agentRevision ?? null) !== (bundle.steps[i].agentRevision ?? null) || s.status !== 'completed')) {
    trainerFail('TRAINER_RELEASE_EVIDENCE', 'release requires completed framework validation of this exact target and bundle');
  }
  trainerId(evidence.runId);
}
function readRelease(root, projectId, releaseId) {
  trainerId(projectId); trainerId(releaseId); const directory = releaseRoot(root);
  const metadata = trainerRead(directory, 'versions', releaseId, 'release.json');
  if (metadata.projectId !== projectId || metadata.releaseId !== releaseId) trainerFail('TRAINER_RELEASE_TARGET', 'release identity mismatch');
  const bytes = fs.readFileSync(trainerSafe(directory, 'versions', releaseId, 'bundle-manifest.json'));
  if (trainerSha(bytes) !== metadata.bundleSha256) trainerFail('TRAINER_INTEGRITY', 'release manifest bytes changed');
  const bundle = { ...JSON.parse(bytes), bundleSha256: metadata.bundleSha256 }; const validation = verifyBundle(bundle);
  if (!validation.ok) trainerFail('TRAINER_INTEGRITY', 'invalid release bundle', validation.errors);
  if (bundle.projectId !== projectId || bundle.targetKind !== metadata.targetKind || bundle.targetId !== metadata.targetId) trainerFail('TRAINER_RELEASE_TARGET', 'release bundle target mismatch');
  const evidenceBytes = fs.readFileSync(trainerSafe(directory, 'versions', releaseId, 'verification.json'));
  if (trainerSha(evidenceBytes) !== metadata.evidenceSha256) trainerFail('TRAINER_INTEGRITY', 'release evidence changed');
  evidenceCheck(bundle, JSON.parse(evidenceBytes));
  return { bundle, metadata };
}
export function stageRelease(root, { projectId, frozenVersionId, runEvidence }) {
  const bundle = loadFrozenBundle(root, { projectId, frozenVersionId });
  if (syntheticInstructionRefs(bundle).length) trainerFail('TRAINER_FROZEN_SYNTHETIC', '该冻结版本包含合成指令，不能发布');
  evidenceCheck(bundle, runEvidence);
  const directory = releaseRoot(root);
  return trainerLock(trainerSafe(directory, 'versions'), () => {
    const versionsRoot = trainerSafe(directory, 'versions'); let maxSequence = 0;
    if (fs.existsSync(versionsRoot)) for (const name of fs.readdirSync(versionsRoot).filter((n) => n.startsWith('release-'))) {
      const marker = trainerSafe(versionsRoot, name, 'release.json'); if (!fs.existsSync(marker)) continue;
      try { maxSequence = Math.max(maxSequence, Number(trainerRead(directory, 'versions', name, 'release.json').sequence) || 0); } catch { /* incomplete entries are not sequence sources */ }
    }
    const releaseId = `release-${randomUUID()}`;
    // Persist only release verification fields; session logs/headers are unnecessary.
    const evidence = { runId: runEvidence.runId, projectId, targetKind: bundle.targetKind, targetId: bundle.targetId, bundleSha256: bundle.bundleSha256,
      executionBundleSha256: runEvidence.bundleSha256, sourceBundleSha256: runEvidence.sourceBundleSha256 ?? runEvidence.bundleSha256,
      workflowRevision: bundle.workflowRevision ?? null, executionMode: runEvidence.executionMode ?? 'FRAMEWORK_TRAINING',
      status: runEvidence.status, validation: runEvidence.validation, businessGatePassed: false,
      steps: runEvidence.steps.map((s) => ({ stepId: s.stepId, agentId: s.agentId, agentRevision: s.agentRevision ?? null, status: s.status })) };
    const evidenceBytes = Buffer.from(trainerJson(evidence));
    const metadata = { schemaVersion: 1, runtimeApiVersion: 'trainer-api-v1', projectId, releaseId, frozenVersionId,
      targetKind: bundle.targetKind, targetId: bundle.targetId, revisionId: bundle.revisionId,
      workflowRevision: bundle.workflowRevision ?? null,
      agentBindings: bundle.steps.map((step) => ({ stepId: step.stepId, agentId: step.agentId, agentRevision: step.agentRevision ?? null })),
      bundleSha256: bundle.bundleSha256, evidenceSha256: trainerSha(evidenceBytes), verifiedRunId: evidence.runId, businessGatePassed: false,
      createdAt: new Date().toISOString(), sequence: maxSequence + 1, validationMode: runEvidence.executionMode ?? 'FRAMEWORK_TRAINING' };
    trainerWrite(directory, `versions/${releaseId}/bundle-manifest.json`, bundleManifestBytes(bundle));
    trainerWrite(directory, `versions/${releaseId}/verification.json`, evidenceBytes);
    // Completion marker is written last; partially staged directories cannot load.
    trainerWrite(directory, `versions/${releaseId}/release.json`, trainerJson(metadata));
    readRelease(root, projectId, releaseId);
    return metadata;
  });
}
export function activateRelease(root, { projectId, releaseId }) {
  const directory = releaseRoot(root);
  return trainerLock(trainerSafe(directory, 'active', trainerId(projectId)), () => {
    const { metadata } = readRelease(root, projectId, releaseId);
    const bundle = loadReleaseBundle(root, { projectId, releaseId, targetKind: metadata.targetKind, targetId: metadata.targetId });
    if (syntheticInstructionRefs(bundle).length) trainerFail('TRAINER_RELEASE_SYNTHETIC', '该发布版本包含合成指令，不能激活');
    const pointer = { schemaVersion: 1, projectId, targetKind: metadata.targetKind, targetId: metadata.targetId, releaseId, bundleSha256: metadata.bundleSha256 };
    trainerWrite(directory, `active/${projectId}/${metadata.targetKind}/${trainerId(metadata.targetId)}.json`, trainerJson(pointer), { replace: true });
    return pointer;
  });
}
export function loadReleaseBundle(root, { projectId, releaseId, targetKind, targetId }) {
  let pointer;
  if (!releaseId) {
    if (!['agent', 'workflow'].includes(targetKind)) trainerFail('TRAINER_RELEASE_TARGET', 'active release requires target kind');
    pointer = trainerRead(releaseRoot(root), 'active', trainerId(projectId), targetKind, `${trainerId(targetId)}.json`); releaseId = pointer.releaseId;
  }
  const { bundle } = readRelease(root, projectId, releaseId);
  if ((targetKind && bundle.targetKind !== targetKind) || (targetId && bundle.targetId !== targetId) || (pointer && pointer.bundleSha256 !== bundle.bundleSha256)) trainerFail('TRAINER_RELEASE_TARGET', 'active release target or digest mismatch');
  return bundle;
}
export function listReleases(root, { projectId }) {
  trainerId(projectId); const directory = releaseRoot(root); const versions = trainerSafe(directory, 'versions'); const releases = []; const active = [];
  if (fs.existsSync(versions)) for (const name of fs.readdirSync(versions).filter((n) => n.startsWith('release-')).sort()) {
    const manifest = trainerSafe(versions, name, 'release.json'); if (!fs.existsSync(manifest)) continue;
    const meta = trainerRead(versions, name, 'release.json'); if (meta.projectId === projectId) {
      const loaded = readRelease(root, projectId, name); const contaminatedRefs = syntheticInstructionRefs(loaded.bundle);
      releases.push({ ...loaded.metadata, createdAt: loaded.metadata.createdAt ?? null, sequence: loaded.metadata.sequence ?? null,
        contaminated: contaminatedRefs.length > 0, contaminatedRefs });
    }
  }
  releases.sort((a, b) => (Number.isSafeInteger(a.sequence) ? 0 : 1) - (Number.isSafeInteger(b.sequence) ? 0 : 1)
    || (Number.isSafeInteger(b.sequence) ? b.sequence - a.sequence : a.releaseId.localeCompare(b.releaseId)));
  for (const kind of ['agent', 'workflow']) {
    const pointers = trainerSafe(directory, 'active', projectId, kind);
    if (fs.existsSync(pointers)) for (const name of fs.readdirSync(pointers).filter((n) => n.endsWith('.json')).sort()) {
      const pointer = trainerRead(pointers, name); loadReleaseBundle(root, { projectId, targetKind: kind, targetId: name.slice(0, -5) }); active.push(pointer);
    }
  }
  return { projectId, releases, active };
}
