import test from 'node:test';
import assert from 'node:assert/strict';
import { createTrainerApi, createTrainerStore, trainerControlState, TRAINER_UNBOUND_NOTICE } from '../client/trainer-state.js';
import { createTrainerNavigator, trainerNativeKey, trainerPreset } from '../client/trainer-native.js';

const tick = () => new Promise(resolve => setImmediate(resolve));
const target = { projectId: 'synthetic-lab', targetKind: 'agent', targetId: 'lab-a' };
const nativeModelSelection = { provider: 'deepseek-official', model: 'deepseek-v4-flash' };
const deferred = () => { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; };

test('Trainer HTTP preserves structured conflict and abort signal', async () => {
  let captured;
  const signal = new AbortController().signal;
  const api = createTrainerApi({ fetchImpl: async (url, options) => {
    captured = { url, options };
    return { ok: false, status: 409, json: async () => ({ ok: false, error: { code: 'REVISION_CONFLICT', message: 'stale', details: { revisionId: 'r2' } } }) };
  } });
  await assert.rejects(api('apply-changes', { requestId: 'request-1' }, { signal }), e => e.code === 'REVISION_CONFLICT' && e.details.revisionId === 'r2');
  assert.equal(captured.options.signal, signal);
  assert.equal(captured.url, '/api/ptc-control/trainer/apply-changes');
  assert.equal(JSON.parse(captured.options.body).requestId, 'request-1');
});

test('late run response cannot replace a newly selected target; stop aborts reads', async () => {
  const old = deferred();
  let oldSignal;
  const store = createTrainerStore({ api: async (op, args, opts) => {
    if (op === 'context') return { project: { revisionId: args.targetId ?? 'initial' } };
    if (op === 'runs' && args.runId === 'old-run') { oldSignal = opts.signal; return old.promise; }
    if (op === 'runs') return { runs: [] };
    return { events: [] };
  } });
  store.enable(); await tick();
  store.select(target, 'training', 'old-run'); await tick();
  store.select({ ...target, targetId: 'lab-b' }); await tick();
  assert.equal(oldSignal.aborted, true);
  old.resolve({ runId: 'old-run', projectId: target.projectId, revisionId: 'old' }); await tick();
  assert.equal(store.getSnapshot().target.targetId, 'lab-b');
  assert.equal(store.getSnapshot().run, null);
  assert.equal(store.getSnapshot().project.revisionId, 'lab-b');
  store.dispose();
});

test('control availability is authoritative including unknown cancellation', () => {
  assert.equal(trainerControlState({ status: 'running' }, 'stop').allowed, false);
  assert.equal(trainerControlState({ status: 'completed', controls: { stop: { allowed: false, reason: 'terminal' } } }, 'stop').reason, 'terminal');
  assert.equal(trainerControlState({ controls: { pause: { allowed: true, reason: 'step boundary' } } }, 'pause').allowed, true);
});

test('accepted binding clears only obsolete unbound notice and preserves actual errors', () => {
  const store = createTrainerStore({ api: async () => { throw new Error('No request expected'); } });
  store.select(target);
  store.update({ notice: TRAINER_UNBOUND_NOTICE, error: '实际操作失败', readError: '真实读取失败' });
  const binding = { ...target, sessionId: 'known', mode: 'training', presetId: 'framework-expert', bindingSchemaVersion: 1, bindingRevision: 1 };
  assert.equal(store.setBinding({ ...binding, targetId: 'other-target' }), false);
  assert.equal(store.getSnapshot().notice, TRAINER_UNBOUND_NOTICE);
  assert.equal(store.setBinding(binding), true);
  assert.equal(store.getSnapshot().notice, '');
  assert.equal(store.getSnapshot().error, '实际操作失败');
  assert.equal(store.getSnapshot().readError, '真实读取失败');
  store.update({ notice: '已受理运行 run-1，以运行终态为准' });
  store.setBinding(binding);
  assert.equal(store.getSnapshot().notice, '已受理运行 run-1，以运行终态为准');
  store.dispose();
});

test('uncertain mutation retry retains request id; accepted next run gets a new id', async () => {
  const requests = [];
  const store = createTrainerStore({ api: async (op, args) => {
    requests.push(args.requestId);
    if (requests.length === 1) throw new TypeError('network disconnected after acceptance');
    return { runId: `run-${requests.length}` };
  } });
  store.select(target);
  await assert.rejects(store.perform('run', { input: {} }));
  await store.perform('run', { input: {} });
  await store.perform('run', { input: {} });
  assert.equal(requests[0], requests[1]);
  assert.notEqual(requests[1], requests[2]);
  store.dispose();
});

