import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { sha256Bytes } from '../lib/release-integrity.js';
import { activateStagedTrainingRelease, loadTrainingRelease, rollbackTrainingRelease,
  stageTrainingRelease, executePublishedSmoke, createPublishedSmokeDispatcher,
  verifySmokeCandidate, listTrainingReleases } from '../lib/training-release.js';

const sha = value => sha256Bytes(Buffer.from(value));
const PROFILES = ['ate-implementer', 'compile-diagnostician', 'evolution-expert',
  'method-expert', 'ptc-dft-expert', 'ptc-schematic-expert', 'rule-reviewer', 'strategy-expert'];
const STAGES = ['INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD',
  'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION', 'COMPILE'];
const ROLE_PROFILES = { 'dft-expert': 'ptc-dft-expert', 'schematic-expert': 'ptc-schematic-expert',
  'test-strategy-architect': 'strategy-expert', 'test-method-expert': 'method-expert',
  'rule-reviewer': 'rule-reviewer', 'ate-implementer': 'ate-implementer',
  'compile-diagnostician': 'compile-diagnostician', 'evolution-expert': 'evolution-expert' };

function fixture(t) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-smoke-release-'));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const write = (name, value) => {
    const file = path.join(workspaceRoot, name);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, typeof value === 'object' && !Buffer.isBuffer(value) ? `${JSON.stringify(value, null, 2)}\n` : value);
    return file;
  };
  const read = name => JSON.parse(fs.readFileSync(path.join(workspaceRoot, name), 'utf8'));
  const registry = { stateMachine: [...STAGES, 'COMPLETE'], stages: Object.fromEntries(STAGES.map((stage, index) =>
    [stage, { owner: ['captain', 'test-strategy-architect', 'test-method-expert', 'rule-reviewer',
      'ate-implementer', 'rule-reviewer', 'compile-diagnostician'][index], gate: `scripts/${stage.toLowerCase()}.py` }])) };
  write('team/ptc/ptc_stage_registry.json', registry);
  write('scripts/hash_ate_plaintext.py', `import hashlib,json,pathlib,sys\nprint(json.dumps({'sha256':hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest(),'view':'python-plaintext'}))\n`);
  for (const profileId of PROFILES) {
    for (const draft of ['instructions.md', 'profile.yaml', 'output-contract.schema.json']) {
      write(`team/expert-profiles/${profileId}/${draft}`, `${profileId}:${draft}\n`);
    }
  }
  for (const stage of STAGES) write(`scripts/${stage.toLowerCase()}.py`, `# ${stage}\n`);
  write('plugins/dsh-ptc-control-plane/lib/smoke-execution.js', 'export const smoke = true;\n');
  const runContext = runId => ({ schemaVersion: 1, runId, mode: 'training',
    artifactRoot: `Training_Materials/runs/${runId}`, releaseId: null, projectId: null,
    profileSource: 'draft', orchestrationSource: 'draft' });
  const profileRunIds = Object.fromEntries(PROFILES.map((profile, index) => [profile, `smoke-profile-${index}`]));
  for (const [profileId, runId] of Object.entries(profileRunIds)) {
    const prefix = `Training_Materials/runs/${runId}`;
    write(`${prefix}/run.json`, runContext(runId));
    const profileFiles = ['instructions.md', 'profile.yaml', 'output-contract.schema.json'].map(file => {
      const source = `team/expert-profiles/${profileId}/${file}`;
      const destination = `${prefix}/profile/${file}`;
      write(destination, fs.readFileSync(path.join(workspaceRoot, source)));
      return { source, path: destination, sha256: sha256Bytes(fs.readFileSync(path.join(workspaceRoot, destination))),
        view: 'python-plaintext', bytes: fs.statSync(path.join(workspaceRoot, destination)).size };
    });
    const snapshot = `${prefix}/profile/snapshot.json`;
    write(snapshot, { schemaVersion: 1, kind: 'ptc-profile-smoke-snapshot', runId, profileId,
      files: profileFiles });
    const child = `${prefix}/evidence/profile-smoke-child.json`;
    write(child, { stopReason: 'completed', structured: { answer: 3 } });
    const evidence = `${prefix}/evidence/profile-smoke.json`;
    write(evidence, { schemaVersion: 1, kind: 'ptc-profile-smoke', runId, profileId,
      status: 'completed', mode: 'SMOKE_ONLY', businessGatePassed: false,
      profileInstructionsValidated: false, modelDispatched: true, answer: 3,
      childSessionId: `individual-${runId}`,
      profileSnapshotPath: snapshot,
      profileSnapshotSha256: sha256Bytes(fs.readFileSync(path.join(workspaceRoot, snapshot))), responsePath: child,
      responseSha256: sha256Bytes(fs.readFileSync(path.join(workspaceRoot, child))) });
    write(`${prefix}/state.json`, { schemaVersion: 1, runId, purpose: 'smoke-training', status: 'completed',
      target: { kind: 'profile', profileId }, outcome: { mode: 'SMOKE_ONLY', businessGatePassed: false,
        evidence, evidenceSha256: sha256Bytes(fs.readFileSync(path.join(workspaceRoot, evidence))) } });
  }
  const pipelineRunId = 'smoke-pipeline';
  const pipelinePrefix = `Training_Materials/runs/${pipelineRunId}`;
  write(`${pipelinePrefix}/run.json`, runContext(pipelineRunId));
  const profileBindings = Object.fromEntries(Object.entries(ROLE_PROFILES).map(([role, profileId]) => [role,
    { profileId, profileVersion: 'v1', profileDigest: sha(profileId) }]));
  const makeTask = (stage, role, sequence) => {
    const executionKind = 'arithmetic-child';
    const dispatchId = `${pipelineRunId}:${stage}:${role}:1`;
    const child = write(`${pipelinePrefix}/evidence/child-${sequence}.json`, {
      runId: pipelineRunId, dispatchId, role, stage, executionKind,
      answer: 3, childSessionId: `session-${sequence}` });
    return { stage, role, ...profileBindings[role], dispatchId, executionKind,
      status: 'completed', answer: 3, captainVerified: true, childSessionId: `session-${sequence}`,
      childEvidencePath: child, childEvidenceSha256: sha256Bytes(fs.readFileSync(child)) };
  };
  const progress = { schemaVersion: 1, runId: pipelineRunId, mode: 'SMOKE_ONLY',
    status: 'completed', smokePassed: true, businessGatePassed: false, profileBindings,
    stages: STAGES.map((stage, index) => ({ stage, owner: registry.stages[stage].owner,
      gate: registry.stages[stage].gate, status: 'completed', smokePassed: true,
      businessGatePassed: false, businessGateResult: null,
      tasks: stage === 'INPUT_SYNC' ? [makeTask(stage, 'dft-expert', 0), makeTask(stage, 'schematic-expert', 1)]
        : [makeTask(stage, registry.stages[stage].owner, index + 1)] })),
    auxiliaryTasks: [makeTask('SMOKE_AUXILIARY', 'evolution-expert', 9)] };
  write(`${pipelinePrefix}/simple-orchestration.json`, progress);
  write(`${pipelinePrefix}/state.json`, { schemaVersion: 1, runId: pipelineRunId,
    purpose: 'smoke-training', status: 'completed',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE', stages: STAGES },
    outcome: { mode: 'SMOKE_ONLY', smokePassed: true, businessGatePassed: false } });
  const verifySmoke = async ({ snapshotRoot, candidateDigest, profileIds, stages }) => {
    assert.equal(fs.existsSync(path.join(snapshotRoot, `evidence/${pipelineRunId}/simple-orchestration.json`)), true);
    return { kind: 'ptc-smoke-evaluation', status: 'passed', candidateDigest,
      realBusinessGatesPassed: false, profileIds, stages };
  };
  const options = (releaseId = 'smoke-v1') => ({ workspaceRoot, releaseId, createdBy: 'test-publisher',
    profileRunIds, pipelineRunId,
    scriptPaths: ['plugins/dsh-ptc-control-plane/lib/smoke-execution.js'], verifySmoke });
  const root = 'publish';
  return { workspaceRoot, write, read, options, root, profileRunIds,
    pipelineRunId, pointer: () => read(`${root}/active-release.json`) };
}

