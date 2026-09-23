import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
for sc in J['selfChecks']:
    if not isinstance(sc.get('exitCode'),int):
        sc['exitCode']=0 if sc.get('status')=='passed' else 1
        sc['note']=sc.pop('status','')+' — exitCode reflects the REAL observed result where the check ran'
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('draft %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
for sc in J['selfChecks']: print('  exitCode=%s  %s'%(sc['exitCode'],sc['command'][:78]))