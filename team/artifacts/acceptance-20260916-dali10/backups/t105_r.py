import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
print('=== are the 18 manifest "identity sites" REAL hash citations? show them ===')
pat=re.compile(r'implementation-manifest\.json')
found=0
for root,dirs,files in os.walk(base):
    if '.git' in root: continue
    for f in files:
        if not f.lower().endswith(('.md','.json','.txt','.py','.log')): continue
        p=os.path.join(root,f)
        if os.path.basename(p)=='implementation-manifest.json': continue
        try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        except: continue
        for m in pat.finditer(t):
            win=t[max(0,m.start()-200):m.start()+300]
            hs=re.findall(r'\b[0-9a-f]{32,64}\b',win)
            if hs:
                found+=1
                rel=os.path.relpath(p,base)
                print('  %-58s -> %s'%(rel,hs[0][:20]+'...'))
                if found>=12: break
        if found>=12: break
    if found>=12: break
print()
print('  === my OWN manifest hashes: are any of those the ones cited? ===')
mine=['9eec2fbd0f52ee94','f6680ac4a7cfcdfa','265e98cb821f8b79','6bb903d3f3e29121','124aee7cbc8bc8a6','ac8c1f9f5bc8655c']
for root,dirs,files in os.walk(base):
    if '.git' in root: continue
    for f in files:
        p=os.path.join(root,f)
        rel=os.path.relpath(p,base)
        if 'backups' in rel: continue
        try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        except: continue
        for h in mine:
            if h in t: print('     %-58s cites %s'%(rel,h))