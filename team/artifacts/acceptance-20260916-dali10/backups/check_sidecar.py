import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
sp=os.path.join(d,'dft-raw','dft-ir-hashes.json')
if os.path.exists(sp):
    S=json.loads(open(sp,'rb').read().decode('utf-8-sig'))
    print('sidecar size',os.path.getsize(sp),'sha256',hashlib.sha256(open(sp,'rb').read()).hexdigest()[:16])
    dl=S.get('deliverable',{})
    print('  deliverable sha256:',dl.get('sha256'))
    print('  selfVerification:',dl.get('selfVerification'))
    print('  lateRulingsNotInIR present:','lateRulingsNotInIR' in S)
    print('  fixtureAnchor present:','fixtureAnchor' in S)
    fa=S.get('fixtureAnchor') or {}
    if fa: print('  fixtureAnchor.drift:',fa.get('drift'),' keys:',list(fa.keys())[:8])
else: print('sidecar ABSENT')
print()
p=os.path.join(d,'schematic-ir.json'); r=open(p,'rb').read()
print('schematic-ir.json %d B %s mtime=%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p)))))
p2=os.path.join(d,'dft-ir.json'); r2=open(p2,'rb').read()
print('dft-ir.json %d B %s'%(len(r2),hashlib.sha256(r2).hexdigest()))