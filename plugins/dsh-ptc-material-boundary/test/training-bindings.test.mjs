import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { decision } from '../lib/policy.js';

/**
 * The training-bindings extension ([28]): a training session's writable set is
 * extended from profileRoot-only to include the address-book directories from
 * Training_Materials/_expert_bindings.json (writes + prefixed verification
 * products), fail-closed. Delivery-labelled experts must be unaffected.
 */
const DENIED = /PTC training boundary/;
const workspaces = [];

function trainingWorkspace(bindings) {
  const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-bindings-')));
  for (const relative of [
    'team/expert-profiles/ptc-dft-expert/instructions.md',
    'team/expert-profiles/ptc-dft-expert/profile.yaml',
    'team/expert-profiles/ptc-dft-expert/CHANGELOG.md',
    'team/expert-profiles/ptc-dft-expert/status.json',
    'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md',
    'team/artifacts/placeholder',
  ]) {
    const full = path.join(ws, relative);
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, 'fixture\n');
  }
  for (const dir of [
    'Training_Materials/Output_Global_Material/dft/TM106',
    'Training_Materials/Output_Global_Material/verification',
    'Training_Materials/Input_GlobalMaterial',
  ]) {
    fs.mkdirSync(path.join(ws, dir), { recursive: true });
  }
  if (bindings !== undefined) writeBindings(ws, bindings);
  workspaces.push(ws);
  return ws;
}

function defaultBindings() {
  return {
    schemaVersion: 2,
    experts: [{
      displayName: 'DFT_Expert',
      profileId: 'ptc-dft-expert',
      stage: 'INPUT_SYNC',
      reads: 'Training_Materials/Input_GlobalMaterial',
      writes: 'Training_Materials/Output_Global_Material/dft',
      verification: 'Training_Materials/Output_Global_Material/verification',
      note: 'fixture',
    }],
  };
}

function writeBindings(ws, doc) {
  const file = path.join(ws, 'Training_Materials', '_expert_bindings.json');
  fs.writeFileSync(file, JSON.stringify(doc, null, 2), 'utf8');
}

const OTHER_ROOT = path.join(os.tmpdir(), 'some-other-deployment-root');
const trainingSession = (ws) => ({ session: { header: { cwd: ws, agentPreset: 'ptc-dft-expert' }, events: [] } });
const call = (name, args, agent) => ({ name, arguments: args, agent });
const write = (ws, relative, agent) => decision(call('write', { file_path: path.join(ws, relative) }, agent), OTHER_ROOT);

after(() => { for (const ws of workspaces) fs.rmSync(ws, { recursive: true, force: true }); });

test('T1: a training session may write inside bindings.writes (training-material snapshot)', () => {
  const ws = trainingWorkspace(defaultBindings());
  const agent = trainingSession(ws);
  assert.equal(write(ws, 'Training_Materials/Output_Global_Material/dft/TM106/dft-meta.json', agent), undefined);
  assert.equal(write(ws, 'Training_Materials/Output_Global_Material/dft/TM106/dft-conditions.yaml', agent), undefined);
});

test('T2: verification products require the expert prefix', () => {
  const ws = trainingWorkspace(defaultBindings());
  const agent = trainingSession(ws);
  assert.equal(write(ws, 'Training_Materials/Output_Global_Material/verification/dft-pin-check-TM106.json', agent), undefined);
  assert.match(write(ws, 'Training_Materials/Output_Global_Material/verification/sch-pin-check-TM106.json', agent), DENIED);
});

test('T3: missing or broken bindings fall back to the profileRoot-only boundary (fail-closed)', () => {
  const ws = trainingWorkspace(); // no bindings file at all
  const agent = trainingSession(ws);
  assert.match(write(ws, 'Training_Materials/Output_Global_Material/dft/TM106/dft-meta.json', agent), DENIED);
  assert.match(write(ws, 'team/artifacts/training-proposals.md', agent), DENIED);
  const ws2 = trainingWorkspace();
  fs.writeFileSync(path.join(ws2, 'Training_Materials', '_expert_bindings.json'), '{not json', 'utf8');
  assert.match(write(ws2, 'Training_Materials/Output_Global_Material/dft/TM106/dft-meta.json', trainingSession(ws2)), DENIED);
});

test('T4: bindings may not grant expert-profile paths (anti self-escalation)', () => {
  const ws = trainingWorkspace({
    schemaVersion: 2,
    experts: [{ profileId: 'ptc-dft-expert', writes: 'team/expert-profiles', verification: 'Training_Materials/Output_Global_Material/verification' }],
  });
  const agent = trainingSession(ws);
  assert.match(write(ws, 'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md', agent), DENIED);
});

test('T5: bindings paths must stay inside the session workspace', () => {
  const ws = trainingWorkspace({
    schemaVersion: 2,
    experts: [{ profileId: 'ptc-dft-expert', writes: '../outside', verification: 'Training_Materials/Output_Global_Material/verification' }],
  });
  const agent = trainingSession(ws);
  assert.match(write(ws, 'Training_Materials/Output_Global_Material/dft/TM106/dft-meta.json', agent), DENIED);
});

test('T6: a delivery-labelled dft expert is unaffected by the training bindings (regression)', () => {
  const ws = trainingWorkspace(defaultBindings());
  const agent = { session: { header: { cwd: ws }, events: [{ type: 'subagent/descriptor', data: { label: 'PTC dft expert [TM106]' } }] } };
  assert.ok(typeof write(ws, 'Training_Materials/Output_Global_Material/dft/TM106/dft-meta.json', agent) === 'string', 'delivery branch must deny non-allowlisted paths exactly as before');
});
