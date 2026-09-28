window.__ModuleLoader__.load({
	id: "dsh-ptc-control-plane",
	factory: (require) => {
		var module = { exports: {} };
		var exports = module.exports;
		Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
		const { createElement, useEffect, useState, useSyncExternalStore } = require("react");
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
		const STOP_TRAINING_URL = "/api/ptc-control/training-runs/stop";
		const EXECUTE_PIPELINE_URL = "/api/ptc-control/training-pipelines/execute";
		const CONTROL_PIPELINE_URL = "/api/ptc-control/training-pipelines/control";
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

		async function createTrainingRunRequest(target, options = {}) {
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

		async function executeTrainingRunRequest(runId, testItems, options = {}) {
		  const url = options.url ?? EXECUTE_TRAINING_URL;
		  const fetchImpl = options.fetchImpl ?? fetch;
		  const response = await fetchImpl(url, {
		    method: "POST",
		    headers: { Accept: "application/json", "Content-Type": "application/json" },
		    credentials: "same-origin",
		    body: JSON.stringify({ runId, testItems })
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) {
		    throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  }
		  return body;
		}

		async function stopTrainingRunRequest(runId, options = {}) {
		  const response = await (options.fetchImpl ?? fetch)(options.url ?? STOP_TRAINING_URL, {
		    method: "POST", headers: { Accept: "application/json", "Content-Type": "application/json" },
		    credentials: "same-origin", body: JSON.stringify({ runId })
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
		  return body;
		}

		async function executeTrainingPipelineRequest(runId, testItems, options = {}) {
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

		function executeFrameworkRehearsalRequest(runId, testItems, options = {}) {
		  return executeTrainingRunRequest(runId, testItems, { ...options, url: options.url ?? EXECUTE_REHEARSAL_URL });
		}

		async function controlTrainingPipelineRequest(runId, action, options = {}) {
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

		function controlFrameworkRehearsalRequest(runId, action, options = {}) {
		  return controlTrainingPipelineRequest(runId, action, { ...options, url: options.url ?? CONTROL_REHEARSAL_URL });
		}

		async function publishFrameworkReleaseRequest(sourceRunId, options = {}) {
		  const url = options.url ?? PUBLISH_FRAMEWORK_URL;
		  const response = await (options.fetchImpl ?? fetch)(url, {
		    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
		    credentials: 'same-origin', body: JSON.stringify({ sourceRunId }),
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  return body;
		}

		async function recoverFrameworkRehearsalRequest(runId, options = {}) {
		  const url = options.url ?? RECOVER_REHEARSAL_URL;
		  const response = await (options.fetchImpl ?? fetch)(url, {
		    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
		    credentials: 'same-origin', body: JSON.stringify({ runId }),
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  return body;
		}

		async function executePublishedFrameworkRequest(options = {}) {
		  const url = options.url ?? EXECUTE_PUBLISHED_FRAMEWORK_URL;
		  const response = await (options.fetchImpl ?? fetch)(url, {
		    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
		    credentials: 'same-origin', body: '{}',
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  return body;
		}

		async function controlPublishedFrameworkRequest(runId, action, options = {}) {
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

		function executeProfileSmokeRequest(runId, options = {}) {
		  return postSmoke(EXECUTE_PROFILE_SMOKE_URL, { runId }, options);
		}

		function stopProfileSmokeRequest(runId, options = {}) {
		  return postSmoke(STOP_PROFILE_SMOKE_URL, { runId }, options);
		}

		function executeSimpleOrchestrationRequest(runId, profileRunIds, options = {}) {
		  return postSmoke(EXECUTE_SIMPLE_ORCHESTRATION_URL, {
		    runId, testItems: ['TM109'], profileRunIds, ...(options.pilot ? { pilot: true } : {}),
		  }, options);
		}

		function controlSimpleOrchestrationRequest(runId, action, options = {}) {
		  if (!['pause', 'resume', 'stop'].includes(action)) throw new Error('不支持的 smoke 流程控制操作');
		  return postSmoke(CONTROL_SIMPLE_ORCHESTRATION_URL, { runId, action }, options);
		}

		function publishTrainingReleaseRequest(profileRunIds, pipelineRunId, options = {}) {
		  return postSmoke(PUBLISH_TRAINING_RELEASE_URL, { profileRunIds, pipelineRunId }, options);
		}

		function freezeTrainingReleaseRequest(profileRunIds, pipelineRunId, options = {}) {
		  return postSmoke(FREEZE_TRAINING_RELEASE_URL, { profileRunIds, pipelineRunId }, options);
		}

		function activateTrainingReleaseRequest(stagingId, options = {}) {
		  return postSmoke(ACTIVATE_TRAINING_RELEASE_URL, { stagingId }, options);
		}

		function executeTrainingReleaseRequest(options = {}) {
		  return postSmoke(EXECUTE_TRAINING_RELEASE_URL, { testItems: ['TM109'] }, options);
		}

		async function createPtcSessionWorkspaceRequest(input, options = {}) {
		  const response = await (options.fetchImpl ?? fetch)(options.url ?? SESSION_WORKSPACE_URL, {
		    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
		    credentials: 'same-origin', body: JSON.stringify(input),
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${SESSION_WORKSPACE_URL} failed with HTTP ${response.status}`);
		  if (typeof body.path !== 'string' || !body.path) throw new Error('服务器未返回安全的会话工作区路径');
		  return body;
		}

		function workflowTemplateRequest(action, input, options = {}) {
		  if (!['read', 'save', 'freeze', 'execute', 'control'].includes(action)) {
		    throw new Error('unsupported workflow template action');
		  }
		  return postSmoke(`${WORKFLOW_TEMPLATE_URL}/${action}`, input, options);
		}

		function workflowTemplateReleaseRequest(action, input, options = {}) {
		  if (!['stage', 'activate', 'read', 'execute', 'control'].includes(action)) {
		    throw new Error('unsupported workflow template release action');
		  }
		  return postSmoke(`${WORKFLOW_TEMPLATE_RELEASE_URL}/${action}`, input, options);
		}

		function controlTrainingReleaseRequest(runId, action, options = {}) {
		  if (action !== 'stop') throw new Error('发布态 smoke 仅支持停止');
		  return postSmoke(CONTROL_TRAINING_RELEASE_URL, { runId, action }, options);
		}

		function parseTrainingTestItems(value) {
		  const items = typeof value === 'string' ? value.trim().toUpperCase().split(/[,，、\s]+/).filter(Boolean) : [];
		  if (!items.length || items.some(item => !/^TM[0-9]+$/.test(item))) throw new Error('请输入 TM 编号列表，例如 TM109,TM110；不支持范围或自由文本');
		  return [...new Set(items)];
		}

		function pipelineTrainingTarget(stages, fromStage, toStage) {
		  const start = stages.indexOf(fromStage);
		  const end = stages.indexOf(toStage);
		  if (start < 0 || end < start) throw new Error('请选择有效的流程起止阶段');
		  return { kind: 'pipeline', fromStage, toStage };
		}

		function pipelineControlActions(status) {
		  if (['preparing', 'running', 'dispatching'].includes(status)) return ['pause', 'stop'];
		  if (status === 'pausing') return ['stop'];
		  if (status === 'paused') return ['resume', 'stop'];
		  return [];
		}

		function normalizePipeline(raw) {
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
		function text(value, fallback = "—") {
		  return typeof value === "string" && value.trim() !== "" ? value : fallback;
		}

		/** Pass through a nullable string field without inventing data. */
		function optionalText(value) {
		  return typeof value === "string" && value.trim() !== "" ? value : null;
		}

		/** Normalize one training-run record with defaults (runId/mode/status/target/updatedAt). */
		function normalizeRun(raw) {
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
		function normalizeTarget(raw) {
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
		function formatTarget(target) {
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
		function normalizeProfile(raw) {
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
		function normalizeDelivery(raw) {
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
		function normalizeActiveRelease(raw) {
		  if (raw === null || typeof raw !== "object") return null;
		  return {
		    releaseId: optionalText(raw.releaseId),
		    manifestDigest: optionalText(raw.manifestDigest),
		    activatedAt: optionalText(raw.activatedAt)
		  };
		}

		/** Normalize the migration block; tolerate an absent block. */
		function normalizeMigration(raw) {
		  const record = raw !== null && typeof raw === "object" ? raw : {};
		  return {
		    legacyConsoleAbandoned: record.legacyConsoleAbandoned === true,
		    legacyMode: optionalText(record.legacyMode),
		    legacyModeAuthoritative: record.legacyModeAuthoritative === true
		  };
		}

		/** Normalize the whole /api/ptc-control/state payload; never throws. */
		function normalizeState(raw) {
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
		function createPtcStateStore(options = {}) {
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

		const SESSION_KEY_PREFIX = 'ptc-native-session:';

		function requireOk(result, operation) {
		  if (!result?.ok) throw new Error(result?.error?.message ?? `${operation} failed`);
		  return result.value;
		}

		function existingSessionId(key) {
		  try { return window.localStorage.getItem(`${SESSION_KEY_PREFIX}${key}`); }
		  catch { return null; }
		}

		function rememberSessionId(key, sessionId) {
		  try { window.localStorage.setItem(`${SESSION_KEY_PREFIX}${key}`, sessionId); }
		  catch { /* Session still opens; it will simply not be reused after refresh. */ }
		}

		function waitForBinding(sessions, sessionId) {
		  const ready = sessions.binding(sessionId);
		  if (ready !== undefined) return Promise.resolve(ready);
		  return new Promise((resolve, reject) => {
		    const timeout = window.setTimeout(() => {
		      unsubscribe();
		      reject(new Error('DSH 创建了会话，但 10 秒内没有出现在会话列表中。'));
		    }, 10_000);
		    const unsubscribe = sessions.list.subscribe(() => {
		      const binding = sessions.binding(sessionId);
		      if (binding === undefined) return;
		      window.clearTimeout(timeout);
		      unsubscribe();
		      resolve(binding);
		    });
		  });
		}

		/** Create or reopen a genuine DSH conversation rooted in its server-approved workspace. */
		async function openPtcNativeSession(scope, workspace, { key, title }) {
		  const api = typeof scope?.get === 'function' ? scope.get('connection')?.api : scope?.connection?.api;
		  if (!api?.agentPresets?.list || !api?.sessions?.create || !scope?.sessions || !scope?.workspaces) {
		    throw new Error('DSH 原生会话服务尚未注入；请确认本机 DSH 已加载会话与工作区服务。');
		  }
		  const remembered = existingSessionId(key);
		  if (remembered && scope.sessions.binding(remembered) !== undefined) {
		    scope.sessions.open(remembered);
		    return { sessionId: remembered, reused: true };
		  }

		  const target = await scope.workspaces.create({ path: workspace.path });
		  if (!target || typeof target.workspaceId !== 'string' || !target.workspaceId) {
		    throw new Error('DSH 没有为会话工作区返回 workspaceId');
		  }
		  const roster = requireOk((await api.agentPresets.list({})).result, '读取 DSH Agent 预设');
		  const presets = Array.isArray(roster?.presets) ? roster.presets : [];
		  const preset = presets.find(item => !item.broken && item.id === 'standard')
		    ?? presets.find(item => !item.broken && item.id === 'code')
		    ?? presets.find(item => !item.broken && item.isDefault);
		  if (!preset) throw new Error('DSH 没有可用的 standard/code Agent 预设');
		  const created = requireOk((await api.sessions.create({ workspaceId: target.workspaceId, agentPreset: preset.id })).result, '创建 DSH 会话');
		  if (typeof created?.sessionId !== 'string' || !created.sessionId) throw new Error('DSH 没有返回 sessionId');
		  const binding = await waitForBinding(scope.sessions, created.sessionId);
		  await binding.session.rename(title);
		  rememberSessionId(key, created.sessionId);
		  scope.sessions.open(created.sessionId);
		  return { sessionId: created.sessionId, reused: false };
		}

		function ptcSessionKey(mode, identity = '') {
		  if (!['agent', 'workflow', 'publish', 'engineering'].includes(mode)) throw new Error('unsupported PTC session mode');
		  return `${mode}:${identity}`;
		}

		const h = createElement;

		async function draftRequest(action, input) {
		  const response = await fetch(`/api/ptc-control/training-drafts/${action}`, {
		    method: 'POST', credentials: 'same-origin',
		    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
		    body: JSON.stringify(input),
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
		  return body;
		}

		/** Only mounted in the training view; immutable run snapshots never change. */
		function DraftEditor({ profileId }) {
		  const [file, setFile] = useState('instructions.md');
		  const [loaded, setLoaded] = useState(null);
		  const [content, setContent] = useState('');
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState('');
		  useEffect(() => { setLoaded(null); setContent(''); setNotice(''); }, [profileId, file]);
		  const read = async () => {
		    setBusy(true); setNotice('');
		    try {
		      const value = await draftRequest('read', { profileId, file });
		      setLoaded(value); setContent(value.content);
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  const save = async () => {
		    if (!loaded || loaded.profileId !== profileId || loaded.file !== file) return;
		    setBusy(true); setNotice('');
		    try {
		      const result = await draftRequest('save', { mode: 'training', profileId, file, content, expectedSha256: loaded.sha256 });
		      setLoaded({ ...loaded, content, sha256: result.sha256 });
		      setNotice(result.changed ? `草稿已保存；历史记录 ${result.historyId}。需新建训练复测，已有运行和发布快照不变。` : '内容未变化，无需保存。');
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  return h('details', { className: 'ptc-cp-draft' },
		    h('summary', null, '训练草稿编辑'),
		    h('p', null, '这里只修改候选专家。保存不会修改已启动训练，也不会自动发布。'),
		    h('select', { 'aria-label': '草稿文件', value: file, disabled: busy, onChange: event => setFile(event.target.value) },
		      ...['instructions.md', 'profile.yaml', 'output-contract.schema.json'].map(name => h('option', { key: name, value: name }, name))),
		    h('button', { type: 'button', disabled: busy || !profileId, onClick: () => void read() }, '读取草稿'),
		    loaded ? h('div', null,
		      h('div', null, `SHA-256：${loaded.sha256}`),
		      h('textarea', { 'aria-label': '专家草稿内容', value: content, disabled: busy, rows: 18,
		        style: { width: '100%', fontFamily: 'monospace' }, onChange: event => setContent(event.target.value) }),
		      h('button', { type: 'button', disabled: busy || content === loaded.content, onClick: () => void save() }, '保存训练草稿')) : null,
		    notice ? h('p', { role: 'status' }, notice) : null);
		}

		const issueElement = createElement;

		function issueOwner(run) {
		  if (run.target?.kind === 'profile' && run.target.profileId === 'ptc-dft-expert') {
		    return { profileId: 'ptc-dft-expert' };
		  }
		  if (run.purpose === 'schematic-statistic-only') {
		    return { profileId: 'ptc-schematic-expert', sourceRole: 'schematic-expert' };
		  }
		  return null;
		}

		function isIssueCandidate(run) {
		  if (run.mode !== 'training' || !['blocked', 'completed'].includes(run.status)
		      || run.purpose === 'framework-rehearsal') return false;
		  return !!issueOwner(run) || (run.purpose === 'business-training' && run.target?.kind === 'pipeline');
		}

		async function post(resource, action, input) {
		  const response = await fetch(`/api/ptc-control/${resource}/${action}`, {
		    method: 'POST', credentials: 'same-origin',
		    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
		    body: JSON.stringify(input),
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
		  return body;
		}

		/** Local training proposals only; no draft write, case promotion or release. */
		function TrainingIssueEditor({ runs }) {
		  const eligible = runs.filter(isIssueCandidate);
		  const [runId, setRunId] = useState('');
		  const [sourceRole, setSourceRole] = useState('');
		  const [title, setTitle] = useState('');
		  const [description, setDescription] = useState('');
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState('');
		  const [issues, setIssues] = useState([]);
		  const [caseIssueId, setCaseIssueId] = useState('');
		  const [expectedBehavior, setExpectedBehavior] = useState('');
		  const [proposals, setProposals] = useState([]);
		  const selected = eligible.find(run => run.runId === runId) ?? eligible[0];
		  const pipelineOwners = selected?.purpose === 'business-training' && selected.target?.kind === 'pipeline'
		    ? (Array.isArray(selected.issueOwners) ? selected.issueOwners : []).filter(entry =>
		      entry && typeof entry.sourceRole === 'string' && typeof entry.profileId === 'string') : [];
		  const owner = selected && (issueOwner(selected)
		    ?? (pipelineOwners.find(entry => entry.sourceRole === sourceRole) ?? pipelineOwners[0] ?? null));
		  // Only the backend can verify run-local frozen materials and participating roles.
		  // Never infer pipeline ownership from the current stage registry or profile list.
		  const needsPipelineOwner = selected?.purpose === 'business-training'
		    && selected.target?.kind === 'pipeline' && !owner;
		  const caseIssues = issues.filter(issue => issue?.disposition === 'proposal-only'
		    && eligible.some(run => run.runId === issue.runId));
		  const selectedIssue = caseIssues.find(issue => issue.issueId === caseIssueId) ?? caseIssues[0];
		  const refresh = async () => {
		    setBusy(true); setNotice('');
		    try {
		      const [issueList, caseList] = await Promise.all([
		        post('training-issues', 'list', {}), post('training-cases', 'list', {}),
		      ]);
		      setIssues(issueList.issues);
		      setProposals(caseList.proposals);
		    }
		    catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  const create = async () => {
		    if (!selected || !owner || !title.trim() || !description.trim()) return;
		    setBusy(true); setNotice('');
		    try {
		      const result = await post('training-issues', 'create', { runId: selected.runId, ...owner,
		        title: title.trim(), description: description.trim() });
		      setTitle(''); setDescription('');
		      setIssues(current => [result.issue, ...current]);
		      setNotice(`已登记训练问题 ${result.issue.issueId}；仅作提案，不会修改草稿、门禁或发布版本。`);
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  const createCase = async () => {
		    if (!selectedIssue || !expectedBehavior.trim()) return;
		    setBusy(true); setNotice('');
		    try {
		      const result = await post('training-cases', 'create', {
		        issueId: selectedIssue.issueId, expectedBehavior: expectedBehavior.trim(),
		      });
		      setExpectedBehavior('');
		      setProposals(current => [result.proposal, ...current]);
		      setNotice(`已登记回归案例候选 ${result.proposal.caseId}；尚未采纳，不会修改回归集或发布版本。`);
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  return issueElement('details', { className: 'ptc-cp-training-issues' },
		    issueElement('summary', null, '训练问题与提案'),
		    issueElement('p', null, '问题绑定训练运行的 SHA-256；登记不会自动更改专家、编排或回归案例。'),
		    issueElement('label', null, '关联运行 ', issueElement('select', { value: selected?.runId ?? '', disabled: busy || !eligible.length,
		      onChange: event => { setRunId(event.target.value); setSourceRole(''); }, 'aria-label': '关联训练运行' },
		      ...eligible.map(run => issueElement('option', { key: run.runId, value: run.runId }, `${run.runId} · ${run.status}`)))),
		    pipelineOwners.length ? issueElement('label', null, '问题归属专家 ', issueElement('select', {
		      value: owner?.sourceRole ?? '', disabled: busy,
		      onChange: event => setSourceRole(event.target.value), 'aria-label': '问题归属专家' },
		    ...pipelineOwners.map(entry => issueElement('option', { key: entry.sourceRole, value: entry.sourceRole },
		      `${entry.sourceRole} · ${entry.profileId}`)))) : null,
		    needsPipelineOwner ? issueElement('p', { role: 'status', 'data-testid': 'ptc-cp-issue-owner-required' },
		      '此真实流程训练运行缺少经该运行冻结材料验证的专家角色与 profile 映射；当前无法安全登记，请勿按现行阶段配置猜测归属。') : null,
		    issueElement('input', { type: 'text', value: title, disabled: busy || !owner, maxLength: 120,
		      placeholder: '问题标题', 'aria-label': '训练问题标题', onChange: event => setTitle(event.target.value) }),
		    issueElement('textarea', { value: description, disabled: busy || !owner, maxLength: 4000,
		      rows: 5, placeholder: '现象、期望及复现步骤', 'aria-label': '训练问题描述',
		      onChange: event => setDescription(event.target.value) }),
		    issueElement('button', { type: 'button', disabled: busy || !owner || !title.trim() || !description.trim(),
		      onClick: () => void create() }, '登记训练问题'),
		    issueElement('button', { type: 'button', disabled: busy, onClick: () => void refresh() }, '刷新问题与案例候选'),
		    issueElement('p', null, '回归案例仅从已核验的训练问题生成候选；需要具体运行证据，登记后不会自动采纳。'),
		    issueElement('label', null, '关联训练问题 ', issueElement('select', {
		      value: selectedIssue?.issueId ?? '', disabled: busy || !caseIssues.length,
		      onChange: event => setCaseIssueId(event.target.value), 'aria-label': '关联训练问题' },
		    ...caseIssues.map(issue => issueElement('option', { key: issue.issueId, value: issue.issueId },
		      `${issue.issueId} · ${issue.title}`)))),
		    issueElement('textarea', { value: expectedBehavior, disabled: busy || !selectedIssue, maxLength: 4000,
		      rows: 4, placeholder: '写明期望行为和可判定的通过条件', 'aria-label': '回归案例预期行为',
		      onChange: event => setExpectedBehavior(event.target.value) }),
		    issueElement('button', { type: 'button', disabled: busy || !selectedIssue || !expectedBehavior.trim(),
		      onClick: () => void createCase() }, '登记回归案例候选'),
		    notice ? issueElement('p', { role: 'status' }, notice) : null,
		    ...issues.slice(0, 20).map(issue => issueElement('div', { key: issue.issueId },
		      `${issue.issueId} · ${issue.profileId} · ${issue.title} · 仅提案`)),
		    ...proposals.slice(0, 20).map(proposal => issueElement('div', { key: proposal.caseId },
		      `${proposal.caseId} · ${proposal.issueId} · 候选未采纳`)));
		}

		/** Summarize only host-recorded orchestration receipts; never infer completion from chat. */
		function workflowStatusSummary(orchestration) {
		  const stages = Array.isArray(orchestration?.stages) ? orchestration.stages : [];
		  const tasks = [
		    ...stages.flatMap(stage => Array.isArray(stage.tasks) ? stage.tasks : []),
		    ...(Array.isArray(orchestration?.auxiliaryTasks) ? orchestration.auxiliaryTasks : []),
		  ];
		  const completed = tasks.filter(task => task.status === 'completed').length;
		  const active = tasks.find(task => task.status === 'dispatching' || task.status === 'running');
		  const blocked = tasks.find(task => task.status === 'blocked' || task.status === 'cancelled');
		  const pending = tasks.find(task => task.status === 'pending');
		  const current = active ?? blocked ?? pending ?? null;
		  const lastCompletedIndex = tasks.findLastIndex(task => task.status === 'completed');
		  const previous = lastCompletedIndex >= 0 ? tasks[lastCompletedIndex] : null;
		  return {
		    completed,
		    total: tasks.length,
		    currentProfileId: current?.profileId ?? current?.role ?? null,
		    handoffFrom: current && previous && previous !== current ? previous.profileId ?? previous.role ?? null : null,
		    currentStatus: current?.status ?? null,
		  };
		}

		/**
		 * PTC control-plane client: read-only panel components.
		 *
		 * Pure React via createElement (no JSX): the module must stay runnable as
		 * plain ESM source until the package entry bundles it. The panel renders the
		 * four mandatory read-only status items (identity, activeRelease, training
		 * runs, delivery) and reserves the Training / ATE PTC Runtime views as
		 * separate components so later phases can extend them without touching the
		 * shell wiring.
		 */

		/** Compact `label: value` status row. */
		function StatusRow({ label, value, testId }) {
		  return createElement(
		    "div",
		    { className: "ptc-cp-row", "data-testid": testId ?? label, key: testId ?? label },
		    createElement("span", { className: "ptc-cp-label", key: "label" }, label),
		    createElement("span", { className: "ptc-cp-value", key: "value" }, value)
		  );
		}

		const ARITHMETIC_PROFILES = ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert',
		  'method-expert', 'rule-reviewer', 'ate-implementer', 'compile-diagnostician', 'evolution-expert'];

		// The DSH shell.overlay slot does not supply a layout or plugin stylesheet.
		// Keep this self-contained so an unloaded stylesheet cannot cover the chat UI.
		const PANEL_CSS = String.raw`
		.ptc-cp-host, .ptc-cp-host * { box-sizing: border-box; }
		.ptc-cp-host .ptc-cp-panel {
		  position: fixed; z-index: 2147483000; top: 82px; right: 16px;
		  width: min(1050px, calc(100vw - 32px)); max-height: calc(100vh - 100px);
		  overflow: auto; overscroll-behavior: contain; color: #eef3fa;
		  background: #182231; border: 1px solid #43536a; border-radius: 14px;
		  box-shadow: 0 18px 50px #0009; font: 13px/1.48 system-ui, "Microsoft YaHei", sans-serif;
		  overflow-wrap: anywhere;
		}
		.ptc-cp-host .ptc-cp-panel[open] {
		  inset: 12px; width: calc(100vw - 24px); max-height: calc(100vh - 24px);
		  border-radius: 12px;
		}
		.ptc-cp-host .ptc-cp-panel:not([open]) { width: max-content; max-width: calc(100vw - 32px); overflow: visible; }
		.ptc-cp-host .ptc-cp-panel > summary {
		  display: block; list-style: none; cursor: pointer; padding: 11px 15px;
		  background: #24446d; color: #fff; font-weight: 700; border-radius: 13px;
		}
		.ptc-cp-host .ptc-cp-panel > summary::-webkit-details-marker { display: none; }
		.ptc-cp-host .ptc-cp-panel[open] > summary {
		  position: sticky; top: 0; z-index: 1; border-radius: 13px 13px 0 0;
		  border-bottom: 1px solid #566c87;
		}
		.ptc-cp-host .ptc-cp-panel > :not(summary) { margin-left: 14px; margin-right: 14px; }
		.ptc-cp-host .ptc-cp-panel > .ptc-cp-header { margin-top: 14px; font-size: 17px; font-weight: 700; }
		.ptc-cp-host .ptc-cp-panel > .ptc-cp-view { margin-bottom: 16px; }
		.ptc-cp-host .ptc-cp-status { display: grid; gap: 5px; margin-top: 8px; margin-bottom: 12px; }
		.ptc-cp-host .ptc-cp-row { display: flex; gap: 8px; justify-content: space-between; min-width: 0; }
		.ptc-cp-host .ptc-cp-label { flex: 0 0 auto; color: #afc1d7; }
		.ptc-cp-host .ptc-cp-value { text-align: right; min-width: 0; overflow-wrap: anywhere; }
		.ptc-cp-host .ptc-cp-tabs { display: flex; gap: 7px; margin-bottom: 12px; }
		.ptc-cp-host .ptc-cp-panel button, .ptc-cp-host .ptc-cp-panel select,
		.ptc-cp-host .ptc-cp-panel input, .ptc-cp-host .ptc-cp-panel textarea {
		  max-width: 100%; font: inherit;
		}
		.ptc-cp-host .ptc-cp-panel button {
		  border: 1px solid #647d9d; background: #2b4463; color: #fff;
		  border-radius: 7px; padding: 6px 9px; cursor: pointer;
		  white-space: normal; text-align: left;
		}
		.ptc-cp-host .ptc-cp-panel button:hover:not(:disabled) { background: #365d89; }
		.ptc-cp-host .ptc-cp-panel button:disabled { opacity: .48; cursor: not-allowed; }
		.ptc-cp-host .ptc-cp-tab-active { background: #2a72b9 !important; border-color: #76b9f5 !important; }
		.ptc-cp-host .ptc-cp-panel select, .ptc-cp-host .ptc-cp-panel input,
		.ptc-cp-host .ptc-cp-panel textarea {
		  min-width: 0; background: #101a27; color: #f5f8fd;
		  border: 1px solid #536783; border-radius: 6px; padding: 6px;
		}
		.ptc-cp-host .ptc-cp-training-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-bottom: 13px; }
		.ptc-cp-host .ptc-cp-training-actions label { grid-column: 1 / -1; display: grid; gap: 3px; }
		.ptc-cp-host .ptc-cp-training-actions label select { width: 100%; }
		.ptc-cp-host .ptc-cp-smoke-controls {
		  display: grid; gap: 7px; margin: 12px 0; padding: 12px;
		  border: 1px solid #526782; border-radius: 10px; background: #202f42;
		}
		.ptc-cp-host .ptc-cp-smoke-controls p { margin: 0 0 5px; }
		.ptc-cp-host .ptc-cp-smoke-controls button { width: 100%; }
		.ptc-cp-host .ptc-cp-run {
		  margin: 10px 0; padding: 10px; background: #202b3b;
		  border: 1px solid #455b75; border-radius: 9px;
		}
		.ptc-cp-host .ptc-cp-run .ptc-cp-row { display: block; }
		.ptc-cp-host .ptc-cp-run .ptc-cp-label { display: block; color: #a9c8ed; font-weight: 700; }
		.ptc-cp-host .ptc-cp-run .ptc-cp-value { display: block; text-align: left; }
		.ptc-cp-host .ptc-cp-panel details:not(.ptc-cp-panel) { margin: 10px 0; padding: 7px; border: 1px solid #43536a; border-radius: 7px; }
		.ptc-cp-host .ptc-cp-panel pre { white-space: pre-wrap; overflow-wrap: anywhere; }
		.ptc-cp-host .ptc-cp-error { color: #ffb9b9; margin: 7px 0; }
		.ptc-cp-host .ptc-cp-notice { color: #abebc8; margin: 9px 0; }
		.ptc-cp-host .ptc-cp-workbench { min-width: 0; }
		.ptc-cp-host .ptc-cp-mode-tabs, .ptc-cp-host .ptc-cp-subtabs { display:flex; flex-wrap:wrap; gap:7px; margin:10px 0; }
		.ptc-cp-host .ptc-cp-layout { display:grid; grid-template-columns:minmax(190px,230px) minmax(0,1fr); gap:18px; }
		.ptc-cp-host .ptc-cp-roster { display:grid; align-content:start; gap:5px; max-height:55vh; overflow:auto; }
		.ptc-cp-host .ptc-cp-roster button { width:100%; }
		.ptc-cp-host .ptc-cp-workspace-main { min-width:0; }
		.ptc-cp-host .ptc-cp-agent-status { display:flex; align-items:center; gap:8px; padding:7px; border:1px solid #43536a; border-radius:8px; margin:5px 0; }
		.ptc-cp-host .ptc-cp-agent-status span:first-child { flex:1; }
		.ptc-cp-host .ptc-cp-stage-status { margin:8px 0; padding:9px; background:#202b3b; border:1px solid #43536a; border-radius:8px; }
		.ptc-cp-host .ptc-cp-stage-status ol { margin:7px 0; padding-left:22px; }
		.ptc-cp-host .ptc-cp-stage-status li { padding:3px 0; }
		.ptc-cp-host .ptc-cp-workflow-select { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:5px 10px; margin:10px 0; }
		.ptc-cp-host .ptc-cp-workflow-select label { display:flex; gap:7px; align-items:center; }
		.ptc-cp-host .ptc-cp-session-card, .ptc-cp-host .ptc-cp-publish-card { padding:12px; border:1px solid #526782; border-radius:10px; background:#202f42; margin:10px 0; }
		@media (max-width: 600px) {
		  .ptc-cp-host .ptc-cp-panel { top: 58px; right: 8px; width: calc(100vw - 16px); max-height: calc(100vh - 66px); }
		  .ptc-cp-host .ptc-cp-panel[open] { inset: 4px; width: calc(100vw - 8px); max-height: calc(100vh - 8px); }
		  .ptc-cp-host .ptc-cp-training-actions { grid-template-columns: 1fr; }
		  .ptc-cp-host .ptc-cp-workbench { min-width:0; width:calc(100vw - 32px); }
		  .ptc-cp-host .ptc-cp-layout { grid-template-columns:1fr; }
		  .ptc-cp-host .ptc-cp-roster { grid-template-columns:repeat(2,minmax(0,1fr)); max-height:28vh; }
		}
		`;

		function latestRun(runs, predicate) {
		  // The run ID contains its creation timestamp. Directory mtime can change
		  // later as evidence is inspected or amended, so it is not a source age.
		  return [...runs].filter(predicate).sort((a, b) => String(b.runId).localeCompare(String(a.runId)))[0] ?? null;
		}

		function smokeSources(runs) {
		  const profileRunIds = {};
		  for (const profileId of ARITHMETIC_PROFILES) {
		    const found = latestRun(runs, run => run.purpose === 'smoke-training'
		      && run.target?.kind === 'profile' && run.target.profileId === profileId);
		    // A newer pending/failed trial must not silently fall back to an older
		    // successful snapshot when composing a new whole-team run.
		    if (found?.status === 'completed' && found.outcome?.mode === 'SMOKE_ONLY'
		        && found.outcome?.smokePassed === true && found.outcome?.businessGatePassed === false) {
		      profileRunIds[profileId] = found.runId;
		    }
		  }
		  const newestPipeline = latestRun(runs, run => run.purpose === 'smoke-training'
		    && run.target?.kind === 'pipeline' && run.target.toStage === 'COMPILE');
		  const pipeline = newestPipeline?.status === 'completed'
		    && newestPipeline.outcome?.mode === 'SMOKE_ONLY' && newestPipeline.outcome?.smokePassed === true
		    && newestPipeline.outcome?.businessGatePassed === false ? newestPipeline : null;
		  const pipelineProfileRunIds = {};
		  for (const value of Object.values(pipeline?.simpleOrchestration?.profileBindings ?? {})) {
		    if (ARITHMETIC_PROFILES.includes(value?.profileId)
		        && typeof value?.profileVersion === 'string' && value.profileVersion.startsWith('draft-')) {
		      pipelineProfileRunIds[value.profileId] = value.profileVersion.slice('draft-'.length);
		    }
		  }
		  return { profileRunIds, pipelineRunId: pipeline?.runId ?? null,
		    pipelineProfileRunIds };
		}

		function SmokeTrainingControls({ state, store, showProfiles = true, showWorkflow = true, showPublish = true }) {
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState(null);
		  const sources = smokeSources(state.trainingRuns);
		  const missing = ARITHMETIC_PROFILES.filter(id => !sources.profileRunIds[id]);
		  const act = async (work, success) => {
		    setBusy(true); setNotice(null);
		    try { const result = await work(); await store.refresh(); setNotice(`${success}${result?.runId ? ` · ${result.runId}` : ''}`); }
		    catch (error) { setNotice(`操作未完成：${error?.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  return createElement('div', { className: 'ptc-cp-smoke-controls', 'data-testid': 'ptc-cp-smoke-controls' },
		    createElement('p', null, '最小训练闭环：八位专家（含 DFT、原理图）分别真实派发相同的 1+2 JSON 算术任务；仅验证派发与回执。不读取私有业务材料、不生成业务产物、不运行业务门禁。以下全为 SMOKE_ONLY，业务门禁未通过。'),
		    ...(showProfiles ? ARITHMETIC_PROFILES.map(profileId => createElement('button', {
		      key: profileId, type: 'button', disabled: busy || !state.profiles.some(profile => profile.profileId === profileId),
		      'data-testid': `ptc-cp-smoke-profile-${profileId}`,
		      onClick: () => void act(async () => {
		        const created = await createTrainingRunRequest({ kind: 'profile', profileId }, { purpose: 'smoke-training' });
		        await executeProfileSmokeRequest(created.runId);
		        return created;
		      }, `${profileId} 算术训练已受理；等待数字 3 回执，非业务通过`),
		    }, `单独训练 ${profileId}（1+2 JSON）`)) : []),
		    showWorkflow ? createElement('div', null, missing.length
		      ? `整体 smoke 尚缺：${missing.join('、')}`
		      : '八个单专家算术回执已齐，可开始整体编排 smoke。') : null,
		    showWorkflow ? createElement('button', { type: 'button', disabled: busy || missing.length > 0,
		      'data-testid': 'ptc-cp-start-simple-orchestration',
		      onClick: () => void act(async () => {
		        const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' },
		          { purpose: 'smoke-training' });
		        await executeSimpleOrchestrationRequest(created.runId, sources.profileRunIds);
		        return created;
		      }, 'TM109 全流程 smoke 已受理；阶段只验证控制链路，业务门禁未通过'),
		    }, '运行八专家整链 1+2 SMOKE_ONLY') : null,
		    showPublish ? createElement('button', { type: 'button', disabled: busy || !sources.pipelineRunId
		      || ARITHMETIC_PROFILES.some(id => !sources.pipelineProfileRunIds[id]),
		      'data-testid': 'ptc-cp-publish-training-release',
		      onClick: () => void act(() => publishTrainingReleaseRequest(sources.pipelineProfileRunIds, sources.pipelineRunId),
		      '已发布冻结 smoke 版本；不是业务交付版本'),
		    }, '发布已冻结的八专家 SMOKE_ONLY 版本（非业务）') : null,
		    notice ? createElement('div', { className: 'ptc-cp-notice' }, notice) : null);
		}

		/** Reserved Training view (PTC Training identity): trainingRuns list. */
		function TrainingView({ state, store, t }) {
		  const runs = state.trainingRuns;
		  const [selectedProfile, setSelectedProfile] = useState(state.profiles.some(p => p.profileId === 'ptc-dft-expert') ? 'ptc-dft-expert' : state.profiles[0]?.profileId ?? "");
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState(null);
		  const [testItem, setTestItem] = useState("TM109");
		  const [trainingModelChoice, setTrainingModelChoice] = useState('default');
		  const stages = state.pipelineStages ?? [];
		  const [fromStage, setFromStage] = useState('');
		  const [toStage, setToStage] = useState('');
		  const selectedFrom = fromStage || stages[0] || '';
		  const selectedTo = toStage || stages.at(-1) || '';
		  let testItems = [];
		  try { testItems = parseTrainingTestItems(testItem); } catch { /* Invalid input keeps execution disabled. */ }
		  const rangeValid = stages.indexOf(selectedFrom) >= 0 && stages.indexOf(selectedTo) >= stages.indexOf(selectedFrom);

		  useEffect(() => {
		    if (selectedProfile === "" && state.profiles[0]?.profileId) {
		      setSelectedProfile(state.profiles.some(p => p.profileId === 'ptc-dft-expert') ? 'ptc-dft-expert' : state.profiles[0].profileId);
		    }
		  }, [selectedProfile, state.profiles]);

		  const createRun = async (target, purpose = 'business-training') => {
		    setBusy(true);
		    setNotice(null);
		    try {
		      const result = await createTrainingRunRequest(target, { purpose });
		      await store.refresh();
		      let execution = null;
		      if (target.kind === "profile" && target.profileId === "ptc-dft-expert") {
		        execution = await executeTrainingRunRequest(result.runId, [testItem.trim().toUpperCase()]);
		      } else if (target.kind === 'pipeline') {
		        execution = purpose === 'framework-rehearsal'
		          ? await executeFrameworkRehearsalRequest(result.runId, parseTrainingTestItems(testItem))
		          : await executeTrainingPipelineRequest(result.runId, parseTrainingTestItems(testItem),
		            { modelChoice: purpose === 'schematic-statistic-only' ? 'default' : trainingModelChoice });
		      }
		      await store.refresh();
		      const outcome = execution?.outcome?.mode ? ` · ${execution.outcome.mode}` : "";
		      const model = execution?.outcome?.modelDispatched === true
		        ? ` · ${t("training.modelDispatched")}`
		        : execution?.outcome?.modelDispatched === false ? ` · ${t("training.noModel")}` : "";
		      setNotice(`${t("training.created")}: ${result.runId}${outcome}${model}${purpose === 'schematic-statistic-only' ? ' · 已受理仅生成 Component-Statistic；不派模型、不执行阶段门禁、不发布。' : purpose === 'framework-rehearsal' ? ' · 框架流程演练已受理；使用独立门禁，不代表真实业务门禁通过。' : target.kind === 'pipeline' ? ' · 流程训练请求已受理，请查看下方实时阶段；不代表已完成，不触发正式交付或发布。' : ''}`);
		    } catch (error) {
		      setNotice(`${t("training.createFailed")}: ${error instanceof Error ? error.message : String(error)}`);
		    } finally {
		      setBusy(false);
		    }
		  };
		  const stopRun = async (runId) => {
		    try {
		      const run = runs.find(item => item.runId === runId);
		      if (run?.purpose === 'smoke-training' && run.target?.kind === 'profile') await stopProfileSmokeRequest(runId);
		      else await stopTrainingRunRequest(runId);
		      setNotice(`${runId}：已请求停止并撤销后续工具权限；子进程是否退出请看清理记录。`);
		      await store.refresh();
		    } catch (error) { setNotice(String(error.message ?? error)); }
		  };
		  const controlPipeline = async (runId, action, purpose) => {
		    setBusy(true);
		    try {
		      if (purpose === 'framework-rehearsal') await controlFrameworkRehearsalRequest(runId, action);
		      else if (purpose === 'smoke-training') await controlSimpleOrchestrationRequest(runId, action);
		      else await controlTrainingPipelineRequest(runId, action);
		      setNotice(`${runId}：${action === 'pause' ? '已请求暂停，当前操作结束后暂停，不进入后续阶段。' : action === 'resume' ? '已请求继续训练。' : '已请求停止训练，退出结果请查看运行记录。'}`);
		      await store.refresh();
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  const publishFramework = async runId => {
		    setBusy(true);
		    try {
		      const published = await publishFrameworkReleaseRequest(runId);
		      setNotice(`${runId}：已发布非业务框架演练版本 ${published.releaseId}；不代表正式业务发布。`);
		      await store.refresh();
		    } catch (error) { setNotice(`框架演练发布失败：${error.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  const recoverFramework = async runId => {
		    setBusy(true);
		    try {
		      await recoverFrameworkRehearsalRequest(runId);
		      setNotice(`${runId}：已请求显式核对持久化回执；无回执的在途阶段不会自动重派。`);
		      await store.refresh();
		    } catch (error) { setNotice(`演练恢复失败：${error.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  return createElement(
		    "div",
		    { className: "ptc-cp-view ptc-cp-view-training", "data-testid": "ptc-cp-training-view" },
		    createElement(StatusRow, {
		      label: t("training.runs"),
		      value: String(runs.length),
		      testId: "ptc-cp-training-count"
		    }),
		    createElement(
		      "div",
		      { className: "ptc-cp-training-actions", "data-testid": "ptc-cp-training-actions", key: "actions" },
		      createElement(
		        "select",
		        {
		          value: selectedProfile,
		          disabled: busy || state.profiles.length === 0,
		          onChange: (event) => setSelectedProfile(event.target.value),
		          "aria-label": t("training.profile")
		        },
		        ...state.profiles.map((profile) => createElement(
		          "option", { value: profile.profileId, key: profile.profileId }, profile.profileId
		        ))
		      ),
		      createElement(
		        "input",
		        {
		          type: "text",
		          value: testItem,
		          disabled: busy,
		          onChange: (event) => setTestItem(event.target.value),
		          placeholder: "TM109,TM110",
		          "aria-label": t("training.testItem"),
		          "data-testid": "ptc-cp-training-tm"
		        }
		      ),
		      createElement(
		        "button",
		        {
		          type: "button",
		          disabled: true,
		          "data-testid": "ptc-cp-create-profile-training"
		        },
		        '旧 DFT 业务训练入口已存档'
		      ),
		      createElement(
		        'label', null, '流程起始阶段 ',
		        createElement('select', {
		          value: selectedFrom, disabled: busy || !stages.length,
		          onChange: event => setFromStage(event.target.value), 'aria-label': '流程起始阶段',
		          'data-testid': 'ptc-cp-pipeline-from',
		        }, ...stages.map(stage => createElement('option', { key: stage, value: stage }, stage)))
		      ),
		      createElement(
		        'label', null, '流程结束阶段 ',
		        createElement('select', {
		          value: selectedTo, disabled: busy || !stages.length,
		          onChange: event => setToStage(event.target.value), 'aria-label': '流程结束阶段',
		          'data-testid': 'ptc-cp-pipeline-to',
		        }, ...stages.map(stage => createElement('option', { key: stage, value: stage, disabled: stages.indexOf(stage) < stages.indexOf(selectedFrom) }, stage)))
		      ),
		      createElement('label', null, '真实流程训练子专家模型 ',
		        createElement('select', { value: trainingModelChoice, disabled: busy,
		          onChange: event => setTrainingModelChoice(event.target.value),
		          'aria-label': '真实流程训练子专家模型', 'data-testid': 'ptc-cp-pipeline-model' },
		        createElement('option', { value: 'default' }, 'DSH 全局默认'),
		        createElement('option', { value: 'deepseek-v4-flash' }, 'DeepSeek-V4-Flash'))),
		      createElement(
		        "button",
		        {
		          type: "button",
		          disabled: true,
		          onClick: () => void createRun(pipelineTrainingTarget(stages, selectedFrom, selectedTo)),
		          "data-testid": "ptc-cp-create-pipeline-training"
		        },
		        '完整原理图流程已存档，暂不启动'
		      ),
		      createElement(
		        'button',
		        { type: 'button', disabled: true,
		          'data-testid': 'ptc-cp-create-schematic-statistic-only' },
		        '旧 Component-Statistic 脚本入口已存档'
		      ),
		      createElement(
		        'button',
		        {
		          type: 'button',
		          disabled: true,
		          onClick: () => void createRun(pipelineTrainingTarget(stages, 'INPUT_SYNC', 'COMPILE'), 'framework-rehearsal'),
		          'data-testid': 'ptc-cp-create-framework-rehearsal',
		        },
		        '全流程框架演练已存档，暂不启动'
		      ),
		      notice ? createElement("div", { className: "ptc-cp-notice", key: "notice" }, notice) : null
		    ),
		    createElement('p', null, '当前只开放下方八专家逐个算术训练与整体编排 SMOKE_ONLY。旧 DFT 业务训练、Component-Statistic 脚本和完整原理图流程均已存档，不参与本轮执行；smoke 不代表业务门禁通过。'),
		    !stages.length ? createElement('p', { className: 'ptc-cp-error' }, '阶段注册表尚未加载，流程入口暂不可用。') : null,
		    createElement(SmokeTrainingControls, { state, store }),
		    createElement(DraftEditor, { key: selectedProfile, profileId: selectedProfile }),
		    createElement(TrainingIssueEditor, { runs }),
		    ...runs.map((run) => {
		      const targetLabel = formatTarget(run.target);
		      const itemLabel = run.testItems.length > 0 ? ` · ${run.testItems.join(",")}` : "";
		      const outcomeLabel = typeof run.outcome?.mode === "string" ? ` · ${run.outcome.mode}` : "";
		      const isPipeline = run.target?.kind === 'pipeline';
		      const isRehearsal = run.purpose === 'framework-rehearsal';
		      const isStatisticOnly = run.purpose === 'schematic-statistic-only';
		      const isSmoke = run.purpose === 'smoke-training';
		      return createElement('div', { key: run.runId, className: 'ptc-cp-run' }, createElement(StatusRow, {
		        label: run.runId,
		        value: `${isSmoke ? 'SMOKE_ONLY · 业务门禁未通过' : isRehearsal ? '框架演练' : isStatisticOnly ? '单项统计训练' : run.mode} · ${run.status}${targetLabel ? ` · ${targetLabel}` : ""}${itemLabel}${isPipeline && !isRehearsal && !isStatisticOnly && !isSmoke && run.modelChoice ? ` · 模型 ${run.modelChoice}` : ''}${outcomeLabel}${isRehearsal && run.status === 'completed' ? ' · 流程演练通过（非真实业务门禁）' : ''}`,
		        testId: `ptc-cp-run-${run.runId}`
		      }),
		      run.artifactRoot ? createElement('div', null, `产物目录：${run.artifactRoot}`) : null,
		      (run.error || run.outcome?.reason) ? createElement('div', { className: 'ptc-cp-error' }, run.error || run.outcome.reason) : null,
		      isRehearsal && run.status === 'completed' ? createElement('button', {
		        type: 'button', disabled: busy, onClick: () => void publishFramework(run.runId),
		        'data-testid': `ptc-cp-publish-framework-${run.runId}`,
		      }, '发布框架演练版本（非业务）') : null,
		      isStatisticOnly && run.outcome?.report ? createElement('div', null,
		        `仅统计产物：${run.outcome.report.outputPath} · SHA-256 ${run.outcome.report.outputSha256} · 阶段门禁未运行`) : null,
		      isSmoke && isPipeline ? createElement('div', { 'data-testid': `ptc-cp-smoke-pipeline-${run.runId}` },
		        run.simpleOrchestration ? createElement('div', null,
		          createElement('div', null, `整体 smoke：${run.simpleOrchestration.status} · businessGatePassed=false`),
		          run.simpleOrchestration.reason ? createElement('div', { className: 'ptc-cp-error' }, run.simpleOrchestration.reason) : null,
		          ...(run.simpleOrchestration.stages ?? []).map(stage => createElement('div', { key: stage.stage },
		            `${stage.stage} · ${stage.status} · SMOKE_ONLY`,
		            ...(stage.tasks ?? []).map(task => createElement('div', { key: task.dispatchId },
		              `${task.role} · ${task.status}${task.answer === 3 ? ' · JSON answer=3' : ''}`)))),
		          ...(run.simpleOrchestration.auxiliaryTasks ?? []).map(task => createElement('div', { key: task.dispatchId },
		            `辅助 ${task.role} · ${task.status}${task.answer === 3 ? ' · JSON answer=3' : ''}`)))
		          : createElement('div', null, '等待整体 smoke 进度；尚未认定任何阶段完成。'),
		        ...pipelineControlActions(run.status).map(action => createElement('button', {
		          key: action, type: 'button', disabled: busy,
		          onClick: () => void controlPipeline(run.runId, action, run.purpose),
		          'aria-label': `${action} ${run.runId}`,
		        }, action === 'pause' ? '暂停整体 smoke' : action === 'resume' ? '继续整体 smoke' : '停止整体 smoke'))
		      ) : isPipeline && !isStatisticOnly ? createElement('div', { 'data-testid': `ptc-cp-pipeline-${run.runId}` },
		        run.pipeline ? createElement('div', null,
		          createElement('div', null, `流程状态：${run.pipeline.status}`),
		          createElement('div', null, `当前阶段：${run.pipeline.stages.find(stage => stage.status !== 'completed')?.stage ?? (run.pipeline.status === 'completed' ? '已完成所选阶段' : '未知')}`),
		          run.pipeline.reason ? createElement('div', { className: 'ptc-cp-error' }, run.pipeline.reason) : null,
		          ...run.pipeline.stages.map(stage => createElement('details', { key: stage.stage },
		            createElement('summary', null, `${stage.stage} · ${stage.status}${stage.gateResult ? ` · 门禁 ${stage.gateResult.status ?? '未知'} (exit ${stage.gateResult.exitCode ?? '未知'})` : ' · 尚无门禁回执'}`),
		            stage.reason ? createElement('div', null, stage.reason) : null,
		            stage.gateResult ? createElement('pre', { style: { whiteSpace: 'pre-wrap' } }, JSON.stringify(stage.gateResult, null, 2)) : null)))
		          : createElement('div', null, '尚无流程进度文件；请等待准备结果，未据此认定派发或完成。'),
		        (run.status === 'interrupted' || run.pipeline?.status === 'interrupted')
		          ? isRehearsal
		            ? createElement('button', { type: 'button', disabled: busy,
		              onClick: () => void recoverFramework(run.runId),
		              'data-testid': `ptc-cp-recover-framework-${run.runId}` }, '核对回执并恢复框架演练')
		            : createElement('p', { className: 'ptc-cp-error' }, '运行已中断：需人工核对专家回执与门禁记录，禁止盲目重派；此处不提供直接继续。')
		          : pipelineControlActions(run.status).map(action => createElement('button', {
		            key: action, type: 'button', disabled: busy, onClick: () => void controlPipeline(run.runId, action, run.purpose),
		            'aria-label': `${action} ${run.runId}`,
		          }, action === 'pause' ? '暂停流程训练' : action === 'resume' ? '继续流程训练' : '停止流程训练'))
		      ) : null,
		      !isPipeline && ['dispatching', 'running'].includes(run.status) ? createElement('button', {
		        type: 'button', onClick: () => void stopRun(run.runId), 'aria-label': `停止 ${run.runId}`
		      }, '停止训练') : null,
		      run.lifecycle ? createElement('details', null, createElement('summary', null, '执行与清理记录'),
		        createElement('pre', { style: { whiteSpace: 'pre-wrap' } }, JSON.stringify(run.lifecycle, null, 2))) : null);
		    })
		  );
		}

		/** Reserved ATE PTC Runtime view: latest delivery (single object or null). */
		function RuntimeView({ state, store, t }) {
		  const delivery = state.delivery;
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState(null);
		  const startPublished = async () => {
		    setBusy(true);
		    try {
		      const result = await executePublishedFrameworkRequest();
		      setNotice(`已从冻结版本 ${result.releaseId} 启动独立框架回放 ${result.runId}；不代表真实业务交付。`);
		      await store.refresh();
		    } catch (error) { setNotice(`发布模式启动失败：${error.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  const controlPublished = async (runId, action) => {
		    setBusy(true);
		    try {
		      await controlPublishedFrameworkRequest(runId, action);
		      setNotice(`${runId}：已请求${action === 'pause' ? '暂停' : action === 'resume' ? '继续' : '停止'}。`);
		      await store.refresh();
		    } catch (error) { setNotice(`发布模式控制失败：${error.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  const startPublishedSmoke = async () => {
		    setBusy(true);
		    try {
		      const result = await executeTrainingReleaseRequest();
		      setNotice(`已从八专家冻结算术 smoke 版本启动 TM109 发布态复跑 ${result.runId ?? ''}；业务门禁未通过。`);
		      await store.refresh();
		    } catch (error) { setNotice(`发布态 smoke 启动失败：${error.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  const stopPublishedSmoke = async runId => {
		    setBusy(true);
		    try {
		      await controlTrainingReleaseRequest(runId, 'stop');
		      setNotice(`${runId}：已请求停止发布态 smoke；请查看终态确认。`);
		      await store.refresh();
		    } catch (error) { setNotice(`发布态 smoke 停止失败：${error.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  return createElement(
		    "div",
		    { className: "ptc-cp-view ptc-cp-view-runtime", "data-testid": "ptc-cp-runtime-view" },
		    createElement(StatusRow, { label: '活动八专家算术训练发布版本（SMOKE_ONLY；非业务）',
		      value: state.activeTrainingRelease?.releaseId ?? '尚未发布',
		      testId: 'ptc-cp-active-training-release' }),
		    state.trainingReleaseError ? createElement('div', { className: 'ptc-cp-error' },
		      `训练发布版本校验失败：${state.trainingReleaseError}`) : null,
		    createElement('button', { type: 'button',
		      disabled: busy || !state.activeTrainingRelease || !!state.trainingReleaseError,
		      onClick: () => void startPublishedSmoke(), 'data-testid': 'ptc-cp-execute-training-release' },
		    '从八专家冻结版本复跑 TM109 SMOKE_ONLY（业务门禁未通过）'),
		    ...(state.publishedSmokeRuns ?? []).map(run => createElement('div', { key: run.runId, className: 'ptc-cp-run' },
		      createElement(StatusRow, { label: run.runId ?? '未知运行',
		        value: `${run.status} · ${run.releaseId ?? '无版本'} · SMOKE_ONLY · 业务门禁未通过` }),
		      run.outcome?.reason ? createElement('div', { className: 'ptc-cp-error' }, run.outcome.reason) : null,
		      ['running', 'preparing', 'dispatching', 'pausing', 'paused'].includes(run.status)
		        ? createElement('button', { type: 'button', disabled: busy,
		          onClick: () => void stopPublishedSmoke(run.runId),
		          'data-testid': `ptc-cp-stop-training-release-${run.runId}` }, '停止发布态 smoke') : null)),
		    createElement(StatusRow, { label: '框架演练发布版本（非业务）',
		      value: state.activeFrameworkRelease?.releaseId ?? '尚未发布',
		      testId: 'ptc-cp-framework-release' }),
		    state.frameworkReleaseError ? createElement('div', { className: 'ptc-cp-error' },
		      `框架发布完整性校验失败：${state.frameworkReleaseError}`) : null,
		    createElement('button', { type: 'button', disabled: busy || !state.activeFrameworkRelease || !!state.frameworkReleaseError,
		      onClick: () => void startPublished(), 'data-testid': 'ptc-cp-start-published-framework' },
		    '从冻结版本执行框架回放（非业务）'),
		    notice ? createElement('div', { className: 'ptc-cp-notice' }, notice) : null,
		    ...state.publishedFrameworkRuns.map(run => createElement('div', { key: run.runId, className: 'ptc-cp-run' },
		      createElement(StatusRow, { label: run.runId ?? '未知运行', value: `${run.status} · ${run.releaseId ?? '无版本'} · 冻结框架回放（非业务）` }),
		      (run.reason || run.outcome?.reason) ? createElement('div', { className: 'ptc-cp-error' }, run.reason || run.outcome.reason) : null,
		      ...(['running', 'preparing'].includes(run.status) ? ['pause', 'stop'] : run.status === 'paused' ? ['resume', 'stop'] : [])
		        .map(action => createElement('button', { key: action, type: 'button', disabled: busy,
		          onClick: () => void controlPublished(run.runId, action),
		          'aria-label': `${action} ${run.runId}` },
		        action === 'pause' ? '暂停发布框架回放' : action === 'resume' ? '继续发布框架回放' : '停止发布框架回放')),
		      ...run.stages.map(stage => createElement('div', { key: stage.stage }, `${stage.stage} · ${stage.status}`)))),
		    delivery === null
		      ? createElement(StatusRow, {
		          label: t("delivery.label"),
		          value: t("delivery.none"),
		          testId: "ptc-cp-delivery"
		        })
		      : createElement(
		          "div",
		          { className: "ptc-cp-delivery", "data-testid": "ptc-cp-delivery", key: "delivery" },
		          createElement(StatusRow, { label: t("delivery.batchId"), value: delivery.batchId, testId: "ptc-cp-delivery-batch" }),
		          createElement(StatusRow, { label: t("delivery.state"), value: delivery.state ?? "—", testId: "ptc-cp-delivery-state" }),
		          createElement(StatusRow, { label: t("delivery.releaseId"), value: delivery.releaseId ?? "—", testId: "ptc-cp-delivery-release" }),
		          createElement(StatusRow, { label: t("delivery.scope"), value: delivery.executionScope ?? "—", testId: "ptc-cp-delivery-scope" }),
		          createElement(StatusRow, { label: t("delivery.updatedAt"), value: delivery.updatedAt, testId: "ptc-cp-delivery-updated" })
		        )
		  );
		}

		const PROFILE_LABELS = Object.freeze({
		  'ptc-dft-expert': 'DFT 专家', 'ptc-schematic-expert': '原理图专家',
		  'strategy-expert': '策略专家', 'method-expert': '方法专家', 'rule-reviewer': '规则评审',
		  'ate-implementer': 'ATE 实现', 'compile-diagnostician': '编译诊断', 'evolution-expert': '演进专家',
		});

		function latestSmokeRun(runs, predicate) {
		  return [...runs].filter(predicate).sort((a, b) => String(b.runId).localeCompare(String(a.runId)))[0] ?? null;
		}

		const FROZEN_CANDIDATE_STORAGE_KEY = 'ptc-smoke-frozen-candidate';
		const STAGED_WORKFLOW_TEMPLATE_KEY = 'ptc-staged-workflow-template-release';
		function readFrozenCandidate() {
		  try {
		    const value = JSON.parse(window.localStorage.getItem(FROZEN_CANDIDATE_STORAGE_KEY) ?? 'null');
		    return value && typeof value.releaseId === 'string' && typeof value.stagingId === 'string'
		      && typeof value.bundleDigest === 'string' ? value : null;
		  } catch { return null; }
		}
		function readStagedWorkflowTemplate() {
		  try {
		    const value = JSON.parse(window.localStorage.getItem(STAGED_WORKFLOW_TEMPLATE_KEY) ?? 'null');
		    return value && typeof value.releaseId === 'string' && typeof value.manifestSha256 === 'string'
		      ? value : null;
		  } catch { return null; }
		}

		function WorkflowStatusBar({ state }) {
		  const run = latestSmokeRun(state.trainingRuns, item => item.purpose === 'smoke-training'
		    && item.target?.kind === 'pipeline');
		  const orchestration = run?.simpleOrchestration;
		  const stages = Array.isArray(orchestration?.stages) ? orchestration.stages : [];
		  const summary = workflowStatusSummary(orchestration);
		  return createElement('section', { className: 'ptc-cp-stage-status', 'data-testid': 'ptc-cp-workflow-status' },
		    createElement('strong', null, '团队工作流执行状态'),
		    createElement('div', null, run ? `${run.runId} · ${run.status} · ${orchestration?.scope === 'INPUT_SYNC_PILOT' ? '双专家 INPUT_SYNC 试点' : '八专家整链'} · SMOKE_ONLY · 业务门禁未通过` : '尚无烟测记录'),
		    run ? createElement('div', { 'data-testid': 'ptc-cp-workflow-progress' },
		      `已完成 ${summary.completed}/${summary.total} · 当前 ${summary.currentProfileId ?? '无'}${summary.currentStatus ? `（${summary.currentStatus}）` : ''}${summary.handoffFrom ? ` · 交接 ${summary.handoffFrom} → ${summary.currentProfileId}` : ''}`) : null,
		    orchestration?.reason ? createElement('div', { className: 'ptc-cp-error' }, orchestration.reason) : null,
		    stages.length ? createElement('ol', null, ...stages.map(stage => createElement('li', { key: stage.stage },
		      `${stage.stage} · ${stage.status} · ${(stage.tasks ?? []).map(task =>
		        `${task.profileId ?? task.role}: ${task.status}${typeof task.answer === 'number' ? ` / answer=${task.answer}` : ''}`
		      ).join('；')}`))) : null,
		    (orchestration?.auxiliaryTasks ?? []).map(task => createElement('div', { key: task.dispatchId },
		      `附加角色 ${task.profileId ?? task.role} · ${task.status}${typeof task.answer === 'number' ? ` / answer=${task.answer}` : ''}`)),
		    run?.outcome?.smokePassed === true ? createElement('div', { className: 'ptc-cp-notice' }, 'Captain 已确认本次所有数字 JSON 回执为 3；仅证明烟测控制链路，不代表业务通过。') : null);
		}

		function PublishedSmokeView({ state, store }) {
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState('');
		  const [frozenCandidate, setFrozenCandidate] = useState(readFrozenCandidate);
		  const execute = async () => {
		    setBusy(true); setNotice('');
		    try { const result = await executeTrainingReleaseRequest(); await store.refresh(); setNotice(`已从冻结版本启动发布态复跑 ${result.runId ?? ''}；业务门禁未通过。`); }
		    catch (error) { setNotice(`发布态复跑失败：${error.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  return createElement('div', { className: 'ptc-cp-publish-card', 'data-testid': 'ptc-cp-published-smoke' },
		    createElement('h3', null, '发布态（冻结版本只读复跑）'),
		    createElement(StatusRow, { label: '当前冻结版本', value: state.activeTrainingRelease?.releaseId ?? '未发布' }),
		    state.trainingReleaseError ? createElement('div', { className: 'ptc-cp-error' }, state.trainingReleaseError) : null,
		    createElement('button', { type: 'button', disabled: busy || !state.activeTrainingRelease || !!state.trainingReleaseError,
		      onClick: () => void execute(), 'data-testid': 'ptc-cp-execute-training-release' }, '复跑冻结版本 1+2 SMOKE_ONLY'),
		    notice ? createElement('div', { role: 'status', className: 'ptc-cp-notice' }, notice) : null,
		    ...(state.publishedSmokeRuns ?? []).map(run => createElement('div', { key: run.runId, className: 'ptc-cp-run' },
		      `${run.runId ?? '未知运行'} · ${run.status} · ${run.releaseId ?? '无版本'} · SMOKE_ONLY · 业务门禁未通过`)));
		}

		function PtcWorkbench({ state, store, sessionServices }) {
		  const [mode, setMode] = useState('training');
		  const [trainingMode, setTrainingMode] = useState('agent');
		  const [selectedProfile, setSelectedProfile] = useState(ARITHMETIC_PROFILES[0]);
		  const [workflowProfiles, setWorkflowProfiles] = useState(ARITHMETIC_PROFILES.slice(0, 2));
		  const [templateName, setTemplateName] = useState('ATE PTC 工作流烟测模板');
		  const [templateDraftSha, setTemplateDraftSha] = useState(null);
		  const [frozenTemplateSha, setFrozenTemplateSha] = useState(null);
		  const [savedTemplateSignature, setSavedTemplateSignature] = useState(null);
		  const [frozenCandidate, setFrozenCandidate] = useState(readFrozenCandidate);
		  const [stagedTemplateRelease, setStagedTemplateRelease] = useState(readStagedWorkflowTemplate);
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState('');
		  const sources = smokeSources(state.trainingRuns);
		  const templateSignature = JSON.stringify({ name: templateName.trim(), profileIds: workflowProfiles });
		  const templateDirty = savedTemplateSignature !== templateSignature;
		  const latestTemplateRun = (state.workflowTemplateRuns ?? []).find(item => item.templateId === 'ate-ptc') ?? null;
		  const latestPublishedTemplateRun = (state.publishedWorkflowTemplateRuns ?? [])[0] ?? null;
		  useEffect(() => {
		    let mounted = true;
		    void workflowTemplateRequest('read', { templateId: 'ate-ptc' }).then(result => {
		      if (!mounted || !result.template) return;
		      setTemplateName(result.template.name);
		      setWorkflowProfiles(result.template.profileIds);
		      setTemplateDraftSha(result.sha256);
		      setFrozenTemplateSha(result.frozenSha256 ?? null);
		      setSavedTemplateSignature(JSON.stringify({ name: result.template.name, profileIds: result.template.profileIds }));
		    }).catch(() => {});
		    return () => { mounted = false; };
		  }, []);
		  const selectedWorkflowIds = new Set(workflowProfiles);
		  const pilotSelection = selectedWorkflowIds.size === 2
		    && ARITHMETIC_PROFILES.slice(0, 2).every(id => selectedWorkflowIds.has(id));
		  const fullSelection = selectedWorkflowIds.size === ARITHMETIC_PROFILES.length
		    && ARITHMETIC_PROFILES.every(id => selectedWorkflowIds.has(id));
		  const pilotPassed = !!latestSmokeRun(state.trainingRuns, item => item.purpose === 'smoke-training'
		    && item.target?.kind === 'pipeline' && item.target.toStage === 'INPUT_SYNC'
		    && item.status === 'completed' && item.outcome?.smokePassed === true
		    && item.simpleOrchestration?.scope === 'INPUT_SYNC_PILOT');
		  const selectedProfileRun = latestSmokeRun(state.trainingRuns, item => item.purpose === 'smoke-training'
		    && item.target?.kind === 'profile' && item.target.profileId === selectedProfile);
		  const run = async (action, doneText) => {
		    setBusy(true); setNotice('');
		    try { const result = await action(); await store.refresh(); setNotice(`${doneText}${result?.runId ? ` · ${result.runId}` : ''}`); }
		    catch (error) { setNotice(`未完成：${error?.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  const openSession = async (kind, identity, request, title) => {
		    setBusy(true); setNotice('正在创建/打开 DSH 原生会话…');
		    try {
		      const workspace = await createPtcSessionWorkspaceRequest(request);
		      await openPtcNativeSession(sessionServices, workspace, { key: ptcSessionKey(kind, identity), title });
		      setNotice(`已打开 DSH 原生会话：${title}`);
		      window.setTimeout(() => document.querySelector('[data-testid="ptc-cp-panel"]')?.removeAttribute('open'), 0);
		    } catch (error) { setNotice(`会话未打开：${error?.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  const freezeProfile = profileId => void run(async () => {
		    const created = await createTrainingRunRequest({ kind: 'profile', profileId }, { purpose: 'smoke-training' });
		    await executeProfileSmokeRequest(created.runId);
		    return created;
		  }, `${PROFILE_LABELS[profileId]}独立 1+2 验证已受理；请以运行终态为准（SMOKE_ONLY）`);
		  const launchWorkflow = () => void run(async () => {
		    if (!fullSelection) throw new Error('八专家整链须先勾选全部八位 Agent');
		    const missing = ARITHMETIC_PROFILES.filter(id => !sources.profileRunIds[id]);
		    if (missing.length) throw new Error(`先完成单 Agent 烟测：${missing.join('、')}`);
		    const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' }, { purpose: 'smoke-training' });
		    await executeSimpleOrchestrationRequest(created.runId, sources.profileRunIds);
		    return created;
		  }, '八专家整链 1+2 烟测已派发；业务门禁未通过');
		  const launchPilot = () => void run(async () => {
		    if (!pilotSelection) throw new Error('双专家试点须只勾选 DFT 与原理图专家');
		    const pair = ARITHMETIC_PROFILES.slice(0, 2);
		    const missing = pair.filter(id => !sources.profileRunIds[id]);
		    if (missing.length) throw new Error(`先完成双专家单体烟测：${missing.join('、')}`);
		    const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' }, { purpose: 'smoke-training' });
		    await executeSimpleOrchestrationRequest(created.runId,
		      Object.fromEntries(pair.map(id => [id, sources.profileRunIds[id]])), { pilot: true });
		    return created;
		  }, '双专家 INPUT_SYNC 顺序交接烟测已派发；业务门禁未通过');
		  const freezeWorkflow = () => void run(async () => {
		    if (!fullSelection) throw new Error('冻结整链须勾选全部八位 Agent');
		    if (!sources.pipelineRunId || ARITHMETIC_PROFILES.some(id => !sources.pipelineProfileRunIds[id])) {
		      throw new Error('须先完成八专家单体和整链烟测');
		    }
		    const candidate = await freezeTrainingReleaseRequest(sources.pipelineProfileRunIds, sources.pipelineRunId);
		    window.localStorage.setItem(FROZEN_CANDIDATE_STORAGE_KEY, JSON.stringify(candidate));
		    setFrozenCandidate(candidate);
		    return candidate;
		  }, '工作流版本已独立冻结，尚未发布');
		  const saveTemplate = () => void run(async () => {
		    const result = await workflowTemplateRequest('save', { expectedSha256: templateDraftSha,
		      template: { templateId: 'ate-ptc', name: templateName, profileIds: workflowProfiles,
		        instruction: '1+2等于几，把答案写在JSON里', expectedAnswer: 3 } });
		    setTemplateDraftSha(result.sha256);
		    setSavedTemplateSignature(templateSignature);
		    setFrozenTemplateSha(null);
		    return result;
		  }, '已保存工作流候选；尚未冻结或发布');
		  const freezeTemplate = () => void run(async () => {
		    if (templateDirty || !templateDraftSha) throw new Error('先保存当前工作流候选');
		    const result = await workflowTemplateRequest('freeze', { templateId: 'ate-ptc', sha256: templateDraftSha });
		    setFrozenTemplateSha(result.versionSha256);
		    return result;
		  }, '已冻结工作流模板；尚未发布');
		  const executeTemplate = () => void run(async () => {
		    if (templateDirty || !frozenTemplateSha) throw new Error('先保存并冻结当前工作流模板');
		    return workflowTemplateRequest('execute', { templateId: 'ate-ptc', versionSha256: frozenTemplateSha });
		  }, '任意 Agent 工作流 1+2 烟测已派发');
		  const controlTemplate = action => void run(() => workflowTemplateRequest('control',
		    { runId: latestTemplateRun?.runId, action }), `工作流${action}请求已受理`);
		  const stageTemplateRelease = () => void run(async () => {
		    if (!latestTemplateRun || latestTemplateRun.status !== 'completed' || latestTemplateRun.smokePassed !== true) {
		      throw new Error('先完成任意 Agent 模板的 1+2 烟测');
		    }
		    const staged = await workflowTemplateReleaseRequest('stage', { runId: latestTemplateRun.runId });
		    window.localStorage.setItem(STAGED_WORKFLOW_TEMPLATE_KEY, JSON.stringify(staged));
		    setStagedTemplateRelease(staged);
		    return staged;
		  }, '已冻结发布候选；尚未激活');
		  const activateTemplateRelease = () => void run(async () => {
		    if (!stagedTemplateRelease) throw new Error('没有待激活的工作流模板版本');
		    const result = await workflowTemplateReleaseRequest('activate', {
		      releaseId: stagedTemplateRelease.releaseId,
		      manifestSha256: stagedTemplateRelease.manifestSha256,
		    });
		    window.localStorage.removeItem(STAGED_WORKFLOW_TEMPLATE_KEY);
		    setStagedTemplateRelease(null);
		    return result;
		  }, '任意 Agent 工作流模板已发布激活');
		  const executePublishedTemplate = () => void run(() =>
		    workflowTemplateReleaseRequest('execute', {}), '冻结模板发布态新运行已派发');
		  const controlPublishedTemplate = action => void run(() => workflowTemplateReleaseRequest('control',
		    { runId: latestPublishedTemplateRun?.runId, action }), `发布态工作流${action}请求已受理`);
		  const activateWorkflow = () => void run(async () => {
		    if (!frozenCandidate?.stagingId) throw new Error('没有待发布的冻结版本');
		    const active = await activateTrainingReleaseRequest(frozenCandidate.stagingId);
		    window.localStorage.removeItem(FROZEN_CANDIDATE_STORAGE_KEY);
		    setFrozenCandidate(null);
		    return active;
		  }, '已激活冻结版本');
		  const modes = [['training', '训练模式'], ['publish', '发布模式'], ['engineering', '工程模式']];
		  const button = (id, label, active, onClick, extra = {}) => createElement('button', { key: id, type: 'button',
		    className: active ? 'ptc-cp-tab-active' : '', 'data-testid': `ptc-cp-mode-${id}`, onClick, ...extra }, label);
		  const agentList = createElement('nav', { className: 'ptc-cp-roster', 'aria-label': 'Agent 列表', 'data-testid': 'ptc-cp-agent-roster' },
		    ...ARITHMETIC_PROFILES.map(id => createElement('button', { key: id, type: 'button',
		      disabled: busy || mode !== 'training', className: selectedProfile === id ? 'ptc-cp-tab-active' : '',
		      'data-testid': `ptc-cp-agent-${id}`,
		      onClick: () => { setSelectedProfile(id); void openSession('agent', id, { mode: 'agent', profileId: id }, `PTC Training · ${PROFILE_LABELS[id]}`); },
		    }, `${PROFILE_LABELS[id]} · ${id}`)));
		  let content;
		  if (mode === 'training') {
		    content = createElement('div', { className: 'ptc-cp-layout' }, agentList,
		      createElement('main', { className: 'ptc-cp-workspace-main' },
		        createElement('div', { className: 'ptc-cp-subtabs' },
		          button('single', '单 Agent 训练', trainingMode === 'agent', () => setTrainingMode('agent')),
		          button('workflow', 'Agent 工作流训练', trainingMode === 'workflow', () => setTrainingMode('workflow'))),
		        trainingMode === 'agent' ? createElement('section', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-agent-training' },
		          createElement('h3', null, `${PROFILE_LABELS[selectedProfile]} · 独立训练`),
		          createElement('p', null, '点左侧专家立即打开其专属 DSH 会话；会话工作目录绑定该专家草稿目录。聊天中逐步讨论/修改，下面的“保存训练草稿”单独保存候选内容。'),
		          createElement('button', { type: 'button', disabled: busy, onClick: () => void openSession('agent', selectedProfile,
		            { mode: 'agent', profileId: selectedProfile }, `PTC Training · ${PROFILE_LABELS[selectedProfile]}`),
		          'data-testid': 'ptc-cp-open-selected-agent' }, '打开独立 DSH 训练会话'),
		          createElement('div', { className: 'ptc-cp-agent-status' }, createElement('span', null, '单 Agent 1+2 验证/冻结快照'),
		            createElement('button', { type: 'button', disabled: busy, onClick: () => freezeProfile(selectedProfile),
		              'data-testid': `ptc-cp-freeze-profile-${selectedProfile}` }, '冻结此版并验证')),
		          selectedProfileRun ? createElement('div', { 'data-testid': 'ptc-cp-selected-profile-run' },
		            `${selectedProfileRun.runId} · ${selectedProfileRun.status} · ${selectedProfileRun.outcome?.smokePassed === true ? '数字 JSON answer=3 已验证' : '等待新鲜回执/未通过'} · SMOKE_ONLY`) : null,
		          createElement(DraftEditor, { key: selectedProfile, profileId: selectedProfile }),
		          createElement('p', null, '冻结会新建一次 SMOKE_ONLY 训练并把本次 Agent 文件、哈希、模型数字 JSON 答案封存到不可变运行快照；它不发布业务版本。'))
		          : createElement('section', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-workflow-training' },
		            createElement('h3', null, '工作流协作训练'),
		            createElement('p', null, '勾选并排序任意 Agent，可保存、冻结和执行独立的 1+2 工作流模板。下方原有的双专家试点与八专家整链按钮仍按 PTC 阶段注册表运行；它们和任意组合模板烟测是两条不同链路，均不代表真实业务门禁通过。会话中的建议须明确保存后才会成为候选。'),
		            createElement('div', { className: 'ptc-cp-workflow-select' }, ...ARITHMETIC_PROFILES.map(id => createElement('label', { key: id },
		              createElement('input', { type: 'checkbox', checked: workflowProfiles.includes(id), disabled: busy,
		                onChange: event => setWorkflowProfiles(old => event.target.checked ? [...new Set([...old, id])] : old.filter(item => item !== id)) }),
		              PROFILE_LABELS[id]))),
		            createElement('div', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-generic-workflow-template' },
		              createElement('h4', null, '任意 Agent 顺序工作流 · SMOKE_ONLY'),
		              createElement('label', null, '模板名称 ', createElement('input', { value: templateName,
		                onChange: event => setTemplateName(event.target.value), maxLength: 120,
		                'data-testid': 'ptc-cp-template-name' })),
		              createElement('ol', { 'data-testid': 'ptc-cp-template-order' }, ...workflowProfiles.map((id, index) =>
		                createElement('li', { key: id }, `${index + 1}. ${PROFILE_LABELS[id] ?? id} `,
		                  createElement('button', { type: 'button', disabled: busy || index === 0,
		                    onClick: () => setWorkflowProfiles(old => { const next = [...old]; [next[index - 1], next[index]] = [next[index], next[index - 1]]; return next; }) }, '上移'),
		                  createElement('button', { type: 'button', disabled: busy || index === workflowProfiles.length - 1,
		                    onClick: () => setWorkflowProfiles(old => { const next = [...old]; [next[index + 1], next[index]] = [next[index], next[index + 1]]; return next; }) }, '下移')))),
		              createElement('button', { type: 'button', disabled: busy || !workflowProfiles.length || !templateDirty,
		                onClick: saveTemplate, 'data-testid': 'ptc-cp-save-workflow-template' }, '保存工作流草稿'),
		              createElement('button', { type: 'button', disabled: busy || templateDirty || !templateDraftSha,
		                onClick: freezeTemplate, 'data-testid': 'ptc-cp-freeze-workflow-template' }, '冻结工作流模板（不发布）'),
		              createElement('button', { type: 'button', disabled: busy || templateDirty || !frozenTemplateSha,
		                onClick: executeTemplate, 'data-testid': 'ptc-cp-execute-workflow-template' }, '执行所选 Agent 1+2 烟测'),
		              createElement('div', null, `草稿 SHA-256：${templateDraftSha ?? '未保存'} · 冻结 SHA-256：${frozenTemplateSha ?? '未冻结'}`),
		              latestTemplateRun ? createElement('div', { 'data-testid': 'ptc-cp-template-run-status' },
		                `${latestTemplateRun.runId} · ${latestTemplateRun.status} · 已完成 ${latestTemplateRun.steps?.filter(step => step.status === 'completed').length ?? 0}/${latestTemplateRun.steps?.length ?? 0} · 当前 ${latestTemplateRun.currentProfileId ?? '无'}${latestTemplateRun.reason ? ` · ${latestTemplateRun.reason}` : ''}`) : null,
		              latestTemplateRun?.steps?.length ? createElement('ol', { 'data-testid': 'ptc-cp-template-step-status' },
		                ...latestTemplateRun.steps.map(step => createElement('li', { key: step.index },
		                  `${PROFILE_LABELS[step.profileId] ?? step.profileId} · ${step.status}${step.answer === 3 ? ' · answer=3' : ''}${step.upstreamEvidenceSha256 ? ` · 上游 SHA-256 ${step.upstreamEvidenceSha256.slice(0, 12)}…` : ''}`))) : null,
		              latestTemplateRun && ['running', 'paused'].includes(latestTemplateRun.status)
		                ? createElement('div', null,
		                  createElement('button', { type: 'button', disabled: busy || latestTemplateRun.status !== 'running',
		                    onClick: () => controlTemplate('pause') }, '暂停'),
		                  createElement('button', { type: 'button', disabled: busy || latestTemplateRun.status !== 'paused',
		                    onClick: () => controlTemplate('resume') }, '继续'),
		                  createElement('button', { type: 'button', disabled: busy || latestTemplateRun.status !== 'running',
		                    onClick: () => controlTemplate('stop') }, '停止')) : null),
		            createElement('button', { type: 'button', disabled: busy || !workflowProfiles.length,
		              onClick: () => void openSession('workflow', `v2:${workflowProfiles.join(',')}`,
		                { mode: 'workflow', profileIds: workflowProfiles }, `PTC Training · 工作流 · ${workflowProfiles.length} Agents`),
		              'data-testid': 'ptc-cp-open-workflow-session' }, '打开工作流 DSH 会话'),
		            createElement(WorkflowStatusBar, { state }),
		            createElement('button', { type: 'button', disabled: busy || !pilotSelection || ARITHMETIC_PROFILES.slice(0, 2).some(id => !sources.profileRunIds[id]),
		              onClick: launchPilot, 'data-testid': 'ptc-cp-start-input-sync-pilot' }, '执行双专家 INPUT_SYNC 交接烟测'),
		            createElement('button', { type: 'button', disabled: busy || !fullSelection || !pilotPassed || ARITHMETIC_PROFILES.some(id => !sources.profileRunIds[id]),
		              onClick: launchWorkflow, 'data-testid': 'ptc-cp-start-simple-orchestration' }, '执行八专家整链 1+2 烟测'),
		            createElement('button', { type: 'button', disabled: busy || !fullSelection || !sources.pipelineRunId
		              || ARITHMETIC_PROFILES.some(id => !sources.pipelineProfileRunIds[id]),
		              onClick: freezeWorkflow, 'data-testid': 'ptc-cp-freeze-workflow' }, '冻结当前整链版本（不发布）'),
		            frozenCandidate ? createElement('div', { className: 'ptc-cp-notice', 'data-testid': 'ptc-cp-frozen-candidate' },
		              `已冻结待发布：${frozenCandidate.releaseId} · SHA-256 ${frozenCandidate.bundleDigest}`) : null,
		            createElement('p', null, '通过标准：整链每个 child receipt 的 JSON answer 都是数字 3，Captain 验证通过；结果仅为 SMOKE_ONLY。'))),
		        notice ? createElement('div', { className: 'ptc-cp-notice', role: 'status' }, notice) : null);
		  } else if (mode === 'publish') {
		    content = createElement('section', { className: 'ptc-cp-publish-card', 'data-testid': 'ptc-cp-publish-mode' },
		      createElement('h3', null, '发布模式'),
		      createElement('div', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-template-publish' },
		        createElement('h4', null, '任意 Agent 工作流模板发布'),
		        createElement('p', null, '仅发布完成 1+2 烟测的冻结模板及精确 Agent 回执绑定；真实业务门禁仍为 false。'),
		        createElement('button', { type: 'button', disabled: busy || latestTemplateRun?.status !== 'completed'
		          || latestTemplateRun?.smokePassed !== true, onClick: stageTemplateRelease,
		          'data-testid': 'ptc-cp-stage-template-release' }, '冻结发布候选'),
		        stagedTemplateRelease ? createElement('div', null,
		          `待激活 ${stagedTemplateRelease.releaseId} · SHA-256 ${stagedTemplateRelease.manifestSha256}`,
		          createElement('button', { type: 'button', disabled: busy, onClick: activateTemplateRelease,
		            'data-testid': 'ptc-cp-activate-template-release' }, '发布/激活模板版本')) : null,
		        createElement(StatusRow, { label: '当前模板发布版',
		          value: state.activeWorkflowTemplateRelease?.releaseId ?? '未发布' })),
		      createElement('p', null, '发布模式使用已冻结的八专家快照。当前后端发布动作会先复核快照完整性与全部 1+2 回执，再激活版本；没有业务产物或业务门禁。'),
		      createElement('button', { type: 'button', disabled: busy,
		        onClick: () => void openSession('publish', 'review', { mode: 'publish' }, 'PTC Publish · 冻结版本审核'),
		        'data-testid': 'ptc-cp-open-publish-session' }, '打开隔离的发布审核 DSH 会话'),
		      frozenCandidate ? createElement('div', { className: 'ptc-cp-agent-status' },
		        createElement('span', null, `待发布冻结版本 ${frozenCandidate.releaseId} · ${frozenCandidate.bundleDigest}`),
		        createElement('button', { type: 'button', disabled: busy, onClick: activateWorkflow,
		          'data-testid': 'ptc-cp-activate-frozen-workflow' }, '发布/激活此冻结版本'))
		        : createElement('p', null, '尚无待发布的冻结工作流版本。先在“训练模式 → Agent 工作流训练”完成整链并单独冻结，再回到此处发布。'),
		      createElement(PublishedSmokeView, { state, store }));
		  } else {
		    const releaseId = state.activeWorkflowTemplateRelease?.releaseId ?? state.activeTrainingRelease?.releaseId;
		    content = createElement('section', { className: 'ptc-cp-publish-card', 'data-testid': 'ptc-cp-engineering-mode' },
		      createElement('h3', null, '工程模式'),
		      createElement('p', null, '工程会话绑定当前已冻结版本的标识，并使用隔离目录；不会把已冻结 Agent/编排目录作为可写工作区。这里用于观察/沟通，不提供候选规则编辑入口。'),
		      createElement(StatusRow, { label: '固定版本', value: releaseId ?? '尚无已冻结版本' }),
		      createElement('div', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-template-engineering' },
		        createElement('h4', null, '任意 Agent 工作流模板 · 发布态'),
		        createElement(StatusRow, { label: '固定模板版本',
		          value: state.activeWorkflowTemplateRelease?.releaseId ?? '未发布' }),
		        state.workflowTemplateReleaseError ? createElement('div', { className: 'ptc-cp-error' },
		          state.workflowTemplateReleaseError) : null,
		        createElement('button', { type: 'button', disabled: busy || !state.activeWorkflowTemplateRelease,
		          onClick: executePublishedTemplate, 'data-testid': 'ptc-cp-execute-published-template' },
		        '从冻结模板新运行 1+2'),
		        latestPublishedTemplateRun ? createElement('div', { 'data-testid': 'ptc-cp-published-template-status' },
		          `${latestPublishedTemplateRun.runId} · ${latestPublishedTemplateRun.status} · 已完成 ${latestPublishedTemplateRun.steps?.filter(step => step.status === 'completed').length ?? 0}/${latestPublishedTemplateRun.steps?.length ?? 0} · 当前 ${latestPublishedTemplateRun.currentProfileId ?? '无'}${latestPublishedTemplateRun.reason ? ` · ${latestPublishedTemplateRun.reason}` : ''}`) : null,
		        latestPublishedTemplateRun?.steps?.length ? createElement('ol', { 'data-testid': 'ptc-cp-published-template-steps' },
		          ...latestPublishedTemplateRun.steps.map(step => createElement('li', { key: step.index },
		            `${PROFILE_LABELS[step.profileId] ?? step.profileId} · ${step.status}${step.answer === 3 ? ' · answer=3' : ''}${step.upstreamEvidenceSha256 ? ` · 上游 SHA-256 ${step.upstreamEvidenceSha256.slice(0, 12)}…` : ''}`))) : null,
		        latestPublishedTemplateRun && ['running', 'paused'].includes(latestPublishedTemplateRun.status)
		          ? createElement('div', null,
		            createElement('button', { type: 'button', disabled: busy || latestPublishedTemplateRun.status !== 'running',
		              onClick: () => controlPublishedTemplate('pause') }, '暂停'),
		            createElement('button', { type: 'button', disabled: busy || latestPublishedTemplateRun.status !== 'paused',
		              onClick: () => controlPublishedTemplate('resume') }, '继续'),
		            createElement('button', { type: 'button', disabled: busy || latestPublishedTemplateRun.status !== 'running',
		              onClick: () => controlPublishedTemplate('stop') }, '停止')) : null),
		      createElement('button', { type: 'button', disabled: busy || !releaseId,
		        onClick: () => void openSession('engineering', releaseId, { mode: 'engineering', releaseId }, `PTC Engineering · ${releaseId}`),
		        'data-testid': 'ptc-cp-open-engineering-session' }, '打开工程沟通 DSH 会话'),
		      createElement(PublishedSmokeView, { state, store }));
		  }
		  return createElement('div', { className: 'ptc-cp-workbench', 'data-testid': 'ptc-cp-workbench' },
		    createElement('div', { className: 'ptc-cp-mode-tabs', 'data-testid': 'ptc-cp-mode-tabs' },
		      ...modes.map(([id, label]) => button(id, label, mode === id, () => setMode(id)))),
		    createElement('div', { className: 'ptc-cp-status' },
		      createElement(StatusRow, { label: '当前发布版', value: state.activeTrainingRelease?.releaseId ?? '无' }),
		      createElement(StatusRow, { label: '训练运行', value: String(state.trainingRuns.length) }),
		      createElement(StatusRow, { label: '烟测边界', value: '1+2 JSON / SMOKE_ONLY / 业务门禁未通过' })),
		    content);
		}

		/** Native DSH workbench for agent training, workflow rehearsal and frozen replay. */
		function PtcControlPanel({ store, t, onNavigate, sessionServices }) {
		  useSyncExternalStore(store.subscribe, store.getRevision, store.getRevision);
		  const state = store.getSnapshot();
		  const error = store.getLastError();
		  const [view, setView] = useState("training");

		  useEffect(() => {
		    store.start();
		    return () => store.stop();
		  }, [store]);

		  const switchTo = (next) => {
		    setView(next);
		    if (typeof onNavigate === "function") onNavigate(next);
		  };

		  const tabButton = (id, label) =>
		    createElement(
		      "button",
		      {
		        key: id,
		        type: "button",
		        className: view === id ? "ptc-cp-tab ptc-cp-tab-active" : "ptc-cp-tab",
		        "data-testid": `ptc-cp-tab-${id}`,
		        onClick: () => switchTo(id)
		      },
		      label
		    );

		  const release = state.activeRelease;

		  return createElement(
		    "div",
		    { className: "ptc-cp-host" },
		    createElement("style", { type: "text/css" }, PANEL_CSS),
		    createElement(
		    "details",
		    { className: "ptc-cp-panel", "data-testid": "ptc-cp-panel" },
		    createElement("summary", null, "PTC 控制面 · 点击展开/收起"),
		    createElement("div", { className: "ptc-cp-header", key: "header" }, t("panel.title")),
		    createElement(
		      "div",
		      { className: "ptc-cp-status", key: "status" },
		      createElement(StatusRow, { label: t("status.identity"), value: state.identity, testId: "ptc-cp-identity" }),
		      createElement(StatusRow, {
		        label: t("status.activeRelease"),
		        value: release
		          ? `${release.releaseId ?? "—"} (${release.manifestDigest ?? "—"})`
		          : t("status.noRelease"),
		        testId: "ptc-cp-active-release"
		      }),
		      createElement(StatusRow, {
		        label: t("status.trainingRuns"),
		        value: String(state.trainingRuns.length),
		        testId: "ptc-cp-training-runs"
		      }),
		      createElement(StatusRow, {
		        label: t("status.delivery"),
		        value: state.delivery === null ? t("delivery.none") : state.delivery.batchId,
		        testId: "ptc-cp-delivery-summary"
		      })
		    ),
		      createElement(PtcWorkbench, { state, store, sessionServices, key: 'workbench' }),
		    error
		      ? createElement(
		          "div",
		          { className: "ptc-cp-error", "data-testid": "ptc-cp-error", key: "error" },
		          `${t("status.error")}: ${error}`
		        )
		      : null
		    )
		  );
		}

		// Trainer API v1. Independent of the legacy SMOKE_ONLY store.
		const TRAINER_UNBOUND_NOTICE = '当前原生会话未绑定框架目标，请选择左侧 Agent 或工作流。';

		function trainerRequestId() {
		  return globalThis.crypto.randomUUID();
		}

		function createTrainerApi({ fetchImpl = globalThis.fetch, baseUrl = '/api/ptc-control/trainer' } = {}) {
		  return async (operation, args = {}, { signal } = {}) => {
		    const response = await fetchImpl(`${baseUrl}/${operation}`, {
		      method: 'POST', credentials: 'same-origin', signal,
		      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
		      body: JSON.stringify(args)
		    });
		    const body = await response.json();
		    if (!response.ok || body?.ok !== true) {
		      const error = new Error(body?.error?.message ?? `Trainer HTTP ${response.status}`);
		      error.code = body?.error?.code ?? 'TRANSPORT_ERROR';
		      error.details = body?.error?.details;
		      throw error;
		    }
		    return body.value;
		  };
		}

		function trainerTargetKey(target) {
		  return JSON.stringify([target.projectId, target.targetKind, target.targetId]);
		}

		function trainerControlState(run, action) {
		  const control = run?.controls?.[action];
		  return { allowed: control?.allowed === true, reason: control?.reason || (run ? '服务端未允许此操作' : '尚未选择运行') };
		}

		function createTrainerStore({ api = createTrainerApi(), projectId = 'synthetic-lab', pollMs = 5000 } = {}) {
		  const listeners = new Set();
		  let state = { enabled: false, surfaceVisible: false, projectId, mode: 'training', target: null, project: null, binding: null,
		    selectedRunId: null, run: null, runs: [], nextRunsCursor: null, events: [], eventsCursor: 0, assets: null, releases: [], frozenVersions: [],
		    loading: false, busy: false, error: null, readError: null, notice: '', detailsVisible: true };
		  let generation = 0;
		  let controller = null;
		  let timer = null;
		  let disposed = false;
		  let reading = false;
		  const uncertainRequests = new Map();
		  const update = patch => {
		    if (disposed) return;
		    state = { ...state, ...patch };
		    listeners.forEach(listener => listener());
		  };
		  function invalidate() {
		    generation += 1;
		    controller?.abort();
		    controller = null;
		    reading = false;
		  }
		  async function refresh() {
		    if (disposed || !state.enabled || reading) return;
		    const epoch = generation;
		    const selected = state;
		    const pending = new AbortController();
		    controller = pending;
		    reading = true;
		    update({ loading: true });
		    try {
		      const identity = { projectId, ...selected.target, mode: selected.mode };
		      // The project context intentionally returns only workflow summaries. Load the
		      // selected workflow definition separately so the workbench can display its
		      // real step count and labels instead of falling back to a fabricated count.
		      // Asset loading is supplemental: a missing/invalid asset must not hide an
		      // otherwise valid project context or run history.
		      const workflowAssetPath = selected.target?.targetKind === 'workflow'
		        ? `workflows/${selected.target.targetId}.json` : null;
		      const workflowTestPath = selected.target?.targetKind === 'workflow'
		        ? `tests/${selected.target.targetId}.json` : null;
		      const targetAssetsPromise = workflowAssetPath
		        ? api('assets', { projectId, paths: [workflowAssetPath] }, { signal: pending.signal })
		          .then(value => ({ value }), error => ({ error }))
		        : Promise.resolve({ value: null });
		      // Test inputs are optional metadata. Read them separately so a workflow
		      // without a test fixture still loads and remains runnable with explicit
		      // user input instead of failing the whole candidate asset read.
		      const workflowTestsPromise = workflowTestPath
		        ? api('assets', { projectId, paths: [workflowTestPath] }, { signal: pending.signal })
		          .then(value => ({ value }), error => ({ error }))
		        : Promise.resolve({ value: null });
		      const [context, history, detail, eventPage, liveBinding, targetAssetsResult, workflowTestsResult] = await Promise.all([
		        api('context', identity, { signal: pending.signal }),
		        api('runs', { projectId }, { signal: pending.signal }),
		        selected.selectedRunId ? api('runs', { projectId, runId: selected.selectedRunId }, { signal: pending.signal }) : null,
		        selected.selectedRunId ? api('events', { projectId, runId: selected.selectedRunId, cursor: selected.eventsCursor }, { signal: pending.signal }) : null,
		        selected.binding ? api('bind-session', { projectId, sessionId: selected.binding.sessionId }, { signal: pending.signal }) : null,
		        targetAssetsPromise,
		        workflowTestsPromise
		      ]);
		      if (epoch !== generation || disposed) return;
		      if (liveBinding) {
		        if (liveBinding.sessionId !== selected.binding.sessionId || liveBinding.presetId !== selected.binding.presetId || liveBinding.mode !== selected.mode || trainerTargetKey(liveBinding) !== trainerTargetKey(selected.target)) throw new Error('会话恢复身份不匹配');
		        if (liveBinding.selectedRunId !== selected.selectedRunId) {
		          select(selected.target, selected.mode, liveBinding.selectedRunId ?? null);
		          update({ binding: liveBinding });
		          return;
		        }
		      }
		      const run = detail?.run ?? detail;
		      if (run && (run.runId !== selected.selectedRunId || run.projectId !== projectId)) throw new Error('运行响应身份不匹配');
		      if (eventPage?.runId && eventPage.runId !== selected.selectedRunId) throw new Error('事件响应身份不匹配');
		      const runs = [...new Map([...(history.runs ?? []), ...state.runs].map(item => [item.runId, item])).values()];
		      // New page values take precedence; preserve already loaded older history.
		      for (const item of history.runs ?? []) { const index = runs.findIndex(run => run.runId === item.runId); runs[index] = item; }
		      const events = [...new Map([...selected.events, ...(eventPage?.events ?? [])].map(item => [item.seq, item])).values()].slice(-1000);
		      const workflowAssets = targetAssetsResult?.value ?? null;
		      const workflowTests = workflowTestsResult?.value ?? null;
		      const targetAssets = workflowAssets || workflowTests
		        ? { ...(workflowAssets ?? {}), files: { ...(workflowAssets?.files ?? {}), ...(workflowTests?.files ?? {}) } }
		        : null;
		      let project = context.project ?? context;
		      if (workflowAssetPath && targetAssets?.files?.[workflowAssetPath]) {
		        try {
		          const definition = JSON.parse(targetAssets.files[workflowAssetPath]);
		          if (Array.isArray(definition.steps)) {
		            project = { ...project, workflows: (project.workflows ?? []).map(item =>
		              item.workflowId === selected.target.targetId ? { ...item, ...definition, steps: definition.steps } : item) };
		          }
		        } catch { /* the editor will expose malformed candidate content */ }
		      }
		      const assetReadError = targetAssetsResult?.error?.message;
		      update({ project, ...(workflowAssetPath ? { assets: targetAssets } : {}), frozenVersions: (context.frozenVersions ?? []).map(version => ({ projectId, ...version })), ...(liveBinding ? { binding: liveBinding } : {}), runs, nextRunsCursor: history.nextCursor == null ? null : runs.length, run,
		        events, eventsCursor: eventPage?.cursor ?? selected.eventsCursor, loading: false, readError: assetReadError ?? null });
		    } catch (error) {
		      if (epoch === generation && !disposed && error.name !== 'AbortError') update({ loading: false, readError: error.message });
		    } finally {
		      if (epoch === generation) { reading = false; controller = null; }
		    }
		  }
		  function select(target, mode = state.mode, selectedRunId = null) {
		    invalidate();
		    update({ target, mode, selectedRunId, binding: null, run: null, events: [], eventsCursor: 0, assets: null, error: null, readError: null,
		      ...(target && state.target && trainerTargetKey(target) === trainerTargetKey(state.target) ? {} : { frozenVersion: null }) });
		    void refresh();
		  }
		  async function perform(operation, args = {}, { mutation = true } = {}) {
		    if (state.busy) throw new Error('上一操作尚未完成');
		    const epoch = generation;
		    const input = { projectId, ...state.target, mode: state.mode, ...args };
		    const retryKey = JSON.stringify([operation, input]);
		    const requestId = mutation ? args.requestId ?? uncertainRequests.get(retryKey) ?? trainerRequestId() : null;
		    if (mutation) uncertainRequests.set(retryKey, requestId);
		    update({ busy: true, error: null, notice: '' });
		    try {
		      const result = await api(operation, { ...input, ...(mutation ? { requestId } : {}) });
		      uncertainRequests.delete(retryKey);
		      if (epoch === generation) {
		        if (operation === 'assets') update({ assets: result });
		        if (operation === 'releases') update({ releases: result.releases ?? result });
		        if (operation === 'freeze') update({ frozenVersion: result,
		          frozenVersions: [...state.frozenVersions.filter(item => item.frozenVersionId !== result.frozenVersionId), { ...input, ...result }] });
		        update({ notice: operation === 'run' ? `已受理运行 ${result.runId}，以运行终态为准` : '操作已完成' });
		      }
		      return result;
		    } catch (error) {
		      if (epoch === generation) update({ error: `${error.code ? `${error.code}：` : ''}${error.message}` });
		      throw error;
		    } finally {
		      update({ busy: false });
		      if (epoch === generation) void refresh();
		    }
		  }
		  return {
		    api, getSnapshot: () => state,
		    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
		    refresh, select, perform, update,
		    async loadMoreRuns() {
		      if (state.nextRunsCursor == null || state.busy) return;
		      const epoch = generation;
		      const page = await perform('runs', { cursor: state.nextRunsCursor }, { mutation: false });
		      if (epoch === generation) update({ runs: [...new Map([...state.runs, ...(page.runs ?? [])].map(item => [item.runId, item])).values()], nextRunsCursor: page.nextCursor });
		    },
		    enable(enabled = true) {
		      invalidate(); update({ enabled, surfaceVisible: enabled, loading: false });
		      if (timer !== null) clearInterval(timer);
		      timer = enabled ? setInterval(() => { void refresh(); }, pollMs) : null;
		      if (enabled) void refresh();
		    },
		    setBinding(binding) {
		      if (binding?.projectId !== projectId || !state.target || trainerTargetKey(binding) !== trainerTargetKey(state.target) || binding.mode !== state.mode) return false;
		      update({ binding, ...(state.notice === TRAINER_UNBOUND_NOTICE ? { notice: '' } : {}) }); return true;
		    },
		    dispose() { invalidate(); if (timer !== null) clearInterval(timer); disposed = true; listeners.clear(); uncertainRequests.clear(); }
		  };
		}

		function trainerNativeKey(target, presetId, mode) {
		  return `trainer-native-v2:${JSON.stringify([target.projectId, presetId, mode, target.targetKind, target.targetId, 1])}`;
		}

		function trainerPreset(targetKind, mode, trainer = false) {
		  return mode === 'engineering' || mode === 'published' ? 'framework-observer'
		    : trainer || targetKind === 'workflow' ? 'agent-trainer' : 'framework-expert';
		}

		function trainerSessionListError(snapshot) {
		  const error = snapshot?.listError;
		  if (error === null || error === undefined) {
		    return snapshot?.listState === 'error' ? new Error('DSH 会话列表同步失败：宿主未提供错误详情') : null;
		  }
		  if (error instanceof Error) return error;
		  const wrapped = new Error(`DSH 会话列表同步失败：${error.message ?? String(error)}`);
		  if (error.code !== undefined) wrapped.code = error.code;
		  if (error.details !== undefined) wrapped.details = error.details;
		  return wrapped;
		}

		function trainerSessionListTimeout(snapshot, timeoutMs) {
		  const phase = snapshot?.phase ?? 'unknown';
		  const listState = snapshot?.listState ?? 'unknown';
		  const error = snapshot?.listError;
		  const detail = error?.message ?? (error === undefined || error === null ? '' : String(error));
		  return new Error(`DSH 会话列表同步超时（${timeoutMs}ms，phase=${phase}, listState=${listState}${detail ? `, listError=${detail}` : ''}），请重试恢复`);
		}

		function isUnknownNativeSession(error) {
		  const code = String(error?.code ?? '').toLowerCase();
		  const message = String(error?.message ?? error ?? '').toLowerCase();
		  return ['session_unknown', 'session_not_found', 'unknown_session', 'not_found'].includes(code)
		    || /unknown session|session .*not found|session .*does not exist/.test(message);
		}

		function nativeSessionKnown(snapshot, sessionId) {
		  if (!snapshot || !sessionId) return false;
		  if (snapshot.byId && Object.prototype.hasOwnProperty.call(snapshot.byId, sessionId)) return true;
		  if (Array.isArray(snapshot.sessions) && snapshot.sessions.some(item => (item?.sessionId ?? item?.id) === sessionId)) return true;
		  if (Array.isArray(snapshot.items) && snapshot.items.some(item => (item?.sessionId ?? item?.id) === sessionId)) return true;
		  return false;
		}

		/**
		 * Ask the host to refresh its public session index before waiting on it. The
		 * refresh method is optional because older DSH hosts only expose the
		 * subscribe/getSnapshot list surface. A failed refresh is surfaced so the
		 * caller can retry; no ready snapshot is manufactured here.
		 */
		async function refreshTrainerSessionList(sessions, signal) {
		  const refresh = sessions?.refresh;
		  if (typeof refresh !== 'function') return;
		  if (signal?.aborted) throw new DOMException('会话选择已更新', 'AbortError');
		  await refresh.call(sessions);
		  if (signal?.aborted) throw new DOMException('会话选择已更新', 'AbortError');
		}

		// The public session list is a sidebar projection, not the authority used to
		// create or bind a trainer session. A cold DSH host can leave this refresh in
		// `pending` while the dedicated session APIs are already usable. Give a
		// refresh a small budget so a fast refresh can repair the list, but do not
		// serialize first-session creation behind an indefinitely pending index.
		async function refreshTrainerSessionListWithBudget(sessions, signal, timeoutMs = 1000) {
		  if (typeof sessions?.refresh !== 'function') return;
		  const refresh = refreshTrainerSessionList(sessions, signal);
		  let timer;
		  const timeout = new Promise(resolve => {
		    timer = setTimeout(() => resolve('timeout'), timeoutMs);
		  });
		  const result = await Promise.race([
		    refresh.then(() => 'ready'),
		    timeout
		  ]);
		  clearTimeout(timer);
		  if (result === 'timeout') refresh.catch(() => {});
		}

		/**
		 * Creating a session and publishing it into the host's sidebar index are
		 * separate operations.  The server binding is authoritative, but the host
		 * selector rejects an id until the public index knows it.  Retry only this
		 * presentation step; never create a second session or drop the binding.
		 */
		async function openTrainerSession(services, sessionId, signal) {
		  try {
		    services.sessions.open(sessionId);
		    return;
		  } catch (error) {
		    if (!isUnknownNativeSession(error)) throw error;
		  }
		  await refreshTrainerSessionList(services.sessions, signal).catch(() => {});
		  // The host can accept the create RPC before its public list snapshot is
		  // ready. Retry the actual open operation itself; waiting only on the list
		  // can deadlock when that presentation index remains `pending`.
		  const deadline = Date.now() + 15000;
		  let lastError;
		  while (Date.now() < deadline) {
		    if (signal?.aborted) throw new DOMException('会话选择已更新', 'AbortError');
		    try {
		      services.sessions.open(sessionId);
		      return;
		    } catch (error) {
		      lastError = error;
		      if (!isUnknownNativeSession(error)) throw error;
		    }
		    await new Promise((resolve, reject) => {
		      const abort = () => { clearTimeout(timer); reject(new DOMException('会话选择已更新', 'AbortError')); };
		      const done = () => { signal?.removeEventListener('abort', abort); resolve(); };
		      const timer = setTimeout(done, 250);
		      signal?.addEventListener('abort', abort, { once: true });
		    });
		  }
		  throw lastError ?? new Error(`DSH 会话 ${sessionId} 在 15 秒内不可打开`);
		}

		function waitTrainerSession(sessions, predicate, { signal, timeoutMs = 10000 } = {}) {
		  if (signal?.aborted) return Promise.reject(new DOMException('会话选择已更新', 'AbortError'));
		  const initial = sessions.list.getSnapshot();
		  const initialError = trainerSessionListError(initial);
		  if (initialError) return Promise.reject(initialError);
		  if (predicate(initial)) return Promise.resolve();
		  return new Promise((resolve, reject) => {
		    let unsubscribe = () => {};
		    const cleanup = () => { clearTimeout(timer); unsubscribe(); signal?.removeEventListener('abort', abort); };
		    const abort = () => { cleanup(); reject(new DOMException('会话选择已更新', 'AbortError')); };
		    const timer = setTimeout(() => {
		      const snapshot = sessions.list.getSnapshot();
		      cleanup();
		      reject(trainerSessionListTimeout(snapshot, timeoutMs));
		    }, timeoutMs);
		    const check = () => {
		      const snapshot = sessions.list.getSnapshot();
		      const error = trainerSessionListError(snapshot);
		      if (error) { cleanup(); reject(error); return true; }
		      if (predicate(snapshot)) { cleanup(); resolve(); return true; }
		      return false;
		    };
		    unsubscribe = sessions.list.subscribe(check);
		    signal?.addEventListener('abort', abort, { once: true });
		    check();
		  });
		}

		// Storage is only a session-id hint. Every reuse must pass server verification.
		function createTrainerNavigator({ services, api, storage = globalThis.localStorage }) {
		  let epoch = 0;
		  let pending = null;
		  const creating = new Map();
		  const read = key => { try { return storage?.getItem(key); } catch { return null; } };
		  const write = (key, id) => { try { storage?.setItem(key, id); } catch { /* server binding remains authoritative */ } };
		  return {
		    cancel() { epoch += 1; pending?.abort(); },
		    async open({ target, mode = 'training', trainer = false, selectedRunId = null, title, _recovering = false }) {
		      pending?.abort();
		      const localEpoch = ++epoch;
		      const signal = (pending = new AbortController()).signal;
		      const current = () => {
		        if (signal.aborted || localEpoch !== epoch) throw new DOMException('会话选择已更新', 'AbortError');
		      };
		      const connection = typeof services.get === 'function' ? services.get('connection') : services.connection;
		      const rpc = connection?.api;
		      let remoteSession;
		      if (typeof services.get === 'function') {
		        try { remoteSession = services.get('remote.session'); } catch { /* optional on older hosts */ }
		      }
		      if ((!rpc?.sessions?.create && !remoteSession?.create) || !services.sessions || !services.workspaces) throw new Error('DSH 原生会话服务尚未就绪');
		      const presetId = trainerPreset(target.targetKind, mode, trainer);
		      const key = trainerNativeKey(target, presetId, mode);
		      const identity = { ...target, presetId, mode, selectedRunId };
		      let sessionId = read(key);
		      let sessionList = services.sessions.list.getSnapshot();
		      let binding;
		      // The public sidebar index is only a presentation surface. It can stay
		      // pending or error while the dedicated session and trainer APIs remain
		      // usable, so verify a remembered id directly through the server binding.
		      // Refresh opportunistically, but never make navigation wait for it.
		      if (sessionList.phase !== 'ready' && !sessionId && typeof services.sessions.refresh === 'function') {
		        // A fast refresh still repairs the sidebar before creation. If the
		        // host keeps the public index pending, continue with the authoritative
		        // server binding and native create RPC instead of adding that delay to
		        // the first open. openTrainerSession() separately retries publication
		        // of the resulting session ID.
		        await refreshTrainerSessionListWithBudget(services.sessions, signal);
		      } else if (sessionList.phase !== 'ready') {
		        void refreshTrainerSessionList(services.sessions, signal).catch(() => {});
		      }
		      if (!sessionId) {
		        const sessionListError = trainerSessionListError(sessionList);
		        if (sessionListError) throw sessionListError;
		      }
		      if (sessionId) {
		        let existing;
		        try { existing = await api('bind-session', { projectId: target.projectId, sessionId }, { signal }); }
		        catch (error) { if (error.code !== 'session_unbound') throw error; }
		        if (existing) {
		          current();
		          binding = await api('bind-session', { ...identity, sessionId, baseBindingRevision: existing.bindingRevision }, { signal });
		          current();
		        } else {
		          // A session created by an earlier attempt can be valid but have no
		          // trainer binding because the UI was waiting on the host index.
		          try {
		            binding = await api('bind-session', { ...identity, sessionId }, { signal });
		            current();
		          } catch (error) {
		            if (!['session_unbound', 'session_identity_mismatch'].includes(error.code)) throw error;
		            sessionId = null;
		          }
		        }
		      }
		      if (!binding) {
		        const prepared = await api('bind-session', identity, { signal });
		        current();
		        if (!prepared.cwd) throw new Error('服务端未返回合成训练工作区');
		        let creation = creating.get(key);
		        if (!creation) {
		          creation = (async () => {
		            const workspace = await services.workspaces.create({ path: prepared.cwd });
		            if (!workspace?.workspaceId) throw new Error('DSH 没有为会话工作区返回 workspaceId');
		            if (remoteSession?.create) {
		              const response = await remoteSession.create({ workspaceId: workspace.workspaceId, agentPreset: presetId });
		              if (!response?.ok) throw new Error(response?.error?.message ?? '创建专用会话失败');
		              return response.value?.sessionId;
		            }
		            const response = await rpc.sessions.create({ workspaceId: workspace.workspaceId, agentPreset: presetId });
		            if (!response?.result?.ok) throw new Error(response?.result?.error?.message ?? '创建专用会话失败');
		            return response.result.value?.sessionId;
		          })();
		          creating.set(key, creation);
		          creation.catch(() => { if (creating.get(key) === creation) creating.delete(key); });
		        }
		        sessionId = await creation;
		        if (!sessionId) throw new Error('DSH 未返回 sessionId');
		        // Remember accepted creation even when navigation was superseded: retry restores, never duplicates.
		        // The host may publish the new session to its sidebar index later (or keep
		        // that index pending while no conversation is selected). Binding is a
		        // server-side operation and must not wait for that presentation index.
		        write(key, sessionId);
		        current();
		        creating.delete(key);
		        binding = await api('bind-session', { ...identity, sessionId }, { signal });
		        current();
		        if (title) {
		          const createdBinding = services.sessions.binding?.(sessionId);
		          if (createdBinding?.session?.rename) await createdBinding.session.rename(title);
		        }
		      }
		      current();
		      if (binding.sessionId !== sessionId || binding.presetId !== presetId || binding.projectId !== target.projectId || binding.targetKind !== target.targetKind || binding.targetId !== target.targetId || binding.mode !== mode || binding.bindingSchemaVersion !== 1) {
		        throw new Error('服务端会话绑定与当前目标不一致');
		      }
		      const selection = binding.nativeModelSelection;
		      if (!selection?.provider || !selection?.model) throw new Error('服务端未提供专用会话模型配置');
		      if (!rpc.sessions.selectModel || !rpc.sessions.models) throw new Error('DSH 会话模型选择 API 尚未就绪');
		      const chosen = await rpc.sessions.selectModel({ sessionId, provider: selection.provider, model: selection.model,
		        ...(selection.reasoningEffort === undefined ? {} : { reasoningEffort: selection.reasoningEffort }) }, signal);
		      current();
		      if (!chosen?.result?.ok) throw new Error(chosen?.result?.error?.message ?? '专用会话模型选择失败');
		      const matches = model => model?.provider === selection.provider && model?.model === selection.model
		        && (selection.reasoningEffort === undefined || model.reasoningEffort === selection.reasoningEffort);
		      if (!matches(chosen.result.value?.selected)) throw new Error('DSH 返回的会话模型与服务端配置不一致');
		      const confirmed = await rpc.sessions.models({ sessionId }, signal);
		      current();
		      if (!confirmed?.result?.ok) throw new Error(confirmed?.result?.error?.message ?? '无法复核专用会话模型');
		      if (confirmed.result.value?.routable !== true || !matches(confirmed.result.value?.current)) throw new Error('专用会话模型未生效或提供方不可用');
		      try {
		        await openTrainerSession(services, sessionId, signal);
		      } catch (error) {
		        // localStorage is only a hint. A browser reload or host restart can
		        // leave an id that no longer exists in the native session service.
		        // Drop that hint and retry exactly once so the user can recover by
		        // clicking the same button instead of seeing an opaque host error.
		        if (!_recovering && isUnknownNativeSession(error) && read(key) === sessionId) {
		          try { storage?.removeItem(key); } catch { /* binding remains server authoritative */ }
		          return this.open({ target, mode, trainer, selectedRunId, title, _recovering: true });
		        }
		        throw error;
		      }
		      return binding;
		    }
		  };
		}

		function trainerNewAgentChanges({ agentId, name }) {
		  if (!/^[a-z][a-z0-9-]{0,63}$/.test(agentId)) throw new Error('Agent ID 须为小写字母开头，后接字母、数字或连字符，最多64位');
		  if (!name.trim()) throw new Error('请填写 Agent 名称');
		  const inputSchemaRef = `contracts/${agentId}-input.schema.json`;
		  const outputSchemaRef = `contracts/${agentId}-output.schema.json`;
		  const instructionsRef = `agents/${agentId}/instructions.md`;
		  const json = value => `${JSON.stringify(value, null, 2)}\n`;
		  const schema = { $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object' };
		  return [
		    { path: `agents/${agentId}/agent.json`, content: json({ agentId, name: name.trim(), instructionsRef, skillRefs: [], toolIds: [], inputSchemaRef, outputSchemaRef }) },
		    { path: instructionsRef, content: 'Process the supplied synthetic JSON input and return a JSON object. Do not load business materials.\n' },
		    { path: inputSchemaRef, content: json(schema) }, { path: outputSchemaRef, content: json(schema) }
		  ];
		}

		function trainerNewWorkflowChanges({ workflowId, name, firstAgentId, secondAgentId }) {
		  if (!/^[a-z][a-z0-9-]{0,63}$/.test(workflowId)) throw new Error('工作流 ID 须为小写字母开头，后接字母、数字或连字符，最多64位');
		  if (!name.trim()) throw new Error('请填写工作流名称');
		  if (!firstAgentId || !secondAgentId) throw new Error('工作流至少需要选择两个 Agent');
		  if (firstAgentId === secondAgentId) throw new Error('请选择两个不同的 Agent');
		  const firstStepId = 'step-1';
		  const secondStepId = 'step-2';
		  const workflow = {
		    workflowId,
		    name: name.trim(),
		    steps: [
		      { stepId: firstStepId, agentId: firstAgentId, inputBindings: { '': { source: 'input', pointer: '' } }, timeoutMs: 120000 },
		      { stepId: secondStepId, agentId: secondAgentId, inputBindings: { '': { source: 'step', stepId: firstStepId, pointer: '' } }, timeoutMs: 120000 }
		    ]
		  };
		  return [{ path: `workflows/${workflowId}.json`, content: `${JSON.stringify(workflow, null, 2)}\n` }];
		}

		function trainerAppendStep(workflow, agentId) {
		  if (workflow.steps.length >= 64) throw new Error('工作流最多64步');
		  const ids = new Set(workflow.steps.map(step => step.stepId));
		  let number = 1;
		  while (ids.has(`step-${number}`)) number += 1;
		  return { ...workflow, steps: [...workflow.steps, { stepId: `step-${number}`, agentId, inputBindings: {}, timeoutMs: 120000 }] };
		}

		function trainerMoveStep(workflow, index, offset) {
		  const next = index + offset;
		  if (next < 0 || next >= workflow.steps.length) return workflow;
		  const steps = [...workflow.steps];
		  [steps[index], steps[next]] = [steps[next], steps[index]];
		  return { ...workflow, steps };
		}

		function trainerFrozenVersionsFor(versions, target) {
		  if (!target) return [];
		  return versions.filter(version => (!version.projectId || version.projectId === target.projectId)
		    && version.targetKind === target.targetKind && version.targetId === target.targetId);
		}

		function trainerFrozenVersionLabel(version) {
		  return `${version.targetKind}/${version.targetId} · ${version.frozenVersionId} · ${version.revisionId} · SHA-256 ${version.bundleSha256}`;
		}

		function trainerStepVersion(workflow, stepId, frozenVersionId, versions, projectId) {
		  const step = workflow.steps.find(item => item.stepId === stepId);
		  if (!step) throw new Error('步骤不存在');
		  if (frozenVersionId && !trainerFrozenVersionsFor(versions, { projectId, targetKind: 'agent', targetId: step.agentId }).some(version => version.frozenVersionId === frozenVersionId)) {
		    throw new Error('冻结版本不属于该步骤的 Agent');
		  }
		  return { ...workflow, steps: workflow.steps.map(item => {
		    if (item.stepId !== stepId) return item;
		    const next = { ...item };
		    if (frozenVersionId) next.agentVersion = { kind: 'frozen', frozenVersionId };
		    else delete next.agentVersion;
		    return next;
		  }) };
		}

		function trainerMatchingEvidence(runs, version) {
		  if (!version) return [];
		  return runs.filter(run => run.status === 'completed' && (!version.projectId || run.projectId === version.projectId)
		    && run.targetKind === version.targetKind && run.targetId === version.targetId && run.bundleSha256 === version.bundleSha256);
		}

		const TRAINER_STYLES = `
		.trainer-ui{font:13px/1.5 system-ui,sans-serif;color:var(--dsw-alias-label-primary,#203029);box-sizing:border-box}
		.trainer-ui *{box-sizing:border-box}.trainer-ui button,.trainer-ui select,.trainer-ui input,.trainer-ui textarea{font:inherit;color:inherit}
		.trainer-ui button{cursor:pointer;border:1px solid #c9d7ce;background:var(--dsw-alias-button-elevated-fill,#fff);border-radius:7px;padding:6px 10px}
		.trainer-ui button:disabled{opacity:.5;cursor:default}.trainer-ui button[aria-pressed=true],.trainer-ui .trainer-primary{background:#176b4e;color:white;border-color:#176b4e}
		.trainer-ui input,.trainer-ui textarea,.trainer-ui select{border:1px solid #c9d7ce;background:var(--dsw-alias-button-elevated-fill,#fff);border-radius:6px;padding:7px;max-width:100%}
		.trainer-nav{padding:12px;overflow:auto;height:100%;min-height:0}.trainer-ui h2{font-size:17px;margin:8px 0}.trainer-ui h3{font-size:13px;margin:15px 0 7px}.trainer-ui p{margin:7px 0}
		.trainer-row{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.trainer-stack{display:grid;gap:6px}.trainer-object{text-align:left;display:flex;justify-content:space-between;width:100%}
		.trainer-meta{font-size:11px;opacity:.75;overflow-wrap:anywhere}.trainer-warning{padding:9px;background:#fff4d7;color:#684d15;border-radius:7px}.trainer-error{color:#a12626;white-space:pre-wrap;overflow-wrap:anywhere}
		.trainer-details{height:100%;overflow:auto;padding:18px}.trainer-controls{position:sticky;bottom:0;padding:10px 0;background:var(--dsw-alias-button-elevated-fill,#fff);border-top:1px solid #d7e2db}
		.trainer-ui pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--dsw-alias-interactive-bg-hover,#f1f5f2);padding:10px;border-radius:6px;font-size:11px;max-height:300px;overflow:auto}
		.trainer-step{border-left:3px solid #98bba8;padding:6px 10px;margin:8px 0}.trainer-modal-backdrop{position:fixed;inset:0;background:#15251f66;display:flex;align-items:center;justify-content:center;pointer-events:auto;z-index:2147483600}
		.trainer-modal{background:var(--dsw-alias-button-elevated-fill,#fff);border:1px solid #bdd0c3;border-radius:12px;box-shadow:0 12px 50px #0003;width:min(980px,94vw);max-height:90vh;overflow:auto;padding:20px}
		.trainer-modal textarea{width:100%;min-height:260px;font:12px/1.6 ui-monospace,monospace}.trainer-diff{display:grid;grid-template-columns:1fr 1fr;gap:12px}.trainer-diff>div{min-width:0}
		.trainer-header{display:flex;align-items:center;gap:8px;max-width:600px}.trainer-header .trainer-meta{max-width:340px}.trainer-empty{padding:10px;border:1px dashed #a1bda9;border-radius:7px}
		`;


		const TRAINER_SURFACE_STYLES = String.raw`
		.trainer-surface,.trainer-surface *{box-sizing:border-box}.trainer-surface{position:fixed;inset:10px;z-index:2147483500;display:flex;flex-direction:column;overflow:hidden;background:#fff;color:#203040;border:1px solid #dfe6ee;border-radius:16px;box-shadow:0 18px 70px #10243a38;font:13px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}.trainer-surface button,.trainer-surface textarea{font:inherit;color:inherit}.trainer-surface button{cursor:pointer;border:1px solid #dfe6ee;background:#fff;border-radius:8px;padding:7px 11px}.trainer-surface button:disabled{cursor:default;opacity:.5}.trainer-surface button[aria-pressed=true],.trainer-surface .trainer-surface-primary{background:#4169e1;border-color:#4169e1;color:#fff}.trainer-surface-top{height:62px;display:flex;align-items:center;gap:16px;padding:12px 18px;border-bottom:1px solid #e5eaf0;flex:0 0 auto}.trainer-surface-brand{display:flex;align-items:center;gap:8px;font-size:15px;white-space:nowrap}.trainer-surface-brand-mark{display:grid;place-items:center;width:32px;height:32px;border-radius:9px;background:#4169e1;color:#fff;font-weight:700;font-size:17px}.trainer-surface-project{color:#8492a6;border-left:1px solid #e1e6ed;padding-left:16px;font-size:13px}.trainer-surface-modes{display:flex;gap:3px;padding:3px;margin:auto;background:#f1f4f8;border-radius:10px}.trainer-surface-modes button{border:0;background:transparent;padding:7px 14px;border-radius:8px;color:#5c6878}.trainer-surface-modes button[aria-pressed=true]{background:#fff;color:#315cd5;box-shadow:0 1px 4px #243b5a25}.trainer-surface-demo{color:#6c7b8c;border:1px solid #dfe6ee;border-radius:8px;padding:6px 10px;white-space:nowrap}.trainer-surface-close{padding:6px 9px!important}.trainer-surface-shell{display:grid;grid-template-columns:188px minmax(0,1fr);min-height:0;flex:1}.trainer-surface-side{min-width:0;overflow:auto;background:#f7f9fb;border-right:1px solid #e5eaf0;padding:18px 10px;display:flex;flex-direction:column;gap:16px}.trainer-surface-side-group{display:grid;gap:2px}.trainer-surface-side-label{font-size:11px;letter-spacing:1px;color:#8794a5;padding:0 9px;margin-bottom:4px}.trainer-surface-nav{display:flex;align-items:center;gap:8px;width:100%;text-align:left;padding:8px 9px!important;border-color:transparent!important;background:transparent!important}.trainer-surface-nav:hover{background:#edf2f8!important}.trainer-surface-nav.selected{background:#e8efff!important;color:#315cd5}.trainer-surface-count{margin-left:auto;font-size:11px;color:#8794a5}.trainer-surface-side-foot{margin-top:auto;border-top:1px solid #e5eaf0;padding:13px 9px 0;color:#8794a5;font-size:11px}.trainer-surface-main{display:flex;flex-direction:column;min-width:0;min-height:0}.trainer-surface-heading{padding:20px 24px 14px;border-bottom:1px solid #e5eaf0;flex:0 0 auto}.trainer-surface-crumb{font-size:11px;color:#8492a6;margin-bottom:8px}.trainer-surface-heading-row{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.trainer-surface-heading h1{font-size:20px;margin:0;color:#1c2a3a}.trainer-surface-subline{font-size:12px;color:#8492a6;margin-top:6px}.trainer-surface-actions{display:flex;gap:7px}.trainer-surface-tabs{display:flex;gap:22px;padding:0 24px;border-bottom:1px solid #e5eaf0;flex:0 0 auto}.trainer-surface-tabs button{border:0;border-bottom:2px solid transparent;border-radius:0;background:transparent;padding:11px 0;color:#8492a6}.trainer-surface-tabs button[aria-pressed=true]{border-bottom-color:#4169e1;color:#1c2a3a}.trainer-surface-workarea{display:grid;grid-template-columns:minmax(0,1fr) 242px;min-height:0;flex:1}.trainer-surface-session{display:flex;flex-direction:column;min-width:0;min-height:0;padding:18px 24px;overflow:auto}.trainer-surface-sessionbar{display:flex;align-items:center;gap:7px;color:#8492a6;font-size:11px;margin-bottom:20px}.trainer-surface-led{width:6px;height:6px;background:#1f9d68;border-radius:50%}.trainer-surface-user{align-self:flex-end;max-width:92%;background:#f1f4f8;border-radius:13px 13px 3px 13px;padding:10px 13px;margin-bottom:18px}.trainer-surface-message{display:flex;gap:10px;align-items:flex-start}.trainer-surface-avatar{width:28px;height:28px;display:grid;place-items:center;border-radius:9px;background:#e8efff;color:#4169e1;flex:0 0 auto}.trainer-surface-message-body{min-width:0}.trainer-surface-message-name{font-weight:600;margin:2px 0 8px}.trainer-surface-evidence{border:1px solid #e2e8ef;border-radius:11px;padding:12px;margin-top:12px}.trainer-surface-step{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #edf1f5}.trainer-surface-step:last-child{border-bottom:0}.trainer-surface-step-mark{display:grid;place-items:center;width:19px;height:19px;border-radius:50%;background:#f1f4f8;color:#6f7d8e;font-size:11px;flex:0 0 auto}.trainer-surface-step-label{min-width:0;overflow-wrap:anywhere}.trainer-surface-step-state{margin-left:auto;color:#8492a6;font-size:11px;white-space:nowrap}.trainer-surface-spacer{flex:1;min-height:18px}.trainer-surface-chips{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}.trainer-surface-chip{font-size:11px!important;color:#6f7d8e!important;padding:5px 8px!important}.trainer-surface-composer{border:1px solid #dfe6ee;border-radius:11px;padding:10px 12px;background:#f7f9fb}.trainer-surface-composer textarea{display:block;width:100%;min-height:60px;resize:vertical;border:0;outline:0;background:transparent}.trainer-surface-composer-bottom{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#8492a6;font-size:11px;margin-top:5px}.trainer-surface-inspector{min-width:0;min-height:0;overflow:auto;align-self:stretch;display:flex;flex-direction:column;justify-content:flex-start;align-content:flex-start;background:#f7f9fb;border-left:1px solid #e5eaf0;padding:12px 14px}.trainer-surface-inspector>*{min-width:0;width:100%;flex:0 0 auto}.trainer-surface-inspector>[data-testid="trainer-run-details"]{display:flex;flex-direction:column;justify-content:flex-start;align-items:stretch;min-width:0;width:100%;min-height:0;flex:1 1 auto;margin:0;overflow:auto;overflow-wrap:anywhere}.trainer-surface-inspector .trainer-details{height:auto;padding:0;overflow:visible}.trainer-surface-inspector h2{font-size:14px;margin:0}.trainer-surface-inspector .trainer-controls{position:static;flex:0 0 auto;background:transparent;border-top:1px solid #e5eaf0;margin-top:14px}.trainer-surface-inspector .trainer-step{min-width:0;white-space:normal;overflow-wrap:anywhere;line-height:1.4;border:1px solid #dfe6ee;border-left-width:1px;border-radius:9px;margin:7px 0;background:#fff}.trainer-surface-inspector .trainer-error{max-width:100%;overflow:auto;word-break:break-word}.trainer-surface-inspector pre{max-height:180px}.trainer-surface-plain{padding:24px;color:#8492a6}.trainer-surface-status{font-size:11px;color:#8492a6;margin-top:8px}.trainer-surface-native-prompt{display:flex;gap:12px;align-items:flex-start;border:1px solid #e2e8ef;border-radius:11px;padding:16px;background:#fbfcfe}.trainer-surface-native-prompt p{margin:7px 0;color:#6f7d8e}.trainer-surface-native-icon{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:#e8efff;color:#4169e1;flex:0 0 auto}.trainer-surface-run-list{display:grid;gap:7px}.trainer-surface-run-row{display:flex;justify-content:space-between;gap:12px;text-align:left;width:100%;background:#fff}.trainer-surface-composer label{display:block;margin-bottom:5px}.trainer-surface-composer textarea{border:1px solid #dfe6ee!important;background:#fff!important;border-radius:7px!important;min-height:72px;padding:8px!important}@media(max-width:900px){.trainer-surface{inset:6px}.trainer-surface-project{display:none}.trainer-surface-top{padding:10px 12px}.trainer-surface-shell{grid-template-columns:162px minmax(0,1fr)}.trainer-surface-workarea{grid-template-columns:minmax(0,1fr) 215px}.trainer-surface-heading,.trainer-surface-session{padding-left:15px;padding-right:15px}.trainer-surface-tabs{padding:0 15px}}@media(max-width:720px){.trainer-surface-workarea{grid-template-columns:1fr}.trainer-surface-inspector{border-left:0;border-top:1px solid #e5eaf0}.trainer-surface-top{flex-wrap:wrap;height:auto}.trainer-surface-modes{order:3;width:100%;justify-content:center}.trainer-surface-demo{display:none}}@media(max-width:480px){.trainer-surface{inset:0;border-radius:0}.trainer-surface-shell{display:block}.trainer-surface-side{border-right:0;border-bottom:1px solid #e5eaf0;max-height:210px}.trainer-surface-side-foot{display:none}.trainer-surface-heading h1{font-size:18px}}
		`;

		// V2 keeps the current full-screen workbench geometry and changes only visual
		// tokens and status treatment.  The base rules above remain the V1 fallback;
		// switching the root data-theme attribute back to "v1" restores them exactly.
		const TRAINER_SURFACE_THEME_KEY = 'trainer-workbench-ui-version-v1-v2';
		const TRAINER_SURFACE_V2_OVERRIDES = String.raw`
		.trainer-surface[data-theme="v2"]{--trainer-v2-ink:#17243a;--trainer-v2-muted:#52647a;--trainer-v2-border:#d7e0ec;--trainer-v2-panel:#f5f8fc;--trainer-v2-blue:#2f5fe5;--trainer-v2-blue-soft:#e8efff;--trainer-v2-complete:#177245;--trainer-v2-complete-soft:#e7f6ee;--trainer-v2-running:#b45309;--trainer-v2-running-soft:#fff4e0;--trainer-v2-error:#b42318;--trainer-v2-error-soft:#fdecec;--trainer-v2-idle:#52647a;--trainer-v2-idle-soft:#edf2f7;color:var(--trainer-v2-ink);font-size:14px;line-height:1.58;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;background:#fff;border-color:var(--trainer-v2-border);box-shadow:0 18px 70px #10243a2b}
		.trainer-surface[data-theme="v2"] button{border-color:var(--trainer-v2-border);transition:background-color .15s ease,border-color .15s ease,color .15s ease,box-shadow .15s ease}
		.trainer-surface[data-theme="v2"] button:hover:not(:disabled){border-color:#9db3dd;box-shadow:0 2px 8px #1f3b7014}
		.trainer-surface[data-theme="v2"] button:focus-visible{outline:3px solid #9db9ff;outline-offset:1px}
		.trainer-surface[data-theme="v2"] .trainer-surface-top{border-bottom-color:var(--trainer-v2-border);background:#fff}
		.trainer-surface[data-theme="v2"] .trainer-surface-brand{font-size:16px;color:var(--trainer-v2-ink)}
		.trainer-surface[data-theme="v2"] .trainer-surface-brand-mark{background:var(--trainer-v2-blue);box-shadow:0 3px 8px #2f5fe53d}
		.trainer-surface[data-theme="v2"] .trainer-surface-project,.trainer-surface[data-theme="v2"] .trainer-surface-crumb,.trainer-surface[data-theme="v2"] .trainer-surface-subline,.trainer-surface[data-theme="v2"] .trainer-surface-status,.trainer-surface[data-theme="v2"] .trainer-surface-step-state{color:var(--trainer-v2-muted)}
		.trainer-surface[data-theme="v2"] .trainer-surface-demo{color:#3155a7;border-color:#b8c8eb;background:#f4f7ff;font-weight:600}
		.trainer-surface[data-theme="v2"] .trainer-surface-theme-toggle{border-color:#b8c8eb;background:#f7f9ff;color:#3155a7;font-weight:600}
		.trainer-surface[data-theme="v2"] .trainer-surface-modes{background:#edf2f8}
		.trainer-surface[data-theme="v2"] .trainer-surface-modes button[aria-pressed=true]{color:var(--trainer-v2-blue)}
		.trainer-surface[data-theme="v2"] .trainer-surface-shell{background:#fff}
		.trainer-surface[data-theme="v2"] .trainer-surface-side,.trainer-surface[data-theme="v2"] .trainer-surface-inspector{background:var(--trainer-v2-panel)}
		.trainer-surface[data-theme="v2"] .trainer-surface-side{border-right-color:var(--trainer-v2-border)}
		.trainer-surface[data-theme="v2"] .trainer-surface-inspector{border-left-color:var(--trainer-v2-border)}
		.trainer-surface[data-theme="v2"] .trainer-surface-side-label{color:#60738c;font-weight:700}
		.trainer-surface[data-theme="v2"] .trainer-surface-side-foot{border-top-color:var(--trainer-v2-border);color:#60738c}
		.trainer-surface[data-theme="v2"] .trainer-surface-nav{color:#243650}
		.trainer-surface[data-theme="v2"] .trainer-surface-nav:hover{background:#eaf0fa!important}
		.trainer-surface[data-theme="v2"] .trainer-surface-nav.selected{background:var(--trainer-v2-blue-soft)!important;color:#234dbd;font-weight:600}
		.trainer-surface[data-theme="v2"] .trainer-surface-count{color:#60738c}
		.trainer-surface[data-theme="v2"] .trainer-surface-heading,.trainer-surface[data-theme="v2"] .trainer-surface-tabs{border-bottom-color:var(--trainer-v2-border)}
		.trainer-surface[data-theme="v2"] .trainer-surface-heading{padding-top:22px;padding-bottom:16px}
		.trainer-surface[data-theme="v2"] .trainer-surface-heading h1{font-size:22px;color:var(--trainer-v2-ink);letter-spacing:-.01em}
		.trainer-surface[data-theme="v2"] .trainer-surface-tabs{gap:25px}
		.trainer-surface[data-theme="v2"] .trainer-surface-tabs button{font-size:14px;padding-top:12px;padding-bottom:12px}
		.trainer-surface[data-theme="v2"] .trainer-surface-tabs button[aria-pressed=true]{background:transparent;border-bottom-color:var(--trainer-v2-blue);color:var(--trainer-v2-ink);font-weight:600}
		.trainer-surface[data-theme="v2"] .trainer-surface-session{padding-top:20px}
		.trainer-surface[data-theme="v2"] .trainer-surface-sessionbar{color:var(--trainer-v2-muted)}
		.trainer-surface[data-theme="v2"] .trainer-surface-led{width:8px;height:8px;background:#9aaabd}
		.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-complete{background:var(--trainer-v2-complete)}
		.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-running{background:var(--trainer-v2-running)}
		.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-error{background:var(--trainer-v2-error)}
		.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-idle{background:#9aaabd}
		.trainer-surface[data-theme="v2"] .trainer-surface-primary{background:var(--trainer-v2-blue);border-color:var(--trainer-v2-blue);color:#fff}
		.trainer-surface[data-theme="v2"] .trainer-surface-primary:hover:not(:disabled){background:#244fc9;border-color:#244fc9}
		.trainer-surface[data-theme="v2"] .trainer-surface-native-prompt{border-color:#cbd8ec;background:#f7faff;box-shadow:0 2px 9px #203b6b0d}
		.trainer-surface[data-theme="v2"] .trainer-surface-native-prompt p{color:#52647a}
		.trainer-surface[data-theme="v2"] .trainer-surface-native-icon{background:var(--trainer-v2-blue-soft);color:var(--trainer-v2-blue)}
		.trainer-surface[data-theme="v2"] .trainer-surface-composer{border-color:#cbd8ec;background:#f5f8fc}
		.trainer-surface[data-theme="v2"] .trainer-surface-composer textarea{border-color:#cbd8ec!important}
		.trainer-surface[data-theme="v2"] .trainer-surface-chip{color:#465a74!important;background:#fff}
		.trainer-surface[data-theme="v2"] .trainer-surface-inspector .trainer-controls{border-top-color:var(--trainer-v2-border)}
		.trainer-surface[data-theme="v2"] .trainer-surface-inspector .trainer-step{border-color:#cbd8ec;background:#fff;box-shadow:0 2px 8px #203b6b0d}.trainer-surface[data-theme="v2"] .trainer-surface-inspector .trainer-step[aria-pressed=true]{background:#fff;color:var(--trainer-v2-ink);border-color:#8daafb}
		.trainer-surface[data-theme="v2"] .trainer-surface-status{font-size:12px}
		.trainer-surface[data-theme="v2"] .trainer-surface-plain{color:var(--trainer-v2-muted)}
		.trainer-surface[data-theme="v2"] .trainer-surface-run-row{background:#fff}
		.trainer-surface[data-theme="v2"] .trainer-status-badge{display:inline-flex;align-items:center;gap:6px;width:max-content;padding:3px 8px;border-radius:999px;font-size:12px;font-weight:700;line-height:1.35}
		.trainer-surface[data-theme="v2"] .trainer-status-badge::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
		.trainer-surface[data-theme="v2"] .trainer-status-complete{color:var(--trainer-v2-complete);background:var(--trainer-v2-complete-soft)}
		.trainer-surface[data-theme="v2"] .trainer-status-running{color:var(--trainer-v2-running);background:var(--trainer-v2-running-soft)}
		.trainer-surface[data-theme="v2"] .trainer-status-error{color:var(--trainer-v2-error);background:var(--trainer-v2-error-soft)}
		.trainer-surface[data-theme="v2"] .trainer-status-idle{color:var(--trainer-v2-idle);background:var(--trainer-v2-idle-soft)}
		.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-complete{border-left:4px solid var(--trainer-v2-complete)}
		.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-running{border-left:4px solid var(--trainer-v2-running)}
		.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-error{border-left:4px solid var(--trainer-v2-error)}
		.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-idle{border-left:4px solid #9aaabd}
		.trainer-surface[data-theme="v2"] .trainer-error{color:var(--trainer-v2-error);background:var(--trainer-v2-error-soft);border-radius:7px;padding:8px}
		.trainer-surface[data-theme="v2"] .trainer-warning{color:#854d0e;background:var(--trainer-v2-running-soft)}
		`;
		const TRAINER_SURFACE_STYLES_V1 = TRAINER_SURFACE_STYLES;
		const TRAINER_SURFACE_STYLES_V2 = TRAINER_SURFACE_STYLES + TRAINER_SURFACE_V2_OVERRIDES;

		function trainerSurfaceTheme() {
		  try { return globalThis.localStorage?.getItem(TRAINER_SURFACE_THEME_KEY) === 'v1' ? 'v1' : 'v2'; }
		  catch { return 'v2'; }
		}

		function trainerStatusTone(status) {
		  if (status === 'completed') return 'complete';
		  if (['queued', 'preparing', 'running', 'pausing', 'stopping'].includes(status)) return 'running';
		  if (['failed', 'cancelled', 'interrupted'].includes(status)) return 'error';
		  return 'idle';
		}

		function trainerStatusClass(status) { return `trainer-status-badge trainer-status-${trainerStatusTone(status)}`; }

		function trainerJson(value) { return JSON.stringify(value ?? null, null, 2); }

		const TRAINER_TARGET_STORAGE_KEY = 'trainer-workbench-target-v1';
		function trainerRememberTarget(target) {
		  if (!target?.projectId || !target?.targetKind || !target?.targetId) return;
		  try { globalThis.localStorage?.setItem(TRAINER_TARGET_STORAGE_KEY, JSON.stringify(target)); } catch { /* optional preference */ }
		}
		function trainerRememberedTarget(projectId, project) {
		  try {
		    const value = JSON.parse(globalThis.localStorage?.getItem(TRAINER_TARGET_STORAGE_KEY) ?? 'null');
		    if (!value || value.projectId !== projectId) return null;
		    const exists = value.targetKind === 'workflow'
		      ? (project?.workflows ?? []).some(item => item.workflowId === value.targetId)
		      : (project?.agents ?? []).some(item => item.agentId === value.targetId);
		    return exists ? { projectId, targetKind: value.targetKind, targetId: value.targetId } : null;
		  } catch { return null; }
		}
		function trainerPreferredTarget(projectId, project, runs = []) {
		  const remembered = trainerRememberedTarget(projectId, project);
		  if (remembered) return remembered;
		  const valid = run => run?.projectId === projectId && ['workflow', 'agent'].includes(run.targetKind) && run.targetId && run.status === 'completed';
		  const recent = [...runs].filter(valid).sort((a, b) => Date.parse(b.updatedAt ?? b.completedAt ?? b.startedAt ?? 0) - Date.parse(a.updatedAt ?? a.completedAt ?? a.startedAt ?? 0))[0];
		  if (recent) {
		    const target = { projectId, targetKind: recent.targetKind, targetId: recent.targetId };
		    const exists = target.targetKind === 'workflow'
		      ? (project?.workflows ?? []).some(item => item.workflowId === target.targetId)
		      : (project?.agents ?? []).some(item => item.agentId === target.targetId);
		    if (exists) return target;
		  }
		  const first = project?.workflows?.[0] ?? project?.agents?.[0];
		  return first ? { projectId, targetKind: first.workflowId ? 'workflow' : 'agent', targetId: first.workflowId ?? first.agentId } : null;
		}
		function trainerWorkflowDefaultInputText(target, assets) {
		  if (target?.targetKind !== 'workflow') return '{}';
		  try {
		    const fixture = JSON.parse(assets?.files?.[`tests/${target.targetId}.json`] ?? 'null');
		    const input = fixture?.cases?.[0]?.input;
		    return input && typeof input === 'object' ? trainerJson(input) : '{}';
		  } catch { return '{}'; }
		}
		function trainerRunLabel(status) {
		  return ({ queued: '已排队', preparing: '准备执行包', running: '运行中', pausing: '等待当前步骤结束后暂停',
		    paused: '已暂停', stopping: '正在请求停止', completed: '框架验证通过', failed: '失败', cancelled: '已取消', interrupted: '重启中断' })[status] ?? status ?? '尚未运行';
		}

		function trainerRunDuration(run, now = Date.now()) {
		  if (!run?.startedAt) return '—';
		  const stamp = value => typeof value === 'number' ? value : Date.parse(value);
		  const elapsed = Math.max(0, (run.completedAt ? stamp(run.completedAt) : now) - stamp(run.startedAt));
		  return Number.isFinite(elapsed) ? `${Math.floor(elapsed / 1000)} 秒` : '—';
		}

		function useTrainerDialogFocus(close) {
		  useEffect(() => {
		    const previous = document.activeElement;
		    const dialog = document.querySelector('.trainer-modal');
		    const controls = () => [...(dialog?.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),summary') ?? [])];
		    controls()[0]?.focus();
		    const keydown = event => {
		      if (event.key === 'Escape') { event.preventDefault(); close(); }
		      if (event.key !== 'Tab') return;
		      const elements = controls(); const first = elements[0]; const last = elements.at(-1);
		      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
		      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
		    };
		    dialog?.addEventListener('keydown', keydown);
		    return () => { dialog?.removeEventListener('keydown', keydown); if (previous?.isConnected) previous.focus?.(); };
		  }, []);
		}

		function TrainerRunDetails({ store, compact = false, onDiagnose }) {
		  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		  const run = state.run;
		  const [stepId, setStepId] = useState(null);
		  const step = run?.steps?.find(item => item.stepId === stepId) ?? run?.steps?.[0];
		  const completed = run?.steps?.filter(item => item.status === 'completed').length ?? 0;
		  const control = action => { void store.perform('control', { runId: run.runId, action }).catch(() => {}); };
		  return createElement('section', { className: 'trainer-ui', 'data-testid': 'trainer-run-details' },
		    createElement('h2', null, '运行观察'),
		    createElement('strong', { className: trainerStatusClass(run?.status) }, trainerRunLabel(run?.status)),
		    createElement('p', null, run ? `完成 ${completed}/${run.steps?.length ?? 0} · ${trainerRunDuration(run)}` : '选择历史运行，或发起合成训练。'),
		    run && createElement('p', { className: 'trainer-meta' }, `本次匹配的测试断言 ${run.testResults?.length ?? 0} 项`),
		    createElement('div', { className: 'trainer-meta' }, run?.runId, run ? ` · ${run.purpose} · ${run.revisionId}` : ''),
		    run?.revisionId && state.project?.revisionId !== run.revisionId && createElement('p', { className: 'trainer-warning' }, `历史运行使用 ${run.revisionId}；当前候选 ${state.project?.revisionId ?? '读取中'}。`),
		    run?.cancellationRequested && createElement('p', { className: 'trainer-warning' }, run.childTerminationConfirmed === true ? '子任务终止已确认' : '已请求取消；子任务终止尚未确认'),
		    run?.error && createElement('pre', { className: 'trainer-error' }, trainerJson(run.error)),
		    state.events.length > 0 && createElement('p', { className: 'trainer-meta' }, '最近可见动作：', trainerJson(state.events[state.events.length - 1])),
		    !compact && run && createElement('div', null,
		      createElement('h3', null, '步骤顺序'),
		      (run.steps ?? []).map(item => createElement('button', { className: `trainer-object trainer-step trainer-status-${trainerStatusTone(item.status)}`, key: item.stepId, onClick: () => setStepId(item.stepId), 'aria-pressed': step?.stepId === item.stepId }, `${item.stepId} · ${item.agentId} · ${trainerRunLabel(item.status)}`)),
		      createElement('div', { className: 'trainer-meta' }, `包 SHA-256：${run.bundleSha256 ?? '未提供'}`),
		      createElement('div', { className: 'trainer-meta' }, `开始：${run.startedAt ?? '—'} · 更新：${run.updatedAt ?? '—'}`),
		      step && createElement('div', null,
		        createElement('h3', null, '实际输入'), createElement('pre', null, trainerJson(step.input)),
		        createElement('h3', null, '实际输出'), createElement('pre', null, trainerJson(step.output)),
		        createElement('h3', null, '子任务与装载证据'), createElement('pre', null, trainerJson({ parentSessionId: step.parentSessionId, childSessionId: step.childSessionId, actualLoadedRefs: step.actualLoadedRefs, error: step.error })))),
		    createElement('div', { className: 'trainer-controls' },
		      createElement('div', { className: 'trainer-row' }, ['pause', 'resume', 'stop'].map(action => {
		        const permission = trainerControlState(run, action);
		        const title = !permission.allowed ? permission.reason : state.busy ? '上一操作尚未完成' : { pause: '当前步骤结束后暂停后续派发', resume: '继续已暂停的运行', stop: '请求取消当前子任务并停止后续派发' }[action];
		        return createElement('button', { key: action, disabled: state.busy || !permission.allowed, title, onClick: () => control(action) }, { pause: '暂停', resume: '继续', stop: '停止' }[action]);
		      })),
		      createElement('div', { className: 'trainer-meta' }, ['pause', 'resume', 'stop'].map(action => {
		        const permission = trainerControlState(run, action);
		        return permission.allowed ? '' : `${{ pause: '暂停', resume: '继续', stop: '停止' }[action]}：${permission.reason}`;
		      }).filter(Boolean).join('；'))),
		    run && createElement('button', { disabled: state.busy, onClick: () => onDiagnose?.(run) }, '让 Trainer 诊断此运行'),
		    createElement('p', { className: 'trainer-meta' }, '仅验证合成训练框架 · 业务门禁未通过'));
		}

		function TrainerAssetEditor({ store, close }) {
		  useTrainerDialogFocus(close);
		  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		  const [base, setBase] = useState(null);
		  const [path, setPath] = useState('');
		  const [drafts, setDrafts] = useState({});
		  const [diff, setDiff] = useState(null);
		  const [error, setError] = useState('');
		  useEffect(() => {
		    let alive = true;
		    void store.perform('assets', {}, { mutation: false }).then(value => {
		      if (alive) { setBase(value); setPath(Object.keys(value.files ?? {})[0] ?? ''); setDrafts({ ...value.files }); }
		    }).catch(e => { if (alive) setError(e.message); });
		    return () => { alive = false; };
		  }, [store]);
		  const changes = base ? Object.keys(drafts).filter(name => drafts[name] !== base.files[name]).map(name => ({ path: name, content: drafts[name] })) : [];
		  const save = async freeze => {
		    setError('');
		    try {
		      let revisionId = base.revisionId;
		      if (freeze) {
		        const result = await store.perform('freeze', { revisionId, baseRevision: revisionId, changes, reason: '工作台保存并冻结当前编辑', linkedRunId: state.selectedRunId });
		        setBase({ ...base, revisionId: result.revisionId, files: { ...drafts } });
		        setDiff(result);
		      } else if (changes.length) {
		        const result = await store.perform('apply-changes', { baseRevision: revisionId, changes, reason: '工作台保存候选', linkedRunId: state.selectedRunId });
		        revisionId = result.revisionId;
		        setBase({ ...base, revisionId, files: { ...drafts } }); setDiff(result.diff);
		      }
		    } catch (e) { setError(e.message); }
		  };
		  return createElement('div', { className: 'trainer-modal-backdrop' }, createElement('section', { className: 'trainer-ui trainer-modal', role: 'dialog', 'aria-modal': true, 'aria-label': '候选资产与差异' },
		    createElement('div', { className: 'trainer-row' }, createElement('h2', null, '候选资产与差异'), createElement('button', { onClick: close }, '关闭')),
		    createElement('p', { className: 'trainer-meta' }, `编辑基线 ${base?.revisionId ?? '读取中'} · ${changes.length} 个未保存文件`),
		    createElement('select', { value: path, 'aria-label': '资产文件', onChange: e => setPath(e.target.value) }, Object.keys(drafts).map(name => createElement('option', { key: name, value: name }, name))),
		    createElement('textarea', { 'aria-label': '资产内容', value: drafts[path] ?? '', disabled: !base || state.mode !== 'training', onChange: e => setDrafts({ ...drafts, [path]: e.target.value }) }),
		    createElement('details', null, createElement('summary', null, '查看当前文件修改'), createElement('div', { className: 'trainer-diff' },
		      createElement('div', null, '保存前', createElement('pre', null, base?.files[path] ?? '')), createElement('div', null, '保存后', createElement('pre', null, drafts[path] ?? '')))),
		    diff && createElement('details', null, createElement('summary', null, '已保存变更记录'), createElement('pre', null, trainerJson(diff))),
		    createElement('div', { className: 'trainer-row' },
		      createElement('button', { disabled: !base || state.busy || state.mode !== 'training' || !changes.length, onClick: () => void save(false) }, '保存'),
		      createElement('button', { disabled: !base || state.busy || state.mode !== 'training', onClick: () => void save(true) }, '保存并冻结')),
		    (error || state.error) && createElement('p', { className: 'trainer-error', role: 'alert' }, error || state.error)));
		}

		function TrainerProjectDialog({ store, kind, close }) {
		  useTrainerDialogFocus(close);
		  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		  const [error, setError] = useState('');
		  const [agentId, setAgentId] = useState('');
		  const [name, setName] = useState('');
		  const [workflowId, setWorkflowId] = useState('');
		  const [workflowName, setWorkflowName] = useState('');
		  const [base, setBase] = useState(null);
		  const [workflow, setWorkflow] = useState(null);
		  const [selectedAgent, setSelectedAgent] = useState(state.project?.agents?.[0]?.agentId ?? '');
		  const [firstWorkflowAgent, setFirstWorkflowAgent] = useState(state.project?.agents?.[0]?.agentId ?? '');
		  const [secondWorkflowAgent, setSecondWorkflowAgent] = useState(state.project?.agents?.[1]?.agentId ?? '');
		  const [frozenVersionId, setFrozenVersionId] = useState(state.frozenVersion?.frozenVersionId ?? '');
		  const [evidenceRunId, setEvidenceRunId] = useState(state.selectedRunId ?? '');
		  const [releaseId, setReleaseId] = useState('');
		  const [beforeRunId, setBeforeRunId] = useState('');
		  const [afterRunId, setAfterRunId] = useState(state.selectedRunId ?? '');
		  const [result, setResult] = useState(null);
		  useEffect(() => {
		    let alive = true;
		    if (kind === 'agent' || kind === 'workflow' || kind === 'workflow-create') {
		      void store.perform('assets', {}, { mutation: false }).then(value => {
		        if (!alive) return;
		        setBase(value);
		        if (kind === 'workflow') {
		          const file = value.files[`workflows/${state.target.targetId}.json`];
		          if (!file) throw new Error('所选工作流文件不存在');
		          setWorkflow(JSON.parse(file));
		        }
		      }).catch(e => { if (alive) setError(e.message); });
		    }
		    if (kind === 'versions') void store.perform('releases', {}, { mutation: false }).catch(e => { if (alive) setError(e.message); });
		    return () => { alive = false; };
		  }, [kind, store]);
		  const action = async task => {
		    try { setError(''); const value = await task(); setResult(value); return value; }
		    catch (e) { setError(e.message); return null; }
		  };
		  const save = () => action(async () => {
		    const changes = kind === 'agent' ? trainerNewAgentChanges({ agentId, name })
		      : kind === 'workflow-create' ? trainerNewWorkflowChanges({ workflowId, name: workflowName, firstAgentId: firstWorkflowAgent, secondAgentId: secondWorkflowAgent })
		      : [{ path: `workflows/${workflow.workflowId}.json`, content: `${JSON.stringify(workflow, null, 2)}\n` }];
		    if (['agent', 'workflow-create'].includes(kind) && changes.some(change => Object.hasOwn(base.files, change.path))) throw new Error(`${kind === 'agent' ? 'Agent ID 或其合同文件' : '工作流 ID'} 已存在，请使用新 ID`);
		    const reason = kind === 'agent' ? '创建合成 Agent 模板' : kind === 'workflow-create' ? '创建合成工作流模板' : '编辑工作流步骤';
		    const saved = await store.perform('apply-changes', { baseRevision: base.revisionId, changes, reason, linkedRunId: state.selectedRunId });
		    setBase({ ...base, revisionId: saved.revisionId, files: { ...base.files, ...Object.fromEntries(changes.map(item => [item.path, item.content])) } });
		    return saved;
		  });
		  const runOptions = state.runs.filter(run => run.projectId === state.projectId).map(run => createElement('option', { key: run.runId, value: run.runId }, `${run.runId} · ${run.status} · ${run.revisionId}`));
		  const frozenVersions = trainerFrozenVersionsFor(state.frozenVersions ?? [], state.target);
		  const selectedFrozen = frozenVersions.find(version => version.frozenVersionId === frozenVersionId);
		  const knownRuns = [...new Map([...state.runs, ...(state.run ? [state.run] : [])].map(run => [run.runId, run])).values()];
		  const matchingRuns = trainerMatchingEvidence(knownRuns, selectedFrozen);
		  const evidence = matchingRuns.find(run => run.runId === evidenceRunId);
		  const agents = state.project?.agents ?? [];
		  return createElement('div', { className: 'trainer-modal-backdrop' }, createElement('section', { className: 'trainer-ui trainer-modal', role: 'dialog', 'aria-modal': true, 'aria-label': { agent: '新建 Agent', 'workflow-create': '新建工作流', workflow: '工作流顺序', versions: '冻结与发布', compare: '运行比较' }[kind] },
		    createElement('div', { className: 'trainer-row' }, createElement('h2', null, { agent: '新建 Agent', 'workflow-create': '新建工作流', workflow: '工作流顺序', versions: '冻结与发布', compare: '运行比较' }[kind]), createElement('button', { onClick: close }, '关闭')),
		    kind === 'agent' && createElement('div', { className: 'trainer-stack' },
		      createElement('label', null, 'Agent ID ', createElement('input', { value: agentId, onChange: e => setAgentId(e.target.value), placeholder: 'lab-new-agent' })),
		      createElement('label', null, '名称 ', createElement('input', { value: name, onChange: e => setName(e.target.value) })),
		      createElement('p', null, '创建合成指令与宽松 JSON 对象合同；注册后可独立训练或加入工作流。')),
		    kind === 'workflow-create' && createElement('div', { className: 'trainer-stack' },
		      createElement('p', { className: 'trainer-warning' }, '新工作流先创建两个不同 Agent 的步骤；保存后可在“工作流配置”中继续添加、删除、排序和修改输入映射。'),
		      createElement('label', null, '工作流 ID ', createElement('input', { value: workflowId, onChange: e => setWorkflowId(e.target.value), placeholder: 'dft-review-flow' })),
		      createElement('label', null, '工作流名称 ', createElement('input', { value: workflowName, onChange: e => setWorkflowName(e.target.value), placeholder: 'DFT 分析 → 复核' })),
		      createElement('label', null, '第 1 步 Agent ', createElement('select', { value: firstWorkflowAgent, onChange: e => setFirstWorkflowAgent(e.target.value), 'aria-label': '第 1 步 Agent' }, agents.map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, agent.name)))),
		      createElement('label', null, '第 2 步 Agent ', createElement('select', { value: secondWorkflowAgent, onChange: e => setSecondWorkflowAgent(e.target.value), 'aria-label': '第 2 步 Agent' }, agents.map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, agent.name)))),
		      createElement('p', { className: 'trainer-meta' }, '默认交接：第 1 步接收整个运行输入，第 2 步接收第 1 步的完整 JSON 输出；保存后可在步骤编辑器中改成 DFT 的实际字段。')),
		    kind === 'workflow' && workflow && createElement('div', { className: 'trainer-stack' },
		      createElement('p', { className: 'trainer-warning' }, '每一步都可以更换 Agent；步骤 ID 与输入映射会保留，但更换 Agent 后请检查输入输出合同和前序步骤引用。保存与运行均由服务端校验。'),
		      workflow.steps.map((step, index) => createElement('div', { key: step.stepId, className: 'trainer-step' },
		        createElement('div', { className: 'trainer-row' }, createElement('strong', null, `${index + 1}. ${step.agentId} · ${step.stepId}`),
		          createElement('button', { disabled: index === 0, onClick: () => setWorkflow(trainerMoveStep(workflow, index, -1)), 'aria-label': `上移 ${step.stepId}` }, '↑'),
		          createElement('button', { disabled: index === workflow.steps.length - 1, onClick: () => setWorkflow(trainerMoveStep(workflow, index, 1)), 'aria-label': `下移 ${step.stepId}` }, '↓'),
		          createElement('button', { disabled: workflow.steps.length === 1, onClick: () => setWorkflow({ ...workflow, steps: workflow.steps.filter(item => item.stepId !== step.stepId) }) }, '移除')),
		        createElement('label', null, 'Agent ', createElement('select', {
		          'aria-label': `${step.stepId} Agent`, value: step.agentId,
		          onChange: e => {
		            const agentId = e.target.value;
		            setError('');
		            setWorkflow({ ...workflow, steps: workflow.steps.map(item => {
		              if (item.stepId !== step.stepId) return item;
		              const next = { ...item, agentId };
		              // A frozen version belongs to the previous Agent and must not
		              // silently travel with a replacement Agent.
		              delete next.agentVersion;
		              return next;
		            }) });
		          }
		        }, agents.map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, `${agent.name} · ${agent.agentId}`)))),
		        createElement('label', null, '版本来源 ', createElement('select', {
		          'aria-label': `${step.stepId} 版本来源`, value: step.agentVersion?.kind === 'frozen' ? step.agentVersion.frozenVersionId : '',
		          onChange: e => { try { setWorkflow(trainerStepVersion(workflow, step.stepId, e.target.value, state.frozenVersions ?? [], state.projectId)); setError(''); } catch (error) { setError(error.message); } }
		        }, createElement('option', { value: '' }, '当前候选（运行开始时固定）'),
		        step.agentVersion?.kind === 'frozen' && !trainerFrozenVersionsFor(state.frozenVersions ?? [], { projectId: state.projectId, targetKind: 'agent', targetId: step.agentId }).some(version => version.frozenVersionId === step.agentVersion.frozenVersionId)
		          && createElement('option', { value: step.agentVersion.frozenVersionId, disabled: true }, `未找到冻结版本：${step.agentVersion.frozenVersionId}（保留原引用）`),
		        ...trainerFrozenVersionsFor(state.frozenVersions ?? [], { projectId: state.projectId, targetKind: 'agent', targetId: step.agentId }).map(version => createElement('option', { key: version.frozenVersionId, value: version.frozenVersionId }, trainerFrozenVersionLabel(version))))),
		        !Object.keys(step.inputBindings ?? {}).length && createElement('p', { className: 'trainer-warning', role: 'status' }, '此步骤尚未配置输入映射：运行时会收到整份运行输入，不会自动接收前一步输出。若需接收其他步骤的结果，请配置 source: "step"、stepId 和 pointer，并核对当前 Agent 的输入合同。'),
		        createElement('label', null, '输入映射 JSON（离开输入框时校验）', createElement('textarea', { style: { minHeight: '70px' }, defaultValue: trainerJson(step.inputBindings), onBlur: e => {
		          try { const inputBindings = JSON.parse(e.target.value); setError(''); setWorkflow({ ...workflow, steps: workflow.steps.map(item => item.stepId === step.stepId ? { ...item, inputBindings } : item) }); }
		          catch (error) { setError(`${step.stepId}: ${error.message}`); }
		        } })))),
		      createElement('div', { className: 'trainer-row' }, createElement('select', { value: selectedAgent, onChange: e => setSelectedAgent(e.target.value), 'aria-label': '添加步骤 Agent' }, (state.project?.agents ?? []).map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, agent.name))),
		        createElement('button', { disabled: !selectedAgent || workflow.steps.length >= 64, onClick: () => setWorkflow(trainerAppendStep(workflow, selectedAgent)) }, '添加步骤（可重复）'))),
		    ['agent', 'workflow-create', 'workflow'].includes(kind) && createElement('button', { disabled: !base || state.busy || state.mode !== 'training' || (kind === 'workflow' && (!workflow || !!error)), onClick: () => void save() }, '保存候选'),
		    kind === 'versions' && createElement('div', { className: 'trainer-stack' },
		      createElement('p', null, '发布使用匹配执行包的成功运行证据。服务端核验包摘要，不接受页面声明的成功。'),
		      createElement('label', null, '冻结版本 ', createElement('select', { value: frozenVersionId, 'aria-label': '冻结版本', onChange: e => { setFrozenVersionId(e.target.value); setEvidenceRunId(''); } },
		        createElement('option', { value: '' }, '请选择冻结版本（不自动选择最新）'),
		        frozenVersionId && !selectedFrozen && createElement('option', { value: frozenVersionId, disabled: true }, `未找到冻结版本：${frozenVersionId}`),
		        ...frozenVersions.map(version => createElement('option', { key: version.frozenVersionId, value: version.frozenVersionId }, trainerFrozenVersionLabel(version))))),
		      selectedFrozen && createElement('div', { className: 'trainer-meta' }, trainerFrozenVersionLabel(selectedFrozen)),
		      !frozenVersions.length && createElement('p', { className: 'trainer-meta' }, '该目标暂无已登记冻结版本；列表从服务端恢复。'),
		      createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => void action(async () => { const frozen = await store.perform('freeze', { revisionId: state.project.revisionId }); setFrozenVersionId(frozen.frozenVersionId); setEvidenceRunId(''); return frozen; }) }, '冻结当前已保存候选'),
		      createElement('label', null, '同包验证运行 ', createElement('select', { value: evidenceRunId, onChange: e => setEvidenceRunId(e.target.value) },
		        createElement('option', { value: '' }, '请选择同目标、同摘要的成功运行'),
		        evidenceRunId && !evidence && createElement('option', { value: evidenceRunId, disabled: true }, `${evidenceRunId}（未匹配当前冻结包）`),
		        ...matchingRuns.map(run => createElement('option', { key: run.runId, value: run.runId }, `${run.runId} · ${run.revisionId} · ${run.bundleSha256}`)))),
		      selectedFrozen && !matchingRuns.length && createElement('p', { className: 'trainer-warning' }, '已加载历史中没有此冻结包的成功记录。可加载更早运行，或让 Trainer 按此冻结版本进行合成验证。'),
		      createElement('button', { disabled: state.busy || !selectedFrozen || !evidence || state.mode === 'engineering', onClick: () => void action(async () => { const staged = await store.perform('stage-release', { frozenVersionId, runId: evidenceRunId }); setReleaseId(staged.releaseId); await store.perform('releases', {}, { mutation: false }); return staged; }) }, '生成自包含发布包'),
		      createElement('label', null, '发布版本 ', createElement('select', { value: releaseId, onChange: e => setReleaseId(e.target.value) }, createElement('option', { value: '' }, '请选择发布包'), ...(state.releases ?? []).map(release => createElement('option', { key: release.releaseId, value: release.releaseId }, `${release.releaseId} · ${release.targetKind}/${release.targetId}`)))),
		      createElement('button', { disabled: state.busy || !releaseId || state.mode === 'engineering', onClick: () => void action(() => store.perform('activate-release', { releaseId })) }, '激活所选发布版本')),
		    kind === 'compare' && createElement('div', { className: 'trainer-stack' },
		      createElement('label', null, '修改前 ', createElement('select', { value: beforeRunId, onChange: e => setBeforeRunId(e.target.value) }, createElement('option', { value: '' }, '请选择'), ...runOptions)),
		      createElement('label', null, '修改后 ', createElement('select', { value: afterRunId, onChange: e => setAfterRunId(e.target.value) }, createElement('option', { value: '' }, '请选择'), ...runOptions)),
		      createElement('button', { disabled: state.busy || !beforeRunId || !afterRunId, onClick: () => void action(() => store.perform('compare', { beforeRunId, afterRunId }, { mutation: false })) }, '比较版本与运行结果')),
		    result && createElement('pre', null, trainerJson(result)),
		    (error || state.error) && createElement('p', { className: 'trainer-error', role: 'alert' }, error || state.error)));
		}


		function TrainerSurfaceSidebar({ store, navigate, openDialog }) {
		  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		  const target = state.target;
		  // Selecting an Agent or workflow is a navigation action inside the
		  // workbench, not permission to create a native DSH session.  Native
		  // creation must remain behind the explicit session-card button so the
		  // button is stable and users can choose when to open a conversation.
		  const select = (kind, id, mode = state.mode, runId = null) => {
		    const next = { projectId: state.projectId, targetKind: kind, targetId: id };
		    trainerRememberTarget(next);
		    store.select(next, mode, runId);
		  };
		  const agents = state.project?.agents ?? [];
		  const workflows = state.project?.workflows ?? [];
		  return createElement('aside', { className: 'trainer-surface-side', 'aria-label': 'Agent 与工作流导航' },
		    createElement('button', { className: 'trainer-surface-nav ' + (!target ? 'selected' : ''), onClick: () => {
		      const first = workflows[0] ?? agents[0];
		      if (first) select(first.workflowId ? 'workflow' : 'agent', first.workflowId ?? first.agentId, 'training', null);
		    } }, '✣', createElement('strong', null, 'Agent Trainer')),
		    createElement('div', { className: 'trainer-surface-side-group' },
		      createElement('div', { className: 'trainer-surface-side-label' }, 'AGENTS ', createElement('span', { className: 'trainer-surface-count' }, agents.length)),
		      ...agents.map(agent => createElement('button', { className: 'trainer-surface-nav ' + (target?.targetKind === 'agent' && target.targetId === agent.agentId ? 'selected' : ''), key: agent.agentId, disabled: state.busy, onClick: () => select('agent', agent.agentId) }, '◌', createElement('span', null, agent.name))),
		      state.mode === 'training' && createElement('button', { className: 'trainer-surface-nav', disabled: state.busy, onClick: () => openDialog('agent') }, '+', createElement('span', null, '新建 Agent'))),
		    createElement('div', { className: 'trainer-surface-side-group' },
		      createElement('div', { className: 'trainer-surface-side-label' }, '工作流'),
		      ...workflows.map(flow => createElement('button', { className: 'trainer-surface-nav ' + (target?.targetKind === 'workflow' && target.targetId === flow.workflowId ? 'selected' : ''), key: flow.workflowId, disabled: state.busy, onClick: () => select('workflow', flow.workflowId) }, '⌘', createElement('span', null, flow.name), createElement('span', { className: 'trainer-surface-count' }, flow.steps?.length ?? ''))),
		      state.mode === 'training' && createElement('button', { className: 'trainer-surface-nav', disabled: state.busy, onClick: () => openDialog('workflow-create') }, '+', createElement('span', null, '新建工作流'))),
		    createElement('div', { className: 'trainer-surface-side-group' },
		      createElement('div', { className: 'trainer-surface-side-label' }, '观察与记录'),
		      createElement('button', { className: 'trainer-surface-nav', disabled: state.busy, onClick: () => openDialog('compare') }, '◷', createElement('span', null, '运行比较'))),
		    createElement('div', { className: 'trainer-surface-side-foot' }, createElement('strong', null, 'ATE-Coding-Flow'), createElement('div', null, state.mode === 'training' ? '训练候选 · 可编辑' : state.mode === 'published' ? '冻结版本 · 待发布' : '已激活版本 · 只读'), createElement('div', null, '仅合成训练 · 业务门禁未通过')));
		}

		function TrainerSurfaceMain({ store, navigate, openEditor, openDialog, diagnose, openNative }) {
		  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		  const [tab, setTab] = useState('chat');
		  const [inputText, setInputText] = useState('{}');
		  const [inputTargetKey, setInputTargetKey] = useState('');
		  const target = state.target;
		  const targetKey = target ? `${target.targetKind}:${target.targetId}` : '';
		  const defaultInputText = trainerWorkflowDefaultInputText(target, state.assets);
		  useEffect(() => {
		    if (!targetKey) return;
		    if (inputTargetKey === targetKey && !(inputText.trim() === '{}' && defaultInputText !== '{}')) return;
		    setInputText(defaultInputText);
		    setInputTargetKey(targetKey);
		  }, [defaultInputText, inputTargetKey, inputText, targetKey]);
		  const workflowSummary = target?.targetKind === 'workflow' ? (state.project?.workflows ?? []).find(item => item.workflowId === target.targetId) : null;
		  const assetWorkflow = state.assets?.files?.['workflows/' + target?.targetId + '.json'];
		  // Workflow summaries intentionally contain only identity fields. Only the
		  // selected candidate asset is authoritative for step count/order; when it is
		  // unavailable, keep the name from the summary but do not infer any steps.
		  let workflow = target?.targetKind === 'workflow' ? null : workflowSummary;
		  try { if (assetWorkflow) workflow = JSON.parse(assetWorkflow); } catch { workflow = null; /* editor shows the parse error */ }
		  const steps = workflow?.steps?.length ? workflow.steps : target?.targetKind === 'agent' ? [{ stepId: 'agent', agentId: target.targetId }] : [];
		  const stepCountLabel = target?.targetKind === 'workflow'
		    ? (Array.isArray(workflow?.steps) ? steps.length : '步骤待读取') : 1;
		  const selectedRun = state.run ?? (state.selectedRunId ? state.runs.find(item => item.runId === state.selectedRunId) : null);
		  const targetName = workflow?.name ?? workflowSummary?.name ?? state.project?.agents?.find(item => item.agentId === target?.targetId)?.name ?? target?.targetId ?? 'Agent Trainer';
		  const trainerSession = state.binding?.sessionId ?? null;
		  const runUnavailableReason = state.busy ? '正在处理操作或刷新状态，请稍候；完成后可再次运行。'
		    : !target ? '请先选择一个 Agent 或工作流。'
		      : state.mode === 'published' ? '发布模式不执行运行，请切换到训练模式或工程模式。'
		        : !state.binding ? '请先创建并打开 DSH 原生会话，绑定完成后即可运行。' : '';
		  const selectRun = run => {
		    if (!run) return;
		    const next = { projectId: run.projectId, targetKind: run.targetKind, targetId: run.targetId };
		    trainerRememberTarget(next);
		    const mode = run.purpose === 'FRAMEWORK_REPLAY' ? 'engineering' : 'training';
		    store.select(next, mode, run.runId); void navigate(next, mode, true, run.runId);
		  };
		  const start = async () => {
		    if (!target || !state.binding) { store.update({ error: TRAINER_UNBOUND_NOTICE }); return; }
		    let input;
		    try { input = JSON.parse(inputText); } catch (error) { store.update({ error: '运行输入 JSON 无效：' + error.message }); return; }
		    try {
		      const result = await store.perform('run', { input, ...(state.selectedRunId ? { derivedFromRunId: state.selectedRunId } : {}) });
		      const current = store.getSnapshot();
		      if (current.target && current.target.targetKind === target.targetKind && current.target.targetId === target.targetId && current.mode === state.mode) {
		        store.select(target, state.mode, result.runId);
		        void navigate(target, state.mode, state.binding?.presetId === 'agent-trainer' || target.targetKind === 'workflow', result.runId);
		      }
		    } catch { /* state.error is rendered below */ }
		  };
		  const error = state.error || state.readError;
		  const surfaceTone = trainerStatusTone(state.run?.status);
		  const modeLabel = state.mode === 'training' ? '训练工作区' : state.mode === 'published' ? '发布管理' : '工程执行';
		  const renderTab = tab === 'chat'
		    ? createElement('div', { className: 'trainer-surface-native-prompt' },
		        createElement('div', { className: 'trainer-surface-native-icon' }, '✣'),
		        createElement('div', null,
		          createElement('strong', null, trainerSession ? '已绑定 DSH 原生会话' : '尚未打开 DSH 原生会话'),
		          createElement('p', null, trainerSession ? '会话内容由 DSH 原生会话渲染。工作台不复制或伪造对话记录。' : '工作台只负责目标、流程和运行控制；打开原生会话后再输入消息。'),
		          createElement('div', { className: 'trainer-row' }, createElement('button', { className: 'trainer-surface-primary', disabled: state.busy || !target, onClick: openNative, title: state.busy ? '正在创建或打开 DSH 原生会话…' : (trainerSession ? '打开已绑定的 DSH 原生会话' : '创建并打开 DSH 原生会话') }, trainerSession ? '打开原生会话' : '创建并打开原生会话'), trainerSession && createElement('span', { className: 'trainer-meta' }, trainerSession))))
		    : tab === 'config'
		      ? createElement('div', { className: 'trainer-surface-plain' }, createElement('h3', null, '工作流配置'), createElement('p', null, target?.targetKind === 'workflow' ? '当前候选包含 ' + steps.length + ' 个步骤。' : 'Agent 候选由指令、Skill 和接口合同组成。'), createElement('button', { disabled: state.busy || !target, onClick: () => openDialog(target?.targetKind === 'workflow' ? 'workflow' : 'assets') }, target?.targetKind === 'workflow' ? '编辑步骤与输入映射' : '打开候选资产'))
		      : tab === 'diff'
		        ? createElement('div', { className: 'trainer-surface-plain' }, createElement('h3', null, '修改记录'), createElement('p', null, '当前候选版本：' + (state.project?.revisionId ?? '读取中')), createElement('p', { className: 'trainer-meta' }, state.assets ? '已加载候选资产，可在编辑器中查看完整文件差异。' : '修改候选后可查看完整文件差异。'), createElement('button', { disabled: state.busy || !target, onClick: openEditor }, '查看候选资产'))
		        : createElement('div', { className: 'trainer-surface-plain' }, createElement('h3', null, '运行记录'), state.runs.length ? createElement('div', { className: 'trainer-surface-run-list' }, ...state.runs.slice(0, 20).map(run => createElement('button', { key: run.runId, className: 'trainer-surface-run-row', onClick: () => selectRun(run), disabled: state.busy }, createElement('span', null, run.runId), createElement('span', { className: trainerStatusClass(run.status) }, trainerRunLabel(run.status) + ' · ' + run.revisionId)))) : createElement('p', null, '尚无运行记录。'), state.nextRunsCursor != null && createElement('button', { disabled: state.busy, onClick: () => void store.loadMoreRuns().catch(() => {}) }, '加载更早运行'));
		  return createElement('main', { className: 'trainer-surface-main' },
		    createElement('section', { className: 'trainer-surface-heading' }, createElement('div', { className: 'trainer-surface-crumb' }, modeLabel, ' 〉 ', target?.targetKind === 'agent' ? '单个 Agent' : '工作流', target ? ' 〉 Agent Trainer' : ''), createElement('div', { className: 'trainer-surface-heading-row' }, createElement('div', null, createElement('h1', null, targetName), createElement('div', { className: 'trainer-surface-subline' }, target ? (target.targetKind === 'workflow' ? '线性编排 · ' : '独立训练 · ') + stepCountLabel + (stepCountLabel === '步骤待读取' ? '' : ' 个执行步骤') + ' · 候选 ' + (state.project?.revisionId ?? '读取中') : '选择一个 Agent 或工作流开始训练')), createElement('div', { className: 'trainer-surface-actions' }, createElement('button', { disabled: state.busy || !target, onClick: openEditor }, '▣ 保存'), createElement('button', { disabled: state.busy || !target, onClick: () => openDialog('versions') }, '❄ 冻结 / 发布')))),
		    createElement('nav', { className: 'trainer-surface-tabs', 'aria-label': '训练工作区标签' }, ...[['chat', '训练会话'], ['config', '工作流配置'], ['diff', '修改记录'], ['runs', '运行记录']].map(item => createElement('button', { key: item[0], 'aria-pressed': tab === item[0], onClick: () => setTab(item[0]) }, item[1]))),
		    createElement('div', { className: 'trainer-surface-workarea' }, createElement('section', { className: 'trainer-surface-session', 'aria-label': 'Trainer 工作区' }, createElement('div', { className: 'trainer-surface-sessionbar' }, createElement('span', { className: `trainer-surface-led trainer-status-${surfaceTone}` }), trainerSession ? 'DSH 会话已绑定' : '工作台概览', ' · ', targetName, createElement('span', { style: { marginLeft: 'auto' } }, trainerSession ?? '未绑定')), renderTab, createElement('div', { className: 'trainer-surface-spacer' }), createElement('div', { className: 'trainer-surface-chips' }, createElement('button', { className: 'trainer-surface-chip', disabled: state.busy || !target, onClick: () => void store.refresh() }, '检查当前运行'), createElement('button', { className: 'trainer-surface-chip', disabled: state.busy || state.mode !== 'training' || !target, onClick: openEditor }, '修改并复测'), createElement('button', { className: 'trainer-surface-chip trainer-surface-primary', disabled: !!runUnavailableReason, title: runUnavailableReason || '运行当前候选', onClick: () => void start() }, '运行一次')), runUnavailableReason && createElement('p', { className: 'trainer-meta', role: 'status' }, runUnavailableReason), createElement('div', { className: 'trainer-surface-composer' }, createElement('label', { className: 'trainer-meta', htmlFor: 'trainer-surface-input' }, '合成运行输入 JSON'), createElement('textarea', { id: 'trainer-surface-input', 'aria-label': '运行输入 JSON', value: inputText, onChange: event => setInputText(event.target.value), placeholder: defaultInputText }), createElement('div', { className: 'trainer-surface-composer-bottom' }, createElement('span', null, '仅合成训练 · 不启动真实业务流'), createElement('button', { disabled: state.busy || !trainerSession, onClick: openNative }, '进入原生会话')))), createElement('aside', { className: 'trainer-surface-inspector', 'aria-label': '运行状态' }, createElement(TrainerRunDetails, { store, onDiagnose: diagnose }), selectedRun && createElement('div', { className: 'trainer-surface-status' }, '候选版本：' + (selectedRun.revisionId ?? '—') + ' · 业务门禁未通过'), error && createElement('p', { className: 'trainer-error', role: 'alert' }, error), state.notice && createElement('p', { className: 'trainer-surface-status', role: 'status' }, state.notice))));
		}

		function TrainerWorkbenchSurface({ store, navigate, openEditor, openDialog, diagnose, openNative }) {
		  const [surfaceTheme, setSurfaceTheme] = useState(trainerSurfaceTheme);
		  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		  useEffect(() => {
		    if (!state.enabled || state.surfaceVisible === false || state.target || !state.project) return;
		    const preferred = trainerPreferredTarget(state.projectId, state.project, state.runs);
		    // Opening the overview must not implicitly create or bind a native DSH
		    // session.  Selecting the first target loads its real project/assets;
		    // the user explicitly starts native-session work with the button in the
		    // session card.  This keeps the empty state recoverable when the host
		    // session index is still pending and avoids a surprise timeout on load.
		    if (preferred) { trainerRememberTarget(preferred); store.select(preferred, state.mode, null); }
		  }, [state.enabled, state.surfaceVisible, state.target, state.project, state.runs, state.loading, state.projectId, state.mode]);
		  if (!state.enabled || state.surfaceVisible === false) return null;
		  const toggleSurfaceTheme = () => {
		    const next = surfaceTheme === 'v2' ? 'v1' : 'v2';
		    setSurfaceTheme(next);
		    try { globalThis.localStorage?.setItem(TRAINER_SURFACE_THEME_KEY, next); } catch { /* optional UI preference */ }
		  };
		  return createElement('div', { className: `trainer-surface trainer-surface-${surfaceTheme}`, 'data-theme': surfaceTheme, 'data-ui-version': surfaceTheme.toUpperCase(), role: 'dialog', 'aria-label': 'DSH Agent Trainer 工作台' }, createElement('style', null, TRAINER_SURFACE_STYLES_V2),
		    createElement('header', { className: 'trainer-surface-top' }, createElement('div', { className: 'trainer-surface-brand' }, createElement('span', { className: 'trainer-surface-brand-mark' }, 'D'), createElement('strong', null, 'DSH'), ' / ', createElement('strong', null, 'PTC 工作台'), createElement('span', { className: 'trainer-surface-project' }, 'ATE-Coding-Flow')),
		      createElement('nav', { className: 'trainer-surface-modes', 'aria-label': '工作模式' }, ...[['training', '训练模式'], ['published', '发布模式'], ['engineering', '工程模式']].map(item => createElement('button', { key: item[0], 'aria-pressed': state.mode === item[0], disabled: state.busy, onClick: () => { const target = state.target; if (target) { store.select(target, item[0], null); void navigate(target, item[0], item[0] === 'training' || target.targetKind === 'workflow', null); } else store.select(null, item[0]); } }, item[1]))),
		      createElement('span', { className: 'trainer-surface-demo' }, `${surfaceTheme.toUpperCase()} · 合成训练·演示数据`), createElement('button', { className: 'trainer-surface-theme-toggle', onClick: toggleSurfaceTheme, title: surfaceTheme === 'v2' ? '切换到 V1 当前样式' : '切换到 V2 试用样式' }, surfaceTheme === 'v2' ? 'V1 样式' : 'V2 样式'), createElement('button', { className: 'trainer-surface-close', onClick: () => store.update({ surfaceVisible: false }) }, '收起')),
		    createElement('div', { className: 'trainer-surface-shell' }, createElement(TrainerSurfaceSidebar, { store, navigate, openDialog }), createElement(TrainerSurfaceMain, { store, navigate, openEditor, openDialog, diagnose, openNative })));
		}

		function TrainerSidebar({ store, navigate, openEditor, openDialog, wide = true, expandSidebar }) {
		  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		  const [inputText, setInputText] = useState('{}');
		  const [tab, setTab] = useState('objects');
		  const [localError, setLocalError] = useState('');
		  const target = state.target;
		  const select = (kind, id, mode = state.mode, trainer = false, runId = null) => {
		    const next = { projectId: state.projectId, targetKind: kind, targetId: id };
		    store.select(next, mode, runId);
		    void navigate(next, mode, trainer, runId);
		  };
		  const start = async () => {
		    try {
		      setLocalError('');
		      const result = await store.perform('run', { input: JSON.parse(inputText), ...(state.selectedRunId ? { derivedFromRunId: state.selectedRunId } : {}) });
		      const current = store.getSnapshot();
		      if (current.target?.targetKind === target.targetKind && current.target?.targetId === target.targetId && current.mode === state.mode) select(target.targetKind, target.targetId, state.mode, state.binding?.presetId === 'agent-trainer', result.runId);
		    } catch (error) { setLocalError(error.message); }
		  };
		  if (!wide) return createElement('div', { className: 'trainer-ui' }, createElement('button', { title: '展开 Agent Trainer', onClick: expandSidebar }, 'AT'));
		  return createElement('aside', { className: 'trainer-ui trainer-nav', 'data-testid': 'trainer-sidebar' },
		    createElement('h2', null, 'Agent Trainer'),
		    createElement('div', { className: 'trainer-meta' }, state.projectId),
		    createElement('div', { className: 'trainer-row' }, ['training', 'published', 'engineering'].map(mode => createElement('button', { key: mode, disabled: state.busy, 'aria-pressed': state.mode === mode,
		      onClick: () => { if (target) select(target.targetKind, target.targetId, mode); else store.select(null, mode); } }, { training: '训练', published: '发布', engineering: '工程' }[mode]))),
		    target && createElement('p', { className: 'trainer-meta' }, `${target.targetKind} / ${target.targetId} · 候选 ${state.project?.revisionId ?? '—'}`),
		    createElement('div', { className: 'trainer-row' }, ['objects', 'history', 'observe'].map(value => createElement('button', { key: value, 'aria-pressed': tab === value, onClick: () => setTab(value) }, { objects: '对象', history: '历史', observe: '观察' }[value]))),
		    tab === 'objects' && createElement('div', null,
		      createElement('h3', null, '已登记 Agent'), createElement('div', { className: 'trainer-stack' }, (state.project?.agents ?? []).map(agent => createElement('button', { className: 'trainer-object', key: agent.agentId, disabled: state.busy, 'aria-pressed': target?.targetKind === 'agent' && target.targetId === agent.agentId, onClick: () => select('agent', agent.agentId) }, agent.name))),
		      createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => openDialog('agent') }, '新建 Agent'),
		      createElement('h3', null, '工作流'), createElement('div', { className: 'trainer-stack' }, (state.project?.workflows ?? []).map(flow => createElement('button', { className: 'trainer-object', key: flow.workflowId, disabled: state.busy, 'aria-pressed': target?.targetKind === 'workflow' && target.targetId === flow.workflowId, onClick: () => select('workflow', flow.workflowId) }, flow.name))),
		      state.mode === 'training' && createElement('button', { disabled: state.busy, onClick: () => openDialog('workflow-create') }, '新建工作流'),
		      !state.project && createElement('p', null, state.loading ? '读取项目…' : '项目尚未就绪'),
		      target && createElement('div', { className: 'trainer-stack' },
		        createElement('h3', null, '训练与版本'),
		        createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => { store.update({ surfaceVisible: true }); select(target.targetKind, target.targetId, 'training', true, state.selectedRunId); } }, '打开 Agent Trainer'),
		        createElement('button', { disabled: state.busy, onClick: openEditor }, state.mode === 'training' ? '编辑候选 / 保存 / 冻结' : '查看候选（只读）'),
		        target.targetKind === 'workflow' && createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => openDialog('workflow') }, '编辑步骤与顺序'),
		        createElement('button', { disabled: state.busy, onClick: () => openDialog('versions') }, '冻结 / 发布 / 激活'),
		        createElement('button', { disabled: state.busy, onClick: () => openDialog('compare') }, '比较运行与修改'),
		        createElement('label', null, '运行输入 JSON', createElement('textarea', { 'aria-label': '运行输入 JSON', value: inputText, onChange: e => setInputText(e.target.value), rows: 3, style: { width: '100%' } })),
		        createElement('button', { className: 'trainer-primary', disabled: state.busy || !state.binding || state.mode === 'published', onClick: () => void start() }, state.mode === 'engineering' ? '运行活动发布版' : '运行当前候选'))),
		    tab === 'history' && createElement('div', { className: 'trainer-stack' }, state.runs.map(run => createElement('button', { key: run.runId, className: 'trainer-object', disabled: state.busy, onClick: () => select(run.targetKind, run.targetId, run.purpose === 'FRAMEWORK_REPLAY' ? 'engineering' : 'training', true, run.runId) }, createElement('span', null, run.runId, createElement('div', { className: 'trainer-meta' }, `${trainerRunLabel(run.status)} · ${run.revisionId}`))))),
		    tab === 'history' && state.nextRunsCursor != null && createElement('button', { disabled: state.busy, onClick: () => void store.loadMoreRuns().catch(() => {}) }, '加载更早运行'),
		    tab === 'observe' && createElement(TrainerRunDetails, { store, compact: true, onDiagnose: run => select(run.targetKind, run.targetId, 'training', true, run.runId) }),
		    createElement('p', { className: 'trainer-empty trainer-meta' }, '布局帮助：新建空会话时，可在左栏“观察”查看运行；非空会话可用顶部“运行观察”打开右栏。'),
		    createElement('div', { className: 'trainer-row' }, createElement('button', { onClick: () => store.update({ detailsVisible: !state.detailsVisible }) }, state.detailsVisible ? '原生工具详情' : '运行观察右栏'), createElement('button', { onClick: () => store.enable(false) }, '退出工作台')),
		    state.notice && createElement('p', { role: 'status' }, state.notice),
		    (localError || state.error || state.readError) && createElement('p', { role: 'alert', className: 'trainer-error' }, localError || state.error || state.readError));
		}

		// Public slot registrations are acquired only while this workbench owns the surface.
		function installTrainerWorkbench(ctx, { store = createTrainerStore() } = {}) {
		  const navigator = createTrainerNavigator({ services: ctx, api: store.api });
		  let navigationVersion = 0;
		  let disposed = false;
		  let editorOpen = false;
		  const editorListeners = new Set();
		  const setEditor = value => { editorOpen = value; editorListeners.forEach(fn => fn()); };
		  const navigate = async (target, mode, trainer, selectedRunId) => {
		    navigationVersion += 1;
		    try {
		      const binding = await navigator.open({ target, mode, trainer, selectedRunId, title: `${trainer ? 'Agent Trainer' : 'Framework'} · ${target.targetId}` });
		      store.setBinding(binding);
		      return binding;
		    } catch (error) { if (error.name !== 'AbortError') store.update({ error: error.message }); return null; }
		  };
		  const openNative = async () => {
		    let current = store.getSnapshot();
		    if (current.busy) return;
		    let target = current.target;
		    if (!target) {
		      target = trainerPreferredTarget(current.projectId, current.project, current.runs);
		      if (!target) { store.update({ error: '项目尚无可用 Agent 或工作流' }); return; }
		      trainerRememberTarget(target);
		      store.select(target, current.mode, null);
		      current = store.getSnapshot();
		    }
		    store.update({ busy: true, error: null, notice: '正在创建或打开 DSH 原生会话…' });
		    try {
		      const binding = await navigate(target, current.mode, current.mode === 'training' || target.targetKind === 'workflow', current.selectedRunId);
		      if (!binding) { store.update({ notice: '' }); return; }
		      current = store.getSnapshot();
		      if (!current.binding?.sessionId) throw new Error('原生会话绑定未完成');
		      store.update({ surfaceVisible: false, detailsVisible: false, notice: '已切换到 DSH 原生会话；工作台仍保留在 Agent Trainer 入口。' });
		    } catch (error) {
		      if (error.name !== 'AbortError') store.update({ error: error.message, notice: '' });
		      else store.update({ notice: '' });
		    }
		    finally { store.update({ busy: false }); }
		  };
		  const diagnose = run => {
		    const target = { projectId: run.projectId, targetKind: run.targetKind, targetId: run.targetId };
		    store.select(target, 'training', run.runId); void navigate(target, 'training', true, run.runId);
		  };
		  const Footer = () => {
		    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		    return createElement('div', { className: 'trainer-ui' }, createElement('style', null, TRAINER_STYLES), createElement('button', { onClick: () => state.enabled ? store.update({ surfaceVisible: !state.surfaceVisible }) : store.enable(true), 'aria-pressed': state.enabled }, 'Agent Trainer'));
		  };
		  const Sidebar = props => createElement(TrainerSidebar, { ...props, store, navigate, openEditor: () => setEditor('assets'), openDialog: setEditor });
		  const Details = ({ sessionId }) => {
		    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		    const sessions = useSyncExternalStore(ctx.sessions.list.subscribe, ctx.sessions.list.getSnapshot, ctx.sessions.list.getSnapshot);
		    const blank = sessions.byId[sessionId]?.blank !== false;
		    useEffect(() => {
		      if (!blank && state.enabled && state.binding?.sessionId === sessionId && state.detailsVisible) ctx.layout?.openDetails?.();
		    }, [sessionId, blank, state.binding?.bindingRevision, state.enabled, state.detailsVisible]);
		    return createElement('div', { className: 'trainer-ui trainer-details' }, createElement('button', { onClick: () => store.update({ detailsVisible: false }) }, '切回原生工具详情'), createElement(TrainerRunDetails, { store, onDiagnose: diagnose }));
		  };
		  const Header = ({ sessionId }) => {
		    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		    if (!state.enabled || state.binding?.sessionId !== sessionId) return null;
		    return createElement('div', { className: 'trainer-ui trainer-header' }, createElement('div', { className: 'trainer-meta' }, `${state.binding.presetId} · ${state.target.targetId} · ${state.selectedRunId ?? '未选择运行'}`), createElement('button', { onClick: () => { store.update({ detailsVisible: true }); ctx.layout?.openDetails?.(); } }, '运行观察'));
		  };
		  const EditorLayer = () => {
		    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
		    const open = useSyncExternalStore(fn => { editorListeners.add(fn); return () => editorListeners.delete(fn); }, () => editorOpen, () => false);
		    return open && state.enabled ? createElement(open === 'assets' ? TrainerAssetEditor : TrainerProjectDialog, { key: `${state.projectId}/${state.target?.targetId}/${state.mode}/${open}`, kind: open, store, close: () => setEditor(false) }) : null;
		  };
		  const fixed = [
		    ctx.slots.inject('sidebar.footer.action', () => ctx.slots.register({ name: 'sidebar.footer.action', id: 'trainer-entry', order: 50 }, Footer)),
		    ctx.slots.inject('conversation.session.header.actions', () => ctx.slots.register({ name: 'conversation.session.header.actions', id: 'trainer-binding', order: -20 }, Header)),
		    ctx.slots.inject('shell.overlay', () => ctx.slots.register({ name: 'shell.overlay', id: 'trainer-editor', order: 95 }, EditorLayer)),
		    // Host fallback only: this surface is a truthful trainer overview; DSH conversation/composer stays native.
		    ctx.slots.inject('shell.overlay', () => ctx.slots.register({ name: 'shell.overlay', id: 'trainer-surface', order: 100 }, () => createElement(TrainerWorkbenchSurface, { store, navigate, openEditor: () => setEditor('assets'), openDialog: setEditor, diagnose, openNative })))
		  ];
		  let sidebarDispose = null;
		  let detailsDispose = null;
		  let observedSession;
		  let observing = false;
		  let restoreVersion = 0;
		  function restore(current) {
		    const version = ++restoreVersion;
		    const navigation = navigationVersion;
		    if (!current) { store.update({ binding: null }); return; }
		    void store.api('bind-session', { projectId: store.getSnapshot().projectId, sessionId: current }).then(binding => {
		      if (disposed || version !== restoreVersion || navigation !== navigationVersion || !store.getSnapshot().enabled || ctx.sessions.list.getSnapshot().current !== current) return;
		      if (binding.projectId !== store.getSnapshot().projectId) throw new Error('当前会话属于其他项目');
		      if (store.getSnapshot().binding?.sessionId === current) return;
		      store.select({ projectId: binding.projectId, targetKind: binding.targetKind, targetId: binding.targetId }, binding.mode, binding.selectedRunId ?? null);
		      store.setBinding(binding);
		    }).catch(error => {
		      if (disposed || version !== restoreVersion || navigation !== navigationVersion || !store.getSnapshot().enabled || ctx.sessions.list.getSnapshot().current !== current) return;
		      store.select(null);
		      store.update({ notice: error.code === 'session_unbound' ? TRAINER_UNBOUND_NOTICE : '', error: error.code === 'session_unbound' ? null : error.message });
		    });
		  }
		  function reconcile() {
		    const state = store.getSnapshot();
		    const current = ctx.sessions.list.getSnapshot().current;
		    try { globalThis.localStorage?.setItem('trainer-workbench-enabled-v1', state.enabled ? 'true' : 'false'); } catch { /* optional UI preference */ }
		    if (state.enabled && (!observing || current !== observedSession)) {
		      observing = true; observedSession = current; restore(current);
		    }
		    if (!state.enabled) { observing = false; restoreVersion += 1; }
		    if (state.enabled && !sidebarDispose) sidebarDispose = ctx.slots.inject('sidebar.workspaces', () => ctx.slots.register({ name: 'sidebar.workspaces', id: 'trainer-navigation', priority: -50 }, Sidebar));
		    if (!state.enabled && sidebarDispose) { sidebarDispose(); sidebarDispose = null; navigator.cancel(); setEditor(false); }
		    const show = state.enabled && state.detailsVisible && current && state.binding?.sessionId === current;
		    if (show && !detailsDispose) detailsDispose = ctx.slots.inject('details', () => ctx.slots.register({ name: 'details', id: 'trainer-observer', priority: -50 }, Details));
		    if (!show && detailsDispose) { detailsDispose(); detailsDispose = null; }
		  }
		  fixed.push(store.subscribe(reconcile), ctx.sessions.list.subscribe(reconcile));
		  let restoreEnabled = false;
		  try {
		    const savedEnabled = globalThis.localStorage?.getItem('trainer-workbench-enabled-v1');
		    // First use opens the white Trainer workbench. After that, the user's
		    // explicit close/disable preference remains authoritative.
		    restoreEnabled = savedEnabled == null ? true : savedEnabled === 'true';
		  } catch { restoreEnabled = true; /* optional UI preference */ }
		  if (restoreEnabled) store.enable(true);
		  reconcile();
		  return () => {
		    disposed = true; restoreVersion += 1;
		    navigator.cancel(); store.dispose(); sidebarDispose?.(); detailsDispose?.();
		    fixed.reverse().forEach(dispose => dispose()); editorListeners.clear();
		  };
		}

		/**
		 * PTC control-plane client entry.
		 *
		 * Follows the DSH client-plugin module contract used by
		 * @nanmicoder/dsh-agent-teams: the bundled module exposes
		 *
		 *   exports.inject = [service names]
		 *   exports.apply  = (ctx) => { register slots / locale / effects }
		 *
		 * and the host loads it via window.__ModuleLoader__.load({ id, factory }).
		 * The package entry (owned by the integrator) re-exports these and declares
		 * the matching `dsh.client.inject` host packages in package.json.
		 *
		 * This skeleton only READS state from GET /api/ptc-control/state (see
		 * lib/control-state.js for the schemaVersion 1 contract) and mounts a
		 * read-only panel through the native client slot registry. It performs no
		 * writes and registers no commands.
		 */

		/** Locale namespace for this plugin. */
		const PTC_CONTROL_PLANE_LOCALE_NAMESPACE = "ptc-control-plane";

		/** Locale dictionaries (zh / en), mirroring the agent-teams pattern. */
		const localeDictionaries = {
		  zh: {
		    "panel.title": "PTC 控制面",
		    "status.identity": "当前身份",
		    "status.activeRelease": "活动 Release",
		    "status.trainingRuns": "训练运行",
		    "status.delivery": "正式交付",
		    "status.noRelease": "无活动 Release",
		    "status.error": "状态读取失败",
		    "view.training": "PTC Training",
		    "view.runtime": "ATE PTC Runtime",
		    "training.runs": "训练运行",
		    "training.profile": "选择专家",
		    "training.testItem": "测试项",
		    "training.createProfile": "创建单专家训练",
		    "training.createPipeline": "创建全流程训练",
		    "training.created": "已创建隔离训练运行",
		    "training.createFailed": "创建失败",
		    "training.noModel": "未派发模型",
		    "training.modelDispatched": "已派发训练专家",
		    "delivery.label": "正式交付",
		    "delivery.none": "暂无正式交付批次",
		    "delivery.batchId": "批次",
		    "delivery.state": "阶段",
		    "delivery.releaseId": "Release",
		    "delivery.scope": "执行范围",
		    "delivery.updatedAt": "更新时间"
		  },
		  en: {
		    "panel.title": "PTC Control Plane",
		    "status.identity": "Identity",
		    "status.activeRelease": "Active release",
		    "status.trainingRuns": "Training runs",
		    "status.delivery": "Delivery",
		    "status.noRelease": "No active release",
		    "status.error": "Failed to read state",
		    "view.training": "PTC Training",
		    "view.runtime": "ATE PTC Runtime",
		    "training.runs": "Training runs",
		    "training.profile": "Select expert",
		    "training.testItem": "Test item",
		    "training.createProfile": "Create profile training",
		    "training.createPipeline": "Create pipeline training",
		    "training.created": "Isolated training run created",
		    "training.createFailed": "Creation failed",
		    "training.noModel": "No model dispatched",
		    "training.modelDispatched": "Training expert dispatched",
		    "delivery.label": "Delivery",
		    "delivery.none": "No delivery batch yet",
		    "delivery.batchId": "Batch",
		    "delivery.state": "Stage",
		    "delivery.releaseId": "Release",
		    "delivery.scope": "Scope",
		    "delivery.updatedAt": "Updated"
		  }
		};

		/** Required host client services: slot registry and locale. */
		const inject = ["slots", "locale"];

		/** Slot mount point proven to exist in the current DSH web client. */
		const SHELL_SLOT_NAME = "shell.overlay";
		const PANEL_SLOT_ID = "ptc-control-plane";

		/**
		 * Install the plugin into a DSH client context.
		 *
		 * @param {{ slots: object, locale: object, effect: Function }} ctx
		 */
		function apply(ctx) {
		  ctx.effect(
		    () => ctx.locale.register(PTC_CONTROL_PLANE_LOCALE_NAMESPACE, localeDictionaries),
		    "ptc-control-plane: dictionaries"
		  );

		  const store = createPtcStateStore();

	  // Always mount the public white workbench from the root slot first. Some DSH
	  // hosts expose an `inject` function but never resolve the optional native
	  // session services while the app is in the blank/new-session state. Waiting
	  // for that callback made the Trainer disappear even though the plugin itself
	  // was loaded. The fallback keeps the workbench visible; when native services
	  // are available they can still be used by a future host integration.
	  let trainerInstalled = false;
	  const mountTrainer = services => {
	    if (trainerInstalled) return;
    // Service injection can be reported before the slot provider is ready.
    // Ignore that partial context and let the native-service injection retry.
    if (!services?.slots?.inject || !services?.slots?.register) {
      try { console.warn('[ptc trainer] slot service unavailable', JSON.stringify({ keys: Object.keys(services || {}), slotsKeys: Object.keys(services?.slots || {}), directInject: typeof services?.inject, slotInject: typeof services?.slots?.inject, slotRegister: typeof services?.slots?.register })); } catch { /* diagnostics only */ }
      return;
    }
	    trainerInstalled = true;
	    const trainerServices = services.layout ? services : { ...services, layout: { openDetails() {} } };
	    (typeof services.effect === "function" ? services.effect.bind(services) : ctx.effect)(() => installTrainerWorkbench(trainerServices), "trainer: public workbench slots");
	  };
  const fallbackSessions = { list: {
	    getSnapshot: () => ({ current: null, byId: {}, phase: 'ready' }),
	    subscribe: () => () => {}
  } };
  const fallbackServices = { ...ctx, sessions: fallbackSessions, workspaces: {}, connection: null,
    layout: { openDetails() {} }, effect: ctx.effect.bind(ctx) };
  if (typeof ctx.inject === "function") {
    // Request the two required host services separately so the workbench can
    // mount even when optional native session services are unavailable on a
    // blank DSH screen.
    ctx.inject(["slots", "locale"], services => mountTrainer({ ...services, sessions: fallbackSessions, workspaces: {}, connection: null, layout: { openDetails() {} } }));
    ctx.inject(["connection", "sessions", "workspaces"], services => mountTrainer(services));
  }
  // A few hosts expose slots directly on the apply context. Use that path only
  // when it is actually present; otherwise the service injection above is the
  // safe source of the slot registry.
  if (ctx.slots?.inject) mountTrainer(fallbackServices);

		  const mount = (sessionServices = null) => {
		    const Panel = ({ t }) => createElement(PtcControlPanel, { store, t, sessionServices });
		    ctx.slots.inject(SHELL_SLOT_NAME, () => ctx.slots.register(
		      { name: SHELL_SLOT_NAME, id: PANEL_SLOT_ID, order: 90,
		        label: "PTC control plane", locale: PTC_CONTROL_PLANE_LOCALE_NAMESPACE }, Panel));
		  };

		  // Native slot injection: the host places the panel in its overlay region.
		  if (typeof ctx.inject === "function") {
		    ctx.inject(["connection", "sessions", "workspaces"],
		      sessionServices => mount(sessionServices));
		  } else mount(null);
		}
		exports.apply = apply;
		exports.inject = inject;
		return module.exports;
	}
});
