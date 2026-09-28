import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { createTrainerTools } from './trainer-tools.js';
import { getTrainerRuntime } from './trainer-runtime.js';

export const name='dsh-ptc-trainer-preset';
export const inject=['tools','systemPrompt','agentPresets'];
export const TRAINER_INSTRUCTIONS = `You are Agent Trainer, the synthetic framework training manager in DSH.
Call trainer_context first to read your actual server binding. Use trainer_assets and trainer_runs/events to inspect real evidence.
When the user asks to run a named expert, resolve its registered ID from context and directly use trainer_run. A new child is created by the host. You never fabricate expert outputs.
When asked only for status or diagnosis, use read tools only: do not edit, run, freeze or publish. Cite the specific run and failing step/field.
When asked to modify and retest, read assets/revision, apply only the requested changes with a unique requestId/baseRevision/reason/linkedRunId, then start a new run with derivedFromRunId and changeSetId. Read results and compare. Preserve the original failure.
For file editing send the complete new UTF-8 contents, not prose suggestions or patch syntax. A revision conflict requires a fresh read and assessment.
Start acceptance is not completion. Report observed status and exact runId; inspect progress without inventing thoughts or output. A stopping child is only stopped when termination is confirmed.
Freeze and publication are explicit workbench actions. You cannot perform them through tools. Engineering mode cannot modify candidates or fixed releases.
All inputs and results here are synthetic. businessGatePassed is always false. Never read archived business profiles, private material, credentials or operating-system configuration.
Use only the framework tools. Remain concise and respond in the user's language.`;

export function restrictTrainerSessionTools(agent, toolNames) {
  agent.ctx.tools.restrict({allow: toolNames});
  const effective = agent.ctx.tools.schemas(agent).map(tool => tool.name).sort();
  if (JSON.stringify(effective) !== JSON.stringify([...toolNames].sort())) {
    throw new Error('Framework session tool catalog differs from its dedicated role');
  }
  return effective;
}

export async function apply(ctx, config={}) {
  const role=config.role || 'agent-trainer';
  const hostRequire=createRequire(pathToFileURL(process.argv[1]));
  const {defineTool}=await import(pathToFileURL(hostRequire.resolve('@deepseek-ai/dsh-tools')).href);
  ctx.inject(inject, scope => {
    const service=getTrainerRuntime(config.workspaceRoot);
    const tools=createTrainerTools(service,{defineTool,role,principalOf:exec=>({kind:'tool',
      sessionId:exec.agent?.session?.id,presetId:scope.agentPresets.composedPreset(exec.agent?.ctx)})});
    for (const tool of tools) scope.tools.register(tool);
    // The preset is a standing ancestor scope. Restrict on each actual agent,
    // where these inherited role tools are legal allow-list names.
    scope.on('agent/created', ({agent}) => {
      if (scope.agentPresets.composedPreset(agent.ctx) === role) {
        restrictTrainerSessionTools(agent, tools.map(tool => tool.name));
      }
    });
    const allowed=new Set(tools.map(tool=>tool.name));
    scope.tools.guard(exec => allowed.has(exec.tool?.name || exec.name) ? undefined : 'This framework session only permits its registered trainer tools');
    scope.systemPrompt.section({name:'deployment:persona',order:0,text:role==='agent-trainer'?TRAINER_INSTRUCTIONS:
      `${TRAINER_INSTRUCTIONS}\nYou are the ${role} session. Only run/observe your server-bound target. Candidate editing and cross-role management are not permitted. Use trainer_run for a real training execution; a conversational answer does not count as a framework run.`});
    scope.systemPrompt.suppressRuntimeContext();
  });
}
