import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';
import { assertSafeRunPath } from './run-context.js';
import { trainingAddressBook } from './training-paths.js';
import { createTrainingLifecycle } from './training-lifecycle.js';
import { resolveTrainingModelChoice } from './training-model.js';

const execFile = promisify(execFileCallback);
const DIGEST = /^[a-f0-9]{64}$/;
const PROFILE = /^[a-z][a-z0-9-]{1,63}$/;
const ARITHMETIC_PROFILES = new Set(['ate-implementer', 'compile-diagnostician', 'evolution-expert',
  'method-expert', 'ptc-dft-expert', 'ptc-schematic-expert', 'rule-reviewer', 'strategy-expert']);
const PROFILE_FILES = ['instructions.md', 'profile.yaml', 'output-contract.schema.json'];
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const relative = (root, file) => path.relative(root, file).split(path.sep).join('/');

function atomic(root, file, value) {
  assertSafeRunPath(root, file);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = assertSafeRunPath(root, `${file}.${crypto.randomUUID()}.tmp`);
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  try { fs.renameSync(temporary, file); } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}

function identity(root, runId) {
  const directory = assertSafeRunPath(root, trainingAddressBook(runId).runRoot);
  const context = read(assertSafeRunPath(root, path.join(directory, 'run.json')));
  const stateFile = assertSafeRunPath(root, path.join(directory, 'state.json'));
  const state = read(stateFile);
  const profileId = state.target?.profileId;
  if (context.mode !== 'training' || context.runId !== runId || context.releaseId !== null
      || context.projectId !== null || path.resolve(root, context.artifactRoot) !== directory
      || state.runId !== runId || state.purpose !== 'smoke-training'
      || state.target?.kind !== 'profile' || !PROFILE.test(profileId ?? '')) {
    throw new Error('not an isolated profile smoke-training identity');
  }
  if (!ARITHMETIC_PROFILES.has(profileId)) {
    throw new Error('profile is not one of the eight PTC arithmetic smoke experts');
  }
  const profileRoot = assertSafeRunPath(root, path.join(root, 'team', 'expert-profiles', profileId));
  if (!fs.statSync(profileRoot).isDirectory()) throw new Error('profile directory is missing');
  return { directory, context, stateFile, state, profileId, profileRoot };
}

// The source may be DLP-protected. Both sides are hashed by the approved
// Python plaintext-view command; Node never hashes canonical profile inputs.
const COPY_PROFILE = String.raw`import json, pathlib, subprocess, sys
source, target, command = map(pathlib.Path, sys.argv[1:])
def digest(file):
 result = subprocess.run([sys.executable, '-X', 'utf8', str(command), str(file), '--json'], capture_output=True, text=True, encoding='utf-8', timeout=10, check=True)
 report = json.loads(result.stdout)
 if report.get('view') != 'python-plaintext': raise RuntimeError('approved plaintext hash view missing')
 return report['sha256']
before = digest(source)
if target.exists():
 if digest(target) != before: raise RuntimeError('private profile snapshot differs')
else:
 target.parent.mkdir(parents=True, exist_ok=True)
 with source.open('rb') as src, target.open('xb') as dst:
  total = 0
  while block := src.read(65536):
   total += len(block)
   if total > 262144: raise RuntimeError('profile source exceeds snapshot limit')
   dst.write(block)
if before != digest(source) or before != digest(target): raise RuntimeError('profile changed while freezing')
print(json.dumps({'sha256': before, 'view': 'python-plaintext', 'bytes': target.stat().st_size}))`;

async function profileFile(root, source, target, signal) {
  const command = assertSafeRunPath(root, path.join(root, 'scripts/hash_ate_plaintext.py'));
  const { stdout } = await execFile('python', ['-X', 'utf8', '-c', COPY_PROFILE, source, target, command], {
    cwd: root, windowsHide: true, encoding: 'utf8', timeout: 30_000, maxBuffer: 256 * 1024, signal,
  });
  const report = JSON.parse(stdout);
  if (!DIGEST.test(report.sha256 ?? '') || report.view !== 'python-plaintext'
      || !Number.isSafeInteger(report.bytes) || report.bytes < 0 || report.bytes > 262144) {
    throw new Error('approved profile snapshot command returned invalid provenance');
  }
  return report;
}

