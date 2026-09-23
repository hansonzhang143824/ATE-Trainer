import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
L=u.split('\n')
print('payload total lines:',len(L))
# locate the two measurement blocks and the 10 V range lines
for i,l in enumerate(L):
    if 'F5 SIGN PREMISE' in l: s1=i
    if 'hs_rdson[site] =' in l or 'ls_rdson[site] =' in l or 'Set(FV, 10.0' in l or 'Set(FV, 10,' in l:
        print('%4d | %s'%(i+1,l.rstrip()[:150]))