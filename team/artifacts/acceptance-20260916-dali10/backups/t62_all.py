import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
t='\n'.join(L)
print('=== all distinct tokens containing K48 / K76 anywhere in the tree ===')
for base in ['K48','K76']:
    toks=sorted(set(re.findall(base+r'[A-Za-z0-9_]*',t)))
    print('  %s variants: %s'%(base,toks))
print()
print('=== per function, ALL K48/K76-bearing mentions (comments INCLUDED) for the four direct closers ===')
def body(name):
    o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int '+name+'('))
    dd=0; st=False
    for i in range(o,len(L)):
        s=re.sub(r'//.*$','',L[i]); dd+=s.count('{')-s.count('}')
        if '{' in s: st=True
        if st and dd==0: return o,i
for n in ['TM607_BUCK_LS_ZCD','TM608_BOOST_HS_ZCD','TM609_BOOST_HS_NEG','TM640_BOOST_HS_OCP']:
    o,j=body(n)
    raw=[(o+1+k,L[o+k]) for k in range(j+1-o) if 'K48' in L[o+k] or 'K76' in L[o+k]]
    code=sum(1 for _,x in raw if not x.strip().startswith('//'))
    com=len(raw)-code
    print('  %-24s total mentions %d (code %d / comment %d)'%(n,len(raw),code,com))
    for ln,x in raw: print('      L%-5d [%s] %s'%(ln,'C' if x.strip().startswith('//') else 'X',x.strip()[:100]))