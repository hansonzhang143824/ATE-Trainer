import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
src=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
L=src.split('\n')
print('=== ANSWER TO THE SCHEMATIC-EXPERT UNKNOWN #1 ===')
print('Does the DEPLOYED TM600_HS_RDSON enable SW12_U1REF_BST_ACM?')
s=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON')]
e=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON')]
print('  TM600 block = L%d-%d'%(s[0]+1,e[0]))
blk=L[s[0]:e[0]]
acm=[(s[0]+1+i,l.strip()) for i,l in enumerate(blk) if 'SW12_U1REF_BST_ACM' in l]
print('  SW12_U1REF_BST_ACM occurrences inside the TM600 RDSON function: %d'%len(acm))
for ln,l in acm: print('     L%-6d %s'%(ln,l[:140]))
print()
print('  => deployed TM600 RDSON drives the ACM source at all?', 'YES' if any('Set(FV' in l for _,l in acm) else 'NO - not driven')
print()
print('=== and the TM600 ACM staircase region the expert cited (L7598/7621 style) ===')
for i in range(7590,7600):
    if 'SW12_U1REF_BST_ACM' in L[i]: print('  L%d| %s'%(i+1,L[i].strip()[:130]))
for i in range(7615,7625):
    if 'SW12_U1REF_BST_ACM' in L[i]: print('  L%d| %s'%(i+1,L[i].strip()[:130]))
print()
print('=== which functions in the deployed tree DO drive it ===')
for i,l in enumerate(L):
    if l.startswith('DUT_API int '):
        name=l.split('(')[0].replace('DUT_API int ','')
        # find block end
        j=next((k for k in range(i+1,len(L)) if L[k].startswith('DUT_API int ')),len(L))
        sets=sum(1 for x in L[i:j] if re.search(r'SW12_U1REF_BST_ACM\.Set\(FV,\s*(?!0,)',x))
        if sets: print('  %-32s drives ACM with non-zero FV: %d set(s)'%(name,sets))