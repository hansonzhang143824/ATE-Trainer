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
  const adapter = createDshFrameworkAdapter(ctx, { workspaceRoot, validateJson });
  const runner = createFrameworkRunner({ workspaceRoot, adapter, verifyBundle: bundles.verifyBundle, validateJson });
  runner.reconcileInterrupted();
  const service = createTrainerService({
    workspaceRoot,
    runner,
    repositories: { ...projects, ...bundles, ...releases },
    modelResolver: async () => ({ provider: 'deepseek-official', model: 'deepseek-v4-flash' }),
    sessionVerifier: async (sessionId, presetId) => {
      const agent = ctx.agents.get(sessionId);
      if (agent) return ctx.agentPresets.composedPreset(agent.ctx) === presetId && presetOf(agent.session) === presetId;
      const session = ctx.sessions?.get(sessionId);
      if (session) return presetOf(session) === presetId;
      const persisted = await ctx.sessionPersistence?.inspect(sessionId);
      return presetOf(persisted) === presetId;
    },
    sessionToolCatalog: async sessionId => {
      const agent = ctx.agents.get(sessionId);
      if (!agent?.ctx?.tools?.schemas) return null;
      return agent.ctx.tools.schemas(agent).map(tool => tool.name).filter(name => Object.hasOwn(TRAINER_TOOL_OPERATIONS, name));
    },
    sessionFactory: async ({ cwd, presetId }) => {
      const created = await ctx.agents.create({
        sessionId: `session-${randomUUID()}`,
        meta: { cwd, agentPreset: presetId },
        setup: async agentCtx => { await ctx.agentPresets.mount(agentCtx, presetId); },
      });
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
  const workbenchRoute = ctx.webServer.register({
    kind: 'exact',
    path: '/agent-trainer',
    handler: (request, response) => {
      if (request.method !== 'GET' && request.method !== 'HEAD') {
        response.writeHead(405, { 'Content-Type': 'text/plain; charset=utf-8' });
        response.end('Method Not Allowed');
        return;
      }
      try {
        const html = fs.readFileSync(workbenchPath);
        response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
        if (request.method === 'HEAD') response.end(); else response.end(html);
      } catch (error) {
        response.writeHead(503, { 'Content-Type': 'text/plain; charset=utf-8' });
        response.end(`Agent Trainer unavailable: ${error.message}`);
      }
    },
  });
  return () => {
    workbenchRoute?.();
    for (const dispose of routes) dispose?.();
    disposeRuntime();
    const listed = runner.listRuns({ projectId: DEFAULT_TRAINER_PROJECT_ID, limit: 1000 });
    for (const run of listed.runs || []) if (run.controls?.stop?.allowed) runner.controlRun({ runId: run.runId, action: 'stop' });
  };
}
