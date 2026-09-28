import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { Readable } from 'node:stream';
import test from 'node:test';
import { apply, createStateHandler, createTrainingExecutionHandler, createTrainingRunHandler, createTrainingStopHandler, createProfileSmokeHandler, createTrainingDraftHandler, createTrainingIssueHandler, createTrainingCaseHandler, createFrameworkReleasePublishHandler, createFrameworkPublishedExecuteHandler, createFrameworkPublishedControlHandler, createPtcSessionWorkspaceHandler, createTrainingSmokeFreezeHandler, createTrainingSmokeActivateHandler, createWorkflowTemplateHandler, createWorkflowTemplateReleaseHandler } from '../lib/index.js';
import { readTrainingDraft } from '../lib/training-drafts.js';

test('plugin registers exact same-origin state and training routes', () => {
  const routes = [];
  const effects = [];
  const guards = [];
  const events = [];
  const ctx = {
    inject(names, callback) {
      assert.deepEqual(names, ['webServer', 'agents', 'agentDefaultModel', 'agentPresets', 'subagents', 'tools']);
      callback({
        webServer: { register(route) { routes.push(route); return () => {}; } },
        tools: { guard(fn) { guards.push(fn); return () => {}; } },
        on(name, fn) { events.push({ name, fn }); return () => {}; },
        effect(factory) { effects.push(factory); factory(); },
      });
    },
    logger: { info() {} },
  };
  apply(ctx, { workspaceRoot: fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-route-registration-')) });
  assert.equal(effects.length, 1);
  assert.equal(guards.length, 1);
  assert.equal(events[0].name, 'tools/pre-execute');
  assert.equal(routes.length, 41);
  assert.equal(routes[0].kind, 'exact');
  assert.equal(routes[0].path, '/api/ptc-control/state');
  assert.equal(typeof routes[0].handler, 'function');
  assert.equal(routes[1].kind, 'exact');
  assert.equal(routes[1].path, '/api/ptc-control/training-runs');
  assert.equal(typeof routes[1].handler, 'function');
  assert.equal(routes[2].kind, 'exact');
  assert.equal(routes[2].path, '/api/ptc-control/training-runs/execute');
  assert.equal(typeof routes[2].handler, 'function');
  assert.deepEqual(routes.slice(3).map((route) => route.path), [
    '/api/ptc-control/business/training-runs/execute', '/api/ptc-control/training-runs/stop',
    '/api/ptc-control/profile-smoke/execute',
    '/api/ptc-control/profile-smoke/stop',
    '/api/ptc-control/simple-orchestration/execute', '/api/ptc-control/simple-orchestration/control',
    '/api/ptc-control/training-release/publish',
    '/api/ptc-control/training-release/freeze', '/api/ptc-control/training-release/activate',
    '/api/ptc-control/training-release/execute', '/api/ptc-control/training-release/control',
    '/api/ptc-control/training-drafts/read', '/api/ptc-control/training-drafts/save',
    '/api/ptc-control/session-workspace',
    '/api/ptc-control/workflow-templates/read', '/api/ptc-control/workflow-templates/save',
    '/api/ptc-control/workflow-templates/freeze', '/api/ptc-control/workflow-templates/execute',
    '/api/ptc-control/workflow-templates/control',
    '/api/ptc-control/workflow-template-releases/stage',
    '/api/ptc-control/workflow-template-releases/activate',
    '/api/ptc-control/workflow-template-releases/read',
    '/api/ptc-control/workflow-template-releases/execute',
    '/api/ptc-control/workflow-template-releases/control',
    '/api/ptc-control/training-issues/create', '/api/ptc-control/training-issues/list',
    '/api/ptc-control/training-cases/create', '/api/ptc-control/training-cases/list',
    '/api/ptc-control/training-pipelines/execute', '/api/ptc-control/training-pipelines/control',
    '/api/ptc-control/business/training-pipelines/execute', '/api/ptc-control/business/training-pipelines/control',
    '/api/ptc-control/framework-rehearsals/execute', '/api/ptc-control/framework-rehearsals/control',
    '/api/ptc-control/framework-releases/publish',
    '/api/ptc-control/framework-rehearsals/recover',
    '/api/ptc-control/framework-releases/execute',
    '/api/ptc-control/framework-releases/control',
  ]);
});

function responseRecorder() {
  const writes = [];
  return {
    writes,
    response: {
      writeHead(status, headers) { writes.push({ status, headers }); },
      end(body) { writes.push({ body }); },
    },
  };
}

test('workflow template HTTP boundary rejects caller release and choreography overrides', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-template-route-'));
  try {
    const runner = { start() { throw new Error('must not dispatch'); }, control() { throw new Error('must not control'); } };
    for (const [handler, body] of [
      [createWorkflowTemplateHandler(root, runner, 'execute'),
        { templateId: 'ate-ptc', versionSha256: 'a'.repeat(64), releaseId: 'foreign' }],
      [createWorkflowTemplateReleaseHandler(root, runner, 'execute'), { releaseId: 'foreign' }],
    ]) {
      const request = Readable.from([JSON.stringify(body)]);
      request.method = 'POST'; request.headers = { 'content-type': 'application/json' };
      const result = responseRecorder();
      await handler(request, result.response);
      assert.equal(result.writes[0].status, 400);
      assert.match(result.writes[1].body, /unsupported or missing fields/);
    }
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('training route creates only a training run from valid JSON', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-route-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  const request = Readable.from([JSON.stringify({
    runId: 'training-route-001',
    target: { kind: 'profile', profileId: 'ptc-dft-expert' },
  })]);
  request.method = 'POST';
  request.headers = { 'content-type': 'application/json; charset=utf-8' };
  const { writes, response } = responseRecorder();
  await createTrainingRunHandler(root)(request, response);
  assert.equal(writes[0].status, 201);
  const body = JSON.parse(writes[1].body);
  assert.equal(body.mode, 'training');
  assert.equal(body.artifactRoot, path.join('Training_Materials', 'runs', 'training-route-001'));
  assert.equal(fs.existsSync(path.join(root, body.artifactRoot, 'run.json')), true);
});

test('training route rejects non-JSON and oversized bodies', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-route-invalid-'));
  for (const [headers, body, expected] of [
    [{ 'content-type': 'text/plain' }, '{}', 415],
    [{ 'content-type': 'application/json' }, 'x'.repeat(16 * 1024 + 1), 413],
  ]) {
    const request = Readable.from([body]);
    request.method = 'POST';
    request.headers = headers;
    const record = responseRecorder();
    await createTrainingRunHandler(root)(request, record.response);
    assert.equal(record.writes[0].status, expected);
  }
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/runs')), false);
});

test('session workspace endpoint accepts only server-derived PTC workspace identities', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-session-route-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  for (const [body, expectedStatus] of [[{ mode: 'agent', profileId: 'ptc-dft-expert' }, 200],
    [{ mode: 'publish', path: 'C:/outside' }, 400]]) {
    const request = Readable.from([JSON.stringify(body)]);
    request.method = 'POST'; request.headers = { 'content-type': 'application/json' };
    const record = responseRecorder();
    await createPtcSessionWorkspaceHandler(root)(request, record.response);
    assert.equal(record.writes[0].status, expectedStatus);
    if (expectedStatus === 200) assert.equal(JSON.parse(record.writes[1].body).path,
      path.join(root, 'team/expert-profiles/ptc-dft-expert'));
  }
});

test('freeze and activate routes reject extra caller-controlled release fields', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-freeze-route-'));
  for (const [handler, body] of [
    [createTrainingSmokeFreezeHandler(root), { profileRunIds: {}, pipelineRunId: 'bad', releaseId: 'caller' }],
    [createTrainingSmokeActivateHandler(root), { stagingId: 'bad', releaseId: 'caller' }],
  ]) {
    const request = Readable.from([JSON.stringify(body)]);
    request.method = 'POST'; request.headers = { 'content-type': 'application/json' };
    const record = responseRecorder();
    await handler(request, record.response);
    assert.equal(record.writes[0].status, 400);
  }
});

