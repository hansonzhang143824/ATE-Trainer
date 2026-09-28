import path from 'node:path';
import fs from 'node:fs';
import { randomUUID } from 'node:crypto';
import { buildControlState } from './control-state.js';
import { createTrainingRun } from './training-run.js';
import { executeTrainingRun, reconcileInterruptedTrainingRuns } from './training-execution.js';
import { createTrainingDispatcher } from './training-dispatch.js';
import { createProfileSmokeManager } from './profile-training.js';
import { createArithmeticRoleDispatcher } from './arithmetic-role-dispatch.js';
import { createSimpleOrchestrationManager } from './simple-orchestration-manager.js';
import { stageTrainingRelease, activateStagedTrainingRelease, executePublishedSmoke,
  createPublishedSmokeDispatcher, verifySmokeCandidate } from './training-release.js';
import { trainingGuardDecision } from './training-guard.js';
import { trainingAddressBook } from './training-paths.js';
import { readTrainingDraft, saveTrainingDraft } from './training-drafts.js';
import { resolvePtcSessionWorkspace } from './session-workspaces.js';
import { readWorkflowTemplate, saveWorkflowTemplate, freezeWorkflowTemplate } from './workflow-template.js';
import { createWorkflowTemplateRunner, reconcileInterruptedWorkflowTemplateRuns } from './workflow-template-run.js';
import { stageWorkflowTemplateRelease, activateWorkflowTemplateRelease,
  loadWorkflowTemplateRelease } from './workflow-template-release.js';
import { createPublishedWorkflowRunner, reconcileInterruptedPublishedWorkflowRuns } from './workflow-template-published.js';
import { createTrainingIssue, listTrainingIssues } from './training-issues.js';
import { createTrainingCaseProposal, listTrainingCaseProposals } from './training-case-proposals.js';
import { createPipelineDispatcher } from './pipeline-dispatch.js';
import { createPipelineExecutionManager, reconcileInterruptedPipelineRuns } from './pipeline-execution.js';
import { pipelineGuardDecision, reconcileStageReceipts } from './pipeline-guard.js';
import { createFrameworkRehearsalManager } from './framework-rehearsal-manager.js';
import { createFrameworkRehearsalAdapters, openFrameworkRehearsalSnapshot, verifyFrameworkChain } from './framework-rehearsal.js';
import { stageFrameworkRelease, activateStagedFrameworkRelease, loadFrameworkRelease, verifyFrameworkRuntimeCompatibility } from './framework-release.js';
import { createFrameworkPublishedRun } from './framework-published-run.js';
import { mountTrainerHost } from './trainer-host.js';

export const name = 'dsh-ptc-control-plane';
export const inject = ['webServer', 'agents', 'agentDefaultModel', 'agentPresets', 'subagents', 'tools'];

function json(response, status, body) {
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  response.end(JSON.stringify(body));
}

export function createStateHandler(workspaceRoot) {
  return async (request, response) => {
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      json(response, 405, { error: 'method_not_allowed' });
      return;
    }
    try {
      const body = buildControlState(workspaceRoot);
      if (request.method === 'HEAD') {
        response.writeHead(200, {
          'Content-Type': 'application/json; charset=utf-8',
          'Cache-Control': 'no-store',
        });
        response.end();
        return;
      }
      json(response, 200, body);
    } catch (error) {
      json(response, 500, { error: 'state_unavailable', detail: String(error?.message ?? error) });
    }
  };
}

async function readJsonBody(request, limit = 16 * 1024) {
  const contentType = String(request.headers?.['content-type'] ?? '').split(';', 1)[0].trim().toLowerCase();
  if (contentType !== 'application/json') {
    const error = new Error('content_type_must_be_application_json');
    error.statusCode = 415;
    throw error;
  }
  let size = 0;
  const chunks = [];
  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buffer.length;
    if (size > limit) {
      const error = new Error('request_body_too_large');
      error.statusCode = 413;
      throw error;
    }
    chunks.push(buffer);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    const error = new Error('invalid_json');
    error.statusCode = 400;
    throw error;
  }
}

