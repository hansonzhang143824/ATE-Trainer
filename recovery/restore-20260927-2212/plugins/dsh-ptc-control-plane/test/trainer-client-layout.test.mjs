import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { createTrainerStore } from '../client/trainer-state.js';
import { trainerNewAgentChanges, trainerNewWorkflowChanges, trainerAppendStep, trainerMoveStep, trainerFrozenVersionsFor, trainerStepVersion, trainerMatchingEvidence } from '../client/trainer-assets.js';

const tick = () => new Promise(resolve => setImmediate(resolve));
const target = { projectId: 'synthetic-lab', targetKind: 'agent', targetId: 'lab-a' };
const binding = { ...target, sessionId: 'session-a', presetId: 'framework-expert', mode: 'training', bindingSchemaVersion: 1, bindingRevision: 1, selectedRunId: null };

function loadWorkbench() {
  const effects = [];
  const react = {
    createElement: (type, props, ...children) => ({ type, props: { ...props, children } }),
    useSyncExternalStore: (subscribe, snapshot) => snapshot(),
    useEffect: effect => effects.push(effect), useState: init => [typeof init === 'function' ? init() : init, () => {}]
  };
  let exported;
  let code = fs.readFileSync(new URL('../lib/client.js', import.meta.url), 'utf8');
  code = code.replace('exports.apply = apply;', 'exports.trainerTest = { installTrainerWorkbench, TrainerRunDetails, TrainerProjectDialog, TrainerSurfaceMain, TrainerWorkbenchSurface, trainerStatusTone, trainerSurfaceTheme, trainerPreferredTarget, trainerWorkflowDefaultInputText, TRAINER_SURFACE_STYLES_V1, TRAINER_SURFACE_STYLES_V2 };\nexports.apply = apply;');
  vm.runInNewContext(code, {
    window: { __ModuleLoader__: { load: spec => { exported = spec.factory(() => react); } } },
    setInterval, clearInterval, setTimeout, clearTimeout, AbortController, DOMException, crypto: globalThis.crypto
  });
  return { ...exported.trainerTest, effects };
}

function layoutFixture() {
  const active = new Map([
    ['sidebar.workspaces/native-browser', { spec: { name: 'sidebar.workspaces', id: 'native-browser', priority: 0 }, component: 'native-browser' }],
    ['details/native-details', { spec: { name: 'details', id: 'native-details', priority: 0 }, component: 'native-details' }]
  ]);
  const listeners = new Set(); const openCalls = [];
  const winner = name => [...active.values()].filter(entry => entry.spec.name === name).sort((a, b) => (a.spec.priority ?? 0) - (b.spec.priority ?? 0))[0];
  const list = { phase: 'ready', current: 'session-a', byId: { 'session-a': { blank: true } } };
  const ctx = {
    slots: { inject: (name, callback) => callback(), register(spec, component) {
      const key = `${spec.name}/${spec.id}`; assert.equal(active.has(key), false);
      if (['sidebar.workspaces', 'details'].includes(spec.name)) {
        assert.equal([...active.values()].some(entry => entry.spec.name === spec.name && (entry.spec.priority ?? 0) === (spec.priority ?? 0)), false,
          `single slot ${spec.name} already has a registration at priority ${spec.priority ?? 0}`);
      }
      active.set(key, { spec, component }); return () => active.delete(key);
    } },
    sessions: { list: { getSnapshot: () => list, subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); } } },
    layout: { openDetails: () => openCalls.push(list.current) }
  };
  return { ctx, active, list, listeners, openCalls, winner };
}

