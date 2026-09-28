import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { createRunStore, frameworkId, frameworkSha } from './trainer-run-events.js';

export const FRAMEWORK_SCRIPT_ADAPTERS = Object.freeze({ 'node-script': '1', 'python-script': '1' });
const captureSchema = { type: 'object', properties: { payload: { type: 'object', additionalProperties: true } }, required: ['payload'], additionalProperties: false };
function asset(bundle, reference) {
  const file = bundle.files.find(item => item.path === reference);
  if (!file || typeof file.content !== 'string' || Buffer.byteLength(file.content) !== file.size || frameworkSha(Buffer.from(file.content)) !== file.sha256) throw new Error(`invalid bundle asset: ${reference}`);
  return file;
}
function safeAssetPath(store, dir, reference) {
  if (typeof reference !== 'string' || reference.includes('\\') || reference.startsWith('/') || reference.split('/').some(part => !part || part === '.' || part === '..')) throw new Error('unsafe bundle asset path');
  const target = store.safe(path.join(dir, reference));
  if (!target.startsWith(`${dir}${path.sep}`)) throw new Error('bundle asset escapes child workspace');
  return target;
}
function scriptProcess(binary, args, { cwd, input, signal, timeoutMs }) {
  return new Promise((resolve, reject) => {
    let stdout = ''; let stderr = ''; let failure;
    const processHandle = spawn(binary, args, { cwd, windowsHide: true, shell: false, signal, stdio: ['pipe', 'pipe', 'pipe'] });
    const timer = setTimeout(() => { failure = new Error('synthetic script timed out'); processHandle.kill(); }, timeoutMs);
    const stop = error => { failure ??= error; processHandle.kill(); };
    processHandle.on('error', error => { failure ??= error; });
    processHandle.stdout.on('data', chunk => { if (failure) return; stdout += chunk; if (Buffer.byteLength(stdout) > 1048576) stop(new Error('synthetic script output exceeds limit')); });
    processHandle.stderr.on('data', chunk => { if (failure) return; stderr += chunk; if (Buffer.byteLength(stderr) > 65536) stop(new Error('synthetic script diagnostics exceed limit')); });
    processHandle.stdin.on('error', error => { failure ??= error; });
    processHandle.on('close', code => {
      clearTimeout(timer);
      if (failure) return reject(failure);
      if (code !== 0) return reject(new Error(`synthetic script exited ${code}`));
      try { resolve(JSON.parse(stdout)); } catch { reject(new Error('synthetic script returned invalid JSON')); }
    });
    processHandle.stdin.end(JSON.stringify(input));
  });
}

/** A mounts framework-worker; this adapter creates scoped worker parents.
 * Registered script tools use fixed interpreters and bundle-owned script bytes. */
