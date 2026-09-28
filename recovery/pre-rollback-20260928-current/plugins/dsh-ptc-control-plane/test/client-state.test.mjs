import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import vm from 'node:vm';
import * as clientState from '../client/state.js';
import { createPtcStateStore, createTrainingRunRequest, executeTrainingRunRequest, executeBusinessTrainingRunRequest, formatTarget, normalizeState,
  executeTrainingPipelineRequest, executeBusinessPipelineRequest, controlTrainingPipelineRequest, controlBusinessPipelineRequest, parseTrainingTestItems, pipelineTrainingTarget,
  pipelineControlActions, executeFrameworkRehearsalRequest, controlFrameworkRehearsalRequest,
  recoverFrameworkRehearsalRequest, publishFrameworkReleaseRequest,
  executePublishedFrameworkRequest, controlPublishedFrameworkRequest, freezeTrainingReleaseRequest,
  activateTrainingReleaseRequest, createPtcSessionWorkspaceRequest } from '../client/state.js';
import { executeProfileSmokeRequest, stopProfileSmokeRequest,
  executeSimpleOrchestrationRequest, controlSimpleOrchestrationRequest,
  publishTrainingReleaseRequest, executeTrainingReleaseRequest,
  controlTrainingReleaseRequest } from '../client/state.js';

test('client state follows the server schema and formats structured targets', () => {
  const state = normalizeState({
    schemaVersion: 1,
    identity: 'unbound',
    activeRelease: { releaseId: 'r1', manifestDigest: 'a'.repeat(64), activatedAt: 'now' },
    trainingRuns: [{
      runId: 't1', mode: 'training', status: 'created',
      target: { kind: 'profile', profileId: 'ptc-dft-expert' }, updatedAt: 'now',
    }],
    delivery: null,
    profiles: [],
    migration: { legacyConsoleAbandoned: true, legacyMode: 'training', legacyModeAuthoritative: false },
  });
  assert.equal(state.activeRelease.manifestDigest, 'a'.repeat(64));
  assert.equal(formatTarget(state.trainingRuns[0].target), 'ptc-dft-expert');
  assert.equal(state.delivery, null);
});

test('client keeps only explicit run-local issue owner mappings', () => {
  const state = normalizeState({ trainingRuns: [{
    runId: 'pipeline-1', mode: 'training', status: 'blocked',
    target: { kind: 'pipeline', stages: ['INPUT_SYNC'] },
    issueOwners: [
      { sourceRole: 'schematic-expert', profileId: 'ptc-schematic-expert' },
      { sourceRole: null, profileId: 'broken' },
    ],
  }] });
  assert.deepEqual(state.trainingRuns[0].issueOwners,
    [{ sourceRole: 'schematic-expert', profileId: 'ptc-schematic-expert' }]);
});

test('client store revision changes on data and error notifications', async () => {
  let mode = 'ok';
  const store = createPtcStateStore({
    fetchImpl: async () => mode === 'ok'
      ? { ok: true, json: async () => ({
          identity: 'unbound',
          trainingRuns: [{ runId: 't1', mode: 'training', status: 'created', target: null, updatedAt: 'now' }],
          delivery: null,
        }) }
      : { ok: false, status: 500 },
  });
  assert.equal(store.getRevision(), 0);
  await store.refresh();
  assert.equal(store.getRevision(), 1);
  await store.refresh();
  assert.equal(store.getRevision(), 1, 'unchanged payload must not repaint');
  mode = 'error';
  await store.refresh();
  assert.equal(store.getRevision(), 2, 'errors must repaint the panel');
  assert.match(store.getLastError(), /HTTP 500/);
});

test('client training request sends only one explicit training target', async () => {
  let request;
  const result = await createTrainingRunRequest(
    { kind: 'profile', profileId: 'ptc-dft-expert' },
    { fetchImpl: async (url, options) => {
      request = { url, options };
      return { ok: true, json: async () => ({ runId: 'training-001', mode: 'training' }) };
    } },
  );
  assert.equal(request.url, '/api/ptc-control/training-runs');
  assert.equal(request.options.method, 'POST');
  assert.deepEqual(JSON.parse(request.options.body), {
    target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  });
  assert.equal(result.mode, 'training');
});