test('training issue routes bind a terminal local run and list only verified proposals', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-training-issue-route-'));
  fs.mkdirSync(path.join(root, 'team/expert-profiles/ptc-dft-expert'), { recursive: true });
  const runId = 'training-issue-route';
  const created = Readable.from([JSON.stringify({ runId, target: { kind: 'profile', profileId: 'ptc-dft-expert' } })]);
  created.method = 'POST'; created.headers = { 'content-type': 'application/json' };
  await createTrainingRunHandler(root)(created, responseRecorder().response);
  const stateFile = path.join(root, 'Training_Materials/runs', runId, 'state.json');
  const evidenceRelative = `Training_Materials/runs/${runId}/evidence/dft-preflight.json`;
  const evidenceFile = path.join(root, evidenceRelative);
  fs.mkdirSync(path.dirname(evidenceFile), { recursive: true });
  fs.writeFileSync(evidenceFile, '{"status":"blocked"}\n');
  fs.writeFileSync(stateFile, JSON.stringify({ ...JSON.parse(fs.readFileSync(stateFile, 'utf8')),
    status: 'blocked', outcome: { evidence: evidenceRelative } }));
  const issueRequest = Readable.from([JSON.stringify({ runId, profileId: 'ptc-dft-expert',
    title: 'DFT 输出层级', description: 'TM109 字段层级不符合契约' })]);
  issueRequest.method = 'POST'; issueRequest.headers = { 'content-type': 'application/json' };
  const createRecord = responseRecorder();
  await createTrainingIssueHandler(root, 'create')(issueRequest, createRecord.response);
  assert.equal(createRecord.writes[0].status, 201);
  const issue = JSON.parse(createRecord.writes[1].body).issue;
  assert.equal(issue.publicationClaim, false);
  const listRequest = Readable.from(['{}']);
  listRequest.method = 'POST'; listRequest.headers = { 'content-type': 'application/json' };
  const listRecord = responseRecorder();
  await createTrainingIssueHandler(root, 'list')(listRequest, listRecord.response);
  assert.equal(listRecord.writes[0].status, 200);
  assert.equal(JSON.parse(listRecord.writes[1].body).issues[0].issueId, issue.issueId);
  const caseRequest = Readable.from([JSON.stringify({ issueId: issue.issueId,
    expectedBehavior: '重新生成符合 v5 层级的 DFT 产物' })]);
  caseRequest.method = 'POST'; caseRequest.headers = { 'content-type': 'application/json' };
  const caseRecord = responseRecorder();
  await createTrainingCaseHandler(root, 'create')(caseRequest, caseRecord.response);
  assert.equal(caseRecord.writes[0].status, 201);
  const proposal = JSON.parse(caseRecord.writes[1].body).proposal;
  assert.equal(proposal.publicationClaim, false);
  assert.equal(proposal.regressionSetClaim, false);
  const caseListRequest = Readable.from(['{}']);
  caseListRequest.method = 'POST'; caseListRequest.headers = { 'content-type': 'application/json' };
  const caseListRecord = responseRecorder();
  await createTrainingCaseHandler(root, 'list')(caseListRequest, caseListRecord.response);
  assert.equal(caseListRecord.writes[0].status, 200);
  assert.equal(JSON.parse(caseListRecord.writes[1].body).proposals[0].caseId, proposal.caseId);
});

