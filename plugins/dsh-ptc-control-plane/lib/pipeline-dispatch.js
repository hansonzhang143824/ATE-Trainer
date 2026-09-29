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
function snapshotProfileDigest(root, manifest, profileRoot) {
  const files = (manifest.files ?? []).filter(entry => {
    const file = path.resolve(root, entry.snapshotPath);
    return file !== profileRoot && file.startsWith(`${profileRoot}${path.sep}`) && path.basename(file) !== 'agent-manifest.json' && path.basename(file) !== 'status.json';
  }).map(entry => ({ path: path.relative(profileRoot, path.resolve(root, entry.snapshotPath)).split(path.sep).join('/'), bytes: entry.size, sha256: entry.sha256 }))
    .sort((a, b) => a.path.localeCompare(b.path));
  return digest(Buffer.from(`${JSON.stringify(files, null, 2)}\n`, 'utf8'));
}

const sameItems = (a, b) => Array.isArray(a) && Array.isArray(b)
  && JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());

function boundedText(root, file, maxBytes = 12000) {
  const safe = assertSafeRunPath(root, file);
  const bytes = fs.readFileSync(safe);
  return new TextDecoder('utf-8', { fatal: false }).decode(bytes.subarray(0, maxBytes));
}

function boundedTextOrNotice(root, file, maxBytes = 12000) {
  try { return boundedText(root, file, maxBytes); }
  catch (error) { return `[host evidence unavailable: ${path.basename(file)} (${error.code ?? error.message})]`; }
}

function lineWindow(text, predicate, before = 1, after = 2, limit = 24) {
  const lines = text.split(/\r?\n/);
  const selected = new Set();
  for (let index = 0; index < lines.length && selected.size < limit; index += 1) {
    if (!predicate(lines[index])) continue;
    for (let offset = Math.max(0, index - before); offset <= Math.min(lines.length - 1, index + after); offset += 1) selected.add(offset);
  }
  return [...selected].sort((a, b) => a - b).map(index => `L${index + 1}: ${lines[index]}`).join('\n');
}

