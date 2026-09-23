import sys,io,os,json,hashlib,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
print('=== 1) my manifest, current ===')
mp=os.path.join(d,'implementation-manifest.json')
r=open(mp,'rb').read(); h=hashlib.sha256(r).hexdigest()
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(mp).st_mtime))))
print('  they cite 57,006 B / ac8c1f9f5bc8655c4a80a8c27e3e482ec6a0b26f651b28e1516035a6dbbb1d9a -> match:', h=='ac8c1f9f5bc8655c4a80a8c27e3e482ec6a0b26f651b28e1516035a6dbbb1d9a')
print()
print('=== 2) PER THEIR §2.9: is implementation-manifest.json referenced by identity elsewhere? ===')
targets={'implementation-manifest.json':r'implementation-manifest\.json',
         'APPLY-TM600-TM601.md':r'APPLY-TM600-TM601\.md'}
for name,pat in targets.items():
    print('  --- %s ---'%name)
    n=0; byhash=0
    for root,dirs,files in os.walk(base):
        if '.git' in root: continue
        for f in files:
            if not f.lower().endswith(('.md','.json','.txt','.py')): continue
            p=os.path.join(root,f)
            if os.path.basename(p)==name: continue
            try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
            except: continue
            for m in re.finditer(pat,t):
                n+=1
                seg=t[max(0,m.start()-200):m.start()+260]
                if re.search(r'[0-9a-f]{16,}',seg): byhash+=1
    print('     name mentioned %d times in other files; of those, ~%d in a window containing a 16+ hex hash'%(n,byhash))