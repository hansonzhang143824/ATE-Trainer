import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=re.sub(r'//.*$','',u,flags=re.M); cl=code.split('\n')
print('total lines: raw=%d  stripped=%d'%(len(u.split('\n')),len(cl)))
print('non-empty stripped lines: %d'%sum(1 for l in cl if l.strip()))
print()
print('=== search for the invariants in the STRIPPED text ===')
for k in ['delay_ms','SetClamp','MeasureVI','ERROR_RES','K126_V1P5_CAP','K57_CAP_BST_SW']:
    print('  %-18s in stripped string: %d   in raw string: %d'%(k,code.count(k),u.count(k)))
print()
print('=== non-empty stripped lines, first 12 (is the code actually present?) ===')
n=0
for i,l in enumerate(cl):
    if l.strip():
        print('  L%-4d %s'%(i+1,l.strip()[:110])); n+=1
        if n>=12: break
print()
print('=== the raw lines around a known code line (L257 ACM) ===')
for i in range(254,259): print('  L%d| %r'%(i+1,u.split('\n')[i][:100]))