function extractReviewPins(conditionText) {
  const pins = new Set();
  // Only consume structured condition fields. A broad key/value regex would
  // mistake valid YAML values such as `V`, `true`, and `false` for board pins,
  // causing the route window to start at unrelated ACDRV/AGND lines.
  for (const match of conditionText.matchAll(/(?:^|\n)\s*(?:involvedPins|vsetPins|dynamicPins):\s*\[([^\]]*)\]/gim)) {
    for (const value of match[1].matchAll(/['\"]?([A-Za-z][A-Za-z0-9_]*)['\"]?/g)) pins.add(value[1]);
  }
  for (const match of conditionText.matchAll(/(?:^|\n)\s*(?:pin|measurement|logicalCheck):\s*['\"]?([A-Za-z][A-Za-z0-9_]*)/gim)) {
    pins.add(match[1]);
  }
  return [...pins].filter(pin => !/^(?:true|false|null|v|a|r|f)$/i.test(pin));
}

// The schematic map contains many board-level routes before the route that a
// DFT item actually exercises.  A first-match window can therefore hide the
// assigned pin's relay state behind unrelated ACDRV/AGND paths.  Collect
// route-shaped lines for the assigned endpoints across the whole map, keeping
// a small neighbourhood so the model receives both the header and its F/S
// legs.  This remains bounded and is still only host-generated evidence.
function routeWindow(text, endpointRe, limit = 48) {
  const lines = text.split(/\r?\n/);
  const selected = new Set();
  const routeShape = /(?:->|←|↔|Relay-|需闭合|Kelvin)/;
  for (let index = 0; index < lines.length; index += 1) {
    if (!endpointRe.test(lines[index]) || !routeShape.test(lines[index])) continue;
    for (let offset = Math.max(0, index - 1); offset <= Math.min(lines.length - 1, index + 2); offset += 1) {
      selected.add(offset);
      if (selected.size >= limit) break;
    }
    if (selected.size >= limit) break;
  }
  return [...selected].sort((a, b) => a - b).map(index => `L${index + 1}: ${lines[index]}`).join('\n');
}

function buildSchematicReviewFacts(root, materials, testItems) {
  const schematicRoot = path.resolve(root, materials.schematicRoot);
  const dftRoot = path.resolve(root, materials.dftRoot);
  const component = boundedTextOrNotice(root, path.join(schematicRoot, 'Component-Statistic.txt'), 36000);
  const connect = boundedTextOrNotice(root, path.join(schematicRoot, 'SCH-Connect-Map.txt'), 80000);
  const proof = boundedTextOrNotice(root, path.join(schematicRoot, 'Path-Proofs.txt'), 4000);
  const conditions = testItems.map(tm => ({
    tm,
    text: boundedTextOrNotice(root, path.join(dftRoot, tm, 'dft-conditions.yaml'), 9000),
  }));
  const involved = new Set();
  for (const item of conditions) {
    for (const pin of extractReviewPins(item.text)) involved.add(pin);
  }
  // Keep a useful bounded review if a malformed/legacy condition file has no
  // structured pin field; this fallback is explicit rather than inferred from
  // arbitrary scalar values.
  if (!involved.size) involved.add('VAC2');
  const tokenRe = new RegExp([...involved].map(token => token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'i');
  return {
    purpose: 'host-bounded-schematic-semantic-review',
    conditions,
    // Keep the semantic child focused on the three contract facts. The full
    // maps remain frozen on disk and are independently gate-validated; sending
    // dozens of alternative routes here causes long-model reasoning to
    // enumerate unrelated scenarios before it submits its structured review.
    sourcePortAndDutCounts: lineWindow(component, line => /任务一: DUT PIN|任务二: 源表|Kelvin \(|Non-Kelvin \(/.test(line), 0, 1, 12),
    relayPathsForAssignedPins: routeWindow(connect, tokenRe, 16),
    pathProofSummary: lineWindow(proof, line => /^(status|sources|raw_best_paths|accepted_path_proofs|kelvin_pairs|issues)=/.test(line), 0, 0, 6),
  };
}
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
      || JSON.stringify(materials.workflowBinding ?? null) !== JSON.stringify(manifest.workflowBinding ?? null)
      || JSON.stringify(materials.profileRevisions ?? {}) !== JSON.stringify(manifest.profileRevisions ?? {})
      || JSON.stringify(materials.profileDigests ?? {}) !== JSON.stringify(manifest.profileDigests ?? {})
      || !Array.isArray(testItems) || !testItems.length || new Set(testItems).size !== testItems.length
      || testItems.some(tm => !/^TM\d+$/.test(tm) || !manifest.testItems.includes(tm))
      || (sourceReview && !sameItems(testItems, manifest.testItems))) throw new Error('stage test items or material identity differ from frozen pipeline');
  for (const key of ['input', 'dftRoot', 'schematicRoot', 'trials', 'registerRoot', 'knowledgeRoot', 'libraryRoot', 'programSourceRoot', 'profileRoots', 'workflowBinding', 'profileRevisions', 'profileDigests']) {
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
  const workflowStep = manifest.workflowBinding?.steps?.find(step => step.role === role);
  const expectedWorkflowRevision = manifest.profileRevisions?.[role] && manifest.profileRevisions[role] !== 'draft'
    ? manifest.profileRevisions[role] : null;
  if (manifest.workflowBinding && (!workflowStep || workflowStep.profileId !== profileId
      || (workflowStep.profileRevision ?? null) !== expectedWorkflowRevision)) {
    throw new Error('workflow step binding differs from frozen Agent mapping');
  }
  const profileRoot = assertSafeRunPath(root, path.resolve(root, materials.profileRoots?.[profileId] ?? ''));
  const relativeProfile = path.relative(path.join(runRoot, 'profiles'), profileRoot);
  if (!relativeProfile || relativeProfile.startsWith('..') || path.isAbsolute(relativeProfile)) throw new Error('profile is not a private snapshot');
  const instructionsFile = assertSafeRunPath(root, path.join(profileRoot, 'instructions.md'));
  const entries = manifest.files?.filter(entry => path.resolve(root, entry.snapshotPath) === instructionsFile) ?? [];
  const instructionsBytes = fs.readFileSync(instructionsFile);
  const profileSha256 = digest(instructionsBytes);
  if (entries.length !== 1 || entries[0].mutable || entries[0].sha256 !== profileSha256) throw new Error('frozen pipeline profile bytes differ');
  const profileDigest = snapshotProfileDigest(root, manifest, profileRoot);
  if (materials.profileDigests?.[role] && materials.profileDigests[role] !== profileDigest) throw new Error('frozen pipeline profile content digest differs');
  const profileRevision = materials.profileRevisions?.[role] ?? null;
  const instructions = new TextDecoder('utf-8', { fatal: true }).decode(instructionsBytes);
  return { runRoot, materials, registry, profileId, profileRevision, profileDigest, profileRoot, instructions, profileSha256, sourceReview };
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
      const { runRoot, registry, profileId, profileRevision, profileDigest, profileRoot, instructions, profileSha256, sourceReview } = bound;
      const dispatchId = `${runId}:${stage}:${role}:1`;
      const receiptFile = path.join(runRoot, 'receipts', `${stage}-${role}.json`);
      const terminalFile = path.join(runRoot, 'receipts', `${stage}-${role}-terminal.json`);
      const lifecycleFile = path.join(runRoot, 'evidence', `${stage}-${role}-lifecycle.json`);
      if (active.has(dispatchId) || fs.existsSync(receiptFile)) throw new Error('stage dispatch already exists; recover its real receipt instead of repeating it');
      // The semantic packet only requires three cited findings.  Keep the
      // response bounded so the business model cannot spend the whole stage
      // budget generating an unnecessary narrative.
      // DeepSeek V4 tends to include a longer evidence-by-evidence rationale
      // before its structured verdict.  Give that explicitly selected,
      // real-business model enough room to submit the verdict; keep the
      // default model's bounded 2048 contract unchanged.
      const agentOptions = { provider: selection.provider, model: selection.model,
        maxTokens: sourceReview && selection.choice === 'deepseek-v4-flash' ? 8192 : sourceReview ? 2048 : 8192 };
      // A semantic review that stops only because the provider exhausted its
      // output budget is recoverable.  Give that one case a single larger
      // retry; all other incomplete/blocked results remain fail-closed.
      const sourceReviewRetryTokens = sourceReview ? 16384 : agentOptions.maxTokens;
      const maxReviewAttempts = sourceReview ? 2 : 1;
      const parentSessionId = `session-training-${runId}-${stage}-${role}`;
      const label = stageDispatchLabel(runId, stage, role);
      let receipt = { schemaVersion: 1, kind: 'ptc-training-stage', runId, stage, role, profileId, gate,
        testItems, dispatchId, registryDigest, label, parentSessionId, childSessionId: null,
        profileSha256, profileRevision, profileDigest, modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model,
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
      // A real schematic semantic review is a model-backed business step.  The
      // bounded evidence packet prevents unbounded tool work, but the model
      // still needs enough wall-clock time to inspect the packet and produce
      // the three cited findings.  Keep the shorter historical default for
      // callers that explicitly pass timeoutMs (tests and controlled embeds),
      // while giving the production business path a bounded five-minute
      // budget.  The enclosing pipeline has an eight-minute dispatch budget,
      // so this leaves room for the subsequent DFT model call.
      const lifecycle = createTrainingLifecycle({ timeoutMs: options.timeoutMs ?? (sourceReview ? 300_000 : 300_000),
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
      let reviewAttempts = 0;
      let retriedAfterMaxTokens = false;
      const reviewAttemptLog = [];
      try {
        const parent = await lifecycle.race(() => ctx.agents.create({ sessionId: parentSessionId,
          meta: { cwd: root, agentPreset: 'ate-ptc' }, agentOptions,
          setup: async agentCtx => { await ctx.agentPresets.mount(agentCtx, 'ate-ptc'); },
        }), { label: 'parent.create', disposeLate: value => value.dispose?.() });
        await lifecycle.race(() => parent.agent.whenIdle(), { label: 'parent.idle' });
        const schematicReviewFacts = sourceReview ? buildSchematicReviewFacts(root, materials, testItems) : null;
        const promptText = `Run ${runId}; stage ${stage}; owner ${role}; TMs ${testItems.join(', ')}.\nFrozen materials: ${JSON.stringify({ input: materials.input, dftRoot: materials.dftRoot, schematicRoot: materials.schematicRoot, trials: materials.trials, registerRoot: materials.registerRoot, knowledgeRoot: materials.knowledgeRoot, programSourceRoot: materials.programSourceRoot, profileRoot })}\nHost-computed SHA-256 facts (copy exact values; never guess): ${JSON.stringify(request.hostFacts ?? [])}\n${sourceReview
            ? `The host generated the seven schematic products under ${materials.schematicRoot} and checked them with the original deterministic schematic gate. This is a BOUNDED semantic review for EVERY assigned TM, not a second parser or exhaustive graph reconstruction. No tools are available in this review; use only the following host-generated evidence packet and the frozen DFT conditions. Do not run a gate yourself; the host performs final validation after your structured response. Compare three concrete facts: source-port identity/count, DUT Kelvin identity/count, and one relay path plus its ON/NC state for a pin ACTUALLY INVOLVED in the assigned TM. Do not choose an unrelated board-level path as the TM's evidence; a separate unrelated hazard may be reported as a warning, but not as this TM's contradiction unless the same electrical route or required state affects the TM. Apply the frozen project relay policy correctly: G6K pins 1/8 are coil, pins 2-7 are signal; default NC contact pairs are 2-3 and 7-6, SetOn pairs are 3-4 and 6-5. Compare relay states within the SAME route scenario: the same relay in different alternative routes is not by itself a contradiction. A confirmed TP-to-pin short establishes endpoint net equivalence, not a bypass of upstream relays. CRITICAL RESPONSE BUDGET: do not emit a reasoning narrative, enumerate names, or perform field-by-field arithmetic. Trust the host-declared counts and compare only the supplied line windows. Call structured_output as the next action after reading the packet. Put exactly three concise findings (each <=240 characters) with source/product line references in outputs; outputs are findings, not file paths. Keep reason <=800 characters. Return structured done only if all three comparisons are supported without conflict; otherwise structured blocked with the exact missing fact or conflict. Do not claim final host validation. Host evidence packet: ${JSON.stringify(schematicReviewFacts)}`
            : `Write this stage's outputs for EVERY assigned TM under its trial directory. Stage contract outputs: ${JSON.stringify(registry.stages[stage].outputs)}. Host gate: ${gate}. Existing signed inputs must stay byte-identical. Implementation may edit only the private source copy, never the approved source original. Respond done only when all requested artifacts are ready for host validation; otherwise blocked with exact reason.`}`;
        let child = null;
        let result = null;
        for (let attempt = 1; attempt <= maxReviewAttempts; attempt += 1) {
          reviewAttempts = attempt;
          const attemptOptions = attempt === 1 ? agentOptions : { ...agentOptions, maxTokens: sourceReviewRetryTokens };
          const attemptPrompt = attempt === 1 ? promptText : `${promptText}\nRETRY: the previous attempt reached the output token limit before structured_output. Do not repeat analysis; call structured_output immediately with exactly three concise findings and a short reason.`;
          // The descriptor label is part of the signed stage-authority binding.
          // Keep it identical to the receipt label on every attempt.  Attempt
          // numbers belong in lifecycle/evidence metadata; adding a suffix here
          // makes the host guard see a different stage identity and reject every
          // child tool call before its payload can run.
          child = await lifecycle.race(() => ctx.subagents.start('spawn', {
            label, parent: parent.agent, signal: lifecycle.signal, agentOptions: attemptOptions,
            // Schematic review receives a bounded, host-generated evidence
            // packet. It is deliberately tool-free so the review cannot hang on
            // a missing parent read tool; host products remain immutable and the
            // stage gate still verifies every byte independently.
            maxDepth: 1, toolFilter: { allow: sourceReview ? [] : ['read', 'write'] },
            persona: `You are a frozen draft PTC TRAINING specialist, not a Captain.\n${instructions}\n\nNATIVE HOST OVERRIDE: use only the injected private run address book. Do not dispatch, advance, access production paths or run shell commands. The host independently executes the registry gate after your output is complete. Do not claim that host gate already passed. Return blocked for unsupported or conflicting source facts. ${sourceReview ? 'No tools are available for this bounded semantic review; reason only from the host-generated evidence packet.' : 'Start the first permitted material tool promptly; the host cancels after 60 seconds without a tool start.'}`,
            prompt: [{ type: 'text', text: attemptPrompt }],
            outputSchema: { type: 'object', properties: { status: { type: 'string', enum: ['done', 'blocked'] }, reason: { type: 'string' }, outputs: { type: 'array', items: { type: 'string' } } }, required: ['status'], additionalProperties: false },
          }), { label: `child.start.attempt-${attempt}`, disposeLate: value => { Promise.resolve(value.result).catch(() => {}); return value.dispose?.(); } });
          if (typeof child.id !== 'string' || !child.id) throw new Error('stage child has no bound session id');
          record.childSessionId = child.id;
          if (!sourceReview) record.armToolDeadline();
          receipt = { ...receipt, childSessionId: child.id, dispatchedAt: new Date().toISOString(), reviewAttempts, retriedAfterMaxTokens };
          atomic(root, receiptFile, signStageReceipt(receipt));
          result = await lifecycle.race(child.result, { label: `child.result.attempt-${attempt}`, trackSettlement: true });
          reviewAttemptLog.push({ attempt, childSessionId: child.id, stopReason: result?.stopReason ?? null, maxTokens: attemptOptions.maxTokens });
          receipt = { ...receipt, reviewAttempts, retriedAfterMaxTokens, reviewAttemptLog };
          atomic(root, receiptFile, signStageReceipt(receipt));
          const stopReason = String(result?.stopReason ?? '').toLowerCase();
          const budgetExhausted = ['max-tokens', 'max_tokens', 'length'].includes(stopReason);
          if (!(sourceReview && budgetExhausted && attempt < maxReviewAttempts)) break;
          retriedAfterMaxTokens = true;
          child.dispose?.();
        }
        const status = result?.stopReason === 'completed' && result?.structured?.status === 'done'
          && (!sourceReview || hasSourceReviewEvidence(result)) ? 'done' : 'blocked';
        const reason = status === 'blocked'
          ? (result?.structured?.reason ?? `${sourceReview ? 'semantic review child' : 'stage child'} stopped: ${result?.stopReason ?? 'unknown'}`)
          : undefined;
        const terminal = { schemaVersion: 1, kind: 'ptc-training-stage-terminal', runId, stage, gate, profileId, profileRevision, profileDigest, profileSha256,
          pipelineCacheKey: materials.pipelineCacheKey, dispatchId, registryDigest, role, testItems, childSessionId: child.id,
          modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model, reviewAttempts, retriedAfterMaxTokens, reviewAttemptLog,
          status, stopReason: result?.stopReason ?? null, ...(reason ? { reason } : {}),
          result, finishedAt: new Date().toISOString() };
        atomic(root, terminalFile, signStageReceipt(terminal));
        return terminal;
      } catch (error) {
        lifecycle.cancel(error);
        const terminal = { schemaVersion: 1, kind: 'ptc-training-stage-terminal', runId, stage, gate, profileId, profileRevision, profileDigest, profileSha256,
          pipelineCacheKey: materials.pipelineCacheKey, dispatchId, registryDigest, role, testItems, childSessionId: receipt.childSessionId, status: 'blocked',
          modelChoice: selection.choice, modelProvider: selection.provider, modelName: selection.model, reviewAttempts, retriedAfterMaxTokens, reviewAttemptLog,
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
      const { runRoot, profileId, profileRevision, profileDigest, profileSha256, materials } = bindRequest(root, request);
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
          || terminal.profileRevision !== profileRevision || terminal.profileDigest !== profileDigest
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
