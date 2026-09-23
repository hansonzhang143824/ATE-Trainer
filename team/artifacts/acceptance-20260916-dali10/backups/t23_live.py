import sys,io,os,json,hashlib,time,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json')
st=os.stat(p); r=open(p,'rb').read()
P=json.loads(r.decode('utf-8-sig'))
print('=== EXACT PATH: %s ==='%p)
print('  size   %d B'%len(r))
print('  sha256 %s'%hashlib.sha256(r).hexdigest())
print('  mtime  %s'%time.strftime('%H:%M:%S',time.localtime(st.st_mtime)))
print('  rev    %s'%str(P.get('revision'))[:70])
print()
print("t4 claim: 166099 / fabdd24f220d3b3e1eaf2bc7... mtime 19:04:49 rev v20")
print("my last read: 166099 / 1925250df53f8b52... (mtime 18:17:42 then)")
print()
print('=== siblings on disk (context only, NOT the anchor) ===')
for q in sorted(glob.glob(os.path.join(d,'test-plan*.json'))):
    rr=open(q,'rb').read()
    try: rev=str(json.loads(rr.decode('utf-8-sig')).get('revision'))[:34]
    except: rev='?'
    print('  %-24s %8d B %s mtime=%s %s'%(os.path.basename(q),len(rr),hashlib.sha256(rr).hexdigest()[:16],time.strftime('%H:%M:%S',time.localtime(os.stat(q).st_mtime)),rev))