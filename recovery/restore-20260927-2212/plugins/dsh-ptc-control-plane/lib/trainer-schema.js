import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const Ajv2020 = require('ajv/dist/2020.js').default;
const addFormats = require('ajv-formats');

export const TRAINER_SCHEMA_DRAFT = 'https://json-schema.org/draft/2020-12/schema';
export const assetPath = (p) => typeof p === 'string' && /^(agents|skills|contracts|workflows|tests|tools)\//.test(p)
  && p.split('/').every((s) => /^[A-Za-z0-9_][A-Za-z0-9_.-]*$/.test(s) && !s.endsWith('.') && !/^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(s));
export function bundleNamespace(reference) { return typeof reference === 'string' ? reference.match(/^dependencies\/[a-f0-9]{64}\//)?.[0] ?? '' : ''; }
export const bundleAssetPath = (p) => assetPath(p) || (Boolean(bundleNamespace(p)) && assetPath(p.slice(bundleNamespace(p).length)));
const error = (path, message, extra = {}) => ({ path, message, ...extra });
const uri = (p) => `https://trainer.invalid/${p}`;
const id = { type: 'string', pattern: '^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$' };
const text = { type: 'string', minLength: 1 };
const refs = { type: 'array', items: text, uniqueItems: true };
const modelDefinition = { type: 'object', required: ['provider', 'model'], properties: { provider: text, model: text, options: { type: 'object' }, credentialRef: text }, additionalProperties: false };
const agentDefinition = { type: 'object', required: ['agentId', 'name', 'instructionsRef', 'inputSchemaRef', 'outputSchemaRef'], properties: {
  agentId: id, name: text, instructionsRef: text, inputSchemaRef: text, outputSchemaRef: text, skillRefs: refs, toolIds: refs, model: modelDefinition,
}, additionalProperties: false };
const skillDefinition = { type: 'object', required: ['skillId', 'entryRef'], properties: { skillId: id, entryRef: text, referenceRefs: refs, scriptRefs: refs }, additionalProperties: false };
const bindingDefinition = { oneOf: [
  { type: 'object', required: ['source', 'pointer'], properties: { source: { const: 'input' }, pointer: { type: 'string' } }, additionalProperties: false },
  { type: 'object', required: ['source', 'stepId', 'pointer'], properties: { source: { const: 'step' }, stepId: id, pointer: { type: 'string' } }, additionalProperties: false },
  { type: 'object', required: ['source', 'value'], properties: { source: { const: 'literal' }, value: {} }, additionalProperties: false },
] };
const workflowDefinition = { type: 'object', required: ['workflowId', 'steps'], properties: { workflowId: id, name: text, steps: {
  type: 'array', minItems: 1, maxItems: 64, items: { type: 'object', required: ['stepId', 'agentId', 'inputBindings'], properties: {
    stepId: id, agentId: id, inputBindings: { type: 'object', additionalProperties: bindingDefinition }, outputSchemaRef: text,
    timeoutMs: { type: 'integer', minimum: 1, maximum: 480000 },
    agentVersion: { oneOf: [
      { type: 'object', required: ['kind'], properties: { kind: { const: 'candidate' } }, additionalProperties: false },
      { type: 'object', required: ['kind', 'frozenVersionId'], properties: { kind: { const: 'frozen' }, frozenVersionId: id }, additionalProperties: false },
    ] },
  }, additionalProperties: false },
} }, additionalProperties: false };
const toolDefinition = { type: 'object', required: ['toolId', 'adapter', 'adapterVersion', 'scriptRef', 'parameters', 'timeoutMs', 'interpreter'], properties: {
  toolId: id, adapter: text, adapterVersion: text, scriptRef: text, parameters: { type: 'object' }, timeoutMs: { type: 'integer', minimum: 1, maximum: 30000 }, interpreter: text,
}, additionalProperties: false };
const testDefinition = { type: 'object', required: ['testId', 'targetKind', 'targetId', 'cases'], properties: {
  testId: id, targetKind: { enum: ['agent', 'workflow'] }, targetId: id, cases: { type: 'array', minItems: 1, items: { type: 'object', required: ['input', 'expected'], properties: { input: {}, expected: { type: 'object' } }, additionalProperties: false } },
}, additionalProperties: false };
const definitionAjv = new Ajv2020({ strict: true, allErrors: true });
const definitions = [
  [/^agents\/[^/]+\/agent\.json$/, definitionAjv.compile(agentDefinition)],
  [/^skills\/[^/]+\/skill\.json$/, definitionAjv.compile(skillDefinition)],
  [/^workflows\/[^/]+\.json$/, definitionAjv.compile(workflowDefinition)],
  [/^tools\/[^/]+\.json$/, definitionAjv.compile(toolDefinition)],
  [/^tests\/[^/]+\.json$/, definitionAjv.compile(testDefinition)],
];
function schemasFrom(files) {
  return Object.entries(files ?? {}).filter(([p]) => p.endsWith('.schema.json')).map(([p, content]) => [p, typeof content === 'string' ? JSON.parse(content) : content]);
}
function checkRefs(node, known, at = '') {
  if (!node || typeof node !== 'object') return;
  if (node.$schema && node.$schema !== TRAINER_SCHEMA_DRAFT) throw new Error(`unsupported schema draft at ${at}`);
  if (node.$id && !known.has(node.$id)) throw new Error(`unregistered schema id at ${at}`);
  if (node.$async) throw new Error('asynchronous schemas are unsupported');
  for (const key of ['$ref', '$dynamicRef']) if (typeof node[key] === 'string') {
    const ref = node[key].split('#')[0];
    if (ref && (/^[a-z][a-z0-9+.-]*:/i.test(ref) || ref.startsWith('//')) && !known.has(ref)) throw new Error(`remote or unregistered reference: ${node[key]}`);
    if (ref.split('/').includes('..') || ref.includes('\\')) throw new Error(`unsafe schema reference: ${ref}`);
  }
  for (const [key, child] of Object.entries(node)) if (!['const', 'enum', 'default', 'examples'].includes(key)) checkRefs(child, known, `${at}/${key}`);
}
function validator(schema, files, schemaRef) {
  const ajv = new Ajv2020({ strict: true, allErrors: true, validateFormats: true, coerceTypes: false, useDefaults: false, removeAdditional: false });
  addFormats(ajv);
  // Preserve frozen schema bytes and their original IDs. Each source package
  // gets a separate registry, so identical IDs in different versions cannot mix.
  const namespace = bundleNamespace(schemaRef);
  const scoped = Object.fromEntries(Object.entries(files ?? {}).filter(([p]) => namespace ? p.startsWith(namespace) : !bundleNamespace(p)).map(([p, value]) => [namespace ? p.slice(namespace.length) : p, value]));
  const entries = schemasFrom(scoped);
  const known = new Set(entries.flatMap(([p, s]) => [uri(p), s.$id].filter(Boolean)));
  for (const [p, s] of entries) { checkRefs(s, known); ajv.addSchema(s, uri(p)); }
  checkRefs(schema, known);
  const localRef = schemaRef?.slice(namespace.length);
  const match = entries.find(([p, s]) => (localRef?.endsWith('.schema.json') ? p === localRef : true) && JSON.stringify(s) === JSON.stringify(schema));
  return match ? ajv.getSchema(uri(match[0])) : ajv.compile(localRef && schema && typeof schema === 'object' && !schema.$id ? { ...schema, $id: uri(localRef) } : schema);
}
/** Draft 2020-12, synchronous registered bundle references only; never fetches a URI. */
export function validateJson(schema, value, { files, schemaRef } = {}) {
  try {
    const validate = validator(schema, files, schemaRef);
    const ok = validate(value);
    return { ok, errors: (validate.errors ?? []).map((e) => error(e.instancePath, e.message, { schemaPath: e.schemaPath, keyword: e.keyword, params: e.params })) };
  } catch (e) { return { ok: false, errors: [error('', e.message, { keyword: 'schema', code: 'TRAINER_SCHEMA_INVALID' })] }; }
}

export function validateProjectFiles(files) {
  const errors = [];
  const parsed = Object.create(null);
  const requireRef = (ref, at) => { if (!assetPath(ref) || !Object.hasOwn(files, ref)) errors.push(error(at, `missing or unsafe dependency: ${ref}`)); };
  if (!files || typeof files !== 'object' || Array.isArray(files)) return { ok: false, errors: [error('', 'files must be an object')] };
  for (const [p, content] of Object.entries(files)) {
    if (!assetPath(p) || typeof content !== 'string' || Buffer.byteLength(content) > 262144 || Buffer.from(content).toString('utf8') !== content) { errors.push(error(p, 'invalid asset path or UTF-8 content (maximum 256 KiB)')); continue; }
    if (p.endsWith('.json')) try { parsed[p] = JSON.parse(content); } catch { errors.push(error(p, 'invalid JSON')); }
  }
  for (const [p, data] of Object.entries(parsed)) {
    if (p.endsWith('.schema.json')) { try { validator(data, files); } catch (e) { errors.push(error(p, e.message)); } continue; }
    if (!data || typeof data !== 'object' || Array.isArray(data)) { errors.push(error(p, 'definition must be an object')); continue; }
    const definition = definitions.find(([pattern]) => pattern.test(p))?.[1];
    if (definition && !definition(data)) { errors.push(...definition.errors.map((e) => error(`${p}${e.instancePath}`, e.message, { keyword: e.keyword, params: e.params }))); continue; }
    if (/^agents\/[^/]+\/agent.json$/.test(p)) {
      if (data.agentId !== p.split('/')[1] || typeof data.name !== 'string') errors.push(error(p, 'agent identity/name mismatch'));
      for (const key of ['instructionsRef', 'inputSchemaRef', 'outputSchemaRef']) requireRef(data[key], `${p}/${key}`);
      for (const id of data.skillRefs ?? []) requireRef(`skills/${id}/skill.json`, p);
      for (const id of data.toolIds ?? []) requireRef(`tools/${id}.json`, p);
    }
    if (/^skills\/[^/]+\/skill.json$/.test(p)) {
      if (data.skillId !== p.split('/')[1]) errors.push(error(p, 'skill identity mismatch'));
      for (const ref of [data.entryRef, ...(data.referenceRefs ?? []), ...(data.scriptRefs ?? [])]) requireRef(ref, p);
    }
    if (/^tools\/[^/]+.json$/.test(p)) {
      if (data.toolId !== p.slice(6, -5)) errors.push(error(p, 'tool identity mismatch'));
      requireRef(data.scriptRef, p);
      if (!data.adapter || !data.adapterVersion || !data.interpreter || !Number.isSafeInteger(data.timeoutMs) || data.timeoutMs < 1) errors.push(error(p, 'incomplete tool adapter registration'));
      if (!data.parameters || !validateJson(data.parameters, {}, { files }).errors.every((e) => e.keyword !== 'schema')) errors.push(error(p, 'invalid tool parameter schema'));
    }
    if (/^tests\/[^/]+\.json$/.test(p)) {
      if (data.testId !== p.slice(6, -5)) errors.push(error(p, 'test identity mismatch'));
      requireRef(data.targetKind === 'agent' ? `agents/${data.targetId}/agent.json` : `workflows/${data.targetId}.json`, p);
    }
    if (/^workflows\/[^/]+.json$/.test(p)) {
      if (data.workflowId !== p.slice(10, -5) || !Array.isArray(data.steps) || !data.steps.length || data.steps.length > 64) { errors.push(error(p, 'invalid workflow identity/steps')); continue; }
      const seen = new Set();
      for (const step of data.steps) {
        if (!step.stepId || seen.has(step.stepId)) errors.push(error(p, 'stepId must be unique'));
        if (step.agentVersion?.kind !== 'frozen') requireRef(`agents/${step.agentId}/agent.json`, p);
        if (step.outputSchemaRef) requireRef(step.outputSchemaRef, p);
        if (step.timeoutMs !== undefined && (!Number.isSafeInteger(step.timeoutMs) || step.timeoutMs < 1)) errors.push(error(p, 'invalid timeoutMs'));
        for (const [dest, binding] of Object.entries(step.inputBindings ?? {})) {
          if (!/^(?:\/(?:[^~]|~[01])*)*$/.test(dest) || !['input', 'step', 'literal'].includes(binding?.source)) errors.push(error(p, 'invalid input binding'));
          if (binding?.source === 'step' && !seen.has(binding.stepId)) errors.push(error(p, 'binding must refer to an earlier step'));
          if (binding?.source !== 'literal' && (typeof binding?.pointer !== 'string' || !/^(?:\/(?:[^~]|~[01])*)*$/.test(binding.pointer))) errors.push(error(p, 'invalid source JSON Pointer'));
        }
        seen.add(step.stepId);
      }
    }
  }
  return { ok: errors.length === 0, errors };
}
