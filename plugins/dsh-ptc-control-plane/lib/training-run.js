import { randomUUID } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { assertSafeRunPath, createRunContext, persistRunContext } from './run-context.js';
import { resolveAgentProfile } from './agent-profile-runtime.js';

const PROFILE_ID = /^[a-z][a-z0-9-]{1,63}$/;

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
  } catch {
    return undefined;
  }
}

function stamp(date) {
  return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z').toLowerCase();
}

function writeExclusiveJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
}

function normalizeAgentBindings(workspaceRoot, target) {
  if (target?.agentBindings === undefined) return undefined;
  if (!target.agentBindings || typeof target.agentBindings !== 'object' || Array.isArray(target.agentBindings)) {
    throw new Error('pipeline agentBindings must be an object');
  }
  const allowedRoles = new Set(['schematic-expert', 'dft-expert']);
  const bindings = {};
  for (const [role, value] of Object.entries(target.agentBindings)) {
    if (!allowedRoles.has(role) || !value || typeof value !== 'object' || Array.isArray(value)
        || typeof value.profileId !== 'string' || !PROFILE_ID.test(value.profileId)) {
      throw new Error(`invalid pipeline Agent binding for ${role}`);
    }
    const profile = resolveAgentProfile(workspaceRoot, value.profileId,
      value.profileRevision ? { revisionId: value.profileRevision } : {});
    if (profile.ownerRole !== role) throw new Error(`profile ${value.profileId} ownerRole must be ${role}`);
    if (role === 'dft-expert' && profile.executionClass !== 'input-dft') {
      throw new Error(`profile ${value.profileId} is not configured for input-dft execution`);
    }
    bindings[role] = { profileId: value.profileId, profileRevision: profile.profileRevision };
  }
  return Object.freeze(bindings);
}

function normalizeTarget(workspaceRoot, target) {
  if (target?.kind === 'profile') {
    if (typeof target.profileId !== 'string' || !PROFILE_ID.test(target.profileId)) {
      throw new Error('profile training requires a valid profileId');
    }
    const resolved = resolveAgentProfile(workspaceRoot, target.profileId,
      target.profileRevision ? { revisionId: target.profileRevision } : {});
    const normalized = { kind: 'profile', profileId: target.profileId };
    // Legacy built-in profiles predate generated manifests. Preserve their
    // historical state shape, while dynamic/cloned profiles bind a concrete
    // revision and content digest into the immutable training identity.
    if (resolved.manifestPath || target.profileRevision) {
      normalized.profileRevision = resolved.profileRevision;
      normalized.profileDigest = resolved.contentDigest;
    }
    return Object.freeze(normalized);
  }
  if (target?.kind === 'pipeline') {
    const registry = readJson(assertSafeRunPath(workspaceRoot, path.join(workspaceRoot, 'team', 'ptc', 'ptc_stage_registry.json')));
    const stages = Array.isArray(registry?.stateMachine)
      ? registry.stateMachine.filter((stage) => stage !== 'COMPLETE')
      : [];
    if (stages.length === 0) throw new Error('stage registry is missing or invalid');
    const fromStage = target.fromStage ?? stages[0];
    const toStage = target.toStage ?? stages[stages.length - 1];
    const from = stages.indexOf(fromStage);
    const to = stages.indexOf(toStage);
    if (from === -1 || to === -1 || from > to) {
      throw new Error('pipeline training requires an ordered stage range');
    }
    const normalized = { kind: 'pipeline', fromStage, toStage, stages: stages.slice(from, to + 1) };
    const agentBindings = normalizeAgentBindings(workspaceRoot, target);
    if (agentBindings) normalized.agentBindings = agentBindings;
    if (target.workflowId !== undefined || target.workflowRevision !== undefined) {
      if (typeof target.workflowId !== 'string' || !/^[a-z][a-z0-9-]{1,63}$/.test(target.workflowId)
          || typeof target.workflowRevision !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(target.workflowRevision)) {
        throw new Error('pipeline workflow binding requires workflowId and workflowRevision');
      }
      if (!agentBindings?.['schematic-expert'] || !agentBindings?.['dft-expert']) {
        throw new Error('workflow binding requires schematic-expert and dft-expert Agent bindings');
      }
      normalized.workflowBinding = {
        workflowId: target.workflowId,
        workflowRevision: target.workflowRevision,
        steps: [
          { order: 1, role: 'schematic-expert', profileId: agentBindings['schematic-expert'].profileId, profileRevision: agentBindings['schematic-expert'].profileRevision },
          { order: 2, role: 'dft-expert', profileId: agentBindings['dft-expert'].profileId, profileRevision: agentBindings['dft-expert'].profileRevision },
        ],
        handoff: 'schematic-output-to-dft-input',
      };
    }
    return Object.freeze(normalized);
  }
  throw new Error('target.kind must be profile or pipeline');
}

export function createTrainingRun(workspaceRoot, input, options = {}) {
  const root = path.resolve(workspaceRoot);
  const now = options.now instanceof Date ? options.now : new Date();
  const suffix = typeof options.suffix === 'string' ? options.suffix : randomUUID().slice(0, 8);
  const runId = input?.runId ?? `training-${stamp(now)}-${suffix}`;
  const target = normalizeTarget(root, input?.target);
  const purpose = input?.purpose ?? 'business-training';
  if (!['business-training', 'framework-rehearsal', 'schematic-statistic-only', 'smoke-training'].includes(purpose)) {
    throw new Error('unsupported training purpose');
  }
  if (purpose === 'schematic-statistic-only' && (target.kind !== 'pipeline'
      || target.fromStage !== 'INPUT_SYNC' || target.toStage !== 'INPUT_SYNC')) {
    throw new Error('statistic-only training requires the isolated INPUT_SYNC target');
  }
  if (purpose === 'framework-rehearsal' && (target.kind !== 'pipeline'
      || target.fromStage !== 'INPUT_SYNC' || target.toStage !== 'COMPILE')) {
    throw new Error('framework rehearsal requires the complete INPUT_SYNC to COMPILE pipeline');
  }
  if (purpose === 'smoke-training' && target.kind === 'pipeline'
      && (target.fromStage !== 'INPUT_SYNC' || !['INPUT_SYNC', 'COMPILE'].includes(target.toStage))) {
    throw new Error('smoke orchestration requires INPUT_SYNC pilot or the complete INPUT_SYNC to COMPILE pipeline');
  }
  const context = createRunContext(root, { mode: 'training', runId, createdAt: now.toISOString() });
  const directory = assertSafeRunPath(root, context.artifactRoot);
  fs.mkdirSync(path.dirname(directory), { recursive: true });
  // The directory itself reserves identity, including interrupted preparations.
  // Never adopt or reset an existing run, even when its run.json is identical.
  try { fs.mkdirSync(directory); } catch (error) {
    throw new Error(`could not create training run; directory already exists or is unavailable: ${error.message}`);
  }
  const runFile = persistRunContext(root, context);
  const state = {
    schemaVersion: 1,
    runId,
    status: 'created',
    target,
    purpose,
    createdAt: now.toISOString(),
    updatedAt: now.toISOString(),
  };
  const stateFile = path.join(path.dirname(runFile), 'state.json');
  try {
    assertSafeRunPath(root, stateFile);
    writeExclusiveJson(stateFile, state);
  } catch (error) {
    throw new Error(`could not create training run state: ${error?.message ?? error}`);
  }
  return { context, state, runFile, stateFile };
}
