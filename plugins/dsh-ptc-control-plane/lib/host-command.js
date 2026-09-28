import { spawn as nativeSpawn } from 'node:child_process';
import path from 'node:path';

const MAX_OUTPUT_BYTES = 2 * 1024 * 1024;
const positiveBudget = (value, maximum, name) => {
  if (!Number.isInteger(value) || value <= 0 || value > maximum) throw new Error(`${name} exceeds ${maximum}`);
  return value;
};
const message = error => String(error?.message ?? error);

/** Fixed-command host adapter helper; never expose executable/args through HTTP.
 * Cancellation requests and observed process termination are separate evidence.
 * spawn/platform and smaller budgets support deterministic in-process tests. */
export async function runHostCommand(executable, args, options = {}) {
  const { cwd, signal, spawn = nativeSpawn, platform = process.platform } = options;
  const timeoutMs = positiveBudget(options.timeoutMs ?? 30_000, 30_000, 'host command budget');
  const killTimeoutMs = positiveBudget(options.killTimeoutMs ?? 3000, 3000, 'tree termination budget');
  const drainTimeoutMs = positiveBudget(options.drainTimeoutMs ?? 1000, 1000, 'child close budget');
  const maxOutputBytes = positiveBudget(options.maxOutputBytes ?? MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES, 'host output limit');
  const command = [executable, ...args].join(' ');
  const startedAt = new Date().toISOString();
  const notStarted = (stopReason, error) => ({ command, startedAt, finishedAt: new Date().toISOString(),
    exitCode: null, status: 'blocked', stopReason, ...(error ? { error } : {}), stdout: '', stderr: '',
    processStarted: false, directChildClosed: false, treeTerminationConfirmed: false,
    termination: { status: 'not_started' }, terminationConfirmed: true });
  if (signal?.aborted) return notStarted('aborted');
  let child;
  try { child = spawn(executable, args, { cwd, windowsHide: true, shell: false }); }
  catch (error) { return notStarted('spawn_error', message(error)); }
  let receivedBytes = 0, capturedBytes = 0, closed = false, closeResult;
  let stopReason, processError, deadline, resolveCompletion, resolveStop;
  const chunks = { stdout: [], stderr: [] };
  const completion = new Promise(resolve => { resolveCompletion = resolve; });
  const stopped = new Promise(resolve => { resolveStop = resolve; });
  const processStarted = Number.isSafeInteger(child.pid) && child.pid > 0;
  const requestStop = reason => {
    if (stopReason || closed) return;
    stopReason = reason;
    resolveStop({ stopReason: reason });
  };
  const capture = name => chunk => {
    const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk));
    receivedBytes += bytes.length;
    const remaining = Math.max(0, maxOutputBytes - capturedBytes);
    if (remaining) {
      const kept = Buffer.from(bytes.subarray(0, remaining));
      chunks[name].push(kept); capturedBytes += kept.length;
    }
    if (receivedBytes > maxOutputBytes) requestStop('output_limit');
  };
  const stdoutData = capture('stdout'); const stderrData = capture('stderr');
  const onError = error => {
    processError = message(error);
    // An error on an existing process is not evidence that it exited. Stop it
    // through the same bounded tree-cancellation path as timeout/abort.
    requestStop(processStarted ? 'process_error' : 'spawn_error');
  };
  const onClose = (exitCode, exitSignal) => {
    closed = true; closeResult = { exitCode, exitSignal };
    resolveCompletion(closeResult);
  };
  child.stdout?.on('data', stdoutData); child.stderr?.on('data', stderrData);
  child.on('error', onError); child.once('close', onClose);
  const abort = () => requestStop('aborted');
  signal?.addEventListener('abort', abort, { once: true });
  if (signal?.aborted) abort();
  deadline = setTimeout(() => requestStop('timeout'), timeoutMs);
  const result = await Promise.race([completion, stopped]);
  clearTimeout(deadline); signal?.removeEventListener('abort', abort);

  let termination = null;
  if (stopReason && processStarted) {
    // Even if the direct child closes after cancellation was requested, it
    // does not prove its descendants exited. Preserve tree-cleanup evidence.
    if (platform === 'win32') {
      const killPath = path.join(process.env.SystemRoot ?? 'C:\\Windows', 'System32', 'taskkill.exe');
      try {
        const killer = spawn(killPath, ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, shell: false });
        let killTimer, killSettled = false, resolveKill;
        let outputBytes = 0, outputTruncated = false;
        const output = [];
        const observeOutput = chunk => {
          const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk));
          const left = Math.max(0, 64 * 1024 - outputBytes);
          if (left) { const kept = Buffer.from(bytes.subarray(0, left)); output.push(kept); outputBytes += kept.length; }
          if (bytes.length > left) outputTruncated = true;
        };
        const killed = new Promise(resolve => { resolveKill = resolve; });
        const settleKill = value => { if (!killSettled) { killSettled = true; resolveKill(value); } };
        const killError = error => settleKill({ status: 'failed', error: message(error) });
        const killClose = exitCode => settleKill({ status: exitCode === 0 ? 'requested' : 'failed', exitCode });
        killer.stdout?.on('data', observeOutput); killer.stderr?.on('data', observeOutput);
        killer.on('error', killError); killer.once('close', killClose);
        killTimer = setTimeout(() => {
          const evidence = { status: 'unknown', reason: 'tree termination command did not settle' };
          // Latch timeout before stopping the helper: killing it may emit close
          // synchronously, which must not become a successful tree-stop report.
          settleKill(evidence);
          try { killer.kill('SIGKILL'); } catch (error) { evidence.helperStopError = message(error); }
        }, killTimeoutMs);
        termination = await killed;
        clearTimeout(killTimer);
        termination = { ...termination, scope: 'process-tree', output: Buffer.concat(output).toString('utf8'), outputTruncated };
        killer.stdout?.removeListener('data', observeOutput); killer.stderr?.removeListener('data', observeOutput);
        killer.stdout?.resume?.(); killer.stderr?.resume?.();
        killer.removeListener('error', killError); killer.removeListener('close', killClose);
        killer.on('error', () => {}); // A timed-out helper may fail after return.
      } catch (error) { termination = { status: 'failed', scope: 'process-tree', error: message(error) }; }
    } else {
      try {
        const requested = child.kill('SIGKILL');
        termination = { status: requested === false ? 'failed' : 'requested', scope: 'direct-child-only' };
      } catch (error) { termination = { status: 'failed', scope: 'direct-child-only', error: message(error) }; }
    }
    if (!closed) {
      let drainTimer;
      await Promise.race([completion, new Promise(resolve => { drainTimer = setTimeout(resolve, drainTimeoutMs); })]);
      clearTimeout(drainTimer);
    }
  } else if (stopReason && !processStarted) {
    termination = { status: 'not_started' };
  }
  child.stdout?.removeListener('data', stdoutData); child.stderr?.removeListener('data', stderrData);
  child.stdout?.resume?.(); child.stderr?.resume?.();
  child.removeListener('error', onError); child.removeListener('close', onClose);
  child.on('error', () => {}); // Late errors must not become unhandled events.
  const treeTerminationConfirmed = Boolean(stopReason && closed && termination?.scope === 'process-tree' && termination?.exitCode === 0);
  return { command, startedAt, finishedAt: new Date().toISOString(), exitCode: null,
    ...result, ...(closeResult ?? {}), ...(stopReason ? { stopReason, exitCode: null, observedExitCode: closeResult?.exitCode ?? null } : {}), ...(processError ? { error: processError } : {}),
    stdout: Buffer.concat(chunks.stdout).toString('utf8'), stderr: Buffer.concat(chunks.stderr).toString('utf8'),
    receivedBytes, outputTruncated: receivedBytes > capturedBytes,
    status: !stopReason && !processError && closeResult?.exitCode === 0 ? 'passed' : 'blocked',
    processStarted, directChildClosed: closed, termination, treeTerminationConfirmed,
    terminationConfirmed: !processStarted || (stopReason ? treeTerminationConfirmed : closed),
  };
}
