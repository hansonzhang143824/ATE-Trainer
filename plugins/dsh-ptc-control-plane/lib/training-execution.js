import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { prepareTrainingMaterials } from './training-materials.js';
import { trainingAddressBook } from './training-paths.js';
import { signTrainingReceipt, verifyTrainingReceipt } from './training-guard.js';
import { assertSafeRunPath } from './run-context.js';

const execFile = promisify(execFileCallback);
const RUN_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const TM = /^TM[0-9]+$/;

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
}

function writeJsonAtomic(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.tmp-${process.pid}-${Date.now()}`;
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
  try {
    fs.renameSync(temporary, file);
  } catch (error) {
    try { fs.unlinkSync(temporary); } catch {}
    throw error;
  }
}

function normalizeTms(value) {
  if (!Array.isArray(value) || value.length === 0) throw new Error('testItems must be a non-empty array');
  const result = [...new Set(value.map((item) => String(item).trim().toUpperCase()))].sort();
  if (result.some((item) => !TM.test(item))) throw new Error('testItems must contain only TM<digits> values');
  return result;
}

export function reconcileInterruptedTrainingRuns(workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  assertSafeRunPath(root, root);
  const runs = path.join(root, 'Training_Materials', 'runs');
  let names;
  try { names = fs.readdirSync(runs); } catch { return []; }
  const reconciled = [];
  const now = options.now instanceof Date ? options.now.toISOString() : new Date().toISOString();
  for (const name of names) {
    try {
      trainingAddressBook(name);
      const stateFile = assertSafeRunPath(root, path.join(runs, name, 'state.json'));
      const state = readJson(stateFile);
      if (!['checking', 'dispatching', 'running'].includes(state.status)) continue;
      const receiptFile = assertSafeRunPath(root, path.join(runs, name, 'dispatch.json'));
      if (fs.existsSync(receiptFile)) {
        const receipt = readJson(receiptFile);
        if (!verifyTrainingReceipt(receipt) || receipt.runId !== name) throw new Error('invalid orphan receipt');
        writeJsonAtomic(receiptFile, signTrainingReceipt({ ...receipt,
          executionStatus: 'closed', closedAt: now, closeReason: 'host_restart',
        }));
      }
      const next = {
        ...state,
        status: 'interrupted',
        outcome: {
          ...(state.outcome && typeof state.outcome === 'object' ? state.outcome : {}),
          mode: 'INTERRUPTED',
          reason: 'host_restarted_before_training_completion',
        },
        updatedAt: now,
        finishedAt: now,
      };
      writeJsonAtomic(stateFile, next);
      reconciled.push(name);
    } catch {}
  }
  return reconciled;
}

async function runDftGate(workspaceRoot, tm, materials) {
  const workbook = path.resolve(workspaceRoot, materials.workbook);
  const outputDirectory = path.resolve(workspaceRoot, materials.dftRoot, tm);
  const args = [
    'scripts/validate_dft_outputs.py', '--tm', tm,
    '--workbook', workbook, '--output-dir', outputDirectory,
  ];
  let stdout;
  let exitCode = 0;
  try {
    ({ stdout } = await execFile('python', args, {
      cwd: workspaceRoot, windowsHide: true, encoding: 'utf8', timeout: 30_000, maxBuffer: 1024 * 1024,
    }));
  } catch (error) {
    if (error.code !== 2 || error.killed) throw error;
    stdout = error.stdout;
    exitCode = 2;
  }
  const report = JSON.parse(stdout);
  if (report.gate !== 'DFT_OUTPUT' || !['ready', 'stale'].includes(report.status)
      || !/^[a-f0-9]{64}$/.test(report.canonicalInput?.sha256)
      || !Array.isArray(report.requiredOutputs) || report.requiredOutputs.length !== 3
      || !Array.isArray(report.missingOrStaleOutputs)
      || (report.status === 'ready' ? exitCode !== 0 || report.missingOrStaleOutputs.length !== 0
        : exitCode !== 2 || report.missingOrStaleOutputs.length === 0)) {
    throw new Error(`invalid DFT_OUTPUT training preflight for ${tm}`);
  }
  return { tm, exitCode, ...report };
}

async function runGateSet(root, testItems, gate, materials) {
  const reports = [];
  for (const tm of testItems) reports.push(await gate(root, tm, materials));
  return reports;
}

function finalProductHashes(root, testItems, materials) {
  return Object.fromEntries(testItems.map(tm => [tm, Object.fromEntries(
    ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'].map(name => {
      const file = assertSafeRunPath(root, path.join(root, materials.dftRoot, tm, name));
      return [name, crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')];
    }),
  )]));
}

async function settleModelExecution({ root, directory, stateFile, checking, dispatch, testItems, gate, materials, productHashes }) {
  try {
    const child = await dispatch.result;
    // A cancelled child may still be draining an already-started tool. Do not
    // certify its partial outputs or delay the blocked state with more gates.
    const cancelled = ['timeout', 'aborted'].includes(child?.stopReason);
    const reports = cancelled ? [] : await runGateSet(root, testItems, gate, materials);
    const ready = !cancelled && reports.every((report) => report.status === 'ready');
    const childDone = child?.stopReason === 'completed' && child?.structured?.status === 'done';
    const completed = ready && childDone;
    const finishedAt = new Date().toISOString();
    const evidenceFile = path.join(directory, 'evidence', 'dft-terminal.json');
    const evidence = {
      schemaVersion: 1,
      runId: checking.runId,
      profileId: 'ptc-dft-expert',
      childSessionId: dispatch.childSessionId,
      childResult: child,
      materialManifest: materials.manifestFile,
      cacheKey: materials.cacheKey,
      finalProducts: completed ? productHashes(root, testItems, materials) : undefined,
      reports,
      verifiedAt: finishedAt,
    };
    writeJsonAtomic(evidenceFile, evidence);
    const state = {
      ...checking,
      status: completed ? 'completed' : 'blocked',
      outcome: {
        mode: completed ? (child.structured.mode ?? 'OVERWRITTEN') : 'BLOCKED',
        modelDispatched: true,
        childSessionId: dispatch.childSessionId,
        reason: completed ? undefined : (child?.structured?.question ?? child?.diagnostic ?? 'child_or_final_gate_did_not_complete'),
        evidence: path.relative(root, evidenceFile),
      },
      updatedAt: finishedAt,
      finishedAt,
    };
    writeJsonAtomic(stateFile, state);
    return { state, evidence, evidenceFile };
  } catch (error) {
    const failedAt = new Date().toISOString();
    const state = {
      ...checking,
      status: 'failed',
      outcome: { mode: 'FAILED', modelDispatched: true, childSessionId: dispatch.childSessionId },
      error: String(error?.message ?? error),
      updatedAt: failedAt,
      finishedAt: failedAt,
    };
    writeJsonAtomic(stateFile, state);
    return { state, error };
  }
}

/**
 * Freeze one DFT training run, then reuse only a matching validated candidate
 * or dispatch a receipt-bound child against the immutable snapshot.
 */
export async function executeTrainingRun(workspaceRoot, input, options = {}) {
  const root = path.resolve(workspaceRoot);
  const runId = input?.runId;
  if (typeof runId !== 'string' || !RUN_ID.test(runId)) throw new Error('runId is invalid');
  trainingAddressBook(runId);
  const testItems = normalizeTms(input?.testItems);
  const directory = path.join(root, 'Training_Materials', 'runs', runId);
  const runFile = assertSafeRunPath(root, path.join(directory, 'run.json'));
  const stateFile = assertSafeRunPath(root, path.join(directory, 'state.json'));
  const lockFile = assertSafeRunPath(root, path.join(directory, 'execution.lock'));
  const context = readJson(runFile);
  const initial = readJson(stateFile);
  if (context.mode !== 'training' || context.runId !== runId) throw new Error('run context is not a matching training identity');
  if (initial.target?.kind !== 'profile' || initial.target.profileId !== 'ptc-dft-expert') {
    throw new Error('the first executable training slice supports only ptc-dft-expert');
  }
  if (initial.status !== 'created') throw new Error(`training run is not startable from status ${initial.status}`);
  fs.writeFileSync(lockFile, `${process.pid}\n`, { encoding: 'utf8', flag: 'wx' });
  const now = options.now instanceof Date ? options.now : new Date();
  const startedAt = now.toISOString();
  const checking = { ...initial, status: 'checking', testItems, startedAt, updatedAt: startedAt };
  writeJsonAtomic(stateFile, checking);
  const gate = options.runDftGate ?? runDftGate;
  const productHashes = options.productHashes ?? finalProductHashes;
  try {
    const materials = await (options.prepareMaterials ?? prepareTrainingMaterials)(root, runId, testItems);
    const reports = await runGateSet(root, testItems, gate, materials);
    const unchanged = materials.cacheCompatible === true && reports.every((report) => report.status === 'ready');
    const evidence = {
      schemaVersion: 1,
      runId,
      profileId: 'ptc-dft-expert',
      mode: unchanged ? 'UNCHANGED' : 'STALE',
      modelDispatched: false,
      materialManifest: materials.manifestFile,
      cacheKey: materials.cacheKey,
      cacheCompatible: materials.cacheCompatible,
      candidateSources: materials.candidateSources,
      finalProducts: unchanged ? productHashes(root, testItems, materials) : undefined,
      reports,
      checkedAt: new Date().toISOString(),
    };
    const evidenceFile = path.join(directory, 'evidence', 'dft-preflight.json');
    writeJsonAtomic(evidenceFile, evidence);
    const finishedAt = new Date().toISOString();
    let state = {
      ...checking,
      status: unchanged ? 'completed' : 'needs_model',
      outcome: unchanged
        ? { mode: 'UNCHANGED', modelDispatched: false, evidence: path.relative(root, evidenceFile) }
        : { mode: 'STALE', modelDispatched: false, reason: 'candidate_outputs_require_isolated_model_execution', evidence: path.relative(root, evidenceFile) },
      updatedAt: finishedAt,
      finishedAt: unchanged ? finishedAt : null,
    };
    writeJsonAtomic(stateFile, state);
    if (!unchanged && typeof options.dispatchModel === 'function') {
      const dispatchingAt = new Date().toISOString();
      state = {
        ...checking,
        status: 'dispatching',
        outcome: { mode: 'STALE', modelDispatched: false, reason: 'dispatch_in_progress', evidence: path.relative(root, evidenceFile) },
        updatedAt: dispatchingAt,
        finishedAt: null,
      };
      writeJsonAtomic(stateFile, state);
      const dispatch = await options.dispatchModel({ runId, context, state, evidence, reports, testItems, runDirectory: directory, materials });
      const runningAt = new Date().toISOString();
      state = {
        ...checking,
        status: 'running',
        outcome: {
          mode: 'MODEL', modelDispatched: true, childSessionId: dispatch.childSessionId,
          receipt: path.relative(root, dispatch.receiptFile), evidence: path.relative(root, evidenceFile),
        },
        updatedAt: runningAt,
        finishedAt: null,
      };
      writeJsonAtomic(stateFile, state);
      const completion = settleModelExecution({ root, directory, stateFile, checking, dispatch, testItems, gate, materials, productHashes });
      completion.catch(() => {});
      options.onBackground?.(completion);
      return { context, state, evidence, evidenceFile, completion, childSessionId: dispatch.childSessionId };
    }
    return { context, state, evidence, evidenceFile };
  } catch (error) {
    const failedAt = new Date().toISOString();
    writeJsonAtomic(stateFile, {
      ...checking,
      status: error?.code === 'TRAINING_CANCELLED' ? 'blocked' : 'failed',
      outcome: error?.code === 'TRAINING_CANCELLED' ? { mode: 'BLOCKED', reason: error.message, stopReason: error.stopReason } : undefined,
      error: String(error?.message ?? error),
      updatedAt: failedAt,
      finishedAt: failedAt,
    });
    throw error;
  } finally {
    try { fs.unlinkSync(lockFile); } catch {}
  }
}
