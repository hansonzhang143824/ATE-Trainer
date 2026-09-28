import fs from 'node:fs';
import path from 'node:path';
import { sha256Bytes } from './release-integrity.js';
import { assertSafeRunPath } from './run-context.js';
import { trainingAddressBook } from './training-paths.js';

const SHA = /^[a-f0-9]{64}$/;
const MAX_JSON_BYTES = 16 * 1024 * 1024;
const MAX_ARTIFACT_BYTES = 64 * 1024 * 1024;
const DEFAULT_BUDGET_MS = 30_000;
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

/**
 * Read-only, deny-by-default preflight for a future *business* publisher.
 * Current run-local records are necessary but not sufficient: the runtime has
 * no independent trusted evaluator attestation binding the candidate snapshot,
 * canonical Python-plaintext inputs, every real gate and compilation. Therefore
 * this API intentionally cannot return eligible=true with the present schema.
 */
export function assessBusinessReleaseEligibility(workspaceRoot, runId, options = {}) {
  const reasons = [];
  const checks = [];
  const started = Date.now();
  const budgetMs = Number.isFinite(options.budgetMs) && options.budgetMs > 0
    ? Math.min(options.budgetMs, DEFAULT_BUDGET_MS) : DEFAULT_BUDGET_MS;
  const checkTime = () => { if (Date.now() - started > budgetMs) throw new Error('30-second deterministic preflight budget exceeded'); };
  const requireProof = (condition, code) => {
    checks.push({ code, passed: Boolean(condition) });
    if (!condition) reasons.push(code);
    return Boolean(condition);
  };
  const root = path.resolve(workspaceRoot);
  let runRoot;
  const file = (name) => {
    checkTime();
    const absolute = assertSafeRunPath(root, path.join(runRoot, name));
    const relative = path.relative(runRoot, absolute);
    if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) throw new Error('evidence escapes run');
    const stat = fs.lstatSync(absolute);
    if (!stat.isFile() || stat.nlink !== 1 || stat.size > MAX_JSON_BYTES) throw new Error(`unsafe evidence file: ${name}`);
    return absolute;
  };
  const json = name => JSON.parse(fs.readFileSync(file(name), 'utf8').replace(/^\uFEFF/, ''));
  const artifactDigest = absolute => {
    checkTime();
    const checked = assertSafeRunPath(root, absolute);
    const relative = path.relative(runRoot, checked);
    if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) throw new Error('artifact escapes run');
    const stat = fs.lstatSync(checked);
    if (!stat.isFile() || stat.nlink !== 1 || stat.size === 0 || stat.size > MAX_ARTIFACT_BYTES) throw new Error('unsafe artifact');
    return { sha256: sha256Bytes(fs.readFileSync(checked)), size: stat.size };
  };
  try {
    runRoot = assertSafeRunPath(root, trainingAddressBook(runId).runRoot);
    const context = json('run.json');
    const state = json('state.json');
    const progress = json('pipeline-progress.json');
    const registry = json('pipeline-registry.json');
    const materials = json('pipeline-material-manifest.json');
    const stages = registry.stateMachine?.filter(stage => stage !== 'COMPLETE');
    requireProof(context.schemaVersion === 1 && context.mode === 'training' && context.runId === runId
      && context.releaseId === null && context.projectId === null
      && path.resolve(root, context.artifactRoot ?? '') === runRoot, 'RUN_IDENTITY_INVALID');
    requireProof(state.runId === runId && state.purpose === 'business-training'
      && state.target?.kind === 'pipeline' && state.status === 'completed'
      && state.outcome?.mode === 'PIPELINE' && state.outcome?.realBusinessGatesPassed !== false,
    'NOT_COMPLETED_BUSINESS_TRAINING');
    requireProof(Array.isArray(stages) && stages.length === 7 && stages[0] === 'INPUT_SYNC'
      && stages.at(-1) === 'COMPILE' && new Set(stages).size === stages.length
      && state.target?.fromStage === 'INPUT_SYNC' && state.target?.toStage === 'COMPILE'
      && equal(state.target?.stages, stages) && progress.status === 'completed'
      && progress.runId === runId && equal(progress.stages?.map(item => item.stage), stages),
    'FULL_AUTHORITATIVE_STAGE_CHAIN_NOT_PROVEN');
    requireProof(materials.schemaVersion === 1 && materials.kind === 'ptc-pipeline-materials'
      && materials.runId === runId && SHA.test(materials.pipelineCacheKey ?? '')
      && Array.isArray(materials.testItems) && materials.testItems.length > 0
      && equal(progress.testItems, materials.testItems), 'FROZEN_MATERIAL_IDENTITY_NOT_PROVEN');
    if (Array.isArray(stages) && Array.isArray(progress.stages)) {
      for (const stageName of stages) {
        checkTime();
        const stage = progress.stages.find(item => item.stage === stageName);
        const definition = registry.stages?.[stageName];
        const gate = stage?.gateResult;
        const common = stage?.status === 'completed' && gate?.status === 'passed' && gate.exitCode === 0
          && gate.gate === definition?.gate && Array.isArray(stage?.terminals)
          && stage.terminals.length === (stageName === 'INPUT_SYNC' ? 2 : 1)
          && stage.terminals.every(item => item.status === 'done' && equal(item.testItems, materials.testItems));
        requireProof(common, `STAGE_${stageName}_NOT_PROVEN`);
        if (!common) continue;
        if (stageName !== 'COMPILE') {
          try {
            const receiptPath = gate.receiptPath;
            const receiptName = path.relative(runRoot, path.resolve(receiptPath));
            if (!receiptName.startsWith(`verification${path.sep}`) || !SHA.test(gate.receiptSha256 ?? '')) throw new Error('unbound gate receipt');
            const receipt = json(receiptName);
            const digest = artifactDigest(receiptPath);
            requireProof(digest.sha256 === gate.receiptSha256 && receipt.kind === 'training-stage-gate'
              && receipt.runId === runId && receipt.stage === stageName && receipt.gate === definition.gate
              && receipt.action === 'gate' && receipt.status === 'passed' && receipt.exitCode === 0
              && receipt.pipelineCacheKey === materials.pipelineCacheKey
              && equal(receipt.testItems, materials.testItems), `STAGE_${stageName}_RECEIPT_INVALID`);
          } catch { requireProof(false, `STAGE_${stageName}_RECEIPT_INVALID`); }
        } else {
          try {
            const report = json('compile/build-report.json');
            const reportPath = path.join(runRoot, 'compile', 'build-report.json');
            const reportDigest = artifactDigest(reportPath).sha256;
            const commandOk = Array.isArray(report.commands) && report.commands.length === 2
              && report.commands.every(command => command.closed === true && command.exitCode === 0);
            const artifactsOk = Array.isArray(report.artifacts) && report.artifacts.length === 2
              && report.artifacts.every(item => {
                if (!SHA.test(item.sha256 ?? '')) return false;
                const checked = artifactDigest(item.path);
                return checked.sha256 === item.sha256 && checked.size === item.size;
              });
            requireProof(gate.adapter === 'training-compile.js' && gate.reportPath === reportPath
              && gate.reportSha256 === reportDigest && report.runId === runId
              && report.mode === 'training' && report.stage === 'COMPILE' && report.status === 'passed'
              && SHA.test(report.sourceSha256 ?? '') && SHA.test(report.projectSha256 ?? '')
              && commandOk && artifactsOk, 'COMPILE_REPORT_OR_ARTIFACT_INVALID');
          } catch { requireProof(false, 'COMPILE_REPORT_OR_ARTIFACT_INVALID'); }
        }
      }
    }
  } catch (error) {
    reasons.push(`PREFLIGHT_EVIDENCE_UNREADABLE: ${error.message}`);
  }
  // Current gate receipts do not independently bind every registry-required
  // output or re-check canonical DLP inputs through the approved Python view.
  // A run-local "passed" flag cannot stand in for those missing proofs.
  reasons.push('CANONICAL_PLAINTEXT_SOURCE_BINDING_UNVERIFIED');
  reasons.push('REQUIRED_STAGE_OUTPUT_BINDING_UNVERIFIED');
  reasons.push('TRUSTED_BUSINESS_EVALUATOR_ATTESTATION_UNAVAILABLE');
  return { eligible: false, runId, checks, reasons: [...new Set(reasons)],
    elapsedMs: Date.now() - started };
}
