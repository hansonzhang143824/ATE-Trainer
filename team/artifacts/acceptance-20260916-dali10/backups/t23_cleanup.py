import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
draft=os.path.join(d,'implementation-manifest.draft.json')
if os.path.exists(draft): os.remove(draft); print('removed superseded draft (canonical implementation-manifest.json now exists)')
for n in ['implementation-payload-TM600-TM601.cpp','APPLY-TM600-TM601.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-46s %7d B %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target unchanged:',hashlib.sha256(s).hexdigest()=='3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479')