test('training execution route returns the terminal preflight state', async () => {
  const request = Readable.from([JSON.stringify({ runId: 'training-route-001', testItems: ['TM109'] })]);
  request.method = 'POST';
  request.headers = { 'content-type': 'application/json' };
  const { writes, response } = responseRecorder();
  await createTrainingExecutionHandler('workspace', {
    executeTrainingRun: async (_root, input) => ({
      context: { runId: input.runId },
      state: { status: 'completed', outcome: { mode: 'UNCHANGED', modelDispatched: false } },
    }),
  })(request, response);
  assert.equal(writes[0].status, 200);
  assert.deepEqual(JSON.parse(writes[1].body), {
    runId: 'training-route-001',
    status: 'completed',
    outcome: { mode: 'UNCHANGED', modelDispatched: false },
  });
});

test('workspaceRoot is mandatory', () => {
  assert.throws(() => apply({}, {}), /workspaceRoot is required/);
});

test('published framework HTTP boundary rejects choreography and release overrides before filesystem access', async () => {
  for (const input of [{ releaseId: 'other' }, { testItems: ['TM109'] }, { stages: ['COMPILE'] }, { executor: 'model' }]) {
    const request = Readable.from([JSON.stringify(input)]);
    request.method = 'POST'; request.headers = { 'content-type': 'application/json' };
    const record = responseRecorder();
    await createFrameworkPublishedExecuteHandler('unused-root', new Map())(request, record.response);
    assert.equal(record.writes[0].status, 409);
    assert.match(record.writes[1].body, /override/);
  }
  const request = Readable.from([JSON.stringify({ runId: 'framework-run-1', action: 'edit' })]);
  request.method = 'POST'; request.headers = { 'content-type': 'application/json' };
  const record = responseRecorder();
  await createFrameworkPublishedControlHandler(new Map())(request, record.response);
  assert.equal(record.writes[0].status, 409);
});

