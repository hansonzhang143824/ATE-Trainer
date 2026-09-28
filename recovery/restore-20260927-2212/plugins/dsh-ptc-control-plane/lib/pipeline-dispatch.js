import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { createTrainingLifecycle, TrainingCancellationError } from './training-lifecycle.js';
import { stageDispatchLabel, signStageReceipt, revokeStageDispatch } from './pipeline-guard.js';
import { trainingAddressBook } from './training-paths.js';
import { resolveTrainingModelChoice } from './training-model.js';

function atomic(root, file, value) {
  assertSafeRunPath(root, file);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.${crypto.randomUUID()}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
  try { fs.renameSync(temporary, file); } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const sameItems = (a, b) => Array.isArray(a) && Array.isArray(b)
  && JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
function hasSourceReviewEvidence(result) {
  const review = result?.structured;
  const outputs = review?.outputs;
  if (!Array.isArray(outputs) || !outputs.length || !outputs.every(value => typeof value === 'string' && value.trim().length >= 20)) return false;
  if (outputs.length === 3 && outputs.every(value => /\bL\d+\b|\bline\s*\d+\b/i.test(value))) return true;
  // Some specialists use outputs for reviewed file paths and put the three
  // comparisons in reason. Accept that established ABI only with all three
  // named findings and concrete line citations; a bare DONE never passes.
  const reason = review.reason;
  return typeof reason === 'string' && reason.length >= 300
    && /SOURCE-PORT IDENTITY\/COUNT/i.test(reason)
    && /DUT KELVIN IDENTITY\/COUNT/i.test(reason)
    && /RELAY PATH \+ ON\/NC STATE/i.test(reason)
    && (reason.match(/\bL\d+\b/g) ?? []).length >= 3;
}

function bindRequest(root, request, suppliedMaterials) {
  const { runId, stage, owner: role, gate, registryDigest, testItems } = request;
  const sourceReview = stage === 'INPUT_SYNC' && role === 'schematic-expert';
  const address = trainingAddressBook(runId);
  if ((!sourceReview && !['STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD', 'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION'].includes(stage))
      || !/^[a-z][a-z0-9-]{1,63}$/.test(role ?? '')) throw new Error('this stage requires its dedicated host source/compile adapter');
  const runRoot = assertSafeRunPath(root, path.join(root, address.runRoot));
  const context = readJson(assertSafeRunPath(root, path.join(runRoot, 'run.json')));
  if (context.mode !== 'training' || context.runId !== runId || context.releaseId !== null) throw new Error('pipeline dispatcher requires a bound training run');
  const runState = readJson(assertSafeRunPath(root, path.join(runRoot, 'state.json')));
  if (runState.runId !== runId || (runState.modelChoice ?? 'default') !== (request.modelChoice ?? 'default')) {
    throw new Error('stage model choice differs from run identity');
  }
  const manifest = readJson(assertSafeRunPath(root, path.join(runRoot, 'pipeline-material-manifest.json')));
  if (manifest.schemaVersion !== 1 || manifest.kind !== 'ptc-pipeline-materials' || manifest.runId !== runId
      || !/^[a-f0-9]{64}$/.test(manifest.pipelineCacheKey ?? '')) throw new Error('invalid frozen pipeline material manifest');
  const materials = suppliedMaterials ?? { runId, testItems: manifest.testItems, ...manifest.addressBook,
    pipelineCacheKey: manifest.pipelineCacheKey, ownerProfiles: manifest.ownerProfiles };
  if (materials.runId !== runId || !sameItems(materials.testItems, manifest.testItems)
      || materials.pipelineCacheKey !== manifest.pipelineCacheKey
      || !Array.isArray(testItems) || !testItems.length || new Set(testItems).size !== testItems.length
      || testItems.some(tm => !/^TM\d+$/.test(tm) || !manifest.testItems.includes(tm))
      || (sourceReview && !sameItems(testItems, manifest.testItems))) throw new Error('stage test items or material identity differ from frozen pipeline');
  for (const key of ['input', 'dftRoot', 'schematicRoot', 'trials', 'registerRoot', 'knowledgeRoot', 'programSourceRoot', 'profileRoots']) {
    if (JSON.stringify(materials[key]) !== JSON.stringify(manifest.addressBook?.[key])) throw new Error('stage address book differs from frozen pipeline');
  }
  const registryFile = assertSafeRunPath(root, path.join(runRoot, 'pipeline-registry.json'));
  const registryBytes = fs.readFileSync(registryFile);
  const registry = JSON.parse(registryBytes.toString('utf8'));
  const definition = registry.stages?.[stage];
  if (digest(registryBytes) !== registryDigest || !registry.stateMachine?.includes(stage) || !definition
      || (!sourceReview && definition.owner !== role) || (sourceReview && definition.owner !== 'captain') || definition.gate !== gate) {
    throw new Error('stage dispatch differs from frozen registry');
  }
  const profileId = manifest.ownerProfiles?.[role];
  if (!profileId || materials.ownerProfiles?.[role] !== profileId) throw new Error('missing frozen pipeline profile mapping');
  const profileRoot = assertSafeRunPath(root, path.resolve(root, materials.profileRoots?.[profileId] ?? ''));
  const relativeProfile = path.relative(path.join(runRoot, 'profiles'), profileRoot);
  if (!relativeProfile || relativeProfile.startsWith('..') || path.isAbsolute(relativeProfile)) throw new Error('profile is not a private snapshot');
  const instructionsFile = assertSafeRunPath(root, path.join(profileRoot, 'instructions.md'));
  const entries = manifest.files?.filter(entry => path.resolve(root, entry.snapshotPath) === instructionsFile) ?? [];
  const instructionsBytes = fs.readFileSync(instructionsFile);
  const profileSha256 = digest(instructionsBytes);
  if (entries.length !== 1 || entries[0].mutable || entries[0].sha256 !== profileSha256) throw new Error('frozen pipeline profile bytes differ');
  const instructions = new TextDecoder('utf-8', { fatal: true }).decode(instructionsBytes);
  return { runRoot, materials, registry, profileId, profileRoot, instructions, profileSha256, sourceReview };
}

/** One real generic stage child. Source parsers and compile remain host adapters. */
export function createPipelineDispatcher(ctx, workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const active = new Map();
  const toolIdleMs = options.toolIdleMs ?? 60_000;
  if (!Number.isFinite(toolIdleMs) || toolIdleMs <= 0 || toolIdleMs > 60_000) throw new Error('stage tool-idle budget must be within 60000 ms');
  return {
    async dispatch(request, materials) {
      const { runId, stage, owner: role, gate, registryDigest, testItems, signal } = request;
      if (!materials) throw new Error('missing frozen pipeline profile mapping');
      const bound = bindRequest(root, request, materials);
      const selection = resolveTrainingModelChoice(request.modelChoice, ctx.agentDefaultModel.currentSelection());
      const { runRoot, registry, profileId, profileRoot, instructions, profileSha256, sourceReview } = bound;
      const dispatchId = `${runId}:${stage}:${role}:1`;
      const receiptFile = path.join(runRoot, 'receipts', `${stage}-${role}.json`);
      const terminalFile = path.join(runRoot, 'receipts', `${stage}-${role}-terminal.json`);
      const lifecycleFile = path.join(runRoot, 'evidence', `${stage}-${role}-lifecycle.json`);
      if (active.has(dispatchId) || fs.existsSync(receiptFile)) throw new Error('stage dispatch already exists; recover its real receipt instead of repeating it');
      const agentOptions = { provider: selection.provider, model: selection.model,
        maxTokens: sourceReview ? 4096 : 8192 };
      const parentSessionId = `session-training-${runId}-${stage}-${role}`;
      const label = stageDispatchLabel(runId, stage, role);
      let receipt = { schemaVersion: 1, kind: 'ptc-training-stage', runId, stage, role, profileId, gate,
        testItems, dispatchId, registryDigest, label, parentSessionId, childSessionId: null,
        profileSha256, modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model,
        pipelineCacheKey: materials.pipelineCacheKey, createdAt: new Date().toISOString() };
      // Reserve this identity across dispatcher instances/processes. An atomic
      // replacement is safe for updates, but would overwrite another starter's
      // first receipt after an exists-check race.
      assertSafeRunPath(root, receiptFile);
      fs.mkdirSync(path.dirname(receiptFile), { recursive: true });
      try { fs.writeFileSync(receiptFile, JSON.stringify(signStageReceipt(receipt), null, 2) + '\n', { flag: 'wx' }); }
      catch (error) {
        if (error.code === 'EEXIST') throw new Error('stage dispatch already exists; recover its real receipt instead of repeating it');
        throw error;
      }
      const close = reason => {
        revokeStageDispatch(root, dispatchId);
        if (receipt.executionStatus === 'closed') return;
        const next = { ...receipt, executionStatus: 'closed', closeReason: reason, closedAt: new Date().toISOString() };
        atomic(root, receiptFile, signStageReceipt(next)); receipt = next;
      };
      const lifecycle = createTrainingLifecycle({ timeoutMs: options.timeoutMs ?? (sourceReview ? 180_000 : 300_000),
        onCancel: error => close(error.message),
        onEvent: (event, state) => atomic(root, lifecycleFile, { runId, dispatchId, event, ...state }),
      });
      const abort = () => lifecycle.cancel(signal?.reason ?? 'pipeline cancelled');
      signal?.addEventListener('abort', abort, { once: true });
      if (signal?.aborted) abort();
      const record = { lifecycle, childSessionId: null, timer: null,
        armToolDeadline() {
          clearTimeout(this.timer);
          this.timer = setTimeout(() => lifecycle.cancel(`no permitted stage tool started for ${toolIdleMs} ms`, { stopReason: 'timeout' }), toolIdleMs);
        } };
      active.set(dispatchId, record);
      try {
        const parent = await lifecycle.race(() => ctx.agents.create({ sessionId: parentSessionId,
          meta: { cwd: root, agentPreset: 'ate-ptc' }, agentOptions,
          setup: async agentCtx => { await ctx.agentPresets.mount(agentCtx, 'ate-ptc'); },
        }), { label: 'parent.create', disposeLate: value => value.dispose?.() });
        await lifecycle.race(() => parent.agent.whenIdle(), { label: 'parent.idle' });
        const child = await lifecycle.race(() => ctx.subagents.start('spawn', {
          label, parent: parent.agent, signal: lifecycle.signal, agentOptions,
          maxDepth: 1, toolFilter: { allow: sourceReview ? ['read'] : ['read', 'write'] },
          persona: `You are a frozen draft PTC TRAINING specialist, not a Captain.\n${instructions}\n\nNATIVE HOST OVERRIDE: use only the injected private run address book. Do not dispatch, advance, access production paths or run shell commands. The host independently executes the registry gate after your output is complete. Do not claim that host gate already passed. Return blocked for unsupported or conflicting source facts. Start the first permitted material tool promptly; the host cancels after 60 seconds without a tool start.`,
          prompt: [{ type: 'text', text: `Run ${runId}; stage ${stage}; owner ${role}; TMs ${testItems.join(', ')}.\nFrozen materials: ${JSON.stringify({ input: materials.input, dftRoot: materials.dftRoot, schematicRoot: materials.schematicRoot, trials: materials.trials, registerRoot: materials.registerRoot, knowledgeRoot: materials.knowledgeRoot, programSourceRoot: materials.programSourceRoot, profileRoot })}\nHost-computed SHA-256 facts (copy exact values; never guess): ${JSON.stringify(request.hostFacts ?? [])}\n${sourceReview
            ? `The host generated the seven schematic products under ${materials.schematicRoot} and checked them with the original deterministic schematic gate. This is a BOUNDED, read-only semantic review for EVERY assigned TM, not a second parser or exhaustive graph reconstruction. First read each assigned TM's ${materials.dftRoot}/<TM>/dft-conditions.yaml and extract involvedPins and power/measurement intent. Then read the small frozen confirmed source at ${materials.input.confirmed}, Path-Proofs.txt, schematic-receipt.json, and only relevant sections of SCH-Connect-Map.txt and Component-Statistic.txt. Compare three concrete facts: source-port identity/count, DUT Kelvin identity/count, and one relay path plus its ON/NC state for a pin ACTUALLY INVOLVED in the assigned TM. Do not choose an unrelated board-level path as the TM's evidence; a separate unrelated hazard may be reported as a warning, but not as this TM's contradiction unless the same electrical route or required state affects the TM. Apply the frozen project relay policy correctly: G6K pins 1/8 are coil, pins 2-7 are signal; default NC contact pairs are 2-3 and 7-6, SetOn pairs are 3-4 and 6-5. Compare relay states within the SAME route scenario: the same relay in different alternative routes is not by itself a contradiction. A confirmed TP-to-pin short establishes endpoint net equivalence, not a bypass of upstream relays. If you find simultaneous source attachment on the TM route, describe the exact net/pin chain and required states as a distinct safety concern; do not mislabel it as an ON/NC contradiction. In structured output, put exactly three short comparison findings with source/product line references in outputs; outputs are evidence, not file paths. Do not page through the entire CSV, reconstruct all nets, or read the multi-megabyte Path-Proofs.json; the host deterministic parser and gate already handle exhaustive structure and hashes. If a targeted CSV line is needed to resolve a contradiction, read only that bounded portion. Return structured done only if all three comparisons are supported without conflict; otherwise structured blocked with the exact missing fact or conflict. Use read-only tools, do not change products or input, do not run a gate yourself, and do not claim final host validation. Finish within the short review budget.`
            : `Write this stage's outputs for EVERY assigned TM under its trial directory. Stage contract outputs: ${JSON.stringify(registry.stages[stage].outputs)}. Host gate: ${gate}. Existing signed inputs must stay byte-identical. Implementation may edit only the private source copy, never the approved source original. Respond done only when all requested artifacts are ready for host validation; otherwise blocked with exact reason.`}` }],
          outputSchema: { type: 'object', properties: { status: { type: 'string', enum: ['done', 'blocked'] }, reason: { type: 'string' }, outputs: { type: 'array', items: { type: 'string' } } }, required: ['status'], additionalProperties: false },
        }), { label: 'child.start', disposeLate: value => { Promise.resolve(value.result).catch(() => {}); return value.dispose?.(); } });
        if (typeof child.id !== 'string' || !child.id) throw new Error('stage child has no bound session id');
        record.childSessionId = child.id;
        record.armToolDeadline();
        receipt = { ...receipt, childSessionId: child.id, dispatchedAt: new Date().toISOString() };
        atomic(root, receiptFile, signStageReceipt(receipt));
        const result = await lifecycle.race(child.result, { label: 'child.result', trackSettlement: true });
        const terminal = { schemaVersion: 1, kind: 'ptc-training-stage-terminal', runId, stage, gate, profileId, profileSha256,
          pipelineCacheKey: materials.pipelineCacheKey, dispatchId, registryDigest, role, testItems, childSessionId: child.id,
          modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model,
          status: result?.stopReason === 'completed' && result?.structured?.status === 'done'
            && (!sourceReview || hasSourceReviewEvidence(result)) ? 'done' : 'blocked',
          result, finishedAt: new Date().toISOString() };
        atomic(root, terminalFile, signStageReceipt(terminal));
        return terminal;
      } catch (error) {
        lifecycle.cancel(error);
        const terminal = { schemaVersion: 1, kind: 'ptc-training-stage-terminal', runId, stage, gate, profileId, profileSha256,
          pipelineCacheKey: materials.pipelineCacheKey, dispatchId, registryDigest, role, testItems, childSessionId: receipt.childSessionId, status: 'blocked',
          modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model,
          stopReason: error instanceof TrainingCancellationError ? error.stopReason : 'error', reason: error.message };
        atomic(root, terminalFile, signStageReceipt(terminal));
        return terminal;
      } finally {
        clearTimeout(record.timer);
        active.delete(dispatchId); signal?.removeEventListener('abort', abort);
        try { close('stage child finished'); } finally { lifecycle.close(); }
      }
    },
    recover(request) {
      const role = request.owner;
      const { runRoot, profileId, profileSha256, materials } = bindRequest(root, request);
      const file = assertSafeRunPath(root, path.join(runRoot, 'receipts', `${request.stage}-${role}-terminal.json`));
      const terminal = readJson(file);
      const receipt = readJson(assertSafeRunPath(root, path.join(runRoot, 'receipts', `${request.stage}-${role}.json`)));
      const runState = readJson(assertSafeRunPath(root, path.join(runRoot, 'state.json')));
      if (receipt.modelChoice !== (runState.modelChoice ?? 'default')
          || terminal.modelChoice !== receipt.modelChoice
          || terminal.modelProvider !== receipt.modelProvider || terminal.modelName !== receipt.modelName
          || typeof receipt.modelProvider !== 'string' || typeof receipt.modelName !== 'string') {
        throw new Error('unbound stage terminal model selection');
      }
      // Recovery returns an observed terminal, never a synthetic successful run.
      const signed = signStageReceipt(terminal);
      if (signed.digest !== terminal.digest || receipt.digest !== signStageReceipt(receipt).digest || receipt.executionStatus !== 'closed'
          || receipt.kind !== 'ptc-training-stage' || receipt.dispatchId !== terminal.dispatchId || receipt.childSessionId !== terminal.childSessionId
          || receipt.registryDigest !== request.registryDigest || receipt.runId !== request.runId || receipt.role !== role
          || receipt.stage !== request.stage || receipt.gate !== request.gate || receipt.profileId !== profileId
          || receipt.profileSha256 !== profileSha256 || receipt.pipelineCacheKey !== materials.pipelineCacheKey
          || !sameItems(receipt.testItems, terminal.testItems)
          || terminal.schemaVersion !== 1 || terminal.kind !== 'ptc-training-stage-terminal'
          || terminal.stage !== request.stage || terminal.gate !== request.gate || terminal.profileId !== profileId
          || terminal.profileSha256 !== profileSha256 || terminal.pipelineCacheKey !== materials.pipelineCacheKey
          || (terminal.status !== 'done' && terminal.status !== 'blocked')
          || (terminal.status === 'done' && (!terminal.childSessionId || terminal.result?.stopReason !== 'completed'
            || terminal.result?.structured?.status !== 'done'
            || (request.stage === 'INPUT_SYNC' && !hasSourceReviewEvidence(terminal.result))))
          || terminal.runId !== request.runId || terminal.registryDigest !== request.registryDigest
          || terminal.role !== role || terminal.dispatchId !== `${request.runId}:${request.stage}:${role}:1`
          || JSON.stringify(terminal.testItems) !== JSON.stringify(request.testItems)) throw new Error('unbound stage terminal receipt');
      return terminal;
    },
    noteToolStart(exec) {
      if (!['read', 'write'].includes(exec.name)) return;
      for (const record of active.values()) {
        if (record.childSessionId && record.childSessionId === exec.agent?.id) record.armToolDeadline();
      }
    },
    shutdown() { for (const record of active.values()) record.lifecycle.cancel('native plugin stopped'); },
  };
}