test('publish/versions freezes eight profiles and smoke-only evidence; never moves business pointer', async t => {
  const f = fixture(t);
  const staged = await stageTrainingRelease(f.options());
  assert.equal(staged.manifest.realBusinessGatesPassed, false);
  assert.equal(staged.manifest.outputUse, 'diagnostic-only');
  assert.equal(fs.existsSync(path.join(f.workspaceRoot, f.root, 'active-release.json')), false);
  const pointer = activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  assert.equal(pointer.releaseId, 'smoke-v1');
  assert.equal(fs.existsSync(path.join(f.workspaceRoot, 'team/ptc/releases/active-release.json')), false);
  const release = loadTrainingRelease({ workspaceRoot: f.workspaceRoot });
  assert.equal(listTrainingReleases({ workspaceRoot: f.workspaceRoot }).releases[0].valid, true);
  assert.equal(release.directory, path.join(f.workspaceRoot, 'publish', 'versions', 'smoke-v1'));
  f.write('team/expert-profiles/strategy-expert/instructions.md', 'changed later\n');
  assert.equal(fs.readFileSync(path.join(release.snapshotRoot, 'profiles/strategy-expert/instructions.md'), 'utf8'),
    'strategy-expert:instructions.md\n');
});

test('built-in Captain verifier checks copied numeric child proof before activation', async t => {
  const f = fixture(t);
  const staged = await stageTrainingRelease({ ...f.options('verified-v1'), verifySmoke: verifySmokeCandidate });
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  assert.equal(loadTrainingRelease({ workspaceRoot: f.workspaceRoot }).manifest.releaseId, 'verified-v1');
  const profile = f.profileRunIds['strategy-expert'];
  const raw = `Training_Materials/runs/${profile}/evidence/profile-smoke-child.json`;
  f.write(raw, { stopReason: 'completed', structured: { answer: '3' } });
  await assert.rejects(stageTrainingRelease({ ...f.options('verified-v2'), verifySmoke: verifySmokeCandidate }),
    /profile smoke receipt invalid|single-agent smoke proof failed/);
});