test('stop route distinguishes a cancellation request from confirmed termination', async () => {
  for (const active of [true, false]) {
    const request = Readable.from([JSON.stringify({ runId: 'training-stop' })]);
    request.method = 'POST'; request.headers = { 'content-type': 'application/json' };
    const { writes, response } = responseRecorder();
    await createTrainingStopHandler({ stop(runId) { assert.equal(runId, 'training-stop'); return active; } })(request, response);
    assert.equal(writes[0].status, active ? 202 : 409);
    if (active) assert.equal(JSON.parse(writes[1].body).terminationConfirmed, false);
  }
});

test('state handler rejects mutation methods before reading state', async () => {
  const writes = [];
  const response = {
    writeHead(status, headers) { writes.push({ status, headers }); },
    end(body) { writes.push({ body }); },
  };
  await createStateHandler(process.cwd())({ method: 'POST' }, response);
  assert.equal(writes[0].status, 405);
  assert.match(writes[1].body, /method_not_allowed/);
});

function draftFixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-draft-http-'));
  const profileId = 'ptc-dft-expert';
  const directory = path.join(root, 'team/expert-profiles', profileId);
  fs.mkdirSync(path.join(directory, 'versions/v6'), { recursive: true });
  fs.writeFileSync(path.join(directory, 'instructions.md'), 'Original draft\r\n');
  fs.writeFileSync(path.join(directory, 'status.json'), '{"publishedVersion":"v6"}');
  fs.writeFileSync(path.join(directory, 'versions/v6/instructions.md'), 'Published frozen copy');
  const draft = readTrainingDraft(root, { profileId, file: 'instructions.md' });
  return { root, directory, draft, input: { mode: 'training', profileId, file: 'instructions.md', expectedSha256: draft.sha256, content: 'Updated draft\n' } };
}

async function draftRequest(root, action, input, options = {}) {
  const request = Readable.from([options.rawBody ?? JSON.stringify(input)]);
  request.method = options.method ?? 'POST';
  request.headers = { 'content-type': options.contentType ?? 'application/json; charset=utf-8' };
  const record = responseRecorder();
  await createTrainingDraftHandler(root, action)(request, record.response);
  return { status: record.writes[0].status, headers: record.writes[0].headers, body: JSON.parse(record.writes[1].body) };
}

