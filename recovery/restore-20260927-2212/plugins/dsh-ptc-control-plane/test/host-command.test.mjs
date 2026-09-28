import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import test from 'node:test';
import { setTimeout as delay } from 'node:timers/promises';
import { runHostCommand } from '../lib/host-command.js';

function child(pid = 42) {
  const process = new EventEmitter();
  process.pid = pid;
  process.stdout = new EventEmitter(); process.stderr = new EventEmitter();
  process.kills = [];
  process.kill = signal => { process.kills.push(signal); return true; };
  return process;
}
function fixture(onLaunch, onKill = (killer, process) => { process.emit('close', null, 'SIGKILL'); killer.emit('close', 0); }) {
  const process = child(); const killer = child(43); const calls = [];
  const spawn = (executable, args, options) => {
    calls.push({ executable, args, options });
    if (calls.length === 1) { queueMicrotask(() => onLaunch?.(process)); return process; }
    queueMicrotask(() => onKill(killer, process));
    return killer;
  };
  return { process, killer, calls, options: { cwd: 'fixture-workspace', spawn, platform: 'win32', timeoutMs: 100, killTimeoutMs: 15, drainTimeoutMs: 15 } };
}

test('fixed host command captures split UTF-8 output and returns passed only after actual zero close', async () => {
  const f = fixture(process => {
    const bytes = Buffer.from('成功');
    process.stdout.emit('data', bytes.subarray(0, 2)); process.stdout.emit('data', bytes.subarray(2));
    process.stderr.emit('data', Buffer.from('diagnostic')); process.emit('close', 0, null);
  });
  const result = await runHostCommand('python', ['fixed.py', '--tm', 'TM109'], f.options);
  assert.equal(result.status, 'passed');
  assert.equal(result.stdout, '成功');
  assert.equal(result.stderr, 'diagnostic');
  assert.equal(result.processStarted, true);
  assert.equal(result.directChildClosed, true);
  assert.equal(result.terminationConfirmed, true);
  assert.equal(result.treeTerminationConfirmed, false);
  assert.equal(result.termination, null);
  assert.equal(result.command, 'python fixed.py --tm TM109');
  assert.deepEqual(f.calls[0].options, { cwd: 'fixture-workspace', windowsHide: true, shell: false });
  await delay(110);
  assert.equal(f.calls.length, 1, 'completed command deadline must be cleared');
});

test('nonzero exit and signal close are blocked without pretending a gate passed', async () => {
  for (const code of [2, null]) {
    const f = fixture(process => process.emit('close', code, code === null ? 'SIGTERM' : null));
    const result = await runHostCommand('python', ['gate.py'], f.options);
    assert.equal(result.status, 'blocked');
    assert.equal(result.exitCode, code);
    assert.equal(result.directChildClosed, true);
    assert.equal(f.calls.length, 1);
  }
});

test('synchronous spawn throw and async spawn error are classified as not-started blocked commands', async () => {
  const thrown = await runHostCommand('missing', [], { spawn() { throw new Error('ENOENT'); } });
  assert.equal(thrown.status, 'blocked');
  assert.equal(thrown.stopReason, 'spawn_error');
  assert.equal(thrown.processStarted, false);
  assert.equal(thrown.termination.status, 'not_started');
  const process = child(undefined); process.pid = undefined;
  const result = await runHostCommand('missing', [], { spawn() { queueMicrotask(() => process.emit('error', new Error('async ENOENT'))); return process; } });
  assert.equal(result.stopReason, 'spawn_error');
  assert.equal(result.processStarted, false);
  assert.equal(result.directChildClosed, false);
  assert.equal(result.terminationConfirmed, true);
  process.emit('error', new Error('late spawn error')); // Must not crash caller.
});

test('error on an existing PID requests tree cancellation and cannot itself confirm termination', async () => {
  const f = fixture(process => process.emit('error', new Error('existing process fault')), killer => killer.emit('close', 1));
  const result = await runHostCommand('python', ['fixed.py'], f.options);
  assert.equal(result.status, 'blocked');
  assert.equal(result.stopReason, 'process_error');
  assert.equal(result.error, 'existing process fault');
  assert.equal(result.directChildClosed, false);
  assert.equal(result.terminationConfirmed, false);
  assert.equal(f.calls.length, 2);
});

test('timeout requests exact Windows tree kill and confirms only after direct close plus kill success', async () => {
  const f = fixture();
  const result = await runHostCommand('python', ['fixed.py'], { ...f.options, timeoutMs: 10 });
  assert.equal(result.stopReason, 'timeout');
  assert.equal(result.status, 'blocked');
  assert.match(f.calls[1].executable, /taskkill\.exe$/i);
  assert.deepEqual(f.calls[1].args, ['/PID', '42', '/T', '/F']);
  assert.equal(result.directChildClosed, true);
  assert.equal(result.treeTerminationConfirmed, true);
  assert.equal(result.terminationConfirmed, true);
});

