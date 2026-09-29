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

const BUSINESS_AGENT_CATALOG = Object.freeze({
  'ptc-dft-expert': {
    kind: 'dft',
    displayName: 'DFT Expert',
    inputs: [
      'Training_Materials/runs/<runId>/input/Dali_testmode.xlsx',
      'Training_Materials/runs/<runId>/input/DALI-special-information.json',
      'Training_Materials/runs/<runId>/input/DFT解析规则.txt',
      'Training_Materials/runs/<runId>/profile/instructions.md',
      'Training_Materials/runs/<runId>/profile/profile.yaml',
      'Training_Materials/runs/<runId>/profile/output-contract.schema.json',
    ],
    outputs: [
      'Training_Materials/runs/<runId>/input-sync/dft/<TM>/dft-meta.json',
      'Training_Materials/runs/<runId>/input-sync/dft/<TM>/dft-conditions.yaml',
      'Training_Materials/runs/<runId>/input-sync/dft/<TM>/dft-semantic-review.json',
      'Training_Materials/runs/<runId>/evidence/dft-terminal.json',
    ],
    skills: [
      'team/expert-profiles/ptc-dft-expert/instructions.md',
      'team/expert-profiles/ptc-dft-expert/profile.yaml',
      'team/expert-profiles/ptc-dft-expert/output-contract.schema.json',
    ],
    scripts: [
      'scripts/hash_ate_plaintext.py', 'scripts/training_dft_source_view.py',
      'scripts/refresh_dft_meta_from_source.py', 'scripts/render_dft_conditions_yaml.py',
      'scripts/training_dft_review_input.py', 'scripts/write_dft_semantic_review.py',
      'scripts/validate_dft_outputs.py',
    ],
  },
  'ptc-schematic-expert': {
    kind: 'schematic',
    displayName: 'Schematic Expert',
    inputs: [
      'Training_Materials/runs/<runId>/input/Dali-SCH.csv',
      'Training_Materials/runs/<runId>/input/sch_confirmed.json',
      'Training_Materials/runs/<runId>/input/CBIT表-DALI.xlsx',
      'Training_Materials/runs/<runId>/profile/instructions.md',
      'Training_Materials/runs/<runId>/profile/profile.yaml',
      'Training_Materials/runs/<runId>/profile/output-contract.schema.json',
    ],
    outputs: [
      'Training_Materials/runs/<runId>/input-sync/schematic/SCH-Connect-Map.txt',
      'Training_Materials/runs/<runId>/input-sync/schematic/SCH-Connect-Map.json',
      'Training_Materials/runs/<runId>/input-sync/schematic/Component-Statistic.txt',
      'Training_Materials/runs/<runId>/input-sync/schematic/Components-Statistic.json',
      'Training_Materials/runs/<runId>/input-sync/schematic/Path-Proofs.txt',
      'Training_Materials/runs/<runId>/input-sync/schematic/Path-Proofs.json',
      'Training_Materials/runs/<runId>/input-sync/schematic/schematic-receipt.json',
      'Training_Materials/runs/<runId>/evidence/pipeline-INPUT_SYNC.json',
    ],
    skills: [
      'team/expert-profiles/ptc-schematic-expert/instructions.md',
      'team/expert-profiles/ptc-schematic-expert/profile.yaml',
      'team/expert-profiles/ptc-schematic-expert/output-contract.schema.json',
    ],
    scripts: [
      'scripts/hash_ate_plaintext.py', 'scripts/training_schematic.py',
      'scripts/generate_schematic_txt.py', 'scripts/validate_schematic_outputs.py',
    ],
  },
});