test('event cursor advances without losing earlier events and resets for another run', async () => {
  const cursors = [];
  const store = createTrainerStore({ api: async (op, args) => {
    if (op === 'context') return { project: { revisionId: 'r1' } };
    if (op === 'runs') return args.runId ? { runId: args.runId, projectId: target.projectId } : { runs: [] };
    cursors.push(args.cursor);
    return { runId: args.runId, events: [{ seq: args.cursor + 1, type: 'observed' }], cursor: args.cursor + 1 };
  } });
  store.enable(); await tick();
  store.select(target, 'training', 'run-a'); await tick();
  await store.refresh();
  assert.deepEqual(cursors, [0, 1]);
  assert.deepEqual(store.getSnapshot().events.map(event => event.seq), [1, 2]);
  store.select(target, 'training', 'run-b'); await tick();
  assert.equal(cursors.at(-1), 0);
  assert.equal(store.getSnapshot().events.length, 1);
  store.dispose();
});

test('chat-started run is followed only through the verified server binding', async () => {
  const bound = { ...target, sessionId: 'trainer', presetId: 'agent-trainer', mode: 'training', bindingSchemaVersion: 1, bindingRevision: 2, selectedRunId: 'chat-run' };
  const store = createTrainerStore({ api: async (op, args) => {
    if (op === 'bind-session') return bound;
    if (op === 'context') return { project: { revisionId: 'r1' } };
    if (op === 'runs') return args.runId ? { runId: args.runId, projectId: target.projectId } : { runs: [{ runId: 'unrelated-newer-run' }] };
    return { runId: args.runId, events: [], cursor: 0 };
  } });
  store.enable(); await tick();
  store.select(target, 'training', 'old-run'); await tick();
  store.setBinding({ ...bound, selectedRunId: 'old-run', bindingRevision: 1 });
  await store.refresh(); await tick();
  assert.equal(store.getSnapshot().selectedRunId, 'chat-run');
  assert.equal(store.getSnapshot().run.runId, 'chat-run');
  assert.equal(store.getSnapshot().binding.bindingRevision, 2);
  store.dispose();
});

test('fresh workbench restores frozen metadata from context without a prior local freeze', async () => {
  const version = { frozenVersionId: 'stable-version', targetKind: 'agent', targetId: target.targetId, revisionId: 'r1', bundleSha256: 'a'.repeat(64) };
  const calls = [];
  const store = createTrainerStore({ api: async op => {
    calls.push(op);
    return op === 'context' ? { project: { revisionId: 'r2' }, frozenVersions: [version] } : { runs: [] };
  } });
  store.enable(); await tick();
  assert.equal(store.getSnapshot().frozenVersion, undefined);
  assert.deepEqual(store.getSnapshot().frozenVersions, [{ projectId: target.projectId, ...version }]);
  assert.equal(calls.includes('freeze'), false);
  store.dispose();
});


test('selected workflow loads its real asset definition and step count', async () => {
  const workflow = {
    workflowId: 'lab-pair', name: 'Synthetic producer → consumer',
    steps: [
      { stepId: 'produce', agentId: 'lab-producer' },
      { stepId: 'consume', agentId: 'lab-consumer' }
    ]
  };
  const calls = [];
  const store = createTrainerStore({ api: async (op, args) => {
    calls.push({ op, args });
    if (op === 'context') return { project: { projectId: 'synthetic-lab', revisionId: 'r1', agents: [], workflows: [{ workflowId: workflow.workflowId, name: workflow.name }] } };
    if (op === 'assets') return { projectId: 'synthetic-lab', revisionId: 'r1', files: { [`workflows/${workflow.workflowId}.json`]: JSON.stringify(workflow) } };
    return { runs: [] };
  } });
  store.enable(); await tick();
  store.select({ projectId: 'synthetic-lab', targetKind: 'workflow', targetId: workflow.workflowId });
  await tick(); await tick();
  const state = store.getSnapshot();
  const assetCall = calls.find(call => call.op === 'assets');
  assert.deepEqual(assetCall?.args.paths, [`workflows/${workflow.workflowId}.json`]);
  assert.equal(state.project.workflows[0].steps.length, 2);
  assert.equal(JSON.parse(state.assets.files[`workflows/${workflow.workflowId}.json`]).steps.length, 2);
  store.dispose();
});

