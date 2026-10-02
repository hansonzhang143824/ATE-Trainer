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
