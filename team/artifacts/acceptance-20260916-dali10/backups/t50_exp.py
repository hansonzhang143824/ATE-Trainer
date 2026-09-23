import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); L=u.split('\n'); code=re.sub(r'//.*$','',u,flags=re.M)
print('payload NOW: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  expert measured 41,797 / 6034af71... -> superseded by the captain-authorised removal')
print()
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
print('=== verifying their "third condition" (co-node instruments not enabled) on the CURRENT payload ===')
print('  TM600 body PB0_BST_ACM occurrences:', sum(l.count('PB0_BST_ACM') for l in L[t6:t7]))
print('  TM600 body FPVI1.Set lines:')
for i in range(t6,t7):
    if 'FPVI1.Set' in L[i]: print('    L%-4d %s'%(i+1,L[i].strip()[:130]))
print()
print('=== and what TM600 now closes (after the authorised removal) ===')
for l in L[t6:t7]:
    if 'cbite.SetOn(' in l: print('  ',l.strip()[:175])
print()
print('=== executable relay counts across the whole payload ===')
for k in ['K48_ACM5_AMP_REF','K76_ACM_BST','K109_BUSL1_PB0','K110_ACM18_BST','K46']:
    print('  %-20s %d'%(k,code.count(k)))