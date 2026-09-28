import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { sha256Bytes } from '../lib/release-integrity.js';
import { createTrainingRun } from '../lib/training-run.js';
import { createTrainingIssue } from '../lib/training-issues.js';
import { createTrainingCaseProposal, readTrainingCaseProposal,
  listTrainingCaseProposals } from '../lib/training-case-proposals.js';

function json(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}
function fixture(kind = 'profile', issueEvidence = true) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-case-proposal-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-schematic-expert'), { recursive: true });
  if (kind === 'pipeline') json(path.join(root, 'team/ptc/ptc_stage_registry.json'), {
    stateMachine: ['INPUT_SYNC', 'STRATEGY', 'COMPLETE'],
  });
  const run = createTrainingRun(root, { runId: 'training-case-test',
    target: kind === 'profile' ? { kind: 'profile', profileId: 'ptc-dft-expert' }
      : { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' },
  });
  const runRoot = path.dirname(run.stateFile);
  const evidence = path.join(runRoot, 'evidence', 'dft-terminal.json');
  json(evidence, { result: 'blocked', source: 'test' });
  json(run.stateFile, { ...run.state, status: 'blocked',
    ...(kind === 'pipeline' ? { purpose: 'schematic-statistic-only' } : {}),
    outcome: { evidence: path.relative(root, evidence) } });
  if (kind === 'pipeline') {
    json(path.join(runRoot, 'pipeline-material-manifest.json'), { runId: run.context.runId,
      ownerProfiles: { 'schematic-expert': 'ptc-schematic-expert' } });
  }
  const input = { runId: run.context.runId,
    profileId: kind === 'profile' ? 'ptc-dft-expert' : 'ptc-schematic-expert',
    ...(kind === 'pipeline' ? { sourceRole: 'schematic-expert' } : {}),
    title: 'TM109 mismatch', description: 'The expected value was lost.',
    evidencePaths: issueEvidence ? ['evidence/dft-terminal.json'] : [] };
  const { file: issueFile, issue } = createTrainingIssue(root, input, { issueId: 'issue-case-test' });
  return { root, runRoot, run, issueFile, issue, evidence };
}
function propose(f) {
  return createTrainingCaseProposal(f.root, { issueId: f.issue.issueId,
    expectedBehavior: 'Preserve the source expected value.',
    reproductionSteps: ['Run TM109 in training.', 'Review the generated artifact.'] },
  { now: new Date('2026-09-23T14:00:00Z') });
}
function blockedPipelineFixture(progressChanges = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-case-pipeline-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-schematic-expert'), { recursive: true });
  json(path.join(root, 'team/ptc/ptc_stage_registry.json'), {
    stateMachine: ['INPUT_SYNC', 'COMPLETE'], stages: { INPUT_SYNC: { owner: 'schematic-expert' } },
  });
  const run = createTrainingRun(root, { runId: 'training-blocked-pipeline',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' } });
  const runRoot = path.dirname(run.stateFile);
  json(run.stateFile, { ...run.state, status: 'blocked', purpose: 'business-training' });
  json(path.join(runRoot, 'pipeline-material-manifest.json'), { runId: run.context.runId,
    ownerProfiles: { 'schematic-expert': 'ptc-schematic-expert' } });
  const registryFile = path.join(runRoot, 'pipeline-registry.json');
  json(registryFile, { stages: { INPUT_SYNC: { owner: 'schematic-expert' } } });
  const progressFile = path.join(runRoot, 'pipeline-progress.json');
  json(progressFile, { schemaVersion: 1, runId: run.context.runId, status: 'blocked',
    reason: 'schematic semantic review failed', sourceRoles: ['schematic-expert'],
    contextDigest: sha256Bytes(fs.readFileSync(path.join(runRoot, 'run.json'))),
    registryDigest: sha256Bytes(fs.readFileSync(registryFile)), ...progressChanges });
  const issue = createTrainingIssue(root, { runId: run.context.runId,
    profileId: 'ptc-schematic-expert', sourceRole: 'schematic-expert',
    title: 'Orchestration failure', description: 'Semantic review blocked.', evidencePaths: [] },
  { issueId: 'issue-blocked-pipeline' }).issue;
  return { root, runRoot, run, issue, progressFile, registryFile };
}

test('explicit conversion seals issue bytes and key run evidence without promotion', () => {
  const f = fixture();
  const { file, proposal } = propose(f);
  assert.equal(file, path.join(f.root, 'Training_Materials/case-proposals/case-issue-case-test.json'));
  assert.equal(proposal.issueSha256, sha256Bytes(fs.readFileSync(f.issueFile)));
  assert.deepEqual(proposal.bindings.map(entry => entry.path),
    ['evidence/dft-terminal.json', 'run.json', 'state.json']);
  assert.equal(proposal.bindings[0].sha256, sha256Bytes(fs.readFileSync(f.evidence)));
  assert.equal(proposal.disposition, 'proposal-only');
  assert.equal(proposal.regressionSetClaim, false);
  assert.equal(proposal.publicationClaim, false);
  assert.deepEqual(readTrainingCaseProposal(f.root, proposal.caseId).proposal, proposal);
  assert.deepEqual(listTrainingCaseProposals(f.root, { runId: f.issue.runId }), [proposal]);
  assert.deepEqual(listTrainingCaseProposals(f.root, { profileId: 'another-profile' }), []);
  assert.equal(fs.existsSync(path.join(f.root, 'team/expert-profiles/ptc-dft-expert/cases')), false);
  assert.equal(fs.existsSync(path.join(f.root, 'Training_Materials/draft-history')), false);
  assert.equal(fs.existsSync(path.join(f.root, 'team/ptc/releases')), false);
});

test('one issue has one case identity and an exclusive write rejects duplicate conversion', () => {
  const f = fixture();
  const { file } = propose(f);
  const before = fs.readFileSync(file);
  assert.throws(() => propose(f), { code: 'EEXIST' });
  assert.deepEqual(fs.readFileSync(file), before);
  assert.deepEqual(listTrainingCaseProposals(f.root, { issueId: f.issue.issueId }).length, 1);
});

test('rejects changed issue, changed evidence and changed run state', () => {
  const a = fixture();
  const ap = propose(a);
  json(a.issueFile, { ...a.issue, description: 'edited after review' });
  assert.throws(() => readTrainingCaseProposal(a.root, ap.proposal.caseId), /invalid issue identity/);
  const b = fixture();
  const bp = propose(b);
  json(b.evidence, { result: 'changed' });
  assert.throws(() => readTrainingCaseProposal(b.root, bp.proposal.caseId), /evidence changed/);
  const c = fixture();
  const cp = propose(c);
  json(c.run.stateFile, { ...c.run.state, status: 'completed' });
  assert.throws(() => readTrainingCaseProposal(c.root, cp.proposal.caseId), /bound run identity changed/);
});

test('empty issue evidence still binds terminal receipt and pipeline material snapshot', () => {
  const f = fixture('pipeline', false);
  const { proposal } = propose(f);
  assert.deepEqual(proposal.bindings.map(entry => entry.path),
    ['evidence/dft-terminal.json', 'pipeline-material-manifest.json', 'run.json', 'state.json']);
  json(path.join(f.runRoot, 'pipeline-material-manifest.json'), { runId: f.run.context.runId,
    ownerProfiles: { 'schematic-expert': 'ptc-schematic-expert' }, changed: true });
  assert.throws(() => readTrainingCaseProposal(f.root, proposal.caseId), /ownership evidence changed|bound run evidence changed/);
});

test('bound blocked pipeline progress can be concrete failure evidence without a child receipt', () => {
  const f = blockedPipelineFixture();
  const { proposal } = createTrainingCaseProposal(f.root, { issueId: f.issue.issueId,
    expectedBehavior: 'Report the cited schematic conflict with a resolvable reason.' });
  assert.ok(proposal.bindings.some(entry => entry.path === 'pipeline-progress.json'));
  assert.deepEqual(readTrainingCaseProposal(f.root, proposal.caseId).proposal, proposal);
  json(f.progressFile, { ...JSON.parse(fs.readFileSync(f.progressFile, 'utf8')), note: 'changed' });
  assert.throws(() => readTrainingCaseProposal(f.root, proposal.caseId), /ownership evidence changed/);
});

test('pipeline progress without a bound terminal failure is not concrete case evidence', () => {
  for (const change of [{ status: 'running' }, { reason: '' },
    { contextDigest: '0'.repeat(64) }, { registryDigest: '0'.repeat(64) }]) {
    const f = blockedPipelineFixture(change);
    assert.throws(() => createTrainingCaseProposal(f.root, { issueId: f.issue.issueId,
      expectedBehavior: 'A bounded failure record.' }), /requires concrete generated evidence/);
  }
});

test('tampered proposal and linked files fail closed; no arbitrary evidence path accepted', () => {
  const f = fixture();
  const { file, proposal } = propose(f);
  json(file, { ...proposal, expectedBehavior: 'silent edit' });
  assert.throws(() => readTrainingCaseProposal(f.root, proposal.caseId), /invalid case proposal identity/);
  const g = fixture();
  const result = propose(g);
  const linked = path.join(g.root, 'Training_Materials/case-proposals/linked.json');
  fs.linkSync(result.file, linked);
  assert.throws(() => readTrainingCaseProposal(g.root, result.proposal.caseId), /hard-linked|unlinked/);
  assert.throws(() => readTrainingCaseProposal(g.root, '../case-issue-case-test'), /invalid caseId/);
  const h = fixture();
  const symlink = path.join(h.root, 'Training_Materials/case-proposals');
  const external = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-case-external-'));
  try {
    fs.symlinkSync(external, symlink, process.platform === 'win32' ? 'junction' : 'dir');
    assert.throws(() => createTrainingCaseProposal(h.root, { issueId: h.issue.issueId,
      expectedBehavior: 'Expected' }), /symbolic link|junction/);
  } catch (error) {
    if (!['EPERM', 'EACCES', 'ENOTSUP'].includes(error.code)) throw error;
  }
});

test('a proposal needs concrete generated evidence and rejects an escaped terminal path', () => {
  const empty = fixture('profile', false);
  json(empty.run.stateFile, { ...empty.run.state, status: 'blocked' });
  const { issue } = createTrainingIssue(empty.root, { runId: empty.run.context.runId,
    profileId: 'ptc-dft-expert', title: 'No receipt', description: 'No generated evidence exists.',
    evidencePaths: [] }, { issueId: 'issue-no-evidence' });
  assert.throws(() => createTrainingCaseProposal(empty.root, { issueId: issue.issueId,
    expectedBehavior: 'A receipt should exist.' }), /requires concrete generated evidence/);
  const escaped = fixture('profile', false);
  json(escaped.run.stateFile, { ...escaped.run.state, status: 'blocked',
    outcome: { evidence: path.join(escaped.root, 'outside.json') } });
  const outsideIssue = createTrainingIssue(escaped.root, { runId: escaped.run.context.runId,
    profileId: 'ptc-dft-expert', title: 'Bad receipt path', description: 'The path escaped.',
    evidencePaths: [] }, { issueId: 'issue-escaped' }).issue;
  assert.throws(() => createTrainingCaseProposal(escaped.root, { issueId: outsideIssue.issueId,
    expectedBehavior: 'Keep receipt inside run.' }), /terminal receipt is outside generated run evidence/);
});
