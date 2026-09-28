import test from 'node:test';
import assert from 'node:assert/strict';
import { setTimeout as delay } from 'node:timers/promises';
import { createTrainingLifecycle } from '../lib/training-lifecycle.js';

const never = () => new Promise(() => {});
function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

test('deadline bounds startup that never resolves and revokes before abort', async () => {
  let revoked = false;
  const lifecycle = createTrainingLifecycle({ timeoutMs: 15, onCancel() { revoked = true; } });
  lifecycle.signal.addEventListener('abort', () => assert.equal(revoked, true));
  const result = assert.rejects(lifecycle.race(never(), { label: 'agents.create' }),
    { code: 'TRAINING_CANCELLED', stopReason: 'timeout' });
  await Promise.all([result, delay(30)]);
  assert.equal(lifecycle.state().deadlineActive, false);
  assert.equal(lifecycle.state().operations[0].status, 'pending');
  assert.equal(lifecycle.state().childSettlement, 'unknown');
});

test('stop works during startup; late parent is disposed and never accepted', async () => {
  const pending = deferred();
  let disposalCount = 0;
  let accepted = false;
  const lifecycle = createTrainingLifecycle({ timeoutMs: 1000 });
  const result = lifecycle.race(pending.promise, {
    label: 'parent', disposeLate: (handle) => handle.dispose(),
  }).then(() => { accepted = true; });
  const rejected = assert.rejects(result, { code: 'TRAINING_CANCELLED' });
  lifecycle.cancel('user stopped startup');
  await rejected;
  pending.resolve({ dispose() { disposalCount += 1; } });
  await delay(0);
  assert.equal(disposalCount, 1);
  assert.equal(accepted, false);
  assert.equal(lifecycle.state().disposals[0].status, 'completed');
});

test('late child launch after cancellation is disposed while raw settlement remains visible', async () => {
  const pending = deferred();
  let disposed = false;
  const lifecycle = createTrainingLifecycle({ timeoutMs: 1000 });
  const rejected = assert.rejects(lifecycle.race(pending.promise, {
    label: 'subagents.start', disposeLate: (child) => child.dispose(),
  }), { code: 'TRAINING_CANCELLED' });
  lifecycle.cancel('stopped');
  await rejected;
  pending.resolve({ dispose() { disposed = true; } });
  await delay(0);
  assert.equal(disposed, true);
  assert.equal(lifecycle.state().operations[0].status, 'fulfilled');
  assert.equal(lifecycle.state().childSettled, null);
});

test('ignored abort cannot hold terminal result or falsely prove child termination', async () => {
  const child = deferred();
  const lifecycle = createTrainingLifecycle({ timeoutMs: 1000 });
  const result = lifecycle.race(child.promise, { label: 'child.result', trackSettlement: true });
  const rejected = assert.rejects(result, { code: 'TRAINING_CANCELLED' });
  lifecycle.cancel('user stopped');
  await rejected;
  assert.equal(lifecycle.state().childSettled, false);
  assert.equal(lifecycle.state().childSettlement, 'unknown');
  child.resolve({ stopReason: 'completed' });
  await delay(0);
  assert.equal(lifecycle.state().childSettled, true);
  assert.equal(lifecycle.state().cancellationRequested, true);
});

test('hung disposal is bounded, recorded, and never holds close or terminal cancellation', async () => {
  const lifecycle = createTrainingLifecycle({ timeoutMs: 1000, disposeTimeoutMs: 10 });
  lifecycle.own({ dispose: never }, 'hung parent');
  const rejected = assert.rejects(lifecycle.race(never(), { trackSettlement: true }),
    { code: 'TRAINING_CANCELLED' });
  lifecycle.cancel('stop');
  await rejected;
  assert.equal(lifecycle.state().disposals[0].status, 'pending');
  await delay(25);
  assert.equal(lifecycle.state().disposals[0].status, 'timed_out');
  assert.match(lifecycle.state().disposals[0].error, /termination unknown/);
  assert.equal(lifecycle.state().childSettled, false);
  assert.equal(lifecycle.state().deadlineActive, false);
});

test('actual completion clears deadline on close and disposes a retained handle once', async () => {
  let disposed = 0;
  let cancels = 0;
  const lifecycle = createTrainingLifecycle({ timeoutMs: 25, onCancel() { cancels += 1; } });
  const handle = { dispose() { disposed += 1; } };
  assert.equal(await lifecycle.race(Promise.resolve(handle), {
    label: 'parent', disposeLate: (value) => value.dispose(),
  }), handle);
  lifecycle.own(handle, 'parent');
  assert.deepEqual(await lifecycle.race(Promise.resolve({ status: 'done' }), {
    label: 'child.result', trackSettlement: true,
  }), { status: 'done' });
  lifecycle.close();
  lifecycle.close();
  await delay(40);
  assert.equal(disposed, 1);
  assert.equal(cancels, 0);
  assert.equal(lifecycle.state().childSettlement, 'fulfilled');
  assert.equal(lifecycle.state().deadlineActive, false);
});

test('throwing disposal is recorded without masking child failure', async () => {
  const lifecycle = createTrainingLifecycle({ timeoutMs: 1000 });
  lifecycle.own({ dispose() { throw new Error('dispose failed'); } }, 'parent');
  await assert.rejects(lifecycle.race(Promise.reject(new Error('child failed')), {
    trackSettlement: true,
  }), /child failed/);
  lifecycle.close();
  await delay(0);
  assert.equal(lifecycle.state().childSettlement, 'rejected');
  assert.equal(lifecycle.state().disposals[0].status, 'failed');
  assert.equal(lifecycle.state().disposals[0].error, 'dispose failed');
});

test('cancelled lifecycle never invokes a new startup thunk', async () => {
  const lifecycle = createTrainingLifecycle({ timeoutMs: 1000 });
  lifecycle.cancel('already stopped');
  let started = false;
  await assert.rejects(lifecycle.race(() => { started = true; }), { code: 'TRAINING_CANCELLED' });
  assert.equal(started, false);
});
