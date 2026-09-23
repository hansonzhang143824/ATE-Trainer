import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

const workspace = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const setup = [
  'import sys, json, hashlib, tempfile, shutil, types',
  'from pathlib import Path',
  'sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))',
  'import training_stage_gate as gate',
  'from project_info import inputs_digest',
  'root=Path(tempfile.mkdtemp(prefix="ptc-stage-gate-test-")).resolve()',
  'run_id="training-stage-fixture"; run=root/"Training_Materials"/"runs"/run_id; run.mkdir(parents=True)',
  'def put(file,value):',
  ' file=Path(file); file.parent.mkdir(parents=True,exist_ok=True)',
  ' file.write_text(json.dumps(value,ensure_ascii=False) if isinstance(value,(dict,list)) else value,encoding="utf-8"); return file',
  'def sha(file): return hashlib.sha256(Path(file).read_bytes()).hexdigest()',
  'files=[]; base_files=[]',
  'def snapshot(relative,content,source=None,kind="fixture",base=False):',
  ' file=put(run/relative,content); name=file.relative_to(root).as_posix()',
  ' entry={"source":str(source or root/relative),"snapshotPath":name,"sha256":sha(file),"view":"python-plaintext","kind":kind}',
  ' if base: entry["path"]=entry.pop("snapshotPath"); base_files.append(entry)',
  ' else: files.append(entry)',
  ' return name',
  'original_program=root/"approved-original-source"',
  'approved={"project":"DALI","projectDir":"project/DALI","roots":{"input":"project/DALI/Input_GlobalMaterial","output":"project/DALI/Output_Global_Material","errorLog":"project/DALI/ErrorLog"},"inputs":{"dft":"dft.xlsx","schematic":"SCH.csv","cbit":"cbit.xlsx","program":str(original_program)},"approval":{"approvedBy":"fixture","approvedAt":"2026-09-22"}}',
  'approved["approval"]["inputsDigest"]=inputs_digest(approved)',
  'config=snapshot("configuration/approved-Project_Info.json",approved)',
  'registry={"stateMachine":list(gate.GATES)+["COMPLETE"],"stages":{stage:{"owner":"captain","gate":script} for stage,script in gate.GATES.items()}}',
  'registry_path=snapshot("orchestration/ptc_stage_registry.json",registry)',
  'inputs={"dft":snapshot("input/Dali_testmode.xlsx","fixture workbook",base=True),"schematic":snapshot("input/Dali-SCH.csv","fixture SCH"),"confirmed":snapshot("input/sch_confirmed.json",{}),"cbit":snapshot("input/CBIT表-DALI.xlsx","fixture CBIT")}',
  'header=snapshot("vs-project/source/Pin_Channel_define.h","fixture header",original_program/"Pin_Channel_define.h","vs-source")',
  'register=snapshot("register/tm109.sv","// Test Item: TM109\\n// field[MODE]\\nentertestmode();\\nI2CWriteSameData(DEV_ADDR, 0x10, 0x02);\\n")',
  'trial=run/"trials/tm109"; trial.mkdir(parents=True)',
  'address={"runRoot":run.relative_to(root).as_posix(),"input":inputs,"approvedProjectInfoPath":config,"registry":registry_path,"outputRoot":(run/"input-sync").relative_to(root).as_posix(),"knowledgeRoot":(run/"knowledge").relative_to(root).as_posix(),"programSourceRoot":(run/"vs-project/source").relative_to(root).as_posix(),"trials":{"TM109":trial.relative_to(root).as_posix()},"registerSources":{"TM109":register}}',
  'put(run/"run.json",{"mode":"training","runId":run_id,"releaseId":None,"projectId":None,"artifactRoot":run.relative_to(root).as_posix()})',
  'base_path=put(run/"material-manifest.json",{"runId":run_id,"cacheKey":"a"*64,"files":base_files})',
  'manifest={"schemaVersion":1,"kind":"ptc-pipeline-materials","runId":run_id,"testItems":["TM109"],"pipelineCacheKey":"b"*64,"baseCacheKey":"a"*64,"baseMaterialManifest":base_path.relative_to(root).as_posix(),"files":files,"addressBook":address,"approvedConfiguration":{"sha256":sha(root/config)}}',
  'def save_manifest(): put(run/"pipeline-material-manifest.json",manifest)',
  'save_manifest()',
  'def context(): return gate.load_context(run_id,["TM109"],root=root)',
  'def contracts():',
  ' put(trial/"input-manifest.json",{"status":"ready","materialRoots":{"input":str(run/"input"),"output":str(run/"input-sync"),"errorLog":str(run/"errorLog")},"canonicalInputs":{"dft":{},"schematic":{}}})',
  ' put(trial/"strategy/tm109-resource-config-contract.json",{"tm":"TM109"})',
  ' put(trial/"strategy/deliverable-ready.json",{})',
  ' put(trial/"method/tm109-test-method-contract.json",{"tm":"TM109"})',
  ' put(trial/"strategy/register-config-evidence.json",{})',
].join('\n');

