import fs from 'node:fs';
import path from 'node:path';
import { isDeepStrictEqual } from 'node:util';
import { createTrainingLifecycle } from './training-lifecycle.js';
import { createRunStore, frameworkId, frameworkSha } from './trainer-run-events.js';

const terminal = new Set(['completed', 'failed', 'cancelled', 'interrupted']);
const clone = value => structuredClone(value);
const errorInfo = error => ({ code: error.code ?? 'FRAMEWORK_EXECUTION_FAILED', message: String(error.message ?? error), details: error.details ?? null });
function fail(code, message, details) { throw Object.assign(new Error(message), { code, details }); }
function freeze(value) {
  if (value && typeof value === 'object') { Object.freeze(value); Object.values(value).forEach(freeze); }
  return value;
}
function pointerParts(pointer) {
  if (pointer === '') return [];
  if (typeof pointer !== 'string' || !pointer.startsWith('/') || /~(?![01])/.test(pointer)) fail('INPUT_BINDING_INVALID', 'invalid JSON Pointer', { pointer });
  const parts = pointer.slice(1).split('/').map(part => part.replace(/~1/g, '/').replace(/~0/g, '~'));
  if (parts.some(part => ['__proto__', 'constructor', 'prototype'].includes(part))) fail('INPUT_BINDING_INVALID', 'unsafe JSON Pointer', { pointer });
  return parts;
}
export function readFrameworkPointer(value, pointer) {
  let current = value;
  for (const part of pointerParts(pointer)) {
    if (!current || typeof current !== 'object' || !Object.hasOwn(current, part)) fail('INPUT_BINDING_MISSING', 'input binding field is missing', { pointer, field: part });
    current = current[part];
  }
  return clone(current);
}
export function resolveFrameworkInput(step, input, completed) {
  const bindings = step.inputBindings ?? {};
  if (!Object.keys(bindings).length) return clone(input);
  if (Object.hasOwn(bindings, '') && Object.keys(bindings).length !== 1) fail('INPUT_BINDING_INVALID', 'root binding cannot overlap other destinations');
  let result = {};
  for (const [destination, binding] of Object.entries(bindings)) {
    let value;
    if (binding.source === 'literal') value = clone(binding.value);
    else if (binding.source === 'input') value = readFrameworkPointer(input, binding.pointer ?? '');
    else if (binding.source === 'step') {
      if (!completed.has(binding.stepId)) fail('INPUT_BINDING_MISSING', 'upstream step has not completed', { stepId: binding.stepId });
      value = readFrameworkPointer(completed.get(binding.stepId), binding.pointer ?? '');
    } else fail('INPUT_BINDING_INVALID', 'unknown input binding source');
    const parts = pointerParts(destination);
    if (!parts.length) { result = value; continue; }
    let cursor = result;
    for (const part of parts.slice(0, -1)) {
      if (!cursor || typeof cursor !== 'object') fail('INPUT_BINDING_INVALID', 'overlapping input bindings');
      if (!Object.hasOwn(cursor, part)) cursor[part] = {};
      cursor = cursor[part];
    }
    if (!cursor || typeof cursor !== 'object' || Object.hasOwn(cursor, parts.at(-1))) fail('INPUT_BINDING_INVALID', 'overlapping input bindings');
    cursor[parts.at(-1)] = value;
  }
  return result;
}
/** Only the declared output projection is visible to downstream step bindings.
 * Use the same JSON Pointer and overlap checks as input mapping; keep the
 * original model response separate so mapping never rewrites model evidence. */
