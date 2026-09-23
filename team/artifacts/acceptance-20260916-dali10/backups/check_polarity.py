import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json'); r=open(p,'rb').read()
print('live setup-contract.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('mtime',time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))))
print("architect claim: 321779 B / 93e417f60b7ff043ed515cf12a72d1708807f7fd7c9caa1b6b7c91d865a201d6")
pp=os.path.join(d,'setup-contract-pin.json')
print('pin file present:',os.path.exists(pp), os.path.getsize(pp) if os.path.exists(pp) else '')
print()
J=json.loads(r.decode('utf-8-sig'))
pd_=J.get('polarityDecision') or {}
print('=== polarityDecision ===')
print(json.dumps(pd_,ensure_ascii=False,indent=1)[:1500])
print()
print('=== does the contract mention a -1 A symbol anywhere? ===')
s=json.dumps(J,ensure_ascii=False)
for tok in ['-1 A','-1.0 A','signConvention','derivationChain','fiSymbol','commandSymbol']:
    print('  %-18s %s'%(tok, tok in s))