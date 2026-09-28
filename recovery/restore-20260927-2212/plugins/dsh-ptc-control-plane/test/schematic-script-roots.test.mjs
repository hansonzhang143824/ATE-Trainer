import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const workspace = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const fixture = () => fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-schematic-roots-'));
function python(code) {
  const root = fixture();
  const output = execFileSync('python', ['-X', 'utf8', '-c', `${setup}\n${code}`, workspace, root], {
    cwd: root, encoding: 'utf8', windowsHide: true, timeout: 30_000,
  });
  assert.match(output, /PASS/);
}

const setup = String.raw`
import sys,json,hashlib,base64
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'scripts'))
import generate_schematic_txt as generator
import validate_schematic_outputs as validator
import training_schematic as training
import project_config_gate
root=Path(sys.argv[2]).resolve(); generator.ROOT=root; validator.ROOT=root; training.ROOT=root
run=root/'Training_Materials'/'runs'/'training-schematic-fixture'
inputs=run/'input'; out=run/'input-sync'/'schematic'; inputs.mkdir(parents=True); out.mkdir(parents=True)
source=inputs/'Dali-SCH.csv'; confirmed=inputs/'sch_confirmed.json'; cbit=inputs/'CBIT表-DALI.xlsx'
for file,content in [(source,b'PORT,pin,Capo,KELVIN\n'),(confirmed,b'{}'),(cbit,b'fixture-CBIT')]: file.write_bytes(content)
def digest(file): return hashlib.sha256(file.read_bytes()).hexdigest()
program=run/'vs-project'/'source'; program.mkdir(parents=True)
header=program/'Pin_Channel_define.h'; header.write_text('extern ACM200 FIXTURE;\n')
fixture_dft=inputs/'Dali_testmode.xlsx'; fixture_dft.write_bytes(b'fixture-DFT')
fixture_project=root/'fixture-project'; fixture_project.mkdir()
project_config=root/'project_config.json'
project_config.write_text(json.dumps({'project':'FIXTURE','project_dir':'fixture-project','inputs':{'dft':fixture_dft.relative_to(root).as_posix(),'csv_schematic':source.relative_to(root).as_posix(),'cbit':cbit.relative_to(root).as_posix(),'vs_src_dir':program.relative_to(root).as_posix()}}))
project_config_gate.approve('fixture',root,project_config)
config=run/'config'/'original-project_config.json'; config.parent.mkdir()
original_config=root/'production'/'project_config.json'; original_header=root/'production'/'source'/'Pin_Channel_define.h'
config.write_text(json.dumps({'inputs':{'channelmap':str(original_header)}}))
rel=lambda p:p.relative_to(root).as_posix()
manifest={'schemaVersion':1,'kind':'ptc-pipeline-materials','runId':run.name,'pipelineCacheKey':'a'*64,
 'addressBook':{'input':{'schematic':rel(source),'confirmed':rel(confirmed),'cbit':rel(cbit)},'originalProjectConfigPath':rel(config),'programSourceRoot':rel(program)},
 'files':[{'source':str(original_config if p==config else original_header if p==header else root/'production'/p.name),'snapshotPath':rel(p),'sha256':digest(p),'view':'python-plaintext'} for p in [source,confirmed,cbit,header,config]],
 'snapshotPaths':{str(original_header):rel(header)}}
(run/'pipeline-material-manifest.json').write_text(json.dumps(manifest))
def rejected(call):
 try: call()
 except (ValueError,OSError): return
 raise AssertionError('unsafe layout was accepted')
def complete_products():
 reads=[{'path':p.relative_to(root).as_posix(),'sha256':digest(p),'insideInputRoot':True} for p in [source,confirmed,cbit]]
 outputs={}
 for txt_name,json_name,kind in generator.PAIRS:
  txt=out/txt_name
  txt.write_text('DUT PIN P1(Kelvin)\n需闭合: Relay-ON=1 Relay-NC=2\n',encoding='utf-8')
  outputs[txt_name]={'sha256':digest(txt),'bytes':txt.stat().st_size}
  outputs[json_name]=generator.make_json(txt,out/json_name,kind,reads)
 proof={'status':'PASS','accepted_path_proofs':[{'path':'fixture'}],'readSources':reads,'input':{'path':reads[0]['path'],'sha256':digest(source)},'cbit':{'path':reads[2]['path'],'sha256':digest(cbit)},'contracts':{'selected_route_cbit_state_consistent':True},'counts':{'selected_route_conflict_proofs':0,'selected_route_conflict_events':0}}
 (out/'Path-Proofs.json').write_text(json.dumps(proof),encoding='utf-8')
 (out/'Path-Proofs.txt').write_text('status=PASS\n',encoding='utf-8')
 for name in generator.PATH_PROOFS: outputs[name]={'sha256':digest(out/name),'bytes':(out/name).stat().st_size}
 (out/'schematic-receipt.json').write_text(json.dumps({'schemaVersion':2,'parserStatus':'PASS','readSources':reads,'outputs':outputs}),encoding='utf-8')
 return reads
def validate_training(): return training.execute('validate',input_root=inputs,out_dir=out,cbit=cbit,run_root=run,source=source,confirmed=confirmed)
`;

