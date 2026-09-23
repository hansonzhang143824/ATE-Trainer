/**
 * The training-session rule (handoff rule 6): a training profile may write only
 * its own draft, cases, evaluation and CHANGELOG.
 *
 * The load-bearing test is that the rule fires when the session's cwd is OUTSIDE
 * the plugin's `workspaceRoot` — that is the real deployment shape (the boundary
 * is bound to one workspace while the user trains in another), and a root-scoped
 * check would silently never apply.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { decision } from '../lib/policy.js';
import { trainingProfileFor } from '../lib/expert-policy-registry.js';
import { agentPresetOf } from '../lib/session-preset.js';

const DENIED = /PTC training boundary/;
const workspaces = [];

/** A workspace the user trains in; the plugin's root is a DIFFERENT tree. */
function trainingWorkspace(presetId = 'ptc-dft-expert') {
  const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-')));
  for (const relative of [
    `team/expert-profiles/${presetId}/cases/TM106/expected.json`,
    `team/expert-profiles/${presetId}/evaluation/expected-results.json`,
    `team/expert-profiles/${presetId}/instructions.md`,
    `team/expert-profiles/${presetId}/output-contract.schema.json`,
    `team/expert-profiles/${presetId}/profile.yaml`,
    `team/expert-profiles/${presetId}/CHANGELOG.md`,
    `team/expert-profiles/${presetId}/status.json`,
    `team/expert-profiles/${presetId}/versions/v1/manifest.json`,
    'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md',
    'team/artifacts/dispatch-receipts/x.json',
    'project/DALI/Output_Global_Material/dft/TM106/dft-meta.json',
    'scripts/validate_dft_outputs.py',
    'plugins/dsh-ptc-material-boundary/lib/policy.js',
  ]) {
    const full = path.join(ws, relative);
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, 'fixture\n');
  }
  workspaces.push(ws);
  return ws;
}

const OTHER_ROOT = path.join(os.tmpdir(), 'some-other-deployment-root');
const session = (ws, presetId) => ({ session: { header: { cwd: ws, agentPreset: presetId }, events: [] } });
const call = (name, args, agent) => ({ name, arguments: args, agent });
const write = (ws, relative, agent) => decision(call('write', { file_path: path.join(ws, relative) }, agent), OTHER_ROOT);
const read = (ws, relative, agent) => decision(call('read', { file_path: path.join(ws, relative) }, agent), OTHER_ROOT);

after(() => {
  for (const ws of workspaces) fs.rmSync(ws, { recursive: true, force: true });
});

test('the rule applies even though the session cwd is outside the plugin workspace root', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  // If the rule were root-scoped this would be undefined (no boundary at all).
  assert.match(write(ws, 'scripts/validate_dft_outputs.py', agent), DENIED);
});

test('a training session may write its own draft, cases, evaluation and changelog', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  for (const relative of [
    'team/expert-profiles/ptc-dft-expert/cases/TM106/expected.json',
    'team/expert-profiles/ptc-dft-expert/evaluation/expected-results.json',
    'team/expert-profiles/ptc-dft-expert/instructions.md',
    'team/expert-profiles/ptc-dft-expert/output-contract.schema.json',
    'team/expert-profiles/ptc-dft-expert/profile.yaml',
    'team/expert-profiles/ptc-dft-expert/CHANGELOG.md',
    'team/expert-profiles/ptc-dft-expert/cases/TM108/expected.json', // may create new
  ]) {
    assert.equal(write(ws, relative, agent), undefined, relative);
  }
});

test('a training session may not touch published versions or status.json', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/versions/v1/manifest.json', agent), DENIED);
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/versions/v2/profile.yaml', agent), DENIED);
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/status.json', agent), DENIED);
});

test('a training session may not write another profile, project code or production artifacts', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  for (const relative of [
    'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md',
    'team/artifacts/dispatch-receipts/x.json',
    'project/DALI/Output_Global_Material/dft/TM106/dft-meta.json',
    'plugins/dsh-ptc-material-boundary/lib/policy.js',
  ]) {
    assert.match(write(ws, relative, agent), DENIED, relative);
  }
});

