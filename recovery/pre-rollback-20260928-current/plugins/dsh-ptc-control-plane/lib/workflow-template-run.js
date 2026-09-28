import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { createTrainingRun } from './training-run.js';
import { loadFrozenWorkflowTemplate } from './workflow-template.js';

const ID = /^[a-z0-9][a-z0-9-]{1,127}$/;
const SHA = /^[a-f0-9]{64}$/;
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
function safe(root, ...parts) { return assertSafeRunPath(root, path.join(root, ...parts)); }
function fileFor(root, runId) {
  if (typeof runId !== 'string' || !ID.test(runId) || !runId.startsWith('workflow-smoke-')) {
    throw new Error('invalid workflow smoke run ID');
  }
  return safe(root, 'Training_Materials', 'workflow-runs', runId, 'state.json');
}
function atomic(root, file, value) {
  const temporary = assertSafeRunPath(root, `${file}.${crypto.randomUUID()}.tmp`);
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
function verifyStep(root, step) {
  if (step.status !== 'completed' || (step.answer !== undefined && (step.answer !== 3 || typeof step.answer !== 'number'))
      || !SHA.test(step.evidenceSha256 ?? '')) throw new Error('workflow step is not verified');
  const file = assertSafeRunPath(root, step.evidencePath);
  const raw = fs.readFileSync(file);
  if (hash(raw) !== step.evidenceSha256) throw new Error('workflow child evidence changed');
  const evidence = JSON.parse(raw.toString('utf8'));
  if (evidence.runId !== step.profileRunId || evidence.profileId !== step.profileId
      || evidence.status !== 'completed' || evidence.answer !== 3
      || typeof evidence.answer !== 'number' || evidence.mode !== 'SMOKE_ONLY'
      || evidence.businessGatePassed !== false || !SHA.test(evidence.profileSnapshotSha256 ?? '')) {
    throw new Error('workflow child evidence identity or numeric answer differs');
  }
  step.answer = 3;
  return evidence;
}

export function readWorkflowTemplateRun(workspaceRoot, runId) {
  const root = path.resolve(workspaceRoot);
  const record = read(fileFor(root, runId));
  if (record?.schemaVersion !== 1 || record.kind !== 'ptc-generic-workflow-smoke-run'
      || record.runId !== runId || record.mode !== 'SMOKE_ONLY' || record.businessGatePassed !== false
      || record.outputUse !== 'diagnostic-only'
      || !['created', 'running', 'paused', 'completed', 'blocked', 'cancelled', 'interrupted'].includes(record.status)
      || !Array.isArray(record.steps) || record.steps.length < 1) throw new Error('invalid workflow run record');
  const frozen = loadFrozenWorkflowTemplate(root, record.templateId, record.templateSha256);
  if (JSON.stringify(record.steps.map(step => step.profileId)) !== JSON.stringify(frozen.template.profileIds)) {
    throw new Error('workflow run order differs from frozen template');
  }
  for (let index = 0; index < record.steps.length; index++) {
    const step = record.steps[index];
    if (step.index !== index || !['pending', 'running', 'completed', 'blocked', 'cancelled'].includes(step.status)) {
      throw new Error('invalid workflow step status');
    }
    if (step.status === 'completed') verifyStep(root, step);
    if (index > 0 && step.status === 'completed'
        && step.upstreamEvidenceSha256 !== record.steps[index - 1].evidenceSha256) {
      throw new Error('workflow handoff binding changed');
    }
  }
  if (record.status === 'completed' && record.steps.some(step => step.status !== 'completed')) {
    throw new Error('workflow claims completion without all child receipts');
  }
  return record;
}

/** A restarted host never silently relaunches a child with the same dispatch identity. */
export function reconcileInterruptedWorkflowTemplateRuns(workspaceRoot) {
  const root = path.resolve(workspaceRoot);
  const directory = safe(root, 'Training_Materials', 'workflow-runs');
  if (!fs.existsSync(directory)) return [];
  const changed = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    let record;
    try { record = readWorkflowTemplateRun(root, entry.name); } catch { continue; }
    if (record.status !== 'running') continue;
    record.status = 'interrupted';
    record.reason = 'host restarted during a workflow child; inspect its receipt before a new run';
    record.currentProfileId = null;
    const current = record.steps.find(step => step.status === 'running');
    if (current) current.status = 'blocked';
    record.updatedAt = new Date().toISOString();
    atomic(root, fileFor(root, entry.name), record);
    changed.push(entry.name);
  }
  return changed;
}

