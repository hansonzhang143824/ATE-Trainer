import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
r=open(p,'rb').read()
print('draft %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
try:
    J=json.loads(r.decode('utf-8-sig')); print('  valid JSON:',True)
    print('  top keys:',list(J.keys()))
    print('  status:',J['status'])
    print('  afterSha256:',J['changes'][0]['afterSha256'])
    print('  limitations count:',len(J['limitations']))
    print('  contentAuthor:',J['authoredBy']['contentAuthor'])
except Exception as e: print('  JSON ERROR',e)
print()
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target test.cpp:',len(s),'B',hashlib.sha256(s).hexdigest())
print('baseline intact:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')