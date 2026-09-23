/**
 * The single host-side dispatcher for expert profiles (handoff section 7).
 *
 * `dispatch_profile(profileId, runId, task, approvedInputs)`:
 *   1. the profile must exist and have a PUBLISHED version (never `latest`);
 *   2. the published snapshot must still match its own manifest hashes — a
 *      drifted snapshot is refused, not dispatched;
 *   3. the profile's declared stage must exist in the stage registry, and the
 *      registry's owner for that stage is recorded (see `registryOwnership`);
 *   4. persona, toolFilter and the written/read boundary come from the published
 *      instructions and the code registry, never from a label;
 *   5. one one-shot child is started with `maxDepth: 1` and an `outputSchema`;
 *   6. a run-level receipt pins profile, version, hashes, executionClass and the
 *      target TMs, and is written to the run's receipt store so the guard and the
 *      gates can verify identity instead of trusting a label.
 *
 * Everything a caller could otherwise fake (label, description, prompt) is
 * display text here. A caller that cannot produce a valid receipt does not
 * dispatch: the refusal is returned, never swallowed.
 */
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { startWithDeadline } from './execution-deadline.js';
import { checkDftReuse } from './dft-reuse.js';
import { buildDispatchReceipt, receiptDigest, verifyDispatchReceipt } from './dispatch-receipt.js';
import { executionClassForProfile, policyFor, runtimeLabelFor } from './expert-policy-registry.js';

const VERSION = /^v[0-9]+$/;
const TM = /^TM[0-9]+$/;

export const RECEIPT_DIR = path.join('team', 'artifacts', 'dispatch-receipts');

const sha256 = (text) => createHash('sha256').update(text, 'utf8').digest('hex');

/** Byte hash, matching how the Python publisher wrote the manifest. */
function sha256File(file) {
  try {
    return createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  } catch {
    return undefined;
  }
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return undefined;
  }
}

function readText(file) {
  try {
    return fs.readFileSync(file, 'utf8');
  } catch {
    return undefined;
  }
}

/** The agent-facing persona: the published instructions plus the hard boundary. */
function composePersona(profileId, version, executionClass, instructions, policy) {
  const boundary = [
    `You are the published ${profileId} master, version ${version}, executionClass ${executionClass}.`,
    `You may read only: ${policy.readable.join('; ')}.`,
    `You may write only: ${policy.writable.join('; ')}.`,
    'Anything outside those paths is refused by the host, not by your judgement.',
    'Report the exact gate command and its exit code; never claim a pass you did not run.',
  ].join('\n');
  return `${boundary}\n\n${instructions}`;
}

/** The schema a child must satisfy; object-rooted, as the runtime requires. */
function contractOutputSchema() {
  return {
    type: 'object',
    properties: {
      status: { type: 'string', enum: ['done', 'blocked'] },
      outputs: { type: 'array', items: { type: 'string' } },
      gates: { type: 'array', items: { type: 'string' } },
      question: { type: 'string' },
      mode: { type: 'string', enum: ['CREATED', 'UNCHANGED', 'OVERWRITTEN'] },
    },
    required: ['status'],
    additionalProperties: false,
  };
}

/**
 * Resolve one profile's published version, verifying the snapshot against its
 * own manifest. Returns `{ ok: false, reason }` for every refusal so the caller
 * can report the exact cause.
 */
