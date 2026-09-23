import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { pipelineGuardDecision, stageDispatchLabel, signStageReceipt, revokeStageDispatch } from '../lib/pipeline-guard.js';

function fixture(stage = 'STRATEGY', role = 'test-strategy-architect') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pipeline-guard-'));
  const runId = 'training-pipeline'; const runRoot = `Training_Materials/runs/${runId}`;
  fs.mkdirSync(path.join(root, runRoot, 'receipts'), { recursive: true });
  fs.writeFileSync(path.join(root, runRoot, 'run.json'), JSON.stringify({ runId, mode: 'training', releaseId: null }));
  const registry = JSON.stringify({ stateMachine: [stage, 'COMPLETE'], stages: { [stage]: { owner: role, gate: 'scripts/gate.py' } } });
  fs.writeFileSync(path.join(root, runRoot, 'pipeline-registry.json'), registry);
  const receipt = { schemaVersion: 1, kind: 'ptc-training-stage', runId, stage, role, gate: 'scripts/gate.py',
    testItems: ['TM109'], dispatchId: `${runId}:${stage}:${role}:1`, childSessionId: 'child',
    registryDigest: crypto.createHash('sha256').update(registry).digest('hex'), label: stageDispatchLabel(runId, stage, role) };
  const profileId = 'strategy-expert';
  const profileRoot = `${runRoot}/profiles/${profileId}`;
  fs.mkdirSync(path.join(root, profileRoot), { recursive: true });
  fs.writeFileSync(path.join(root, profileRoot, 'instructions.md'), 'FROZEN');
  receipt.profileId = profileId; receipt.pipelineCacheKey = 'b'.repeat(64);
  receipt.profileSha256 = crypto.createHash('sha256').update('FROZEN').digest('hex');
  fs.writeFileSync(path.join(root, runRoot, 'pipeline-material-manifest.json'), JSON.stringify({ runId,
    pipelineCacheKey: receipt.pipelineCacheKey, ownerProfiles: { [role]: profileId }, testItems: ['TM109'],
    addressBook: { profileRoots: { [profileId]: profileRoot } },
    files: [{ snapshotPath: `${profileRoot}/instructions.md`, sha256: receipt.profileSha256 }],
  }));
  const file = path.join(root, runRoot, 'receipts/child.json');
  fs.writeFileSync(file, JSON.stringify(signStageReceipt(receipt)));
  const agent = { id: 'child', session: { header: { cwd: root }, events: [{ type: 'subagent/descriptor', data: { label: receipt.label } }] } };
  const decide = (name, target) => pipelineGuardDecision({ agent, name, arguments: { file_path: target } }, root);
  return { root, runRoot, receipt, file, agent, decide };
}

test('pipeline stage can read its snapshot and write only its own stage/TM', () => {
  const f = fixture();
  assert.equal(f.decide('write', `${f.runRoot}/trials/tm109/strategy/deliverable-ready.json`), undefined);
  assert.equal(f.decide('read', `${f.runRoot}/input-sync/dft/TM109/dft-meta.json`), undefined);
  for (const target of ['project/DALI/a.json', `${f.runRoot}/trials/tm110/strategy/a.json`, `${f.runRoot}/trials/tm109/method/a.json`, `${f.runRoot}/input/a.json`, `${f.runRoot}/receipts/a.json`]) assert.ok(f.decide('write', target));
  assert.ok(f.decide('pwsh', 'anything'));
});

test('pipeline mismatched child, registry drift and memory revocation fail closed', () => {
  const f = fixture();
  f.agent.id = 'wrong'; assert.ok(f.decide('run_code', ''));
  f.agent.id = 'child';
  fs.appendFileSync(path.join(f.root, f.runRoot, 'pipeline-registry.json'), ' ');
  assert.ok(f.decide('run_code', ''));
  const g = fixture(); revokeStageDispatch(g.root, g.receipt.dispatchId);
  assert.ok(g.decide('run_code', ''));
});

test('review stages cannot overwrite the other review stage evidence', () => {
  const f = fixture('RULE_REVIEW_IMPLEMENTATION', 'rule-reviewer');
  assert.equal(f.decide('write', `${f.runRoot}/trials/tm109/review/implementation-review.json`), undefined);
  assert.ok(f.decide('write', `${f.runRoot}/trials/tm109/review/method-contract-review.json`));
});
