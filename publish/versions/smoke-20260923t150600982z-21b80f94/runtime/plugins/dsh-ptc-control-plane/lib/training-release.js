import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { sha256Bytes, buildReleaseFileEntries, digestReleaseEntries, verifyReleaseDirectory } from './release-integrity.js';
import { runHostCommand } from './host-command.js';
import { resolveTrainingModelChoice } from './training-model.js';

const ID = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/;
const PROFILE = /^[a-z][a-z0-9-]{1,63}$/;
const SHA = /^[a-f0-9]{64}$/;
const MANIFEST = 'release-manifest.json';
const POINTER = 'active-release.json';
const MAX_FILES = 1000;
const MAX_BYTES = 128 * 1024 * 1024;
const DRAFT_FILES = ['instructions.md', 'profile.yaml', 'output-contract.schema.json'];
const ARITHMETIC_PROFILES = Object.freeze(['ate-implementer', 'compile-diagnostician', 'evolution-expert',
  'method-expert', 'rule-reviewer', 'strategy-expert']);
const HASH_PROFILE_BATCH = String.raw`import contextlib, io, json, pathlib, runpy, sys
command=pathlib.Path(sys.argv[1]); jobs=json.loads(sys.argv[2]); reports=[]
sys.path.insert(0,str(command.parent))
for job in jobs:
 sys.argv=[str(command),job['path'],'--json']
 output=io.StringIO()
 with contextlib.redirect_stdout(output):
  try: runpy.run_path(str(command),run_name='__main__')
  except SystemExit as result:
   if result.code not in (None,0): raise
 report=json.loads(output.getvalue())
 reports.append({'path':job['path'],'sha256':report['sha256'],'view':report['view']})
print(json.dumps(reports))`;
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
function fail(message) { throw new Error(`smoke training release: ${message}`); }
function identity(value, label, pattern = ID) {
  if (typeof value !== 'string' || !pattern.test(value) || /[. ]$/.test(value)
    || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(value)) fail(`invalid ${label}`);
  return value;
}
function safe(root, ...segments) { return assertSafeRunPath(root, path.join(root, ...segments)); }
function releaseRoot(workspaceRoot) { return safe(path.resolve(workspaceRoot), 'publish'); }
function relative(value, label) {
  if (typeof value !== 'string' || !value || value.includes('\\') || value.includes(':') || value.startsWith('/')
    || value.split('/').some(part => !part || part === '.' || part === '..' || /[. ]$/.test(part)
      || /[\x00-\x1f<>"|?*]/.test(part)
      || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(part))) fail(`unsafe ${label}`);
  return value;
}
function bytes(root, relativePath) {
  const file = safe(root, ...relative(relativePath, 'source path').split('/'));
  const descriptor = fs.openSync(file, fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0));
  try {
    const stat = fs.fstatSync(descriptor);
    const current = fs.lstatSync(file);
    if (!stat.isFile() || stat.nlink !== 1 || stat.dev !== current.dev || stat.ino !== current.ino
      || stat.size > MAX_BYTES) fail(`unsafe source file: ${relativePath}`);
    return fs.readFileSync(descriptor);
  } finally { fs.closeSync(descriptor); }
}
function json(root, name) {
  try { return JSON.parse(bytes(root, name).toString('utf8').replace(/^\uFEFF/, '')); }
  catch (error) { fail(`invalid ${name}: ${error.message}`); }
}
async function verifyProfilePlaintext(workspace, materialRoot, bindings) {
  const command = safe(workspace, 'scripts', 'hash_ate_plaintext.py');
  const jobs = bindings.map(binding => ({ path: safe(materialRoot, ...binding.path.split('/')) }));
  const result = await runHostCommand('python', ['-X', 'utf8', '-c', HASH_PROFILE_BATCH,
    command, JSON.stringify(jobs)], { cwd: workspace, timeoutMs: 30_000 });
  if (result.status !== 'passed' || result.exitCode !== 0) fail('approved profile plaintext hash command failed');
  let reports;
  try { reports = JSON.parse(result.stdout); } catch { fail('approved profile hash report invalid'); }
  if (!Array.isArray(reports) || reports.length !== bindings.length) fail('approved profile hash coverage incomplete');
  for (let index = 0; index < bindings.length; index += 1) {
    if (reports[index].path !== jobs[index].path || reports[index].view !== 'python-plaintext'
      || reports[index].sha256 !== bindings[index].sha256 || !SHA.test(reports[index].sha256)) {
      fail(`trained profile plaintext hash changed: ${bindings[index].path}`);
    }
  }
}
function lock(root, action) {
  fs.mkdirSync(root, { recursive: true });
  const directory = safe(root, '.publisher-lock');
  try { fs.mkdirSync(directory); }
  catch (error) { if (error.code === 'EEXIST') fail('publisher lock exists'); throw error; }
  try { return action(); } finally { fs.rmdirSync(directory); }
}
async function lockAsync(root, action) {
  fs.mkdirSync(root, { recursive: true });
  const directory = safe(root, '.publisher-lock');
  try { fs.mkdirSync(directory); }
  catch (error) { if (error.code === 'EEXIST') fail('publisher lock exists'); throw error; }
  try { return await action(); } finally { fs.rmdirSync(directory); }
}
function runIdentity(workspace, runId, target, registry) {
  const prefix = `Training_Materials/runs/${identity(runId, 'runId')}`;
  const context = json(workspace, `${prefix}/run.json`);
  const state = json(workspace, `${prefix}/state.json`);
  if (context.schemaVersion !== 1 || context.runId !== runId || context.mode !== 'training'
    || context.releaseId !== null || context.projectId !== null
    || context.profileSource !== 'draft' || context.orchestrationSource !== 'draft'
    || path.resolve(workspace, context.artifactRoot ?? '') !== safe(workspace, ...prefix.split('/'))
    || state.schemaVersion !== 1 || state.runId !== runId || state.purpose !== 'smoke-training'
    || state.status !== 'completed' || state.outcome?.mode !== 'SMOKE_ONLY'
    || state.outcome?.businessGatePassed !== false) fail(`run is not a completed smoke identity: ${runId}`);
  if (target.kind === 'profile') {
    if (state.target?.kind !== 'profile' || state.target.profileId !== target.profileId) fail('profile smoke ownership mismatch');
    const receipt = json(workspace, `${prefix}/evidence/profile-smoke.json`);
    if (receipt.schemaVersion !== 1 || receipt.kind !== 'ptc-profile-smoke' || receipt.runId !== runId
      || receipt.profileId !== target.profileId || receipt.status !== 'completed'
      || receipt.mode !== 'SMOKE_ONLY' || receipt.businessGatePassed !== false
      || receipt.profileInstructionsValidated !== false || receipt.modelDispatched !== true
      || receipt.answer !== 3 || !SHA.test(receipt.responseSha256 ?? '')
      || !SHA.test(receipt.profileSnapshotSha256 ?? '')
      || receipt.responsePath !== `${prefix}/evidence/profile-smoke-child.json`
      || sha256Bytes(bytes(workspace, receipt.responsePath)) !== receipt.responseSha256
      || (json(workspace, receipt.responsePath)?.structured?.answer
        ?? json(workspace, receipt.responsePath)?.answer) !== 3) fail('profile smoke receipt invalid');
    const evidenceRelative = `${prefix}/evidence/profile-smoke.json`;
    if (state.outcome.evidence !== evidenceRelative
      || state.outcome.evidenceSha256 !== sha256Bytes(bytes(workspace, evidenceRelative))) fail('profile smoke state/receipt binding invalid');
    const snapshotName = `${prefix}/profile/snapshot.json`;
    const snapshot = json(workspace, snapshotName);
    if (receipt.profileSnapshotPath !== snapshotName
      || receipt.profileSnapshotSha256 !== sha256Bytes(bytes(workspace, snapshotName))
      || snapshot.kind !== 'ptc-profile-smoke-snapshot' || snapshot.runId !== runId
      || snapshot.profileId !== target.profileId || !Array.isArray(snapshot.files)
      || !equal(snapshot.files.map(file => path.posix.basename(file.path)).sort(), [...DRAFT_FILES].sort())) {
      fail('trained profile snapshot is not bound to its completed smoke receipt');
    }
    for (const file of snapshot.files) {
      if (file.source !== `team/expert-profiles/${target.profileId}/${path.posix.basename(file.path)}`
        || file.path !== `${prefix}/profile/${path.posix.basename(file.path)}`
        || file.view !== 'python-plaintext' || !SHA.test(file.sha256 ?? '')) {
        fail('trained profile source provenance is invalid');
      }
    }
    return ['run.json', 'state.json', 'evidence/profile-smoke.json', 'evidence/profile-smoke-child.json',
      'profile/snapshot.json', ...DRAFT_FILES.map(file => `profile/${file}`)].map(name => `${prefix}/${name}`);
  }
  const stages = registry.stateMachine?.filter(stage => stage !== 'COMPLETE');
  if (state.target?.kind !== 'pipeline' || state.target.fromStage !== stages?.[0]
    || state.target.toStage !== stages?.at(-1) || !equal(state.target.stages, stages)) fail('pipeline smoke is not full authoritative chain');
  const progress = json(workspace, `${prefix}/simple-orchestration.json`);
  if (progress.runId !== runId || progress.status !== 'completed' || progress.mode !== 'SMOKE_ONLY'
    || progress.smokePassed !== true || progress.businessGatePassed !== false
    || !equal(progress.stages?.map(item => item.stage), stages)
    || !Array.isArray(progress.auxiliaryTasks)) fail('pipeline smoke record incomplete');
  const evidencePaths = [];
  const arithmeticSessions = new Set();
  function verifyTask(task, stageName) {
    const runRoot = safe(workspace, ...prefix.split('/'));
    const absolute = assertSafeRunPath(workspace, task.childEvidencePath);
    const runRelative = path.relative(runRoot, absolute);
    const evidenceRelative = path.relative(workspace, absolute).split(path.sep).join('/');
    if (task.status !== 'completed' || !PROFILE.test(task.profileId ?? '')
      || !SHA.test(task.childEvidenceSha256 ?? '')
      || typeof task.childEvidencePath !== 'string'
      || runRelative === '..' || runRelative.startsWith(`..${path.sep}`) || path.isAbsolute(runRelative)
      || sha256Bytes(bytes(workspace, evidenceRelative)) !== task.childEvidenceSha256) {
      fail(`child smoke receipt invalid: ${stageName}`);
    }
    const child = json(workspace, evidenceRelative);
    if (child.runId !== runId || child.dispatchId !== task.dispatchId || child.role !== task.role
      || child.stage !== task.stage || child.executionKind !== task.executionKind) fail('child dispatch identity mismatch');
    if (task.executionKind === 'arithmetic-child') {
      if (task.answer !== 3 || task.captainVerified !== true
        || child.answer !== 3 || typeof child.childSessionId !== 'string' || !child.childSessionId
        || task.childSessionId !== child.childSessionId || arithmeticSessions.has(child.childSessionId)) {
        fail(`Captain arithmetic check failed: ${stageName}`);
      }
      arithmeticSessions.add(child.childSessionId);
    } else if (!['dft-delivery', 'statistic-only'].includes(task.executionKind)
      || task.answer !== null || task.captainVerified !== false || stageName !== 'INPUT_SYNC') {
      fail(`unapproved source task kind: ${stageName}`);
    }
    evidencePaths.push(evidenceRelative);
  }
  for (const stage of progress.stages) {
    if (stage.owner !== registry.stages?.[stage.stage]?.owner || stage.gate !== registry.stages[stage.stage].gate
      || stage.status !== 'completed' || stage.smokePassed !== true || stage.businessGatePassed !== false
      || stage.businessGateResult !== null || !Array.isArray(stage.tasks)
      || !equal(stage.tasks.map(task => task.role), stage.stage === 'INPUT_SYNC'
        ? ['dft-expert', 'schematic-expert'] : [stage.owner])) fail(`stage smoke record invalid: ${stage.stage}`);
    for (const task of stage.tasks) {
      if (task.profileId !== progress.profileBindings?.[task.role]?.profileId
        || task.profileDigest !== progress.profileBindings[task.role].profileDigest
        || task.profileVersion !== progress.profileBindings[task.role].profileVersion) fail('child profile binding changed');
      verifyTask(task, stage.stage);
    }
  }
  if (progress.auxiliaryTasks.length !== 1 || progress.auxiliaryTasks[0].role !== 'evolution-expert') {
    fail('evolution-expert auxiliary smoke missing');
  }
  verifyTask(progress.auxiliaryTasks[0], 'AUXILIARY');
  if (progress.auxiliaryTasks[0].profileId !== progress.profileBindings?.['evolution-expert']?.profileId) {
    fail('auxiliary profile binding changed');
  }
  if (state.outcome.smokePassed !== true) fail('pipeline state does not confirm completed smoke');
  return [...['run.json', 'state.json', 'simple-orchestration.json'].map(name => `${prefix}/${name}`),
    ...new Set(evidencePaths)];
}
function sourceRunIdentity(workspace, runId, kind) {
  const prefix = `Training_Materials/runs/${identity(runId, 'source runId')}`;
  const context = json(workspace, `${prefix}/run.json`);
  const state = json(workspace, `${prefix}/state.json`);
  if (context.runId !== runId || context.mode !== 'training' || context.releaseId !== null
    || context.projectId !== null || path.resolve(workspace, context.artifactRoot ?? '') !== safe(workspace, ...prefix.split('/'))
    || state.runId !== runId || state.status !== 'completed') fail(`${kind} source run is not complete`);
  let evidence;
  if (kind === 'dft') {
    const normalizedEvidence = typeof state.outcome?.evidence === 'string'
      ? state.outcome.evidence.replace(/\\/g, '/') : null;
    if (state.target?.kind !== 'profile' || state.target.profileId !== 'ptc-dft-expert'
      || !['UNCHANGED', 'CREATED', 'OVERWRITTEN'].includes(state.outcome?.mode)
      || !normalizedEvidence?.startsWith(`${prefix}/evidence/`)) fail('DFT source outcome invalid');
    evidence = normalizedEvidence;
  } else {
    if (state.purpose !== 'schematic-statistic-only' || state.outcome?.mode !== 'STATISTIC_ONLY'
      || state.outcome.report?.gatePassed !== false || state.outcome.report?.modelDispatched !== false) {
      fail('statistic-only source outcome invalid');
    }
    const report = state.outcome.report;
    evidence = path.relative(workspace, report.path).split(path.sep).join('/');
    if (evidence !== `${prefix}/evidence/component-statistic-only.json`
      || sha256Bytes(bytes(workspace, evidence)) !== report.sha256) fail('statistic-only source evidence binding invalid');
  }
  const profilePrefix = kind === 'dft' ? `${prefix}/profile` : `${prefix}/profiles/ptc-schematic-expert`;
  for (const file of DRAFT_FILES) bytes(workspace, `${profilePrefix}/${file}`);
  return [`${prefix}/run.json`, `${prefix}/state.json`, evidence,
    ...DRAFT_FILES.map(file => `${profilePrefix}/${file}`)];
}
function sources(workspace, { profileRunIds, dftRunId, statisticRunId, pipelineRunId, scriptPaths }) {
  if (!profileRunIds || typeof profileRunIds !== 'object' || Array.isArray(profileRunIds)
    || !Object.keys(profileRunIds).length) fail('profileRunIds required');
  const profiles = Object.keys(profileRunIds).sort();
  if (!equal(profiles, [...ARITHMETIC_PROFILES].sort())
    || new Set(Object.values(profileRunIds)).size !== profiles.length) fail('all six arithmetic profile smoke runs are required');
  const registry = json(workspace, 'team/ptc/ptc_stage_registry.json');
  const stages = registry.stateMachine?.filter(stage => stage !== 'COMPLETE');
  if (!Array.isArray(stages) || stages.length !== 7 || stages[0] !== 'INPUT_SYNC'
    || stages.at(-1) !== 'COMPILE' || new Set(stages).size !== stages.length
    || stages.some(stage => typeof registry.stages?.[stage]?.owner !== 'string'
      || typeof registry.stages?.[stage]?.gate !== 'string')) fail('invalid authoritative registry');
  const gateScripts = stages.map(stage => relative(registry.stages[stage].gate, 'gate script'));
  if (gateScripts.some(name => !/^scripts\/[A-Za-z0-9_.-]+\.(py|mjs|js)$/.test(name))) fail('gate scripts must remain in scripts/');
  if (!Array.isArray(scriptPaths) || !scriptPaths.length || scriptPaths.some(name =>
    typeof name !== 'string' || !/^(scripts\/[A-Za-z0-9_./-]+|plugins\/dsh-ptc-control-plane\/lib\/[A-Za-z0-9_./-]+)$/.test(name))) fail('explicit smoke runtime scriptPaths required');
  const profileEvidence = profiles.flatMap(profileId => runIdentity(workspace, profileRunIds[profileId], { kind: 'profile', profileId }, registry));
  const sourceEvidence = [...sourceRunIdentity(workspace, dftRunId, 'dft'),
    ...sourceRunIdentity(workspace, statisticRunId, 'statistic')];
  const pipelineEvidence = runIdentity(workspace, pipelineRunId, { kind: 'pipeline' }, registry);
  const progress = json(workspace, `Training_Materials/runs/${pipelineRunId}/simple-orchestration.json`);
  const inputKinds = progress.stages[0]?.tasks?.map(task => task.executionKind).sort();
  if (!equal(inputKinds, ['dft-delivery', 'statistic-only'])
    || progress.stages[0].tasks.find(task => task.executionKind === 'dft-delivery')?.profileId !== 'ptc-dft-expert'
    || progress.stages[0].tasks.find(task => task.executionKind === 'statistic-only')?.profileId !== 'ptc-schematic-expert') {
    fail('INPUT_SYNC must bind DFT and statistic-only paths');
  }
  const usedProfiles = [...new Set([...progress.stages.flatMap(stage => stage.tasks), ...progress.auxiliaryTasks]
    .filter(task => task.executionKind === 'arithmetic-child').map(task => task.profileId))].sort();
  if (!equal(usedProfiles, profiles)) fail('single-agent smoke evidence does not cover every pipeline participant');
  const roleProfiles = Object.fromEntries(Object.entries(progress.profileBindings ?? {}).map(([role, binding]) => [role, binding.profileId]));
  if (!equal(Object.values(roleProfiles).sort(), [...profiles, 'ptc-dft-expert', 'ptc-schematic-expert'].sort())) {
    fail('pipeline role bindings do not cover exactly the eight participating profiles');
  }
  const mapping = new Map();
  const put = (source, target) => {
    relative(source, 'source path'); relative(target, 'snapshot path');
    if (mapping.has(target.toLowerCase())) fail(`duplicate snapshot path: ${target}`);
    mapping.set(target.toLowerCase(), { source, target });
  };
  for (const profileId of profiles) for (const file of DRAFT_FILES) {
    put(`Training_Materials/runs/${profileRunIds[profileId]}/profile/${file}`, `profiles/${profileId}/${file}`);
  }
  for (const file of DRAFT_FILES) {
    put(`Training_Materials/runs/${dftRunId}/profile/${file}`, `profiles/ptc-dft-expert/${file}`);
    put(`Training_Materials/runs/${statisticRunId}/profiles/ptc-schematic-expert/${file}`,
      `profiles/ptc-schematic-expert/${file}`);
  }
  put('team/ptc/ptc_stage_registry.json', 'orchestration/ptc_stage_registry.json');
  for (const source of [...new Set([...gateScripts, ...scriptPaths])].sort()) put(source, `runtime/${source}`);
  for (const source of [...profileEvidence, ...sourceEvidence, ...pipelineEvidence]) {
    const tail = source.split('/').slice(3).join('/');
    const runId = source.split('/')[2];
    put(source, `evidence/${runId}/${tail}`);
  }
  const entries = [...mapping.values()].sort((a, b) => a.target < b.target ? -1 : a.target > b.target ? 1 : 0);
  if (entries.length > MAX_FILES) fail('too many snapshot files');
  const profilePlaintextBindings = profiles.flatMap(profileId =>
    json(workspace, `Training_Materials/runs/${profileRunIds[profileId]}/profile/snapshot.json`).files
      .map(file => ({ path: file.path, sha256: file.sha256, target: `profiles/${profileId}/${path.posix.basename(file.path)}` })));
  return { entries, profiles, stages, profileRunIds: Object.fromEntries(profiles.map(name => [name, profileRunIds[name]])),
    dftRunId, statisticRunId, pipelineRunId, roleProfiles, profilePlaintextBindings };
}
function readPointer(root) {
  const file = safe(root, POINTER);
  if (!fs.existsSync(file)) return null;
  const pointer = JSON.parse(bytes(root, POINTER).toString('utf8'));
  if (pointer.schemaVersion !== 1 || pointer.kind !== 'SMOKE_ONLY'
    || !SHA.test(pointer.bundleDigest ?? '') || !Number.isFinite(Date.parse(pointer.activatedAt))) fail('invalid active training pointer');
  identity(pointer.releaseId, 'releaseId');
  if (pointer.previousReleaseId !== null) identity(pointer.previousReleaseId, 'previousReleaseId');
  return pointer;
}
function verified(root, releaseId) {
  const directory = safe(root, identity(releaseId, 'releaseId'));
  const manifest = json(directory, MANIFEST);
  if (manifest.schemaVersion !== 1 || manifest.kind !== 'SMOKE_ONLY'
    || (manifest.releaseId !== releaseId && !releaseId.startsWith('stage-'))
    || manifest.realBusinessGatesPassed !== false || manifest.outputUse !== 'diagnostic-only'
    || manifest.verification?.kind !== 'ptc-smoke-evaluation' || manifest.verification.status !== 'passed'
    || !SHA.test(manifest.bundleDigest ?? '') || !Array.isArray(manifest.files)) fail('invalid training release manifest');
  const actual = buildReleaseFileEntries(directory);
  if (!equal(actual, manifest.files) || digestReleaseEntries(actual) !== manifest.bundleDigest) fail('training snapshot file list or digest mismatch');
  const integrity = verifyReleaseDirectory(directory, manifest);
  if (!integrity.ok) fail(integrity.errors.join('; '));
  if (fs.readdirSync(directory).filter(name => name !== MANIFEST).sort().join('|') !== 'evidence|orchestration|profiles|runtime') fail('unexpected training release entries');
  const source = Object.fromEntries(actual.map(entry => [entry.path, entry]));
  if (!source['orchestration/ptc_stage_registry.json'] || !Array.isArray(manifest.profileIds)
    || !equal(manifest.profileIds, ARITHMETIC_PROFILES)
    || !equal(manifest.stages, json(directory, 'orchestration/ptc_stage_registry.json').stateMachine?.filter(name => name !== 'COMPLETE'))
    || !equal(Object.keys(manifest.profileRunIds ?? {}).sort(), manifest.profileIds)
    || !source[`evidence/${manifest.pipelineRunId}/simple-orchestration.json`]
    || !equal(Object.values(manifest.roleProfiles ?? {}).sort(),
      [...manifest.profileIds, 'ptc-dft-expert', 'ptc-schematic-expert'].sort())) fail('training scope coverage invalid');
  for (const profileId of [...manifest.profileIds, 'ptc-dft-expert', 'ptc-schematic-expert']) {
    for (const file of DRAFT_FILES) if (!source[`profiles/${profileId}/${file}`]) fail('profile draft snapshot missing');
  }
  for (const profileId of manifest.profileIds) {
    const runId = manifest.profileRunIds[profileId];
    if (!source[`evidence/${runId}/run.json`] || !source[`evidence/${runId}/state.json`]
      || !source[`evidence/${runId}/evidence/profile-smoke.json`]
      || !source[`evidence/${runId}/evidence/profile-smoke-child.json`]
      || !source[`evidence/${runId}/profile/snapshot.json`]) fail('profile smoke evidence missing');
    const state = json(directory, `evidence/${runId}/state.json`);
    const receipt = json(directory, `evidence/${runId}/evidence/profile-smoke.json`);
    const child = json(directory, `evidence/${runId}/evidence/profile-smoke-child.json`);
    if (state.runId !== runId || state.target?.profileId !== profileId
      || state.status !== 'completed' || state.outcome?.mode !== 'SMOKE_ONLY'
      || receipt.runId !== runId || receipt.profileId !== profileId || receipt.answer !== 3
      || child.structured?.answer !== 3
      || source[`evidence/${runId}/evidence/profile-smoke-child.json`].sha256 !== receipt.responseSha256) {
      fail('frozen profile smoke identity changed');
    }
    const snapshot = json(directory, `evidence/${runId}/profile/snapshot.json`);
    if (receipt.profileSnapshotSha256 !== source[`evidence/${runId}/profile/snapshot.json`].sha256
      || snapshot.runId !== runId || snapshot.profileId !== profileId) fail('frozen trained profile manifest changed');
    for (const file of DRAFT_FILES) {
      if (source[`profiles/${profileId}/${file}`]?.sha256
        !== source[`evidence/${runId}/profile/${file}`]?.sha256) fail('published profile differs from trained snapshot');
    }
  }
  if (!source[`evidence/${manifest.dftRunId}/run.json`] || !source[`evidence/${manifest.dftRunId}/state.json`]
    || !source[`evidence/${manifest.statisticRunId}/run.json`]
    || !source[`evidence/${manifest.statisticRunId}/state.json`]) fail('DFT/statistic source evidence missing');
  for (const file of DRAFT_FILES) {
    if (source[`profiles/ptc-dft-expert/${file}`]?.sha256
      !== source[`evidence/${manifest.dftRunId}/profile/${file}`]?.sha256
      || source[`profiles/ptc-schematic-expert/${file}`]?.sha256
      !== source[`evidence/${manifest.statisticRunId}/profiles/ptc-schematic-expert/${file}`]?.sha256) {
      fail('DFT/statistic profile differs from its source run');
    }
  }
  const progress = json(directory, `evidence/${manifest.pipelineRunId}/simple-orchestration.json`);
  const roleProfiles = Object.fromEntries(Object.entries(progress.profileBindings ?? {})
    .map(([role, binding]) => [role, binding.profileId]));
  if (progress.runId !== manifest.pipelineRunId || progress.status !== 'completed'
    || progress.mode !== 'SMOKE_ONLY' || progress.businessGatePassed !== false
    || !equal(roleProfiles, manifest.roleProfiles)
    || !equal(progress.stages?.map(stage => stage.stage), manifest.stages)) {
    fail('frozen pipeline role/stage binding changed');
  }
  if (manifest.verification.candidateDigest !== manifest.bundleDigest
    || !equal(manifest.verification.profileIds, manifest.profileIds)
    || !equal(manifest.verification.stages, manifest.stages)) fail('smoke evaluation is not bound to this bundle');
  return { directory, snapshotRoot: directory, manifest };
}
function active(root) {
  const pointer = readPointer(root);
  if (!pointer) return null;
  const release = verified(safe(root, 'versions'), pointer.releaseId);
  if (pointer.bundleDigest !== release.manifest.bundleDigest) fail('active training pointer digest mismatch');
  return { pointer, release };
}
function switchPointer(root, release, previousReleaseId) {
  const pointer = { schemaVersion: 1, kind: 'SMOKE_ONLY', releaseId: release.manifest.releaseId,
    bundleDigest: release.manifest.bundleDigest, previousReleaseId, activatedAt: new Date().toISOString() };
  const temporary = safe(root, `.pointer-${randomUUID()}.tmp`);
  try {
    fs.writeFileSync(temporary, `${JSON.stringify(pointer, null, 2)}\n`, { flag: 'wx' });
    const fd = fs.openSync(temporary, 'r+');
    try { fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
    fs.renameSync(temporary, safe(root, POINTER));
  } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
  return pointer;
}

/** Captain-side candidate evaluator. It reads only the copied immutable
 * candidate, recomputes every relevant SHA-256 and checks numeric child JSON.
 * The publisher still checks this verdict against the candidate digest. */
export async function verifySmokeCandidate({ workspaceRoot, snapshotRoot, candidateDigest,
  profileIds, profileRunIds, dftRunId, statisticRunId, pipelineRunId, stages }) {
  const workspace = path.resolve(workspaceRoot);
  const snapshot = assertSafeRunPath(workspace, snapshotRoot);
  const files = buildReleaseFileEntries(snapshot);
  if (digestReleaseEntries(files) !== candidateDigest || !equal(profileIds, ARITHMETIC_PROFILES)
    || !equal(Object.keys(profileRunIds ?? {}).sort(), profileIds)) fail('candidate identity changed');
  const fileMap = new Map(files.map(file => [file.path, file]));
  const plaintextBindings = [];
  const frozen = name => {
    if (!fileMap.has(name)) fail(`candidate proof missing: ${name}`);
    return json(snapshot, name);
  };
  const usedSessions = new Set();
  for (const profileId of profileIds) {
    const runId = identity(profileRunIds[profileId], 'profile runId');
    const state = frozen(`evidence/${runId}/state.json`);
    const receipt = frozen(`evidence/${runId}/evidence/profile-smoke.json`);
    const childName = `evidence/${runId}/evidence/profile-smoke-child.json`;
    const child = frozen(childName);
    const snapshotName = `evidence/${runId}/profile/snapshot.json`;
    const trained = frozen(snapshotName);
    if (state.runId !== runId || state.status !== 'completed' || state.purpose !== 'smoke-training'
      || state.target?.profileId !== profileId || state.outcome?.mode !== 'SMOKE_ONLY'
      || state.outcome.businessGatePassed !== false || receipt.runId !== runId
      || receipt.profileId !== profileId || receipt.status !== 'completed'
      || receipt.businessGatePassed !== false || receipt.answer !== 3
      || receipt.modelDispatched !== true || child.stopReason !== 'completed'
      || typeof child.structured?.answer !== 'number' || child.structured.answer !== 3
      || receipt.responseSha256 !== fileMap.get(childName).sha256
      || receipt.profileSnapshotSha256 !== fileMap.get(snapshotName).sha256
      || trained.profileId !== profileId || trained.runId !== runId
      || typeof receipt.childSessionId !== 'string' || !receipt.childSessionId
      || usedSessions.has(receipt.childSessionId)) fail(`single-agent smoke proof failed: ${profileId}`);
    for (const file of DRAFT_FILES) {
      if (fileMap.get(`profiles/${profileId}/${file}`)?.sha256
        !== fileMap.get(`evidence/${runId}/profile/${file}`)?.sha256) {
        fail(`candidate profile differs from trained version: ${profileId}`);
      }
      const item = trained.files.find(entry => path.posix.basename(entry.path) === file);
      if (!item || !SHA.test(item.sha256 ?? '') || item.view !== 'python-plaintext') {
        fail(`trained profile provenance missing: ${profileId}/${file}`);
      }
      plaintextBindings.push({ path: `profiles/${profileId}/${file}`, sha256: item.sha256 });
    }
    usedSessions.add(receipt.childSessionId);
  }
  const dftState = frozen(`evidence/${dftRunId}/state.json`);
  const statisticState = frozen(`evidence/${statisticRunId}/state.json`);
  if (dftState.status !== 'completed' || dftState.target?.profileId !== 'ptc-dft-expert'
    || !['UNCHANGED', 'CREATED', 'OVERWRITTEN'].includes(dftState.outcome?.mode)
    || statisticState.status !== 'completed' || statisticState.purpose !== 'schematic-statistic-only'
    || statisticState.outcome?.mode !== 'STATISTIC_ONLY'
    || statisticState.outcome.report?.gatePassed !== false) fail('DFT/statistic source proof failed');
  for (const file of DRAFT_FILES) {
    if (fileMap.get(`profiles/ptc-dft-expert/${file}`)?.sha256
      !== fileMap.get(`evidence/${dftRunId}/profile/${file}`)?.sha256
      || fileMap.get(`profiles/ptc-schematic-expert/${file}`)?.sha256
      !== fileMap.get(`evidence/${statisticRunId}/profiles/ptc-schematic-expert/${file}`)?.sha256) {
      fail('DFT/statistic profile source snapshot changed');
    }
  }
  const pipelineState = frozen(`evidence/${pipelineRunId}/state.json`);
  const progress = frozen(`evidence/${pipelineRunId}/simple-orchestration.json`);
  if (pipelineState.status !== 'completed' || pipelineState.purpose !== 'smoke-training'
    || pipelineState.outcome?.mode !== 'SMOKE_ONLY' || pipelineState.outcome.businessGatePassed !== false
    || progress.runId !== pipelineRunId || progress.mode !== 'SMOKE_ONLY' || progress.status !== 'completed'
    || progress.smokePassed !== true || progress.businessGatePassed !== false
    || !equal(progress.stages?.map(stage => stage.stage), stages)
    || !Array.isArray(progress.auxiliaryTasks) || progress.auxiliaryTasks.length !== 1
    || progress.auxiliaryTasks[0].role !== 'evolution-expert') fail('full-chain smoke proof failed');
  const seenProfiles = new Set();
  const verifyTask = task => {
    const absolute = assertSafeRunPath(workspace, task.childEvidencePath);
    const expectedRoot = safe(workspace, 'Training_Materials', 'runs', pipelineRunId);
    const relativePath = path.relative(expectedRoot, absolute).split(path.sep).join('/');
    if (relativePath.startsWith('../') || relativePath === '..' || path.isAbsolute(relativePath)) fail('child evidence escapes source run');
    const name = `evidence/${pipelineRunId}/${relativePath}`;
    const child = frozen(name);
    if (task.status !== 'completed' || task.childEvidenceSha256 !== fileMap.get(name).sha256
      || child.runId !== pipelineRunId || child.dispatchId !== task.dispatchId
      || child.role !== task.role || child.stage !== task.stage
      || child.executionKind !== task.executionKind) fail('full-chain child binding failed');
    if (task.executionKind === 'arithmetic-child') {
      if (task.answer !== 3 || task.captainVerified !== true || child.answer !== 3
        || typeof child.answer !== 'number' || !child.childSessionId
        || child.childSessionId !== task.childSessionId || usedSessions.has(child.childSessionId)) {
        fail('full-chain numeric child verification failed');
      }
      usedSessions.add(child.childSessionId);
      seenProfiles.add(task.profileId);
    } else if (task.stage !== 'INPUT_SYNC' || task.answer !== null || task.captainVerified !== false) {
      fail('source task misrepresented as arithmetic');
    }
  };
  for (const stage of progress.stages) {
    const definition = json(snapshot, 'orchestration/ptc_stage_registry.json').stages?.[stage.stage];
    if (stage.owner !== definition?.owner || stage.gate !== definition.gate
      || stage.status !== 'completed' || stage.smokePassed !== true
      || stage.businessGatePassed !== false || stage.businessGateResult !== null
      || !equal(stage.tasks?.map(task => task.role), stage.stage === 'INPUT_SYNC'
        ? ['dft-expert', 'schematic-expert'] : [stage.owner])) fail('stage order or owner proof failed');
    stage.tasks.forEach(verifyTask);
  }
  verifyTask(progress.auxiliaryTasks[0]);
  if (!equal([...seenProfiles].sort(), profileIds)) fail('full-chain smoke omitted a profile');
  await verifyProfilePlaintext(workspace, snapshot, plaintextBindings);
  return { kind: 'ptc-smoke-evaluation', status: 'passed', candidateDigest,
    realBusinessGatesPassed: false, profileIds, stages };
}

/** A diagnostic smoke package only. verifySmoke must independently inspect the
 * frozen candidate and bind its verdict to the exact candidate digest. */
export async function stageTrainingRelease({ workspaceRoot, releaseId, createdBy, profileRunIds,
  dftRunId, statisticRunId, pipelineRunId, scriptPaths, verifySmoke }) {
  const workspace = path.resolve(workspaceRoot);
  identity(releaseId, 'releaseId');
  if (typeof createdBy !== 'string' || !createdBy.trim() || typeof verifySmoke !== 'function') fail('publisher identity and trusted smoke verifier required');
  const selection = sources(workspace, { profileRunIds, dftRunId, statisticRunId, pipelineRunId, scriptPaths });
  await verifyProfilePlaintext(workspace, workspace, selection.profilePlaintextBindings);
  const sourceBytes = selection.entries.map(entry => ({ ...entry, data: bytes(workspace, entry.source) }));
  const root = releaseRoot(workspace);
  return lockAsync(root, async () => {
    const prior = active(root);
    if (fs.existsSync(safe(root, 'versions', releaseId))) fail('release identity already exists');
    const stagingId = `stage-${randomUUID()}`;
    const stagingRoot = safe(root, '.staging');
    fs.mkdirSync(stagingRoot, { recursive: true });
    const directory = safe(stagingRoot, stagingId);
    fs.mkdirSync(directory);
    try {
      for (const entry of sourceBytes) {
        const target = safe(directory, ...entry.target.split('/'));
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.writeFileSync(target, entry.data, { flag: 'wx' });
      }
      const files = buildReleaseFileEntries(directory);
      if (files.length !== sourceBytes.length || files.reduce((sum, item) => sum + item.size, 0) > MAX_BYTES
        || sourceBytes.some(entry => {
          const found = files.find(item => item.path === entry.target);
          return !found || found.sha256 !== sha256Bytes(entry.data);
        })) fail('staged bytes differ from source');
      const bundleDigest = digestReleaseEntries(files);
      const verdict = await verifySmoke({ workspaceRoot: workspace, snapshotRoot: directory,
        candidateDigest: bundleDigest, profileIds: [...selection.profiles],
        profileRunIds: { ...selection.profileRunIds }, dftRunId, statisticRunId,
        pipelineRunId, stages: [...selection.stages] });
      if (verdict?.kind !== 'ptc-smoke-evaluation' || verdict.status !== 'passed'
        || verdict.candidateDigest !== bundleDigest || verdict.realBusinessGatesPassed !== false
        || !equal(verdict.profileIds, selection.profiles) || !equal(verdict.stages, selection.stages)) fail('trusted smoke evaluation failed or stale');
      if (!equal(buildReleaseFileEntries(directory), files)) fail('snapshot changed during smoke evaluation');
      if (sourceBytes.some(entry => sha256Bytes(bytes(workspace, entry.source)) !== sha256Bytes(entry.data))) fail('source changed during snapshot');
      const manifest = { schemaVersion: 1, kind: 'SMOKE_ONLY', outputUse: 'diagnostic-only',
        realBusinessGatesPassed: false, releaseId, createdAt: new Date().toISOString(), createdBy,
        previousReleaseId: prior?.pointer.releaseId ?? null, profileIds: selection.profiles,
        profileRunIds: selection.profileRunIds, dftRunId, statisticRunId, pipelineRunId,
        roleProfiles: selection.roleProfiles, stages: selection.stages,
        files, bundleDigest,
        verification: { kind: 'ptc-smoke-evaluation', status: 'passed', candidateDigest: bundleDigest,
          profileIds: selection.profiles, stages: selection.stages } };
      fs.writeFileSync(safe(directory, MANIFEST), `${JSON.stringify(manifest, null, 2)}\n`, { flag: 'wx' });
      // Temporarily verify through the same immutable reader without adopting it.
      const staged = verified(stagingRoot, stagingId);
      if (staged.manifest.releaseId !== releaseId) fail('staged release identity mismatch');
      return { stagingId, manifest };
    } catch (error) { fs.rmSync(directory, { recursive: true }); throw error; }
  });
}

export function activateStagedTrainingRelease({ workspaceRoot, stagingId }) {
  if (typeof stagingId !== 'string' || !/^stage-[a-f0-9-]{36}$/.test(stagingId)) fail('invalid stagingId');
  const root = releaseRoot(workspaceRoot);
  return lock(root, () => {
    const directory = safe(root, '.staging', stagingId);
    const staged = verified(safe(root, '.staging'), stagingId);
    const prior = active(root);
    if ((prior?.pointer.releaseId ?? null) !== staged.manifest.previousReleaseId) fail('active training release changed; restage');
    const versionRoot = safe(root, 'versions');
    fs.mkdirSync(versionRoot, { recursive: true });
    const target = safe(versionRoot, staged.manifest.releaseId);
    if (fs.existsSync(target)) fail('release identity already exists');
    fs.renameSync(directory, target);
    return switchPointer(root, verified(versionRoot, staged.manifest.releaseId), prior?.pointer.releaseId ?? null);
  });
}

/** Pass releaseId from a delivery run's immutable identity to remain pinned even
 * if the active training pointer later changes. Never resolves business release. */
export function loadTrainingRelease({ workspaceRoot, releaseId }) {
  const root = releaseRoot(workspaceRoot);
  if (releaseId !== undefined) return verified(safe(root, 'versions'), identity(releaseId, 'releaseId'));
  const current = active(root);
  if (!current) fail('no active smoke training release');
  return current.release;
}

export function rollbackTrainingRelease({ workspaceRoot, releaseId }) {
  const root = releaseRoot(workspaceRoot);
  return lock(root, () => {
    const current = active(root);
    if (!current) fail('no active smoke training release');
    const wanted = releaseId ?? current.pointer.previousReleaseId;
    if (!wanted || wanted === current.pointer.releaseId) fail('no different rollback target');
    return switchPointer(root, verified(safe(root, 'versions'), wanted), current.pointer.releaseId);
  });
}

export function listTrainingReleases({ workspaceRoot }) {
  const root = releaseRoot(workspaceRoot);
  if (!fs.existsSync(root)) return { active: null, releases: [] };
  const current = active(root);
  const directory = safe(root, 'versions');
  if (!fs.existsSync(directory)) return { active: current?.pointer ?? null, releases: [] };
  const releases = fs.readdirSync(directory, { withFileTypes: true })
    .filter(entry => entry.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))
    .map(entry => {
      try { return { releaseId: entry.name, valid: true, manifest: verified(directory, entry.name).manifest }; }
      catch (error) { return { releaseId: entry.name, valid: false, error: error.message }; }
    });
  return { active: current?.pointer ?? null, releases };
}