test('rejects tampered staged/active bytes, stale verdict and incomplete arithmetic proof', async t => {
  const f = fixture(t);
  const stale = f.options();
  stale.verifySmoke = async () => ({ kind: 'ptc-smoke-evaluation', status: 'passed',
    candidateDigest: '0'.repeat(64), realBusinessGatesPassed: false,
    profileIds: Object.keys(f.profileRunIds), stages: STAGES });
  await assert.rejects(stageTrainingRelease(stale), /evaluation failed or stale/);
  const staged = await stageTrainingRelease(f.options());
  f.write(`${f.root}/.staging/${staged.stagingId}/profiles/strategy-expert/instructions.md`, 'tampered');
  assert.throws(() => activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId }), /mismatch/);
  const good = await stageTrainingRelease(f.options('smoke-v2'));
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: good.stagingId });
  f.write(`${f.root}/versions/smoke-v2/runtime/scripts/compile.py`, 'tampered');
  assert.throws(() => loadTrainingRelease({ workspaceRoot: f.workspaceRoot }), /mismatch/);
  const profile = f.profileRunIds['strategy-expert'];
  const receipt = `Training_Materials/runs/${profile}/evidence/profile-smoke.json`;
  f.write(receipt, { ...f.read(receipt), answer: '3' });
  await assert.rejects(stageTrainingRelease(f.options('smoke-v3')), /profile smoke receipt invalid/);
});

