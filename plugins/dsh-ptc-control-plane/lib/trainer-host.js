import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import * as projects from './trainer-project.js';
import * as bundles from './trainer-bundle.js';
import * as releases from './trainer-release.js';
import { validateJson } from './trainer-schema.js';
import { createFrameworkRunner } from './framework-agent-run.js';
import { createDshFrameworkAdapter } from './framework-dsh-adapter.js';
import { createTrainerService, DEFAULT_TRAINER_PROJECT_ID } from './trainer-service.js';
import { registerTrainerRuntime } from './trainer-runtime.js';
import { createTrainerApiHandler, TRAINER_API_OPERATIONS } from './trainer-api.js';
import { TRAINER_TOOL_OPERATIONS } from './trainer-tools.js';

function presetOf(session) {
  const events = session?.events || [];
  for (let i = events.length - 1; i >= 0; i -= 1) {
    if (events[i]?.type === 'agent-preset/selected') return events[i].data?.agentPreset;
  }
  return session?.header?.agentPreset;
}

export function mountTrainerHost(ctx, config) {
  const workspaceRoot = path.resolve(config.trainerWorkspaceRoot || config.workspaceRoot);
  const hostModel = () => {
    const selection = ctx.agentDefaultModel?.currentSelection?.();
    if (!selection || typeof selection.provider !== 'string' || typeof selection.model !== 'string') {
      throw Object.assign(new Error('The DSH host did not expose a current default model'), { code: 'native_model_unavailable' });
    }
    return { provider: selection.provider, model: selection.model };
  };
  const adapter = createDshFrameworkAdapter(ctx, { workspaceRoot, validateJson });
  const runner = createFrameworkRunner({ workspaceRoot, adapter, verifyBundle: bundles.verifyBundle, validateJson });
  runner.reconcileInterrupted();
  // A persisted Trainer session is not necessarily attached to the fresh DSH
  // host after a restart.  Reuse must materialize that exact session before
  // trainer-service verifies its preset and tool catalog; otherwise the
  // authoritative target record is discarded as "unbound" and the client
  // falls back to creating a new conversation.
  const persistedAgentResumes = new Map();
  const resumePersistedTrainerAgent = async (sessionId, presetId) => {
    const existing = ctx.agents.get(sessionId);
    if (existing) return existing;
    if (typeof ctx.agents.resume !== 'function' || typeof ctx.sessionPersistence?.inspect !== 'function') return null;
    let pending = persistedAgentResumes.get(sessionId);
    if (!pending) {
      pending = (async () => {
        const inspected = await ctx.sessionPersistence.inspect(sessionId);
        const headerPreset = inspected?.meta?.agentPreset || inspected?.header?.agentPreset;
        if (headerPreset !== presetId) return null;
        const resumed = await ctx.agents.resume({
          resumeSessionId: sessionId,
          agentOptions: hostModel(),
          setup: async agentCtx => { await ctx.agentPresets.mount(agentCtx, presetId); },
        });
        return resumed?.agent || null;
      })();
      persistedAgentResumes.set(sessionId, pending);
    }
    try { return await pending; }
    finally {
      if (persistedAgentResumes.get(sessionId) === pending) persistedAgentResumes.delete(sessionId);
    }
  };
  const service = createTrainerService({
    workspaceRoot,
    runner,
    repositories: { ...projects, ...bundles, ...releases },
    modelResolver: async () => hostModel(),
    sessionVerifier: async (sessionId, presetId) => {
      const agent = ctx.agents.get(sessionId) || await resumePersistedTrainerAgent(sessionId, presetId);
      if (agent) return ctx.agentPresets.composedPreset(agent.ctx) === presetId && presetOf(agent.session) === presetId;
      const session = ctx.sessions?.get(sessionId);
      if (session) return presetOf(session) === presetId;
      const persisted = await ctx.sessionPersistence?.inspect(sessionId);
      return presetOf(persisted) === presetId;
    },
    sessionToolCatalog: async sessionId => {
      const agent = ctx.agents.get(sessionId) || await resumePersistedTrainerAgent(sessionId, 'agent-trainer');
      if (!agent?.ctx?.tools?.schemas) return null;
      return agent.ctx.tools.schemas(agent).map(tool => tool.name).filter(name => Object.hasOwn(TRAINER_TOOL_OPERATIONS, name));
    },
    sessionFactory: async ({ cwd, presetId, nativeModelSelection, targetKind, targetId }) => {
      const model = nativeModelSelection || hostModel();
      const workspaceRegistry = ctx.workspaceRegistry || ctx.get?.('workspaceRegistry');
      if (!workspaceRegistry?.create) {
        throw Object.assign(new Error('The DSH workspace registry is unavailable'), { code: 'native_host_unavailable' });
      }
      // The native session list is workspace-backed. Creating an agent directly
      // only persists its log; it does not make the session selectable in the
      // host sidebar. Adopt the Trainer cwd first, then attach the new session
      // through the same registry boundary used by DSH's session.create API.
      const workspace = await workspaceRegistry.create(cwd, `ATE Trainer · ${targetKind}:${targetId}`);
      const created = await ctx.agents.create({
        sessionId: `session-${randomUUID()}`,
        meta: { cwd, agentPreset: presetId },
        agentOptions: { provider: model.provider, model: model.model },
        setup: async agentCtx => { await ctx.agentPresets.mount(agentCtx, presetId); },
      });
      await workspace.attachSession(created.agent.id);
      return created.agent.id;
    },
  });
  const disposeRuntime = registerTrainerRuntime(workspaceRoot, service);
  const routes = TRAINER_API_OPERATIONS.map(operation => ctx.webServer.register({
    kind: 'exact',
    path: `/api/ptc-control/trainer/${operation}`,
    handler: createTrainerApiHandler(service, operation),
  }));
  const workbenchPath = path.resolve(workspaceRoot, 'docs/prototypes/agent-trainer-repair-prototype.html');
  const guidePath = path.resolve(workspaceRoot, 'docs/prototypes/agent-trainer-user-guide.html');
  const evidencePath = path.resolve(workspaceRoot, 'docs/agent-trainer-empty-system-acceptance-evidence-20260930.json');
  const serveHtml = (filePath, title) => (request, response) => {
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      response.writeHead(405, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('Method Not Allowed');
      return;
    }
    try {
      const html = fs.readFileSync(filePath);
      response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      if (request.method === 'HEAD') response.end(); else response.end(html);
    } catch (error) {
      response.writeHead(503, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end(`${title} unavailable: ${error.message}`);
    }
  };
  const workbenchRoute = ctx.webServer.register({
    kind: 'exact',
    path: '/agent-trainer',
    handler: serveHtml(workbenchPath, 'Agent Trainer'),
  });
  const guideRoute = ctx.webServer.register({
    kind: 'exact',
    path: '/agent-trainer-guide',
    handler: serveHtml(guidePath, 'Agent Trainer guide'),
  });
  const evidenceRoute = ctx.webServer.register({
    kind: 'exact',
    path: '/agent-trainer-evidence.json',
    handler: (request, response) => {
      if (request.method !== 'GET' && request.method !== 'HEAD') {
        response.writeHead(405, { 'Content-Type': 'text/plain; charset=utf-8' });
        response.end('Method Not Allowed');
        return;
      }
      try {
        const evidence = fs.readFileSync(evidencePath);
        response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
        if (request.method === 'HEAD') response.end(); else response.end(evidence);
      } catch (error) {
        response.writeHead(503, { 'Content-Type': 'text/plain; charset=utf-8' });
        response.end(`Agent Trainer evidence unavailable: ${error.message}`);
      }
    },
  });
  return () => {
    workbenchRoute?.();
    guideRoute?.();
    evidenceRoute?.();
    for (const dispose of routes) dispose?.();
    disposeRuntime();
    const listed = runner.listRuns({ projectId: DEFAULT_TRAINER_PROJECT_ID, limit: 1000 });
    for (const run of listed.runs || []) if (run.controls?.stop?.allowed) runner.controlRun({ runId: run.runId, action: 'stop' });
  };
}
