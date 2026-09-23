import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';
import { prepareTrainingMaterials, verifyTrainingMaterials } from './training-materials.js';
import { assertSafeRunPath } from './run-context.js';
import { trainingAddressBook } from './training-paths.js';

const execFile = promisify(execFileCallback);
const DIGEST = /^[a-f0-9]{64}$/;
const EXCLUDED_DIRS = new Set(['.git', '.vs', '__pycache__', 'node_modules', 'debug', 'release', 'build', 'bin', 'obj', 'x64', 'ipch', 'backup', 'backups', 'bak']);
const EXCLUDED_EXTENSIONS = new Set(['.bak', '.dll', '.pdb', '.obj', '.pch', '.ilk', '.exp', '.idb', '.sdf', '.opensdf', '.suo', '.tlog', '.lastbuildstate', '.pgs', '.ldf']);
const DEFAULT_LIMITS = Object.freeze({ maxFiles: 5000, maxBytes: 512 * 1024 * 1024, maxFileBytes: 64 * 1024 * 1024, batchFiles: 40, timeoutMs: 30_000 });

const INSPECT = `import ast, contextlib, io, json, pathlib, re, runpy, sys
root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / 'scripts'))
def safe(file):
 if not file.is_relative_to(root): raise RuntimeError('inspection source outside workspace')
 for p in [file, *file.parents]:
  if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()): raise RuntimeError('linked inspection source denied')
 return file
def digest(file):
 sys.argv = [str(root / 'scripts/hash_ate_plaintext.py'), str(file), '--json']
 output = io.StringIO()
 with contextlib.redirect_stdout(output):
  try: runpy.run_path(sys.argv[0], run_name='__main__')
  except SystemExit as exc:
   if exc.code not in (None, 0): raise
 return json.loads(output.getvalue())['sha256']
info_path = safe(root / 'Project_Info.json')
info = json.loads(info_path.read_text(encoding='utf-8-sig'))
module = runpy.run_path(str(safe(root / 'scripts/project_info.py')))
approval = info.get('approval') or {}
if not approval.get('approvedBy') or not approval.get('approvedAt') or approval.get('inputsDigest') != module['inputs_digest'](info): raise RuntimeError('Project_Info configuration is not approved or approval digest differs')
registry = json.loads(safe(root / 'team/ptc/ptc_stage_registry.json').read_text(encoding='utf-8-sig'))
tree = ast.parse(safe(root / 'scripts/validate_expert_roster.py').read_text(encoding='utf-8-sig'))
mapping = None
for node in tree.body:
 if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'OWNER_PROFILE' for t in node.targets): mapping = ast.literal_eval(node.value)
if not isinstance(mapping, dict): raise RuntimeError('approved owner/profile mapping is missing')
owners = {'dft-expert', 'schematic-expert'}
for stage in registry.get('stateMachine', []):
 if stage == 'COMPLETE': continue
 owner = (registry.get('stages', {}).get(stage) or {}).get('owner')
 if not isinstance(owner, str): raise RuntimeError('stage owner missing: ' + str(stage))
 if owner != 'captain': owners.add(owner)
profiles = {}; inspected_hashes = {'Project_Info.json': digest(info_path), 'team/ptc/ptc_stage_registry.json': digest(root / 'team/ptc/ptc_stage_registry.json'), 'scripts/validate_expert_roster.py': digest(root / 'scripts/validate_expert_roster.py')}
for owner in sorted(owners):
 profile = mapping.get(owner)
 if not isinstance(profile, str) or not re.fullmatch(r'[a-z][a-z0-9-]{1,63}', profile): raise RuntimeError('unmapped pipeline owner: ' + owner)
 text = safe(root / 'team/expert-profiles' / profile / 'profile.yaml').read_text(encoding='utf-8-sig')
 actual = re.search(r'^ownerRole:\\s*[\\\"\\\']?([^\\s#\\\"\\\']+)', text, re.M)
 if not actual or actual.group(1) != owner: raise RuntimeError('profile ownerRole mismatch: ' + profile)
 profiles[owner] = profile
 inspected_hashes['team/expert-profiles/' + profile + '/profile.yaml'] = digest(root / 'team/expert-profiles' / profile / 'profile.yaml')
print(json.dumps({'projectInfo': info, 'projectInfoSha256': inspected_hashes['Project_Info.json'], 'registry': registry, 'ownerProfiles': profiles, 'inspectedHashes': inspected_hashes}, ensure_ascii=False))`;

