import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { ensureTrainerProject, readProject } from '../lib/trainer-project.js';
import { createTrainerService, DEFAULT_TRAINER_PROJECT_ID } from '../lib/trainer-service.js';
import { createFrameworkRunner } from '../lib/framework-agent-run.js';
import * as bundles from '../lib/trainer-bundle.js';
import * as releases from '../lib/trainer-release.js';
import { validateJson } from '../lib/trainer-schema.js';

const repo = fileURLToPath(new URL('../../../', import.meta.url));
const read = file => fs.readFileSync(path.join(repo, file), 'utf8');

function serviceAt(root) {
  const runner = createFrameworkRunner({
    workspaceRoot: root,
    adapter: { async dispatch() { throw new Error('empty registry must not dispatch'); } },
    verifyBundle: bundles.verifyBundle,
    validateJson,
  });
  return createTrainerService({ workspaceRoot: root, runner,
    repositories: { ...requireRepositories(), ...bundles, ...releases },
    modelResolver: () => ({ provider: 'test', model: 'test' }),
  });
}
function requireRepositories() {
  // Avoid importing the module namespace twice in the test's top-level setup.
  return { ensureTrainerProject, readProject };
}

test('D1 active registry is empty and historical profiles are archive-only', () => {
  const registry = JSON.parse(read('team/ptc/ptc_stage_registry.json'));
  assert.deepEqual(registry.stateMachine, []);
  assert.deepEqual(registry.stages, {});
  const index = JSON.parse(read('team/ptc/native-control-plane/archive/DFT-SCHEMATIC-LEGACY-20260923/HISTORICAL-EXPERT-MATERIALS-INDEX.json'));
  assert.equal(index.readOnly, true);
  assert.equal(index.profiles.length, 8);
  for (const relative of index.profiles) {
    assert.match(relative, /^historical-experts\/team\/expert-profiles\//);
    assert.equal(fs.existsSync(path.join(repo, 'team/ptc/native-control-plane/archive/DFT-SCHEMATIC-LEGACY-20260923', relative)), true);
  }
  assert.doesNotMatch(read('plugins/dsh-ptc-control-plane/lib/trainer-synthetic-fixture.js'), /ptc-dft-expert|ptc-schematic-expert/);
});

test('D1 default project never reads archive material and starts with no assets', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-empty-project-'));
  try {
    const project = ensureTrainerProject(root, { projectId: DEFAULT_TRAINER_PROJECT_ID });
    assert.deepEqual(project.agents, []);
    assert.deepEqual(project.workflows, []);
    assert.deepEqual(readProject(root, { projectId: DEFAULT_TRAINER_PROJECT_ID }).agents, []);
    assert.deepEqual(readProject(root, { projectId: DEFAULT_TRAINER_PROJECT_ID }).workflows, []);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('D2 page context exposes the empty registry and cannot run a missing workflow', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-empty-context-'));
  try {
    const service = serviceAt(root);
    const context = await service.invoke('context', {}, { kind: 'page' });
    assert.equal(context.ok, true, JSON.stringify(context));
    assert.equal(context.value.project.projectId, DEFAULT_TRAINER_PROJECT_ID);
    assert.deepEqual(context.value.project.agents, []);
    assert.deepEqual(context.value.project.workflows, []);
    const run = await service.invoke('run', { targetKind: 'workflow', targetId: 'history', requestId: 'empty-run', input: {} }, { kind: 'page' });
    assert.equal(run.ok, false);
    assert.equal(typeof run.error.code, 'string');
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('D2 white page starts blank and PTC panel only exposes the bridge entry', () => {
  const page = read('docs/prototypes/agent-trainer-repair-prototype.html');
  assert.match(page, /const agents=\{\};/);
  assert.match(page, /workflow:null/);
  assert.match(page, /empty:true/);
  assert.doesNotMatch(page, /ptc-dft-expert|ptc-schematic-expert|Offline-Coding-Flow/);
  const panel = read('plugins/dsh-ptc-control-plane/client/panel.js');
  assert.match(panel, /ptc-cp-open-white-trainer/);
  assert.match(panel, /ptc-cp-host-capability/);
  assert.doesNotMatch(panel.slice(panel.lastIndexOf('return createElement(')), /PtcWorkbench/);
});
