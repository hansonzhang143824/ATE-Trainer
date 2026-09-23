import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
import glob
print('=== test-plan* files present ===')
for p in sorted(glob.glob(os.path.join(d,'test-plan*'))):
    if os.path.isfile(p):
        r=open(p,'rb').read()
        print('  %-34s %8d B %s'%(os.path.basename(p),len(r),hashlib.sha256(r).hexdigest()))
p=os.path.join(d,'test-plan.json')
r=open(p,'rb').read()
import json
J=json.loads(r.decode('utf-8-sig'))
print()
print('live test-plan.json revision:',str(J.get('revision'))[:110])
print('pulseCap present?','pulseCap' in json.dumps(J))
it=[x for x in J['items'] if x.get('tm')=='TM600'][0]
m=it.get('measurement',{})
print('TM600 measurement.pulseCap:',json.dumps(m.get('pulseCap'),ensure_ascii=False)[:200])
print('TM600 params:',[x.get('name') for x in it.get('parameters',[])])
print('revisionHistory present?','revisionHistory' in J)
print()
print("architect's v4 claim: 128624 B / 738998ca98414f326fb0fdde895f4bf8aa6bd921672480cbd215384f6087a72b")
print('match live:',len(r)==128624 and hashlib.sha256(r).hexdigest().startswith('738998ca'))