import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
L=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig').split('\n')
for i,l in enumerate(L):
    if 'return 0;' in l:
        print('--- return at line %d; preceding 8 lines: ---'%(i+1))
        for j in range(max(0,i-8),min(len(L),i+2)): print('%4d| %s'%(j+1,L[j].rstrip()[:120]))