export function resolveFrameworkOutput(step, output) {
  const bindings = step.outputBindings ?? {};
  const inputBindings = Object.fromEntries(Object.entries(bindings).map(([destination, binding]) => {
    if (binding?.source !== 'output' || typeof binding.pointer !== 'string') {
      fail('OUTPUT_BINDING_INVALID', 'output binding requires an output source and JSON Pointer');
    }
    return [destination, { source: 'input', pointer: binding.pointer }];
  }));
  try { return resolveFrameworkInput({ inputBindings }, output, new Map()); }
  catch (error) {
    if (error.code?.startsWith('INPUT_BINDING_')) {
      error.code = error.code.replace('INPUT_BINDING_', 'OUTPUT_BINDING_');
      error.message = error.message.replace(/input binding/g, 'output binding');
    }
    throw error;
  }
}
function controls(run) {
  const unfinished = !terminal.has(run.status);
  const more = run.steps.filter(step => step.status === 'pending').length > 0;
  const options = {
    pause: [run.status === 'running' && more, more ? 'Pause after the current step' : 'No later step to pause'],
    resume: [run.status === 'paused', 'Only a paused run can resume'],
    stop: [unfinished && run.status !== 'stopping', 'Run is terminal or already stopping'],
  };
  return Object.fromEntries(Object.entries(options).map(([key, [allowed, reason]]) => [key, { allowed, reason: allowed ? null : reason }]));
}

/** Only resolved bundles enter this runner. Production validation is B-owned;
 * explicit injected validators are useful for adapter unit tests, never a fallback. */
