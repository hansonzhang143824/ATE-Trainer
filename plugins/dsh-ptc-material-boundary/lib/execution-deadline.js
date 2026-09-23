export const DFT_DEADLINE_MS = 8 * 60 * 1000;

/** Keep the controller alive until the child settles, independent of Captain's turn. */
export async function startWithDeadline(ctx, request, timeoutMs = DFT_DEADLINE_MS) {
  const controller = new AbortController();
  let timer;
  let timedOut = false;
  const forwardAbort = () => controller.abort(request.signal.reason);
  request.signal?.addEventListener('abort', forwardAbort, { once: true });
  if (request.signal?.aborted) forwardAbort();
  const diagnostic = `${request.label}: BLOCKED — execution exceeded ${timeoutMs} ms; child cancellation requested; no retry or stage advance`;
  let finishTimeout;
  const timeout = new Promise((resolve) => { finishTimeout = resolve; });
  const cleanup = () => {
    clearTimeout(timer);
    request.signal?.removeEventListener('abort', forwardAbort);
  };
  timer = setTimeout(() => {
    timedOut = true;
    controller.abort(new Error(diagnostic));
    ctx.logger?.warn?.(diagnostic);
    finishTimeout({ stopReason: 'timeout', diagnostic, structured: { status: 'blocked', question: diagnostic } });
  }, timeoutMs);
  timer.unref?.();
  try {
    const run = await ctx.subagents.start('spawn', { ...request, signal: controller.signal });
    const result = Promise.race([
      Promise.resolve(run.result).then((outcome) => timedOut
        ? { stopReason: 'timeout', diagnostic, structured: { status: 'blocked', question: diagnostic } }
        : outcome),
      timeout,
    ]).finally(cleanup);
    return { ...run, result };
  } catch (error) {
    cleanup();
    throw error;
  }
}
