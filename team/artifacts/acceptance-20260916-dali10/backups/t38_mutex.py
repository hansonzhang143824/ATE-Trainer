import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
ls='\n'.join(L)
def body(name):
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+name+'('))
    j=next(k for k in range(o+1,len(L)) if L[k].startswith('DUT_API int ') and k>o+5)
    return L[o:j]
print('=== A) TM640 K48/K76: lines vs distinct token occurrences ===')
b=body('TM640_BOOST_HS_OCP')
print('  K48 lines=%d ; K48 distinct occurrences=%d'%(sum(1 for x in b if 'K48' in x),sum(x.count('K48') for x in b)))
print('  K76 lines=%d ; K76 distinct occurrences=%d'%(sum(1 for x in b if 'K76' in x),sum(x.count('K76') for x in b)))
print('  expert said "K48/K76 各 3 次" -> lines differ; distinct tokens likely 3')
for x in b:
    if 'K48' in x and not x.strip().startswith('//'): print('     EXEC L:',x.strip()[:120])
print()
print('=== B) MUTUAL EXCLUSIVITY: which functions drive ch5 (S5_ACM200_FH5) ? ===')
print('  ch5 destinations in the netlist:')
for i,l in enumerate(L[:0]): pass
sch=open(r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\SCH-Connect-Map.txt','rb').read().decode('utf-8-sig',errors='replace').split('\n')
for i,l in enumerate(sch):
    if 'S5_ACM200_FH5' in l: print('    L%d| %s'%(i+1,l.strip()[:120]))
print()
print('  functions in the TREE that use the ACM instrument AND whose SetOn closes K48/K76:')
for i,l in enumerate(L):
    if l.startswith('DUT_API int '):
        nm=l.split('(')[0].replace('DUT_API int ','')
        j=next((k for k in range(i+1,len(L)) if L[k].startswith('DUT_API int ') and k>i+5),len(L))
        blk=L[i:j]
        acm=any('SW12_U1REF_BST_ACM' in x for x in blk)
        k48=any('K48' in x for x in blk); k76=any('K76' in x for x in blk)
        if acm and (k48 or k76): print('    %-28s ACM=yes K48=%s K76=%s'%(nm,k48,k76))