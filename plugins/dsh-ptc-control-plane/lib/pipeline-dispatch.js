import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { createTrainingLifecycle, TrainingCancellationError } from './training-lifecycle.js';
import { stageDispatchLabel, signStageReceipt, revokeStageDispatch } from './pipeline-guard.js';

function atomic(root, file, value) {
  assertSafeRunPath(root, file);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
  try { fs.renameSync(temporary, file); } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));

/** One real generic stage child. Source parsers and compile remain host adapters. */
export function createPipelineDispatcher(ctx, workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const active = new Map();
  return {
    async dispatch(request, materials) {
      const { runId, stage, owner: role, gate, registryDigest, testItems, signal } = request;
      if (!['STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD', 'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION'].includes(stage)) {
        throw new Error('this stage requires its dedicated host source/compile adapter');
      }
      const runRoot = assertSafeRunPath(root, path.join(root, 'Training_Materials/runs', runId));
      if (materials?.runId !== runId || !materials.profileRoots || !materials.ownerProfiles?.[role]) throw new Error('missing frozen pipeline profile mapping');
      const registryFile = assertSafeRunPath(root, path.join(runRoot, 'pipeline-registry.json'));
      const registryBytes = fs.readFileSync(registryFile);
      const registry = JSON.parse(registryBytes.toString('utf8'));
      if (crypto.createHash('sha256').update(registryBytes).digest('hex') !== registryDigest
          || registry.stages?.[stage]?.owner !== role || registry.stages[stage].gate !== gate
          || !Array.isArray(testItems) || !testItems.length || testItems.some(tm => !/^TM\d+$/.test(tm))) throw new Error('stage dispatch differs from frozen registry');
      const profileId = materials.ownerProfiles[role];
      const profileRoot = assertSafeRunPath(root, path.resolve(root, materials.profileRoots[profileId]));
      const relativeProfile = path.relative(runRoot, profileRoot);
      if (relativeProfile.startsWith('..') || path.isAbsolute(relativeProfile)) throw new Error('profile is not a private snapshot');
      const instructions = fs.readFileSync(assertSafeRunPath(root, path.join(profileRoot, 'instructions.md')), 'utf8');
      const dispatchId = `${runId}:${stage}:${role}:1`;
      const receiptFile = path.join(runRoot, 'receipts', `${stage}-${role}.json`);
      const terminalFile = path.join(runRoot, 'receipts', `${stage}-${role}-terminal.json`);
      const lifecycleFile = path.join(runRoot, 'evidence', `${stage}-${role}-lifecycle.json`);
      if (active.has(dispatchId) || fs.existsSync(receiptFile)) throw new Error('stage dispatch already exists; recover its real receipt instead of repeating it');
      const selection = ctx.agentDefaultModel.currentSelection();
      const parentSessionId = `session-training-${runId}-${stage}-${role}`;
      const label = stageDispatchLabel(runId, stage, role);
      let receipt = { schemaVersion: 1, kind: 'ptc-training-stage', runId, stage, role, profileId, gate,
        testItems, dispatchId, registryDigest, label, parentSessionId, childSessionId: null,
        profileSha256: crypto.createHash('sha256').update(instructions).digest('hex'),
        pipelineCacheKey: materials.pipelineCacheKey, createdAt: new Date().toISOString() };
      atomic(root, receiptFile, signStageReceipt(receipt));
      const close = reason => {
        revokeStageDispatch(root, dispatchId);
        if (receipt.executionStatus === 'closed') return;
        const next = { ...receipt, executionStatus: 'closed', closeReason: reason, closedAt: new Date().toISOString() };
        atomic(root, receiptFile, signStageReceipt(next)); receipt = next;
      };
      const lifecycle = createTrainingLifecycle({ timeoutMs: options.timeoutMs ?? 300_000,
        onCancel: error => close(error.message),
        onEvent: (event, state) => atomic(root, lifecycleFile, { runId, dispatchId, event, ...state }),
      });
      const abort = () => lifecycle.cancel(signal?.reason ?? 'pipeline cancelled');
      signal?.addEventListener('abort', abort, { once: true });
      if (signal?.aborted) abort();
      active.set(dispatchId, lifecycle);
      try {
        const parent = await lifecycle.race(() => ctx.agents.create({ sessionId: parentSessionId,
          meta: { cwd: root, agentPreset: 'ate-ptc' }, agentOptions: selection,
          setup: async agentCtx => { await ctx.agentPresets.mount(agentCtx, 'ate-ptc'); },
        }), { label: 'parent.create', disposeLate: value => value.dispose?.() });
        await lifecycle.race(() => parent.agent.whenIdle(), { label: 'parent.idle' });
        const child = await lifecycle.race(() => ctx.subagents.start('spawn', {
          label, parent: parent.agent, signal: lifecycle.signal, agentOptions: selection,
          maxDepth: 1, toolFilter: { allow: ['read', 'write'] },
          persona: `You are a frozen draft PTC TRAINING specialist, not a Captain.\n${instructions}\n\nNATIVE HOST OVERRIDE: use only the injected private run address book. Do not dispatch, advance, access production paths or run shell commands. The host independently executes the registry gate after your output is complete. Do not claim that host gate already passed. Return blocked for unsupported or conflicting source facts.`,
          prompt: [{ type: 'text', text: `Run ${runId}; stage ${stage}; owner ${role}; TMs ${testItems.join(', ')}.\nFrozen materials: ${JSON.stringify({ input: materials.input, trials: materials.trials, registerRoot: materials.registerRoot, knowledgeRoot: materials.knowledgeRoot, programSourceRoot: materials.programSourceRoot, profileRoot })}\nWrite this stage's outputs for EVERY assigned TM under its trial directory. Stage contract outputs: ${JSON.stringify(registry.stages[stage].outputs)}. Host gate: ${gate}. Existing signed inputs must stay byte-identical. Implementation may edit only the private source copy, never the approved source original. Respond done only when all requested artifacts are ready for host validation; otherwise blocked with exact reason.` }],
          outputSchema: { type: 'object', properties: { status: { type: 'string', enum: ['done', 'blocked'] }, reason: { type: 'string' }, outputs: { type: 'array', items: { type: 'string' } } }, required: ['status'], additionalProperties: false },
        }), { label: 'child.start', disposeLate: value => { Promise.resolve(value.result).catch(() => {}); return value.dispose?.(); } });
        if (typeof child.id !== 'string' || !child.id) throw new Error('stage child has no bound session id');
        receipt = { ...receipt, childSessionId: child.id, dispatchedAt: new Date().toISOString() };
        atomic(root, receiptFile, signStageReceipt(receipt));
        const result = await lifecycle.race(child.result, { label: 'child.result', trackSettlement: true });
        const terminal = { runId, dispatchId, registryDigest, role, testItems, childSessionId: child.id,
          status: result?.stopReason === 'completed' && result?.structured?.status === 'done' ? 'done' : 'blocked',
          result, finishedAt: new Date().toISOString() };
        atomic(root, terminalFile, signStageReceipt(terminal));
        return terminal;
      } catch (error) {
        lifecycle.cancel(error);
        const terminal = { runId, dispatchId, registryDigest, role, testItems, status: 'blocked',
          stopReason: error instanceof TrainingCancellationError ? error.stopReason : 'error', reason: error.message };
        atomic(root, terminalFile, signStageReceipt(terminal));
        return terminal;
      } finally {
        active.delete(dispatchId); signal?.removeEventListener('abort', abort);
        try { close('stage child finished'); } finally { lifecycle.close(); }
      }
    },
    recover(request) {
      const role = request.owner;
      const file = assertSafeRunPath(root, path.join(root, 'Training_Materials/runs', request.runId, 'receipts', `${request.stage}-${role}-terminal.json`));
      const terminal = readJson(file);
      // Recovery returns an observed terminal, never a synthetic successful run.
      const signed = signStageReceipt(terminal);
      if (signed.digest !== terminal.digest || terminal.runId !== request.runId || terminal.registryDigest !== request.registryDigest
          || terminal.role !== role || terminal.dispatchId !== `${request.runId}:${request.stage}:${role}:1`
          || JSON.stringify(terminal.testItems) !== JSON.stringify(request.testItems)) throw new Error('unbound stage terminal receipt');
      return terminal;
    },
    shutdown() { for (const lifecycle of active.values()) lifecycle.cancel('native plugin stopped'); },
  };
}