async function freezeProfile(root, record, lifecycle) {
  const files = [];
  for (const name of PROFILE_FILES) {
    const source = assertSafeRunPath(root, path.join(record.profileRoot, name));
    if (!fs.existsSync(source)) {
      if (name === 'instructions.md') throw new Error('profile instructions are required');
      continue;
    }
    if (!fs.statSync(source).isFile()) throw new Error('profile source is not a regular file');
    const target = assertSafeRunPath(root, path.join(record.directory, 'profile', name));
    const report = await lifecycle.race(() => profileFile(root, source, target, lifecycle.signal), { label: `freeze ${name}` });
    files.push({ source: relative(root, source), path: relative(root, target), sha256: report.sha256,
      view: 'python-plaintext', bytes: report.bytes });
  }
  const file = assertSafeRunPath(root, path.join(record.directory, 'profile', 'snapshot.json'));
  const manifest = { schemaVersion: 1, kind: 'ptc-profile-smoke-snapshot', runId: record.state.runId,
    profileId: record.profileId, files, createdAt: new Date().toISOString() };
  atomic(root, file, manifest);
  return { file, manifest, sha256: sha(fs.readFileSync(file)) };
}

async function verifyProfile(root, record, snapshot, lifecycle) {
  if (sha(fs.readFileSync(assertSafeRunPath(root, snapshot.file))) !== snapshot.sha256) {
    throw new Error('profile snapshot manifest changed');
  }
  for (const entry of snapshot.manifest.files) {
    const report = await lifecycle.race(() => profileFile(root,
      assertSafeRunPath(root, path.join(root, entry.source)),
      assertSafeRunPath(root, path.join(root, entry.path)), lifecycle.signal), { label: 'verify profile' });
    if (report.sha256 !== entry.sha256) throw new Error('profile changed during smoke training');
  }
}

function terminal(root, record, snapshot, child, selection, result, error) {
  const now = new Date().toISOString();
  const passed = !error && result?.stopReason === 'completed'
    && result?.structured?.answer === 3 && typeof result.structured.answer === 'number'
    && typeof child?.id === 'string' && child.id.length > 0;
  let responseSha256 = null; let responsePath = null;
  if (result) {
    const responseFile = assertSafeRunPath(root, path.join(record.directory, 'evidence', 'profile-smoke-child.json'));
    fs.mkdirSync(path.dirname(responseFile), { recursive: true });
    fs.writeFileSync(responseFile, `${JSON.stringify(result, null, 2)}\n`, { flag: 'wx' });
    responseSha256 = sha(fs.readFileSync(responseFile));
    responsePath = relative(root, responseFile);
  }
  const evidenceFile = assertSafeRunPath(root, path.join(record.directory, 'evidence', 'profile-smoke.json'));
  const evidence = { schemaVersion: 1, kind: 'ptc-profile-smoke', runId: record.state.runId,
    profileId: record.profileId, status: passed ? 'completed' : 'blocked', mode: 'SMOKE_ONLY',
    smokePassed: passed,
    businessGatePassed: false, profileInstructionsValidated: false, modelDispatched: Boolean(child?.id),
    profileSnapshotPath: snapshot ? relative(root, snapshot.file) : null,
    profileSnapshotSha256: snapshot?.sha256 ?? null,
    answer: passed ? 3 : null, responsePath, responseSha256,
    childResultSha256: responseSha256,
    childSessionId: child?.id ?? null, modelChoice: selection?.choice ?? null,
    modelProvider: selection?.provider ?? null, modelName: selection?.model ?? null,
    stopReason: result?.stopReason ?? error?.stopReason ?? 'error',
    reason: passed ? null : String(error?.message ?? 'smoke child did not return numeric JSON answer 3'),
    finishedAt: now };
  atomic(root, evidenceFile, evidence);
  const evidenceSha256 = sha(fs.readFileSync(evidenceFile));
  const state = { ...record.state, status: evidence.status, updatedAt: now, finishedAt: now,
    outcome: { mode: 'SMOKE_ONLY', smokePassed: passed, businessGatePassed: false, profileInstructionsValidated: false,
      modelDispatched: evidence.modelDispatched,
      profileSnapshotSha256: evidence.profileSnapshotSha256,
      responseSha256, childResultSha256: responseSha256, reason: evidence.reason,
      evidence: relative(root, evidenceFile), evidenceSha256 } };
  atomic(root, record.stateFile, state);
  return { state, evidence, evidenceFile, evidenceSha256 };
}

