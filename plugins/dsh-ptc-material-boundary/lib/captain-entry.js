import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import fs from 'node:fs';
import { dispatchProfile } from './dispatch-profile.js';
import { executionClassForProfile, runtimeLabelFor } from './expert-policy-registry.js';
import { agentPresetOf } from './session-preset.js';

const execFile = promisify(execFileCallback);
const TM = /\bTM\s*\d+\b/ui;

function textOf(message) {
  if (!Array.isArray(message?.content)) return '';
  return message.content
    .filter((block) => block?.type === 'text' && typeof block.text === 'string')
    .map((block) => block.text)
    .join('\n')
    .trim();
}

/** PTC is opt-in: only the ATE PTC preset in this exact DSH workspace can be Captain. */
export function isPtcCaptainAgent(agent, workspaceRoot) {
  const header = agent?.session?.header ?? {};
  const cwd = header.cwd;
  // The preset is resolved the way DSH resolves it (newest agent-preset/selected
  // event, header fallback): reading the header alone would miss a session the
  // user switched INTO the ate-ptc preset, so Captain would never engage.
  return agentPresetOf(agent) === 'ate-ptc'
    && typeof cwd === 'string'
    && path.resolve(cwd).toLowerCase() === path.resolve(workspaceRoot).toLowerCase()
    && !agent?.session?.events?.some((event) => event?.type === 'subagent/descriptor');
}

/** Only a new Captain conversation's first human message may start a batch. */
export function firstDeliveryRequest(messages) {
  const userMessages = (messages ?? []).filter((message) => message?.source?.kind === 'user');
  if (userMessages.length !== 1) return undefined;
  const message = userMessages[0];
  const text = textOf(message).normalize('NFKC');
  return TM.test(text) ? { id: String(message.id ?? text), text } : undefined;
}

export function latestDeliveryRequest(messages) {
  const userMessages = (messages ?? []).filter((message) => message?.source?.kind === 'user');
  const message = userMessages.at(-1);
  if (!message) return undefined;
  const text = textOf(message).normalize('NFKC');
  return TM.test(text) ? { id: String(message.id ?? text), text } : undefined;
}

export function deliveryExecutionScope(text) {
  const normalized = String(text ?? '').normalize('NFKC');
  const mentionsDft = /DFT\s*(?:expert|专家)?/iu.test(normalized);
  const only = /(?:只|仅)\s*(?:(?:执行|运行|跑|做)(?:到|性)?)?\s*DFT\s*(?:expert|专家)?|(?:其余|其他).{0,12}不执行|(?:only\s+(?:run\s+)?DFT|DFT\s+(?:expert\s+)?only)/iu.test(normalized);
  return { sourceRoles: mentionsDft && only ? ['dft-expert'] : ['dft-expert', 'schematic-expert'], stopAfter: mentionsDft && only ? 'INPUT_SYNC' : null };
}

async function runPython(workspaceRoot, args, run = execFile) {
  const { stdout, stderr } = await run('python', args, {
    cwd: workspaceRoot,
    windowsHide: true,
    maxBuffer: 1024 * 1024,
    encoding: 'utf8',
  });
  let result;
  try {
    result = JSON.parse(stdout);
  } catch {
    throw new Error(`Captain entry returned invalid JSON: ${(stdout || stderr).trim()}`);
  }
  if (!result || typeof result !== 'object' || typeof result.state !== 'string') {
    throw new Error('Captain entry returned no state');
  }
  return result;
}

export function runCaptainEntry(workspaceRoot, request, run = execFile) {
  return runPython(workspaceRoot, [path.join(workspaceRoot, 'scripts', 'captain_delivery_entry.py'), '--request', request], run);
}

export function runCaptainContinuation(workspaceRoot, batchId, run = execFile) {
  return runPython(workspaceRoot, [path.join(workspaceRoot, 'scripts', 'captain_delivery_entry.py'), '--continue-batch', batchId], run);
}

export function runCaptainScopeUpdate(workspaceRoot, batchId, request, run = execFile) {
  return runPython(workspaceRoot, [path.join(workspaceRoot, 'scripts', 'captain_delivery_entry.py'), '--scope-update-batch', batchId, '--scope-text', request], run);
}

export function captainDirective(result) {
  return [
    'PTC Captain entry hook already created or checked this batch. Do not ask the user for a batch id, trial directory, or command.',
    `batchId: ${result.batchId ?? '(not created)'}`,
    `state: ${result.state}`,
    'The Hook has already started every INPUT_SYNC source specialist. Do not read team/CURRENT_STATUS.md, old trial directories, or role manuals. Do not call subagent again. Wait for the specialist handoffs; the next stage begins only from those results.',
    `CAPTAIN_ENTRY_JSON=${JSON.stringify(result)}`,
  ].join('\n');
}

