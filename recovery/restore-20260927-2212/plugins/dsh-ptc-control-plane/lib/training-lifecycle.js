export class TrainingCancellationError extends Error {
  constructor(reason, stopReason = 'aborted') {
    super(String(reason?.message ?? reason ?? 'training run stopped'));
    this.name = 'TrainingCancellationError';
    this.code = 'TRAINING_CANCELLED';
    this.stopReason = stopReason;
  }
}

/** Deadline covers startup as well as execution. Cancellation is not proof of
 * child termination: raw settlement and disposal evidence remain independent. */
export function createTrainingLifecycle(options = {}) {
  const timeoutMs = options.timeoutMs ?? 8 * 60 * 1000;
  const disposeTimeoutMs = options.disposeTimeoutMs ?? 1000;
  if (!(timeoutMs > 0) || !Number.isFinite(timeoutMs)
      || !(disposeTimeoutMs > 0) || !Number.isFinite(disposeTimeoutMs)) {
    throw new Error('training lifecycle timeouts must be finite positive numbers');
  }
  const controller = new AbortController();
  const operations = [];
  const disposals = [];
  const resources = new Map();
  let cancellation;
  let closed = false;
  let deadline;
  let childSettled = null;
  let childSettlement = 'unknown';
  const now = () => new Date().toISOString();
  const state = () => ({
    cancellationRequested: Boolean(cancellation), closed,
    reason: cancellation?.message ?? null, stopReason: cancellation?.stopReason ?? null,
    childSettled, childSettlement, deadlineActive: Boolean(deadline),
    operations: operations.map((entry) => ({ ...entry })),
    disposals: disposals.map((entry) => ({ ...entry })),
  });
  function emit(type, details = {}) {
    try { options.onEvent?.({ type, ...details, at: now() }, state()); } catch {}
  }
  function clearDeadline() {
    if (deadline) clearTimeout(deadline);
    deadline = undefined;
  }
  function disposeResource(resource) {
    if (resource.started) return;
    resource.started = true;
    const entry = { label: resource.label, status: 'pending', startedAt: now() };
    disposals.push(entry);
    const timer = setTimeout(() => {
      entry.status = 'timed_out';
      entry.error = `disposal exceeded ${disposeTimeoutMs} ms; termination unknown`;
      entry.finishedAt = now();
      emit('disposal_timeout', { label: entry.label, error: entry.error });
    }, disposeTimeoutMs);
    timer.unref?.();
    emit('disposal_started', { label: entry.label });
    Promise.resolve().then(() => resource.dispose(resource.handle)).then(
      () => {
        clearTimeout(timer);
        const late = entry.status === 'timed_out';
        entry.status = late ? 'completed_late' : 'completed';
        entry.finishedAt = now();
        emit('disposal_completed', { label: entry.label });
      },
      (error) => {
        clearTimeout(timer);
        entry.status = 'failed';
        entry.error = String(error?.message ?? error);
        entry.finishedAt = now();
        emit('disposal_failed', { label: entry.label, error: entry.error });
      },
    );
  }
  function own(handle, label = 'resource', dispose = (value) => value?.dispose?.()) {
    if (handle == null) return handle;
    if (!resources.has(handle)) resources.set(handle, { handle, label, dispose, started: false });
    if (closed || cancellation) disposeResource(resources.get(handle));
    return handle;
  }
  function close() {
    clearDeadline();
    closed = true;
    for (const resource of resources.values()) disposeResource(resource);
    emit('closed');
  }
  function cancel(reason = 'training run stopped', { stopReason = 'aborted' } = {}) {
    if (cancellation || closed) return false;
    cancellation = new TrainingCancellationError(reason, stopReason);
    clearDeadline();
    // Revoke access synchronously before any child observes the abort signal.
    try { options.onCancel?.(cancellation, state()); } catch (error) {
      emit('cancel_hook_failed', { error: String(error?.message ?? error) });
    }
    controller.abort(cancellation);
    emit('cancellation_requested');
    close();
    return true;
  }
  async function race(promiseOrThunk, settings = {}) {
    if (cancellation || closed) {
      // A caller may already have started a promise; still consume its result
      // and dispose a late resource. A thunk is never invoked after close.
      if (typeof promiseOrThunk !== 'function') Promise.resolve(promiseOrThunk).then(
        (value) => { if (settings.disposeLate) own(value, settings.label, settings.disposeLate); }, () => {},
      );
      throw cancellation ?? new TrainingCancellationError('training lifecycle closed');
    }
    const entry = { label: settings.label ?? 'operation', status: 'pending', startedAt: now() };
    operations.push(entry);
    if (settings.trackSettlement) childSettled = false;
    emit('operation_started', { label: entry.label });
    let onAbort;
    const cancelled = new Promise((resolve, reject) => {
      onAbort = () => reject(cancellation ?? new TrainingCancellationError(controller.signal.reason));
      controller.signal.addEventListener('abort', onAbort, { once: true });
    });
    const raw = Promise.resolve().then(() => {
      if (typeof promiseOrThunk !== 'function') return promiseOrThunk;
      if (cancellation || closed) throw cancellation ?? new TrainingCancellationError('training lifecycle closed');
      return promiseOrThunk();
    }).then((value) => {
      entry.status = 'fulfilled';
      entry.settledAt = now();
      if (settings.trackSettlement) { childSettled = true; childSettlement = 'fulfilled'; }
      if (settings.disposeLate) own(value, entry.label, settings.disposeLate);
      emit('operation_settled', { label: entry.label });
      return value;
    }, (error) => {
      entry.status = 'rejected';
      entry.error = String(error?.message ?? error);
      entry.settledAt = now();
      if (settings.trackSettlement) { childSettled = true; childSettlement = 'rejected'; }
      emit('operation_settled', { label: entry.label, error: entry.error });
      throw error;
    });
    try {
      const value = await Promise.race([raw, cancelled]);
      if (cancellation || closed) throw cancellation ?? new TrainingCancellationError('training lifecycle closed');
      return value;
    } finally {
      controller.signal.removeEventListener('abort', onAbort);
    }
  }
  deadline = setTimeout(() => cancel(`training execution exceeded ${timeoutMs} ms`, { stopReason: 'timeout' }), timeoutMs);
  deadline.unref?.();
  return { signal: controller.signal, race, own, cancel, close, state };
}