export function resolvePublishedProfile(workspaceRoot, profileId) {
  const directory = path.join(workspaceRoot, 'team', 'expert-profiles', profileId);
  if (!fs.existsSync(directory)) return { ok: false, reason: `${profileId}: no expert profile at ${directory}` };
  const status = readJson(path.join(directory, 'status.json'));
  if (status === undefined) return { ok: false, reason: `${profileId}: status.json is missing or invalid` };
  const version = status.publishedVersion;
  if (typeof version !== 'string' || !VERSION.test(version)) {
    return { ok: false, reason: `${profileId}: nothing is published (publishedVersion = ${JSON.stringify(version ?? null)})` };
  }
  const snapshotDir = path.join(directory, 'versions', version);
  const manifest = readJson(path.join(snapshotDir, 'manifest.json'));
  if (manifest === undefined) return { ok: false, reason: `${profileId}@${version}: manifest.json is missing or invalid` };
  if (manifest.version !== version) return { ok: false, reason: `${profileId}@${version}: manifest names version ${manifest.version}` };
  if (status.manifestDigest !== manifest.digest) {
    return { ok: false, reason: `${profileId}@${version}: status.json digest does not match the manifest` };
  }
  const drifted = [];
  for (const [relative, digest] of Object.entries(manifest.files ?? {})) {
    if (sha256File(path.join(snapshotDir, relative)) !== digest) drifted.push(relative);
  }
  if (drifted.length > 0) {
    return { ok: false, reason: `${profileId}@${version}: the published snapshot drifted from its manifest: ${drifted.join(', ')}` };
  }

  const profileYaml = readText(path.join(snapshotDir, 'profile.yaml')) ?? '';
  const executionClass = /^executionClass:[ \t]*(\S+)[ \t]*$/m.exec(profileYaml)?.[1];
  const declaredStage = /^stage:[ \t]*(\S+)[ \t]*$/m.exec(profileYaml)?.[1];
  const ownerRole = /^ownerRole:[ \t]*(\S+)[ \t]*$/m.exec(profileYaml)?.[1];
  const runtimeLabel = /^runtimeLabel:[ \t]*(.+?)[ \t]*$/m.exec(profileYaml)?.[1];
  const instructions = readText(path.join(snapshotDir, 'instructions.md'));
  const contractText = readText(path.join(snapshotDir, 'output-contract.schema.json'));
  if (executionClass === undefined || declaredStage === undefined || ownerRole === undefined) {
    return { ok: false, reason: `${profileId}@${version}: published profile.yaml is missing executionClass, stage or ownerRole` };
  }
  // Identity first (which class does this profile actually belong to?), then the
  // label shape that class must carry. Checking the label first would report a
  // label problem for what is really a wrong-class claim.
  const mapped = executionClassForProfile(profileId);
  if (mapped !== executionClass) {
    return { ok: false, reason: `${profileId}@${version}: declares executionClass ${executionClass} but the policy registry maps it to ${mapped}` };
  }
  const policy = policyFor(executionClass);
  if (policy === undefined) return { ok: false, reason: `${profileId}@${version}: executionClass ${executionClass} is not registered` };
  if (typeof runtimeLabel !== 'string' || runtimeLabel.trim() === '') {
    // Refused rather than defaulted: a label the material boundary does not
    // recognise would leave the child with NO boundary at all (fail-open).
    return { ok: false, reason: `${profileId}@${version}: profile.yaml must declare a runtimeLabel, or the material boundary cannot recognise the child` };
  }
  const declaredLabel = runtimeLabelFor(executionClass);
  if (declaredLabel === undefined || declaredLabel !== runtimeLabel) {
    return {
      ok: false,
      reason: `${profileId}@${version}: runtimeLabel ${JSON.stringify(runtimeLabel)} is not the label the policy registry declares for ${executionClass} (${JSON.stringify(declaredLabel)})`,
    };
  }
  if (instructions === undefined || contractText === undefined) {
    return { ok: false, reason: `${profileId}@${version}: published instructions or output contract is unreadable` };
  }

  return {
    ok: true,
    profileId,
    version,
    executionClass,
    declaredStage,
    ownerRole,
    runtimeLabel,
    manifest,
    snapshotDir,
    instructions,
    contractText,
    policy,
    persona: composePersona(profileId, version, executionClass, instructions, policy),
    status,
  };
}

/** Which stage the registry says this profile's stage belongs to. */
export function registryOwnership(workspaceRoot, declaredStage) {
  const registry = readJson(path.join(workspaceRoot, 'team', 'ptc', 'ptc_stage_registry.json'));
  if (registry === undefined) return { ok: false, reason: 'the stage registry is missing or invalid' };
  const states = Array.isArray(registry.stateMachine) ? registry.stateMachine : [];
  if (!states.includes(declaredStage)) {
    return { ok: false, reason: `the stage registry has no stage ${declaredStage}` };
  }
  const stage = registry.stages?.[declaredStage];
  const owner = stage?.owner;
  return {
    ok: true,
    stage: declaredStage,
    registryOwner: owner ?? null,
    // Recorded rather than hidden: today the registry names `captain` as the
    // INPUT_SYNC owner and does not list the input experts as owners, so a
    // profile's ownerRole is a source role OF that stage, not the stage owner.
    ownershipNote: owner === undefined
      ? 'the registry names no owner for this stage'
      : `registry owner for ${declaredStage} is ${owner}; the profile's ownerRole is dispatched as a source role of that stage`,
  };
}