function signature(result) {
  return JSON.stringify({
    state: result.state,
    dispatch: result.dispatch ?? null,
    dispatches: result.dispatches ?? null,
    targetTms: result.targetTms ?? null,
    nextRequiredStage: result.nextRequiredStage ?? null,
    reason: result.reason ?? null,
  });
}

export function initializeSessionState(record, requestId = 'unbound') {
  return record && typeof record === 'object'
    ? { batchId: record.batchId, requestId: record.requestId ?? requestId, lastSignature: typeof record.lastSignature === 'string' ? record.lastSignature : '' }
    : { batchId: undefined, requestId, lastSignature: '' };
}

/**
 * Dispatch the INPUT_SYNC source specialists for one batch.
 *
 * A source role listed in `config.pinnedProfiles` is dispatched through the
 * published expert profile (`dispatchProfile`): pinned version, persona,
 * toolFilter, maxDepth 1, an outputSchema and a run-level receipt. A role that
 * is NOT listed keeps the historical label dispatch, and the gap is reported in
 * the returned `unpinnedRoles` so it stays visible rather than being assumed.
 *
 * Pinning is opt-in through configuration on purpose: the live deployment binds
 * the boundary to a workspace that has no expert profiles yet, and defaulting it
 * on would refuse every source dispatch there. Once every source role has a
 * published profile the map covers them all and the unpinned path is unused.
 *
 * When a listed role's pinning fails, the handoff rule applies: do NOT dispatch
 * an unpinned child and do NOT advance the stage. The returned marker settles
 * with `stopReason: 'refused'`, which the caller already treats as "do not
 * advance".
 */
export async function startRequiredSourceDispatches(ctx, result, agent, signal, config = {}) {
  const dispatches = Array.isArray(result?.dispatches) ? result.dispatches : [];
  const allowedRoles = result.executionScope?.sourceRoles;
  const required = Array.isArray(allowedRoles) ? dispatches.filter((item) => allowedRoles.includes(item.role)) : dispatches;
  if (required.length === 0) return [];
  if (!ctx?.subagents?.getProvider?.('spawn')) {
    throw new Error('PTC Captain entry cannot dispatch INPUT_SYNC specialists: DSH subagent provider "spawn" is unavailable');
  }
  // The Captain turn is deliberately ended after dispatch; its abort signal
  // must not cancel the source specialists that it has just started.
  const pinnedProfiles = config.pinnedProfiles && typeof config.pinnedProfiles === 'object' ? config.pinnedProfiles : {};
  const roleTask = (item, label) => [
    `Work only on these requested test items: ${Array.isArray(item.tms) ? item.tms.join(', ') : ''}.`,
    `Your isolated trial directories are: ${item.trialDirs && typeof item.trialDirs === 'object' ? JSON.stringify(item.trialDirs) : '{}'}.`,
    `This is batch ${result.batchId}, the enforced INPUT_SYNC stage.`,
    'Follow your installed role contract and material boundary. Do not read Captain status, old trial records, or files outside your authorized input/output paths.',
    'Produce the required source-stage artifacts and report the result to the Captain.',
    `Your runtime label is: ${label}`,
  ].join('\n');

  const runs = await Promise.all(required.map(async (item) => {
    const controller = new AbortController();
    const childSignal = controller.signal;
    const decorate = (run) => ({ ...run, role: item.role, abort: (reason = 'scope narrowed by user') => controller.abort(new Error(reason)) });
    const profileId = pinnedProfiles[item.role];
    // The label a pinned child carries comes from the policy registry's
    // RUNTIME_LABEL for that profile's executionClass (never from the role
      // name), because the material boundary recognises exactly that shape.
        let label = item.role === 'dft-expert' ? `PTC dft expert [${(item.tms || []).join(',')}]` : item.role === 'schematic-expert' ? 'PTC schematic expert' : `PTC ${item.role}`;
        if (typeof profileId === 'string' && profileId !== '') {
        const declared = runtimeLabelFor(executionClassForProfile(profileId));
        if (typeof declared === 'string' && declared !== '') {
        label = declared.includes('<TM>') ? declared.split('<TM>').join((item.tms || []).join(',')) : declared;
        }
        }
        if (typeof profileId === 'string' && profileId !== '') {
      const outcome = await dispatchProfile({
            ctx,
            workspaceRoot: config.workspaceRoot,
            profileId,
            runId: String(result.batchId ?? 'unbound'),
            targetTms: Array.isArray(item.tms) ? item.tms : [],
            trialDirs: Array.isArray(item.trialDirs) ? item.trialDirs : undefined,
            stage: typeof item.stage === 'string' && item.stage !== '' ? item.stage : undefined,
            task: roleTask(item, label),
            parent: agent,
            signal: childSignal,
            checkDftReuse: config.checkDftReuse,
          });
      if (outcome.dispatched) return decorate(outcome.run);
      ctx.logger?.warn?.(`PTC ${item.role}: pinned dispatch refused, so no child was started — ${outcome.reason}`);
      return { role: item.role, abort() {}, result: Promise.resolve({ stopReason: 'refused', diagnostic: `${item.role}: ${outcome.reason}` }), refused: outcome.reason };
    }
    const prompt = [`You are the ${label} for batch ${result.batchId}.`, roleTask(item, label)].join('\n');
    return decorate(await ctx.subagents.start('spawn', { label, prompt: [{ type: 'text', text: prompt }], parent: agent, signal: childSignal }));
  }));
  runs.unpinnedRoles = required.filter((item) => !pinnedProfiles[item.role]).map((item) => item.role);
  return runs;
}

