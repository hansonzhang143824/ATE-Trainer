import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
print('=== THEIR CORRECTION: mirrorSize key still exists somewhere (I said it did not) ===')
hits=[]
for root,dirs,files in os.walk(base):
    if '.git' in root: continue
    for f in files:
        p=os.path.join(root,f)
        try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        except: continue
        if 'mirrorSize' in t:
            for i,l in enumerate(t.split('\n')):
                if 'mirrorSize' in l:
                    hits.append((os.path.relpath(p,base),i+1,l.strip()[:110]))
print('  occurrences of the TOKEN mirrorSize across the tree: %d'%len(hits))
for p,ln,l in hits[:14]: print('    %-58s L%-5d %s'%(p,ln,l))
print()
print('=== and confirm the rename they describe ===')
for f in ['gate-logs-t28/setupArchitect-freeze-snapshots.json','gate-logs-t28/t28-anchors.json']:
    p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10',f)
    if os.path.exists(p):
        t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        print('  %-52s mirrorSize=%d  mirrorSizeAtMirrorTime=%d'%(f.split("/")[-1],t.count('mirrorSize')-t.count('mirrorSizeAtMirrorTime'),t.count('mirrorSizeAtMirrorTime')))
print()
print('=== 97636 occurrences, scoped properly this time ===')
n=0
for root,dirs,files in os.walk(base):
    if '.git' in root: continue
    for f in files:
        p=os.path.join(root,f)
        try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        except: continue
        c=t.count('97636')
        if c: print('    %-58s %d x'%(os.path.relpath(p,base),c)); n+=c
print('  total 97636 occurrences tree-wide: %d'%n)