function refuse(reason, extra = {}) {
  return { dispatched: false, reason, ...extra };
}

/**
 * Dispatch one published expert profile as a one-shot child.
 *
 * @param {object} options
 * @param {object} options.ctx host context exposing `subagents.start`
 * @param {string} options.workspaceRoot
 * @param {string} options.profileId
 * @param {string} options.runId
 * @param {string[]} options.targetTms
 * @param {string} options.task
 * @param {object} options.parent parent agent
 * @param {AbortSignal} [options.signal]
 * @param {string} [options.createdAt] fixed timestamp, for reproducible tests
 */
export async function dispatchProfile(options) {
  const { ctx, workspaceRoot, profileId, runId, task, parent } = options;
  const resolved = resolvePublishedProfile(workspaceRoot, profileId);
  if (!resolved.ok) return refuse(resolved.reason);
  // The evolution expert is a NON-STAGE role: no TMs, no trials, no registry
  // stage — its scope is closed run evidence and governance documents.
  const evolution = resolved.executionClass === 'evolution-proposal';
  const targetTms = Array.isArray(options.targetTms) ? [...options.targetTms].sort() : [];
  if (!evolution && (targetTms.length === 0 || targetTms.some((tm) => typeof tm !== 'string' || !TM.test(tm)))) {
    return refuse('targetTms must be a non-empty list of TM<digits> values');
  }
  if (evolution && targetTms.length !== 0) {
    return refuse('the evolution expert takes no target TMs');
  }
  const trialDirs = Array.isArray(options.trialDirs) ? options.trialDirs.map((item) => String(item)) : undefined;
  if (evolution && trialDirs !== undefined && trialDirs.length !== 0) {
    return refuse('the evolution expert takes no trial directories');
  }
  if (!evolution && trialDirs !== undefined && trialDirs.length !== targetTms.length) {
    return refuse('trialDirs, when provided, must be one directory per target TM');
  }
  if (typeof runId !== 'string' || runId === '') return refuse('runId is required');
  if (typeof task !== 'string' || task.trim() === '') return refuse('task is required');
  if (ctx?.subagents?.getProvider?.('spawn') === undefined) {
    return refuse('the DSH "spawn" subagent provider is unavailable, so no expert can be dispatched');
  }

  // The rule-reviewer owns TWO stages (RULE_REVIEW_METHOD and
  // RULE_REVIEW_IMPLEMENTATION); the caller names the stage actually being
  // worked, and the receipt records that instead of silently reusing the
  // profile's declared primary stage.
  const dispatchStage = typeof options.stage === 'string' && options.stage !== ''
  ? options.stage
  : resolved.declaredStage;
    const ownership = evolution
    ? { ok: true, stage: dispatchStage, registryOwner: null, ownershipNote: 'the evolution expert is a non-stage role dispatched by the user on closed runs' }
  : registryOwnership(workspaceRoot, dispatchStage);
  if (!ownership.ok) return refuse(ownership.reason);

  const dispatchId = `${profileId}-${runId}-${targetTms.join('-')}`.replace(/[^A-Za-z0-9._-]/g, '_');
  // The label comes from the published profile, not from the caller: the
  // material boundary recognises a child by this exact shape, so a caller-chosen
  // label could otherwise hand a child no boundary at all.
  const label = resolved.runtimeLabel.split('<TM>').join(targetTms.join(','));
  let receipt;
  try {
    receipt = buildDispatchReceipt({
      dispatchId,
      runId,
      profileId,
      profileVersion: resolved.version,
      executionClass: resolved.executionClass,
      personaSha256: sha256(resolved.persona),
      contractSha256: sha256(resolved.contractText),
      policySha256: sha256(JSON.stringify(resolved.policy)),
      targetTms,
      ...options.createdAt === undefined ? {} : { createdAt: options.createdAt },
      label,
    });
  } catch (error) {
    return refuse(`could not pin a dispatch receipt: ${error?.message ?? error}`);
  }

  const receiptDir = path.join(workspaceRoot, RECEIPT_DIR);
  fs.mkdirSync(receiptDir, { recursive: true });
  const receiptPath = path.join(receiptDir, `${receipt.dispatchId}.json`);
  if (fs.existsSync(receiptPath)) {
    return refuse(`a receipt for ${receipt.dispatchId} already exists; refusing to dispatch the same run twice`);
  }

  const prompt = [
    `You are the published ${profileId} (${resolved.version}), executionClass ${resolved.executionClass}.`,
    `Run ${runId}. Your assigned test items: ${targetTms.join(', ')}.`,
    task.trim(),
  ].join('\n');

  let run;
  let preflight;
  try {
    if (resolved.executionClass === 'input-dft') {
      preflight = await (options.checkDftReuse ?? checkDftReuse)(workspaceRoot, targetTms);
    }
    const request = {
      label,
      prompt: [{ type: 'text', text: prompt }],
      parent,
      signal: options.signal ?? new AbortController().signal,
      persona: resolved.persona,
      toolFilter: { allow: options.visibleTools ?? ['read', 'write', 'pwsh', 'glob', 'grep'] },
      maxDepth: 1,
      outputSchema: contractOutputSchema(),
    };
    if (preflight?.unchanged) {
      const structured = {
        status: 'done', mode: 'UNCHANGED',
        outputs: preflight.reports.flatMap((report) => report.requiredOutputs),
        gates: preflight.reports.map((report) => `python scripts/validate_dft_outputs.py --tm ${report.tm}; gateExit=0; sourceSha256=${report.canonicalInput.sha256}`),
      };
      run = { mode: 'UNCHANGED', result: Promise.resolve({ stopReason: 'completed', structured }), dispose: async () => {} };
    } else {
      run = resolved.executionClass === 'input-dft'
        ? await startWithDeadline(ctx, request)
        : await ctx.subagents.start('spawn', request);
    }
  } catch (error) {
    return refuse(`the host refused the one-shot dispatch: ${error?.message ?? error}`, { receipt });
  }

  // The child session id is only known once the run exists; recording it lets a
  // guard match a live child back to exactly one pinned receipt. The digest is
  // recomputed over the FINAL record, so the stored receipt verifies as a whole
  // and any later tampering — including with the session id — breaks it.
  const childSessionId = typeof run?.id === 'string' ? run.id : null;
  const record = {
    ...receipt,
    stage: dispatchStage,
    ...(trialDirs === undefined ? {} : { trialDirs }),
    registryOwnership: ownership,
    manifestDigest: resolved.manifest.digest,
    childSessionId,
    task: task.trim(),
    dispatchedAt: new Date().toISOString(),
    ...(preflight === undefined ? {} : { preflight, executionMode: preflight.unchanged ? 'UNCHANGED' : 'MODEL' }),
  };
  record.digest = receiptDigest(record);
  fs.writeFileSync(receiptPath, `${JSON.stringify(record, null, 2)}\n`, 'utf8');

  return { dispatched: true, receipt: record, receiptPath, run, childSessionId, ownership };
}

