import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
print('=== scope test: where does the TM640 comment block END and real code begin? ===')
for i in range(7574,7592):
    l=L[i]
    print('  L%d| %s%s'%(i+1,l.rstrip()[:135],'   <-- EXECUTABLE' if re.sub(r'//.*$','',l).strip() else ''))
print()
print('=== all warning comments about K48/K76 + SW12_U1REF_BST_ACM, with their owning function ===')
for i,l in enumerate(L):
    if '全程 RELAY_OFF' in l or ('共用接入 BST' in l):
        o=next((k for k in reversed(range(i)) if L[k].startswith('DUT_API int ')),None)
        nm=L[o].split('(')[0].replace('DUT_API int ','') if o is not None else '?'
        # does that function drive the ACM?
        j=next((k for k in range(o+1,len(L)) if L[k].startswith('DUT_API int ')),len(L)) if o is not None else 0
        nz=sum(1 for x in L[o:j] if re.search(r'SW12_U1REF_BST_ACM\.Set\(FV,\s*(?!0,)',x)) if o is not None else 0
        print('  L%-6d in %-28s drives ACM non-zero: %d  "%s"'%(i+1,nm,nz,l.strip()[:80]))