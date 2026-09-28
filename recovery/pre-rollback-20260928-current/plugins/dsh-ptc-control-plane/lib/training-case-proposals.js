import fs from 'node:fs';
import path from 'node:path';
import { assertSafeRunPath } from './run-context.js';
import { sha256Bytes } from './release-integrity.js';
import { readTrainingIssue } from './training-issues.js';
import { trainingAddressBook } from './training-paths.js';

const CASE_ID = /^case-[a-z0-9][a-z0-9-]{0,127}$/;
const ISSUE_ID = /^[a-z0-9][a-z0-9-]{0,127}$/;
const GENERATED_ROOTS = new Set(['evidence', 'receipts', 'verification', 'input-sync',
  'strategy', 'method', 'review', 'implementation', 'compile', 'trials']);

function fail(message) { throw new Error(`training case proposal: ${message}`); }
function ordinaryBytes(root, file) {
  assertSafeRunPath(root, file);
  const descriptor = fs.openSync(file, fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0));
  try {
    const opened = fs.fstatSync(descriptor);
    const current = fs.lstatSync(file);
    if (!opened.isFile() || opened.nlink !== 1 || opened.dev !== current.dev || opened.ino !== current.ino) {
      fail('bound file must be an ordinary unlinked file');
    }
    return fs.readFileSync(descriptor);
  } finally { fs.closeSync(descriptor); }
}
function parse(bytes, label) {
  try { return JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, '')); }
  catch { fail(`invalid ${label}`); }
}
function text(value, label, max) {
  if (typeof value !== 'string' || !value.trim() || value.length > max
      || /[\u0000-\u0008\u000B\u000C\u000E-\u001F]/.test(value)) {
    fail(`${label} must be nonempty text of at most ${max} characters`);
  }
  return value.trim();
}
function proposalFile(root, caseId) {
  if (typeof caseId !== 'string' || !CASE_ID.test(caseId)) fail('invalid caseId');
  return assertSafeRunPath(root, path.join(root, 'Training_Materials', 'case-proposals', `${caseId}.json`));
}
function fileBinding(root, runRoot, relativePath) {
  if (typeof relativePath !== 'string' || relativePath.includes('\\') || path.posix.isAbsolute(relativePath)
      || /^[A-Za-z]:/.test(relativePath)) fail('invalid run evidence path');
  const parts = relativePath.split('/');
  if (!parts.length || parts.some(part => !part || part === '.' || part === '..')) fail('invalid run evidence path');
  if (!['run.json', 'state.json', 'pipeline-material-manifest.json', 'pipeline-progress.json',
    'pipeline-registry.json'].includes(relativePath) && (parts.length < 2 || !GENERATED_ROOTS.has(parts[0]))) {
    fail('only run identity or generated run evidence may be bound');
  }
  const file = assertSafeRunPath(root, path.join(runRoot, ...parts));
  const inside = path.relative(runRoot, file);
  if (!inside || inside === '..' || inside.startsWith(`..${path.sep}`) || path.isAbsolute(inside)) {
    fail('evidence escapes its training run');
  }
  const bytes = ordinaryBytes(root, file);
  return { path: relativePath, sha256: sha256Bytes(bytes), sizeBytes: bytes.length };
}
function referencedOutcomePath(root, runRoot, value) {
  if (typeof value !== 'string' || !value) return null;
  const absolute = assertSafeRunPath(root, path.isAbsolute(value) ? value : path.join(root, value));
  const relative = path.relative(runRoot, absolute).split(path.sep).join('/');
  if (!relative.startsWith('evidence/')) fail('terminal receipt is outside generated run evidence');
  return relative;
}
function currentBindings(root, issue) {
  const runRoot = assertSafeRunPath(root, path.join(root, trainingAddressBook(issue.runId).runRoot));
  const stateBytes = ordinaryBytes(root, path.join(runRoot, 'state.json'));
  const state = parse(stateBytes, 'run state');
  if (state.runId !== issue.runId || !['completed', 'blocked'].includes(state.status)) {
    fail('run is not a verified terminal training run');
  }
  const paths = new Set(['run.json', 'state.json', ...(issue.evidence ?? []).map(entry => entry.path)]);
  if (state.target?.kind === 'pipeline') {
    paths.add('pipeline-material-manifest.json');
    if (state.purpose !== 'schematic-statistic-only') {
      paths.add('pipeline-progress.json');
      paths.add('pipeline-registry.json');
    }
  }
  const outcomePath = referencedOutcomePath(root, runRoot,
    state.outcome?.evidence ?? state.outcome?.report?.path);
  if (outcomePath) paths.add(outcomePath);
  const bindings = [...paths].sort().map(item => fileBinding(root, runRoot, item));
  let blockedProgressEvidence = false;
  if (state.target?.kind === 'pipeline' && state.purpose !== 'schematic-statistic-only'
      && state.status === 'blocked' && paths.has('pipeline-progress.json')) {
    const progress = parse(ordinaryBytes(root, path.join(runRoot, 'pipeline-progress.json')), 'pipeline progress');
    const digest = name => bindings.find(entry => entry.path === name)?.sha256;
    blockedProgressEvidence = progress.schemaVersion === 1 && progress.runId === issue.runId
      && progress.status === 'blocked' && typeof progress.reason === 'string' && !!progress.reason.trim()
      && progress.contextDigest === digest('run.json')
      && progress.registryDigest === digest('pipeline-registry.json');
  }
  if (!blockedProgressEvidence && ![...paths].some(item => item !== 'run.json' && item !== 'state.json'
      && !item.startsWith('pipeline-'))) fail('case proposal requires concrete generated evidence');
  return bindings;
}
function verifiedIssue(root, issueId) {
  if (typeof issueId !== 'string' || !ISSUE_ID.test(issueId)) fail('invalid issueId');
  const { file, issue } = readTrainingIssue(root, issueId);
  const bytes = ordinaryBytes(root, file);
  if (JSON.stringify(parse(bytes, 'issue')) !== JSON.stringify(issue)) fail('issue changed during verification');
  return { issue, issueSha256: sha256Bytes(bytes), issueSizeBytes: bytes.length };
}

