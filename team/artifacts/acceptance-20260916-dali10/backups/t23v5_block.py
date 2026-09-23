import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
L=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig').split('\n')
s=[i for i,l in enumerate(L) if 'DUT_API int TM600_HS_RDSON' in l][0]
print('=== TM600 block from function start, lines with content ===')
for j in range(s,min(s+30,len(L))):
    print('%4d| %s'%(j+1,L[j].rstrip()[:140]))