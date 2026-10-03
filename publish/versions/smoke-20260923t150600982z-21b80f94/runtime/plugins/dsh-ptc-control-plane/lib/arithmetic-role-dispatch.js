import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { createTrainingLifecycle } from './training-lifecycle.js';
import { resolveTrainingModelChoice } from './training-model.js';

const DIGEST = /^[a-f0-9]{64}$/;
const ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const ROLE = /^[a-z][a-z0-9-]{1,63}$/;
const STAGE = /^(?:STRATEGY|METHOD|RULE_REVIEW_METHOD|IMPLEMENTATION|RULE_REVIEW_IMPLEMENTATION|COMPILE|SMOKE_AUXILIARY)$/;
const PROFILE_IDS = new Set(['ate-implementer', 'compile-diagnostician', 'evolution-expert',
  'method-expert', 'rule-reviewer', 'strategy-expert']);
const INSTRUCTION = '1+2等于几，把答案写在JSON里';
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const relative = (root, file) => path.relative(root, file).split(path.sep).join('/');

function exclusive(root, file, value) {
  assertSafeRunPath(root, file);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  return sha(fs.readFileSync(file));
}

function boundRequest(root, request) {
  if (!request || !ID.test(request.runId ?? '') || !STAGE.test(request.stage ?? '')
      || !ROLE.test(request.role ?? '') || !PROFILE_IDS.has(request.profileId)
      || !/^draft-[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(request.profileVersion ?? '')
      || !DIGEST.test(request.profileDigest ?? '') || !DIGEST.test(request.registryDigest ?? '')
      || request.mode !== 'SMOKE_ONLY' || request.instruction !== INSTRUCTION
      || request.provisional !== false
      || request.dispatchId !== `${request.runId}:${request.stage}:${request.role}:1`
      || !Array.isArray(request.testItems) || !request.testItems.length
      || request.testItems.some(item => typeof item !== 'string' || !/^TM\d+$/.test(item))
      || new Set(request.testItems).size !== request.testItems.length) {
    throw new Error('arithmetic dispatch requires one bound non-source smoke task');
  }
  const runRoot = assertSafeRunPath(root, path.join(root, 'Training_Materials', 'runs', request.runId));
  if (path.resolve(request.runRoot ?? '') !== runRoot) throw new Error('arithmetic task runRoot differs');
  const context = read(assertSafeRunPath(root, path.join(runRoot, 'run.json')));
  const state = read(assertSafeRunPath(root, path.join(runRoot, 'state.json')));
  if (context.mode !== 'training' || context.runId !== request.runId || context.releaseId !== null
      || context.projectId !== null || path.resolve(root, context.artifactRoot) !== runRoot
      || state.runId !== request.runId || state.purpose !== 'smoke-training'
      || state.target?.kind !== 'pipeline' || !['running', 'pausing'].includes(state.status)) {
    throw new Error('arithmetic task is not in its own live training pipeline run');
  }
  const record = read(assertSafeRunPath(root, path.join(runRoot, 'simple-orchestration.json')));
  const registryFile = assertSafeRunPath(root, path.join(runRoot, 'simple-orchestration-registry.json'));
  if (record.runId !== request.runId || record.mode !== 'SMOKE_ONLY'
      || record.registryDigest !== request.registryDigest
      || sha(fs.readFileSync(registryFile)) !== request.registryDigest
      || JSON.stringify(record.testItems) !== JSON.stringify(request.testItems)) {
    throw new Error('arithmetic task differs from frozen orchestration');
  }
  const task = request.stage === 'SMOKE_AUXILIARY'
    ? record.auxiliaryTasks?.find(item => item.dispatchId === request.dispatchId)
    : record.stages?.find(item => item.stage === request.stage)?.tasks?.find(item => item.dispatchId === request.dispatchId);
  const stage = record.stages?.find(item => item.stage === request.stage);
  if (!task || task.status !== 'dispatching' || task.role !== request.role || task.profileId !== request.profileId
      || task.profileVersion !== request.profileVersion || task.profileDigest !== request.profileDigest
      || (request.stage !== 'SMOKE_AUXILIARY' && (stage?.owner !== request.owner || stage?.gate !== request.registryGate))
      || (request.stage === 'SMOKE_AUXILIARY' && (request.owner !== null || request.registryGate !== null))) {
    throw new Error('arithmetic task role/profile/gate binding differs');
  }
  if (request.signal !== undefined && !(request.signal instanceof AbortSignal)) throw new Error('invalid abort signal');
  const evidenceRoot = assertSafeRunPath(root, path.join(runRoot, 'evidence', 'roles'));
  const stem = `${request.stage}-${request.role}`;
  return { runRoot, evidenceRoot, stem };
}

/** Dispatch a REAL child for a non-source role in this pipeline run. This is
 * intentionally a control-plane arithmetic smoke, not stage implementation.
 * The authoritative orchestration controller independently checks the receipt.
 */
export function createArithmeticRoleDispatcher(ctx, workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const active = new Map();
  async function executeSmokeRole(request) {
    const bound = boundRequest(root, request);
    if (active.has(request.dispatchId)) throw new Error('arithmetic role is already active');
    if (!ctx?.agents?.create || !ctx?.subagents?.start || !ctx?.agentDefaultModel?.currentSelection) {
      throw new Error('DSH arithmetic child services are unavailable');
    }
    const selection = resolveTrainingModelChoice(options.modelChoice ?? 'default', ctx.agentDefaultModel.currentSelection());
    const receiptId = crypto.randomUUID();
    const receiptFile = assertSafeRunPath(root, path.join(bound.evidenceRoot, `${bound.stem}-dispatch.json`));
    const resultFile = assertSafeRunPath(root, path.join(bound.evidenceRoot, `${bound.stem}-child.json`));
    const evidenceFile = assertSafeRunPath(root, path.join(bound.evidenceRoot, `${bound.stem}.json`));
    const dispatchReceiptSha256 = exclusive(root, receiptFile, { schemaVersion: 1, kind: 'arithmetic-role-dispatch',
      runId: request.runId, dispatchId: request.dispatchId, receiptId, stage: request.stage,
      role: request.role, profileId: request.profileId, profileVersion: request.profileVersion,
      profileDigest: request.profileDigest, registryDigest: request.registryDigest,
      mode: 'SMOKE_ONLY', businessGatePassed: false,
      modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model,
      createdAt: new Date().toISOString() });
    const lifecycle = createTrainingLifecycle({ timeoutMs: options.timeoutMs ?? 300_000 });
    const abort = () => lifecycle.cancel(request.signal?.reason ?? 'smoke orchestration cancelled');
    request.signal?.addEventListener('abort', abort, { once: true });
    if (request.signal?.aborted) abort();
    active.set(request.dispatchId, lifecycle);
    let child; let result; let responseSha256 = null;
    try {
      const agentOptions = { provider: selection.provider, model: selection.model, maxTokens: 256 };
      const parent = await lifecycle.race(() => ctx.agents.create({
        sessionId: `session-arithmetic-${receiptId}`, meta: { cwd: root }, agentOptions,
      }), { label: 'parent.create', disposeLate: handle => handle.dispose?.() });
      await lifecycle.race(() => parent.agent.whenIdle(), { label: 'parent.idle' });
      child = await lifecycle.race(() => ctx.subagents.start('spawn', {
        label: `PTC smoke ${request.profileId} ${request.runId} ${request.stage}`,
        parent: parent.agent, signal: lifecycle.signal, agentOptions, maxDepth: 1,
        toolFilter: { allow: [] },
        persona: `PTC smoke child for ${request.profileId}. Do not use tools or project materials; this is not business execution.`,
        prompt: [{ type: 'text', text: INSTRUCTION }],
        outputSchema: { type: 'object', properties: { answer: { type: 'number' } },
          required: ['answer'], additionalProperties: false },
      }), { label: 'child.start', disposeLate: handle => {
        Promise.resolve(handle.result).catch(() => {}); return handle.dispose?.();
      } });
      if (typeof child?.id !== 'string' || !child.id) throw new Error('DSH child returned no session ID');
      result = await lifecycle.race(child.result, { label: 'child.result', trackSettlement: true });
      if (result?.stopReason !== 'completed' || typeof result?.structured?.answer !== 'number'
          || result.structured.answer !== 3) throw new Error('arithmetic child did not return numeric JSON answer 3');
      // Capture the host-observed child result first; this SHA is over its
      // exact on-disk bytes, not over a model-supplied digest.
      responseSha256 = exclusive(root, resultFile, result);
      const evidence = { schemaVersion: 1, kind: 'ptc-arithmetic-role', runId: request.runId,
        dispatchId: request.dispatchId, stage: request.stage, role: request.role,
        profileId: request.profileId, profileVersion: request.profileVersion,
        profileDigest: request.profileDigest, executionKind: 'arithmetic-child',
        mode: 'SMOKE_ONLY', businessGatePassed: false,
        childReceiptId: receiptId, childSessionId: child.id, answer: 3,
        dispatchReceiptPath: relative(root, receiptFile), dispatchReceiptSha256,
        responsePath: relative(root, resultFile), responseSha256,
        modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model,
        finishedAt: new Date().toISOString() };
      const childEvidenceSha256 = exclusive(root, evidenceFile, evidence);
      return { status: 'done', executionKind: 'arithmetic-child', stage: request.stage,
        role: request.role, profileId: request.profileId, profileVersion: request.profileVersion,
        profileDigest: request.profileDigest, testItems: [...request.testItems],
        childReceiptId: receiptId, childEvidencePath: evidenceFile, childEvidenceSha256,
        businessGatePassed: false };
    } catch (error) {
      if (result && !fs.existsSync(resultFile)) {
        responseSha256 = exclusive(root, resultFile, result);
      }
      if (!fs.existsSync(evidenceFile)) {
        exclusive(root, evidenceFile, { schemaVersion: 1, kind: 'ptc-arithmetic-role',
          runId: request.runId, dispatchId: request.dispatchId, stage: request.stage, role: request.role,
          profileId: request.profileId, profileVersion: request.profileVersion,
          profileDigest: request.profileDigest, executionKind: 'arithmetic-child',
          status: 'blocked', mode: 'SMOKE_ONLY', businessGatePassed: false,
          childReceiptId: receiptId, childSessionId: child?.id ?? null,
          answer: null, dispatchReceiptPath: relative(root, receiptFile), dispatchReceiptSha256,
          responsePath: result ? relative(root, resultFile) : null, responseSha256,
          stopReason: result?.stopReason ?? error?.stopReason ?? 'error',
          reason: String(error?.message ?? error), finishedAt: new Date().toISOString() });
      }
      throw error;
    } finally {
      active.delete(request.dispatchId);
      request.signal?.removeEventListener('abort', abort);
      lifecycle.close();
    }
  }
  return {
    executeSmokeRole,
    shutdown() { for (const lifecycle of active.values()) lifecycle.cancel('arithmetic role dispatcher stopped'); },
  };
}