test('client training execution request binds one run and explicit TM set', async () => {
  let request;
  const result = await executeTrainingRunRequest('training-001', ['TM109'], {
    fetchImpl: async (url, options) => {
      request = { url, options };
      return { ok: true, json: async () => ({ runId: 'training-001', status: 'completed', outcome: { mode: 'UNCHANGED' } }) };
    },
  });
  assert.equal(request.url, '/api/ptc-control/training-runs/execute');
  assert.deepEqual(JSON.parse(request.options.body), { runId: 'training-001', testItems: ['TM109'] });
  assert.equal(result.outcome.mode, 'UNCHANGED');
});

test('pipeline creation keeps a range target; execution has a dedicated training endpoint', async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, ...options });
    return { ok: true, status: 202, json: async () => ({ runId: 'pipeline-1', status: 'preparing', outcome: null }) };
  };
  const target = pipelineTrainingTarget(['INPUT_SYNC', 'STRATEGY', 'COMPILE'], 'INPUT_SYNC', 'COMPILE');
  await createTrainingRunRequest(target, { fetchImpl });
  const execution = await executeTrainingPipelineRequest('pipeline-1', ['TM109', 'TM110'], { fetchImpl });
  assert.deepEqual(JSON.parse(calls[0].body), { target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' } });
  assert.equal(calls[1].url, '/api/ptc-control/training-pipelines/execute');
  assert.equal(calls[1].credentials, 'same-origin');
  assert.equal(calls[1].method, 'POST');
  assert.deepEqual(JSON.parse(calls[1].body), { runId: 'pipeline-1', testItems: ['TM109', 'TM110'] });
  assert.equal(execution.status, 'preparing', '202 acceptance is not completion');
});

test('real pipeline training sends its explicit model choice without changing rehearsal payloads', async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => ({ runId: 'pipeline-model', status: 'preparing' }) };
  };
  await executeTrainingPipelineRequest('pipeline-model', ['TM109'], { fetchImpl, modelChoice: 'deepseek-v4-flash' });
  await executeFrameworkRehearsalRequest('rehearsal-model', ['TM109'], { fetchImpl });
  assert.deepEqual(calls, [
    { url: '/api/ptc-control/training-pipelines/execute', body: { runId: 'pipeline-model', testItems: ['TM109'], modelChoice: 'deepseek-v4-flash' } },
    { url: '/api/ptc-control/framework-rehearsals/execute', body: { runId: 'rehearsal-model', testItems: ['TM109'] } },
  ]);
});

test('business training helpers use explicit BUSINESS_ONLY endpoints', async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body) });
    return { ok: true, status: 202, json: async () => ({ runId: 'business-1', status: 'preparing', mode: 'BUSINESS_ONLY' }) };
  };
  await executeBusinessTrainingRunRequest('business-dft', ['TM109'], { fetchImpl, modelChoice: 'deepseek-v4-flash' });
  await executeBusinessPipelineRequest('business-pipeline', ['TM109'], { fetchImpl, modelChoice: 'deepseek-v4-flash' });
  await controlBusinessPipelineRequest('business-pipeline', 'stop', { fetchImpl });
  assert.deepEqual(calls, [
    { url: '/api/ptc-control/business/training-runs/execute', body: { runId: 'business-dft', testItems: ['TM109'], modelChoice: 'deepseek-v4-flash' } },
    { url: '/api/ptc-control/business/training-pipelines/execute', body: { runId: 'business-pipeline', testItems: ['TM109'], modelChoice: 'deepseek-v4-flash' } },
    { url: '/api/ptc-control/business/training-pipelines/control', body: { runId: 'business-pipeline', action: 'stop' } },
  ]);
});

