import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
print('manifest keys:',list(M.keys()))
print()
print('=== provenance / drift content already recorded ===')
print('inputDriftAtReferenceTime.test-plan.json:',json.dumps(M.get('inputDriftAtReferenceTime',{}).get('test-plan.json'),ensure_ascii=False)[:280])
print()
print('frozenInputs[test-plan.json]:',json.dumps(M['frozenInputs']['test-plan.json'],ensure_ascii=False))
print()
p=os.path.join(d,'test-plan.json'); P=json.loads(open(p,'rb').read().decode('utf-8-sig'))
rh=P.get('revisionHistory') or []
print('=== t4 provenance claim, independently checked ===')
print('  top-level revision:',str(P.get('revision'))[:70])
print('  revisionHistory entries:',len(rh))
last=rh[-1] if rh else {}
print('  last history entry revision:',str(last.get('revision'))[:60] if isinstance(last,dict) else str(last)[:60])
print('  gap claim (top v20 but history last is v19):', 'v20' in str(P.get('revision')) and 'v19' in str(last))
print('  v20 present anywhere in history:', 'v20' in json.dumps(rh)[:200000])
print('  v12 entry mentions captain-applied:','captain' in json.dumps(rh).lower())