/** Real DSH child dispatch for any of the eight PTC profiles.
 * It verifies only identity, lifecycle and numeric JSON answer 3, never a
 * business gate. The smoke command reads no DFT or schematic business input.
 */
export function createProfileSmokeManager(ctx, workspaceRoot, options = {}) {
  const root = path.resolve(workspaceRoot);
  const active = new Map();
  return {
    start(input) {
      const record = identity(root, input?.runId);
      if (record.state.status !== 'created' || active.has(input.runId)) throw new Error('profile smoke run is not startable');
      const lock = assertSafeRunPath(root, path.join(record.directory, 'profile-smoke.lock'));
      fs.writeFileSync(lock, `${process.pid}\n`, { flag: 'wx' });
      const lifecycle = createTrainingLifecycle({ timeoutMs: options.timeoutMs ?? 300_000,
        onEvent: (event, state) => atomic(root, path.join(record.directory, 'evidence', 'profile-smoke-lifecycle.json'),
          { schemaVersion: 1, runId: input.runId, event, ...state }) });
      record.lifecycle = lifecycle;
      active.set(input.runId, record);
      const startedAt = new Date().toISOString();
      record.state = { ...record.state, status: 'running', startedAt, updatedAt: startedAt,
        modelChoice: input.modelChoice ?? 'default' };
      atomic(root, record.stateFile, record.state);
      const completion = (async () => {
        let snapshot; let child; let selection; let result; let error;
        try {
          snapshot = await (options.freezeProfile ?? freezeProfile)(root, record, lifecycle);
          selection = resolveTrainingModelChoice(input.modelChoice, ctx.agentDefaultModel.currentSelection());
          if (!ctx?.agents?.create || !ctx?.agentPresets?.mount || !ctx?.subagents?.start) {
            throw new Error('DSH child services are unavailable');
          }
          const agentOptions = { provider: selection.provider, model: selection.model, maxTokens: 256 };
          const parent = await lifecycle.race(() => ctx.agents.create({
            sessionId: `session-profile-smoke-${input.runId}`,
            meta: { cwd: root, agentPreset: 'ate-ptc' }, agentOptions,
            setup: async agentCtx => { await ctx.agentPresets.mount(agentCtx, 'ate-ptc'); },
          }), { label: 'parent.create', disposeLate: handle => handle.dispose?.() });
          await lifecycle.race(() => parent.agent.whenIdle(), { label: 'parent.idle' });
          child = await lifecycle.race(() => ctx.subagents.start('spawn', {
            label: `PTC smoke ${record.profileId} ${input.runId}`, parent: parent.agent,
            signal: lifecycle.signal, agentOptions, maxDepth: 1, toolFilter: { allow: [] },
            persona: `PTC training dispatch smoke child for ${record.profileId}. This is not business execution. Do not use tools, files, project facts, private inputs or expert instructions.`,
            prompt: [{ type: 'text', text: '1+2等于几，把答案写在JSON里' }],
            outputSchema: { type: 'object', properties: {
              answer: { type: 'number' },
            }, required: ['answer'], additionalProperties: false },
          }), { label: 'child.start', disposeLate: handle => {
            Promise.resolve(handle.result).catch(() => {}); return handle.dispose?.();
          } });
          if (typeof child.id !== 'string' || !child.id) throw new Error('DSH returned no child identity');
          result = await lifecycle.race(child.result, { label: 'child.result', trackSettlement: true });
          await (options.verifyProfile ?? verifyProfile)(root, record, snapshot, lifecycle);
        } catch (caught) { error = caught; }
        try { return terminal(root, record, snapshot, child, selection, result, error); }
        finally {
          active.delete(input.runId);
          lifecycle.close();
          try { fs.unlinkSync(lock); } catch {}
        }
      })();
      record.completion = completion;
      options.onBackground?.(completion);
      return { runId: input.runId, status: 'running', mode: 'SMOKE_ONLY', completion };
    },
    stop(runId, reason = 'user stopped profile smoke training') {
      trainingAddressBook(runId);
      const record = active.get(runId);
      return record ? record.lifecycle.cancel(reason) : false;
    },
    shutdown() {
      for (const record of active.values()) record.lifecycle.cancel('PTC smoke manager stopped');
    },
  };
}
