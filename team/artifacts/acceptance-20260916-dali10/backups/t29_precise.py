import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
r=open(p,'rb').read(); t=r.decode('utf-8-sig')
print('test.cpp %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print()
print('=== exact string counts (case-sensitive, plain substring) ===')
for s in ['TM600_HS_RDSON','TM601_LS_RDSON','K109_BUSL1_PB0','K110_ACM18_BST','K_FPVIH_TO_BST_B','K126_V1P5_CAP']:
    print('  %-20s %d'%(s,t.count(s)))
print()
print('=== the DUT_API definition lines ===')
L=t.split('\n')
for i,l in enumerate(L):
    if l.strip().startswith('DUT_API int TM600') or l.strip().startswith('DUT_API int TM601'):
        print('  L%d: %s'%(i+1,l.strip()[:100]))
print()
print('=== any other file in the tree defining them? ===')
src=r'D:\PROJECT6-DALI\ForCodexDebug\source'
for f in sorted(os.listdir(src)):
    q=os.path.join(src,f)
    if not os.path.isfile(q) or not f.lower().endswith(('.cpp','.h')): continue
    try: tt=open(q,'rb').read().decode('utf-8-sig',errors='replace')
    except: continue
    c=tt.count('TM600_HS_RDSON')
    if c: print('  %-28s %d occurrence(s)'%(f,c))