test('pipeline controls send only explicit supported actions and surface host rejection', async () => {
  for (const action of ['pause', 'resume', 'stop']) {
    await controlTrainingPipelineRequest('pipeline-1', action, { fetchImpl: async (url, options) => {
      assert.equal(url, '/api/ptc-control/training-pipelines/control');
      assert.deepEqual(JSON.parse(options.body), { runId: 'pipeline-1', action });
      return { ok: true, json: async () => ({ status: 'accepted' }) };
    } });
  }
  await assert.rejects(controlTrainingPipelineRequest('pipeline-1', 'publish', { fetchImpl: () => assert.fail('must not fetch') }), /不支持/);
  await assert.rejects(executeTrainingPipelineRequest('pipeline-1', ['TM109'], { fetchImpl: async () => ({
    ok: false, status: 409, json: async () => ({ detail: 'pipeline interrupted; reconcile receipts' }),
  }) }), /reconcile receipts/);
});

test('framework rehearsal uses a separate purpose and execution/control routes', async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => ({ runId: 'rehearsal-1', status: 'preparing' }) };
  };
  const target = pipelineTrainingTarget(['INPUT_SYNC', 'COMPILE'], 'INPUT_SYNC', 'COMPILE');
  await createTrainingRunRequest(target, { purpose: 'framework-rehearsal', fetchImpl });
  await executeFrameworkRehearsalRequest('rehearsal-1', ['TM109'], { fetchImpl });
  await controlFrameworkRehearsalRequest('rehearsal-1', 'pause', { fetchImpl });
  await recoverFrameworkRehearsalRequest('rehearsal-1', { fetchImpl });
  await publishFrameworkReleaseRequest('rehearsal-1', { fetchImpl });
  assert.deepEqual(calls, [
    { url: '/api/ptc-control/training-runs', body: { target, purpose: 'framework-rehearsal' } },
    { url: '/api/ptc-control/framework-rehearsals/execute', body: { runId: 'rehearsal-1', testItems: ['TM109'] } },
    { url: '/api/ptc-control/framework-rehearsals/control', body: { runId: 'rehearsal-1', action: 'pause' } },
    { url: '/api/ptc-control/framework-rehearsals/recover', body: { runId: 'rehearsal-1' } },
    { url: '/api/ptc-control/framework-releases/publish', body: { sourceRunId: 'rehearsal-1' } },
  ]);
  assert.equal(normalizeState({ trainingRuns: [{ purpose: 'framework-rehearsal' }] }).trainingRuns[0].purpose, 'framework-rehearsal');
});

test('published framework UI sends no mutable release, TM, or stage fields', async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => ({ runId: 'framework-run-1', releaseId: 'framework-1' }) };
  };
  await executePublishedFrameworkRequest({ fetchImpl });
  await controlPublishedFrameworkRequest('framework-run-1', 'pause', { fetchImpl });
  assert.deepEqual(calls, [
    { url: '/api/ptc-control/framework-releases/execute', body: {} },
    { url: '/api/ptc-control/framework-releases/control', body: { runId: 'framework-run-1', action: 'pause' } },
  ]);
  await assert.rejects(controlPublishedFrameworkRequest('framework-run-1', 'edit', { fetchImpl }), /不支持/);
  const runs = normalizeState({ publishedFrameworkRuns: [{ runId: 'framework-run-1', releaseId: 'framework-1', status: 'completed', stages: [] }] }).publishedFrameworkRuns;
  assert.equal(runs[0].releaseId, 'framework-1');
});

