import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRunContext, persistRunContext } from '../lib/run-context.js';
import { createProfileSmokeManager } from '../lib/profile-training.js';

const PROFILE_IDS = ['ate-implementer', 'compile-diagnostician', 'evolution-expert', 'method-expert',
  'ptc-dft-expert', 'ptc-schematic-expert', 'rule-reviewer', 'strategy-expert'];
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function fixture(profileId, index = 0) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-profile-smoke-'));
  const source = path.join(root, 'team', 'expert-profiles', profileId);
  fs.mkdirSync(source, { recursive: true });
  fs.writeFileSync(path.join(source, 'instructions.md'), 'private instructions must not enter the smoke prompt\n');
  const runId = `training-smoke-${index}`;
  const context = createRunContext(root, { mode: 'training', runId });
  persistRunContext(root, context);
  const directory = path.join(root, context.artifactRoot);
  fs.writeFileSync(path.join(directory, 'state.json'), `${JSON.stringify({ schemaVersion: 1, runId,
    target: { kind: 'profile', profileId }, purpose: 'smoke-training', status: 'created',
    createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() })}\n`);
  return { root, runId, directory, profileId, cleanup: () => fs.rmSync(root, { recursive: true, force: true }) };
}

function fakeSnapshot(root, record) {
  const file = path.join(record.directory, 'profile', 'snapshot.json');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, '{"frozen":true}\n');
  return { file, sha256: sha(fs.readFileSync(file)), manifest: { files: [] } };
}

function ctxFor(profileId, inspect = () => {}, childResult) {
  return {
    agentDefaultModel: { currentSelection: () => ({ provider: 'fake', model: 'fake' }) },
    agentPresets: { mount: async () => {} },
    agents: { create: async () => ({ agent: { whenIdle: async () => {} }, dispose: async () => {} }) },
    subagents: { start: async (_kind, request) => {
      inspect(request);
      return { id: `child-${profileId}`, result: Promise.resolve(childResult ?? {
        stopReason: 'completed', structured: { answer: 3 },
      }), dispose: async () => {} };
    } },
  };
}

test('all eight arithmetic profiles dispatch a real child and seal only SMOKE_ONLY evidence', async () => {
  for (const [index, profileId] of PROFILE_IDS.entries()) {
    const f = fixture(profileId, index);
    try {
      let spawned = false;
      const manager = createProfileSmokeManager(ctxFor(profileId, request => {
        spawned = true;
        assert.deepEqual(request.toolFilter.allow, []);
        assert.ok(!JSON.stringify(request).includes('private instructions'));
        assert.equal(request.prompt[0].text, '1+2等于几，把答案写在JSON里');
      }), f.root, { freezeProfile: fakeSnapshot, verifyProfile: async () => {} });
      const started = manager.start({ runId: f.runId });
      const result = await started.completion;
      assert.equal(spawned, true);
      assert.equal(result.state.status, 'completed');
      assert.equal(result.state.outcome.mode, 'SMOKE_ONLY');
      assert.equal(result.state.outcome.businessGatePassed, false);
      assert.equal(result.evidence.profileInstructionsValidated, false);
      assert.equal(result.evidence.modelDispatched, true);
      assert.equal(result.evidence.answer, 3);
      assert.match(result.evidence.profileSnapshotSha256, /^[a-f0-9]{64}$/);
      assert.equal(result.evidenceSha256, sha(fs.readFileSync(result.evidenceFile)));
      assert.equal(result.evidence.responseSha256,
        sha(fs.readFileSync(path.join(f.directory, 'evidence', 'profile-smoke-child.json'))));
    } finally { f.cleanup(); }
  }
});

test('wrong or nonnumeric answer is BLOCKED, never business success', async () => {
  const f = fixture('strategy-expert', 40);
  try {
    const manager = createProfileSmokeManager(ctxFor(f.profileId, () => {}, {
      stopReason: 'completed', structured: { answer: '3' },
    }), f.root, { freezeProfile: fakeSnapshot, verifyProfile: async () => {} });
    const result = await manager.start({ runId: f.runId }).completion;
    assert.equal(result.state.status, 'blocked');
    assert.equal(result.evidence.businessGatePassed, false);
    assert.match(result.evidence.responseSha256, /^[a-f0-9]{64}$/);
  } finally { f.cleanup(); }
});

test('unknown ninth profile cannot enter the eight-expert smoke path', () => {
  const f = fixture('not-an-ate-expert', 50);
  try {
    const manager = createProfileSmokeManager(ctxFor(f.profileId), f.root);
    assert.throws(() => manager.start({ runId: f.runId }), /not one of the eight/);
  } finally { f.cleanup(); }
});

test('stop settles as BLOCKED without accepting a late child', async () => {
  const f = fixture('rule-reviewer', 41);
  try {
    const ctx = ctxFor(f.profileId);
    ctx.subagents.start = async () => ({ id: 'late-child', result: new Promise(() => {}), dispose: async () => {} });
    const manager = createProfileSmokeManager(ctx, f.root, {
      freezeProfile: fakeSnapshot, verifyProfile: async () => {}, timeoutMs: 2000,
    });
    const started = manager.start({ runId: f.runId });
    assert.equal(manager.stop(f.runId), true);
    const result = await started.completion;
    assert.equal(result.state.status, 'blocked');
    assert.equal(result.evidence.businessGatePassed, false);
    assert.equal(result.evidence.stopReason, 'aborted');
  } finally { f.cleanup(); }
});

test('deadline covers a stalled parent before any child is dispatched', async () => {
  const f = fixture('method-expert', 42);
  try {
    const ctx = ctxFor(f.profileId);
    let dispatched = false;
    ctx.agents.create = async () => new Promise(() => {});
    ctx.subagents.start = async () => { dispatched = true; throw new Error('must not dispatch'); };
    const manager = createProfileSmokeManager(ctx, f.root, {
      freezeProfile: fakeSnapshot, verifyProfile: async () => {}, timeoutMs: 30,
    });
    const result = await manager.start({ runId: f.runId }).completion;
    assert.equal(dispatched, false);
    assert.equal(result.state.status, 'blocked');
    assert.equal(result.evidence.stopReason, 'timeout');
    assert.equal(result.evidence.modelDispatched, false);
  } finally { f.cleanup(); }
});

test('profile snapshot drift rejects an otherwise correct arithmetic response', async () => {
  const f = fixture('evolution-expert', 43);
  try {
    const manager = createProfileSmokeManager(ctxFor(f.profileId), f.root, {
      freezeProfile: fakeSnapshot, verifyProfile: async () => { throw new Error('profile changed during smoke training'); },
    });
    const result = await manager.start({ runId: f.runId }).completion;
    assert.equal(result.state.status, 'blocked');
    assert.match(result.evidence.reason, /profile changed/);
    assert.equal(result.evidence.answer, null);
  } finally { f.cleanup(); }
});
