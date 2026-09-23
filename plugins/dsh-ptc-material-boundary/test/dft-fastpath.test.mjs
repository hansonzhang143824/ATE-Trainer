import assert from 'node:assert/strict';
import test from 'node:test';
import { setTimeout as delay } from 'node:timers/promises';
import { checkDftReuse } from '../lib/dft-reuse.js';
import { startWithDeadline } from '../lib/execution-deadline.js';
import { deliveryExecutionScope, installCaptainEntryHook } from '../lib/captain-entry.js';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ready = { gate: 'DFT_OUTPUT', status: 'ready', canonicalInput: { sha256: 'a'.repeat(64) }, requiredOutputs: ['meta', 'yaml', 'review'], missingOrStaleOutputs: [] };
test('DFT-only parser accepts the observed typo and explicit exclusion wording', () => {
  assert.deepEqual(deliveryExecutionScope('生成TM109的code,执行性DFT expert，其余都不执行'), { sourceRoles: ['dft-expert'], stopAfter: 'INPUT_SYNC' });
  assert.deepEqual(deliveryExecutionScope('帮我写TM109的code,只执行DFT expert，其他不执行'), { sourceRoles: ['dft-expert'], stopAfter: 'INPUT_SYNC' });
  assert.deepEqual(deliveryExecutionScope('写 TM109'), { sourceRoles: ['dft-expert', 'schematic-expert'], stopAfter: null });
});

