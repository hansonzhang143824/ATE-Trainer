import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
S=open(sbx,'rb').read().decode('utf-8-sig').split('\n')
print('=== sandbox: what is at line 9133? ===')
for n in (9130,9131,9132,9133,9134):
    if n-1<len(S): print('  L%-5d %s'%(n,S[n-1].strip()[:150]))
print()
print('=== sandbox: TM600 function start and its SetOn line ===')
st=[i+1 for i,l in enumerate(S) if l.startswith('DUT_API int TM600_HS_RDSON')]
print('  DUT_API int TM600_HS_RDSON at L%s'%st)
if st:
    for i in range(st[0]-1,st[0]+45):
        if 'cbite.SetOn(' in S[i]: print('  SetOn at L%d: %s'%(i+1,S[i].strip()[:160]))
print()
tp=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
D=open(tp,'rb').read().decode('utf-8-sig').split('\n')
print('=== deployed: what is at line 9133? ===')
for n in (9132,9133,9134):
    if n-1<len(D): print('  L%-5d %s'%(n,D[n-1].strip()[:150]))
print()
print('=== deployed: TM600 start + SetOn ===')
st2=[i+1 for i,l in enumerate(D) if l.startswith('DUT_API int TM600_HS_RDSON')]
print('  DUT_API int TM600_HS_RDSON at L%s'%st2)