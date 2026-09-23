import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
ch=J['changes'][0]
ch['payloadSha256']='f2e020bf64ab7384c9b547a8fd8a0f4cdda1b4595eed9a3d60a6bf3f9cbcc509'
ch['payloadSize']=34788
ch['repairNote']=('t23 amendment (user code review): positive-magnitude reporting with a same-sign criterion, '
 'fail-CLOSED via ERROR_RES on absent current or sign mismatch (Test_Method.h:32; precedent test.cpp:8087-8090), '
 'PMID 10 V steps moved from FXVIe_PLUS_10V (1x, a >=2x violation) to FXVIe_PLUS_20V, the TM601 sign text removed '
 'from the TM600 function, and two orphaned/malformed comment fragments repaired. All Set(FV,v,range) pairs now '
 'satisfy range >= 2x v (0 V exempt). See t23-amendment-evidence.md.')
for extra in [
 'TM601/TM600 RDSON reporting: the value is a POSITIVE magnitude (fabs/fabs). A sign mismatch between MVRET and MIRET is treated as a polarity/fixture fault and reports ERROR_RES, never a negative resistance. Verified 159/160/161 sequence: no code path emits a negative value.',
 'Absent current (|I| <= 0.1 A) or a MVRET/MIRET sign mismatch reports ERROR_RES (9999; Test_Method.h:32, precedent test.cpp:8087-8090). The earlier fail-OPEN behaviour that returned 0.0 mohm for an open circuit has been removed; the 0.1 A floor is a provisional engineering default (bench-signoff-required).',
 'The pulse budget is nominal and has ZERO margin on paper; the real pulse is >= 2 ms once driver/call/relay latency is included, so compliance is a bring-up verification item, not a measured result.',
]:
    if not any(extra[:40] in x for x in J['limitations']): J['limitations'].append(extra)
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); J2=json.loads(r.decode('utf-8'))
print('draft %d B / %s valid=%s limitations=%d'%(len(r),hashlib.sha256(r).hexdigest(),bool(J2),len(J2['limitations'])))
print('recorded payload:',J2['changes'][0]['payloadSha256'][:16],J2['changes'][0]['payloadSize'])
a=os.path.join(d,'t23-amendment-evidence.md'); ra=open(a,'rb').read()
print('evidence doc %d B / %s'%(len(ra),hashlib.sha256(ra).hexdigest()))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
print('payload %d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()))