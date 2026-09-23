import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
def body(name):
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+name+'('))
    depth=0; started=False
    for i in range(o,len(L)):
        s=re.sub(r'//.*$','',L[i]); depth+=s.count('{')-s.count('}')
        if '{' in s: started=True
        if started and depth==0: return o,i
    return o,len(L)
print('=== FACT: which functions close the K48/K76 leg? (brace-depth bodies) ===')
names=[l.split('(')[0].replace('DUT_API int ','') for l in L if l.startswith('DUT_API int ')]
for n in names:
    o,j=body(n); blk=L[o:j+1]
    st=[re.sub(r'//.*$','',x) for x in blk]
    k48=any('K48' in x for x in st); k76=any('K76' in x for x in st)
    comp=any('K_FPVIH_TO_BST_A' in x for x in st)
    ment=sum(x.count('SW12_U1REF_BST_ACM') for x in st)          # non-comment
    sets=sum(1 for x in st if 'SW12_U1REF_BST_ACM.Set' in x)
    if k48 or k76 or comp:
        kind='explicit K48/K76' if (k48 and k76) else ('composite K_FPVIH_TO_BST_A only' if comp else 'partial')
        print('  %-30s L%-5d-L%-5d %-30s ACM .Set=%d non-comment-mentions=%d'%(n,o+1,j+1,kind,sets,ment))
print()
print('=== the SetOn lines that carry the leg (any form) ===')
for i,l in enumerate(L):
    if 'cbite.SetOn(' in l and ('K48' in l or 'K76' in l or 'K_FPVIH_TO_BST_A' in l):
        owner=next((L[k].split('(')[0].replace('DUT_API int ','') for k in reversed(range(i)) if L[k].startswith('DUT_API int ')),'?')
        print('  L%-5d [%s] %s'%(i+1,owner,l.strip()[:140]))