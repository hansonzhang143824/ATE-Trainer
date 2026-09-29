import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import test from 'node:test';
import { setTimeout as delay } from 'node:timers/promises';
import { createNativePipelineAdapters, createPipelineExecutionManager, reconcileInterruptedPipelineRuns } from '../lib/pipeline-execution.js';

const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
function write(file, data) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, JSON.stringify(data)); }
function bytes(file, data = 'fixture') { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, data); }
function deferred() { let resolve; const promise = new Promise(yes => { resolve = yes; }); return { promise, resolve }; }
const schematicNames = ['SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt', 'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json'];
const dftNames = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-pipeline-execution-'));
  const runId = 'training-pipeline-execution'; const runRelative = `Training_Materials/runs/${runId}`; const directory = path.join(root, runRelative);
  const context = { runId, mode: 'training', projectId: null, releaseId: null, artifactRoot: runRelative };
  const state = { runId, status: 'created', target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'STRATEGY' } };
  write(path.join(directory, 'run.json'), context); write(path.join(directory, 'state.json'), state);
  const registry = { stateMachine: ['INPUT_SYNC', 'STRATEGY', 'COMPILE', 'COMPLETE'], stages: {
    INPUT_SYNC: { owner: 'captain', gate: 'scripts/prepare_input_sync_v2.py', outputs: ['input-manifest.json'] },
    STRATEGY: { owner: 'test-strategy-architect', gate: 'scripts/validate_strategy_contract.py', outputs: ['strategy/deliverable-ready.json'] },
    COMPILE: { owner: 'compile-diagnostician', gate: 'scripts/compile.py', outputs: ['compile/build-report.json'] },
  } };
  const materials = { runId, testItems: ['TM109'], cacheCompatible: true, pipelineCacheKey: 'a'.repeat(64),
    registry: `${runRelative}/orchestration/ptc_stage_registry.json`, workbook: `${runRelative}/input/Dali_testmode.xlsx`,
    dftRoot: `${runRelative}/input-sync/dft`, schematicRoot: `${runRelative}/input-sync/schematic`,
    input: { schematic: `${runRelative}/input/Dali-SCH.csv`, confirmed: `${runRelative}/input/sch_confirmed.json`, cbit: `${runRelative}/input/CBIT表-DALI.xlsx` },
    vsProjectRoot: `${runRelative}/vs-project`, programSourceRoot: `${runRelative}/vs-project/source`, vsProjects: [`${runRelative}/vs-project/source/Dali.vcxproj`] };
  write(path.join(root, materials.registry), registry); write(path.join(root, 'team/ptc/ptc_stage_registry.json'), registry);
  for (const file of [materials.workbook, ...Object.values(materials.input), `${materials.programSourceRoot}/test.cpp`, ...materials.vsProjects]) bytes(path.join(root, file));
  for (const name of dftNames) bytes(path.join(root, materials.dftRoot, 'TM109', name));
  for (const name of schematicNames) bytes(path.join(root, materials.schematicRoot, name));
  const registryDigest = sha(fs.readFileSync(path.join(root, materials.registry)));
  const request = stage => ({ runId, stage, owner: registry.stages[stage].owner, gate: registry.stages[stage].gate, registryDigest,
    testItems: ['TM109'], expectedRoles: stage === 'INPUT_SYNC' ? ['dft-expert', 'schematic-expert'] : [registry.stages[stage].owner],
    dispatchId: `${runId}:${stage}:1`, signal: new AbortController().signal });
  return { root, runId, directory, materials, context, state, request, stateFile: path.join(directory, 'state.json') };
}

