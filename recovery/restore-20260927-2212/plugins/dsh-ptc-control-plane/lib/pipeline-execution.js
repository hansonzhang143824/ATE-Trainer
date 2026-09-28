import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { trainingAddressBook } from './training-paths.js';
import { preparePipelineMaterials } from './pipeline-materials.js';
import { createTrainingPipeline } from './training-pipeline.js';
import { runHostCommand } from './host-command.js';
import { runDftGate, finalProductHashes } from './training-execution.js';
import { compileTrainingProject } from './training-compile.js';
import { TRAINING_MODEL_CHOICES } from './training-model.js';

const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const sameItems = (a, b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
function save(root, file, value) {
  assertSafeRunPath(root, file);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
  try { fs.renameSync(temporary, file); } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
function notCancelled(signal) { if (signal?.aborted) throw signal.reason ?? new Error('training cancelled'); }
function itemsOf(value) {
  if (!Array.isArray(value) || !value.length || value.some(tm => typeof tm !== 'string' || !/^TM\d+$/.test(tm))
      || new Set(value).size !== value.length) throw new Error('pipeline requires unique explicit TM identifiers');
  return [...value].sort((a, b) => Number(a.slice(2)) - Number(b.slice(2)));
}

function sealedStatistic(root, directory, runId, pipelineCacheKey, report) {
  const file = assertSafeRunPath(root, path.join(directory, 'evidence', 'component-statistic-only.json'));
  if (fs.existsSync(file)) throw new Error('statistic-only evidence already exists');
  const receipt = { schemaVersion: 1, purpose: 'schematic-statistic-only', runId,
    pipelineCacheKey, gatePassed: false, modelDispatched: false, report };
  save(root, file, receipt);
  return { path: file, sha256: sha(fs.readFileSync(file)), outputPath: report.requiredOutputs[0],
    outputSha256: report.outputSha256, gatePassed: false, modelDispatched: false };
}

/** Never silently restart an in-flight pipeline or script after a host crash.
 * A new training run is required unless a separate explicit receipt recovery
 * proves the complete operation. Terminal histories are never rewritten. */
export function reconcileInterruptedPipelineRuns(workspaceRoot) {
  const root = path.resolve(workspaceRoot);
  const runs = assertSafeRunPath(root, 'Training_Materials/runs');
  let names;
  try { names = fs.readdirSync(runs); } catch { return []; }
  const changed = [];
  for (const runId of names) {
    try {
      trainingAddressBook(runId);
      const directory = assertSafeRunPath(root, path.join(runs, runId));
      const context = read(assertSafeRunPath(root, path.join(directory, 'run.json')));
      const stateFile = assertSafeRunPath(root, path.join(directory, 'state.json'));
      const state = read(stateFile);
      if (context.mode !== 'training' || context.runId !== runId || context.projectId !== null
          || context.releaseId !== null || state.runId !== runId || state.target?.kind !== 'pipeline'
          || !['business-training', 'schematic-statistic-only'].includes(state.purpose)
          || !['preparing', 'running', 'pausing', 'paused'].includes(state.status)) continue;
      const now = new Date().toISOString();
      save(root, stateFile, { ...state, status: 'interrupted', updatedAt: now, finishedAt: now,
        outcome: { mode: state.purpose === 'schematic-statistic-only' ? 'STATISTIC_ONLY' : 'PIPELINE',
          reason: 'host_restarted_before_training_completion; do not redispatch without receipt reconciliation',
          stage: null } });
      changed.push(runId);
    } catch { /* Unverifiable runs remain untouched and cannot be resumed by a live controller. */ }
  }
  return changed;
}

/** Concrete, fixed host adapters. No executable or filesystem root comes from HTTP. */
export function createNativePipelineAdapters(root, materials, dftDispatcher, stageDispatcher, options = {}) {
  const runId = materials.runId;
  const directory = assertSafeRunPath(root, trainingAddressBook(runId).runRoot);
  const command = options.runHostCommand ?? runHostCommand;
  const dftGate = options.runDftGate ?? runDftGate;
  const verify = options.verifyMaterials ?? (async () => {
    const checked = await preparePipelineMaterials(root, runId, materials.testItems);
    if (checked.pipelineCacheKey !== materials.pipelineCacheKey) throw new Error('pipeline material identity changed');
  });
  let hostFacts = [];
  const evidencePath = stage => path.join(directory, 'evidence', `pipeline-${stage}.json`);
  const sealed = (stage, result) => {
    const value = { schemaVersion: 1, runId, pipelineCacheKey: materials.pipelineCacheKey, ...result };
    save(root, evidencePath(stage), value);
    return value;
  };
  async function check(request) {
    notCancelled(request.signal);
    if (request.runId !== runId || !sameItems(request.testItems, materials.testItems)) throw new Error('pipeline callback identity differs');
    await verify(); notCancelled(request.signal);
    const registry = fs.readFileSync(assertSafeRunPath(root, path.resolve(root, materials.registry)));
    if (sha(registry) !== request.registryDigest) throw new Error('engine registry differs from material snapshot');
    const definition = JSON.parse(registry.toString('utf8')).stages?.[request.stage];
    if (!definition || definition.owner !== request.owner || definition.gate !== request.gate) throw new Error('stage owner or gate differs from frozen registry');
  }
  async function python(args, request) {
    notCancelled(request.signal);
    const result = await command('python', ['-X', 'utf8', ...args], { cwd: root, signal: request.signal, timeoutMs: 30_000 });
    notCancelled(request.signal);
    if (result.status !== 'passed' || result.exitCode !== 0) {
      sealed(`${request.stage}-command-failure`, { stage: request.stage, commandResult: result });
      throw new Error(`${args[0]} failed: ${result.stopReason ?? result.stderr ?? result.stdout ?? result.exitCode}`);
    }
    return result;
  }
  async function stageGate(request, action = 'gate') {
    const result = await python(['scripts/training_stage_gate.py', '--run-id', runId, '--stage', request.stage,
      '--action', action, ...request.testItems.flatMap(tm => ['--tm', tm])], request);
    const report = JSON.parse(result.stdout);
    if (report.runId !== runId || report.stage !== request.stage || report.gate !== request.gate
        || report.pipelineCacheKey !== materials.pipelineCacheKey || !sameItems(report.testItems ?? [], request.testItems)
        || report.status !== 'passed' || report.exitCode !== 0 || report.action !== action) throw new Error('host stage gate returned an unbound report');
    const receipt = assertSafeRunPath(root, report.receiptPath);
    const relative = path.relative(path.join(directory, 'verification'), receipt);
    if (!relative || relative.startsWith('..') || path.isAbsolute(relative)
        || sha(fs.readFileSync(receipt)) !== report.receiptSha256) throw new Error('host stage gate evidence differs');
    hostFacts = report.shaFacts ?? [];
    return { ...report, adapterCommand: result.command };
  }
  async function sourceDft(request) {
    const reports = [];
    for (const tm of request.testItems) { notCancelled(request.signal); reports.push(await dftGate(root, tm, materials)); }
    let result = null;
    let mode = 'UNCHANGED';
    if (!(materials.cacheCompatible === true && reports.every(report => report.status === 'ready' && report.exitCode === 0))) {
      const abort = () => dftDispatcher.stop(runId, 'pipeline source stage cancelled');
      request.signal?.addEventListener('abort', abort, { once: true });
      try {
        notCancelled(request.signal);
        const dispatch = await dftDispatcher.dispatch({ runId, testItems: request.testItems, reports, materials, runDirectory: directory,
          modelChoice: options.modelChoice });
        if (request.signal?.aborted) abort();
        result = await dispatch.result; notCancelled(request.signal);
        if (result?.stopReason !== 'completed' || result?.structured?.status !== 'done') throw new Error(result?.diagnostic ?? 'DFT expert did not complete');
        mode = 'OVERWRITTEN';
      } finally { request.signal?.removeEventListener('abort', abort); }
    }
    const finalReports = [];
    for (const tm of request.testItems) { notCancelled(request.signal); finalReports.push(await dftGate(root, tm, materials)); }
    if (finalReports.some(report => report.status !== 'ready' || report.exitCode !== 0)) throw new Error('DFT terminal gate did not pass');
    return sealed('INPUT_SYNC-dft', { role: 'dft-expert', status: 'done', testItems: request.testItems, mode,
      childResult: result, reports: finalReports, finalProducts: finalProductHashes(root, request.testItems, materials) });
  }
  async function sourceSchematic(request) {
    const args = ['scripts/training_schematic.py', '--run-root', directory,
      '--input-root', path.join(directory, 'input'), '--out-dir', path.resolve(root, materials.schematicRoot),
      '--source', path.resolve(root, materials.input.schematic), '--confirmed', path.resolve(root, materials.input.confirmed),
      '--cbit', path.resolve(root, materials.input.cbit)];
    for (const action of ['generate', 'validate']) {
      const result = await python([...args, '--action', action], request);
      const report = JSON.parse(result.stdout);
      const expectedOutputs = ['SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
        'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json']
        .map(name => path.resolve(root, materials.schematicRoot, name));
      const actualOutputs = Array.isArray(report.requiredOutputs)
        ? report.requiredOutputs.map(file => typeof file === 'string' ? path.resolve(root, file) : null) : [];
      if (report.gate !== 'SCHEMATIC_OUTPUT' || report.status !== 'ready'
          || report.trainingContext?.runId !== runId || report.trainingContext?.pipelineCacheKey !== materials.pipelineCacheKey
          || report.trainingContext?.validator !== 'scripts/validate_schematic_outputs.py'
          || typeof report.canonicalInput?.path !== 'string'
          || path.resolve(root, report.canonicalInput.path) !== path.resolve(root, materials.input.schematic)
          || actualOutputs.length !== 7 || !sameItems(actualOutputs, expectedOutputs)
          || expectedOutputs.some(file => !fs.statSync(assertSafeRunPath(root, file)).isFile())) throw new Error('schematic host report is not bound to this run');
    }
    const terminal = await stageDispatcher.dispatch({ ...request, owner: 'schematic-expert', modelChoice: options.modelChoice }, materials);
    if (terminal.status !== 'done') {
      const detail = terminal.reason ?? terminal.result?.structured?.reason;
      const summary = typeof detail === 'string' && detail.trim()
        ? `${detail.trim().slice(0, 300)}${detail.trim().length > 300 ? '… (see signed schematic terminal)' : ''}`
        : 'schematic semantic review did not complete';
      throw new Error(summary);
    }
    return terminal;
  }
  return {
    async dispatchStage(request) {
      await check(request);
      let terminals;
      if (request.stage === 'INPUT_SYNC') {
        // Source children use disjoint products. Abort the sibling on a failure.
        const controller = new AbortController();
        const abort = () => controller.abort(request.signal?.reason ?? new Error('source stage cancelled'));
        request.signal?.addEventListener('abort', abort, { once: true });
        if (request.signal?.aborted) abort();
        try {
          const childRequest = { ...request, signal: controller.signal };
          terminals = await Promise.all([sourceDft(childRequest), sourceSchematic(childRequest)]);
        } catch (error) { controller.abort(error); throw error; }
        finally { request.signal?.removeEventListener('abort', abort); }
      } else if (request.stage === 'COMPILE') {
        if (materials.vsProjects?.length !== 1) throw new Error('compile requires exactly one unambiguous frozen vcxproj');
        const reportFile = path.join(directory, 'compile', 'build-report.json');
        const report = await (options.compile ?? compileTrainingProject)({ workspaceRoot: root, runId,
          vsProjectRoot: path.resolve(root, materials.vsProjectRoot), projectFile: path.resolve(root, materials.vsProjects[0]),
          source: path.resolve(root, materials.programSourceRoot, 'test.cpp'), report: reportFile,
        }, { signal: request.signal, timeoutMs: 30_000 });
        notCancelled(request.signal);
        if (report.status !== 'passed') throw new Error(report.reason ?? 'isolated compile did not pass');
        terminals = [{ role: request.owner, status: 'done', testItems: request.testItems,
          executionKind: 'deterministic-host-compile-adapter', report: reportFile, reportSha256: sha(fs.readFileSync(reportFile)) }];
      } else {
        if (request.stage === 'STRATEGY') await stageGate(request, 'prepare-register');
        const terminal = await stageDispatcher.dispatch({ ...request, hostFacts, modelChoice: options.modelChoice }, materials);
        terminals = [terminal];
      }
      notCancelled(request.signal);
      if (terminals.some(terminal => terminal.status !== 'done')) throw new Error('a stage expert reported blocked');
      return sealed(request.stage, { stage: request.stage, registryDigest: request.registryDigest, terminals });
    },
    async recoverStage(request) {
      await check(request);
      // Only a host-sealed terminal is recoverable. Unknown in-flight work is
      // blocked, never guessed successful and never automatically sent twice.
      const result = read(assertSafeRunPath(root, evidencePath(request.stage)));
      if (result.runId !== runId || result.stage !== request.stage || result.registryDigest !== request.registryDigest
          || result.pipelineCacheKey !== materials.pipelineCacheKey) throw new Error('stage recovery lacks matching host evidence');
      if (!Array.isArray(result.terminals) || result.terminals.length !== request.expectedRoles.length
          || new Set(result.terminals.map(item => item.role)).size !== request.expectedRoles.length
          || result.terminals.some(item => !request.expectedRoles.includes(item.role) || item.status !== 'done'
            || !sameItems(item.testItems ?? [], request.testItems))) throw new Error('stage recovery has incomplete terminals');
      if (request.stage === 'INPUT_SYNC') {
        const dft = read(assertSafeRunPath(root, evidencePath('INPUT_SYNC-dft')));
        if (dft.runId !== runId || dft.pipelineCacheKey !== materials.pipelineCacheKey || dft.status !== 'done'
            || !sameItems(dft.testItems ?? [], request.testItems)
            || JSON.stringify(dft.finalProducts) !== JSON.stringify(finalProductHashes(root, request.testItems, materials))) throw new Error('source recovery lacks unchanged DFT evidence');
        const schematic = stageDispatcher.recover({ ...request, owner: 'schematic-expert', modelChoice: options.modelChoice });
        if (schematic.status !== 'done') throw new Error('source recovery lacks real schematic review');
        result.terminals = [dft, schematic];
      }
      if (!['INPUT_SYNC', 'COMPILE'].includes(request.stage)) {
        const terminal = stageDispatcher.recover({ ...request, modelChoice: options.modelChoice });
        if (terminal.status !== 'done') throw new Error('stage receipt is not completed');
        result.terminals = [terminal];
      }
      return result;
    },
    async runStageGate(request) {
      await check(request);
      if (request.stage !== 'COMPILE') return stageGate(request);
      const terminal = read(assertSafeRunPath(root, evidencePath('COMPILE')))?.terminals?.[0];
      const reportFile = assertSafeRunPath(root, path.join(directory, 'compile', 'build-report.json'));
      if (terminal?.report !== reportFile || terminal.reportSha256 !== sha(fs.readFileSync(reportFile))) throw new Error('compile receipt changed');
      const report = read(reportFile);
      if (typeof report.source !== 'string' || typeof report.project !== 'string'
          || path.resolve(report.source) !== path.resolve(root, materials.programSourceRoot, 'test.cpp')
          || path.resolve(report.project) !== path.resolve(root, materials.vsProjects[0])
          || sha(fs.readFileSync(assertSafeRunPath(root, report.source))) !== report.sourceSha256
          || sha(fs.readFileSync(assertSafeRunPath(root, report.project))) !== report.projectSha256) throw new Error('compiled source or project changed after build');
      const artifactValid = item => {
        const file = assertSafeRunPath(root, item.path);
        const relative = path.relative(path.join(directory, 'compile'), file);
        return relative && !relative.startsWith('..') && !path.isAbsolute(relative)
          && item.size > 0 && fs.statSync(file).size === item.size && sha(fs.readFileSync(file)) === item.sha256;
      };
      if (report.runId !== runId || report.mode !== 'training' || report.status !== 'passed'
          || report.artifacts?.length !== 2 || report.commands?.length !== 2
          || report.commands.some(item => item.exitCode !== 0 || item.closed !== true)
          || report.artifacts.some(item => !artifactValid(item))) throw new Error('compile gate has no verified fresh build evidence');
      const result = { runId, stage: 'COMPILE', gate: request.gate, status: 'passed', exitCode: 0,
        adapter: 'training-compile.js', reportPath: reportFile, reportSha256: terminal.reportSha256 };
      sealed('COMPILE-gate', result);
      return result;
    },
  };
}

/** Owns asynchronous preparation and one controller per run. */
export function createPipelineExecutionManager(workspaceRoot, dftDispatcher, stageDispatcher, options = {}) {
  const root = path.resolve(workspaceRoot);
  const active = new Map();
  function locate(runId) {
    const directory = assertSafeRunPath(root, trainingAddressBook(runId).runRoot);
    const context = read(assertSafeRunPath(root, path.join(directory, 'run.json')));
    const file = assertSafeRunPath(root, path.join(directory, 'state.json'));
    const state = read(file);
    if (context.runId !== runId || context.mode !== 'training' || context.projectId !== null || context.releaseId !== null
        || path.resolve(root, context.artifactRoot) !== directory || state.runId !== runId || state.target?.kind !== 'pipeline'
        || state.purpose === 'framework-rehearsal') throw new Error('not an isolated business pipeline training identity');
    return { directory, context, file, state };
  }
  function update(record, progress) {
    const now = new Date().toISOString();
    const statisticOnly = record.state.purpose === 'schematic-statistic-only';
    record.state = { ...record.state, status: progress.status, updatedAt: now,
      outcome: { mode: statisticOnly ? 'STATISTIC_ONLY' : 'PIPELINE', reason: progress.reason ?? null,
        stage: statisticOnly ? null : progress.stages?.find(stage => stage.status !== 'completed')?.stage ?? null,
        ...(progress.report ? { report: progress.report } : {}) },
      finishedAt: ['completed', 'blocked', 'cancelled'].includes(progress.status) ? now : null };
    save(root, record.file, record.state);
  }
  return {
    start(input) {
      const runId = input?.runId;
      const located = locate(runId);
      const testItems = itemsOf(input?.testItems);
      const modelChoice = input?.modelChoice ?? 'default';
      if (typeof modelChoice !== 'string' || !Object.hasOwn(TRAINING_MODEL_CHOICES, modelChoice)) throw new Error('unsupported training model choice');
      const statisticOnly = located.state.purpose === 'schematic-statistic-only';
      if (!statisticOnly && options.allowArchivedFullPipeline !== true) {
        throw new Error('complete schematic pipeline is archived during statistic-only training');
      }
      if (statisticOnly && (located.state.target?.fromStage !== 'INPUT_SYNC'
          || located.state.target?.toStage !== 'INPUT_SYNC' || modelChoice !== 'default')) {
        throw new Error('statistic-only training cannot dispatch a model or other stages');
      }
      if (active.has(runId) || located.state.status !== 'created') throw new Error('pipeline is already started; use its control action');
      const lock = assertSafeRunPath(root, path.join(located.directory, 'pipeline-execution.lock'));
      fs.writeFileSync(lock, `${process.pid}\n`, { flag: 'wx' });
      const record = { ...located, state: { ...located.state, testItems, modelChoice }, cancelled: false, paused: false, controller: null };
      active.set(runId, record);
      update(record, { status: 'preparing', reason: 'freezing private training materials' });
      const completion = (async () => {
        try {
          const materials = await (options.prepareMaterials ?? preparePipelineMaterials)(root, runId, testItems);
          if (record.cancelled) return record.state;
          if (materials?.runId !== runId || !Array.isArray(materials.testItems) || !sameItems(materials.testItems, testItems)) throw new Error('prepared pipeline identity differs');
          if (statisticOnly) {
            const output = path.resolve(root, materials.schematicRoot, 'Component-Statistic.txt');
            const result = await (options.runHostCommand ?? runHostCommand)('python', ['-X', 'utf8',
              'scripts/training_schematic.py', '--action', 'statistic', '--run-root', located.directory,
              '--input-root', path.join(located.directory, 'input'), '--out-dir', path.resolve(root, materials.schematicRoot),
              '--source', path.resolve(root, materials.input.schematic),
              '--confirmed', path.resolve(root, materials.input.confirmed),
              '--cbit', path.resolve(root, materials.input.cbit)], { cwd: root, timeoutMs: 30_000 });
            if (record.cancelled) return record.state;
            if (result.status !== 'passed' || result.exitCode !== 0) throw new Error(result.stderr || result.stopReason || 'statistic-only producer failed');
            const report = JSON.parse(result.stdout);
            if (report.mode !== 'STATISTIC_ONLY' || report.status !== 'generated' || report.gate !== null
                || report.trainingContext?.runId !== runId
                || report.trainingContext?.pipelineCacheKey !== materials.pipelineCacheKey
                || report.canonicalInput?.path !== path.resolve(root, materials.input.schematic)
                || !/^[a-f0-9]{64}$/.test(report.canonicalInput?.sha256 ?? '')
                || !/^[a-f0-9]{64}$/.test(report.outputSha256 ?? '')
                || !sameItems(report.requiredOutputs ?? [], [output])
                || sha(fs.readFileSync(assertSafeRunPath(root, output))) !== report.outputSha256) {
              throw new Error('statistic-only result is not bound to this frozen run');
            }
            const receipt = sealedStatistic(root, located.directory, runId, materials.pipelineCacheKey, report);
            update(record, { status: 'completed', report: receipt });
            return record.state;
          }
          const adapters = (options.createAdapters ?? createNativePipelineAdapters)(root, materials, dftDispatcher, stageDispatcher,
            { modelChoice });
          record.controller = (options.createEngine ?? createTrainingPipeline)({ workspaceRoot: root, runId, testItems,
            sourceRoles: ['dft-expert', 'schematic-expert'], ...adapters, onState: progress => update(record, progress),
            dispatchTimeoutMs: 8 * 60_000, gateTimeoutMs: 30_000 });
          if (record.paused) { record.controller.pause(); return record.state; }
          await record.controller.start();
        } catch (error) {
          if (!record.cancelled) update(record, { status: 'blocked', reason: error.message });
        } finally {
          // A cancelled preparer can still be draining a bounded copy command.
          // Do not release its lock or allow any child until that command settles.
          try { fs.unlinkSync(lock); } catch {}
        }
        return record.state;
      })();
      record.completion = completion;
      options.onBackground?.(completion);
      return { runId, status: record.state.status, outcome: record.state.outcome, completion };
    },
    control(runId, action) {
      trainingAddressBook(runId);
      if (!['pause', 'resume', 'stop'].includes(action)) throw new Error('unsupported pipeline action');
      const record = active.get(runId);
      if (!record) throw new Error('pipeline has no live controller; interrupted runs require explicit receipt recovery');
      if (['completed', 'blocked', 'cancelled'].includes(record.state.status)) throw new Error('pipeline is already terminal');
      if (action === 'stop') {
        record.cancelled = true;
        if (record.controller) record.controller.cancel('user stopped pipeline training');
        else update(record, { status: 'cancelled', reason: 'cancelled during preparation; pending copy may still be draining' });
        dftDispatcher.stop(runId, 'user stopped pipeline training');
      } else if (action === 'pause') {
        record.paused = true;
        if (record.controller) record.controller.pause();
        else update(record, { status: 'pausing', reason: 'pause requested; material preparation is draining' });
      } else {
        if (record.state.status !== 'paused' || !record.controller) throw new Error('wait until pipeline is paused before resuming');
        record.paused = false;
        record.completion = record.controller.resume();
        record.completion.catch(error => update(record, { status: 'blocked', reason: error.message }));
        options.onBackground?.(record.completion);
      }
      return { runId, status: record.state.status, outcome: record.state.outcome, terminationConfirmed: false };
    },
    shutdown() {
      for (const [runId, record] of active) {
        if (!['completed', 'blocked', 'cancelled'].includes(record.state.status)) this.control(runId, 'stop');
      }
    },
  };
}