test('smoke UI requests keep eight profile sources and TM109 bound to fixed native routes', async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body) });
    return { ok: true, status: 202, json: async () => ({ runId: 'accepted', status: 'running' }) };
  };
  const profiles = { 'ptc-dft-expert': 'smoke-dft', 'ptc-schematic-expert': 'smoke-schematic',
    'strategy-expert': 'smoke-strategy', 'method-expert': 'smoke-method',
    'rule-reviewer': 'smoke-review', 'ate-implementer': 'smoke-implement',
    'compile-diagnostician': 'smoke-compile', 'evolution-expert': 'smoke-evolution' };
  await executeProfileSmokeRequest('smoke-strategy', { fetchImpl });
  await stopProfileSmokeRequest('smoke-strategy', { fetchImpl });
  await executeSimpleOrchestrationRequest('pipeline-1', profiles, { fetchImpl });
  await executeSimpleOrchestrationRequest('pilot-1', Object.fromEntries(Object.entries(profiles).slice(0, 2)),
    { fetchImpl, pilot: true });
  await controlSimpleOrchestrationRequest('pipeline-1', 'pause', { fetchImpl });
  await publishTrainingReleaseRequest(profiles, 'pipeline-1', { fetchImpl });
  await executeTrainingReleaseRequest({ fetchImpl });
  await controlTrainingReleaseRequest('published-1', 'stop', { fetchImpl });
  assert.deepEqual(calls, [
    { url: '/api/ptc-control/profile-smoke/execute', body: { runId: 'smoke-strategy' } },
    { url: '/api/ptc-control/profile-smoke/stop', body: { runId: 'smoke-strategy' } },
    { url: '/api/ptc-control/simple-orchestration/execute', body: {
      runId: 'pipeline-1', testItems: ['TM109'], profileRunIds: profiles } },
    { url: '/api/ptc-control/simple-orchestration/execute', body: {
      runId: 'pilot-1', testItems: ['TM109'], profileRunIds: {
        'ptc-dft-expert': 'smoke-dft', 'ptc-schematic-expert': 'smoke-schematic' }, pilot: true } },
    { url: '/api/ptc-control/simple-orchestration/control', body: { runId: 'pipeline-1', action: 'pause' } },
    { url: '/api/ptc-control/training-release/publish', body: { profileRunIds: profiles, pipelineRunId: 'pipeline-1' } },
    { url: '/api/ptc-control/training-release/execute', body: { testItems: ['TM109'] } },
    { url: '/api/ptc-control/training-release/control', body: { runId: 'published-1', action: 'stop' } },
  ]);
  assert.throws(() => controlTrainingReleaseRequest('published-1', 'resume', { fetchImpl }), /仅支持停止/);
});

test('freeze, publish activation, and native session workspace use separate constrained requests', async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body) });
    return { ok: true, json: async () => url.endsWith('/session-workspace')
      ? { path: 'D:/ptc/isolated' } : { status: 'frozen-unpublished' } };
  };
  const profiles = { 'ptc-dft-expert': 'dft', 'ptc-schematic-expert': 'schematic', strategy: 's', method: 'm',
    review: 'r', implement: 'i', compile: 'c', evolution: 'e' };
  await freezeTrainingReleaseRequest(profiles, 'pipeline-1', { fetchImpl });
  await activateTrainingReleaseRequest('stage-00000000-0000-4000-8000-000000000000', { fetchImpl });
  await createPtcSessionWorkspaceRequest({ mode: 'agent', profileId: 'ptc-dft-expert' }, { fetchImpl });
  assert.deepEqual(calls, [
    { url: '/api/ptc-control/training-release/freeze', body: { profileRunIds: profiles, pipelineRunId: 'pipeline-1' } },
    { url: '/api/ptc-control/training-release/activate', body: { stagingId: 'stage-00000000-0000-4000-8000-000000000000' } },
    { url: '/api/ptc-control/session-workspace', body: { mode: 'agent', profileId: 'ptc-dft-expert' } },
  ]);
  await assert.rejects(createPtcSessionWorkspaceRequest({ mode: 'agent', profileId: '../private' }, {
    fetchImpl: async () => ({ ok: true, json: async () => ({}) }),
  }), /未返回安全/);
});