function adaptersFixture(f, overrides = {}) {
  const calls = { commands: [], stages: [], dft: 0, stopped: 0, verified: 0 };
  const dftDispatcher = { async dispatch() { calls.dft += 1; return { result: Promise.resolve({ stopReason: 'completed', structured: { status: 'done' } }) }; }, stop() { calls.stopped += 1; } };
  const terminal = request => ({ runId: f.runId, stage: request.stage, role: request.owner, testItems: request.testItems, status: 'done', registryDigest: request.registryDigest,
    pipelineCacheKey: f.materials.pipelineCacheKey, childSessionId: 'fixture-child', dispatchId: `${f.runId}:${request.stage}:${request.owner}:1`,
    result: { stopReason: 'completed', structured: { status: 'done' } } });
  const stageDispatcher = { async dispatch(request) { calls.stages.push(request.stage); return terminal(request); }, recover(request) { return terminal(request); } };
  const dftReport = tm => ({ tm, gate: 'DFT_OUTPUT', status: 'ready', exitCode: 0,
    canonicalInput: { path: path.join(f.root, f.materials.workbook), sha256: sha(fs.readFileSync(path.join(f.root, f.materials.workbook))) },
    requiredOutputs: dftNames.map(name => path.join(f.root, f.materials.dftRoot, tm, name)), missingOrStaleOutputs: [] });
  const schematicReport = () => ({ role: 'schematic-expert', gate: 'SCHEMATIC_OUTPUT', status: 'ready',
    canonicalInput: { path: path.join(f.root, f.materials.input.schematic), sha256: sha(fs.readFileSync(path.join(f.root, f.materials.input.schematic))) },
    requiredOutputs: schematicNames.map(name => path.join(f.root, f.materials.schematicRoot, name)), missingOrStaleOutputs: [],
    trainingContext: { runId: f.runId, pipelineCacheKey: f.materials.pipelineCacheKey, validator: 'scripts/validate_schematic_outputs.py' } });
  const command = async (executable, args, options) => {
    calls.commands.push({ executable, args, options });
    let report;
    if (args.includes('scripts/training_schematic.py')) report = schematicReport();
    else {
      const stage = args[args.indexOf('--stage') + 1]; const action = args[args.indexOf('--action') + 1]; const request = f.request(stage);
      const receiptPath = path.join(f.directory, 'verification', `${stage}-${action}.json`);
      report = { runId: f.runId, stage, gate: request.gate, testItems: request.testItems, pipelineCacheKey: f.materials.pipelineCacheKey,
        status: 'passed', exitCode: 0, action, shaFacts: [], receiptPath };
      write(receiptPath, report); report.receiptSha256 = sha(fs.readFileSync(receiptPath));
    }
    return { status: 'passed', exitCode: 0, stdout: JSON.stringify(report), stderr: '', command: [executable, ...args].join(' ') };
  };
  const options = { runHostCommand: command, runDftGate: async (_root, tm) => dftReport(tm), verifyMaterials: async () => { calls.verified += 1; },
    prepareDftSourceView: async (_root, testItems) => ({ status: 'SOURCE_VIEW', runId: f.runId,
      path: `${f.materials.runRoot}/input/dft-source-view.json`, sha256: 'b'.repeat(64), sourceSha256: 'a'.repeat(64),
      testItems: [...testItems].sort() }),
    prepareDftReviewInput: async (_root, testItems, materials, sourceView) => ({ schemaVersion: 1, runId: f.runId,
      sourceSha256: sourceView.sourceSha256, items: testItems.map(tm => ({ tm,
        producerDigests: { 'dft-meta.json': 'c'.repeat(64), 'dft-conditions.yaml': 'd'.repeat(64) } })) }),
    bindDftSemanticReviews: async () => {}, ...overrides };
  return { calls, command, schematicReport, dftReport, dftDispatcher, stageDispatcher, options,
    create: () => createNativePipelineAdapters(f.root, f.materials, dftDispatcher, stageDispatcher, options) };
}

function mockEngine(observed) {
  return options => {
    observed.engineOptions = options;
    return {
      async start() { observed.started += 1; options.onState({ status: 'completed', stages: [] }); },
      pause() { observed.paused += 1; options.onState({ status: 'paused', stages: [] }); },
      async resume() { observed.resumed += 1; options.onState({ status: 'completed', stages: [] }); },
      cancel() { observed.cancelled += 1; options.onState({ status: 'cancelled', stages: [] }); },
    };
  };
}
const observedEngine = () => ({ started: 0, paused: 0, resumed: 0, cancelled: 0 });

