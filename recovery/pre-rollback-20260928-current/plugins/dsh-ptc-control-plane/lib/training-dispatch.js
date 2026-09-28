import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { signTrainingReceipt, trainingDispatchLabel, revokeTrainingRun } from './training-guard.js';
import { createTrainingLifecycle, TrainingCancellationError } from './training-lifecycle.js';
import { trainingAddressBook } from './training-paths.js';
import { resolveTrainingModelChoice } from './training-model.js';

export const TRAINING_DEADLINE_MS = 5 * 60 * 1000;
export const TRAINING_RESPONSE_MAX_TOKENS = 2048;
export const TRAINING_SEMANTIC_REVIEW_MS = 60_000;

function writeJsonAtomic(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.tmp-${process.pid}-${Date.now()}`;
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
  try { fs.renameSync(temporary, file); } catch (error) {
    try { fs.unlinkSync(temporary); } catch {}
    throw error;
  }
}

function terminalSchema() {
  return {
    type: 'object', properties: {
      status: { type: 'string', enum: ['done', 'blocked'] },
      reviews: { type: 'array', items: {
        type: 'object', properties: {
          tm: { type: 'string' }, verdict: { type: 'string', enum: ['PASS', 'BLOCKED'] },
          findings: { type: 'array', items: { type: 'string' } },
        }, required: ['tm', 'verdict', 'findings'], additionalProperties: false,
      } },
      question: { type: 'string' },
    },
    required: ['status', 'reviews'], additionalProperties: false,
  };
}

function persona() {
  return [
    'You are the semantic-review step of the DSH-native TRAINING ptc-dft-expert.',
    'The host has already frozen the profile and source, run the approved deterministic producers, and supplied their complete bounded evidence below.',
    'Review sourceEvidence against metaProjection and conditionsProjection. Check identity, raw source coverage, expected value, power sequence, register intent, measurement, involved pins, helper/ramp meaning, and contradictions.',
    'Before blocking a contradiction, inspect the assigned item intentResolution. When it has status=resolved, its authority and decision are the accepted project baseline for the listed conflict: record copied source wording as a non-blocking finding and judge generated facts against that decision. Block only when generated facts disagree with the resolved decision, or when no authoritative resolution exists.',
    'Use no more than eight internal checklist comparisons. Do not narrate field-by-field analysis.',
    'Do not calculate or repeat hashes. Do not use tools, write files, dispatch agents, or advance a stage.',
    'CRITICAL RESPONSE BUDGET: call structured_output as your next action after reading the packet. Do not emit a reasoning narrative before the call. Return exactly one concise finding per assigned TM (each finding <=240 characters, with a source/product line reference); keep question <=800 characters.',
    'Return the structured result immediately. PASS only when every generated semantic fact is supported by the supplied source; otherwise use status=blocked and verdict=BLOCKED with the concrete conflict.',
    'You never dispatch another agent and never advance a PTC stage.',
  ].join('\n\n');
}

function taskPrompt(runId, testItems, materials, reviewInput) {
  const semanticInput = { items: reviewInput.items.map((item) => ({
    tm: item.tm, sourceEvidence: item.sourceEvidence,
    metaProjection: item.metaProjection, conditionsProjection: item.conditionsProjection,
    intentResolution: item.intentResolution ?? null,
  })) };
  return [
    `Training run ${runId}; assigned items ${testItems.join(', ')}; frozen material cache ${materials.cacheKey}.`,
    'Return status=done with one PASS review per assigned TM, or status=blocked with BLOCKED reviews and a short question explaining the first unsupported or contradictory fact. If intentResolution.status is resolved, apply its decision and do not ask the user to re-resolve that listed conflict; mention the copied wording only as a non-blocking finding. Call structured_output immediately; do not write a prose analysis first. Keep each finding <=240 characters and cite the supplied source/product line.',
    `Semantic-review input: ${JSON.stringify(semanticInput)}`,
  ].join('\n');
}

function requireMaterials(runId, testItems, materials) {
  const expected = trainingAddressBook(runId);
  if (!materials || materials.runId !== runId || !Array.isArray(materials.testItems)
      || JSON.stringify([...new Set(materials.testItems)].sort()) !== JSON.stringify([...new Set(testItems)].sort())
      || Object.entries(expected).some(([key, value]) => materials[key] !== value)) {
    throw new Error('dispatch requires matching prepared training materials');
  }
}

function requireSourceView(runId, testItems, materials, sourceView) {
  if (!sourceView || sourceView.status !== 'SOURCE_VIEW' || sourceView.runId !== runId
      || sourceView.path !== materials.sourceView || !/^[a-f0-9]{64}$/.test(sourceView.sha256 ?? '')
      || !/^[a-f0-9]{64}$/.test(sourceView.sourceSha256 ?? '')
      || JSON.stringify(sourceView.testItems) !== JSON.stringify([...new Set(testItems)].sort())) {
    throw new Error('dispatch requires matching host-generated DFT source view');
  }
}

function requireReviewInput(runId, testItems, reviewInput) {
  if (!reviewInput || reviewInput.schemaVersion !== 1 || reviewInput.runId !== runId
      || !Array.isArray(reviewInput.items) || reviewInput.items.length !== testItems.length
      || JSON.stringify(reviewInput.items.map((item) => item.tm).sort()) !== JSON.stringify([...new Set(testItems)].sort())
      || reviewInput.items.some((item) => !/^[a-f0-9]{64}$/.test(item.sourceSha256 ?? '')
        || !/^[a-f0-9]{64}$/.test(item.producerDigests?.['dft-meta.json'] ?? '')
        || !/^[a-f0-9]{64}$/.test(item.producerDigests?.['dft-conditions.yaml'] ?? ''))) {
    throw new Error('dispatch requires matching host-generated semantic-review input');
  }
}

export function createTrainingDispatcher(ctx, workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const active = new Map();
  const timeoutMs = options.timeoutMs ?? TRAINING_DEADLINE_MS;
  const reviewTimeoutMs = options.reviewTimeoutMs ?? options.progressTimeoutMs ?? TRAINING_SEMANTIC_REVIEW_MS;
  if (!Number.isFinite(reviewTimeoutMs) || reviewTimeoutMs <= 0 || reviewTimeoutMs > TRAINING_SEMANTIC_REVIEW_MS) throw new Error('semantic review deadline must be at most 60 seconds');
  return {
    async dispatch({ runId, testItems, sourceView, reviewInput, reviewInputFile, runDirectory, materials, modelChoice }) {
      requireMaterials(runId, testItems, materials);
      requireSourceView(runId, testItems, materials, sourceView);
      requireReviewInput(runId, testItems, reviewInput);
      if (path.resolve(runDirectory) !== path.join(root, materials.runRoot)) throw new Error('training run directory differs from prepared materials');
      if (path.resolve(reviewInputFile) !== path.join(root, materials.runRoot, 'evidence', 'dft-review-input.json')) throw new Error('semantic-review evidence path differs from prepared run');
      if (active.has(runId)) throw new Error('training run already has an active dispatcher');
      if (!ctx?.subagents?.getProvider?.('spawn')) throw new Error('DSH subagent provider "spawn" is unavailable');
      if (!ctx?.agents?.create || !ctx?.agentDefaultModel?.currentSelection || !ctx?.agentPresets?.mount) {
        throw new Error('DSH agent creation and preset composition services are unavailable');
      }
      const selection = resolveTrainingModelChoice(modelChoice, ctx.agentDefaultModel.currentSelection());
      // The explicitly selected DeepSeek V4 business model emits a longer
      // semantic justification before its required reviews array.  Preserve
      // the historical 2048-token smoke/default contract, but give this real
      // business model enough room to submit structured DFT reviews.
      const responseMaxTokens = selection.choice === 'deepseek-v4-flash'
        ? 8192 : TRAINING_RESPONSE_MAX_TOKENS;
      const parentSessionId = `session-ptc-training-parent-${runId}`;
      const label = trainingDispatchLabel(runId, testItems);
      const receiptFile = path.join(runDirectory, 'dispatch.json');
      const lifecycleFile = path.join(runDirectory, 'evidence', 'lifecycle.json');
      let receipt = {
        schemaVersion: 1, kind: 'ptc-training-dispatch', runId,
        profileId: 'ptc-dft-expert', profileSource: 'draft-snapshot', testItems,
        label, parentSessionId, childSessionId: null,
        addressBook: { reads: materials.inputRoot, writes: materials.dftRoot, verification: materials.verificationRoot },
        sourceView: { path: sourceView.path, sha256: sourceView.sha256, sourceSha256: sourceView.sourceSha256 },
        reviewInput: { path: path.relative(root, reviewInputFile).split(path.sep).join('/'),
          sha256: crypto.createHash('sha256').update(fs.readFileSync(reviewInputFile)).digest('hex') },
        materialCacheKey: materials.cacheKey, createdAt: new Date().toISOString(),
      };
      writeJsonAtomic(receiptFile, signTrainingReceipt(receipt));
      function closeReceipt(reason) {
        revokeTrainingRun(root, runId);
        if (receipt.executionStatus === 'closed') return;
        const closed = { ...receipt, executionStatus: 'closed', closedAt: new Date().toISOString(), ...(reason ? { closeReason: reason } : {}) };
        writeJsonAtomic(receiptFile, signTrainingReceipt(closed));
        receipt = closed;
      }
      let reviewTimer;
      const clearReviewTimer = () => { clearTimeout(reviewTimer); reviewTimer = undefined; };
      const lifecycle = createTrainingLifecycle({
        timeoutMs, disposeTimeoutMs: options.disposeTimeoutMs,
        onCancel(error) { clearReviewTimer(); closeReceipt(error.message); },
        onEvent(event, state) {
          writeJsonAtomic(lifecycleFile, { schemaVersion: 1, runId, event, phase: 'semantic_review', ...state });
        },
      });
      const record = {
        childSessionId: null, parentSessionId, receiptFile, lifecycleFile, result: null,
        abort(reason = 'training run stopped') { return lifecycle.cancel(reason); },
        lifecycleState: () => lifecycle.state(),
      };
      // Register before awaited host operations so stop/shutdown can cancel
      // stalled creation, preset setup, idle wait and subagent launch.
      active.set(runId, record);
      const dispose = (handle) => {
        // A launch may return only after cancellation. Observe its result even
        // though it can never be accepted, so late rejection is not unhandled.
        if (handle?.result) Promise.resolve(handle.result).catch(() => {});
        return handle?.dispose?.();
      };
      const blocked = (error) => ({
        stopReason: error.stopReason,
        diagnostic: `${error.message}; cancellation requested; child result ${lifecycle.state().childSettled ? 'settled' : 'settlement unknown'}; process termination unconfirmed`,
        structured: { status: 'blocked', question: error.message }, lifecycle: lifecycle.state(),
      });
      function finish() {
        clearReviewTimer();
        active.delete(runId);
        try { closeReceipt(); } finally { lifecycle.close(); }
      }
      try {
        const parentHandle = await lifecycle.race(() => ctx.agents.create({
          sessionId: parentSessionId,
          meta: { cwd: root, agentPreset: 'ate-ptc' },
          agentOptions: { provider: selection.provider, model: selection.model, maxTokens: responseMaxTokens },
          setup: async (agentCtx) => { await ctx.agentPresets.mount(agentCtx, 'ate-ptc'); },
        }), { label: 'agents.create', disposeLate: dispose });
        await lifecycle.race(() => parentHandle.agent.whenIdle(), { label: 'parent.whenIdle' });
        const childRun = await lifecycle.race(() => ctx.subagents.start('spawn', {
          label, prompt: [{ type: 'text', text: taskPrompt(runId, testItems, materials, reviewInput) }],
          parent: parentHandle.agent, signal: lifecycle.signal,
          agentOptions: { provider: selection.provider, model: selection.model, maxTokens: responseMaxTokens },
          persona: persona(), toolFilter: { allow: [] },
          maxDepth: 1, outputSchema: terminalSchema(),
        }), { label: 'subagents.start', disposeLate: dispose });
        if (typeof childRun.id !== 'string' || !childRun.id) throw new Error('DSH returned no child session id');
        record.childSessionId = childRun.id;
        receipt = { ...receipt, childSessionId: childRun.id, dispatchedAt: new Date().toISOString() };
        writeJsonAtomic(receiptFile, signTrainingReceipt(receipt));
        reviewTimer = setTimeout(() => lifecycle.cancel(`semantic review did not finish within ${reviewTimeoutMs} ms`, { stopReason: 'timeout' }), reviewTimeoutMs);
        record.result = lifecycle.race(childRun.result, { label: 'child.result', trackSettlement: true }).catch((error) => {
          if (error instanceof TrainingCancellationError) return blocked(error);
          throw error;
        }).finally(finish);
        return record;
      } catch (error) {
        if (!(error instanceof TrainingCancellationError)) lifecycle.cancel(error);
        finish();
        if (error instanceof TrainingCancellationError) {
          record.result = Promise.resolve(blocked(error));
          return record;
        }
        throw error;
      }
    },
    stop(runId, reason) {
      const record = active.get(runId);
      return record ? record.abort(reason) : false;
    },
    noteToolStart(exec) {
      if (!['read', 'write', 'pwsh'].includes(exec.name)) return;
      for (const record of active.values()) {
        if (record.childSessionId && record.childSessionId === exec.agent?.id) {
          record.abort('semantic review child attempted an unauthorized tool');
        }
      }
    },
    shutdown() {
      for (const record of active.values()) record.abort('PTC control-plane plugin stopped');
      active.clear();
    },
  };
}