test('normalization preserves smoke progress and frozen training release status', () => {
  const simpleOrchestration = { status: 'running', stages: [{ stage: 'INPUT_SYNC', status: 'completed' }],
    smokePassed: false, businessGatePassed: false };
  const state = normalizeState({
    activeTrainingRelease: { releaseId: 'training-release-1', manifestDigest: 'a'.repeat(64), activatedAt: 'now' },
    publishedSmokeRuns: [{ runId: 'published-1', releaseId: 'training-release-1', status: 'running',
      outcome: { mode: 'SMOKE_ONLY', businessGatePassed: false } }],
    trainingRuns: [{ runId: 'pipeline-1', status: 'running', purpose: 'smoke-training',
      target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' }, simpleOrchestration }],
  });
  assert.equal(state.activeTrainingRelease.releaseId, 'training-release-1');
  assert.equal(state.publishedSmokeRuns[0].outcome.businessGatePassed, false);
  assert.deepEqual(state.trainingRuns[0].simpleOrchestration, simpleOrchestration);
});

test('TM parsing accepts comma lists and never silently drops invalid text', () => {
  assert.deepEqual(parseTrainingTestItems(' tm109，TM110,tm109、 TM111 '), ['TM109', 'TM110', 'TM111']);
  for (const value of ['', 'TM109-TM110', 'TM109,wrong', '109', null]) assert.throws(() => parseTrainingTestItems(value));
  assert.throws(() => pipelineTrainingTarget(['INPUT_SYNC', 'METHOD'], 'METHOD', 'INPUT_SYNC'));
  assert.throws(() => pipelineTrainingTarget([], 'INPUT_SYNC', 'COMPILE'));
});

test('pipeline controls never resume interrupted or terminal runs automatically', () => {
  assert.deepEqual(pipelineControlActions('preparing'), ['pause', 'stop']);
  assert.deepEqual(pipelineControlActions('running'), ['pause', 'stop']);
  assert.deepEqual(pipelineControlActions('pausing'), ['stop']);
  assert.deepEqual(pipelineControlActions('paused'), ['resume', 'stop']);
  for (const status of ['interrupted', 'completed', 'blocked', 'cancelled', 'unknown']) assert.deepEqual(pipelineControlActions(status), []);
});

test('normalization preserves pipeline progress, failure reason and actual gate evidence', () => {
  const gateResult = { status: 'failed', exitCode: 2, gate: 'scripts/check.py', receiptPath: 'run/verification/gate.json' };
  const state = normalizeState({ pipelineStages: ['INPUT_SYNC', 'METHOD', 'COMPLETE', null], trainingRuns: [{
    runId: 'r1', status: 'blocked', target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'METHOD' },
    pipeline: { runId: 'r1', status: 'blocked', reason: 'source hash mismatch', stages: [{ stage: 'METHOD', status: 'blocked', gateResult }] },
  }] });
  assert.deepEqual(state.pipelineStages, ['INPUT_SYNC', 'METHOD']);
  assert.equal(state.trainingRuns[0].pipeline.reason, 'source hash mismatch');
  assert.deepEqual(state.trainingRuns[0].pipeline.stages[0].gateResult, gateResult);
  assert.equal(formatTarget(state.trainingRuns[0].target), 'INPUT_SYNC→METHOD');
  assert.equal(normalizeState({ trainingRuns: [{}] }).trainingRuns[0].pipeline, null);
});

test('panel exposes experimental pipeline controls but never a blind interrupted resume', () => {
  // Render the source with minimal hook/element doubles; no build output or
  // browser is changed and no network/expert dispatch is performed.
  const source = fs.readFileSync(new URL('../client/panel.js', import.meta.url), 'utf8')
    .replace(/^import[\s\S]*?;\s*/gm, '').replace(/export function /g, 'function ');
  const context = {
    ...clientState, DraftEditor() {}, TrainingIssueEditor() {}, useEffect() {}, useSyncExternalStore() {},
    useState: value => [value, () => {}],
    createElement: (type, props, ...children) => ({ type, props: props ?? {}, children }),
  };
  vm.createContext(context);
  vm.runInContext(`${source}\nthis.renderTraining = TrainingView;`, context);
  const runs = ['preparing', 'pausing', 'paused', 'interrupted', 'blocked'].map(status => ({
    runId: status, status, mode: 'training', target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' },
    pipeline: { runId: status, status, reason: 'fixture reason', stages: [{ stage: 'INPUT_SYNC', status: 'pending' }] },
  }));
  runs.push({ runId: 'framework-done', status: 'completed', mode: 'training', purpose: 'framework-rehearsal',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' },
    pipeline: { runId: 'framework-done', status: 'completed', stages: [] } });
  runs.push({ runId: 'framework-interrupted', status: 'interrupted', mode: 'training', purpose: 'framework-rehearsal',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' },
    pipeline: { runId: 'framework-interrupted', status: 'interrupted', stages: [] } });
  const state = normalizeState({ profiles: [{ profileId: 'ptc-dft-expert' }], pipelineStages: ['INPUT_SYNC', 'COMPILE'], trainingRuns: runs });
  const tree = context.renderTraining({ state, store: {}, t: value => value });
  const nodes = [];
  function walk(value) {
    if (Array.isArray(value)) return value.forEach(walk);
    if (!value || typeof value !== 'object') return;
    nodes.push(value); value.children?.forEach(walk);
  }
  walk(tree);
  const pipelineButton = nodes.find(node => node.props['data-testid'] === 'ptc-cp-create-pipeline-training');
  assert.equal(pipelineButton.props.disabled, true);
  assert.match(pipelineButton.children.join(''), /已存档/);
  const statisticButton = nodes.find(node => node.props['data-testid'] === 'ptc-cp-create-schematic-statistic-only');
  assert.equal(statisticButton.props.disabled, true);
  assert.match(statisticButton.children.join(''), /Component-Statistic/);
  assert.equal(nodes.find(node => node.props['data-testid'] === 'ptc-cp-create-profile-training').props.disabled, true);
  const rehearsalButton = nodes.find(node => node.props['data-testid'] === 'ptc-cp-create-framework-rehearsal');
  assert.equal(rehearsalButton.props.disabled, true);
  assert.match(rehearsalButton.children.join(''), /已存档/);
  const labels = nodes.filter(node => node.type === 'button').map(node => node.props['aria-label']);
  assert.ok(labels.includes('pause preparing'));
  assert.ok(labels.includes('stop pausing'));
  assert.ok(labels.includes('resume paused'));
  assert.ok(!labels.includes('resume interrupted'));
  assert.ok(!labels.includes('resume blocked'));
  assert.ok(nodes.some(node => node.props['data-testid'] === 'ptc-cp-publish-framework-framework-done'));
  assert.ok(nodes.some(node => node.props['data-testid'] === 'ptc-cp-recover-framework-framework-interrupted'));
  assert.equal(nodes.find(node => node.props['data-testid'] === 'ptc-cp-pipeline-from').props.value, 'INPUT_SYNC');
  assert.equal(nodes.find(node => node.props['data-testid'] === 'ptc-cp-pipeline-to').props.value, 'COMPILE');
});

test('smoke panel enables the full chain only from completed local source receipts', () => {
  const source = fs.readFileSync(new URL('../client/panel.js', import.meta.url), 'utf8')
    .replace(/^import[\s\S]*?;\s*/gm, '').replace(/export function /g, 'function ');
  const context = { ...clientState, DraftEditor() {}, TrainingIssueEditor() {}, useEffect() {}, useSyncExternalStore() {},
    useState: value => [value, () => {}],
    createElement: (type, props, ...children) => ({ type, props: props ?? {}, children }) };
  vm.createContext(context);
  vm.runInContext(`${source}\nthis.renderSmoke = SmokeTrainingControls; this.renderRuntime = RuntimeView;`, context);
  const profileIds = ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert', 'method-expert', 'rule-reviewer', 'ate-implementer',
    'compile-diagnostician', 'evolution-expert'];
  const runs = profileIds.map((profileId, index) => ({ runId: `profile-${index}`, status: 'completed',
    purpose: 'smoke-training', target: { kind: 'profile', profileId },
    outcome: { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false }, updatedAt: `2026-09-23T00:00:0${index}Z` }));
  const profileBindings = Object.fromEntries(profileIds.map((profileId, index) => [profileId,
    { profileId, profileVersion: `draft-profile-${index}` }]));
  runs.push({ runId: 'pipeline-1', status: 'completed', purpose: 'smoke-training',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' },
    outcome: { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false },
    simpleOrchestration: { profileBindings } });
  const state = normalizeState({ profiles: profileIds.map(profileId => ({ profileId })), trainingRuns: runs,
    activeTrainingRelease: { releaseId: 'release-1' },
    publishedSmokeRuns: [{ runId: 'published-1', releaseId: 'release-1', status: 'running' }] });
  const flatten = root => {
    const nodes = [];
    const walk = value => { if (Array.isArray(value)) return value.forEach(walk);
      if (!value || typeof value !== 'object') return; nodes.push(value); value.children?.forEach(walk); };
    walk(root); return nodes;
  };
  const nodes = flatten(context.renderSmoke({ state, store: {} }));
  for (const profileId of profileIds) assert.equal(nodes.find(node => node.props['data-testid'] ===
    `ptc-cp-smoke-profile-${profileId}`).props.disabled, false);
  assert.equal(nodes.find(node => node.props['data-testid'] === 'ptc-cp-start-simple-orchestration').props.disabled, false);
  assert.equal(nodes.find(node => node.props['data-testid'] === 'ptc-cp-publish-training-release').props.disabled, false);
  const runtime = flatten(context.renderRuntime({ state, store: {}, t: value => value }));
  assert.equal(runtime.find(node => node.props['data-testid'] === 'ptc-cp-execute-training-release').props.disabled, false);
  assert.ok(runtime.some(node => node.props['data-testid'] === 'ptc-cp-stop-training-release-published-1'));
});

