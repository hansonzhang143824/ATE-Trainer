import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
print('=== does ANY file cite my manifest by a specific hash? ===')
known=['ac8c1f9f5bc8655c','f6680ac4a7cfcdfa','265e98cb821f8b79','6bb903d3f3e29121','124aee7cbc8bc8a6']
hits={k:[] for k in known}
applyhash='429ad881d67d3feb'
applyhits=[]
for root,dirs,files in os.walk(base):
    if '.git' in root: continue
    for f in files:
        if not f.lower().endswith(('.md','.json','.txt','.py')): continue
        p=os.path.join(root,f)
        try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        except: continue
        for k in known:
            if k in t: hits[k].append(os.path.relpath(p,base))
        if applyhash in t: applyhits.append(os.path.relpath(p,base))
for k,v in hits.items():
    print('  %s -> %d file(s) %s'%(k,len(v),v[:3]))
print()
print('=== is APPLY-TM600-TM601.md cited by its hash anywhere? ===')
print('  %s -> %d file(s) %s'%(applyhash,len(applyhits),applyhits[:4]))