const ACTIVE_RUNS = new Set();
const ARITHMETIC_PROMPT = '1+2等于几，把答案写在JSON里';
function atomicJson(file, value) {
  const temporary = `${file}.${randomUUID()}.tmp`;
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  try { fs.renameSync(temporary, file); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
function runJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  return sha256Bytes(fs.readFileSync(file));
}
function testItemsOf(items) {
  if (!Array.isArray(items) || !items.length || items.some(item => typeof item !== 'string' || !/^TM\d+$/.test(item))
    || new Set(items).size !== items.length) fail('unique explicit testItems required');
  return [...items].sort((a, b) => Number(a.slice(2)) - Number(b.slice(2)));
}
function profileDigest(release, profileId) {
  const entries = release.manifest.files.filter(entry => entry.path.startsWith(`profiles/${profileId}/`));
  if (entries.length !== DRAFT_FILES.length) fail(`frozen profile is incomplete: ${profileId}`);
  return digestReleaseEntries(entries);
}
function deadline(action, timeoutMs, label) {
  const controller = new AbortController();
  let timer;
  const timeout = new Promise((resolve, reject) => {
    timer = setTimeout(() => { controller.abort(); reject(new Error(`${label} exceeded ${timeoutMs} ms`)); }, timeoutMs);
  });
  return Promise.race([Promise.resolve().then(() => action(controller.signal)), timeout])
    .finally(() => clearTimeout(timer));
}
async function abortable(action, signal, disposeLate) {
  if (signal?.aborted) throw signal.reason ?? new Error('published smoke cancelled');
  const operation = Promise.resolve().then(action);
  if (!signal) return operation;
  let abort;
  const stopped = new Promise((resolve, reject) => {
    abort = () => reject(signal.reason ?? new Error('published smoke cancelled'));
    signal.addEventListener('abort', abort, { once: true });
  });
  try { return await Promise.race([operation, stopped]); }
  catch (error) {
    if (signal.aborted) operation.then(value => { try { disposeLate?.(value); } catch {} }, () => {});
    throw error;
  } finally { signal.removeEventListener('abort', abort); }
}

/** Actually dispatch against one pinned smoke snapshot. The two injected host
 * adapters must respect signal and may write only under outputRoot. The host,
 * not a child claim, checks each numeric structured.answer. No business gate is
 * invoked or certified by this function. Interrupted runs are never resumed. */
export async function executePublishedSmoke({ workspaceRoot, runId, releaseId, testItems,
  dispatchArithmetic, dispatchSource, childTimeoutMs = 8 * 60_000, signal }) {
  const workspace = path.resolve(workspaceRoot);
  identity(runId, 'runId');
  if (typeof dispatchArithmetic !== 'function' || typeof dispatchSource !== 'function') {
    fail('real arithmetic and source dispatch adapters required');
  }
  if (!Number.isFinite(childTimeoutMs) || childTimeoutMs <= 0 || childTimeoutMs > 8 * 60_000) {
    fail('child timeout exceeds execution contract');
  }
  const items = testItemsOf(testItems);
  const release = loadTrainingRelease({ workspaceRoot: workspace, releaseId });
  const pinnedReleaseId = release.manifest.releaseId;
  const pinnedDigest = release.manifest.bundleDigest;
  const registry = json(release.snapshotRoot, 'orchestration/ptc_stage_registry.json');
  const stages = registry.stateMachine.filter(stage => stage !== 'COMPLETE');
  if (!equal(stages, release.manifest.stages)) fail('frozen stage chain changed');
  const root = releaseRoot(workspace);
  const outputRoot = safe(root, 'runs', runId);
  if (ACTIVE_RUNS.has(outputRoot)) fail('published smoke run already active');
  fs.mkdirSync(safe(root, 'runs'), { recursive: true });
  fs.mkdirSync(outputRoot); // reserves identity; never adopt an old or partial run
  ACTIVE_RUNS.add(outputRoot);
  const now = new Date().toISOString();
  const context = { schemaVersion: 1, kind: 'ptc-published-smoke-run', mode: 'published-smoke',
    scope: 'SMOKE_ONLY', realBusinessGatesPassed: false, runId, releaseId: pinnedReleaseId,
    releaseDigest: pinnedDigest, testItems: items, createdAt: now,
    artifactRoot: path.relative(workspace, outputRoot).split(path.sep).join('/') };
  runJson(safe(outputRoot, 'run.json'), context);
  const stateFile = safe(outputRoot, 'state.json');
  let state = { schemaVersion: 1, runId, releaseId: pinnedReleaseId, status: 'running',
    mode: 'SMOKE_ONLY', businessGatePassed: false, createdAt: now, updatedAt: now,
    stages: [], auxiliaryTasks: [], reason: null };
  runJson(stateFile, state);
  const usedSessions = new Set();
  function save() {
    state.updatedAt = new Date().toISOString();
    atomicJson(stateFile, state);
  }
  async function dispatch(stage, role, executionKind, index) {
    if (signal?.aborted) fail('published smoke stopped by user');
    const current = loadTrainingRelease({ workspaceRoot: workspace, releaseId: pinnedReleaseId });
    if (current.manifest.bundleDigest !== pinnedDigest) fail('pinned release changed during run');
    const profileId = current.manifest.roleProfiles[role];
    if (!profileId) fail(`frozen role mapping missing: ${role}`);
    const profileRoot = safe(current.snapshotRoot, 'profiles', profileId);
    const dispatchId = `${runId}:${stage}:${role}:1`;
    const evidenceRoot = safe(outputRoot, 'evidence');
    fs.mkdirSync(evidenceRoot, { recursive: true });
    const request = Object.freeze({ workspaceRoot: workspace, outputRoot, evidenceRoot,
      snapshotRoot: current.snapshotRoot, releaseId: pinnedReleaseId, releaseDigest: pinnedDigest,
      runId, stage, role, profileId, profileRoot, profileDigest: profileDigest(current, profileId),
      dispatchId, testItems: [...items], executionKind,
      ...(executionKind === 'arithmetic-child' ? { prompt: ARITHMETIC_PROMPT,
        persona: `PTC published smoke child for ${profileId}. This is not business execution. Do not use tools, files, project facts, private inputs or expert instructions.`,
        outputSchema: { type: 'object', properties: { answer: { type: 'number' } },
          required: ['answer'], additionalProperties: false } } : {}) });
    const adapter = executionKind === 'arithmetic-child' ? dispatchArithmetic : dispatchSource;
    const returned = await deadline(childSignal => {
      const abort = () => childSignal.throwIfAborted();
      if (signal?.aborted) abort();
      const linked = new AbortController();
      const onStop = () => linked.abort(signal?.reason ?? new Error('published smoke stopped by user'));
      const onDeadline = () => linked.abort(childSignal.reason ?? new Error('child deadline exceeded'));
      signal?.addEventListener('abort', onStop, { once: true });
      childSignal.addEventListener('abort', onDeadline, { once: true });
      return Promise.resolve(adapter({ ...request, signal: linked.signal })).finally(() => {
        signal?.removeEventListener('abort', onStop);
        childSignal.removeEventListener('abort', onDeadline);
      });
    }, childTimeoutMs, `${stage}/${role}`);
    if (!returned || typeof returned !== 'object' || returned.status !== 'completed'
      || returned.runId !== runId || returned.dispatchId !== dispatchId
      || returned.releaseId !== pinnedReleaseId || returned.executionKind !== executionKind) {
      fail(`adapter did not complete the exact frozen dispatch: ${stage}/${role}`);
    }
    let answer = null;
    let captainVerified = false;
    if (executionKind === 'arithmetic-child') {
      if (typeof returned.childSessionId !== 'string' || !returned.childSessionId
        || usedSessions.has(returned.childSessionId) || returned.result?.stopReason !== 'completed'
        || typeof returned.result?.structured?.answer !== 'number'
        || returned.result.structured.answer !== 3) fail(`Captain numeric answer check failed: ${stage}/${role}`);
      usedSessions.add(returned.childSessionId);
      answer = 3; captainVerified = true;
    } else if (executionKind === 'dft-delivery') {
      if (returned.dftGateStatus !== 'ready' || returned.dftGateExitCode !== 0) fail('published DFT source is not gate-ready');
    } else if (returned.statisticMode !== 'STATISTIC_ONLY' || returned.businessGatePassed !== false) {
      fail('published schematic source is not statistic-only');
    }
    if (executionKind !== 'arithmetic-child') {
      if (!Array.isArray(returned.artifacts) || !returned.artifacts.length) fail('published source artifacts missing');
      for (const artifact of returned.artifacts) {
        if (typeof artifact?.path !== 'string' || !SHA.test(artifact.sha256 ?? '')) fail('invalid published source artifact binding');
        const absolute = assertSafeRunPath(workspace, artifact.path);
        const inside = path.relative(outputRoot, absolute);
        if (inside === '..' || inside.startsWith(`..${path.sep}`) || path.isAbsolute(inside)
          || sha256Bytes(bytes(workspace, path.relative(workspace, absolute).split(path.sep).join('/'))) !== artifact.sha256) {
          fail('published source artifact escapes run or changed');
        }
      }
    }
    const rawFile = safe(evidenceRoot, `${index}-${role}-raw.json`);
    const rawSha256 = runJson(rawFile, returned);
    const receipt = { schemaVersion: 1, kind: 'ptc-published-smoke-task', mode: 'SMOKE_ONLY',
      businessGatePassed: false, runId, releaseId: pinnedReleaseId, releaseDigest: pinnedDigest,
      stage, role, profileId, profileDigest: request.profileDigest, dispatchId, executionKind,
      childSessionId: returned.childSessionId ?? null, answer, captainVerified,
      rawPath: path.relative(workspace, rawFile).split(path.sep).join('/'), rawSha256,
      status: 'completed', finishedAt: new Date().toISOString() };
    const receiptFile = safe(evidenceRoot, `${index}-${role}-receipt.json`);
    runJson(receiptFile, receipt);
    return receipt;
  }
  try {
    let index = 0;
    for (const stage of stages) {
      const roles = stage === 'INPUT_SYNC' ? ['dft-expert', 'schematic-expert'] : [registry.stages[stage].owner];
      const tasks = [];
      for (const role of roles) {
        const kind = role === 'dft-expert' ? 'dft-delivery'
          : role === 'schematic-expert' ? 'statistic-only' : 'arithmetic-child';
        tasks.push(await dispatch(stage, role, kind, index++));
        state.stages = [...state.stages.filter(item => item.stage !== stage),
          { stage, owner: registry.stages[stage].owner, gate: registry.stages[stage].gate,
            status: 'running', smokePassed: false, businessGatePassed: false, tasks }];
        save();
      }
      state.stages.at(-1).status = 'completed';
      state.stages.at(-1).smokePassed = true;
      save();
    }
    state.auxiliaryTasks = [await dispatch('SMOKE_AUXILIARY', 'evolution-expert', 'arithmetic-child', index++)];
    state.status = 'completed';
    state.smokePassed = true;
    state.finishedAt = new Date().toISOString();
    save();
  } catch (error) {
    state.status = 'blocked';
    state.smokePassed = false;
    state.reason = error?.message ?? String(error);
    state.finishedAt = new Date().toISOString();
    save();
  } finally { ACTIVE_RUNS.delete(outputRoot); }
  return { context, state, outputRoot };
}

const PROJECT_PATHS = String.raw`import json, pathlib
root=pathlib.Path.cwd()
info=json.loads((root/'Project_Info.json').read_text(encoding='utf-8-sig'))
config=json.loads((root/'project_config.json').read_text(encoding='utf-8-sig'))
print(json.dumps({'workbook':info['inputs']['dft'],'schematic':info['inputs']['schematic'],
 'projectDir':info['projectDir'],
 'output':info['roots']['output'],'confirmed':str(root/'project/DALI/Input_GlobalMaterial/sch_confirmed.json'),
 'channelmap':config['inputs']['channelmap']}))`;

/** DSH adapter for the published diagnostic replay. The arithmetic child gets
 * no private material, tools, or profile instructions; its identity is bound to
 * the frozen profile digest supplied by executePublishedSmoke. DFT is a
 * read-only ready gate plus copied products. Schematic runs only the fixed
 * Component-Statistic producer, with output inside publish/runs. */
export function createPublishedSmokeDispatcher(ctx, workspaceRoot, { modelChoice = 'default',
  runHost = runHostCommand } = {}) {
  const workspace = path.resolve(workspaceRoot);
  let configured;
  async function projectPaths(signal) {
    if (configured) return configured;
    const result = await runHost('python', ['-X', 'utf8', '-c', PROJECT_PATHS],
      { cwd: workspace, timeoutMs: 30_000, signal });
    if (result.status !== 'passed' || result.exitCode !== 0) fail('approved project configuration is unreadable');
    const data = JSON.parse(result.stdout);
    for (const key of ['workbook', 'schematic', 'output', 'confirmed', 'channelmap', 'projectDir']) {
      if (typeof data[key] !== 'string' || !data[key]) fail(`approved ${key} path missing`);
    }
    configured = data;
    return data;
  }
  return {
    async dispatchArithmetic(request) {
      if (!ctx?.agents?.create || !ctx?.subagents?.start
        || !ctx?.agentDefaultModel?.currentSelection) fail('DSH child services unavailable');
      if (request.signal?.aborted) fail('published child cancelled');
      const selection = resolveTrainingModelChoice(modelChoice, ctx.agentDefaultModel.currentSelection());
      const agentOptions = { provider: selection.provider, model: selection.model, maxTokens: 256 };
      const parent = await abortable(() => ctx.agents.create({ sessionId: `session-published-smoke-${randomUUID()}`,
        meta: { cwd: workspace }, agentOptions }),
      request.signal, handle => { Promise.resolve(handle?.dispose?.()).catch(() => {}); });
      let child;
      try {
        await abortable(() => parent.agent.whenIdle(), request.signal);
        if (request.signal?.aborted) fail('published child cancelled');
        child = await abortable(() => ctx.subagents.start('spawn', { label: `PTC published smoke ${request.role} ${request.runId}`,
          parent: parent.agent, signal: request.signal, agentOptions, maxDepth: 1,
          toolFilter: { allow: [] }, persona: request.persona,
          prompt: [{ type: 'text', text: request.prompt }], outputSchema: request.outputSchema }),
        request.signal, handle => {
          Promise.resolve(handle?.result).catch(() => {});
          Promise.resolve(handle?.dispose?.()).catch(() => {});
        });
        if (typeof child.id !== 'string' || !child.id) fail('DSH returned no published child identity');
        const result = await abortable(() => child.result, request.signal);
        return { status: 'completed', executionKind: request.executionKind,
          runId: request.runId, dispatchId: request.dispatchId, releaseId: request.releaseId,
          childSessionId: child.id, result };
      } finally {
        Promise.resolve(child?.result).catch(() => {});
        await Promise.resolve(child?.dispose?.()).catch(() => {});
        await Promise.resolve(parent.dispose?.()).catch(() => {});
      }
    },
    async dispatchSource(request) {
      const config = await projectPaths(request.signal);
      const artifacts = [];
      if (request.executionKind === 'dft-delivery') {
        for (const tm of request.testItems) {
          const sourceDirectory = safe(workspace, ...`${config.output}/dft/${tm}`.split('/'));
          const workbook = safe(workspace, ...config.workbook.split('/'));
          const args = ['-X', 'utf8', 'scripts/validate_dft_outputs.py', '--tm', tm,
            '--workbook', workbook, '--output-dir', sourceDirectory];
          const result = await runHost('python', args, { cwd: workspace, timeoutMs: 30_000, signal: request.signal });
          if (result.status !== 'passed' || result.exitCode !== 0) fail(`published DFT gate did not pass: ${tm}`);
          const report = JSON.parse(result.stdout);
          if (report.gate !== 'DFT_OUTPUT' || report.status !== 'ready'
            || !SHA.test(report.canonicalInput?.sha256 ?? '')
            || !Array.isArray(report.requiredOutputs) || report.requiredOutputs.length !== 3
            || report.missingOrStaleOutputs?.length !== 0) fail(`invalid published DFT gate result: ${tm}`);
          const destination = safe(request.outputRoot, 'input-sync', 'dft', tm);
          fs.mkdirSync(destination, { recursive: true });
          for (const source of report.requiredOutputs) {
            if (typeof source !== 'string' || path.dirname(path.resolve(source)) !== sourceDirectory) {
              fail('DFT gate reported output outside the approved directory');
            }
            const target = safe(destination, path.basename(source));
            fs.copyFileSync(assertSafeRunPath(workspace, source), target, fs.constants.COPYFILE_EXCL);
            const digest = sha256Bytes(fs.readFileSync(target));
            if (digest !== sha256Bytes(fs.readFileSync(assertSafeRunPath(workspace, source)))) {
              fail('DFT product changed during published smoke copy');
            }
            artifacts.push({ path: target, sha256: digest });
          }
          const recheck = await runHost('python', args, { cwd: workspace, timeoutMs: 30_000, signal: request.signal });
          if (recheck.status !== 'passed' || recheck.exitCode !== 0) fail(`DFT product changed after smoke copy: ${tm}`);
          const current = JSON.parse(recheck.stdout);
          if (current.status !== 'ready' || current.canonicalInput?.sha256 !== report.canonicalInput.sha256) {
            fail(`DFT canonical source changed after smoke copy: ${tm}`);
          }
        }
        return { status: 'completed', executionKind: request.executionKind,
          runId: request.runId, dispatchId: request.dispatchId, releaseId: request.releaseId,
          dftGateStatus: 'ready', dftGateExitCode: 0, artifacts };
      }
      if (request.executionKind !== 'statistic-only') fail('unsupported published source kind');
      const source = safe(workspace, ...config.schematic.split('/'));
      const confirmed = assertSafeRunPath(workspace, config.confirmed);
      const projectDir = path.resolve(workspace, config.projectDir);
      const channelmap = assertSafeRunPath(projectDir, config.channelmap);
      const destination = safe(request.outputRoot, 'input-sync', 'schematic', 'Component-Statistic.txt');
      fs.mkdirSync(path.dirname(destination), { recursive: true });
      const args = ['-X', 'utf8', 'scripts/generate_component_statistic_only.py',
        '--source', source, '--confirmed', confirmed, '--channelmap', channelmap, '--out', destination];
      const result = await runHost('python', args, { cwd: workspace, timeoutMs: 30_000, signal: request.signal });
      if (result.status !== 'passed' || result.exitCode !== 0) fail('published statistic-only producer failed');
      const report = JSON.parse(result.stdout);
      if (report.status !== 'STATISTIC_ONLY' || report.outputPath !== destination
        || !SHA.test(report.outputSha256 ?? '') || sha256Bytes(fs.readFileSync(destination)) !== report.outputSha256) {
        fail('published statistic-only output binding failed');
      }
      artifacts.push({ path: destination, sha256: report.outputSha256 });
      return { status: 'completed', executionKind: request.executionKind,
        runId: request.runId, dispatchId: request.dispatchId, releaseId: request.releaseId,
        statisticMode: 'STATISTIC_ONLY', businessGatePassed: false, artifacts };
    },
  };
}