export function createFrameworkRunner({ workspaceRoot, adapter, now = () => new Date().toISOString(), verifyBundle, validateJson }) {
  if (typeof adapter?.dispatch !== 'function') throw new Error('framework adapter is required');
  const store = createRunStore(workspaceRoot);
  const live = new Map();
  const readRun = ({ runId }) => {
    const dir = store.locate(runId);
    const record = store.read(dir);
    const bytes = fs.readFileSync(store.safe(path.join(dir, 'execution-bundle.json')));
    if (record.bundleArtifact?.sha256 !== frameworkSha(bytes)) fail('RUN_BUNDLE_CHANGED', 'stored run bundle bytes changed');
    const bundle = JSON.parse(bytes);
    if (bundle.bundleSha256 !== record.bundleSha256) fail('RUN_BUNDLE_CHANGED', 'stored run bundle identity changed');
    return { ...record, bundle, controls: controls(record) };
  };
  function save(entry) {
    entry.run.updatedAt = now();
    entry.run.controls = controls(entry.run);
    store.write(entry.dir, 'framework-run.json', entry.run);
  }
  function event(entry, type, details = {}) {
    const item = { ...details, seq: ++entry.seq, runId: entry.run.runId, at: now(), type, status: entry.run.status };
    store.append(entry.dir, item);
    entry.run.lastEvent = item;
    save(entry);
  }
  function childEvent(entry, step, observed) {
    // Adapter observations are a narrow projection, not raw provider logs.
    const details = { stepId: step.stepId, source: 'adapter' };
    for (const name of ['phase', 'childSessionId', 'parentSessionId', 'hostSubagentRunId', 'toolId', 'toolName', 'summary', 'childTerminationConfirmed', 'disposalStatus', 'effectiveTools', 'toolSchemasSha256']) {
      if (observed[name] !== undefined) details[name] = clone(observed[name]);
    }
    if (observed.effectiveTools) { step.effectiveTools = clone(observed.effectiveTools); step.toolSchemasSha256 = observed.toolSchemasSha256; }
    if (observed.childTerminationConfirmed === true) {
      step.childTerminationConfirmed = true;
      entry.run.childTerminationConfirmed = true;
      if (entry.run.status === 'stopping') finishCancellation(entry);
    }
    event(entry, observed.type ?? 'observation', details);
  }
  function finishCancellation(entry) {
    if (entry.run.cancellationRequested && entry.run.childTerminationConfirmed === true) {
      entry.run.status = entry.timedOut ? 'failed' : 'cancelled';
      entry.run.completedAt = now();
      const current = entry.run.steps.find(step => step.status === 'running');
      if (current) { current.status = entry.timedOut ? 'failed' : 'cancelled'; current.completedAt = now(); }
      save(entry);
    }
  }
  async function validate(entry, reference, value, phase, stepId) {
    const files = Object.fromEntries(entry.bundle.files.map(file => [file.path, file.content]));
    if (!Object.hasOwn(files, reference)) fail('BUNDLE_DEPENDENCY_MISSING', 'schema missing from execution bundle', { reference });
    const schema = JSON.parse(files[reference]);
    const result = await entry.validateJson(schema, value, { files, schemaRef: reference });
    if (!result?.ok) fail('SCHEMA_VALIDATION_FAILED', `${phase} contract failed`, { stepId, phase, errors: result?.errors ?? [] });
    return result;
  }
  async function execute(entry) {
    const run = entry.run;
    const completed = new Map();
    try {
      run.status = 'preparing'; event(entry, 'preparing', { phase: 'bundle' });
      for (let index = 0; index < entry.bundle.steps.length; index++) {
        if (run.cancellationRequested) break;
        if (entry.pauseRequested) {
          run.status = 'paused'; event(entry, 'paused', { phase: 'step-boundary' });
          await new Promise(resolve => { entry.resume = resolve; });
          entry.resume = null;
          if (run.cancellationRequested) break;
        }
        const definition = entry.bundle.steps[index];
        const step = run.steps[index];
        run.status = 'running';
        step.input = resolveFrameworkInput(definition, entry.input, completed);
        step.inputValidation = await validate(entry, definition.inputSchemaRef, step.input, 'input', step.stepId);
        if (run.cancellationRequested) break;
        step.inputArtifact = store.write(entry.dir, `${step.stepId}.input.json`, step.input, true);
        const refs = new Set([definition.instructionsRef, definition.inputSchemaRef, definition.outputSchemaRef, definition.processRef, ...(definition.scriptRefs ?? [])].filter(Boolean));
        for (const skillId of definition.skillRefs ?? []) {
          const skill = entry.bundle.skills?.[skillId];
          if (!skill) fail('BUNDLE_DEPENDENCY_MISSING', 'skill missing', { skillId });
          [skill.entryRef, ...(skill.referenceRefs ?? []), ...(skill.scriptRefs ?? [])].forEach(ref => refs.add(ref));
        }
        for (const toolId of definition.toolIds ?? []) {
          const tool = entry.bundle.tools?.[toolId];
          if (!tool) fail('BUNDLE_DEPENDENCY_MISSING', 'tool missing', { toolId });
          refs.add(tool.scriptRef);
        }
        step.actualLoadedRefs = [...refs].map(ref => {
          const file = entry.bundle.files.find(file => file.path === ref);
          if (!file) fail('BUNDLE_DEPENDENCY_MISSING', 'execution asset missing', { ref });
          return { path: ref, sha256: file.sha256, size: file.size };
        });
        step.status = 'running'; step.startedAt = now();
        step.model = clone(definition.model ?? entry.bundle.model);
        run.childTerminationConfirmed = null;
        event(entry, 'dispatching', { stepId: step.stepId, phase: 'dispatch' });
        const lifecycle = createTrainingLifecycle({ timeoutMs: definition.timeoutMs ?? 300000,
          onCancel(error) {
            entry.timedOut = error.stopReason === 'timeout';
            run.cancellationRequested = true;
            run.childTerminationConfirmed = false;
            run.status = 'stopping';
            run.error = errorInfo(error);
            event(entry, 'cancellation-requested', { stepId: step.stepId, phase: 'stopping' });
          },
        });
        entry.lifecycle = lifecycle;
        entry.rawPending = true;
        const raw = Promise.resolve().then(() => {
          if (lifecycle.signal.aborted) return { cancelledBeforeDispatch: true, childTerminationConfirmed: true };
          return adapter.dispatch({ runId: run.runId, step: definition, bundle: entry.bundle, input: clone(step.input), signal: lifecycle.signal,
            onStart(identity) {
              if (!identity?.childSessionId) fail('CHILD_IDENTITY_MISSING', 'adapter supplied no child identity');
              step.childSessionId = identity.childSessionId;
              step.parentSessionId = identity.parentSessionId ?? null;
              step.childTerminationConfirmed = false;
              run.childTerminationConfirmed = false;
              event(entry, 'child-started', { ...identity, stepId: step.stepId, phase: 'waiting-model' });
            },
            onEvent: observation => childEvent(entry, step, observation),
          });
        });
        raw.then(result => {
          entry.rawPending = false;
          if (result?.childTerminationConfirmed === true) { step.childTerminationConfirmed = true; run.childTerminationConfirmed = true; }
          finishCancellation(entry);
          if (run.cancellationRequested) event(entry, 'late-settlement', { stepId: step.stepId, phase: 'cleanup', childTerminationConfirmed: run.childTerminationConfirmed });
          if (entry.finished && run.childTerminationConfirmed === true) live.delete(run.runId);
        }, error => {
          entry.rawPending = false;
          if (error.childTerminationConfirmed === true) { step.childTerminationConfirmed = true; run.childTerminationConfirmed = true; }
          finishCancellation(entry);
          if (run.cancellationRequested) event(entry, 'late-settlement', { stepId: step.stepId, phase: 'cleanup', childTerminationConfirmed: run.childTerminationConfirmed });
          if (entry.finished && run.childTerminationConfirmed === true) live.delete(run.runId);
        }).catch(() => {});
        let result;
        try { result = await lifecycle.race(raw, { label: 'framework.child', trackSettlement: true }); }
        finally { lifecycle.close(); entry.lifecycle = null; }
        if (run.cancellationRequested) break;
        if (!step.childSessionId || result.childSessionId !== step.childSessionId) fail('CHILD_IDENTITY_MISMATCH', 'child result identity differs from start');
        if (result.stopReason && result.stopReason !== 'completed') fail('MODEL_EXECUTION_FAILED', `child stopped: ${result.stopReason}`);
        if (result.childTerminationConfirmed !== true) fail('CHILD_TERMINATION_UNCONFIRMED', 'child result did not confirm resource cleanup');
        step.output = clone(result.output);
        step.outputArtifact = store.write(entry.dir, `${step.stepId}.output.json`, step.output, true);
        event(entry, 'validating-output', { stepId: step.stepId, phase: 'validation' });
        step.validation = await validate(entry, definition.outputSchemaRef, step.output, 'output', step.stepId);
        step.handoffOutput = resolveFrameworkOutput(definition, step.output);
        step.handoffArtifact = store.write(entry.dir, `${step.stepId}.handoff.json`, step.handoffOutput, true);
        step.status = 'completed'; step.completedAt = now();
        completed.set(step.stepId, clone(step.handoffOutput));
        run.output = clone(step.handoffOutput);
        event(entry, 'step-completed', { stepId: step.stepId, phase: 'handoff' });
      }
      if (run.cancellationRequested) finishCancellation(entry);
      else {
        run.testResults = [];
        for (const test of entry.bundle.tests ?? []) {
          if (!Array.isArray(test.cases)) fail('TEST_DEFINITION_UNSUPPORTED', 'test definition requires cases', { testId: test.testId });
          for (const [caseIndex, testCase] of test.cases.entries()) {
            if (!isDeepStrictEqual(testCase.input, entry.input)) continue;
            if (!testCase.expected || typeof testCase.expected !== 'object') fail('TEST_DEFINITION_UNSUPPORTED', 'test expected must be an object');
            const errors = Object.entries(testCase.expected).filter(([key, value]) => !Object.hasOwn(run.output, key) || !isDeepStrictEqual(run.output[key], value))
              .map(([key, expected]) => ({ path: `/${key}`, expected, actual: run.output[key] }));
            run.testResults.push({ testId: test.testId, caseIndex, ok: !errors.length, errors });
            if (errors.length) fail('TEST_EXPECTATION_FAILED', 'configured output expectation failed', { testId: test.testId, caseIndex, errors });
          }
        }
        run.status = 'completed'; run.validation = { ok: true, errors: [] }; run.completedAt = now(); event(entry, 'completed', { phase: 'terminal' });
      }
    } catch (error) {
      run.error = errorInfo(error);
      run.validation = { ok: false, errors: error.details?.errors ?? [{ code: run.error.code, message: run.error.message }] };
      if (run.cancellationRequested) finishCancellation(entry);
      else { run.status = 'failed'; run.completedAt = now(); }
      const step = run.steps.find(step => step.status === 'running') ?? run.steps.find(step => step.status === 'pending');
      if (step) { step.error = errorInfo(error); if (run.status !== 'stopping') { step.status = 'failed'; step.completedAt = now(); } }
      event(entry, 'execution-error', { phase: run.status === 'stopping' ? 'cleanup' : 'terminal', stepId: step?.stepId });
    } finally {
      entry.finished = true;
      if (!entry.rawPending && run.childTerminationConfirmed !== false) live.delete(run.runId);
      save(entry);
    }
    return readRun({ runId: run.runId });
  }
  return {
    async startRun(input) {
      frameworkId(input.runId);
      if (!['training', 'published'].includes(input.mode)) fail('MODE_INVALID', 'framework run mode must be training or published');
      const bundle = freeze(clone(input.bundle));
      const verify = verifyBundle ?? (await import('./trainer-bundle.js')).verifyBundle;
      const validator = validateJson ?? (await import('./trainer-schema.js')).validateJson;
      const verification = await verify(bundle);
      if (verification === false || verification?.ok === false) fail('BUNDLE_INVALID', 'bundle verification failed', verification);
      if (!bundle.steps?.length || new Set(bundle.steps.map(step => step.stepId)).size !== bundle.steps.length) fail('BUNDLE_INVALID', 'steps must have unique identities');
      bundle.steps.forEach(step => frameworkId(step.stepId));
      if (bundle.runtimeApiVersion !== 'trainer-api-v1') fail('BUNDLE_INVALID', 'unsupported runtime API');
      for (const entry of live.values()) if (entry.run.projectId === bundle.projectId && entry.run.targetKind === bundle.targetKind && entry.run.targetId === bundle.targetId && (entry.run.cancellationRequested || entry.finished) && entry.run.childTerminationConfirmed !== true) fail('TERMINATION_UNCONFIRMED', 'previous target child has not confirmed termination');
      const optimization = input.purpose === 'agent-optimization';
      if (optimization && (input.mode !== 'training' || bundle.targetKind !== 'agent'
        || typeof input.derivedFromRunId !== 'string' || !input.derivedFromRunId
        || typeof input.changeSetId !== 'string' || !input.changeSetId)) {
        fail('OPTIMIZATION_BINDING_INVALID', 'agent-optimization requires a training Agent run, a base run and a change set');
      }
      if (input.purpose !== undefined && input.purpose !== 'agent-optimization') {
        fail('PURPOSE_INVALID', 'unsupported framework run purpose');
      }
      const run = { schemaVersion: 1, kind: 'framework-run', runId: input.runId, requestId: input.requestId,
        projectId: bundle.projectId, targetKind: bundle.targetKind, targetId: bundle.targetId, revisionId: bundle.revisionId,
        workflowRevision: bundle.workflowRevision ?? null,
        bundleSha256: bundle.bundleSha256, model: clone(bundle.model), mode: input.mode,
        purpose: input.mode === 'published' ? 'FRAMEWORK_REPLAY' : (optimization ? 'agent-optimization' : 'FRAMEWORK_TRAINING'), status: 'queued',
        startedAt: now(), updatedAt: now(), completedAt: null, derivedFromRunId: input.derivedFromRunId ?? null,
        changeSetId: input.changeSetId ?? null, releaseId: input.releaseId ?? null, businessGatePassed: false,
        cancellationRequested: false, childTerminationConfirmed: null, output: null, validation: null, error: null,
        steps: bundle.steps.map(step => ({ stepId: step.stepId, agentId: step.agentId,
          agentRevision: step.agentRevision ?? null, status: 'pending',
          inputBindings: clone(step.inputBindings ?? {}), outputBindings: clone(step.outputBindings ?? {}),
          parentSessionId: null, childSessionId: null, childTerminationConfirmed: null, actualLoadedRefs: [] })),
      };
      const dir = store.create(run);
      run.bundleArtifact = store.write(dir, 'execution-bundle.json', bundle, true);
      store.write(dir, 'run-input.json', input.input ?? {}, true);
      const entry = { run, dir, bundle, input: clone(input.input ?? {}), validateJson: validator, seq: 0, rawPending: false, finished: false };
      live.set(run.runId, entry);
      event(entry, 'queued', { phase: 'accepted' });
      entry.completion = Promise.resolve().then(() => execute(entry));
      entry.completion.catch(() => {});
      return { runId: run.runId, status: 'queued' };
    },
    readRun,
    listRuns({ projectId, targetKind, targetId, limit = 50, cursor = 0 } = {}) {
      const offset = Number(cursor);
      if (!Number.isSafeInteger(offset) || offset < 0 || !Number.isInteger(limit) || limit < 1) throw new Error('invalid run pagination');
      const all = store.list().filter(run => (!projectId || run.projectId === projectId) && (!targetKind || run.targetKind === targetKind) && (!targetId || run.targetId === targetId)).sort((a, b) => b.startedAt.localeCompare(a.startedAt) || b.runId.localeCompare(a.runId));
      const runs = all.slice(offset, offset + Math.min(limit, 200)).map(run => ({ ...run, controls: controls(run) }));
      return { runs, nextCursor: offset + runs.length < all.length ? offset + runs.length : null };
    },
    readEvents({ runId, cursor = 0 }) { const page = store.events(store.locate(runId), cursor); return { runId, ...page, nextCursor: page.cursor }; },
    controlRun({ runId, action }) {
      const entry = live.get(runId);
      if (!entry) fail('RUN_NOT_ACTIVE', 'run is not active');
      const run = entry.run;
      if (!controls(run)[action]?.allowed) fail('CONTROL_NOT_ALLOWED', controls(run)[action]?.reason ?? 'unknown action');
      if (action === 'pause') { entry.pauseRequested = true; run.status = 'pausing'; event(entry, 'pause-requested', { phase: 'control' }); }
      if (action === 'resume') { entry.pauseRequested = false; run.status = 'running'; event(entry, 'resumed', { phase: 'control' }); entry.resume?.(); }
      if (action === 'stop') {
        run.cancellationRequested = true;
        run.status = 'stopping';
        if (entry.lifecycle) entry.lifecycle.cancel('user stopped framework run');
        else { run.childTerminationConfirmed = true; finishCancellation(entry); }
        event(entry, 'stop-requested', { phase: 'control' });
        entry.resume?.();
      }
      return readRun({ runId });
    },
    waitForRun({ runId }) { return live.get(runId)?.completion ?? Promise.resolve(readRun({ runId })); },
    reconcileInterrupted() {
      const changed = [];
      for (const run of store.list()) {
        if (terminal.has(run.status) || live.has(run.runId)) continue;
        run.status = 'interrupted'; run.updatedAt = now(); run.completedAt = now();
        run.error = { code: 'HOST_RESTARTED', message: 'Host restarted; inspect child evidence before a new run', details: null };
        run.controls = controls(run);
        store.write(store.locate(run.runId), 'framework-run.json', run);
        changed.push(run.runId);
      }
      return changed;
    },
  };
}
