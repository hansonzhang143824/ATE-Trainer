import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
L=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig').split('\n')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
print('=== full comment region L180-246 in the TM600 body ===')
for i in range(179,246):
    if i<len(L):
        s=L[i].rstrip()
        mark=''
        if 'cbite.SetOn(' in s: mark='  <-- SETON'
        if s.strip().startswith('// t29 FIX'): mark='  <-- t29 BLOCK START'
        if s.strip().startswith('// t50:'): mark='  <-- t50 BLOCK START'
        if s.strip().startswith('// t43 RULING'): mark='  <-- t43'
        print('  L%-4d %s%s'%(i+1,s[:125],mark))