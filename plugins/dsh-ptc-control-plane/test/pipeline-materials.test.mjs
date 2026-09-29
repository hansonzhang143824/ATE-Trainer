import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { preparePipelineMaterials } from '../lib/pipeline-materials.js';
import { TRAINING_POLICY_FILES } from '../lib/training-materials.js';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
function write(root, name, bytes) { const file = path.join(root, name); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, bytes); return file; }
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-pipeline-materials-'));
  const external = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-approved-vs-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  t.after(() => fs.rmSync(external, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, 'scripts'));
  for (const policy of TRAINING_POLICY_FILES) write(root, policy, `# fixture ${policy}\n`);
  for (const name of ['hash_ate_plaintext.py', 'material_plaintext_hash.py']) fs.copyFileSync(path.join(repo, 'scripts', name), path.join(root, 'scripts', name));
  write(root, 'scripts/project_info.py', "import hashlib,json\ndef inputs_digest(info):\n payload={k:info.get(k) for k in ['project','projectDir','roots','inputs']}\n return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()\n");
  const mapping = { 'dft-expert': 'ptc-dft-expert', 'schematic-expert': 'ptc-schematic-expert', 'test-strategy-architect': 'strategy-expert' };
  write(root, 'scripts/validate_expert_roster.py', `OWNER_PROFILE = ${JSON.stringify(mapping)}\n`);
  for (const [owner, profile] of Object.entries(mapping)) {
    write(root, `team/expert-profiles/${profile}/profile.yaml`, `id: ${profile}\nownerRole: ${owner}\n`);
    write(root, `team/expert-profiles/${profile}/instructions.md`, `draft ${profile}`);
    write(root, `team/expert-profiles/${profile}/cases/case.md`, 'draft case');
    write(root, `team/expert-profiles/${profile}/versions/v1/instructions.md`, 'published exclude');
  }
  const registry = { stateMachine: ['INPUT_SYNC', 'STRATEGY', 'COMPLETE'], stages: {
    INPUT_SYNC: { owner: 'captain', gate: 'scripts/prepare_input_sync_v2.py' }, STRATEGY: { owner: 'test-strategy-architect', gate: 'scripts/validate_strategy_contract.py' },
  } };
  write(root, 'team/ptc/ptc_stage_registry.json', JSON.stringify(registry));
  for (const stage of Object.values(registry.stages)) write(root, stage.gate, '# gate fixture');
  for (const [name, data] of Object.entries({ 'Dali_testmode.xlsx': 'DFT fixture', 'Dali-SCH.csv': 'PORT,pin\n1,A', 'CBIT表-DALI.xlsx': 'CBIT fixture', 'sch_confirmed.json': '{}', 'DALI-special-information.json': '{}' })) write(root, `Training_Materials/Input_GlobalMaterial/${name}`, data);
  write(root, 'User_input/DFT解析规则.txt', 'rules');
  write(root, 'knowledge/standards/treg.md', 'treg contract');
  write(root, 'knowledge/hardware/relays.md', 'relay rules');
  write(root, 'project/DALI/reg_config/tm109.sv', 'register declaration');
  for (const [name, data] of Object.entries({
    'source/F12011.vcxproj': '<Project><ItemGroup><ClCompile Include="test.cpp"/><None Include="..\\NU1201.spec"/><None Include="..\\NU1201.treg"/></ItemGroup></Project>',
    'source/F12011.sln': 'solution', 'source/test.cpp': 'void TM109() {}', 'source/StdAfx.h': '#pragma once',
    'source/Pin_Channel_define.h': '#define PIN_A 1', 'source/src/visa.lib': Buffer.from([0, 128, 255]),
    'source/src/visa.h': 'visa', 'source/debug/old.obj': 'exclude', 'source/old.bak': 'exclude',
    'source/old.dll': 'exclude', 'NU1201.spec': 'spec', 'NU1201.treg': 'treg', 'unapproved.txt': 'do not copy',
  })) write(external, name, data);
  const info = { schemaVersion: 2, project: 'DALI', projectDir: 'project/DALI',
    roots: { input: 'project/DALI/Input_GlobalMaterial', output: 'project/DALI/Output_Global_Material', errorLog: 'project/DALI/ErrorLog' },
    inputs: { dft: 'project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx', schematic: 'project/DALI/Input_GlobalMaterial/Dali-SCH.csv', cbit: 'project/DALI/Input_GlobalMaterial/CBIT表-DALI.xlsx', program: path.join(external, 'source') },
    approval: { approvedBy: 'fixture-user', approvedAt: '2026-09-22', inputsDigest: '' } };
  const infoFile = write(root, 'Project_Info.json', JSON.stringify(info));
  info.approval.inputsDigest = execFileSync('python', ['-X', 'utf8', '-c', "import json,runpy,sys; m=runpy.run_path(sys.argv[1]); print(m['inputs_digest'](json.load(open(sys.argv[2],encoding='utf-8'))))", path.join(root, 'scripts/project_info.py'), infoFile], { encoding: 'utf8', windowsHide: true, timeout: 30_000 }).trim();
  fs.writeFileSync(infoFile, JSON.stringify(info));
  write(root, 'project_config.json', JSON.stringify({ inputs: { channelmap: path.join(external, 'source/Pin_Channel_define.h') } }));
  return { root, external, info };
}

