import sys,io,os,json,hashlib,glob,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== CURRENT manifest state (the thing I must align) ===')
p=os.path.join(d,'implementation-manifest.json'); r=open(p,'rb').read()
M=json.loads(r.decode('utf-8-sig'))
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
ch=M['changes'][0]
for k in ('path','payloadSha256','payloadSize','beforeSha256','afterSha256','afterSize','afterSha256IsPending'):
    if k in ch: print('  changes[0].%s = %s'%(k,str(ch[k])[:90]))
print('  status:',str(M.get('status'))[:110])
print('  frozenInputs.test-plan.json:',json.dumps(M['frozenInputs']['test-plan.json'],ensure_ascii=False)[:200])
print('  frozenInputs.setup-contract.json:',json.dumps(M['frozenInputs']['setup-contract.json'],ensure_ascii=False)[:200])
print()
print('=== do t28 / t33 artefacts exist? ===')
for pat in ['*t28*','*t33*','build-report.json','*generationReplay*','*RS*']:
    hits=glob.glob(os.path.join(d,'**',pat),recursive=True)
    print('  %-22s %s'%(pat,[os.path.relpath(h,d) for h in hits[:5]] if hits else 'NONE'))
print()
print('=== current payload on disk (source of truth) ===')
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
print('  %d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()))
print('  task text says: 36381 B / 73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e')
print('  MATCH:',len(rp)==36381)
print()
print('=== plan and contract live values ===')
for n in ('test-plan.json','setup-contract.json'):
    q=os.path.join(d,n); rq=open(q,'rb').read()
    print('  %-22s %8d B / %s'%(n,len(rq),hashlib.sha256(rq).hexdigest()))