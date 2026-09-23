/**
 * Receipt-first identity for the material boundary (handoff section 7.1).
 *
 * Today `lib/policy.js` decides who a child is from the `subagent/descriptor`
 * LABEL, which fails open: a label its regex does not recognise leaves the child
 * with no boundary at all (there is a test that says so). A pinned dispatch now
 * also writes a run-level receipt, so identity can come from something the child
 * cannot type:
 *
 *   - the receipt pins profile, version, executionClass and the target TMs;
 *   - the child's session id (the same id `ctx.subagents.start()` returns) is
 *     recorded on it, which is what the guard sees as `exec.agent.id`;
 *   - the receipt is digest-verified, so a hand-edited copy stops matching.
 *
 * Resolution is deliberately conservative:
 *   `pinned`     a single valid receipt claims this child — its TMs are the scope,
 *                whatever the label says;
 *   `mismatch`   receipts carry this child's label but name a DIFFERENT session —
 *                refused, never resolved to "allowed";
 *   `unpinned`   no receipt claims this child: the legacy label logic still runs
 *                (the handoff allows keeping it), and the caller can tell the two
 *                apart from the returned `reason`.
 */
import { verifyDispatchReceipt } from './dispatch-receipt.js';
import { listReceipts } from './dispatch-profile.js';

/** The descriptor label the child itself carries. */
function descriptorLabel(agent) {
  const label = agent?.session?.events?.findLast((event) => event.type === 'subagent/descriptor')?.data?.label;
  return typeof label === 'string' && label !== '' ? label : undefined;
}

/**
 * Identity for one agent, from the pinned receipts first.
 *
 * @param {string} workspaceRoot
 * @param {object} agent the agent the guard is deciding for
 * @returns {{kind: 'pinned', receipt: object, targetTms: string[], executionClass: string}
 *          | {kind: 'mismatch', reason: string}
 *          | {kind: 'unpinned', reason: string, label?: string}}
 */
export function receiptIdentityFor(workspaceRoot, agent) {
  const label = descriptorLabel(agent);
  const agentId = typeof agent?.id === 'string' && agent.id !== '' ? agent.id : undefined;
  const all = listReceipts(workspaceRoot);
  const receipts = all.filter((receipt) => verifyDispatchReceipt(receipt).ok);
  if (receipts.length === 0) {
    if (all.length > 0 && label !== undefined && all.some((receipt) => receipt.label === label)) {
      // A receipt with this child's label exists but does not verify: that is a
      // tampered (or half-written) pin, not an absent one. Refuse rather than
      // fall back to the label, which is exactly what the receipt was meant to
      // stop being authoritative.
      return { kind: 'mismatch', reason: 'a dispatch receipt carries this child\'s label but fails verification' };
    }
    return { kind: 'unpinned', reason: 'no valid dispatch receipt exists in this run', label };
  }

  const byId = agentId === undefined ? [] : receipts.filter((receipt) => receipt.childSessionId === agentId);
  if (byId.length === 1) {
    const receipt = byId[0];
    // The receipt wins outright: it is the pinned dispatch, so its TMs are the
    // authorised set even when the label claims more.
    return {
      kind: 'pinned',
      receipt,
      targetTms: Array.isArray(receipt.targetTms) ? [...receipt.targetTms] : [],
      executionClass: receipt.executionClass,
    };
  }
  if (byId.length > 1) {
    return { kind: 'mismatch', reason: `${byId.length} pinned receipts claim this child session; the identity is ambiguous` };
  }

  if (label !== undefined) {
    const byLabel = receipts.filter((receipt) => receipt.label === label);
    if (byLabel.length > 0) {
      // Receipts carry this child's label but none names its session: either the
      // child is an impostor using a pinned label, or the receipt was written
      // without a session id. Both are refused rather than trusted.
      const withoutSession = byLabel.filter((receipt) => receipt.childSessionId === undefined || receipt.childSessionId === null);
      if (withoutSession.length === 1 && byLabel.length === 1) {
        const receipt = withoutSession[0];
        return {
          kind: 'pinned',
          receipt,
          targetTms: Array.isArray(receipt.targetTms) ? [...receipt.targetTms] : [],
          executionClass: receipt.executionClass,
        };
      }
      return {
        kind: 'mismatch',
        reason: `a pinned receipt carries this child's label (${JSON.stringify(label)}) but names a different session`,
      };
    }
  }

  return { kind: 'unpinned', reason: 'no pinned receipt claims this child', label };
}