test('pre-abort never spawns; running abort is sticky even if child closes successfully immediately afterwards', async () => {
  const before = new AbortController(); before.abort('stop before start'); let started = false;
  const skipped = await runHostCommand('python', [], { signal: before.signal, spawn() { started = true; } });
  assert.equal(started, false);
  assert.equal(skipped.stopReason, 'aborted');
  assert.equal(skipped.processStarted, false);
  const controller = new AbortController();
  const f = fixture(process => { controller.abort('stop'); process.emit('close', 0); });
  const result = await runHostCommand('python', [], { ...f.options, signal: controller.signal });
  assert.equal(result.stopReason, 'aborted');
  assert.equal(result.status, 'blocked');
  assert.equal(result.exitCode, null);
  assert.equal(result.observedExitCode, 0);
  assert.equal(f.calls.length, 2, 'descendant cleanup is still requested after direct close');
});

test('taskkill failure plus late direct close does not claim the process tree was terminated', async () => {
  const f = fixture(process => process.stdout.emit('data', 'too much output'), (killer, process) => {
    killer.stderr.emit('data', 'access denied'); killer.emit('close', 1);
    setTimeout(() => process.emit('close', null, 'SIGKILL'), 5);
  });
  const result = await runHostCommand('python', [], { ...f.options, maxOutputBytes: 4 });
  assert.equal(result.stopReason, 'output_limit');
  assert.equal(result.termination.status, 'failed');
  assert.equal(result.directChildClosed, true);
  assert.equal(result.terminationConfirmed, false);
  assert.equal(result.treeTerminationConfirmed, false);
});

test('taskkill throw/error/hang remain bounded and never count helper shutdown as tree success', async () => {
  for (const behavior of ['throw', 'error', 'hang']) {
    const f = fixture(process => process.stdout.emit('data', 'overflow'), killer => {
      if (behavior === 'error') killer.emit('error', new Error('kill failed'));
    });
    const original = f.options.spawn;
    if (behavior === 'throw') f.options.spawn = (...args) => {
      if (f.calls.length) throw new Error('cannot launch taskkill');
      return original(...args);
    };
    if (behavior === 'hang') f.killer.kill = signal => { f.killer.kills.push(signal); f.killer.emit('close', 0); return true; };
    const result = await runHostCommand('python', [], { ...f.options, maxOutputBytes: 1 });
    assert.equal(result.status, 'blocked');
    assert.equal(result.terminationConfirmed, false);
    assert.equal(result.termination.status, behavior === 'hang' ? 'unknown' : 'failed');
    if (behavior === 'hang') assert.deepEqual(f.killer.kills, ['SIGKILL']);
    if (behavior !== 'throw') f.killer.emit('error', new Error('late helper error'));
  }
});

test('taskkill exit zero without observed child close is cancellation requested, not confirmed', async () => {
  const f = fixture(process => process.stdout.emit('data', 'overflow'), killer => killer.emit('close', 0));
  const result = await runHostCommand('python', [], { ...f.options, maxOutputBytes: 1 });
  assert.equal(result.termination.status, 'requested');
  assert.equal(result.terminationConfirmed, false);
  assert.equal(result.directChildClosed, false);
  f.process.emit('close', 0);
  assert.equal(result.terminationConfirmed, false, 'a returned evidence snapshot must not silently turn into a success');
});

test('stdout plus stderr enforce one byte budget and taskkill diagnostics have their own bounded cap', async () => {
  const f = fixture(process => {
    process.stdout.emit('data', '123'); process.stderr.emit('data', '456789'); process.stdout.emit('data', 'later');
  }, (killer, process) => {
    killer.stdout.emit('data', Buffer.alloc(80 * 1024, 65)); killer.stderr.emit('data', 'extra');
    process.emit('close', null, 'SIGKILL'); killer.emit('close', 0);
  });
  const result = await runHostCommand('python', [], { ...f.options, maxOutputBytes: 5 });
  assert.equal(result.stdout, '123');
  assert.equal(result.stderr, '45');
  assert.equal(result.outputTruncated, true);
  assert.equal(result.receivedBytes, 14);
  assert.equal(Buffer.byteLength(result.termination.output), 64 * 1024);
  assert.equal(result.termination.outputTruncated, true);
});

test('non-Windows direct kill evidence never claims the whole descendant tree was stopped', async () => {
  const f = fixture(process => process.stdout.emit('data', 'overflow'));
  f.process.kill = () => { queueMicrotask(() => f.process.emit('close', null, 'SIGKILL')); return true; };
  const result = await runHostCommand('python', [], { ...f.options, platform: 'linux', maxOutputBytes: 1 });
  assert.equal(result.termination.scope, 'direct-child-only');
  assert.equal(result.directChildClosed, true);
  assert.equal(result.treeTerminationConfirmed, false);
  assert.equal(result.terminationConfirmed, false);
  assert.equal(f.calls.length, 1);
});

test('invalid or excessive host budgets fail before any spawn', async () => {
  for (const options of [{ timeoutMs: 30_001 }, { timeoutMs: 0 }, { killTimeoutMs: 3001 }, { drainTimeoutMs: 1001 }, { maxOutputBytes: 2 * 1024 * 1024 + 1 }]) {
    let spawned = false;
    await assert.rejects(runHostCommand('python', [], { ...options, spawn() { spawned = true; } }));
    assert.equal(spawned, false);
  }
});
