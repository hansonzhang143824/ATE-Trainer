import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { sha256Bytes } from '../lib/release-integrity.js';
import { createTrainingRun } from '../lib/training-run.js';
import { createTrainingIssue, readTrainingIssue, listTrainingIssues } from '../lib/training-issues.js';

function json(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}
function fixture(kind = 'profile') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-issue-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-schematic-expert'), { recursive: true });
  if (kind === 'pipeline') json(path.join(root, 'team/ptc/ptc_stage_registry.json'), {
    stateMachine: ['INPUT_SYNC', 'STRATEGY', 'COMPLETE'],
  });
  const created = createTrainingRun(root, { runId: 'training-test-1',
    target: kind === 'profile' ? { kind: 'profile', profileId: 'ptc-dft-expert' }
      : { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' },
  });
  json(created.stateFile, { ...created.state, status: 'blocked' });
  const runRoot = path.dirname(created.stateFile);
  const evidenceFile = path.join(runRoot, 'evidence', 'review.json');
  json(evidenceFile, { finding: 'source row differs' });
  if (kind === 'pipeline') {
    json(path.join(runRoot, 'pipeline-material-manifest.json'), { runId: created.context.runId,
      ownerProfiles: { 'schematic-expert': 'ptc-schematic-expert' } });
    json(path.join(runRoot, 'pipeline-progress.json'), { runId: created.context.runId,
      sourceRoles: ['schematic-expert'] });
    json(path.join(runRoot, 'pipeline-registry.json'), { stages: {} });
  }
  return { root, runRoot, evidenceFile, created,
    input: { runId: created.context.runId, profileId: kind === 'profile' ? 'ptc-dft-expert' : 'ptc-schematic-expert',
      ...(kind === 'pipeline' ? { sourceRole: 'schematic-expert' } : {}),
      title: 'TM109 review mismatch', description: 'Check the cited generated review.',
      evidencePaths: ['evidence/review.json'] } };
}

test('writes an immutable local issue with exact evidence bytes and terminal run binding', () => {
  const { root, input, evidenceFile, runRoot } = fixture();
  const { file, issue } = createTrainingIssue(root, input, { issueId: 'issue-test-1', now: new Date('2026-09-23T12:00:00Z') });
  assert.equal(file, path.join(root, 'Training_Materials/training-issues/issue-test-1.json'));
  assert.equal(issue.evidence[0].sha256, sha256Bytes(fs.readFileSync(evidenceFile)));
  assert.equal(issue.stateSha256, sha256Bytes(fs.readFileSync(path.join(runRoot, 'state.json'))));
  assert.equal(issue.disposition, 'proposal-only');
  assert.deepEqual(issue.ownership, []);
  assert.equal(issue.publicationClaim, false);
  assert.match(issue.bodySha256, /^[a-f0-9]{64}$/);
  assert.deepEqual(readTrainingIssue(root, 'issue-test-1').issue, issue);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/draft-history')), false);
  assert.equal(fs.existsSync(path.join(root, 'team/expert-profiles/ptc-dft-expert/cases')), false);
});

test('pipeline issue seals every run-local file used to decide expert ownership', () => {
  for (const [name, change] of [
    ['pipeline-material-manifest.json', { note: 'changed but same owner' }],
    ['pipeline-progress.json', { reason: 'changed but same source roles' }],
    ['pipeline-registry.json', { note: 'changed but same stage owner' }],
  ]) {
    const f = fixture('pipeline');
    const { issue } = createTrainingIssue(f.root, f.input, { issueId: 'ownership-bound' });
    assert.equal(issue.ownership.length, 3);
    const file = path.join(f.runRoot, name);
    json(file, { ...JSON.parse(fs.readFileSync(file, 'utf8')), ...change });
    assert.throws(() => readTrainingIssue(f.root, 'ownership-bound'), /ownership evidence changed/);
    assert.throws(() => listTrainingIssues(f.root), /ownership evidence changed/);
  }
});

