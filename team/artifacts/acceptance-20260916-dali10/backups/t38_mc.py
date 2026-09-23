import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
blk=M.get('handoffCitationRisk',{})
print('=== my current mustContain (written before t4\'s amendment) ===')
for k in blk.get('authoritativeCurrentValues',[])[:1]:
    for m in k.get('mustContain',[]): print('   -',m)
print()
print('  criterion field:',blk.get('criterion','')[:200])
print()
print('manifest on disk: %d B / %s @%s'%(os.path.getsize(p),hashlib.sha256(open(p,'rb').read()).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print()
print("t4's ③ still lists manifest as 45,296 / b3f1dc93... -> stale by one revision")