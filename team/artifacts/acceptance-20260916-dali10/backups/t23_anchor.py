import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
r=open(os.path.join(d,'test-plan.json'),'rb').read()
M['frozenInputs']['test-plan.json']={
 'size':len(r),
 'sha256':hashlib.sha256(r).hexdigest(),
 'revision':'v20 (t17 closure - BST-SW ruling (ii) + idempotent generatedAt)',
 'path':'team/artifacts/acceptance-20260916-dali10/test-plan.json',
 'measuredAt':time.strftime('%Y-%m-%dT%H:%M:%S%z'),
 'note':('Measured on this EXACT path (not a glob or a test-plan.v*.json copy). The task pinned 1925250df53f8b52... / mtime 18:17:42; '
   'the same path has since moved to this value with the revision string UNCHANGED. The pinned bytes remain on disk as the preserved copy '
   'test-plan.v20.json (166099 B / 1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016, mtime 18:17:42), so the pinned '
   'anchor is still resolvable. Registered by revision string + hash computed at reference time, per the adopted convention.')}
M['inputDriftAtReferenceTime']['test-plan.json']={
 'liveWhenManifestWritten':'%d B / %s'%(len(r),hashlib.sha256(r).hexdigest()),
 'pinnedByTask':'166099 B / 1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016 (now the preserved copy test-plan.v20.json)',
 'semanticDiff':'MEASURED, NOT ASSUMED: live vs the preserved pinned copy differ in exactly 3 values and nothing else — 0 keys added, 0 keys removed, 3 changed values, all of them inputArtifacts[].sha256: [2] setup-contract.json 7f505fdb... -> fd00a508...; [4] project/DALI/meta/dali_tm_meta.json 1f5eeb5e... -> 50efba4e... (the meta was regenerated after the t20 write, which is why its size/hash moved); [5] project/DALI/meta/test_conditions.yaml 0f4354ed... -> c919b11d.... All three recorded hashes equal the live files, so the plan is CONSISTENT with its inputs; no rule, parameter, arbitration, limit or wording value changed.',
 'conclusion':'Normal upstream drift of the kind hashSemanticsGuidance describes. The plan is semantically frozen and internally consistent; only its self-recorded input hashes moved. This must not be read as a plan change or a freeze violation.'}
M['hashSemanticsGuidance']=M['hashSemanticsGuidance']+' THIS CASE HAS NOW OCCURRED AT THE EXACT PATH: test-plan.json moved from 1925250d... to fabdd24f... with the revision string unchanged and only inputArtifacts hashes differing (measured by structural diff, not inferred).'
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
raw=open(p,'rb').read(); K=json.loads(raw.decode('utf-8'))
print('manifest %d B / %s'%(len(raw),hashlib.sha256(raw).hexdigest()))
print('recorded test-plan anchor:',K['frozenInputs']['test-plan.json']['sha256'][:16],'size',K['frozenInputs']['test-plan.json']['size'])
print('drift entry present:','semanticDiff' in K['inputDriftAtReferenceTime']['test-plan.json'])