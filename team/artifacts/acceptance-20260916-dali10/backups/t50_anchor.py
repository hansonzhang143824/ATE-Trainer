import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
print('current: %d B / %s'%(len(u.encode('utf-8')),hashlib.sha256(open(p,'rb').read()).hexdigest()))
print()
L=u.split('\n')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
print('=== CHECK: is the two-case operational fact already present? ===')
for pat in ['K48(NC)','K48(Relay-NC)','SW1_F/SW2_F','落 SW1','two-case','未激磁']:
    print('  %-18s hits: %d'%(pat,u.count(pat)))
print()
print('=== the TM600 comment region above the SetOn (anchors for insertion) ===')
for i in range(t6+22,t6+42):
    if i<len(L): print('  L%-4d %s'%(i+1,L[i].rstrip()[:140]))