function injectedMessage(requestId, result) {
  return {
    id: `ptc-captain-entry:${requestId}:${result.state}`,
    role: 'user',
    content: [{ type: 'text', text: captainDirective(result) }],
    source: { kind: 'plugin', plugin: 'dsh-ptc-material-boundary' },
  };
}

/** Record the terminal outcome without advancing a user-scoped source-only batch. */
export async function finishScopedSources(root, entry, runs) {
  const outcomes = await Promise.all(runs.map((run) => Promise.resolve(run.result).catch((error) => ({ stopReason: 'error', diagnostic: error.message }))));
  const done = outcomes.length > 0 && outcomes.every((o) => o?.stopReason === 'completed' && o?.structured?.status === 'done');
  const result = {
    batchId: entry.batchId, state: 'INPUT_SYNC', status: done ? 'done' : 'blocked',
    mode: done && outcomes.every((o) => o.structured.mode === 'UNCHANGED') ? 'UNCHANGED' : undefined,
    executionScope: entry.executionScope, advanced: false, outcomes,
    completedAt: new Date().toISOString(),
  };
  if (!/^[A-Za-z0-9._-]+$/.test(entry.batchId) || entry.batchId === '.' || entry.batchId === '..') throw new Error('Invalid batch id');
  const directory = path.join(root, 'team', 'artifacts', entry.batchId);
  fs.mkdirSync(directory, { recursive: true });
  fs.writeFileSync(path.join(directory, 'source-terminal.json'), `${JSON.stringify(result, null, 2)}\n`);
  return result;
}

function terminalMessage(requestId, result) {
  return {
    id: `ptc-source-terminal:${requestId}`, role: 'user',
    source: { kind: 'plugin', plugin: 'dsh-ptc-material-boundary' },
    content: [{ type: 'text', text: `The host has completed the requested DFT-only execution. Reply with its status and mode in one short Chinese sentence. Do not call tools, write verification files, dispatch anyone, or advance this batch. Runtime result: ${JSON.stringify(result)}` }],
  };
}