function nativeFixture({ remembered = null, apiOverride, listOverride = {}, refreshOverride = null } = {}) {
  const listeners = new Set();
  const values = new Map();
  const list = { phase: 'ready', listState: 'idle', listError: null, byId: remembered ? { [remembered]: { id: remembered } } : {}, current: undefined, ...listOverride };
  const opened = []; const created = []; const calls = []; const modelCalls = [];
  const services = {
    sessions: { list: { getSnapshot: () => list, subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); } },
      binding: () => ({ session: { rename: async () => {} } }), open: id => { opened.push(id); list.current = id; } },
    workspaces: { create: async () => ({ workspaceId: 'synthetic-workspace' }) },
    connection: { api: { sessions: {
      create: async args => { created.push(args); list.byId.fresh = { id: 'fresh' }; listeners.forEach(fn => fn()); return { result: { ok: true, value: { sessionId: 'fresh' } } }; },
      selectModel: async args => { modelCalls.push(args); assert.equal(opened.length, 0); return { result: { ok: true, value: { selected: { provider: args.provider, model: args.model } } } }; },
      models: async () => ({ result: { ok: true, value: { current: nativeModelSelection, routable: true } } })
    } } }
  };
  const refreshCalls = [];
  if (refreshOverride) {
    services.sessions.refresh = async (...args) => {
      refreshCalls.push(args);
      return refreshOverride({ list, notify: () => listeners.forEach(fn => fn()), args });
    };
  }
  if (remembered) values.set(trainerNativeKey(target, 'framework-expert', 'training'), remembered);
  const api = async (op, args, opts) => { calls.push(args); if (apiOverride) return { nativeModelSelection, ...await apiOverride(op, args, opts) }; return { ...args, cwd: 'fixture/synthetic', bindingSchemaVersion: 1, bindingRevision: 1, nativeModelSelection }; };
  return { services, opened, created, calls, values, modelCalls, refreshCalls, nav: createTrainerNavigator({ services, api, storage: { getItem: k => values.get(k), setItem: (k, v) => values.set(k, v) } }) };
}

test('native session list errors are surfaced without waiting for the timeout', async () => {
  const f = nativeFixture({ listOverride: { phase: 'pending', listState: 'error', listError: { code: 'SESSION_QUERY_INDEX_FAILED', message: 'SQLite unavailable' } } });
  const started = Date.now();
  await assert.rejects(f.nav.open({ target }), error => {
    assert.equal(error.code, 'SESSION_QUERY_INDEX_FAILED');
    assert.match(error.message, /SQLite unavailable/);
    return true;
  });
  assert.ok(Date.now() - started < 1000);
  assert.equal(f.calls.length, 0);
  assert.deepEqual(f.opened, []);
});

test('native session list timeout includes host snapshot diagnostics', async () => {
  const f = nativeFixture({ listOverride: { phase: 'pending', listState: 'loading' } });
  const { waitTrainerSession } = await import('../client/trainer-native.js');
  await assert.rejects(waitTrainerSession(f.services.sessions, list => !!list.byId.missing, { timeoutMs: 5 }), error => {
    assert.match(error.message, /5ms/);
    assert.match(error.message, /phase=pending/);
    assert.match(error.message, /listState=loading/);
    return true;
  });
});

test('native session refresh is requested before waiting for a pending list', async () => {
  const f = nativeFixture({
    listOverride: { phase: 'pending', listState: 'loading' },
    refreshOverride: async ({ list, notify }) => {
      list.phase = 'ready';
      list.listState = 'idle';
      notify();
    }
  });
  const result = await f.nav.open({ target });
  assert.equal(f.refreshCalls.length, 1);
  assert.equal(result.sessionId, 'fresh');
});

test('slow public session refresh does not block first native creation', async () => {
  let release;
  const refreshGate = new Promise(resolve => { release = resolve; });
  const f = nativeFixture({
    listOverride: { phase: 'pending', listState: 'loading' },
    refreshOverride: async () => refreshGate
  });
  const result = await Promise.race([
    f.nav.open({ target }),
    new Promise(resolve => setTimeout(() => resolve('timeout'), 1500))
  ]);
  release();
  assert.notEqual(result, 'timeout');
  assert.equal(result.sessionId, 'fresh');
});

test('a failed session refresh is recoverable by retrying navigation', async () => {
  let attempts = 0;
  const f = nativeFixture({
    listOverride: { phase: 'pending', listState: 'loading' },
    refreshOverride: async ({ list, notify }) => {
      attempts += 1;
      if (attempts === 1) {
        const error = new Error('temporary session index failure');
        error.code = 'SESSION_REFRESH_FAILED';
        throw error;
      }
      list.phase = 'ready';
      list.listState = 'idle';
      notify();
    }
  });
  await assert.rejects(f.nav.open({ target }), error => {
    assert.equal(error.code, 'SESSION_REFRESH_FAILED');
    assert.match(error.message, /temporary session index failure/);
    return true;
  });
  assert.equal(f.created.length, 0);
  const result = await f.nav.open({ target });
  assert.equal(attempts, 2);
  assert.equal(result.sessionId, 'fresh');
});

