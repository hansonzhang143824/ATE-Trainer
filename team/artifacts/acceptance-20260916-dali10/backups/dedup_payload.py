import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
dup=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
if os.path.exists(dup):
    print('duplicate existed:',os.path.getsize(dup),'B',hashlib.sha256(open(dup,'rb').read()).hexdigest())
    os.remove(dup); print('deleted')
else: print('duplicate already absent')
print()
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp','backups/test.cpp.before_TM600_TM601.bak','APPLY-TM600-TM601.md','t5-input-confirmation.md','HASH-AUDIT.md']:
    p=os.path.join(d,n)
    if os.path.exists(p):
        r=open(p,'rb').read(); print('  %-58s %6d B %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
    else: print('  %-58s (absent)'%n)
print()
src=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(src,'rb').read().decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('=== payload final state ===')
print('  BST rail drive:',sum(1 for l in code if 'SW12_U1REF_BST_ACM.Set' in l),'SW12 calls; FPVI1 refs:',[l.strip()[:60] for l in code if 'FPVI1' in l])
print('  code relays 131/132/134/135:',[t for t in ('K131','K132','K134','K135') if any(t in l for l in code)])
print('  delay_ms(1)=%d delay_ms(2)=%d | FI lines:'%(sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code)))
for l in code:
    if 'Set(FI, ' in l and ('1.0' in l or '-1.0' in l): print('     ',l.strip()[:95])
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('  target baseline intact:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')