import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
def body(name):
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+name+'('))
    j=next(k for k in range(o+1,len(L)) if L[k].startswith('DUT_API int ') and k>o+5)
    return o,j
o,j=body('TM600_HS_RDSON')
print('=== TM600_HS_RDSON (L%d-%d) ACM calls, value by value ==='%(o+1,j))
nz=0; ron=0; roff=0; vals=[]
for i in range(o,j):
    l=L[i]
    m=re.search(r'SW12_U1REF_BST_ACM\.Set\(FV,\s*([0-9.]+)',l)
    if m:
        v=float(m.group(1)); vals.append(v)
        if v!=0: nz+=1
    if 'SW12_U1REF_BST_ACM' in l and 'RELAY_ON' in l: ron+=1
    if 'SW12_U1REF_BST_ACM' in l and 'RELAY_OFF' in l: roff+=1
print('  mentions=%d  values=%s'%(len(vals),vals))
print('  non-zero FV = %d   RELAY_ON = %d   RELAY_OFF = %d'%(nz,ron,roff))
print('  expert says: mentions 10, non-zero 7, RELAY_ON 9, RELAY_OFF 1')
print('  MY EARLIER CLAIM was "9 at non-zero FV" -> %s'%('WRONG; expert correct' if nz==7 else 'matches'))
print()
print('=== TM640_BOOST_HS_OCP recount (expert says 7 mentions / 3 non-zero) ===')
o2,j2=body('TM640_BOOST_HS_OCP')
v2=[float(m.group(1)) for i in range(o2,j2) for m in [re.search(r'SW12_U1REF_BST_ACM\.Set\(FV,\s*([0-9.]+)',L[i])] if m]
print('  mentions=%d  non-zero=%d  K48=%d  K76=%d'%(len(v2),sum(1 for x in v2 if x),sum(1 for i in range(o2,j2) if 'K48' in L[i]),sum(1 for i in range(o2,j2) if 'K76' in L[i])))
print()
print('=== TM600 relay hits (expert says all zero) ===')
for r in ['K46','K48','K49','K76','K109','K110']:
    hits=[i+1 for i in range(o,j) if r in L[i]]
    print('  %-5s %d %s'%(r,len(hits),hits[:4]))