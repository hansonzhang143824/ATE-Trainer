import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
t=open(p,'rb').read().decode('utf-8-sig')
print('=== how does existing code report a test failure? ===')
for pat in ['Assert(','SetTestResult','ThrowError','ASSERT','return -1','FAIL','ErrorMsg','SetResult']:
    n=t.count(pat)
    if n: print('  %-14s %d occurrence(s)'%(pat,n))
print()
print('=== sample failure idiom in context ===')
for m in list(re.finditer(r'\bAssert\(',t))[:5]:
    s=t.rfind('\n',0,m.start()); e=t.find('\n',m.end())
    print('  ',t[s+1:e].strip()[:120])
print()
print('=== does the golden / any function guard a near-zero measurement? ===')
for pat in ['fabs(','if (','if(']:
    print('  %-8s %d'%(pat,t.count(pat)))
print()
print('=== my payload current measurement lines ===')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
for l in u.split('\n'):
    if 'v_meas' in l or 'i_meas' in l or 'rdson' in l.lower(): print('  ',l.strip()[:130])