test('workbench releases public slot registrations; never replaces native conversation', async () => {
  const loaded = loadWorkbench(); const f = layoutFixture();
  const store = createTrainerStore({ api: async (op, args) => {
    if (op === 'bind-session') {
      if (args.sessionId === 'session-a') return binding;
      throw Object.assign(new Error('unbound'), { code: 'session_unbound' });
    }
    return op === 'context' ? { project: { projectId: target.projectId, agents: [], workflows: [] } } : { runs: [] };
  } });
  const dispose = loaded.installTrainerWorkbench(f.ctx, { store });
  assert.equal(f.active.size, 6);
  assert.ok(f.active.has('shell.overlay/trainer-surface'));
  store.enable(); await tick();
  assert.equal(store.getSnapshot().binding.sessionId, 'session-a');
  assert.ok(f.active.has('sidebar.workspaces/trainer-navigation'));
  assert.ok(f.active.has('details/trainer-observer'));
  assert.equal(f.winner('sidebar.workspaces').spec.id, 'trainer-navigation');
  assert.equal(f.winner('details').spec.id, 'trainer-observer');
  assert.equal([...f.active.values()].some(item => ['root', 'conversation', 'conversation.session'].includes(item.spec.name)), false);
  const Details = f.active.get('details/trainer-observer').component;
  Details({ sessionId: 'session-a', useSessions: selector => selector(f.list) });
  loaded.effects.splice(0).forEach(effect => effect());
  assert.equal(f.openCalls.length, 0, 'blank session must not pretend right panel is open');
  f.list.byId['session-a'].blank = false;
  Details({ sessionId: 'session-a', useSessions: selector => selector(f.list) });
  loaded.effects.splice(0).forEach(effect => effect());
  assert.deepEqual(f.openCalls, ['session-a']);
  f.list.current = 'unrelated'; f.listeners.forEach(fn => fn()); await tick();
  assert.equal(f.active.has('details/trainer-observer'), false);
  assert.equal(f.winner('details').component, 'native-details');
  assert.equal(store.getSnapshot().target, null);
  store.enable(false);
  assert.equal(f.active.has('sidebar.workspaces/trainer-navigation'), false);
  assert.equal(f.winner('sidebar.workspaces').component, 'native-browser');
  dispose(); assert.equal(f.active.size, 2); assert.equal(f.listeners.size, 0);
});

test('run controls remain rendered in terminal state and termination is not invented', () => {
  const loaded = loadWorkbench();
  const state = { run: { status: 'cancelled', runId: 'r1', steps: [], cancellationRequested: true, childTerminationConfirmed: null }, events: [], project: {}, busy: false };
  const tree = loaded.TrainerRunDetails({ store: { getSnapshot: () => state, subscribe: () => () => {} } });
  const elements = [];
  function visit(node) { if (Array.isArray(node)) return node.forEach(visit); if (!node || typeof node !== 'object') return; elements.push(node); visit(node.props?.children); }
  visit(tree);
  const controls = elements.filter(node => node.type === 'button' && ['暂停', '继续', '停止'].includes(node.props.children[0]));
  assert.equal(controls.length, 3); assert.ok(controls.every(button => button.props.disabled));
  assert.match(JSON.stringify(tree), /子任务终止尚未确认/);
  assert.match(JSON.stringify(tree), /本次匹配的测试断言 0 项/);
});

test('surface is truthful and run control uses the bound synthetic target', async () => {
  const loaded = loadWorkbench();
  const calls = [];
  const state = { projectId: 'synthetic-lab', mode: 'training', target: { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'lab-pair' }, project: { revisionId: 'revision-test', agents: [{ agentId: 'lab-producer', name: 'Synthetic producer' }], workflows: [{ workflowId: 'lab-pair', name: 'Synthetic producer → consumer', steps: [{ stepId: 'produce', agentId: 'lab-producer' }, { stepId: 'consume', agentId: 'lab-consumer' }] }] }, assets: null, binding: { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'lab-pair', sessionId: 'session-a', presetId: 'agent-trainer', mode: 'training' }, selectedRunId: null, runs: [], nextRunsCursor: null, run: null, events: [], busy: false, error: null, readError: null, notice: '' };
  const store = { getSnapshot: () => state, subscribe: () => () => {}, refresh: () => {}, loadMoreRuns: async () => {}, perform: async (...args) => { calls.push(args); return { runId: 'run-synthetic' }; }, select: () => {} };
  const tree = loaded.TrainerSurfaceMain({ store, navigate: async () => {}, openEditor: () => {}, openDialog: () => {}, diagnose: () => {}, openNative: () => {} });
  const json = JSON.stringify(tree);
  assert.doesNotMatch(json, /先用两位专家验证协作/);
  assert.doesNotMatch(json, /已记录训练指令/);
  assert.match(json, /工作台不复制或伪造对话记录/);
  const elements = []; const visit = node => { if (Array.isArray(node)) return node.forEach(visit); if (!node || typeof node !== 'object') return; elements.push(node); visit(node.props?.children); }; visit(tree);
  const runButton = elements.find(node => node.type === 'button' && node.props.children?.[0] === '运行一次');
  assert.ok(runButton); assert.equal(runButton.props.disabled, false); await runButton.props.onClick();
  assert.equal(calls[0][0], 'run'); assert.equal(JSON.stringify(calls[0][1].input), '{}');
});

