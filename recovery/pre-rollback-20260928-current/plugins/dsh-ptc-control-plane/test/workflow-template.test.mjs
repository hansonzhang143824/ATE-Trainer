import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { readWorkflowTemplate, saveWorkflowTemplate, freezeWorkflowTemplate,
  loadFrozenWorkflowTemplate } from '../lib/workflow-template.js';

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-workflow-template-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  for (const id of ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert']) {
    fs.mkdirSync(path.join(root, 'team', 'expert-profiles', id), { recursive: true });
  }
  return root;
}
const candidate = profileIds => ({ templateId: 'pilot', name: 'Smoke pilot', profileIds,
  instruction: '1+2等于几，把答案写在JSON里', expectedAnswer: 3 });

test('one, three and reordered Agents save as exact-byte immutable workflow candidates', t => {
  const root = fixture(t);
  let previous = null;
  for (const ids of [
    ['ptc-dft-expert'],
    ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert'],
    ['strategy-expert', 'ptc-dft-expert', 'ptc-schematic-expert'],
  ]) {
    const saved = saveWorkflowTemplate(root, { expectedSha256: previous, template: candidate(ids) });
    assert.deepEqual(saved.template.profileIds, ids);
    const frozen = freezeWorkflowTemplate(root, { templateId: 'pilot', sha256: saved.sha256 });
    assert.deepEqual(loadFrozenWorkflowTemplate(root, 'pilot', frozen.versionSha256).template.profileIds, ids);
    previous = saved.sha256;
  }
  assert.equal(readWorkflowTemplate(root, 'pilot').sha256, previous);
  assert.equal(readWorkflowTemplate(root, 'pilot').frozenSha256, previous);
});

test('stale save and modified frozen bytes fail closed', t => {
  const root = fixture(t);
  const saved = saveWorkflowTemplate(root, { expectedSha256: null,
    template: candidate(['ptc-dft-expert']) });
  assert.throws(() => saveWorkflowTemplate(root, { expectedSha256: null,
    template: candidate(['strategy-expert']) }), { code: 'WORKFLOW_TEMPLATE_CONFLICT' });
  const frozen = freezeWorkflowTemplate(root, { templateId: 'pilot', sha256: saved.sha256 });
  fs.appendFileSync(path.join(root, frozen.path), ' ');
  assert.throws(() => loadFrozenWorkflowTemplate(root, 'pilot', frozen.versionSha256), /modified/);
});

test('an active template edit lock rejects a competing save without changing bytes', t => {
  const root = fixture(t);
  const first = saveWorkflowTemplate(root, { expectedSha256: null,
    template: candidate(['ptc-dft-expert']) });
  const lock = path.join(root, 'Training_Materials', 'workflow-templates', 'pilot', '.edit-lock');
  fs.mkdirSync(lock);
  try {
    assert.throws(() => saveWorkflowTemplate(root, { expectedSha256: first.sha256,
      template: candidate(['strategy-expert']) }), { code: 'WORKFLOW_TEMPLATE_CONFLICT' });
    assert.equal(readWorkflowTemplate(root, 'pilot').sha256, first.sha256);
  } finally { fs.rmdirSync(lock); }
});
