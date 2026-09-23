/**
 * Dev-only dispatch probe (NOT part of the PTC plugin).
 *
 * Why it exists: the handoff prescribes `ctx.subagents.start('spawn', request)`
 * for expert dispatch, and that is the ONE-SHOT path. The `subagent` TOOL in this
 * deployment is configured `backgroundMode: continuable`, so exercising the tool
 * proves nothing about the one-shot path. This probe performs exactly one
 * one-shot dispatch from real plugin code in a real host, then records what the
 * API accepted and what identity it returned.
 *
 * It is mounted only by the `ptcflow` dev profile, so it changes no production
 * composition. It writes its finding to `config.out` and never fails the session.
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const name = 'ptc-dispatch-probe';
export const inject = ['subagents'];

export function apply(ctx, config = {}) {
  if (typeof config.out !== 'string' || !config.out) {
    throw new Error('ptc-dispatch-probe: config.out is required');
  }
  const mode = ['dispatch-profile', 'receipt-narrowing', 'inert'].includes(config.mode) ? config.mode : 'raw-one-shot';
  let done = false;
  ctx.on('agent/pre-step', async ({ agent }, next) => {
    const decision = await next();
    if (done) return decision;
    done = true;
    const header = agent?.session?.header ?? {};
    const record = {
      at: new Date().toISOString(),
      mode,
      parentAgentId: agent?.id ?? null,
      // Recorded in every mode: this is how a run proves whether the session
      // actually carries a preset (a training session is identified by it).
      parentHeader: { cwd: header.cwd ?? null, agentPreset: header.agentPreset ?? null },
      ok: false,
    };
    try {
      const prompt = [{ type: 'text', text: 'Return a JSON object with exactly one field "token" whose value is the string ONESHOT-CHILD-OK.' }];
      const signal = new AbortController().signal;
      const run = mode === 'inert'
        // The session's OWN tool calls are the probe; nothing is dispatched.
        ? null
        : mode === 'dispatch-profile'
        ? await probeDispatchProfile(ctx, config, agent, signal, record)
        : mode === 'receipt-narrowing'
        ? await probeReceiptNarrowing(ctx, config, agent, signal, record)
        : await ctx.subagents.start('spawn', {
            label: 'probe-oneshot-child',
            prompt,
            parent: agent,
            signal,
            persona: 'You are a probe child. Answer only with the requested JSON object.',
            toolFilter: { allow: ['read'] },
            maxDepth: 1,
            outputSchema: { type: 'object', properties: { token: { type: 'string' } }, required: ['token'], additionalProperties: false },
          });
      record.ok = record.ok || true;
      record.runKeys = Object.keys(run ?? {}).sort();
      record.runIdentity = {
        id: run?.id ?? null,
        agentId: run?.agentId ?? null,
        subagentId: run?.subagentId ?? null,
        sessionId: run?.sessionId ?? null,
        status: run?.status ?? null,
        stopReason: run?.stopReason ?? null,
      };
      const settled = await (run?.result ?? run);
      record.settled = {
        keys: Object.keys(settled ?? {}).sort(),
        stopReason: settled?.stopReason ?? null,
        output: JSON.stringify(settled?.output ?? null).slice(0, 600),
      };
      record.finalIdentity = { id: run?.id ?? null, agentId: run?.agentId ?? null, subagentId: run?.subagentId ?? null, sessionId: run?.sessionId ?? null };
    } catch (error) {
      record.error = `${error?.name ?? 'Error'}: ${error?.message ?? error}`;
    }
    try {
      fs.writeFileSync(config.out, `${JSON.stringify(record, null, 2)}\n`, 'utf8');
    } catch (error) {
      ctx.logger?.error?.(`ptc-dispatch-probe could not write its finding: ${error?.message ?? error}`);
    }
    return decision;
  }, { prepend: true });
}

/**
 * Discriminating experiment for receipt-first identity (handoff 7.1).
 *
 * The child is started with a label that authorises TWO test modes while the
 * receipt written immediately afterwards pins ONE. If identity comes from the
 * receipt, reading the second mode's output is refused. If the label wins, that
 * read succeeds — which is precisely the widening the receipt is meant to stop.
 *
 * The probe is dev-only and deliberately bypasses `dispatchProfile` (whose whole
 * job is to render the label FROM the receipt), so the two can disagree here.
 */
