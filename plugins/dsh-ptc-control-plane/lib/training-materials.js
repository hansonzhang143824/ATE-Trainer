import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';
import { trainingAddressBook } from './training-paths.js';

const execFile = promisify(execFileCallback);
const PRODUCTS = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];
const DIGEST = /^[a-f0-9]{64}$/;
export const TRAINING_POLICY_FILES = Object.freeze([
  'scripts/hash_ate_plaintext.py', 'scripts/material_plaintext_hash.py',
  'scripts/refresh_dft_meta_from_source.py', 'scripts/render_dft_conditions_yaml.py',
  'scripts/validate_dft_outputs.py', 'scripts/dft_source.py', 'scripts/dft_test_condition.py',
  'scripts/ptc_contract_schema.py', 'scripts/ptc_trim_validation.py', 'scripts/project_info.py',
]);
const DEVICE = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;
// Invoke the approved hash command for each policy in one Python interpreter.
// This avoids ten interpreter startups without introducing a second hasher.
const HASH_POLICIES = `import contextlib, io, json, pathlib, runpy, sys
command = pathlib.Path(sys.argv[1])
files = json.loads(sys.argv[2])
sys.path.insert(0, str(command.parent))
reports = []
for file in files:
 sys.argv = [str(command), file, '--json']
 output = io.StringIO()
 with contextlib.redirect_stdout(output):
  try: runpy.run_path(str(command), run_name='__main__')
  except SystemExit as result:
   if result.code not in (None, 0): raise
 reports.append(json.loads(output.getvalue()))
print(json.dumps(reports))`;
const COPY_PLAINTEXT = `import json, pathlib, subprocess, sys
source, target, command = map(pathlib.Path, sys.argv[1:])
def digest(p):
 result = subprocess.run([sys.executable, '-X', 'utf8', str(command), str(p), '--json'], check=True, capture_output=True, text=True, encoding='utf-8', timeout=10)
 return json.loads(result.stdout)['sha256']
before = digest(source)
with source.open('rb') as src, target.open('xb') as dst:
 while block := src.read(1024 * 1024): dst.write(block)
after = digest(source)
copied = digest(target)
if before != after or before != copied: raise RuntimeError('material changed during plaintext snapshot')
print(json.dumps({'sha256': copied, 'view': 'python-plaintext'}))`;

function id(value, label) {
  if (typeof value !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(value)
      || DEVICE.test(value) || /[. ]$/.test(value)) throw new Error(`unsafe ${label}`);
  return value;
}

function exists(file) { try { fs.lstatSync(file); return true; } catch (error) { if (error.code === 'ENOENT') return false; throw error; } }

