import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { resolvePtcSessionWorkspace } from '../lib/session-workspaces.js';
import { openPtcNativeSession, ptcSessionKey } from '../client/native-sessions.js';

test('server maps each training mode to a constrained DSH workspace', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-session-workspace-'));
  try {
    fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
    const agent = resolvePtcSessionWorkspace(root, { mode: 'agent', profileId: 'ptc-dft-expert' });
    assert.equal(agent.path, path.join(root, 'team/expert-profiles/ptc-dft-expert'));
    const input = { mode: 'workflow', profileIds: ['method-expert', 'ptc-dft-expert'] };
    const first = resolvePtcSessionWorkspace(root, input);
    const second = resolvePtcSessionWorkspace(root, { ...input, profileIds: [...input.profileIds].reverse() });
    assert.notEqual(first.key, second.key);
    assert.match(first.key, /^[a-f0-9]{64}$/);
    assert.equal(fs.statSync(first.path).isDirectory(), true);
    const guidance = fs.readFileSync(path.join(first.path, 'AGENTS.md'), 'utf8');
    assert.match(guidance, /SMOKE_ONLY/);
    assert.match(guidance, /method-expert -> ptc-dft-expert/);
    assert.match(guidance, /\{"answer":3\}/);
    assert.match(fs.readFileSync(path.join(second.path, 'AGENTS.md'), 'utf8'), /ptc-dft-expert -> method-expert/);
    fs.writeFileSync(path.join(first.path, 'AGENTS.md'), '# User training notes\n');
    resolvePtcSessionWorkspace(root, input);
    assert.equal(fs.readFileSync(path.join(first.path, 'AGENTS.md'), 'utf8'), '# User training notes\n');
    assert.equal(resolvePtcSessionWorkspace(root, { mode: 'publish' }).path,
      path.join(root, 'Training_Materials/session-workspaces/publish-review'));
    assert.throws(() => resolvePtcSessionWorkspace(root, { mode: 'agent', profileId: '..' }));
    assert.throws(() => resolvePtcSessionWorkspace(root, { mode: 'workflow', profileIds: ['unknown'] }));
    assert.throws(() => resolvePtcSessionWorkspace(root, { mode: 'publish', path: 'C:/outside' }));
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('native session helper creates a DSH session in the API-approved workspace and reuses it', async () => {
  const previousWindow = globalThis.window;
  const storage = new Map();
  globalThis.window = { localStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value) },
    setTimeout, clearTimeout };
  try {
    const opened = [];
    const renamed = [];
    const bindings = new Map();
    const scope = {
      workspaces: { async create(input) { assert.equal(input.path, 'D:/ptc/expert'); return { workspaceId: 'ws-1' }; } },
      get(name) { assert.equal(name, 'connection'); return { api: {
        agentPresets: { async list(input) { assert.deepEqual(input, {}); return { result: { ok: true, value: { presets: [{ id: 'standard' }] } } }; } },
        sessions: { async create(input) { assert.deepEqual(input, { workspaceId: 'ws-1', agentPreset: 'standard' });
          bindings.set('s-1', { session: { async rename(title) { renamed.push(title); } } });
          return { result: { ok: true, value: { sessionId: 's-1' } } }; } },
      } }; },
      sessions: { binding: id => bindings.get(id), open: id => opened.push(id), list: { subscribe() { return () => {}; } } },
    };
    const result = await openPtcNativeSession(scope, { path: 'D:/ptc/expert' }, { key: 'agent:ptc-dft-expert', title: 'DFT' });
    assert.deepEqual(result, { sessionId: 's-1', reused: false });
    assert.deepEqual(renamed, ['DFT']);
    assert.deepEqual(opened, ['s-1']);
    const reused = await openPtcNativeSession(scope, { path: 'D:/ptc/expert' }, { key: 'agent:ptc-dft-expert', title: 'DFT' });
    assert.deepEqual(reused, { sessionId: 's-1', reused: true });
    assert.deepEqual(opened, ['s-1', 's-1']);
    assert.equal(ptcSessionKey('workflow', 'dft'), 'workflow:dft');
    assert.throws(() => ptcSessionKey('business', 'TM109'));
  } finally {
    if (previousWindow === undefined) delete globalThis.window;
    else globalThis.window = previousWindow;
  }
});
