import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t5-input-confirmation.md'); r=open(p,'rb').read()
print('t5-input-confirmation.md %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
t=r.decode('utf-8-sig')
print('  remaining _(pending)_ cells:',t.count('_(pending)_'))
for k in ['1925250df53f8b52','295d483a6d689e04','9554d4d6f4fe878d','d8f900a41e6a30f2','43ad8c84ed21290e']:
    print('  %s present: %s'%(k[:16], k in t))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('target test.cpp:',len(s),'B',hashlib.sha256(s).hexdigest())
print('baseline intact (no write occurred):',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')