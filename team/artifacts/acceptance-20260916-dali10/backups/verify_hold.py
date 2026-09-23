import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t5-input-confirmation.md'); raw=open(p,'rb').read()
print('t5-input-confirmation.md %d B %s'%(len(raw),hashlib.sha256(raw).hexdigest()))
t=raw.decode('utf-8-sig')
print('blank HASH cells:',t.count('_(pending)_'))
print('HOLD stated:', 'STATE: HOLD' in t)
# final safety: confirm no write occurred to the target this turn
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target test.cpp sha256:',hashlib.sha256(s).hexdigest())
print('baseline intact:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')
print('run dir listing (top-level artifacts I own):')
for n in sorted(os.listdir(d)):
    q=os.path.join(d,n)
    if os.path.isfile(q) and ('payload' in n or 'APPLY' in n or 'HASH-AUDIT' in n or 'confirmation' in n or n.startswith('implementer')):
        print('   %-58s %7d B'%(n,os.path.getsize(q)))