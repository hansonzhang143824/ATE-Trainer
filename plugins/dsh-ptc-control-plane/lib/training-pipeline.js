import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { sha256Bytes } from './release-integrity.js';

const ACTIVE = new Map();
const ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const ROLE = /^[a-z][a-z0-9-]{1,63}$/;
const TERMINAL = new Set(['completed', 'blocked', 'cancelled']);
const clone = (value) => structuredClone(value);
function fail(message) { throw new Error(`training pipeline: ${message}`); }
function safePath(root, relative = '') {
  const absolute = path.resolve(root, relative);
  const rel = path.relative(path.resolve(root), absolute);
  if (rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) fail('path escapes run');
  const parsed = path.parse(absolute);
  let current = parsed.root;
  for (const segment of absolute.slice(parsed.root.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, segment);
    try { if (fs.lstatSync(current).isSymbolicLink()) fail('symbolic link in training path'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
  return absolute;
}
function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '')); }
function atomicJson(file, value) {
  const temporary = `${file}.${randomUUID()}.tmp`;
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
function normalizedItems(items) {
  if (!Array.isArray(items) || !items.length || items.some((item) => typeof item !== 'string' || !/^TM\d+$/.test(item))
    || new Set(items).size !== items.length) fail('testItems must be unique explicit TMs');
  return [...items].sort((left, right) => Number(left.slice(2)) - Number(right.slice(2)));
}
function same(left, right) { return JSON.stringify(left) === JSON.stringify(right); }
function registryStages(registry, target) {
  const stages = registry.stateMachine?.filter((stage) => stage !== 'COMPLETE');
  if (!Array.isArray(stages) || !stages.length || new Set(stages).size !== stages.length
    || stages.some((stage) => typeof stage !== 'string' || !/^[A-Z][A-Z0-9_]+$/.test(stage)
      || !ROLE.test(registry.stages?.[stage]?.owner) || typeof registry.stages?.[stage]?.gate !== 'string'
      || !/^scripts\/[A-Za-z0-9_.-]+\.(py|mjs|js)$/.test(registry.stages[stage].gate))) fail('invalid authoritative stage registry');
  const from = stages.indexOf(target.fromStage);
  const to = stages.indexOf(target.toStage);
  if (from < 0 || to < from) fail('invalid stage range');
  const selected = stages.slice(from, to + 1);
  if (target.stages && !same(target.stages, selected)) fail('training stage range disagrees with registry');
  return selected;
}

/**
 * Pure orchestration engine: adapters own real DSH dispatch, gate commands and
 * tool boundary enforcement. This module never invokes production advance_batch.
 *
 * dispatchStage(request) / recoverStage(request) return
 * {terminals:[{role,status:'done',testItems:[...]}]}; no role or TM may be omitted.
 * runStageGate(request) returns {status:'passed',exitCode:0,gate:request.gate,...}.
 * Every request includes immutable-by-copy registry owner/gate, all TMs,
 * expectedRoles, dispatchId, run-local addressBook and an AbortSignal. The adapter
 * must honor the signal and must never replace addressBook with delivery paths.
 * sourceRoles is the trusted INPUT_SYNC planner's role list; the registry owns
 * that stage as captain and does not itself enumerate parsing specialists.
 *
 * Pause drains an in-flight operation then stops before the next operation.
 * Cancel aborts immediately and discards late results. An interrupted dispatch
 * can only recover through recoverStage; it is never silently redispatched.
 */
export function createTrainingPipeline({ workspaceRoot, runId, testItems, sourceRoles,
  dispatchStage, runStageGate, recoverStage, onState,
  dispatchTimeoutMs = 8 * 60_000, gateTimeoutMs = 30_000 }) {
  if (!ID.test(runId) || /[. ]$/.test(runId) || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)/i.test(runId)) fail('invalid runId');
  if (typeof dispatchStage !== 'function' || typeof runStageGate !== 'function') fail('real dispatch and gate adapters are required');
  if (!Number.isFinite(dispatchTimeoutMs) || dispatchTimeoutMs <= 0 || dispatchTimeoutMs > 8 * 60_000
    || !Number.isFinite(gateTimeoutMs) || gateTimeoutMs <= 0 || gateTimeoutMs > 30_000) fail('timeouts exceed execution contract');
  const root = safePath(path.resolve(workspaceRoot), `Training_Materials/runs/${runId}`);
  if (ACTIVE.has(root)) fail('run already has an active pipeline controller');
  const contextFile = safePath(root, 'run.json');
  const contextBytes = fs.readFileSync(contextFile);
  const context = JSON.parse(contextBytes.toString('utf8').replace(/^\uFEFF/, ''));
  if (context.runId !== runId || context.mode !== 'training' || context.releaseId !== null || context.projectId !== null
    || path.resolve(workspaceRoot, context.artifactRoot) !== root) fail('run is not an isolated training identity');
  const runState = readJson(safePath(root, 'state.json'));
  if (runState.target?.kind !== 'pipeline') fail('run target must be pipeline');
  const progressFile = safePath(root, 'pipeline-progress.json');
  let expectedProgressDigest = fs.existsSync(progressFile) ? sha256Bytes(fs.readFileSync(progressFile)) : null;
  const registryFile = safePath(root, 'pipeline-registry.json');
  const addressBook = Object.fromEntries(['input', 'input-sync', 'strategy', 'method', 'review', 'implementation', 'compile', 'verification', 'receipts', 'ErrorLog']
    .map((name) => [name, safePath(root, name)]));
  addressBook.runRoot = root;
  for (const directory of Object.values(addressBook)) fs.mkdirSync(directory, { recursive: true });
  let registry;
  let state;
  if (fs.existsSync(progressFile)) {
    state = readJson(progressFile);
    const registryBytes = fs.readFileSync(registryFile);
    registry = JSON.parse(registryBytes.toString('utf8').replace(/^\uFEFF/, ''));
    if (state.schemaVersion !== 1 || state.runId !== runId || state.contextDigest !== sha256Bytes(contextBytes)
      || state.registryDigest !== sha256Bytes(registryBytes)) fail('persisted run or registry binding changed');
    if (!Array.isArray(state.stages) || !same(state.stages.map((stage) => stage.stage), registryStages(registry, runState.target))) fail('persisted stages disagree with registry');
    if (testItems && !same(normalizedItems(testItems), state.testItems)) fail('testItems cannot change on resume');
    if (sourceRoles && !same(sourceRoles, state.sourceRoles)) fail('sourceRoles cannot change on resume');
    if (!TERMINAL.has(state.status) && state.status !== 'created' && state.status !== 'paused') {
      state.status = 'interrupted';
      state.reason = 'host_interrupted; reconcile any in-flight dispatch before resuming';
    }
  } else {
    const registryBytes = fs.readFileSync(safePath(path.resolve(workspaceRoot), 'team/ptc/ptc_stage_registry.json'));
    registry = JSON.parse(registryBytes.toString('utf8').replace(/^\uFEFF/, ''));
    const selected = registryStages(registry, runState.target);
    const items = normalizedItems(testItems);
    const roles = sourceRoles ?? [];
    if (!Array.isArray(roles) || roles.some((role) => !ROLE.test(role)) || new Set(roles).size !== roles.length
      || (selected.includes('INPUT_SYNC') && !roles.length)) fail('INPUT_SYNC requires an explicit source-role plan');
    if (fs.existsSync(registryFile)) fail('orphan registry snapshot requires explicit recovery');
    fs.writeFileSync(registryFile, registryBytes, { flag: 'wx' });
    state = { schemaVersion: 1, runId, contextDigest: sha256Bytes(contextBytes), registryDigest: sha256Bytes(registryBytes),
      testItems: items, sourceRoles: [...roles], status: 'created', pauseRequested: false,
      createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), reason: null,
      stages: selected.map((stage) => ({ stage, status: 'pending', dispatchId: `${runId}:${stage}:1`, terminals: null, gateResult: null })) };
  }
  let inFlight;
  let activePromise;
  function save() {
    const actualDigest = fs.existsSync(progressFile) ? sha256Bytes(fs.readFileSync(progressFile)) : null;
    if (actualDigest !== expectedProgressDigest) fail('progress changed; reopen this stale controller');
    state.updatedAt = new Date().toISOString();
    safePath(root, 'pipeline-progress.json');
    atomicJson(progressFile, state);
    expectedProgressDigest = sha256Bytes(fs.readFileSync(progressFile));
    // Display observers must not turn a successful command into a duplicate retry.
    try { onState?.(clone(state)); } catch {}
  }
  function request(stage) {
    const definition = registry.stages[stage.stage];
    return { runId, mode: 'training', stage: stage.stage, owner: definition.owner, gate: definition.gate,
      families: clone(definition.families ?? []), outputs: clone(definition.outputs ?? []),
      expectedRoles: stage.stage === 'INPUT_SYNC' ? [...state.sourceRoles] : [definition.owner],
      testItems: [...state.testItems], dispatchId: stage.dispatchId, addressBook: { ...addressBook },
      registryDigest: state.registryDigest, terminals: clone(stage.terminals) };
  }
  async function operation(callback, payload, timeout, name) {
    const controller = new AbortController();
    inFlight = controller;
    let timer;
    const aborted = new Promise((resolve, reject) => {
      controller.signal.addEventListener('abort', () => reject(controller.signal.reason ?? new Error('cancelled')), { once: true });
      timer = setTimeout(() => controller.abort(new Error(`${name} exceeded ${timeout} ms: ${payload.gate}`)), timeout);
    });
    try { return await Promise.race([Promise.resolve().then(() => callback({ ...payload, signal: controller.signal })), aborted]); }
    finally { clearTimeout(timer); if (inFlight === controller) inFlight = undefined; }
  }
  function validateTerminals(result, payload) {
    const terminals = result?.terminals;
    if (!Array.isArray(terminals) || terminals.length !== payload.expectedRoles.length) fail('all expected roles must report terminal done');
    const roles = new Set();
    for (const terminal of terminals) {
      if (!payload.expectedRoles.includes(terminal.role) || roles.has(terminal.role) || terminal.status !== 'done'
        || !same(normalizedItems(terminal.testItems), state.testItems)) fail('missing, failed, duplicate or wrong-TM role terminal');
      roles.add(terminal.role);
    }
    return clone(terminals);
  }
  // Persisted "completed" is usable only together with its whole-batch terminal
  // and matching gate. Host guards additionally protect these evidence records.
  if (!same(normalizedItems(state.testItems), state.testItems) || !Array.isArray(state.sourceRoles)
    || state.sourceRoles.some((role) => !ROLE.test(role)) || new Set(state.sourceRoles).size !== state.sourceRoles.length
    || (state.stages.some((stage) => stage.stage === 'INPUT_SYNC') && !state.sourceRoles.length)) fail('invalid persisted batch identity');
  if (!['created', 'running', 'pausing', 'paused', 'interrupted', 'completed', 'blocked', 'cancelled'].includes(state.status)) fail('invalid persisted pipeline status');
  let unfinished = false;
  for (const stage of state.stages) {
    if (!['pending', 'dispatching', 'gate_pending', 'gating', 'completed', 'blocked', 'cancelled'].includes(stage.status)
      || stage.dispatchId !== `${runId}:${stage.stage}:1`) fail('invalid persisted stage identity');
    if (unfinished && stage.status !== 'pending') fail('persisted stages skip an unfinished gate');
    if (stage.status !== 'completed') unfinished = true;
    if (['gate_pending', 'gating', 'completed'].includes(stage.status)) validateTerminals({ terminals: stage.terminals }, request(stage));
    if (stage.status === 'completed' && (stage.gateResult?.status !== 'passed' || stage.gateResult.exitCode !== 0
      || stage.gateResult.gate !== registry.stages[stage.stage].gate)) fail('completed stage is missing passing gate evidence');
  }
  if (state.status === 'completed' && unfinished) fail('completed pipeline has unfinished stages');
  save();
  async function drive() {
    if (ACTIVE.has(root)) fail('run already active');
    ACTIVE.set(root, true);
    try {
      state.status = 'running'; state.reason = null; save();
      for (const stage of state.stages) {
        if (stage.status === 'completed') continue;
        if (state.status === 'cancelled') break;
        if (state.pauseRequested) { state.status = 'paused'; save(); break; }
        if (stage.status === 'blocked' || stage.status === 'cancelled') fail('failed stage requires a new explicit training run');
        if (stage.status === 'pending' || stage.status === 'dispatching') {
          const recovering = stage.status === 'dispatching';
          if (recovering && typeof recoverStage !== 'function') fail(`cannot recover in-flight dispatch ${stage.dispatchId} without receipt adapter`);
          stage.status = 'dispatching'; save();
          const payload = request(stage);
          const terminal = await operation(recovering ? recoverStage : dispatchStage, payload, dispatchTimeoutMs, recovering ? 'recover dispatch' : 'dispatch');
          if (state.status === 'cancelled') break;
          stage.terminals = validateTerminals(terminal, payload);
          stage.status = 'gate_pending'; save();
        }
        if (state.pauseRequested) { state.status = 'paused'; save(); break; }
        if (stage.status === 'gate_pending' || stage.status === 'gating') {
          stage.status = 'gating'; save();
          const payload = request(stage);
          const gate = await operation(runStageGate, payload, gateTimeoutMs, 'gate command');
          if (state.status === 'cancelled') break;
          stage.gateResult = clone(gate);
          if (gate?.status !== 'passed' || gate.exitCode !== 0 || gate.gate !== payload.gate) fail(`gate failed: ${payload.gate}`);
          stage.status = 'completed'; save();
        }
      }
      if (state.status === 'running' || state.status === 'pausing') {
        state.status = state.stages.every((stage) => stage.status === 'completed') ? 'completed'
          : state.pauseRequested ? 'paused' : 'blocked';
        save();
      }
    } catch (error) {
      if (state.status !== 'cancelled') {
        const stage = state.stages.find((item) => item.status !== 'completed');
        if (stage) stage.status = 'blocked';
        state.status = 'blocked'; state.reason = error.message; save();
      }
    } finally { ACTIVE.delete(root); }
    return clone(state);
  }
  const controller = {
    getState: () => clone(state),
    start() {
      if (activePromise) return activePromise;
      if (TERMINAL.has(state.status)) return Promise.resolve(clone(state));
      if (state.status === 'paused' || state.pauseRequested) fail('pipeline is paused; use resume');
      activePromise = drive().finally(() => { activePromise = undefined; });
      return activePromise;
    },
    pause() {
      if (TERMINAL.has(state.status)) return clone(state);
      state.pauseRequested = true; state.status = activePromise ? 'pausing' : 'paused'; save();
      return clone(state);
    },
    resume() {
      if (activePromise) fail('wait for the in-flight operation to drain before resuming');
      if (TERMINAL.has(state.status)) return Promise.resolve(clone(state));
      state.pauseRequested = false; state.status = 'created'; save();
      return controller.start();
    },
    cancel(reason = 'cancelled by user') {
      if (TERMINAL.has(state.status)) return clone(state);
      state.status = 'cancelled'; state.reason = String(reason);
      const stage = state.stages.find((item) => item.status !== 'completed');
      if (stage) stage.status = 'cancelled';
      save(); inFlight?.abort(new Error(state.reason));
      return clone(state);
    },
  };
  return controller;
}
