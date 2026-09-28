import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { sha256Bytes } from './release-integrity.js';
import { trainingAddressBook } from './training-paths.js';

const PROFILE = /^[a-z][a-z0-9-]{1,63}$/;
const ROLE = /^[a-z][a-z0-9-]{1,63}$/;
const ISSUE_ID = /^[a-z0-9][a-z0-9-]{0,127}$/;
const EVIDENCE_ROOTS = new Set(['evidence', 'receipts', 'verification', 'input-sync',
  'strategy', 'method', 'review', 'implementation', 'compile', 'trials']);

function fail(message) { throw new Error(`training issue: ${message}`); }
function readJson(bytes, label) {
  try { return JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, '')); }
  catch { fail(`invalid ${label}`); }
}
function readOwnedFile(root, file) {
  assertSafeRunPath(root, file);
  const descriptor = fs.openSync(file, fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0));
  try {
    const opened = fs.fstatSync(descriptor);
    const current = fs.lstatSync(file);
    if (!opened.isFile() || opened.nlink !== 1 || opened.dev !== current.dev || opened.ino !== current.ino) {
      fail('evidence must be an ordinary unlinked file');
    }
    return fs.readFileSync(descriptor);
  } finally { fs.closeSync(descriptor); }
}
function runFiles(workspaceRoot, runId) {
  const root = path.resolve(workspaceRoot);
  const runRoot = assertSafeRunPath(root, path.join(root, trainingAddressBook(runId).runRoot));
  const contextBytes = readOwnedFile(root, path.join(runRoot, 'run.json'));
  const stateBytes = readOwnedFile(root, path.join(runRoot, 'state.json'));
  const context = readJson(contextBytes, 'run context');
  const state = readJson(stateBytes, 'run state');
  if (context.schemaVersion !== 1 || context.mode !== 'training' || context.runId !== runId
      || context.releaseId !== null || context.projectId !== null
      || context.profileSource !== 'draft' || context.orchestrationSource !== 'draft'
      || typeof context.artifactRoot !== 'string' || path.isAbsolute(context.artifactRoot)
      || path.resolve(root, context.artifactRoot ?? '') !== runRoot
      || state.schemaVersion !== 1 || state.runId !== runId
      || !['completed', 'blocked'].includes(state.status)) fail('run is not a completed or blocked training identity');
  return { root, runRoot, contextBytes, stateBytes, state };
}
function validateOwner(run, profileId, sourceRole) {
  if (!PROFILE.test(profileId ?? '')) fail('invalid profileId');
  if (run.state.target?.kind === 'profile') {
    if (run.state.target.profileId !== profileId || sourceRole !== undefined) fail('profile does not own this run');
    return null;
  }
  if (run.state.target?.kind !== 'pipeline' || !ROLE.test(sourceRole ?? '')) {
    fail('pipeline issue requires an explicit source role');
  }
  const manifest = readJson(readOwnedFile(run.root, path.join(run.runRoot, 'pipeline-material-manifest.json')),
    'pipeline material manifest');
  if (manifest.runId !== run.state.runId || manifest.ownerProfiles?.[sourceRole] !== profileId) {
    fail('profile does not own the source role in this run');
  }
  if (run.state.purpose === 'schematic-statistic-only') {
    if (sourceRole !== 'schematic-expert') fail('statistic-only issue belongs to schematic-expert');
  } else {
    const progressFile = path.join(run.runRoot, 'pipeline-progress.json');
    const progress = readJson(readOwnedFile(run.root, progressFile), 'pipeline progress');
    const stages = run.state.target.stages ?? [];
    const registry = readJson(readOwnedFile(run.root, path.join(run.runRoot, 'pipeline-registry.json')),
      'pipeline registry');
    const included = progress.sourceRoles?.includes(sourceRole)
      || stages.some(stage => registry.stages?.[stage]?.owner === sourceRole);
    if (progress.runId !== run.state.runId || !included) fail('source role did not participate in this run');
  }
  return sourceRole;
}
function evidencePath(run, relativePath) {
  if (typeof relativePath !== 'string' || !relativePath || relativePath.includes('\\')
      || path.posix.isAbsolute(relativePath) || /^[A-Za-z]:/.test(relativePath)) fail('invalid relative evidence path');
  const segments = relativePath.split('/');
  if (segments.length < 2 || segments.some(segment => !segment || segment === '.' || segment === '..')
      || !EVIDENCE_ROOTS.has(segments[0])) fail('evidence must be a generated run-owned file');
  const file = assertSafeRunPath(run.root, path.join(run.runRoot, ...segments));
  const relative = path.relative(run.runRoot, file);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) fail('evidence escapes run');
  return file;
}
function evidenceEntries(run, paths) {
  if (!Array.isArray(paths) || paths.length > 20 || new Set(paths).size !== paths.length) {
    fail('evidencePaths must be a unique array of at most 20 paths');
  }
  return [...paths].sort().map(relativePath => {
    const bytes = readOwnedFile(run.root, evidencePath(run, relativePath));
    return { path: relativePath, sha256: sha256Bytes(bytes), sizeBytes: bytes.length };
  });
}
function ownershipBindings(run) {
  if (run.state.target?.kind !== 'pipeline') return [];
  const names = run.state.purpose === 'schematic-statistic-only'
    ? ['pipeline-material-manifest.json']
    : ['pipeline-material-manifest.json', 'pipeline-progress.json', 'pipeline-registry.json'];
  return names.map(name => {
    const bytes = readOwnedFile(run.root, path.join(run.runRoot, name));
    return { path: name, sha256: sha256Bytes(bytes), sizeBytes: bytes.length };
  });
}
function shortText(value, label, maximum) {
  if (typeof value !== 'string' || !value.trim() || value.length > maximum || /[\u0000-\u0008\u000B\u000C\u000E-\u001F]/.test(value)) {
    fail(`${label} must be nonempty text of at most ${maximum} characters`);
  }
  return value.trim();
}
function issueFile(root, issueId) {
  if (typeof issueId !== 'string' || !ISSUE_ID.test(issueId)) fail('invalid issueId');
  return assertSafeRunPath(root, path.join(root, 'Training_Materials', 'training-issues', `${issueId}.json`));
}

