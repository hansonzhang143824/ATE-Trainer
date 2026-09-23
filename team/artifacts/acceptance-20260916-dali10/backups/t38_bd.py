import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
def bd(name):
    """brace-depth delimitation: from the DUT_API line to the first closing brace at column 0"""
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+name+'('))
    depth=0; started=False
    for i in range(o,len(L)):
        s=re.sub(r'//.*$','',L[i])
        depth+=s.count('{')-s.count('}')
        if '{' in s: started=True
        if started and depth==0: return o,i
    return o,len(L)
def stats(name):
    o,j=bd(name); blk=L[o:j]
    st=[re.sub(r'//.*$','',x) for x in blk]
    ment=sum(x.count('SW12_U1REF_BST_ACM') for x in st)
    nz=sum(1 for x in st if re.search(r'SW12_U1REF_BST_ACM\.Set\(FV,\s*((?!0[,)])\d)',x))
    k48=sum(x.count('K48') for x in st); k76=sum(x.count('K76') for x in st)
    return o+1,j,ment,nz,k48,k76
print('=== brace-depth delimitation, my independent run ===')
for f in ['TM600_HS_RDSON','TM601_LS_RDSON','TM607_BUCK_LS_ZCD','TM608_BOOST_HS_ZCD','TM609_BOOST_HS_NEG','TM616_VC_OFFSET','TM640_BOOST_HS_OCP','TM641_BST_UV','TM643_VBAT_LOOP_INDICTOR']:
    try:
        o,j,m,nz,k48,k76=stats(f)
        flag=''
        if m and (k48 or k76): flag=' <== uses instrument AND closes leg'
        elif k48 or k76: flag=' <== closes leg, does NOT drive instrument'
        print('  %-26s L%-5d-L%-5d ment=%-2d nonzero=%-2d K48=%-2d K76=%-2d%s'%(f,o,j,m,nz,k48,k76,flag))
    except StopIteration: print('  %-26s NOT FOUND'%f)
print()
print('=== their claim: deployed TM601 body still drives it ===')
o,j,m,nz,_,_=stats('TM601_LS_RDSON')
print('  TM601 body L%d-%d: mentions=%d non-zero=%d'%(o,j,m,nz))
for i in range(o-1,j):
    if 'SW12_U1REF_BST_ACM' in L[i]: print('    L%d| %s'%(i+1,L[i].strip()[:110]))