function python(lines) {
  const program = setup + '\ntry:\n' + lines.map((line) => ' ' + line).join('\n') + '\nfinally:\n shutil.rmtree(root)\n';
  const result = spawnSync('python', ['-X', 'utf8', '-', workspace], {
    input: program, encoding: 'utf8', windowsHide: true, timeout: 30_000, maxBuffer: 2 * 1024 * 1024,
  });
  if (result.error) throw result.error;
  assert.equal(result.status, 0, result.stdout + '\n' + result.stderr);
}

test('verified material context rejects immutable source changes', () => python([
  'c=context(); assert c["header"]==run/"vs-project/source/Pin_Channel_define.h"',
  'put(root/inputs["schematic"],"changed")',
  'try: context(); raise AssertionError("accepted changed snapshot")',
  'except ValueError as error: assert "snapshot differs" in str(error)',
]));

test('embedded external/traversal paths and hardlinks are rejected', () => python([
  'for value in [str(root/"production/test.cpp"),"../production/test.cpp"]:',
  ' try: gate.validate_embedded_paths({"changes":[{"path":value}]},run); raise AssertionError("accepted escape")',
  ' except ValueError: pass',
  'gate.validate_embedded_paths({"selectedPath":"S30 -> DUT","sourcePath":str(run/"register/tm109.sv")},run)',
  '(run/"input/linked.csv").hardlink_to(root/inputs["schematic"])',
  'try: context(); raise AssertionError("accepted hardlink")',
  'except ValueError as error: assert "hardlink" in str(error)',
]));

test('mutable VS verifies sealed baseline while allowing working changes', () => python([
  'entry=next(item for item in files if item["snapshotPath"]==header)',
  'baseline=put(run/"vs-baseline/source/Pin_Channel_define.h",(root/header).read_text())',
  'entry.update(mutable=True,baselinePath=baseline.relative_to(root).as_posix()); save_manifest()',
  'put(root/header,"working edit"); context(); put(baseline,"baseline tamper")',
  'try: context(); raise AssertionError("accepted baseline tamper")',
  'except ValueError as error: assert "snapshot differs" in str(error)',
]));

test('METHOD supplies current deterministic strategy hash to original validator', () => python([
  'c=context(); contracts(); calls=[]; module=types.ModuleType("validate_method_contract")',
  'def main():',
  ' calls.append(list(sys.argv)); assert sys.argv[-1]==sha(trial/"strategy/tm109-resource-config-contract.json"); print("PASS")',
  'module.main=main; sys.modules["validate_method_contract"]=module',
  'with gate.configured(c): result=gate.downstream(c,"METHOD")',
  'assert len(calls)==1 and result[0]["status"]=="passed"',
]));