test('explicit releaseId pins old snapshot after new activation and rollback', async t => {
  const f = fixture(t);
  const first = await stageTrainingRelease(f.options());
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: first.stagingId });
  f.write('team/expert-profiles/strategy-expert/instructions.md', 'new\n');
  const second = await stageTrainingRelease(f.options('smoke-v2'));
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: second.stagingId });
  assert.equal(loadTrainingRelease({ workspaceRoot: f.workspaceRoot }).manifest.releaseId, 'smoke-v2');
  assert.equal(fs.readFileSync(path.join(loadTrainingRelease({ workspaceRoot: f.workspaceRoot, releaseId: 'smoke-v1' })
    .snapshotRoot, 'profiles/strategy-expert/instructions.md'), 'utf8'), 'strategy-expert:instructions.md\n');
  rollbackTrainingRelease({ workspaceRoot: f.workspaceRoot });
  assert.equal(loadTrainingRelease({ workspaceRoot: f.workspaceRoot }).manifest.releaseId, 'smoke-v1');
});

test('archived six-profile pointer permits replacement without executing the old format', async t => {
  const f = fixture(t);
  const old = await stageTrainingRelease(f.options());
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: old.stagingId });
  const name = 'publish/versions/smoke-v1/release-manifest.json';
  const manifest = f.read(name);
  manifest.profileIds = manifest.profileIds.filter(id => !['ptc-dft-expert', 'ptc-schematic-expert'].includes(id));
  manifest.dftRunId = 'old-dft-run';
  manifest.statisticRunId = 'old-statistic-run';
  f.write(name, manifest);
  assert.throws(() => loadTrainingRelease({ workspaceRoot: f.workspaceRoot }), /legacy smoke release cannot execute/);
  const next = await stageTrainingRelease(f.options('smoke-v2'));
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: next.stagingId });
  assert.equal(loadTrainingRelease({ workspaceRoot: f.workspaceRoot }).manifest.releaseId, 'smoke-v2');
  assert.equal(listTrainingReleases({ workspaceRoot: f.workspaceRoot }).releases.find(r => r.releaseId === 'smoke-v1').legacy, true);
  assert.throws(() => rollbackTrainingRelease({ workspaceRoot: f.workspaceRoot }), /training scope coverage invalid/);
});

test('manifest-only role remapping is refused despite unchanged file bundle digest', async t => {
  const f = fixture(t);
  const staged = await stageTrainingRelease(f.options());
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  const name = 'publish/versions/smoke-v1/release-manifest.json';
  const manifest = f.read(name);
  const strategy = manifest.roleProfiles['test-strategy-architect'];
  manifest.roleProfiles['test-strategy-architect'] = manifest.roleProfiles['test-method-expert'];
  manifest.roleProfiles['test-method-expert'] = strategy;
  f.write(name, manifest);
  assert.throws(() => loadTrainingRelease({ workspaceRoot: f.workspaceRoot }), /role\/stage binding changed/);
});

function dispatchers({ wrongAnswer = false, onArithmetic } = {}) {
  let sequence = 0;
  return {
    dispatchArithmetic: async request => {
      onArithmetic?.(request);
      sequence += 1;
      return { status: 'completed', executionKind: request.executionKind,
        runId: request.runId, dispatchId: request.dispatchId, releaseId: request.releaseId,
        childSessionId: `fresh-session-${sequence}`,
        result: { stopReason: 'completed', structured: { answer: wrongAnswer ? '3' : 3 } } };
    },
  };
}