test('a completed two-expert pilot is never selected as the publishable full-chain source', () => {
  const source = fs.readFileSync(new URL('../client/panel.js', import.meta.url), 'utf8')
    .replace(/^import[\s\S]*?;\s*/gm, '').replace(/export function /g, 'function ');
  const context = {};
  vm.createContext(context);
  vm.runInContext(`${source}\nthis.smokeSourcesForTest = smokeSources;`, context);
  const runs = ['ptc-dft-expert', 'ptc-schematic-expert'].map((profileId, index) => ({
    runId: `training-profile-${index}`, status: 'completed', purpose: 'smoke-training',
    target: { kind: 'profile', profileId },
    outcome: { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false },
  }));
  runs.push({ runId: 'training-pilot', status: 'completed', purpose: 'smoke-training',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' },
    outcome: { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false },
    simpleOrchestration: { scope: 'INPUT_SYNC_PILOT', profileBindings: {
      'dft-expert': { profileId: 'ptc-dft-expert', profileVersion: 'draft-training-profile-0' },
      'schematic-expert': { profileId: 'ptc-schematic-expert', profileVersion: 'draft-training-profile-1' },
    } },
  });
  const sources = context.smokeSourcesForTest(runs);
  assert.equal(sources.profileRunIds['ptc-dft-expert'], 'training-profile-0');
  assert.equal(sources.profileRunIds['ptc-schematic-expert'], 'training-profile-1');
  assert.equal(sources.pipelineRunId, null);
  assert.deepEqual(Object.keys(sources.pipelineProfileRunIds), []);
});

