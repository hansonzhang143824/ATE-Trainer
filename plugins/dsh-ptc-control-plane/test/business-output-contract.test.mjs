import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {
  createBusinessOutputHashRecord,
  verifyBusinessOutputHashRecord,
} from '../lib/business-output-contract.js';

const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const jsonBytes = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`, 'utf8');

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-tm109-contract-'));
  const runId = 'business-contract-run';
  const directory = path.join(root, 'Training_Materials', 'runs', runId, 'input-sync', 'dft', 'TM109');
  fs.mkdirSync(directory, { recursive: true });
  const sourceInputSha256 = 'a'.repeat(64);
  const meta = {
    schemaVersion: 1,
    artifactId: 'dft-meta',
    tm: 'TM109',
    parseStatus: 'ok',
    sourceSha256: sourceInputSha256,
  };
  const conditions = [
    'schemaVersion: 1',
    'artifact: dft-conditions',
    'tm: TM109',
    `sourceSha256: ${sourceInputSha256}`,
    '',
  ].join('\n');
  const metaBytes = jsonBytes(meta);
  const conditionsBytes = Buffer.from(conditions, 'utf8');
  const review = {
    schemaVersion: 1,
    artifactId: 'dft-semantic-review',
    tm: 'TM109',
    verdict: 'PASS',
    sourceSha256: sourceInputSha256,
    artifactHashes: {
      'dft-meta.json': sha256(metaBytes),
      'dft-conditions.yaml': sha256(conditionsBytes),
    },
  };
  fs.writeFileSync(path.join(directory, 'dft-meta.json'), metaBytes);
  fs.writeFileSync(path.join(directory, 'dft-conditions.yaml'), conditionsBytes);
  fs.writeFileSync(path.join(directory, 'dft-semantic-review.json'), jsonBytes(review));
  return { root, runId, directory, sourceInputSha256 };
}

test('TM109 BUSINESS_ONLY outputs produce an immutable hash evidence record', () => {
  const input = fixture();
  const result = createBusinessOutputHashRecord({
    workspaceRoot: input.root,
    runId: input.runId,
    testItems: ['TM109'],
    outputRoot: path.relative(input.root,
      path.join(input.root, 'Training_Materials', 'runs', input.runId, 'input-sync', 'dft')),
    sourceInputSha256: input.sourceInputSha256,
    profileId: 'ptc-dft-expert-copy',
    profileRevision: 'rev-20260928',
  });
  assert.equal(result.record.mode, 'BUSINESS_ONLY');
  assert.equal(result.record.businessGatePassed, true);
  assert.equal(result.record.testItems[0], 'TM109');
  assert.equal(result.record.outputs.length, 3);
  assert.deepEqual([...new Set(result.record.outputs.map(row => row.status))], ['validated']);
  assert.ok(result.record.outputs.every(row => row.agentId === 'ptc-dft-expert-copy'));
  assert.ok(result.record.outputs.every(row => row.agentRevision === 'rev-20260928'));
  assert.ok(fs.existsSync(result.evidenceFile));
  const verified = verifyBusinessOutputHashRecord(input.root, result.evidenceFile);
  assert.equal(verified.record.outputs.length, 3);
  assert.equal(verified.evidenceSha256, result.evidenceSha256);
});

test('TM109 hash evidence rejects a changed output byte', () => {
  const input = fixture();
  const result = createBusinessOutputHashRecord({
    workspaceRoot: input.root,
    runId: input.runId,
    outputRoot: path.relative(input.root,
      path.join(input.root, 'Training_Materials', 'runs', input.runId, 'input-sync', 'dft')),
    sourceInputSha256: input.sourceInputSha256,
  });
  fs.appendFileSync(path.join(input.directory, 'dft-conditions.yaml'), '# tampered\n');
  assert.throws(() => verifyBusinessOutputHashRecord(input.root, result.evidenceFile), /output changed after hash record/);
});

test('TM109 contract rejects missing or non-PASS semantic review', () => {
  const input = fixture();
  const reviewFile = path.join(input.directory, 'dft-semantic-review.json');
  const review = JSON.parse(fs.readFileSync(reviewFile, 'utf8'));
  review.verdict = 'BLOCKED';
  fs.writeFileSync(reviewFile, jsonBytes(review));
  assert.throws(() => createBusinessOutputHashRecord({
    workspaceRoot: input.root,
    runId: input.runId,
    outputRoot: path.relative(input.root,
      path.join(input.root, 'Training_Materials', 'runs', input.runId, 'input-sync', 'dft')),
    sourceInputSha256: input.sourceInputSha256,
  }), /semantic-review.json did not PASS/);
});
