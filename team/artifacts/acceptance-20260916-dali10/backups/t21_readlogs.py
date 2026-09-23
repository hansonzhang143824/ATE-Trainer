import sys,io,os,glob,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
g=os.path.join(d,'gate-logs-t20')
print('gate-logs-t20 contents:')
for p in sorted(glob.glob(os.path.join(g,'*'))):
    r=open(p,'rb').read(); print('  %-28s %7d B %s'%(os.path.basename(p),len(r),hashlib.sha256(r).hexdigest()[:16]))
print()
for n in ['relay-trace.log','cbit.log']:
    p=os.path.join(g,n)
    if not os.path.exists(p): print(n,'ABSENT'); continue
    t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    print('='*70); print('####',n); print(t[:3000])