test('schematic training roots require one exact run layout and all explicit inputs', () => python(String.raw`
layout=training.training_layout(inputs,out,run,source,confirmed,cbit)
assert layout==(run,inputs,out,source,confirmed,cbit)
for kwargs in [dict(input_root=None),dict(run_root=None),dict(source=None),dict(confirmed=None),dict(cbit=None)]:
 args=dict(input_root=inputs,out_dir=out,run_root=run,source=source,confirmed=confirmed,cbit=cbit); args.update(kwargs)
 rejected(lambda:training.training_layout(**args))
rejected(lambda:training.training_layout(inputs,root/'project/DALI/Output_Global_Material/schematic',run,source,confirmed,cbit))
rejected(lambda:training.training_layout(inputs,out,root/'Training_Materials/runs',source,confirmed,cbit))
rejected(lambda:training.training_layout(inputs,out,run,source,source,cbit))
print('PASS')
`));

test('schematic roots reject cross-run materials, source traversal and linked outputs', () => python(String.raw`
external=root/'outside.csv'; external.write_bytes(b'outside')
for position in range(3):
 args=[source,confirmed,cbit]; args[position]=external
 rejected(lambda:training.training_layout(inputs,out,run,*args))
rejected(lambda:training.training_layout(inputs,out,run,inputs/'sub/../Dali-SCH.csv',confirmed,cbit))
import os
os.link(source,out/'SCH-Connect-Map.txt')
rejected(lambda:training.training_layout(inputs,out,run,source,confirmed,cbit))
print('PASS')
`));

test('training validator retains complete seven-product hash and path-proof validation', () => python(String.raw`
complete_products()
report=validate_training(); assert report['status']=='ready',report
assert len(report['requiredOutputs'])==7
assert all(Path(p).is_relative_to(out) for p in report['requiredOutputs'])
assert report['canonicalInput']['sha256']==digest(source)
for name in [name for pair in generator.PAIRS for name in pair[:2]]+list(generator.PATH_PROOFS)+['schematic-receipt.json']:
 original=(out/name).read_bytes(); (out/name).write_bytes(b'corrupt')
 assert validate_training()['status']=='stale',name
 (out/name).write_bytes(original)
print('PASS')
`));

test('training validator refuses unapproved receipt source even with matching fixture hash', () => python(String.raw`
complete_products()
receipt_file=out/'schematic-receipt.json'; receipt=json.loads(receipt_file.read_text())
receipt['readSources'][0]['path']='project/DALI/Input_GlobalMaterial/source.csv'
receipt_file.write_text(json.dumps(receipt))
assert validate_training()['status']=='stale'
rejected(lambda:training.execute('validate',source=source,confirmed=confirmed,input_root=inputs,out_dir=out,cbit=None,run_root=run))
print('PASS')
`));

test('schematic default validation calls keep their production-default contract', () => python(String.raw`
complete_products()
# Redirect only module defaults into this fixture; no real delivery file is read
# or written and the original two-positional-argument API remains exercised.
validator.INPUT=inputs; validator.OUT=out
complete_products()
assert validator.validate(source,confirmed)['status']=='ready'
generator.INPUT_ROOT=inputs
assert generator.inside_input(source)==source
rejected(lambda:generator.inside_input(root/'outside.csv'))
print('PASS')
`));

test('original CLI stays unchanged and separate training wrapper exposes mandatory run context', () => {
  for (const script of ['generate_schematic_txt.py', 'validate_schematic_outputs.py']) {
    const help = execFileSync('python', ['-X', 'utf8', path.join(workspace, 'scripts', script), '--help'], {
      cwd: fixture(), encoding: 'utf8', windowsHide: true, timeout: 30_000,
    });
    for (const flag of ['--source', '--confirmed']) assert.ok(help.includes(flag), `${script} ${flag}`);
    assert.equal(help.includes('--run-root'), false);
  }
  const help = execFileSync('python', ['-X', 'utf8', path.join(workspace, 'scripts/training_schematic.py'), '--help'], {
    cwd: fixture(), encoding: 'utf8', windowsHide: true, timeout: 30_000,
  });
  for (const flag of ['--action', '--run-root', '--input-root', '--out-dir', '--source', '--confirmed', '--cbit']) assert.ok(help.includes(flag), flag);
});

