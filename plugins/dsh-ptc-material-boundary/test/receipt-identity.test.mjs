/**
 * Receipt-first identity for the material boundary (handoff section 7.1).
 *
 * The property that matters most here is the FIRST test: with no receipt on disk
 * the boundary behaves exactly as before, so adopting pinned dispatch cannot
 * silently change an existing deployment.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { decision } from '../lib/policy.js';
import { receiptIdentityFor } from '../lib/receipt-scope.js';
import { buildDispatchReceipt, receiptDigest } from '../lib/dispatch-receipt.js';

const DENIED = /PTC material boundary/;
const PINNED_DENIED = /PTC pinned identity/;
const workspaces = [];

function workspace({ withReceipt = true, receiptOverrides = {}, corruptReceipt = false } = {}) {
  const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-receipt-id-')));
  const put = (rel, text = 'x\n') => {
    const full = path.join(ws, rel);
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, text);
    return full;
  };
  put('project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx');
  put('project/DALI/Output_Global_Material/dft/TM106/dft-meta.json');
  put('project/DALI/Output_Global_Material/dft/TM110/dft-meta.json');
  if (withReceipt) {
    const receipt = buildDispatchReceipt({
      dispatchId: 'ptc-dft-expert-run-1-TM106',
      runId: 'run-1',
      profileId: 'ptc-dft-expert',
      profileVersion: 'v3',
      executionClass: 'input-dft',
      personaSha256: 'a'.repeat(64),
      contractSha256: 'b'.repeat(64),
      policySha256: 'c'.repeat(64),
      targetTms: ['TM106'],
      createdAt: '2026-09-19T12:00:00.000Z',
      label: 'PTC dft expert [TM106]',
      ...receiptOverrides,
    });
    const record = { ...receipt, childSessionId: 'child-session-1', dispatchedAt: '2026-09-19T12:00:01.000Z' };
    record.digest = receiptDigest(record);
    if (corruptReceipt) record.targetTms = ['TM106', 'TM110', 'TM425']; // digest now stale
    put(path.join('team', 'artifacts', 'dispatch-receipts', 'ptc-dft-expert-run-1-TM106.json'), `${JSON.stringify(record, null, 2)}\n`);
  }
  workspaces.push(ws);
  return ws;
}

const child = (ws, { id = 'child-session-1', label = 'PTC dft expert [TM106]' } = {}) => ({
  id,
  session: { header: { cwd: ws }, events: label === null ? [] : [{ type: 'subagent/descriptor', data: { label } }] },
});
const call = (name, args, agent) => ({ name, arguments: args, agent });
const out = (ws, tm) => path.join(ws, 'project', 'DALI', 'Output_Global_Material', 'dft', tm, 'dft-meta.json');

after(() => {
  for (const ws of workspaces) fs.rmSync(ws, { recursive: true, force: true });
});

// ── the safety property: no receipt means today's behaviour ────────────────

test('with no receipt on disk the boundary behaves exactly as before', () => {
  const ws = workspace({ withReceipt: false });
  const agent = child(ws);
  assert.equal(decision(call('read', { file_path: out(ws, 'TM106') }, agent), ws), undefined);
  assert.match(decision(call('read', { file_path: out(ws, 'TM110') }, agent), ws), DENIED);
  // The documented fail-open case is unchanged too: an unrecognised label still
  // gets no boundary when nothing is pinned.
  const spoofed = child(ws, { label: 'PTC dft EXPERt [TM106]' });
  assert.equal(decision(call('read', { file_path: out(ws, 'TM110') }, spoofed), ws), undefined);
  assert.equal(receiptIdentityFor(ws, agent).kind, 'unpinned');
});

// ── a pinned receipt becomes the authoritative identity ────────────────────

test('a pinned child whose label is unrecognisable is STILL boundary-controlled', () => {
  const ws = workspace();
  const agent = child(ws, { label: 'PTC dft EXPERt [TM106]' }); // legacy regex does not match
  assert.equal(receiptIdentityFor(ws, agent).kind, 'pinned');
  assert.equal(decision(call('read', { file_path: out(ws, 'TM106') }, agent), ws), undefined, 'its own output stays readable');
  assert.match(decision(call('read', { file_path: out(ws, 'TM110') }, agent), ws), DENIED, 'the receipt closes the fail-open hole');
  assert.match(decision(call('read', { file_path: out(ws, 'TM110') }, agent), ws), DENIED);
});

test('a pinned child with NO descriptor label at all is still boundary-controlled', () => {
  const ws = workspace();
  const agent = child(ws, { label: null });
  assert.equal(decision(call('read', { file_path: out(ws, 'TM106') }, agent), ws), undefined);
  assert.match(decision(call('read', { file_path: out(ws, 'TM110') }, agent), ws), DENIED);
});

test('the receipt narrows the scope even when the label claims more TMs', () => {
  const ws = workspace();
  const agent = child(ws, { label: 'PTC dft expert [TM106,TM110]' }); // label scope would allow TM110
  assert.match(decision(call('read', { file_path: out(ws, 'TM110') }, agent), ws), DENIED,
    'the pinned receipt pins TM106 only, so TM110 must be refused');
  assert.equal(decision(call('read', { file_path: out(ws, 'TM106') }, agent), ws), undefined);
});

test('a pinned schematic child is judged by the schematic rule, not by its label shape', () => {
  const ws = workspace({ receiptOverrides: { profileId: 'ptc-schematic-expert', executionClass: 'input-schematic', label: 'PTC schematic expert', dispatchId: 'ptc-schematic-expert-run-1-TM106' } });
  const agent = child(ws, { label: 'totally-unknown-label' });
  assert.equal(receiptIdentityFor(ws, agent).kind, 'pinned');
  assert.match(decision(call('read', { file_path: out(ws, 'TM106') }, agent), ws), DENIED, 'a schematic expert cannot read DFT output');
});

// ── refusals, never fail-open ─────────────────────────────────────────────

test('a child using a pinned label from a DIFFERENT session is refused', () => {
  const ws = workspace();
  const impostor = child(ws, { id: 'some-other-session' });
  const identity = receiptIdentityFor(ws, impostor);
  assert.equal(identity.kind, 'mismatch');
  assert.match(identity.reason, /names a different session/);
  assert.match(decision(call('read', { file_path: out(ws, 'TM106') }, impostor), ws), PINNED_DENIED);
  assert.match(decision(call('read', { file_path: out(ws, 'TM106') }, impostor), ws), PINNED_DENIED);
});

test('a tampered receipt is refused rather than silently ignored', () => {
  const ws = workspace({ corruptReceipt: true });
  const agent = child(ws);
  const identity = receiptIdentityFor(ws, agent);
  assert.equal(identity.kind, 'mismatch');
  assert.match(identity.reason, /fails verification/);
  assert.match(decision(call('read', { file_path: out(ws, 'TM110') }, agent), ws), PINNED_DENIED,
    'a corrupted pin must not fall back to a label that might have been the lie');
});

test('an ambiguous claim across two receipts is refused', () => {
  const ws = workspace();
  const file = path.join(ws, 'team', 'artifacts', 'dispatch-receipts', 'duplicate.json');
  const original = JSON.parse(fs.readFileSync(path.join(ws, 'team', 'artifacts', 'dispatch-receipts', 'ptc-dft-expert-run-1-TM106.json'), 'utf8'));
  const duplicate = { ...original, dispatchId: 'ptc-dft-expert-run-1-TM106-copy' };
  duplicate.digest = receiptDigest(duplicate);
  fs.writeFileSync(file, `${JSON.stringify(duplicate, null, 2)}\n`);
  const identity = receiptIdentityFor(ws, child(ws));
  assert.equal(identity.kind, 'mismatch');
  assert.match(identity.reason, /ambiguous/);
});

test('an unrelated child that no receipt mentions still falls back to the label rule', () => {
  const ws = workspace();
  const other = child(ws, { id: 'child-session-9', label: 'PTC schematic expert' });
  assert.equal(receiptIdentityFor(ws, other).kind, 'unpinned');
  assert.match(decision(call('read', { file_path: out(ws, 'TM106') }, other), ws), DENIED, 'the legacy schematic rule still applies');
});