test('a traversal out of the profile folder is denied after resolution', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/../../../scripts/validate_dft_outputs.py', agent), DENIED);
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/cases/../../ptc-schematic-expert/CHANGELOG.md', agent), DENIED);
});

test('reads stay unrestricted for a training session: the rule constrains writes', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  for (const relative of [
    'scripts/validate_dft_outputs.py',
    'team/expert-profiles/ptc-dft-expert/versions/v1/manifest.json',
    'project/DALI/Output_Global_Material/dft/TM106/dft-meta.json',
    'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md',
  ]) {
    assert.equal(read(ws, relative, agent), undefined, relative);
  }
});

test('only the two gated scripts may be run, and only for its own profile', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  assert.equal(decision(call('pwsh', { command: 'python scripts/evaluate_expert_profile.py --profile ptc-dft-expert --version draft' }, agent), OTHER_ROOT), undefined);
  assert.equal(decision(call('pwsh', { command: 'python scripts/publish_expert_profile.py --profile ptc-dft-expert --version v4' }, agent), OTHER_ROOT), undefined);
  for (const command of [
    'python scripts/publish_expert_profile.py --profile ptc-schematic-expert --version v3',
    'python scripts/validate_dft_outputs.py --tm TM106',
    'rm -rf team/expert-profiles/ptc-dft-expert/versions',
    'python scripts/evaluate_expert_profile.py --profile ptc-dft-expert --version v1',
  ]) {
    assert.match(decision(call('pwsh', { command }, agent), OTHER_ROOT), DENIED, command);
  }
  // A workdir or a background run would escape the recipe, so both are refused.
  assert.match(decision(call('pwsh', { command: 'python scripts/evaluate_expert_profile.py --profile ptc-dft-expert --version draft', workdir: ws }, agent), OTHER_ROOT), DENIED);
});

test('a training session does not dispatch specialists', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  assert.match(decision(call('subagent', { description: 'anything', prompt: 'do work' }, agent), OTHER_ROOT), /does not dispatch/);
});

test('the result channel stays open so a training session can answer', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  for (const name of ['structured_output', 'run_code', 'report']) {
    assert.equal(decision(call(name, { status: 'done' }, agent), OTHER_ROOT), undefined, name);
  }
});

test('a preset selected DURING the session counts, not just the creation header', () => {
  // DSH resolves a session's preset as "newest agent-preset/selected event, else
  // the creation header" (dsh-agent-presets/lib/types/session.js). A header-only
  // read would miss a session the user switched INTO a training preset, leaving it
  // unconfined.
  const ws = trainingWorkspace();
  const switched = {
    session: {
      header: { cwd: ws }, // no preset at creation
      events: [{ type: 'agent-preset/selected', data: { agentPreset: 'ptc-dft-expert' } }],
    },
  };
  assert.match(write(ws, 'scripts/validate_dft_outputs.py', switched), DENIED);
  assert.equal(write(ws, 'team/expert-profiles/ptc-dft-expert/instructions.md', switched), undefined);
});

test('a session that switched AWAY from a training preset is not a training session', () => {
  const ws = trainingWorkspace();
  const away = {
    session: {
      header: { cwd: ws, agentPreset: 'ptc-dft-expert' },
      events: [{ type: 'agent-preset/selected', data: { agentPreset: 'standard-70' } }],
    },
  };
  // The newest selection wins, exactly as DSH resolves it.
  assert.equal(write(ws, 'scripts/validate_dft_outputs.py', away), undefined);
  assert.equal(agentPresetOf(away), 'standard-70');
});

