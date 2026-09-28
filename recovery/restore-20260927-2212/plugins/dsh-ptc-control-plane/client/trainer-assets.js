export function trainerNewAgentChanges({ agentId, name }) {
  if (!/^[a-z][a-z0-9-]{0,63}$/.test(agentId)) throw new Error('Agent ID 须为小写字母开头，后接字母、数字或连字符，最多64位');
  if (!name.trim()) throw new Error('请填写 Agent 名称');
  const inputSchemaRef = `contracts/${agentId}-input.schema.json`;
  const outputSchemaRef = `contracts/${agentId}-output.schema.json`;
  const instructionsRef = `agents/${agentId}/instructions.md`;
  const json = value => `${JSON.stringify(value, null, 2)}\n`;
  const schema = { $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object' };
  return [
    { path: `agents/${agentId}/agent.json`, content: json({ agentId, name: name.trim(), instructionsRef, skillRefs: [], toolIds: [], inputSchemaRef, outputSchemaRef }) },
    { path: instructionsRef, content: 'Process the supplied synthetic JSON input and return a JSON object. Do not load business materials.\n' },
    { path: inputSchemaRef, content: json(schema) }, { path: outputSchemaRef, content: json(schema) }
  ];
}

export function trainerNewWorkflowChanges({ workflowId, name, firstAgentId, secondAgentId }) {
  if (!/^[a-z][a-z0-9-]{0,63}$/.test(workflowId)) throw new Error('工作流 ID 须为小写字母开头，后接字母、数字或连字符，最多64位');
  if (!name.trim()) throw new Error('请填写工作流名称');
  if (!firstAgentId || !secondAgentId) throw new Error('工作流至少需要选择两个 Agent');
  if (firstAgentId === secondAgentId) throw new Error('请选择两个不同的 Agent');
  const firstStepId = 'step-1';
  const secondStepId = 'step-2';
  const workflow = {
    workflowId,
    name: name.trim(),
    steps: [
      { stepId: firstStepId, agentId: firstAgentId, inputBindings: { '': { source: 'input', pointer: '' } }, timeoutMs: 120000 },
      { stepId: secondStepId, agentId: secondAgentId, inputBindings: { '': { source: 'step', stepId: firstStepId, pointer: '' } }, timeoutMs: 120000 }
    ]
  };
  return [{ path: `workflows/${workflowId}.json`, content: `${JSON.stringify(workflow, null, 2)}\n` }];
}

export function trainerAppendStep(workflow, agentId) {
  if (workflow.steps.length >= 64) throw new Error('工作流最多64步');
  const ids = new Set(workflow.steps.map(step => step.stepId));
  let number = 1;
  while (ids.has(`step-${number}`)) number += 1;
  return { ...workflow, steps: [...workflow.steps, { stepId: `step-${number}`, agentId, inputBindings: {}, timeoutMs: 120000 }] };
}

export function trainerMoveStep(workflow, index, offset) {
  const next = index + offset;
  if (next < 0 || next >= workflow.steps.length) return workflow;
  const steps = [...workflow.steps];
  [steps[index], steps[next]] = [steps[next], steps[index]];
  return { ...workflow, steps };
}

export function trainerFrozenVersionsFor(versions, target) {
  if (!target) return [];
  return versions.filter(version => (!version.projectId || version.projectId === target.projectId)
    && version.targetKind === target.targetKind && version.targetId === target.targetId);
}

export function trainerFrozenVersionLabel(version) {
  return `${version.targetKind}/${version.targetId} · ${version.frozenVersionId} · ${version.revisionId} · SHA-256 ${version.bundleSha256}`;
}

export function trainerStepVersion(workflow, stepId, frozenVersionId, versions, projectId) {
  const step = workflow.steps.find(item => item.stepId === stepId);
  if (!step) throw new Error('步骤不存在');
  if (frozenVersionId && !trainerFrozenVersionsFor(versions, { projectId, targetKind: 'agent', targetId: step.agentId }).some(version => version.frozenVersionId === frozenVersionId)) {
    throw new Error('冻结版本不属于该步骤的 Agent');
  }
  return { ...workflow, steps: workflow.steps.map(item => {
    if (item.stepId !== stepId) return item;
    const next = { ...item };
    if (frozenVersionId) next.agentVersion = { kind: 'frozen', frozenVersionId };
    else delete next.agentVersion;
    return next;
  }) };
}

export function trainerMatchingEvidence(runs, version) {
  if (!version) return [];
  return runs.filter(run => run.status === 'completed' && (!version.projectId || run.projectId === version.projectId)
    && run.targetKind === version.targetKind && run.targetId === version.targetId && run.bundleSha256 === version.bundleSha256);
}
