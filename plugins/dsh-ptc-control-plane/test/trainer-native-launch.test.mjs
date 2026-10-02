import assert from 'node:assert/strict';
import test from 'node:test';
import { openTrainerNativeSession } from '../client/native-sessions.js';

const request = { projectId: 'agent-trainer', mode: 'training', presetId: 'agent-trainer',
  targetKind: 'agent', targetId: 'agent-T2', candidateRevision: 'revision-1', selectedRunId: null };

function fixture(t) {
  const previousWindow = globalThis.window;
  const local = new Map(), native = new Map(), server = new Map(), events = [];
  let current, serial = 0;
  globalThis.window = { setTimeout, clearTimeout, localStorage: {
    getItem: key => local.get(key), setItem: (key, value) => local.set(key, value), removeItem: key => local.delete(key),
  } };
  t.after(() => { if (previousWindow === undefined) delete globalThis.window; else globalThis.window = previousWindow; });
  const f = { native, server, events, created: [], revision: 'revision-1', rejectBind: false, rejectOpen: false, select: true };
  f.scope = {
    get() { return { api: {
      agentPresets: { async list() { return { result: { ok: true, value: { presets: [{ id: 'agent-trainer' }] } } }; } },
      sessions: { async create(input) {
        const sessionId = `session-${++serial}`; events.push('create');
        f.created.push(input);
        native.set(sessionId, { session: { header: { agentPreset: 'agent-trainer' }, async rename() { events.push('rename'); } } });
        return { result: { ok: true, value: { sessionId } } };
      } },
    } }; },
    workspaces: { async create() { return { workspaceId: 'workspace-1' }; } },
    sessions: { binding: id => native.get(id), async open(id) {
      events.push('open'); if (f.rejectOpen) throw new Error('selection rejected');
      assert.ok(server.has(id), 'Trainer binding must exist before the input window opens');
      if (f.select) current = id;
    }, list: { getSnapshot: () => ({ current }), subscribe: () => () => {} } },
  };
  f.post = async (operation, input) => {
    if (operation === 'session-workspace') { events.push('workspace'); return { path: '/fixture', candidateRevision: f.revision }; }
    if (operation === 'open-native-session') {
      if (f.rejectBind) throw new Error('binding rejected');
      events.push('open-native');
      const sessionId = `session-${++serial}`;
      native.set(sessionId, { session: { header: { agentPreset: 'agent-trainer' }, async rename() { events.push('rename'); } } });
      const binding = { ...input, sessionId, bindingRevision: 1, effectiveTools: ['trainer_context'] };
      server.set(sessionId, binding);
      return { sessionId, binding };
    }
    assert.equal(operation, 'bind-session');
    if (!input.targetId) { events.push('read-binding'); return server.get(input.sessionId); }
    if (f.rejectBind) throw new Error('binding rejected');
    events.push('bind');
    const old = server.get(input.sessionId);
    if (old) assert.equal(input.baseBindingRevision, old.bindingRevision);
    const binding = { ...input, bindingRevision: (old?.bindingRevision || 0) + 1, effectiveTools: ['trainer_context'] };
    server.set(input.sessionId, binding); return binding;
  };
  f.open = input => openTrainerNativeSession(f.scope, { ...request, ...input }, { post: f.post, title: 'Agent Trainer' });
  return f;
}

test('Trainer binds before native selection and checks current session', async t => {
  const f = fixture(t), result = await f.open();
  assert.equal(result.scopeOpened, true);
  assert.deepEqual(f.events, ['workspace', 'open-native', 'open']);
  assert.equal(result.binding.targetId, 'agent-T2');
});

test('server-side native factory returns a bound session before selection', async t => {
  const f = fixture(t);
  const result = await f.open();
  assert.equal(result.scopeOpened, true);
  assert.deepEqual(f.events, ['workspace', 'open-native', 'open']);
});

test('duplicate concurrent launcher requests create only one bound native session', async t => {
  const f = fixture(t), results = await Promise.all([f.open(), f.open(), f.open()]);
  assert.equal(new Set(results.map(x => x.sessionId)).size, 1);
  assert.equal(f.events.filter(x => x === 'open-native').length, 1);
  assert.equal(f.events.filter(x => x === 'bind').length, 0);
});