const COPY_BATCH = `import contextlib, io, json, pathlib, runpy, sys
plan_path = pathlib.Path(sys.argv[1]); plan = json.loads(plan_path.read_text(encoding='utf-8'))
start, end = int(sys.argv[2]), int(sys.argv[3])
root = pathlib.Path(plan['workspaceRoot']); run_root = pathlib.Path(plan['runRoot'])
sys.path.insert(0, str(root / 'scripts'))
def safe(file):
 for p in [file, *file.parents]:
  if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()): raise RuntimeError('link/junction denied: ' + str(p))
def digest(file):
 sys.argv = [str(root / 'scripts/hash_ate_plaintext.py'), str(file), '--json']
 output = io.StringIO()
 with contextlib.redirect_stdout(output):
  try: runpy.run_path(sys.argv[0], run_name='__main__')
  except SystemExit as exc:
   if exc.code not in (None, 0): raise
 report = json.loads(output.getvalue())
 if report.get('view') != 'python-plaintext': raise RuntimeError('canonical hash view missing')
 return report['sha256']
result = []
for entry in plan['files'][start:end]:
 source, target = pathlib.Path(entry['source']), root / entry['snapshotPath']
 baseline = root / entry['baselinePath'] if entry.get('mutable') else None
 safe(source); safe(target)
 if not target.is_relative_to(run_root): raise RuntimeError('snapshot target outside run')
 if baseline:
  safe(baseline)
  if not baseline.is_relative_to(run_root): raise RuntimeError('baseline target outside run')
 allowed = source.is_relative_to(root) or source.is_relative_to(pathlib.Path(plan['programRoot'])) or (source.parent == pathlib.Path(plan['programRoot']).parent and source.suffix.lower() in ['.spec', '.treg'])
 if not allowed: raise RuntimeError('source outside approved scope')
 before = digest(source)
 if entry.get('expectedSha256') and entry['expectedSha256'] != before: raise RuntimeError('approved source changed after inspection')
 target.parent.mkdir(parents=True, exist_ok=True)
 if baseline: baseline.parent.mkdir(parents=True, exist_ok=True)
 count = 0
 with contextlib.ExitStack() as stack:
  src = stack.enter_context(source.open('rb')); dst = stack.enter_context(target.open('xb'))
  original = stack.enter_context(baseline.open('xb')) if baseline else None
  while block := src.read(1024 * 1024):
   count += len(block)
   if count > plan['limits']['maxFileBytes']: raise RuntimeError('plaintext file exceeds size limit')
   dst.write(block)
   if original: original.write(block)
 if before != digest(source) or before != digest(target): raise RuntimeError('source changed during snapshot')
 if baseline and before != digest(baseline): raise RuntimeError('baseline copy digest differs')
 result.append({**entry, 'sha256': before, 'size': count, 'view': 'python-plaintext'})
print(json.dumps(result, ensure_ascii=False))`;

const VERIFY_BATCH = `import contextlib, io, json, pathlib, runpy, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')); root = pathlib.Path(sys.argv[2]); start, end = int(sys.argv[3]), int(sys.argv[4])
sys.path.insert(0, str(root / 'scripts'))
for entry in manifest['files'][start:end]:
 file = root / (entry['baselinePath'] if entry.get('mutable') else entry['snapshotPath'])
 sys.argv = [str(root / 'scripts/hash_ate_plaintext.py'), str(file), '--json']; output = io.StringIO()
 with contextlib.redirect_stdout(output):
  try: runpy.run_path(sys.argv[0], run_name='__main__')
  except SystemExit as exc:
   if exc.code not in (None, 0): raise
 if json.loads(output.getvalue())['sha256'] != entry['sha256']: raise RuntimeError('immutable pipeline snapshot changed: ' + entry['snapshotPath'])
print('verified')`;

