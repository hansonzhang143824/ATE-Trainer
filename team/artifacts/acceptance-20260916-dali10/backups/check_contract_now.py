import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json'); raw=open(p,'rb').read()
J=json.loads(raw.decode('utf-8-sig'))
print('setup-contract.json %d B %s'%(len(raw),hashlib.sha256(raw).hexdigest()))
for tm in ('TM600','TM601'):
    v=J['tmDeltas'][tm]
    for s in v.get('powerSequenceDelta',[]):
        if 'power on' in str(s).lower() or 'VBAT' in str(s): print('  %s: %s'%(tm,str(s)[:150]))
    st=v.get('stimuli')
    if st: print('  %s stimuli[0..1]: %s'%(tm,[str(x)[:80] for x in st[:2]]))