test('native creation uses exact expert preset and server synthetic cwd binding', async () => {
  const f = nativeFixture();
  const result = await f.nav.open({ target, title: 'Synthetic expert' });
  assert.equal(f.created[0].agentPreset, 'framework-expert');
  assert.equal(result.sessionId, 'fresh');
  assert.equal(f.calls.length, 2);
  assert.deepEqual(f.modelCalls, [{ sessionId: 'fresh', ...nativeModelSelection }]);
  assert.deepEqual(f.opened, ['fresh']);
  assert.equal(trainerPreset('workflow', 'training'), 'agent-trainer');
  assert.equal(trainerPreset('agent', 'engineering'), 'framework-observer');
});

test('native creation retries a host that publishes the new session after the create RPC', async () => {
  const f = nativeFixture();
  const originalOpen = f.services.sessions.open;
  let attempts = 0;
  f.services.sessions.open = id => {
    attempts += 1;
    if (attempts === 1) {
      const error = new Error(`sessions.select: unknown session ${id}`);
      error.code = 'session_unknown';
      throw error;
    }
    originalOpen(id);
  };
  const result = await f.nav.open({ target });
  assert.equal(result.sessionId, 'fresh');
  assert.equal(attempts, 2);
  assert.deepEqual(f.opened, ['fresh']);
});

test('remembered native session is server verified and wrong preset never opened', async () => {
  const f = nativeFixture({ remembered: 'old-standard', apiOverride: async (op, args) => ({ ...args, presetId: 'standard', bindingSchemaVersion: 1 }) });
  await assert.rejects(f.nav.open({ target }), /绑定/);
  assert.equal(f.calls[0].sessionId, 'old-standard');
  assert.deepEqual(f.opened, []);
  assert.deepEqual(f.created, []);
});

test('superseded navigation never opens the old session', async () => {
  const blocked = deferred();
  const f = nativeFixture({ remembered: 'old', apiOverride: async (op, args) => args.targetId === 'lab-a' ? blocked.promise : { ...args, cwd: 'fixture/synthetic', bindingSchemaVersion: 1 } });
  const first = f.nav.open({ target });
  const rejected = assert.rejects(first, e => e.name === 'AbortError');
  await tick();
  await f.nav.open({ target: { ...target, targetId: 'lab-b' } });
  blocked.resolve({ ...target, sessionId: 'old', presetId: 'framework-expert', mode: 'training', bindingSchemaVersion: 1 });
  await rejected;
  assert.deepEqual(f.opened, ['fresh']);
});

test('verified native reuse passes binding revision and clears selected run explicitly', async () => {
  const f = nativeFixture({ remembered: 'known', apiOverride: async (op, args) => {
    if (!args.targetId) return { ...target, sessionId: 'known', presetId: 'framework-expert', mode: 'training', bindingSchemaVersion: 1, bindingRevision: 4 };
    assert.equal(args.baseBindingRevision, 4);
    assert.equal(args.selectedRunId, null);
    return { ...args, bindingSchemaVersion: 1, bindingRevision: 5 };
  } });
  const value = await f.nav.open({ target });
  assert.equal(value.bindingRevision, 5);
  assert.deepEqual(f.opened, ['known']);
  assert.equal(f.created.length, 0);
  assert.deepEqual(f.modelCalls, [{ sessionId: 'known', ...nativeModelSelection }]);
});

test('native model selection rejection stops navigation without fallback', async () => {
  const f = nativeFixture();
  f.services.connection.api.sessions.selectModel = async args => {
    f.modelCalls.push(args); return { result: { ok: false, error: { message: 'DeepSeek unavailable' } } };
  };
  await assert.rejects(f.nav.open({ target }), /DeepSeek unavailable/);
  assert.deepEqual(f.opened, []);
  assert.equal(f.modelCalls.length, 1);
  assert.equal(f.modelCalls[0].provider, 'deepseek-official');
});

test('native model readback mismatch stops navigation', async () => {
  const f = nativeFixture();
  f.services.connection.api.sessions.models = async () => ({ result: { ok: true, value: { current: { provider: 'other', model: 'other' }, routable: true } } });
  await assert.rejects(f.nav.open({ target }), /未生效/);
  assert.deepEqual(f.opened, []);
  assert.equal(f.modelCalls.length, 1);
});
