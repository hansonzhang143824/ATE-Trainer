import sys,io,os,glob,hashlib,json,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); r=open(p,'rb').read()
J=json.loads(r.decode('utf-8-sig'))
print('live test-plan.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('revision:',str(J.get('revision'))[:130])
print('mtime:',time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))))
print("t4 v9 claim: 142445 B / 19ff5e842d45168aae68b24b3eb2a0d41deaff72d9f28e4080577ab7a2a14842")
print('  test-plan.v9.json exists:',os.path.exists(os.path.join(d,'test-plan.v9.json')))
print()
# do their v9 changes appear in the live file?
s=json.dumps(J,ensure_ascii=False)
for k in ['clampAnnotation','ceiling','failure signature','200 non','samples','assumptions']:
    print('  live contains %-18s %s'%(k, k in s))
it=[x for x in J.get('items',[]) if x.get('tm')=='TM600'][0]
m=it.get('measurement',{})
print()
print('TM600 measurement.samples:',json.dumps(m.get('samples'),ensure_ascii=False)[:260])
print('TM600 unresolved (BD-05 wording):',json.dumps(it.get('unresolved'),ensure_ascii=False)[:300])
ca=m.get('clampAnnotation') or it.get('clampAnnotation')
print('clampAnnotation:',json.dumps(ca,ensure_ascii=False)[:300] if ca else '(absent at these keys)')