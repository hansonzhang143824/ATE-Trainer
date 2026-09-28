/**
 * PTC control-plane client: shared read-only state store.
 *
 * Same-origin endpoint (registered by the plugin's lib/index.js):
 *   GET /api/ptc-control/state
 *
 * Server contract (lib/control-state.js buildControlState, schemaVersion 1):
 * {
 *   "schemaVersion": 1,
 *   "identity": "unbound",
 *   "activeRelease": { "releaseId": string|null, "manifestDigest": string|null, "activatedAt": string|null } | null,
 *   "trainingRuns": [ { "runId": string, "mode": string, "status": string, "target": Target|null, "updatedAt": string } ],
 *   "delivery": { "batchId": string, "state": string|null, "releaseId": string|null, "executionScope": string|null, "updatedAt": string } | null,
 *   "profiles": [ { "profileId": string, "publishedVersion": string|null, "manifestDigest": string|null, "draftVerdict": string|null } ],
 *   "migration": { "legacyConsoleAbandoned": boolean, "legacyMode": string|null, "legacyModeAuthoritative": boolean }
 * }
 *
 * Target (from the run's state.json) is an object or null:
 *   { "kind": "profile", "profileId": string }
 *   { "kind": "pipeline", "fromStage": string, "toStage": string, "stages": string[] }
 * The client preserves the object and renders it as the profileId or the
 * stage range (see formatTarget).
 *
 * The store follows the React useSyncExternalStore contract so the panel can
 * subscribe without extra state plumbing. It never mutates host state.
 */

const STATE_URL = "/api/ptc-control/state";
const CREATE_TRAINING_URL = "/api/ptc-control/training-runs";
const EXECUTE_TRAINING_URL = "/api/ptc-control/training-runs/execute";
const EXECUTE_BUSINESS_TRAINING_URL = "/api/ptc-control/business/training-runs/execute";
const STOP_TRAINING_URL = "/api/ptc-control/training-runs/stop";
const EXECUTE_PIPELINE_URL = "/api/ptc-control/training-pipelines/execute";
const CONTROL_PIPELINE_URL = "/api/ptc-control/training-pipelines/control";
const EXECUTE_BUSINESS_PIPELINE_URL = "/api/ptc-control/business/training-pipelines/execute";
const CONTROL_BUSINESS_PIPELINE_URL = "/api/ptc-control/business/training-pipelines/control";
const EXECUTE_REHEARSAL_URL = "/api/ptc-control/framework-rehearsals/execute";
const CONTROL_REHEARSAL_URL = "/api/ptc-control/framework-rehearsals/control";
const PUBLISH_FRAMEWORK_URL = "/api/ptc-control/framework-releases/publish";
const RECOVER_REHEARSAL_URL = "/api/ptc-control/framework-rehearsals/recover";
const EXECUTE_PUBLISHED_FRAMEWORK_URL = "/api/ptc-control/framework-releases/execute";
const CONTROL_PUBLISHED_FRAMEWORK_URL = "/api/ptc-control/framework-releases/control";
const EXECUTE_PROFILE_SMOKE_URL = '/api/ptc-control/profile-smoke/execute';
const STOP_PROFILE_SMOKE_URL = '/api/ptc-control/profile-smoke/stop';
const EXECUTE_SIMPLE_ORCHESTRATION_URL = '/api/ptc-control/simple-orchestration/execute';
const CONTROL_SIMPLE_ORCHESTRATION_URL = '/api/ptc-control/simple-orchestration/control';
const PUBLISH_TRAINING_RELEASE_URL = '/api/ptc-control/training-release/publish';
const EXECUTE_TRAINING_RELEASE_URL = '/api/ptc-control/training-release/execute';
const CONTROL_TRAINING_RELEASE_URL = '/api/ptc-control/training-release/control';
const SESSION_WORKSPACE_URL = '/api/ptc-control/session-workspace';
const WORKFLOW_TEMPLATE_URL = '/api/ptc-control/workflow-templates';
const WORKFLOW_TEMPLATE_RELEASE_URL = '/api/ptc-control/workflow-template-releases';
const FREEZE_TRAINING_RELEASE_URL = '/api/ptc-control/training-release/freeze';
const ACTIVATE_TRAINING_RELEASE_URL = '/api/ptc-control/training-release/activate';
const DEFAULT_POLL_MS = 5000;
const SUPPORTED_SCHEMA_VERSION = 1;

