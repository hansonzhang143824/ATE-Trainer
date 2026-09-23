import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
for i,l in enumerate(u.split('\n')):
    if 'NEGATIVE LIST' in l or '87' in l and l.strip().startswith('//'):
        print('%4d: %s'%(i+1,l.rstrip()[:150]))