test('allowTrainingPublish: false makes training strictly draft-only', () => {
  const ws = trainingWorkspace();
  const agent = session(ws, 'ptc-dft-expert');
  const publish = 'python scripts/publish_expert_profile.py --profile ptc-dft-expert --version v4';
  assert.equal(decision(call('pwsh', { command: publish }, agent), OTHER_ROOT), undefined, 'default follows handoff 5.1');
  assert.match(decision(call('pwsh', { command: publish }, agent), OTHER_ROOT, { allowTrainingPublish: false }), DENIED);
  assert.equal(
    decision(call('pwsh', { command: 'python scripts/evaluate_expert_profile.py --profile ptc-dft-expert --version draft' }, agent), OTHER_ROOT, { allowTrainingPublish: false }),
    undefined,
    'evaluation stays available in either mode',
  );
});

test('published snapshots are immutable by PATH, independent of any preset', () => {
  // This is the rule that survives the unverified `agentPreset` question: a
  // headless run recorded agentPreset: null, so protection that depended on that
  // field alone would be unproven. An ordinary coding session (no preset at all)
  // still must not be able to hand-edit a published version.
  const ws = trainingWorkspace();
  const plain = { session: { header: { cwd: ws }, events: [] } };
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/versions/v3/profile.yaml', plain), /published version snapshot and status\.json are immutable/);
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/versions/v1/manifest.json', plain), /immutable/);
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/status.json', plain), /immutable/);
  assert.match(write(ws, 'team/expert-profiles/ptc-schematic-expert/status.json', plain), /immutable/);
  // Draft assets stay editable, so training remains possible.
  assert.equal(write(ws, 'team/expert-profiles/ptc-dft-expert/instructions.md', plain), undefined);
  assert.equal(write(ws, 'team/expert-profiles/ptc-dft-expert/cases/TM106/expected.json', plain), undefined);
  // A traversal into versions/ is denied after resolution.
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/cases/../../ptc-dft-expert/versions/v1/x', plain), /immutable/);
  // Even the Captain cannot hand-edit a published snapshot; releasing goes
  // through the gated publisher, which writes it as a program, not via `write`.
  const captain = session(ws, 'ate-ptc');
  assert.match(write(ws, 'team/expert-profiles/ptc-dft-expert/versions/v3/profile.yaml', captain), /immutable/);
});

test('the Captain check resolves the preset the same way, so a switch INTO ate-ptc engages it', async () => {
  // The reviewer flagged this second header-only read. Same defect class as the
  // training rule: a session the user switched into `ate-ptc` kept its old header,
  // so Captain would never engage.
  const { isPtcCaptainAgent } = await import('../lib/captain-entry.js');
  const ws = trainingWorkspace();
  const switched = {
    session: {
      header: { cwd: ws },
      events: [{ type: 'agent-preset/selected', data: { agentPreset: 'ate-ptc' } }],
    },
  };
  assert.equal(isPtcCaptainAgent(switched, ws), true);
  const headerOnly = { session: { header: { cwd: ws, agentPreset: 'ate-ptc' }, events: [] } };
  assert.equal(isPtcCaptainAgent(headerOnly, ws), true, 'the header fallback still works');
  const plain = { session: { header: { cwd: ws, agentPreset: 'standard-70' }, events: [] } };
  assert.equal(isPtcCaptainAgent(plain, ws), false);
});

test('the schematic training preset is covered too, and other sessions are untouched', () => {
  const ws = trainingWorkspace('ptc-schematic-expert');
  const schematic = session(ws, 'ptc-schematic-expert');
  assert.equal(write(ws, 'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md', schematic), undefined);
  assert.match(write(ws, 'team/expert-profiles/ptc-schematic-expert/versions/v1/manifest.json', schematic), DENIED);
  assert.equal(trainingProfileFor('ptc-schematic-expert'), 'ptc-schematic-expert');

  // A Captain session and an ordinary coding session are not training sessions.
  assert.equal(trainingProfileFor('ate-ptc'), undefined);
  assert.equal(trainingProfileFor('standard-70'), undefined);
  const captain = session(ws, 'ate-ptc');
  assert.equal(write(ws, 'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md', captain), undefined, 'the Captain rule is unchanged');
});