test('reuse reads authoritative binding and uses its current revision for rebind', async t => {
  const f = fixture(t), first = await f.open();
  f.server.get(first.sessionId).bindingRevision = 8;
  const again = await f.open();
  assert.equal(again.sessionId, first.sessionId);
  assert.equal(again.reused, true);
  assert.equal(again.binding.bindingRevision, 9);
  assert.ok(f.events.includes('read-binding'));
});

test('reuse survives a DSH session-service wrapper refresh for the same host', async t => {
  const f = fixture(t), first = await openTrainerNativeSession(f.scope, request, {
    post: f.post, title: 'Agent Trainer', hostId: 'host-1',
  });
  const refreshedScope = { ...f.scope, sessions: { ...f.scope.sessions } };
  const again = await openTrainerNativeSession(refreshedScope, request, {
    post: f.post, title: 'Agent Trainer', hostId: 'host-1',
  });
  assert.equal(again.sessionId, first.sessionId);
  assert.equal(again.reused, true);
  assert.ok(f.events.includes('read-binding'));
});

test('cached session with changed target or candidate is never reused', async t => {
  const f = fixture(t), first = await f.open();
  f.server.get(first.sessionId).targetId = 'wrong-agent';
  const second = await f.open(); assert.notEqual(second.sessionId, first.sessionId);
  f.server.get(second.sessionId).candidateRevision = 'revision-new';
  const third = await f.open(); assert.equal(third.sessionId, second.sessionId);
  assert.equal(third.reused, true);
});

test('deleted native session and wrong preset both cause a fresh session', async t => {
  const f = fixture(t), first = await f.open();
  f.native.delete(first.sessionId);
  const second = await f.open(); assert.notEqual(second.sessionId, first.sessionId);
  f.native.get(second.sessionId).session.header.agentPreset = 'standard';
  const third = await f.open(); assert.notEqual(third.sessionId, second.sessionId);
});

test('project, mode, run, target kind and candidate all participate in session identity', async t => {
  const f = fixture(t), sessions = [await f.open()];
  sessions.push(await f.open({ projectId: 'other-project' }));
  sessions.push(await f.open({ mode: 'engineering' }));
  sessions.push(await f.open({ selectedRunId: 'run-1' }));
  sessions.push(await f.open({ targetKind: 'workflow' }));
  f.revision = 'revision-2'; sessions.push(await f.open({ candidateRevision: 'revision-2' }));
  assert.equal(new Set(sessions.map(x => x.sessionId)).size, 4);
});

test('stale page revision and wrong preset are rejected before creating anything', async t => {
  const f = fixture(t);
  await assert.rejects(f.open({ candidateRevision: 'old-revision' }), /STALE_SESSION/);
  await assert.rejects(f.open({ presetId: 'standard' }), /PRESET_MISMATCH/);
  assert.equal(f.native.size, 0);
});

test('binding failure never opens a window and retry does not keep rejected promise', async t => {
  const f = fixture(t); f.rejectBind = true;
  await assert.rejects(f.open(), /binding rejected/);
  assert.ok(!f.events.includes('open'));
  f.rejectBind = false; assert.equal((await f.open()).scopeOpened, true);
});

test('native selection rejection or no-op cannot produce success', async t => {
  const f = fixture(t); f.rejectOpen = true;
  await assert.rejects(f.open(), /selection rejected/);
  f.rejectOpen = false; f.select = false;
  await assert.rejects(f.open(), /OPEN_FAILED/);
  f.select = true; assert.equal((await f.open()).scopeOpened, true);
});


