import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { prepareTrainingMaterials, verifyTrainingMaterials } from './training-materials.js';
import { trainingAddressBook } from './training-paths.js';
import { signTrainingReceipt, verifyTrainingReceipt } from './training-guard.js';
import { assertSafeRunPath } from './run-context.js';
import { resolveAgentProfile, assertDftExecutionCapability } from './agent-profile-runtime.js';
import { createBusinessOutputHashRecord } from './business-output-contract.js';

const execFile = promisify(execFileCallback);
const RUN_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const TM = /^TM[0-9]+$/;
const DIGEST = /^[a-f0-9]{64}$/;

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
      const receiptFile = assertSafeRunPath(root, path.join(runs, name, 'dispatch.json'));
      if (fs.existsSync(receiptFile)) {
        const receipt = readJson(receiptFile);
        if (!verifyTrainingReceipt(receipt) || receipt.runId !== name) throw new Error('invalid orphan receipt');
        writeJsonAtomic(receiptFile, signTrainingReceipt({ ...receipt,
          executionStatus: 'closed', closedAt: now, closeReason: 'host_restart',
        }));
      }
      if (!['checking', 'dispatching', 'running'].includes(state.status)) continue;
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

export async function runDftGate(workspaceRoot, tm, materials) {
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

/** Host-generated, bounded raw workbook evidence for the model. The producer
 * owns both hashes; this adapter validates and records them without inventing
 * another byte view or allowing a caller-selected command/path. */
export async function prepareDftSourceView(workspaceRoot, testItems, materials, verifyMaterials = verifyTrainingMaterials) {
  const root = path.resolve(workspaceRoot);
  await verifyMaterials(root, materials);
  const args = ['-X', 'utf8', 'scripts/training_dft_source_view.py', '--run-id', materials.runId,
    ...testItems.flatMap((tm) => ['--tm', tm])];
  const { stdout } = await execFile('python', args, {
    cwd: root, windowsHide: true, encoding: 'utf8', timeout: 30_000, maxBuffer: 512 * 1024,
  });
  const report = JSON.parse(stdout);
  const expectedItems = [...new Set(testItems)].sort();
  const file = assertSafeRunPath(root, path.join(root, materials.sourceView));
  if (report.status !== 'SOURCE_VIEW' || report.runId !== materials.runId || report.path !== materials.sourceView
      || !/^[a-f0-9]{64}$/.test(report.sha256) || !/^[a-f0-9]{64}$/.test(report.sourceSha256)
      || JSON.stringify(report.testItems) !== JSON.stringify(expectedItems)
      || !Number.isSafeInteger(report.bytes) || report.bytes <= 0 || report.bytes > 128 * 1024
      || !fs.statSync(file).isFile() || fs.statSync(file).size !== report.bytes) {
    throw new Error('invalid DFT source-view producer report');
  }
  await verifyMaterials(root, materials);
  return report;
}

async function runPython(root, args, maxBuffer = 1024 * 1024) {
  return execFile('python', ['-X', 'utf8', ...args], {
    cwd: root, windowsHide: true, encoding: 'utf8', timeout: 30_000, maxBuffer,
  });
}

function reportedDigest(stdout, name) {
  const value = new RegExp(`(?:^|[;\\s])${name}=([a-f0-9]{64})(?:[;\\s]|$)`, 'm').exec(stdout)?.[1];
  if (!DIGEST.test(value ?? '')) throw new Error(`DFT producer did not report ${name}`);
  return value;
}

/** Run the deterministic producers before model review.  The model receives
 * plaintext through one fixed Python adapter because protected materials are
 * deliberately unreadable through Node's byte view. */
export async function prepareDftReviewInput(workspaceRoot, testItems, materials, sourceView,
  preflightReports, verifyMaterials = verifyTrainingMaterials) {
  const root = path.resolve(workspaceRoot);
  if (!DIGEST.test(sourceView?.sourceSha256 ?? '')) throw new Error('source view lacks canonical digest');
  await verifyMaterials(root, materials);
  const items = [];
  for (const tm of testItems) {
    const output = `${materials.dftRoot}/${tm}`;
    const meta = `${output}/dft-meta.json`;
    const completeBefore = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json']
      .every((name) => fs.existsSync(assertSafeRunPath(root, path.join(root, output, name))));
    const refresh = await runPython(root, [
      'scripts/refresh_dft_meta_from_source.py', '--source', materials.workbook,
      '--tm', tm, '--meta', meta, '--expected-sha', sourceView.sourceSha256,
      '--input-root', materials.runRoot,
    ], 2 * 1024 * 1024);
    const metaSha256 = reportedDigest(refresh.stdout, 'metaSha256');
    const render = await runPython(root, [
      'scripts/render_dft_conditions_yaml.py', '--tm', tm,
      '--out', `${output}/dft-conditions.yaml`, '--expected-sha', sourceView.sourceSha256,
      '--workbook', materials.workbook,
    ]);
    const conditionsSha256 = reportedDigest(render.stdout, 'outputSha256');
    const { stdout } = await runPython(root, [
      'scripts/training_dft_review_input.py', '--run-id', materials.runId, '--tm', tm,
      '--source-sha', sourceView.sourceSha256, '--meta-sha', metaSha256,
      '--conditions-sha', conditionsSha256,
    ], 2 * 1024 * 1024);
    const reviewInput = JSON.parse(stdout);
    if (reviewInput.status !== 'REVIEW_INPUT' || reviewInput.runId !== materials.runId
        || reviewInput.tm !== tm || reviewInput.sourceSha256 !== sourceView.sourceSha256
        || reviewInput.producerDigests?.['dft-meta.json'] !== metaSha256
        || reviewInput.producerDigests?.['dft-conditions.yaml'] !== conditionsSha256) {
      throw new Error(`invalid DFT semantic-review input for ${tm}`);
    }
    const preflight = preflightReports.find((report) => report.tm === tm);
    if (!preflight) throw new Error(`missing DFT preflight report for ${tm}`);
    const mode = completeBefore ? 'OVERWRITTEN' : 'CREATED';
    items.push({ ...reviewInput, mode });
  }
  await verifyMaterials(root, materials);
  return { schemaVersion: 1, runId: materials.runId, sourceSha256: sourceView.sourceSha256, items };
}

export async function bindDftSemanticReviews(workspaceRoot, materials, reviewInput, structured,
  verifyMaterials = verifyTrainingMaterials) {
  const root = path.resolve(workspaceRoot);
  const reviews = structured?.reviews;
  if (structured?.status !== 'done' || !Array.isArray(reviews)
      || reviews.length !== reviewInput.items.length) throw new Error('DFT semantic reviewer did not return all assigned reviews');
  await verifyMaterials(root, materials);
  for (const item of reviewInput.items) {
    const review = reviews.find((candidate) => candidate?.tm === item.tm);
    if (!review || review.verdict !== 'PASS' || !Array.isArray(review.findings)
        || review.findings.length === 0 || review.findings.some((finding) => typeof finding !== 'string' || !finding.trim())) {
      throw new Error(`DFT semantic review did not PASS for ${item.tm}`);
    }
    const output = `${materials.dftRoot}/${item.tm}/dft-semantic-review.json`;
    const { stdout } = await runPython(root, [
      'scripts/write_dft_semantic_review.py', '--tm', item.tm, '--out', output,
      '--source-sha', item.sourceSha256,
      '--meta-sha', item.producerDigests['dft-meta.json'],
      '--conditions-sha', item.producerDigests['dft-conditions.yaml'],
      '--findings-json', JSON.stringify(review.findings),
    ]);
    const report = JSON.parse(stdout);
    if (report.status !== 'REVIEW_BOUND' || report.tm !== item.tm
        || report.sourceSha256 !== item.sourceSha256
        || report.metaSha256 !== item.producerDigests['dft-meta.json']
        || report.conditionsSha256 !== item.producerDigests['dft-conditions.yaml']) {
      throw new Error(`invalid DFT semantic-review binding report for ${item.tm}`);
    }
  }
  await verifyMaterials(root, materials);
}

/** Return a host-owned PASS only when the approved adapter has already proven
 * exact source preservation and cross-product semantic equality. Anything
 * less certain returns null and remains model-review work. */
export function deterministicDftSemanticReviews(reviewInput) {
  if (!Array.isArray(reviewInput?.items) || reviewInput.items.length === 0) return null;
  const reviews = [];
  for (const item of reviewInput.items) {
    const facts = item?.sourceEvidence?.facts;
    const meta = item?.metaProjection;
    const condition = meta?.testCondition;
    const sourceLocation = meta?.sourceLocation;
    const exact = typeof facts === 'object' && facts !== null
      && String(facts.Item ?? '').trim().toUpperCase() === item.tm
      && sourceLocation?.sheet === item.sourceEvidence?.sheet
      && sourceLocation?.row === item.sourceEvidence?.row
      && meta?.parseStatus === 'ok'
      && Array.isArray(meta?.openItems) && meta.openItems.length === 0
      && meta?.rawIntentMatchesSource === true
      && condition?.identity === facts.Name
      && condition?.remarks === facts.Notes
      && condition?.expectedValue === facts.ExpectValue
      && condition?.measurement === facts.Check
      && item?.conditionsProjection?.tm === item.tm
      && item.conditionsProjection?.sourceSha256 === item.sourceSha256
      && item.conditionsProjection?.semanticFieldsMatchMeta === true;
    if (!exact) return null;
    reviews.push({
      tm: item.tm,
      verdict: 'PASS',
      findings: [
        'Approved source adapter proved exact workbook-row preservation in dft-meta rawIntent.',
        'Approved conditions adapter proved semantic equality with dft-meta; source notes were retained without inference.',
      ],
    });
  }
  return { status: 'done', reviews };
}

async function runGateSet(root, testItems, gate, materials, verifyMaterials) {
  await verifyMaterials(root, materials);
  const reports = [];
  for (const tm of testItems) reports.push(await gate(root, tm, materials));
  await verifyMaterials(root, materials);
  return reports;
}

export function finalProductHashes(root, testItems, materials) {
  return Object.fromEntries(testItems.map(tm => [tm, Object.fromEntries(
    ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'].map(name => {
      const file = assertSafeRunPath(root, path.join(root, materials.dftRoot, tm, name));
      return [name, crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')];
    }),
  )]));
}

