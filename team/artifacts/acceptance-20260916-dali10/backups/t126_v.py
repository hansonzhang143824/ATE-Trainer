import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== FINAL STATE (dual-hash fingerprint check, all three artefacts) ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    p=os.path.join(d,f); b=open(p,'rb').read()
    raw=hashlib.sha256(b).hexdigest(); lf=hashlib.sha256(b.replace(b'\r\n',b'\n')).hexdigest()
    print('  %-40s %6d B | CRLF=%-4d loneLF=%-4d differ=%-5s'%(f,len(b),b.count(b'\r\n'),b.count(b'\n')-b.count(b'\r\n'),raw!=lf))
    print('       raw=%s  lf=%s'%(raw[:20],lf[:20]))
print()
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); b=open(p,'rb').read()
print('FROZEN payload intact:', hashlib.sha256(b).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')