test('original failure is propagated and header/global overrides are restored', () => python([
  'c=context(); contracts(); module=types.ModuleType("validate_strategy_contract"); module.__file__="original.py"',
  'original=lambda value: Path("/original/header"); module.approved_source_header=original',
  'def main():',
  ' assert module.approved_source_header(None)==c["header"]; assert Path(module.__file__).parent.parent==run',
  ' print("fixture original failure"); raise SystemExit(2)',
  'module.main=main; sys.modules["validate_strategy_contract"]=module',
  'try:',
  ' with gate.configured(c): gate.downstream(c,"STRATEGY")',
  ' raise AssertionError("accepted failure")',
  'except ValueError as error: assert "original failure" in str(error)',
  'assert module.__file__=="original.py" and module.approved_source_header is original',
]));

test('INPUT_SYNC must pass actual DFT and schematic gates after collector', () => python([
  'c=context(); contracts(); calls=[]',
  'def report(role,status): return {"role":role,"status":status,"canonicalInput":{"path":str(c["inputs"]["dft"] if role=="dft-expert" else c["inputs"]["schematic"]),"sha256":"c"*64},"requiredOutputs":[],"missingOrStaleOutputs":[] if status=="ready" else ["stale"]}',
  'gate.schematic=lambda context: report("schematic-expert","ready")',
  'collector=types.ModuleType("prepare_input_sync"); collector.ROOT=root; collector.INTENT_RESOLUTIONS=root/"formal"; collector.SPECIAL_INFORMATION=root/"formal"; collector.validate_schematic_outputs=None',
  'def collect(): calls.append("collector"); contracts(); return 0',
  'collector.main=collect; sys.modules["prepare_input_sync"]=collector',
  'dft=types.ModuleType("validate_dft_outputs")',
  'def validate(tm,workbook,output_dir):',
  ' calls.append("dft"); assert workbook==c["inputs"]["dft"]; assert output_dir==run/"input-sync/dft/TM109"; return report("dft-expert","stale")',
  'dft.validate=validate; sys.modules["validate_dft_outputs"]=dft',
  'try:',
  ' with gate.configured(c): gate.input_sync(c)',
  ' raise AssertionError("collector alone certified ready")',
  'except ValueError as error: assert "not ready" in str(error)',
  'saved=json.loads((trial/"input-manifest.json").read_text()); assert saved["status"]=="needs-derived-artifacts"',
  'assert calls==["collector","dft"] and saved["dispatchableRoles"]==["dft-expert"]',
]));

test('empty implementation or external source is blocked before original validator', () => python([
  'c=context(); contracts()',
  'for changes in [[],[{"path":str(root/"production/test.cpp"),"symbols":["TM109"]}]]:',
  ' put(trial/"implementation/implementation-manifest.json",{"changes":changes})',
  ' try:',
  '  with gate.configured(c): gate.downstream(c,"IMPLEMENTATION")',
  '  raise AssertionError("accepted empty/external implementation")',
  ' except ValueError: pass',
]));

test('real register extractor preserves signed values and corrects only training locator', () => python([
  'c=context(); contracts(); put(run/"input-sync/dft/TM109/dft-meta.json",{"rawIntent":{"Code2":"field[MODE]"}})',
  'with gate.configured(c): result=gate.prepare_register(c)',
  'evidence=json.loads((trial/"strategy/register-config-evidence.json").read_text())',
  'assert evidence["source"]["path"]==str(root/register)',
  'assert evidence["orderedWrites"][0]["value"]=="0X02" and evidence["dftBinding"]["verifiedAgainstDftCode2"] is True',
  'assert result[0]["evidenceSha256"]==sha(trial/"strategy/register-config-evidence.json")',
]));

test('unknown replacement registry gate is rejected rather than bypassed', () => python([
  'registry["stages"]["METHOD"]["gate"]="scripts/not_approved.py"; put(root/registry_path,registry)',
  'next(entry for entry in files if entry["snapshotPath"]==registry_path)["sha256"]=sha(root/registry_path)',
  'save_manifest(); gate.ROOT=root',
  'try: gate.execute(run_id,"METHOD",["TM109"]); raise AssertionError("accepted replacement gate")',
  'except ValueError as error: assert "not registered" in str(error)',
]));
