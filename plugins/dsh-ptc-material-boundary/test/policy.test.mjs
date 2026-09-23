import assert from 'node:assert/strict';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import test from 'node:test';
import { decision } from '../lib/policy.js';
import { createImplementationDescriptor } from '../lib/implementation-contract.js';
import { apply } from '../lib/index.js';
const root = path.resolve('D:/Newtest/DSH/ATE-Coding-Plat');
const schematic = { session: { header: { cwd: root }, events: [{ type: 'subagent/descriptor', data: { label: 'PTC schematic expert' } }] } };
const dft = { session: { header: { cwd: root }, events: [{ type: 'subagent/descriptor', data: { label: 'PTC dft expert [TM106,TM108,TM425]' } }] } };
const unscopedDft = { session: { header: { cwd: root }, events: [{ type: 'subagent/descriptor', data: { label: 'PTC dft expert' } }] } };
const call = (name, arguments_, agent) => ({ name, arguments: arguments_, agent });
const implLabel = createImplementationDescriptor(root, 'team/artifacts/tm425-ptc/method/tm425-test-method-contract.json');
const implementer = { session: { header: { cwd: root }, events: [{ type: 'subagent/descriptor', data: { label: implLabel } }] } };
const dftOut = (tm, file = 'dft-meta.json') => path.join(root, 'project', 'DALI', 'Output_Global_Material', 'dft', tm, file);
test('DFT reads canonical workbook and only assigned output', () => { assert.equal(decision(call('read', { file_path: path.join(root, 'project','DALI','Input_GlobalMaterial','Dali_testmode.xlsx') }, dft), root), undefined); assert.equal(decision(call('read', { file_path: dftOut('TM106') }, dft), root), undefined); assert.match(decision(call('read', { file_path: dftOut('TM110') }, dft), root), /PTC material boundary/); assert.match(decision(call('read', { file_path: path.join(root,'project','DALI','schematic-ir.json') }, dft), root), /PTC material boundary/); });
test('DFT write and shell scope are enforced', () => { assert.equal(decision(call('write', { file_path: dftOut('TM425','dft-semantic-review.json') }, dft), root), undefined); assert.match(decision(call('write', { file_path: dftOut('TM109') }, dft), root), /PTC material boundary/); const cmd='python scripts/refresh_dft_meta_from_source.py --source project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx --tm TM106 --meta project/DALI/Output_Global_Material/dft/TM106/dft-meta.json --expected-sha 896770d29f8ae58852e1031c1e6210c5435e52df38e0f6a0fb8fc1836622c04b'; assert.equal(decision(call('pwsh',{command:cmd},dft),root),undefined); assert.match(decision(call('pwsh',{command:'python scripts/validate_dft_outputs.py --tm TM110'},dft),root),/PTC material boundary/); });
test('unscoped DFT is denied', () => assert.match(decision(call('read',{file_path:dftOut('TM106')},unscopedDft),root),/PTC material boundary/));
test('schematic reads only canonical source and self output', () => { const map=path.join(root,'project','DALI','Output_Global_Material','schematic','SCH-Connect-Map.json'); assert.equal(decision(call('read',{file_path:path.join(root,'project','DALI','Input_GlobalMaterial','Dali-SCH.csv')},schematic),root),undefined); assert.equal(decision(call('read',{file_path:map},schematic),root),undefined); assert.match(decision(call('read',{file_path:dftOut('TM106')},schematic),root),/PTC material boundary/); });
test('pre-execute denies before execution', () => {
  // The fake context mirrors the real one closely enough for `apply()`: it
  // registers pre-execute handlers AND the monotonic guard the plugin now mounts
  // (a fake that silently dropped `tools.guard` would hide that registration).
  let handler;
  const guards = [];
  const guarded = { on: (_name, fn) => { handler = fn; }, tools: { guard: (fn) => { guards.push(fn); return () => {}; } }, logger: { info() {} } };
  apply(guarded, { workspaceRoot: root });
  let called = false;
  const r = handler(call('read', { file_path: dftOut('TM110') }, dft), () => { called = true; return { kind: 'allow' }; });
  assert.equal(r.kind, 'deny');
  assert.equal(called, false);
  assert.equal(guards.length, 1, 'the plugin must also register one monotonic guard');
  assert.match(guards[0](call('read', { file_path: dftOut('TM110') }, dft)), /PTC material boundary/);
  assert.equal(guards[0](call('read', { file_path: dftOut('TM106') }, dft)), undefined);
});

