import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import test from 'node:test';
import { listTrainingDrafts, readTrainingDraft, saveTrainingDraft, TRAINING_DRAFT_MAX_BYTES } from '../lib/training-drafts.js';

const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-draft-edit-'));
  const profileId = 'ptc-dft-expert';
  const directory = path.join(root, 'team/expert-profiles', profileId);
  fs.mkdirSync(directory, { recursive: true });
  const initial = Buffer.from('\uFEFFOriginal\r\n规则\r\n');
  fs.writeFileSync(path.join(directory, 'instructions.md'), initial);
  fs.writeFileSync(path.join(directory, 'profile.yaml'), 'id: ptc-dft-expert\n');
  fs.writeFileSync(path.join(directory, 'output-contract.schema.json'), '{"type":"object"}\n');
  fs.writeFileSync(path.join(directory, 'status.json'), '{"publishedVersion":"v6"}\n');
  return { root, profileId, directory, initial, input: { mode: 'training', profileId, file: 'instructions.md', expectedSha256: sha(initial), content: 'Revised\n新规则\n' } };
}

test('list/read return only editable existing drafts and exact-byte SHA256', () => {
  const { root, profileId, initial } = fixture();
  const profiles = listTrainingDrafts(root);
  assert.equal(profiles.length, 1);
  assert.equal(profiles[0].profileId, profileId);
  assert.deepEqual(profiles[0].files.map((entry) => entry.file), ['instructions.md', 'profile.yaml', 'output-contract.schema.json']);
  const draft = readTrainingDraft(root, { profileId, file: 'instructions.md' });
  assert.equal(draft.content, initial.toString('utf8'));
  assert.equal(draft.sha256, sha(initial));
  assert.equal(draft.sizeBytes, initial.length);
});

test('save records exact old/new bytes and changes no published version or snapshot', () => {
  const { root, directory, initial, input } = fixture();
  const frozen = path.join(directory, 'versions/v6');
  fs.mkdirSync(frozen, { recursive: true });
  fs.writeFileSync(path.join(frozen, 'instructions.md'), 'PUBLISHED');
  const status = fs.readFileSync(path.join(directory, 'status.json'));
  const result = saveTrainingDraft(root, input);
  assert.equal(result.changed, true);
  assert.equal(result.previousSha256, sha(initial));
  assert.equal(result.sha256, sha(Buffer.from(input.content)));
  const auditRoot = path.join(root, 'Training_Materials/draft-history', result.historyId);
  assert.deepEqual(fs.readFileSync(path.join(auditRoot, 'before.bin')), initial);
  assert.deepEqual(fs.readFileSync(path.join(auditRoot, 'after.bin')), Buffer.from(input.content));
  const audit = JSON.parse(fs.readFileSync(path.join(auditRoot, 'audit.json'), 'utf8'));
  assert.equal(audit.status, 'applied');
  assert.equal(audit.mode, 'training');
  assert.equal(audit.sha256, result.sha256);
  assert.equal(readTrainingDraft(root, input).content, input.content);
  assert.deepEqual(fs.readFileSync(path.join(directory, 'status.json')), status);
  assert.equal(fs.readFileSync(path.join(frozen, 'instructions.md'), 'utf8'), 'PUBLISHED');
  assert.equal(fs.existsSync(path.join(directory, '.training-draft.lock')), false);
});

test('stale editor cannot overwrite a newer draft', () => {
  const { root, input } = fixture();
  const first = saveTrainingDraft(root, input);
  assert.throws(() => saveTrainingDraft(root, { ...input, content: 'stale overwrite' }), { code: 'DRAFT_CONFLICT' });
  assert.equal(readTrainingDraft(root, input).sha256, first.sha256);
});

test('profile lock prevents concurrent edits even to different draft files', () => {
  const { root, directory, input } = fixture();
  fs.writeFileSync(path.join(directory, '.training-draft.lock'), 'another process');
  assert.throws(() => saveTrainingDraft(root, input), { code: 'DRAFT_BUSY' });
  assert.equal(fs.readFileSync(path.join(directory, '.training-draft.lock'), 'utf8'), 'another process');
});

test('unchanged save does not rewrite draft or create history', () => {
  const { root, directory, initial, input } = fixture();
  const before = fs.statSync(path.join(directory, input.file)).mtimeMs;
  const result = saveTrainingDraft(root, { ...input, content: initial.toString('utf8') });
  assert.equal(result.changed, false);
  assert.equal(result.historyId, null);
  assert.equal(fs.statSync(path.join(directory, input.file)).mtimeMs, before);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/draft-history')), false);
});

