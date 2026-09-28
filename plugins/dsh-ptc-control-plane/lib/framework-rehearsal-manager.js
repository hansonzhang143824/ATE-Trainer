import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { trainingAddressBook } from './training-paths.js';
import { createTrainingPipeline } from './training-pipeline.js';
import { preflightFrameworkRehearsalSources, assertFrameworkSourcesUnchanged } from './framework-rehearsal-source.js';
import { openFrameworkRehearsalSnapshot, verifyFrameworkStage } from './framework-rehearsal.js';

const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const terminal = status => ['completed', 'blocked', 'cancelled'].includes(status);

function write(root, file, value) {
  assertSafeRunPath(root, file);
  const temp = `${file}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(temp, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  try { fs.renameSync(temp, file); }
  finally { if (fs.existsSync(temp)) fs.unlinkSync(temp); }
}

function itemsOf(value) {
  if (!Array.isArray(value) || !value.length || value.some(tm => typeof tm !== 'string' || !/^TM\d+$/.test(tm))
      || new Set(value).size !== value.length) throw new Error('framework rehearsal requires unique explicit TM identifiers');
  return [...value].sort((a, b) => Number(a.slice(2)) - Number(b.slice(2)));
}

/**
 * Runs a separately labeled, host-only framework rehearsal through the real
 * persisted stage engine. Its adapters are independent of business experts and
 * business gates; `completed` is granted only after full-chain verification.
 */
export function createFrameworkRehearsalManager(workspaceRoot, adapters, options = {}) {
  const root = path.resolve(workspaceRoot);
  for (const name of ['snapshot', 'executeStage', 'verifyStage', 'recoverStage', 'verifyChain']) {
    if (typeof adapters?.[name] !== 'function') throw new Error(`framework rehearsal adapter missing ${name}`);
  }
  const active = new Map();
  const preflight = options.preflight ?? preflightFrameworkRehearsalSources;
  const engine = options.createEngine ?? createTrainingPipeline;

  function locate(runId) {
    const directory = assertSafeRunPath(root, trainingAddressBook(runId).runRoot);
    const context = read(assertSafeRunPath(root, path.join(directory, 'run.json')));
    const stateFile = assertSafeRunPath(root, path.join(directory, 'state.json'));
    const state = read(stateFile);
    if (context.runId !== runId || context.mode !== 'training' || context.releaseId !== null
        || context.projectId !== null || path.resolve(root, context.artifactRoot) !== directory
        || state.runId !== runId || state.purpose !== 'framework-rehearsal'
        || state.target?.kind !== 'pipeline' || state.target.fromStage !== 'INPUT_SYNC'
        || state.target.toStage !== 'COMPILE') {
      throw new Error('run is not an isolated full-chain framework rehearsal');
    }
    return { runId, directory, stateFile, state };
  }

  function update(record, status, reason = null, commandEvidence = null) {
    const now = new Date().toISOString();
    record.state = { ...record.state, status, updatedAt: now,
      outcome: { mode: 'FRAMEWORK_REHEARSAL', reason,
        result: status === 'completed' ? '流程演练通过' : null,
        realBusinessGatesPassed: false,
        ...(commandEvidence ? { commandEvidence,
          terminationConfirmed: commandEvidence.terminationConfirmed === true } : {}) },
      ...(terminal(status) ? { finishedAt: now } : {}) };
    write(root, record.stateFile, record.state);
  }

  function cleanup(record) {
    if (!terminal(record.state.status)) return;
    active.delete(record.runId);
    if (record.state.outcome?.terminationConfirmed === false) return;
    try { fs.unlinkSync(record.lock); } catch {}
  }

  function reserveRecoveryLock(record) {
    const lock = assertSafeRunPath(root, path.join(record.directory, 'framework-rehearsal.lock'));
    if (fs.existsSync(lock)) {
      const pid = Number(fs.readFileSync(lock, 'utf8').trim());
      if (!Number.isSafeInteger(pid) || pid <= 0) throw new Error('rehearsal lock has no trustworthy process identity');
      try { process.kill(pid, 0); throw new Error(`rehearsal process ${pid} may still be active; recovery denied`); }
      catch (error) {
        if (error.code !== 'ESRCH') throw error;
      }
      const preserved = assertSafeRunPath(root, path.join(record.directory,
        `framework-rehearsal.stale-${pid}-${Date.now()}.lock`));
      fs.renameSync(lock, preserved);
    }
    fs.writeFileSync(lock, `${process.pid}\n`, { flag: 'wx' });
    record.lock = lock;
  }

  async function finish(record, progress) {
    if (record.cancelled || record.state.status === 'cancelled') {
      cleanup(record);
      return record.state;
    }
    if (progress.status === 'completed') {
      update(record, 'verifying', 'checking complete framework hash chain');
      try {
        const verdict = await adapters.verifyChain({ workspaceRoot: root, runId: record.runId,
          testItems: record.testItems, snapshot: record.snapshot, signal: record.abort.signal });
        if (record.cancelled) { cleanup(record); return record.state; }
        if (verdict?.status !== 'passed') throw new Error(verdict?.reason ?? 'full rehearsal chain did not pass');
        update(record, 'completed');
      } catch (error) { if (!record.cancelled) update(record, 'blocked', error.message); }
    } else if (progress.status === 'paused') update(record, 'paused', progress.reason ?? null);
    else if (progress.status === 'blocked') update(record, 'blocked', progress.reason ?? 'stage rehearsal blocked');
    else if (progress.status === 'cancelled') update(record, 'cancelled', progress.reason ?? 'rehearsal stopped');
    cleanup(record);
    return record.state;
  }

  function observe(record, promise) {
    const completion = Promise.resolve(promise).then(progress => finish(record, progress))
      .catch(error => {
        if (!record.cancelled) update(record, 'blocked', error.message, error.commandEvidence);
        cleanup(record);
        return record.state;
      });
    record.completion = completion;
    options.onBackground?.(completion);
    return completion;
  }

  return {
    start(input) {
      const record = locate(input?.runId);
      const testItems = itemsOf(input?.testItems);
      if (record.state.status !== 'created' || active.has(record.runId)) throw new Error('framework rehearsal already started');
      record.testItems = testItems;
      record.lock = assertSafeRunPath(root, path.join(record.directory, 'framework-rehearsal.lock'));
      fs.writeFileSync(record.lock, `${process.pid}\n`, { flag: 'wx' });
      record.abort = new AbortController();
      record.cancelled = false;
      record.pauseRequested = false;
      record.controller = null;
      active.set(record.runId, record);
      record.state = { ...record.state, testItems };
      update(record, 'preparing', 'validating and freezing source products');
      const preparation = (async () => {
        try {
          const source = await preflight(root, testItems, { signal: record.abort.signal });
          if (record.cancelled) { cleanup(record); return record.state; }
          const snapshot = await adapters.snapshot({ workspaceRoot: root, runId: record.runId,
            runDirectory: record.directory, testItems, source, signal: record.abort.signal });
          if (record.cancelled) { cleanup(record); return record.state; }
          assertFrameworkSourcesUnchanged(root, source);
          const postflight = await preflight(root, testItems, { signal: record.abort.signal });
          if (record.cancelled) { cleanup(record); return record.state; }
          const identity = value => JSON.stringify({
            schematic: { source: value.schematic.canonicalInput, files: value.schematic.fileHashes },
            dft: value.dft.map(item => ({ tm: item.tm, source: item.canonicalInput, files: item.fileHashes })),
          });
          if (identity(source) !== identity(postflight)) {
            throw new Error('framework source changed between preflight and private snapshot');
          }
          record.snapshot = snapshot;
          record.state = { ...record.state, snapshotBinding: {
            manifestSha256: snapshot.manifestSha256, registrySha256: snapshot.registrySha256 } };
          update(record, 'prepared', 'source snapshot and canonical inputs rebound');
          record.controller = engine({ workspaceRoot: root, runId: record.runId, testItems,
            sourceRoles: ['dft-expert', 'schematic-expert'],
            dispatchStage: request => adapters.executeStage(request, snapshot),
            recoverStage: request => adapters.recoverStage(request, snapshot),
            runStageGate: request => adapters.verifyStage(request, snapshot),
            onState: progress => {
              if (record.cancelled) return;
              update(record, progress.status === 'completed' ? 'verifying' : progress.status, progress.reason ?? null);
            },
            dispatchTimeoutMs: 30_000, gateTimeoutMs: 30_000 });
          if (record.pauseRequested) record.controller.pause();
          const progress = record.pauseRequested ? record.controller.getState() : await record.controller.start();
          return finish(record, progress);
        } catch (error) {
          if (!record.cancelled) update(record, 'blocked', error.message, error.commandEvidence);
          else if (error.commandEvidence) update(record, 'cancelled', error.message, error.commandEvidence);
          cleanup(record);
          return record.state;
        }
      })();
      record.completion = preparation;
      options.onBackground?.(preparation);
      return { runId: record.runId, status: record.state.status, outcome: record.state.outcome, completion: preparation };
    },
    control(runId, action) {
      trainingAddressBook(runId);
      if (!['pause', 'resume', 'stop'].includes(action)) throw new Error('unsupported framework rehearsal action');
      const record = active.get(runId);
      if (!record) throw new Error('framework rehearsal has no live controller; interrupted runs need receipt review');
      if (terminal(record.state.status)) throw new Error('framework rehearsal is already terminal');
      if (action === 'pause') {
        record.pauseRequested = true;
        if (record.controller) record.controller.pause();
        else update(record, 'pausing', 'waiting for source preflight to finish');
      } else if (action === 'stop') {
        const idle = record.state.status === 'paused';
        record.cancelled = true;
        record.abort.abort(new Error('user stopped framework rehearsal'));
        if (record.controller) record.controller.cancel('user stopped framework rehearsal');
        update(record, 'cancelled', 'user stopped framework rehearsal');
        if (idle) cleanup(record);
      } else {
        if (record.state.status !== 'paused' || !record.controller) throw new Error('rehearsal must be paused before resume');
        record.pauseRequested = false;
        observe(record, record.controller.resume());
      }
      return { runId, status: record.state.status, outcome: record.state.outcome, terminationConfirmed: false };
    },
    recover(runId) {
      const record = locate(runId);
      if (active.has(runId) || !['interrupted', 'paused'].includes(record.state.status)) {
        throw new Error('only an inactive interrupted or paused rehearsal may be explicitly recovered');
      }
      const progressFile = assertSafeRunPath(root, path.join(record.directory, 'pipeline-progress.json'));
      if (!fs.existsSync(progressFile)) throw new Error('no persisted stage progress; create a new rehearsal run');
      const progress = read(progressFile);
      const testItems = itemsOf(record.state.testItems);
      if (progress.runId !== runId || JSON.stringify(progress.testItems) !== JSON.stringify(testItems)
          || !Array.isArray(progress.stages) || progress.stages.length !== 7) {
        throw new Error('recovery stage progress differs from run identity');
      }
      const snapshot = openFrameworkRehearsalSnapshot(root, runId);
      if (progress.registryDigest !== snapshot.registrySha256) throw new Error('recovery registry digest differs');
      reserveRecoveryLock(record);
      record.testItems = testItems;
      record.snapshot = snapshot;
      record.abort = new AbortController();
      record.cancelled = false;
      record.pauseRequested = false;
      active.set(runId, record);
      update(record, 'recovering', 'verifying persisted stage receipts before explicit resume');
      const recovery = (async () => {
        try {
          const registry = read(assertSafeRunPath(root, path.join(record.directory, 'pipeline-registry.json')));
          for (const stage of progress.stages.filter(item => item.status === 'completed')) {
            const definition = registry.stages?.[stage.stage];
            if (!definition) throw new Error(`recovery stage definition missing: ${stage.stage}`);
            await verifyFrameworkStage({ runId, mode: 'training', stage: stage.stage,
              owner: definition.owner, gate: definition.gate, registryDigest: snapshot.registrySha256,
              testItems, expectedRoles: stage.stage === 'INPUT_SYNC'
                ? ['dft-expert', 'schematic-expert'] : [definition.owner],
              addressBook: { runRoot: record.directory } }, snapshot);
          }
          if (progress.status === 'completed') {
            return finish(record, progress);
          }
          record.controller = engine({ workspaceRoot: root, runId, testItems,
            sourceRoles: ['dft-expert', 'schematic-expert'],
            dispatchStage: request => adapters.executeStage(request, snapshot),
            recoverStage: request => adapters.recoverStage(request, snapshot),
            runStageGate: request => adapters.verifyStage(request, snapshot),
            onState: next => {
              if (!record.cancelled) update(record, next.status === 'completed' ? 'verifying' : next.status, next.reason ?? null);
            }, dispatchTimeoutMs: 30_000, gateTimeoutMs: 30_000 });
          return finish(record, await record.controller.resume());
        } catch (error) {
          if (!record.cancelled) update(record, 'blocked', error.message, error.commandEvidence);
          cleanup(record);
          return record.state;
        }
      })();
      record.completion = recovery;
      options.onBackground?.(recovery);
      return { runId, status: record.state.status, outcome: record.state.outcome, completion: recovery };
    },
    shutdown() {
      for (const [runId, record] of active) {
        if (!terminal(record.state.status)) this.control(runId, 'stop');
      }
    },
  };
}
