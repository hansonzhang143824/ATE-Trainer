import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== the three identities, re-measured NOW (they confirm the same) ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    p=os.path.join(d,f); r=open(p,'rb').read()
    print('  %-40s %7d B / %s @%s'%(f,len(r),hashlib.sha256(r).hexdigest()[:16],time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print()
print('=== THEIR REINFORCEMENT (B): can I mechanise step 1 cheaply? Prototype the one-liner now ===')
import re
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
def refs(target):
    pat=re.escape(target); n=0; sites=[]
    for root,dirs,files in os.walk(base):
        if '.git' in root: continue
        for f in files:
            if not f.lower().endswith(('.md','.json','.txt','.py','.log')): continue
            p=os.path.join(root,f)
            if os.path.basename(p)==target: continue
            try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
            except: continue
            for m in re.finditer(pat,t):
                n+=1
                win=t[max(0,m.start()-200):m.start()+260]
                if re.search(r'[0-9a-f]{16,}',win): sites.append(os.path.relpath(p,base))
    return n,sorted(set(sites))
for tgt in ['implementation-manifest.json','APPLY-TM600-TM601.md','implementation-payload-TM600-TM601.cpp']:
    n,s=refs(tgt)
    print('  %-40s name-mentions=%-4d by-identity-sites=%d'%(tgt,n,len(s)))
    for x in s[:4]: print('        %s'%x)