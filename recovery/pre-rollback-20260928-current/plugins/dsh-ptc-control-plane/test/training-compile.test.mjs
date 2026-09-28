import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { EventEmitter } from 'node:events';
import test from 'node:test';
import { createRunContext, persistRunContext } from '../lib/run-context.js';
import { compileTrainingProject, inspectTrainingCompile, TRAINING_MSBUILD } from '../lib/training-compile.js';

const projectXml = `<Project DefaultTargets="Build" ToolsVersion="12.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />
<PropertyGroup><_ProjectFileVersion>12.0.30501.0</_ProjectFileVersion><ConfigurationType>DynamicLibrary</ConfigurationType><PlatformToolset>v120</PlatformToolset><OutDir>../</OutDir><IntDir>.\\$(Configuration)\\</IntDir></PropertyGroup>
<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />
<Import Project="$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props" />
<ItemDefinitionGroup><Link><OutputFile>..\\F12011.dll</OutputFile></Link><ClCompile><ObjectFileName>.\\$(Configuration)\\</ObjectFileName></ClCompile></ItemDefinitionGroup>
<ItemGroup><ClCompile Include="test.cpp" /><ClCompile Include="sub.cpp" /><None Include="..\\NU1201.treg" /></ItemGroup>
<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />
</Project>`;
function fixture(t, xml = projectXml) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-compile-test-'));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const context = createRunContext(workspaceRoot, { mode: 'training', runId: 'training-compile-fixture' });
  persistRunContext(workspaceRoot, context);
  const runRoot = path.join(workspaceRoot, context.artifactRoot);
  const vsProjectRoot = path.join(runRoot, 'vs-project');
  const sourceRoot = path.join(vsProjectRoot, 'source');
  fs.mkdirSync(sourceRoot, { recursive: true });
  const projectFile = path.join(sourceRoot, 'F12011.vcxproj');
  fs.writeFileSync(projectFile, xml);
  const source = path.join(sourceRoot, 'test.cpp');
  fs.writeFileSync(source, 'int fixture_test() { return 0; }');
  fs.writeFileSync(path.join(sourceRoot, 'sub.cpp'), 'void fixture_sub() {}');
  fs.writeFileSync(path.join(vsProjectRoot, 'NU1201.treg'), '[fixture]');
  return { workspaceRoot, runId: context.runId, runRoot, vsProjectRoot, projectFile, source,
    report: path.join(runRoot, 'verification/build-report.json'), configurations: ['Release'] };
}
function child(pid = 4242) {
  const result = new EventEmitter(); result.pid = pid;
  result.stdout = new EventEmitter(); result.stderr = new EventEmitter();
  return result;
}
function fakeBuild({ artifact = true, exitCode = 0, stale = false, alterSource } = {}) {
  const calls = [];
  const spawn = (executable, args, options) => {
    calls.push({ executable, args, options });
    const process = child();
    queueMicrotask(() => {
      if (artifact) {
        const target = args.find((arg) => arg.startsWith('/p:TargetPath=')).slice('/p:TargetPath='.length);
        fs.writeFileSync(target, Buffer.from('fixture DLL bytes'));
        if (stale) fs.utimesSync(target, new Date(0), new Date(0));
      }
      if (alterSource) fs.appendFileSync(alterSource, '\nchanged during compilation');
      process.stdout.emit('data', Buffer.from('fixture msbuild output'));
      process.stderr.emit('data', Buffer.from(exitCode ? 'fixture compiler error' : ''));
      process.emit('close', exitCode, null);
    });
    return process;
  };
  return { spawn, calls };
}

test('fixed native MSBuild build uses private outputs and records fresh exact-byte evidence', async (t) => {
  const f = fixture(t);
  const original = fs.readFileSync(f.projectFile);
  const fake = fakeBuild();
  const result = await compileTrainingProject(f, fake);
  assert.equal(result.status, 'passed');
  assert.equal(result.artifacts.length, 1);
  assert.match(result.artifacts[0].sha256, /^[a-f0-9]{64}$/);
  assert.ok(result.artifacts[0].path.startsWith(f.runRoot));
  assert.equal(fake.calls.length, 1);
  const call = fake.calls[0];
  assert.equal(call.executable, TRAINING_MSBUILD);
  assert.ok(call.args.includes('/nodeReuse:false'));
  assert.ok(call.args.includes('/m:1'));
  assert.equal(call.options.shell, false);
  assert.equal(call.options.windowsHide, true);
  assert.ok(call.options.env.TEMP.startsWith(f.runRoot));
  const overlayPath = call.args.find((arg) => arg.startsWith('/p:ForceImportAfterCppTargets=')).split('=').slice(1).join('=');
  const overlay = fs.readFileSync(overlayPath, 'utf8');
  assert.match(overlay, /<RegisterOutput>false<\/RegisterOutput>/);
  assert.ok(overlay.includes(result.artifacts[0].path));
  assert.deepEqual(fs.readFileSync(f.projectFile), original, 'never rewrite project or toolset');
  assert.equal(JSON.parse(fs.readFileSync(f.report)).status, 'passed');
});

test('forbidden task/event/import/property function/toolset is rejected before spawning', async (t) => {
  const additions = ['<Exec Command="evil" />', '<UsingTask TaskName="evil" AssemblyFile="evil.dll" />',
    '<PreBuildEvent><Command>evil</Command></PreBuildEvent>', '<PostBuildEvent />',
    '<Import Project="D:\\production\\evil.targets" />', '<PropertyGroup><OutDir>$([System.IO.Path]::GetTempPath())</OutDir></PropertyGroup>',
    '<PropertyGroup><PlatformToolset>v143</PlatformToolset></PropertyGroup>', '<Target Name="Build" />'];
  for (const addition of additions) {
    const f = fixture(t, projectXml.replace('</Project>', `${addition}</Project>`));
    const fake = fakeBuild();
    await assert.rejects(compileTrainingProject(f, fake));
    assert.equal(fake.calls.length, 0);
  }
});

