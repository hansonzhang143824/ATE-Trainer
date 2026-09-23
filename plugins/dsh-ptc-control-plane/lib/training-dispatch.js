import fs from 'node:fs';
import path from 'node:path';
import { signTrainingReceipt, trainingDispatchLabel } from './training-guard.js';

export const TRAINING_DEADLINE_MS = 5 * 60 * 1000;

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
    type: 'object',
    properties: {
      status: { type: 'string', enum: ['done', 'blocked'] },
      outputs: { type: 'array', items: { type: 'string' } },
      gates: { type: 'array', items: { type: 'string' } },
      question: { type: 'string' },
      mode: { type: 'string', enum: ['CREATED', 'UNCHANGED', 'OVERWRITTEN'] },
    },
    required: ['status'], additionalProperties: false,
  };
}

function persona(workspaceRoot) {
  const instructions = fs.readFileSync(path.join(workspaceRoot, 'team', 'expert-profiles', 'ptc-dft-expert', 'instructions.md'), 'utf8').replace(/^\uFEFF/, '');
  return [
    'You are the DSH-native TRAINING instance of the draft ptc-dft-expert profile.',
    'This is not delivery. The host enforces the training address book and refuses every production write.',
    'You never dispatch another agent and never advance a PTC stage.',
    instructions,
  ].join('\n\n');
}

function taskPrompt(runId, testItems, reports) {
  const commands = testItems.flatMap((tm) => [
    `python scripts/refresh_dft_meta_from_source.py --source Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx --tm ${tm} --meta Training_Materials/Output_Global_Material/dft/${tm}/dft-meta.json --expected-sha <SOURCE_SHA> --input-root Training_Materials/Input_GlobalMaterial`,
    `python scripts/render_dft_conditions_yaml.py --tm ${tm} --out Training_Materials/Output_Global_Material/dft/${tm}/dft-conditions.yaml --expected-sha <SOURCE_SHA> --workbook Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx`,
    `python scripts/validate_dft_outputs.py --tm ${tm} --workbook Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx --output-dir Training_Materials/Output_Global_Material/dft/${tm}`,
  ]);
  return [
    `Training run: ${runId}. Assigned items: ${testItems.join(', ')}.`,
    'Address book: reads=Training_Materials/Input_GlobalMaterial; writes=Training_Materials/Output_Global_Material/dft; verification=Training_Materials/Output_Global_Material/verification.',
    'The host preflight already proved the candidate is STALE. Regenerate the complete three-product set, independently review it against the source and bind the review to producer-reported hashes. Use PASS only if the review supports it; unresolved conflicts must return blocked. Then run the final validator.',
    'First obtain SOURCE_SHA with exactly: python scripts/hash_ate_plaintext.py Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx',
    'Then use only these commands, replacing <SOURCE_SHA> with that exact digest:',
    ...commands,
    `Preflight summary: ${JSON.stringify(reports.map((report) => ({
      tm: report.tm,
      status: report.status,
      sourceSha256: report.canonicalInput?.sha256,
      staleReasonCount: report.missingOrStaleOutputs?.length ?? 0,
    })))}`,
    'Keep model work to at most three steps. Prefer run_code to batch the permitted hash/refresh/render/read operations, then one final run_code for semantic-review write, validation, verification write and structured_output.',
    'Return structured status=done only after every final validator exits 0. Otherwise return status=blocked with the exact reason. Do not use delivery paths.',
  ].join('\n');
}

function deadlineResult(childRun, controller, label, timeoutMs, logger) {
  const diagnostic = `${label}: BLOCKED — training execution exceeded ${timeoutMs} ms; child cancellation requested`;
  const timedOutResult = { stopReason: 'timeout', diagnostic, structured: { status: 'blocked', question: diagnostic } };
  let timer;
  let timedOut = false;
  let resolveTimeout;
  const timeout = new Promise((resolve) => { resolveTimeout = resolve; });
  const onAbort = () => resolveTimeout(timedOut ? timedOutResult : {
    stopReason: 'aborted',
    structured: { status: 'blocked', question: String(controller.signal.reason?.message ?? 'training run stopped') },
  });
  controller.signal.addEventListener('abort', onAbort, { once: true });
  if (controller.signal.aborted) onAbort();
  timer = setTimeout(() => {
    timedOut = true;
    controller.abort(new Error(diagnostic));
    resolveTimeout(timedOutResult);
    try { logger?.warn?.(diagnostic); } catch {}
  }, timeoutMs);
  timer.unref?.();
  const child = Promise.resolve(childRun.result).then(
    (result) => (timedOut ? timedOutResult : result),
    (error) => {
      if (timedOut) return timedOutResult;
      throw error;
    },
  );
  return Promise.race([child, timeout]).finally(() => {
    clearTimeout(timer);
    controller.signal.removeEventListener('abort', onAbort);
  });
}

