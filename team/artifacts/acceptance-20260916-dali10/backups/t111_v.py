import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'gate-logs-t28','setupArchitect-freeze-snapshots.json')
r=open(p,'rb').read()
st=os.stat(p)
print('=== THEIR NEGATIVE VALIDATION: was it static between their two readings? ===')
print('  they cite reading #8 = 244,558 B')
print('  measured now        = %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()[:24]))
print('  mtime               = %s'%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(st.st_mtime)))
now=time.time()
print('  age of mtime        = %.1f minutes ago'%((now-st.st_mtime)/60))
print()
print('  reading sequence:')
for i,(v,who) in enumerate([(159366,'schematic-expert'),(196874,'schematic-expert'),(200758,'me'),
                            (210620,'them'),(214271,'me'),(231250,'them'),(234150,'me'),
                            (244558,'them #8'),(len(r),'ME NOW')],1):
    print('    #%-2d %8d  <- %s'%(i,v,who))
print()
print('  => static between their two readings? size moved from 244,558 to %d'%len(r))
print('     delta = %d B'%(len(r)-244558))
print()
print('=== and my three artefacts ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    q=os.path.join(d,f); rr=open(q,'rb').read()
    print('  %-40s %7d B / %s @%s'%(f,len(rr),hashlib.sha256(rr).hexdigest()[:16],time.strftime('%H:%M:%S',time.localtime(os.stat(q).st_mtime))))