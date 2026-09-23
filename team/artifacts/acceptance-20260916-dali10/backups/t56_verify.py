import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
print('=== THE DISPUTED LINES: do TM641/TM643 close K48/K76? (raw bytes, not summaries) ===')
for ln in (7623,7734):
    print('  L%-5d %s'%(ln,L[ln-1].strip()[:180]))
print()
print('=== their line citations (L7619 / L7730) ===')
for ln in (7619,7730):
    print('  L%-5d %s'%(ln,L[ln-1].strip()[:180]))
print()
print('=== the macro expansion ===')
h=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h','rb').read().decode('utf-8-sig',errors='replace')
for m in re.finditer(r'#define\s+(K_FPVIH_TO_BST_A)\s+([^\r\n/]*)',h):
    print('  %s = %s'%(m.group(1),m.group(2).strip()))
print()
print('=== measure BOTH ways, per function ===')
def body(name):
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+name+'('))
    d=0; st=False
    for i in range(o,len(L)):
        s=re.sub(r'//.*$','',L[i]); d+=s.count('{')-s.count('}')
        if '{' in s: st=True
        if st and d==0: return o,i
for n in ['TM607_BUCK_LS_ZCD','TM608_BOOST_HS_ZCD','TM609_BOOST_HS_NEG','TM640_BOOST_HS_OCP','TM641_BST_UV','TM643_VBAT_LOOP_INDICTOR','TM600_HS_RDSON']:
    o,j=body(n); st=[re.sub(r'//.*$','',x) for x in L[o:j+1]]
    lit48=sum(x.count('K48') for x in st); lit76=sum(x.count('K76') for x in st)
    comp=sum(x.count('K_FPVIH_TO_BST_A') for x in st)
    acm=sum(1 for x in st if 'SW12_U1REF_BST_ACM.Set' in x)
    print('  %-28s literal K48=%d K76=%d | composite K_FPVIH_TO_BST_A=%d | ACM .Set=%d'%(n,lit48,lit76,comp,acm))