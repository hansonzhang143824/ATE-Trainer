import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
live=json.loads(open(os.path.join(d,'test-plan.json'),'rb').read().decode('utf-8-sig'))
old =json.loads(open(os.path.join(d,'test-plan.v20.json'),'rb').read().decode('utf-8-sig'))
print('=== the 3 changed inputArtifacts entries ===')
for i,(a,b) in enumerate(zip(live['inputArtifacts'],old['inputArtifacts'])):
    mark='CHANGED' if a.get('sha256')!=b.get('sha256') else 'same   '
    print('  [%d] %-10s %s'%(i,mark,a.get('path')))
    if a.get('sha256')!=b.get('sha256'):
        print('        old %s'%b.get('sha256'))
        print('        new %s'%a.get('sha256'))
        q=os.path.join(r'D:\Newtest\DSH\ATE-Coding-Plat',a['path'].replace('/',os.sep))
        if os.path.exists(q):
            rr=open(q,'rb').read()
            print('        live file now: %d B / %s  MATCHES=%s'%(len(rr),hashlib.sha256(rr).hexdigest()[:16],hashlib.sha256(rr).hexdigest()==a.get('sha256')))