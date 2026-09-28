/** Summarize only host-recorded orchestration receipts; never infer completion from chat. */
export function workflowStatusSummary(orchestration) {
  const stages = Array.isArray(orchestration?.stages) ? orchestration.stages : [];
  const tasks = [
    ...stages.flatMap(stage => Array.isArray(stage.tasks) ? stage.tasks : []),
    ...(Array.isArray(orchestration?.auxiliaryTasks) ? orchestration.auxiliaryTasks : []),
  ];
  const completed = tasks.filter(task => task.status === 'completed').length;
  const active = tasks.find(task => task.status === 'dispatching' || task.status === 'running');
  const blocked = tasks.find(task => task.status === 'blocked' || task.status === 'cancelled');
  const pending = tasks.find(task => task.status === 'pending');
  const current = active ?? blocked ?? pending ?? null;
  const lastCompletedIndex = tasks.findLastIndex(task => task.status === 'completed');
  const previous = lastCompletedIndex >= 0 ? tasks[lastCompletedIndex] : null;
  return {
    completed,
    total: tasks.length,
    currentProfileId: current?.profileId ?? current?.role ?? null,
    handoffFrom: current && previous && previous !== current ? previous.profileId ?? previous.role ?? null : null,
    currentStatus: current?.status ?? null,
  };
}