// Reject links on every existing ancestor, including workspace ancestors. This
// intentionally rejects even in-workspace links: run ownership stays unambiguous.
function safe(root, file) {
  const absolute = path.resolve(file);
  const relative = path.relative(root, absolute);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) throw new Error('path escapes workspace');
  let cursor = absolute;
  while (true) {
    const part = path.basename(cursor);
    if (part && (DEVICE.test(part) || /[. ]$/.test(part) || /[<>:"|?*]/.test(part))) throw new Error('unsafe Windows path');
    if (exists(cursor) && fs.lstatSync(cursor).isSymbolicLink()) throw new Error(`links are forbidden: ${cursor}`);
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  return absolute;
}

function sha(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function relative(root, file) { return path.relative(root, file).split(path.sep).join('/'); }
function json(file) { return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '')); }
function freeze(value) { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; }

function fingerprint(files, policies) {
  return sha(Buffer.from(JSON.stringify({
    materials: files.map(({ source, sha256 }) => ({ source, sha256 })),
    policies: policies.map(({ path, sha256 }) => ({ path, sha256 })),
  }), 'utf8'));
}

function readManifest(root, runId, expectedCacheKey) {
  id(runId, 'runId');
  const manifest = json(safe(root, path.join(root, 'Training_Materials/runs', runId, 'material-manifest.json')));
  if (manifest.schemaVersion !== 2 || manifest.runId !== runId || !Array.isArray(manifest.files)
      || !Array.isArray(manifest.policies) || !Array.isArray(manifest.testItems)
      || manifest.testItems.length === 0 || manifest.testItems.some((tm) => !/^TM[0-9]+$/.test(tm))
      || JSON.stringify(manifest.policies.map((entry) => entry.path)) !== JSON.stringify(TRAINING_POLICY_FILES)
      || manifest.policies.some((entry) => !DIGEST.test(entry.sha256) || !DIGEST.test(entry.diskSha256))
      || manifest.files.some((entry) => !DIGEST.test(entry.sha256))
      || manifest.cacheKey !== fingerprint(manifest.files, manifest.policies)
      || (expectedCacheKey !== undefined && expectedCacheKey !== manifest.cacheKey)) throw new Error('invalid or changed material snapshot fingerprint');
  const prefix = `Training_Materials/runs/${runId}/`;
  const expectedSources = new Map([
    ['Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx', ['input/Dali_testmode.xlsx', 'python-plaintext']],
    ['Training_Materials/Input_GlobalMaterial/DALI-special-information.json', ['input/DALI-special-information.json', 'python-plaintext']],
    ['User_input/DFT解析规则.txt', ['input/DFT解析规则.txt', 'python-plaintext']],
    ['team/expert-profiles/ptc-dft-expert/instructions.md', ['profile/instructions.md', 'exact-bytes']],
    ['team/expert-profiles/ptc-dft-expert/profile.yaml', ['profile/profile.yaml', 'exact-bytes']],
    ['team/expert-profiles/ptc-dft-expert/output-contract.schema.json', ['profile/output-contract.schema.json', 'exact-bytes']],
  ]);
  if (new Set(manifest.files.map((entry) => entry.source)).size !== manifest.files.length
      || !manifest.files.some((entry) => entry.path === `${prefix}input/Dali_testmode.xlsx`)
      || !manifest.files.some((entry) => entry.path === `${prefix}profile/instructions.md`)) throw new Error('snapshot required material is missing');
  for (const entry of manifest.files) {
    const expected = expectedSources.get(entry.source);
    if (!expected || entry.path !== `${prefix}${expected[0]}` || entry.view !== expected[1]) throw new Error('invalid snapshot material path or byte view');
    safe(root, path.join(root, entry.path));
  }
  return manifest;
}

/** Synchronous guard check: disk hashes here detect policy-file changes only;
 * they are NOT canonical input material hashes and never read the workbook.
 * Plaintext policy SHA-256 is verified by verifyTrainingMaterials at host gates.
 */
export function verifyTrainingPolicySync(workspaceRoot, runId, expectedCacheKey) {
  const root = path.resolve(workspaceRoot);
  const manifest = readManifest(root, runId, expectedCacheKey);
  for (const entry of manifest.policies) {
    const file = safe(root, path.join(root, entry.path));
    if (sha(fs.readFileSync(file)) !== entry.diskSha256) throw new Error(`training policy changed: ${entry.path}; create a new run`);
  }
  for (const entry of manifest.files.filter((file) => file.view === 'exact-bytes')) {
    if (sha(fs.readFileSync(safe(root, path.join(root, entry.path)))) !== entry.sha256) throw new Error('immutable material snapshot changed');
  }
  return true;
}

/** Validate frozen input/profile bytes and live policy plaintext before/after a
 * host gate. Does not rebind, patch or refresh any snapshot. Drift fails closed.
 */
export async function verifyTrainingMaterials(workspaceRoot, materials) {
  const root = path.resolve(workspaceRoot);
  if (!materials || typeof materials.cacheKey !== 'string') throw new Error('prepared material fingerprint is required');
  const manifest = readManifest(root, materials.runId, materials.cacheKey);
  verifyTrainingPolicySync(root, materials.runId, materials.cacheKey);
  for (const entry of manifest.files) {
    const file = safe(root, path.join(root, entry.path));
    const digest = entry.view === 'python-plaintext' ? await plaintextDigest(root, file) : sha(fs.readFileSync(file));
    if (digest !== entry.sha256) throw new Error('immutable material snapshot changed');
  }
  const policyDigests = await policyPlaintextDigests(root);
  for (const [index, entry] of manifest.policies.entries()) {
    if (policyDigests[index] !== entry.sha256) throw new Error(`training policy changed: ${entry.path}; create a new run`);
  }
  verifyTrainingPolicySync(root, materials.runId, materials.cacheKey);
  return true;
}

function completedProducts(root, directory, state, runId, cacheKey, tm) {
  const value = state.outcome?.evidence;
  if (typeof value !== 'string') return null;
  const file = safe(root, path.resolve(root, value));
  if (!['dft-terminal.json', 'dft-preflight.json'].some((name) => file === path.join(directory, 'evidence', name))) return null;
  const evidence = json(file);
  const products = evidence.finalProducts?.[tm];
  if (evidence.runId !== runId || evidence.cacheKey !== cacheKey
      || !Array.isArray(evidence.reports) || !evidence.reports.some((report) => report.tm === tm && report.status === 'ready' && report.exitCode === 0)
      || !products || PRODUCTS.some((name) => !DIGEST.test(products[name]))) return null;
  for (const name of PRODUCTS) {
    const candidate = safe(root, path.join(directory, 'input-sync/dft', tm, name));
    if (!exists(candidate) || sha(fs.readFileSync(candidate)) !== products[name]) return null;
  }
  return products;
}

async function plaintextDigest(root, file) {
  const command = safe(root, path.join(root, 'scripts/hash_ate_plaintext.py'));
  const { stdout } = await execFile('python', ['-X', 'utf8', command, safe(root, file), '--json'], {
    cwd: root, windowsHide: true, timeout: 30_000, encoding: 'utf8', maxBuffer: 1024 * 1024,
  });
  const report = JSON.parse(stdout);
  if (!DIGEST.test(report.sha256) || report.view !== 'python-plaintext') throw new Error('invalid canonical material hash report');
  return report.sha256;
}

async function policyPlaintextDigests(root) {
  const command = safe(root, path.join(root, 'scripts/hash_ate_plaintext.py'));
  const files = TRAINING_POLICY_FILES.map((file) => safe(root, path.join(root, file)));
  const { stdout } = await execFile('python', ['-X', 'utf8', '-c', HASH_POLICIES, command, JSON.stringify(files)], {
    cwd: root, windowsHide: true, timeout: 30_000, encoding: 'utf8', maxBuffer: 1024 * 1024,
  });
  const reports = JSON.parse(stdout);
  if (!Array.isArray(reports) || reports.length !== files.length
      || reports.some((report, index) => report.path !== files[index] || !DIGEST.test(report.sha256) || report.view !== 'python-plaintext')) throw new Error('invalid canonical policy hash report');
  return reports.map((report) => report.sha256);
}

async function copyMaterial(root, source, target) {
  safe(root, source); safe(root, target);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  const { stdout } = await execFile('python', ['-X', 'utf8', '-c', COPY_PLAINTEXT, source, target, safe(root, path.join(root, 'scripts/hash_ate_plaintext.py'))], {
    cwd: root, windowsHide: true, timeout: 30_000, encoding: 'utf8', maxBuffer: 1024 * 1024,
  });
  const report = JSON.parse(stdout);
  if (!DIGEST.test(report.sha256)) throw new Error('invalid plaintext snapshot digest');
  return report.sha256;
}

function copyBytes(root, source, target) {
  safe(root, source); safe(root, target);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target, fs.constants.COPYFILE_EXCL);
  return sha(fs.readFileSync(target));
}

function addressBook(root, manifest) {
  const paths = {
    ...trainingAddressBook(manifest.runId),
    manifestFile: `Training_Materials/runs/${manifest.runId}/material-manifest.json`,
  };
  return freeze({ schemaVersion: 2, runId: manifest.runId, testItems: manifest.testItems,
    ...paths, cacheKey: manifest.cacheKey, candidateSources: manifest.candidateSources,
    cacheCompatible: Object.values(manifest.candidateSources).every((candidate) => candidate.cacheCompatible),
    absolute: Object.fromEntries(Object.entries(paths).map(([key, value]) => [key, path.join(root, value)])),
  });
}

/**
 * Host-owned, one-time material preparation. Returns workspace-relative forward
 * slash paths (plus `absolute` equivalents), a cacheKey binding all input/draft
 * bytes and per-TM candidate provenance. Await before dispatching or gating.
 * Outputs are private copies, never links. Candidate validity is NOT certified:
 * caller must run its gate and require cacheCompatible for UNCHANGED reuse.
 * Reentry verifies immutable snapshots and never overwrites products. A partial
 * preparation fails closed; use a new runId rather than repairing it in place.
 */
export async function prepareTrainingMaterials(workspaceRoot, runId, testItems) {
  id(runId, 'runId');
  if (!Array.isArray(testItems) || !testItems.length || testItems.some((tm) => typeof tm !== 'string' || !/^TM[0-9]+$/.test(tm))) throw new Error('invalid testItems');
  const tms = [...new Set(testItems)].sort();
  const root = path.resolve(workspaceRoot);
  safe(root, root);
  const runRoot = safe(root, path.join(root, 'Training_Materials/runs', runId));
  const manifestFile = safe(root, path.join(runRoot, 'material-manifest.json'));
  if (exists(manifestFile)) {
    const manifest = readManifest(root, runId);
    if (JSON.stringify(manifest.testItems) !== JSON.stringify(tms)) throw new Error('material snapshot identity differs');
    await verifyTrainingMaterials(root, addressBook(root, manifest));
    for (const folder of ['input-sync/dft', 'verification']) safe(root, path.join(runRoot, folder));
    for (const tm of tms) for (const product of PRODUCTS) safe(root, path.join(runRoot, 'input-sync/dft', tm, product));
    return addressBook(root, manifest);
  }
  const lock = safe(root, path.join(runRoot, 'material-preparation.lock'));
  fs.mkdirSync(runRoot, { recursive: true });
  fs.writeFileSync(lock, 'material preparation started\n', { flag: 'wx' });
  const policies = [];
  const policyDiskDigests = TRAINING_POLICY_FILES.map((policy) => sha(fs.readFileSync(safe(root, path.join(root, policy)))));
  const policyDigests = await policyPlaintextDigests(root);
  for (const [index, policy] of TRAINING_POLICY_FILES.entries()) {
    const file = safe(root, path.join(root, policy));
    const diskSha256 = policyDiskDigests[index];
    const digest = policyDigests[index];
    if (sha(fs.readFileSync(file)) !== diskSha256) throw new Error(`training policy changed during snapshot: ${policy}`);
    policies.push({ path: policy, sha256: digest, diskSha256 });
  }
  const sources = [
    ['Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx', 'input/Dali_testmode.xlsx', true, true],
    ['Training_Materials/Input_GlobalMaterial/DALI-special-information.json', 'input/DALI-special-information.json', false, true],
    ['User_input/DFT解析规则.txt', 'input/DFT解析规则.txt', false, true],
    ['team/expert-profiles/ptc-dft-expert/instructions.md', 'profile/instructions.md', true, false],
    ['team/expert-profiles/ptc-dft-expert/profile.yaml', 'profile/profile.yaml', false, false],
    ['team/expert-profiles/ptc-dft-expert/output-contract.schema.json', 'profile/output-contract.schema.json', false, false],
  ];
  const files = [];
  for (const [sourcePath, destination, required, plaintext] of sources) {
    const source = safe(root, path.join(root, sourcePath));
    if (!exists(source)) { if (required) throw new Error(`required training material missing: ${sourcePath}`); continue; }
    const target = safe(root, path.join(runRoot, destination));
    const digest = plaintext ? await copyMaterial(root, source, target) : copyBytes(root, source, target);
    files.push({ source: sourcePath, path: relative(root, target), sha256: digest, view: plaintext ? 'python-plaintext' : 'exact-bytes' });
  }
  const cacheKey = fingerprint(files, policies);
  const runsRoot = path.dirname(runRoot);
  const prior = [];
  for (const name of fs.readdirSync(runsRoot)) {
    if (name === runId) continue;
    try {
      id(name, 'prior runId');
      const directory = safe(root, path.join(runsRoot, name));
      const stateFile = safe(root, path.join(directory, 'state.json'));
      const priorManifestFile = safe(root, path.join(directory, 'material-manifest.json'));
      if (!exists(stateFile) || !exists(priorManifestFile)) continue;
      const state = json(stateFile); const previous = readManifest(root, name, cacheKey);
      if (state.status === 'completed' && previous.cacheKey === cacheKey && previous.runId === name) prior.push({ name, directory, previous, state, finishedAt: state.finishedAt ?? state.updatedAt ?? '' });
    } catch { /* Untrusted or incomplete runs are not cache candidates. */ }
  }
  prior.sort((a, b) => b.finishedAt.localeCompare(a.finishedAt));
  const candidateSources = {};
  for (const tm of tms) {
    const destination = safe(root, path.join(runRoot, 'input-sync/dft', tm));
    fs.mkdirSync(destination, { recursive: true });
    const completed = prior.find((entry) => {
      try {
        if (!entry.previous.testItems?.includes(tm)) return false;
        entry.sealedProducts = completedProducts(root, entry.directory, entry.state, entry.name, cacheKey, tm);
        return Boolean(entry.sealedProducts);
      } catch { return false; }
    });
    const source = completed ? path.join(completed.directory, 'input-sync/dft', tm) : path.join(root, 'Training_Materials/Output_Global_Material/dft', tm);
    safe(root, source);
    const copied = [];
    for (const name of PRODUCTS) {
      const candidate = safe(root, path.join(source, name));
      if (!exists(candidate)) continue;
      const copiedDigest = copyBytes(root, candidate, path.join(destination, name));
      if (completed && copiedDigest !== completed.sealedProducts[name]) throw new Error(`completed candidate changed while copying: ${tm}/${name}`);
      copied.push(name);
    }
    candidateSources[tm] = { kind: completed ? 'run' : copied.length ? 'legacy' : 'none', ...(completed ? { runId: completed.name } : {}), cacheCompatible: Boolean(completed), copied };
  }
  fs.mkdirSync(safe(root, path.join(runRoot, 'verification')), { recursive: true });
  const manifest = { schemaVersion: 2, runId, testItems: tms, createdAt: new Date().toISOString(), cacheKey, files, policies, candidateSources };
  fs.writeFileSync(manifestFile, `${JSON.stringify(manifest, null, 2)}\n`, { flag: 'wx', encoding: 'utf8' });
  const materials = addressBook(root, manifest);
  await verifyTrainingMaterials(root, materials);
  return materials;
}