const CHECK_PROJECTS = `import json, pathlib, sys, xml.etree.ElementTree as ET
plan = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')); root = pathlib.Path(plan['workspaceRoot']); run_root = pathlib.Path(plan['runRoot'])
listed = {str((root / e['snapshotPath']).resolve()).lower() for e in plan['files']}
references = []; dynamic = []
for entry in plan['files']:
 if not entry['snapshotPath'].lower().endswith('.vcxproj'): continue
 project = root / entry['snapshotPath']
 for element in ET.parse(project).iter():
  tag = element.tag.rsplit('}', 1)[-1]
  value = element.attrib.get('Include')
  if tag not in ['ClCompile','ClInclude','ResourceCompile','None','ProjectReference','CustomBuild','Image','Text'] or not value: continue
  if '$(' in value or '%(' in value or '*' in value or '?' in value:
   dynamic.append({'project': entry['snapshotPath'], 'reference': value}); continue
  file = (project.parent / value.replace('\\\\', '/')).resolve()
  if not file.is_relative_to(run_root / 'vs-project') or str(file).lower() not in listed or not file.is_file(): raise RuntimeError('project participating file was not safely copied: ' + value)
  references.append({'project': entry['snapshotPath'], 'snapshotPath': str(file.relative_to(root)).replace('\\\\', '/')})
print(json.dumps({'participatingFiles': references, 'dynamicProjectReferences': dynamic}))`;

function relative(root, file) { return path.relative(root, file).split(path.sep).join('/'); }
function sha(value) { return crypto.createHash('sha256').update(value).digest('hex'); }
function freeze(value) { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; }
function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '')); }
function exists(file) { try { fs.lstatSync(file); return true; } catch (error) { if (error.code === 'ENOENT') return false; throw error; } }
function safeAny(file) {
  const absolute = path.resolve(file);
  // assertSafeRunPath also checks ancestors above this explicit approved root.
  return assertSafeRunPath(path.parse(absolute).root, absolute);
}
function inside(file, root) { const rel = path.relative(root, file); return rel === '' || (rel !== '..' && !rel.startsWith(`..${path.sep}`) && !path.isAbsolute(rel)); }
function limitsFor(options) {
  const limits = { ...DEFAULT_LIMITS, ...(options.limits ?? {}) };
  for (const [key, value] of Object.entries(limits)) if (!Number.isInteger(value) || value <= 0 || value > DEFAULT_LIMITS[key]) throw new Error(`invalid pipeline copy limit: ${key}`);
  return limits;
}
async function python(root, source, args, limits) {
  const { stdout } = await execFile('python', ['-X', 'utf8', '-c', source, ...args], { cwd: root,
    windowsHide: true, encoding: 'utf8', timeout: limits.timeoutMs, maxBuffer: 8 * 1024 * 1024 });
  return stdout;
}
function walk(root, { draft = false, vs = false } = {}) {
  const files = [];
  function visit(directory, depth = 0) {
    if (depth > 64) throw new Error('snapshot source exceeds directory depth limit');
    safeAny(directory);
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : 1)) {
      const file = safeAny(path.join(directory, entry.name));
      if (entry.isDirectory()) {
        if (EXCLUDED_DIRS.has(entry.name.toLowerCase()) || (draft && entry.name.toLowerCase() === 'versions')) continue;
        visit(file, depth + 1);
      } else if (entry.isFile()) {
        if ((draft && ['status.json'].includes(entry.name)) || (vs && (EXCLUDED_EXTENSIONS.has(path.extname(entry.name).toLowerCase()) || /\.bak(?:\.|$)/i.test(entry.name)))) continue;
        files.push(file);
        if (files.length > DEFAULT_LIMITS.maxFiles) throw new Error('snapshot source exceeds file count limit');
      } else throw new Error(`unsupported snapshot source type: ${file}`);
    }
  }
  visit(root);
  return files;
}
function pipelineFingerprint(manifest) {
  return sha(JSON.stringify({ runId: manifest.runId, testItems: manifest.testItems, baseCacheKey: manifest.baseCacheKey,
    approvedConfiguration: manifest.approvedConfiguration, ownerProfiles: manifest.ownerProfiles, addressBook: manifest.addressBook,
    files: manifest.files.map(({ source, snapshotPath, baselinePath, mutable, sha256, size, kind }) => ({ source, snapshotPath, baselinePath, mutable, sha256, size, kind })), generatedFiles: manifest.generatedFiles, snapshotPaths: manifest.snapshotPaths, projectReferences: manifest.projectReferences, missingOptional: manifest.missingOptional }));
}
function resultOf(base, manifest) { return freeze({ ...base, ...manifest.addressBook, pipelineManifestFile: `${base.runRoot}/pipeline-material-manifest.json`,
  pipelineCacheKey: manifest.pipelineCacheKey, ownerProfiles: manifest.ownerProfiles, snapshotPaths: manifest.snapshotPaths,
  missingOptional: manifest.missingOptional, approvedConfiguration: manifest.approvedConfiguration }); }

