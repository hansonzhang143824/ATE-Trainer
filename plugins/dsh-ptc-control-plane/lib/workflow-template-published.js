import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { loadWorkflowTemplateRelease } from './workflow-template-release.js';
import { createTrainingLifecycle } from './training-lifecycle.js';
import { resolveTrainingModelChoice } from './training-model.js';

const ID = /^workflow-published-[a-z0-9-]+$/;
const SHA = /^[a-f0-9]{64}$/;
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const json = value => `${JSON.stringify(value, null, 2)}\n`;
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
function safe(root, ...parts) { return assertSafeRunPath(root, path.join(root, ...parts)); }
function stateFile(root, runId) {
  if (typeof runId !== 'string' || !ID.test(runId)) throw new Error('invalid published workflow run ID');
  return safe(root, 'publish', 'workflow-templates', 'runs', runId, 'state.json');
}
function write(root, file, value) {
  const temporary = assertSafeRunPath(root, `${file}.${crypto.randomUUID()}.tmp`);
  fs.writeFileSync(temporary, json(value), { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}

export function readPublishedWorkflowRun(workspaceRoot, runId) {
  const root = path.resolve(workspaceRoot);
  const state = read(stateFile(root, runId));
  if (state.schemaVersion !== 1 || state.kind !== 'ptc-published-workflow-smoke-run'
      || state.runId !== runId || state.mode !== 'SMOKE_ONLY' || state.businessGatePassed !== false
      || state.outputUse !== 'diagnostic-only' || !Array.isArray(state.steps)) {
    throw new Error('invalid published workflow run');
  }
  const release = loadWorkflowTemplateRelease(root, state.releaseId);
  if (release.manifestSha256 !== state.releaseManifestSha256
      || JSON.stringify(state.steps.map(step => step.profileId))
        !== JSON.stringify(release.manifest.steps.map(step => step.profileId))) {
    throw new Error('published workflow run changed its release binding');
  }
  for (let index = 0; index < state.steps.length; index++) {
    const stateStep = state.steps[index];
    const releaseStep = release.manifest.steps[index];
    for (const field of ['agentRevision', 'agentManifestSha256', 'agentContentSha256']) {
      if (releaseStep[field] !== undefined && stateStep[field] !== releaseStep[field]) {
        throw new Error('published workflow Agent revision binding changed');
      }
    }
  }
  const childSessions = new Set();
  for (const step of state.steps) {
    if (step.status !== 'completed') continue;
    if ((step.answer !== undefined && (step.answer !== 3 || typeof step.answer !== 'number'))
        || !SHA.test(step.evidenceSha256 ?? '') || typeof step.evidencePath !== 'string') {
      throw new Error('published workflow child has no evidence hash');
    }
    const evidenceFile = assertSafeRunPath(root, step.evidencePath);
    const raw = fs.readFileSync(evidenceFile);
    const evidence = JSON.parse(raw.toString('utf8'));
    const responseFile = assertSafeRunPath(root, evidence.responsePath);
    const responseBytes = fs.readFileSync(responseFile);
    const result = JSON.parse(responseBytes.toString('utf8'));
    if (hash(raw) !== step.evidenceSha256 || evidence.runId !== runId
        || evidence.index !== step.index || evidence.profileId !== step.profileId
        || evidence.childSessionId !== step.childSessionId || evidence.answer !== 3
        || typeof evidence.answer !== 'number'
        || evidence.releaseManifestSha256 !== state.releaseManifestSha256
        || (step.agentRevision !== null && evidence.agentRevision !== step.agentRevision)
        || (step.agentManifestSha256 !== null && evidence.agentManifestSha256 !== step.agentManifestSha256)
        || (step.agentContentSha256 !== null && evidence.agentContentSha256 !== step.agentContentSha256)
        || hash(responseBytes) !== evidence.responseSha256
        || result?.stopReason !== 'completed' || result?.structured?.answer !== 3
        || typeof step.childSessionId !== 'string' || !step.childSessionId
        || childSessions.has(step.childSessionId)) {
      throw new Error('published workflow child evidence changed');
    }
    childSessions.add(step.childSessionId);
    step.answer = 3;
    if (step.index > 0 && step.upstreamEvidenceSha256 !== state.steps[step.index - 1].evidenceSha256) {
      throw new Error('published workflow handoff changed');
    }
  }
  if (state.status === 'completed' && (state.steps.some(step => step.status !== 'completed') || state.smokePassed !== true)) {
    throw new Error('published workflow lacks completed child receipts');
  }
  return state;
}

export function reconcileInterruptedPublishedWorkflowRuns(workspaceRoot) {
  const root = path.resolve(workspaceRoot);
  const directory = safe(root, 'publish', 'workflow-templates', 'runs');
  if (!fs.existsSync(directory)) return [];
  const changed = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    let state;
    try { state = readPublishedWorkflowRun(root, entry.name); } catch { continue; }
    if (state.status !== 'running') continue;
    state.status = 'interrupted';
    state.reason = 'host restarted during a published child; no automatic redispatch';
    state.currentProfileId = null;
    const current = state.steps.find(step => step.status === 'running');
    if (current) current.status = 'blocked';
    state.updatedAt = new Date().toISOString();
    write(root, stateFile(root, entry.name), state);
    changed.push(entry.name);
  }
  return changed;
}

/** Fresh model dispatch using only the activated frozen diagnostic release. */
export function createPublishedWorkflowRunner(ctx, workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const live = new Map();
  function launch(state) {
    const controller = { stopped: false, pauseRequested: false, lifecycle: null };
    live.set(state.runId, controller);
    const file = stateFile(root, state.runId);
    const save = () => { state.updatedAt = new Date().toISOString(); write(root, file, state); options.onState?.(structuredClone(state)); };
    const completion = (async () => {
      try {
        state.status = 'running'; save();
        const release = loadWorkflowTemplateRelease(root, state.releaseId);
        if (release.manifestSha256 !== state.releaseManifestSha256) throw new Error('frozen release changed');
        const selection = resolveTrainingModelChoice(options.modelChoice ?? 'default',
          ctx.agentDefaultModel.currentSelection());
        if (!ctx?.agents?.create || !ctx?.subagents?.start) throw new Error('DSH child services unavailable');
        for (const step of state.steps) {
          if (step.status === 'completed') continue;
          if (controller.stopped) break;
          if (controller.pauseRequested) { state.status = 'paused'; save(); return state; }
          loadWorkflowTemplateRelease(root, state.releaseId);
          const upstream = step.index > 0 ? state.steps[step.index - 1] : null;
          if (upstream) {
            readPublishedWorkflowRun(root, state.runId);
            step.upstreamEvidenceSha256 = upstream.evidenceSha256;
          }
          step.status = 'running'; state.currentProfileId = step.profileId; save();
          const lifecycle = createTrainingLifecycle({ timeoutMs: options.timeoutMs ?? 300_000 });
          controller.lifecycle = lifecycle;
          let child; let result;
          try {
            const agentOptions = { provider: selection.provider, model: selection.model, maxTokens: 256 };
            const parent = await lifecycle.race(() => ctx.agents.create({
              sessionId: `session-published-workflow-${crypto.randomUUID()}`,
              meta: { cwd: root }, agentOptions,
            }), { label: 'parent.create', disposeLate: handle => handle.dispose?.() });
            await lifecycle.race(() => parent.agent.whenIdle(), { label: 'parent.idle' });
            child = await lifecycle.race(() => ctx.subagents.start('spawn', {
              label: `PTC published smoke ${step.profileId} ${state.runId}`,
              parent: parent.agent, signal: lifecycle.signal, agentOptions, maxDepth: 1,
              toolFilter: { allow: [] },
              persona: `Frozen PTC diagnostic smoke role ${step.profileId}. Do not use tools, files or private project materials. This does not execute business rules.`,
              prompt: [{ type: 'text', text: '1+2等于几，把答案写在JSON里' }],
              outputSchema: { type: 'object', properties: { answer: { type: 'number' } },
                required: ['answer'], additionalProperties: false },
            }), { label: 'child.start', disposeLate: handle => {
              Promise.resolve(handle.result).catch(() => {}); return handle.dispose?.();
            } });
            result = await lifecycle.race(child.result, { label: 'child.result', trackSettlement: true });
            if (controller.stopped) break;
            if (result?.stopReason !== 'completed' || result?.structured?.answer !== 3
                || typeof result.structured.answer !== 'number' || !child?.id) {
              throw new Error(`Agent ${step.profileId} did not return numeric JSON answer 3`);
            }
            const responseFile = safe(root, 'publish', 'workflow-templates', 'runs', state.runId,
              'evidence', `${step.index}-${step.profileId}-response.json`);
            fs.mkdirSync(path.dirname(responseFile), { recursive: true });
            fs.writeFileSync(responseFile, json(result), { flag: 'wx' });
            const evidence = { schemaVersion: 1, kind: 'ptc-published-workflow-child',
              runId: state.runId, index: step.index, profileId: step.profileId,
              agentRevision: step.agentRevision ?? null,
              agentManifestSha256: step.agentManifestSha256 ?? null,
              agentContentSha256: step.agentContentSha256 ?? null,
              childSessionId: child.id, answer: 3, releaseManifestSha256: state.releaseManifestSha256,
              upstreamEvidenceSha256: step.upstreamEvidenceSha256,
              responsePath: path.relative(root, responseFile).split(path.sep).join('/'),
              responseSha256: hash(fs.readFileSync(responseFile)),
              finishedAt: new Date().toISOString() };
            const evidenceFile = safe(root, 'publish', 'workflow-templates', 'runs', state.runId,
              'evidence', `${step.index}-${step.profileId}.json`);
            fs.mkdirSync(path.dirname(evidenceFile), { recursive: true });
            fs.writeFileSync(evidenceFile, json(evidence), { flag: 'wx' });
            step.evidencePath = path.relative(root, evidenceFile).split(path.sep).join('/');
            step.evidenceSha256 = hash(fs.readFileSync(evidenceFile));
            step.childSessionId = child.id;
            step.answer = 3;
            step.status = 'completed'; save();
          } finally { lifecycle.close(); controller.lifecycle = null; }
        }
        state.currentProfileId = null;
        state.status = controller.stopped ? 'cancelled' : 'completed';
        state.smokePassed = state.status === 'completed' && state.steps.every(step => step.status === 'completed');
        save();
      } catch (error) {
        state.status = controller.stopped ? 'cancelled' : 'blocked';
        state.reason = String(error?.message ?? error);
        const current = state.steps.find(step => step.status === 'running');
        if (current) current.status = state.status;
        state.currentProfileId = null; save();
      } finally { live.delete(state.runId); }
      return state;
    })();
    options.onBackground?.(completion);
    return { runId: state.runId, status: 'running', mode: 'SMOKE_ONLY', completion };
  }
  return {
    start() {
      const release = loadWorkflowTemplateRelease(root);
      const runId = `workflow-published-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${crypto.randomUUID().slice(0, 8)}`;
      const file = stateFile(root, runId);
      fs.mkdirSync(path.dirname(file), { recursive: true });
      const state = { schemaVersion: 1, kind: 'ptc-published-workflow-smoke-run', runId,
        releaseId: release.manifest.releaseId, releaseManifestSha256: release.manifestSha256,
        mode: 'SMOKE_ONLY', outputUse: 'diagnostic-only', businessGatePassed: false,
        status: 'created', smokePassed: false, currentProfileId: null, reason: null,
        createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
        steps: release.manifest.steps.map((entry, index) => ({ index, profileId: entry.profileId,
          agentRevision: entry.agentRevision ?? null,
          agentManifestSha256: entry.agentManifestSha256 ?? null,
          agentContentSha256: entry.agentContentSha256 ?? null,
          status: 'pending', upstreamEvidenceSha256: null, childSessionId: null,
          evidencePath: null, evidenceSha256: null, answer: null })) };
      fs.writeFileSync(file, json(state), { flag: 'wx' });
      return launch(state);
    },
    control(runId, action) {
      if (action === 'resume') {
        if (live.has(runId)) throw new Error('published workflow already active');
        const state = readPublishedWorkflowRun(root, runId);
        if (state.status !== 'paused') throw new Error('only paused published workflow can resume');
        return launch(state);
      }
      const controller = live.get(runId);
      if (!controller) throw new Error('published workflow not active');
      if (action === 'pause') controller.pauseRequested = true;
      else if (action === 'stop') {
        controller.stopped = true;
        controller.lifecycle?.cancel('published workflow stopped by user');
      } else throw new Error('unsupported published workflow control');
      return { runId, status: action === 'pause' ? 'pausing' : 'stop_requested' };
    },
    shutdown() {
      for (const controller of live.values()) {
        controller.stopped = true;
        controller.lifecycle?.cancel('plugin shutting down');
      }
    },
  };
}
