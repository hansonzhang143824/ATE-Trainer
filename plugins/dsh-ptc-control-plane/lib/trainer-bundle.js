import fs from 'node:fs';
import { randomUUID } from 'node:crypto';
import { readAssets, trainerFail, trainerId, trainerJson, trainerProjectRoot, trainerRead, trainerSafe, trainerSha, trainerWrite } from './trainer-project.js';
import { assetPath, bundleAssetPath, bundleNamespace, validateProjectFiles } from './trainer-schema.js';

function ordered(value) {
  if (Array.isArray(value)) return value.map(ordered);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map((k) => [k, ordered(value[k])]));
  return value;
}
/** Exact persisted manifest bytes. bundleSha256 is an external reference. */
export function bundleManifestBytes(bundle) {
  const { bundleSha256, ...manifest } = bundle;
  return Buffer.from(`${JSON.stringify(ordered(manifest))}\n`);
}
const sha = (bundle) => trainerSha(bundleManifestBytes(bundle));
function modelCheck(model) {
  if (!model || typeof model.provider !== 'string' || !model.provider || typeof model.model !== 'string' || !model.model) trainerFail('TRAINER_MODEL_REQUIRED', 'resolved provider and model required');
  if (Object.keys(model).some((k) => !['provider', 'model', 'options', 'credentialRef'].includes(k))) trainerFail('TRAINER_MODEL_INVALID', 'model must contain configuration and credential reference only');
  const secret = (v) => v && typeof v === 'object' && Object.entries(v).some(([k, value]) => /^(api[-_]?key|token|secret|password|authorization|headers)$/i.test(k) || secret(value));
  if (secret(model.options)) trainerFail('TRAINER_MODEL_INVALID', 'credentials cannot enter bundle options');
}
export function verifyBundle(bundle) {
  try {
    if (bundle?.schemaVersion !== 1 || bundle.runtimeApiVersion !== 'trainer-api-v1' || !['agent', 'workflow'].includes(bundle.targetKind)) trainerFail('TRAINER_BUNDLE_INVALID', 'unsupported bundle identity');
    for (const id of [bundle.projectId, bundle.targetId, bundle.revisionId]) trainerId(id);
    modelCheck(bundle.model);
    if (!/^[a-f0-9]{64}$/.test(bundle.bundleSha256) || sha(bundle) !== bundle.bundleSha256) trainerFail('TRAINER_INTEGRITY', 'bundle manifest digest mismatch');
    const files = Object.create(null); let previous = '';
    for (const entry of bundle.files) {
      if (!bundleAssetPath(entry.path) || entry.path <= previous || typeof entry.content !== 'string') trainerFail('TRAINER_INTEGRITY', 'bundle files must be unique and sorted');
      previous = entry.path; const bytes = Buffer.from(entry.content);
      if (bytes.toString('utf8') !== entry.content || bytes.length !== entry.size || trainerSha(bytes) !== entry.sha256) trainerFail('TRAINER_INTEGRITY', 'bundle asset digest mismatch', { path: entry.path });
      files[entry.path] = entry.content;
    }
    const validation = validateProjectFiles(Object.fromEntries(Object.entries(files).filter(([p]) => !bundleNamespace(p))));
    if (!validation.ok) trainerFail('TRAINER_BUNDLE_INVALID', 'invalid bundle dependency closure', validation.errors);
    if (!Array.isArray(bundle.steps) || !bundle.steps.length || bundle.steps.length > 64) trainerFail('TRAINER_BUNDLE_INVALID', 'invalid bundle steps');
    const seen = new Set();
    for (const step of bundle.steps) {
      trainerId(step.stepId); trainerId(step.agentId);
      if (seen.has(step.stepId)) trainerFail('TRAINER_BUNDLE_INVALID', 'duplicate step ID');
      seen.add(step.stepId);
      for (const ref of [step.instructionsRef, step.inputSchemaRef, step.outputSchemaRef]) if (!Object.hasOwn(files, ref)) trainerFail('TRAINER_BUNDLE_INVALID', `missing step dependency ${ref}`);
      for (const id of step.skillRefs) if (!Object.hasOwn(bundle.skills, id)) trainerFail('TRAINER_BUNDLE_INVALID', `missing skill ${id}`);
      for (const id of step.toolIds) if (!Object.hasOwn(bundle.tools, id)) trainerFail('TRAINER_BUNDLE_INVALID', `missing tool ${id}`);
      const toolNames = step.toolIds.map((id) => bundle.tools[id].toolId);
      if (new Set(toolNames).size !== toolNames.length) trainerFail('TRAINER_BUNDLE_INVALID', 'duplicate actual toolId in one step');
      if (step.model) modelCheck(step.model);
    }
    // The digest alone proves bytes, not that the resolved projection follows
    // its authored definitions. Rebuild from bundled files without live reads.
    const definition = resolveDefinition({ ...bundle, files });
    if (!bundleManifestBytes(definition).equals(bundleManifestBytes(bundle))) trainerFail('TRAINER_BUNDLE_DEFINITION_MISMATCH', 'resolved steps, tools, skills, tests or closure differ from bundled definitions');
    return { ok: true, errors: [] };
  } catch (e) { return { ok: false, errors: [{ code: e.code ?? 'TRAINER_BUNDLE_INVALID', message: e.message, details: e.details }] }; }
}
function assertBundle(bundle) { const result = verifyBundle(bundle); if (!result.ok) trainerFail('TRAINER_INTEGRITY', 'bundle verification failed', result.errors); }
export function resolveBundle(root, input) {
  const { projectId, targetKind, targetId, frozenVersionId, model } = input;
  trainerId(targetId);
  if (frozenVersionId) {
    const bundle = loadFrozenBundle(root, { projectId, frozenVersionId });
    if (bundle.targetKind !== targetKind || bundle.targetId !== targetId) trainerFail('TRAINER_TARGET_MISMATCH', 'frozen target mismatch');
    return bundle;
  }
  if (!['agent', 'workflow'].includes(targetKind)) trainerFail('TRAINER_TARGET_INVALID', 'invalid target kind');
  modelCheck(model);
  const { revisionId, files } = readAssets(root, input);
  const dependencyBundles = Object.create(null); const frozenDependencies = Object.create(null);
  if (targetKind === 'workflow') {
    const workflow = JSON.parse(files[`workflows/${targetId}.json`] ?? 'null');
    if (!workflow) trainerFail('TRAINER_DEPENDENCY_MISSING', 'workflow not found');
    for (const step of workflow.steps) if (step.agentVersion?.kind === 'frozen') {
      const version = trainerId(step.agentVersion.frozenVersionId);
      const source = loadFrozenBundle(root, { projectId, frozenVersionId: version });
      if (source.targetKind !== 'agent' || source.targetId !== step.agentId) trainerFail('TRAINER_TARGET_MISMATCH', 'workflow frozen Agent reference differs from source target');
      frozenDependencies[version] = source.bundleSha256;
      dependencyBundles[source.bundleSha256] = { manifestContent: bundleManifestBytes(source).toString('utf8') };
    }
  }
  const bundle = resolveDefinition({ projectId, targetKind, targetId, revisionId, files, model, dependencyBundles, frozenDependencies });
  bundle.bundleSha256 = sha(bundle); assertBundle(bundle);
  return JSON.parse(JSON.stringify(bundle));
}
function resolveDefinition({ projectId, targetKind, targetId, revisionId, files, model, dependencyBundles = {}, frozenDependencies = {} }) {
  const selected = new Set(); const skills = Object.create(null); const tools = Object.create(null);
  const importedFiles = Object.create(null); const usedBundles = Object.create(null); const usedFrozen = Object.create(null); const sourceCache = new Map();
  const take = (p) => { if (!assetPath(p) || !Object.hasOwn(files, p)) trainerFail('TRAINER_DEPENDENCY_MISSING', `missing dependency: ${p}`); selected.add(p); return files[p]; };
  const parse = (p) => JSON.parse(take(p));
  const schemaFiles = Object.entries(files).filter(([p]) => assetPath(p) && p.endsWith('.schema.json'));
  const schemaIds = new Map(schemaFiles.map(([p, c]) => [JSON.parse(c).$id ?? `https://trainer.invalid/${p}`, p]));
  function takeSchema(p) {
    if (selected.has(p)) return;
    const schema = parse(p);
    const visit = (node) => {
      if (!node || typeof node !== 'object') return;
      for (const key of ['$ref', '$dynamicRef']) if (typeof node[key] === 'string' && !node[key].startsWith('#')) {
        const ref = node[key].split('#')[0]; const resolved = new URL(ref, schema.$id ?? `https://trainer.invalid/${p}`).href;
        const dependency = schemaIds.get(ref) ?? schemaIds.get(resolved) ?? (resolved.startsWith('https://trainer.invalid/') ? resolved.slice('https://trainer.invalid/'.length) : null);
        if (!dependency) trainerFail('TRAINER_DEPENDENCY_MISSING', `unregistered schema reference ${ref}`);
        takeSchema(dependency);
      }
      for (const [k, child] of Object.entries(node)) if (!['const', 'enum', 'default', 'examples'].includes(k)) visit(child);
    }; visit(schema);
  }
  const workflow = targetKind === 'workflow' ? parse(`workflows/${targetId}.json`) : null;
  const sourceSteps = workflow?.steps ?? [{ stepId: 'step-1', agentId: targetId, inputBindings: {} }];
  const steps = sourceSteps.map((step) => {
    if (step.agentVersion?.kind === 'frozen') {
      if (targetKind !== 'workflow') trainerFail('TRAINER_BUNDLE_INVALID', 'only a workflow can contain frozen Agent dependencies');
      const version = trainerId(step.agentVersion.frozenVersionId); const digest = frozenDependencies[version]; const descriptor = dependencyBundles[digest];
      if (!/^[a-f0-9]{64}$/.test(digest ?? '') || typeof descriptor?.manifestContent !== 'string' || trainerSha(Buffer.from(descriptor.manifestContent)) !== digest) trainerFail('TRAINER_INTEGRITY', 'missing or corrupt frozen source manifest');
      let source = sourceCache.get(digest);
      if (!source) {
        const manifest = JSON.parse(descriptor.manifestContent);
        if (manifest.targetKind !== 'agent' || manifest.dependencyBundles || manifest.frozenDependencies || manifest.bundleSha256) trainerFail('TRAINER_BUNDLE_INVALID', 'frozen dependency must be a standalone Agent manifest');
        source = { ...manifest, bundleSha256: digest }; assertBundle(source); sourceCache.set(digest, source);
      }
      if (source.projectId !== projectId || source.targetId !== step.agentId || source.steps.length !== 1) trainerFail('TRAINER_TARGET_MISMATCH', 'frozen dependency target/project mismatch');
      usedBundles[digest] = { manifestContent: descriptor.manifestContent }; usedFrozen[version] = digest;
      const prefix = `dependencies/${digest}/`; const key = (id) => `frozen-${digest}-${id}`; const sourceStep = source.steps[0];
      for (const entry of source.files) { const p = `${prefix}${entry.path}`; selected.add(p); importedFiles[p] = entry.content; }
      for (const id of sourceStep.skillRefs) {
        const skill = source.skills[id]; skills[key(id)] = { ...skill, entryRef: `${prefix}${skill.entryRef}`, referenceRefs: (skill.referenceRefs ?? []).map((p) => `${prefix}${p}`), scriptRefs: (skill.scriptRefs ?? []).map((p) => `${prefix}${p}`) };
      }
      for (const id of sourceStep.toolIds) { const tool = source.tools[id]; tools[key(id)] = { ...tool, scriptRef: `${prefix}${tool.scriptRef}` }; }
      if (step.outputSchemaRef) takeSchema(step.outputSchemaRef);
      return { ...sourceStep, stepId: step.stepId, agentId: step.agentId, instructionsRef: `${prefix}${sourceStep.instructionsRef}`,
        inputSchemaRef: `${prefix}${sourceStep.inputSchemaRef}`, outputSchemaRef: step.outputSchemaRef ?? `${prefix}${sourceStep.outputSchemaRef}`,
        skillRefs: sourceStep.skillRefs.map(key), toolIds: sourceStep.toolIds.map(key), inputBindings: step.inputBindings ?? {}, timeoutMs: step.timeoutMs ?? sourceStep.timeoutMs,
        model: sourceStep.model ?? source.model, sourceBundleSha256: digest, frozenVersionId: version };
    }
    const agent = parse(`agents/${trainerId(step.agentId)}/agent.json`);
    take(agent.instructionsRef); takeSchema(agent.inputSchemaRef); takeSchema(step.outputSchemaRef ?? agent.outputSchemaRef);
    // Agent definition also declares its own output contract, even when a step overrides it.
    takeSchema(agent.outputSchemaRef);
    for (const id of agent.skillRefs ?? []) {
      const skill = parse(`skills/${trainerId(id)}/skill.json`);
      for (const ref of [skill.entryRef, ...(skill.referenceRefs ?? []), ...(skill.scriptRefs ?? [])]) take(ref);
      skills[id] = skill;
    }
    for (const id of agent.toolIds ?? []) {
      const tool = parse(`tools/${trainerId(id)}.json`); take(tool.scriptRef); tools[id] = tool;
    }
    if (agent.model) modelCheck(agent.model);
    return { stepId: step.stepId, agentId: agent.agentId, instructionsRef: agent.instructionsRef, skillRefs: agent.skillRefs ?? [], inputSchemaRef: agent.inputSchemaRef,
      outputSchemaRef: step.outputSchemaRef ?? agent.outputSchemaRef, inputBindings: step.inputBindings ?? {}, toolIds: agent.toolIds ?? [], timeoutMs: step.timeoutMs ?? 120000, ...(agent.model ? { model: agent.model } : {}) };
  });
  const tests = [];
  for (const [p, text] of Object.entries(files)) if (p.startsWith('tests/') && p.endsWith('.json')) {
    const test = JSON.parse(text); if (test.targetKind === targetKind && test.targetId === targetId) { take(p); tests.push(test); }
  }
  const contentFor = (p) => Object.hasOwn(importedFiles, p) ? importedFiles[p] : files[p];
  const bundle = { schemaVersion: 1, runtimeApiVersion: 'trainer-api-v1', projectId, targetKind, targetId, revisionId, model: JSON.parse(JSON.stringify(model)),
    files: [...selected].sort().map((p) => ({ path: p, size: Buffer.byteLength(contentFor(p)), sha256: trainerSha(Buffer.from(contentFor(p))), content: contentFor(p) })), steps, skills, tools, tests,
    ...(Object.keys(usedBundles).length ? { dependencyBundles: usedBundles, frozenDependencies: usedFrozen } : {}) };
  return bundle;
}
export function freezeTarget(root, { projectId, targetKind, targetId, revisionId, bundle }) {
  if (!bundle) trainerFail('TRAINER_BUNDLE_REQUIRED', 'freeze requires a resolved bundle with pinned model configuration');
  assertBundle(bundle);
  if (bundle.projectId !== projectId || bundle.targetKind !== targetKind || bundle.targetId !== targetId || (revisionId && bundle.revisionId !== revisionId)) trainerFail('TRAINER_TARGET_MISMATCH', 'freeze target/revision differs from exact bundle');
  const frozenVersionId = `frozen-${randomUUID()}`; const directory = trainerProjectRoot(root, projectId);
  trainerWrite(directory, `versions/${frozenVersionId}/bundle-manifest.json`, bundleManifestBytes(bundle));
  const result = { frozenVersionId, bundleSha256: bundle.bundleSha256, revisionId: bundle.revisionId, targetKind, targetId };
  trainerWrite(directory, `versions/${frozenVersionId}/version.json`, trainerJson(result));
  return result;
}
export function loadFrozenBundle(root, { projectId, frozenVersionId }) {
  const directory = trainerProjectRoot(root, projectId); trainerId(frozenVersionId);
  const version = trainerRead(directory, 'versions', frozenVersionId, 'version.json');
  if (version.frozenVersionId !== frozenVersionId) trainerFail('TRAINER_INTEGRITY', 'frozen version identifier mismatch');
  const bytes = fs.readFileSync(trainerSafe(directory, 'versions', frozenVersionId, 'bundle-manifest.json'));
  if (trainerSha(bytes) !== version.bundleSha256) trainerFail('TRAINER_INTEGRITY', 'frozen manifest bytes changed');
  const bundle = { ...JSON.parse(bytes), bundleSha256: version.bundleSha256 }; assertBundle(bundle);
  if (bundle.projectId !== projectId || bundle.targetId !== version.targetId || bundle.targetKind !== version.targetKind || bundle.revisionId !== version.revisionId) trainerFail('TRAINER_INTEGRITY', 'frozen version binding mismatch');
  return bundle;
}

/** List verified completed snapshots; incomplete writes have no version marker. */
export function listFrozenVersions(root, { projectId, targetKind, targetId }) {
  if (targetKind !== undefined && !['agent', 'workflow'].includes(targetKind)) trainerFail('TRAINER_TARGET_INVALID', 'invalid frozen target kind');
  if (targetId !== undefined) trainerId(targetId);
  const directory = trainerProjectRoot(root, projectId); const versionsRoot = trainerSafe(directory, 'versions'); const versions = [];
  if (!fs.existsSync(versionsRoot)) return { projectId, versions };
  for (const name of fs.readdirSync(versionsRoot).filter((name) => name.startsWith('frozen-')).sort()) {
    trainerId(name);
    const marker = trainerSafe(versionsRoot, name, 'version.json');
    if (!fs.existsSync(marker)) continue;
    const bundle = loadFrozenBundle(root, { projectId, frozenVersionId: name });
    if ((targetKind && bundle.targetKind !== targetKind) || (targetId && bundle.targetId !== targetId)) continue;
    versions.push({ frozenVersionId: name, bundleSha256: bundle.bundleSha256, revisionId: bundle.revisionId, targetKind: bundle.targetKind, targetId: bundle.targetId });
  }
  return { projectId, versions };
}
