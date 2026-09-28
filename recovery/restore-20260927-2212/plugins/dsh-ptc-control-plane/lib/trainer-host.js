import path from 'node:path';
import * as projects from './trainer-project.js';
import * as bundles from './trainer-bundle.js';
import * as releases from './trainer-release.js';
import { validateJson } from './trainer-schema.js';
import { createFrameworkRunner } from './framework-agent-run.js';
import { createDshFrameworkAdapter } from './framework-dsh-adapter.js';
import { createTrainerService } from './trainer-service.js';
import { registerTrainerRuntime } from './trainer-runtime.js';
import { createTrainerApiHandler, TRAINER_API_OPERATIONS } from './trainer-api.js';

function presetOf(session) {
  const events=session?.events || [];
  for(let i=events.length-1;i>=0;i--) if(events[i]?.type==='agent-preset/selected') return events[i].data?.agentPreset;
  return session?.header?.agentPreset;
}
export function mountTrainerHost(ctx,config) {
  const workspaceRoot=path.resolve(config.trainerWorkspaceRoot || config.workspaceRoot);
  const adapter=createDshFrameworkAdapter(ctx,{workspaceRoot,validateJson});
  const runner=createFrameworkRunner({workspaceRoot,adapter,verifyBundle:bundles.verifyBundle,validateJson});
  runner.reconcileInterrupted();
  const service=createTrainerService({workspaceRoot,runner,repositories:{...projects,...bundles,...releases},
    modelResolver:async()=>({provider:'deepseek-official',model:'deepseek-v4-flash'}),
    sessionVerifier:async(sessionId,presetId)=>{
      const agent=ctx.agents.get(sessionId);
      if(agent) return ctx.agentPresets.composedPreset(agent.ctx)===presetId && presetOf(agent.session)===presetId;
      const session=ctx.sessions?.get(sessionId);
      if(session) return presetOf(session)===presetId;
      const persisted=await ctx.sessionPersistence?.inspect(sessionId);
      return presetOf(persisted)===presetId;
    },
  });
  const disposeRuntime=registerTrainerRuntime(workspaceRoot,service);
  const routes=TRAINER_API_OPERATIONS.map(operation=>ctx.webServer.register({kind:'exact',path:`/api/ptc-control/trainer/${operation}`,handler:createTrainerApiHandler(service,operation)}));
  return ()=>{
    for(const dispose of routes)dispose?.();
    disposeRuntime();
    const listed=runner.listRuns({projectId:'synthetic-lab',limit:1000});
    for(const run of listed.runs||[]) if(run.controls?.stop?.allowed)runner.controlRun({runId:run.runId,action:'stop'});
  };
}
