import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';

const ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const ROLE = /^[a-z][a-z0-9-]{1,63}$/;
const DIGEST = /^[a-f0-9]{64}$/;
const FINAL = new Set(['completed', 'blocked', 'cancelled']);
const ACTIVE = new Set();
const copy = value => structuredClone(value);
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
function fail(reason) { throw new Error(`simple orchestration: ${reason}`); }
function atomic(file, value) {
  const temporary = `${file}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
function items(value) {
  if (!Array.isArray(value) || !value.length || value.some(tm => typeof tm !== 'string' || !/^TM\d+$/.test(tm))
      || new Set(value).size !== value.length) fail('unique explicit testItems are required');
  return [...value].sort((a, b) => Number(a.slice(2)) - Number(b.slice(2)));
}
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
function binding(value, workspace) {
  if (!value || typeof value !== 'object' || !ROLE.test(value.profileId)
      || typeof value.profileVersion !== 'string'
      || !(/^(?:v[1-9]\d*|draft-[A-Za-z0-9][A-Za-z0-9._-]{0,127})$/.test(value.profileVersion))
      || !DIGEST.test(value.profileDigest)) fail('each role requires a versioned SHA-256 profile binding');
  if (value.profileVersion.startsWith('draft-')) {
    const draftRunId = value.profileVersion.slice('draft-'.length);
    const relative = 'profile/snapshot.json';
    const snapshotRelative = `Training_Materials/runs/${draftRunId}/${relative}`;
    if (value.profileSnapshotPath !== undefined
        && value.profileSnapshotPath.replaceAll('\\', '/') !== snapshotRelative) {
      fail('draft snapshot path differs from its fixed source-role address');
    }
    const snapshot = assertSafeRunPath(workspace, snapshotRelative);
    if (!fs.existsSync(snapshot) || !fs.statSync(snapshot).isFile()
        || hash(fs.readFileSync(snapshot)) !== value.profileDigest) {
      fail('draft profile digest does not bind the frozen candidate snapshot');
    }
    const manifest = read(snapshot);
    if (manifest.runId !== draftRunId) fail('draft profile snapshot run identity differs');
    if (manifest.profileId !== value.profileId || manifest.kind !== 'ptc-profile-smoke-snapshot') {
      fail('draft profile snapshot identity differs');
    }
    return { profileId: value.profileId, profileVersion: value.profileVersion,
      profileDigest: value.profileDigest, profileSnapshotPath: snapshotRelative };
  }
  return { profileId: value.profileId, profileVersion: value.profileVersion, profileDigest: value.profileDigest };
}
function stagesFrom(registry, sourceRoles, pilot = false) {
  const names = registry?.stateMachine;
  if (!Array.isArray(names) || names.length !== 8 || names.at(-1) !== 'COMPLETE'
      || new Set(names).size !== names.length || names[0] !== 'INPUT_SYNC' || names.at(-2) !== 'COMPILE') {
    fail('authoritative registry must contain the complete seven-stage chain');
  }
  if (!equal(sourceRoles, ['dft-expert', 'schematic-expert'])) {
    fail('INPUT_SYNC smoke order must be DFT then schematic statistic-only');
  }
  return (pilot ? names.slice(0, 1) : names.slice(0, -1)).map(stage => {
    const definition = registry.stages?.[stage];
    if (!ROLE.test(definition?.owner) || typeof definition.gate !== 'string'
        || !/^scripts\/[A-Za-z0-9_.-]+\.(py|js|mjs)$/.test(definition.gate)) fail(`invalid ${stage} registry definition`);
    return { stage, owner: definition.owner, gate: definition.gate,
      roles: stage === 'INPUT_SYNC' ? [...sourceRoles] : [definition.owner] };
  });
}
function verifyReceipt(root, runId, task, result, testItems) {
  const expectedKind = 'arithmetic-child';
  if (result?.status !== 'done' || result.executionKind !== expectedKind
      || result.businessGatePassed !== false
      || result.stage !== task.stage || result.role !== task.role
      || result.profileId !== task.profileId || result.profileVersion !== task.profileVersion
      || result.profileDigest !== task.profileDigest || !equal(items(result.testItems), testItems)
      || typeof result.childReceiptId !== 'string' || !ID.test(result.childReceiptId)
      || !DIGEST.test(result.childEvidenceSha256)
      || typeof result.childEvidencePath !== 'string') fail(`invalid real-child smoke receipt for ${task.stage}/${task.role}`);
  const file = assertSafeRunPath(root, result.childEvidencePath);
  if (!fs.statSync(file).isFile() || hash(fs.readFileSync(file)) !== result.childEvidenceSha256) {
    fail(`child evidence changed for ${task.stage}/${task.role}`);
  }
  const evidence = read(file);
  if (evidence.runId !== runId || evidence.dispatchId !== task.dispatchId
      || evidence.role !== task.role || evidence.stage !== task.stage
      || evidence.executionKind !== expectedKind || evidence.businessGatePassed !== false) {
    fail('child evidence does not belong to this exact dispatch');
  }
  let answer = null;
  let captainVerified = false;
  // Captain's host check is independent of a child saying it passed. No
  // coercion: {"answer":"3"}, {"answer":true} and invented PASS all fail.
  if (typeof evidence.childSessionId !== 'string' || !evidence.childSessionId
      || typeof evidence.answer !== 'number' || evidence.answer !== 3) fail(`arithmetic answer is not numeric 3 from a fresh child for ${task.role}`);
  answer = evidence.answer;
  captainVerified = true;
  return { status: 'completed', executionKind: expectedKind, answer, captainVerified,
    childSessionId: evidence.childSessionId,
    childReceiptId: result.childReceiptId, childEvidencePath: file, childEvidenceSha256: result.childEvidenceSha256 };
}

/**
 * SMOKE_ONLY chain. The caller injects an adapter that really launches a child
 * profile; this controller cannot synthesize a child or run a business gate.
 * Each child must leave a run-local evidence file and return its exact SHA-256.
 * An interrupted dispatch is recovered only through recoverSmokeRole, never
 * silently sent again. Every completed stage is smoke-only, not business-ready.
 */
export function createSimpleOrchestration({ workspaceRoot, runId, testItems, sourceRoles,
  profileBindings, executeSmokeRole, recoverSmokeRole, onState, pilot = false, childTimeoutMs = 8 * 60_000 }) {
  if (!ID.test(runId) || /[. ]$/.test(runId) || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])([.]|$)/i.test(runId)) fail('invalid runId');
  if (typeof executeSmokeRole !== 'function') fail('a real child dispatch adapter is required');
  if (!Number.isFinite(childTimeoutMs) || childTimeoutMs <= 0 || childTimeoutMs > 8 * 60_000) fail('child deadline exceeds contract');
  const workspace = path.resolve(workspaceRoot);
  const root = assertSafeRunPath(workspace, `Training_Materials/runs/${runId}`);
  if (ACTIVE.has(root)) fail('run already has a live smoke controller');
  const contextFile = assertSafeRunPath(workspace, path.join(root, 'run.json'));
  const stateFile = assertSafeRunPath(workspace, path.join(root, 'state.json'));
  const recordFile = assertSafeRunPath(workspace, path.join(root, 'simple-orchestration.json'));
  const registryFile = assertSafeRunPath(workspace, path.join(root, 'simple-orchestration-registry.json'));
  const contextBytes = fs.readFileSync(contextFile);
  const context = JSON.parse(contextBytes.toString('utf8').replace(/^\uFEFF/, ''));
  const runState = read(stateFile);
  if (context.mode !== 'training' || context.runId !== runId || context.projectId !== null
      || context.releaseId !== null || path.resolve(workspace, context.artifactRoot) !== root
      || runState.runId !== runId || runState.purpose !== 'smoke-training'
      || runState.target?.kind !== 'pipeline') fail('run is not an isolated smoke-training pipeline');
  if (runState.target.fromStage !== 'INPUT_SYNC'
      || runState.target.toStage !== (pilot ? 'INPUT_SYNC' : 'COMPILE')) fail('pilot/full run target mismatch');
  const canonicalRegistry = assertSafeRunPath(workspace, 'team/ptc/ptc_stage_registry.json');
  let record;
  if (fs.existsSync(recordFile)) {
    if (!fs.existsSync(registryFile)) fail('registry snapshot missing');
    const frozenBytes = fs.readFileSync(registryFile);
    record = read(recordFile);
    if (record.schemaVersion !== 1 || record.mode !== 'SMOKE_ONLY' || record.runId !== runId
        || record.contextDigest !== hash(contextBytes) || record.registryDigest !== hash(frozenBytes)
        || record.businessGatePassed !== false || !equal(record.testItems, items(record.testItems))) {
      fail('persisted smoke run binding changed');
    }
    if ((record.scope === 'INPUT_SYNC_PILOT') !== pilot) fail('persisted smoke scope changed');
    const expected = stagesFrom(JSON.parse(frozenBytes.toString('utf8')), record.sourceRoles, pilot);
    if (!equal(record.stages.map(s => ({ stage: s.stage, owner: s.owner, gate: s.gate, roles: s.tasks.map(t => t.role) })), expected)) {
      fail('persisted stage order or ownership changed');
    }
    if (testItems && !equal(items(testItems), record.testItems)) fail('testItems changed on resume');
    if (sourceRoles && !equal(sourceRoles, record.sourceRoles)) fail('sourceRoles changed on resume');
    if (profileBindings && !equal(Object.fromEntries(Object.keys(record.profileBindings)
      .map(role => [role, binding(profileBindings[role], workspace)])), record.profileBindings)) fail('profile versions changed on resume');
    if (!FINAL.has(record.status) && !['created', 'paused', 'interrupted'].includes(record.status)) {
      record.status = 'interrupted';
      record.reason = 'host interrupted; recover the in-flight child receipt before resuming';
    }
  } else {
    if (fs.existsSync(registryFile)) fail('orphan registry snapshot requires explicit recovery');
    const registryBytes = fs.readFileSync(canonicalRegistry);
    const definitions = stagesFrom(JSON.parse(registryBytes.toString('utf8')), sourceRoles, pilot);
    if (!equal(runState.target.stages, definitions.map(d => d.stage))
        || runState.target.fromStage !== 'INPUT_SYNC'
        || runState.target.toStage !== (pilot ? 'INPUT_SYNC' : 'COMPILE')) fail('run stage range differs from smoke scope');
    const roles = new Set([...definitions.flatMap(def => def.roles), ...(pilot ? [] : ['evolution-expert'])]);
    if (!profileBindings || [...roles].some(role => !profileBindings[role])) fail('all dispatched roles need profile bindings');
    const normalizedBindings = Object.fromEntries([...roles].map(role => [role, binding(profileBindings[role], workspace)]));
    fs.writeFileSync(registryFile, registryBytes, { flag: 'wx' });
    record = { schemaVersion: 1, runId, mode: 'SMOKE_ONLY', scope: pilot ? 'INPUT_SYNC_PILOT' : 'FULL_CHAIN', status: 'created', reason: null,
      contextDigest: hash(contextBytes), registryDigest: hash(registryBytes), testItems: items(testItems),
      sourceRoles: [...sourceRoles], profileBindings: normalizedBindings, smokePassed: false,
      businessGatePassed: false, pauseRequested: false, createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(), auxiliaryTasks: pilot ? [] : [{ stage: 'SMOKE_AUXILIARY', role: 'evolution-expert',
        ...normalizedBindings['evolution-expert'], status: 'pending',
        dispatchId: `${runId}:SMOKE_AUXILIARY:evolution-expert:1`, provisional: false,
        executionKind: null, answer: null, captainVerified: false, childSessionId: null,
        childReceiptId: null, childEvidencePath: null, childEvidenceSha256: null }],
      stages: definitions.map(def => ({
        stage: def.stage, owner: def.owner, gate: def.gate, status: 'pending', smokePassed: false,
        businessGatePassed: false, businessGateResult: null,
        tasks: def.roles.map(role => ({ stage: def.stage, role, ...normalizedBindings[role],
          status: 'pending', dispatchId: `${runId}:${def.stage}:${role}:1`,
          provisional: false,
          executionKind: null, answer: null, captainVerified: false, childSessionId: null,
          childReceiptId: null, childEvidencePath: null, childEvidenceSha256: null })) })) };
  }
  let expectedDigest = fs.existsSync(recordFile) ? hash(fs.readFileSync(recordFile)) : null;
  let activePromise;
  let inFlight;
  function save() {
    const currentDigest = fs.existsSync(recordFile) ? hash(fs.readFileSync(recordFile)) : null;
    if (expectedDigest !== currentDigest) fail('progress changed under this controller');
    record.updatedAt = new Date().toISOString();
    atomic(recordFile, record);
    expectedDigest = hash(fs.readFileSync(recordFile));
    const display = read(stateFile);
    if (display.runId !== runId || display.purpose !== 'smoke-training') fail('run state changed identity');
    atomic(stateFile, { ...display, status: record.status, updatedAt: record.updatedAt,
      outcome: { mode: 'SMOKE_ONLY', smokePassed: record.smokePassed, businessGatePassed: false,
        reason: record.reason, stage: record.stages.find(stage => stage.status !== 'completed')?.stage ?? null },
      finishedAt: FINAL.has(record.status) ? record.updatedAt : null });
    try { onState?.(copy(record)); } catch { /* Observer cannot change a child result. */ }
  }
  let unfinished = false;
  const seenChildSessions = new Set();
  for (const stage of record.stages) {
    if (!['pending', 'running', 'completed', 'blocked', 'cancelled'].includes(stage.status)
        || stage.businessGatePassed !== false || stage.businessGateResult !== null) fail('invalid persisted stage status');
    if (unfinished && stage.status === 'completed') fail('stages skip an unfinished predecessor');
    if (stage.status !== 'completed') unfinished = true;
    let taskUnfinished = false;
    for (const task of stage.tasks) {
      if (task.dispatchId !== `${runId}:${stage.stage}:${task.role}:1`
          || !equal(binding(task, workspace), record.profileBindings[task.role])
          || !['pending', 'dispatching', 'completed', 'blocked', 'cancelled'].includes(task.status)
          || (taskUnfinished && task.status === 'completed')) fail('invalid persisted child identity/order');
      if (task.status !== 'completed') taskUnfinished = true;
      if (task.status === 'completed') {
        const checked = verifyReceipt(root, runId, task, { ...task,
        status: 'done', testItems: record.testItems,
        businessGatePassed: false }, record.testItems);
        if (checked.childSessionId !== task.childSessionId) fail('persisted child session changed');
        if (checked.childSessionId) {
          if (seenChildSessions.has(checked.childSessionId)) fail('child session was reused across tasks');
          seenChildSessions.add(checked.childSessionId);
        }
      }
    }
    if (stage.status === 'completed' && (taskUnfinished || stage.smokePassed !== true)) fail('completed stage lacks smoke receipts');
  }
  if (!Array.isArray(record.auxiliaryTasks) || record.auxiliaryTasks.length !== (pilot ? 0 : 1)
      || (!pilot && (record.auxiliaryTasks[0].role !== 'evolution-expert'
      || !equal(binding(record.auxiliaryTasks[0], workspace), record.profileBindings['evolution-expert'])))) fail('invalid evolution auxiliary binding');
  const auxiliary = record.auxiliaryTasks[0];
  if (auxiliary && (auxiliary.dispatchId !== `${runId}:SMOKE_AUXILIARY:evolution-expert:1`
      || !['pending', 'dispatching', 'completed', 'blocked', 'cancelled'].includes(auxiliary.status))) {
    fail('invalid auxiliary dispatch identity');
  }
  if (auxiliary?.status === 'completed') {
    const checked = verifyReceipt(root, runId, auxiliary, { ...auxiliary,
      status: 'done', businessGatePassed: false, testItems: record.testItems }, record.testItems);
    if (checked.childSessionId !== auxiliary.childSessionId || seenChildSessions.has(checked.childSessionId)) {
      fail('auxiliary child session changed or reused');
    }
    seenChildSessions.add(checked.childSessionId);
  }
  if (record.status === 'completed' && (unfinished || (auxiliary && auxiliary.status !== 'completed') || record.smokePassed !== true)) {
    fail('completed chain lacks all smoke receipts');
  }
  if (!['created', 'running', 'pausing', 'paused', 'interrupted', 'completed', 'blocked', 'cancelled'].includes(record.status)) fail('invalid persisted run status');
  save();
  function payload(stage, task) {
    return { runId, mode: 'SMOKE_ONLY', stage: stage.stage, owner: stage.owner, registryGate: stage.gate,
      role: task.role, profileId: task.profileId, profileVersion: task.profileVersion,
      profileDigest: task.profileDigest, profileSnapshotPath: task.profileSnapshotPath ?? null,
      testItems: [...record.testItems], dispatchId: task.dispatchId,
      runRoot: root, registryDigest: record.registryDigest,
      instruction: '1+2等于几，把答案写在JSON里',
      provisional: task.provisional };
  }
  async function call(adapter, request) {
    const controller = new AbortController();
    inFlight = controller;
    let timer;
    const aborted = new Promise((resolve, reject) => {
      controller.signal.addEventListener('abort', () => reject(controller.signal.reason ?? new Error('cancelled')), { once: true });
      timer = setTimeout(() => controller.abort(new Error(`child deadline exceeded: ${request.stage}/${request.role}`)), childTimeoutMs);
    });
    try { return await Promise.race([Promise.resolve().then(() => adapter({ ...request, signal: controller.signal })), aborted]); }
    finally { clearTimeout(timer); if (inFlight === controller) inFlight = undefined; }
  }
  async function drive() {
    if (ACTIVE.has(root)) fail('run already has a live smoke controller');
    ACTIVE.add(root);
    try {
      record.status = 'running'; record.reason = null; save();
      for (const stage of record.stages) {
        if (stage.status === 'completed') continue;
        if (record.status === 'cancelled') break;
        if (record.pauseRequested) { record.status = 'paused'; save(); break; }
        stage.status = 'running'; save();
        for (const task of stage.tasks) {
          if (task.status === 'completed') continue;
          if (record.status === 'cancelled') break;
          if (record.pauseRequested) { record.status = 'paused'; save(); break; }
          const recovering = task.status === 'dispatching';
          if (recovering && typeof recoverSmokeRole !== 'function') fail(`unknown in-flight child ${task.dispatchId}; receipt recovery required`);
          if (task.status === 'blocked' || task.status === 'cancelled') fail('failed child requires a new training run');
          task.status = 'dispatching'; save();
          const result = await call(recovering ? recoverSmokeRole : executeSmokeRole, payload(stage, task));
          if (record.status === 'cancelled') break;
          const checked = verifyReceipt(root, runId, task, result, record.testItems);
          if (checked.childSessionId && seenChildSessions.has(checked.childSessionId)) fail('child session was reused across tasks');
          if (checked.childSessionId) seenChildSessions.add(checked.childSessionId);
          Object.assign(task, checked);
          save();
        }
        if (record.status === 'cancelled' || record.status === 'paused') break;
        if (stage.tasks.every(task => task.status === 'completed')) {
          stage.status = 'completed'; stage.smokePassed = true; save();
        }
      }
      if (auxiliary && record.status !== 'cancelled' && record.status !== 'paused' && record.stages.every(stage => stage.status === 'completed')) {
        const task = record.auxiliaryTasks[0];
        if (task.status !== 'completed') {
          if (record.pauseRequested) { record.status = 'paused'; save(); }
          else {
            const recovering = task.status === 'dispatching';
            if (recovering && typeof recoverSmokeRole !== 'function') fail(`unknown in-flight child ${task.dispatchId}; receipt recovery required`);
            task.status = 'dispatching'; save();
            const result = await call(recovering ? recoverSmokeRole : executeSmokeRole,
              payload({ stage: 'SMOKE_AUXILIARY', owner: null, gate: null }, task));
            if (record.status !== 'cancelled') {
              const checked = verifyReceipt(root, runId, task, result, record.testItems);
              if (seenChildSessions.has(checked.childSessionId)) fail('child session was reused across tasks');
              seenChildSessions.add(checked.childSessionId);
              Object.assign(task, checked); save();
            }
          }
        }
      }
      if (record.status === 'running' || record.status === 'pausing') {
        record.smokePassed = record.stages.every(stage => stage.status === 'completed')
          && record.auxiliaryTasks.every(task => task.status === 'completed');
        record.status = record.smokePassed ? 'completed' : record.pauseRequested ? 'paused' : 'blocked';
        save();
      }
    } catch (error) {
      if (record.status !== 'cancelled') {
        const stage = record.stages.find(item => item.status !== 'completed');
        if (stage) { stage.status = 'blocked'; const task = stage.tasks.find(item => item.status !== 'completed'); if (task) task.status = 'blocked'; }
        else { const task = record.auxiliaryTasks.find(item => item.status !== 'completed'); if (task) task.status = 'blocked'; }
        record.status = 'blocked'; record.reason = error.message; save();
      }
    } finally { ACTIVE.delete(root); }
    return copy(record);
  }
  const controller = {
    getState: () => copy(record),
    start() {
      if (activePromise) return activePromise;
      if (FINAL.has(record.status)) return Promise.resolve(copy(record));
      if (record.status === 'paused' || record.pauseRequested) fail('paused chain requires resume');
      activePromise = drive().finally(() => { activePromise = undefined; });
      return activePromise;
    },
    pause() {
      if (FINAL.has(record.status)) return copy(record);
      record.pauseRequested = true;
      record.status = activePromise ? 'pausing' : 'paused'; save();
      return copy(record);
    },
    resume() {
      if (activePromise) fail('wait for the in-flight child to drain');
      if (FINAL.has(record.status)) return Promise.resolve(copy(record));
      record.pauseRequested = false; record.status = 'created'; save();
      return controller.start();
    },
    cancel(reason = 'stopped by user') {
      if (FINAL.has(record.status)) return copy(record);
      record.status = 'cancelled'; record.reason = String(reason);
      const stage = record.stages.find(item => item.status !== 'completed');
      if (stage) { stage.status = 'cancelled'; const task = stage.tasks.find(item => item.status !== 'completed'); if (task) task.status = 'cancelled'; }
      else { const task = record.auxiliaryTasks.find(item => item.status !== 'completed'); if (task) task.status = 'cancelled'; }
      save(); inFlight?.abort(new Error(record.reason));
      return copy(record);
    },
  };
  return controller;
}