/** Every receipt on disk for one run (or all runs). */
export function listReceipts(workspaceRoot, runId) {
  const directory = path.join(workspaceRoot, RECEIPT_DIR);
  let names = [];
  try {
    names = fs.readdirSync(directory).filter((name) => name.endsWith('.json'));
  } catch {
    return [];
  }
  const receipts = [];
  for (const name of names) {
    const value = readJson(path.join(directory, name));
    if (value === undefined) continue;
    if (runId !== undefined && value.runId !== runId) continue;
    receipts.push(value);
  }
  return receipts;
}

/**
 * Match a live child back to exactly ONE pinned receipt.
 *
 * Fail-closed by construction: no match, or more than one match, is a refusal —
 * an ambiguous identity must never resolve to "allowed".
 */
export function findReceiptForChild(workspaceRoot, { label, targetTms, childSessionId } = {}) {
  const wanted = Array.isArray(targetTms) ? [...targetTms].sort() : undefined;
  const matches = listReceipts(workspaceRoot).filter((receipt) => {
    if (childSessionId !== undefined && receipt.childSessionId !== childSessionId) return false;
    if (label !== undefined && receipt.label !== label) return false;
    if (wanted !== undefined) {
      const have = Array.isArray(receipt.targetTms) ? [...receipt.targetTms].sort() : [];
      if (have.join(',') !== wanted.join(',')) return false;
    }
    return verifyDispatchReceipt(receipt).ok;
  });
  if (matches.length === 0) return { ok: false, reason: 'no pinned dispatch receipt matches this child' };
  if (matches.length > 1) return { ok: false, reason: `${matches.length} pinned receipts match this child; the identity is ambiguous` };
  return { ok: true, receipt: matches[0] };
}
