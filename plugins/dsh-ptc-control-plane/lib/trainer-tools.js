/** Preset scoped tools. The service rechecks identity and binding on every call. */
export const TRAINER_TOOL_OPERATIONS = Object.freeze({
  trainer_context: 'context', trainer_assets: 'assets', trainer_runs: 'runs',
  trainer_events: 'events', trainer_apply_changes: 'apply-changes', trainer_validate: 'validate',
  trainer_run: 'run', trainer_control: 'control', trainer_compare: 'compare',
});
const DESCRIPTIONS = {
  trainer_context: 'Read the server-bound project, target, selected run, candidate revision and permissions. Call first. Reading does not dispatch or edit.',
  trainer_assets: 'Read candidate asset files and exact revision. paths optionally selects relative files; omit to list/read all. Use these real contents before editing.',
  trainer_runs: 'Read a specific runId with step inputs, outputs, loaded versions, errors and cancellation evidence, or list project runs. Never infer completion from acceptance.',
  trainer_events: 'Read observed events for runId after an optional cursor. No internal model thinking is available.',
  trainer_apply_changes: 'Save an atomic candidate changes array [{path,content}] using baseRevision, requestId and reason; null content deletes. Link repairs with linkedRunId. Only after the user requests changes; diagnostic/status requests never authorize edits.',
  trainer_validate: 'Resolve and validate a saved target and its dependencies without calling a model. Requires targetKind and targetId.',
  trainer_run: 'Start the selected agent or linear workflow using its actual saved instructions and Skills. Requires requestId, targetKind, targetId and input. Returns a real runId, not completion. For repairs pass derivedFromRunId/changeSetId. Never launch just to answer status or diagnose.',
  trainer_control: 'Request pause/resume/stop for runId. Pause is at a step boundary; stop requested differs from child termination confirmed. Requires requestId and action.',
  trainer_compare: 'Compare beforeRunId and afterRunId, exact versions, outputs and linked candidate changes. Old failures remain unchanged.',
};
const fields = {
  projectId:'Bound project ID; normally omit', targetKind:'agent or workflow',targetId:'Registered target ID',
  runId:'Specific run to inspect/control',beforeRunId:'Original run',afterRunId:'New run',
  revisionId:'Saved candidate revision',baseRevision:'Exact revision read before editing',requestId:'Unique ASCII letters/digits/hyphen/underscore ID (1-128 chars); reuse only for an identical retry',
  reason:'User-requested reason for candidate changes',linkedRunId:'Run being repaired',derivedFromRunId:'Original run to preserve',
  changeSetId:'Applied change set',frozenVersionId:'Optional fixed candidate version',action:'pause, resume or stop',
};
const used = {
  context:[], assets:['revisionId','paths'], runs:['runId','limit','cursor'],events:['runId','cursor'],
  'apply-changes':['requestId','baseRevision','changes','reason','linkedRunId'],validate:['targetKind','targetId','revisionId'],
  run:['requestId','targetKind','targetId','input','revisionId','frozenVersionId','derivedFromRunId','changeSetId'],
  control:['requestId','runId','action'],compare:['beforeRunId','afterRunId'],
};
export function createTrainerTools(service, { defineTool, principalOf, role = 'agent-trainer' }) {
  return Object.entries(TRAINER_TOOL_OPERATIONS).filter(([,op]) => role === 'agent-trainer' || !['apply-changes','validate'].includes(op)).map(([name,operation]) => {
    const parameters = {};
    for (const field of used[operation]) parameters[field] = ['changes','input','paths','cursor','limit'].includes(field)
      ? { type:'json', description: field === 'changes' ? 'Array of {path,content}; exact UTF-8 replacement text, null deletes' : field }
      : { type:'string', description: fields[field] || field };
    return defineTool({ name, description: DESCRIPTIONS[name],parameters,
      output: { schema: {type:'json'}, render: (_args,value) => [{type:'text',text:JSON.stringify(value)}] },
      isConcurrencySafe: () => !['apply-changes','run','control'].includes(operation),
      execute: async (args,exec) => service.invoke(operation,args,await principalOf(exec)),
    });
  });
}