// Cleanup may itself hang; terminal state must not depend on disposal finishing.
function requestDisposal(handle) {
  try { Promise.resolve(handle?.dispose?.()).catch(() => {}); } catch {}
}

export function createTrainingDispatcher(ctx, workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const active = new Map();
  const timeoutMs = options.timeoutMs ?? TRAINING_DEADLINE_MS;
  return {
    async dispatch({ runId, testItems, reports, runDirectory }) {
      if (!ctx?.subagents?.getProvider?.('spawn')) throw new Error('DSH subagent provider "spawn" is unavailable');
      if (!ctx?.agents?.create || !ctx?.agentDefaultModel?.currentSelection || !ctx?.agentPresets?.mount) {
        throw new Error('DSH agent creation and preset composition services are unavailable');
      }
      const selection = ctx.agentDefaultModel.currentSelection();
      const parentSessionId = `session-ptc-training-parent-${runId}`;
      const label = trainingDispatchLabel(runId, testItems);
      const receiptFile = path.join(runDirectory, 'dispatch.json');
      const baseReceipt = {
        schemaVersion: 1, kind: 'ptc-training-dispatch', runId,
        profileId: 'ptc-dft-expert', profileSource: 'draft', testItems,
        label, parentSessionId, childSessionId: null,
        addressBook: {
          reads: 'Training_Materials/Input_GlobalMaterial',
          writes: 'Training_Materials/Output_Global_Material/dft',
          verification: 'Training_Materials/Output_Global_Material/verification',
        },
        createdAt: new Date().toISOString(),
      };
      writeJsonAtomic(receiptFile, signTrainingReceipt(baseReceipt));
      let parentHandle;
      let childRun;
      const controller = new AbortController();
      try {
        parentHandle = await ctx.agents.create({
          sessionId: parentSessionId,
          meta: { cwd: root, agentPreset: 'ate-ptc' },
          agentOptions: { provider: selection.provider, model: selection.model },
          setup: async (agentCtx) => { await ctx.agentPresets.mount(agentCtx, 'ate-ptc'); },
        });
        await parentHandle.agent.whenIdle();
        childRun = await ctx.subagents.start('spawn', {
          label,
          prompt: [{ type: 'text', text: taskPrompt(runId, testItems, reports) }],
          parent: parentHandle.agent,
          signal: controller.signal,
          agentOptions: { provider: selection.provider, model: selection.model },
          persona: persona(root),
          toolFilter: { allow: ['read', 'write', 'pwsh'] },
          maxDepth: 1,
          outputSchema: terminalSchema(),
        });
        const childSessionId = typeof childRun.id === 'string' ? childRun.id : null;
        if (childSessionId === null) throw new Error('DSH returned no child session id');
        const dispatchedReceipt = { ...baseReceipt, childSessionId, dispatchedAt: new Date().toISOString() };
        writeJsonAtomic(receiptFile, signTrainingReceipt(dispatchedReceipt));
        const completion = deadlineResult(childRun, controller, label, timeoutMs, ctx.logger).finally(() => {
          active.delete(runId);
          try {
            writeJsonAtomic(receiptFile, signTrainingReceipt({
              ...dispatchedReceipt, executionStatus: 'closed', closedAt: new Date().toISOString(),
            }));
          } finally {
            requestDisposal(childRun);
            requestDisposal(parentHandle);
          }
        });
        const record = {
          childSessionId, parentSessionId, receiptFile, result: completion,
          abort(reason = 'training run stopped') { controller.abort(new Error(reason)); },
        };
        active.set(runId, record);
        return record;
      } catch (error) {
        controller.abort(error);
        requestDisposal(childRun);
        requestDisposal(parentHandle);
        throw error;
      }
    },
    stop(runId, reason) {
      const record = active.get(runId);
      if (!record) return false;
      record.abort(reason);
      return true;
    },
    shutdown() {
      for (const record of active.values()) record.abort('PTC control-plane plugin stopped');
      active.clear();
    },
  };
}