export async function createTrainingRunRequest(target, options = {}) {
  const url = options.url ?? CREATE_TRAINING_URL;
  const fetchImpl = options.fetchImpl ?? fetch;
  const response = await fetchImpl(url, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify({ target, ...(options.purpose ? { purpose: options.purpose } : {}) })
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  }
  return body;
}

export async function executeTrainingRunRequest(runId, testItems, options = {}) {
  const url = options.url ?? EXECUTE_TRAINING_URL;
  const fetchImpl = options.fetchImpl ?? fetch;
  const response = await fetchImpl(url, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify({ runId, testItems, ...(options.modelChoice ? { modelChoice: options.modelChoice } : {}) })
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  }
  return body;
}

export function executeBusinessTrainingRunRequest(runId, testItems, options = {}) {
  return executeTrainingRunRequest(runId, testItems, {
    ...options, url: options.url ?? EXECUTE_BUSINESS_TRAINING_URL,
  });
}

export async function stopTrainingRunRequest(runId, options = {}) {
  const response = await (options.fetchImpl ?? fetch)(options.url ?? STOP_TRAINING_URL, {
    method: "POST", headers: { Accept: "application/json", "Content-Type": "application/json" },
    credentials: "same-origin", body: JSON.stringify({ runId })
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
  return body;
}

export async function executeTrainingPipelineRequest(runId, testItems, options = {}) {
  const url = options.url ?? EXECUTE_PIPELINE_URL;
  const response = await (options.fetchImpl ?? fetch)(url, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify({ runId, testItems, ...(options.modelChoice ? { modelChoice: options.modelChoice } : {}) }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  return body;
}

export function executeBusinessPipelineRequest(runId, testItems, options = {}) {
  return executeTrainingPipelineRequest(runId, testItems, {
    ...options, url: options.url ?? EXECUTE_BUSINESS_PIPELINE_URL,
  });
}

export function executeFrameworkRehearsalRequest(runId, testItems, options = {}) {
  return executeTrainingRunRequest(runId, testItems, { ...options, url: options.url ?? EXECUTE_REHEARSAL_URL });
}

export async function controlTrainingPipelineRequest(runId, action, options = {}) {
  if (!['pause', 'resume', 'stop'].includes(action)) throw new Error('不支持的流程控制操作');
  const url = options.url ?? CONTROL_PIPELINE_URL;
  const response = await (options.fetchImpl ?? fetch)(url, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: JSON.stringify({ runId, action }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  return body;
}

export function controlBusinessPipelineRequest(runId, action, options = {}) {
  return controlTrainingPipelineRequest(runId, action, {
    ...options, url: options.url ?? CONTROL_BUSINESS_PIPELINE_URL,
  });
}


export function controlFrameworkRehearsalRequest(runId, action, options = {}) {
  return controlTrainingPipelineRequest(runId, action, { ...options, url: options.url ?? CONTROL_REHEARSAL_URL });
}

export async function publishFrameworkReleaseRequest(sourceRunId, options = {}) {
  const url = options.url ?? PUBLISH_FRAMEWORK_URL;
  const response = await (options.fetchImpl ?? fetch)(url, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: JSON.stringify({ sourceRunId }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  return body;
}

export async function recoverFrameworkRehearsalRequest(runId, options = {}) {
  const url = options.url ?? RECOVER_REHEARSAL_URL;
  const response = await (options.fetchImpl ?? fetch)(url, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: JSON.stringify({ runId }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  return body;
}

export async function executePublishedFrameworkRequest(options = {}) {
  const url = options.url ?? EXECUTE_PUBLISHED_FRAMEWORK_URL;
  const response = await (options.fetchImpl ?? fetch)(url, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: '{}',
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  return body;
}

export async function controlPublishedFrameworkRequest(runId, action, options = {}) {
  if (!['pause', 'resume', 'stop'].includes(action)) throw new Error('不支持的发布流程操作');
  const url = options.url ?? CONTROL_PUBLISHED_FRAMEWORK_URL;
  const response = await (options.fetchImpl ?? fetch)(url, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: JSON.stringify({ runId, action }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
  return body;
}

async function postSmoke(url, body, options = {}) {
  const response = await (options.fetchImpl ?? fetch)(options.url ?? url, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: JSON.stringify(body),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail ?? payload.error ?? `POST ${url} failed with HTTP ${response.status}`);
  return payload;
}

export function executeProfileSmokeRequest(runId, options = {}) {
  return postSmoke(EXECUTE_PROFILE_SMOKE_URL, { runId }, options);
}

export function stopProfileSmokeRequest(runId, options = {}) {
  return postSmoke(STOP_PROFILE_SMOKE_URL, { runId }, options);
}

export function executeSimpleOrchestrationRequest(runId, profileRunIds, options = {}) {
  return postSmoke(EXECUTE_SIMPLE_ORCHESTRATION_URL, {
    runId, testItems: ['TM109'], profileRunIds, ...(options.pilot ? { pilot: true } : {}),
  }, options);
}

export function controlSimpleOrchestrationRequest(runId, action, options = {}) {
  if (!['pause', 'resume', 'stop'].includes(action)) throw new Error('不支持的 smoke 流程控制操作');
  return postSmoke(CONTROL_SIMPLE_ORCHESTRATION_URL, { runId, action }, options);
}

export function publishTrainingReleaseRequest(profileRunIds, pipelineRunId, options = {}) {
  return postSmoke(PUBLISH_TRAINING_RELEASE_URL, { profileRunIds, pipelineRunId }, options);
}

export function freezeTrainingReleaseRequest(profileRunIds, pipelineRunId, options = {}) {
  return postSmoke(FREEZE_TRAINING_RELEASE_URL, { profileRunIds, pipelineRunId }, options);
}

export function activateTrainingReleaseRequest(stagingId, options = {}) {
  return postSmoke(ACTIVATE_TRAINING_RELEASE_URL, { stagingId }, options);
}

export function executeTrainingReleaseRequest(options = {}) {
  return postSmoke(EXECUTE_TRAINING_RELEASE_URL, { testItems: ['TM109'] }, options);
}

export async function createPtcSessionWorkspaceRequest(input, options = {}) {
  const response = await (options.fetchImpl ?? fetch)(options.url ?? SESSION_WORKSPACE_URL, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: JSON.stringify(input),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${SESSION_WORKSPACE_URL} failed with HTTP ${response.status}`);
  if (typeof body.path !== 'string' || !body.path) throw new Error('服务器未返回安全的会话工作区路径');
  return body;
}

export function workflowTemplateRequest(action, input, options = {}) {
  if (!['read', 'save', 'freeze', 'execute', 'control'].includes(action)) {
    throw new Error('unsupported workflow template action');
  }
  return postSmoke(`${WORKFLOW_TEMPLATE_URL}/${action}`, input, options);
}

export function workflowTemplateReleaseRequest(action, input, options = {}) {
  if (!['stage', 'activate', 'read', 'execute', 'control'].includes(action)) {
    throw new Error('unsupported workflow template release action');
  }
  return postSmoke(`${WORKFLOW_TEMPLATE_RELEASE_URL}/${action}`, input, options);
}

export function controlTrainingReleaseRequest(runId, action, options = {}) {
  if (action !== 'stop') throw new Error('发布态 smoke 仅支持停止');
  return postSmoke(CONTROL_TRAINING_RELEASE_URL, { runId, action }, options);
}

export function parseTrainingTestItems(value) {
  const items = typeof value === 'string' ? value.trim().toUpperCase().split(/[,，、\s]+/).filter(Boolean) : [];
  if (!items.length || items.some(item => !/^TM[0-9]+$/.test(item))) throw new Error('请输入 TM 编号列表，例如 TM109,TM110；不支持范围或自由文本');
  return [...new Set(items)];
}

export function pipelineTrainingTarget(stages, fromStage, toStage) {
  const start = stages.indexOf(fromStage);
  const end = stages.indexOf(toStage);
  if (start < 0 || end < start) throw new Error('请选择有效的流程起止阶段');
  return { kind: 'pipeline', fromStage, toStage };
}

export function pipelineControlActions(status) {
  if (['preparing', 'running', 'dispatching'].includes(status)) return ['pause', 'stop'];
  if (status === 'pausing') return ['stop'];
  if (status === 'paused') return ['resume', 'stop'];
  return [];
}

export function normalizePipeline(raw) {
  if (raw === null || typeof raw !== 'object' || Array.isArray(raw)) return null;
  return {
    runId: optionalText(raw.runId), status: text(raw.status, 'unknown'), reason: optionalText(raw.reason),
    updatedAt: optionalText(raw.updatedAt), pauseRequested: raw.pauseRequested === true,
    stages: (Array.isArray(raw.stages) ? raw.stages : []).filter(stage => stage && typeof stage === 'object').map(stage => ({
      stage: text(stage.stage), status: text(stage.status, 'unknown'),
      reason: optionalText(stage.reason),
      gateResult: stage.gateResult && typeof stage.gateResult === 'object' ? stage.gateResult : null,
    })),
  };
}

/** Coerce an unknown value into a display-safe string. */
export function text(value, fallback = "—") {
  return typeof value === "string" && value.trim() !== "" ? value : fallback;
}

/** Pass through a nullable string field without inventing data. */
export function optionalText(value) {
  return typeof value === "string" && value.trim() !== "" ? value : null;
}

/** Normalize one training-run record with defaults (runId/mode/status/target/updatedAt). */
export function normalizeRun(raw) {
  const record = raw !== null && typeof raw === "object" ? raw : {};
  return {
    runId: text(record.runId, "unnamed-run"),
    mode: text(record.mode, "training"),
    status: text(record.status, "unknown"),
    target: normalizeTarget(record.target),
    purpose: text(record.purpose, "business-training"),
    issueOwners: Array.isArray(record.issueOwners) ? record.issueOwners.filter(owner => owner &&
      typeof owner.sourceRole === 'string' && typeof owner.profileId === 'string')
      .map(owner => ({ sourceRole: owner.sourceRole, profileId: owner.profileId })) : [],
    modelChoice: optionalText(record.modelChoice),
    testItems: Array.isArray(record.testItems) ? record.testItems.filter((item) => typeof item === "string") : [],
    outcome: record.outcome !== null && typeof record.outcome === "object" ? record.outcome : null,
    error: optionalText(record.error),
    artifactRoot: optionalText(record.artifactRoot),
    lifecycle: record.lifecycle !== null && typeof record.lifecycle === "object" ? record.lifecycle : null,
    pipeline: normalizePipeline(record.pipeline),
    simpleOrchestration: record.simpleOrchestration && typeof record.simpleOrchestration === 'object'
      ? record.simpleOrchestration : null,
    updatedAt: text(record.updatedAt, "—")
  };
}

/**
 * Normalize a training-run target: a profile or pipeline object, or null.
 * Keeps the object shape so views can render profileId or stage ranges.
 */
export function normalizeTarget(raw) {
  if (raw === null || raw === undefined) return null;
  if (typeof raw === "string") {
    return raw.trim() !== "" ? raw : null;
  }
  if (typeof raw !== "object") return null;
  if (raw.kind === "profile") {
    return { kind: "profile", profileId: optionalText(raw.profileId) };
  }
  if (raw.kind === "pipeline") {
    const stages = Array.isArray(raw.stages)
      ? raw.stages.filter((stage) => typeof stage === "string" && stage.trim() !== "")
      : [];
    return {
      kind: "pipeline",
      fromStage: optionalText(raw.fromStage),
      toStage: optionalText(raw.toStage),
      stages
    };
  }
  return { kind: "unknown" };
}

/**
 * Human-readable label for a normalized target: profileId for a profile
 * target, a stage range (or stage list) for a pipeline target; null when
 * there is nothing to show.
 */
export function formatTarget(target) {
  if (target === null || target === undefined) return null;
  if (typeof target === "string") return target;
  if (target.kind === "profile") return target.profileId;
  if (target.kind === "pipeline") {
    if (target.stages.length > 0) return target.stages.join("→");
    if (target.fromStage !== null && target.toStage !== null) {
      return `${target.fromStage}→${target.toStage}`;
    }
    return target.fromStage ?? target.toStage ?? null;
  }
  return null;
}

/** Normalize one expert-profile record (profileId/publishedVersion/manifestDigest/draftVerdict). */
export function normalizeProfile(raw) {
  const record = raw !== null && typeof raw === "object" ? raw : {};
  return {
    profileId: text(record.profileId, "unnamed-profile"),
    publishedVersion: optionalText(record.publishedVersion),
    manifestDigest: optionalText(record.manifestDigest),
    draftVerdict: optionalText(record.draftVerdict)
  };
}

/**
 * Normalize the delivery record: a single object or null.
 * Never fabricates a delivery when the server reports none.
 */
export function normalizeDelivery(raw) {
  if (raw === null || typeof raw !== "object") return null;
  return {
    batchId: text(raw.batchId, "unnamed-batch"),
    state: optionalText(raw.state),
    releaseId: optionalText(raw.releaseId),
    executionScope: optionalText(raw.executionScope),
    updatedAt: text(raw.updatedAt, "—")
  };
}

/** Normalize the active release record: a single object or null. */
export function normalizeActiveRelease(raw) {
  if (raw === null || typeof raw !== "object") return null;
  return {
    releaseId: optionalText(raw.releaseId),
    manifestDigest: optionalText(raw.manifestDigest),
    activatedAt: optionalText(raw.activatedAt)
  };
}

/** Normalize the migration block; tolerate an absent block. */
export function normalizeMigration(raw) {
  const record = raw !== null && typeof raw === "object" ? raw : {};
  return {
    legacyConsoleAbandoned: record.legacyConsoleAbandoned === true,
    legacyMode: optionalText(record.legacyMode),
    legacyModeAuthoritative: record.legacyModeAuthoritative === true
  };
}

function normalizeBusinessAgent(raw) {
  const record = raw !== null && typeof raw === 'object' ? raw : {};
  const resources = key => Array.isArray(record[key]) ? record[key].filter(item => item && typeof item.path === 'string')
    .map(item => ({ path: item.path, used: item.used === true })) : [];
  return {
    profileId: text(record.profileId, 'unknown-agent'),
    displayName: text(record.displayName, 'Agent'),
    latestRunId: optionalText(record.latestRunId),
    latestRunStatus: optionalText(record.latestRunStatus),
    inputs: resources('inputs'), outputs: resources('outputs'),
    skills: resources('skills'), scripts: resources('scripts'),
  };
}

/** Normalize the whole /api/ptc-control/state payload; never throws. */
export function normalizeState(raw) {
  const body = raw !== null && typeof raw === "object" ? raw : {};
  const trainingRuns = Array.isArray(body.trainingRuns) ? body.trainingRuns : [];
  const profiles = Array.isArray(body.profiles) ? body.profiles : [];
  return {
    schemaVersion:
      typeof body.schemaVersion === "number" ? body.schemaVersion : null,
    identity: text(body.identity, "unbound"),
    activeRelease: normalizeActiveRelease(body.activeRelease),
    activeFrameworkRelease: body.activeFrameworkRelease && typeof body.activeFrameworkRelease === 'object'
      ? { releaseId: optionalText(body.activeFrameworkRelease.releaseId),
        bundleDigest: optionalText(body.activeFrameworkRelease.bundleDigest),
        activatedAt: optionalText(body.activeFrameworkRelease.activatedAt),
        sourceRunId: optionalText(body.activeFrameworkRelease.sourceRunId) } : null,
    frameworkReleaseError: optionalText(body.frameworkReleaseError),
    activeTrainingRelease: body.activeTrainingRelease && typeof body.activeTrainingRelease === 'object'
      ? { releaseId: optionalText(body.activeTrainingRelease.releaseId),
        manifestDigest: optionalText(body.activeTrainingRelease.manifestDigest),
        activatedAt: optionalText(body.activeTrainingRelease.activatedAt) } : null,
    trainingReleaseError: optionalText(body.trainingReleaseError),
    publishedSmokeRuns: Array.isArray(body.publishedSmokeRuns)
      ? body.publishedSmokeRuns.filter(run => run && typeof run === 'object').map(run => ({
        runId: optionalText(run.runId), releaseId: optionalText(run.releaseId),
        status: text(run.status, 'unknown'), updatedAt: optionalText(run.updatedAt),
        outcome: run.outcome && typeof run.outcome === 'object' ? run.outcome : null,
      })) : [],
    publishedFrameworkRuns: Array.isArray(body.publishedFrameworkRuns)
      ? body.publishedFrameworkRuns.filter(run => run && typeof run === 'object').map(run => ({
        runId: optionalText(run.runId), releaseId: optionalText(run.releaseId),
        status: text(run.status, 'unknown'), purpose: optionalText(run.purpose),
        reason: optionalText(run.reason),
        outcome: run.outcome && typeof run.outcome === 'object' ? run.outcome : null,
        stages: Array.isArray(run.stages) ? run.stages : [],
      })) : [],
    trainingRuns: trainingRuns.map(normalizeRun),
    workflowTemplateRuns: Array.isArray(body.workflowTemplateRuns)
      ? body.workflowTemplateRuns.filter(run => run && typeof run === 'object') : [],
    activeWorkflowTemplateRelease: body.activeWorkflowTemplateRelease && typeof body.activeWorkflowTemplateRelease === 'object'
      ? body.activeWorkflowTemplateRelease : null,
    workflowTemplateReleaseError: optionalText(body.workflowTemplateReleaseError),
    publishedWorkflowTemplateRuns: Array.isArray(body.publishedWorkflowTemplateRuns)
      ? body.publishedWorkflowTemplateRuns.filter(run => run && typeof run === 'object') : [],
    delivery: normalizeDelivery(body.delivery),
    profiles: profiles.map(normalizeProfile),
    businessAgents: Array.isArray(body.businessAgents) ? body.businessAgents.map(normalizeBusinessAgent) : [],
    pipelineStages: Array.isArray(body.pipelineStages) ? body.pipelineStages.filter(stage => typeof stage === 'string' && stage !== 'COMPLETE') : [],
    migration: normalizeMigration(body.migration)
  };
}

/**
 * Create the shared read-only state store.
 *
 * @param {object} [options]
 * @param {string} [options.url]        State endpoint, same-origin.
 * @param {number} [options.pollMs]     Poll cadence while started.
 * @param {typeof fetch} [options.fetchImpl] Injectable fetch for tests.
 * @returns {{ subscribe, getSnapshot, getRevision, getLastError, refresh, start, stop }}
 */
export function createPtcStateStore(options = {}) {
  const url = options.url ?? STATE_URL;
  const pollMs = options.pollMs ?? DEFAULT_POLL_MS;
  const fetchImpl = options.fetchImpl ?? fetch;
  const listeners = new Set();
  let snapshot = normalizeState(null);
  let lastError = null;
  let started = false;
  let timer = null;
  let inFlight = false;
  let revision = 0;

  function publish() {
    revision += 1;
    for (const listener of listeners) listener();
  }

  async function refresh() {
    if (inFlight) return;
    inFlight = true;
    try {
      const response = await fetchImpl(url, {
        method: "GET",
        headers: { Accept: "application/json" },
        credentials: "same-origin"
      });
      if (!response.ok) {
        throw new Error(`GET ${url} failed with HTTP ${response.status}`);
      }
      const body = await response.json();
      const next = normalizeState(body);
      lastError = null;
      const changed = JSON.stringify(next) !== JSON.stringify(snapshot);
      snapshot = next;
      if (changed) publish();
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
      publish();
    } finally {
      inFlight = false;
    }
  }

  function subscribe(listener) {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }

  function getSnapshot() {
    return snapshot;
  }

  function getLastError() {
    return lastError;
  }

  function getRevision() {
    return revision;
  }

  function start() {
    if (started) return;
    started = true;
    void refresh();
    timer = setInterval(() => {
      void refresh();
    }, pollMs);
  }

  function stop() {
    if (timer !== null) {
      clearInterval(timer);
      timer = null;
    }
    started = false;
  }

  return { subscribe, getSnapshot, getRevision, getLastError, refresh, start, stop };
}