test('implementation Hook accepts only a complete signed recipe and formal sources', () => {
  const contract = path.join(root, 'team', 'artifacts', 'tm425-ptc', 'method', 'tm425-test-method-contract.json');
  const testCpp = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp';
  assert.equal(decision(call('read', { file_path: contract }, implementer), root), undefined);
  assert.equal(decision(call('read', { file_path: testCpp }, implementer), root), undefined);
  assert.match(decision(call('read', { file_path: path.join(root, 'team', 'CURRENT_STATUS.md') }, implementer), root), /current signed method contract/);
  assert.match(decision(call('glob', { pattern: '**/*' }, implementer), root), /directory enumeration/);
  assert.match(decision(call('read', { file_path: path.join(root, 'team', 'artifacts', 'tm106-ptc', 'method', 'tm106-test-method-contract.json') }, implementer), root), /current signed method contract/);
  assert.equal(decision(call('write', { file_path: testCpp, content: '// tool policy test only' }, implementer), root), undefined);
  assert.equal(decision(call('pwsh', { command: 'python scripts/verify_implementation_batch.py team/artifacts/tm425-ptc' }, implementer), root), undefined);
});
test('implementation Hook rejects an unsiged generic dispatch', () => {
  const generic = { session: { header: { cwd: root }, events: [{ type: 'subagent/descriptor', data: { label: 'ate-implementer' } }] } };
  assert.match(decision(call('read', { file_path: 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp' }, generic), root), /missing Hook-generated contract recipe/);
});
test('implementation dispatch requires the Hook-generated recipe descriptor', () => {
  assert.match(decision(call('subagent', { description: 'ate-implementer', prompt: 'Read team/roles/ate-implementer.md' }, schematic), root), /Hook-generated/);
  assert.equal(decision(call('subagent', { description: implLabel, prompt: 'Read team/roles/ate-implementer.md' }, schematic), root), undefined);
});

test('DFT reads [31] reference materials but cannot write them', () => {
  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'dft-refs-'));
  try {
    const mk = (rel, content = 'x') => { const p = path.join(tmpRoot, rel); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, content, 'utf8'); return p; };
    const reg = mk(path.join('project', 'DALI', 'reg_config', 'boost_300.sv'));
    const sch = mk(path.join('project', 'DALI', 'Output_Global_Material', 'schematic', 'SCH-Connect-Map.json'));
    const special = mk(path.join('project', 'DALI', 'Input_GlobalMaterial', 'DALI-special-information.json'));
    const manual = mk(path.join('User_input', 'rule.txt'));
    const cbit = mk(path.join('project', 'DALI', 'Input_GlobalMaterial', 'CBIT表-DALI.xlsx'));
    const schSrc = mk(path.join('project', 'DALI', 'Input_GlobalMaterial', 'Dali-SCH.csv'));
    const dftLocal = { session: { header: { cwd: tmpRoot }, events: [{ type: 'subagent/descriptor', data: { label: 'PTC dft expert [TM106,TM108,TM425]' } }] } };
    assert.equal(decision(call('read', { file_path: reg }, dftLocal), tmpRoot), undefined);
    assert.equal(decision(call('read', { file_path: sch }, dftLocal), tmpRoot), undefined);
    assert.equal(decision(call('read', { file_path: special }, dftLocal), tmpRoot), undefined);
    assert.equal(decision(call('read', { file_path: manual }, dftLocal), tmpRoot), undefined);
    assert.match(decision(call('write', { file_path: reg }, dftLocal), tmpRoot), /PTC material boundary/);
    assert.match(decision(call('write', { file_path: sch }, dftLocal), tmpRoot), /PTC material boundary/);
    assert.match(decision(call('read', { file_path: cbit }, dftLocal), tmpRoot), /PTC material boundary/);
    assert.match(decision(call('read', { file_path: schSrc }, dftLocal), tmpRoot), /PTC material boundary/);
  } finally { fs.rmSync(tmpRoot, { recursive: true, force: true }); }
});
