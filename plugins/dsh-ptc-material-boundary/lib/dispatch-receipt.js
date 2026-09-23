/**
 * Run-level dispatch receipt (handoff deliverables 4-5).
 *
 * Why this exists rather than trusting the persisted subagent descriptor: a
 * ONE-SHOT child's persisted descriptor carries only `label`
 * (`dsh-subagent/lib/index.js` snapshot for `mode: 'one-shot'`), so the label is
 * currently the whole identity surface — and `lib/policy.js` proved it fails
 * open for any label its regex does not recognise. A receipt pins the profile,
 * the version, the contract/persona/policy hashes, the executionClass and the
 * target TMs at dispatch time, and is validated on every use.
 *
 * This module is pure: no filesystem, no clock unless the caller omits
 * `createdAt`, no host services. That keeps it testable without a workspace and
 * usable by both the dispatcher (writing) and the guard (verifying).
 */
import { createHash } from 'node:crypto';
import { executionClassForProfile, isExecutionClass } from './expert-policy-registry.js';

export const RECEIPT_SCHEMA_VERSION = 1;

const SHA256 = /^[a-f0-9]{64}$/;
const TM = /^TM\d+$/;
const ID = /^[A-Za-z0-9._-]{1,120}$/;
const VERSION = /^v\d+$|^draft$/;

/** Deterministic JSON: object keys sorted, arrays preserved. */
function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return `{${keys.map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value ?? null);
}

/** Structural + cross-field problems, as short human-readable strings. */
function problems(receipt) {
  const errors = [];
  if (receipt === null || typeof receipt !== 'object' || Array.isArray(receipt)) {
    return ['receipt must be an object'];
  }
  if (receipt.schemaVersion !== RECEIPT_SCHEMA_VERSION) {
    errors.push(`schemaVersion must be ${RECEIPT_SCHEMA_VERSION}`);
  }
  for (const field of ['dispatchId', 'runId']) {
    if (typeof receipt[field] !== 'string' || !ID.test(receipt[field])) {
      errors.push(`${field} must match ${String(ID)}`);
    }
  }
  for (const field of ['personaSha256', 'contractSha256', 'policySha256']) {
    if (typeof receipt[field] !== 'string' || !SHA256.test(receipt[field])) {
      errors.push(`${field} must be a lowercase sha256`);
    }
  }
  if (typeof receipt.profileId !== 'string' || receipt.profileId === '') {
    errors.push('profileId must be a non-empty string');
  }
  if (typeof receipt.profileVersion !== 'string' || !VERSION.test(receipt.profileVersion)) {
    errors.push('profileVersion must be "draft" or "v<n>"');
  }
  if (!isExecutionClass(receipt.executionClass)) {
    errors.push(`executionClass ${JSON.stringify(receipt.executionClass)} is not registered`);
  } else if (typeof receipt.profileId === 'string') {
    const declared = executionClassForProfile(receipt.profileId);
    if (declared === undefined) {
      errors.push(`profileId ${JSON.stringify(receipt.profileId)} is not a registered expert profile`);
    } else if (declared !== receipt.executionClass) {
      // The anti-spoofing check: a receipt cannot claim a wider class than the
      // profile it names, whatever the label or description says.
      errors.push(`profile ${receipt.profileId} declares executionClass ${declared}, received ${receipt.executionClass}`);
    }
  }
  // The evolution expert is a NON-STAGE role: its receipt carries an empty
    // targetTms list on purpose — its scope is closed run evidence, not TMs.
  const evolutionReceipt = receipt.executionClass === 'evolution-proposal';
  if (!Array.isArray(receipt.targetTms) || (receipt.targetTms.length === 0 && !evolutionReceipt)) {
    errors.push('targetTms must be a non-empty array');
  } else if (evolutionReceipt && receipt.targetTms.length !== 0) {
    errors.push('an evolution-proposal receipt takes no target TMs');
  } else {
    if (receipt.targetTms.some((tm) => typeof tm !== 'string' || !TM.test(tm))) {
      errors.push('every targetTm must match TM<digits> (uppercase)');
    }
    if (new Set(receipt.targetTms).size !== receipt.targetTms.length) {
      errors.push('targetTms must not repeat');
    }
    const sorted = [...receipt.targetTms].sort();
    if (receipt.targetTms.some((tm, at) => tm !== sorted[at])) {
      errors.push('targetTms must be sorted for a stable digest');
    }
  }
  if (typeof receipt.createdAt !== 'string' || Number.isNaN(Date.parse(receipt.createdAt))) {
    errors.push('createdAt must be an ISO-8601 timestamp');
  }
  if (receipt.label !== undefined && typeof receipt.label !== 'string') {
    errors.push('label, when present, must be a string');
  }
  return errors;
}

/** The digest covers every field except `digest` itself. */
export function receiptDigest(receipt) {
  const { digest: _ignored, ...rest } = receipt ?? {};
  return createHash('sha256').update(canonical(rest), 'utf8').digest('hex');
}

/**
 * Build a frozen receipt. Throws on invalid input: a dispatcher that cannot
 * produce a valid receipt must not dispatch at all.
 * @param {object} input
 */
export function buildDispatchReceipt(input) {
  const receipt = {
    schemaVersion: RECEIPT_SCHEMA_VERSION,
    dispatchId: input?.dispatchId,
    runId: input?.runId,
    profileId: input?.profileId,
    profileVersion: input?.profileVersion,
    executionClass: input?.executionClass,
    personaSha256: input?.personaSha256,
    contractSha256: input?.contractSha256,
    policySha256: input?.policySha256,
    targetTms: Array.isArray(input?.targetTms) ? [...input.targetTms].sort() : input?.targetTms,
    createdAt: input?.createdAt ?? new Date().toISOString(),
    ...input?.label === undefined ? {} : { label: input.label },
  };
  const errors = problems(receipt);
  if (errors.length > 0) {
    throw new Error(`PTC dispatch receipt is invalid: ${errors.join('; ')}`);
  }
  return Object.freeze({ ...receipt, digest: receiptDigest(receipt) });
}

/**
 * Structural, cross-field and tamper checks.
 * @returns {{ok: boolean, errors: string[]}}
 */
export function verifyDispatchReceipt(receipt) {
  const errors = problems(receipt);
  if (errors.length === 0) {
    if (typeof receipt.digest !== 'string' || receipt.digest !== receiptDigest(receipt)) {
      errors.push('digest does not match the receipt contents (tampered or truncated)');
    }
  }
  return { ok: errors.length === 0, errors };
}

/**
 * The authoritative identity of a run. Callers must read identity from here and
 * never from a label or description: those are display text an agent can type.
 * @returns {{profileId: string, profileVersion: string, executionClass: string, targetTms: string[]}}
 */
export function identityFromReceipt(receipt) {
  const { ok, errors } = verifyDispatchReceipt(receipt);
  if (!ok) throw new Error(`PTC dispatch receipt rejected: ${errors.join('; ')}`);
  return {
    profileId: receipt.profileId,
    profileVersion: receipt.profileVersion,
    executionClass: receipt.executionClass,
    targetTms: [...receipt.targetTms],
  };
}
