import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'t38-acm-pin5-exposure.md'),'rb').read().decode('utf-8-sig').split('\n')
for i in range(58,78):
    if i<len(t): print('  L%-3d %s'%(i+1,t[i].rstrip()[:175]))