import fs from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';

const MUTATIONS = new Set(['apply-changes', 'run', 'control', 'freeze', 'stage-release', 'activate-release']);
const TRAINING = new Set(['apply-changes', 'freeze']);
const PAGE_ONLY = new Set(['freeze', 'stage-release', 'activate-release', 'bind-session']);
const TOOL_PRESETS = new Set(['agent-trainer', 'framework-expert', 'framework-observer']);
const clone = value => JSON.parse(JSON.stringify(value));
function fail(code, message, details) { throw Object.assign(new Error(message), { code, details }); }
function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${stable(value[k])}`).join(',')}}`;
  return JSON.stringify(value);
}
function id(value, field) {
  if (typeof value !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$/.test(value)
    || /^(con|prn|aux|nul|com[0-9]|lpt[0-9])$/i.test(value)) fail('invalid_identity', `Invalid ${field}`);
  return value;
}
function atomic(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temp = `${file}.${randomUUID()}.tmp`;
  fs.writeFileSync(temp, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  fs.renameSync(temp, file);
}
function read(file, fallback) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return fallback; throw error; }
}

/** One authority for UI and preset tools. repositories contains B's named exports. */
export function createTrainerService({ workspaceRoot, runner, repositories, modelResolver, sessionVerifier }) {
  const storage = path.join(workspaceRoot, 'Training_Materials/framework/control');
  let queue = Promise.resolve();
  const serial = task => { const next = queue.then(task, task); queue = next.catch(() => {}); return next; };
  const bindingFile = sessionId => path.join(storage, 'bindings', `${id(sessionId, 'sessionId')}.json`);
  const getBinding = sessionId => read(bindingFile(sessionId), null);
  const call = (name, args) => {
    if (typeof repositories[name] !== 'function') fail('operation_unavailable', `Repository operation ${name} is unavailable`);
    return repositories[name](workspaceRoot, args);
  };
  async function authorize(operation, supplied, principal) {
    const args = clone(supplied || {});
    if (principal?.kind === 'page') {
      if (!['training', 'published', 'engineering'].includes(args.mode || 'training')) fail('invalid_mode', 'Unknown workbench mode');
      return { args: { mode: 'training', projectId: 'synthetic-lab', ...args }, binding: null };
    }
    if (principal?.kind !== 'tool' || !TOOL_PRESETS.has(principal.presetId)) fail('forbidden', 'A dedicated framework session is required');
    if (PAGE_ONLY.has(operation)) fail('page_action_required', 'Freeze and release require an explicit workbench action');
    const binding = getBinding(principal.sessionId);
    if (!binding || binding.presetId !== principal.presetId) fail('session_unbound', 'Open and bind this session from the workbench');
    if (sessionVerifier && !(await sessionVerifier(principal.sessionId, principal.presetId))) fail('session_identity_mismatch', 'Native session identity does not match its binding');
    if (args.projectId && args.projectId !== binding.projectId) fail('project_forbidden', 'Session is bound to another project');
    if (args.mode && args.mode !== binding.mode) fail('mode_forbidden', 'Session mode is controlled by its server binding');
    if (principal.presetId !== 'agent-trainer') {
      if (!['context', 'assets', 'run', 'runs', 'events', 'control', 'compare'].includes(operation)) fail('expert_management_forbidden', 'This session has no candidate management permission');
      if ((args.targetId && args.targetId !== binding.targetId) || (args.targetKind && args.targetKind !== binding.targetKind)) fail('target_forbidden', 'Expert session may only run its bound target');
    }
    return { args: { ...binding, ...args, projectId: binding.projectId, mode: binding.mode }, binding };
  }
  async function bind(args) {
    if (args.sessionId && !args.targetId && !args.presetId) {
      const existing=getBinding(args.sessionId);
      if (!existing || !sessionVerifier || !(await sessionVerifier(args.sessionId,existing.presetId))) fail('session_unbound','Session has no verified framework binding');
      const project=await call('readProject',{projectId:existing.projectId});
      return {...existing,candidateRevision:project.revisionId};
    }
    id(args.projectId, 'projectId'); id(args.targetId, 'targetId');
    if (!['agent', 'workflow'].includes(args.targetKind) || !TOOL_PRESETS.has(args.presetId)) fail('invalid_binding', 'Invalid target or preset');
    if (args.presetId === 'framework-observer' && args.mode === 'training') fail('invalid_binding', 'Observer requires published or engineering mode');
    if (args.presetId === 'framework-expert' && (args.targetKind !== 'agent' || args.mode !== 'training')) fail('invalid_binding', 'Expert requires a training agent target');
    const project = await call('ensureTrainerProject', { projectId: args.projectId });
    const items = args.targetKind === 'agent' ? project.agents : project.workflows;
    if (!(items || []).some(item => (item.agentId || item.workflowId) === args.targetId)) fail('target_missing', 'Target is not registered');
    const key = createHash('sha256').update(stable([args.projectId,args.mode,args.presetId,args.targetKind,args.targetId])).digest('hex');
    const cwd = path.join(storage, 'sessions', key);
    fs.mkdirSync(cwd, { recursive: true });
    const instructions = '# Synthetic Agent Trainer workspace\nOnly synthetic framework assets and runs. Do not load archived business profiles or private inputs. Use the registered framework tools and server binding. businessGatePassed remains false.\n';
    if (!fs.existsSync(path.join(cwd, 'AGENTS.md'))) fs.writeFileSync(path.join(cwd, 'AGENTS.md'), instructions);
    const result = { projectId: args.projectId, targetKind: args.targetKind, targetId: args.targetId,
      presetId: args.presetId, mode: args.mode, selectedRunId: args.selectedRunId || null,
      nativeModelSelection: {provider:'deepseek-official',model:'deepseek-v4-flash'},
      candidateRevision: project.revisionId, bindingSchemaVersion: 1, cwd };
    if (!args.sessionId) return { ...result, bindingRevision: 0 };
    if (!sessionVerifier || !(await sessionVerifier(args.sessionId, args.presetId))) fail('session_identity_mismatch', 'Native session must use the requested dedicated preset');
    if (args.selectedRunId) await ownedRun({ projectId: args.projectId, runId: args.selectedRunId });
    const old = getBinding(args.sessionId);
    if (old && (old.projectId !== args.projectId || old.presetId !== args.presetId || old.targetId !== args.targetId || old.targetKind !== args.targetKind || old.mode !== args.mode)) fail('session_binding_conflict', 'Native session identity cannot be reused for another target');
    if (old && args.baseBindingRevision !== old.bindingRevision) fail('binding_conflict', 'Refresh the binding before changing its selected run');
    const binding = { ...result, sessionId: args.sessionId, bindingRevision: (old?.bindingRevision || 0) + 1 };
    atomic(bindingFile(args.sessionId), binding);
    return binding;
  }
  async function ownedRun(args, binding) {
    const run = await runner.readRun({ runId: id(args.runId || args.selectedRunId, 'runId') });
    if (!run || run.projectId !== args.projectId) fail('run_not_found', 'Run is not in the bound project');
    if (binding && binding.presetId !== 'agent-trainer' && (run.targetId !== binding.targetId || run.targetKind !== binding.targetKind)) fail('target_forbidden', 'Run belongs to another target');
    return run;
  }
  async function execute(operation, args, binding) {
    if (operation === 'bind-session') return bind(args);
    id(args.projectId, 'projectId');
    if (TRAINING.has(operation) && args.mode !== 'training') fail('read_only_mode', 'Published and engineering sessions cannot modify candidates or versions');
    if (['stage-release','activate-release'].includes(operation) && args.mode === 'engineering') fail('read_only_mode','Activate versions from the publication page');
    const target = { projectId: args.projectId, targetKind: args.targetKind, targetId: args.targetId };
    switch (operation) {
      case 'bind-session': return bind(args);
      case 'context': {
        const project = await call('ensureTrainerProject', { projectId: args.projectId });
        const frozenVersions = repositories.listFrozenVersions ? (await call('listFrozenVersions',{projectId:args.projectId})).versions : [];
        return { project, binding, frozenVersions, candidateRevision: project.revisionId, mode: args.mode,
          selectedRun: args.selectedRunId ? await ownedRun(args, binding) : null,
          capabilities: { edit: args.mode === 'training' && (!binding || binding.presetId === 'agent-trainer'), freeze: !binding && args.mode === 'training' } };
      }
      case 'assets': return call('readAssets', args);
      case 'apply-changes':
        if (args.linkedRunId) await ownedRun({...args,runId:args.linkedRunId},binding);
        return call('applyChanges', args);
      case 'changes': return call('readChangeSet', args);
      case 'validate': {
        const model = await modelResolver(args);
        const bundle = await call('resolveBundle', { ...args, model });
        return { validation: await repositories.verifyBundle(bundle), bundleSha256: bundle.bundleSha256, revisionId: bundle.revisionId };
      }
      case 'run': {
        if (args.derivedFromRunId) await ownedRun({ ...args, runId: args.derivedFromRunId }, binding);
        if (args.mode !== 'training' && !args.releaseId) {
          const versions=await call('listReleases',{projectId:args.projectId});
          const active=versions.active.find(item=>item.targetKind===args.targetKind && item.targetId===args.targetId);
          if (!active) fail('release_not_active','No active release for this target');
          args={...args,releaseId:active.releaseId};
        }
        const bundle = args.mode === 'training'
          ? await call('resolveBundle', { ...args, model: await modelResolver(args) })
          : await call('loadReleaseBundle', args);
        const resolved = bundle.bundle || bundle;
        if (resolved.projectId !== args.projectId) fail('bundle_project_mismatch', 'Bundle project mismatch');
        const started=await runner.startRun({ runId: args._runId, requestId: args.requestId, bundle: resolved,
          input: args.input || {}, mode: args.mode === 'training' ? 'training' : 'published',
          derivedFromRunId: args.derivedFromRunId, changeSetId: args.changeSetId, releaseId: bundle.releaseId || args.releaseId });
        if (binding) {
          const current=getBinding(binding.sessionId);
          atomic(bindingFile(binding.sessionId),{...current,selectedRunId:started.runId,bindingRevision:current.bindingRevision+1});
        }
        return started;
      }
      case 'runs': return args.runId ? ownedRun(args, binding)
        : runner.listRuns({ projectId: args.projectId, limit: args.limit, cursor: args.cursor, ...(binding?.presetId !== 'agent-trainer' && binding ? target : {}) });
      case 'events': await ownedRun(args, binding); return runner.readEvents({ runId: args.runId || args.selectedRunId, cursor: args.cursor });
      case 'control': await ownedRun(args, binding); return runner.controlRun({ runId: args.runId || args.selectedRunId, action: args.action });
      case 'freeze': {
        let bundle;
        if (args.changes?.length) {
          const saved=await call('applyChanges',args);
          args={...args,revisionId:saved.revisionId};
        }
        if (args.runId) { const run = await ownedRun(args); bundle = run.bundle; if (!bundle) fail('run_bundle_unavailable', 'Run snapshot is unavailable'); }
        else bundle = await call('resolveBundle', { ...args, model: await modelResolver(args) });
        return call('freezeTarget', { ...target, revisionId: args.revisionId, bundle });
      }
      case 'stage-release': return call('stageRelease', { ...args, runEvidence: await ownedRun(args) });
      case 'activate-release': return call('activateRelease', args);
      case 'releases': return call('listReleases', args);
      case 'compare': {
        const before = await ownedRun({ ...args, runId: args.beforeRunId }, binding);
        const after = await ownedRun({ ...args, runId: args.afterRunId }, binding);
        return { before, after, sameBundle: before.bundleSha256 === after.bundleSha256,
          changeSet: after.changeSetId ? await call('readChangeSet', { projectId: args.projectId, changeSetId: after.changeSetId }) : null };
      }
      default: fail('unknown_operation', `Unknown trainer operation: ${operation}`);
    }
  }
  async function invoke(operation, input, principal) {
    try {
      const { args, binding } = await authorize(operation, input, principal);
      if (!MUTATIONS.has(operation)) return { ok: true, value: await (operation === 'bind-session' ? serial(() => execute(operation, args, binding)) : execute(operation, args, binding)) };
      id(args.requestId, 'requestId');
      return await serial(async () => {
        const fingerprint = createHash('sha256').update(stable({ operation, input: input || {}, projectId: args.projectId, mode: args.mode,
          principal: principal?.kind === 'page' ? 'page' : principal })).digest('hex');
        const journal = path.join(storage, 'requests', id(args.projectId, 'projectId'), `${args.requestId}.json`);
        const previous = read(journal, null);
        if (previous) {
          if (previous.fingerprint !== fingerprint) fail('request_conflict', 'requestId was already used with different content');
          if (previous.response) return previous.response;
          if (previous.runId) {
            try { const run = await runner.readRun({ runId: previous.runId }); if (run) return { ok: true, value: run }; } catch { /* no durable run */ }
          }
          fail('request_interrupted', 'Previous request did not finish; inspect its recorded state before using a new requestId', { runId: previous.runId });
        }
        const runId = operation === 'run' ? `framework-${randomUUID()}` : undefined;
        atomic(journal, { fingerprint, operation, runId, status: 'pending' });
        let response;
        try { response = { ok: true, value: await execute(operation, { ...args, _runId: runId }, binding) }; }
        catch (error) { response = errorResult(error); }
        response = clone(response);
        atomic(journal, { fingerprint, operation, runId, status: 'settled', response });
        return response;
      });
    } catch (error) { return errorResult(error); }
  }
  return { invoke, getBinding };
}
function errorResult(error) {
  return { ok: false, error: { code: error.code || 'trainer_operation_failed', message: error.message || String(error), ...(error.details === undefined ? {} : { details: error.details }) } };
}
