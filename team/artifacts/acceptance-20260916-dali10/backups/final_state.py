import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t5-input-confirmation.md'); r=open(p,'rb').read()
print('t5-input-confirmation.md %d B %s'%(len(r),hashlib.sha256(r).hexdigest()))
t=r.decode('utf-8-sig')
print('pending HASH cells (expect 5):',t.count('_(pending)_'))
print('C2 ruling table present:','## C2. Rulings applied' in t)
print('ruling (A) recorded:','ruling (A)' in t)
print('sign convention recorded:','-1.0 A` (derived' in t or 'derived, NOT the DFT literal' in t)
print()
print('=== final artefact set ===')
for n in ['implementation-payload-TM600-TM601.cpp','backups/test.cpp.before_TM600_TM601.bak','APPLY-TM600-TM601.md','t5-input-confirmation.md','HASH-AUDIT.md','implementer-t5-prep.md']:
    q=os.path.join(d,n)
    if os.path.exists(q):
        rr=open(q,'rb').read(); print('  %-52s %7d B %s'%(n,len(rr),hashlib.sha256(rr).hexdigest()[:16]))
print('  implementation-payload-TM600-TM601.pulse2ms-variant.cpp  -> DELETED (per captain instruction (b)/(A) dedup)')
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('target test.cpp:',len(s),'B',hashlib.sha256(s).hexdigest()[:16],'baseline:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')