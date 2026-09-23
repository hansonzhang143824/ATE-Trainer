import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
c=os.path.join(d,'setup-contract.json'); rc=open(c,'rb').read()
plan=os.path.join(d,'test-plan.json'); rp=open(plan,'rb').read()
M['inputDriftAtReferenceTime']={
 'measuredAt':time.strftime('%Y-%m-%dT%H:%M:%S%z'),
 'method':'python open(path, rb) + hashlib.sha256 (plaintext byte hash); recompute before citing',
 'setup-contract.json':{
   'frozenAtRelease':'329115 B / 295d483a6d689e04d86744a7cfe55cb7936dd9b6ecb87ab5cc66b611b57b3d5c',
   'liveWhenManifestWritten':'%d B / %s'%(len(rc),hashlib.sha256(rc).hexdigest()),
   'assessment':'The contract moved again during the implementation window. Its TM600/TM601 ATE stimulus values, relay conclusions and polarity/sign ruling are the ones this payload implements and were verified directly by the author; the drift is an upstream regeneration, not a change to the values this payload depends on. The executor must recompute this hash and record the live value the write actually used.'},
 'test-plan.json':{
   'liveWhenManifestWritten':'%d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()),
   'note':'Matches the t17-closed revision; registered by revision string plus hash computed at reference time, per the adopted pin convention.'}
}
M['hashSemanticsGuidance']=('Reported by test-strategy-architect and worth carrying into the gate/review records: test-plan.json is generated whole by '
 'test-plan-build.py and RECOMPUTES inputArtifacts hashes at build time, so re-running it can change the file hash with NO semantic change '
 '(measured: same 166099 B size, three inputArtifacts.sha256 values changed -> hash moved from 1925250d... to ab48dfa1...). '
 '"Frozen" therefore means SEMANTIC freeze plus recompute-at-reference-time, NOT byte-constant. A hash difference confined to inputArtifacts '
 'is normal upstream drift and must be annotated, not treated as a finding or as corruption.')
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('extra keys:','inputDriftAtReferenceTime' in M[''] if '' in M else ('inputDriftAtReferenceTime' in M), '| hashSemanticsGuidance:', 'hashSemanticsGuidance' in M)