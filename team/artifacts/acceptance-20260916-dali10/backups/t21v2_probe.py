import sys,io,os,re,hashlib,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('=== my current payload (t21 v1) SetOn + ranges ===')
for l in code:
    if 'SetOn(' in l: print('  SetOn:',l.strip()[:165])
print()
for l in code:
    if re.search(r'\.Set\(F[VI],',l): print('  ',l.strip()[:140])
print()
print('=== SDK range enums (read-only verification) ===')
inc=r'C:\AccoTEST\AccoTEST System\INCLude'
for f,pat in [('FXVIe.h',r'FXVIe_PLUS_\w+'),('ACM200.h',r'ACM200_\w+'),('FPVIe.h',r'FPVIe_\w+')]:
    p=os.path.join(inc,f)
    if not os.path.exists(p): print('  %s ABSENT'%f); continue
    t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    vals=sorted(set(re.findall(pat,t)))
    print('  %-10s %s'%(f,[v for v in vals if any(x in v for x in ('V','A'))][:20]))