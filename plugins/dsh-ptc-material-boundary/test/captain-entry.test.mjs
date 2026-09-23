import assert from 'node:assert/strict';
import test from 'node:test';
import path from 'node:path';
import { captainDirective, firstDeliveryRequest, initializeSessionState, installCaptainEntryHook, isPtcCaptainAgent, runCaptainContinuation, runCaptainEntry } from '../lib/captain-entry.js';

const root = path.resolve('D:/Newtest/DSH/ATE-Coding-Plat');
const user = (id, text) => ({ id, source: { kind: 'user' }, content: [{ type: 'text', text }] });
const signal = new AbortController().signal;
const captain = (id = 'captain') => ({ id, session: { header: { cwd: root, agentPreset: 'ate-ptc' }, events: [] } });
const normalCoding = (id = 'coding') => ({ id, session: { header: { cwd: root, agentPreset: 'code' }, events: [] } });
const foreignPtc = (id = 'foreign') => ({ id, session: { header: { cwd: 'D:/other-workspace', agentPreset: 'ate-ptc' }, events: [] } });
function hooks() {
  const handlers = new Map(); const calls = [];
  return { calls, handlers, ctx: {
    on: (event, callback) => handlers.set(event, callback),
    subagents: {
      getProvider: (name) => name === 'spawn' ? {} : undefined,
      start: async (provider, request) => { calls.push({ provider, request }); return { id: `child-${calls.length}` }; },
    },
  }};
}

test('missing Captain session state initializes an empty signature safely', () => {
  assert.deepEqual(initializeSessionState(undefined), { batchId: undefined, requestId: 'unbound', lastSignature: '' });
  assert.deepEqual(initializeSessionState({ batchId: 'b1' }, 'u1'), { batchId: 'b1', requestId: 'u1', lastSignature: '' });
});

test('Captain hook accepts only the first natural-language TM request', () => {
  assert.deepEqual(firstDeliveryRequest([user('u1', '跑 TM102、TM105')]), { id: 'u1', text: '跑 TM102、TM105' });
  assert.equal(firstDeliveryRequest([user('u1', 'TM102 做什么'), user('u2', '继续')]), undefined);
  assert.equal(firstDeliveryRequest([user('u1', '普通聊天')]), undefined);
});

test('PTC activation requires both ATE preset and exact DSH workspace', () => {
  assert.equal(isPtcCaptainAgent(captain(), root), true);
  assert.equal(isPtcCaptainAgent(normalCoding(), root), false);
  assert.equal(isPtcCaptainAgent(foreignPtc(), root), false);
});

test('ordinary coding mentioning TM never enters PTC', async () => {
  const { handlers, ctx, calls } = hooks(); let entries = 0;
  installCaptainEntryHook(ctx, { workspaceRoot: root, runCaptainEntry: async () => { entries += 1; return { state: 'INPUT_SYNC', batchId: 'wrong' }; } });
  const result = await handlers.get('agent/pre-step')({ agent: normalCoding(), messages: [user('u', '请改 TM425 的普通代码')], signal }, async () => ({ kind: 'enter', messages: [] }));
  assert.equal(entries, 0);
  assert.equal(calls.length, 0);
  assert.equal(result.kind, 'enter');
});

test('ATE preset outside DSH workspace never enters PTC', async () => {
  const { handlers, ctx } = hooks(); let entries = 0;
  installCaptainEntryHook(ctx, { workspaceRoot: root, runCaptainEntry: async () => { entries += 1; return { state: 'INPUT_SYNC', batchId: 'wrong' }; } });
  await handlers.get('agent/pre-step')({ agent: foreignPtc(), messages: [user('u', '跑 TM425')], signal }, async () => ({ kind: 'enter', messages: [] }));
  assert.equal(entries, 0);
});

test('real Chinese shorthand creates fixed source dispatch in one pre-step', async () => {
  const { handlers, ctx, calls } = hooks();
  const starts = [];
  const request = '帮我写TM103/106/108/109/425的code';
  installCaptainEntryHook(ctx, { workspaceRoot: root, runCaptainEntry: async (workspace, text) => {
    starts.push([workspace, text]);
    return { state: 'INPUT_SYNC', batchId: 'b', dispatch: null, dispatches: [{ role: 'dft-expert', tms: ['TM103', 'TM106', 'TM108', 'TM109', 'TM425'] }, { role: 'schematic-expert', tms: ['TM103', 'TM106', 'TM108', 'TM109', 'TM425'] }] };
  }});
  const step = handlers.get('agent/pre-step');
  const result = await step({ agent: captain(), messages: [user('u', request)], signal }, async () => ({ kind: 'enter', messages: [] }));
  assert.deepEqual(starts, [[root, request]]);
  assert.equal(result.kind, 'reject');
  assert.deepEqual(calls.map(({ provider, request }) => [provider, request.label]), [['spawn', 'PTC dft expert [TM103,TM106,TM108,TM109,TM425]'], ['spawn', 'PTC schematic expert']]);
});

test('source specialists are started before the Captain receives the entry directive', async () => {
  const { handlers, ctx, calls } = hooks();
  installCaptainEntryHook(ctx, { workspaceRoot: root, runCaptainEntry: async () => ({ state: 'INPUT_SYNC', batchId: 'b', dispatches: [{ role: 'dft-expert', tms: ['TM106'] }, { role: 'schematic-expert', tms: ['TM106'] }] }) });
  const agent = captain();
  await handlers.get('agent/pre-step')({ agent, messages: [user('u', 'write TM106')], signal }, async () => ({ kind: 'enter', messages: [] }));
  assert.equal(calls.length, 2);
  assert.equal(handlers.has('tools/pre-execute'), false);
});

test('Captain hook calls internal entry and keeps fast policy out of first source dispatch', async () => {
  const result = await runCaptainEntry(root, '跑 TM102', async (command, args, options) => {
    assert.equal(command, 'python');
    assert.deepEqual(args, [path.join(root, 'scripts', 'captain_delivery_entry.py'), '--request', '跑 TM102']);
    assert.equal(options.cwd, root);
    return { stdout: '{"state":"INPUT_SYNC","batchId":"isolated-hook-test","dispatch":null}', stderr: '' };
  });
  assert.match(captainDirective(result), /batchId: isolated-hook-test/);
  assert.match(captainDirective(result), /already started every INPUT_SYNC source specialist/);
});

test('continuation command remains explicit and pre-step never auto-advances', async () => {
  await runCaptainContinuation(root, 'isolated-hook-test', async (_command, args) => {
    assert.deepEqual(args, [path.join(root, 'scripts', 'captain_delivery_entry.py'), '--continue-batch', 'isolated-hook-test']);
    return { stdout: '{"state":"FAST_DELIVERY_PENDING_AUDIT","batchId":"isolated-hook-test"}', stderr: '' };
  });
  const { handlers, ctx } = hooks(); let advances = 0;
  installCaptainEntryHook(ctx, { workspaceRoot: root, runCaptainEntry: async () => ({ state: 'STRATEGY', batchId: 'b' }), runCaptainContinuation: async () => { advances += 1; return {}; } });
  const step = handlers.get('agent/pre-step'); const input = { agent: { id: 'captain', session: { events: [] } }, messages: [user('u', '跑 TM102')], signal };
  await step(input, async () => ({ kind: 'enter', messages: [] }));
  await step(input, async () => ({ kind: 'enter', messages: [] }));
  assert.equal(advances, 0);
});
