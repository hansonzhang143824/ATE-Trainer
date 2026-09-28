import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { createSimpleOrchestration } from './simple-orchestration.js';

const PROFILE_IDS = Object.freeze({
  'dft-expert': 'ptc-dft-expert',
  'schematic-expert': 'ptc-schematic-expert',
  'test-strategy-architect': 'strategy-expert',
  'test-method-expert': 'method-expert',
  'rule-reviewer': 'rule-reviewer',
  'ate-implementer': 'ate-implementer',
  'compile-diagnostician': 'compile-diagnostician',
  'evolution-expert': 'evolution-expert',
});
const ARITHMETIC_ROLES = Object.freeze(Object.keys(PROFILE_IDS));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));

function inputBindings(workspaceRoot, input) {
  const pilot = input?.pilot === true;
  const roles = pilot ? ARITHMETIC_ROLES.slice(0, 2) : ARITHMETIC_ROLES;
  if (!input?.profileRunIds || typeof input.profileRunIds !== 'object'
      || Array.isArray(input.profileRunIds)
      || Object.keys(input.profileRunIds).sort().join('|')
        !== roles.map(role => PROFILE_IDS[role]).sort().join('|')) {
    throw new Error(pilot ? 'two completed INPUT_SYNC arithmetic expert run IDs are required'
      : 'eight completed arithmetic expert run IDs are required');
  }
  const ids = Object.fromEntries(roles.map(role => [role, input.profileRunIds[PROFILE_IDS[role]]]));
  if (new Set(Object.values(ids)).size !== Object.keys(ids).length) throw new Error('source training runs must be distinct');
  return Object.fromEntries(Object.entries(ids).map(([role, runId]) => {
    if (typeof runId !== 'string' || !/^training-[a-z0-9-]+$/.test(runId)) {
      throw new Error(`invalid ${role} source run ID`);
    }
    const base = `Training_Materials/runs/${runId}`;
    const state = read(assertSafeRunPath(workspaceRoot, `${base}/state.json`));
    if (state.runId !== runId || state.status !== 'completed') throw new Error(`${role} source run is not completed`);
    const profileId = PROFILE_IDS[role];
    const manifestName = 'profile/snapshot.json';
    if (state.target?.kind !== 'profile' || state.target.profileId !== profileId
        || state.purpose !== 'smoke-training' || state.outcome?.mode !== 'SMOKE_ONLY'
        || state.outcome?.smokePassed !== true || state.outcome?.businessGatePassed !== false) {
      throw new Error(`${role} arithmetic source did not pass`);
    }
    const profileSnapshotPath = `${base}/${manifestName}`;
    const profileDigest = sha(fs.readFileSync(assertSafeRunPath(workspaceRoot, profileSnapshotPath)));
    return [role, { profileId, profileVersion: `draft-${runId}`, profileDigest, profileSnapshotPath }];
  }));
}

export function createSimpleOrchestrationManager(workspaceRoot, options = {}) {
  if (typeof options.executeSmokeRole !== 'function') throw new Error('real smoke role adapter required');
  const root = path.resolve(workspaceRoot);
  const controllers = new Map();
  return {
    start(input) {
      const runId = input?.runId;
      if (controllers.has(runId)) throw new Error('smoke orchestration is already active');
      const profileBindings = inputBindings(root, input);
      const controller = createSimpleOrchestration({ workspaceRoot: root, runId,
        testItems: input.testItems, sourceRoles: ['dft-expert', 'schematic-expert'], profileBindings,
        pilot: input.pilot === true,
        executeSmokeRole: options.executeSmokeRole,
        onState: options.onState });
      controllers.set(runId, controller);
      const completion = controller.start().finally(() => {
        if (['completed', 'blocked', 'cancelled'].includes(controller.getState().status)) controllers.delete(runId);
      });
      options.onBackground?.(completion);
      return { runId, status: 'running', mode: 'SMOKE_ONLY', completion };
    },
    control(runId, action) {
      const controller = controllers.get(runId);
      if (!controller) throw new Error('no live smoke orchestration; interrupted runs require receipt recovery');
      if (action === 'pause') return controller.pause();
      if (action === 'resume') {
        const completion = controller.resume().finally(() => {
          if (['completed', 'blocked', 'cancelled'].includes(controller.getState().status)) controllers.delete(runId);
        });
        options.onBackground?.(completion);
        return controller.getState();
      }
      if (action === 'stop') return controller.cancel('stopped from native training panel');
      throw new Error('unsupported smoke orchestration action');
    },
    shutdown() {
      for (const controller of controllers.values()) controller.cancel('plugin shutting down');
      controllers.clear();
    },
  };
}