test('pipeline snapshot copies approved private sources, every draft owner and immutable VS baseline', async (t) => {
  const { root, external, info } = fixture(t);
  const original = fs.readFileSync(path.join(root, 'Project_Info.json'));
  const result = await preparePipelineMaterials(root, 'pipeline-one', ['TM109']);
  assert.equal(result.ownerProfiles['test-strategy-architect'], 'strategy-expert');
  assert.equal(result.trials.TM109, 'Training_Materials/runs/pipeline-one/trials/tm109');
  assert.equal(fs.existsSync(path.join(root, result.profileRoots['strategy-expert'], 'cases/case.md')), true);
  assert.equal(fs.existsSync(path.join(root, result.profileRoots['strategy-expert'], 'versions')), false);
  assert.deepEqual(fs.readFileSync(path.join(root, result.approvedProjectInfoPath)), original);
  assert.deepEqual(result.approvedConfiguration.approval, info.approval);
  assert.equal(JSON.parse(fs.readFileSync(path.join(root, result.projectInfoPath), 'utf8')).approval, undefined);
  assert.equal(fs.existsSync(path.join(root, result.programSourceRoot, 'debug')), false);
  assert.equal(fs.existsSync(path.join(root, result.programSourceRoot, 'old.dll')), false);
  assert.deepEqual(fs.readFileSync(path.join(root, result.programSourceRoot, 'src/visa.lib')), Buffer.from([0, 128, 255]));
  assert.equal(fs.readFileSync(path.join(root, result.vsProjectRoot, 'NU1201.spec'), 'utf8'), 'spec');
  assert.equal(fs.existsSync(path.join(root, result.vsProjectRoot, 'unapproved.txt')), false);
  const edited = path.join(root, result.programSourceRoot, 'test.cpp');
  fs.writeFileSync(edited, 'changed training implementation');
  assert.equal(fs.readFileSync(path.join(external, 'source/test.cpp'), 'utf8'), 'void TM109() {}');
  assert.equal(fs.readFileSync(path.join(root, result.immutableProgramSourceRoot, 'test.cpp'), 'utf8'), 'void TM109() {}');
  const independent = await preparePipelineMaterials(root, 'pipeline-two', ['TM109']);
  assert.equal(fs.readFileSync(path.join(root, independent.programSourceRoot, 'test.cpp'), 'utf8'), 'void TM109() {}');
  assert.notEqual(independent.programSourceRoot, result.programSourceRoot);
  const again = await preparePipelineMaterials(root, 'pipeline-one', ['TM109']);
  assert.equal(again.pipelineCacheKey, result.pipelineCacheKey);
  assert.equal(fs.readFileSync(edited, 'utf8'), 'changed training implementation');
  fs.writeFileSync(path.join(root, result.immutableProgramSourceRoot, 'test.cpp'), 'tampered baseline');
  await assert.rejects(preparePipelineMaterials(root, 'pipeline-one', ['TM109']), /snapshot changed/);
  assert.deepEqual(fs.readFileSync(path.join(root, 'Project_Info.json')), original);
});