function authoritativeFixture(t, { bindError = null } = {}) {
  const previousWindow = globalThis.window;
  const local = new Map();
  let current = null;
  let loaded = false;
  let created = 0;
  const calls = [];
  const serverId = 'session-server-authoritative';
  let serverBinding = { ...request, sessionId: serverId, bindingRevision: 4, effectiveTools: ['trainer_context'], resolved: { source: 'candidate', revisionId: 'revision-1' } };
  globalThis.window = { setTimeout, clearTimeout, localStorage: {
    getItem: key => local.get(key) ?? null,
    setItem: (key, value) => local.set(key, value),
    removeItem: key => local.delete(key),
    get length() { return local.size; },
    key: index => [...local.keys()][index] ?? null,
  } };
  t.after(() => { if (previousWindow === undefined) delete globalThis.window; else globalThis.window = previousWindow; });
  const scope = {
    get() { return { api: { sessions: { async create() { throw new Error('unexpected browser create'); } } } }; },
    sessions: {
      binding(id) { return id === serverId && loaded ? { session: { header: {} } } : undefined; },
      async refresh() { calls.push('refresh'); loaded = true; },
      async open(id) { calls.push(`open:${id}`); current = id; },
      list: { getSnapshot: () => ({ current }), subscribe: () => () => {} },
    },
  };
  const post = async (operation, input) => {
    calls.push(operation);
    if (operation === 'session-workspace') return { path: '/fixture', candidateRevision: 'revision-1' };
    if (operation === 'target-session') return { sessionId: serverId, binding: serverBinding };
    if (operation === 'bind-session') {
      if (bindError) throw Object.assign(new Error(bindError), { code: bindError });
      if (!input.targetId) return serverBinding;
      serverBinding = { ...serverBinding, ...input, bindingRevision: serverBinding.bindingRevision + 1 };
      return serverBinding;
    }
    if (operation === 'forget-target-session') return { ok: true };
    if (operation === 'open-native-session') {
      created += 1;
      const id = `session-created-${created}`;
      serverBinding = { ...input, sessionId: id, bindingRevision: 1, effectiveTools: ['trainer_context'], resolved: { source: 'candidate', revisionId: input.candidateRevision } };
      loaded = true;
      scope.sessions.binding = value => value === id ? { session: { header: {} } } : undefined;
      return { sessionId: id, binding: serverBinding };
    }
    throw new Error(`unexpected operation ${operation}`);
  };
  return { scope, post, calls, get created() { return created; }, open: input => openTrainerNativeSession(scope, { ...request, ...input }, { post, title: 'Agent Trainer' }) };
}

test('server target-session is authoritative before local binding refresh', async t => {
  const f = authoritativeFixture(t);
  const result = await f.open();
  assert.equal(result.sessionId, 'session-server-authoritative');
  assert.equal(result.reused, true);
  assert.equal(f.created, 0);
  assert.equal(f.calls.filter(call => call === 'refresh').length, 1);
  assert.equal(f.calls.filter(call => call === 'forget-target-session').length, 0);
});

test('only an allowed bind-session identity error forgets and creates', async t => {
  const f = authoritativeFixture(t, { bindError: 'session_unbound' });
  const result = await f.open();
  assert.equal(result.reused, false);
  assert.equal(f.created, 1);
  assert.equal(f.calls.filter(call => call === 'forget-target-session').length, 1);
});


const flushLaunch = async () => { for (let i = 0; i < 30; i++) await Promise.resolve(); };

for (const missing of ['refresh never resolves', 'binding never appears']) {
  test(`authoritative reuse ${missing}: times out, clears pending and retries without forget or factory`, async t => {
    t.mock.timers.enable({ apis: ['setTimeout', 'Date'] });
    const f = authoritativeFixture(t);
    window.setTimeout = globalThis.setTimeout;
    window.clearTimeout = globalThis.clearTimeout;
    let subscriptions = 0;
    f.scope.sessions.list.subscribe = () => { subscriptions++; return () => { subscriptions--; }; };
    const originalRefresh = f.scope.sessions.refresh;
    f.scope.sessions.refresh = missing === 'refresh never resolves'
      ? () => { f.calls.push('blocked-refresh'); return new Promise(() => {}); }
      : async () => { f.calls.push('empty-refresh'); };
    const failed = f.open();
    const assertion = assert.rejects(failed, error => error.code === 'NATIVE_SESSION_NOT_LISTED'
      && error.sessionId === 'session-server-authoritative' && error.message.includes('请刷新 DSH 页面后重试'));
    await flushLaunch();
    t.mock.timers.tick(missing === 'refresh never resolves' ? 10_000 : 30_000);
    await assertion;
    assert.equal(subscriptions, 0, 'timeout must unsubscribe the binding listener');
    assert.equal(f.calls.filter(call => call === 'forget-target-session').length, 0);
    assert.equal(f.created, 0);
    const previousReads = f.calls.filter(call => call === 'target-session').length;
    f.scope.sessions.refresh = originalRefresh;
    const retried = await f.open();
    assert.equal(retried.sessionId, 'session-server-authoritative');
    assert.equal(retried.reused, true);
    assert.equal(f.calls.filter(call => call === 'target-session').length, previousReads + 1,
      'retry must issue a new request after the rejected pending promise is cleared');
    assert.equal(f.calls.filter(call => call === 'forget-target-session').length, 0);
    assert.equal(f.created, 0);
  });
}