/** Attach a real conversation boundary hook to the loaded DSH plugin. */
export function installCaptainEntryHook(ctx, config) {
  const root = path.resolve(config.workspaceRoot);
  const active = new Map();
  const executeStart = typeof config.runCaptainEntry === 'function' ? config.runCaptainEntry : runCaptainEntry;
  const executeContinue = typeof config.runCaptainContinuation === 'function' ? config.runCaptainContinuation : runCaptainContinuation;
  const executeScopeUpdate = typeof config.runCaptainScopeUpdate === 'function' ? config.runCaptainScopeUpdate : runCaptainScopeUpdate;
  const startSources = typeof config.startRequiredSourceDispatches === 'function' ? config.startRequiredSourceDispatches : startRequiredSourceDispatches;
  const followCompletedRuns = (record, agent) => {
    Promise.all(record.sourceRuns.map((run) => run.result)).then(async (outcomes) => {
      if (outcomes.some((outcome) => outcome?.stopReason !== 'completed')) {
        const reasons = outcomes.map((outcome) => outcome?.diagnostic).filter(Boolean).join('; ');
        ctx.logger?.warn?.(`PTC batch ${record.batchId}: a ${record.state} specialist did not complete${reasons === '' ? '' : ` — ${reasons}`}`);
        return;
      }
      const nextResult = await executeContinue(root, record.batchId);
      const nextRuns = await startSources(ctx, nextResult, agent, undefined, config);
      if (nextRuns.length === 0) { ctx.logger?.info?.(`PTC batch ${record.batchId}: no further automatic dispatch (${nextResult.state})`); return; }
      record.state = nextResult.state; record.sourceRuns = nextRuns; followCompletedRuns(record, agent);
    }).catch((error) => ctx.logger?.error?.(`PTC batch ${record.batchId}: automatic stage transition failed: ${error?.message ?? error}`));
  };
  ctx.on('agent/pre-step', async ({ agent, messages, signal }, next) => {
    const decision = await next();
    if (decision.kind === 'reject' || !isPtcCaptainAgent(agent, root)) return decision;
    const sessionKey = String(agent?.id ?? 'captain');
    let record = active.get(sessionKey) ?? null;
    let result;
    if (!record) {
        const request = firstDeliveryRequest(messages);
        if (!request) return decision;
        signal?.throwIfAborted?.();
        result = await executeStart(root, request.text);
        if (typeof result.batchId === 'string' && result.batchId) {
          // This is a runtime dispatch, not a model suggestion: source specialists
          // exist before the Captain can make a tool call or inspect old state.
          const runs = await startSources(ctx, result, agent, signal, config);
          record = { batchId: result.batchId, requestId: request.id, lastSignature: signature(result), sourceRuns: runs, entry: result };
          active.set(sessionKey, record);
          if (result.executionScope?.stopAfter === 'INPUT_SYNC' && runs.every((run) => run.mode === 'UNCHANGED')) {
            const terminal = await finishScopedSources(root, result, runs);
            return { kind: 'enter', messages: [...decision.messages, terminalMessage(request.id, terminal)] };
          }
          // INPUT_SYNC is now owned by the direct specialists. End the Captain
          // turn before it can make a read/glob/list_agents call; the later
          // handoff creates the next Captain turn.
          agent.cancel?.({ kind: 'hook', reason: 'PTC INPUT_SYNC specialists dispatched directly' });
          if (result.executionScope?.stopAfter === 'INPUT_SYNC') {
            finishScopedSources(root, result, runs)
              .then((terminal) => agent.followup?.(terminalMessage(request.id, terminal)))
              .catch((error) => ctx.logger?.error?.(`PTC scoped source completion failed: ${error.message}`));
          }
          return { kind: 'reject' };
        }
      return {
        kind: 'enter',
        messages: [...decision.messages, injectedMessage(request.id, result)],
      };
    }

    const correction = latestDeliveryRequest(messages);
    if (correction && correction.id !== record.requestId && deliveryExecutionScope(correction.text).stopAfter === 'INPUT_SYNC') {
      const narrowed = await executeScopeUpdate(root, record.batchId, correction.text);
      if (narrowed.state === 'BLOCKED') {
        return { kind: 'enter', messages: [...decision.messages, injectedMessage(correction.id, narrowed)] };
      }
      record.requestId = correction.id;
      record.entry = { ...record.entry, ...narrowed };
      const allowed = new Set(narrowed.executionScope.sourceRoles);
      const kept = record.sourceRuns.filter((run) => allowed.has(run.role));
      const removed = record.sourceRuns.filter((run) => !allowed.has(run.role));
      removed.forEach((run) => run.abort?.('user narrowed this batch to DFT only'));
      Promise.allSettled(removed.map((run) => run.result)).catch(() => {});
      record.sourceRuns = kept;
      if (kept.every((run) => run.mode === 'UNCHANGED')) {
        const terminal = await finishScopedSources(root, record.entry, kept);
        return { kind: 'enter', messages: [...decision.messages, terminalMessage(correction.id, terminal)] };
      }
      agent.cancel?.({ kind: 'hook', reason: 'PTC batch narrowed to DFT only' });
      finishScopedSources(root, record.entry, kept)
        .then((terminal) => agent.followup?.(terminalMessage(correction.id, terminal)))
        .catch((error) => ctx.logger?.error?.(`PTC scoped source completion failed: ${error.message}`));
      return { kind: 'reject' };
    }

    // Further advancement is driven by a completed specialist handoff, never by
      // ordinary model tool steps. Advancing here would consume INPUT_SYNC before
      // the source experts have run.
      return decision;
  }, { prepend: true });

}
