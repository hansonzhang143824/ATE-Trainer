import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const OUTPUTS = Object.freeze([
  ['dft-conditions.yaml', 'conditions'],
  ['dft-meta.json', 'meta'],
  ['dft-semantic-review.json', 'semantic-review'],
]);
const TM_ID = /^TM[0-9]+$/;
const DIGEST = /^[a-f0-9]{64}$/;

const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const relPath = value => value.split(path.sep).join('/');
function safeResolve(root, relative, label) {
  const base = path.resolve(root);
  const target = path.resolve(base, relative);
  if (target !== base && !target.startsWith(`${base}${path.sep}`)) throw new Error(`${label} escapes workspace`);
  return target;
}
function parseJson(file, label) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '')); }
  catch (error) { throw new Error(`${label} is not valid JSON: ${error.message}`); }
}
function normalizeItems(testItems) {
  const items = testItems === undefined || testItems === null ? ['TM109'] : (Array.isArray(testItems) ? testItems : [testItems]);
  const unique = [...new Set(items.filter(item => typeof item === 'string'))];
  if (!unique.length || unique.some(item => !TM_ID.test(item))) throw new Error('BUSINESS_ONLY requires valid TM test items');
  return unique;
}
function outputRootFor(root, runId, outputRoot) {
  if (typeof runId !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId)) throw new Error('invalid business run id');
  const runRoot = safeResolve(root, `Training_Materials/runs/${runId}`, 'run root');
  const output = safeResolve(root, outputRoot ?? `Training_Materials/runs/${runId}/input-sync/dft`, 'output root');
  if (output !== runRoot && !output.startsWith(`${runRoot}${path.sep}`)) throw new Error('business output root must stay inside the run');
  return { runRoot, output };
}
function validateOutputSet({ root, runId, testItems, outputRoot, sourceInputSha256, profileId, profileRevision }) {
  const { runRoot, output } = outputRootFor(root, runId, outputRoot);
  if (sourceInputSha256 !== undefined && sourceInputSha256 !== null && !DIGEST.test(sourceInputSha256)) throw new Error('source input SHA-256 is invalid');
  const outputs = [];
  for (const tm of normalizeItems(testItems)) {
    const tmRoot = safeResolve(root, path.join(relPath(path.relative(root, output)), tm), `${tm} output`);
    for (const [name, role] of OUTPUTS) {
      const file = safeResolve(root, path.join(relPath(path.relative(root, tmRoot)), name), `${tm}/${name}`);
      if (!fs.existsSync(file) || !fs.statSync(file).isFile()) throw new Error(`missing required output: ${tm}/${name}`);
      const bytes = fs.readFileSync(file);
      const digest = sha256(bytes);
      outputs.push({ tm, role, path: relPath(path.relative(root, file)), bytes: bytes.length, sha256: digest,
        status: 'validated', agentId: profileId ?? null, agentRevision: profileRevision ?? null });
      if (name === 'dft-meta.json') {
        const meta = parseJson(file, `${tm}/dft-meta.json`);
        if (meta.tm !== tm || !['ok', 'PASS', 'passed'].includes(meta.parseStatus)) throw new Error(`${tm}/dft-meta.json parseStatus is not PASS`);
        if (sourceInputSha256 && meta.sourceSha256 !== sourceInputSha256) throw new Error(`${tm}/dft-meta.json source SHA-256 mismatch`);
      }
      if (name === 'dft-conditions.yaml') {
        const text = bytes.toString('utf8');
        if (!text.includes(`tm: ${tm}`)) throw new Error(`${tm}/dft-conditions.yaml is not bound to ${tm}`);
        if (sourceInputSha256 && !text.includes(`sourceSha256: ${sourceInputSha256}`)) throw new Error(`${tm}/dft-conditions.yaml source SHA-256 mismatch`);
      }
    }
    const reviewFile = path.join(tmRoot, 'dft-semantic-review.json');
    const review = parseJson(reviewFile, `${tm}/dft-semantic-review.json`);
    if (review.tm !== tm || review.verdict !== 'PASS') throw new Error(`${tm}/semantic-review.json did not PASS`);
    if (sourceInputSha256 && review.sourceSha256 !== sourceInputSha256) throw new Error(`${tm}/semantic-review.json source SHA-256 mismatch`);
    const byName = Object.fromEntries(outputs.filter(item => item.tm === tm).map(item => [path.posix.basename(item.path), item.sha256]));
    for (const name of ['dft-meta.json', 'dft-conditions.yaml']) if (review.artifactHashes?.[name] !== byName[name]) throw new Error(`${tm}/semantic-review.json hash mismatch for ${name}`);
  }
  return { runRoot, outputs };
}

export function createBusinessOutputHashRecord({ workspaceRoot, runId, testItems, outputRoot, sourceInputSha256, profileId, profileRevision }) {
  const root = path.resolve(workspaceRoot);
  const validated = validateOutputSet({ root, runId, testItems, outputRoot, sourceInputSha256, profileId, profileRevision });
  const evidenceFile = safeResolve(root, path.join(relPath(path.relative(root, validated.runRoot)), 'evidence', 'tm109-output-hashes.json'), 'business evidence');
  fs.mkdirSync(path.dirname(evidenceFile), { recursive: true });
  if (fs.existsSync(evidenceFile)) {
    const existing = verifyBusinessOutputHashRecord(root, evidenceFile);
    return { record: existing.record, evidenceFile, evidencePath: relPath(path.relative(root, evidenceFile)), evidenceSha256: existing.evidenceSha256 };
  }
  const record = {
    schemaVersion: 1,
    mode: 'BUSINESS_ONLY',
    businessGatePassed: true,
    runId,
    testItems: normalizeItems(testItems),
    sourceInputSha256: sourceInputSha256 ?? null,
    profileId: profileId ?? null,
    profileRevision: profileRevision ?? null,
    outputs: validated.outputs,
    createdAt: new Date().toISOString(),
  };
  const bytes = Buffer.from(`${JSON.stringify(record, null, 2)}\n`, 'utf8');
  fs.writeFileSync(evidenceFile, bytes, { flag: 'wx' });
  return { record, evidenceFile, evidencePath: relPath(path.relative(root, evidenceFile)), evidenceSha256: sha256(bytes) };
}

export function verifyBusinessOutputHashRecord(workspaceRoot, evidenceFile) {
  const root = path.resolve(workspaceRoot);
  const absolute = safeResolve(root, evidenceFile, 'business evidence');
  const bytes = fs.readFileSync(absolute);
  const record = parseJson(absolute, 'business evidence');
  if (record.mode !== 'BUSINESS_ONLY' || record.businessGatePassed !== true) throw new Error('business output evidence is not a passing BUSINESS_ONLY record');
  if (!Array.isArray(record.outputs) || !record.outputs.length) throw new Error('business output evidence has no outputs');
  for (const output of record.outputs) {
    if (!DIGEST.test(output.sha256) || output.status !== 'validated') throw new Error('business output evidence contains an invalid output row');
    const file = safeResolve(root, output.path, 'business output');
    const runRoot = safeResolve(root, `Training_Materials/runs/${record.runId}`, 'run root');
    if (!file.startsWith(`${runRoot}${path.sep}`)) throw new Error('business output escapes run root');
    const current = sha256(fs.readFileSync(file));
    if (current !== output.sha256) throw new Error(`output changed after hash record: ${output.path}`);
  }
  return { record, evidenceSha256: sha256(bytes), evidenceFile: absolute };
}