async function settleModelExecution({ root, directory, stateFile, checking, dispatch, testItems, gate, materials,
  productHashes, verifyMaterials, reviewInput, bindReviews, profileId, requireBusinessOutputContract }) {
  try {
    const child = await dispatch.result;
    // A cancelled child may still be draining an already-started tool. Do not
    // certify its partial outputs or delay the blocked state with more gates.
    const cancelled = ['timeout', 'aborted'].includes(child?.stopReason);
    const childDone = child?.stopReason === 'completed' && child?.structured?.status === 'done';
    if (!cancelled && childDone) await bindReviews(root, materials, reviewInput, child.structured, verifyMaterials);
    const reports = cancelled || !childDone ? [] : await runGateSet(root, testItems, gate, materials, verifyMaterials);
    const ready = !cancelled && reports.every((report) => report.status === 'ready');
    const completed = ready && childDone;
    const outputHashes = completed && requireBusinessOutputContract
      ? createBusinessOutputHashRecord({ workspaceRoot: root, runId: checking.runId,
        testItems, outputRoot: materials.dftRoot, sourceInputSha256: reviewInput.sourceSha256,
        profileId, profileRevision: materials.profileRevision }) : null;
    const finishedAt = new Date().toISOString();
    const evidenceFile = path.join(directory, 'evidence', 'dft-terminal.json');
    const evidence = {
      schemaVersion: 1,
      runId: checking.runId,
      profileId,
      childSessionId: dispatch.childSessionId,
      childResult: child,
      materialManifest: materials.manifestFile,
      cacheKey: materials.cacheKey,
      reviewInput,
      finalProducts: completed ? productHashes(root, testItems, materials) : undefined,
      reports,
      businessOutputHashes: outputHashes?.evidencePath ?? null,
      businessOutputHashesSha256: outputHashes?.evidenceSha256 ?? null,
      verifiedAt: finishedAt,
    };
    writeJsonAtomic(evidenceFile, evidence);
    const state = {
      ...checking,
      status: completed ? 'completed' : 'blocked',
      outcome: {
        mode: completed ? (reviewInput.items.every((item) => item.mode === 'CREATED') ? 'CREATED' : 'OVERWRITTEN') : 'BLOCKED',
        modelDispatched: true,
        childSessionId: dispatch.childSessionId,
        reason: completed ? undefined : (child?.structured?.question ?? child?.diagnostic ?? 'child_or_final_gate_did_not_complete'),
        evidence: path.relative(root, evidenceFile),
        businessOutputHashes: outputHashes?.evidencePath ?? null,
        businessOutputHashesSha256: outputHashes?.evidenceSha256 ?? null,
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
  if (initial.target?.kind !== 'profile') {
    throw new Error('the first executable training slice requires a profile target');
  }
  const profileId = initial.target.profileId;
  const profile = resolveAgentProfile(root, profileId,
    initial.target.profileRevision ? { revisionId: initial.target.profileRevision } : {});
  // Capability is configuration-driven; the profile id is never a grant.
  assertDftExecutionCapability(profile);
  if (initial.status !== 'created') throw new Error(`training run is not startable from status ${initial.status}`);
  fs.writeFileSync(lockFile, `${process.pid}\n`, { encoding: 'utf8', flag: 'wx' });
  const now = options.now instanceof Date ? options.now : new Date();
  const startedAt = now.toISOString();
  const checking = { ...initial, status: 'checking', testItems, startedAt, updatedAt: startedAt };
  writeJsonAtomic(stateFile, checking);
  const gate = options.runDftGate ?? runDftGate;
  const productHashes = options.productHashes ?? finalProductHashes;
  const verifyMaterials = options.verifyMaterials ?? verifyTrainingMaterials;
  const prepareSourceView = options.prepareSourceView ?? prepareDftSourceView;
  const prepareReviewInput = options.prepareReviewInput ?? prepareDftReviewInput;
  const bindReviews = options.bindReviews ?? bindDftSemanticReviews;
  const requireBusinessOutputContract = options.requireBusinessOutputContract === true;
  try {
    const materials = await (options.prepareMaterials ?? prepareTrainingMaterials)(root, runId, testItems, {
      profileId, profileRevision: profile.manifestPath ? profile.profileRevision : null,
    });
    const reports = await runGateSet(root, testItems, gate, materials, verifyMaterials);
    const unchanged = materials.cacheCompatible === true && reports.every((report) => report.status === 'ready');
    const unchangedOutputHashes = unchanged && requireBusinessOutputContract
      ? createBusinessOutputHashRecord({ workspaceRoot: root, runId, testItems,
        outputRoot: materials.dftRoot,
        sourceInputSha256: reports.find(report => report.canonicalInput?.sha256)?.canonicalInput?.sha256,
        profileId, profileRevision: materials.profileRevision }) : null;
    const sourceView = unchanged ? null : await prepareSourceView(root, testItems, materials, verifyMaterials);
    const evidence = {
      schemaVersion: 1,
      runId,
      profileId,
      mode: unchanged ? 'UNCHANGED' : 'STALE',
      modelDispatched: false,
      materialManifest: materials.manifestFile,
      cacheKey: materials.cacheKey,
      cacheCompatible: materials.cacheCompatible,
      candidateSources: materials.candidateSources,
      sourceView,
      finalProducts: unchanged ? productHashes(root, testItems, materials) : undefined,
      reports,
      businessOutputHashes: unchangedOutputHashes?.evidencePath ?? null,
      businessOutputHashesSha256: unchangedOutputHashes?.evidenceSha256 ?? null,
      checkedAt: new Date().toISOString(),
    };
    const evidenceFile = path.join(directory, 'evidence', 'dft-preflight.json');
    writeJsonAtomic(evidenceFile, evidence);
    const finishedAt = new Date().toISOString();
    let state = {
      ...checking,
      status: unchanged ? 'completed' : 'needs_model',
      outcome: unchanged
        ? { mode: 'UNCHANGED', modelDispatched: false, evidence: path.relative(root, evidenceFile),
          businessOutputHashes: unchangedOutputHashes?.evidencePath ?? null,
          businessOutputHashesSha256: unchangedOutputHashes?.evidenceSha256 ?? null }
        : { mode: 'STALE', modelDispatched: false, reason: 'candidate_outputs_require_isolated_model_execution', evidence: path.relative(root, evidenceFile) },
      updatedAt: finishedAt,
      finishedAt: unchanged ? finishedAt : null,
    };
    writeJsonAtomic(stateFile, state);
    if (!unchanged && typeof options.dispatchModel === 'function') {
      const reviewInput = await prepareReviewInput(root, testItems, materials, sourceView, reports, verifyMaterials);
      const reviewInputFile = path.join(directory, 'evidence', 'dft-review-input.json');
      writeJsonAtomic(reviewInputFile, reviewInput);
      // SMOKE/framework compatibility keeps the proven host-only binding as the
      // default.  BUSINESS_ONLY must exercise the actual DFT expert, however;
      // otherwise a business button can complete with modelDispatched=false and
      // silently certify a deterministic adapter instead of the expert profile.
      const deterministicReviews = options.forceModelReview === true
        ? null
        : deterministicDftSemanticReviews(reviewInput);
      if (deterministicReviews) {
        await bindReviews(root, materials, reviewInput, deterministicReviews, verifyMaterials);
        const finalReports = await runGateSet(root, testItems, gate, materials, verifyMaterials);
        const completed = finalReports.every((report) => report.status === 'ready');
        const outputHashes = completed && requireBusinessOutputContract
          ? createBusinessOutputHashRecord({ workspaceRoot: root, runId, testItems,
            outputRoot: materials.dftRoot, sourceInputSha256: reviewInput.sourceSha256,
            profileId, profileRevision: materials.profileRevision }) : null;
        const terminalAt = new Date().toISOString();
        const terminalFile = path.join(directory, 'evidence', 'dft-terminal.json');
        const terminalEvidence = {
          schemaVersion: 1,
          runId,
          profileId,
          reviewMethod: 'deterministic-source-binding',
          modelDispatched: false,
          materialManifest: materials.manifestFile,
          cacheKey: materials.cacheKey,
          reviewInput,
          reviews: deterministicReviews.reviews,
          businessOutputHashes: outputHashes?.evidencePath ?? null,
          businessOutputHashesSha256: outputHashes?.evidenceSha256 ?? null,
          finalProducts: completed ? productHashes(root, testItems, materials) : undefined,
          reports: finalReports,
          verifiedAt: terminalAt,
        };
        writeJsonAtomic(terminalFile, terminalEvidence);
        state = {
          ...checking,
          status: completed ? 'completed' : 'blocked',
          outcome: {
            mode: completed
              ? (reviewInput.items.every((item) => item.mode === 'CREATED') ? 'CREATED' : 'OVERWRITTEN')
              : 'BLOCKED',
            modelDispatched: false,
            reviewMethod: 'deterministic-source-binding',
            reason: completed ? undefined : 'final_gate_did_not_complete',
            evidence: path.relative(root, terminalFile),
            businessOutputHashes: outputHashes?.evidencePath ?? null,
            businessOutputHashesSha256: outputHashes?.evidenceSha256 ?? null,
          },
          updatedAt: terminalAt,
          finishedAt: terminalAt,
        };
        writeJsonAtomic(stateFile, state);
        return { context, state, evidence: terminalEvidence, evidenceFile: terminalFile };
      }
      const dispatchingAt = new Date().toISOString();
      state = {
        ...checking,
        status: 'dispatching',
        outcome: { mode: 'STALE', modelDispatched: false, reason: 'dispatch_in_progress', evidence: path.relative(root, evidenceFile) },
        updatedAt: dispatchingAt,
        finishedAt: null,
      };
      writeJsonAtomic(stateFile, state);
      const dispatch = await options.dispatchModel({ runId, context, state, evidence, reports, sourceView,
        reviewInput, reviewInputFile, testItems, runDirectory: directory, materials });
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
      const completion = settleModelExecution({ root, directory, stateFile, checking, dispatch, testItems, gate,
        materials, productHashes, verifyMaterials, reviewInput, bindReviews, profileId,
        requireBusinessOutputContract });
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