test('reusing a bound pipeline resolves legacy draft profile revisions before identity comparison', async (t) => {
  const { root } = fixture(t);
  write(root, 'team/expert-profiles/ptc-dft-expert/profile.yaml', 'id: ptc-dft-expert\nownerRole: dft-expert\nexecutionClass: input-dft\nexecutionAdapter: ptc-dft\ncapabilityContract: ptc-dft-business-v1\n');
  const profileBindings = {
    'schematic-expert': { profileId: 'ptc-schematic-expert' },
    'dft-expert': { profileId: 'ptc-dft-expert' },
  };
  const workflowBinding = {
    workflowId: 'tm109-input-sync', workflowRevision: 'business-v1',
    steps: [
      { order: 1, role: 'schematic-expert', profileId: 'ptc-schematic-expert' },
      { order: 2, role: 'dft-expert', profileId: 'ptc-dft-expert' },
    ],
    handoff: 'schematic-output-to-dft-input',
  };
  const options = { profileBindings, workflowBinding };
  const first = await preparePipelineMaterials(root, 'pipeline-bound', ['TM109'], options);
  assert.deepEqual(first.profileRevisions, { 'dft-expert': 'draft', 'schematic-expert': 'draft' });
  const reused = await preparePipelineMaterials(root, 'pipeline-bound', ['TM109'], options);
  assert.equal(reused.pipelineCacheKey, first.pipelineCacheKey);
});

test('changed approval or owner mapping blocks snapshot without production writes', async (t) => {
  const { root, info } = fixture(t);
  info.inputs.program = path.join(root, 'unapproved');
  fs.writeFileSync(path.join(root, 'Project_Info.json'), JSON.stringify(info));
  await assert.rejects(preparePipelineMaterials(root, 'pipeline-unapproved', ['TM109']), /not approved|approval digest differs/);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/runs/pipeline-unapproved/vs-project')), false);
  const second = fixture(t);
  write(second.root, 'team/expert-profiles/strategy-expert/profile.yaml', 'ownerRole: wrong-owner');
  await assert.rejects(preparePipelineMaterials(second.root, 'pipeline-wrong-owner', ['TM109']), /ownerRole mismatch/);
});

test('copy limits, path traversal and external junctions fail closed', async (t) => {
  const { root, external } = fixture(t);
  await assert.rejects(preparePipelineMaterials(root, '../escape', ['TM109']), /invalid training run id/);
  await assert.rejects(preparePipelineMaterials(root, 'pipeline-limits', ['TM109'], { limits: { maxFiles: 2 } }), /count or total size limit/);
  fs.symlinkSync(path.join(root, 'knowledge'), path.join(external, 'source/linked'), process.platform === 'win32' ? 'junction' : 'dir');
  await assert.rejects(preparePipelineMaterials(root, 'pipeline-linked', ['TM109']), /link|junction/);
  assert.equal(fs.readFileSync(path.join(external, 'source/test.cpp'), 'utf8'), 'void TM109() {}');
});

test('missing project participating source blocks instead of claiming a complete VS copy', async (t) => {
  const { root, external } = fixture(t);
  write(external, 'source/F12011.vcxproj', '<Project><ItemGroup><ClCompile Include="missing.cpp"/></ItemGroup></Project>');
  await assert.rejects(preparePipelineMaterials(root, 'pipeline-incomplete-project', ['TM109']), /participating file was not safely copied/);
  assert.equal(fs.existsSync(path.join(root, 'Training_Materials/runs/pipeline-incomplete-project/pipeline-material-manifest.json')), false);
});
