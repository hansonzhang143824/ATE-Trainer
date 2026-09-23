import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
bad=os.path.join(d,'insert_tm600_601.py')
if os.path.exists(bad):
    raw=open(bad,'rb').read()
    print('corrupt copy present:',len(raw),'bytes, has NUL:',b'\x00' in raw)
    os.remove(bad); print('removed the corrupt PowerShell copy')
print()
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp','backups/test.cpp.before_TM600_TM601.bak','APPLY-TM600-TM601.md','HASH-AUDIT.md','implementer-t5-prep.md']:
    p=os.path.join(d,n)
    if not os.path.exists(p): print('%-58s ABSENT'%n); continue
    r=open(p,'rb').read()
    print('%-58s %7d B %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
print()
t=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()
print('payload BOM',t[:3]==b'\xef\xbb\xbf','CRLF',t.count(b'\r\n'),'loneLF',t.count(b'\n')-t.count(b'\r\n'))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('TARGET test.cpp still baseline:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')