import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { sha256Bytes } from '../lib/release-integrity.js';
import { assessBusinessReleaseEligibility } from '../lib/business-release-eligibility.js';

const STAGES = ['INPUT_SYNC', 'STRATEGY', 'METHOD', 'RULE_REVIEW_METHOD',
  'IMPLEMENTATION', 'RULE_REVIEW_IMPLEMENTATION', 'COMPILE'];
const RUN_ID = 'training-business-fixture';
const KEY = 'a'.repeat(64);
const TM = ['TM109'];

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-business-preflight-'));
  const run = path.join(root, 'Training_Materials', 'runs', RUN_ID);
  const put = (relative, value) => {
    const file = path.join(run, relative);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, typeof value === 'string' ? value : JSON.stringify(value));
    return file;
  };
  const registry = { stateMachine: [...STAGES, 'COMPLETE'], stages: Object.fromEntries(STAGES.map(stage => [stage,
    { owner: stage === 'INPUT_SYNC' ? 'captain' : `${stage.toLowerCase().replaceAll('_', '-')}-expert`, gate: `scripts/${stage.toLowerCase()}.py` }])) };
  const context = { schemaVersion: 1, mode: 'training', runId: RUN_ID, releaseId: null, projectId: null,
    artifactRoot: path.relative(root, run) };
  const state = { runId: RUN_ID, purpose: 'business-training', status: 'completed',
    target: { kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE', stages: STAGES },
    outcome: { mode: 'PIPELINE' } };
  const materials = { schemaVersion: 1, kind: 'ptc-pipeline-materials', runId: RUN_ID,
    pipelineCacheKey: KEY, testItems: TM };
  put('run.json', context); put('state.json', state); put('pipeline-registry.json', registry);
  put('pipeline-material-manifest.json', materials);
  const stages = STAGES.map(stage => {
    const gate = registry.stages[stage].gate;
    const terminals = (stage === 'INPUT_SYNC' ? ['dft-expert', 'schematic-expert'] : [registry.stages[stage].owner])
      .map(role => ({ role, status: 'done', testItems: TM }));
    const gateResult = { status: 'passed', exitCode: 0, gate };
    if (stage !== 'COMPILE') {
      const receipt = { kind: 'training-stage-gate', runId: RUN_ID, stage, gate,
        action: 'gate', status: 'passed', exitCode: 0, pipelineCacheKey: KEY, testItems: TM };
      const receiptPath = put(`verification/stage-${stage.toLowerCase()}.json`, receipt);
      gateResult.receiptPath = receiptPath;
      gateResult.receiptSha256 = sha256Bytes(fs.readFileSync(receiptPath));
    } else {
      const artifacts = ['Debug', 'Release'].map(configuration => {
        const file = put(`compile/${configuration}/training.dll`, `${configuration} bytes`);
        return { path: file, configuration, size: fs.statSync(file).size, sha256: sha256Bytes(fs.readFileSync(file)) };
      });
      const reportPath = put('compile/build-report.json', { runId: RUN_ID, mode: 'training', stage: 'COMPILE',
        status: 'passed', sourceSha256: 'b'.repeat(64), projectSha256: 'c'.repeat(64),
        commands: [{ closed: true, exitCode: 0 }, { closed: true, exitCode: 0 }], artifacts });
      Object.assign(gateResult, { adapter: 'training-compile.js', reportPath,
        reportSha256: sha256Bytes(fs.readFileSync(reportPath)) });
    }
    return { stage, status: 'completed', terminals, gateResult };
  });
  const progress = { runId: RUN_ID, status: 'completed', testItems: TM, stages };
  put('pipeline-progress.json', progress);
  return { root, run, put, state, progress, materials };
}

test('synthetic all-green stage and compile files never substitute for independent business attestation', () => {
  const f = fixture();
  const result = assessBusinessReleaseEligibility(f.root, RUN_ID);
  assert.equal(result.eligible, false);
  assert.deepEqual(result.reasons, [
    'CANONICAL_PLAINTEXT_SOURCE_BINDING_UNVERIFIED',
    'REQUIRED_STAGE_OUTPUT_BINDING_UNVERIFIED',
    'TRUSTED_BUSINESS_EVALUATOR_ATTESTATION_UNAVAILABLE',
  ]);
  assert.ok(result.checks.every(item => item.passed));
});

test('framework rehearsal, statistic-only and partial or blocked run are denied', () => {
  for (const mutate of [
    f => { f.state.purpose = 'framework-rehearsal'; f.state.outcome = { mode: 'FRAMEWORK_REHEARSAL', realBusinessGatesPassed: false }; f.put('state.json', f.state); },
    f => { f.state.purpose = 'schematic-statistic-only'; f.state.outcome = { mode: 'STATISTIC_ONLY' }; f.put('state.json', f.state); },
    f => { f.state.target.toStage = 'METHOD'; f.state.target.stages = STAGES.slice(0, 3); f.put('state.json', f.state); },
    f => { f.state.status = 'blocked'; f.put('state.json', f.state); },
  ]) {
    const f = fixture(); mutate(f);
    const result = assessBusinessReleaseEligibility(f.root, RUN_ID);
    assert.equal(result.eligible, false);
    assert.ok(result.reasons.some(reason => reason === 'NOT_COMPLETED_BUSINESS_TRAINING'
      || reason === 'FULL_AUTHORITATIVE_STAGE_CHAIN_NOT_PROVEN'));
  }
});

test('a failed stage gate and tampered receipt are independently visible', () => {
  const f = fixture();
  f.progress.stages[2].gateResult.exitCode = 2;
  f.put('pipeline-progress.json', f.progress);
  assert.ok(assessBusinessReleaseEligibility(f.root, RUN_ID).reasons.includes('STAGE_METHOD_NOT_PROVEN'));
  f.progress.stages[2].gateResult.exitCode = 0;
  f.put('pipeline-progress.json', f.progress);
  fs.appendFileSync(f.progress.stages[1].gateResult.receiptPath, '\n');
  assert.ok(assessBusinessReleaseEligibility(f.root, RUN_ID).reasons.includes('STAGE_STRATEGY_RECEIPT_INVALID'));
});

test('tampered compile artifact and missing or unsafe run evidence are denied', () => {
  const f = fixture();
  fs.appendFileSync(f.progress.stages.at(-1).gateResult.reportPath, '\n');
  assert.ok(assessBusinessReleaseEligibility(f.root, RUN_ID).reasons.includes('COMPILE_REPORT_OR_ARTIFACT_INVALID'));
  fs.unlinkSync(path.join(f.run, 'pipeline-progress.json'));
  assert.ok(assessBusinessReleaseEligibility(f.root, RUN_ID).reasons.some(reason => reason.startsWith('PREFLIGHT_EVIDENCE_UNREADABLE')));
  assert.equal(assessBusinessReleaseEligibility(f.root, '../escape').eligible, false);
});