test('rejects wrong profile, wrong source role and nonterminal or delivery run', () => {
  const f = fixture();
  assert.throws(() => createTrainingIssue(f.root, { ...f.input, profileId: 'ptc-schematic-expert' }), /does not own/);
  json(path.join(f.runRoot, 'state.json'), { ...f.created.state, status: 'running' });
  assert.throws(() => createTrainingIssue(f.root, f.input), /completed or blocked/);
  json(path.join(f.runRoot, 'state.json'), { ...f.created.state, status: 'completed' });
  json(path.join(f.runRoot, 'run.json'), { ...f.created.context, mode: 'delivery' });
  assert.throws(() => createTrainingIssue(f.root, f.input), /completed or blocked/);
  const p = fixture('pipeline');
  assert.equal(createTrainingIssue(p.root, p.input, { issueId: 'pipeline-one' }).issue.sourceRole, 'schematic-expert');
  assert.throws(() => createTrainingIssue(p.root, { ...p.input, sourceRole: 'dft-expert' }), /does not own/);
  assert.throws(() => createTrainingIssue(p.root, { ...p.input, sourceRole: undefined }), /explicit source role/);
});

test('rejects traversal, absolute, source snapshot, duplicate and linked evidence', () => {
  const f = fixture();
  for (const bad of ['../outside.txt', 'evidence/../state.json', '/tmp/outside', 'C:/outside',
    'evidence\\review.json', 'input/Dali_testmode.xlsx']) {
    assert.throws(() => createTrainingIssue(f.root, { ...f.input, evidencePaths: [bad] }), /evidence|relative/);
  }
  assert.throws(() => createTrainingIssue(f.root, { ...f.input,
    evidencePaths: ['evidence/review.json', 'evidence/review.json'] }), /unique array/);
  const linked = path.join(f.runRoot, 'evidence', 'linked.json');
  fs.linkSync(f.evidenceFile, linked);
  assert.throws(() => createTrainingIssue(f.root, { ...f.input, evidencePaths: ['evidence/linked.json'] }), /hard-linked|unlinked/);
});

test('duplicate issue identity cannot overwrite, and tampered evidence or run state fails verification', () => {
  const f = fixture();
  const first = createTrainingIssue(f.root, f.input, { issueId: 'same-identity' });
  const before = fs.readFileSync(first.file);
  assert.throws(() => createTrainingIssue(f.root, { ...f.input, title: 'another title' },
    { issueId: 'same-identity' }), { code: 'EEXIST' });
  assert.deepEqual(fs.readFileSync(first.file), before);
  fs.writeFileSync(f.evidenceFile, '{"finding":"changed"}\n');
  assert.throws(() => readTrainingIssue(f.root, 'same-identity'), /evidence changed/);
  json(f.evidenceFile, { finding: 'source row differs' });
  json(path.join(f.runRoot, 'state.json'), { ...f.created.state, status: 'completed' });
  assert.throws(() => readTrainingIssue(f.root, 'same-identity'), /bound run identity changed/);
});

test('modified issue description fails its immutable body seal', () => {
  const f = fixture();
  const { file, issue } = createTrainingIssue(f.root, f.input, { issueId: 'sealed-issue' });
  json(file, { ...issue, description: 'silently changed' });
  assert.throws(() => readTrainingIssue(f.root, 'sealed-issue'), /invalid issue identity/);
});

test('list filters verified issues; empty evidence still binds the run context and state', () => {
  const f = fixture();
  const input = { ...f.input, evidencePaths: [] };
  const one = createTrainingIssue(f.root, input, { issueId: 'issue-one' }).issue;
  const two = createTrainingIssue(f.root, { ...input, title: 'Second issue' }, { issueId: 'issue-two' }).issue;
  assert.deepEqual(one.evidence, []);
  assert.equal(one.contextSha256, sha256Bytes(fs.readFileSync(path.join(f.runRoot, 'run.json'))));
  assert.equal(one.stateSha256, sha256Bytes(fs.readFileSync(path.join(f.runRoot, 'state.json'))));
  assert.deepEqual(listTrainingIssues(f.root, { runId: f.input.runId }), [one, two]);
  assert.deepEqual(listTrainingIssues(f.root, { profileId: 'another-profile' }), []);
  json(path.join(f.root, 'Training_Materials/training-issues/issue-two.json'), { ...two, title: 'tampered' });
  assert.throws(() => listTrainingIssues(f.root), /invalid issue identity/);
});