test('workbench restores the latest successful target and uses the first workflow test input', () => {
  const loaded = loadWorkbench();
  const project = { workflows: [{ workflowId: 'lab-pair' }, { workflowId: 'offline-coding-flow' }], agents: [] };
  const target = loaded.trainerPreferredTarget('synthetic-lab', project, [
    { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'lab-pair', status: 'failed', updatedAt: '2026-09-27T11:53:10.069Z' },
    { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'offline-coding-flow', status: 'completed', updatedAt: '2026-09-27T10:46:19.201Z' }
  ]);
  assert.deepEqual(JSON.parse(JSON.stringify(target)), { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'offline-coding-flow' });
  const input = loaded.trainerWorkflowDefaultInputText({ projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'lab-pair' }, { files: { 'tests/lab-pair.json': JSON.stringify({ cases: [{ input: { seed: 7 } }] }) } });
  assert.equal(input, '{\n  "seed": 7\n}');
});

test('V2 is the default full-screen theme and keeps V1 CSS fallback plus semantic status tones', () => {
  const loaded = loadWorkbench();
  assert.equal(loaded.trainerStatusTone('completed'), 'complete');
  assert.equal(loaded.trainerStatusTone('running'), 'running');
  assert.equal(loaded.trainerStatusTone('failed'), 'error');
  assert.equal(loaded.trainerStatusTone(undefined), 'idle');
  assert.notEqual(loaded.TRAINER_SURFACE_STYLES_V1, loaded.TRAINER_SURFACE_STYLES_V2);
  assert.match(loaded.TRAINER_SURFACE_STYLES_V2, /data-theme="v2"/);
  assert.match(loaded.TRAINER_SURFACE_STYLES_V2, /trainer-surface-inspector\{[^}]*align-self:stretch/);
  assert.match(loaded.TRAINER_SURFACE_STYLES_V2, /trainer-surface-inspector>\[data-testid="trainer-run-details"\]\{[^}]*justify-content:flex-start/);
  // A long running step/evidence trace must scroll inside the details panel;
  // otherwise the flex item can paint over the sibling candidate status/error.
  assert.match(loaded.TRAINER_SURFACE_STYLES_V2, /trainer-surface-inspector>\[data-testid="trainer-run-details"\]\{[^}]*overflow:auto/);
  const detailSource = loaded.TrainerRunDetails.toString();
  assert.ok(detailSource.indexOf('执行顺序') < detailSource.indexOf('包 SHA-256'));
  const state = { enabled: true, surfaceVisible: true, mode: 'training', target: null, project: null, busy: false };
  const store = { getSnapshot: () => state, subscribe: () => () => {} };
  const tree = loaded.TrainerWorkbenchSurface({ store, navigate: async () => {}, openEditor: () => {}, openDialog: () => {}, diagnose: () => {}, openNative: () => {} });
  assert.equal(tree.props['data-theme'], 'v2');
  assert.equal(tree.props['data-ui-version'], 'V2');
  assert.match(JSON.stringify(tree), /V1 样式/);
});


test('workflow heading does not invent one step while its definition is unavailable', () => {
  const loaded = loadWorkbench();
  const state = { projectId: 'synthetic-lab', mode: 'training', target: { projectId: 'synthetic-lab', targetKind: 'workflow', targetId: 'lab-pair' }, project: { revisionId: 'r1', agents: [], workflows: [{ workflowId: 'lab-pair', name: 'Synthetic producer → consumer' }] }, assets: null, binding: null, selectedRunId: null, runs: [], nextRunsCursor: null, run: null, events: [], busy: false, error: null, readError: null, notice: '' };
  const store = { getSnapshot: () => state, subscribe: () => () => {}, refresh: () => {}, loadMoreRuns: async () => {}, perform: async () => ({ runId: 'run-synthetic' }), select: () => {} };
  const tree = loaded.TrainerSurfaceMain({ store, navigate: async () => {}, openEditor: () => {}, openDialog: () => {}, diagnose: () => {}, openNative: () => {} });
  const json = JSON.stringify(tree);
  assert.match(json, /步骤待读取/);
  assert.doesNotMatch(json, /1 个执行步骤/);
});