test('statistic-only training writes one product and evidence without DFT, model or stage gate', async () => {
  const f = fixture();
  write(f.stateFile, { ...f.state, purpose: 'schematic-statistic-only',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' } });
  for (const name of schematicNames) fs.unlinkSync(path.join(f.root, f.materials.schematicRoot, name));
  let dispatched = 0; let commands = 0;
  const manager = createPipelineExecutionManager(f.root, { stop() { dispatched += 1; } },
    { dispatch() { dispatched += 1; } }, { prepareMaterials: async () => f.materials,
      createEngine() { dispatched += 1; throw new Error('must not create a pipeline engine'); },
      runHostCommand: async (_executable, args) => {
        commands += 1;
        assert.ok(args.includes('statistic'));
        const output = path.join(f.root, f.materials.schematicRoot, 'Component-Statistic.txt');
        bytes(output, 'statistic-only fixture\n');
        const report = { mode: 'STATISTIC_ONLY', status: 'generated', gate: null,
          trainingContext: { runId: f.runId, pipelineCacheKey: f.materials.pipelineCacheKey },
          canonicalInput: { path: path.join(f.root, f.materials.input.schematic), sha256: 'b'.repeat(64) },
          requiredOutputs: [output], outputSha256: sha(fs.readFileSync(output)) };
        return { status: 'passed', exitCode: 0, stdout: JSON.stringify(report) };
      } });
  const accepted = manager.start({ runId: f.runId, testItems: ['TM109'] });
  await accepted.completion;
  const result = read(f.stateFile);
  assert.equal(result.status, 'completed');
  assert.equal(result.outcome.mode, 'STATISTIC_ONLY');
  assert.equal(result.outcome.report.gatePassed, false);
  assert.equal(result.outcome.report.modelDispatched, false);
  assert.equal(commands, 1);
  assert.equal(dispatched, 0);
  assert.deepEqual(fs.readdirSync(path.join(f.root, f.materials.schematicRoot)), ['Component-Statistic.txt']);
  assert.equal(fs.existsSync(path.join(f.directory, 'pipeline-progress.json')), false);
});

test('default host rejects archived complete schematic pipeline before material preparation', () => {
  const f = fixture();
  let prepared = 0;
  const manager = createPipelineExecutionManager(f.root, { stop() {} }, {}, {
    prepareMaterials: async () => { prepared += 1; return f.materials; },
  });
  assert.throws(() => manager.start({ runId: f.runId, testItems: ['TM109'] }), /archived/);
  assert.equal(prepared, 0);
  assert.equal(read(f.stateFile).status, 'created');
});

test('restart marks unfinished statistic and business pipelines interrupted without restarting or rewriting terminal runs', () => {
  const running = fixture();
  write(running.stateFile, { ...running.state, purpose: 'schematic-statistic-only', status: 'preparing',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' } });
  const completeFile = path.join(running.root, 'Training_Materials/runs/training-complete', 'state.json');
  write(path.join(path.dirname(completeFile), 'run.json'), { ...running.context, runId: 'training-complete',
    artifactRoot: 'Training_Materials/runs/training-complete' });
  write(completeFile, { runId: 'training-complete', purpose: 'business-training', target: running.state.target,
    status: 'completed' });
  const completeBytes = fs.readFileSync(completeFile);
  assert.deepEqual(reconcileInterruptedPipelineRuns(running.root), [running.runId]);
  const next = read(running.stateFile);
  assert.equal(next.status, 'interrupted');
  assert.match(next.outcome.reason, /do not redispatch/);
  assert.equal(next.outcome.mode, 'STATISTIC_ONLY');
  assert.deepEqual(fs.readFileSync(completeFile), completeBytes);
  assert.deepEqual(reconcileInterruptedPipelineRuns(running.root), []);
});

test('manager start tracks preparation asynchronously, rejects duplicate starts and invalid isolated identities', async () => {
  const f = fixture(); const pending = deferred(); const observed = observedEngine(); const background = [];
  const manager = createPipelineExecutionManager(f.root, { stop() {} }, {}, { allowArchivedFullPipeline: true, prepareMaterials: () => pending.promise,
    createAdapters: () => ({}), createEngine: mockEngine(observed), onBackground: promise => background.push(promise) });
  const execution = manager.start({ runId: f.runId, testItems: ['TM109'] });
  assert.equal(execution.status, 'preparing');
  assert.equal(background.length, 1);
  assert.throws(() => manager.start({ runId: f.runId, testItems: ['TM109'] }), /already started/);
  pending.resolve(f.materials); await execution.completion;
  assert.equal(observed.started, 1); assert.equal(read(f.stateFile).status, 'completed');
  assert.equal(fs.existsSync(path.join(f.directory, 'pipeline-execution.lock')), false);
  const other = fixture(); write(path.join(other.directory, 'run.json'), { ...other.context, mode: 'delivery', releaseId: 'published' });
  const invalid = createPipelineExecutionManager(other.root, {}, {}, {});
  assert.throws(() => invalid.start({ runId: other.runId, testItems: ['TM109'] }), /isolated/);
  assert.throws(() => manager.start({ runId: '../outside', testItems: ['TM109'] }));
});

test('business pipeline gets the extended bounded material-gate budget while smoke keeps its default', async () => {
  const f = fixture();
  write(f.stateFile, { ...f.state, purpose: 'business-training' });
  let adapterOptions; let engineOptions;
  const observed = observedEngine();
  const manager = createPipelineExecutionManager(f.root, { stop() {} }, {}, {
    requiredPurpose: 'business-training', allowArchivedFullPipeline: true,
    prepareMaterials: async () => f.materials,
    createAdapters: (...args) => { adapterOptions = args.at(-1); return {}; },
    createEngine: mockEngine(observed),
  });
  await manager.start({ runId: f.runId, testItems: ['TM109'] }).completion;
  engineOptions = observed.engineOptions;
  assert.equal(adapterOptions.hostCommandTimeoutMs, 120_000);
  assert.equal(engineOptions.gateTimeoutMs, 120_000);
});

test('cancelling preparation keeps copy lock until it drains and cannot create a late expert', async () => {
  const f = fixture(); const pending = deferred(); const observed = observedEngine(); let stops = 0;
  const manager = createPipelineExecutionManager(f.root, { stop() { stops += 1; } }, {}, { allowArchivedFullPipeline: true, prepareMaterials: () => pending.promise,
    createAdapters: () => ({}), createEngine: mockEngine(observed) });
  const execution = manager.start({ runId: f.runId, testItems: ['TM109'] });
  const control = manager.control(f.runId, 'stop');
  assert.equal(control.status, 'cancelled'); assert.equal(control.terminationConfirmed, false);
  assert.equal(fs.existsSync(path.join(f.directory, 'pipeline-execution.lock')), true);
  pending.resolve(f.materials); await execution.completion;
  assert.equal(observed.started, 0); assert.equal(observed.engineOptions, undefined);
  assert.equal(stops, 1); assert.equal(read(f.stateFile).status, 'cancelled');
  assert.equal(fs.existsSync(path.join(f.directory, 'pipeline-execution.lock')), false);
});

test('pause during preparation drains into paused and resume registers a new background completion', async () => {
  const f = fixture(); const pending = deferred(); const observed = observedEngine(); const background = [];
  const manager = createPipelineExecutionManager(f.root, { stop() {} }, {}, { allowArchivedFullPipeline: true, prepareMaterials: () => pending.promise,
    createAdapters: () => ({}), createEngine: mockEngine(observed), onBackground: promise => background.push(promise) });
  const execution = manager.start({ runId: f.runId, testItems: ['TM109'] });
  assert.equal(manager.control(f.runId, 'pause').status, 'pausing');
  assert.throws(() => manager.control(f.runId, 'resume'), /paused/);
  pending.resolve(f.materials); await execution.completion;
  assert.equal(observed.started, 0); assert.equal(observed.paused, 1); assert.equal(read(f.stateFile).status, 'paused');
  manager.control(f.runId, 'resume'); await delay(0);
  assert.equal(observed.resumed, 1); assert.equal(read(f.stateFile).status, 'completed');
  assert.equal(background.length, 2, 'resumed work must remain tracked by host background ownership');
});

test('manager rejects a preparer returning another run or TM before constructing an engine', async () => {
  for (const changed of [{ runId: 'different-run' }, { testItems: ['TM999'] }]) {
    const f = fixture(); const observed = observedEngine();
    const manager = createPipelineExecutionManager(f.root, { stop() {} }, {}, { allowArchivedFullPipeline: true, prepareMaterials: async () => ({ ...f.materials, ...changed }),
      createAdapters: () => ({}), createEngine: mockEngine(observed) });
    await manager.start({ runId: f.runId, testItems: ['TM109'] }).completion;
    assert.equal(observed.started, 0); assert.equal(read(f.stateFile).status, 'blocked');
  }
});

test('native source adapters reuse DFT and run fixed schematic commands before source semantic review', async () => {
  const f = fixture(); const a = adaptersFixture(f);
  const result = await a.create().dispatchStage(f.request('INPUT_SYNC'));
  assert.deepEqual(result.terminals.map(item => item.role), ['schematic-expert', 'dft-expert']);
  assert.equal(result.terminals[1].mode, 'UNCHANGED'); assert.equal(a.calls.dft, 0);
  assert.equal(a.calls.commands.length, 2); assert.deepEqual(a.calls.stages, ['INPUT_SYNC']);
  for (const call of a.calls.commands) { assert.equal(call.executable, 'python'); assert.equal(call.options.cwd, f.root); assert.equal(call.options.timeoutMs, 30_000); assert.ok(call.args.includes('scripts/training_schematic.py')); }
  assert.equal(result.pipelineCacheKey, f.materials.pipelineCacheKey);
});

test('blocked schematic semantic review surfaces the specialist reason without running a stage gate', async () => {
  const f = fixture(); const a = adaptersFixture(f);
  a.stageDispatcher.dispatch = async () => ({ status: 'blocked', result: { structured: { status: 'blocked', reason: 'K110 contact topology requires source review' } } });
  await assert.rejects(a.create().dispatchStage(f.request('INPUT_SYNC')), /K110 contact topology requires source review/);
  assert.equal(a.calls.commands.length, 2);
});

test('native adapters reject wrong run/TM/registry/owner/gate and pre-abort before any child or host command', async () => {
  for (const mutate of [r => { r.runId = 'other'; }, r => { r.testItems = ['TM999']; }, r => { r.registryDigest = 'b'.repeat(64); },
    r => { r.owner = 'wrong-expert'; }, r => { r.gate = 'scripts/wrong.py'; }, r => { const controller = new AbortController(); controller.abort(new Error('already cancelled')); r.signal = controller.signal; }]) {
    const f = fixture(); const a = adaptersFixture(f); const request = f.request('STRATEGY'); mutate(request);
    await assert.rejects(a.create().dispatchStage(request));
    assert.equal(a.calls.stages.length, 0); assert.equal(a.calls.commands.length, 0);
  }
});

test('source role failure aborts sibling and the real orchestration engine never dispatches downstream', async () => {
  const f = fixture(); f.materials.cacheCompatible = false; const a = adaptersFixture(f); const dft = deferred(); let stopped = 0;
  a.dftDispatcher.dispatch = async () => ({ result: dft.promise });
  a.dftDispatcher.stop = () => { stopped += 1; dft.resolve({ stopReason: 'aborted', structured: { status: 'blocked' } }); };
  a.options.runHostCommand = async () => ({ status: 'blocked', exitCode: 2, stderr: 'source parser conflict' });
  const manager = createPipelineExecutionManager(f.root, a.dftDispatcher, a.stageDispatcher, {
    allowArchivedFullPipeline: true, prepareMaterials: async () => f.materials, createAdapters: () => a.create(),
  });
  await manager.start({ runId: f.runId, testItems: ['TM109'] }).completion;
  assert.equal(read(f.stateFile).status, 'blocked'); assert.equal(stopped, 0);
  assert.deepEqual(a.calls.stages, []);
  const progress = read(path.join(f.directory, 'pipeline-progress.json'));
  assert.equal(progress.stages[0].status, 'blocked'); assert.equal(progress.stages[1].status, 'pending');
});

test('schematic command exit zero cannot substitute an unbound or stale source report', async () => {
  for (const change of [r => { r.trainingContext.runId = 'wrong-run'; }, r => { r.trainingContext.pipelineCacheKey = 'b'.repeat(64); },
    r => { r.status = 'stale'; }, r => { r.canonicalInput.path = path.join('project', 'DALI', 'input.csv'); }, r => { r.requiredOutputs = []; }]) {
    const f = fixture(); const a = adaptersFixture(f);
    a.options.runHostCommand = async () => { const report = a.schematicReport(); change(report); return { status: 'passed', exitCode: 0, stdout: JSON.stringify(report) }; };
    await assert.rejects(a.create().dispatchStage(f.request('INPUT_SYNC')));
    assert.equal(a.calls.stages.length, 0);
  }
});

test('stage host gate checks report identity and receipt bytes instead of trusting exit zero', async () => {
  const f = fixture(); const a = adaptersFixture(f);
  const request = f.request('STRATEGY'); const good = await a.create().runStageGate(request);
  assert.equal(good.status, 'passed'); assert.equal(good.receiptSha256, sha(fs.readFileSync(good.receiptPath)));
  for (const mutate of [r => { r.runId = 'wrong'; }, r => { r.gate = 'wrong'; }, r => { r.receiptSha256 = '0'.repeat(64); }, r => { r.action = 'prepare-register'; }]) {
    a.options.runHostCommand = async (...args) => { const command = await a.command(...args); const report = JSON.parse(command.stdout); mutate(report); return { ...command, stdout: JSON.stringify(report) }; };
    await assert.rejects(a.create().runStageGate(request), /unbound|evidence differs/);
  }
});

test('INPUT_SYNC recovery rejects incomplete or wrong-TM host-sealed terminals', async () => {
  for (const terminals of [[], [{ role: 'dft-expert', status: 'done', testItems: ['TM109'] }],
    [{ role: 'dft-expert', status: 'done', testItems: ['TM999'] }, { role: 'schematic-expert', status: 'done', testItems: ['TM109'] }]]) {
    const f = fixture(); const a = adaptersFixture(f); const request = f.request('INPUT_SYNC');
    write(path.join(f.directory, 'evidence/pipeline-INPUT_SYNC.json'), { schemaVersion: 1, runId: f.runId, stage: 'INPUT_SYNC', registryDigest: request.registryDigest, pipelineCacheKey: f.materials.pipelineCacheKey, terminals });
    await assert.rejects(a.create().recoverStage(request));
    assert.equal(a.calls.stages.length, 0);
  }
});

function fakeCompile(f, mutate = () => {}) {
  return async (options, execution) => {
    assert.equal(execution.timeoutMs, 30_000);
    const configurations = ['Debug', 'Release']; const startedAt = new Date(Date.now() - 1000).toISOString();
    const artifacts = configurations.map(configuration => {
      const file = path.join(f.directory, 'compile/build-fixture', configuration, 'out/training.dll'); bytes(file, `${configuration} binary`);
      return { configuration, path: file, size: fs.statSync(file).size, mtimeMs: fs.statSync(file).mtimeMs, sha256: sha(fs.readFileSync(file)) };
    });
    const report = { schemaVersion: 1, runId: f.runId, stage: 'COMPILE', mode: 'training', status: 'passed', startedAt,
      source: options.source, sourceSha256: sha(fs.readFileSync(options.source)), project: options.projectFile, projectSha256: sha(fs.readFileSync(options.projectFile)), artifacts,
      commands: artifacts.map(item => ({ configuration: item.configuration, startedAt, exitCode: 0, closed: true, expectedArtifact: item.path })) };
    mutate(report); write(options.report, report); return report;
  };
}

test('compile gate accepts fresh isolated two-configuration evidence then rejects altered source bytes', async () => {
  const f = fixture(); const a = adaptersFixture(f, { compile: fakeCompile(f) }); const adapter = a.create(); const request = f.request('COMPILE');
  await adapter.dispatchStage(request); assert.equal((await adapter.runStageGate(request)).status, 'passed');
  bytes(path.join(f.root, f.materials.programSourceRoot, 'test.cpp'), 'changed after compile');
  await assert.rejects(adapter.runStageGate(request));
});

test('compile gate rejects artifacts outside private compile output even with matching bytes and fake size', async () => {
  for (const outside of [true, false]) {
    const f = fixture(); const a = adaptersFixture(f, { compile: fakeCompile(f, report => {
      if (outside) { const file = path.join(f.root, 'production-fixture.dll'); bytes(file, 'not a training build'); report.artifacts[0] = { ...report.artifacts[0], path: file, size: fs.statSync(file).size, sha256: sha(fs.readFileSync(file)) }; }
      else report.artifacts[0].size += 1;
    }) });
    const adapter = a.create(); const request = f.request('COMPILE'); await adapter.dispatchStage(request);
    await assert.rejects(adapter.runStageGate(request));
  }
});
