import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
L=u.split('\n')
# find the TM600 F5 comment block (the misplaced TM601 text)
s=u.find('DUT_API int TM600_HS_RDSON'); e=u.find('DUT_API int TM601_LS_RDSON')
blk=L[[i for i,l in enumerate(L) if 'DUT_API int TM600_HS_RDSON' in l][0]:[i for i,l in enumerate(L) if 'DUT_API int TM601_LS_RDSON' in l][0]]
print('=== TM600 function-local comment lines mentioning TM601 / derived ===')
for i,l in enumerate(blk):
    if 'TM601' in l or 'derived' in l.lower(): print('  local %d: %s'%(i+1,l.strip()[:150]))
print()
# look for orphaned fragments generally: lines ending mid-sentence patterns
print('=== scan for suspicious orphan fragments (lines starting with ") " or lowercase continuation) ===')
for i,l in enumerate(L):
    st=l.strip()
    if st.startswith(')') or (st.startswith('and ') and '//' in l) or (st.startswith('the ') and '//' in l and not re.search(r'[.=]',st[-8:])):
        print('  %4d: %s'%(i+1,st[:120]))