export function createTrainingRunHandler(workspaceRoot) {
  return async (request, response) => {
    if (request.method !== 'POST') {
      json(response, 405, { error: 'method_not_allowed' });
      return;
    }
    try {
      const input = await readJsonBody(request);
      const result = createTrainingRun(workspaceRoot, input);
      json(response, 201, {
        runId: result.context.runId,
        mode: result.context.mode,
        status: result.state.status,
        target: result.state.target,
        purpose: result.state.purpose,
        artifactRoot: result.context.artifactRoot,
      });
    } catch (error) {
      const status = Number.isInteger(error?.statusCode) ? error.statusCode : 400;
      json(response, status, { error: 'training_run_rejected', detail: String(error?.message ?? error) });
    }
  };
}

export function createTrainingExecutionHandler(workspaceRoot, options = {}) {
  return async (request, response) => {
    if (request.method !== 'POST') {
      json(response, 405, { error: 'method_not_allowed' });
      return;
    }
    try {
      const input = await readJsonBody(request);
      const result = await (options.executeTrainingRun ?? executeTrainingRun)(workspaceRoot, input);
      json(response, 200, {
        runId: result.context.runId,
        status: result.state.status,
        outcome: result.state.outcome,
      });
    } catch (error) {
      const status = Number.isInteger(error?.statusCode) ? error.statusCode : 400;
      json(response, status, { error: 'training_execution_rejected', detail: String(error?.message ?? error) });
    }
  };
}

export function createTrainingStopHandler(dispatcher) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      trainingAddressBook(input.runId);
      if (!dispatcher.stop(input.runId, 'user stopped training from native control panel')) {
        return json(response, 409, { error: 'training_not_active', detail: 'This run has no active cancellable dispatcher.' });
      }
      json(response, 202, { runId: input.runId, cancellationRequested: true, terminationConfirmed: false });
    } catch (error) {
      json(response, error.statusCode ?? 400, { error: 'training_stop_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createProfileSmokeHandler(manager, action) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('smoke request must be an object');
      if (action === 'execute') {
        if (Object.keys(input).some(key => !['runId', 'modelChoice'].includes(key))) {
          throw new Error('smoke execute contains unsupported fields');
        }
        const started = manager.start(input);
        return json(response, 202, { runId: started.runId, status: started.status, mode: started.mode });
      }
      if (action === 'stop') {
        if (Object.keys(input).sort().join('|') !== 'runId') throw new Error('smoke stop requires only runId');
        if (!manager.stop(input.runId, 'stopped from native training panel')) {
          return json(response, 409, { error: 'smoke_not_active', detail: 'No active profile smoke run.' });
        }
        return json(response, 202, { runId: input.runId, status: 'stop_requested' });
      }
      throw new Error('unknown profile smoke action');
    } catch (error) {
      return json(response, error.statusCode ?? 400, {
        error: 'profile_smoke_rejected', detail: String(error.message ?? error),
      });
    }
  };
}

export function createSimpleOrchestrationHandler(manager, action) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('smoke request must be an object');
      if (action === 'execute') {
        if (Object.keys(input).some(key => !['runId', 'testItems', 'profileRunIds', 'pilot'].includes(key))
            || (input.pilot !== undefined && input.pilot !== true)) {
          throw new Error('unexpected smoke orchestration input');
        }
        const started = manager.start(input);
        return json(response, 202, { runId: started.runId, status: started.status, mode: started.mode });
      }
      if (action === 'control') {
        if (Object.keys(input).sort().join('|') !== 'action|runId') throw new Error('control requires runId and action');
        const state = manager.control(input.runId, input.action);
        return json(response, 202, { runId: input.runId, status: state.status, mode: 'SMOKE_ONLY' });
      }
      throw new Error('unknown smoke orchestration action');
    } catch (error) {
      return json(response, error.statusCode ?? 400, { error: 'simple_orchestration_rejected', detail: String(error.message ?? error) });
    }
  };
}

function archivedLegacyExecution(request, response) {
  return json(response, 410, { error: 'legacy_execution_archived',
    detail: 'DFT/schematic business execution is archived. Use eight-expert SMOKE_ONLY training.' });
}

const SMOKE_RUNTIME_PATHS = Object.freeze([
  'plugins/dsh-ptc-control-plane/lib/profile-training.js',
  'plugins/dsh-ptc-control-plane/lib/arithmetic-role-dispatch.js',
  'plugins/dsh-ptc-control-plane/lib/simple-orchestration.js',
  'plugins/dsh-ptc-control-plane/lib/simple-orchestration-manager.js',
  'plugins/dsh-ptc-control-plane/lib/training-release.js',
]);

