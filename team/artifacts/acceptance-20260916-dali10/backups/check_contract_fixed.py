import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'setup-contract.json'); r=open(p,'rb').read()
print('live setup-contract.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('mtime',time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))))
J=json.loads(r.decode('utf-8-sig'))
for tm in ('TM600','TM601'):
    for s in J['tmDeltas'][tm].get('powerSequenceDelta',[]):
        if 'power on' in str(s).lower(): print('  %s: %s'%(tm,str(s)[:170]))
print()
print('any 3.5 V left in the powerSequenceDelta of either item?')
for tm in ('TM600','TM601'):
    txt=' '.join(str(x) for x in J['tmDeltas'][tm].get('powerSequenceDelta',[]))
    print('  %s contains 3.5: %s'%(tm,'3.5' in txt))
print()
print("captain claim: 321169 B / abebeaf9...")