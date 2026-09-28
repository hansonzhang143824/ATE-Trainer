import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { createTrainingRun } from './training-run.js';
import { executeTrainingRun } from './training-execution.js';

const DIGEST = /^[a-f0-9]{64}$/;
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
function fail(reason) { throw new Error(`simple source adapter: ${reason}`); }
function output(root, file, value) {
  assertSafeRunPath(root, file);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  return sha(fs.readFileSync(file));
}
function sourceId(request) {
  return `source-${sha(Buffer.from(request.dispatchId, 'utf8')).slice(0, 32)}`;
}
function identity(root, request) {
  if (!request || request.mode !== 'SMOKE_ONLY' || request.stage !== 'INPUT_SYNC'
      || !['dft-expert', 'schematic-expert'].includes(request.role)
      || request.dispatchId !== `${request.runId}:INPUT_SYNC:${request.role}:1`
      || !Array.isArray(request.testItems) || !request.testItems.length
      || request.testItems.some(tm => typeof tm !== 'string' || !/^TM\d+$/.test(tm))
      || new Set(request.testItems).size !== request.testItems.length
      || !DIGEST.test(request.profileDigest ?? '')
      || request.profileId !== (request.role === 'dft-expert' ? 'ptc-dft-expert' : 'ptc-schematic-expert')) {
    fail('not a bound INPUT_SYNC source request');
  }
  const runRoot = assertSafeRunPath(root, `Training_Materials/runs/${request.runId}`);
  if (path.resolve(request.runRoot ?? '') !== runRoot) fail('parent run root differs');
  const progress = read(assertSafeRunPath(root, path.join(runRoot, 'simple-orchestration.json')));
  const task = progress.stages?.[0]?.tasks?.find(item => item.dispatchId === request.dispatchId);
  if (progress.runId !== request.runId || progress.mode !== 'SMOKE_ONLY'
      || progress.registryDigest !== request.registryDigest
      || JSON.stringify(progress.testItems) !== JSON.stringify(request.testItems)
      || task?.role !== request.role || task?.profileId !== request.profileId
      || task?.profileVersion !== request.profileVersion || task?.profileDigest !== request.profileDigest) {
    fail('source request differs from frozen parent orchestration');
  }
  return { runRoot, sourceRunId: sourceId(request), kind: request.role === 'dft-expert' ? 'dft-delivery' : 'statistic-only' };
}
function sourceOutcome(root, request, located) {
  const sourceRoot = assertSafeRunPath(root, `Training_Materials/runs/${located.sourceRunId}`);
  const stateFile = assertSafeRunPath(root, path.join(sourceRoot, 'state.json'));
  const state = read(stateFile);
  if (state.runId !== located.sourceRunId || state.status !== 'completed') fail(`${request.role} source run did not complete`);
  if (located.kind === 'dft-delivery') {
    if (state.target?.kind !== 'profile' || state.target.profileId !== 'ptc-dft-expert'
        || !['UNCHANGED', 'CREATED', 'OVERWRITTEN'].includes(state.outcome?.mode)
        || typeof state.outcome.evidence !== 'string') fail('DFT source has no valid terminal mode');
    const evidenceFile = assertSafeRunPath(root, state.outcome.evidence);
    const evidence = read(evidenceFile);
    const reports = evidence.reports;
    if (evidence.runId !== located.sourceRunId || !Array.isArray(reports)
        || reports.length !== request.testItems.length
        || request.testItems.some(tm => !reports.some(report => report.tm === tm && report.gate === 'DFT_OUTPUT'
          && report.status === 'ready' && report.exitCode === 0))) fail('not every DFT TM has a ready gate');
    return { stateFile, sourceEvidenceFile: evidenceFile, sourceMode: state.outcome.mode,
      dftGateStatus: 'ready', dftGateExitCode: 0 };
  }
  if (state.purpose !== 'schematic-statistic-only' || state.target?.kind !== 'pipeline'
      || state.outcome?.mode !== 'STATISTIC_ONLY' || state.outcome?.report?.gatePassed !== false
      || state.outcome?.report?.modelDispatched !== false) fail('schematic source was not statistic-only');
  const evidenceFile = assertSafeRunPath(root, state.outcome.report.path);
  const evidence = read(evidenceFile);
  if (evidence.runId !== located.sourceRunId || evidence.mode !== undefined && evidence.mode !== 'STATISTIC_ONLY'
      || evidence.gatePassed !== false || evidence.modelDispatched !== false) fail('statistic-only evidence differs');
  return { stateFile, sourceEvidenceFile: evidenceFile, sourceMode: 'STATISTIC_ONLY',
    statisticMode: 'STATISTIC_ONLY', businessGatePassed: false };
}
function parentReceipt(root, request, located, outcome) {
  const file = assertSafeRunPath(root, path.join(located.runRoot, 'evidence', 'sources', `${request.role}.json`));
  const sourceStateSha256 = sha(fs.readFileSync(outcome.stateFile));
  const sourceEvidenceSha256 = sha(fs.readFileSync(outcome.sourceEvidenceFile));
  if (!fs.existsSync(file)) {
    output(root, file, { schemaVersion: 1, kind: 'ptc-simple-source',
      runId: request.runId, dispatchId: request.dispatchId, stage: request.stage, role: request.role,
      executionKind: located.kind, profileId: request.profileId,
      profileVersion: request.profileVersion, profileDigest: request.profileDigest,
      sourceRunId: located.sourceRunId, sourceMode: outcome.sourceMode,
      sourceStatePath: outcome.stateFile, sourceStateSha256,
      sourceEvidencePath: outcome.sourceEvidenceFile, sourceEvidenceSha256,
      businessGatePassed: false, createdAt: new Date().toISOString() });
  }
  const existing = read(file);
  if (existing.runId !== request.runId || existing.dispatchId !== request.dispatchId
      || existing.sourceRunId !== located.sourceRunId || existing.executionKind !== located.kind
      || existing.sourceStateSha256 !== sourceStateSha256
      || existing.sourceEvidenceSha256 !== sourceEvidenceSha256) fail('source receipt changed or source evidence was modified');
  return { status: 'done', executionKind: located.kind, stage: request.stage, role: request.role,
    profileId: request.profileId, profileVersion: request.profileVersion,
    profileDigest: request.profileDigest, testItems: [...request.testItems],
    childReceiptId: located.sourceRunId, childEvidencePath: file, childEvidenceSha256: sha(fs.readFileSync(file)),
    ...(located.kind === 'dft-delivery' ? { dftGateStatus: 'ready', dftGateExitCode: 0 }
      : { statisticMode: 'STATISTIC_ONLY', businessGatePassed: false }) };
}