test('project inputs and every declared output must remain inside private project/run', async (t) => {
  for (const value of ['../../../../production.dll', 'D:\\PROJECT6-DALI\\production.dll', '$(UntrustedOutput)\\evil.dll']) {
    const f = fixture(t, projectXml.replace('..\\F12011.dll', value));
    await assert.rejects(compileTrainingProject(f, fakeBuild()), /escapes|unresolved/);
  }
  const f = fixture(t);
  await assert.rejects(compileTrainingProject({ ...f, report: path.join(f.workspaceRoot, 'outside.json') }, fakeBuild()), /escapes/);
  const contextPath = path.join(f.runRoot, 'run.json');
  const context = JSON.parse(fs.readFileSync(contextPath)); context.mode = 'delivery';
  fs.writeFileSync(contextPath, JSON.stringify(context));
  assert.throws(() => inspectTrainingCompile(f), /training identity/);
});

test('source and project-tree hardlinks or junctions are rejected', (t) => {
  const f = fixture(t);
  const target = path.join(f.vsProjectRoot, 'hardlink.cpp');
  fs.linkSync(f.source, target);
  assert.throws(() => inspectTrainingCompile(f), /links are forbidden/);
  fs.unlinkSync(target);
  const link = path.join(f.vsProjectRoot, 'linked');
  fs.symlinkSync(path.dirname(f.source), link, process.platform === 'win32' ? 'junction' : 'dir');
  assert.throws(() => inspectTrainingCompile(f), /links are forbidden/);
});

test('nonzero exit and missing or stale DLL cannot become successful evidence', async (t) => {
  for (const options of [{ exitCode: 1 }, { artifact: false }, { stale: true }]) {
    const f = fixture(t);
    const result = await compileTrainingProject(f, fakeBuild(options));
    assert.equal(result.status, 'blocked');
    assert.equal(result.commands.length, 1);
    assert.equal(result.commands[0].stdout, 'fixture msbuild output');
    if (options.exitCode) assert.equal(result.commands[0].stderr, 'fixture compiler error');
    assert.equal(JSON.parse(fs.readFileSync(f.report)).status, 'blocked');
  }
});

test('source changed during build invalidates success even with new DLL', async (t) => {
  const f = fixture(t);
  const result = await compileTrainingProject(f, fakeBuild({ alterSource: f.source }));
  assert.equal(result.status, 'blocked');
  assert.match(result.reason, /changed during build/);
});

test('deadline terminates exact Windows process tree and records confirmation', async (t) => {
  const f = fixture(t);
  const calls = []; let build;
  const spawn = (exe, args) => {
    calls.push({ exe, args });
    if (exe === TRAINING_MSBUILD) { build = child(7890); return build; }
    const killer = child(9876);
    queueMicrotask(() => { build.emit('close', 1); killer.emit('close', 0); });
    return killer;
  };
  // The deadline must expire after setup reaches the fake MSBuild child, even
  // when the full Windows suite is contending for filesystem time.
  const result = await compileTrainingProject(f, { spawn, timeoutMs: 3000 });
  assert.equal(result.status, 'blocked');
  assert.equal(result.commands[0].stopped, 'timeout');
  assert.equal(result.commands[0].termination.confirmed, true);
  assert.deepEqual(calls[1].args, ['/PID', '7890', '/T', '/F']);
  assert.equal(calls[1].exe, 'C:\\Windows\\System32\\taskkill.exe');
});

test('cancelled command with failed taskkill is blocked and explicitly unconfirmed', async (t) => {
  const f = fixture(t); const abort = new AbortController(); let build;
  const spawn = (exe) => {
    if (exe === TRAINING_MSBUILD) { build = child(); queueMicrotask(() => abort.abort()); return build; }
    const killer = child(2222);
    queueMicrotask(() => { build.emit('close', 1); killer.stderr.emit('data', Buffer.from('access denied')); killer.emit('close', 1); });
    return killer;
  };
  const result = await compileTrainingProject(f, { spawn, signal: abort.signal });
  assert.equal(result.status, 'blocked');
  assert.equal(result.commands[0].termination.confirmed, false);
  assert.match(result.reason, /unconfirmed/);
  assert.equal(result.commands[0].termination.stderr, 'access denied');
});

test('already cancelled build never spawns and report IDs are never overwritten', async (t) => {
  const f = fixture(t); const abort = new AbortController(); abort.abort();
  const fake = fakeBuild();
  const result = await compileTrainingProject(f, { ...fake, signal: abort.signal });
  assert.equal(result.status, 'blocked'); assert.equal(fake.calls.length, 0);
  const before = fs.readFileSync(f.report);
  await assert.rejects(compileTrainingProject(f, fake), /new run-local JSON/);
  assert.deepEqual(fs.readFileSync(f.report), before);
});

test('spawn errors are retained and unrelated cpp cannot be reported as built', async (t) => {
  const f = fixture(t);
  const result = await compileTrainingProject(f, { spawn: () => { const process = child(); queueMicrotask(() => process.emit('error', new Error('MSBuild unavailable'))); return process; } });
  assert.equal(result.status, 'blocked'); assert.match(result.reason, /MSBuild unavailable/);
  const other = path.join(f.vsProjectRoot, 'other.cpp'); fs.writeFileSync(other, 'int other;');
  assert.throws(() => inspectTrainingCompile({ ...f, report: path.join(f.runRoot, 'verification/other.json'), source: other }), /not a participating/);
});
