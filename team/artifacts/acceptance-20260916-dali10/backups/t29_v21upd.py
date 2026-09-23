import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
r=open(os.path.join(d,'test-plan.json'),'rb').read()
h=hashlib.sha256(r).hexdigest()
J=json.loads(r.decode('utf-8-sig'))
M['frozenInputs']['test-plan.json']={
 'size':len(r),'sha256':h,'revision':str(J.get('revision'))[:60],
 'path':'team/artifacts/acceptance-20260916-dali10/test-plan.json',
 'measuredAt':time.strftime('%Y-%m-%dT%H:%M:%S%z'),
 'note':('Measured on this EXACT path. The plan advanced again while this repair was in progress: v20 (166099 B, in two builds differing '
   'only in inputArtifacts hashes) -> v21 (this value), the authorised t27 revision. Registered by revision string + hash computed at '
   'reference time per the adopted convention; earlier revisions are recorded below and the v20 copies remain on disk.')}
M['inputDriftAtReferenceTime']['test-plan.json']={
 'liveWhenManifestWritten':'%d B / %s'%(len(r),h),
 'pinnedByTask':'166099 B / 1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016 (an earlier v20 build, preserved as test-plan.v20.json)',
 'semanticDiff':('v20 -> v21 is a SUBSTANTIVE authorised change, not drift. v21 (t27, freeze lifted inside this scope only) closes all three '
   'plan-side gaps this implementation had recorded as unclosable: (1) teardown wording disambiguated - with two floating channels the '
   'MEASUREMENT channel (floating channel 0, the R-VIR pair) is released LAST and the bootstrap source channel first, the strict R-POFF-04 '
   'reading, which is exactly what the payload already implements; (2) the initialisation range is now stated for both high-current items '
   '(1 V range with the 10 uA current range) with the minimal-compliant-step reasoning (6 occurrences of "minimal compliant", 4 of "10UA"); '
   '(3) the sampling wording is corrected to make the (200, 5) pair golden-specific (6 occurrences of "golden-specific", "(50, 5)" x4). '
   'Also adds revisionHistory[19] for v20 (the entry whose absence had been reported) and inputPin = setup-contract-pin.json revision 24.')}
# the gaps are no longer unclosable -> record that the plan now carries them
if 'planGapsRecordedNotFixed' in M:
    M['planGapsRecordedNotFixed']['statusUpdate']=('RESOLVED BY THE PLAN at v21 (t27, authorised). All three items are now stated in test-plan.json '
      'itself, so the payload comments are no longer the sole authority for them and a reviewer should read the plan. This section is retained '
      'unchanged as the record of what was reported while the plan was frozen; nothing here is deleted.')
    M['planGapsRecordedNotFixed']['soloAuthorityNote']=('SUPERSEDED BY v21: the plan now states all three items, so it and not this manifest is the '
      'authority. Retained for history only.')
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
raw=open(p,'rb').read()
print('manifest %d B / %s'%(len(raw),hashlib.sha256(raw).hexdigest()))
print('frozenInputs.test-plan.json ->',json.loads(raw.decode('utf-8'))['frozenInputs']['test-plan.json']['sha256'][:16])
print('valid JSON:',bool(json.loads(raw.decode('utf-8'))))