test('mode, traversal, versions, unpublished file creation and non-text payloads fail closed', () => {
  const { root, input } = fixture();
  for (const mode of [undefined, 'published', 'delivery']) {
    assert.throws(() => saveTrainingDraft(root, { ...input, mode }), { code: 'DRAFT_MODE_REQUIRED' });
  }
  for (const profileId of ['../ptc-dft-expert', 'ptc-dft-expert/versions/v6', 'CON', 'ptc-dft-expert.']) {
    assert.throws(() => saveTrainingDraft(root, { ...input, profileId }), { code: 'DRAFT_INVALID_PROFILE' });
  }
  for (const file of ['status.json', 'versions/v6/instructions.md', '../instructions.md']) {
    assert.throws(() => saveTrainingDraft(root, { ...input, file }), { code: 'DRAFT_INVALID_FILE' });
  }
  assert.throws(() => saveTrainingDraft(root, { ...input, profileId: 'missing-expert' }));
  assert.throws(() => saveTrainingDraft(root, { ...input, content: {} }), { code: 'DRAFT_INVALID_TEXT' });
  assert.throws(() => saveTrainingDraft(root, { ...input, content: '\ud800' }), { code: 'DRAFT_INVALID_TEXT' });
  assert.throws(() => saveTrainingDraft(root, { ...input, content: 'a'.repeat(TRAINING_DRAFT_MAX_BYTES + 1) }), { code: 'DRAFT_TOO_LARGE' });
  assert.throws(() => saveTrainingDraft(root, { ...input, expectedSha256: input.expectedSha256.toUpperCase() }), { code: 'DRAFT_CONFLICT' });
});

test('hardlinked draft cannot change its linked published copy', () => {
  const { root, directory, input } = fixture();
  const link = path.join(directory, 'published-copy.md');
  fs.linkSync(path.join(directory, input.file), link);
  assert.throws(() => readTrainingDraft(root, input), { code: 'DRAFT_UNSAFE_PATH' });
  assert.throws(() => saveTrainingDraft(root, input), { code: 'DRAFT_UNSAFE_PATH' });
});

test('junction profile and redirected history roots fail closed', () => {
  const { root, directory, input } = fixture();
  fs.symlinkSync(directory, path.join(root, 'team/expert-profiles/linked-expert'), 'junction');
  assert.throws(() => readTrainingDraft(root, { ...input, profileId: 'linked-expert' }), { code: 'DRAFT_UNSAFE_PATH' });
  assert.throws(() => listTrainingDrafts(root), { code: 'DRAFT_UNSAFE_PATH' });
  fs.mkdirSync(path.join(root, 'Training_Materials'));
  fs.symlinkSync(directory, path.join(root, 'Training_Materials/draft-history'), 'junction');
  assert.throws(() => saveTrainingDraft(root, input), { code: 'DRAFT_UNSAFE_PATH' });
});

test('failed replacement preserves preimage audit and never reports success', () => {
  const { root, initial, input } = fixture();
  const original = fs.renameSync;
  fs.renameSync = () => { throw Object.assign(new Error('replacement denied'), { code: 'EACCES' }); };
  try { assert.throws(() => saveTrainingDraft(root, input), /replacement denied/); }
  finally { fs.renameSync = original; }
  assert.equal(readTrainingDraft(root, input).sha256, sha(initial));
  const histories = fs.readdirSync(path.join(root, 'Training_Materials/draft-history'));
  assert.equal(histories.length, 1);
  const auditRoot = path.join(root, 'Training_Materials/draft-history', histories[0]);
  assert.equal(JSON.parse(fs.readFileSync(path.join(auditRoot, 'audit.json'), 'utf8')).status, 'prepared');
  assert.deepEqual(fs.readFileSync(path.join(auditRoot, 'before.bin')), initial);
});

test('audit finalization failure is an error even if replacement already occurred', () => {
  const { root, directory, input } = fixture();
  const original = fs.writeFileSync;
  fs.writeFileSync = (file, data, options) => {
    if (String(file).endsWith('audit.json') && String(data).includes('"applied"')) throw new Error('audit finalization denied');
    return original(file, data, options);
  };
  try { assert.throws(() => saveTrainingDraft(root, input), /audit finalization denied/); }
  finally { fs.writeFileSync = original; }
  assert.equal(readTrainingDraft(root, input).content, input.content);
  assert.equal(fs.existsSync(path.join(directory, '.training-draft.lock')), false);
});
