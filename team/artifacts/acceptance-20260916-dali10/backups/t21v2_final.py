import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
# update the draft manifest to the revision-2 payload + F1..F7 outcomes
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
ch=J['changes'][0]
ch['payloadSha256']='620d99eaa87b6971cddb16a2dbb1f4af4c950f9fc0b0edcf9b266eb824b53ebf'
ch['payloadSize']=31133
ch['repairNote']=('t21 rev2: closed F2 (TM601 now closes K44_Cap_SW2_BST2/K45_Cap_SW1_BST1/K57_CAP_BST_SW/K5_VBUS_Cap per FR-001 '
 'reverse), F3 (bare relay token 126 -> K126_V1P5_CAP, StdAfx.h:299), F4 (voltage ranges: PMID 15 V -> FXVIe_PLUS_30V, '
 'PMID 9 V -> FXVIe_PLUS_20V, ACM 10 V step -> ACM200_20V; 4.2/5 V keep 10V as the minimum compliant step), '
 'F5 (MVRET kept signed; division guarded at 0.1 A per the project idiom test.cpp:7884, below which 0 mohm is reported), '
 'F6 (pulse budget restated as THEORETICAL with zero on-paper margin, compliance moved to bring-up), '
 'F7 (meta/test_conditions landing recorded as the DSH workspace, not the VS tree).')
J['newRedTriage']['cbit_K168_K169_K170']={
 'status':'HARNESS FALSE POSITIVE (supersedes my earlier pre-existing attribution)',
 'evidence':'run_gates.ps1:65 reads scripts/gate_baseline.json with Get-Content -Raw -Encoding UTF8, which returns the 8192 B TSZ ciphertext (%TSD-Header-###%) instead of the 28 B BOM-prefixed {"cbit": true}; ConvertFrom-Json throws, $baseline is empty, and every red gate is then classified NEW-RED. The fix belongs in the harness (parse via the python-authorised reader) and gate_baseline.json must NOT be edited to mask it. It is in scripts/, outside this task scope.'}
J['gateEvidence']={
 'field':'workspace sandbox rebuild of the target with the final payload substituted in',
 'relay-trace':'PASSED - only the two pre-existing TM643 warnings; all four TM601 findings and both fabricated-name errors gone',
 'awg-params':'PASSED - FAIL=0 WARN=0 over 42 AWG functions, so the F4 range changes introduce no range violation',
 'bst-sw-sequence':'PASSED - targets=4 FAIL=0',
 'sandboxSha256':'7d97590d048cd347ffa9505b75b470f22136e3458f0b9b17fbf96afab3acdfda'}
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('draft %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('valid JSON:',bool(json.loads(r.decode('utf-8'))))
a=os.path.join(d,'t21-new-red-analysis.md'); ra=open(a,'rb').read()
print('analysis %d B / %s'%(len(ra),hashlib.sha256(ra).hexdigest()))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
v=rp.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print('payload %d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()))
print('  invariants: delay_ms(1)=%d delay_ms(2)=%d SetClamp=%d MeasureVI=%d ramp=%d guards=%d bare126=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('rampi_capv')+l.count('rampv_capv') for l in code),
 sum(l.count('i_meas[site] > 0.1') for l in code),sum(1 for l in code if ', 126,' in l)))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target unchanged:',len(s),'B',hashlib.sha256(s).hexdigest()[:16],hashlib.sha256(s).hexdigest()=='3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479')