function listBusinessAgentCatalog(workspaceRoot, runs) {
  // Active product starts empty; legacy expert profiles remain archive-only.
  const catalog = {};
  const profilesRoot = path.join(workspaceRoot, 'team', 'expert-profiles');
  try {
    for (const entry of fs.readdirSync(profilesRoot, { withFileTypes: true })) {
      if (!entry.isDirectory() || catalog[entry.name]) continue;
      const profileFile = path.join(profilesRoot, entry.name, 'profile.yaml');
      const text = (() => { try { return fs.readFileSync(profileFile, 'utf8'); } catch { return ''; } })();
      const owner = /^ownerRole\s*:\s*([^#\r\n]+)/mi.exec(text)?.[1]?.trim();
      const displayName = /^displayName\s*:\s*([^#\r\n]+)/mi.exec(text)?.[1]?.trim() || entry.name;
      if (owner === 'dft-expert' && (!/^executionClass\s*:\s*input-dft/m.test(text)
          || !/^executionAdapter\s*:\s*ptc-dft/m.test(text)
          || !/^capabilityContract\s*:\s*ptc-dft-business-v1/m.test(text))) continue;
      const base = owner === 'dft-expert' ? BUSINESS_AGENT_CATALOG['ptc-dft-expert']
        : owner === 'schematic-expert' ? BUSINESS_AGENT_CATALOG['ptc-schematic-expert'] : null;
      if (base) catalog[entry.name] = { ...base, kind: base.kind, displayName, skills: base.skills.map(item => item.replace(/ptc-(?:dft|schematic)-expert/, entry.name)) };
    }
  } catch { /* an empty profile catalog is rendered as no available Agent */ }
  return Object.entries(catalog).map(([profileId, definition]) => {
    const isDft = definition.kind === 'dft';
    const isSchematic = !isDft;
    const candidates = runs.filter(run => run.purpose === 'business-training' && (
      (run.target?.kind === 'profile' && run.target.profileId === profileId)
      || (run.target?.kind === 'pipeline' && run.issueOwners?.some(owner => owner.profileId === profileId))
      || (profileId === 'ptc-dft-expert' && run.target?.kind === 'pipeline' && run.target.fromStage === 'INPUT_SYNC')
      || (profileId === 'ptc-schematic-expert' && run.target?.kind === 'pipeline' && run.target.fromStage === 'INPUT_SYNC')));
    const latest = candidates[0] ?? null;
    const runId = latest?.runId ?? null;
    const runRoot = runId ? path.join(workspaceRoot, 'Training_Materials', 'runs', runId) : null;
    const hasEvidence = relative => Boolean(runRoot && fs.existsSync(path.join(runRoot, relative)));
    const hasAnyEvidence = (...relativePaths) => relativePaths.some(hasEvidence);
    const used = isDft
      ? Boolean(latest && (latest.target?.kind === 'profile'
        ? hasAnyEvidence('evidence/dft-terminal.json', 'evidence/dft-preflight.json', 'evidence/dft-review-input.json')
        : hasAnyEvidence('evidence/pipeline-INPUT_SYNC-dft.json', 'evidence/pipeline-INPUT_SYNC-dft-child.json', 'evidence/dft-review-input.json')))
      : Boolean(latest && hasAnyEvidence('evidence/pipeline-INPUT_SYNC-schematic.json', 'evidence/INPUT_SYNC-schematic-expert-lifecycle.json', 'input-sync/schematic/schematic-receipt.json'));
    const outputs = isDft && latest?.target?.kind === 'pipeline'
      ? definition.outputs.map(pathname => pathname.endsWith('/evidence/dft-terminal.json')
        ? pathname.replace('/evidence/dft-terminal.json', '/evidence/pipeline-INPUT_SYNC-dft.json') : pathname) : definition.outputs;
    return { profileId, kind: definition.kind, displayName: definition.displayName, latestRunId: runId, latestRunStatus: latest?.status ?? null,
      inputs: definition.inputs.map(pathname => ({ path: pathname, used })), outputs: outputs.map(pathname => ({ path: pathname, used })),
      skills: definition.skills.map(pathname => ({ path: pathname, used })), scripts: definition.scripts.map(pathname => ({ path: pathname, used })) };
  });
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
  const trainingRuns = listTrainingRuns(workspaceRoot);
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
    trainingRuns,
    businessAgents: listBusinessAgentCatalog(workspaceRoot, trainingRuns),
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