test('a newer unfinished trial never falls back to an old smoke source', () => {
  const source = fs.readFileSync(new URL('../client/panel.js', import.meta.url), 'utf8')
    .replace(/^import[\s\S]*?;\s*/gm, '').replace(/export function /g, 'function ');
  const context = {};
  vm.createContext(context);
  vm.runInContext(`${source}\nthis.smokeSourcesForTest = smokeSources;`, context);
  const good = { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false };
  const runs = [
    { runId: 'training-20260923-old-profile', purpose: 'smoke-training', status: 'completed',
      target: { kind: 'profile', profileId: 'evolution-expert' }, outcome: good },
    { runId: 'training-20260924-new-profile', purpose: 'smoke-training', status: 'running',
      target: { kind: 'profile', profileId: 'evolution-expert' } },
    { runId: 'training-20260923-old-pipeline', purpose: 'smoke-training', status: 'completed',
      target: { kind: 'pipeline', toStage: 'COMPILE' }, outcome: good,
      simpleOrchestration: { profileBindings: {} } },
    { runId: 'training-20260924-new-pipeline', purpose: 'smoke-training', status: 'running',
      target: { kind: 'pipeline', toStage: 'COMPILE' } },
  ];
  const sources = context.smokeSourcesForTest(runs);
  assert.equal(sources.profileRunIds['evolution-expert'], undefined);
  assert.equal(sources.pipelineRunId, null);
});

