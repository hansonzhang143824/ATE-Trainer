import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { readWorkflowTemplateRun } from './workflow-template-run.js';
import { loadFrozenWorkflowTemplate } from './workflow-template.js';

const SHA = /^[a-f0-9]{64}$/;
const ID = /^[a-z0-9][a-z0-9-]{1,127}$/;
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const json = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
function safe(root, ...parts) {
  const target = path.isAbsolute(parts[0]) ? path.join(...parts) : path.join(root, ...parts);
  return assertSafeRunPath(root, target);
}
function releaseFile(root, releaseId) {
  if (typeof releaseId !== 'string' || !ID.test(releaseId) || !releaseId.startsWith('workflow-release-')) {
    throw new Error('invalid workflow release ID');
  }
  return safe(root, 'publish', 'workflow-templates', 'versions', releaseId, 'manifest.json');
}
function pointerFile(root) { return safe(root, 'publish', 'workflow-templates', 'active.json'); }
function sourceBindings(root, record) {
  return record.steps.map(step => {
    const base = safe(root, 'Training_Materials', 'runs', step.profileRunId);
    const snapshot = safe(root, base, 'profile', 'snapshot.json');
    const raw = fs.readFileSync(snapshot);
    const evidence = read(assertSafeRunPath(root, step.evidencePath));
    if (hash(raw) !== evidence.profileSnapshotSha256 || !SHA.test(step.evidenceSha256)) {
      throw new Error(`Agent snapshot or evidence changed: ${step.profileId}`);
    }
    return { profileId: step.profileId, profileRunId: step.profileRunId,
      profileSnapshotSha256: hash(raw), childEvidenceSha256: step.evidenceSha256,
      upstreamEvidenceSha256: step.upstreamEvidenceSha256 };
  });
}
function verifySources(root, manifest) {
  const record = readWorkflowTemplateRun(root, manifest.sourceRunId);
  if (record.status !== 'completed' || record.smokePassed !== true
      || record.templateId !== manifest.templateId || record.templateSha256 !== manifest.templateSha256) {
    throw new Error('workflow release source run is no longer verified');
  }
  const source = safe(root, 'Training_Materials', 'workflow-runs', record.runId, 'state.json');
  if (hash(fs.readFileSync(source)) !== manifest.sourceRunSha256) throw new Error('workflow release source record changed');
  const bindings = sourceBindings(root, record);
  if (JSON.stringify(bindings) !== JSON.stringify(manifest.steps)) throw new Error('workflow release Agent bindings changed');
  loadFrozenWorkflowTemplate(root, manifest.templateId, manifest.templateSha256);
}

/** Stage a diagnostic-only release from a fully verified arbitrary workflow. */
export function stageWorkflowTemplateRelease(workspaceRoot, runId) {
  const root = path.resolve(workspaceRoot);
  const record = readWorkflowTemplateRun(root, runId);
  if (record.status !== 'completed' || record.smokePassed !== true) throw new Error('only a completed smoke workflow can be released');
  const source = safe(root, 'Training_Materials', 'workflow-runs', runId, 'state.json');
  const releaseId = `workflow-release-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${crypto.randomUUID().slice(0, 8)}`;
  const file = releaseFile(root, releaseId);
  const manifest = { schemaVersion: 1, kind: 'ptc-workflow-template-smoke-release', releaseId,
    templateId: record.templateId, templateSha256: record.templateSha256,
    sourceRunId: runId, sourceRunSha256: hash(fs.readFileSync(source)),
    steps: sourceBindings(root, record), mode: 'SMOKE_ONLY', outputUse: 'diagnostic-only',
    businessGatePassed: false, createdAt: new Date().toISOString() };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, json(manifest), { flag: 'wx' });
  return { releaseId, manifestSha256: hash(fs.readFileSync(file)), status: 'frozen',
    businessGatePassed: false };
}

export function loadWorkflowTemplateRelease(workspaceRoot, releaseId = null) {
  const root = path.resolve(workspaceRoot);
  const pointer = releaseId === null ? read(pointerFile(root)) : null;
  const id = releaseId ?? pointer?.releaseId;
  const file = releaseFile(root, id);
  const raw = fs.readFileSync(file);
  const digest = hash(raw);
  if (pointer && (pointer.manifestSha256 !== digest || pointer.releaseId !== id)) {
    throw new Error('active workflow release pointer changed');
  }
  const manifest = JSON.parse(raw.toString('utf8'));
  if (manifest.schemaVersion !== 1 || manifest.kind !== 'ptc-workflow-template-smoke-release'
      || manifest.releaseId !== id || manifest.mode !== 'SMOKE_ONLY'
      || manifest.outputUse !== 'diagnostic-only' || manifest.businessGatePassed !== false
      || !Array.isArray(manifest.steps) || manifest.steps.length < 1) {
    throw new Error('invalid workflow release manifest');
  }
  verifySources(root, manifest);
  return { manifest, manifestSha256: digest, activatedAt: pointer?.activatedAt ?? null };
}

export function activateWorkflowTemplateRelease(workspaceRoot, releaseId, expectedManifestSha256) {
  const root = path.resolve(workspaceRoot);
  if (!SHA.test(expectedManifestSha256 ?? '')) throw new Error('release manifest SHA-256 required');
  const release = loadWorkflowTemplateRelease(root, releaseId);
  if (release.manifestSha256 !== expectedManifestSha256) throw new Error('workflow release changed before activation');
  const file = pointerFile(root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const value = { schemaVersion: 1, releaseId, manifestSha256: expectedManifestSha256,
    activatedAt: new Date().toISOString() };
  const temporary = assertSafeRunPath(root, `${file}.${crypto.randomUUID()}.tmp`);
  fs.writeFileSync(temporary, json(value), { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
  return value;
}
