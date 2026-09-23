import fs from 'node:fs';
import path from 'node:path';
import { spawn as nativeSpawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { sha256Bytes } from './release-integrity.js';

export const TRAINING_MSBUILD = 'C:\\Program Files (x86)\\MSBuild\\12.0\\Bin\\MSBuild.exe';
const TASKKILL = 'C:\\Windows\\System32\\taskkill.exe';
const VC_TARGETS = 'C:\\Program Files (x86)\\MSBuild\\Microsoft.Cpp\\v4.0\\V120\\';
const TAGS = new Set(('Project ItemGroup ProjectConfiguration Configuration Platform PropertyGroup ProjectGuid WindowsTargetPlatformVersion Import ConfigurationType PlatformToolset UseOfMfc CharacterSet ImportGroup _ProjectFileVersion OutDir IntDir LinkIncremental ItemDefinitionGroup Midl PreprocessorDefinitions MkTypLibCompatible SuppressStartupBanner TargetEnvironment TypeLibraryName HeaderFileName ClCompile Optimization AdditionalIncludeDirectories BasicRuntimeChecks RuntimeLibrary PrecompiledHeader PrecompiledHeaderFile PrecompiledHeaderOutputFile AssemblerListingLocation ObjectFileName ProgramDataBaseFileName WarningLevel DebugInformationFormat ResourceCompile Culture Link AdditionalDependencies OutputFile AdditionalLibraryDirectories GenerateDebugInformation ProgramDatabaseFile ImportLibrary TargetMachine AdditionalOptions Bscmake BscMake InlineFunctionExpansion StringPooling FunctionLevelLinking ClInclude None ResourceOutputFileName TargetName TargetExt').split(' '));
const IMPORTS = new Set(['$(VCTargetsPath)\\Microsoft.Cpp.Default.props', '$(VCTargetsPath)\\Microsoft.Cpp.props',
  '$(VCTargetsPath)Microsoft.CPP.UpgradeFromVC60.props', '$(VCTargetsPath)\\Microsoft.Cpp.targets',
  '$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props'].map((name) => name.toLowerCase()));
const OUTPUTS = new Set(['OutDir', 'IntDir', 'OutputFile', 'TypeLibraryName', 'HeaderFileName', 'PrecompiledHeaderOutputFile',
  'AssemblerListingLocation', 'ObjectFileName', 'ProgramDataBaseFileName', 'ProgramDatabaseFile', 'ImportLibrary', 'ResourceOutputFileName']);
function fail(message) { throw new Error(`training compile: ${message}`); }
function safe(root, value, required = false) {
  if (typeof value !== 'string' || !value) fail('path is required');
  const file = path.resolve(root, value);
  const relative = path.relative(root, file);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) fail(`path escapes training run: ${value}`);
  let cursor = file;
  while (true) {
    const part = path.basename(cursor);
    if (part && (/[. ]$/.test(part) || /[<>:"|?*]/.test(part) || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)/i.test(part))) fail('unsafe Windows path');
    try {
      const stat = fs.lstatSync(cursor);
      if (stat.isSymbolicLink() || (stat.isFile() && stat.nlink !== 1)) fail(`links are forbidden: ${cursor}`);
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = path.dirname(cursor); if (parent === cursor) break; cursor = parent;
  }
  if (required && !fs.statSync(file).isFile()) fail(`file is missing: ${file}`);
  return file;
}
function privateTree(root, directory) {
  safe(root, directory);
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const file = safe(root, path.join(directory, entry.name));
    if (entry.isDirectory()) privateTree(root, file);
    else if (!entry.isFile()) fail('unsupported project entry');
  }
}
function textXml(value) {
  if (/&(?!amp;|lt;|gt;|quot;|apos;)/.test(value)) fail('unsupported XML entity');
  return value.replace(/&(amp|lt|gt|quot|apos);/g, (_, name) => ({ amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" })[name]);
}
function parseProject(xml) {
  if (/<!DOCTYPE|<!ENTITY|<!\[CDATA\[/i.test(xml)) fail('DTD/entities/CDATA are forbidden');
  xml = xml.replace(/^\uFEFF/, '').replace(/^\s*<\?xml\s[^?]*\?>/, '').replace(/<!--[\s\S]*?-->/g, '');
  const tokens = xml.match(/<[^>]*>|[^<]+/g) ?? [];
  const stack = []; const nodes = []; let rootCount = 0;
  for (const token of tokens) {
    if (!token.startsWith('<')) {
      if (!stack.length && token.trim()) fail('text outside XML root');
      if (stack.length) stack.at(-1).text += textXml(token);
      continue;
    }
    const closing = /^<\/([A-Za-z_][A-Za-z0-9._]*)\s*>$/.exec(token);
    if (closing) { if (stack.pop()?.name !== closing[1]) fail('unbalanced XML'); continue; }
    const match = /^<([A-Za-z_][A-Za-z0-9._]*)(\s[^<>]*?)?\s*(\/?)>$/.exec(token);
    if (!match || !TAGS.has(match[1])) fail(`unapproved project element: ${token.slice(0, 80)}`);
    const attributes = {}; let rest = match[2] ?? '';
    while (rest.trim()) {
      const attribute = /^\s+([A-Za-z][A-Za-z0-9.:]*)\s*=\s*("[^"]*"|'[^']*')/.exec(rest);
      if (!attribute || Object.hasOwn(attributes, attribute[1])) fail('invalid XML attribute');
      attributes[attribute[1]] = textXml(attribute[2].slice(1, -1)); rest = rest.slice(attribute[0].length);
    }
    if (Object.keys(attributes).some((key) => !['Include', 'Condition', 'Label', 'Project', 'DefaultTargets', 'ToolsVersion', 'xmlns'].includes(key))) fail('unapproved project attribute');
    const node = { name: match[1], attributes, text: '', parent: stack.at(-1)?.name ?? null };
    if (!stack.length && (++rootCount !== 1 || node.name !== 'Project')) fail('invalid XML project root');
    nodes.push(node); if (!match[3]) stack.push(node);
  }
  if (stack.length || rootCount !== 1) fail('unbalanced XML');
  return nodes;
}

function expand(value, directory, config) {
  const properties = { ProjectDir: `${directory}${path.sep}`, MSBuildProjectDirectory: directory,
    Configuration: config, Platform: 'Win32' };
  const expanded = value.replace(/\$\(([^)]+)\)/g, (whole, key) => properties[key] ?? whole);
  if (/[\$%@]/.test(expanded)) fail(`unresolved path expression: ${value}`);
  return expanded.replace(/\\/g, path.sep);
}

/** Inspect only. An explicit vcxproj is required; solution files can hide more projects. */
export function inspectTrainingCompile({ workspaceRoot, runId, vsProjectRoot, projectFile, source, report,
  configurations = ['Release', 'Debug'] }) {
  if (typeof runId !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(runId)) fail('invalid runId');
  const workspace = path.resolve(workspaceRoot);
  const runRoot = safe(workspace, `Training_Materials/runs/${runId}`);
  const contextFile = safe(runRoot, 'run.json', true);
  const context = JSON.parse(fs.readFileSync(contextFile, 'utf8'));
  if (context.runId !== runId || context.mode !== 'training' || context.releaseId !== null || context.projectId !== null
    || path.resolve(workspace, context.artifactRoot) !== runRoot) fail('not a matching isolated training identity');
  const projectRoot = safe(runRoot, vsProjectRoot);
  privateTree(runRoot, projectRoot);
  const project = safe(projectRoot, projectFile, true);
  const sourceFile = safe(projectRoot, source, true);
  if (!project.toLowerCase().endsWith('.vcxproj') || !sourceFile.toLowerCase().endsWith('.cpp')) fail('explicit vcxproj and cpp source required');
  const reportFile = safe(runRoot, report);
  if (!reportFile.toLowerCase().endsWith('.json') || fs.existsSync(reportFile)) fail('report must be a new run-local JSON file');
  if (!Array.isArray(configurations) || !configurations.length || new Set(configurations).size !== configurations.length
    || configurations.some((config) => !['Release', 'Debug'].includes(config))) fail('unsupported configurations');
  const projectBytes = fs.readFileSync(project);
  const nodes = parseProject(projectBytes.toString('utf8'));
  const directory = path.dirname(project);
  let hasTargets = false;
  const compiledSources = new Set();
  for (const node of nodes) {
    const value = node.text.trim();
    if (/\$\(\[|\$\([^)]*::/.test(value + Object.values(node.attributes).join(''))) fail('MSBuild property functions are forbidden');
    if (node.name === 'Import') {
      const imported = node.attributes.Project?.toLowerCase();
      if (!IMPORTS.has(imported)) fail(`unapproved MSBuild import: ${node.attributes.Project}`);
      if (imported.endsWith('microsoft.cpp.targets')) hasTargets = true;
    }
    if (node.name === 'PlatformToolset' && value !== 'v120') fail('only the installed v120 toolset is approved; no auto-fix');
    if (node.name === 'ConfigurationType' && value !== 'DynamicLibrary') fail('training build must be a DLL, never an executable');
    if (node.name === 'AdditionalOptions' && value && value !== '/SAFESEH:NO') fail('unapproved raw compiler/linker options');
    if (OUTPUTS.has(node.name) && value) for (const config of configurations) safe(runRoot, path.resolve(directory, expand(value, directory, config)));
    if (['ClCompile', 'ClInclude', 'None'].includes(node.name) && node.attributes.Include) {
      if (node.attributes.Condition) fail('conditional source membership is not approved');
      const included = node.attributes.Include;
      if (/[;*?]/.test(included)) fail('wildcard/project item list is not approved');
      const includedFile = safe(projectRoot, path.resolve(directory, expand(included, directory, configurations[0])), true);
      if (node.name === 'ClCompile') compiledSources.add(includedFile.toLowerCase());
    }
  }
  if (!hasTargets || !nodes.some((node) => node.name === 'ConfigurationType') || !nodes.some((node) => node.name === 'PlatformToolset')) fail('incomplete native C++ project');
  if (!compiledSources.has(sourceFile.toLowerCase())) fail('reported source is not a participating ClCompile item');
  return { runRoot, projectRoot, project, source: sourceFile, report: reportFile, configurations: [...configurations],
    sourceSha256: sha256Bytes(fs.readFileSync(sourceFile)), projectSha256: sha256Bytes(projectBytes) };
}

const xml = (value) => value.replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' })[char]);
function overlay(output, intermediate, artifact) {
  const out = xml(`${output}${path.sep}`); const temp = xml(`${intermediate}${path.sep}`);
  return `<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003"><PropertyGroup><OutDir>${out}</OutDir><IntDir>${temp}</IntDir></PropertyGroup><ItemDefinitionGroup><ClCompile><ObjectFileName>${temp}</ObjectFileName><ProgramDataBaseFileName>${temp}compiler.pdb</ProgramDataBaseFileName><PrecompiledHeaderOutputFile>${temp}training.pch</PrecompiledHeaderOutputFile><AssemblerListingLocation>${temp}</AssemblerListingLocation></ClCompile><Link><OutputFile>${xml(artifact)}</OutputFile><ProgramDatabaseFile>${out}training.pdb</ProgramDatabaseFile><ImportLibrary>${out}training.lib</ImportLibrary><RegisterOutput>false</RegisterOutput></Link><Bscmake><OutputFile>${temp}training.bsc</OutputFile></Bscmake><Midl><TypeLibraryName>${temp}training.tlb</TypeLibraryName></Midl><ResourceCompile><ResourceOutputFileName>${temp}training.res</ResourceOutputFileName></ResourceCompile></ItemDefinitionGroup></Project>\n`;
}
function capture(child) {
  let stdout = ''; let stderr = '';
  child.stdout?.on('data', (data) => { stdout = (stdout + data.toString()).slice(-64_000); });
  child.stderr?.on('data', (data) => { stderr = (stderr + data.toString()).slice(-64_000); });
  const closed = new Promise((resolve) => {
    child.once('error', (error) => resolve({ exitCode: null, error: error.message, closed: false }));
    child.once('close', (code, signal) => resolve({ exitCode: code, signal, closed: true }));
  });
  return { closed, logs: () => ({ stdout, stderr }) };
}
async function bounded(promise, ms, fallback) {
  let timer;
  try { return await Promise.race([promise, new Promise((resolve) => { timer = setTimeout(() => resolve(fallback), ms); })]); }
  finally { clearTimeout(timer); }
}

/**
 * Build only an already-prepared private project. Adapters may inject spawn for
 * lifecycle tests; real execution always uses fixed MSBuild/taskkill binaries.
 * This writes only fresh build-control/output/report files under the run root.
 * No fast_rebuild, DTE, toolset rewrites, DLL loading or hardware calls occur.
 */
export async function compileTrainingProject(options, { spawn = nativeSpawn, signal, timeoutMs = 30_000 } = {}) {
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0 || timeoutMs > 30_000) fail('build budget must be at most 30 seconds');
  const checked = inspectTrainingCompile(options);
  const startedAt = Date.now();
  const evidence = { schemaVersion: 1, runId: options.runId, stage: 'COMPILE', mode: 'training',
    status: 'blocked', startedAt: new Date(startedAt).toISOString(), source: checked.source,
    sourceSha256: checked.sourceSha256, project: checked.project, projectSha256: checked.projectSha256,
    commands: [], artifacts: [], reason: null };
  const controlRoot = safe(checked.runRoot, `compile/build-${randomUUID()}`);
  fs.mkdirSync(controlRoot, { recursive: true });
  const propsRoot = path.join(controlRoot, 'user-props');
  fs.mkdirSync(propsRoot);
  fs.writeFileSync(path.join(propsRoot, 'Microsoft.Cpp.Win32.user.props'), '<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003" />\n', { flag: 'wx' });
  try {
    for (const configuration of checked.configurations) {
      if (signal?.aborted) throw new Error('build cancelled before command');
      const remaining = timeoutMs - (Date.now() - startedAt);
      if (remaining <= 0) throw new Error('build deadline exceeded');
      const output = safe(checked.runRoot, path.join(controlRoot, configuration, 'out'));
      const intermediate = safe(checked.runRoot, path.join(controlRoot, configuration, 'obj'));
      fs.mkdirSync(output, { recursive: true }); fs.mkdirSync(intermediate, { recursive: true });
      const artifact = path.join(output, 'training.dll');
      const controlFile = path.join(controlRoot, `${configuration}.targets`);
      fs.writeFileSync(controlFile, overlay(output, intermediate, artifact), { flag: 'wx' });
      const args = [checked.project, '/t:Build', '/m:1', '/nodeReuse:false', '/v:minimal', '/nologo',
        `/p:Configuration=${configuration}`, '/p:Platform=Win32', `/p:VCTargetsPath=${VC_TARGETS}`,
        `/p:UserRootDir=${propsRoot}${path.sep}`, `/p:ForceImportAfterCppTargets=${controlFile}`,
        '/p:ForceImportBeforeCppTargets=', `/p:OutDir=${output}${path.sep}`, `/p:IntDir=${intermediate}${path.sep}`,
        `/p:TargetPath=${artifact}`, '/p:TargetName=training', '/p:TargetExt=.dll', '/p:RegisterOutput=false'];
      const command = { executable: TRAINING_MSBUILD, args, configuration, startedAt: new Date().toISOString(), expectedArtifact: artifact };
      evidence.commands.push(command);
      const environment = Object.fromEntries(['SystemRoot', 'WINDIR', 'PATH', 'PATHEXT', 'COMSPEC', 'TEMP', 'TMP', 'ProgramFiles', 'ProgramFiles(x86)']
        .filter((key) => process.env[key]).map((key) => [key, process.env[key]]));
      environment.TEMP = intermediate; environment.TMP = intermediate;
      const child = spawn(TRAINING_MSBUILD, args, { cwd: path.dirname(checked.project), shell: false, windowsHide: true, env: environment });
      const captured = capture(child);
      let timer; let abortHandler;
      const abort = new Promise((resolve) => {
        abortHandler = () => resolve({ stop: 'cancelled' });
        signal?.addEventListener('abort', abortHandler, { once: true });
        if (signal?.aborted) abortHandler();
        timer = setTimeout(() => resolve({ stop: 'timeout' }), remaining);
      });
      let result;
      try { result = await Promise.race([captured.closed, abort]); }
      finally { clearTimeout(timer); signal?.removeEventListener('abort', abortHandler); }
      if (result.stop) {
        const termination = { requested: true, pid: child.pid, confirmed: false };
        command.termination = termination;
        if (Number.isSafeInteger(child.pid) && child.pid > 0) {
          const killArgs = ['/PID', String(child.pid), '/T', '/F'];
          termination.command = { executable: TASKKILL, args: killArgs };
          try {
            const killer = capture(spawn(TASKKILL, killArgs, { shell: false, windowsHide: true }));
            const killed = await bounded(killer.closed, 5_000, { closed: false, exitCode: null, error: 'taskkill confirmation timed out' });
            Object.assign(termination, { ...killed, ...killer.logs() });
            const stopped = await bounded(captured.closed, 2_000, { closed: false });
            termination.buildClosed = stopped.closed;
            termination.confirmed = killed.closed === true && killed.exitCode === 0 && stopped.closed === true;
          } catch (error) { termination.error = error.message; }
        }
        Object.assign(command, captured.logs(), { exitCode: null, stopped: result.stop });
        throw new Error(`${result.stop}; process tree termination ${termination.confirmed ? 'confirmed' : 'unconfirmed'}`);
      }
      Object.assign(command, result, captured.logs(), { finishedAt: new Date().toISOString() });
      if (!result.closed || result.exitCode !== 0) throw new Error(`MSBuild failed: ${result.error ?? result.exitCode}`);
      if (signal?.aborted) throw new Error('cancelled before artifact verification');
      const file = safe(checked.runRoot, artifact, true);
      const stat = fs.statSync(file);
      if (stat.size === 0 || stat.mtimeMs < Date.parse(command.startedAt)) throw new Error('missing or stale build artifact');
      evidence.artifacts.push({ configuration, path: file, size: stat.size, mtimeMs: stat.mtimeMs, sha256: sha256Bytes(fs.readFileSync(file)) });
    }
    safe(checked.runRoot, checked.source, true); safe(checked.runRoot, checked.project, true);
    if (sha256Bytes(fs.readFileSync(checked.source)) !== checked.sourceSha256
      || sha256Bytes(fs.readFileSync(checked.project)) !== checked.projectSha256) throw new Error('source/project changed during build');
    evidence.status = 'passed';
  } catch (error) { evidence.reason = error.message; }
  evidence.finishedAt = new Date().toISOString(); evidence.elapsedMs = Date.now() - startedAt;
  safe(checked.runRoot, checked.report);
  fs.mkdirSync(path.dirname(checked.report), { recursive: true });
  fs.writeFileSync(checked.report, `${JSON.stringify(evidence, null, 2)}\n`, { flag: 'wx' });
  return evidence;
}