/** Explicitly convert one verified issue to one immutable, non-promoted case candidate. */
export function createTrainingCaseProposal(workspaceRoot, input, options = {}) {
  const root = path.resolve(workspaceRoot);
  const { issue, issueSha256, issueSizeBytes } = verifiedIssue(root, input?.issueId);
  const expectedBehavior = text(input?.expectedBehavior, 'expectedBehavior', 4000);
  const reproductionSteps = input?.reproductionSteps ?? [];
  if (!Array.isArray(reproductionSteps) || reproductionSteps.length > 20) fail('invalid reproductionSteps');
  const steps = reproductionSteps.map((step, index) => text(step, `reproductionSteps[${index}]`, 500));
  const caseId = `case-${issue.issueId}`;
  const file = proposalFile(root, caseId);
  const createdAt = options.now instanceof Date ? options.now.toISOString() : new Date().toISOString();
  const body = { schemaVersion: 1, kind: 'ptc-training-case-proposal', caseId, createdAt,
    issueId: issue.issueId, issueSha256, issueSizeBytes,
    runId: issue.runId, runStatus: issue.runStatus, profileId: issue.profileId,
    sourceRole: issue.sourceRole, title: issue.title, observedProblem: issue.description,
    expectedBehavior, reproductionSteps: steps, bindings: currentBindings(root, issue),
    disposition: 'proposal-only', regressionSetClaim: false, publicationClaim: false };
  const proposal = { ...body, bodySha256: sha256Bytes(Buffer.from(JSON.stringify(body), 'utf8')) };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  assertSafeRunPath(root, file);
  fs.writeFileSync(file, `${JSON.stringify(proposal, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
  return { file, proposal };
}

/** Fail closed if the proposal, its issue, or any bound run evidence changed. */
export function readTrainingCaseProposal(workspaceRoot, caseId) {
  const root = path.resolve(workspaceRoot);
  const file = proposalFile(root, caseId);
  const proposal = parse(ordinaryBytes(root, file), 'case proposal');
  const { bodySha256, ...body } = proposal;
  if (proposal.schemaVersion !== 1 || proposal.kind !== 'ptc-training-case-proposal'
      || proposal.caseId !== caseId || proposal.disposition !== 'proposal-only'
      || proposal.regressionSetClaim !== false || proposal.publicationClaim !== false
      || bodySha256 !== sha256Bytes(Buffer.from(JSON.stringify(body), 'utf8'))) {
    fail('invalid case proposal identity');
  }
  const { issue, issueSha256, issueSizeBytes } = verifiedIssue(root, proposal.issueId);
  if (caseId !== `case-${issue.issueId}` || proposal.issueSha256 !== issueSha256
      || proposal.issueSizeBytes !== issueSizeBytes || proposal.runId !== issue.runId
      || proposal.runStatus !== issue.runStatus || proposal.profileId !== issue.profileId
      || proposal.sourceRole !== issue.sourceRole || proposal.title !== issue.title
      || proposal.observedProblem !== issue.description) fail('bound issue changed');
  const actual = currentBindings(root, issue);
  if (JSON.stringify(actual) !== JSON.stringify(proposal.bindings)) fail('bound run evidence changed');
  return { file, proposal };
}

/** List only verified proposals; a tampered entry rejects the entire listing. */
export function listTrainingCaseProposals(workspaceRoot, { issueId, runId, profileId } = {}) {
  const root = path.resolve(workspaceRoot);
  if (issueId !== undefined && (typeof issueId !== 'string' || !ISSUE_ID.test(issueId))) fail('invalid issueId filter');
  if (runId !== undefined) trainingAddressBook(runId);
  if (profileId !== undefined && (typeof profileId !== 'string' || !/^[a-z][a-z0-9-]{1,63}$/.test(profileId))) {
    fail('invalid profileId filter');
  }
  const directory = assertSafeRunPath(root, path.join(root, 'Training_Materials', 'case-proposals'));
  if (!fs.existsSync(directory)) return [];
  if (!fs.lstatSync(directory).isDirectory()) fail('case proposal ledger is not a directory');
  return fs.readdirSync(directory).filter(name => name.endsWith('.json')).sort().map(name =>
    readTrainingCaseProposal(root, name.slice(0, -5)).proposal)
    .filter(proposal => (issueId === undefined || proposal.issueId === issueId)
      && (runId === undefined || proposal.runId === runId)
      && (profileId === undefined || proposal.profileId === profileId));
}