export function createDshFrameworkAdapter(ctx, { workspaceRoot, pythonExecutable = 'python', validateJson } = {}) {
  const store = createRunStore(workspaceRoot);
  return {
    async dispatch({ runId, step, bundle, input, signal, onEvent, onStart }) {
      frameworkId(runId); frameworkId(step.stepId);
      const model = step.model ?? bundle.model;
      if (!model?.provider || !model?.model) throw new Error('resolved provider/model required');
      if (!ctx.agents?.create || !ctx.agentPresets?.mount || !ctx.subagents?.start || !ctx.on) throw new Error('DSH child services unavailable');
      const validator = validateJson ?? (await import('./trainer-schema.js')).validateJson;
      const modeDir = store.locate(runId);
      const cwd = store.safe(path.join(modeDir, 'workers', step.stepId));
      fs.mkdirSync(cwd, { recursive: true });
      for (const file of bundle.files) {
        asset(bundle, file.path);
        const target = safeAssetPath(store, cwd, file.path);
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.writeFileSync(target, file.content, { flag: 'wx', encoding: 'utf8' });
        if (frameworkSha(fs.readFileSync(target)) !== file.sha256) throw new Error('materialized bundle asset mismatch');
      }
      const instruction = asset(bundle, step.instructionsRef).content;
      const skills = (step.skillRefs ?? []).map(id => {
        const skill = bundle.skills[id];
        if (!skill) throw new Error(`missing skill ${id}`);
        return [skill.entryRef, ...(skill.referenceRefs ?? [])].map(ref => ({ path: ref, content: asset(bundle, ref).content }));
      }).flat();
      const outputSchema = JSON.parse(asset(bundle, step.outputSchemaRef).content);
      const files = Object.fromEntries(bundle.files.map(file => [file.path, file.content]));
      const names = new Set();
      const tools = (step.toolIds ?? []).map(toolId => {
        const definition = bundle.tools[toolId];
        if (!definition || FRAMEWORK_SCRIPT_ADAPTERS[definition.adapter] !== definition.adapterVersion) throw new Error(`unsupported script adapter for ${toolId}`);
        const toolName = definition.toolId ?? toolId;
        if (names.has(toolName) || toolName === 'structured_output' || toolName === 'run_code') throw new Error('duplicate or reserved script tool name within one step');
        if (!/^[A-Za-z0-9_-]{1,64}$/.test(toolName)) throw new Error('invalid script tool name');
        names.add(toolName);
        if (!(definition.timeoutMs > 0 && definition.timeoutMs <= 30000)) throw new Error('script timeout must be within 30 seconds');
        const isNode = definition.adapter === 'node-script';
        if (definition.interpreter !== (isNode ? 'node>=20' : 'python>=3')) throw new Error('script interpreter does not match registered adapter');
        const file = asset(bundle, definition.scriptRef);
        const script = safeAssetPath(store, cwd, file.path);
        return {
          name: toolName, description: `Run the declared synthetic JSON script ${toolName}.`, parameters: definition.parameters,
          output: { schema: { type: 'object', properties: { json: { type: 'string' } }, required: ['json'], additionalProperties: false }, render: (_args, value) => [{ type: 'text', text: value.json }] },
          async execute(args, exec) {
            if (signal.aborted) throw new Error('framework run stopped');
            const validation = await validator(definition.parameters, args, { files, schemaRef: definition.scriptRef });
            if (!validation.ok) throw new Error('synthetic script parameters failed validation');
            if (frameworkSha(fs.readFileSync(script)) !== file.sha256) throw new Error('synthetic script changed after loading');
            onEvent({ type: 'tool-started', phase: 'tool', toolId, toolName, summary: file.sha256 });
            try {
              const combined = exec.signal ? AbortSignal.any([signal, exec.signal]) : signal;
              const result = await scriptProcess(isNode ? process.execPath : pythonExecutable, isNode ? [script] : ['-X', 'utf8', script], { cwd, input: args, signal: combined, timeoutMs: definition.timeoutMs });
              onEvent({ type: 'tool-completed', phase: 'tool', toolId, toolName });
              return { json: JSON.stringify(result) };
            } catch (error) { onEvent({ type: 'tool-failed', phase: 'tool', toolId, toolName }); throw error; }
          },
        };
      });
      let parent; let child; let result; let failure; let confirmed = false;
      const listeners = [];
      let childSessionId;
      const parentSessionId = `framework-parent-${runId}-${step.stepId}`;
      const publish = id => {
        if (childSessionId === id) return;
        if (childSessionId) throw new Error('multiple child identities for one step');
        childSessionId = id;
        onStart({ parentSessionId, childSessionId: id });
      };
      try {
        // composeFrom joins the standing preset, NOT the parent's agent-local
        // tools. agent/created is synchronous and precedes loop startup. A
        // registration error here rejects publication and rolls creation back.
        listeners.push(ctx.on('agent/created', ({ agent }) => {
          if (agent.session.header.parentSession !== parentSessionId) return;
          publish(agent.id);
          const permitted = new Set([...tools.map(tool => tool.name), 'structured_output']);
          agent.ctx.tools.guard(exec => permitted.has(exec.name) ? undefined : 'tool is outside the immutable step policy');
          for (const tool of tools) agent.ctx.tools.register(tool);
          // Public schemas(scope) resolves the effective scoped registry. Do
          // not report the requested allow-list as observed host evidence.
          const schemas = agent.ctx.tools.schemas(agent);
          const effectiveTools = schemas.map(schema => schema.name).sort();
          onEvent({ type: 'effective-tools', phase: 'composition', childSessionId: agent.id,
            effectiveTools, toolSchemasSha256: frameworkSha(Buffer.from(JSON.stringify(schemas))) });
          if (effectiveTools.length !== permitted.size || effectiveTools.some(name => !permitted.has(name))) {
            throw new Error('effective child tools differ from immutable step policy; worker requires native tools and no extra local capabilities');
          }
        }));
        if (ctx.on) listeners.push(ctx.on('session/event', (session, observed) => {
          if (session.header?.parentSession !== parentSessionId) return;
          const phases = { 'assistant/message': 'visible-output', 'tool/call': 'tool', 'tool/result': 'tool', 'step/start': 'waiting-model', 'step/end': 'result' };
          if (!Object.hasOwn(phases, observed.type)) return;
          onEvent({ type: observed.type, phase: phases[observed.type], childSessionId: session.id ?? session.header.id, summary: observed.type });
        }));
        onEvent({ type: 'parent-creating', phase: 'session-create' });
        parent = await ctx.agents.create({ sessionId: parentSessionId, signal,
          meta: { cwd, agentPreset: 'framework-worker' }, agentOptions: { ...model.options, provider: model.provider, model: model.model },
          setup: async agentCtx => {
            await ctx.agentPresets.mount(agentCtx, 'framework-worker');
          },
        });
        if (signal.aborted) throw new Error('framework run stopped during parent creation');
        const scope = parent.agent.ctx;
        if (scope?.on) {
          listeners.push(scope.on('subagent/start', info => {
            publish(info.id);
            onEvent({ type: 'host-child-started', phase: 'waiting-model', childSessionId: info.id, hostSubagentRunId: info.runId });
          }));
          listeners.push(scope.on('subagent/end', info => onEvent({ type: 'host-child-settled', phase: 'result', childSessionId: info.id, hostSubagentRunId: info.runId, summary: info.stopReason })));
        }
        child = await ctx.subagents.start('spawn', { parent: parent.agent, signal,
          label: `Framework ${runId}/${step.stepId}`, agentOptions: { ...model.options, provider: model.provider, model: model.model },
          // DSH restrict() accepts global names only; scoped scripts and the
          // child-scoped structured_output remain visible under an empty mask.
          maxDepth: 1, toolFilter: { allow: [] },
          persona: 'You execute a synthetic framework training step. Follow its selected instructions and Skill documents. Use only declared tools. This is not business certification.',
          prompt: [{ type: 'text', text: JSON.stringify({ instructions: instruction, skills, input, outputSchema,
            response: 'Call structured_output with {payload: YOUR_RESULT_OBJECT}. The payload must satisfy outputSchema. Do not add an extra payload wrapper inside your result.' }) }],
          outputSchema: captureSchema,
        });
        if (typeof child.id !== 'string' || !child.id) throw new Error('DSH returned no child identity');
        publish(child.id);
        if (signal.aborted) await child.dispose();
        result = await child.result;
        onEvent({ type: 'child-result', phase: 'result', childSessionId: child.id, summary: result.stopReason });
        if (!signal.aborted && result.stopReason === 'completed' && (!result.structured || !Object.hasOwn(result.structured, 'payload'))) throw new Error('DSH returned no captured payload');
      } catch (error) { failure = error; }
      finally {
        try {
          if (child) await child.dispose();
          if (parent) await parent.dispose();
          confirmed = true;
          onEvent({ type: 'child-termination-confirmed', phase: 'cleanup', childSessionId: child?.id, childTerminationConfirmed: true, disposalStatus: 'completed' });
        } catch (error) {
          failure ??= error;
          onEvent({ type: 'child-disposal-failed', phase: 'cleanup', childSessionId: child?.id, childTerminationConfirmed: false, disposalStatus: 'failed' });
        } finally { for (const dispose of listeners) if (typeof dispose === 'function') dispose(); }
      }
      if (failure) { failure.childTerminationConfirmed = confirmed; throw failure; }
      return { output: result?.structured?.payload, stopReason: result?.stopReason ?? 'aborted', parentSessionId, childSessionId, childTerminationConfirmed: confirmed };
    },
  };
}
