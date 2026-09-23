import sys,io,os,hashlib,re,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(p,'rb').read(); t=r.decode('utf-8-sig')
print('note: %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  they say: 43,294 B / 18043e4155cdef43e30c7b93dd105854739e282049d28bf75546f8e5299fc2aa @22:09:40')
print()
print('=== STATUS: is the INTERSECTION action still prescribed, or updated to removal? ===')
for pat in ['INTERSECTION','保留 `K109`','保留 K109','REMOV','removal','K109/K110 = 0','K109`/`K110` = 0','K109_K110']:
    print('  %-22s %d'%(pat,t.count(pat)))
print()
print('=== the INTERSECTION lines in context ===')
for i,l in enumerate(t.split('\n')):
    if 'INTERSECTION' in l or ('K109' in l and ('保留' in l or 'keep' in l)):
        print('  L%-5d %s'%(i+1,l.strip()[:160]))