export function createTrainingSmokePublishHandler(workspaceRoot) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)
          || Object.keys(input).sort().join('|') !== 'pipelineRunId|profileRunIds') {
        throw new Error('publish requires pipelineRunId and six profileRunIds');
      }
      trainingAddressBook(input.pipelineRunId);
      const progress = JSON.parse(fs.readFileSync(path.join(workspaceRoot, 'Training_Materials', 'runs',
        input.pipelineRunId, 'simple-orchestration.json'), 'utf8'));
      if (progress.runId !== input.pipelineRunId || progress.status !== 'completed'
          || progress.smokePassed !== true || progress.businessGatePassed !== false) {
        throw new Error('whole-chain arithmetic smoke is not complete');
      }
      const releaseId = `smoke-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${randomUUID().slice(0, 8)}`;
      const staged = await stageTrainingRelease({ workspaceRoot, releaseId, createdBy: 'DSH native training panel',
        profileRunIds: input.profileRunIds, pipelineRunId: input.pipelineRunId,
        scriptPaths: [...SMOKE_RUNTIME_PATHS], verifySmoke: verifySmokeCandidate });
      const active = activateStagedTrainingRelease({ workspaceRoot, stagingId: staged.stagingId });
      return json(response, 201, { releaseId, status: 'active', mode: 'SMOKE_ONLY',
        businessGatePassed: false, bundleDigest: staged.manifest.bundleDigest, activatedAt: active.activatedAt });
    } catch (error) {
      return json(response, error.statusCode ?? 400, { error: 'smoke_publish_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createTrainingSmokeFreezeHandler(workspaceRoot) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)
          || Object.keys(input).sort().join('|') !== 'pipelineRunId|profileRunIds') {
        throw new Error('freeze requires pipelineRunId and eight profileRunIds');
      }
      trainingAddressBook(input.pipelineRunId);
      const progress = JSON.parse(fs.readFileSync(path.join(workspaceRoot, 'Training_Materials', 'runs',
        input.pipelineRunId, 'simple-orchestration.json'), 'utf8'));
      if (progress.runId !== input.pipelineRunId || progress.status !== 'completed'
          || progress.smokePassed !== true || progress.businessGatePassed !== false) {
        throw new Error('whole-chain arithmetic smoke is not complete');
      }
      const releaseId = `smoke-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${randomUUID().slice(0, 8)}`;
      const staged = await stageTrainingRelease({ workspaceRoot, releaseId, createdBy: 'DSH native training panel',
        profileRunIds: input.profileRunIds, pipelineRunId: input.pipelineRunId,
        scriptPaths: [...SMOKE_RUNTIME_PATHS], verifySmoke: verifySmokeCandidate });
      return json(response, 201, { releaseId, stagingId: staged.stagingId, status: 'frozen-unpublished',
        mode: 'SMOKE_ONLY', businessGatePassed: false, bundleDigest: staged.manifest.bundleDigest,
        frozenAt: staged.manifest.createdAt });
    } catch (error) {
      return json(response, error.statusCode ?? 400, { error: 'smoke_freeze_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createTrainingSmokeActivateHandler(workspaceRoot) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)
          || Object.keys(input).sort().join('|') !== 'stagingId'
          || typeof input.stagingId !== 'string' || !/^stage-[a-f0-9-]{36}$/.test(input.stagingId)) {
        throw new Error('activate requires one verified stagingId');
      }
      const pointer = activateStagedTrainingRelease({ workspaceRoot, stagingId: input.stagingId });
      return json(response, 200, { releaseId: pointer.releaseId, status: 'active', mode: 'SMOKE_ONLY',
        businessGatePassed: false, bundleDigest: pointer.bundleDigest, activatedAt: pointer.activatedAt });
    } catch (error) {
      return json(response, error.statusCode ?? 400, { error: 'smoke_activation_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createPublishedSmokeHandler(workspaceRoot, dispatcher, controllers, action, logger) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('published smoke request must be an object');
      if (action === 'execute') {
        if (Object.keys(input).sort().join('|') !== 'testItems') throw new Error('published execute only accepts testItems');
        const runId = `published-smoke-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${randomUUID().slice(0, 8)}`;
        const controller = new AbortController();
        controllers.set(runId, controller);
        const completion = executePublishedSmoke({ workspaceRoot, runId,
          testItems: input.testItems, ...dispatcher, signal: controller.signal });
        void completion.catch(error => logger?.error?.(`PTC published smoke failed: ${error.message}`))
          .finally(() => controllers.delete(runId));
        return json(response, 202, { runId, status: 'running', mode: 'SMOKE_ONLY' });
      }
      if (action === 'control') {
        if (Object.keys(input).sort().join('|') !== 'action|runId' || input.action !== 'stop') {
          throw new Error('published smoke control only supports stop');
        }
        const controller = controllers.get(input.runId);
        if (!controller) return json(response, 409, { error: 'published_smoke_not_active' });
        controller.abort(new Error('stopped from native published panel'));
        return json(response, 202, { runId: input.runId, status: 'stop_requested' });
      }
      throw new Error('unknown published smoke action');
    } catch (error) {
      return json(response, error.statusCode ?? 400, { error: 'published_smoke_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createTrainingDraftHandler(workspaceRoot, action) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request, 2 * 1024 * 1024);
      const result = action === 'read' ? readTrainingDraft(workspaceRoot, input)
        : action === 'save' ? saveTrainingDraft(workspaceRoot, input) : (() => { throw new Error('unknown draft action'); })();
      json(response, 200, result);
    } catch (error) {
      const status = ['DRAFT_CONFLICT', 'DRAFT_BUSY'].includes(error.code) ? 409 : error.statusCode ?? 400;
      json(response, status, { error: error.code ?? 'draft_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createPtcSessionWorkspaceHandler(workspaceRoot) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      const workspace = resolvePtcSessionWorkspace(workspaceRoot, input);
      json(response, 200, workspace);
    } catch (error) {
      json(response, error.statusCode ?? 400, { error: 'session_workspace_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createWorkflowTemplateHandler(workspaceRoot, runner, action) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request, 256 * 1024);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('workflow request must be an object');
      const keys = Object.keys(input).sort().join('|');
      const expected = { read: 'templateId', save: 'expectedSha256|template',
        freeze: 'sha256|templateId', execute: 'templateId|versionSha256',
        control: 'action|runId' }[action];
      if (keys !== expected) throw new Error('workflow request has unsupported or missing fields');
      let result;
      if (action === 'read') result = readWorkflowTemplate(workspaceRoot, input.templateId);
      else if (action === 'save') result = saveWorkflowTemplate(workspaceRoot, input);
      else if (action === 'freeze') result = freezeWorkflowTemplate(workspaceRoot, input);
      else if (action === 'execute') {
        const started = runner.start(input);
        result = { runId: started.runId, status: started.status, mode: started.mode };
      } else if (action === 'control') result = runner.control(input.runId, input.action);
      else throw new Error('unknown workflow template action');
      json(response, action === 'execute' || action === 'control' ? 202 : 200, result);
    } catch (error) {
      json(response, error.code === 'WORKFLOW_TEMPLATE_CONFLICT' ? 409 : error.statusCode ?? 400,
        { error: error.code ?? 'workflow_template_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createWorkflowTemplateReleaseHandler(workspaceRoot, publishedRunner, action) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('release request must be an object');
      const keys = Object.keys(input).sort().join('|');
      const expected = { stage: 'runId', activate: 'manifestSha256|releaseId',
        execute: '', control: 'action|runId' }[action];
      if (action === 'read' ? !['', 'releaseId'].includes(keys) : keys !== expected) {
        throw new Error('workflow release request has unsupported or missing fields');
      }
      let result;
      if (action === 'stage') result = stageWorkflowTemplateRelease(workspaceRoot, input.runId);
      else if (action === 'activate') result = activateWorkflowTemplateRelease(workspaceRoot,
        input.releaseId, input.manifestSha256);
      else if (action === 'read') result = loadWorkflowTemplateRelease(workspaceRoot, input.releaseId ?? null);
      else if (action === 'execute') {
        const started = publishedRunner.start();
        result = { runId: started.runId, status: started.status, mode: started.mode };
      } else if (action === 'control') result = publishedRunner.control(input.runId, input.action);
      else throw new Error('unknown workflow release action');
      json(response, ['execute', 'control'].includes(action) ? 202 : 200, result);
    } catch (error) {
      json(response, error.statusCode ?? 400,
        { error: 'workflow_release_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createTrainingIssueHandler(workspaceRoot, action) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('issue request must be an object');
      if (action === 'create') {
        const allowed = new Set(['runId', 'profileId', 'sourceRole', 'title', 'description', 'evidencePaths']);
        if (Object.keys(input).some(key => !allowed.has(key))) throw new Error('issue request contains unsupported fields');
        const result = createTrainingIssue(workspaceRoot, input);
        return json(response, 201, result);
      }
      if (action === 'list') {
        const allowed = new Set(['runId', 'profileId']);
        if (Object.keys(input).some(key => !allowed.has(key))) throw new Error('issue list contains unsupported filters');
        return json(response, 200, { issues: listTrainingIssues(workspaceRoot, input) });
      }
      throw new Error('unknown training issue action');
    } catch (error) {
      json(response, error.statusCode ?? 400, { error: 'training_issue_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createTrainingCaseHandler(workspaceRoot, action) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('case request must be an object');
      if (action === 'create') {
        const allowed = new Set(['issueId', 'expectedBehavior', 'reproductionSteps']);
        if (Object.keys(input).some(key => !allowed.has(key))) throw new Error('case request contains unsupported fields');
        return json(response, 201, createTrainingCaseProposal(workspaceRoot, input));
      }
      if (action === 'list') {
        const allowed = new Set(['issueId', 'runId', 'profileId']);
        if (Object.keys(input).some(key => !allowed.has(key))) throw new Error('case list contains unsupported filters');
        return json(response, 200, { proposals: listTrainingCaseProposals(workspaceRoot, input) });
      }
      throw new Error('unknown training case action');
    } catch (error) {
      json(response, error.statusCode ?? 400, { error: 'training_case_rejected', detail: String(error.message ?? error) });
    }
  };
}

export function createPipelineHandler(manager, action, options = {}) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('pipeline request must be an object');
      const allowed = action === 'execute' ? ['runId', 'testItems', ...(options.allowModelChoice ? ['modelChoice'] : [])] : ['runId', 'action'];
      if (Object.keys(input).some(key => !allowed.includes(key))) throw new Error('pipeline request contains unsupported fields');
      const result = action === 'execute' ? manager.start(input) : manager.control(input.runId, input.action);
      json(response, 202, { runId: result.runId, status: result.status, outcome: result.outcome,
        ...(action === 'control' ? { terminationConfirmed: result.terminationConfirmed === true } : {}) });
    } catch (error) {
      json(response, error.statusCode ?? 400, { error: 'pipeline_request_rejected', detail: error.message });
    }
  };
}

export function createFrameworkReleasePublishHandler(workspaceRoot) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)
          || Object.keys(input).sort().join('|') !== 'sourceRunId') throw new Error('sourceRunId is the only supported publish field');
      trainingAddressBook(input.sourceRunId);
      const releaseId = `framework-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${randomUUID().slice(0, 8)}`;
      const staged = await stageFrameworkRelease({ workspaceRoot, releaseId, sourceRunId: input.sourceRunId,
        createdBy: 'native-ptc-control-panel',
        verifyRehearsal: async ({ workspaceRoot: root, runId }) => {
          const snapshot = openFrameworkRehearsalSnapshot(root, runId);
          const verdict = await verifyFrameworkChain({ workspaceRoot: root, runId,
            testItems: snapshot.testItems, snapshot });
          return { kind: 'framework-rehearsal', status: verdict.status, runId };
        } });
      const pointer = activateStagedFrameworkRelease({ workspaceRoot, stagingId: staged.stagingId });
      json(response, 201, { kind: 'framework-rehearsal', realBusinessGatesPassed: false,
        releaseId, sourceRunId: input.sourceRunId, bundleDigest: pointer.bundleDigest, activatedAt: pointer.activatedAt });
    } catch (error) {
      json(response, error.statusCode ?? 409, { error: 'framework_release_rejected', detail: error.message });
    }
  };
}

export function createFrameworkRecoveryHandler(manager) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)
          || Object.keys(input).sort().join('|') !== 'runId') throw new Error('runId is the only supported recovery field');
      const result = manager.recover(input.runId);
      json(response, 202, { runId: result.runId, status: result.status, outcome: result.outcome,
        recoveryKind: 'explicit-receipt-verified' });
    } catch (error) {
      json(response, error.statusCode ?? 409, { error: 'framework_recovery_rejected', detail: error.message });
    }
  };
}

export function createFrameworkPublishedExecuteHandler(workspaceRoot, controllers, logger) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input) || Object.keys(input).length !== 0) {
        throw new Error('published framework run accepts no release, TM, stage or executor override');
      }
      const release = loadFrameworkRelease({ workspaceRoot });
      verifyFrameworkRuntimeCompatibility({ workspaceRoot, releaseId: release.manifest.releaseId });
      const runId = `framework-run-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${randomUUID().slice(0, 8)}`;
      const controller = createFrameworkPublishedRun({ workspaceRoot, runId });
      controllers.set(runId, controller);
      void controller.start().catch(error => logger?.error?.(`PTC published framework replay ${runId}: ${error.message}`));
      json(response, 202, { runId, releaseId: release.manifest.releaseId, status: 'accepted',
        purpose: 'framework-published-replay', realBusinessGatesPassed: false });
    } catch (error) {
      json(response, error.statusCode ?? 409, { error: 'framework_published_run_rejected', detail: error.message });
    }
  };
}

