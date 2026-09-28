import fs from 'node:fs';
import path from 'node:path';
import { listFrameworkReleases, verifyFrameworkRuntimeCompatibility } from './framework-release.js';
import { readFrameworkPublishedRun } from './framework-published-run.js';
import { loadTrainingRelease } from './training-release.js';
import { readWorkflowTemplateRun } from './workflow-template-run.js';
import { loadWorkflowTemplateRelease } from './workflow-template-release.js';
import { readPublishedWorkflowRun } from './workflow-template-published.js';

const readJson = (file) => {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
  } catch {
    return undefined;
  }
};

const modifiedMs = (file) => {
  try {
    return fs.statSync(file).mtimeMs;
  } catch {
    return 0;
  }
};

function newestJson(directory) {
  let files;
  try {
    files = fs.readdirSync(directory)
      .filter((name) => name.endsWith('.json'))
      .map((name) => path.join(directory, name))
      .sort((left, right) => modifiedMs(right) - modifiedMs(left));
  } catch {
    return undefined;
  }
  for (const file of files) {
    const value = readJson(file);
    if (value !== undefined) return { file, value };
  }
  return undefined;
}

function listProfiles(workspaceRoot) {
  const root = path.join(workspaceRoot, 'team', 'expert-profiles');
  let names;
  try {
    names = fs.readdirSync(root, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort();
  } catch {
    return [];
  }
  return names.map((profileId) => {
    const status = readJson(path.join(root, profileId, 'status.json')) ?? {};
    return {
      profileId,
      publishedVersion: typeof status.publishedVersion === 'string' ? status.publishedVersion : null,
      manifestDigest: typeof status.manifestDigest === 'string' ? status.manifestDigest : null,
      draftVerdict: typeof status.draftVerdict === 'string' ? status.draftVerdict : null,
    };
  });
}

function listTrainingRuns(workspaceRoot, limit = 100) {
  const root = path.join(workspaceRoot, 'Training_Materials', 'runs');
  let entries;
  try {
    entries = fs.readdirSync(root, { withFileTypes: true }).filter((entry) => entry.isDirectory());
  } catch {
    return [];
  }
  return entries.map((entry) => {
    const directory = path.join(root, entry.name);
    const runFile = path.join(directory, 'run.json');
    const run = readJson(runFile) ?? {};
    const stateFile = path.join(directory, 'state.json');
    const state = readJson(stateFile) ?? {};
    const pipelineFile = path.join(directory, 'pipeline-progress.json');
    const progress = readJson(pipelineFile);
    const pipeline = progress?.runId === entry.name ? progress : null;
    const simple = readJson(path.join(directory, 'simple-orchestration.json'));
    const purpose = state.purpose ?? 'business-training';
    const materialManifest = purpose === 'business-training' && state.target?.kind === 'pipeline'
      ? readJson(path.join(directory, 'pipeline-material-manifest.json')) : null;
    const issueOwners = materialManifest?.runId === entry.name && Array.isArray(pipeline?.sourceRoles)
      && materialManifest.ownerProfiles && typeof materialManifest.ownerProfiles === 'object'
      ? [...new Set(pipeline.sourceRoles)].filter(sourceRole => typeof sourceRole === 'string')
        .map(sourceRole => ({ sourceRole, profileId: materialManifest.ownerProfiles[sourceRole] }))
        .filter(owner => typeof owner.profileId === 'string' && owner.profileId.length > 0)
      : [];
    return {
      runId: entry.name,
      mode: run.mode ?? 'training',
      status: state.status ?? pipeline?.status ?? 'unknown',
      target: state.target ?? run.target ?? null,
      purpose,
      issueOwners,
      modelChoice: state.modelChoice ?? null,
      testItems: Array.isArray(state.testItems) ? state.testItems : Array.isArray(pipeline?.testItems) ? pipeline.testItems : [],
      outcome: state.outcome ?? null,
      error: typeof state.error === 'string' ? state.error : null,
      artifactRoot: run.artifactRoot ?? null,
      lifecycle: readJson(path.join(directory, 'evidence', 'lifecycle.json')) ?? null,
      pipeline,
      simpleOrchestration: simple?.runId === entry.name ? simple : null,
      updatedAt: new Date(Math.max(modifiedMs(runFile), modifiedMs(stateFile), modifiedMs(pipelineFile), modifiedMs(directory))).toISOString(),
    };
  }).sort((left, right) => right.updatedAt.localeCompare(left.updatedAt)).slice(0, limit);
}

function activeRelease(workspaceRoot) {
  const pointer = readJson(path.join(workspaceRoot, 'team', 'ptc', 'releases', 'active-release.json'));
  if (pointer === undefined) return null;
  return {
    releaseId: typeof pointer.releaseId === 'string' ? pointer.releaseId : null,
    manifestDigest: typeof pointer.bundleDigest === 'string' ? pointer.bundleDigest : typeof pointer.manifestDigest === 'string' ? pointer.manifestDigest : null,
    activatedAt: typeof pointer.activatedAt === 'string' ? pointer.activatedAt : null,
  };
}

function latestDelivery(workspaceRoot) {
  const latest = newestJson(path.join(workspaceRoot, 'team', 'artifacts', 'ptc-batches'));
  if (latest === undefined) return null;
  const batch = latest.value;
  return {
    batchId: batch.batchId ?? path.basename(latest.file, '.json'),
    state: batch.state ?? batch.stage ?? null,
    releaseId: batch.releaseId ?? null,
    executionScope: batch.executionScope ?? null,
    updatedAt: new Date(modifiedMs(latest.file)).toISOString(),
  };
}

function listPublishedFrameworkRuns(workspaceRoot, limit = 20) {
  const directory = path.join(workspaceRoot, 'Published_Materials', 'framework-runs');
  let names;
  try { names = fs.readdirSync(directory, { withFileTypes: true }).filter(entry => entry.isDirectory()).map(entry => entry.name); }
  catch { return []; }
  return names.map(runId => {
    try { return readFrameworkPublishedRun({ workspaceRoot, runId }); }
    catch (error) { return { runId, status: 'blocked', reason: `持久化运行记录校验失败：${error.message}` }; }
  }).sort((left, right) => String(right.updatedAt ?? '').localeCompare(String(left.updatedAt ?? ''))).slice(0, limit);
}

function listWorkflowTemplateRuns(workspaceRoot, limit = 20) {
  const directory = path.join(workspaceRoot, 'Training_Materials', 'workflow-runs');
  let names;
  try { names = fs.readdirSync(directory, { withFileTypes: true })
    .filter(entry => entry.isDirectory()).map(entry => entry.name); }
  catch { return []; }
  return names.map(runId => {
    try { return readWorkflowTemplateRun(workspaceRoot, runId); }
    catch (error) { return { runId, status: 'blocked', reason: `工作流记录校验失败：${error.message}` }; }
  }).sort((left, right) => String(right.updatedAt ?? '').localeCompare(String(left.updatedAt ?? ''))).slice(0, limit);
}

function listPublishedWorkflowTemplateRuns(workspaceRoot, limit = 20) {
  const directory = path.join(workspaceRoot, 'publish', 'workflow-templates', 'runs');
  let names;
  try { names = fs.readdirSync(directory, { withFileTypes: true })
    .filter(entry => entry.isDirectory()).map(entry => entry.name); }
  catch { return []; }
  return names.map(runId => {
    try { return readPublishedWorkflowRun(workspaceRoot, runId); }
    catch (error) { return { runId, status: 'blocked', reason: `发布运行记录校验失败：${error.message}` }; }
  }).sort((left, right) => String(right.updatedAt ?? '').localeCompare(String(left.updatedAt ?? ''))).slice(0, limit);
}

/**
 * Read-only state for the native DSH control surface.
 *
 * `identity` is deliberately `unbound` here: mode belongs to an immutable run
 * context, never to this process-wide state response. A later session-scoped
 * endpoint will expose the caller's concrete training or delivery identity.
 */
export function buildControlState(workspaceRoot) {
  const legacyBindings = readJson(path.join(workspaceRoot, 'Training_Materials', '_expert_bindings.json'));
  const registry = readJson(path.join(workspaceRoot, 'team', 'ptc', 'ptc_stage_registry.json'));
  let frameworkRelease = { active: null, releases: [] };
  let frameworkReleaseError = null;
  let trainingRelease = null;
  let trainingReleaseError = null;
  let activeWorkflowTemplateRelease = null;
  let workflowTemplateReleaseError = null;
  const trainingPointer = readJson(path.join(workspaceRoot, 'publish', 'active-release.json'));
  try { trainingRelease = loadTrainingRelease({ workspaceRoot }); }
  catch (error) {
    if (!String(error.message).includes('no active smoke training release')) trainingReleaseError = error.message;
  }
  try {
    const release = loadWorkflowTemplateRelease(workspaceRoot);
    activeWorkflowTemplateRelease = { releaseId: release.manifest.releaseId,
      templateId: release.manifest.templateId, manifestSha256: release.manifestSha256,
      activatedAt: release.activatedAt };
  } catch (error) {
    if (fs.existsSync(path.join(workspaceRoot, 'publish', 'workflow-templates', 'active.json'))) {
      workflowTemplateReleaseError = String(error.message ?? error);
    }
  }
  let publishedSmokeRuns = [];
  try {
    const directory = path.join(workspaceRoot, 'publish', 'runs');
    publishedSmokeRuns = fs.readdirSync(directory, { withFileTypes: true })
      .filter(entry => entry.isDirectory()).map(entry => {
        const state = readJson(path.join(directory, entry.name, 'state.json'));
        return state?.runId === entry.name ? state : { runId: entry.name, status: 'blocked',
          reason: '发布态运行记录缺失或身份不符' };
      }).sort((left, right) => String(right.updatedAt ?? '').localeCompare(String(left.updatedAt ?? ''))).slice(0, 20);
  } catch { /* No published smoke runs yet. */ }
  try {
    frameworkRelease = listFrameworkReleases({ workspaceRoot });
    if (frameworkRelease.active) verifyFrameworkRuntimeCompatibility({ workspaceRoot });
  }
  catch (error) { frameworkReleaseError = error.message; }
  return {
    schemaVersion: 1,
    identity: 'unbound',
    activeRelease: activeRelease(workspaceRoot),
    activeTrainingRelease: trainingRelease ? {
      releaseId: trainingRelease.manifest.releaseId,
      manifestDigest: trainingRelease.manifest.bundleDigest,
      activatedAt: trainingPointer?.activatedAt ?? null,
    } : null,
    trainingReleaseError,
    activeWorkflowTemplateRelease,
    workflowTemplateReleaseError,
    publishedWorkflowTemplateRuns: listPublishedWorkflowTemplateRuns(workspaceRoot),
    publishedSmokeRuns,
    activeFrameworkRelease: frameworkRelease.active ? {
      releaseId: frameworkRelease.active.releaseId,
      bundleDigest: frameworkRelease.active.bundleDigest,
      activatedAt: frameworkRelease.active.activatedAt,
      sourceRunId: frameworkRelease.releases.find(entry => entry.releaseId === frameworkRelease.active.releaseId)?.manifest?.sourceRunId ?? null,
    } : null,
    frameworkReleaseError,
    publishedFrameworkRuns: listPublishedFrameworkRuns(workspaceRoot),
    trainingRuns: listTrainingRuns(workspaceRoot),
    workflowTemplateRuns: listWorkflowTemplateRuns(workspaceRoot),
    delivery: latestDelivery(workspaceRoot),
    profiles: listProfiles(workspaceRoot),
    pipelineStages: Array.isArray(registry?.stateMachine)
      ? registry.stateMachine.filter(stage => typeof stage === 'string' && stage !== 'COMPLETE' && typeof registry.stages?.[stage]?.gate === 'string') : [],
    migration: {
      legacyConsoleAbandoned: true,
      legacyMode: legacyBindings?.activeMode ?? null,
      legacyModeAuthoritative: false,
    },
  };
}
