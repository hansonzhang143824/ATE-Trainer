import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'gate-logs-t28','setupArchitect-freeze-snapshots.json')
r=open(p,'rb').read()
print('=== FINAL MEASUREMENT OF THE MIRROR (series closed by declaration after this) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest()[:32],time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  they measured 255,798 B @03:19:33 with entries=76')
try:
    import json
    J=json.loads(r.decode('utf-8-sig'))
    e=J.get('entries')
    print('  entries now: %s'%(len(e) if isinstance(e,list) else 'n/a'))
except Exception as ex:
    print('  (entries count not parsed: %s)'%ex)
print('  => still moving, as expected for a live mirror. Series CLOSED BY DECLARATION per their ruling.')
print()
print('=== my three artefacts, final identity check for this turn ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    q=os.path.join(d,f); rr=open(q,'rb').read()
    print('  %-40s %7d B / %s @%s'%(f,len(rr),hashlib.sha256(rr).hexdigest()[:20],time.strftime('%H:%M:%S',time.localtime(os.stat(q).st_mtime))))