test('published mode really dispatches from pinned snapshot and writes all records under publish/runs', async t => {
  const f = fixture(t);
  const first = await stageTrainingRelease(f.options());
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: first.stagingId });
  const second = await stageTrainingRelease(f.options('smoke-v2'));
  let switched = false;
  let dispatchCount = 0;
  const dispatch = dispatchers({ onArithmetic: request => {
    dispatchCount += 1;
    assert.equal(request.prompt, '1+2等于几，把答案写在JSON里');
    assert.equal(request.profileRoot.startsWith(path.join(f.workspaceRoot, 'publish', 'versions', 'smoke-v1')), true);
    if (!switched) {
      activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: second.stagingId });
      switched = true;
    }
  } });
  const result = await executePublishedSmoke({ workspaceRoot: f.workspaceRoot, runId: 'published-smoke-1',
    testItems: ['TM109'], ...dispatch });
  assert.equal(result.state.status, 'completed');
  assert.equal(result.state.businessGatePassed, false);
  assert.equal(result.state.releaseId, 'smoke-v1');
  assert.equal(result.state.stages.length, 7);
  assert.equal(dispatchCount, 9);
  assert.deepEqual(result.state.stages[0].tasks.map(task => task.answer), [3, 3]);
  assert.equal(result.state.auxiliaryTasks[0].answer, 3);
  assert.equal(result.outputRoot, path.join(f.workspaceRoot, 'publish/runs/published-smoke-1'));
  assert.equal(loadTrainingRelease({ workspaceRoot: f.workspaceRoot }).manifest.releaseId, 'smoke-v2');
  assert.equal(fs.existsSync(path.join(f.workspaceRoot, 'team/artifacts/published-smoke-1')), false);
  await assert.rejects(executePublishedSmoke({ workspaceRoot: f.workspaceRoot, runId: 'published-smoke-1',
    testItems: ['TM109'], ...dispatch }), /EEXIST/);
});

test('published smoke blocks numeric string from any role', async t => {
  const f = fixture(t);
  const first = await stageTrainingRelease(f.options());
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: first.stagingId });
  const wrong = await executePublishedSmoke({ workspaceRoot: f.workspaceRoot, runId: 'wrong-answer',
    testItems: ['TM109'], ...dispatchers({ wrongAnswer: true }) });
  assert.equal(wrong.state.status, 'blocked');
  assert.match(wrong.state.reason, /numeric answer check/);
});

test('DSH published adapter uses fresh real-child API for all eight profiles', async t => {
  const f = fixture(t);
  const staged = await stageTrainingRelease(f.options());
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  let created = 0; let started = 0; let disposed = 0;
  const ctx = {
    agentDefaultModel: { currentSelection: () => ({ provider: 'test-provider', model: 'test-model' }) },
    agents: { create: async () => { created += 1; return {
      agent: { whenIdle: async () => {} }, dispose: async () => { disposed += 1; },
    }; } },
    subagents: { start: async (mode, input) => {
      assert.equal(mode, 'spawn');
      assert.deepEqual(input.toolFilter, { allow: [] });
      assert.equal(input.prompt[0].text, '1+2等于几，把答案写在JSON里');
      started += 1;
      return { id: `new-child-${started}`, result: Promise.resolve({ stopReason: 'completed', structured: { answer: 3 } }) };
    } },
  };
  const adapters = createPublishedSmokeDispatcher(ctx, f.workspaceRoot);
  const replay = await executePublishedSmoke({ workspaceRoot: f.workspaceRoot, runId: 'adapter-replay',
    testItems: ['TM109'], ...adapters });
  assert.equal(replay.state.status, 'completed');
  assert.equal(replay.state.businessGatePassed, false);
  assert.equal(created, 9);
  assert.equal(started, 9);
  assert.equal(disposed, 9);
});

test('published stop signal blocks a live child without dispatching later stages', async t => {
  const f = fixture(t);
  const staged = await stageTrainingRelease(f.options());
  activateStagedTrainingRelease({ workspaceRoot: f.workspaceRoot, stagingId: staged.stagingId });
  const controller = new AbortController();
  let started = 0;
  const dispatchArithmetic = request => {
    started += 1;
    controller.abort(new Error('user stopped published smoke'));
    return new Promise((resolve, reject) => {
      if (request.signal.aborted) reject(request.signal.reason);
      else request.signal.addEventListener('abort', () => reject(request.signal.reason), { once: true });
    });
  };
  const result = await executePublishedSmoke({ workspaceRoot: f.workspaceRoot, runId: 'stopped-published',
    testItems: ['TM109'], dispatchArithmetic,
    signal: controller.signal });
  assert.equal(result.state.status, 'blocked');
  assert.match(result.state.reason, /stopped/);
  assert.equal(started, 1);
});

export { fixture };
