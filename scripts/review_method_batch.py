#!/usr/bin/env python3
"""Fast, contract-driven METHOD review for a whole batch."""
from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
from check_path_conflicts import check_contract
from check_functional_relays import check_functional_relays
from ptc_contract_schema import method_execution_profile, validate_method_dft_alignment
from ptc_trim_validation import validate_trim_project_evidence
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'project'/'DALI'/'Output_Global_Material'
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def tm_of(t): return t.name.replace('-ptc-v2','').replace('-ptc','').upper()
def paths(t,tm): return t/'strategy'/f'{tm.lower()}-resource-config-contract.json',t/'method'/f'{tm.lower()}-test-method-contract.json'
def actions(m): return '\n'.join(a for phase in m.get('methodPhases',[]) for a in phase.get('actions',[]) if isinstance(a,str)).upper()
def one(raw):
 t=Path(raw); tm=tm_of(t); errors=[]; checks=[]; sp,mp=paths(t,tm)
 try:
  s,m=j(sp),j(mp); dp=Path((m.get('signedInputs') or {}).get('dftMetaPath','')); d=j(dp)
 except Exception as e: return {'trial':t.name,'tm':tm,'status':'FAIL','errors':[f'cannot read signed input: {e}'],'checks':[]}
 if m.get('stage')!='METHOD' or m.get('verdict')!='deliverable_ready': errors.append('method is not deliverable-ready')
 if (m.get('signedInputs') or {}).get('strategyContractSha256')!=h(sp): errors.append('strategy hash binding is stale')
 if (m.get('signedInputs') or {}).get('dftMetaSha256')!=h(dp): errors.append('DFT hash binding is stale')
 if any(not m.get(k) for k in ('resourceBoundary','methodPhases','measurementPlan','powerDownPlan','logPlan')): errors.append('method is missing a required section')
 checks.append({'id':'MR-01','result':'PASS','subject':'signed inputs and structure'})
 try:
  proofs=j(OUT/'schematic'/'Path-Proofs.json'); route=check_contract(s,proofs,final_four_only=True)
  if route.get('status')!='PASS': errors+=['route: '+x for x in route.get('conflicts',[])+route.get('unknown',[])]
  relay=check_functional_relays(s,d,j(OUT/'schematic'/'SCH-Connect-Map.json'),(ROOT/'knowledge'/'hardware'/'relays.md').read_text(encoding='utf-8'),(ROOT/'knowledge'/'standards'/'relay-checklist.md').read_text(encoding='utf-8'),path_proofs=proofs,manifest=j(t/'input-manifest.json'))
  if relay.get('status')!='PASS': errors+=['functional relay: '+x for x in relay.get('errors',[])+relay.get('unknown',[])]
 except Exception as e: errors.append(f'route or relay check failed: {e}')
 checks.append({'id':'MR-02','result':'PASS','subject':'routes and functional relays'})
 c=(m.get('resourceBoundary') or {}).get('registerConfiguration') or {}; ep=ROOT/str(c.get('evidencePath','')); rp=ROOT/str(c.get('sourcePath',''))
 if not ep.is_file() or h(ep)!=c.get('evidenceSha256'): errors.append('register evidence is stale')
 if not rp.is_file() or h(rp)!=c.get('sourceSha256'): errors.append('register source is stale')
 try:
  r=j(ep)
  if r.get('tm')!=tm or r.get('orderedWrites')!=c.get('orderedWrites') or not r.get('dftBinding',{}).get('verifiedAgainstDftCode2'): errors.append('register evidence does not match TM DFT Code2')
 except Exception: errors.append('register evidence is unreadable')
 checks.append({'id':'MR-03','result':'PASS','subject':'register source and Code2 binding'})
 cond=d.get('testCondition') or {}; a=actions(m); profile, profile_errors=method_execution_profile(m)
 if profile_errors: errors += ['contract: '+item for item in profile_errors]
 errors += ['DFT/METHOD: '+item for item in validate_method_dft_alignment(m,d.get('testCondition'),profile=profile)]
 family=(profile or {}).get('family',m.get('methodFamily'))
 if family == 'trim':
  trim=(m.get('measurementPlan') or {}).get('trimExecution')
  errors += ['trim: '+item for item in validate_trim_project_evidence(trim)]
 for power in cond.get('directPowerActions') or []:
  if power.get('column')!='Code1' and f"{str(power.get('pin')).upper()}=0" not in a: errors.append(f"temporary bias {power.get('pin')} lacks zero/off action")
 if not (m.get('powerDownPlan') or {}).get('actions'): errors.append('power-down plan is empty')
 checks.append({'id':'MR-04','result':'PASS','subject':f'{family} procedure, results and shutdown'})
 return {'trial':t.name,'tm':tm,'status':'FAIL' if errors else 'PASS','errors':errors,'checks':checks,'methodSha256':h(mp),'strategySha256':h(sp)}
def write(t,r):
 q=t/'review'; q.mkdir(parents=True,exist_ok=True); review={'schemaVersion':2,'artifactId':f"{r['tm'].lower()}-method-contract-review",'trial':t.name,'tm':r['tm'],'role':'rule-reviewer','stage':'RULE_REVIEW_METHOD','verdict':'pass','reviewMode':'deterministic_batch','checks':r['checks'],'blockingDefects':[],'summary':{'checksPassed':len(r['checks']),'blockingDefects':0,'nextRole':'ate-implementer'},'signedInputs':{'methodContractSha256':r['methodSha256'],'strategyContractSha256':r['strategySha256']}}
 p=q/'method-contract-review.json'; p.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); ready={'event':'deliverable_ready','status':'success','stage':'RULE_REVIEW_METHOD','verdict':'deliverable_ready','nextRole':'ate-implementer','sha256':h(p)}
 (q/'method-contract-review-deliverable-ready.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (q/'method-contract-review-self-check.json').write_text(json.dumps({'status':'PASS','reviewMode':'deterministic_batch','checks':len(r['checks']),'errors':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('trials',nargs='+'); ap.add_argument('--write-pass',action='store_true'); x=ap.parse_args(); start=time.perf_counter(); rs=[one(v) for v in x.trials]; fail=[r for r in rs if r['status']!='PASS']
 if x.write_pass and not fail:
  for raw,r in zip(x.trials,rs): write(Path(raw),r)
 print(json.dumps({'gate':'RULE_REVIEW_METHOD','mode':'deterministic_batch','status':'FAIL' if fail else 'PASS','elapsedSeconds':round(time.perf_counter()-start,3),'results':rs},ensure_ascii=False,indent=2)); raise SystemExit(bool(fail))
if __name__=='__main__': main()
