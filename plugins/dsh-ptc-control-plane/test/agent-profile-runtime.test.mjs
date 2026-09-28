import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { cloneAgentProfile, createAgentProfileRevision, resolveAgentProfile } from '../lib/agent-profile-runtime.js';
import { createTrainingRun } from '../lib/training-run.js';

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-agent-profile-runtime-'));
  const source = path.join(root, 'team/expert-profiles/ptc-dft-expert');
  fs.mkdirSync(path.join(source, 'cases/TM109'), { recursive: true });
  fs.writeFileSync(path.join(source, 'profile.yaml'), [
    'schemaVersion: 1', 'id: ptc-dft-expert', 'displayName: DFT Expert',
    'executionClass: input-dft', 'ownerRole: dft-expert', '',
  ].join('\n'));
  fs.writeFileSync(path.join(source, 'instructions.md'), 'DFT instructions\n');
  fs.writeFileSync(path.join(source, 'output-contract.schema.json'), '{}\n');
  fs.writeFileSync(path.join(source, 'cases/TM109/expected.json'), '{"ok":true}\n');
  return { root, source };
}

test('clone creates an independent profile revision and manifest', () => {
  const f = fixture();
  try {
    const clone = cloneAgentProfile(f.root, {
      sourceProfileId: 'ptc-dft-expert', targetProfileId: 'tm109-dft-copy',
      revisionId: 'draft-1', displayName: 'TM109 DFT Copy',
    });
    assert.equal(clone.profileId, 'tm109-dft-copy');
    assert.equal(clone.baseProfileId, 'ptc-dft-expert');
    assert.equal(clone.profileRevision, 'draft-1');
    assert.match(clone.contentDigest, /^[a-f0-9]{64}$/);
    assert.match(clone.manifestDigest, /^[a-f0-9]{64}$/);
    assert.equal(fs.existsSync(path.join(f.root, 'team/expert-profiles/tm109-dft-copy/versions/draft-1/manifest.json')), true);
    assert.match(fs.readFileSync(path.join(f.root, 'team/expert-profiles/tm109-dft-copy/profile.yaml'), 'utf8'), /id: tm109-dft-copy/);
    assert.match(fs.readFileSync(path.join(f.root, 'team/expert-profiles/tm109-dft-copy/profile.yaml'), 'utf8'), /displayName: TM109 DFT Copy/);
    fs.writeFileSync(path.join(f.root, 'team/expert-profiles/tm109-dft-copy/instructions.md'), 'copy changed\n');
    assert.equal(fs.readFileSync(path.join(f.root, 'team/expert-profiles/ptc-dft-expert/instructions.md'), 'utf8'), 'DFT instructions\n');
    assert.throws(() => resolveAgentProfile(f.root, 'tm109-dft-copy', { revisionId: 'draft-1' }), /files changed/);
    assert.throws(() => cloneAgentProfile(f.root, {
      sourceProfileId: 'ptc-dft-expert', targetProfileId: 'tm109-dft-copy', revisionId: 'draft-2',
    }), /already exists/);
  } finally { fs.rmSync(f.root, { recursive: true, force: true }); }
});

test('revision pointer advances while previous revision remains immutable', () => {
  const f = fixture();
  try {
    cloneAgentProfile(f.root, { sourceProfileId: 'ptc-dft-expert', targetProfileId: 'copy', revisionId: 'draft-1' });
    const next = createAgentProfileRevision(f.root, 'copy', { revisionId: 'draft-2' });
    assert.equal(next.profileRevision, 'draft-2');
    assert.equal(resolveAgentProfile(f.root, 'copy').profileRevision, 'draft-2');
    assert.equal(resolveAgentProfile(f.root, 'copy', { revisionId: 'draft-1' }).profileRevision, 'draft-1');
  } finally { fs.rmSync(f.root, { recursive: true, force: true }); }
});

test('training run binds a dynamic profile revision without changing legacy shape', () => {
  const f = fixture();
  try {
    cloneAgentProfile(f.root, { sourceProfileId: 'ptc-dft-expert', targetProfileId: 'copy', revisionId: 'draft-1' });
    const run = createTrainingRun(f.root, {
      runId: 'dynamic-profile-run', purpose: 'business-training',
      target: { kind: 'profile', profileId: 'copy', profileRevision: 'draft-1' },
    });
    assert.deepEqual(run.state.target, {
      kind: 'profile', profileId: 'copy', profileRevision: 'draft-1', profileDigest: run.state.target.profileDigest,
    });
    assert.match(run.state.target.profileDigest, /^[a-f0-9]{64}$/);
  } finally { fs.rmSync(f.root, { recursive: true, force: true }); }
});
