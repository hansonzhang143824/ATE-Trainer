import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
def owner(ln):
    for i in range(ln-1,-1,-1):
        if L[i].startswith('DUT_API int '): return i+1, L[i].split('(')[0].replace('DUT_API int ','')
    return None,None
for target in (7598,7621):
    o,n=owner(target)
    print('L%d belongs to %s (defined L%d)'%(target,n,o))
    # does that function drive the ACM?
    j=next((k for k in range(o,len(L)) if L[k].startswith('DUT_API int ')),len(L))
    sets=[(o+1+i,x.strip()) for i,x in enumerate(L[o:j]) if 'SW12_U1REF_BST_ACM.Set' in x]
    print('   ACM sets in that function: %d'%len(sets))
    for ln,t in sets: print('      L%-6d %s'%(ln,t[:130]))
    print()
print('=== side-by-side: the four functions the warning names vs TM600 ===')
for f in ['TM607_BUCK_LS_ZCD','TM640_BOOST_HS_OCP','TM600_HS_RDSON']:
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+f+'('))
    j=next((k for k in range(o+1,len(L)) if L[k].startswith('DUT_API int ')),len(L))
    blk=L[o:j]
    k48=sum(1 for x in blk if 'K48' in x); k76=sum(1 for x in blk if 'K76' in x)
    off=sum(1 for x in blk if 'SW12_U1REF_BST_ACM.Set(FV, 0' in x and 'RELAY_OFF' in x)
    nz=sum(1 for x in blk if re.search(r'SW12_U1REF_BST_ACM\.Set\(FV,\s*(?!0,)',x))
    print('  %-26s K48=%d K76=%d  ACM non-zero=%d RELAY_OFF=%d'%(f,k48,k76,nz,off))