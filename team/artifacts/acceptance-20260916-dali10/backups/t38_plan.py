import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== new artefact + freeze state ===')
for n in ['t38-parameterised-batch-plan.md','implementation-payload-TM600-TM601.cpp','t40-tm601-bst-evidence.md','t38-acm-pin5-exposure.md']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-40s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('  target tree unchanged by me:',hashlib.sha256(s).hexdigest()=='15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c412c819ac3317' or hashlib.sha256(s).hexdigest()=='15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a')
print()
t=open(os.path.join(d,'t38-parameterised-batch-plan.md'),'rb').read().decode('utf-8-sig')
print('  four-combination matrix rows present:',all(('| **%d** |'%i) in t for i in (1,2,3,4)))
print('  coupling dependency section present:','§ 3' in t or '## 3. The one dependency' in t)
print('  coupling-argument concession present:','weakly reasoned' in t)