/** Source execution is always a fresh run derived from this parent dispatch.
 * Recovery reads only that same run; it never adopts an unrelated old result.
 */
export function createSimpleOrchestrationSourceAdapters(workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const dft = options.executeDftRun ?? executeTrainingRun;
  const pipelineManager = options.pipelineManager;
  return {
    async executeSmokeRole(request) {
      const located = identity(root, request);
      if (request.signal?.aborted) throw request.signal.reason ?? new Error('source dispatch cancelled');
      const target = located.kind === 'dft-delivery'
        ? { kind: 'profile', profileId: 'ptc-dft-expert' }
        : { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' };
      createTrainingRun(root, { runId: located.sourceRunId, target,
        purpose: located.kind === 'statistic-only' ? 'schematic-statistic-only' : 'business-training' });
      const stop = () => {
        if (located.kind === 'dft-delivery') options.stopDftRun?.(located.sourceRunId);
        else { try { pipelineManager?.control(located.sourceRunId, 'stop'); } catch {} }
      };
      request.signal?.addEventListener('abort', stop, { once: true });
      try {
        if (located.kind === 'dft-delivery') {
          if (options.dispatchModel && typeof options.stopDftRun !== 'function') fail('DFT model dispatch requires a child stop adapter');
          const run = await dft(root, { runId: located.sourceRunId, testItems: request.testItems },
            options.dispatchModel ? { dispatchModel: options.dispatchModel } : {});
          if (run.completion) await run.completion;
        } else {
          if (!pipelineManager || typeof pipelineManager.start !== 'function') fail('statistic-only pipeline manager is unavailable');
          const run = pipelineManager.start({ runId: located.sourceRunId, testItems: request.testItems, modelChoice: 'default' });
          if (!run?.completion) fail('statistic-only manager returned no completion');
          await run.completion;
        }
        if (request.signal?.aborted) throw request.signal.reason ?? new Error('source dispatch cancelled');
        return parentReceipt(root, request, located, sourceOutcome(root, request, located));
      } finally { request.signal?.removeEventListener('abort', stop); }
    },
    recoverSmokeRole(request) {
      const located = identity(root, request);
      return parentReceipt(root, request, located, sourceOutcome(root, request, located));
    },
  };
}
