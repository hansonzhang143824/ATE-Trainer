import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== freeze still intact + new addendum ===')
for n in ['implementation-payload-TM600-TM601.cpp','t40-tm601-bst-evidence.md','t38-acm-pin5-exposure.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-38s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('  target tree UNCHANGED:',len(s),'B /',hashlib.sha256(s).hexdigest()[:16],'(t23, untouched by me)')
print()
print('=== verify the SCH:673 locator the captain cited ===')
m=open(r'D:\PROJECT6-DALI\ForCodexDebug\project\DALI\SCH-Connect-Map.txt','rb').read().decode('utf-8-sig',errors='replace').split('\n')
for i in (671,672,673):
    if i<len(m): print('  L%d| %s'%(i+1,m[i].rstrip()[:140]))