async function probeReceiptNarrowing(ctx, config, agent, signal, record) {
  const { createHash } = await import('node:crypto');
  const pluginDir = path.resolve(config.pluginDir);
  const { resolvePublishedProfile, RECEIPT_DIR } = await import(pathToFileURL(path.join(pluginDir, 'lib', 'dispatch-profile.js')).href);
  const { buildDispatchReceipt, receiptDigest } = await import(pathToFileURL(path.join(pluginDir, 'lib', 'dispatch-receipt.js')).href);

  const resolved = resolvePublishedProfile(config.workspaceRoot, config.profileId);
  if (!resolved.ok) throw new Error(`published profile unresolved: ${resolved.reason}`);
  const label = config.labelOverride;
  record.labelUsed = label;
  const startedAt = Date.now();
  const run = await ctx.subagents.start('spawn', {
    label,
    prompt: [{ type: 'text', text: config.task }],
    parent: agent,
    signal,
    persona: resolved.persona,
    // `run_code` must NOT appear here: it is the reserved Code Mode presentation
    // transport, and `tools.restrict()` rejects a filter that names it
    // ("restrict end-capability tools instead"). In code mode it is available to
    // the child regardless of this list.
    toolFilter: { allow: ['read', 'write', 'pwsh'] },
    maxDepth: 1,
    outputSchema: { type: 'object', properties: { status: { type: 'string' }, outputs: { type: 'array', items: { type: 'string' } } }, required: ['status'], additionalProperties: false },
  });
  const sha = (text) => createHash('sha256').update(text, 'utf8').digest('hex');
  const receipt = buildDispatchReceipt({
    dispatchId: config.runId,
    runId: config.runId,
    profileId: config.profileId,
    profileVersion: resolved.version,
    executionClass: resolved.executionClass,
    personaSha256: sha(resolved.persona),
    contractSha256: sha(resolved.contractText),
    policySha256: sha(JSON.stringify(resolved.policy)),
    targetTms: config.targetTms,
    label,
    createdAt: new Date().toISOString(),
  });
  const stored = { ...receipt, childSessionId: typeof run?.id === 'string' ? run.id : null, dispatchedAt: new Date().toISOString() };
  stored.digest = receiptDigest(stored);
  const receiptPath = path.join(config.workspaceRoot, RECEIPT_DIR, `${stored.dispatchId}.json`);
  fs.mkdirSync(path.dirname(receiptPath), { recursive: true });
  fs.writeFileSync(receiptPath, `${JSON.stringify(stored, null, 2)}\n`, 'utf8');
  record.receiptWrittenMsAfterStart = Date.now() - startedAt;
  record.receiptPath = receiptPath;
  record.receiptTargetTms = stored.targetTms;
  record.receiptChildSessionId = stored.childSessionId;
  return run;
}
async function probeDispatchProfile(ctx, config, agent, signal, record) {
  const modulePath = path.resolve(config.pluginDir, 'lib', 'dispatch-profile.js');
  const { dispatchProfile } = await import(pathToFileURL(modulePath).href);
  const outcome = await dispatchProfile({
    ctx,
    workspaceRoot: config.workspaceRoot,
    profileId: config.profileId,
    runId: config.runId,
    targetTms: config.targetTms,
    trialDirs: Array.isArray(config.trialDirs) ? config.trialDirs : undefined,
    stage: typeof config.stage === 'string' && config.stage !== '' ? config.stage : undefined,
    task: config.task ?? 'Reply with a JSON object {"status":"done","outputs":[],"gates":[]} to confirm you received this pinned dispatch. Do not read or write any file.',
  parent: agent,
    signal,
  });
  record.dispatched = outcome.dispatched === true;
  record.refusalReason = outcome.reason ?? null;
  record.receiptPath = outcome.receiptPath ?? null;
  record.receipt = outcome.receipt ? {
    profileId: outcome.receipt.profileId,
    profileVersion: outcome.receipt.profileVersion,
    executionClass: outcome.receipt.executionClass,
    targetTms: outcome.receipt.targetTms,
    label: outcome.receipt.label,
    digest: outcome.receipt.digest,
    childSessionId: outcome.receipt.childSessionId,
  } : null;
  record.ownership = outcome.ownership ?? null;
  if (!outcome.dispatched) throw new Error(`pinned dispatch refused: ${outcome.reason}`);
  return outcome.run;
}