test('legacy PTC stage buttons remain constrained while template control is separate', () => {
  const source = fs.readFileSync(new URL('../client/panel.js', import.meta.url), 'utf8')
    .replace(/^import[\s\S]*?;\s*/gm, '').replace(/export function /g, 'function ');
  const ids = ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert', 'method-expert',
    'rule-reviewer', 'ate-implementer', 'compile-diagnostician', 'evolution-expert'];
  const good = { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false };
  const trainingRuns = ids.map((profileId, index) => ({
    runId: `training-profile-${index}`, purpose: 'smoke-training', status: 'completed',
    target: { kind: 'profile', profileId }, outcome: good,
  }));
  trainingRuns.push({ runId: 'training-pilot', purpose: 'smoke-training', status: 'completed',
    target: { kind: 'pipeline', toStage: 'INPUT_SYNC' }, outcome: good,
    simpleOrchestration: { scope: 'INPUT_SYNC_PILOT', stages: [] } });
  const flatten = root => {
    const nodes = [];
    const walk = value => { if (Array.isArray(value)) return value.forEach(walk);
      if (!value || typeof value !== 'object') return; nodes.push(value); value.children?.forEach(walk); };
    walk(root); return nodes;
  };
  const buttons = (selected, mode = 'training') => {
    let stateCall = 0;
    const context = { ...clientState, DraftEditor() {}, useEffect() {},
      workflowStatusSummary: () => ({ completed: 0, total: 0, currentProfileId: null, currentStatus: null, handoffFrom: null }),
      window: { localStorage: { getItem: () => null } },
      useState: value => { stateCall += 1; return [stateCall === 1 ? mode : stateCall === 2 ? 'workflow'
        : stateCall === 4 ? selected : typeof value === 'function' ? value() : value, () => {}]; },
      createElement: (type, props, ...children) => ({ type, props: props ?? {}, children }) };
    vm.createContext(context);
    vm.runInContext(`${source}\nthis.renderWorkbench = PtcWorkbench;`, context);
    const nodes = flatten(context.renderWorkbench({ state: { trainingRuns, activeTrainingRelease: null },
      store: {}, sessionServices: {} }));
    return Object.fromEntries(nodes.filter(node => node.props['data-testid'])
      .map(node => [node.props['data-testid'], node]));
  };
  const pair = buttons(ids.slice(0, 2));
  assert.equal(pair['ptc-cp-start-input-sync-pilot'].props.disabled, false);
  assert.equal(pair['ptc-cp-start-simple-orchestration'].props.disabled, true);
  const all = buttons(ids);
  assert.equal(all['ptc-cp-start-input-sync-pilot'].props.disabled, true);
  assert.equal(all['ptc-cp-start-simple-orchestration'].props.disabled, false);
  const partial = buttons(ids.slice(0, 3));
  assert.equal(partial['ptc-cp-start-input-sync-pilot'].props.disabled, true);
  assert.equal(partial['ptc-cp-start-simple-orchestration'].props.disabled, true);
  assert.ok(buttons(ids.slice(0, 3), 'publish')['ptc-cp-template-publish']);
  assert.ok(buttons(ids.slice(0, 3), 'engineering')['ptc-cp-template-engineering']);
});