export function createFrameworkPublishedControlHandler(controllers) {
  return async (request, response) => {
    if (request.method !== 'POST') return json(response, 405, { error: 'method_not_allowed' });
    try {
      const input = await readJsonBody(request);
      if (!input || typeof input !== 'object' || Array.isArray(input)
          || Object.keys(input).sort().join('|') !== 'action|runId'
          || !['pause', 'resume', 'stop'].includes(input.action)) throw new Error('unsupported published replay control');
      trainingAddressBook(input.runId);
      const controller = controllers.get(input.runId);
      if (!controller) throw new Error('published replay has no live controller; restart cannot blindly resume');
      let state;
      if (input.action === 'pause') state = controller.pause();
      else if (input.action === 'stop') state = controller.stop('stopped from native control panel');
      else {
        const completion = controller.resume();
        void Promise.resolve(completion).catch(() => {});
        state = controller.getState();
      }
      json(response, 202, { runId: input.runId, status: state.status, action: input.action,
        terminationConfirmed: input.action === 'stop' && state.status === 'cancelled' });
    } catch (error) {
      json(response, error.statusCode ?? 409, { error: 'framework_published_control_rejected', detail: error.message });
    }
  };
}

export function apply(ctx, config = {}) {
  if (typeof config.workspaceRoot !== 'string' || config.workspaceRoot.trim() === '') {
    throw new Error('dsh-ptc-control-plane: workspaceRoot is required');
  }
  const workspaceRoot = path.resolve(config.workspaceRoot);
  ctx.inject(config.trainerEnabled === true ? [...inject, 'sessions', 'sessionPersistence'] : inject, (webCtx) => {
    webCtx.effect(() => {
      if (typeof webCtx?.tools?.guard !== 'function' || typeof webCtx?.on !== 'function') {
        throw new Error('dsh-ptc-control-plane: tools.guard and tools/pre-execute are required');
      }
      const reconciled = reconcileInterruptedTrainingRuns(workspaceRoot);
      const reconciledTemplateRuns = reconcileInterruptedWorkflowTemplateRuns(workspaceRoot);
      const reconciledPublishedTemplates = reconcileInterruptedPublishedWorkflowRuns(workspaceRoot);
      const reconciledPipelines = reconcileInterruptedPipelineRuns(workspaceRoot);
      reconcileStageReceipts(workspaceRoot);
      if (reconciled.length > 0) webCtx.logger?.warn?.(`PTC reconciled interrupted training runs: ${reconciled.join(', ')}`);
      if (reconciledTemplateRuns.length > 0) webCtx.logger?.warn?.(`PTC interrupted workflow templates: ${reconciledTemplateRuns.join(', ')}`);
      if (reconciledPublishedTemplates.length > 0) webCtx.logger?.warn?.(`PTC interrupted published workflow templates: ${reconciledPublishedTemplates.join(', ')}`);
      if (reconciledPipelines.length > 0) webCtx.logger?.warn?.(`PTC marked interrupted pipeline runs: ${reconciledPipelines.join(', ')}`);
      const dispatcher = createTrainingDispatcher(webCtx, workspaceRoot);
      const profileSmoke = createProfileSmokeManager(webCtx, workspaceRoot, {
        onBackground: completion => void completion.catch(error =>
          webCtx.logger?.error?.(`PTC profile smoke failed: ${error.message}`)),
      });
      const workflowTemplates = createWorkflowTemplateRunner(workspaceRoot, profileSmoke, {
        onBackground: completion => void completion.catch(error =>
          webCtx.logger?.error?.(`PTC workflow template smoke failed: ${error.message}`)),
      });
      const publishedWorkflowTemplates = createPublishedWorkflowRunner(webCtx, workspaceRoot, {
        onBackground: completion => void completion.catch(error =>
          webCtx.logger?.error?.(`PTC published workflow template failed: ${error.message}`)),
      });
      const stageDispatcher = createPipelineDispatcher(webCtx, workspaceRoot);
      const pipelines = createPipelineExecutionManager(workspaceRoot, dispatcher, stageDispatcher);
      const arithmeticSmoke = createArithmeticRoleDispatcher(webCtx, workspaceRoot);
      const simpleOrchestration = createSimpleOrchestrationManager(workspaceRoot, {
        executeSmokeRole: request => arithmeticSmoke.executeSmokeRole(request),
        onBackground: completion => void completion.catch(error =>
          webCtx.logger?.error?.(`PTC simple orchestration failed: ${error.message}`)),
      });
      const rehearsals = createFrameworkRehearsalManager(workspaceRoot, createFrameworkRehearsalAdapters());
      const publishedFrameworkControllers = new Map();
      const trainingBoundary = exec => trainingGuardDecision(exec, workspaceRoot) ?? pipelineGuardDecision(exec, workspaceRoot);
      const preExecute = webCtx.on('tools/pre-execute', (exec, next) => {
        const reason = trainingBoundary(exec);
        if (!reason) {
          dispatcher.noteToolStart(exec);
          stageDispatcher.noteToolStart(exec);
        }
        return reason ? { kind: 'deny', reason } : next();
      }, { prepend: true });
      const guard = webCtx.tools.guard(trainingBoundary);
      const unregisterState = webCtx.webServer.register({
        kind: 'exact',
        path: '/api/ptc-control/state',
        handler: createStateHandler(workspaceRoot),
      });
      const unregisterTraining = webCtx.webServer.register({
        kind: 'exact',
        path: '/api/ptc-control/training-runs',
        handler: createTrainingRunHandler(workspaceRoot),
      });
      const unregisterTrainingExecution = webCtx.webServer.register({
        kind: 'exact',
        path: '/api/ptc-control/training-runs/execute',
        handler: archivedLegacyExecution,
      });
      const unregisterStop = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/training-runs/stop',
        handler: createTrainingStopHandler(dispatcher),
      });
      const unregisterProfileSmoke = ['execute', 'stop'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/profile-smoke/${action}`,
        handler: createProfileSmokeHandler(profileSmoke, action),
      }));
      const unregisterSimpleSmoke = ['execute', 'control'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/simple-orchestration/${action}`,
        handler: createSimpleOrchestrationHandler(simpleOrchestration, action),
      }));
      const unregisterTrainingSmokePublish = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/training-release/publish',
        handler: createTrainingSmokePublishHandler(workspaceRoot),
      });
      const unregisterTrainingSmokeFreeze = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/training-release/freeze',
        handler: createTrainingSmokeFreezeHandler(workspaceRoot),
      });
      const unregisterTrainingSmokeActivate = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/training-release/activate',
        handler: createTrainingSmokeActivateHandler(workspaceRoot),
      });
      const publishedSmokeDispatcher = createPublishedSmokeDispatcher(webCtx, workspaceRoot);
      const publishedSmokeControllers = new Map();
      const unregisterPublishedSmoke = ['execute', 'control'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/training-release/${action}`,
        handler: createPublishedSmokeHandler(workspaceRoot, publishedSmokeDispatcher,
          publishedSmokeControllers, action, webCtx.logger),
      }));
      const unregisterDrafts = ['read', 'save'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/training-drafts/${action}`,
        handler: createTrainingDraftHandler(workspaceRoot, action),
      }));
      const unregisterSessionWorkspace = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/session-workspace',
        handler: createPtcSessionWorkspaceHandler(workspaceRoot),
      });
      const unregisterWorkflowTemplates = ['read', 'save', 'freeze', 'execute', 'control'].map(action =>
        webCtx.webServer.register({ kind: 'exact', path: `/api/ptc-control/workflow-templates/${action}`,
          handler: createWorkflowTemplateHandler(workspaceRoot, workflowTemplates, action) }));
      const unregisterWorkflowTemplateReleases = ['stage', 'activate', 'read', 'execute', 'control'].map(action =>
        webCtx.webServer.register({ kind: 'exact', path: `/api/ptc-control/workflow-template-releases/${action}`,
          handler: createWorkflowTemplateReleaseHandler(workspaceRoot, publishedWorkflowTemplates, action) }));
      const unregisterIssues = ['create', 'list'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/training-issues/${action}`,
        handler: createTrainingIssueHandler(workspaceRoot, action),
      }));
      const unregisterCases = ['create', 'list'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/training-cases/${action}`,
        handler: createTrainingCaseHandler(workspaceRoot, action),
      }));
      const unregisterPipelines = ['execute', 'control'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/training-pipelines/${action}`,
        handler: archivedLegacyExecution,
      }));
      const unregisterRehearsals = ['execute', 'control'].map(action => webCtx.webServer.register({
        kind: 'exact', path: `/api/ptc-control/framework-rehearsals/${action}`,
        handler: archivedLegacyExecution,
      }));
      const unregisterFrameworkPublish = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/framework-releases/publish',
        handler: archivedLegacyExecution,
      });
      const unregisterFrameworkRecovery = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/framework-rehearsals/recover',
        handler: archivedLegacyExecution,
      });
      const unregisterPublishedFrameworkExecute = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/framework-releases/execute',
        handler: archivedLegacyExecution,
      });
      const unregisterPublishedFrameworkControl = webCtx.webServer.register({
        kind: 'exact', path: '/api/ptc-control/framework-releases/control',
        handler: archivedLegacyExecution,
      });
      const disposeTrainer = config.trainerEnabled === true ? mountTrainerHost(webCtx, config) : null;
      return () => {
        disposeTrainer?.();
        for (const controller of publishedFrameworkControllers.values()) controller.stop('plugin shutting down');
        publishedFrameworkControllers.clear();
        rehearsals.shutdown();
        simpleOrchestration.shutdown();
        workflowTemplates.shutdown();
        publishedWorkflowTemplates.shutdown();
        arithmeticSmoke.shutdown();
        for (const controller of publishedSmokeControllers.values()) controller.abort(new Error('plugin shutting down'));
        publishedSmokeControllers.clear();
        pipelines.shutdown();
        stageDispatcher.shutdown();
        dispatcher.shutdown();
        profileSmoke.shutdown();
        unregisterPublishedFrameworkControl?.();
        unregisterPublishedFrameworkExecute?.();
        unregisterFrameworkRecovery?.();
        unregisterFrameworkPublish?.();
        unregisterRehearsals.forEach(unregister => unregister?.());
        unregisterPipelines.forEach(unregister => unregister?.());
        unregisterDrafts.forEach(unregister => unregister?.());
        unregisterSessionWorkspace?.();
        unregisterWorkflowTemplates.forEach(unregister => unregister?.());
        unregisterWorkflowTemplateReleases.forEach(unregister => unregister?.());
        unregisterIssues.forEach(unregister => unregister?.());
        unregisterCases.forEach(unregister => unregister?.());
        unregisterStop?.();
        unregisterProfileSmoke.forEach(unregister => unregister?.());
        unregisterSimpleSmoke.forEach(unregister => unregister?.());
        unregisterTrainingSmokePublish?.();
        unregisterTrainingSmokeFreeze?.();
        unregisterTrainingSmokeActivate?.();
        unregisterPublishedSmoke.forEach(unregister => unregister?.());
        unregisterTrainingExecution?.();
        unregisterTraining?.();
        unregisterState?.();
        guard?.();
        preExecute?.();
      };
    }, 'dsh-ptc-control-plane: same-origin endpoints');
  });
  ctx.logger?.info?.(`dsh-ptc-control-plane active for ${workspaceRoot}`);
}
