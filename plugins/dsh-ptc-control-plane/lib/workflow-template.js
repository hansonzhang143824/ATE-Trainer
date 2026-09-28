import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { resolveAgentProfile } from './agent-profile-runtime.js';

const ID = /^[a-z][a-z0-9-]{1,63}$/;
const SHA = /^[a-f0-9]{64}$/;
const MAX_STEPS = 32;
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const bytes = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

function safe(root, ...parts) {
  const target = path.isAbsolute(parts[0]) ? path.join(...parts) : path.join(root, ...parts);
  return assertSafeRunPath(root, target);
}
function fail(message, code = 'WORKFLOW_TEMPLATE_REJECTED') {
  const error = new Error(message); error.code = code; throw error;
}
function atomic(root, file, value) {
  const temporary = safe(root, `${file}.${crypto.randomUUID()}.tmp`);
  fs.writeFileSync(temporary, bytes(value), { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
function location(root, templateId) {
  if (typeof templateId !== 'string' || !ID.test(templateId)) fail('invalid workflow template id');
  return safe(root, 'Training_Materials', 'workflow-templates', templateId);
}
function locked(root, templateId, action) {
  const directory = location(root, templateId);
  fs.mkdirSync(directory, { recursive: true });
  const lock = safe(root, directory, '.edit-lock');
  try { fs.mkdirSync(lock); }
  catch (error) {
    if (error?.code === 'EEXIST') fail('workflow template is being edited', 'WORKFLOW_TEMPLATE_CONFLICT');
    throw error;
  }
  try { return action(directory); }
  finally { fs.rmdirSync(lock); }
}
function normalize(root, input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)
      || Object.keys(input).some(key => !['schemaVersion', 'kind', 'templateId', 'name', 'profileIds',
        'instruction', 'expectedAnswer', 'outputContract', 'handoffContract',
        'executionMode', 'modelPolicy', 'outputUse', 'businessGatePassed'].includes(key))) {
    fail('workflow template contains unsupported fields');
  }
  if ((input.schemaVersion !== undefined && input.schemaVersion !== 1)
      || (input.kind !== undefined && input.kind !== 'ptc-smoke-workflow-template')
      || (input.outputUse !== undefined && input.outputUse !== 'diagnostic-only')
      || (input.handoffContract !== undefined && input.handoffContract !== 'previous-evidence-sha256')
      || (input.executionMode !== undefined && input.executionMode !== 'sequential')
      || (input.modelPolicy !== undefined && input.modelPolicy !== 'tool-free')
      || (input.outputContract !== undefined && !same(input.outputContract, {
        type: 'object', properties: { answer: { type: 'number' } },
        required: ['answer'], additionalProperties: false }))
      || (input.businessGatePassed !== undefined && input.businessGatePassed !== false)) {
    fail('workflow smoke boundary changed');
  }
  const templateId = input.templateId;
  location(root, templateId);
  if (typeof input.name !== 'string' || !input.name.trim() || input.name.length > 120) fail('workflow name is required');
  if (!Array.isArray(input.profileIds) || input.profileIds.length < 1 || input.profileIds.length > MAX_STEPS
      || input.profileIds.some(id => typeof id !== 'string' || !ID.test(id))
      || new Set(input.profileIds).size !== input.profileIds.length) fail('workflow needs unique ordered Agent ids');
  for (const profileId of input.profileIds) {
    try { resolveAgentProfile(root, profileId); }
    catch (error) { fail(`unknown Agent: ${profileId} (${error?.message ?? 'profile is not resolvable'})`); }
  }
  if (input.instruction !== '1+2等于几，把答案写在JSON里' || input.expectedAnswer !== 3) {
    fail('this round only permits the fixed 1+2 numeric JSON smoke contract');
  }
  return { schemaVersion: 1, kind: 'ptc-smoke-workflow-template', templateId,
    name: input.name.trim(), profileIds: [...input.profileIds],
    instruction: input.instruction, expectedAnswer: 3,
    outputContract: { type: 'object', properties: { answer: { type: 'number' } },
      required: ['answer'], additionalProperties: false },
    handoffContract: 'previous-evidence-sha256', executionMode: 'sequential',
    modelPolicy: 'tool-free', outputUse: 'diagnostic-only',
    businessGatePassed: false };
}

/** Read the editable candidate and its exact-byte optimistic-lock digest. */
export function readWorkflowTemplate(workspaceRoot, templateId) {
  const root = path.resolve(workspaceRoot);
  const file = safe(root, location(root, templateId), 'draft.json');
  if (!fs.existsSync(file)) return { template: null, sha256: null, frozenSha256: null };
  const raw = fs.readFileSync(file);
  const value = JSON.parse(raw.toString('utf8').replace(/^\uFEFF/, ''));
  const normalized = normalize(root, value);
  if (!same(value, normalized)) fail('workflow draft shape changed');
  const sha256 = hash(raw);
  const frozenFile = safe(root, location(root, templateId), 'versions', `${sha256}.json`);
  const frozenSha256 = fs.existsSync(frozenFile) && hash(fs.readFileSync(frozenFile)) === sha256 ? sha256 : null;
  return { template: normalized, sha256, frozenSha256 };
}

/** Save is separate from freeze and activation; stale editors fail closed. */
export function saveWorkflowTemplate(workspaceRoot, input) {
  const root = path.resolve(workspaceRoot);
  if (input?.expectedSha256 !== null && !SHA.test(input?.expectedSha256 ?? '')) {
    fail('expected SHA-256 or null is required');
  }
  const template = normalize(root, input?.template);
  return locked(root, template.templateId, directory => {
    const existing = readWorkflowTemplate(root, template.templateId);
    if (existing.sha256 !== input.expectedSha256) fail('workflow draft changed in another editor', 'WORKFLOW_TEMPLATE_CONFLICT');
    atomic(root, safe(root, directory, 'draft.json'), template);
    return readWorkflowTemplate(root, template.templateId);
  });
}

/** Freeze the exact saved bytes, never an unsaved form or conversation. */
export function freezeWorkflowTemplate(workspaceRoot, input) {
  const root = path.resolve(workspaceRoot);
  return locked(root, input?.templateId, directory => {
    const current = readWorkflowTemplate(root, input.templateId);
    if (!current.template || !SHA.test(input?.sha256 ?? '') || current.sha256 !== input.sha256) {
      fail('saved workflow candidate changed before freeze', 'WORKFLOW_TEMPLATE_CONFLICT');
    }
    const source = safe(root, directory, 'draft.json');
    const sourceBytes = fs.readFileSync(source);
    if (hash(sourceBytes) !== current.sha256) fail('workflow draft changed during freeze', 'WORKFLOW_TEMPLATE_CONFLICT');
    const frozen = safe(root, directory, 'versions', `${current.sha256}.json`);
    fs.mkdirSync(path.dirname(frozen), { recursive: true });
    if (fs.existsSync(frozen)) {
      if (hash(fs.readFileSync(frozen)) !== current.sha256) fail('frozen workflow version changed');
    } else fs.writeFileSync(frozen, sourceBytes, { flag: 'wx' });
    return { templateId: input.templateId, versionSha256: current.sha256,
      path: path.relative(root, frozen).split(path.sep).join('/'), template: current.template };
  });
}

export function loadFrozenWorkflowTemplate(workspaceRoot, templateId, versionSha256) {
  const root = path.resolve(workspaceRoot);
  if (!SHA.test(versionSha256 ?? '')) fail('invalid workflow version SHA-256');
  const file = safe(root, location(root, templateId), 'versions', `${versionSha256}.json`);
  const raw = fs.readFileSync(file);
  if (hash(raw) !== versionSha256) fail('frozen workflow version was modified');
  const value = JSON.parse(raw.toString('utf8').replace(/^\uFEFF/, ''));
  const normalized = normalize(root, value);
  if (!same(value, normalized)) fail('frozen workflow shape changed');
  return { template: normalized, sha256: versionSha256, path: file };
}