/**
 * Freeze the inputs of a complete pipeline training run. No expert, compiler,
 * approval stamping or production write occurs. The approved external program
 * root is read only; only its direct parent .spec/.treg files may join it.
 * options.limits may LOWER fixed copy budgets, never broaden source authority.
 * Existing final snapshots are verified and reused; interrupted plans reserve
 * their identity and fail closed rather than replacing any partially copied data.
 */
export async function preparePipelineMaterials(workspaceRoot, runId, testItems, options = {}) {
  const root = path.resolve(workspaceRoot);
  const address = trainingAddressBook(runId);
  const runRoot = assertSafeRunPath(root, address.runRoot);
  if (!Array.isArray(testItems) || !testItems.length || testItems.some((tm) => typeof tm !== 'string' || !/^TM[0-9]+$/.test(tm))) throw new Error('invalid pipeline testItems');
  const tms = [...new Set(testItems)].sort();
  const limits = limitsFor(options);
  let baseSourceBytes = 0;
  let baseSourceFiles = 0;
  for (const source of ['Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx', 'Training_Materials/Input_GlobalMaterial/DALI-special-information.json', 'User_input/DFT解析规则.txt', 'team/expert-profiles/ptc-dft-expert/instructions.md', 'team/expert-profiles/ptc-dft-expert/profile.yaml', 'team/expert-profiles/ptc-dft-expert/output-contract.schema.json']) {
    const file = assertSafeRunPath(root, source);
    if (!exists(file)) continue;
    const stat = fs.statSync(file);
    baseSourceBytes += stat.size; baseSourceFiles += 1;
    if (stat.size > limits.maxFileBytes || baseSourceBytes > limits.maxBytes || baseSourceFiles > limits.maxFiles) throw new Error('pipeline snapshot exceeds file count or total size limit');
  }
  const manifestPath = assertSafeRunPath(root, path.join(runRoot, 'pipeline-material-manifest.json'));
  const base = await prepareTrainingMaterials(root, runId, tms);
  const baseManifest = readJson(path.join(root, base.manifestFile));
  const baseDigests = new Map(baseManifest.files.map((entry) => [path.resolve(root, entry.source), entry.sha256]));
  if (exists(manifestPath)) {
    const manifest = readJson(manifestPath);
    if (manifest.schemaVersion !== 1 || manifest.kind !== 'ptc-pipeline-materials' || manifest.runId !== runId
        || JSON.stringify(manifest.testItems) !== JSON.stringify(tms) || manifest.baseCacheKey !== base.cacheKey
        || manifest.pipelineCacheKey !== pipelineFingerprint(manifest)) throw new Error('pipeline snapshot identity or fingerprint differs');
    for (const entry of manifest.files) {
      const file = assertSafeRunPath(root, entry.snapshotPath);
      if (!inside(file, runRoot) || !DIGEST.test(entry.sha256)) throw new Error('invalid pipeline snapshot path');
      if (entry.mutable && !inside(assertSafeRunPath(root, entry.baselinePath), path.join(runRoot, 'vs-baseline'))) throw new Error('invalid immutable VS baseline path');
    }
    for (const entry of manifest.generatedFiles ?? []) if (sha(fs.readFileSync(assertSafeRunPath(root, entry.snapshotPath))) !== entry.sha256) throw new Error('generated pipeline context changed');
    for (let start = 0; start < manifest.files.length; start += limits.batchFiles) await python(root, VERIFY_BATCH, [manifestPath, root, String(start), String(start + limits.batchFiles)], limits);
    return resultOf(base, manifest);
  }
  const lock = assertSafeRunPath(root, path.join(runRoot, 'pipeline-preparation.lock'));
  fs.writeFileSync(lock, 'pipeline snapshot preparation reserved\n', { flag: 'wx' });
  for (const file of ['Project_Info.json', 'scripts/project_info.py', 'scripts/validate_expert_roster.py', 'team/ptc/ptc_stage_registry.json']) assertSafeRunPath(root, file);
  const inspected = JSON.parse(await python(root, INSPECT, [root], limits));
  const info = inspected.projectInfo;
  if (!DIGEST.test(inspected.projectInfoSha256) || typeof info.inputs?.program !== 'string' || !info.inputs.program.trim()) throw new Error('approved program root is missing');
  if (typeof info.inputs.dft !== 'string' || path.basename(info.inputs.dft.replaceAll('\\', '/')) !== 'Dali_testmode.xlsx') throw new Error('approved DFT locator does not match the training workbook');
  const programRoot = safeAny(path.resolve(root, info.inputs.program));
  if (!fs.statSync(programRoot).isDirectory()) throw new Error('approved program source is not a directory');
  if (inside(runRoot, programRoot) || inside(programRoot, runRoot)) throw new Error('approved program source overlaps training run');
  const programName = path.basename(programRoot);
  const vsProjectRoot = `${address.runRoot}/vs-project`;
  const vsBaselineRoot = `${address.runRoot}/vs-baseline`;
  const programSourceRoot = `${vsProjectRoot}/${programName}`;
  const files = [];
  const sourceToDestination = new Map();
  const missingOptional = [];
  let sourceBytes = baseSourceBytes;
  let storedFiles = baseSourceFiles;
  function add(source, snapshotPath, kind, { optional = false, expectedSha256 } = {}) {
    source = safeAny(source);
    if (!exists(source)) { if (optional) { missingOptional.push(relative(root, source)); return null; } throw new Error(`required pipeline source missing: ${source}`); }
    const destination = assertSafeRunPath(root, snapshotPath);
    if (!inside(destination, runRoot)) throw new Error('pipeline destination escapes run');
    if (!inside(source, root) && !inside(source, programRoot)
        && !(path.dirname(source) === path.dirname(programRoot) && ['.spec', '.treg'].includes(path.extname(source).toLowerCase()))) throw new Error('source outside approved program scope');
    if (sourceToDestination.has(source)) return sourceToDestination.get(source);
    const stat = fs.statSync(source);
    if (!stat.isFile() || stat.size > limits.maxFileBytes) throw new Error(`source exceeds file limit or is not a file: ${source}`);
    const mutable = kind === 'vs-source' || kind === 'vs-spec-treg';
    sourceBytes += stat.size * (mutable ? 2 : 1);
    storedFiles += mutable ? 2 : 1;
    if (storedFiles > limits.maxFiles || sourceBytes > limits.maxBytes) throw new Error('pipeline snapshot exceeds file count or total size limit');
    if (files.some((entry) => entry.snapshotPath.toLowerCase() === snapshotPath.toLowerCase())) throw new Error('duplicate pipeline snapshot target');
    const inspectedDigest = expectedSha256 ?? inspected.inspectedHashes[relative(root, source)] ?? baseDigests.get(source);
    if (inspectedDigest && baseDigests.has(source) && inspectedDigest !== baseDigests.get(source)) throw new Error('draft changed after base training snapshot');
    files.push({ source, snapshotPath, kind, ...(mutable ? { mutable: true, baselinePath: snapshotPath.replace(`${vsProjectRoot}/`, `${vsBaselineRoot}/`) } : {}), ...(inspectedDigest ? { expectedSha256: inspectedDigest } : {}) });
    sourceToDestination.set(source, snapshotPath);
    return snapshotPath;
  }
  const input = { dft: base.workbook, special: exists(path.join(root, base.special)) ? base.special : null };
  for (const [name, category] of [['schematic', 'schematic'], ['cbit', 'cbit']]) {
    if (typeof info.inputs?.[category] !== 'string') throw new Error(`approved ${category} source is ambiguous`);
    const basename = path.basename(info.inputs[category].replaceAll('\\', '/'));
    input[name] = add(path.join(root, 'Training_Materials/Input_GlobalMaterial', basename), `${address.inputRoot}/${basename}`, category);
  }
  input.confirmed = add(path.join(root, 'Training_Materials/Input_GlobalMaterial/sch_confirmed.json'), `${address.inputRoot}/sch_confirmed.json`, 'confirmed');
  const projectDir = assertSafeRunPath(root, info.projectDir);
  const registerRoot = `${address.runRoot}/register`;
  const registerSources = {};
  for (const tm of tms) registerSources[tm] = add(path.join(projectDir, 'reg_config', `${tm.toLowerCase()}.sv`), `${registerRoot}/${tm.toLowerCase()}.sv`, 'register');
  const intentResolutions = add(path.join(projectDir, 'meta/intent-resolutions.json'), `${address.inputRoot}/intent-resolutions.json`, 'intent-resolutions', { optional: true });
  const approvedProjectInfoPath = add(path.join(root, 'Project_Info.json'), `${address.runRoot}/configuration/approved-Project_Info.json`, 'approved-config', { expectedSha256: inspected.projectInfoSha256 });
  const originalProjectConfigPath = add(path.join(root, 'project_config.json'), `${address.runRoot}/configuration/original-project_config.json`, 'project-config', { optional: true });
  const registry = add(path.join(root, 'team/ptc/ptc_stage_registry.json'), `${address.runRoot}/orchestration/ptc_stage_registry.json`, 'registry');
  add(path.join(root, 'scripts/validate_expert_roster.py'), `${address.runRoot}/orchestration/validate_expert_roster.py`, 'owner-profile-mapping');
  for (const script of new Set(['scripts/ptc_trim_validation.py', ...Object.values(inspected.registry.stages).map((stage) => stage.gate)])) {
    if (typeof script !== 'string' || !/^scripts\/[A-Za-z0-9._-]+\.py$/.test(script)) throw new Error('pipeline registry gate is not a scoped Python script');
    add(path.join(root, script), `${address.runRoot}/${script}`, 'gate-policy');
  }
  const profileRoots = {};
  for (const profileId of [...new Set(Object.values(inspected.ownerProfiles))].sort()) {
    const source = assertSafeRunPath(root, `team/expert-profiles/${profileId}`);
    profileRoots[profileId] = `${address.runRoot}/profiles/${profileId}`;
    for (const name of ['instructions.md', 'profile.yaml']) if (!exists(path.join(source, name))) throw new Error(`required draft file missing: ${profileId}/${name}`);
    for (const file of walk(source, { draft: true })) add(file, `${profileRoots[profileId]}/${relative(source, file)}`, 'draft-profile');
  }
  const knowledgeRoot = `${address.runRoot}/knowledge`;
  const rulesRoot = `${address.runRoot}/rules`;
  const libraryRoot = `${address.runRoot}/Library-Functions`;
  for (const [source, destination, kind] of [['knowledge', knowledgeRoot, 'knowledge'], ['User_input', rulesRoot, 'rules'], ['Library-Functions', libraryRoot, 'library']]) {
    const directory = assertSafeRunPath(root, source);
    if (!exists(directory)) { missingOptional.push(source); continue; }
    for (const file of walk(directory)) add(file, `${destination}/${relative(directory, file)}`, kind);
  }
  for (const file of walk(programRoot, { vs: true })) add(file, `${programSourceRoot}/${relative(programRoot, file)}`, 'vs-source');
  for (const entry of fs.readdirSync(path.dirname(programRoot), { withFileTypes: true })) {
    if (['.spec', '.treg'].includes(path.extname(entry.name).toLowerCase())) add(path.join(path.dirname(programRoot), entry.name), `${vsProjectRoot}/${entry.name}`, 'vs-spec-treg');
  }
  const vsProjects = files.filter((entry) => entry.kind === 'vs-source' && entry.snapshotPath.toLowerCase().endsWith('.vcxproj')).map((entry) => entry.snapshotPath);
  const vsSolutions = files.filter((entry) => entry.kind === 'vs-source' && entry.snapshotPath.toLowerCase().endsWith('.sln')).map((entry) => entry.snapshotPath);
  if (!vsProjects.length) throw new Error('approved program contains no vcxproj');
  const trials = Object.fromEntries(tms.map((tm) => [tm, `${address.runRoot}/trials/${tm.toLowerCase()}`]));
  const projectInfoPath = `${address.runRoot}/configuration/training-context.json`;
  const addressBook = { runRoot: address.runRoot, input, inputSyncRoot: `${address.runRoot}/input-sync`, outputRoot: `${address.runRoot}/input-sync`, dftRoot: base.dftRoot,
    schematicRoot: `${address.runRoot}/input-sync/schematic`, errorRoot: `${address.runRoot}/errorLog`, verificationRoot: base.verificationRoot,
    registerRoot, registerSources, intentResolutions, trials, knowledgeRoot, rulesRoot, libraryRoot,
    registry, profileRoots, approvedProjectInfoPath, originalProjectConfigPath, projectInfoPath, vsProjectRoot, vsBaselineRoot,
    programSourceRoot, immutableProgramSourceRoot: `${vsBaselineRoot}/${programName}`, vsProjects, vsSolutions,
    specFiles: files.filter((entry) => entry.snapshotPath.toLowerCase().endsWith('.spec')).map((entry) => entry.snapshotPath),
    tregFiles: files.filter((entry) => entry.snapshotPath.toLowerCase().endsWith('.treg')).map((entry) => entry.snapshotPath) };
  const planFile = assertSafeRunPath(root, path.join(runRoot, 'pipeline-copy-plan.json'));
  fs.writeFileSync(planFile, JSON.stringify({ workspaceRoot: root, runRoot, programRoot, limits, files }), { flag: 'wx', encoding: 'utf8' });
  const copied = [];
  for (let start = 0; start < files.length; start += limits.batchFiles) {
    const batch = JSON.parse(await python(root, COPY_BATCH, [planFile, String(start), String(start + limits.batchFiles)], limits));
    if (!Array.isArray(batch) || batch.length !== Math.min(limits.batchFiles, files.length - start)
        || batch.some((entry, index) => entry.source !== files[start + index].source || entry.snapshotPath !== files[start + index].snapshotPath || !DIGEST.test(entry.sha256))) throw new Error('invalid plaintext pipeline copy report');
    copied.push(...batch);
    if (copied.reduce((sum, entry) => sum + entry.size * (entry.mutable ? 2 : 1), baseSourceBytes) > limits.maxBytes) throw new Error('pipeline plaintext total exceeds size limit');
  }
  await verifyTrainingMaterials(root, base);
  const projectReferences = JSON.parse(await python(root, CHECK_PROJECTS, [planFile], limits));
  for (const trial of Object.values(trials)) fs.mkdirSync(assertSafeRunPath(root, trial), { recursive: true });
  const approvedConfiguration = { source: 'Project_Info.json', sha256: inspected.projectInfoSha256, approval: info.approval };
  const context = { schemaVersion: 1, mode: 'training', runId, approvedConfiguration, sourceConfiguration: approvedProjectInfoPath,
    programSourceRoot, inputs: input, registerSources, outputRoot: `${address.runRoot}/input-sync`, trials,
    note: 'Training snapshot mapping only; this is not a new approval and does not replace Project_Info.json.' };
  fs.writeFileSync(assertSafeRunPath(root, projectInfoPath), `${JSON.stringify(context, null, 2)}\n`, { flag: 'wx', encoding: 'utf8' });
  const generatedFiles = [{ snapshotPath: projectInfoPath, sha256: sha(fs.readFileSync(path.join(root, projectInfoPath))), view: 'exact-bytes' }];
  const snapshotPaths = Object.fromEntries(copied.map(({ source, snapshotPath }) => [source, snapshotPath]));
  for (const entry of baseManifest.files) snapshotPaths[path.resolve(root, entry.source)] ??= entry.path;
  const manifest = { schemaVersion: 1, kind: 'ptc-pipeline-materials', runId, testItems: tms, createdAt: new Date().toISOString(),
    baseMaterialManifest: base.manifestFile, baseCacheKey: base.cacheKey, approvedConfiguration, ownerProfiles: inspected.ownerProfiles,
    addressBook, files: copied, generatedFiles, snapshotPaths, missingOptional, limits, projectReferences,
    exclusions: { directories: [...EXCLUDED_DIRS], extensions: [...EXCLUDED_EXTENSIONS], draft: ['versions', 'status.json'] } };
  manifest.pipelineCacheKey = pipelineFingerprint(manifest);
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, { flag: 'wx', encoding: 'utf8' });
  return resultOf(base, manifest);
}
