import sys,io,os,hashlib,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-payload-TM600-TM601.cpp','t29-k110-evidence.md']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-46s %6d B / %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('  target test.cpp unchanged:',hashlib.sha256(s).hexdigest()=='3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479')