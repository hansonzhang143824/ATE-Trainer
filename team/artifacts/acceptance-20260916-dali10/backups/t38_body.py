import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
L=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig').split('\n')
s=[i for i,l in enumerate(L) if 'DUT_API int TM601_LS_RDSON' in l][0]
print('=== TM601 body: Step 2/3 region around the ACM drive (payload L405–L440) ===')
for i in range(404,440):
    if i<len(L): print('%4d| %s'%(i+1,L[i].rstrip()[:150]))
print()
print('=== TM601 teardown region (L485–L505) ===')
for i in range(484,505):
    if i<len(L): print('%4d| %s'%(i+1,L[i].rstrip()[:150]))