test('same-session correction cancels schematic and returns existing DFT reuse result', async () => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-scope-correction-'));
  let schematicAborted = false;
  try {
    const handlers = new Map();
    const entry = { state: 'INPUT_SYNC', batchId: 'scope-correction', executionScope: { sourceRoles: ['dft-expert', 'schematic-expert'], stopAfter: null } };
    const dft = { role: 'dft-expert', mode: 'UNCHANGED', result: Promise.resolve({ stopReason: 'completed', structured: { status: 'done', mode: 'UNCHANGED' } }) };
    const schematic = { role: 'schematic-expert', abort: () => { schematicAborted = true; }, result: Promise.resolve({ stopReason: 'aborted' }) };
    installCaptainEntryHook({ on: (event, fn) => handlers.set(event, fn) }, {
      workspaceRoot,
      runCaptainEntry: async () => entry,
      runCaptainScopeUpdate: async () => ({ ...entry, executionScope: { sourceRoles: ['dft-expert'], stopAfter: 'INPUT_SYNC' } }),
      startRequiredSourceDispatches: async () => [dft, schematic],
    });
    const agent = { id: 'corrected', cancel() {}, session: { header: { cwd: workspaceRoot, agentPreset: 'ate-ptc' }, events: [] } };
    const first = await handlers.get('agent/pre-step')({ agent, messages: [{ id: 'first', source: { kind: 'user' }, content: [{ type: 'text', text: '写 TM109' }] }], signal: new AbortController().signal }, async () => ({ kind: 'enter', messages: [] }));
    assert.equal(first.kind, 'reject');
    const second = await handlers.get('agent/pre-step')({ agent, messages: [{ id: 'second', source: { kind: 'user' }, content: [{ type: 'text', text: 'TM109，只执行DFT expert，其他不执行' }] }], signal: new AbortController().signal }, async () => ({ kind: 'enter', messages: [] }));
    assert.equal(second.kind, 'enter');
    assert.equal(schematicAborted, true);
    assert.match(second.messages[0].content[0].text, /UNCHANGED/);
  } finally { fs.rmSync(workspaceRoot, { recursive: true, force: true }); }
});
test('DFT-only ready entry reports a terminal result without another stage or model', async () => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-scoped-hook-'));
  try {
    const handlers = new Map();
    let advances = 0;
    const entry = { state: 'INPUT_SYNC', batchId: 'scope-test', executionScope: { sourceRoles: ['dft-expert'], stopAfter: 'INPUT_SYNC' } };
    installCaptainEntryHook({ on: (event, fn) => handlers.set(event, fn) }, {
      workspaceRoot,
      runCaptainEntry: async () => entry,
      startRequiredSourceDispatches: async () => [{ mode: 'UNCHANGED', result: Promise.resolve({ stopReason: 'completed', structured: { status: 'done', mode: 'UNCHANGED' } }) }],
      runCaptainContinuation: async () => { advances++; throw new Error('must not advance'); },
    });
    const agent = { id: 'scoped', session: { header: { cwd: workspaceRoot, agentPreset: 'ate-ptc' }, events: [] } };
    const result = await handlers.get('agent/pre-step')({ agent, messages: [{ id: 'scope', source: { kind: 'user' }, content: [{ type: 'text', text: 'ＴＭ１０９，只执行ＤＦＴ' }] }], signal: new AbortController().signal }, async () => ({ kind: 'enter', messages: [] }));
    assert.equal(result.kind, 'enter');
    assert.match(result.messages[0].content[0].text, /UNCHANGED/);
    assert.equal(advances, 0);
    const terminal = JSON.parse(fs.readFileSync(path.join(workspaceRoot, 'team/artifacts/scope-test/source-terminal.json')));
    assert.equal(terminal.mode, 'UNCHANGED');
    assert.equal(terminal.advanced, false);
  } finally { fs.rmSync(workspaceRoot, { recursive: true, force: true }); }
});
test('reuse checks exact TM gate with a 30 second command limit', async () => {
  const result = await checkDftReuse('workspace', ['TM109'], async (exe, args, options) => {
    assert.equal(exe, 'python');
    assert.deepEqual(args, ['scripts/validate_dft_outputs.py', '--tm', 'TM109']);
    assert.equal(options.timeout, 30_000);
    return { stdout: JSON.stringify(ready) };
  });
  assert.equal(result.unchanged, true);
});
test('stale bindings require regeneration; a gate crash or malformed response fails closed', async () => {
  const stale = { ...ready, status: 'stale', missingOrStaleOutputs: ['review hash mismatch'] };
  const result = await checkDftReuse('workspace', ['TM109'], async () => { throw Object.assign(new Error(), { code: 2, stdout: JSON.stringify(stale) }); });
  assert.equal(result.unchanged, false);
  for (const value of ['not json', JSON.stringify({ ...ready, canonicalInput: {} }), JSON.stringify(stale)]) {
    await assert.rejects(checkDftReuse('workspace', ['TM109'], async () => ({ stdout: value })));
  }
  await assert.rejects(checkDftReuse('workspace', ['TM109'], async () => { throw Object.assign(new Error('timeout'), { code: 2, killed: true }); }));
});
test('deadline aborts the actual child signal and settles even if provider result never resolves', async () => {
  let childSignal;
  let cancellations = 0;
  const run = await startWithDeadline({ subagents: { start: async (_provider, request) => {
    childSignal = request.signal;
    childSignal.addEventListener('abort', () => { cancellations++; });
    return { id: 'hung-child', result: new Promise(() => {}) };
  } } }, { label: 'PTC dft expert [TM109]' }, 20);
  const [result] = await Promise.all([run.result, delay(40)]);
  assert.equal(result.stopReason, 'timeout');
  assert.equal(result.structured.status, 'blocked');
  assert.equal(childSignal.aborted, true);
  assert.equal(cancellations, 1);
});
test('successful child clears its deadline and is never cancelled later', async () => {
  let childSignal;
  const run = await startWithDeadline({ subagents: { start: async (_provider, request) => {
    childSignal = request.signal;
    return { result: Promise.resolve({ stopReason: 'completed' }) };
  } } }, { label: 'DFT' }, 10);
  assert.equal((await run.result).stopReason, 'completed');
  await delay(25);
  assert.equal(childSignal.aborted, false);
});