/** Sequential smoke-only execution of any saved, ordered Agent subset. */
export function createWorkflowTemplateRunner(workspaceRoot, profileSmoke, options = {}) {
  const root = path.resolve(workspaceRoot);
  const live = new Map();
  function launch(record) {
    if (live.has(record.runId)) throw new Error('workflow run already active');
    const controller = { stopped: false, pauseRequested: false, activeProfileRunId: null };
    live.set(record.runId, controller);
    const file = fileFor(root, record.runId);
    const save = () => { record.updatedAt = new Date().toISOString(); atomic(root, file, record); options.onState?.(structuredClone(record)); };
    const completion = (async () => {
      try {
        record.status = 'running'; save();
        for (const step of record.steps) {
          if (step.status === 'completed') { verifyStep(root, step); continue; }
          if (controller.stopped) break;
          if (controller.pauseRequested) { record.status = 'paused'; save(); return record; }
          const prior = step.index > 0 ? record.steps[step.index - 1] : null;
          if (prior) {
            verifyStep(root, prior);
            step.upstreamEvidenceSha256 = prior.evidenceSha256;
          }
          const created = createTrainingRun(root, { target: { kind: 'profile', profileId: step.profileId },
            purpose: 'smoke-training' });
          step.profileRunId = created.state.runId;
          step.status = 'running';
          record.currentProfileId = step.profileId;
          controller.activeProfileRunId = step.profileRunId;
          save();
          const started = profileSmoke.start({ runId: step.profileRunId, modelChoice: options.modelChoice ?? 'default' });
          await started.completion;
          controller.activeProfileRunId = null;
          if (controller.stopped) break;
          const state = read(safe(root, 'Training_Materials', 'runs', step.profileRunId, 'state.json'));
          if (state.status !== 'completed' || state.outcome?.smokePassed !== true) {
            throw new Error(`Agent ${step.profileId} failed its fresh 1+2 child run`);
          }
          const evidencePath = state.outcome?.evidence;
          const evidenceSha256 = state.outcome?.evidenceSha256;
          if (typeof evidencePath !== 'string' || !SHA.test(evidenceSha256 ?? '')) {
            throw new Error('Agent returned no bound evidence');
          }
          step.evidencePath = evidencePath;
          step.evidenceSha256 = evidenceSha256;
          step.answer = 3;
          step.status = 'completed';
          verifyStep(root, step);
          save();
        }
        record.currentProfileId = null;
        record.status = controller.stopped ? 'cancelled' : 'completed';
        record.smokePassed = record.status === 'completed' && record.steps.every(step => step.status === 'completed');
        save();
      } catch (error) {
        record.status = controller.stopped ? 'cancelled' : 'blocked';
        record.reason = String(error?.message ?? error);
        const active = record.steps.find(step => step.status === 'running');
        if (active) active.status = record.status;
        record.currentProfileId = null;
        save();
      } finally { live.delete(record.runId); }
      return record;
    })();
    options.onBackground?.(completion);
    return { runId: record.runId, status: 'running', mode: 'SMOKE_ONLY', completion };
  }
  return {
    start(input) {
      const frozen = loadFrozenWorkflowTemplate(root, input?.templateId, input?.versionSha256);
      const runId = `workflow-smoke-${new Date().toISOString().replace(/[-:.]/g, '').toLowerCase()}-${crypto.randomUUID().slice(0, 8)}`;
      const file = fileFor(root, runId);
      fs.mkdirSync(path.dirname(file), { recursive: true });
      const record = { schemaVersion: 1, kind: 'ptc-generic-workflow-smoke-run', runId,
        templateId: frozen.template.templateId, templateSha256: frozen.sha256,
        mode: 'SMOKE_ONLY', status: 'created', smokePassed: false, businessGatePassed: false,
        outputUse: 'diagnostic-only', currentProfileId: null, reason: null,
        createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
        steps: frozen.template.profileIds.map((profileId, index) => ({ index, profileId,
          status: 'pending', profileRunId: null, upstreamEvidenceSha256: null,
          evidencePath: null, evidenceSha256: null, answer: null })) };
      fs.writeFileSync(file, `${JSON.stringify(record, null, 2)}\n`, { flag: 'wx' });
      return launch(record);
    },
    control(runId, action) {
      if (action === 'resume') {
        if (live.has(runId)) throw new Error('workflow run is already active');
        const record = readWorkflowTemplateRun(root, runId);
        if (record.status !== 'paused') throw new Error('only a paused workflow can resume');
        return launch(record);
      }
      const controller = live.get(runId);
      if (!controller) throw new Error('workflow run is not active');
      if (action === 'pause') controller.pauseRequested = true;
      else if (action === 'stop') {
        controller.stopped = true;
        if (controller.activeProfileRunId) profileSmoke.stop(controller.activeProfileRunId,
          'workflow stopped by user');
      } else throw new Error('unsupported workflow run action');
      return { runId, status: action === 'pause' ? 'pausing' : 'stop_requested' };
    },
    shutdown() {
      for (const controller of live.values()) {
        controller.stopped = true;
        if (controller.activeProfileRunId) profileSmoke.stop(controller.activeProfileRunId,
          'workflow runner shutting down');
      }
    },
  };
}
