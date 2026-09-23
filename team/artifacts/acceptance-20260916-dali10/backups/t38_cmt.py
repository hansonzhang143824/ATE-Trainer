import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
print('=== TM640_L7503: full comment block containing the "RELAY_OFF" claim ===')
for i in range(7590,7604):
    print('  L%d| %s'%(i+1,L[i].rstrip()[:150]))
print()
print('=== and TM641_L7606 (the other one) ===')
for i in range(7616,7626):
    print('  L%d| %s'%(i+1,L[i].rstrip()[:150]))
print()
print('=== literal check: is the ACM drive ever turned OFF during TM640? ===')
o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM640_BOOST_HS_OCP('))
j=next(k for k in range(o+1,len(L)) if L[k].startswith('DUT_API int '))
seq=[(o+1+i,x.strip()) for i,x in enumerate(L[o:j]) if 'SW12_U1REF_BST_ACM' in x]
for ln,t in seq: print('  L%-6d %s'%(ln,t[:120]))
nz=sum(1 for _,t in seq if re.search(r'Set\(FV,\s*(?!0,)',t))
off=sum(1 for _,t in seq if 'RELAY_OFF' in t)
print()
print('  non-zero FV sets: %d ; RELAY_OFF calls: %d  => the claim "全程 RELAY_OFF 不驱动" is %s'%(nz,off,'FALSE as literal text' if nz else 'consistent'))