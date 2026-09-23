import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); r=open(p,'rb').read()
print('=== full text of the TM600 resource-arbitration assumption (live v13) ===')
print('live sha256:',hashlib.sha256(r).hexdigest())
J=json.loads(r.decode('utf-8-sig'))
it=[x for x in J.get('items',[]) if x.get('tm')=='TM600'][0]
for a in it.get('assumptions',[]):
    if 'arbitration' in str(a).lower(): print(' ',str(a))
print()
print('=== TM601 assumptions (does it echo ch1?) ===')
jt=[x for x in J.get('items',[]) if x.get('tm')=='TM601'][0]
for a in jt.get('assumptions',[]): print('  -',str(a)[:200])
print()
print('=== my payload: BST drive + FPVI1 usage (code only) ===')
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('  SW12_U1REF_BST_ACM.Set calls:',sum(1 for l in code if 'SW12_U1REF_BST_ACM.Set' in l))
print('  FPVI1 references:',[l.strip()[:70] for l in code if 'FPVI1' in l])
print('  K131/K132/K134/K135 in code:',[t for t in ('K131','K132','K134','K135') if any(t in l for l in code)])
print('  payload sha256:',hashlib.sha256(open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()).hexdigest())