/** Create a local, immutable issue. options.issueId is for caller idempotency; collisions fail closed. */
export function createTrainingIssue(workspaceRoot, input, options = {}) {
  const run = runFiles(workspaceRoot, input?.runId);
  const profileId = input?.profileId;
  const sourceRole = validateOwner(run, profileId, input?.sourceRole);
  const title = shortText(input?.title, 'title', 160);
  const description = shortText(input?.description, 'description', 4000);
  const evidence = evidenceEntries(run, input?.evidencePaths ?? []);
  const ownership = ownershipBindings(run);
  const issueId = options.issueId ?? `issue-${randomUUID()}`;
  const file = issueFile(run.root, issueId);
  const createdAt = options.now instanceof Date ? options.now.toISOString() : new Date().toISOString();
  const body = { schemaVersion: 1, kind: 'ptc-training-issue', issueId, createdAt,
    runId: input.runId, runStatus: run.state.status, profileId, sourceRole,
    title, description, contextSha256: sha256Bytes(run.contextBytes),
    stateSha256: sha256Bytes(run.stateBytes), ownership, evidence,
    disposition: 'proposal-only', publicationClaim: false };
  const issue = { ...body, bodySha256: sha256Bytes(Buffer.from(JSON.stringify(body), 'utf8')) };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  assertSafeRunPath(run.root, file);
  fs.writeFileSync(file, `${JSON.stringify(issue, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
  return { file, issue };
}

/** Recheck the bound terminal run and exact on-disk evidence bytes. */
export function readTrainingIssue(workspaceRoot, issueId) {
  const root = path.resolve(workspaceRoot);
  const file = issueFile(root, issueId);
  const issue = readJson(readOwnedFile(root, file), 'issue');
  const { bodySha256, ...body } = issue;
  if (issue.schemaVersion !== 1 || issue.kind !== 'ptc-training-issue' || issue.issueId !== issueId
      || issue.disposition !== 'proposal-only' || issue.publicationClaim !== false
      || bodySha256 !== sha256Bytes(Buffer.from(JSON.stringify(body), 'utf8'))) fail('invalid issue identity');
  const run = runFiles(root, issue.runId);
  if (issue.runStatus !== run.state.status || issue.contextSha256 !== sha256Bytes(run.contextBytes)
      || issue.stateSha256 !== sha256Bytes(run.stateBytes)
      || validateOwner(run, issue.profileId, issue.sourceRole ?? undefined) !== issue.sourceRole) {
    fail('bound run identity changed');
  }
  const actual = evidenceEntries(run, issue.evidence?.map(entry => entry.path));
  if (JSON.stringify(actual) !== JSON.stringify(issue.evidence)) fail('evidence changed after issue creation');
  if (JSON.stringify(ownershipBindings(run)) !== JSON.stringify(issue.ownership)) {
    fail('ownership evidence changed after issue creation');
  }
  return { file, issue };
}

/** List only verified local issues; a tampered record fails the whole read. */
export function listTrainingIssues(workspaceRoot, { runId, profileId } = {}) {
  const root = path.resolve(workspaceRoot);
  if (runId !== undefined) trainingAddressBook(runId);
  if (profileId !== undefined && (typeof profileId !== 'string' || !PROFILE.test(profileId))) {
    fail('invalid profileId filter');
  }
  const directory = assertSafeRunPath(root, path.join(root, 'Training_Materials', 'training-issues'));
  if (!fs.existsSync(directory)) return [];
  if (!fs.lstatSync(directory).isDirectory()) fail('issue ledger is not a directory');
  return fs.readdirSync(directory).filter(name => name.endsWith('.json')).sort().map(name => {
    const issueId = name.slice(0, -5);
    return readTrainingIssue(root, issueId).issue;
  }).filter(issue => (runId === undefined || issue.runId === runId)
      && (profileId === undefined || issue.profileId === profileId));
}
