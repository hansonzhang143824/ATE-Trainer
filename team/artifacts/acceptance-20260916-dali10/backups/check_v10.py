import sys,io,os,glob,hashlib,json,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); r=open(p,'rb').read()
J=json.loads(r.decode('utf-8-sig'))
print('live test-plan.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('revision:',str(J.get('revision'))[:140])
print('mtime:',time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))))
print()
print("t4 v10 claim: 144250 B / c47098a37dc11ffd54d034ecb990721674b3b764be32f5c60556ba8069af0e2e")
pv10=os.path.join(d,'test-plan.v10.json')
if os.path.exists(pv10):
    rv=open(pv10,'rb').read()
    print('  test-plan.v10.json: %d B / %s'%(len(rv),hashlib.sha256(rv).hexdigest()))
else: print('  test-plan.v10.json absent')
print()
print('=== their three v10 points present in LIVE? ===')
s=json.dumps(J,ensure_ascii=False)
for k in ['provenance','simulationDomainReference','bench-signoff-required','failure signature','clamp condition']:
    print('  %-26s %s'%(k,k in s))
it=[x for x in J.get('items',[]) if x.get('tm') in ('TM600','TM601')]
for x in it:
    st=x.get('stimulus') or []
    print('  %s stimulus provenance fields: %d/%d'%(x.get('tm'),sum(1 for e in st if 'provenance' in e),len(st)))
print()
print('revisionHistory entries:',len(J.get('revisionHistory') or []))