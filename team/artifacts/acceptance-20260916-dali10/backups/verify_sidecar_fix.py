import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'dft-raw','dft-ir-hashes.json'); r=open(p,'rb').read()
print('sidecar live: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('mtime',time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))))
print("claimed: 20483 B / 4ebc10891ccd1191aa574bf962f73989ed52ca266ba320c9a1823dd628e6f697")
S=json.loads(r.decode('utf-8-sig'))
print('top-level keys (%d):'%len(S),list(S.keys()))
aux=['hashHistory','provenanceCorrection','lateRulingsNotInIR','notRebuilt','fixtureAnchor','verificationReports']
print('aux blocks present:',{k:(k in S) for k in aux})
lr=S.get('lateRulingsNotInIR')
print('lateRulingsNotInIR:',json.dumps(lr,ensure_ascii=False)[:300] if lr else '(absent)')
hh=S.get('hashHistory')
print('hashHistory entries:',len(hh) if isinstance(hh,list) else hh)
print()
q=os.path.join(d,'dft-ir.json'); rq=open(q,'rb').read()
print('dft-ir.json: %d B / %s'%(len(rq),hashlib.sha256(rq).hexdigest()))