test('new agent is one four-file change and repeated steps keep unique ids and mappings', () => {
  const files = trainerNewAgentChanges({ agentId: 'lab-ninth', name: 'Ninth Agent' });
  assert.equal(files.length, 4);
  const agent = JSON.parse(files[0].content);
  assert.ok(files.some(file => file.path === agent.instructionsRef));
  assert.equal(JSON.parse(files[2].content).type, 'object');
  assert.throws(() => trainerNewAgentChanges({ agentId: '../escape', name: 'No' }));
  const generated = JSON.parse(trainerNewWorkflowChanges({ workflowId: 'root-handoff', name: 'Root handoff', firstAgentId: 'a', secondAgentId: 'b' })[0].content);
  assert.deepEqual(generated.steps.map(step => step.inputBindings), [
    { '': { source: 'input', pointer: '' } },
    { '': { source: 'step', stepId: 'step-1', pointer: '' } },
  ]);
  const original = { workflowId: 'repeat', steps: [{ stepId: 'step-1', agentId: 'a', inputBindings: { '/value': { source: 'input', pointer: '/value' } } }] };
  const next = trainerAppendStep(original, 'a');
  assert.equal(next.steps[1].agentId, 'a'); assert.notEqual(next.steps[0].stepId, next.steps[1].stepId);
  const moved = trainerMoveStep(next, 0, 1);
  assert.deepEqual(moved.steps[1].inputBindings, original.steps[0].inputBindings);
  assert.equal(original.steps.length, 1);
});

test('repeated Agent steps select independent frozen versions and preserve references when reordered', () => {
  const versions = [
    { ...target, frozenVersionId: 'v1', revisionId: 'r1', bundleSha256: 'a'.repeat(64) },
    { ...target, frozenVersionId: 'v2', revisionId: 'r2', bundleSha256: 'b'.repeat(64) },
    { ...target, targetId: 'other-agent', frozenVersionId: 'other', revisionId: 'r2' }
  ];
  const flow = { workflowId: 'repeat', steps: [{ stepId: 'one', agentId: 'lab-a', inputBindings: {} }, { stepId: 'two', agentId: 'lab-a', inputBindings: {} }] };
  const one = trainerStepVersion(flow, 'one', 'v1', versions, target.projectId);
  const two = trainerStepVersion(one, 'two', 'v2', versions, target.projectId);
  const moved = trainerMoveStep(two, 0, 1);
  assert.equal(moved.steps[0].agentVersion.frozenVersionId, 'v2');
  assert.equal(moved.steps[1].agentVersion.frozenVersionId, 'v1');
  const candidate = trainerStepVersion(moved, 'one', '', versions, target.projectId);
  assert.equal(candidate.steps[1].agentVersion, undefined);
  assert.equal(candidate.steps[0].agentVersion.frozenVersionId, 'v2');
  assert.throws(() => trainerStepVersion(flow, 'one', 'other', versions, target.projectId), /不属于/);
  assert.throws(() => trainerStepVersion(flow, 'one', 'missing', versions, target.projectId), /不属于/);
  assert.equal(trainerFrozenVersionsFor(versions, target).length, 2);
  assert.equal(flow.steps[0].agentVersion, undefined);
});

test('release evidence must match target and exact bundle, not only candidate revision', () => {
  const version = { ...target, frozenVersionId: 'v1', revisionId: 'r1', bundleSha256: 'a'.repeat(64) };
  const matching = { ...target, status: 'completed', runId: 'good', revisionId: 'r1', bundleSha256: version.bundleSha256 };
  const candidates = [matching, { ...matching, runId: 'other-bundle', bundleSha256: 'b'.repeat(64) }, { ...matching, runId: 'wrong-target', targetId: 'other' }, { ...matching, runId: 'failed', status: 'failed' }];
  assert.deepEqual(trainerMatchingEvidence(candidates, version).map(run => run.runId), ['good']);
});

test('frozen-version panel restores server options without selecting the newest or accepting a free-form ID', () => {
  const loaded = loadWorkbench();
  const versions = [{ ...target, frozenVersionId: 'v1', revisionId: 'r1', bundleSha256: 'a'.repeat(64) }, { ...target, frozenVersionId: 'v2', revisionId: 'r2', bundleSha256: 'b'.repeat(64) }];
  const state = { ...target, target, mode: 'published', runs: [], releases: [], frozenVersions: versions, project: { revisionId: 'r2' } };
  const tree = loaded.TrainerProjectDialog({ store: { getSnapshot: () => state, subscribe: () => () => {} }, kind: 'versions', close() {} });
  const elements = [];
  function visit(node) { if (Array.isArray(node)) return node.forEach(visit); if (!node || typeof node !== 'object') return; elements.push(node); visit(node.props?.children); }
  visit(tree);
  const selector = elements.find(node => node.type === 'select' && node.props['aria-label'] === '冻结版本');
  assert.equal(selector.props.value, '');
  assert.equal(elements.filter(node => node.type === 'input').length, 0);
  const display = JSON.stringify(selector);
  assert.match(display, /v1/); assert.match(display, /v2/); assert.match(display, /agent\/lab-a/); assert.ok(display.includes('a'.repeat(64)));
  const publish = elements.find(node => node.type === 'button' && node.props.children[0] === '生成自包含发布包');
  assert.equal(publish.props.disabled, true);
});
