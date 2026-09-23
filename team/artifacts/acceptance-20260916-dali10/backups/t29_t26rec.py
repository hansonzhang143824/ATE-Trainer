import sys,io,os,hashlib,json,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
s=cur.find('DUT_API int TM600_HS_RDSON'); pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s); e=cur.find('\nDUT_API int',j+10)
if e<0: e=len(cur)
patched=cur[:pre]+'\n'+body.rstrip('\n')+'\n'+(cur[e:] if e<len(cur) else '')
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
open(sbx,'w',encoding='utf-8',newline='').write(patched)
r=open(sbx,'rb').read(); print('sandbox: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
# record the resolution in the manifest
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
M['newRedTriage']['T22_findings_resolution']={
 'metaAuthorityNow':'project/DALI/meta/dali_tm_meta.json = 147520 B / 50efba4ec6c271923c5f956b9c2a9f2f19173f7c0900a24ce0ec2ac3704b1f42, mtime 2026-09-16 18:52:27',
 'T22-01_K5_VBUS_Cap':('RESOLVED BY t26 (run-scope meta override), not invalidated. The meta now carries powered_pins ["ISW","SW","VBAT","VDRV"] for '
   'TM601 - VBUS removed - and its _t26OverrideNote states the removal reason in terms of the frozen ATE stimulus and the real VBUS arrival path '
   '(K3, SCH-Connect-Map.txt:213/421). My payload omission of K5 is therefore now the CORRECT state under the meta authority as well as under BD-08.'),
 'T22-03_mi_pins':('RESOLVED BY t26. capAuthority.mi_pins for TM601 is now ["PMID_SW","SW"] and for TM600 ["SW"]; the override note says the derivation had '
   'missed both, which is exactly why the FR-001 reverse check demanded K57_CAP_BST_SW / K5_VBUS_Cap "for a measured-current pin" - the gap I reported. '
   'K57 remains closed, which is now doubly justified: it sits on SW, and SW is an explicitly declared measured-current pin.'),
 'T22-02_prefix_fold':('CORROBORATED BY t26. The override note states that SW / SW1 / SW2 are DISTINCT nodes (SCH-Connect-Map L174 vs L177/L183), '
   'which is the same finding I derived from fam_intersect() prefix matching (verify_relay_trace.py:56-58).'),
 'consequence':'Findings T22-01/02/03 stand as recorded (they were measured against the pre-t26 meta) and are now marked resolved-by-t26 with the new meta hash as the re-verification basis. No payload change results.'}
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
raw=open(p,'rb').read(); print('manifest %d B / %s'%(len(raw),hashlib.sha256(raw).hexdigest()))