test('missing or altered channelmap snapshot blocks instead of reading original VS files', () => python(String.raw`
complete_products()
header.write_text('changed')
rejected(validate_training)
header.unlink()
rejected(validate_training)
assert not original_header.exists()
print('PASS')
`));

test('runtime configuration isolates parser dependencies and original engine globals are restored', () => python(String.raw`
(root/'scripts').mkdir(); (root/'scripts'/'fixture.py').write_text('# trusted fixture code')
runtime=training.prepare_runtime(run,header)
runtime_config=json.loads((runtime/'project_config.json').read_text())
assert runtime_config['inputs']=={'channelmap':str(header)}
assert 'derived' not in runtime_config
assert all(not Path(value).is_absolute() and '..' not in Path(value).parts for value in runtime_config['intermediates'].values())
before=(generator.ROOT,generator.INPUT_ROOT,validator.ROOT,validator.INPUT,validator.OUT)
import os
os.environ['PTC_SCHEMATIC_STAGE_DIR']=str(root/'outside-stage')
with training.engine_context(inputs,out,runtime):
 assert generator.ROOT==runtime and validator.OUT==out
 assert os.environ['PTC_SCHEMATIC_STAGE_DIR']==str(out)
 assert generator.relative(source)==source.relative_to(root).as_posix()
assert before==(generator.ROOT,generator.INPUT_ROOT,validator.ROOT,validator.INPUT,validator.OUT)
assert os.environ['PTC_SCHEMATIC_STAGE_DIR']==str(root/'outside-stage')
print('PASS')
`));

test('schematic dependencies use immutable VS baseline after implementation changes the working header', () => python(String.raw`
baseline=run/'vs-baseline'/'source'/'Pin_Channel_define.h'; baseline.parent.mkdir(parents=True); baseline.write_bytes(header.read_bytes())
entry=next(item for item in manifest['files'] if item['snapshotPath']==rel(header))
entry['mutable']=True; entry['baselinePath']=rel(baseline)
manifest['addressBook']['immutableProgramSourceRoot']=rel(baseline.parent)
(run/'pipeline-material-manifest.json').write_text(json.dumps(manifest))
header.write_text('implementation changed worktree header')
dependencies=training.load_dependencies(run,source,confirmed,cbit)
assert dependencies['channelmap']==baseline
baseline.write_text('corrupt frozen baseline')
rejected(lambda:training.load_dependencies(run,source,confirmed,cbit))
print('PASS')
`));

test('training generation invokes original artifact engine using isolated runtime and authentic run source references', () => python(String.raw`
(root/'scripts').mkdir(); (root/'scripts'/'fixture.py').write_text('# fixture trusted code')
from types import SimpleNamespace
calls=[]
original_run=generator.subprocess.run
def parser_fixture(cmd,**kwargs):
 stage=Path(kwargs['cwd']); assert stage.is_relative_to(out)
 runtime_config=json.loads((stage/'project_config.json').read_text())
 assert runtime_config['inputs']=={'channelmap':str(header)}
 calls.append(cmd)
 stage_dali=stage/'Project'/'DALI'
 if str(cmd[1]).endswith('csv_schematic_adapter_v2.py'):
  (stage_dali/'validation_manifest.json.txt').write_text(json.dumps({'status':'PASS'}))
  stage_out=stage/'project'/'DALI'/'Output_Global_Material'/'schematic'
  for txt_name,_,_ in generator.PAIRS: (stage_out/txt_name).write_text('DUT PIN P1(Kelvin)\n需闭合: Relay-ON=1 Relay-NC=2\n',encoding='utf-8')
 else:
  assert str(cmd[1]).endswith('csv_pathproof_v2.py')
  (stage_dali/'path_proofs.json.txt').write_text(json.dumps({'status':'PASS','accepted_path_proofs':[{'fixture':True}],'contracts':{'selected_route_cbit_state_consistent':True},'counts':{'selected_route_conflict_proofs':0,'selected_route_conflict_events':0}}))
  (stage_dali/'PATHPROOF-VALIDATION.txt').write_text('status=PASS\n')
 return SimpleNamespace(returncode=0,stdout='',stderr='')
generator.subprocess.run=parser_fixture
try:
 result=training.execute('generate',run_root=run,input_root=inputs,out_dir=out,source=source,confirmed=confirmed,cbit=cbit)
finally: generator.subprocess.run=original_run
assert result['status']=='ready',result
assert len(calls)==2
receipt=json.loads((out/'schematic-receipt.json').read_text())
assert {entry['path'] for entry in receipt['readSources']}=={rel(source),rel(confirmed),rel(cbit)}
assert not (root/'project').exists()
print('PASS')
`));