test('draft HTTP read and save return exact content, digest and history without changing published bytes', async () => {
  const { root, directory, draft, input } = draftFixture();
  const read = await draftRequest(root, 'read', { profileId: input.profileId, file: input.file });
  assert.equal(read.status, 200);
  assert.deepEqual(read.body, draft);
  assert.equal(read.headers['Cache-Control'], 'no-store');
  assert.match(read.headers['Content-Type'], /^application\/json/);
  const saved = await draftRequest(root, 'save', input);
  assert.equal(saved.status, 200);
  assert.equal(saved.body.changed, true);
  assert.equal(saved.body.previousSha256, draft.sha256);
  assert.match(saved.body.sha256, /^[a-f0-9]{64}$/);
  assert.equal(readTrainingDraft(root, input).sha256, saved.body.sha256);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/draft-history', saved.body.historyId, 'before.bin')), true);
  assert.equal(fs.readFileSync(path.join(directory, 'status.json'), 'utf8'), '{"publishedVersion":"v6"}');
  assert.equal(fs.readFileSync(path.join(directory, 'versions/v6/instructions.md'), 'utf8'), 'Published frozen copy');
});

test('draft HTTP save rejects delivery mode and missing explicit training mode', async () => {
  const { root, draft, input } = draftFixture();
  for (const mode of ['delivery', 'published', undefined]) {
    const result = await draftRequest(root, 'save', { ...input, mode });
    assert.equal(result.status, 400);
    assert.equal(result.body.error, 'DRAFT_MODE_REQUIRED');
  }
  assert.equal(readTrainingDraft(root, input).sha256, draft.sha256);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/draft-history')), false);
});

test('draft HTTP stale expectedSha and profile lock return 409 without overwriting', async () => {
  const { root, directory, input } = draftFixture();
  const saved = await draftRequest(root, 'save', input);
  const stale = await draftRequest(root, 'save', { ...input, content: 'Stale overwrite' });
  assert.equal(stale.status, 409);
  assert.equal(stale.body.error, 'DRAFT_CONFLICT');
  assert.equal(readTrainingDraft(root, input).sha256, saved.body.sha256);
  fs.writeFileSync(path.join(directory, '.training-draft.lock'), 'other editor');
  const busy = await draftRequest(root, 'save', { ...input, expectedSha256: saved.body.sha256 });
  assert.equal(busy.status, 409);
  assert.equal(busy.body.error, 'DRAFT_BUSY');
});

test('draft HTTP limits request bytes and decoded content bytes before mutation', async () => {
  const { root, draft, input } = draftFixture();
  const oversizedBody = await draftRequest(root, 'save', input, { rawBody: 'x'.repeat(2 * 1024 * 1024 + 1) });
  assert.equal(oversizedBody.status, 413);
  assert.match(oversizedBody.body.detail, /request_body_too_large/);
  const oversizedContent = await draftRequest(root, 'save', { ...input, content: 'x'.repeat(256 * 1024 + 1) });
  assert.equal(oversizedContent.status, 400);
  assert.equal(oversizedContent.body.error, 'DRAFT_TOO_LARGE');
  assert.equal(readTrainingDraft(root, input).sha256, draft.sha256);
});

test('draft HTTP cannot read versions, status files or paths outside a profile', async () => {
  const { root, input } = draftFixture();
  for (const file of ['versions/v6/instructions.md', 'status.json', '../instructions.md']) {
    const result = await draftRequest(root, 'read', { ...input, file });
    assert.equal(result.status, 400);
    assert.equal(result.body.error, 'DRAFT_INVALID_FILE');
    assert.equal(result.body.content, undefined);
  }
  const traversal = await draftRequest(root, 'read', { ...input, profileId: '../ptc-dft-expert' });
  assert.equal(traversal.status, 400);
  assert.equal(traversal.body.error, 'DRAFT_INVALID_PROFILE');
});

test('draft HTTP rejects unsupported methods, non-JSON, malformed JSON and null payloads', async () => {
  const { root, input } = draftFixture();
  for (const action of ['read', 'save']) {
    assert.equal((await draftRequest(root, action, input, { method: 'GET' })).status, 405);
    assert.equal((await draftRequest(root, action, input, { contentType: 'text/plain' })).status, 415);
    assert.equal((await draftRequest(root, action, input, { rawBody: '{' })).status, 400);
    assert.equal((await draftRequest(root, action, null)).status, 400);
  }
});
