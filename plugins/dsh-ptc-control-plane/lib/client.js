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
		    body: JSON.stringify({ runId, testItems, ...(options.modelChoice ? { modelChoice: options.modelChoice } : {}) })
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) {
		    throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  }
		  return body;
		}

		function executeBusinessTrainingRunRequest(runId, testItems, options = {}) {
		  return executeTrainingRunRequest(runId, testItems, {
		    ...options, url: options.url ?? EXECUTE_BUSINESS_TRAINING_URL,
		  });
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

		function executeBusinessPipelineRequest(runId, testItems, options = {}) {
		  return executeTrainingPipelineRequest(runId, testItems, {
		    ...options, url: options.url ?? EXECUTE_BUSINESS_PIPELINE_URL,
		  });
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

		function controlBusinessPipelineRequest(runId, action, options = {}) {
		  return controlTrainingPipelineRequest(runId, action, {
		    ...options, url: options.url ?? CONTROL_BUSINESS_PIPELINE_URL,
		  });
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

		function normalizeBusinessAgent(raw) {
		  const record = raw !== null && typeof raw === 'object' ? raw : {};
		  const resources = key => Array.isArray(record[key]) ? record[key].filter(item => item && typeof item.path === 'string')
		    .map(item => ({ path: item.path, used: item.used === true })) : [];
		  return {
		    profileId: text(record.profileId, 'unknown-agent'),
		    kind: text(record.kind, 'agent'),
		    displayName: text(record.displayName, 'Agent'),
		    latestRunId: optionalText(record.latestRunId),
		    latestRunStatus: optionalText(record.latestRunStatus),
		    inputs: resources('inputs'), outputs: resources('outputs'),
		    skills: resources('skills'), scripts: resources('scripts'),
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

		function sessionPreset(binding) {
		  const session = binding?.session ?? binding;
		  const events = Array.isArray(session?.events) ? session.events : [];
		  for (let i = events.length - 1; i >= 0; i -= 1) {
		    if (events[i]?.type === 'agent-preset/selected') return events[i].data?.agentPreset;
		  }
		  return session?.header?.agentPreset;
		}

		const NATIVE_READINESS_TIMEOUT_MS = 30_000;
		const NATIVE_REFRESH_TIMEOUT_MS = 10_000;

		function notListed(sessionId, reused = false) {
		  return Object.assign(new Error(`NATIVE_SESSION_NOT_LISTED: 服务端已${reused ? '复用' : '绑定'}会话 ${sessionId}，但宿主会话列表未加载该会话，请刷新 DSH 页面后重试，或点击「新开训练会话」继续。`),
		    { code: 'NATIVE_SESSION_NOT_LISTED', sessionId });
		}

		async function refreshForBinding(scope, sessionId, deadline, reused = false, workspacePath = null) {
		  const sessions = scope.sessions;
		  if (sessions.binding(sessionId) !== undefined) return;
		  // A freshly opened host can start with no selected workspace. Registering the
		  // server-approved Trainer workspace is idempotent and lets SessionRuntime's
		  // list mirror include persisted sessions before refresh() runs.
		  if (workspacePath && typeof scope.workspaces?.create === 'function') {
		    let timer;
		    let workspaceResult;
		    try {
		      workspaceResult = await Promise.race([
		        Promise.resolve().then(() => scope.workspaces.create({ path: workspacePath })),
		        new Promise((_, reject) => { timer = window.setTimeout(() => reject(notListed(sessionId, reused)),
		          Math.max(0, Math.min(NATIVE_REFRESH_TIMEOUT_MS, deadline - Date.now()))); }),
		      ]);
		    } finally { window.clearTimeout(timer); }
		    // A cold host may have a persisted session that is not in the browser's
		    // list yet. Adopt the server-approved ID explicitly after registering its
		    // workspace; DSH's create path resumes an existing live/persisted session
		    // and publishes it to the list without minting a replacement ID.
		    const workspaceId = workspaceResult?.value?.workspace?.workspaceId
		      ?? workspaceResult?.workspace?.workspaceId
		      ?? workspaceResult?.workspaceId;
		    if (workspaceId && typeof sessions.create === 'function'
		      && sessions.binding(sessionId) === undefined) {
		      let createTimer;
		      try {
		        await Promise.race([
		          Promise.resolve().then(() => sessions.create({ sessionId, workspaceId })),
		          new Promise((_, reject) => { createTimer = window.setTimeout(() => reject(notListed(sessionId, reused)),
		            Math.max(0, Math.min(NATIVE_REFRESH_TIMEOUT_MS, deadline - Date.now()))); }),
		        ]);
		      } finally { window.clearTimeout(createTimer); }
		    }
		    if (sessions.binding(sessionId) !== undefined) return;
		  }
		  if (typeof sessions.refresh !== 'function') return;
		  let timer;
		  try {
		    await Promise.race([
		      Promise.resolve().then(() => sessions.refresh()),
		      new Promise((_, reject) => { timer = window.setTimeout(() => reject(notListed(sessionId, reused)),
		        Math.max(0, Math.min(NATIVE_REFRESH_TIMEOUT_MS, deadline - Date.now()))); }),
		    ]);
		  } finally { window.clearTimeout(timer); }
		}

		function waitForBinding(sessions, sessionId, deadline = Date.now() + NATIVE_READINESS_TIMEOUT_MS, reused = false) {
		  const ready = sessions.binding(sessionId);
		  if (ready !== undefined) return Promise.resolve(ready);
		  return new Promise((resolve, reject) => {
		    let unsubscribe = () => {};
		    let settled = false;
		    const finish = (error, binding) => {
		      if (settled) return;
		      settled = true;
		      window.clearTimeout(timeout);
		      unsubscribe();
		      if (error) reject(error); else resolve(binding);
		    };
		    const timeout = window.setTimeout(() => finish(notListed(sessionId, reused)), Math.max(0, deadline - Date.now()));
		    const check = () => {
		      const binding = sessions.binding(sessionId);
		      if (binding !== undefined) finish(null, binding);
		    };
		    unsubscribe = sessions.list.subscribe(check);
		    if (settled) unsubscribe(); else check();
		  });
		}

		async function openPtcSessionView(scope, sessionId) {
		  await scope.sessions.open(sessionId);
		  const snapshot = scope.sessions.list?.getSnapshot?.();
		  if (snapshot && snapshot.current !== sessionId) {
		    throw new Error('OPEN_FAILED: DSH 没有选中请求的原生会话');
		  }
		}

		/** Create or reopen a genuine DSH conversation rooted in its server-approved workspace. */
		async function openPtcNativeSession(scope, workspace, {
		  key, title, agentPreset = 'standard', rememberedSessionId, validateRemembered, beforeOpen,
		}) {
		  const api = typeof scope?.get === 'function' ? scope.get('connection')?.api : scope?.connection?.api;
		  if (!api?.sessions?.create || !scope?.sessions) {
		    throw new Error('DSH 原生会话服务尚未注入；请确认本机 DSH 已加载会话与工作区服务。');
		  }
		  const remembered = rememberedSessionId || existingSessionId(key);
		  if (remembered) {
		    const rememberedBinding = scope.sessions.binding(remembered);
		    if (rememberedBinding !== undefined && sessionPreset(rememberedBinding) === agentPreset
		      && (!validateRemembered || await validateRemembered(remembered))) {
		      await beforeOpen?.(remembered, true);
		      await openPtcSessionView(scope, remembered);
		      return { sessionId: remembered, reused: true };
		    }
		    try { window.localStorage.removeItem(`${SESSION_KEY_PREFIX}${key}`); } catch { /* stale mapping is disposable */ }
		  }

		  const cwd = workspace?.cwd || workspace?.path;
		  if (typeof cwd !== 'string' || !cwd) throw new Error('Trainer 没有返回可用的原生会话 cwd');
		  // DSH's session.create contract accepts either a registered workspaceId or
		  // an absolute cwd.  The web host used by this plugin exposes the latter;
		  // workspace.create is not available in that profile and returns HTTP 404.
		  // Let the Host resolve and validate the preset.  Some DSH web profiles
		  // intentionally omit the optional agentPreset.list route while session.create
		  // still accepts the requested preset.
		  const created = requireOk((await api.sessions.create({ cwd, agentPreset })).result, '创建 DSH 会话');
		  if (typeof created?.sessionId !== 'string' || !created.sessionId) throw new Error('DSH 没有返回 sessionId');
		  // The low-level API create call does not update the client SessionRuntime's
		  // list store.  Refresh it before waiting for binding(), otherwise a valid
		  // server-created session can remain locally unaddressable until the bridge
		  // timeout expires.  DSH's high-level sessions.create() has this guarantee,
		  // but it cannot select the dedicated agentPreset, so the low-level call is
		  // required here.
		  const deadline = Date.now() + NATIVE_READINESS_TIMEOUT_MS;
		  await refreshForBinding(scope, created.sessionId, deadline, false, workspace?.path || workspace?.cwd);
		  if (typeof scope.sessions.noteAgentPreset === 'function') {
		    scope.sessions.noteAgentPreset(created.sessionId, agentPreset);
		  }
		  const binding = await waitForBinding(scope.sessions, created.sessionId, deadline);
		  await binding.session.rename(title);
		  await beforeOpen?.(created.sessionId, false);
		  await openPtcSessionView(scope, created.sessionId);
		  rememberSessionId(key, created.sessionId);
		  return { sessionId: created.sessionId, reused: false };
		}

		const trainerLaunchStates = new WeakMap();
		const trainerLaunchStatesByHost = new Map();

		function matchesTarget(binding, request) {
		  return !!binding && ['projectId', 'mode', 'targetKind', 'targetId', 'presetId']
		    .every(field => binding[field] === request[field]);
		}

		function legacySessionIds(request) {
		  const found = [];
		  try {
		    const storage = window.localStorage;
		    for (let i = 0; i < storage.length; i++) {
		      const key = storage.key(i), prefix = `${SESSION_KEY_PREFIX}${request.targetKind}:`;
		      if (!key?.startsWith(prefix)) continue;
		      try {
		        const parts = JSON.parse(key.slice(prefix.length));
		        if ([request.projectId, request.mode, request.targetId, request.presetId].every((v, index) => parts[index] === v)) {
		          found.push({ key, sessionId: storage.getItem(key) });
		        }
		      } catch { /* Ignore unrelated or malformed cache entries. */ }
		    }
		  } catch { /* Server authority works even when browser storage is unavailable. */ }
		  return found;
		}

		const resolvedIdentity = binding => binding?.resolved || { source: binding?.mode === 'engineering' ? 'release' : 'candidate',
		  revisionId: binding?.mode === 'engineering' ? null : binding?.candidateRevision ?? null, frozenVersionId: null, releaseId: null };
		function contextChange(previous, binding) {
		  return ['source', 'revisionId', 'frozenVersionId', 'releaseId'].some(k => (resolvedIdentity(previous)[k] ?? null) !== (resolvedIdentity(binding)[k] ?? null))
		    || (previous?.selectedRunId || null) !== (binding?.selectedRunId || null);
		}

		/** Only return success after the server binding and native selection agree. */
		async function openTrainerNativeSession(scope, request, { post, title, hostId = null }) {
		  if (!scope?.sessions) throw new Error('HOST_UNAVAILABLE: DSH 原生会话服务尚未注入');
		  if (!request?.projectId || !['agent', 'workflow'].includes(request.targetKind) || !request.targetId) {
		    throw new Error('TARGET_INVALID: Trainer 会话目标不完整');
		  }
		  if (request.presetId !== 'agent-trainer') throw new Error('PRESET_MISMATCH: 原生训练必须使用 agent-trainer preset');
		  if (!['training', 'published', 'engineering'].includes(request.mode)) throw new Error('MODE_INVALID: 训练模式无效');
		  const workspace = await post('session-workspace', request);
		  if (request.mode === 'training' && request.candidateRevision !== workspace.candidateRevision) {
		    throw new Error('STALE_SESSION: 候选 revision 已更新，请刷新工作台后重新打开');
		  }
		  const key = ptcSessionKey(request.targetKind, JSON.stringify([
		    request.projectId, request.mode, request.targetId, request.presetId,
		  ]));
		  let state = hostId ? trainerLaunchStatesByHost.get(hostId) : trainerLaunchStates.get(scope.sessions);
		  if (!state) {
		    state = { pending: new Map(), sessions: new Map() };
		    if (hostId) {
		      trainerLaunchStatesByHost.set(hostId, state);
		      if (trainerLaunchStatesByHost.size > 32) trainerLaunchStatesByHost.delete(trainerLaunchStatesByHost.keys().next().value);
		    } else trainerLaunchStates.set(scope.sessions, state);
		  }
		  if (state.pending.has(key)) {
		    const opened = await state.pending.get(key);
		    await openPtcSessionView(scope, opened.sessionId);
		    return { ...opened, reused: true };
		  }
		  const pending = (async () => {
		    const identity = Object.fromEntries(['projectId', 'mode', 'targetKind', 'targetId', 'presetId'].map(k => [k, request[k]]));
		    const legacy = legacySessionIds(request);
		    const clearCache = () => {
		      state.sessions.delete(key);
		      try {
		        window.localStorage.removeItem(`${SESSION_KEY_PREFIX}${key}`);
		        for (const entry of legacy) window.localStorage.removeItem(entry.key);
		      } catch { /* Disposable cache. */ }
		    };
		    let record = null, targetApiAvailable = false;
		    try { record = await post('target-session', identity); targetApiAvailable = true; } catch (error) {
		      // Older host bridges may not expose the new operation yet; legacy caches remain usable.
		      if (['target_missing', 'release_not_active', 'forbidden', 'invalid_binding'].includes(error?.code)) throw error;
		    }
		    const previousSessionId = record?.sessionId || state.sessions.get(key) || existingSessionId(key) || legacy.at(-1)?.sessionId || null;
		    if (request.freshSession) {
		      await post('forget-target-session', identity);
		      clearCache();
		    }
		    const remembered = !request.freshSession && previousSessionId;
		    // A verified server target-session is authoritative. The browser session
		    // runtime may not yet have loaded its binding or preset event after a
		    // server-side factory creates it; do not discard the durable mapping for
		    // that local cache miss. Refresh first, then bind and open the exact id.
		    const serverAuthoritative = !!record?.sessionId;
		    const rememberedLocalBinding = remembered ? scope.sessions.binding(remembered) : undefined;
		    const canTryReuse = remembered && (serverAuthoritative
		      || (rememberedLocalBinding !== undefined && sessionPreset(rememberedLocalBinding) === request.presetId));
		    if (canTryReuse) {
		      try {
		        let previousBinding = await post('bind-session', {
		          projectId: request.projectId, mode: request.mode, sessionId: remembered,
		        });
		        if (matchesTarget(previousBinding, request)) {
		          const before = previousBinding;
		          let binding;
		          for (let attempt = 0; attempt < 2; attempt++) {
		            try {
		              binding = await post('bind-session', { ...request, sessionId: remembered, baseBindingRevision: previousBinding.bindingRevision });
		              break;
		            } catch (error) {
		              if (error.code !== 'binding_conflict' || attempt) throw error;
		              previousBinding = await post('bind-session', { projectId: request.projectId, mode: request.mode, sessionId: remembered });
		              if (!matchesTarget(previousBinding, request)) throw Object.assign(new Error('TARGET_MISMATCH: 服务端绑定与请求不一致'), { code: 'target_mismatch' });
		            }
		          }
		          if (!matchesTarget(binding, request)) throw new Error('TARGET_MISMATCH: 服务端绑定与请求不一致');
		          if (!binding.effectiveTools?.includes('trainer_context')) throw new Error('TRAINER_TOOLS_MISSING: 原生会话缺少 Trainer 工具');
		          const deadline = Date.now() + NATIVE_READINESS_TIMEOUT_MS;
		          await refreshForBinding(scope, remembered, deadline, true, binding?.cwd || workspace?.path || workspace?.cwd);
		          await waitForBinding(scope.sessions, remembered, deadline, true);
		          await openPtcSessionView(scope, remembered);
		          state.sessions.set(key, remembered);
		          rememberSessionId(key, remembered);
		          return { sessionId: remembered, binding, reused: true, scopeOpened: true,
		            previousResolved: resolvedIdentity(before), resolved: resolvedIdentity(binding), previousSelectedRunId: before.selectedRunId || null,
		            contextUpdated: contextChange(before, binding) ? 'binding-only' : false };
		        }
		      } catch (error) {
		        if (!['session_unbound', 'session_identity_mismatch', 'target_mismatch'].includes(error.code)) throw error;
		      }
		    }
		    if (remembered && targetApiAvailable && (serverAuthoritative || canTryReuse)) { await post('forget-target-session', identity); clearCache(); }

		    // Browser DSH profiles may omit the public session.create and
		    // agentPreset.list endpoints.  The Trainer service owns a server-side
		    // factory in the same DSH context, so it can create and verify the real
		    // agent session without relying on those optional browser routes.
		    const created = await post('open-native-session', { ...request,
		      ...(request.freshSession && previousSessionId ? { previousSessionId } : {}) });
		    if (typeof created?.sessionId !== 'string' || !created.sessionId || !created.binding) {
		      throw new Error('NATIVE_CREATE_FAILED: DSH 没有返回已绑定的原生会话');
		    }
		    const binding = created.binding;
		    if (!matchesTarget(binding, request)) throw new Error('TARGET_MISMATCH: 服务端绑定与请求不一致');
		    if (!binding.effectiveTools?.includes('trainer_context')) throw new Error('TRAINER_TOOLS_MISSING: 原生会话缺少 Trainer 工具');
		    // The server-side factory creates the real DSH agent in the host process,
		    // but that does not automatically push the new session into the browser
		    // SessionRuntime. Refresh before waiting so the native opener can resolve
		    // and select the exact session instead of leaving the host on blank 新会话.
		    const deadline = Date.now() + NATIVE_READINESS_TIMEOUT_MS;
		    await refreshForBinding(scope, created.sessionId, deadline, created.reused === true, created.binding?.cwd || workspace?.path || workspace?.cwd);
		    if (typeof scope.sessions.noteAgentPreset === 'function') {
		      scope.sessions.noteAgentPreset(created.sessionId, request.presetId);
		    }
		    await waitForBinding(scope.sessions, created.sessionId, deadline, created.reused === true);
		    await openPtcSessionView(scope, created.sessionId);
		    state.sessions.set(key, created.sessionId);
		    rememberSessionId(key, created.sessionId);
		    return { ...created, sessionId: created.sessionId, binding, reused: created.reused === true, scopeOpened: true,
		      previousResolved: created.previousResolved || null, resolved: resolvedIdentity(binding),
		      previousSelectedRunId: created.previousSelectedRunId || null, contextUpdated: created.contextUpdated || false };
		  })();
		  state.pending.set(key, pending);
		  try { return await pending; }
		  finally { if (state.pending.get(key) === pending) state.pending.delete(key); }
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

		function stableNativeHostId() {
		  const key = '__dshAteTrainerHostId';
		  if (typeof window === 'undefined') return crypto.randomUUID();
		  if (typeof window[key] === 'string' && window[key]) return window[key];
		  try {
		    const stored = window.sessionStorage?.getItem(key);
		    if (stored) {
		      window[key] = stored;
		      return stored;
		    }
		  } catch { /* session storage may be unavailable in an embedded host */ }
		  const id = crypto.randomUUID();
		  try {
		    window[key] = id;
		    window.sessionStorage?.setItem(key, id);
		  } catch { /* a read-only host object is still valid for this mount */ }
		  return id;
		}

		async function trainerPagePost(operation, input) {
		  const response = await fetch(`/api/ptc-control/trainer/${operation}`, {
		    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
		    credentials: 'same-origin', body: JSON.stringify(input),
		  });
		  const payload = await response.json().catch(() => ({}));
		  if (!response.ok || payload.ok === false) throw Object.assign(new Error(payload.error?.message ?? payload.detail ?? `Trainer ${operation} failed`), { code: payload.error?.code });
		  return payload.value ?? payload;
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
		  position: fixed; z-index: 2147483000; top: 18px; right: 16px;
		  width: min(1480px, calc(100vw - 32px)); max-height: calc(100vh - 36px);
		  overflow: auto; overscroll-behavior: contain; color: #233044;
		  background: #fff; border: 1px solid #dfe4eb; border-radius: 12px;
		  box-shadow: 0 12px 32px #24334a18; font: 13px/1.45 "Segoe UI", "Microsoft YaHei", sans-serif;
		  overflow-wrap: anywhere;
		}
		.ptc-cp-host .ptc-cp-panel[open] {
		  inset: 12px; width: calc(100vw - 24px); max-height: calc(100vh - 24px);
		  border-radius: 12px;
		}
		.ptc-cp-host .ptc-cp-panel:not([open]) { width: max-content; max-width: calc(100vw - 32px); overflow: visible; }
		.ptc-cp-host .ptc-cp-panel > summary {
		  display: block; list-style: none; cursor: pointer; padding: 11px 15px;
		  background: #fff; color: #233044; font-weight: 700; border-radius: 12px 12px 0 0;
		}
		.ptc-cp-host .ptc-cp-panel > summary::-webkit-details-marker { display: none; }
		.ptc-cp-host .ptc-cp-panel[open] > summary {
		  position: sticky; top: 0; z-index: 1; border-radius: 12px 12px 0 0;
		  border-bottom: 1px solid #e5e9ef;
		}
		.ptc-cp-host .ptc-cp-panel > :not(summary) { margin-left: 14px; margin-right: 14px; }
		.ptc-cp-host .ptc-cp-panel > .ptc-cp-header { margin-top: 14px; font-size: 17px; font-weight: 700; }
		.ptc-cp-host .ptc-cp-bridge-actions { display:flex; align-items:center; gap:9px; margin-top:8px; margin-bottom:6px; }
		.ptc-cp-host .ptc-cp-bridge-actions button { color:#285db7; border-color:#b8cbed; background:#f7faff; }
		.ptc-cp-host .ptc-cp-bridge-actions .ptc-cp-open-white-trainer { display:inline-block; color:#285db7; border:1px solid #b8cbed; background:#f7faff; border-radius:7px; padding:7px 10px; cursor:pointer; text-decoration:none; white-space:normal; }
		.ptc-cp-host .ptc-cp-bridge-actions .ptc-cp-open-white-trainer:hover { background:#edf4ff; color:#285db7; }
		.ptc-cp-host .ptc-cp-bridge-actions span { font-size:11px; }
		.ptc-cp-host .ptc-cp-panel > .ptc-cp-view { margin-bottom: 16px; }
		.ptc-cp-host .ptc-cp-status { display: grid; gap: 5px; margin-top: 8px; margin-bottom: 12px; }
		.ptc-cp-host .ptc-cp-row { display: flex; gap: 8px; justify-content: space-between; min-width: 0; }
		.ptc-cp-host .ptc-cp-label { flex: 0 0 auto; color: #657186; }
		.ptc-cp-host .ptc-cp-value { text-align: right; min-width: 0; overflow-wrap: anywhere; color: #233044; }
		.ptc-cp-host .ptc-cp-tabs { display: flex; gap: 7px; margin-bottom: 12px; }
		.ptc-cp-host .ptc-cp-panel button, .ptc-cp-host .ptc-cp-panel select,
		.ptc-cp-host .ptc-cp-panel input, .ptc-cp-host .ptc-cp-panel textarea {
		  max-width: 100%; font: inherit;
		}
		.ptc-cp-host .ptc-cp-panel button {
		  border: 1px solid #d5dce6; background: #fff; color: #4e5d73;
		  border-radius: 7px; padding: 7px 10px; cursor: pointer;
		  white-space: normal; text-align: left;
		}
		.ptc-cp-host .ptc-cp-panel button:hover:not(:disabled) { background: #edf4ff; color: #285db7; }
		.ptc-cp-host .ptc-cp-panel button:disabled { opacity: .48; cursor: not-allowed; }
		.ptc-cp-host .ptc-cp-tab-active { background: #2d60c8 !important; border-color: #2d60c8 !important; color: #fff !important; font-weight: 600; }
		.ptc-cp-host .ptc-cp-panel select, .ptc-cp-host .ptc-cp-panel input,
		.ptc-cp-host .ptc-cp-panel textarea {
		  min-width: 0; background: #fff; color: #233044;
		  border: 1px solid #d5dce6; border-radius: 6px; padding: 6px;
		}
		.ptc-cp-host .ptc-cp-training-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-bottom: 13px; }
		.ptc-cp-host .ptc-cp-training-actions label { grid-column: 1 / -1; display: grid; gap: 3px; }
		.ptc-cp-host .ptc-cp-training-actions label select { width: 100%; }
		.ptc-cp-host .ptc-cp-smoke-controls {
		  display: grid; gap: 7px; margin: 12px 0; padding: 12px;
		  border: 1px solid #dfe5ec; border-radius: 10px; background: #f8faff;
		}
		.ptc-cp-host .ptc-cp-smoke-controls p { margin: 0 0 5px; }
		.ptc-cp-host .ptc-cp-smoke-controls button { width: 100%; }
		.ptc-cp-host .ptc-cp-run {
		  margin: 10px 0; padding: 10px; background: #fbfcfe;
		  border: 1px solid #e0e6ee; border-radius: 9px;
		}
		.ptc-cp-host .ptc-cp-run .ptc-cp-row { display: block; }
		.ptc-cp-host .ptc-cp-run .ptc-cp-label { display: block; color: #526581; font-weight: 700; }
		.ptc-cp-host .ptc-cp-run .ptc-cp-value { display: block; text-align: left; }
		.ptc-cp-host .ptc-cp-panel details:not(.ptc-cp-panel) { margin: 10px 0; padding: 7px; border: 1px solid #e1e7ef; border-radius: 7px; }
		.ptc-cp-host .ptc-cp-panel pre { white-space: pre-wrap; overflow-wrap: anywhere; }
		.ptc-cp-host .ate-trainer-direct-entry {
		  position: fixed; z-index: 2147483000; top: 18px; right: 16px;
		  display: flex; align-items: center; gap: 10px; max-width: min(520px, calc(100vw - 32px));
		  padding: 10px 12px; color: #233044; background: #fff; border: 1px solid #dfe4eb;
		  border-radius: 10px; box-shadow: 0 12px 32px #24334a18;
		  font: 13px/1.45 "Segoe UI", "Microsoft YaHei", sans-serif;
		}
		.ptc-cp-host .ate-trainer-direct-entry a {
		  display: inline-block; color: #fff; background: #2d60c8; border-radius: 7px;
		  padding: 8px 12px; font-weight: 700; text-decoration: none; white-space: nowrap;
		}
		.ptc-cp-host .ate-trainer-direct-entry a:hover { background: #234fae; }
		.ptc-cp-host .ate-trainer-direct-entry span { color: #657186; }
		.ptc-cp-host .ptc-cp-error { color: #ffb9b9; margin: 7px 0; }
		.ptc-cp-host .ptc-cp-notice { color: #187344; margin: 9px 0; }
		.ptc-cp-host .ptc-cp-workbench { min-width: 0; }
		.ptc-cp-host .ptc-cp-mode-tabs, .ptc-cp-host .ptc-cp-subtabs { display:flex; flex-wrap:wrap; gap:7px; margin:10px 0; }
		.ptc-cp-host .ptc-cp-layout { display:grid; grid-template-columns:minmax(190px,232px) minmax(0,1fr) minmax(260px,350px); gap:18px; align-items:start; }
		.ptc-cp-host .ptc-cp-roster { display:grid; align-content:start; gap:4px; max-height:62vh; overflow:auto; padding:8px 0; }
		.ptc-cp-host .ptc-cp-roster button { width:100%; text-align:left; }
		.ptc-cp-host .ptc-cp-roster-column { min-width:0; padding:4px 8px 10px 0; border-right:1px solid #e5e9ef; }
		.ptc-cp-host .ptc-cp-side-title { padding:0 12px 8px; color:#93a0b3; font-size:10px; letter-spacing:1.35px; text-transform:uppercase; font-weight:700; }
		.ptc-cp-host .ptc-cp-side-group { margin-top:20px; }
		.ptc-cp-host .ptc-cp-side-title-with-count { display:flex; justify-content:space-between; align-items:center; }
		.ptc-cp-host .ptc-cp-side-count { padding:2px 7px; border-radius:99px; background:#e8f0fc; color:#4d73b3; font-size:10px; letter-spacing:0; }
		.ptc-cp-host .ptc-cp-side-nav { display:flex; align-items:center; width:100%; min-width:0; gap:7px; }
		.ptc-cp-host .ptc-cp-side-nav .ptc-cp-side-symbol { flex:0 0 auto; color:#70819a; font-size:14px; }
		.ptc-cp-host .ptc-cp-side-nav .ptc-cp-side-label { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
		.ptc-cp-host .ptc-cp-workspace-main { min-width:0; }
		.ptc-cp-host .ptc-cp-agent-status { display:flex; align-items:center; gap:8px; padding:8px; border:1px solid #dfe5ec; border-radius:8px; margin:5px 0; background:#fff; }
		.ptc-cp-host .ptc-cp-agent-status span:first-child { flex:1; }
		.ptc-cp-host .ptc-cp-stage-status { margin:8px 0; padding:9px; background:#f7f9fc; border:1px solid #e3e8ef; border-radius:8px; }
		.ptc-cp-host .ptc-cp-stage-status ol { margin:7px 0; padding-left:22px; }
		.ptc-cp-host .ptc-cp-stage-status li { padding:3px 0; }
		.ptc-cp-host .ptc-cp-workflow-select { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:5px 10px; margin:10px 0; }
		.ptc-cp-host .ptc-cp-workflow-select label { display:flex; gap:7px; align-items:center; }
		.ptc-cp-host .ptc-cp-session-card, .ptc-cp-host .ptc-cp-publish-card { padding:12px; border:1px solid #dfe5ec; border-radius:10px; background:#fff; margin:10px 0; }
		.ptc-cp-host .ptc-cp-resource-panel { margin:9px 0; padding:10px; border:1px solid #e3e8ef; border-radius:8px; background:#f7f9fc; }
		.ptc-cp-host .ptc-cp-inspector { min-width:0; padding:4px 0 10px 16px; border-left:1px solid #e5e9ef; }
		.ptc-cp-host .ptc-cp-inspector h3 { margin:0 0 4px; font-size:15px; }
		.ptc-cp-host .ptc-cp-inspector-sub { margin:0 0 12px; color:#7b8799; font-size:12px; }
		.ptc-cp-host .ptc-cp-inspector-card { padding:12px; border:1px solid #dfe5ed; border-radius:9px; background:#fff; margin-bottom:11px; }
		.ptc-cp-host .ptc-cp-lock-note { padding:8px 9px; border-radius:7px; background:#f3f5f8; color:#718096; font-size:11px; margin-bottom:11px; }
		.ptc-cp-host .ptc-cp-inspector-list { margin:8px 0 0; padding-left:17px; color:#52627a; font-size:11px; }
		.ptc-cp-host .ptc-cp-resource-group { margin:9px 0; }
		.ptc-cp-host .ptc-cp-resource-group h4 { margin:5px 0; }
		.ptc-cp-host .ptc-cp-resource-group ul { margin:4px 0; padding-left:20px; }
		.ptc-cp-host .ptc-cp-resource-group li { display:flex; gap:8px; justify-content:space-between; padding:3px 5px; border-radius:4px; }
		.ptc-cp-host .ptc-cp-resource-used { color:#187344; background:#eaf8ef; }
		.ptc-cp-host .ptc-cp-resource-unused { color:#718096; }
		.ptc-cp-host .ptc-cp-resource-badge { flex:0 0 auto; color:#7b8799; font-size:11px; }
		.ptc-cp-host .ptc-cp-resource-used .ptc-cp-resource-badge { color:#187344; font-weight:700; }
		@media (max-width: 600px) {
		  .ptc-cp-host .ptc-cp-panel { top: 8px; right: 8px; width: calc(100vw - 16px); max-height: calc(100vh - 16px); }
		  .ptc-cp-host .ptc-cp-panel[open] { inset: 4px; width: calc(100vw - 8px); max-height: calc(100vh - 8px); }
		  .ptc-cp-host .ptc-cp-training-actions { grid-template-columns: 1fr; }
		  .ptc-cp-host .ptc-cp-workbench { min-width:0; width:calc(100vw - 32px); }
		  .ptc-cp-host .ptc-cp-layout { grid-template-columns:1fr; }
		  .ptc-cp-host .ptc-cp-roster-column, .ptc-cp-host .ptc-cp-inspector { border:0; padding:0; }
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

		function BusinessResourceList({ title, items }) {
		  return createElement('div', { className: 'ptc-cp-resource-group' },
		    createElement('h4', null, title),
		    items.length ? createElement('ul', null, ...items.map(item => createElement('li', {
		      key: item.path, className: item.used ? 'ptc-cp-resource-used' : 'ptc-cp-resource-unused' },
		      createElement('span', null, item.path), createElement('span', { className: 'ptc-cp-resource-badge' }, item.used ? '本次使用' : '已加载'))))
		      : createElement('p', null, '暂无已加载项'));
		}

		function BusinessTrainingControls({ state, store }) {
		  const [page, setPage] = useState('run');
		  const [selectedAgentId, setSelectedAgentId] = useState('ptc-dft-expert');
		  const [testItem, setTestItem] = useState('TM109');
		  const [modelChoice, setModelChoice] = useState('default');
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState('');
		  const businessRuns = (state.trainingRuns ?? []).filter(run => run.purpose === 'business-training');
		  const latestDft = latestRun(businessRuns, run => run.target?.kind === 'profile'
		    && run.target.profileId === 'ptc-dft-expert');
		  const latestInputSync = latestRun(businessRuns, run => run.target?.kind === 'pipeline'
		    && run.target.fromStage === 'INPUT_SYNC' && run.target.toStage === 'INPUT_SYNC');
		  const items = (() => { try { return parseTrainingTestItems(testItem); } catch { return null; } })();
		  const act = async work => {
		    setBusy(true); setNotice('');
		    try { const result = await work(); await store.refresh(); setNotice(`真实业务运行已受理${result?.runId ? ` · ${result.runId}` : ''}`); }
		    catch (error) { setNotice(`业务运行未启动：${error?.message ?? error}`); }
		    finally { setBusy(false); }
		  };
		  const launchDft = () => void act(async () => {
		    if (!items) throw new Error('请输入有效的 TM 编号，例如 TM109');
		    const created = await createTrainingRunRequest({ kind: 'profile', profileId: selectedAgentId }, { purpose: 'business-training' });
		    return executeBusinessTrainingRunRequest(created.runId, items, { modelChoice });
		  });
		  const launchInputSync = () => void act(async () => {
		    if (!items) throw new Error('请输入有效的 TM 编号，例如 TM109');
		    const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC',
		      workflowId: 'tm109-input-sync', workflowRevision: 'business-v1', agentBindings: {
		        'schematic-expert': { profileId: 'ptc-schematic-expert' },
		        'dft-expert': { profileId: selectedAgentId },
		      } }, { purpose: 'business-training' });
		    return executeBusinessPipelineRequest(created.runId, items, { modelChoice });
		  });
		  const controlInputSync = action => void act(() => controlBusinessPipelineRequest(latestInputSync?.runId, action));
		  const inputSyncControls = latestInputSync
		    ? pipelineControlActions(latestInputSync.status).map(action => createElement('button', { key: action, type: 'button', disabled: busy,
		      onClick: () => controlInputSync(action) }, action === 'pause' ? '暂停' : action === 'resume' ? '继续' : '停止'))
		    : [];
		  const inputSyncStatusText = latestInputSync
		    ? ['INPUT_SYNC', latestInputSync.runId, latestInputSync.status,
		      latestInputSync.outcome?.mode ?? '等待终态', latestInputSync.outcome?.stage ? `当前 ${latestInputSync.outcome.stage}` : null]
		      .filter(Boolean).join(' · ')
		    : '';
		  const businessAgents = Array.isArray(state.businessAgents) ? state.businessAgents : [];
		  const selectedAgent = businessAgents.find(agent => agent.profileId === selectedAgentId) ?? businessAgents[0] ?? null;
		  const inputSyncStatus = latestInputSync ? createElement('div', { className: 'ptc-cp-stage-status', 'data-testid': 'ptc-cp-business-input-sync-status' },
		    inputSyncStatusText,
		    ...inputSyncControls) : null;
		  const runChildren = [
		    createElement('h3', null, '真实业务 Agent · 原理图专家 → DFT 专家 INPUT_SYNC'),
		    createElement('p', null, '这里才会读取冻结到本次 Training_Materials/runs/<runId> 的业务材料：原理图先由固定 host 解析器生成七项产物，再由原理图 Agent 做只读语义审查；审查通过后才进入 DFT，由 DFT Agent 处理并做语义审查。结果只写本次训练运行目录，不发布业务版本。'),
		    createElement('label', null, 'TM 编号 ', createElement('input', { value: testItem, disabled: busy,
		      onChange: event => setTestItem(event.target.value), 'data-testid': 'ptc-cp-business-test-items' })),
		    createElement('label', null, '业务 DFT Agent ', createElement('select', { value: selectedAgentId, disabled: busy,
		      onChange: event => setSelectedAgentId(event.target.value), 'data-testid': 'ptc-cp-business-agent' },
		      ...businessAgents.filter(agent => agent.kind === 'dft').map(agent => createElement('option', { key: agent.profileId, value: agent.profileId }, `${agent.displayName} · ${agent.profileId}`)))),
		    createElement('label', null, '模型 ', createElement('select', { value: modelChoice, disabled: busy,
		      onChange: event => setModelChoice(event.target.value), 'data-testid': 'ptc-cp-business-model' },
		      createElement('option', { value: 'default' }, '默认模型'),
		      createElement('option', { value: 'deepseek-v4-flash' }, 'DeepSeek V4 Flash'))),
		    createElement('div', { className: 'ptc-cp-training-actions' },
		      createElement('button', { type: 'button', disabled: busy || !items,
		        onClick: launchDft, 'data-testid': 'ptc-cp-business-dft' }, '运行真实 DFT Agent'),
		      createElement('button', { type: 'button', disabled: busy || !items,
		        onClick: launchInputSync, 'data-testid': 'ptc-cp-business-input-sync' }, '运行真实 原理图 → DFT INPUT_SYNC')),
		    latestDft ? createElement('div', { className: 'ptc-cp-stage-status', 'data-testid': 'ptc-cp-business-dft-status' },
		      ['DFT', latestDft.runId, latestDft.status, latestDft.outcome?.mode ?? '等待终态', latestDft.outcome?.reason].filter(Boolean).join(' · ')) : null,
		    inputSyncStatus,
		    notice ? createElement('div', { className: 'ptc-cp-notice', role: 'status' }, notice) : null,
		  ];
		  const resourceTabs = createElement('div', { className: 'ptc-cp-subtabs', role: 'tablist' },
		    createElement('button', { type: 'button', className: page === 'run' ? 'ptc-cp-tab-active' : '',
		      onClick: () => setPage('run'), 'data-testid': 'ptc-cp-business-page-run' }, '运行记录'),
		    createElement('button', { type: 'button', className: page === 'io' ? 'ptc-cp-tab-active' : '',
		      onClick: () => setPage('io'), 'data-testid': 'ptc-cp-business-page-io' }, '输入 / 输出'),
		    createElement('button', { type: 'button', className: page === 'resources' ? 'ptc-cp-tab-active' : '',
		      onClick: () => setPage('resources'), 'data-testid': 'ptc-cp-business-page-resources' }, 'Skill / 脚本'));
		  const agentPicker = selectedAgent ? createElement('label', { className: 'ptc-cp-business-agent-picker' }, '查看 Agent ',
		    createElement('select', { value: selectedAgent.profileId, onChange: event => setSelectedAgentId(event.target.value) },
		      ...businessAgents.map(agent => createElement('option', { key: agent.profileId, value: agent.profileId }, `${agent.displayName} · ${agent.profileId}`)))) : null;
		  const resourcePanel = page === 'io' && selectedAgent
		    ? createElement('div', { className: 'ptc-cp-resource-panel', 'data-testid': 'ptc-cp-business-io' },
		      agentPicker, createElement('p', null, `最新业务运行：${selectedAgent.latestRunId ?? '尚未运行'} · ${selectedAgent.latestRunStatus ?? '无状态'}`),
		      createElement(BusinessResourceList, { title: '输入材料', items: selectedAgent.inputs }),
		      createElement(BusinessResourceList, { title: '输出材料', items: selectedAgent.outputs }))
		    : page === 'resources' && selectedAgent
		      ? createElement('div', { className: 'ptc-cp-resource-panel', 'data-testid': 'ptc-cp-business-resources' },
		        agentPicker, createElement('p', null, '绿色“本次使用”表示最新业务运行已留下对应证据；其余条目是该 Agent 的完整加载清单。'),
		        createElement(BusinessResourceList, { title: 'Skills / 规则', items: selectedAgent.skills }),
		        createElement(BusinessResourceList, { title: '脚本', items: selectedAgent.scripts }))
		      : page !== 'run' ? createElement('div', { className: 'ptc-cp-resource-panel' }, '尚未加载业务 Agent 清单；先启动一次 BUSINESS_ONLY 训练。') : null;
		  const children = [
		    createElement('h3', null, '真实业务 Agent · 原理图专家 → DFT 专家 INPUT_SYNC'),
		    resourceTabs,
		    resourcePanel,
		    ...(page === 'run' ? runChildren : []),
		  ];
		  return createElement('section', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-business-training' }, ...children);
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
		    content = createElement('div', { className: 'ptc-cp-workbench' },
		      createElement('div', { className: 'ptc-cp-layout' },
		      createElement('aside', { className: 'ptc-cp-roster-column', 'data-testid': 'ptc-cp-agent-sidebar' },
		        createElement('div', { className: 'ptc-cp-side-group' },
		          createElement('div', { className: 'ptc-cp-side-title ptc-cp-side-title-with-count' },
		            createElement('span', null, 'AGENTS'),
		            createElement('span', { className: 'ptc-cp-side-count' }, String(ARITHMETIC_PROFILES.length))),
		          agentList),
		        createElement('div', { className: 'ptc-cp-side-group' },
		          createElement('div', { className: 'ptc-cp-side-title ptc-cp-side-title-with-count' },
		            createElement('span', null, '工作流'),
		            createElement('span', { className: 'ptc-cp-side-count' }, '1')),
		          createElement('button', { type: 'button', className: `ptc-cp-side-nav ${trainingMode === 'workflow' ? 'ptc-cp-tab-active' : ''}`,
		            onClick: () => setTrainingMode('workflow'), 'data-testid': 'ptc-cp-workflow-sidebar' },
		            createElement('span', { className: 'ptc-cp-side-symbol' }, '⌘'),
		            createElement('span', { className: 'ptc-cp-side-label' }, templateName || 'ATE PTC 工作流')))),
		      createElement('main', { className: 'ptc-cp-workspace-main' },
		        createElement(BusinessTrainingControls, { state, store }),
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
		      createElement('aside', { className: 'ptc-cp-inspector', 'data-testid': 'ptc-cp-agent-inspector' },
		        createElement('h3', null, PROFILE_LABELS[selectedProfile] ?? selectedProfile),
		        createElement('p', { className: 'ptc-cp-inspector-sub' }, 'Agent 配置与执行状态'),
		        createElement('div', { className: 'ptc-cp-lock-note' }, '训练模式可编辑草稿；发布与工程模式使用冻结版本。'),
		        createElement('div', { className: 'ptc-cp-inspector-card' },
		          createElement(StatusRow, { label: 'Agent ID', value: selectedProfile }),
		          createElement(StatusRow, { label: '工作流候选', value: `${workflowProfiles.length} 个` }),
		          createElement(StatusRow, { label: '最新运行', value: selectedProfileRun?.status ?? '未运行' }),
		          createElement('ul', { className: 'ptc-cp-inspector-list' },
		            createElement('li', null, '输入：1+2 等于几'),
		            createElement('li', null, '输出：JSON answer=3'),
		            createElement('li', null, '范围：SMOKE_ONLY'))),
		        selectedProfileRun ? createElement('div', { className: 'ptc-cp-inspector-card' },
		          createElement('strong', null, '最近验收'),
		          createElement('p', null, `${selectedProfileRun.runId} · ${selectedProfileRun.outcome?.smokePassed === true ? '通过' : selectedProfileRun.status}`)) : null),
		        notice ? createElement('div', { className: 'ptc-cp-notice', role: 'status' }, notice) : null));
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
		  const [nativeHostId] = useState(stableNativeHostId);

		  useEffect(() => {
		    store.start();
		    return () => store.stop();
		  }, [store]);

		  useEffect(() => {
		    const trainerWorkbenchOrigins = new Set([
		      window.location.origin,
		      'http://127.0.0.1:8123',
		      'http://localhost:8123',
		    ]);
		    const trainerStorageRequestPrefix = 'dsh-agent-trainer-bridge:request:';
		    const trainerStorageResponsePrefix = 'dsh-agent-trainer-bridge:response:';
		    const requests = new Map();
		    const onWorkbenchMessage = async event => {
		      const data = event?.data;
		      // The formal white prototype is sometimes served by the local static
		      // preview on :8123. Keep the same-origin check for normal DSH tabs, but
		      // explicitly allow that trusted local origin for a window.opener bridge.
		      if (!trainerWorkbenchOrigins.has(event.origin) || data?.type !== 'dsh-agent-trainer-open-session') return;
		      if (data.hostId && data.hostId !== nativeHostId) return;
		      const reply = payload => event.source?.postMessage({ type: 'dsh-agent-trainer-session-result', bridgeId: data.bridgeId, nonce: data.nonce, hostId: nativeHostId, ...payload }, event.origin);
		      try {
		        if (!sessionServices) throw new Error('HOST_UNAVAILABLE: DSH 原生会话服务尚未注入，请从 DSH ATE Trainer 按钮打开白色工作台。');
		        const request = data.request;
		        if (!request || !['agent', 'workflow'].includes(request.targetKind) || typeof request.targetId !== 'string') throw new Error('TARGET_INVALID: Trainer 会话目标不完整');
		        if (request.presetId && request.presetId !== 'agent-trainer') throw new Error('PRESET_MISMATCH: 原生训练必须使用 agent-trainer preset');
		        if (!data.bridgeId || !data.nonce) throw new Error('BRIDGE_INVALID: 缺少 bridgeId 或 nonce');
		        const title = data.title || `Agent Trainer · ${request.targetId}`;
		        const fingerprint = JSON.stringify(request);
		        let job = requests.get(data.nonce);
		        if (job && job.fingerprint !== fingerprint) throw new Error('BRIDGE_CONFLICT: 同一 nonce 的目标不能改变');
		        if (!job) {
		          job = { fingerprint, promise: openTrainerNativeSession(sessionServices, request, { post: trainerPagePost, title, hostId: nativeHostId }) };
		          requests.set(data.nonce, job);
		          if (requests.size > 200) requests.delete(requests.keys().next().value);
		        }
		        const opened = await job.promise;
		        const binding = opened.binding;
		        reply({ ok: true, sessionId: opened.sessionId, binding, title, reused: opened.reused, openedAt: new Date().toISOString(), targetKind: binding.targetKind, targetId: binding.targetId, candidateRevision: binding.candidateRevision, presetId: binding.presetId, scopeOpened: opened.scopeOpened, contextUpdated: opened.contextUpdated, previousResolved: opened.previousResolved, resolved: opened.resolved, previousSelectedRunId: opened.previousSelectedRunId });
		      } catch (error) {
		        reply({ ok: false, code: error.code || String(error.message).split(':')[0], error: error?.message ?? String(error) });
		      }
		    };
		    window.addEventListener('message', onWorkbenchMessage);
		    const channel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('dsh-agent-trainer-bridge') : null;
		    const onChannelMessage = event => event.data?.hostId === nativeHostId && onWorkbenchMessage({ origin: window.location.origin, data: event.data,
		      source: { postMessage: payload => channel?.postMessage(payload) } });
		    channel?.addEventListener('message', onChannelMessage);
		    const onStorageMessage = event => {
		      if (!event.key?.startsWith(trainerStorageRequestPrefix) || !event.newValue) return;
		      let data;
		      try { data = JSON.parse(event.newValue); } catch { return; }
		      if (!data?.bridgeId || data.type !== 'dsh-agent-trainer-open-session' || data.hostId !== nativeHostId) return;
		      const responseKey = `${trainerStorageResponsePrefix}${data.bridgeId}`;
		      const source = { postMessage: payload => {
		        try { window.localStorage.setItem(responseKey, JSON.stringify(payload)); } catch { /* storage is best effort */ }
		      } };
		      void onWorkbenchMessage({ origin: window.location.origin, data, source });
		    };
		    window.addEventListener('storage', onStorageMessage);
		    return () => {
		      window.removeEventListener('message', onWorkbenchMessage);
		      window.removeEventListener('storage', onStorageMessage);
		      channel?.removeEventListener('message', onChannelMessage);
		      channel?.close();
		    };
		  }, [sessionServices, nativeHostId]);

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
		      "div",
		      { className: "ate-trainer-direct-entry", "data-testid": "ate-trainer-direct-entry" },
		      createElement("a", { href: `/agent-trainer?nativeHost=${nativeHostId}`, target: "_blank", rel: "opener", "data-testid": "ate-trainer-open" }, "打开 ATE Trainer"),
		      createElement("span", null, "直接进入 Trainer；原生会话仍由 DSH 宿主承载。")
		    ),
		    error
		      ? createElement(
		          "div",
		          { className: "ptc-cp-error", "data-testid": "ptc-cp-error", key: "error" },
		          `${t("status.error")}: ${error}`
		        )
		      : null
		  );
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
		 * The native client slot mounts the ATE Trainer direct entry. The entry keeps
		 * the DSH host available so the Trainer can open real native sessions without
		 * exposing a second PTC panel click.
		 */

		/** Locale namespace for this plugin. */
		const PTC_CONTROL_PLANE_LOCALE_NAMESPACE = "ptc-control-plane";

		/** Locale dictionaries (zh / en), mirroring the agent-teams pattern. */
		const localeDictionaries = {
		  zh: {
		    "panel.title": "ATE Trainer",
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
		    "panel.title": "ATE Trainer",
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
		const PANEL_SLOT_ID = "ate-trainer-direct-entry";

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

		  const mount = (sessionServices = null) => {
		    const Panel = ({ t }) => createElement(PtcControlPanel, { store, t, sessionServices });
		    ctx.slots.inject(SHELL_SLOT_NAME, () => ctx.slots.register(
		      { name: SHELL_SLOT_NAME, id: PANEL_SLOT_ID, order: 90,
		        label: "ATE Trainer", locale: PTC_CONTROL_PLANE_LOCALE_NAMESPACE }, Panel));
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
