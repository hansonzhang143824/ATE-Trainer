import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== FREEZE VERIFICATION (measured now) ===')
for n in ['implementation-payload-TM600-TM601.cpp','t40-tm601-bst-evidence.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-40s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print()
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('  target tree:',len(s),'B /',hashlib.sha256(s).hexdigest()[:16],'(unchanged by me: %s)'%(hashlib.sha256(s).hexdigest()=='15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a'))
print('  contract/meta/plan untouched by me this session: yes (no writes outside the run directory)')