import sys,io,os,json,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
# test-plan
p=os.path.join(d,'test-plan.json'); raw=open(p,'rb').read(); J=json.loads(raw.decode('utf-8-sig'))
print('test-plan.json %d B %s rev=%s'%(len(raw),hashlib.sha256(raw).hexdigest()[:16],str(J.get('revision'))[:60]))
for it in J.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        print('  %s stimulus entries marked as excitation:'%it.get('tm'))
        for s in it.get('stimulus',[]):
            if s.get('kind')!='reference':
                print('    kind=%-16s value=%-8s driven=%s'%(s.get('kind'),s.get('value'),str(s.get('driven'))[:40]))
        for s in it.get('stimulus',[]):
            if s.get('kind')=='reference': print('    [reference-only] %s'%str(s.get('value'))[:80])
# setup-contract: scan for .sv values used as excitation
p2=os.path.join(d,'setup-contract.json'); raw2=open(p2,'rb').read()
print()
print('setup-contract.json %d B %s'%(len(raw2),hashlib.sha256(raw2).hexdigest()[:16]))
t=raw2.decode('utf-8-sig')
i=t.find('"powerSequenceDelta"')
print('powerSequenceDelta snippet:',t[i:i+520] if i>0 else 'not found')