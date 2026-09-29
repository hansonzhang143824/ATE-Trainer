const json = (value) => `${JSON.stringify(value, null, 2)}\n`;
const object = (properties) => ({ $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object', properties, required: Object.keys(properties), additionalProperties: false });
/** Synthetic assets only. IDs and fields are fixture data, never runner behavior. */
export function createSyntheticTrainerFixture() {
  const files = {
    'agents/lab-producer/instructions.md': 'Return JSON value equal to input.seed + 1. Read the lab-marker Skill and its reference. Call lab-marker for its scriptMarker. Return value, marker (from reference), and scriptMarker (from tool).\n',
    'agents/lab-consumer/instructions.md': 'Return JSON receivedValue exactly equal to input.receivedValue. Do not invent a fixed answer.\n',
    'skills/lab-marker/SKILL.md': 'Load references/marker.json to obtain marker. Invoke declared lab-marker tool to obtain scriptMarker.\n',
    'skills/lab-marker/references/marker.json': json({ marker: 'v1' }),
    'skills/lab-marker/scripts/marker.mjs': 'process.stdout.write(JSON.stringify({scriptMarker:"script-v1"}));\n',
    'skills/lab-marker/skill.json': json({ skillId: 'lab-marker', entryRef: 'skills/lab-marker/SKILL.md', referenceRefs: ['skills/lab-marker/references/marker.json'], scriptRefs: ['skills/lab-marker/scripts/marker.mjs'] }),
    'contracts/producer-input.schema.json': json(object({ seed: { type: 'integer' } })),
    'contracts/producer-output.schema.json': json(object({ value: { type: 'integer' }, marker: { type: 'string' }, scriptMarker: { type: 'string' } })),
    'contracts/consumer-input.schema.json': json(object({ receivedValue: { type: 'integer' } })),
    'contracts/consumer-output.schema.json': json(object({ receivedValue: { type: 'integer' } })),
    'tools/lab-marker.json': json({ toolId: 'lab-marker', adapter: 'node-script', adapterVersion: '1', scriptRef: 'skills/lab-marker/scripts/marker.mjs', parameters: { type: 'object', additionalProperties: false }, timeoutMs: 5000, interpreter: 'node>=20' }),
    'workflows/lab-pair.json': json({ workflowId: 'lab-pair', name: 'Synthetic producer → consumer', steps: [
      { stepId: 'produce', agentId: 'lab-producer', inputBindings: { '/seed': { source: 'input', pointer: '/seed' } }, timeoutMs: 120000 },
      { stepId: 'consume', agentId: 'lab-consumer', inputBindings: { '/receivedValue': { source: 'step', stepId: 'produce', pointer: '/value' } }, timeoutMs: 120000 },
    ] }),
    'tests/lab-pair.json': json({ testId: 'lab-pair', targetKind: 'workflow', targetId: 'lab-pair', cases: [{ input: { seed: 7 }, expected: { receivedValue: 8 } }, { input: { seed: 19 }, expected: { receivedValue: 20 } }] }),
  };
  for (const [id, name, prefix, skillRefs, toolIds] of [
    ['lab-producer', 'Synthetic producer', 'producer', ['lab-marker'], ['lab-marker']],
    ['lab-consumer', 'Synthetic consumer', 'consumer', [], []],
  ]) files[`agents/${id}/agent.json`] = json({ agentId: id, name, instructionsRef: `agents/${id}/instructions.md`, skillRefs, toolIds, inputSchemaRef: `contracts/${prefix}-input.schema.json`, outputSchemaRef: `contracts/${prefix}-output.schema.json` });
  return { files };
}
