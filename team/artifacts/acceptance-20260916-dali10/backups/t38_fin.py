import sys,io,os,hashlib,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== FINAL STATE (re-frozen) ===')
for n in ['implementation-payload-TM600-TM601.cpp','t40-tm601-bst-evidence.md','t38-acm-pin5-exposure.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-38s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('  target tree:',len(s),'B /',hashlib.sha256(s).hexdigest())
print('  unchanged by me:',hashlib.sha256(s).hexdigest()=='15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a')
print()
print('=== the t40 doc no longer asserts any superseded payload hash ===')
t=open(os.path.join(d,'t40-tm601-bst-evidence.md'),'rb').read().decode('utf-8-sig')
for old in ['f536c7e4','38,888','2d0984d9','39,457','272667f3','73b511b7']:
    print('  %-12s occurrences: %d'%(old,t.count(old)))