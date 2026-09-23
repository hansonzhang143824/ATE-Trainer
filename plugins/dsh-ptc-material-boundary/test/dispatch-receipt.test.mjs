/**
 * P0-A: run-level dispatch receipt tests (handoff deliverable 5).
 *
 * The point of these tests is anti-spoofing: identity must come from a pinned,
 * digest-verified receipt, never from a label or description an agent can type.
 */
import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildDispatchReceipt,
  identityFromReceipt,
  receiptDigest,
  verifyDispatchReceipt,
} from '../lib/dispatch-receipt.js';
import {
  EXECUTION_CLASSES,
  PROFILE_EXECUTION_CLASS,
  executionClassForProfile,
  isDeclaredPath,
  isExecutionClass,
  policyFor,
} from '../lib/expert-policy-registry.js';

const sha = (char) => char.repeat(64);
const valid = (overrides = {}) => ({
  dispatchId: 'dispatch-tm106-1',
  runId: 'dali-20260919-2200-tm106',
  profileId: 'ptc-dft-expert',
  profileVersion: 'v1',
  executionClass: 'input-dft',
  personaSha256: sha('a'),
  contractSha256: sha('b'),
  policySha256: sha('c'),
  targetTms: ['TM106'],
  createdAt: '2026-09-19T12:00:00.000Z',
  ...overrides,
});

// ── the registry table ─────────────────────────────────────────────────────

test('every declared executionClass is complete and uses only supported placeholders', () => {
  const classes = Object.keys(EXECUTION_CLASSES);
  assert.ok(classes.length >= 6, 'the handoff table has six classes');
  for (const name of classes) {
    const policy = policyFor(name);
    assert.ok(isExecutionClass(name));
    assert.ok(policy.readable.length > 0, `${name} must declare what it may read`);
    assert.ok(policy.writable.length > 0, `${name} must declare where it may write`);
    assert.ok(policy.gates.length > 0, `${name} must declare its gates`);
    for (const declared of [...policy.readable, ...policy.writable]) {
      assert.ok(isDeclaredPath(declared), `${name}: unsupported placeholder in ${declared}`);
    }
  }
  assert.equal(isExecutionClass('nope'), false);
  assert.equal(policyFor('nope'), undefined);
});

test('every expert profile maps to exactly one registered executionClass', () => {
  for (const [profileId, executionClass] of Object.entries(PROFILE_EXECUTION_CLASS)) {
    assert.equal(executionClassForProfile(profileId), executionClass);
    assert.ok(isExecutionClass(executionClass), `${profileId} maps to an unregistered class`);
  }
  assert.equal(executionClassForProfile('captain'), undefined, 'Captain is not an expert profile');
});

test('the input specialists cannot read the other stage products', () => {
  const dft = policyFor('input-dft');
  const schematic = policyFor('input-schematic');
  assert.ok(!dft.readable.some((entry) => entry.includes('schematic')), 'DFT must not read schematic output');
  assert.ok(!schematic.readable.some((entry) => entry.includes('/dft')), 'schematic must not read DFT output');
  // The old IR the handoff calls out explicitly must not appear as a canonical input.
  assert.ok(!schematic.readable.some((entry) => entry.includes('schematic-ir.json')));
});

// ── receipts ───────────────────────────────────────────────────────────────

test('a well-formed receipt verifies, is frozen, and yields pinned identity', () => {
  const receipt = buildDispatchReceipt(valid());
  assert.ok(Object.isFrozen(receipt));
  assert.deepEqual(verifyDispatchReceipt(receipt), { ok: true, errors: [] });
  assert.deepEqual(identityFromReceipt(receipt), {
    profileId: 'ptc-dft-expert',
    profileVersion: 'v1',
    executionClass: 'input-dft',
    targetTms: ['TM106'],
  });
});

test('targetTms are sorted on build so the digest is stable regardless of input order', () => {
  const one = buildDispatchReceipt(valid({ targetTms: ['TM425', 'TM106', 'TM108'] }));
  const two = buildDispatchReceipt(valid({ targetTms: ['TM106', 'TM108', 'TM425'] }));
  assert.deepEqual(one.targetTms, ['TM106', 'TM108', 'TM425']);
  assert.equal(one.digest, two.digest);
});

test('tampering with any pinned field breaks the digest', () => {
  const receipt = buildDispatchReceipt(valid());
  const wider = { ...receipt, targetTms: ['TM106', 'TM110'] };
  const checked = verifyDispatchReceipt(wider);
  assert.equal(checked.ok, false);
  assert.match(checked.errors.join('; '), /digest does not match/);
  assert.throws(() => identityFromReceipt(wider), /receipt rejected/);
});

test('a receipt cannot claim an executionClass its profile does not declare', () => {
  // The anti-spoof check: the label or the description may say anything, but a
  // DFT profile cannot be dispatched as a strategy or implementation expert.
  assert.throws(
    () => buildDispatchReceipt(valid({ executionClass: 'implementation-standard' })),
    /declares executionClass input-dft/,
  );
  assert.throws(
    () => buildDispatchReceipt(valid({ profileId: 'captain' })),
    /not a registered expert profile/,
  );
  assert.throws(
    () => buildDispatchReceipt(valid({ executionClass: 'input-schematic' })),
    /declares executionClass input-dft/,
  );
});

test('a receipt with no target TMs is rejected: unscoped input experts are not dispatchable', () => {
  assert.throws(() => buildDispatchReceipt(valid({ targetTms: [] })), /non-empty array/);
  assert.throws(() => buildDispatchReceipt(valid({ targetTms: ['tm106'] })), /TM<digits>/);
  assert.throws(() => buildDispatchReceipt(valid({ targetTms: ['TM106', 'TM106'] })), /must not repeat/);
});

test('a draft version is representable; a bogus version is not', () => {
  assert.equal(buildDispatchReceipt(valid({ profileVersion: 'draft' })).profileVersion, 'draft');
  assert.throws(() => buildDispatchReceipt(valid({ profileVersion: 'latest' })), /draft.*v<|v<n>/);
  assert.throws(() => buildDispatchReceipt(valid({ profileVersion: '2' })), /draft|v<n>/);
});

test('unpinned hashes are rejected', () => {
  assert.throws(() => buildDispatchReceipt(valid({ personaSha256: 'not-a-hash' })), /personaSha256/);
  assert.throws(() => buildDispatchReceipt(valid({ policySha256: sha('C') })), /policySha256/, 'uppercase hex is not a pinned lowercase sha256');
});

test('a label may be recorded for display, and never changes the identity', () => {
  const withLabel = buildDispatchReceipt(valid({ label: 'PTC dft expert [TM106]' }));
  const withoutLabel = buildDispatchReceipt(valid());
  assert.equal(identityFromReceipt(withLabel).executionClass, 'input-dft');
  assert.deepEqual(identityFromReceipt(withoutLabel).targetTms, identityFromReceipt(withLabel).targetTms);
  assert.notEqual(withLabel.digest, withoutLabel.digest, 'the recorded label is covered by the digest');
});

test('the digest is a pure function of the receipt contents', () => {
  const receipt = buildDispatchReceipt(valid());
  assert.equal(receiptDigest(receipt), receipt.digest);
  assert.equal(receiptDigest({ ...receipt, digest: 'anything' }), receipt.digest, 'the digest field is excluded from its own input');
});
